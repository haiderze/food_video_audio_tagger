# Food Video Audio Tagger

A Flask-based application for tagging food-related videos by analyzing both visual frames and audio segments. The application extracts frames and audio from uploaded videos, generates captions for frames using a vision model, and classifies audio segments using an audio classification model. The results are combined into a structured JSON output, aligning visual and audio tags by timestamp.

## Features

- **Video Frame Extraction**: Extracts evenly spaced frames from a video based on its duration.
- **Image Captioning**: Uses the Salesforce BLIP model to generate captions for extracted frames.
- **Audio Segmentation and Classification**: Extracts short audio segments aligned with frames and classifies them using the MIT AST model.
- **REST API**: Provides an endpoint to upload videos and receive tagged results.
- **Docker Support**: Includes a Dockerfile for easy deployment.

## Requirements

- Python 3.10
- FFmpeg (for audio extraction)
- System dependencies: `libsm6`, `libxext6`, `libxrender1`, `libglib2.0-0`, `libjpeg-dev`, `zlib1g-dev`, `libsndfile1`
- Python dependencies listed in `requirements.txt`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/haiderze/food_video_audio_tagger.git
   cd food_video_audio_tagger
   ```

2. **Install System Dependencies** (for local development):
   ```bash
   sudo apt-get update
   sudo apt-get install -y ffmpeg libsm6 libxext6 libxrender1 libglib2.0-0 libjpeg-dev zlib1g-dev libsndfile1
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application Locally**:
   ```bash
   gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 300 --access-logfile -
   ```

## Docker Setup

1. **Build the Docker Image**:
   ```bash
   docker build -t food-video-audio-tagger .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8000:8000 food-video-audio-tagger
   ```

## Usage

### API Endpoint
- **POST /api/process**
  - **Content-Type**: `multipart/form-data`
  - **Parameter**: `video` (video file, e.g., `.mp4`)
  - **Response**: JSON object containing tagged frames and audio segments.

  **Example Request** (using `curl`):
  ```bash
  curl -X POST -F "video=@/path/to/your/video.mp4" http://localhost:8000/api/process
  ```

  **Example Response**:
  ```json
  {
    "message": "10 frames tagged, 10 audio segments classified",
    "results": [
      {
        "index": 0,
        "frame": {
          "index": 0,
          "caption": "A plate of pasta with tomato sauce",
          "timestamp": 0.0
        },
        "audio": {
          "index": 0,
          "tags": [
            {"label": "cooking", "score": 0.85},
            {"label": "speech", "score": 0.10}
          ],
          "timestamp": 0.0
        }
      },
      ...
    ]
  }
  ```

### How It Works
1. Upload a video file to the `/api/process` endpoint.
2. The application extracts frames (default: 1 frame per second of video) and corresponding 1-second audio segments.
3. Frames are captioned using the Salesforce BLIP model (`Salesforce/blip-image-captioning-base`).
4. Audio segments are classified using the MIT AST model (`MIT/ast-finetuned-audioset-16-16-0.442`).
5. Results are aligned by timestamp and returned in a structured JSON format.
6. Temporary files (video and audio segments) are cleaned up after processing.

## Project Structure

- `app.py`: Main Flask application and API setup.
- `video_processing.py`: Handles frame and audio extraction using OpenCV and FFmpeg.
- `visualtagger.py`: Generates captions for frames using the BLIP model.
- `audiotagger.py`: Classifies audio segments using the AST model.
- `process.py`: Defines the API endpoint and orchestrates video processing.
- `Dockerfile`: Docker configuration for building and running the application.
- `requirements.txt`: Python dependencies.

## Dependencies

- **Flask**: Web framework for the API.
- **Flask-RESTX**: For building and documenting the REST API.
- **OpenCV**: For video frame extraction.
- **Pillow**: For image processing.
- **Transformers**: For BLIP and AST models.
- **FFmpeg**: For audio extraction.
- **NumPy, Torch, Torchaudio, Librosa, Datasets**: For audio and model processing.

## Notes

- The application assumes FFmpeg is installed and accessible in the system PATH.
- Temporary files are stored in a temporary directory and cleaned up after processing.
- The number of frames extracted is based on video duration (1 frame per second by default).
- Audio segments are 1-second clips centered around each frame’s timestamp.
- The BLIP and AST models are loaded once at startup to optimize performance.

## Limitations

- The application is optimized for food-related videos but can process any video.
- Large videos may require significant memory and processing time.
- Audio classification is limited to the labels provided by the AST model.
- Ensure sufficient disk space for temporary files during processing.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/haiderze/food_video_audio_tagger).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Footer

© 2025 GitHub, Inc.