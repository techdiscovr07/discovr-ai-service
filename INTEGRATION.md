# Integration Guide

## How Go Backend Calls AI Service

The Go backend (`discovr-backend`) calls this AI service via HTTP REST API.

### Architecture

```
Frontend (Next.js)
    ↓ HTTP
Go Backend (discovr-backend)
    ↓ HTTP REST
Python AI Service (discovr-ai-service) ← You are here
    ↓ REST API
OpenRouter / LLMs
```

### Go Backend Integration

The Go backend has an AI handler at `internal/ai/handler.go` that calls this service:

```go
aiHandler := ai.NewHandler("http://your-ai-service-url", "api-key")
result, err := aiHandler.AnalyzeCampaign(ctx, request)
```

### Endpoints Called by Go Backend

1. **Campaign Analysis**
   - Go endpoint: `POST /brand/campaigns/ai/analyze`
   - Calls: `POST http://ai-service/ai/campaign/analyze`

2. **Script Review**
   - Go endpoint: `POST /brand/campaigns/ai/review-script`
   - Calls: `POST http://ai-service/ai/script/review`

3. **Video Review**
   - Go endpoint: `POST /brand/campaigns/ai/review-video`
   - Calls: `POST http://ai-service/ai/video/review`

### Authentication

The Go backend can authenticate with this service using:
- API key in `Authorization: Bearer <api-key>` header
- Set `AI_SERVICE_API_KEY` in Go backend `.env`
- Set `AI_SERVICE_API_KEY` in this service `.env` (for validation)

### Deployment

1. **Deploy AI Service** (separate from Go backend)
   - Render, Railway, Fly.io, etc.
   - Get URL: `https://discovr-ai-service.onrender.com`

2. **Update Go Backend Config**
   ```bash
   AI_SERVICE_URL=https://discovr-ai-service.onrender.com
   AI_SERVICE_API_KEY=your-secret-key
   ```

3. **Test Integration**
   ```bash
   # From Go backend, test AI service
   curl -X POST http://localhost:8080/brand/campaigns/ai/analyze \
     -H "Authorization: Bearer <go-backend-token>" \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

### Error Handling

If AI service is unavailable:
- Go backend should handle gracefully
- Return error to frontend
- Frontend shows fallback UI (manual review)

### CORS

This service allows CORS from:
- Go backend domain
- Frontend domain
- Configure in `app/main.py` if needed
