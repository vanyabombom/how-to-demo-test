import os
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import (
    settings, 
    STATIC_DIR, 
    FRAMES_DIR, 
    UPLOADS_DIR, 
    SAMPLE_DIR
)
from app.schemas import (
    HowToAnalysisResult, 
    SampleInfo, 
    ConfigResponse, 
    UpdateConfigRequest
)
from app.sample_service import get_sample_list, get_cached_ground_truth
from app.video_service import extract_frame_at_timestamp
from app.analyzer import analyze_video

app = FastAPI(
    title="Video Demonstration to How-To API",
    description="Transforms screen recordings into concise, verified step-by-step guides with grounding frames and mistake pruning.",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folders for video & frame playback
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/sample_data", StaticFiles(directory=str(SAMPLE_DIR)), name="sample_data")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Video to How-To API",
        "endpoints": ["/api/samples", "/api/sample/{id}", "/api/process", "/api/config"]
    }

@app.get("/api/samples", response_model=List[SampleInfo])
def list_samples():
    """Returns available reproducible test cases."""
    return get_sample_list()

@app.get("/api/sample/{sample_id}", response_model=HowToAnalysisResult)
async def get_sample_analysis(sample_id: str):
    """
    Returns pre-computed ground-truth analysis for sample video,
    extracting actual frame screenshots from the local MP4.
    """
    video_path = SAMPLE_DIR / f"{sample_id}.mp4"
    if not video_path.exists():
        # Try finding with test_ prefix
        video_path = SAMPLE_DIR / f"test_{sample_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample video '{sample_id}' not found")
        
    result = get_cached_ground_truth(sample_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Ground truth not found for '{sample_id}'")

    # Ensure frame screenshots are extracted locally
    for step in result.steps:
        frame_name = f"frame_{sample_id}_step_{step.step_number}.jpg"
        step.screenshot_url = extract_frame_at_timestamp(
            video_path, step.timestamp_keyframe_sec, frame_name
        )

    return result

@app.post("/api/process", response_model=HowToAnalysisResult)
async def process_video(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None)
):
    """
    Processes an uploaded MP4 video recording through the multi-modal analyzer.
    """
    if not file.filename.lower().endswith((".mp4", ".mov", ".webm", ".mkv")):
        raise HTTPException(status_code=400, detail="Only video files (.mp4, .mov, .webm) are supported")

    # Save uploaded file
    safe_name = f"upload_{os.getpid()}_{file.filename}"
    upload_path = UPLOADS_DIR / safe_name
    
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = await analyze_video(
            video_path=upload_path,
            api_key=api_key or settings.API_KEY,
            base_url=base_url or settings.BASE_URL,
            model_name=model_name or settings.MODEL_NAME,
            sample_id=file.filename.replace(".mp4", "")
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sample/{sample_id}/process", response_model=HowToAnalysisResult)
async def process_sample_video(
    sample_id: str,
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None)
):
    """
    Runs multi-modal video analysis directly on an existing video in sample_data.
    """
    video_path = SAMPLE_DIR / f"{sample_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample video '{sample_id}' not found")

    try:
        result = await analyze_video(
            video_path=video_path,
            api_key=api_key or settings.API_KEY,
            base_url=base_url or settings.BASE_URL,
            model_name=model_name or settings.MODEL_NAME,
            sample_id=sample_id
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
def list_provider_models():
    """Lists available models from current provider."""
    from openai import OpenAI
    key = settings.API_KEY or ""
    if not key:
        return {"models": []}
    try:
        client = OpenAI(api_key=key, base_url=settings.BASE_URL)
        models = client.models.list()
        return {"models": [m.id for m in models.data]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/config", response_model=ConfigResponse)
def get_config():
    """Returns current API configuration (with masked key)."""
    key = settings.API_KEY or ""
    masked = f"{key[:4]}...{key[-4:]}" if len(key) >= 8 else ("Set" if key else "Not set")
    return ConfigResponse(
        api_provider=settings.API_PROVIDER,
        base_url=settings.BASE_URL,
        model_name=settings.MODEL_NAME,
        has_api_key=bool(key),
        masked_key=masked
    )

@app.post("/api/config")
def update_config(req: UpdateConfigRequest):
    """Allows UI to update API key, base URL, or model during runtime and persists to .env."""
    if req.api_key is not None:
        settings.API_KEY = req.api_key.strip()
    if req.base_url is not None:
        settings.BASE_URL = req.base_url.strip()
    if req.model_name is not None:
        settings.MODEL_NAME = req.model_name.strip()
    if req.api_provider is not None:
        settings.API_PROVIDER = req.api_provider.strip()

    try:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        lines = [
            f"API_PROVIDER={settings.API_PROVIDER}",
            f"API_KEY={settings.API_KEY}",
            f"BASE_URL={settings.BASE_URL}",
            f"MODEL_NAME={settings.MODEL_NAME}\n"
        ]
        env_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"Failed to persist .env: {e}")

    return {"status": "updated", "model": settings.MODEL_NAME, "has_key": bool(settings.API_KEY)}

@app.post("/api/export")
def export_guide_markdown(data: HowToAnalysisResult):
    """Exports guide to clean Markdown format."""
    lines = [
        f"# {data.guide_title}",
        f"**Target Operation:** {data.target_operation}  ",
        f"**Application:** {data.app_detected}  ",
        f"**Status:** {'Success Verified' if data.final_success_achieved else 'Incomplete / Needs Clarification'}",
        ""
    ]
    if data.declined_to_conclude:
        lines.extend([
            "> [!WARNING] Decline Notice",
            f"> {data.decline_reason}",
            ""
        ])

    lines.append("## Ordered Recommended Steps\n")
    recommended = [s for s in data.steps if s.is_in_recommended_path]
    for step in recommended:
        badge = f" `[{step.step_type.upper()}]`" if step.step_type != "normal" else ""
        lines.append(f"### Step {step.step_number}: {step.title}{badge}")
        lines.append(f"**Timestamp:** {step.timestamp_start} - {step.timestamp_end}")
        lines.append(f"{step.instruction}\n")
        if step.chosen_setting:
            lines.append(f"- **Applied Setting:** `{step.chosen_setting}`")
        if step.warning_or_gap_note:
            lines.append(f"- **Note:** {step.warning_or_gap_note}")
        lines.append("")

    if data.abandoned_mistakes:
        lines.append("## Abandoned Mistakes (Pruned from Guide)")
        for m in data.abandoned_mistakes:
            lines.append(f"- ~{m}~")
        lines.append("")

    if data.final_settings_summary:
        lines.append("## Final Configuration Summary")
        for k, v in data.final_settings_summary.items():
            lines.append(f"- **{k}:** `{v}`")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated in {data.processing_time_sec}s | Variable cost: ${data.variable_cost_usd:.5f} | Model: {data.model_name}*")

    return {"markdown": "\n".join(lines)}
