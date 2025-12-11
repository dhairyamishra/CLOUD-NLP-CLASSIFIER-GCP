# Backend vs Frontend Deployment Comparison

## 📊 Side-by-Side Analysis

This document compares the backend API deployment (WORKING ✅) with the planned frontend UI deployment to ensure we follow the same proven pattern.

---

## 🏗️ Deployment Pattern Comparison

| Aspect | Backend API (DONE ✅) | Frontend UI (PLANNED) |
|--------|----------------------|----------------------|
| **VM** | nlp-classifier-vm | Same VM (nlp-classifier-vm) |
| **Container Name** | `nlp-api` | `nlp-ui` |
| **Port** | 8000 | 8501 |
| **Dockerfile** | `Dockerfile` | `Dockerfile.streamlit.api` (new) |
| **Image Name** | `cloud-nlp-classifier:latest` | `cloud-nlp-ui:latest` |
| **Models** | Included in image (~2.5GB) | NOT included (API mode) |
| **Size** | ~2.5GB | ~500MB (much smaller) |
| **Dependencies** | PyTorch, transformers, FastAPI | Streamlit, requests (lightweight) |
| **Health Check** | `/health` | `/_stcore/health` |
| **External URL** | http://35.232.76.140:8000 | http://35.232.76.140:8501 |

---

## 📋 Deployment Script Comparison

### Backend Script Pattern (gcp-complete-deployment.ps1)

```powershell
# PHASE 1: Upload Models to GCS
✅ Create/verify GCS bucket
✅ Upload models (770 MB with -NoCheckpoints)
✅ Verify uploads

# PHASE 2: Verify/Start VM
✅ Check VM status
✅ Start VM if stopped

# PHASE 3: Deploy Application
✅ Clone repository from GitHub
✅ Download models from GCS
✅ Build Docker image (5-10 min)
✅ Stop old container
✅ Run new container
✅ Test health (internal)
✅ Test health (external)

# PHASE 4: Summary
✅ Show endpoints
✅ Show duration
✅ Show costs
```

### Frontend Script Pattern (gcp-deploy-ui.ps1) - TO CREATE

```powershell
# PHASE 1: Verify API is Running
✅ Check nlp-api container status
✅ Test API health endpoint
✅ Verify API is accessible

# PHASE 2: Verify/Update Firewall
✅ Check port 8501 firewall rule
✅ Create rule if missing

# PHASE 3: Deploy UI Application
✅ SSH into VM (same as backend)
✅ cd ~/CLOUD-NLP-CLASSIFIER-GCP (same directory)
✅ Pull latest code (git pull)
✅ Build UI Docker image (2-3 min, much faster)
✅ Stop old nlp-ui container
✅ Run new UI container with API_URL
✅ Test health (internal)
✅ Test health (external)
✅ Test API connectivity from UI

# PHASE 4: Summary
✅ Show UI URL
✅ Show API URL
✅ Show duration
✅ No cost increase
```

---

## 🔧 Docker Commands Comparison

### Backend Container

```bash
# Build
sudo docker build -t cloud-nlp-classifier:latest .

# Run
sudo docker run -d \
    --name nlp-api \
    -p 8000:8000 \
    --restart unless-stopped \
    cloud-nlp-classifier:latest

# Health Check
curl http://localhost:8000/health

# Logs
sudo docker logs -f nlp-api
```

### Frontend Container (PLANNED)

```bash
# Build
sudo docker build -f Dockerfile.streamlit.api -t cloud-nlp-ui:latest .

# Run
sudo docker run -d \
    --name nlp-ui \
    -p 8501:8501 \
    -e API_URL=http://localhost:8000 \
    --restart unless-stopped \
    cloud-nlp-ui:latest

# Health Check
curl http://localhost:8501/_stcore/health

# Logs
sudo docker logs -f nlp-ui
```

---

## 🌐 Network Architecture

### Current (API Only)
```
Internet
   │
   ▼
Firewall (port 8000)
   │
   ▼
VM: nlp-classifier-vm
   │
   ▼
Container: nlp-api (port 8000)
   │
   ▼
FastAPI + Models
```

### After UI Deployment
```
Internet
   │
   ├─────────────────┬─────────────────┐
   │                 │                 │
   ▼                 ▼                 ▼
Firewall       Firewall          Firewall
(port 22)      (port 8000)       (port 8501)
   │                 │                 │
   └─────────────────┴─────────────────┘
                     │
                     ▼
          VM: nlp-classifier-vm
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Container: nlp-api      Container: nlp-ui
   (port 8000)             (port 8501)
        │                         │
        │                         │
   FastAPI + Models          Streamlit
        ▲                         │
        │                         │
        └─────────────────────────┘
           API calls (localhost)
```

---

## 📦 File Structure Comparison

### Backend Files (EXISTING ✅)
```
CLOUD-NLP-CLASSIFIER-GCP/
├── Dockerfile                    ✅ Backend API
├── src/api/server.py            ✅ FastAPI app
├── models/                       ✅ ML models
│   ├── baselines/
│   ├── transformer/
│   └── toxicity_multi_head/
└── scripts/
    └── gcp-complete-deployment.ps1  ✅ Backend deploy script
```

### Frontend Files (TO CREATE)
```
CLOUD-NLP-CLASSIFIER-GCP/
├── Dockerfile.streamlit          ✅ Exists (local mode)
├── Dockerfile.streamlit.api      ❌ TO CREATE (API mode)
├── src/ui/
│   ├── streamlit_app.py         ✅ Exists (needs API mode)
│   └── utils/
│       └── api_inference.py     ❌ TO CREATE (API client)
└── scripts/
    └── gcp-deploy-ui.ps1        ❌ TO CREATE (UI deploy script)
```

---

## 🔄 Deployment Workflow Comparison

### Backend Deployment Flow
```
Local Machine
    │
    ├─ 1. Upload models to GCS (770 MB)
    │
    ▼
GCP Cloud Storage
    │
    ▼
GCP VM
    │
    ├─ 2. Clone code from GitHub
    ├─ 3. Download models from GCS
    ├─ 4. Build Docker image (includes models)
    ├─ 5. Run container
    │
    ▼
Running API (port 8000)
```

### Frontend Deployment Flow (PLANNED)
```
Local Machine
    │
    ├─ 1. Push code to GitHub (no models needed)
    │
    ▼
GitHub Repository
    │
    ▼
GCP VM (same as backend)
    │
    ├─ 2. Pull latest code
    ├─ 3. Build Docker image (NO models, lightweight)
    ├─ 4. Run container with API_URL env var
    │
    ▼
Running UI (port 8501)
    │
    ├─ Connects to API on localhost:8000
    │
    ▼
Full Stack Running
```

---

## 💰 Cost Comparison

### Backend Only (CURRENT)
```
VM (e2-standard-2):     $49/month
Static IP:              $7/month
GCS Storage (1GB):      $0.02/month
────────────────────────────────
Total:                  $56/month
```

### Backend + Frontend (AFTER)
```
VM (e2-standard-2):     $49/month  (no change)
Static IP:              $7/month   (no change)
GCS Storage (1GB):      $0.02/month (no change)
UI Container:           $0/month   (same VM)
────────────────────────────────
Total:                  $56/month  (NO INCREASE ✅)
```

---

## ⚡ Performance Comparison

### Backend Container
- **Memory**: ~1.5GB (includes PyTorch + models)
- **CPU**: ~0.1-0.5 cores (idle/active)
- **Startup**: ~10 seconds (model loading)
- **Image Size**: ~2.5GB

### Frontend Container (EXPECTED)
- **Memory**: ~500MB (Streamlit + requests only)
- **CPU**: ~0.05-0.2 cores (idle/active)
- **Startup**: ~5 seconds (no model loading)
- **Image Size**: ~500MB

### Combined (Same VM)
- **Total Memory**: ~2GB / 8GB available (25% usage) ✅
- **Total CPU**: ~0.15-0.7 cores / 2 available (35% usage) ✅
- **Plenty of headroom** for traffic spikes ✅

---

## 🎯 Key Similarities (Why This Will Work)

Both deployments use:
1. ✅ Same VM infrastructure
2. ✅ Same GitHub repository
3. ✅ Same Docker pattern (build on VM)
4. ✅ Same error handling (`set -e`, `sudo docker`)
5. ✅ Same health check pattern
6. ✅ Same restart policy (`unless-stopped`)
7. ✅ Same validation approach (exit codes + output markers)
8. ✅ Same security (non-root user, firewall rules)

---

## 🔑 Key Differences (What Changes)

| Aspect | Backend | Frontend |
|--------|---------|----------|
| **Models** | Included in image | NOT included (calls API) |
| **Size** | Large (~2.5GB) | Small (~500MB) |
| **Build Time** | 5-10 minutes | 2-3 minutes |
| **Dependencies** | Heavy (PyTorch) | Light (Streamlit) |
| **Port** | 8000 | 8501 |
| **Health Endpoint** | `/health` | `/_stcore/health` |
| **Environment** | Minimal | Needs `API_URL` |

---

## 📝 Implementation Checklist

### Code Changes
- [ ] Create `Dockerfile.streamlit.api` (API mode, no models)
- [ ] Create `src/ui/utils/api_inference.py` (API client)
- [ ] Modify `src/ui/streamlit_app.py` (support API mode)
- [ ] Test locally with docker-compose

### Infrastructure Changes
- [ ] Add firewall rule for port 8501
- [ ] Verify VM has capacity (it does ✅)

### Deployment Script
- [ ] Create `scripts/gcp-deploy-ui.ps1`
- [ ] Follow backend script pattern exactly
- [ ] Add API connectivity verification
- [ ] Add comprehensive error handling

### Testing
- [ ] Local: docker-compose up (both services)
- [ ] Cloud: Deploy and test end-to-end
- [ ] Performance: Monitor resource usage
- [ ] Reliability: Test auto-restart

### Documentation
- [ ] Update README with UI URL
- [ ] Create UI deployment guide
- [ ] Add troubleshooting section
- [ ] Update architecture diagrams

---

## 🎉 Expected Outcome

After successful deployment:

```
✅ API Running:  http://35.232.76.140:8000
✅ UI Running:   http://35.232.76.140:8501
✅ Both containers on same VM
✅ UI calls API via localhost (fast)
✅ Auto-restart on failure
✅ Health checks passing
✅ No cost increase
✅ Full-stack NLP app live!
```

---

## 🚀 Next Action

**READY TO IMPLEMENT** following this proven pattern:
1. Create API-mode files (Dockerfile, API client)
2. Create deployment script (following backend pattern)
3. Deploy to GCP
4. Test and verify
5. Document and celebrate! 🎉

**Estimated Time**: 2 hours
**Risk**: LOW (following working pattern)
**Cost**: $0 additional
