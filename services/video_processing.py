import cv2
import tempfile
import os
import subprocess
from PIL import Image

def extract_frames_and_audio(video_path, num_segments=60, audio_segment_duration=1.0):
    """
    Extract frames and corresponding audio segments from a video file, aligned with a specified number of segments.
    
    Args:
        video_path (str): Path to the video file.
        num_segments (int): Number of frames to extract (default: 60).
        audio_segment_duration (float): Duration of audio segment around each frame in seconds (default: 1.0).
        
    Returns:
        tuple: (List of PIL Image objects, list of audio segment file paths, list of timestamps).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    if duration <= 0:
        cap.release()
        return [], [], []

    # Calculate frame interval to match num_segments
    frame_interval = max(1, total_frames // num_segments) if num_segments > 0 else 1
    frames = []
    audio_segments = []
    timestamps = []
    frame_count = 0
    target_frames = set([i * frame_interval for i in range(num_segments)])

    # FFmpeg executable path (modify for your system)
    ffmpeg_path = "ffmpeg"  # Assumes ffmpeg is in PATH
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory for audio segments

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        if frame_count in target_frames:
            # Calculate timestamp for this frame
            timestamp = frame_count / fps if fps > 0 else 0
            timestamps.append(round(timestamp, 3))

            # Convert frame (OpenCV BGR) to PIL Image (RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)

            # Extract audio segment centered around the frame's timestamp
            start_time = max(0, timestamp - audio_segment_duration / 2)
            audio_segment_path = os.path.join(temp_dir, f"audio_segment_{len(frames)}.wav")
            command = [
                ffmpeg_path, "-i", video_path,
                "-ss", str(start_time),  # Start time
                "-t", str(audio_segment_duration),  # Duration of audio segment
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
                "-ar", "16000",  # Sampling rate (AST model expects 16kHz)
                "-ac", "1",  # Mono
                "-loglevel", "error",  # Suppress FFmpeg output except errors
                audio_segment_path,
                "-y"  # Overwrite output file if it exists
            ]

            try:
                subprocess.run(command, check=True, text=True, capture_output=True)
                audio_segments.append(audio_segment_path)
            except subprocess.CalledProcessError as e:
                audio_segments.append(None)  # Append None if audio extraction fails
                print(f"Warning: Failed to extract audio segment at {timestamp}s: {e.stderr}")

            if len(frames) >= num_segments:
                break

        frame_count += 1

    cap.release()
    return frames, audio_segments, timestamps