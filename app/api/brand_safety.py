"""
Brand Safety AI API endpoints
"""

from typing import Dict, Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.brand_safety_ai import evaluate_brand_safety_async
from app.services.creator_audit_ai import evaluate_creator_audit_async

router = APIRouter()


class BrandSafetyRequest(BaseModel):
    campaign_brief: Dict
    script_text: str
    post_caption: str
    influencer_profile: Dict
    brand_policies: Dict
    target_platforms: List[str] = ["Instagram", "YouTube"]
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


@router.post("/review")
async def evaluate_brand_safety(request: BrandSafetyRequest):
    """Evaluate creator content against brand safety guidelines in background"""
    try:
        task = evaluate_brand_safety_async.delay(
            campaign_brief=request.campaign_brief,
            script_text=request.script_text,
            post_caption=request.post_caption,
            influencer_profile=request.influencer_profile,
            brand_policies=request.brand_policies,
            target_platforms=request.target_platforms,
            video_url=request.video_url,
            thumbnail_url=request.thumbnail_url,
        )
        return {"task_id": task.id, "status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreatorAuditRequest(BaseModel):
    instagram_handle: Optional[str] = None
    youtube_handle: Optional[str] = None
    brand_policies: Optional[Dict] = None

@router.post("/audit-creator")
async def evaluate_creator_audit(request: CreatorAuditRequest):
    """Deep scan of creator history"""
    try:
        task = evaluate_creator_audit_async.delay(
            instagram_handle=request.instagram_handle,
            youtube_handle=request.youtube_handle,
            brand_policies=request.brand_policies,
        )
        return {"task_id": task.id, "status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
