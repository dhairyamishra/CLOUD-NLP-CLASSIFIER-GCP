# 🚀 Quick Deployment Guide - Your Trained Models

**Model Performance:** 96.29% Accuracy | 17-20ms Inference | Ready for Production!

---

## ⚡ 3 Ways to Deploy (Choose One)

### **Option 1: Local API Server** ⭐ EASIEST
```bash
# Start server
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

# Test it
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"text\": \"This is amazing!\"}"

# Interactive docs
# Open browser: http://localhost:8000/docs
```

**✅ Currently Running!** Your server is live at http://localhost:8000

---

### **Option 2: Docker** ⭐ PRODUCTION READY
```bash
# Build image (one time)
docker build -t cloud-nlp-classifier .

# Run container
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier

# Test it
curl http://localhost:8000/health

# View logs
docker logs -f nlp-api

# Stop
docker stop nlp-api && docker rm nlp-api
```

**Choose Your Model:**
```bash
# High Accuracy (96.29%) - Default
docker run -d -p 8000:8000 cloud-nlp-classifier

# Fast (85-88% accuracy, 10x faster)
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression cloud-nlp-classifier

# Ultra-Fast (85-88% accuracy, 20x faster)
docker run -d -p 8000:8000 -e DEFAULT_MODEL=linear_svm cloud-nlp-classifier
```

---

### **Option 3: Google Cloud Run** ⭐ SERVERLESS
```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Build & push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier

# 3. Deploy
gcloud run deploy cloud-nlp-classifier \
  --image gcr.io/YOUR_PROJECT_ID/cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi

# 4. Get URL
gcloud run services describe cloud-nlp-classifier \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## 🎯 Quick Test Commands

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Make Prediction**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is fantastic!"}'
```

### **List Available Models**
```bash
curl http://localhost:8000/models
```

### **Switch Models (Zero Downtime!)**
```bash
# Switch to fast model
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Switch back to accurate model
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "distilbert"}'
```

### **Python Client**
```bash
# Run example client
python scripts/client_example.py

# Run multi-model client
python scripts/client_multimodel_example.py
```

---

## 📊 Model Comparison

| Model | Accuracy | Speed | Memory | Best For |
|-------|----------|-------|--------|----------|
| **DistilBERT** | 96.29% | 17-20ms | 1.2GB | Highest accuracy |
| **Logistic Regression** | 85-88% | 1.7ms | 100MB | Balanced |
| **Linear SVM** | 85-88% | 0.9ms | 100MB | Ultra-fast |

**Your Current Model:** DistilBERT (96.29% accuracy) ✅

---

## 🔄 Switch Models On-The-Fly

```python
import requests

# Switch to fast model during high traffic
requests.post("http://localhost:8000/models/switch", 
              json={"model_name": "logistic_regression"})

# Switch back during low traffic
requests.post("http://localhost:8000/models/switch", 
              json={"model_name": "distilbert"})
```

**No restart needed!** Switch models in milliseconds.

---

## 🐛 Troubleshooting

### **Server won't start?**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
python -m uvicorn src.api.server:app --port 8001
```

### **Docker build fails?**
```bash
# Check Docker is running
docker ps

# Clean build
docker build --no-cache -t cloud-nlp-classifier .
```

### **Slow predictions?**
```bash
# First request is always slower (warmup)
# Switch to faster model:
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "linear_svm"}'
```

---

## 📚 Full Documentation

For complete details, see: [docs/USING_YOUR_TRAINED_MODELS.md](docs/USING_YOUR_TRAINED_MODELS.md)

---

## ✅ Deployment Checklist

- [x] ✅ Models trained (96.29% accuracy!)
- [x] ✅ API server running (http://localhost:8000)
- [ ] 🔲 Test predictions (`python scripts/client_example.py`)
- [ ] 🔲 Build Docker image
- [ ] 🔲 Test Docker locally
- [ ] 🔲 Deploy to cloud

---

**🎉 Your models are ready! Start with Option 1 (already running!) or build Docker for production.**
