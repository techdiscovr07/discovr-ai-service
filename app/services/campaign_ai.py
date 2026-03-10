"""
Campaign Creation AI Service
"""
from typing import Dict, Optional

from app.services.llm_service import llm_service
from app.utils.prompt_templates import CAMPAIGN_ANALYSIS_PROMPT


class CampaignAI:
    """AI service for campaign creation assistance"""
    
    async def analyze_campaign(
        self,
        campaign_name: str,
        description: str,
        target_audience: str,
        goals: str,
        brand_name: Optional[str] = None,
    ) -> Dict:
        """
        Analyze campaign brief and provide AI suggestions
        
        Returns:
            {
                "suggestions": [...],
                "improved_title": "...",
                "improved_description": "...",
                "cta_suggestions": [...],
                "score": 0.85,
                "strengths": [...],
                "weaknesses": [...]
            }
        """
        prompt = CAMPAIGN_ANALYSIS_PROMPT.format(
            campaign_name=campaign_name,
            description=description,
            target_audience=target_audience,
            goals=goals,
            brand_name=brand_name or "the brand",
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert marketing strategist helping brands create effective campaigns. Provide actionable, specific suggestions.",
            },
            {"role": "user", "content": prompt},
        ]
        
        json_schema = {
            "type": "object",
            "properties": {
                "score": {"type": "number", "description": "Overall quality score 0-1"},
                "improved_title": {"type": "string"},
                "improved_description": {"type": "string"},
                "cta_suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "suggestion": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                    },
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["score", "improved_title", "improved_description", "suggestions"],
            "additionalProperties": False
        }
        
        result = await llm_service.chat_completion_json(
            messages=messages,
            json_schema=json_schema,
            temperature=0.7,
        )
        
        return result
        
    async def chat_strategist(
        self,
        messages: list,
        competitor_urls: list = None
    ) -> Dict:
        """
        Handle a chat turn for the Strategist AI.
        """
        response_schema = {
            "type": "object",
            "properties": {
                "ready": {"type": "boolean"},
                "chat_reply": {"type": "string"},
                "strategy_playbook": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "improved_title": {"type": "string"},
                        "improved_description": {"type": "string"},
                        "cta_suggestions": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "suggestion": {"type": "string"},
                                    "reason": {"type": "string"}
                                },
                                "required": ["category", "suggestion", "reason"],
                                "additionalProperties": False
                            }
                        },
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "weaknesses": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": [
                        "score", "improved_title", "improved_description", 
                        "cta_suggestions", "suggestions", "strengths", "weaknesses"
                    ],
                    "additionalProperties": False
                }
            },
            "required": ["ready", "chat_reply", "strategy_playbook"],
            "additionalProperties": False
        }
        
        system_msg = {
            "role": "system", 
            "content": "You are a friendly influencer marketing strategist AI. You need to create a complete strategy playbook. If you don't have enough details (like campaign goal and target audience), ask the user follow-up questions in 'chat_reply'. Once you have enough info, set 'ready' to true and fill out 'strategy_playbook'."
        }
        
        full_messages = [system_msg] + messages
        
        result = await llm_service.chat_completion_json(
            messages=full_messages,
            json_schema=response_schema,
            temperature=0.7,
        )
        return result

campaign_ai = CampaignAI()
