"""
Campaign AI API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.campaign_ai import campaign_ai

router = APIRouter()


class CampaignAnalysisRequest(BaseModel):
    campaign_name: str
    description: str
    target_audience: str
    goals: str
    brand_name: str | None = None


@router.post("/analyze")
async def analyze_campaign(request: CampaignAnalysisRequest):
    """Analyze campaign brief and provide AI suggestions"""
    try:
        result = await campaign_ai.analyze_campaign(
            campaign_name=request.campaign_name,
            description=request.description,
            target_audience=request.target_audience,
            goals=request.goals,
            brand_name=request.brand_name,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
