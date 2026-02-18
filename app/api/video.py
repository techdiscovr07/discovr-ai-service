"""
Video Review AI API endpoints
"""
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.video_ai import video_ai

router = APIRouter()


class VideoReviewRequest(BaseModel):
    video_url: str
    campaign_brief: Dict
    script_content: Optional[str] = None


@router.post("/review")
async def review_video(request: VideoReviewRequest):
    """Review creator video and provide comprehensive analysis"""
    try:
        result = await video_ai.review_video(
            video_url=request.video_url,
            campaign_brief=request.campaign_brief,
            script_content=request.script_content,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
