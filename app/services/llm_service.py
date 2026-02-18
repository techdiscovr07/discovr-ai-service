"""
LLM Service - Wrapper for OpenRouter and other LLM providers
"""
import json
from typing import Dict, List, Optional

import httpx

from app.config import settings


class LLMService:
    """Service for interacting with LLMs via OpenRouter"""
    
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.model_name
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://discovr.ai",
                "X-Title": "Discovr AI Service",
            },
            timeout=60.0,
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
    ) -> Dict:
        """
        Send chat completion request to OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: JSON schema for structured output
        
        Returns:
            Response dict with 'content' and 'usage'
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if response_format:
            payload["response_format"] = response_format
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        return {
            "content": content,
            "usage": data.get("usage", {}),
            "model": data.get("model"),
        }
    
    async def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        json_schema: Dict,
        temperature: float = 0.3,
    ) -> Dict:
        """
        Get structured JSON response from LLM
        
        Args:
            messages: Chat messages
            json_schema: JSON schema for response structure
            temperature: Lower temperature for more consistent JSON
        
        Returns:
            Parsed JSON dict
        """
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": json_schema,
            },
        }
        
        result = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        
        # Parse JSON from response
        content = result["content"]
        if isinstance(content, str):
            return json.loads(content)
        return content
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ):
        """
        Stream chat completion (for real-time responses)
        
        Yields:
            Chunks of response text
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
llm_service = LLMService()
