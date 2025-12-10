# Frontend UI Deployment Plan

## 📋 Overview

This document outlines the plan to deploy the Streamlit frontend UI to GCP, following the same proven pattern used for the backend API deployment.

---

## 🎯 Current State Analysis

### Backend API Deployment (WORKING ✅)
- **VM**: `nlp-classifier-vm` (e2-standard-2, 2 vCPU, 8GB RAM)
- **External IP**: `35.232.76.140`
- **Port**: `8000`
- **Container**: `nlp-api` (Docker)
- **Status**: LIVE and operational

### Backend Deployment Pattern
1. **GCS Storage**: Models uploaded to `gs://nlp-classifier-models/DPM-MODELS/`
2. **Git Clone**: Code cloned from GitHub to VM
3. **Model Download**: Models downloaded from GCS to VM
4. **Docker Build**: Image built on VM (`cloud-nlp-classifier:latest`)
5. **Container Run**: Container started with port mapping
6. **Health Check**: External access verified

### Frontend Current State
- **Dockerfile**: `Dockerfile.streamlit` ✅ (already exists)
- **App**: `src/ui/streamlit_app.py` ✅ (already exists)
- **Config**: `.streamlit/config.toml` ✅ (already exists)
- **Components**: Full UI implementation ✅ (already exists)
- **Problem**: Currently loads models LOCALLY (not API-based)

---

## 🚀 Deployment Strategy

### Option 1: Same VM, Separate Container (RECOMMENDED)
**Deploy UI container on the SAME VM as the API**

#### Advantages ✅
- Uses existing VM infrastructure
- No additional VM costs
- API and UI on same network (fast communication)
- Simpler deployment (one VM to manage)
- Can use `localhost:8000` for API connection
- Total cost: ~$56/month (no increase)

#### Architecture
```
GCP VM (nlp-classifier-vm)
├── Container 1: nlp-api (port 8000)
└── Container 2: nlp-ui (port 8501)
```

#### Deployment Steps
1. Build Streamlit Docker image on VM
2. Run UI container with API_URL=http://localhost:8000
3. Expose port 8501 in firewall
4. Access UI at http://35.232.76.140:8501

---

### Option 2: Separate VM (Alternative)
**Deploy UI on a NEW dedicated VM**

#### Advantages ✅
- Complete isolation between API and UI
- Independent scaling
- Can use smaller VM for UI (e2-micro)

#### Disadvantages ❌
- Additional VM cost (~$7-15/month)
- More complex networking
- Need to manage 2 VMs
- API calls over external network (slower)

#### Architecture
```
GCP VM 1 (nlp-classifier-vm)
└── Container: nlp-api (port 8000)

GCP VM 2 (nlp-ui-vm)
└── Container: nlp-ui (port 8501)
```

---

## 📝 Implementation Plan (Option 1 - RECOMMENDED)

### Phase 1: Modify UI to Use API (NOT Local Models)
**Problem**: Current UI loads models locally via `model_manager.py`
**Solution**: Create API-based mode that connects to deployed backend

#### Files to Create/Modify
1. **Create**: `src/ui/utils/api_inference.py`
   - API client for backend communication
   - Replace local model loading with API calls
   - Handle API errors gracefully

2. **Modify**: `src/ui/streamlit_app.py`
   - Add environment variable `USE_API_MODE` (default: true)
   - If `USE_API_MODE=true`: Use API client
   - If `USE_API_MODE=false`: Use local models (for development)

3. **Create**: `Dockerfile.streamlit.api`
   - Lightweight version WITHOUT models
   - Only includes UI code
   - Sets `API_URL` environment variable
   - Much smaller image (~500MB vs 2.5GB)

### Phase 2: Update Firewall Rules
```bash
gcloud compute firewall-rules create allow-streamlit \
    --project=mnist-k8s-pipeline \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:8501 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server
```

### Phase 3: Create Deployment Script
**File**: `scripts/gcp-deploy-ui.ps1`

Following the EXACT pattern from `gcp-complete-deployment.ps1`:

```powershell
# PHASE 1: Verify API is Running
- Check nlp-api container is UP
- Test API health endpoint

# PHASE 2: Build UI Docker Image
- SSH into VM
- cd ~/CLOUD-NLP-CLASSIFIER-GCP
- sudo docker build -f Dockerfile.streamlit.api -t cloud-nlp-ui:latest .

# PHASE 3: Run UI Container
- Stop old nlp-ui container (if exists)
- Run new container:
  sudo docker run -d \
    --name nlp-ui \
    -p 8501:8501 \
    -e API_URL=http://localhost:8000 \
    --restart unless-stopped \
    cloud-nlp-ui:latest

# PHASE 4: Health Check
- Wait 10 seconds
- Test internal: curl http://localhost:8501/_stcore/health
- Test external: curl http://35.232.76.140:8501

# PHASE 5: Verify API Connection
- Test UI can reach API
- curl http://localhost:8000/health from UI container
```

### Phase 4: Update docker-compose.yml
Add API_URL environment variable to UI service:
```yaml
ui:
  environment:
    - API_URL=http://api:8000  # For docker-compose
    # OR
    - API_URL=http://localhost:8000  # For same-VM deployment
```

---

## 🔧 Technical Implementation Details

### 1. API Client Implementation
```python
# src/ui/utils/api_inference.py
class APIInferenceHandler:
    def __init__(self, api_url):
        self.api_url = api_url  # e.g., http://localhost:8000
    
    def predict(self, text, model_key):
        # Call POST /predict
        response = requests.post(
            f"{self.api_url}/predict",
            json={"text": text}
        )
        return response.json()
    
    def get_models(self):
        # Call GET /models
        response = requests.get(f"{self.api_url}/models")
        return response.json()
    
    def switch_model(self, model_name):
        # Call POST /models/switch
        response = requests.post(
            f"{self.api_url}/models/switch",
            json={"model_name": model_name}
        )
        return response.json()
```

### 2. Dockerfile Changes
```dockerfile
# Dockerfile.streamlit.api (NEW - API Mode)
FROM python:3.11-slim

# Install only UI dependencies (NO PyTorch, NO transformers)
RUN pip install streamlit plotly requests

# Copy only UI code (NO models directory)
COPY src/ui/ ./src/ui/
COPY .streamlit/ ./.streamlit/

# Environment variable for API URL
ENV API_URL=http://localhost:8000

CMD ["streamlit", "run", "src/ui/streamlit_app.py"]
```

### 3. Environment Variables
```bash
# Backend API Container
API_URL=http://localhost:8000  # Internal communication

# Frontend UI Container
API_URL=http://localhost:8000  # Points to API on same VM
```

---

## 📊 Resource Requirements

### Current (API Only)
- VM: e2-standard-2 (2 vCPU, 8GB RAM)
- Memory Usage: ~1.5GB (API container)
- Available: ~6.5GB

### After UI Deployment (Same VM)
- VM: e2-standard-2 (2 vCPU, 8GB RAM) - NO CHANGE
- Memory Usage: 
  - API: ~1.5GB
  - UI: ~500MB (API mode, no models)
  - Total: ~2GB
- Available: ~6GB ✅ PLENTY OF ROOM

### Cost Analysis
- **Option 1 (Same VM)**: $56/month (no increase)
- **Option 2 (Separate VM)**: $63-71/month (+$7-15)

---

## 🎨 User Experience

### After Deployment
1. **API Access**: http://35.232.76.140:8000/docs
2. **UI Access**: http://35.232.76.140:8501
3. **User Flow**:
   - User visits UI in browser
   - Enters text to analyze
   - UI sends request to API (backend)
   - API processes with ML models
   - API returns prediction
   - UI displays results beautifully

---

## ✅ Success Criteria

1. ✅ UI accessible at http://35.232.76.140:8501
2. ✅ UI successfully connects to API
3. ✅ Text prediction works end-to-end
4. ✅ Model switching works via UI
5. ✅ Both containers auto-restart on failure
6. ✅ Health checks passing for both services
7. ✅ No increase in monthly costs

---

## 🚦 Deployment Phases

### Phase 1: Code Changes (30 min)
- [ ] Create `src/ui/utils/api_inference.py`
- [ ] Modify `src/ui/streamlit_app.py` for API mode
- [ ] Create `Dockerfile.streamlit.api`
- [ ] Test locally with docker-compose

### Phase 2: Firewall Setup (5 min)
- [ ] Add firewall rule for port 8501
- [ ] Verify rule is active

### Phase 3: Deployment Script (30 min)
- [ ] Create `scripts/gcp-deploy-ui.ps1`
- [ ] Follow backend deployment pattern
- [ ] Add error handling and validation

### Phase 4: Deploy to GCP (10 min)
- [ ] Run deployment script
- [ ] Build UI image on VM
- [ ] Start UI container
- [ ] Verify health checks

### Phase 5: Testing (15 min)
- [ ] Test UI access from browser
- [ ] Test text prediction
- [ ] Test model switching
- [ ] Test error handling
- [ ] Performance testing

### Phase 6: Documentation (15 min)
- [ ] Update README with UI URLs
- [ ] Create UI deployment guide
- [ ] Add troubleshooting section

**Total Time**: ~2 hours

---

## 🔍 Testing Plan

### Local Testing (Before Deployment)
```bash
# Terminal 1: Start API
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:latest

# Terminal 2: Start UI
docker run -d -p 8501:8501 -e API_URL=http://host.docker.internal:8000 --name nlp-ui cloud-nlp-ui:latest

# Browser: Test
http://localhost:8501
```

### Cloud Testing (After Deployment)
```bash
# 1. Health Checks
curl http://35.232.76.140:8000/health  # API
curl http://35.232.76.140:8501/_stcore/health  # UI

# 2. Browser Test
http://35.232.76.140:8501

# 3. End-to-End Test
- Enter text in UI
- Click "Analyze"
- Verify prediction appears
- Switch model
- Test again
```

---

## 🛠️ Rollback Plan

If deployment fails:
1. Stop UI container: `sudo docker stop nlp-ui`
2. Remove UI container: `sudo docker rm nlp-ui`
3. API continues running (no impact)
4. Fix issues locally
5. Redeploy

---

## 📚 Next Steps

1. **Review this plan** - Confirm approach
2. **Implement Phase 1** - Code changes for API mode
3. **Test locally** - Verify UI works with API
4. **Create deployment script** - Following backend pattern
5. **Deploy to GCP** - Run script and verify
6. **Document** - Update all docs with UI access

---

## 🎯 Final Architecture

```
┌─────────────────────────────────────────────────────┐
│  GCP VM: nlp-classifier-vm (35.232.76.140)         │
│  ┌───────────────────────────────────────────────┐ │
│  │  Docker Network: nlp-network                  │ │
│  │                                               │ │
│  │  ┌─────────────────┐  ┌────────────────────┐ │ │
│  │  │  nlp-api        │  │  nlp-ui            │ │ │
│  │  │  Port: 8000     │◄─┤  Port: 8501        │ │ │
│  │  │  (FastAPI)      │  │  (Streamlit)       │ │ │
│  │  │  + Models       │  │  API Client Only   │ │ │
│  │  └─────────────────┘  └────────────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
           │                        │
           │                        │
    Port 8000 (API)          Port 8501 (UI)
           │                        │
           ▼                        ▼
    http://35.232.76.140:8000/docs
    http://35.232.76.140:8501
```

---

## 💡 Key Insights from Backend Deployment

1. **Use `set -e`** in all bash commands (exit on error)
2. **Use `sudo`** for all docker commands on VM
3. **Verify success** with markers in output, not just exit codes
4. **Test health** both internally (localhost) and externally (IP)
5. **Wait after start** (10 seconds) for container initialization
6. **Show logs** if container fails to start
7. **Fail fast** with clear error messages

These patterns will be replicated in the UI deployment script.

---

**Status**: ✅ PLAN COMPLETE - Ready for Implementation
**Estimated Time**: 2 hours
**Risk Level**: LOW (following proven pattern)
**Cost Impact**: NONE (same VM)
