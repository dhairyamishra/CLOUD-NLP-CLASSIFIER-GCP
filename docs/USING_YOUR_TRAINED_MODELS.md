# Using Your Newly Trained Models - Complete Guide

**Last Updated:** December 9, 2024  
**Model Performance:** 96.29% Accuracy | 2.24ms Avg Inference | 98.99% ROC-AUC

---

## 📊 Your Current Models

You have **3 trained models** ready for deployment:

| Model | Type | Accuracy | Inference Time | Best For |
|-------|------|----------|----------------|----------|
| **DistilBERT** | Transformer | 96.29% | 17-20ms | Highest accuracy |
| **Logistic Regression** | Baseline | 85-88% | 0.6-1.7ms | Speed & interpretability |
| **Linear SVM** | Baseline | 85-88% | 0.6-0.9ms | Ultra-fast predictions |

### Model Locations
```
models/
├── transformer/distilbert/          # Your newly trained DistilBERT
│   ├── model.safetensors           # 267 MB model weights
│   ├── config.json                 # Model configuration
│   ├── tokenizer_config.json       # Tokenizer settings
│   ├── vocab.txt                   # Vocabulary
│   ├── labels.json                 # Class labels
│   └── training_info.json          # Training metrics
└── baselines/
    ├── logistic_regression_tfidf.joblib  # 459 KB
    └── linear_svm_tfidf.joblib           # 459 KB
```

---

## 🚀 Deployment Options

### **Option 1: Local API Server (Currently Running!)**

#### ✅ **Your Server is Already Running**
```bash
# Server URL
http://localhost:8000

# Current Model: DistilBERT (96.29% accuracy)
# Status: ✅ READY
```

#### **Available Endpoints**

##### 1. **Health Check**
```bash
# PowerShell
curl http://localhost:8000/health

# Response
{
  "status": "ok",
  "model_loaded": true,
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "num_classes": 2,
  "classes": ["0", "1"]
}
```

##### 2. **Make Predictions**
```bash
# PowerShell
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"text": "This is an amazing product!"}'

# Response
{
  "predicted_label": "0",
  "confidence": 0.9774,
  "scores": [
    {"label": "0", "score": 0.9774},
    {"label": "1", "score": 0.0226}
  ],
  "inference_time_ms": 17.2
}
```

##### 3. **List Available Models**
```bash
curl http://localhost:8000/models

# Response
{
  "current_model": "distilbert",
  "available_models": [
    {
      "name": "distilbert",
      "type": "transformer",
      "description": "DistilBERT transformer model (best accuracy)",
      "path": "models/transformer/distilbert"
    },
    {
      "name": "logistic_regression",
      "type": "baseline",
      "description": "Logistic Regression with TF-IDF (fast, interpretable)",
      "path": "models/baselines/logistic_regression_tfidf.joblib"
    },
    {
      "name": "linear_svm",
      "type": "baseline",
      "description": "Linear SVM with TF-IDF (fast, robust)",
      "path": "models/baselines/linear_svm_tfidf.joblib"
    }
  ]
}
```

##### 4. **Switch Models (Zero Downtime!)**
```bash
# Switch to faster Logistic Regression model
curl -X POST http://localhost:8000/models/switch `
  -H "Content-Type: application/json" `
  -d '{"model_name": "logistic_regression"}'

# Response
{
  "message": "Successfully switched to model: logistic_regression",
  "previous_model": "distilbert",
  "current_model": "logistic_regression"
}

# Switch back to DistilBERT
curl -X POST http://localhost:8000/models/switch `
  -H "Content-Type: application/json" `
  -d '{"model_name": "distilbert"}'
```

#### **Interactive API Documentation**
```bash
# Open in browser
http://localhost:8000/docs        # Swagger UI (interactive)
http://localhost:8000/redoc       # ReDoc (clean documentation)
```

#### **Python Client Example**
```python
# Use the provided client
python scripts/client_example.py

# Or use the multi-model client
python scripts/client_multimodel_example.py
```

---

### **Option 2: Docker Deployment (Production Ready)**

#### **Build Docker Image with Your New Models**
```bash
# Build image (includes all 3 models)
docker build -t cloud-nlp-classifier:latest .

# Image size: ~2.1 GB
# Build time: 5-10 minutes (first time), 1-2 min (cached)
```

#### **Run with Different Models**

##### **A. Run with DistilBERT (Default - Best Accuracy)**
```bash
docker run -d \
  -p 8000:8000 \
  --name nlp-api \
  cloud-nlp-classifier:latest

# Test
curl http://localhost:8000/health
```

##### **B. Run with Logistic Regression (Fast)**
```bash
docker run -d \
  -p 8000:8000 \
  -e DEFAULT_MODEL=logistic_regression \
  --name nlp-api-fast \
  cloud-nlp-classifier:latest

# 10x faster inference (0.6-1.7ms)
```

##### **C. Run with Linear SVM (Ultra-Fast)**
```bash
docker run -d \
  -p 8000:8000 \
  -e DEFAULT_MODEL=linear_svm \
  --name nlp-api-ultrafast \
  cloud-nlp-classifier:latest

# 20x faster inference (0.6-0.9ms)
```

#### **Docker Management**
```bash
# View logs
docker logs -f nlp-api

# Stop container
docker stop nlp-api

# Remove container
docker rm nlp-api

# View running containers
docker ps

# Check resource usage
docker stats nlp-api
```

#### **Docker Compose (Multi-Container)**
```bash
# Run full stack (API + UI)
docker-compose -f docker-compose.full.yml up -d

# Run API only
docker-compose -f docker-compose.api-only.yml up -d

# Run with different models
docker-compose -f docker-compose.prod.yml up -d

# Stop all
docker-compose down
```

---

### **Option 3: Cloud Deployment (GCP/AWS/Azure)**

#### **A. Google Cloud Run (Serverless)**

##### **Prerequisites**
```bash
# Install gcloud CLI
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

##### **Deploy to Cloud Run**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier

# Deploy to Cloud Run
gcloud run deploy cloud-nlp-classifier \
  --image gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars DEFAULT_MODEL=distilbert

# Get service URL
gcloud run services describe cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

##### **Deploy with Different Models**
```bash
# Fast model (Logistic Regression)
gcloud run deploy cloud-nlp-classifier-fast \
  --image gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier \
  --set-env-vars DEFAULT_MODEL=logistic_regression \
  --memory 1Gi \
  --cpu 1

# Ultra-fast model (Linear SVM)
gcloud run deploy cloud-nlp-classifier-ultrafast \
  --image gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier \
  --set-env-vars DEFAULT_MODEL=linear_svm \
  --memory 1Gi \
  --cpu 1
```

##### **Test Cloud Deployment**
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test prediction
curl -X POST $SERVICE_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!"}'
```

#### **B. AWS Elastic Container Service (ECS)**

```bash
# Build and push to ECR
aws ecr create-repository --repository-name cloud-nlp-classifier
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag cloud-nlp-classifier:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cloud-nlp-classifier:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cloud-nlp-classifier:latest

# Deploy to ECS (use AWS Console or CLI)
```

#### **C. Azure Container Instances**

```bash
# Login to Azure
az login

# Create resource group
az group create --name nlp-classifier-rg --location eastus

# Create container registry
az acr create --resource-group nlp-classifier-rg --name nlpclassifieracr --sku Basic

# Push image
az acr login --name nlpclassifieracr
docker tag cloud-nlp-classifier:latest nlpclassifieracr.azurecr.io/cloud-nlp-classifier:latest
docker push nlpclassifieracr.azurecr.io/cloud-nlp-classifier:latest

# Deploy container
az container create \
  --resource-group nlp-classifier-rg \
  --name nlp-classifier \
  --image nlpclassifieracr.azurecr.io/cloud-nlp-classifier:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables DEFAULT_MODEL=distilbert
```

---

## 🔄 Switching Between Models

### **Why Switch Models?**

| Scenario | Recommended Model | Reason |
|----------|------------------|--------|
| **High accuracy needed** | DistilBERT | 96.29% accuracy, best performance |
| **Low latency required** | Linear SVM | 0.6-0.9ms inference (20x faster) |
| **Balanced performance** | Logistic Regression | 85-88% accuracy, 1.7ms inference |
| **High traffic** | Linear SVM or Logistic | Handle 1500+ req/s |
| **Limited resources** | Baseline models | 100MB vs 1.2GB memory |

### **Runtime Model Switching**

```python
import requests

# Switch to fast model during high traffic
response = requests.post(
    "http://localhost:8000/models/switch",
    json={"model_name": "logistic_regression"}
)
print(response.json())
# {"message": "Successfully switched to model: logistic_regression"}

# Switch back to accurate model during low traffic
response = requests.post(
    "http://localhost:8000/models/switch",
    json={"model_name": "distilbert"}
)
```

### **Load Balancing Strategy**
```bash
# Run multiple containers with different models
docker run -d -p 8001:8000 -e DEFAULT_MODEL=distilbert --name nlp-accurate cloud-nlp-classifier
docker run -d -p 8002:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-fast cloud-nlp-classifier
docker run -d -p 8003:8000 -e DEFAULT_MODEL=linear_svm --name nlp-ultrafast cloud-nlp-classifier

# Use nginx or load balancer to route:
# - High priority requests → Port 8001 (DistilBERT)
# - Normal requests → Port 8002 (Logistic Regression)
# - Bulk/batch requests → Port 8003 (Linear SVM)
```

---

## 📈 Performance Benchmarks

### **Your New DistilBERT Model**
```
Training Metrics:
├── Accuracy: 96.29%
├── F1 Score (Macro): 93.44%
├── F1 Score (Weighted): 96.31%
├── Precision (Macro): 92.89%
├── Recall (Macro): 94.03%
├── ROC-AUC: 98.99%
├── Training Time: 10.44 minutes
└── Avg Inference: 2.24ms (test set)

Production Performance:
├── First Request: 455ms (model warmup)
├── Subsequent Requests: 17-20ms
├── Throughput: ~50-60 req/s (single worker)
└── Memory Usage: ~1.2 GB
```

### **Baseline Models**
```
Logistic Regression:
├── Accuracy: 85-88%
├── Inference: 0.6-1.7ms
├── Throughput: ~1500 req/s
└── Memory: ~100 MB

Linear SVM:
├── Accuracy: 85-88%
├── Inference: 0.6-0.9ms
├── Throughput: ~1600 req/s
└── Memory: ~100 MB
```

---

## 🧪 Testing Your Deployment

### **1. Quick Health Check**
```bash
curl http://localhost:8000/health
```

### **2. Single Prediction**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Your test text here"}'
```

### **3. Comprehensive Testing**
```bash
# Test all models
python scripts/client_multimodel_example.py

# Performance testing
python tests/test_performance.ps1

# API endpoint testing
python test_api_endpoints.py
```

### **4. Load Testing**
```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Test with 1000 requests, 10 concurrent
ab -n 1000 -c 10 -p request.json -T application/json http://localhost:8000/predict

# request.json content:
# {"text": "This is a test message"}
```

### **5. Docker Testing**
```bash
# Test multi-model Docker
.\test_multimodel_docker.ps1

# Test API in Docker
.\test_docker_api.ps1

# Performance testing
.\test_performance.ps1
```

---

## 🔧 Troubleshooting

### **Issue: Model Not Loading**
```bash
# Check model files exist
ls models/transformer/distilbert/
# Should see: model.safetensors, config.json, tokenizer_config.json, etc.

# Check logs
docker logs nlp-api

# Verify model path in server.py
# Default: models/transformer/distilbert
```

### **Issue: Slow Inference**
```bash
# First request is always slower (model warmup)
# Solution: Send a dummy request after startup

# If consistently slow:
# 1. Check CPU/memory usage
# 2. Switch to faster model (logistic_regression or linear_svm)
# 3. Enable GPU if available
```

### **Issue: Out of Memory**
```bash
# DistilBERT uses ~1.2GB memory
# Solutions:
# 1. Increase Docker memory limit
docker run -m 2g -p 8000:8000 cloud-nlp-classifier

# 2. Use baseline model (100MB memory)
docker run -e DEFAULT_MODEL=logistic_regression cloud-nlp-classifier

# 3. Reduce batch size in config
```

### **Issue: Container Won't Start**
```bash
# Check logs
docker logs nlp-api

# Common issues:
# 1. Port already in use → Change port: -p 8001:8000
# 2. Model files missing → Rebuild image
# 3. Insufficient memory → Increase Docker memory
```

---

## 📚 Additional Resources

### **Documentation**
- [API Documentation](../src/api/README.md)
- [Docker Guide](DOCKER_GUIDE.md)
- [Multi-Model Guide](MULTI_MODEL_DOCKER_GUIDE.md)
- [Performance Summary](PHASE9_PERFORMANCE_SUMMARY.md)
- [Training Guide](PHASE10_ADVANCED_TRAINING_SUMMARY.md)

### **Scripts**
```bash
# API Server
scripts/run_api_local.ps1              # Windows
scripts/run_api_local.sh               # Linux/Mac

# Client Examples
scripts/client_example.py              # Basic client
scripts/client_multimodel_example.py   # Multi-model client

# Testing
tests/test_api.py                      # API tests
test_api_endpoints.py                  # Endpoint tests
test_multimodel_docker.ps1             # Multi-model tests
test_performance.ps1                   # Performance tests
```

### **Configuration Files**
```bash
config/config_transformer.yaml         # Local training config
config/config_transformer_cloud.yaml   # Cloud training config
config/config_baselines.yaml           # Baseline models config
```

---

## 🎯 Quick Start Checklist

- [x] ✅ **Models Trained** (96.29% accuracy!)
- [x] ✅ **API Server Running** (http://localhost:8000)
- [ ] 🔲 **Test Predictions** (`python scripts/client_example.py`)
- [ ] 🔲 **Build Docker Image** (`docker build -t cloud-nlp-classifier .`)
- [ ] 🔲 **Test Docker Deployment** (`docker run -p 8000:8000 cloud-nlp-classifier`)
- [ ] 🔲 **Deploy to Cloud** (GCP/AWS/Azure)
- [ ] 🔲 **Set Up Monitoring** (logs, metrics, alerts)
- [ ] 🔲 **Configure CI/CD** (automated deployments)

---

## 🚀 Next Steps

### **Immediate (Today)**
1. ✅ Test local API server (DONE - Running!)
2. Test all 3 models with `client_multimodel_example.py`
3. Build Docker image with your new models
4. Test Docker deployment locally

### **Short Term (This Week)**
1. Deploy to cloud platform (GCP Cloud Run recommended)
2. Set up monitoring and logging
3. Configure auto-scaling
4. Add authentication if needed

### **Long Term (This Month)**
1. Set up CI/CD pipeline
2. Add A/B testing for models
3. Implement model versioning
4. Add batch prediction endpoint
5. Set up model retraining pipeline

---

## 💡 Pro Tips

### **1. Model Selection Strategy**
```python
# Use this decision tree:
if accuracy_critical and latency_ok:
    use_model = "distilbert"  # 96.29% accuracy, 17-20ms
elif high_traffic or low_latency_critical:
    use_model = "linear_svm"  # 85-88% accuracy, 0.6-0.9ms
else:
    use_model = "logistic_regression"  # Balanced: 85-88%, 1.7ms
```

### **2. Cost Optimization**
```bash
# Cloud Run pricing (pay per request):
# - DistilBERT: ~$0.10 per 1000 requests (2GB memory, 2 CPU)
# - Baseline models: ~$0.02 per 1000 requests (512MB memory, 1 CPU)

# Save 80% by using baseline models for non-critical requests!
```

### **3. Zero-Downtime Deployment**
```bash
# Use model switching instead of redeploying:
# 1. Deploy with DistilBERT
# 2. Switch to fast model during high traffic
# 3. Switch back during low traffic
# No container restart needed!
```

### **4. Monitoring**
```python
# Track these metrics:
# - Inference time per model
# - Prediction distribution
# - Error rates
# - Memory usage
# - Request throughput

# Use /health endpoint for health checks
# Use /models endpoint for model inventory
```

---

## 📞 Support

**Issues?** Check the troubleshooting section above or review:
- Server logs: `docker logs nlp-api`
- API docs: http://localhost:8000/docs
- Project README: [README.md](../README.md)

**Performance Questions?** See:
- [PHASE9_PERFORMANCE_SUMMARY.md](PHASE9_PERFORMANCE_SUMMARY.md)
- [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md)

---

**🎉 Congratulations! Your models are production-ready with 96.29% accuracy!**
