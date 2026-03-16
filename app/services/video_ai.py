import os
import asyncio
import base64
from typing import Dict, Optional

from app.celery_app import celery_app
from app.services.llm_service import llm_service

class VideoAI:
    """Enhanced AI service for end-to-end multi-modal video review using Gemini 3.1 Flash"""

    async def review_video(
        self,
        video_url: str,
        campaign_brief: Dict,
        script_content: Optional[str] = None,
        target_language: str = "English",
        target_platforms: list[str] = ["TikTok", "Instagram Reels"],
        cultural_context: Optional[str] = None,
        caption: Optional[str] = None,
        brand_guidelines: Optional[str] = None,
        platform_policies: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
    ) -> Dict:
        """
        Review locally saved raw video using Gemini Multi-Modal capabilities.
        Extracts script, timeline issues, UI scorecard, and pass/fail metrics. 
        """
        
        # Clean local file path from `file:///path` format
        local_path = video_url.replace("file://", "")
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Video file not found at {local_path}")

        try:
            # 1. Read the raw mp4 file and encode to base64
            with open(local_path, "rb") as video_file:
                video_b64 = base64.b64encode(video_file.read()).decode("utf-8")

            thumbnail_b64 = None
            if thumbnail_url:
                local_thumb_path = thumbnail_url.replace("file://", "")
                if os.path.exists(local_thumb_path):
                    with open(local_thumb_path, "rb") as thumb_file:
                        thumbnail_b64 = base64.b64encode(thumb_file.read()).decode("utf-8")
                
            # 2. Prepare the exhaustive system prompt
            system_prompt = (
                "You are an elite Brand Compliance Officer and Senior Creative Director auditing a Draft Video. "
                "You have been provided with the raw video file and the brand's campaign brief. "
                "Your job is to perform a rigorous Multi-Layer Content Audit.\n\n"
                "CRITICAL DIRECTIVES:\n"
                "1. SCRIPT EXTRACTION: Listen to the audio and transcribe the speaker perfectly.\n"
                "2. VISUAL/AUDIO TIMELINE: Pinpoint exact timestamps (e.g. '00:07', '00:15') where errors, missing disclosures, or brilliant hooks occur.\n"
                "4. EXACT FIXES: Do not give generic advice. Give exact replacement text/actions for any issue found.\n"
                "5. HUMAN IN LOOP: If you find critical compliance issues, misleading claims, or severe brand safety risks, set requires_manual_review to true and list the reasons.\n"
                f"--- CAMPAIGN BRIEF ---\n"
                f"Name: {campaign_brief.get('name', '')}\n"
                f"Target Platforms: {', '.join(target_platforms) if target_platforms else 'Any'}\n"
                f"Primary Focus: {campaign_brief.get('primary_focus', '')}\n"
                f"Required Do's: {campaign_brief.get('dos', '')}\n"
                f"Prohibited Dont's: {campaign_brief.get('donts', '')}\n"
            )
            
            if caption:
                system_prompt += f"\n--- PROVIDED CAPTION ---\n{caption}\n"
            if brand_guidelines:
                system_prompt += f"\n--- BRAND GUIDELINES ---\n{brand_guidelines}\n"
            if platform_policies:
                system_prompt += f"\n--- PLATFORM POLICIES ---\n{platform_policies}\n"

            # 3. Construct Multi-Modal Payload for OpenRouter (Gemini Support)
            user_content = []
            
            # Put video FIRST
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:video/mp4;base64,{video_b64}"
                }
            })
            
            # Add thumbnail if exists
            if thumbnail_b64:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{thumbnail_b64}"
                    }
                })

            user_content.append({
                "type": "text", 
                "text": f"{system_prompt}\n\nPlease strictly evaluate the attached video content according to these parameters."
            })

            messages = [
                {"role": "user", "content": user_content}
            ]

            # 4. Strict Exact JSON Schema requested by User
            json_schema = {
                "type": "object",
                "properties": {
                    "script_extraction": {
                        "type": "string",
                        "description": "Exact transcription of spoken words in the video"
                    },
                    "pass_fail_checklist": {
                        "type": "object",
                        "properties": {
                            "brief_adherence": {
                                "type": "object",
                                "properties": {"status": {"type": "string", "enum": ["Pass", "Fail"]}, "notes": {"type": "string"}}
                            },
                            "key_messages": {
                                "type": "object",
                                "properties": {"status": {"type": "string", "enum": ["Pass", "Fail"]}, "notes": {"type": "string"}}
                            },
                            "brand_tone": {
                                "type": "object",
                                "properties": {"status": {"type": "string", "enum": ["Pass", "Fail"]}, "notes": {"type": "string"}}
                            },
                            "required_assets": {
                                "type": "object",
                                "properties": {"status": {"type": "string", "enum": ["Pass", "Fail"]}, "notes": {"type": "string"}}
                            },
                            "disclosure_compliance": {
                                "type": "object",
                                "properties": {"status": {"type": "string", "enum": ["Pass", "Fail"]}, "notes": {"type": "string"}}
                            }
                        }
                    },
                    "timestamped_issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string", "description": "e.g., 00:12"},
                                "issue": {"type": "string"},
                                "severity": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]}
                            }
                        }
                    },
                    "risk_flags": {
                        "type": "array",
                        "items": {"type": "string", "description": "High level risk flags like competitor mentions or compliance gaps"}
                    },
                    "human_in_loop": {
                        "type": "object",
                        "properties": {
                            "requires_manual_review": {"type": "boolean"},
                            "manual_review_reasons": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "exact_fixes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "original": {"type": "string", "description": "The flawed text or action"},
                                "replacement": {"type": "string", "description": "Exact replacement text or explicit edit instruction"}
                            }
                        }
                    },
                    "publish_score": {
                        "type": "integer",
                        "description": "Overall score 0-100"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["Low", "Moderate", "High"]
                    },
                    "advanced_analysis": {
                        "type": "object",
                        "properties": {
                            "cta_effectiveness": {"type": "string"},
                            "thumbnail_psychology": {"type": "string"}
                        }
                    }
                },
                "required": [
                    "script_extraction", "pass_fail_checklist", "timestamped_issues", 
                    "exact_fixes", "publish_score", "risk_level", "risk_flags", "human_in_loop", "advanced_analysis"
                ]
            }

            # 5. Call LLM Service
            result = await llm_service.chat_completion_json(
                messages=messages,
                json_schema=json_schema,
                temperature=0.1,  # Strictness for Auditing
                model_override="google/gemini-3.1-flash-lite-preview",
            )

            return result

        finally:
            # We don't delete the local video yet so the frontend can potentially stream it
            pass


video_ai = VideoAI()

@celery_app.task(name="tasks.video_review")
def review_video_async(
    video_url: str,
    campaign_brief: Dict,
    script_content: Optional[str] = None,
    target_language: str = "English",
    target_platforms: list[str] = ["Instagram Reels"],
    cultural_context: Optional[str] = None,
    caption: Optional[str] = None,
    brand_guidelines: Optional[str] = None,
    platform_policies: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
) -> Dict:
    """Celery background task for multi-modal video review"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            video_ai.review_video(
                video_url,
                campaign_brief,
                script_content,
                target_language,
                target_platforms,
                cultural_context,
                caption,
                brand_guidelines,
                platform_policies,
                thumbnail_url,
            )
        )
    finally:
        loop.close()
