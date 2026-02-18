"""
Discovr AI Service - FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import campaign, script, video
from app.config import settings

app = FastAPI(
    title="Discovr AI Service",
    description="AI-powered content analysis and review",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaign.router, prefix="/ai/campaign", tags=["campaign"])
app.include_router(script.router, prefix="/ai/script", tags=["script"])
app.include_router(video.router, prefix="/ai/video", tags=["video"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "discovr-ai-service"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "discovr-ai-service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
