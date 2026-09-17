import os
import sys
from pathlib import Path
import pytest

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.schemas import GuideStep, HowToAnalysisResult, StepType
from app.cost_service import calculate_costs_and_metrics
from app.sample_service import get_sample_list, get_cached_ground_truth
from app.video_service import get_video_duration, extract_frame_at_timestamp

SAMPLE_DIR = backend_dir / "sample_data"

def test_schemas_validation():
    step = GuideStep(
        step_number=1,
        title="Click Filter",
        instruction="Click the Date filter button",
        timestamp_start="00:02",
        timestamp_end="00:05",
        timestamp_keyframe_sec=3.5,
        step_type=StepType.SILENT_ACTION,
        is_in_recommended_path=True,
        chosen_setting={"Date": "Past 30 Days"}
    )
    assert step.step_type == StepType.SILENT_ACTION
    assert step.is_in_recommended_path is True
    assert step.chosen_setting["Date"] == "Past 30 Days"

def test_cost_calculation():
    metrics = calculate_costs_and_metrics(
        prompt_tokens=10_000,
        completion_tokens=500,
        video_duration_sec=30.0,
        elapsed_time_sec=6.5,
        model_name="google/gemini-2.0-flash-exp:free"
    )
    assert metrics["processing_time_sec"] == 6.5
    assert metrics["variable_cost_usd"] > 0
    assert "token_usage" in metrics
    assert metrics["token_usage"]["total_tokens"] == 10_500

def test_sample_service():
    samples = get_sample_list()
    assert len(samples) == 3
    sample_ids = [s.id for s in samples]
    assert "demo_base" in sample_ids
    assert "demo_edgecase" in sample_ids
    assert "demo_variation" in sample_ids
    
    base = get_cached_ground_truth("demo_base")
    assert base is not None
    assert base.final_success_achieved is True
    assert len(base.steps) == 6
    assert all(step.is_in_recommended_path for step in base.steps)

    edgecase = get_cached_ground_truth("demo_edgecase")
    assert edgecase is not None
    assert edgecase.final_success_achieved is False
    assert edgecase.declined_to_conclude is True
    assert edgecase.decline_reason is not None
    # Check that validation failure gap step exists
    gap_steps = [s for s in edgecase.steps if s.step_type == StepType.MISSING_STEP_GAP]
    assert len(gap_steps) == 1
    assert gap_steps[0].is_in_recommended_path is False

    variation = get_cached_ground_truth("demo_variation")
    assert variation is not None
    assert variation.final_success_achieved is True
    # Silent action detected in variation
    silent_steps = [s for s in variation.steps if s.step_type == StepType.SILENT_ACTION]
    assert len(silent_steps) >= 1

def test_video_frame_extraction():
    video_path = SAMPLE_DIR / "demo_base.mp4"
    assert video_path.exists()
    
    duration = get_video_duration(video_path)
    assert 50.0 <= duration <= 60.0

    # Extract frame at 7.0s
    url = extract_frame_at_timestamp(video_path, 7.0, "test_extract_frame.jpg")
    assert url is not None
    assert url.startswith("/static/frames/")
    
    saved_file = Path("D:/HowTo/backend/static/frames/test_extract_frame.jpg")
    assert saved_file.exists()
    assert saved_file.stat().st_size > 1000  # Non-empty valid image
