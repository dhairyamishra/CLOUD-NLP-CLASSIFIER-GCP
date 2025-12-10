# 🚀 Quick Start: Full-Stack Deployment

## Deploy Backend API + Frontend UI to GCP in 30 Minutes

---

## ⚡ TL;DR - Just Run These Commands

```powershell
# Step 1: Deploy Backend API (if not already deployed)
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Step 2: Deploy Frontend UI
.\scripts\gcp-deploy-ui.ps1

# Step 3: Open in browser
# http://YOUR_IP:8501
```

**That's it!** 🎉

---

## 📋 Prerequisites

- ✅ GCP account with billing enabled
- ✅ `gcloud` CLI installed and configured
- ✅ Git repository pushed to GitHub
- ✅ Models trained locally (in `models/` directory)
- ✅ PowerShell (Windows) or Bash (Linux/Mac)

---

## 🎯 Step-by-Step Guide

### Step 1: Deploy Backend API (20 minutes)

If you haven't deployed the API yet:

```powershell
# Navigate to project directory
cd C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP

# Deploy API with optimized model upload
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**What this does:**
- ✅ Creates GCS bucket for models
- ✅ Uploads models (770 MB, ~3 minutes)
- ✅ Creates/starts VM (e2-standard-2)
- ✅ Clones code from GitHub
- ✅ Downloads models from GCS
- ✅ Builds Docker image (~10 minutes)
- ✅ Starts API container
- ✅ Tests health endpoints

**Expected Output:**
```
[OK] Your NLP API is now live!
API Endpoints:
  Health:  http://35.232.76.140:8000/health
  Predict: http://35.232.76.140:8000/predict
  Docs:    http://35.232.76.140:8000/docs
```

**Save your External IP!** You'll need it to access the UI.

---

### Step 2: Deploy Frontend UI (5 minutes)

```powershell
# Deploy UI to the same VM
.\scripts\gcp-deploy-ui.ps1
```

**What this does:**
- ✅ Verifies API is running
- ✅ Creates firewall rule for port 8501
- ✅ Pulls latest code
- ✅ Builds lightweight UI image (~3 minutes)
- ✅ Starts UI container
- ✅ Tests connectivity

**Expected Output:**
```
[OK] Your full-stack NLP app is now live!

Backend API:
  Health:  http://35.232.76.140:8000/health
  Docs:    http://35.232.76.140:8000/docs

Frontend UI:
  URL:     http://35.232.76.140:8501
```

---

### Step 3: Access Your App

**Open in Browser:**
```
http://YOUR_EXTERNAL_IP:8501
```

**You should see:**
- 🎨 Beautiful Streamlit interface
- 🤖 Model selection dropdown
- 💬 Chat-style interaction
- 📊 Real-time predictions
- 🔄 Dynamic model switching

**Try it:**
1. Enter text: "I love this product!"
2. Click "🚀 Analyze"
3. See prediction results with confidence scores
4. Switch models and try again

---

## 🧪 Test Locally First (Optional)

Before deploying to GCP, test everything locally:

```powershell
# Test full-stack with docker-compose
.\scripts\test-fullstack-local.ps1

# Or manually
docker-compose -f docker-compose.fullstack.yml up -d

# Access locally
# API:  http://localhost:8000/docs
# UI:   http://localhost:8501

# Stop when done
docker-compose -f docker-compose.fullstack.yml down
```

---

## 🔍 Verify Deployment

### Check Container Status

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Check both containers are running
sudo docker ps

# Should see:
# CONTAINER ID   IMAGE                    PORTS                    NAMES
# xxxxx          cloud-nlp-classifier     0.0.0.0:8000->8000/tcp   nlp-api
# xxxxx          cloud-nlp-ui             0.0.0.0:8501->8501/tcp   nlp-ui
```

### Test Endpoints

```bash
# Test API
curl http://localhost:8000/health
# {"status":"healthy","model_loaded":true,...}

# Test UI
curl http://localhost:8501/_stcore/health
# {"status":"ok"}

# Test from outside VM
curl http://YOUR_IP:8000/health
curl http://YOUR_IP:8501
```

---

## 📊 What You Get

### Architecture

```
┌─────────────────────────────────────────┐
│  GCP VM: nlp-classifier-vm             │
│  External IP: 35.232.76.140            │
│                                         │
│  ┌─────────────┐    ┌───────────────┐ │
│  │  nlp-api    │◄───┤  nlp-ui       │ │
│  │  Port: 8000 │    │  Port: 8501   │ │
│  │  FastAPI    │    │  Streamlit    │ │
│  │  + Models   │    │  API Client   │ │
│  └─────────────┘    └───────────────┘ │
└─────────────────────────────────────────┘
       │                      │
       ▼                      ▼
  API Endpoints          Web Interface
```

### Features

**Backend API (Port 8000):**
- ✅ 3 ML models (DistilBERT, Logistic Regression, Linear SVM)
- ✅ Dynamic model switching
- ✅ REST API with OpenAPI docs
- ✅ Health checks and monitoring
- ✅ 0.6-8ms inference time

**Frontend UI (Port 8501):**
- ✅ Beautiful Streamlit interface
- ✅ Chat-style interaction
- ✅ Real-time predictions
- ✅ Model selection and switching
- ✅ Confidence scores and probabilities
- ✅ Inference time display

---

## 💰 Cost

**Monthly Cost: ~$56**
- VM (e2-standard-2): $49/month
- Static IP: $7/month
- GCS Storage (1GB): $0.02/month
- UI Container: $0 (same VM)

**Cost Optimization:**
```bash
# Stop VM when not in use
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a

# Start when needed
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
```

---

## 🛠️ Common Commands

### View Logs

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# API logs
sudo docker logs -f nlp-api

# UI logs
sudo docker logs -f nlp-ui

# Both logs
sudo docker logs -f nlp-api & sudo docker logs -f nlp-ui
```

### Restart Services

```bash
# Restart API
sudo docker restart nlp-api

# Restart UI
sudo docker restart nlp-ui

# Restart both
sudo docker restart nlp-api nlp-ui
```

### Update Code

```bash
# 1. Make changes locally and push to GitHub
git add .
git commit -m "Update code"
git push

# 2. Redeploy UI (pulls latest code automatically)
.\scripts\gcp-deploy-ui.ps1

# 3. Or redeploy both
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
.\scripts\gcp-deploy-ui.ps1
```

---

## 🐛 Troubleshooting

### UI Shows "Cannot Connect to API"

```bash
# Check API is running
sudo docker ps | grep nlp-api

# Check API health
curl http://localhost:8000/health

# Restart UI
sudo docker restart nlp-ui
```

### Container Not Starting

```bash
# Check logs
sudo docker logs nlp-api
sudo docker logs nlp-ui

# Check disk space
df -h

# Check memory
free -h
```

### Cannot Access from Browser

```bash
# Check firewall rules
gcloud compute firewall-rules list | grep -E "8000|8501"

# Should see:
# - allow-http (port 8000)
# - allow-streamlit (port 8501)

# If missing, redeploy UI
.\scripts\gcp-deploy-ui.ps1
```

---

## 🔄 Update Workflow

### Update UI Only

```powershell
# 1. Make UI changes
# 2. Commit and push
git add src/ui/
git commit -m "Update UI"
git push

# 3. Redeploy UI
.\scripts\gcp-deploy-ui.ps1
```

### Update API Only

```powershell
# 1. Make API changes
# 2. Commit and push
git add src/api/
git commit -m "Update API"
git push

# 3. Redeploy API (skip model upload)
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

### Update Both

```powershell
# 1. Make changes
# 2. Commit and push
git add .
git commit -m "Update full-stack"
git push

# 3. Redeploy both
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
.\scripts\gcp-deploy-ui.ps1
```

---

## 📚 Next Steps

### Enhance Your App

1. **Add Authentication**
   - Implement user login
   - Add API keys
   - Rate limiting

2. **Add More Features**
   - Batch predictions
   - Export results
   - History tracking
   - Analytics dashboard

3. **Optimize Performance**
   - Add caching
   - Load balancing
   - Auto-scaling

4. **Add Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert notifications

### Production Hardening

1. **Security**
   - Enable HTTPS (SSL/TLS)
   - Add authentication
   - Implement rate limiting
   - Regular security updates

2. **Reliability**
   - Set up backups
   - Implement CI/CD
   - Add health monitoring
   - Configure auto-restart

3. **Scalability**
   - Use managed services (Cloud Run)
   - Add load balancer
   - Implement caching
   - Optimize database

---

## 📖 Documentation

- [UI Deployment Guide](./docs/UI_DEPLOYMENT_GUIDE.md) - Detailed UI deployment
- [Frontend Deployment Plan](./docs/FRONTEND_DEPLOYMENT_PLAN.md) - Architecture and planning
- [Backend vs Frontend](./docs/BACKEND_VS_FRONTEND_DEPLOYMENT.md) - Comparison
- [Docker Guide](./docs/DOCKER_GUIDE.md) - Docker best practices
- [GCP Deployment Progress](./GCP_DEPLOYMENT_PROGRESS.md) - Overall status

---

## ✅ Success Checklist

After following this guide, you should have:

- ✅ API running at `http://YOUR_IP:8000`
- ✅ UI running at `http://YOUR_IP:8501`
- ✅ Both containers healthy
- ✅ UI can connect to API
- ✅ Predictions work end-to-end
- ✅ Model switching works
- ✅ Auto-restart enabled
- ✅ Firewall rules configured
- ✅ Total cost: ~$56/month

---

## 🎉 You're Done!

Your full-stack NLP application is now live on GCP!

**Share your app:**
- API Docs: `http://YOUR_IP:8000/docs`
- Web Interface: `http://YOUR_IP:8501`

**Questions?** Check the troubleshooting section or view detailed documentation.

---

**Last Updated:** 2025-12-10  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION READY
