import os
import json
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from openai import OpenAI

from app.config import settings, FRAMES_DIR
from app.schemas import HowToAnalysisResult, GuideStep, StepType
from app.video_service import (
    get_video_duration,
    extract_keyframe_samples,
    extract_frame_at_timestamp
)
from app.cost_service import calculate_costs_and_metrics

SYSTEM_PROMPT = """
You are an expert technical documentation generator analyzing a screen demonstration video.
Your job is to produce an accurate, ordered, actionable how-to guide so a new user can complete the demonstrated operation.

CRITICAL RULES TO FOLLOW RIGOROUSLY:
1. VISUAL GROUNDING OVER SPEECH:
   - Recover necessary visible screen actions rather than merely summarizing speech.
   - If an action is visible on screen but the speaker is silent, you MUST include it as a step with step_type="silent_action".

2. MISTAKES & CORRECTIONS PRUNING:
   - If the demonstrator makes a mistaken choice, pauses, and corrects it:
     * Flag the mistaken action with step_type="corrected_mistake" and is_in_recommended_path=false.
     * Record a concise summary of the mistake in abandoned_mistakes.
     * Include ONLY the final corrected choice as a valid step (is_in_recommended_path=true) with the final chosen_setting.
     * Do NOT prescribe the wrong action in the recommended guide!

3. ANTI-HALLUCINATION & GAP DETECTION:
   - Do NOT invent clicks, buttons, or dialogs not seen in the recording.
   - Do NOT describe a final success state unless the recording actually displays visible proof (e.g. downloaded file bar, success notification, completed status).
   - If the video jumps over a critical prerequisite step (a jump cut or gap), flag it:
     * Add a step or warning with step_type="missing_step_gap" and warning_or_gap_note explaining the gap.
     * Set declined_to_conclude=true and specify decline_reason if the procedure cannot be reliably completed without that missing information.

4. TIMESTAMP ACCURACY:
   - Every step must have timestamp_start and timestamp_end ("MM:SS"), plus timestamp_keyframe_sec (the exact second where the action/setting is most clearly visible).

OUTPUT FORMAT:
Return a single valid JSON object strictly matching this structure:
{
  "guide_title": "How to Export Filtered Orders",
  "target_operation": "Exporting Filtered Orders to CSV",
  "app_detected": "Orders Management Dashboard",
  "final_success_achieved": true,
  "final_success_evidence": "Toast message 'Export successful: orders_2026.csv' appeared",
  "declined_to_conclude": false,
  "decline_reason": null,
  "steps": [
    {
      "step_number": 1,
      "title": "Open Date Range Filter",
      "instruction": "Click the 'Filter by Date' dropdown in the top action bar.",
      "timestamp_start": "00:02",
      "timestamp_end": "00:06",
      "timestamp_keyframe_sec": 4.0,
      "step_type": "normal",
      "is_in_recommended_path": true,
      "chosen_setting": {"Date Range": "Last 30 Days"},
      "evidence_description": "Dropdown menu expanded displaying date options",
      "warning_or_gap_note": null
    }
  ],
  "abandoned_mistakes": [
    "Demonstrator initially clicked JSON format, then switched to CSV"
  ],
  "final_settings_summary": {
    "Date Range": "Last 30 Days",
    "Format": "CSV"
  }
}
"""

def format_seconds_to_mmss(sec: float) -> str:
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

def extract_and_parse_json(content: str) -> Dict[str, Any]:
    """
    Robustly parses JSON from LLM responses, handling markdown blocks,
    fences, prefix/suffix commentary, and trailing characters.
    """
    cleaned = content.strip()
    
    # 1. Try direct json.loads
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Extract content from ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except Exception:
            pass

    # 3. Search for outermost balanced { ... }
    first_brace = cleaned.find('{')
    if first_brace != -1:
        last_brace = cleaned.rfind('}')
        while last_brace > first_brace:
            candidate = cleaned[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except Exception:
                # Walk backward to find the preceding closing brace
                last_brace = cleaned.rfind('}', first_brace, last_brace)

    # 4. Fallback regex
    json_match = re.search(r"(\{[\s\S]*\})", cleaned)
    if json_match:
        return json.loads(json_match.group(1))

    raise ValueError(f"Failed to parse valid JSON from AI model response: {content[:300]}")

async def analyze_video(
    video_path: Path,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    sample_id: Optional[str] = None
) -> HowToAnalysisResult:
    """
    Analyzes an MP4 video file and produces a verified HowToAnalysisResult.
    """
    start_time = time.time()
    duration = get_video_duration(video_path)
    
    key = api_key or settings.API_KEY
    url = base_url or settings.BASE_URL
    model = model_name or settings.MODEL_NAME

    # If no API key is set, check if we have a precomputed ground truth for this sample
    if not key:
        from app.sample_service import get_cached_ground_truth
        clean_stem = re.sub(r"^upload_\d+_", "", video_path.stem)
        clean_id = sample_id or clean_stem
        cached = get_cached_ground_truth(clean_id) or get_cached_ground_truth(clean_stem)
        if cached:
            # Extract actual frames for the cached steps if missing
            for step in cached.steps:
                frame_name = f"frame_{clean_stem}_step_{step.step_number}.jpg"
                step.screenshot_url = extract_frame_at_timestamp(
                    video_path, step.timestamp_keyframe_sec, frame_name
                )
            cached.processing_time_sec = round(time.time() - start_time, 2)
            cached.source_mode = "offline_ground_truth"
            return cached
        else:
            raise ValueError(
                "No API Key configured. Please configure an OpenRouter, Groq, or Gemini API key in Settings, "
                "or test one of the preloaded sample videos."
            )

    # 1. Sample frames from the video with timestamps
    frames_data = extract_keyframe_samples(video_path, sample_interval_sec=3.5, max_frames=14)
    
    # 2. Build multi-modal message payload
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text", 
            "text": (
                f"Analyze this screen demonstration video. The total duration is {duration:.1f} seconds. "
                f"Here are sequential keyframes sampled at specific timestamps. "
                f"Identify every action, recover silent actions, prune out corrected mistakes from the main path, "
                f"and flag any gaps/jumps. Produce the required JSON."
            )
        }
    ]
    
    for t, data_url in frames_data:
        user_content.append({
            "type": "text",
            "text": f"--- Frame at timestamp {format_seconds_to_mmss(t)} ({t:.1f}s) ---"
        })
        user_content.append({
            "type": "image_url",
            "image_url": {"url": data_url}
        })

    client = OpenAI(api_key=key, base_url=url)
    try:
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT + "\nCRITICAL: Output strictly the final valid JSON object."},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,
            "max_tokens": 3000
        }
        if "gemini" in model.lower() or "gpt" in model.lower():
            kwargs["response_format"] = {"type": "json_object"}
        if "openrouter" in url.lower():
            kwargs["extra_body"] = {"reasoning": {"effort": "none", "exclude": True}}

        response = client.chat.completions.create(**kwargs)
    except Exception as exc:
        err_msg = str(exc)
        if "No endpoints found" in err_msg:
            raise ValueError(
                f"Model '{model}' is no longer available on OpenRouter. "
                "Please select 'openrouter/free' (Auto Free Vision Router) in Model & API Settings."
            ) from exc
        if "content must be a string" in err_msg:
            raise ValueError(
                f"Model '{model}' is a text-only model and cannot process video frames. "
                "Please select a multimodal Vision model (e.g. 'openrouter/free')."
            ) from exc
        if "model_decommissioned" in err_msg:
            raise ValueError(
                f"Model '{model}' has been decommissioned by the provider. "
                "Please choose an active multimodal model (e.g. 'openrouter/free')."
            ) from exc
        raise
    
    elapsed = time.time() - start_time
    msg = response.choices[0].message
    content = msg.content or getattr(msg, "reasoning", "") or "{}"
    
    # Robustly parse JSON from model response
    data = extract_and_parse_json(content)

    # Extract token usage
    usage = getattr(response, "usage", None)
    prompt_tokens = usage.prompt_tokens if usage else int(duration * 260)
    completion_tokens = usage.completion_tokens if usage else len(content) // 4

    metrics = calculate_costs_and_metrics(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        video_duration_sec=duration,
        elapsed_time_sec=elapsed,
        model_name=model
    )

    result = HowToAnalysisResult(
        guide_title=data.get("guide_title", "Generated How-To Guide"),
        target_operation=data.get("target_operation", "Demonstrated Operation"),
        app_detected=data.get("app_detected", "Web Application"),
        final_success_achieved=data.get("final_success_achieved", False),
        final_success_evidence=data.get("final_success_evidence"),
        declined_to_conclude=bool(data.get("declined_to_conclude", False)),
        decline_reason=data.get("decline_reason"),
        steps=[
            GuideStep(
                step_number=int(s.get("step_number", idx + 1)),
                title=str(s.get("title", f"Step {idx + 1}")),
                instruction=str(s.get("instruction", "")),
                timestamp_start=str(s.get("timestamp_start", "00:00")),
                timestamp_end=str(s.get("timestamp_end", "00:00")),
                timestamp_keyframe_sec=float(s.get("timestamp_keyframe_sec", 0.0)),
                step_type=s.get("step_type") if s.get("step_type") in ["normal", "silent_action", "corrected_mistake", "missing_step_gap"] else "normal",
                is_in_recommended_path=bool(s.get("is_in_recommended_path", True)),
                chosen_setting=s.get("chosen_setting") if isinstance(s.get("chosen_setting"), dict) else ({"Setting": s.get("chosen_setting")} if s.get("chosen_setting") is not None else None),
                evidence_description=str(s.get("evidence_description", "")) if s.get("evidence_description") else None,
                warning_or_gap_note=str(s.get("warning_or_gap_note", "")) if s.get("warning_or_gap_note") else None
            )
            for idx, s in enumerate(data.get("steps", []))
            if isinstance(s, dict)
        ],
        abandoned_mistakes=[str(m) for m in data.get("abandoned_mistakes", []) if m],
        final_settings_summary={
            str(k): (", ".join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v))
            for k, v in (data.get("final_settings_summary") or {}).items()
        } if isinstance(data.get("final_settings_summary"), dict) else {},
        processing_time_sec=metrics["processing_time_sec"],
        variable_cost_usd=metrics["variable_cost_usd"],
        token_usage=metrics["token_usage"],
        model_name=model,
        source_mode="live_ai_inference"
    )

    # 3. Extract exact screenshots for each step using FFmpeg
    video_hash = str(abs(hash(str(video_path))))[:8]
    for step in result.steps:
        frame_filename = f"frame_{video_hash}_step_{step.step_number}.jpg"
        step.screenshot_url = extract_frame_at_timestamp(
            video_path, 
            step.timestamp_keyframe_sec, 
            frame_filename
        )

    return result
