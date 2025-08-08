import os
import shutil
from flask import request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_restx import Namespace, Resource, fields
from services.video_processing import extract_frames_and_audio
from flask_restx import reqparse
from services.visualtagger import tag_frames
from services.audiotagger import audio_classifier, get_video_duration
import tempfile

api = Namespace("process", description="Video processing routes")

upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    'video',
    location='files',
    type=FileStorage,  
    required=True,
    help='The food video file to upload'
)

@api.route("/")
class ProcessVideo(Resource):
    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        video = args['video']

        if not video:
            return {"error": "No video provided"}, 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            video.save(tmp_file.name)
            video_path = tmp_file.name

        # Get video duration to determine number of segments
        duration = get_video_duration(video_path)
        # Use 1 frame per second as a reasonable default (adjustable)
        num_segments = max(1, int(duration))  # At least 1 segment
        # num_segments = 5

        # Extract frames, audio segments, and timestamps
        frames, audio_segments, timestamps = extract_frames_and_audio(video_path, num_segments=num_segments, audio_segment_duration=1.0)

        # Tag frames
        captions = tag_frames(frames)
        tagged_frames = [
            {"index": idx, "caption": caption, "timestamp": timestamps[idx]}
            for idx, caption in enumerate(captions)
        ]

        # Audio tagging for each segment
        audio_tags = []
        for idx, audio_segment_path in enumerate(audio_segments):
            if audio_segment_path and os.path.exists(audio_segment_path):
                try:
                    segment_results = audio_classifier(audio_segment_path)
                    segment_results = sorted(segment_results, key=lambda x: x['score'], reverse=True)[:5] 
                    audio_tags.append({"index": idx, "tags": segment_results, "timestamp": timestamps[idx]})
                except Exception as e:
                    audio_tags.append({"index": idx, "tags": [], "timestamp": timestamps[idx], "error": str(e)})
            else:
                audio_tags.append({"index": idx, "tags": [], "timestamp": timestamps[idx], "error": "No audio segment extracted"})

        # Combine results, ensuring alignment
        combined_results = [
            {
                "index": idx,
                "frame": tagged_frames[idx] if idx < len(tagged_frames) else {"caption": None, "timestamp": timestamps[idx]},
                "audio": audio_tags[idx] if idx < len(audio_tags) else {"tags": [], "timestamp": timestamps[idx]}
            }
            for idx in range(max(len(tagged_frames), len(audio_tags)))
        ]

        # Clean up temporary files
        temp_dir = os.path.dirname(audio_segments[0]) if audio_segments else None
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)  # Remove the temporary directory and all audio segments
        if os.path.exists(video_path):
            os.remove(video_path)

        return jsonify({
            "message": f"{len(frames)} frames tagged, {len(audio_tags)} audio segments classified",
            "results": combined_results
        })