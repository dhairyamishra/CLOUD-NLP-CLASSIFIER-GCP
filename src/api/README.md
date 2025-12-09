# FastAPI Inference Server

This directory contains the FastAPI server for text classification inference using the trained DistilBERT model.

## Features

- **FastAPI** web framework with automatic OpenAPI documentation
- **Pydantic** models for request/response validation
- **Automatic model loading** on server startup
- **Health check** endpoint for monitoring
- **Prediction** endpoint with confidence scores
- **CORS** middleware for cross-origin requests
- **Comprehensive error handling** and logging

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Text Classification API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "docs": "/docs",
    "redoc": "/redoc"
  },
  "model": "DistilBERT",
  "status": "running"
}
```

### 2. Health Check
```
GET /health
```
Check if the API server and model are healthy and ready.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": "models/transformer/distilbert",
  "num_classes": 2,
  "classes": ["Normal", "Hate/Offensive"]
}
```

### 3. Predict
```
POST /predict
```
Classify input text and return predicted label with confidence scores.

**Request Body:**
```json
{
  "text": "This is a sample text for classification."
}
```

**Response:**
```json
{
  "predicted_label": "Normal",
  "confidence": 0.9234,
  "scores": [
    {
      "label": "Normal",
      "score": 0.9234
    },
    {
      "label": "Hate/Offensive",
      "score": 0.0766
    }
  ],
  "inference_time_ms": 12.34
}
```

### 4. Interactive Documentation
```
GET /docs
```
Swagger UI interactive API documentation.

```
GET /redoc
```
ReDoc alternative API documentation.

## Running the Server

### Using PowerShell (Windows)
```powershell
.\scripts\run_api_local.ps1
```

### Using Bash (Linux/Mac)
```bash
./scripts/run_api_local.sh
```

### Using Python directly
```bash
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

### Using the server module
```bash
python -m src.api.server
```

## Testing the API

### Using the Example Client
```bash
python scripts/client_example.py
```

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message."}'
```

### Using Python requests
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Prediction
payload = {"text": "This is a test message."}
response = requests.post("http://localhost:8000/predict", json=payload)
print(response.json())
```

## Configuration

The server loads the model from the path specified in `config/config_transformer.yaml`:
```yaml
model_save_dir: "models/transformer/distilbert"
```

## Requirements

The following packages are required (already in `requirements.txt`):
- `fastapi>=0.100.0`
- `uvicorn[standard]>=0.23.0`
- `pydantic>=2.0.0`
- `transformers>=4.30.0`
- `torch>=2.0.0`

## Error Handling

The API provides comprehensive error handling:

- **422 Unprocessable Entity**: Invalid request (e.g., empty text, missing fields)
- **503 Service Unavailable**: Model not loaded
- **500 Internal Server Error**: Prediction failed

## Model Loading

The model is automatically loaded on server startup:
1. Loads the DistilBERT model from `models/transformer/distilbert/`
2. Loads the tokenizer
3. Loads label mappings from `labels.json`
4. Sets the model to evaluation mode
5. Moves the model to the appropriate device (GPU/CPU)

If the model is not found, the server will start but predictions will fail with a 503 error.

## Performance

- **Inference Time**: Typically 10-50ms per request (depending on hardware)
- **Throughput**: Can handle multiple concurrent requests
- **Device**: Automatically uses GPU if available, falls back to CPU

## Development

### Hot Reload
The server supports hot reload during development:
```bash
uvicorn src.api.server:app --reload
```

### Testing
Run the API tests:
```bash
pytest tests/test_api.py -v
```

### Logging
The server provides detailed logging:
- Model loading progress
- Request handling
- Errors and warnings

## Production Deployment

For production deployment, consider:
1. **Remove `--reload` flag** for better performance
2. **Use a production ASGI server** like Gunicorn with Uvicorn workers
3. **Configure CORS** to allow only specific origins
4. **Add authentication** if needed
5. **Use environment variables** for configuration
6. **Set up monitoring** and logging
7. **Use a reverse proxy** like Nginx

Example production command:
```bash
gunicorn src.api.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

## Architecture

```
src/api/
├── __init__.py
├── server.py          # Main FastAPI application
└── README.md          # This file

Key Components:
- ModelManager: Handles model loading and inference
- Pydantic Models: Request/response validation
- FastAPI App: Web server and routing
- Startup Events: Automatic model loading
```

## Troubleshooting

### Model Not Found
```
Error: Model directory not found
Solution: Train the model first using: python -m src.models.transformer_training
```

### Port Already in Use
```
Error: Address already in use
Solution: Use a different port: uvicorn src.api.server:app --port 8001
```

### CUDA Out of Memory
```
Error: CUDA out of memory
Solution: The server will automatically fall back to CPU
```

## Next Steps

- Add batch prediction endpoint
- Implement caching for repeated requests
- Add rate limiting
- Add authentication/authorization
- Deploy to cloud (GCP Cloud Run, AWS Lambda, etc.)
