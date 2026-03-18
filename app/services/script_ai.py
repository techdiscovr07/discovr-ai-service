"""
Script Review AI Service
"""

from typing import Dict, Optional
import asyncio

from app.celery_app import celery_app
from app.services.llm_service import llm_service
from app.utils.prompt_templates import SCRIPT_REVIEW_PROMPT


class ScriptAI:
    """AI service for script review and analysis"""

    async def review_script(
        self,
        script_content: str,
        campaign_brief: Dict,
        brand_guidelines: Optional[str] = None,
        target_language: str = "English",
        target_platforms: list[str] = ["Instagram Reels"],
        cultural_context: Optional[str] = None,
    ) -> Dict:
        """
        Review creator script and provide detailed feedback

        Returns:
            {
                "overall_score": 0.82,
                "brand_fit_score": 0.9,
                "compliance_score": 0.85,
                "quality_score": 0.75,
                "engagement_score": 0.8,
                "feedback": "...",
                "suggestions": [...],
                "issues": [...],
                "strengths": [...]
            }
        """
        prompt = SCRIPT_REVIEW_PROMPT.format(
            script_content=script_content,
            campaign_name=campaign_brief.get("name", ""),
            campaign_description=campaign_brief.get("description", ""),
            video_title=campaign_brief.get("video_title", ""),
            primary_focus=campaign_brief.get("primary_focus", ""),
            dos=campaign_brief.get("dos", ""),
            donts=campaign_brief.get("donts", ""),
            cta=campaign_brief.get("cta", ""),
            brand_guidelines=brand_guidelines or "Standard brand guidelines apply",
            target_language=target_language,
            target_platforms=(
                ", ".join(target_platforms) if target_platforms else "All applicable platforms"
            ),
            cultural_context=cultural_context or "None specified",
        )

        messages = [
            {
                "role": "system",
                "content": "You are a top-tier Brand Strategist and strict FTC Compliance Officer reviewing creator scripts. Provide detailed Chain-of-Thought reasoning before scoring. Generate actionable feedback and highly creative platform-specific variants.",
            },
            {"role": "user", "content": prompt},
        ]

        json_schema = {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "Write a highly detailed, step-by-step internal monologue analyzing the script against the brief before assigning any scores.",
                },
                "overall_score": {
                    "type": "integer",
                    "description": "Overall script quality score from 0 to 100",
                    "minimum": 0,
                    "maximum": 100,
                },
                "brand_fit_score": {
                    "type": "integer",
                    "description": "Brand fit score from 0 to 100",
                    "minimum": 0,
                    "maximum": 100,
                },
                "compliance_score": {
                    "type": "integer",
                    "description": "Compliance score from 0 to 100",
                    "minimum": 0,
                    "maximum": 100,
                },
                "quality_score": {
                    "type": "integer",
                    "description": "Writing quality and engagement score from 0 to 100",
                    "minimum": 0,
                    "maximum": 100,
                },
                "hook_pacing_cta_scores": {
                    "type": "object",
                    "properties": {
                        "hook_strength": {"type": "number"},
                        "pacing": {"type": "number"},
                        "cta_clarity": {"type": "number"},
                    },
                },
                "feedback": {"type": "string", "description": "Overall feedback summary"},
                "line_by_line_feedback": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_text": {"type": "string"},
                            "issue": {"type": "string"},
                            "suggestion": {"type": "string"},
                            "aspect": {
                                "type": "string",
                                "enum": ["hook", "pacing", "clarity", "cta", "other"],
                            },
                        },
                    },
                },
                "platform_fit_edits": {
                    "type": "object",
                    "properties": {
                        "youtube_longform": {
                            "type": "string",
                            "description": "Edits/tips for YouTube",
                        },
                        "reels": {
                            "type": "string",
                            "description": "Edits/tips for Instagram Reels",
                        },
                        "shorts": {
                            "type": "string",
                            "description": "Edits/tips for YouTube Shorts",
                        },
                    },
                },
                "platform_variants": {
                    "type": "object",
                    "properties": {
                        "safe": {
                            "type": "string",
                            "description": "A very safe, compliance-first rewrite",
                        },
                        "bolder": {
                            "type": "string",
                            "description": "An edgier, high-energy hook and pacing",
                        },
                        "shorter": {
                            "type": "string",
                            "description": "Trimmed down heavily for short-form platforms (under 15s)",
                        },
                    },
                },
                "brand_safety_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "disallowed_claim_or_competitor": {"type": "string"},
                            "explanation": {"type": "string"},
                            "recommended_fix": {"type": "string"},
                        },
                    },
                },
                "automated_checks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "passed": {"type": "boolean"},
                            "details": {"type": "string"},
                            "reasoning": {"type": "string"},
                            "recommendation": {"type": "string"},
                        },
                        "required": ["title", "passed", "details", "reasoning", "recommendation"],
                    },
                },
            },
            "required": [
                "reasoning",
                "overall_score",
                "brand_fit_score",
                "compliance_score",
                "quality_score",
                "hook_pacing_cta_scores",
                "feedback",
                "line_by_line_feedback",
                "platform_fit_edits",
                "platform_variants",
                "brand_safety_issues",
                "automated_checks",
            ],
        }

        result = await llm_service.chat_completion_json(
            messages=messages,
            json_schema=json_schema,
            temperature=0.4,  # Lowered for stricter adherence + reasoning stability
        )

        return result


script_ai = ScriptAI()


@celery_app.task(name="tasks.script_review")
def review_script_async(
    script_content: str,
    campaign_brief: Dict,
    brand_guidelines: Optional[str] = None,
    target_language: str = "English",
    target_platforms: list[str] = ["Instagram Reels"],
    cultural_context: Optional[str] = None,
) -> Dict:
    """Celery background task for script review"""
    # Create new event loop for async LLM call in this worker thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            script_ai.review_script(
                script_content,
                campaign_brief,
                brand_guidelines,
                target_language,
                target_platforms,
                cultural_context,
            )
        )
    finally:
        loop.close()
