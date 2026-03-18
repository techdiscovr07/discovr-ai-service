"""
AI Helper (Copilot) API endpoints
"""
from typing import List, Dict
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm_service import llm_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/chat")
async def chat_with_helper(request: ChatRequest):
    """
    Streaming chat endpoint for the Discovr Copilot
    """
    try:
        # Convert pydantic models to dicts for the service
        dict_messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Add a system prompt to define the Copilot's personality if not present
        if not any(m["role"] == "system" for m in dict_messages):
            system_prompt = {
                "role": "system",
                "content": (
                    "You are Discovr Copilot, a helpful AI assistant integrated into the Discovr influencer marketing platform. "
                    "Your goal is to help brand owners and marketers with their influencer marketing strategy. "
                    "You can help with drafting outreach emails, brainstorming campaign concepts, understanding metrics, and platform guidance. "
                    "Be professional, concise, and helpful."
                )
            }
            dict_messages.insert(0, system_prompt)

        async def event_generator():
            async for chunk in llm_service.stream_completion(messages=dict_messages):
                if chunk:
                    yield chunk

        return StreamingResponse(event_generator(), media_type="text/plain")
        
    except Exception as e:
        print(f"Copilot Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
