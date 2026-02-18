# Quick Start Guide

Get the AI service running in 5 minutes!

## 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
# Edit .env and add: OPENROUTER_API_KEY=sk-or-v1-...
```

## 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

## 4. Test

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## 5. Integrate with Go Backend

In your Go backend `.env`:
```bash
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-secret-key
```

That's it! 🎉

For detailed setup, see [SETUP.md](./SETUP.md)
