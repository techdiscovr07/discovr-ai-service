"""
Script Review AI API endpoints
"""
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.script_ai import script_ai

router = APIRouter()


class ScriptReviewRequest(BaseModel):
    script_content: str
    campaign_brief: Dict
    brand_guidelines: Optional[str] = None


@router.post("/review")
async def review_script(request: ScriptReviewRequest):
    """Review creator script and provide detailed feedback"""
    try:
        result = await script_ai.review_script(
            script_content=request.script_content,
            campaign_brief=request.campaign_brief,
            brand_guidelines=request.brand_guidelines,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
