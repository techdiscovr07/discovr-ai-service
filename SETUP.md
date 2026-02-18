# Setup Guide - Discovr AI Service

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai))
- (Optional) MongoDB for storing analysis results
- (Optional) Redis for caching

## Quick Start

### 1. Clone/Create Repository

```bash
# If this is a separate repo
git clone <your-repo-url> discovr-ai-service
cd discovr-ai-service

# Or if creating fresh
mkdir discovr-ai-service
cd discovr-ai-service
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# Required: OPENROUTER_API_KEY
```

### 4. Run Service

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Verify It's Working

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status": "healthy", "service": "discovr-ai-service"}

# View API docs
open http://localhost:8000/docs
```

## Docker Setup

### Build and Run

```bash
# Build image
docker build -t discovr-ai-service .

# Run container
docker run -p 8000:8000 --env-file .env discovr-ai-service
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Integration with Go Backend

1. **Deploy AI Service** (Render, Railway, Fly.io, etc.)
   - Get the service URL (e.g., `https://discovr-ai-service.onrender.com`)

2. **Update Go Backend `.env`**:
   ```bash
   AI_SERVICE_URL=https://discovr-ai-service.onrender.com
   AI_SERVICE_API_KEY=your-secret-key-here
   ```

3. **Go Backend will call AI Service**:
   - `/brand/campaigns/ai/analyze` → Calls AI service
   - `/brand/campaigns/ai/review-script` → Calls AI service
   - `/brand/campaigns/ai/review-video` → Calls AI service

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
make format
# or
black app/
isort app/

# Run tests
make test
# or
pytest

# Lint
make lint
```

## Deployment Options

### Option 1: Render
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

### Option 2: Railway
1. Connect repository
2. Railway auto-detects Python
3. Add environment variables
4. Deploy!

### Option 3: Fly.io
```bash
fly launch
fly secrets set OPENROUTER_API_KEY=your-key
fly deploy
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | Your OpenRouter API key |
| `MODEL_NAME` | No | `openai/gpt-4-turbo-preview` | LLM model to use |
| `PORT` | No | `8000` | Service port |
| `AI_SERVICE_API_KEY` | No | - | API key for Go backend auth |
| `REDIS_URL` | No | - | Redis connection (for caching) |
| `MONGODB_URI` | No | `mongodb://localhost:27017` | MongoDB connection |
| `VIDEO_TEMP_DIR` | No | `/tmp/discovr-videos` | Temp directory for videos |

## Testing Endpoints

### Campaign Analysis
```bash
curl -X POST http://localhost:8000/ai/campaign/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Summer Sale",
    "description": "Promote our summer collection",
    "target_audience": "18-35 year olds",
    "goals": "Increase sales by 20%"
  }'
```

### Script Review
```bash
curl -X POST http://localhost:8000/ai/script/review \
  -H "Content-Type: application/json" \
  -d '{
    "script_content": "Hey everyone! Today I am reviewing...",
    "campaign_brief": {
      "name": "Product Launch",
      "description": "Launch new product",
      "video_title": "Product Review"
    }
  }'
```

## Troubleshooting

### "OpenRouter API key not found"
- Make sure `.env` file exists and has `OPENROUTER_API_KEY` set

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "Port already in use"
- Change port: `uvicorn app.main:app --port 8001`
- Or kill process using port 8000

### Video processing errors
- Install ffmpeg: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)
- Ensure video URLs are publicly accessible
