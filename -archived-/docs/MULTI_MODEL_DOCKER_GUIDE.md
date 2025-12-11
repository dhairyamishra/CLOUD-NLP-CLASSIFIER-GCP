# Multi-Model Docker Deployment Guide

## Overview

The Cloud NLP Classifier Docker image now supports **multiple models** with dynamic model switching capabilities. This allows you to choose the best model for your use case without rebuilding the container.

### Available Models

| Model | Type | Description | Speed | Accuracy | Size |
|-------|------|-------------|-------|----------|------|
| **distilbert** | Transformer | DistilBERT fine-tuned model | Slow (~50ms) | Best (90-93%) | ~500MB |
| **logistic_regression** | Baseline | Logistic Regression + TF-IDF | Fast (~5ms) | Good (85-88%) | ~500KB |
| **linear_svm** | Baseline | Linear SVM + TF-IDF | Fast (~5ms) | Good (85-88%) | ~500KB |

---

## Quick Start

### 1. Build Docker Image

```bash
# Build the image with all models
docker build -t cloud-nlp-classifier .
```

### 2. Run with Default Model (DistilBERT)

```bash
# Run with default model (distilbert)
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier
```

### 3. Run with Specific Model

```bash
# Run with Logistic Regression (faster)
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-api cloud-nlp-classifier

# Run with Linear SVM
docker run -d -p 8000:8000 -e DEFAULT_MODEL=linear_svm --name nlp-api cloud-nlp-classifier
```

---

## API Endpoints

### Core Endpoints

#### 1. **GET /** - Root Endpoint
Get API information and available models.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Text Classification API",
  "version": "2.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "models": "/models",
    "switch_model": "/models/switch",
    "docs": "/docs",
    "redoc": "/redoc"
  },
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "status": "running"
}
```

#### 2. **GET /health** - Health Check
Check API health and current model status.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "model_path": "models/transformer/distilbert",
  "num_classes": 4,
  "classes": ["World", "Sports", "Business", "Sci/Tech"]
}
```

#### 3. **POST /predict** - Make Prediction
Classify text using the current model.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple announces new iPhone with advanced AI features"}'
```

**Response:**
```json
{
  "predicted_label": "Sci/Tech",
  "confidence": 0.92,
  "scores": [
    {"label": "Sci/Tech", "score": 0.92},
    {"label": "Business", "score": 0.05},
    {"label": "World", "score": 0.02},
    {"label": "Sports", "score": 0.01}
  ],
  "inference_time_ms": 45.3,
  "model": "distilbert"
}
```

### Model Management Endpoints

#### 4. **GET /models** - List All Models
Get detailed information about all available models.

```bash
curl http://localhost:8000/models
```

**Response:**
```json
{
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "models": {
    "distilbert": {
      "type": "transformer",
      "description": "DistilBERT transformer model (best accuracy)",
      "path": "models/transformer/distilbert",
      "is_current": true
    },
    "logistic_regression": {
      "type": "baseline",
      "description": "Logistic Regression with TF-IDF (fast, interpretable)",
      "path": "models/baselines/logistic_regression_tfidf.joblib",
      "is_current": false
    },
    "linear_svm": {
      "type": "baseline",
      "description": "Linear SVM with TF-IDF (fast, robust)",
      "path": "models/baselines/linear_svm_tfidf.joblib",
      "is_current": false
    }
  }
}
```

#### 5. **POST /models/switch** - Switch Model
Dynamically switch to a different model without restarting the container.

```bash
# Switch to Logistic Regression
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Switch to Linear SVM
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "linear_svm"}'

# Switch back to DistilBERT
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "distilbert"}'
```

**Response:**
```json
{
  "message": "Successfully switched to model 'logistic_regression'",
  "model": "logistic_regression",
  "type": "baseline",
  "num_classes": 4,
  "classes": ["World", "Sports", "Business", "Sci/Tech"]
}
```

---

## Usage Examples

### Python Client Example

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000"

# 1. Check available models
response = requests.get(f"{BASE_URL}/models")
print("Available models:", response.json()["available_models"])

# 2. Switch to fast model (Logistic Regression)
switch_response = requests.post(
    f"{BASE_URL}/models/switch",
    json={"model_name": "logistic_regression"}
)
print("Switched to:", switch_response.json()["model"])

# 3. Make prediction
text = "Apple announces new iPhone with advanced AI features"
predict_response = requests.post(
    f"{BASE_URL}/predict",
    json={"text": text}
)
result = predict_response.json()
print(f"Prediction: {result['predicted_label']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Inference time: {result['inference_time_ms']:.2f}ms")
print(f"Model used: {result['model']}")

# 4. Switch to best accuracy model (DistilBERT)
switch_response = requests.post(
    f"{BASE_URL}/models/switch",
    json={"model_name": "distilbert"}
)
print("Switched to:", switch_response.json()["model"])

# 5. Make prediction with DistilBERT
predict_response = requests.post(
    f"{BASE_URL}/predict",
    json={"text": text}
)
result = predict_response.json()
print(f"Prediction: {result['predicted_label']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Inference time: {result['inference_time_ms']:.2f}ms")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function classifyText() {
  // 1. Check available models
  const modelsResponse = await axios.get(`${BASE_URL}/models`);
  console.log('Available models:', modelsResponse.data.available_models);
  
  // 2. Switch to fast model
  const switchResponse = await axios.post(`${BASE_URL}/models/switch`, {
    model_name: 'logistic_regression'
  });
  console.log('Switched to:', switchResponse.data.model);
  
  // 3. Make prediction
  const text = 'Apple announces new iPhone with advanced AI features';
  const predictResponse = await axios.post(`${BASE_URL}/predict`, {
    text: text
  });
  
  const result = predictResponse.data;
  console.log(`Prediction: ${result.predicted_label}`);
  console.log(`Confidence: ${(result.confidence * 100).toFixed(2)}%`);
  console.log(`Inference time: ${result.inference_time_ms.toFixed(2)}ms`);
  console.log(`Model used: ${result.model}`);
}

classifyText();
```

### cURL Examples

```bash
# Complete workflow
# 1. Check health
curl http://localhost:8000/health

# 2. List models
curl http://localhost:8000/models

# 3. Make prediction with current model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "NASA launches new Mars rover mission"}'

# 4. Switch to faster model
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# 5. Make prediction with new model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "NASA launches new Mars rover mission"}'

# 6. Compare inference times
echo "Testing inference speed..."
time curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Test text for speed comparison"}'
```

---

## Docker Commands

### Basic Operations

```bash
# Build image
docker build -t cloud-nlp-classifier .

# Run with default model (DistilBERT)
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier

# Run with specific model
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-api cloud-nlp-classifier

# View logs
docker logs -f nlp-api

# Stop container
docker stop nlp-api

# Remove container
docker rm nlp-api

# Restart container
docker restart nlp-api
```

### Advanced Operations

```bash
# Run with custom port
docker run -d -p 9000:8000 --name nlp-api cloud-nlp-classifier

# Run with resource limits
docker run -d -p 8000:8000 \
  --memory="2g" \
  --cpus="2" \
  --name nlp-api \
  cloud-nlp-classifier

# Run with environment variables
docker run -d -p 8000:8000 \
  -e DEFAULT_MODEL=logistic_regression \
  -e LOG_LEVEL=DEBUG \
  --name nlp-api \
  cloud-nlp-classifier

# Run in interactive mode (for debugging)
docker run -it -p 8000:8000 cloud-nlp-classifier /bin/bash

# Execute command in running container
docker exec -it nlp-api bash

# Inspect container
docker inspect nlp-api

# View container stats
docker stats nlp-api
```

---

## Model Selection Guide

### When to Use Each Model

#### DistilBERT (Best Accuracy)
**Use when:**
- Accuracy is critical
- You have GPU available
- Latency < 100ms is acceptable
- Processing batch requests

**Characteristics:**
- Accuracy: 90-93%
- Inference time: 45-60ms (CPU), 10-20ms (GPU)
- Memory: ~1.2 GB
- Model size: ~500 MB

#### Logistic Regression (Fast & Interpretable)
**Use when:**
- Speed is critical (< 10ms latency)
- You need interpretable results
- Processing high-volume requests
- Resource-constrained environments

**Characteristics:**
- Accuracy: 85-88%
- Inference time: 3-7ms
- Memory: ~100 MB
- Model size: ~500 KB
- Provides feature importance

#### Linear SVM (Fast & Robust)
**Use when:**
- Speed is critical (< 10ms latency)
- You need robust predictions
- Processing high-volume requests
- Handling noisy data

**Characteristics:**
- Accuracy: 85-88%
- Inference time: 3-7ms
- Memory: ~100 MB
- Model size: ~500 KB
- Good generalization

### Performance Comparison

| Metric | DistilBERT | Logistic Regression | Linear SVM |
|--------|------------|---------------------|------------|
| **Accuracy** | 90-93% | 85-88% | 85-88% |
| **F1 Score** | 0.88-0.91 | 0.82-0.85 | 0.82-0.85 |
| **Inference (CPU)** | 45-60ms | 3-7ms | 3-7ms |
| **Inference (GPU)** | 10-20ms | N/A | N/A |
| **Memory** | ~1.2 GB | ~100 MB | ~100 MB |
| **Throughput** | 20-50 req/s | 200-500 req/s | 200-500 req/s |
| **Startup Time** | 5-8s | 1-2s | 1-2s |

---

## Environment Variables

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `DEFAULT_MODEL` | `distilbert` | Model to load on startup | `logistic_regression` |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output | `1` |
| `LOG_LEVEL` | `INFO` | Logging level | `DEBUG` |

**Usage:**
```bash
docker run -d -p 8000:8000 \
  -e DEFAULT_MODEL=logistic_regression \
  -e LOG_LEVEL=DEBUG \
  --name nlp-api \
  cloud-nlp-classifier
```

---

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  nlp-api:
    build: .
    image: cloud-nlp-classifier
    container_name: nlp-api
    ports:
      - "8000:8000"
    environment:
      - DEFAULT_MODEL=distilbert
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

**Commands:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## Troubleshooting

### Issue: Model not found

**Error:**
```
Model not found: models/baselines/logistic_regression_tfidf.joblib
```

**Solution:**
1. Ensure models are trained:
   ```bash
   python run_baselines.py
   ```
2. Verify models exist:
   ```bash
   ls models/baselines/
   ```
3. Rebuild Docker image:
   ```bash
   docker build -t cloud-nlp-classifier .
   ```

### Issue: Model switch fails

**Error:**
```
Model 'xyz' not available
```

**Solution:**
1. Check available models:
   ```bash
   curl http://localhost:8000/models
   ```
2. Use correct model name:
   - `distilbert`
   - `logistic_regression`
   - `linear_svm`

### Issue: Slow inference with DistilBERT

**Solution:**
1. Switch to faster model:
   ```bash
   curl -X POST http://localhost:8000/models/switch \
     -H "Content-Type: application/json" \
     -d '{"model_name": "logistic_regression"}'
   ```
2. Or use GPU:
   ```bash
   docker run --gpus all -d -p 8000:8000 --name nlp-api cloud-nlp-classifier
   ```

### Issue: Out of memory

**Solution:**
1. Use baseline model (lower memory):
   ```bash
   docker run -d -p 8000:8000 \
     -e DEFAULT_MODEL=logistic_regression \
     --name nlp-api \
     cloud-nlp-classifier
   ```
2. Increase Docker memory limit:
   ```bash
   docker run -d -p 8000:8000 \
     --memory="3g" \
     --name nlp-api \
     cloud-nlp-classifier
   ```

---

## Best Practices

### 1. Model Selection Strategy

```python
# Example: Dynamic model selection based on load
import requests

def get_optimal_model(request_volume):
    """Select model based on current load."""
    if request_volume > 100:  # High load
        return "logistic_regression"  # Fast model
    else:  # Low load
        return "distilbert"  # Best accuracy

# Switch model based on load
optimal_model = get_optimal_model(current_load)
requests.post(
    "http://localhost:8000/models/switch",
    json={"model_name": optimal_model}
)
```

### 2. Health Monitoring

```bash
# Monitor health continuously
while true; do
  curl -s http://localhost:8000/health | jq '.status, .current_model'
  sleep 30
done
```

### 3. Performance Testing

```bash
# Benchmark different models
for model in distilbert logistic_regression linear_svm; do
  echo "Testing $model..."
  curl -X POST http://localhost:8000/models/switch \
    -H "Content-Type: application/json" \
    -d "{\"model_name\": \"$model\"}"
  
  # Run 100 predictions and measure time
  time for i in {1..100}; do
    curl -s -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"text": "Test text"}' > /dev/null
  done
done
```

### 4. Load Balancing

For high-traffic scenarios, run multiple containers:

```bash
# Start 3 containers with different models
docker run -d -p 8001:8000 -e DEFAULT_MODEL=distilbert --name nlp-api-1 cloud-nlp-classifier
docker run -d -p 8002:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-api-2 cloud-nlp-classifier
docker run -d -p 8003:8000 -e DEFAULT_MODEL=linear_svm --name nlp-api-3 cloud-nlp-classifier

# Use nginx or load balancer to distribute requests
```

---

## API Documentation

Access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Summary

✅ **Multi-Model Support**: 3 models available (DistilBERT, Logistic Regression, Linear SVM)  
✅ **Dynamic Switching**: Change models without restarting container  
✅ **Environment Configuration**: Set default model via `DEFAULT_MODEL`  
✅ **Performance Options**: Choose speed vs accuracy based on needs  
✅ **Production Ready**: Health checks, CORS, error handling  
✅ **Easy to Use**: RESTful API with comprehensive documentation  

**Next Steps:**
1. Build and run the Docker image
2. Test all three models with your data
3. Choose the best model for your use case
4. Deploy to production (GCP Cloud Run, AWS ECS, etc.)
