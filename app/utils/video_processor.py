"""
Video processing utilities
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from app.config import settings


class VideoProcessor:
    """Utility for processing videos"""
    
    def __init__(self):
        self.temp_dir = Path(settings.video_temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.max_duration = settings.max_video_duration_seconds
    
    async def download_video(self, video_url: str) -> str:
        """Download video from URL to temp file"""
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()
            
            # Determine file extension from URL or content-type
            ext = ".mp4"  # Default
            if ".mp4" in video_url:
                ext = ".mp4"
            elif ".mov" in video_url:
                ext = ".mov"
            
            temp_path = self.temp_dir / f"video_{os.urandom(8).hex()}{ext}"
            temp_path.write_bytes(response.content)
            
            return str(temp_path)
    
    async def extract_key_frames(self, video_path: str, num_frames: int = 5) -> List[str]:
        """Extract key frames from video"""
        try:
            metadata = await self.get_metadata(video_path)
            duration = float(metadata.get("duration", 0))
            if duration > self.max_duration:
                raise ValueError(f"Video exceeds max duration of {self.max_duration}s")
            if duration <= 0:
                return []

            # Extract frames at intervals
            frame_times = [duration * i / (num_frames + 1) for i in range(1, num_frames + 1)]
            frames = []

            for t in frame_times:
                frame_path = self.temp_dir / f"frame_{t:.1f}.jpg"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-ss", str(t),
                        "-i", video_path,
                        "-frames:v", "1",
                        "-q:v", "2",
                        "-y",
                        str(frame_path),
                    ],
                    check=True,
                    capture_output=True,
                )
                if frame_path.exists():
                    frames.append(str(frame_path))

            return frames
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []
    
    async def extract_transcript(self, video_path: str) -> Optional[str]:
        """Extract audio transcript from video"""
        try:
            # Extract audio
            audio_path = self.temp_dir / f"audio_{os.urandom(8).hex()}.wav"
            
            # Use ffmpeg to extract audio
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", video_path,
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(audio_path),
                ],
                check=True,
                capture_output=True,
            )
            
            # Use Whisper API or local Whisper for transcription
            # For now, return None (implement with OpenAI Whisper API or local model)
            return None
            
        except Exception as e:
            print(f"Error extracting transcript: {e}")
            return None
    
    async def get_metadata(self, video_path: str) -> Dict:
        """Get video metadata"""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-print_format", "json",
                    "-show_streams",
                    "-show_format",
                    video_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            info = json.loads(result.stdout or "{}")
            video_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
                {},
            )
            return {
                "duration": float(info.get("format", {}).get("duration", 0) or 0),
                "fps": video_stream.get("r_frame_rate", "0/1"),
                "width": int(video_stream.get("width", 0) or 0),
                "height": int(video_stream.get("height", 0) or 0),
                "size": os.path.getsize(video_path),
            }
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}
