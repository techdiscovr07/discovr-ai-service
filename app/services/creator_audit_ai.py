import os
import asyncio
from typing import Dict, List, Optional
from app.celery_app import celery_app
from app.services.llm_service import llm_service
from app.services.social_scraper import DeepCreatorScraper

class CreatorAuditAI:
    """AI service for deep historical creator audit, including sentiment analysis of comments."""

    async def audit_creator(
        self,
        instagram_handle: Optional[str] = None,
        youtube_handle: Optional[str] = None,
        brand_policies: Optional[Dict] = None,
    ) -> Dict:
        """
        Deep scan of creator's history and audience sentiment.
        """
        if not brand_policies:
            brand_policies = {}

        # 1. Scrape Content
        scrape_results = await DeepCreatorScraper.get_creator_history(
            instagram_handle=instagram_handle,
            youtube_handle=youtube_handle
        )

        content_summary = ""
        comments_summary = ""
        analyzed_comments_list = []
        errors = []

        for platform, data in scrape_results.items():
            if not data or data.get("error"):
                error_msg = data.get('error', 'Unknown') if data else 'Not requested'
                errors.append(f"{platform} error: {error_msg}")
                continue
            
            for post in data.get("posts", []):
                platform_title = "Caption" if platform == "instagram" else "Title"
                post_metrics = f"Likes: {post.get('likes', 0)}" if post.get("likes") else ""
                content_summary += f"[{platform.upper()}] Post URL: {post.get('url')}\n"
                content_summary += f"Date: {post.get('date', 'Unknown')}\n"
                content_summary += f"{platform_title}: {post.get('caption', '')} | {post_metrics}\n\n"
                
                for comment in post.get("comments", []):
                    # add comment formatting
                    comment_text = comment.get('text', '')
                    comment_likes = comment.get('likes', 0)
                    comments_summary += f"[{platform.upper()}] Comment on {post.get('url')}: {comment_text} (Likes: {comment_likes})\n"
                    analyzed_comments_list.append({
                        "platform": platform.upper(),
                        "url": post.get("url"),
                        "text": comment_text,
                        "likes": comment_likes
                    })

        if not content_summary.strip():
            content_summary = "No posts scraped or available."
        if not comments_summary.strip():
            comments_summary = "No comments scraped or available."

        system_prompt = (
            "You are an elite, objective, and strict Creator Deep Audit Agent. "
            "Your job is to deeply analyze a creator's historical content and audience comments "
            "to determine their risk profile for brand partnerships.\n\n"
            "CRITICAL DIRECTIVES:\n"
            "- Evaluate overall brand safety based on the provided historical posts.\n"
            "- Perform sentiment analysis on the provided comments. Classify comments as Positive, Negative, Neutral, or Toxic.\n"
            "- Return numeric scores (0-100) for overall safety, where 100 means completely safe.\n"
            "- Provide a detailed breakdown of comment sentiment.\n"
            "- Highlight any flagged past posts or toxic comments.\n\n"
            f"--- BRAND POLICIES ---\n"
            f"Banned Keywords: {', '.join(brand_policies.get('banned_keywords', []))}\n"
            f"Sensitive Topics: {', '.join(brand_policies.get('sensitive_topics', []))}\n"
            f"Restricted Categories: {', '.join(brand_policies.get('restricted_categories', []))}\n"
            f"Tone Restrictions: {brand_policies.get('tone_restrictions', '')}\n\n"
        )
        
        user_content = [
            {"type": "text", "text": "Analyze the following creator history and comments:"},
            {"type": "text", "text": f"Posts:\n{content_summary}"},
            {"type": "text", "text": f"Comments:\n{comments_summary}"}
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Define a reusable schema for each platform analysis
        platform_analysis_schema = {
            "type": "object",
            "properties": {
                "historical_safety_score": {"type": "number", "description": "0-100, 100=Safe"},
                "sentiment_analysis": {
                    "type": "object",
                    "properties": {
                        "positive_percentage": {"type": "number"},
                        "negative_percentage": {"type": "number"},
                        "neutral_percentage": {"type": "number"},
                        "toxic_percentage": {"type": "number"},
                        "summary": {"type": "string", "description": "Overall summary of audience sentiment"}
                    },
                    "required": ["positive_percentage", "negative_percentage", "neutral_percentage", "toxic_percentage", "summary"]
                },
                "content_analysis": {"type": "string", "description": "Analysis of the post captions, video titles, themes, and metrics"},
                "flagged_content": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content_type": {"type": "string", "enum": ["post", "comment"]},
                            "content_text": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["content_type", "content_text", "reason"]
                    }
                }
            },
            "required": ["historical_safety_score", "sentiment_analysis", "content_analysis", "flagged_content"]
        }

        json_schema = {
            "type": "object",
            "properties": {
                "overall_assessment": {"type": "string"},
                "instagram_analysis": platform_analysis_schema,
                "youtube_analysis": platform_analysis_schema
            },
            "required": ["overall_assessment"]
        }

        result = await llm_service.chat_completion_json(
            messages=messages,
            json_schema=json_schema,
            temperature=0.0,
            model_override="google/gemini-3.1-flash-lite-preview",
        )
        
        result["analyzed_comments"] = analyzed_comments_list

        return result

creator_audit_ai = CreatorAuditAI()

@celery_app.task(name="tasks.creator_audit")
def evaluate_creator_audit_async(
    instagram_handle: Optional[str] = None,
    youtube_handle: Optional[str] = None,
    brand_policies: Optional[Dict] = None,
) -> Dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            creator_audit_ai.audit_creator(
                instagram_handle,
                youtube_handle,
                brand_policies,
            )
        )
    finally:
        loop.close()
