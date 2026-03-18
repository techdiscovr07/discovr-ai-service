"""Configuration management"""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenRouter Configuration
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model_name: str = os.getenv("MODEL_NAME", "openai/gpt-4-turbo-preview")
    
    # Redis (for caching)
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # MongoDB (for storing analysis results)
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "discovr_ai")
    
    # Celery Background Tasks
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Service Configuration
    port: int = int(os.getenv("PORT", "8000"))
    ai_service_api_key: Optional[str] = None  # For auth with Go backend
    
    # Video Processing
    max_video_duration_seconds: int = 300  # 5 minutes
    video_temp_dir: str = os.getenv("VIDEO_TEMP_DIR", "/tmp/discovr-videos")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
        protected_namespaces = ('settings_',)


settings = Settings()
