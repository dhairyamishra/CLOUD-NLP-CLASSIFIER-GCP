# UI Deployment Guide

## 🎯 Overview

This guide explains how to deploy the Streamlit frontend UI to GCP alongside the existing FastAPI backend.

---

## 📋 Prerequisites

Before deploying the UI, ensure:

1. ✅ **Backend API is deployed** - Run `gcp-complete-deployment.ps1` first
2. ✅ **API is healthy** - Verify at `http://YOUR_IP:8000/health`
3. ✅ **VM is running** - `nlp-classifier-vm` in GCP
4. ✅ **Code is committed** - Latest changes pushed to GitHub

---

## 🚀 Quick Deployment

### Option 1: Deploy to GCP (Production)

```powershell
# Deploy UI to the same VM as the API
.\scripts\gcp-deploy-ui.ps1

# With custom parameters
.\scripts\gcp-deploy-ui.ps1 -VMName "nlp-classifier-vm" -Zone "us-central1-a"

# Skip firewall setup (if already configured)
.\scripts\gcp-deploy-ui.ps1 -SkipFirewall
```

**Expected Duration:** 5-10 minutes

**What it does:**
1. Verifies API is running
2. Creates firewall rule for port 8501
3. Pulls latest code on VM
4. Builds lightweight UI Docker image (~500MB)
5. Starts UI container with API_URL=http://localhost:8000
6. Tests health endpoints

### Option 2: Test Locally (Development)

```powershell
# Test full-stack locally with docker-compose
.\scripts\test-fullstack-local.ps1

# Or manually
docker-compose -f docker-compose.fullstack.yml up -d

# View logs
docker-compose -f docker-compose.fullstack.yml logs -f

# Stop
docker-compose -f docker-compose.fullstack.yml down
```

---

## 🏗️ Architecture

### Deployment Architecture

```
GCP VM: nlp-classifier-vm (35.232.76.140)
├── Container: nlp-api (port 8000)
│   ├── FastAPI server
│   ├── ML models (DistilBERT, Logistic Regression, Linear SVM)
│   └── Model switching API
│
└── Container: nlp-ui (port 8501)
    ├── Streamlit app
    ├── API client (no models)
    └── Connects to nlp-api via localhost:8000
```

### Network Flow

```
User Browser
    │
    ├─────────────────┬─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
Port 8000         Port 8501       Port 22 (SSH)
(API Docs)        (UI)            (Management)
    │                 │                 │
    └─────────────────┴─────────────────┘
                      │
                      ▼
          VM: nlp-classifier-vm
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
   nlp-api (8000)              nlp-ui (8501)
        │                           │
        │    localhost:8000         │
        │◄──────────────────────────┘
        │
   ML Models
```

---

## 📦 What Gets Deployed

### Files Created

1. **`Dockerfile.streamlit.api`** - Lightweight UI container
   - Size: ~500MB (vs 2.5GB for API)
   - No ML models included
   - Only Streamlit + requests

2. **`src/ui/streamlit_app_api.py`** - API-mode Streamlit app
   - Connects to FastAPI backend
   - Dynamic model selection
   - Real-time predictions

3. **`src/ui/utils/api_inference.py`** - API client
   - HTTP requests to backend
   - Retry logic
   - Error handling

4. **`scripts/gcp-deploy-ui.ps1`** - Deployment script
   - Follows backend pattern
   - Comprehensive error handling
   - Health checks

---

## 🔧 Configuration

### Environment Variables

The UI container uses these environment variables:

```bash
# API endpoint (set automatically by deployment script)
API_URL=http://localhost:8000

# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Firewall Rules

The deployment script creates this firewall rule:

```bash
Name: allow-streamlit
Direction: INGRESS
Priority: 1000
Network: default
Action: ALLOW
Rules: tcp:8501
Source: 0.0.0.0/0
Target tags: http-server
```

---

## ✅ Verification

### After Deployment

1. **Check Container Status**
   ```bash
   # SSH into VM
   gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
   
   # Check both containers
   sudo docker ps
   
   # Should see:
   # - nlp-api (port 8000)
   # - nlp-ui (port 8501)
   ```

2. **Test API Health**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", ...}
   ```

3. **Test UI Health**
   ```bash
   curl http://localhost:8501/_stcore/health
   # Should return: {"status": "ok"}
   ```

4. **Test External Access**
   ```bash
   # From your local machine
   curl http://35.232.76.140:8000/health  # API
   curl http://35.232.76.140:8501         # UI
   ```

5. **Test in Browser**
   - Open: `http://35.232.76.140:8501`
   - Should see Streamlit UI
   - Enter text and click "Analyze"
   - Should get prediction results

---

## 🐛 Troubleshooting

### UI Container Not Starting

```bash
# Check logs
sudo docker logs nlp-ui

# Common issues:
# 1. API not running - check: sudo docker ps | grep nlp-api
# 2. Port conflict - check: sudo netstat -tulpn | grep 8501
# 3. Build failed - check: sudo docker images | grep nlp-ui
```

### Cannot Connect to API

```bash
# From inside UI container
sudo docker exec -it nlp-ui curl http://localhost:8000/health

# If fails:
# 1. Check API is running: sudo docker ps | grep nlp-api
# 2. Check API health: curl http://localhost:8000/health
# 3. Check network: sudo docker network inspect nlp-network
```

### UI Shows "Cannot Connect to API"

**Symptoms:** UI loads but shows connection error

**Solutions:**
1. Check API_URL environment variable:
   ```bash
   sudo docker inspect nlp-ui | grep API_URL
   # Should show: API_URL=http://localhost:8000
   ```

2. Restart UI container:
   ```bash
   sudo docker restart nlp-ui
   ```

3. Check API from UI container:
   ```bash
   sudo docker exec -it nlp-ui curl http://localhost:8000/health
   ```

### Firewall Issues

```bash
# Check firewall rule exists
gcloud compute firewall-rules describe allow-streamlit

# If missing, create manually:
gcloud compute firewall-rules create allow-streamlit \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:8501 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server
```

### Slow Performance

**Check resource usage:**
```bash
# CPU and memory
sudo docker stats

# If high usage:
# 1. API container should use ~1.5GB RAM
# 2. UI container should use ~500MB RAM
# 3. Total should be under 6GB (VM has 8GB)
```

---

## 🔄 Updates and Redeployment

### Update UI Code

```bash
# 1. Make changes locally
# 2. Commit and push to GitHub
git add .
git commit -m "Update UI"
git push

# 3. Redeploy
.\scripts\gcp-deploy-ui.ps1
```

### Restart UI Container

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Restart UI
sudo docker restart nlp-ui

# View logs
sudo docker logs -f nlp-ui
```

### Rebuild UI Image

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Navigate to repo
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Pull latest code
git pull

# Rebuild image
sudo docker build -f Dockerfile.streamlit.api -t cloud-nlp-ui:latest .

# Stop old container
sudo docker stop nlp-ui
sudo docker rm nlp-ui

# Start new container
sudo docker run -d \
    --name nlp-ui \
    -p 8501:8501 \
    -e API_URL=http://localhost:8000 \
    --restart unless-stopped \
    cloud-nlp-ui:latest
```

---

## 💰 Cost Impact

### Before UI Deployment
- VM (e2-standard-2): $49/month
- Static IP: $7/month
- GCS Storage: $0.02/month
- **Total: $56/month**

### After UI Deployment
- VM (e2-standard-2): $49/month (no change)
- Static IP: $7/month (no change)
- GCS Storage: $0.02/month (no change)
- UI Container: $0/month (same VM)
- **Total: $56/month (NO INCREASE)**

---

## 📊 Performance

### Expected Resource Usage

| Component | Memory | CPU | Startup Time |
|-----------|--------|-----|--------------|
| API Container | ~1.5GB | 0.1-0.5 cores | ~10 seconds |
| UI Container | ~500MB | 0.05-0.2 cores | ~5 seconds |
| **Total** | **~2GB / 8GB** | **~0.15-0.7 / 2 cores** | **~15 seconds** |

### Image Sizes

| Image | Size | Build Time |
|-------|------|------------|
| cloud-nlp-classifier (API) | ~2.5GB | 5-10 minutes |
| cloud-nlp-ui (UI) | ~500MB | 2-3 minutes |

---

## 🎉 Success Checklist

After successful deployment, you should have:

- ✅ API accessible at `http://YOUR_IP:8000`
- ✅ API docs at `http://YOUR_IP:8000/docs`
- ✅ UI accessible at `http://YOUR_IP:8501`
- ✅ Both containers running (`sudo docker ps`)
- ✅ Both health checks passing
- ✅ UI can connect to API
- ✅ Predictions work end-to-end
- ✅ Model switching works
- ✅ Auto-restart enabled
- ✅ No cost increase

---

## 📚 Related Documentation

- [Frontend Deployment Plan](./FRONTEND_DEPLOYMENT_PLAN.md) - Detailed planning
- [Backend vs Frontend Comparison](./BACKEND_VS_FRONTEND_DEPLOYMENT.md) - Architecture comparison
- [GCP Deployment Progress](../GCP_DEPLOYMENT_PROGRESS.md) - Overall deployment status
- [Docker Guide](./DOCKER_GUIDE.md) - Docker best practices

---

## 🆘 Support

### View Logs

```bash
# API logs
sudo docker logs -f nlp-api

# UI logs
sudo docker logs -f nlp-ui

# Both logs
sudo docker logs -f nlp-api & sudo docker logs -f nlp-ui
```

### Container Management

```bash
# List all containers
sudo docker ps -a

# Stop containers
sudo docker stop nlp-api nlp-ui

# Start containers
sudo docker start nlp-api nlp-ui

# Restart containers
sudo docker restart nlp-api nlp-ui

# Remove containers
sudo docker rm -f nlp-api nlp-ui
```

### System Status

```bash
# Disk usage
df -h

# Memory usage
free -h

# Docker stats
sudo docker stats

# Network status
sudo docker network ls
sudo docker network inspect nlp-network
```

---

**Status:** ✅ READY FOR DEPLOYMENT
**Last Updated:** 2025-12-10
**Version:** 1.0.0
