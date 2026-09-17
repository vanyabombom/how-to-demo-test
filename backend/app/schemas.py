from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class StepType(str, Enum):
    NORMAL = "normal"
    SILENT_ACTION = "silent_action"          # Necessary visual action not spoken
    CORRECTED_MISTAKE = "corrected_mistake"  # Mistake demonstrator corrected; prune from path
    MISSING_STEP_GAP = "missing_step_gap"    # Video skipped a critical step

class GuideStep(BaseModel):
    step_number: int = Field(description="Sequential order in the recommended path")
    title: str = Field(description="Concise imperative step title, e.g. 'Select Date Range'")
    instruction: str = Field(description="Clear explanation of how to perform this step")
    timestamp_start: str = Field(description="Start time format MM:SS")
    timestamp_end: str = Field(description="End time format MM:SS")
    timestamp_keyframe_sec: float = Field(description="Exact second in video to extract thumbnail screenshot")
    step_type: StepType = Field(default=StepType.NORMAL)
    is_in_recommended_path: bool = Field(
        default=True, 
        description="True if step is part of ideal path; False if it was an abandoned mistake"
    )
    chosen_setting: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Final selected parameter/filter value"
    )
    evidence_description: str = Field(
        default="", 
        description="Visual confirmation or visible UI state proving this step occurred"
    )
    warning_or_gap_note: Optional[str] = Field(
        default=None, 
        description="Warning note if video jumped or skipped context"
    )
    screenshot_url: Optional[str] = Field(
        default=None, 
        description="URL to the extracted screenshot frame"
    )

class HowToAnalysisResult(BaseModel):
    guide_title: str = Field(description="Clear title of the how-to guide")
    target_operation: str = Field(description="Specific operation demonstrated")
    app_detected: str = Field(description="Name or type of web application")
    final_success_achieved: bool = Field(
        description="Whether the recording clearly showed the completed success state"
    )
    final_success_evidence: Optional[str] = Field(
        default=None, 
        description="Visual evidence of success (e.g. downloaded file bar, toast message)"
    )
    declined_to_conclude: bool = Field(
        default=False, 
        description="True if recording jumped critical step or terminated without success"
    )
    decline_reason: Optional[str] = Field(
        default=None, 
        description="Explanation when declining or asking for clarification"
    )
    steps: List[GuideStep] = Field(default_factory=list)
    abandoned_mistakes: List[str] = Field(
        default_factory=list, 
        description="List of mistaken actions made and corrected by demonstrator"
    )
    final_settings_summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Dictionary of all finalized settings used in successful run"
    )
    processing_time_sec: float = Field(default=0.0)
    variable_cost_usd: float = Field(default=0.0)
    token_usage: Dict[str, int] = Field(
        default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )
    model_name: str = Field(default="unknown")
    source_mode: str = Field(
        default="offline_ground_truth",
        description="'offline_ground_truth' or 'live_ai_inference'"
    )

class SampleInfo(BaseModel):
    id: str
    title: str
    description: str
    scenario_type: str  # "normal", "corrected_mistake", "incomplete_gap"
    video_url: str
    has_cached_result: bool

class ConfigResponse(BaseModel):
    api_provider: str
    base_url: str
    model_name: str
    has_api_key: bool
    masked_key: str

class UpdateConfigRequest(BaseModel):
    api_provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
