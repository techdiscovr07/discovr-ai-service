"""
Video Review AI API endpoints
"""
import os
import shutil
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from pydantic import BaseModel

from app.services.video_ai import review_video_async

router = APIRouter()


class VideoReviewRequest(BaseModel):
    video_url: str
    campaign_brief: Dict
    script_content: Optional[str] = None
    target_language: Optional[str] = ""
    target_platforms: Optional[list] = []
    cultural_context: Optional[str] = ""


@router.post("/review")
async def review_video(request: VideoReviewRequest):
    """Review creator video from URL and provide comprehensive analysis via Celery"""
    try:
        # Inject top-level props into the brief for prompt formatting
        brief = request.campaign_brief.copy()
        brief.setdefault("target_language", request.target_language)
        brief.setdefault("target_platforms", request.target_platforms)
        brief.setdefault("cultural_context", request.cultural_context)

        task = review_video_async.delay(
            video_url=request.video_url,
            campaign_brief=brief,
            script_content=request.script_content,
        )
        return {"task_id": task.id, "status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_video(
    video: UploadFile = File(...),
    campaign_name: Optional[str] = Form(""),
    description: Optional[str] = Form(""),
    video_title: Optional[str] = Form(""),
    primary_focus: Optional[str] = Form(""),
    dos: Optional[str] = Form(""),
    donts: Optional[str] = Form(""),
    script_content: Optional[str] = Form(None),
    target_language: Optional[str] = Form(""),
    target_platforms: Optional[str] = Form(""),
    cultural_context: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    brand_guidelines: Optional[str] = Form(None),
    platform_policies: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
):
    """Upload a video file for review via Celery"""
    try:
        # Save temp file
        temp_dir = "/tmp/discovr_videos"
        os.makedirs(temp_dir, exist_ok=True)
        filename = video.filename if video.filename else "upload.mp4"
        temp_path = os.path.join(temp_dir, f"{os.urandom(8).hex()}_{filename}")
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        campaign_brief = {
            "name": campaign_name,
            "description": description,
            "video_title": video_title,
            "primary_focus": primary_focus,
            "dos": dos,
            "donts": donts,
            "script_content": script_content,
            "target_language": target_language,
            "target_platforms": target_platforms,
            "cultural_context": cultural_context,
        }

        task = review_video_async.delay(
            video_url=temp_path,  # Use absolute local path
            campaign_brief=campaign_brief,
            script_content=script_content,
        )
        return {"task_id": task.id, "file_path": temp_path, "status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
