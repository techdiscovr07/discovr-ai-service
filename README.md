# Discovr AI Service

Standalone Python microservice for AI-powered content analysis, strategist playbooks, and real-time assistance.

## Features

- **Influencer Strategist** - Generates massive, agency-grade influencer strategy playbooks from an 8-part campaign brief.
- **Discovr Copilot** - Real-time streaming assistant for generic platform help and brand guidance.
- **Video Review AI (Multi-Modal)** - Analyzes creator reels via base64 encoding for deep quality, compliance, and hook analysis. Supports captions, thumbnails, and brand guidelines.
- **Script Review AI** - High-speed analysis of creator scripts against campaign briefs and platform policies.
- **Background Processing** - Asynchronous task execution for heavy video/script review via Celery and Redis.

## Tech Stack

- **Framework**: FastAPI (Async, Pydantic v2, Auto-Docs)
- **LLM**: OpenRouter (Unified multi-provider wrapper)
- **Background Tasks**: Celery + Redis
- **Database**: MongoDB (Audit logs & analysis results)
- **Video Processing**: OpenCV / Face-Analysis logic

## Quick Start

### Prerequisites

- Python 3.11+
- Redis Server (for background tasks)
- OpenRouter API key

### Installation

```bash
# Clone or create the repository
cd discovr-ai-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your keys
```

### Run Locally

**1. Start the API:**
```bash
uvicorn app.main:app --reload --port 8000
```

**2. Start the Worker (for Video/Script review):**
```bash
celery -A app.celery_app worker --loglevel=info
```

Visit http://localhost:8000/docs for API documentation.

## API Endpoints

### 1. Influencer Strategist
`POST /ai/campaign/chat`
Instantly generates a structured JSON playbook including creator mix, content story arcs, hooks, and measurement plans.

### 2. Discovr Copilot
`POST /ai/helper/chat`
Streaming endpoint for conversational assistance. Accepts message history and returns a real-time stream.

### 3. Video & Script Review
- `POST /ai/video/upload` - Upload video for analysis.
- `POST /ai/video/review` - Start asynchronous video review task.
- `POST /ai/script/review` - Start asynchronous script review task.
- `GET /tasks/{task_id}` - Poll for asynchronously completed analysis results.

## Project Structure

```
discovr-ai-service/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── celery_app.py        # Background task config
│   ├── api/
│   │   ├── campaign.py      # Strategist endpoints
│   │   ├── helper.py        # Copilot endpoints
│   │   ├── video.py         # Video review logic
│   │   └── tasks.py         # Celery status polling
│   ├── services/
│   │   ├── campaign_ai.py   # Strategy generation logic
│   │   ├── helper_ai.py     # Streaming assistant logic
│   │   └── llm_service.py   # Unified OpenRouter wrapper
│   └── utils/
│       ├── prompt_templates.py # Standardized AI instructions
│       └── video_processor.py  # Encoding & visual analysis
├── requirements.txt
├── Dockerfile
└── README.md
```

## License

Proprietary - Discovr Platform
