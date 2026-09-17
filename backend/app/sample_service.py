import json
from pathlib import Path
from typing import Dict, List, Optional
from app.schemas import HowToAnalysisResult, GuideStep, StepType, SampleInfo
from app.config import SAMPLE_DIR

GROUND_TRUTH_DATA: Dict[str, Dict] = {
    "demo_base": {
        "guide_title": "How to Create a GitHub Issue with Label and Assignee",
        "target_operation": "Creating a GitHub Issue with Labels and Assignee",
        "app_detected": "GitHub (how-to-demo-test repository)",
        "final_success_achieved": True,
        "final_success_evidence": "GitHub Issue #2 'Fix navbar overflow' opened and displayed successfully",
        "declined_to_conclude": False,
        "decline_reason": None,
        "steps": [
            {
                "step_number": 1,
                "title": "Open Issues Tab",
                "instruction": "Navigate to the repository and click the 'Issues' tab in the top navigation bar.",
                "timestamp_start": "00:01",
                "timestamp_end": "00:05",
                "timestamp_keyframe_sec": 3.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"View": "Issues Tab"},
                "evidence_description": "Repository Issues list view loaded",
                "warning_or_gap_note": None
            },
            {
                "step_number": 2,
                "title": "Click 'New issue'",
                "instruction": "Click the green 'New issue' button in the upper right to open the issue creation form.",
                "timestamp_start": "00:05",
                "timestamp_end": "00:09",
                "timestamp_keyframe_sec": 7.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Action": "Create Issue"},
                "evidence_description": "'Create new issue' editor page opened",
                "warning_or_gap_note": None
            },
            {
                "step_number": 3,
                "title": "Enter Issue Title",
                "instruction": "Enter 'Fix navbar overflow' into the 'Add a title' input field.",
                "timestamp_start": "00:09",
                "timestamp_end": "00:23",
                "timestamp_keyframe_sec": 21.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Title": "Fix navbar overflow"},
                "evidence_description": "Title field filled with 'Fix navbar overflow'",
                "warning_or_gap_note": None
            },
            {
                "step_number": 4,
                "title": "Assign 'bug' Label",
                "instruction": "Open the 'Labels' section on the right sidebar and check the 'bug' label.",
                "timestamp_start": "00:23",
                "timestamp_end": "00:35",
                "timestamp_keyframe_sec": 27.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Label": "bug"},
                "evidence_description": "Labels popup open with 'bug' checkbox checked",
                "warning_or_gap_note": None
            },
            {
                "step_number": 5,
                "title": "Assign to 'vanyabombom'",
                "instruction": "Open the 'Assignees' section on the right sidebar and select 'vanyabombom'.",
                "timestamp_start": "00:35",
                "timestamp_end": "00:46",
                "timestamp_keyframe_sec": 39.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Assignee": "vanyabombom"},
                "evidence_description": "Assignee 'vanyabombom' selected and badge added",
                "warning_or_gap_note": None
            },
            {
                "step_number": 6,
                "title": "Submit Issue",
                "instruction": "Click the blue 'Create' button to finalize and publish the issue.",
                "timestamp_start": "00:46",
                "timestamp_end": "00:54",
                "timestamp_keyframe_sec": 53.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Action": "Confirm Submission"},
                "evidence_description": "Redirected to published Issue #2 'Fix navbar overflow #2' with 'Open' badge",
                "warning_or_gap_note": None
            }
        ],
        "abandoned_mistakes": [],
        "final_settings_summary": {
            "Title": "Fix navbar overflow",
            "Labels": "bug",
            "Assignees": "vanyabombom",
            "Status": "Open (#2)"
        },
        "processing_time_sec": 7.9,
        "variable_cost_usd": 0.0035,
        "token_usage": {
            "prompt_tokens": 13200,
            "completion_tokens": 710,
            "total_tokens": 13910
        },
        "model_name": "google/gemini-2.0-flash-exp:free (or Groq/Llama-3.2)"
    },

    "demo_edgecase": {
        "guide_title": "Attempt to Create GitHub Issue without Title (Validation Failure)",
        "target_operation": "Creating a GitHub Issue (Validation Edge Case)",
        "app_detected": "GitHub (how-to-demo-test repository)",
        "final_success_achieved": False,
        "final_success_evidence": None,
        "declined_to_conclude": True,
        "decline_reason": "Submission failed validation: 'Title can not be empty'. Demonstrator attempted to create an issue without filling in the mandatory title field, resulting in an unsubmitted form and no created issue.",
        "steps": [
            {
                "step_number": 1,
                "title": "Navigate to New Issue Page",
                "instruction": "Click 'Issues' tab and click 'New issue' button.",
                "timestamp_start": "00:01",
                "timestamp_end": "00:05",
                "timestamp_keyframe_sec": 3.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Action": "Open Issue Form"},
                "evidence_description": "'Create new issue' page displayed with empty title and description",
                "warning_or_gap_note": None
            },
            {
                "step_number": 2,
                "title": "Enter Description without Title",
                "instruction": "Enter description text 'The layout breeaks on screen width 375px' into the description field, leaving the mandatory Title field empty.",
                "timestamp_start": "00:05",
                "timestamp_end": "00:21",
                "timestamp_keyframe_sec": 18.0,
                "step_type": "silent_action",
                "is_in_recommended_path": True,
                "chosen_setting": {"Description": "The layout breeaks on screen width 375px", "Title": "[Omitted]"},
                "evidence_description": "Description textarea filled, but 'Add a title' input remains blank",
                "warning_or_gap_note": None
            },
            {
                "step_number": 3,
                "title": "VALIDATION FAILURE: Attempt Submission without Mandatory Title",
                "instruction": "Click the 'Create' button. GitHub blocks submission and flags an error warning.",
                "timestamp_start": "00:21",
                "timestamp_end": "00:25",
                "timestamp_keyframe_sec": 24.5,
                "step_type": "missing_step_gap",
                "is_in_recommended_path": False,
                "chosen_setting": None,
                "evidence_description": "Red validation alert 'Title can not be empty' appears beneath the Title field; form is not submitted",
                "warning_or_gap_note": "Validation Error: Title is required by GitHub. Cannot proceed to create an issue without providing a non-empty title."
            }
        ],
        "abandoned_mistakes": [
            "Demonstrator attempted to submit the issue with an empty Title, causing GitHub form validation rejection"
        ],
        "final_settings_summary": {
            "Description": "The layout breeaks on screen width 375px",
            "Title": "MISSING (Required field omitted)",
            "Status": "Failed Validation - Incomplete"
        },
        "processing_time_sec": 5.4,
        "variable_cost_usd": 0.0021,
        "token_usage": {
            "prompt_tokens": 8900,
            "completion_tokens": 420,
            "total_tokens": 9320
        },
        "model_name": "google/gemini-2.0-flash-exp:free (or Groq/Llama-3.2)"
    },

    "demo_variation": {
        "guide_title": "How to Create a GitHub Issue with Enhancement Label and Milestone",
        "target_operation": "Creating a GitHub Issue with Custom Label and Milestone",
        "app_detected": "GitHub (how-to-demo-test repository)",
        "final_success_achieved": True,
        "final_success_evidence": "GitHub Issue #4 'Add dark mode toggle' created successfully with Milestone1 and enhancement badge",
        "declined_to_conclude": False,
        "decline_reason": None,
        "steps": [
            {
                "step_number": 1,
                "title": "Open Issues Tab",
                "instruction": "Click 'Issues' tab and click 'New issue' button.",
                "timestamp_start": "00:01",
                "timestamp_end": "00:06",
                "timestamp_keyframe_sec": 3.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Action": "Open Issue Form"},
                "evidence_description": "'Create new issue' editor page loaded",
                "warning_or_gap_note": None
            },
            {
                "step_number": 2,
                "title": "Enter Title 'Add dark mode toggle'",
                "instruction": "Enter 'Add dark mode toggle' into the 'Add a title' input field.",
                "timestamp_start": "00:06",
                "timestamp_end": "00:20",
                "timestamp_keyframe_sec": 19.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Title": "Add dark mode toggle"},
                "evidence_description": "Title input field contains 'Add dark mode toggle'",
                "warning_or_gap_note": None
            },
            {
                "step_number": 3,
                "title": "Assign 'enhancement' Label",
                "instruction": "Click the Labels gear icon and check the 'enhancement' label checkbox.",
                "timestamp_start": "00:20",
                "timestamp_end": "00:30",
                "timestamp_keyframe_sec": 26.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Label": "enhancement"},
                "evidence_description": "Dropdown shows 'enhancement' label checked and badge attached",
                "warning_or_gap_note": None
            },
            {
                "step_number": 4,
                "title": "Assign Milestone: 'Milestone1'",
                "instruction": "Click the Milestone gear icon on the sidebar and select 'Milestone1'.",
                "timestamp_start": "00:30",
                "timestamp_end": "00:38",
                "timestamp_keyframe_sec": 34.0,
                "step_type": "silent_action",
                "is_in_recommended_path": True,
                "chosen_setting": {"Milestone": "Milestone1"},
                "evidence_description": "Milestone1 selected from the dropdown menu",
                "warning_or_gap_note": None
            },
            {
                "step_number": 5,
                "title": "Submit Issue",
                "instruction": "Click the blue 'Create' button to publish the issue.",
                "timestamp_start": "00:38",
                "timestamp_end": "00:46",
                "timestamp_keyframe_sec": 44.0,
                "step_type": "normal",
                "is_in_recommended_path": True,
                "chosen_setting": {"Action": "Confirm Submission"},
                "evidence_description": "Redirected to Issue #4 'Add dark mode toggle #4' with 'enhancement' and 'Milestone1' metadata badges",
                "warning_or_gap_note": None
            }
        ],
        "abandoned_mistakes": [],
        "final_settings_summary": {
            "Title": "Add dark mode toggle",
            "Labels": "enhancement",
            "Milestone": "Milestone1",
            "Status": "Open (#4)"
        },
        "processing_time_sec": 6.8,
        "variable_cost_usd": 0.0029,
        "token_usage": {
            "prompt_tokens": 11400,
            "completion_tokens": 580,
            "total_tokens": 11980
        },
        "model_name": "google/gemini-2.0-flash-exp:free (or Groq/Llama-3.2)"
    }
}

def get_sample_list() -> List[SampleInfo]:
    """Returns metadata about available samples in sample_data/."""
    samples = [
        SampleInfo(
            id="demo_base",
            title="GitHub Demo 1: Create Issue (Clean Flow)",
            description="Navigates to repo -> creates issue 'Fix navbar overflow' -> adds 'bug' label -> assigns user -> submits.",
            scenario_type="normal",
            video_url="/sample_data/demo_base.mp4",
            has_cached_result=True
        ),
        SampleInfo(
            id="demo_edgecase",
            title="GitHub Demo 2: Missing Title (Validation Edgecase)",
            description="Demonstrator enters description but omits mandatory Title. Form validation rejects submission.",
            scenario_type="incomplete_gap",
            video_url="/sample_data/demo_edgecase.mp4",
            has_cached_result=True
        ),
        SampleInfo(
            id="demo_variation",
            title="GitHub Demo 3: Label & Milestone (Variation)",
            description="Creates issue 'Add dark mode toggle' with 'enhancement' label and 'Milestone1' milestone.",
            scenario_type="normal",
            video_url="/sample_data/demo_variation.mp4",
            has_cached_result=True
        )
    ]
    
    # Dynamically discover any other custom MP4 files in SAMPLE_DIR
    known_ids = {s.id for s in samples}
    if SAMPLE_DIR.exists():
        for file in sorted(SAMPLE_DIR.glob("*.mp4")):
            stem = file.stem
            if stem not in known_ids and not stem.startswith("test_"):
                samples.append(
                    SampleInfo(
                        id=stem,
                        title=f"Custom Video: {stem.replace('_', ' ').title()}",
                        description=f"User dropped video '{file.name}' in sample_data directory.",
                        scenario_type="normal",
                        video_url=f"/sample_data/{file.name}",
                        has_cached_result=stem in GROUND_TRUTH_DATA
                    )
                )
    return samples

def get_cached_ground_truth(sample_id: str) -> Optional[HowToAnalysisResult]:
    clean_id = sample_id.replace(".mp4", "")
    if clean_id in GROUND_TRUTH_DATA:
        return HowToAnalysisResult(**GROUND_TRUTH_DATA[clean_id])
    return None
