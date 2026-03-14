from typing import Dict, List
import json

from app.services.llm_service import llm_service


class CampaignAI:
    """Conversational AI service for campaign creation assistance"""

    async def chat_stream(
        self, messages: List[Dict[str, str]], scraped_data: List[Dict] = None
    ) -> Dict:
        """
        Takes conversation history (form brief) and optional scraped competitor data.
        Generates the final playbook in ONE shot instead of conversational querying.
        """
        system_prompt = (
            "You are an elite Senior Influencer Strategist AI working at a top-tier global advertising agency. "
            "You have received a comprehensive 8-part campaign brief from a high-profile brand client containing their core objective, target audience, budget, and creative preferences.\n\n"
            "CRITICAL DIRECTIVES FOR GENERATION:\n"
            "1. You do NO CONSULTING. The user has explicitly requested to skip straight to the deliverable. Do not say 'Here is your playbook'. You must generate the final 'strategy_playbook' JSON immediately based on their inputs.\n"
            "2. Set 'ready' to true permanently.\n"
            "3. If any field in the playbook is loosely defined by their brief, use your Senior Strategist capabilities to extrapolate safely and intelligently based on the context they provided. Make bold, data-backed assumptions rather than generating generic or tepid advice.\n"
            "4. Your single goal is to deliver the most detailed, actionable, agency-grade influencer strategy playbook possible, directly mapping their inputs to bespoke, tactical recommendations.\n"
            "5. Tone: Authoritative, deeply analytical, hyper-tactical, and modern. Use contemporary marketing terminology (e.g., 'CAC', 'ROAS', 'Halo Effect', 'Signal Loss', 'Creator-Led Authenticity') appropriately, but avoid meaningless buzzwords.\n"
            "6. For the Content Playbook, do not suggest generic ideas like 'show the product'. Suggest specific, nuanced story arcs (e.g., 'A day in the life struggling with [Pain Point] seamlessly solved by [Product] in the final 3 seconds').\n"
            "7. CRITICAL: You MUST generate EXACTLY 5 complete influencer scripts in the `scripts` array. These scripts MUST be written natively in the Target Language specified by the user. Ensure cultural nuance and platform-appropriate formatting.\n"
        )

        if scraped_data:
            system_prompt += f"\nWe scraped the provided competitor URLs and performed a Deep Visual Analysis (via Multi-Modal AI) on their last 10 partnership reels/posts:\n{json.dumps(scraped_data, indent=2)}\n"
            system_prompt += "You must act as the primary Data Analyst for this scraped data. Scrutinize the captions, tags, and 'deep_visual_analysis' fields to deduce their actual video content, story arcs, and hooks. Build out an exhaustive 'competitor_analysis' array. Be highly specific, cite patterns, and avoid generic info.\n"

        # Format messages for LLM
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append(msg)

        json_schema = {
            "type": "object",
            "properties": {
                "ready": {
                    "type": "boolean",
                    "description": "Always set this to true.",
                },
                "strategy_playbook": {
                    "type": "object",
                    "properties": {
                        "strategy_brief": {
                            "type": "object",
                            "properties": {
                                "objective_clarity": {"type": "string"},
                                "audience_summary": {"type": "string"},
                                "strategic_angle": {"type": "string"},
                                "core_messaging_pillars": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "3-5 distinct bullet points"
                                },
                                "recommended_formats": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "creator_mix": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tier_split_percentage": {"type": "string"},
                                    "suggested_categories": {"type": "array", "items": {"type": "string"}},
                                    "geo_split": {"type": "array", "items": {"type": "string"}},
                                    "language_split": {"type": "array", "items": {"type": "string"}},
                                    "suggested_volume": {"type": "string", "description": "e.g., 10 micro + 2 mid"},
                                    "rationale": {"type": "string"},
                                },
                            },
                            "description": "Array of records to function as a table in the UI",
                        },
                        "content_playbook": {
                            "type": "object",
                            "properties": {
                                "hook_frameworks": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "5 example hook styles"
                                },
                                "story_arcs": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "e.g., Problem->Agitate->Solution, Before/After, Demo-led"
                                },
                                "dos": {"type": "array", "items": {"type": "string"}},
                                "donts": {"type": "array", "items": {"type": "string"}},
                                "cta_options": {"type": "array", "items": {"type": "string"}, "description": "Based on funnel stage"},
                            },
                        },
                        "timeline_and_sequencing": {
                            "type": "object",
                            "properties": {
                                "phase_1_tease": {"type": "string"},
                                "phase_2_burst": {"type": "string"},
                                "phase_3_reinforcement": {"type": "string"},
                                "phase_4_always_on": {"type": "string"},
                                "week_wise_rollout": {"type": "string"},
                                "volume_per_week": {"type": "string"},
                                "paid_amplification_timing": {"type": "string"},
                            },
                        },
                        "measurement_plan": {
                            "type": "object",
                            "properties": {
                                "primary_kpi": {"type": "string"},
                                "secondary_kpis": {"type": "array", "items": {"type": "string"}},
                                "benchmark_targets": {"type": "string"},
                                "tracking_method": {"type": "string"},
                                "attribution_approach": {"type": "string"},
                                "optimization_triggers": {"type": "string"},
                                "learning_framework": {"type": "string"},
                            },
                        },
                        "risk_assessment": {
                            "type": "object",
                            "properties": {
                                "execution_risks": {"type": "array", "items": {"type": "string"}},
                                "messaging_risks": {"type": "array", "items": {"type": "string"}},
                                "creator_mismatch_risk": {"type": "array", "items": {"type": "string"}},
                                "platform_dependency_risk": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "experiment_framework": {
                            "type": "object",
                            "properties": {
                                "creative_variable_testing": {"type": "string"},
                                "creator_tier_testing": {"type": "string"},
                                "hook_testing": {"type": "string"},
                            },
                        },
                        "human_in_loop": {
                            "type": "object",
                            "properties": {
                                "confidence_score": {
                                    "type": "number",
                                    "description": "0 to 1 score indicating confidence in this strategy given the inputs"
                                },
                                "manual_review_areas": {"type": "array", "items": {"type": "string"}},
                                "assumptions_made": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "scripts": {
                            "type": "array",
                            "description": "Exactly 5 complete influencer scripts written in the user's requested target language.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "target_platform": {"type": "string"},
                                    "creator_tier": {"type": "string"},
                                    "visual_hook": {"type": "string"},
                                    "spoken_script": {"type": "string", "description": "The exact script to be spoken, translated to the target language if required."},
                                    "captions_or_text_on_screen": {"type": "string"},
                                    "estimated_duration_seconds": {"type": "number"}
                                },
                                "required": ["title", "target_platform", "creator_tier", "visual_hook", "spoken_script", "captions_or_text_on_screen", "estimated_duration_seconds"]
                            },
                            "minItems": 5,
                            "maxItems": 5
                        },
                    },
                    "required": [
                        "strategy_brief",
                        "creator_mix",
                        "content_playbook",
                        "timeline_and_sequencing",
                        "measurement_plan",
                        "risk_assessment",
                        "experiment_framework",
                        "human_in_loop",
                        "scripts"
                    ],
                },
            },
            "required": ["ready", "strategy_playbook"],
        }

        result = await llm_service.chat_completion_json(
            messages=formatted_messages, json_schema=json_schema, temperature=0.7
        )

        # Enforce rule of returning ready state
        result["ready"] = True
        if "chat_reply" not in result:
            result["chat_reply"] = "Strategy playbook generated successfully."

        return result
