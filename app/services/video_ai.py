"""
Video Review AI Service
"""
import os
from typing import Dict, Optional

from app.services.llm_service import llm_service
from app.utils.prompt_templates import VIDEO_REVIEW_PROMPT
from app.utils.video_processor import VideoProcessor


class VideoAI:
    """AI service for video review and analysis"""
    
    def __init__(self):
        self.video_processor = VideoProcessor()
    
    async def review_video(
        self,
        video_url: str,
        campaign_brief: Dict,
        script_content: Optional[str] = None,
    ) -> Dict:
        """
        Review creator video and provide comprehensive analysis
        
        Returns:
            {
                "overall_score": 0.88,
                "visual_quality": 0.9,
                "audio_quality": 0.85,
                "brand_alignment": 0.9,
                "compliance": 0.85,
                "engagement": 0.87,
                "transcript": "...",
                "timeline_analysis": [
                    {"timestamp": "0:05", "type": "issue", "description": "...", "suggestion": "..."}
                ],
                "key_moments": [...],
                "feedback": "..."
            }
        """
        # Download and process video
        video_path = await self.video_processor.download_video(video_url)
        
        try:
            # Extract frames, audio, transcript
            frames = await self.video_processor.extract_key_frames(video_path)
            audio_transcript = await self.video_processor.extract_transcript(video_path)
            video_metadata = await self.video_processor.get_metadata(video_path)
            
            # Prepare analysis prompt
            prompt = VIDEO_REVIEW_PROMPT.format(
                campaign_name=campaign_brief.get("name", ""),
                campaign_description=campaign_brief.get("description", ""),
                video_title=campaign_brief.get("video_title", ""),
                primary_focus=campaign_brief.get("primary_focus", ""),
                dos=campaign_brief.get("dos", ""),
                donts=campaign_brief.get("donts", ""),
                script_content=script_content or "Not provided",
                transcript=audio_transcript or "Could not extract transcript",
                video_duration=video_metadata.get("duration", 0),
                video_resolution=f"{video_metadata.get('width', 0)}x{video_metadata.get('height', 0)}",
            )
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert video content reviewer. Analyze videos for visual quality, audio quality, brand alignment, compliance, and engagement. Provide specific feedback with timestamps.",
                },
                {"role": "user", "content": prompt},
            ]
            
            # For video analysis, we might want to use vision-capable models
            # If using GPT-4 Vision or similar, include frame descriptions
            if frames:
                frame_descriptions = await self._describe_frames(frames)
                prompt += f"\n\nKey Frame Descriptions:\n{frame_descriptions}"
            
            json_schema = {
                "type": "object",
                "properties": {
                    "overall_score": {"type": "number"},
                    "visual_quality": {"type": "number"},
                    "audio_quality": {"type": "number"},
                    "brand_alignment": {"type": "number"},
                    "compliance": {"type": "number"},
                    "engagement": {"type": "number"},
                    "transcript": {"type": "string"},
                    "timeline_analysis": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "type": {"type": "string", "enum": ["issue", "strength", "suggestion"]},
                                "description": {"type": "string"},
                                "suggestion": {"type": "string"},
                                "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                            },
                        },
                    },
                    "key_moments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "description": {"type": "string"},
                                "significance": {"type": "string"},
                            },
                        },
                    },
                    "feedback": {"type": "string"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["overall_score", "visual_quality", "audio_quality", "brand_alignment", "compliance"],
            }
            
            result = await llm_service.chat_completion_json(
                messages=messages,
                json_schema=json_schema,
                temperature=0.3,
            )
            
            # Add video metadata
            result["video_metadata"] = video_metadata
            
            return result
            
        finally:
            # Cleanup downloaded video
            if os.path.exists(video_path):
                os.remove(video_path)
    
    async def _describe_frames(self, frames: list) -> str:
        """Describe extracted frames (can use vision model if available)"""
        # For now, return placeholder
        # In production, use GPT-4 Vision or similar to describe frames
        return "Frame analysis available"


video_ai = VideoAI()
