"""
Video processing utilities
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from moviepy.editor import VideoFileClip

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
            clip = VideoFileClip(video_path)
            duration = clip.duration
            
            if duration > self.max_duration:
                raise ValueError(f"Video exceeds max duration of {self.max_duration}s")
            
            # Extract frames at intervals
            frame_times = [duration * i / (num_frames + 1) for i in range(1, num_frames + 1)]
            frames = []
            
            for t in frame_times:
                frame = clip.get_frame(t)
                # Save frame as image (for vision model analysis)
                frame_path = self.temp_dir / f"frame_{t:.1f}.jpg"
                # Use PIL or opencv to save frame
                frames.append(str(frame_path))
            
            clip.close()
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
            clip = VideoFileClip(video_path)
            metadata = {
                "duration": clip.duration,
                "fps": clip.fps,
                "width": clip.w,
                "height": clip.h,
                "size": os.path.getsize(video_path),
            }
            clip.close()
            return metadata
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}
