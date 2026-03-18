"""
Campaign AI API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.campaign_ai import CampaignAI, analyze_campaign_async

router = APIRouter()
campaign_service = CampaignAI()


class CampaignCore(BaseModel):
    objective: str = Field(description="Primary Objective (Sales/Installs/Leads/Awareness/Launch)")
    target_kpi: Optional[str] = None
    target_cpa: Optional[str] = None
    duration: Optional[str] = None
    total_budget: Optional[str] = None

class BrandContext(BaseModel):
    brand_name: str
    product_name: str
    category: Optional[str] = None
    price_point: Optional[str] = None
    usp: List[str] = []
    why_buy_instead_of_competitors: Optional[str] = None
    top_competitors: List[str] = []
    website: Optional[str] = None
    brand_stage: Optional[str] = None

class TargetAudience(BaseModel):
    age_range: Optional[str] = None
    gender_split: Optional[str] = None
    geography: Optional[str] = None
    language: Optional[str] = None
    interests: List[str] = []
    aspirations: List[str] = []
    pain_points: List[str] = []
    content_consumed: List[str] = []
    spending_power: Optional[str] = None

class FunnelStage(BaseModel):
    stage: str = Field(description="Cold acquisition, Consideration, Retargeting, Launch hype, Always-on")

class PlatformRules(BaseModel):
    allowed_platforms: List[str] = []
    allowed_formats: List[str] = []
    whitelisting_allowed: Optional[bool] = None
    paid_amplification_budget: Optional[str] = None

class CreatorConstraints(BaseModel):
    preferred_tiers: List[str] = []
    regional_creators_needed: Optional[str] = None
    excluded_categories: List[str] = []
    mandatory_creators: List[str] = []

class BrandGuardrails(BaseModel):
    tone: Optional[str] = None
    claims_allowed: Optional[str] = None
    words_to_avoid: List[str] = []
    legal_restrictions: Optional[str] = None
    mandatory_cta: Optional[str] = None
    coupon_codes_available: Optional[bool] = None

class TrackingInfrastructure(BaseModel):
    pixel_installed: Optional[bool] = None
    utm_tracking: Optional[bool] = None
    coupon_tracking: Optional[bool] = None
    affiliate_tracking: Optional[bool] = None
    reporting_frequency: Optional[str] = None


class ComprehensiveCampaignBrief(BaseModel):
    core: CampaignCore
    brand: BrandContext
    audience: TargetAudience
    funnel: FunnelStage
    platforms: PlatformRules
    creators: CreatorConstraints
    guardrails: BrandGuardrails
    tracking: TrackingInfrastructure
    target_language: Optional[str] = "English"
    currency: Optional[str] = "USD"


class CampaignRequest(BaseModel):
    campaign_name: str
    description: str
    target_audience: str
    goals: str
    brand_name: str
    target_language: str = "English"
    target_platforms: List[str] = ["Instagram Reels"]
    cultural_context: Optional[str] = None


@router.post("/chat")
async def generate_strategy(request: ComprehensiveCampaignBrief):
    """Instantly generates an agency-grade Influencer Strategy Playbook from 9-part brief"""
    try:
        # Convert the massive Pydantic object into a clean dictionary
        brief_data = request.model_dump()
        
        # Serialize the structured brief into a single comprehensive system prompt
        target_lang = request.target_language or "English"
        currency = request.currency or "USD"
        context = (
            f"Here is the comprehensive 9-part campaign brief from the client:\n\n{brief_data}\n\n"
            f"CRITICAL: The client has requested all 5 scripts in the `scripts` array to be written NATIVELY in: **{target_lang}**. "
            f"Do NOT generate scripts in any other language. Apply appropriate cultural nuance for this language/market.\n"
            f"CURRENCY: All monetary values in the strategy (budgets, CPAs, CPCs, earnings estimates) MUST be expressed in **{currency}**."
        )

        dict_messages = [{"role": "user", "content": context}]

        response = await campaign_service.chat_stream(
            messages=dict_messages
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_campaign(request: CampaignRequest):
    """Analyze campaign in background"""
    try:
        task = analyze_campaign_async.delay(
            campaign_name=request.campaign_name,
            description=request.description,
            target_audience=request.target_audience,
            goals=request.goals,
            brand_name=request.brand_name,
            target_language=request.target_language,
            target_platforms=request.target_platforms,
            cultural_context=request.cultural_context,
        )
        return {"task_id": task.id, "status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
