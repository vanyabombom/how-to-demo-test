import os
import subprocess
import json
import base64
import re
from pathlib import Path
from typing import List, Tuple, Optional
import imageio_ffmpeg
from app.config import FRAMES_DIR

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

def get_video_duration(video_path: Path) -> float:
    """Extract duration in seconds using ffmpeg output header."""
    try:
        cmd = [ffmpeg_exe, "-i", str(video_path)]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", result.stderr)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except Exception as e:
        print(f"Error reading duration: {e}")
    return 60.0  # Fallback assumption

def extract_frame_at_timestamp(
    video_path: Path, 
    timestamp_sec: float, 
    output_filename: str
) -> Optional[str]:
    """
    Extracts a high quality screenshot at exact timestamp and saves to static/frames.
    Returns relative URL path: /static/frames/<output_filename>
    """
    output_path = FRAMES_DIR / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    duration = get_video_duration(video_path)
    safe_sec = max(0.0, min(timestamp_sec, max(0.0, duration - 0.1))) if duration > 0 else max(0.0, timestamp_sec)

    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(safe_sec),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if output_path.exists() and output_path.stat().st_size > 0:
            return f"/static/frames/{output_filename}"
    except Exception as e:
        print(f"Failed to extract frame at {timestamp_sec}s: {e}")
    return None

def extract_keyframe_samples(
    video_path: Path, 
    sample_interval_sec: float = 3.0,
    max_frames: int = 24
) -> List[Tuple[float, str]]:
    """
    Extracts a list of (timestamp_sec, base64_jpeg_data) for feeding vision LLMs.
    """
    duration = get_video_duration(video_path)
    if duration <= 0:
        duration = 30.0

    # Determine timestamps
    count = min(max_frames, max(4, int(duration // sample_interval_sec)))
    interval = duration / count
    timestamps = [round(i * interval, 2) for i in range(count)]
    
    frames_data: List[Tuple[float, str]] = []
    
    for t in timestamps:
        temp_img = FRAMES_DIR / f"temp_sample_{os.getpid()}_{t:.1f}.jpg"
        cmd = [
            ffmpeg_exe,
            "-y",
            "-ss", str(t),
            "-i", str(video_path),
            "-vframes", "1",
            "-vf", "scale='min(1024,iw)':-1", # Max 1024px width for efficient tokens
            "-q:v", "3",
            str(temp_img)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if temp_img.exists():
                with open(temp_img, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                frames_data.append((t, f"data:image/jpeg;base64,{b64}"))
                temp_img.unlink(missing_ok=True)
        except Exception as e:
            print(f"Error sampling frame at {t}s: {e}")
            if temp_img.exists():
                temp_img.unlink(missing_ok=True)

    return frames_data
