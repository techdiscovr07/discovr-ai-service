# Discovr AI Service

Standalone Python microservice for AI-powered content analysis and review.

## Features

- **Campaign Creation AI** - Helps brands create better campaigns
- **Script Review AI** - Reviews creator scripts for quality, compliance, brand fit
- **Video Review AI** - Analyzes creator reels for quality, compliance, brand alignment

## Tech Stack

- **Framework**: FastAPI (async, auto-docs, type hints)
- **LLM**: OpenRouter (supports GPT-4, Claude, etc.)
- **Video Processing**: OpenCV, moviepy, ffmpeg
- **Storage**: MongoDB (for analysis results), Redis (for caching)

## Quick Start

### Prerequisites

- Python 3.11+
- OpenRouter API key ([get one here](https://openrouter.ai))
- MongoDB (optional, for storing results)
- Redis (optional, for caching)

### Installation

```bash
# Clone or create the repository
cd discovr-ai-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenRouter API key
```

### Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for API documentation.

### Run with Docker

```bash
docker build -t discovr-ai-service .
docker run -p 8000:8000 --env-file .env discovr-ai-service
```

## Environment Variables

See `.env.example` for all configuration options.

Required:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

Optional:
- `MODEL_NAME` - LLM model to use (default: `openai/gpt-4-turbo-preview`)
- `REDIS_URL` - Redis connection for caching
- `MONGODB_URI` - MongoDB connection for storing results
- `PORT` - Service port (default: 8000)
- `AI_SERVICE_API_KEY` - API key for authentication with Go backend

## API Endpoints

### Campaign Analysis
```
POST /ai/campaign/analyze
Body: {
  "campaign_name": "...",
  "description": "...",
  "target_audience": "...",
  "goals": "...",
  "brand_name": "..." (optional)
}
```

### Script Review
```
POST /ai/script/review
Body: {
  "script_content": "...",
  "campaign_brief": {...},
  "brand_guidelines": "..." (optional)
}
```

### Video Review
```
POST /ai/video/review
Body: {
  "video_url": "...",
  "campaign_brief": {...},
  "script_content": "..." (optional)
}
```

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

## Deployment

### Render / Railway / Fly.io

1. Connect your repository
2. Set environment variables
3. Deploy!

### Docker

```bash
docker build -t discovr-ai-service .
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key \
  discovr-ai-service
```

## Integration with Go Backend

The Go backend calls this service via HTTP:

```go
aiHandler := ai.NewHandler("http://your-ai-service-url", "api-key")
result, err := aiHandler.AnalyzeCampaign(ctx, request)
```

See `../discovr-backend/internal/ai/handler.go` for integration code.

## Project Structure

```
discovr-ai-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── campaign.py      # Campaign AI endpoints
│   │   ├── script.py        # Script review endpoints
│   │   └── video.py         # Video review endpoints
│   ├── services/
│   │   ├── llm_service.py   # OpenRouter wrapper
│   │   ├── campaign_ai.py   # Campaign analysis logic
│   │   ├── script_ai.py      # Script review logic
│   │   └── video_ai.py       # Video analysis logic
│   └── utils/
│       ├── video_processor.py    # Video processing
│       └── prompt_templates.py  # Prompt engineering
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## License

Proprietary - Discovr Platform
# discovr-ai-service
# discovr-ai-service
# discovr-ai-service
# discovr-ai-service
# discovr-ai-service
