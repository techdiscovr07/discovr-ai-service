"""
Script Review AI Service
"""
from typing import Dict, Optional

from app.services.llm_service import llm_service
from app.utils.prompt_templates import SCRIPT_REVIEW_PROMPT


class ScriptAI:
    """AI service for script review and analysis"""
    
    async def review_script(
        self,
        script_content: str,
        campaign_brief: Dict,
        brand_guidelines: Optional[str] = None,
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
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert content reviewer specializing in video scripts. Evaluate scripts for brand alignment, compliance, quality, and engagement. Provide specific, actionable feedback.",
            },
            {"role": "user", "content": prompt},
        ]
        
        json_schema = {
            "type": "object",
            "properties": {
                "overall_score": {"type": "number", "description": "Overall score 0-1"},
                "brand_fit_score": {"type": "number", "description": "Brand alignment 0-1"},
                "compliance_score": {"type": "number", "description": "Compliance with guidelines 0-1"},
                "quality_score": {"type": "number", "description": "Script quality 0-1"},
                "engagement_score": {"type": "number", "description": "Engagement potential 0-1"},
                "feedback": {"type": "string", "description": "Overall feedback summary"},
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["improvement", "addition", "removal"]},
                            "suggestion": {"type": "string"},
                            "reason": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        },
                    },
                },
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "issue": {"type": "string"},
                            "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                            "suggestion": {"type": "string"},
                        },
                    },
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["overall_score", "brand_fit_score", "compliance_score", "quality_score", "feedback"],
        }
        
        result = await llm_service.chat_completion_json(
            messages=messages,
            json_schema=json_schema,
            temperature=0.3,  # Lower temperature for consistent scoring
        )
        
        return result


script_ai = ScriptAI()
