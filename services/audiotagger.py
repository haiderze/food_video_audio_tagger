import cv2
import transformers
from transformers import pipeline

# Check transformers version
required_version = "4.44.2"
if transformers.__version__ < required_version:
    raise ImportError(f"Transformers version {transformers.__version__} is outdated. Please upgrade to {required_version} or higher using `pip install --upgrade transformers`.")

# Load model once (singleton to avoid reloading)
try:
    audio_classifier = pipeline(
        "audio-classification",
        model="MIT/ast-finetuned-audioset-16-16-0.442",
        chunk_length_s=1,  # Process 1-second chunks
        top_k=5  # Return top 5 labels per segment
    )
except Exception as e:
    raise RuntimeError(f"Failed to load audio classification model: {e}")

def get_video_duration(video_path):
    """
    Get the duration of a video using OpenCV.
    
    Args:
        video_path (str): Path to the video file.
        
    Returns:
        float: Duration in seconds.
        
    Raises:
        RuntimeError: If video cannot be opened.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video for duration check: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    return total_frames / fps if fps > 0 else 0