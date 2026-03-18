import os
import asyncio
import base64
from typing import Dict, Optional

from app.celery_app import celery_app
from app.services.llm_service import llm_service

class BrandSafetyAI:
    """AI service for deterministic Brand Safety evaluation across text, brand policy, video, platform, and creator risks."""

    async def evaluate_campaign(
        self,
        campaign_brief: Dict,
        script_text: str,
        post_caption: str,
        influencer_profile: Dict,
        brand_policies: Dict,
        target_platforms: list[str] = ["Instagram", "YouTube"],
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
    ) -> Dict:
        """
        Evaluate campaign content against multiple risk vectors to produce a deterministic final score.
        """

        # Prepare images/videos if available
        video_b64 = None
        thumbnail_b64 = None

        if video_url:
            local_path = video_url.replace("file://", "")
            if os.path.exists(local_path):
                with open(local_path, "rb") as video_file:
                    video_b64 = base64.b64encode(video_file.read()).decode("utf-8")

        if thumbnail_url:
            local_thumb_path = thumbnail_url.replace("file://", "")
            if os.path.exists(local_thumb_path):
                with open(local_thumb_path, "rb") as thumb_file:
                    thumbnail_b64 = base64.b64encode(thumb_file.read()).decode("utf-8")

        # System Prompt
        system_prompt = (
            "You are an elite, objective, deterministic, strict, and non-emotional Brand Safety Agent. "
            "Your job is to evaluate campaign content across five distinct risk vectors: "
            "1. Text Content Risk\n"
            "2. Brand Policy Matching\n"
            "3. Video Safety Risk\n"
            "4. Platform Compliance\n"
            "5. Creator Risk\n\n"
            "CRITICAL DIRECTIVES:\n"
            "- You must strictly adhere to the defined risk vectors.\n"
            "- You must be deterministic and objective in your scoring.\n"
            "- Return numeric scores (0-100) for each vector, where 100 means COMPLETELY SAFE (0 Risk) and 0 means MAXIMUM RISK.\n"
            "- Calculate the final_score using this exact formula:\n"
            "  final_score = (text_risk_score * 0.30) + (brand_violation_score * 0.25) + (video_risk_score * 0.20) + (compliance_score * 0.15) + (creator_risk_score * 0.10)\n\n"
            f"--- CAMPAIGN CONTENT ---\n"
            f"Script Text:\n{script_text}\n\n"
            f"Post Caption:\n{post_caption}\n\n"
            f"--- BRAND POLICIES ---\n"
            f"Banned Keywords: {', '.join(brand_policies.get('banned_keywords', []))}\n"
            f"Sensitive Topics: {', '.join(brand_policies.get('sensitive_topics', []))}\n"
            f"Restricted Categories: {', '.join(brand_policies.get('restricted_categories', []))}\n"
            f"Tone Restrictions: {brand_policies.get('tone_restrictions', '')}\n\n"
            f"--- INFLUENCER PROFILE ---\n"
            f"Name: {influencer_profile.get('name', '')}\n"
            f"Volatility Score (0-100, higher is worse): {influencer_profile.get('volatility_score', 0)}\n"
            f"Political Frequency: {influencer_profile.get('political_frequency', 'Low')}\n"
            f"Offensive Content History: {influencer_profile.get('offensive_content_history', 'None')}\n\n"
            f"--- TARGET PLATFORMS ---\n"
            f"{', '.join(target_platforms)}\n"
        )

        user_content = [
            {"type": "text", "text": "Evaluate the provided assets and metadata against the safety criteria and return the exact JSON payload."}
        ]

        if thumbnail_b64:
            user_content.append({"type": "text", "text": "Review this thumbnail preview:"})
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{thumbnail_b64}"}
            })

        if video_b64:
            user_content.append({"type": "text", "text": "Also review this video content:"})
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:video/mp4;base64,{video_b64}"}
            })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        json_schema = {
            "type": "object",
            "properties": {
                "text_risk": {
                    "type": "object",
                    "properties": {
                        "text_risk_score": {"type": "number", "description": "0-100, 100=Safe"},
                        "identified_risks": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "notes": {"type": "string"}
                    },
                    "description": "Evaluation of script_text and post_caption for Hate speech, Religious sensitivity, Political persuasion, Sexual explicitness, Gender discrimination, Violence references, Drugs / alcohol, Gambling, Medical claims, Financial guarantees, Unrealistic income claims, Misleading superlatives, Legal violations."
                },
                "brand_policy": {
                    "type": "object",
                    "properties": {
                        "brand_violation_score": {"type": "number", "description": "0-100, 100=Safe"},
                        "violations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "notes": {"type": "string"}
                    },
                    "description": "Evaluation against banned_keywords, sensitive_topics, restricted_categories, tone_restrictions."
                },
                "video_risk": {
                    "type": "object",
                    "properties": {
                        "video_risk_score": {"type": "number", "description": "0-100, 100=Safe"},
                        "identified_risks": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "notes": {"type": "string"}
                    },
                    "description": "Evaluation of video/visuals for Alcohol visible, Weapons visible, Political symbols, Religious symbols, Unsafe stunts, Nudity above allowed level, Violence level. If no video is provided, score as 100 (Safe)."
                },
                "platform_compliance": {
                    "type": "object",
                    "properties": {
                        "compliance_score": {"type": "number", "description": "0-100, 100=Safe"},
                        "instagram_issues": {"type": "array", "items": {"type": "string"}},
                        "youtube_issues": {"type": "array", "items": {"type": "string"}},
                        "notes": {"type": "string"}
                    },
                    "description": "Instagram: Paid partnership disclosure, False claims. YouTube: Dangerous activities, Misleading thumbnail behavior."
                },
                "creator_risk": {
                    "type": "object",
                    "properties": {
                        "creator_risk_score": {"type": "number", "description": "0-100, 100=Safe"},
                        "risk_factors": {"type": "array", "items": {"type": "string"}},
                        "notes": {"type": "string"}
                    },
                    "description": "Evaluation based on influencer_profile (volatility_score, political frequency, offensive content history)."
                },
                "final_score": {
                    "type": "number",
                    "description": "Calculated as: (text_risk_score * 0.30) + (brand_violation_score * 0.25) + (video_risk_score * 0.20) + (compliance_score * 0.15) + (creator_risk_score * 0.10)"
                },
                "overall_assessment": {"type": "string"}
            },
            "required": ["text_risk", "brand_policy", "video_risk", "platform_compliance", "creator_risk", "final_score", "overall_assessment"]
        }

        # Call LLM Service
        result = await llm_service.chat_completion_json(
            messages=messages,
            json_schema=json_schema,
            temperature=0.0,  # Extremely strict/deterministic
            model_override="google/gemini-3.1-flash-lite-preview",
        )

        return result

brand_safety_ai = BrandSafetyAI()

@celery_app.task(name="tasks.brand_safety_evaluation")
def evaluate_brand_safety_async(
    campaign_brief: Dict,
    script_text: str,
    post_caption: str,
    influencer_profile: Dict,
    brand_policies: Dict,
    target_platforms: list[str] = ["Instagram", "YouTube"],
    video_url: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
) -> Dict:
    """Celery background task for brand safety evaluation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            brand_safety_ai.evaluate_campaign(
                campaign_brief,
                script_text,
                post_caption,
                influencer_profile,
                brand_policies,
                target_platforms,
                video_url,
                thumbnail_url,
            )
        )
    finally:
        loop.close()
