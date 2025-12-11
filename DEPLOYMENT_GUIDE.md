# 🚀 Deployment Guide - Master Controller

## Quick Start

### 🎯 One-Command Deployment

```bash
# Clone and deploy in 5 minutes
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP
python deploy-master-controller.py --profile quick
```

**Result:** Fully functional API at `http://localhost:8000` and UI at `http://localhost:8501`

---

## 📋 Deployment Profiles

| Profile | Epochs | Training Time | Accuracy | Use Case |
|---------|--------|---------------|----------|----------|
| **quick** | 1 | 1-2 min GPU | 80-85% | Testing, development |
| **full** | 15 | 15-25 min GPU | 90-93% | Production |
| **cloud** | 10 | 20-40 min GPU | 90-93% | GCP optimized |

---

## 🎮 Usage Examples

### Local Deployment

```bash
# Quick deployment (default)
python deploy-master-controller.py --profile quick

# Full production deployment
python deploy-master-controller.py --profile full

# Interactive mode (asks for confirmation at each stage)
python deploy-master-controller.py --mode interactive --profile quick
```

### Cloud Deployment

```bash
# Deploy to GCP
python deploy-master-controller.py --target cloud --gcp-project YOUR_PROJECT_ID

# Cloud deployment with full profile
python deploy-master-controller.py --target cloud --gcp-project YOUR_PROJECT_ID --profile full
```

### Resume & Force Options

```bash
# Resume from last checkpoint (if deployment was interrupted)
python deploy-master-controller.py --resume

# Force re-run all stages from scratch
python deploy-master-controller.py --force --profile quick

# Force re-run specific stage
python deploy-master-controller.py --stage 6 --force
```

### Skip Optional Stages

```bash
# Skip toxicity model training (saves ~30 min)
python deploy-master-controller.py --skip-toxicity

# Skip UI deployment
python deploy-master-controller.py --skip-ui

# Skip both
python deploy-master-controller.py --skip-toxicity --skip-ui
```

### Run Specific Stages

```bash
# Run only Docker build (Stage 6)
python deploy-master-controller.py --stage 6

# Run only tests (Stage 7)
python deploy-master-controller.py --stage 7

# Run only cloud deployment (Stages 8-10)
python deploy-master-controller.py --stage 8
python deploy-master-controller.py --stage 9
python deploy-master-controller.py --stage 10
```

---

## 📊 Deployment Stages

The master controller executes these stages automatically:

### Local Deployment (Stages 0-7)

- **Stage 0:** Environment Setup (5 min)
  - Creates virtual environment
  - Installs all dependencies
  - Validates prerequisites

- **Stage 1:** Data Preprocessing (3 min)
  - Downloads dataset
  - Cleans and preprocesses text
  - Creates train/val/test splits

- **Stage 2:** Baseline Training (4 min)
  - Trains Logistic Regression model
  - Trains Linear SVM model
  - Saves models to `models/baselines/`

- **Stage 3:** Transformer Training (varies by profile)
  - Quick: 1-2 min GPU (1 epoch)
  - Full: 15-25 min GPU (15 epochs)
  - Cloud: 20-40 min GPU (10 epochs)
  - Trains DistilBERT model
  - Saves to `models/transformer/distilbert/`

- **Stage 4:** Toxicity Training (30 min, optional)
  - Trains multi-head toxicity classifier
  - 6 toxicity categories
  - Saves to `models/toxicity_multi_head/`

- **Stage 5:** Local API Testing (2 min)
  - Starts FastAPI server
  - Tests all endpoints
  - Validates model loading

- **Stage 6:** Docker Build (12 min)
  - Builds API image with docker-compose
  - Builds UI image (lightweight)
  - Parallel builds for speed

- **Stage 7:** Full Stack Testing (4 min)
  - Runs pytest test suite
  - Runs PowerShell integration tests
  - Validates Docker containers

### Cloud Deployment (Stages 8-10)

- **Stage 8:** GCS Upload (3 min)
  - Uploads models to Google Cloud Storage
  - Version tracking
  - Optimized upload (excludes checkpoints)

- **Stage 9:** GCP Deployment (25 min)
  - Creates/configures GCP VM
  - Builds Docker image on VM
  - Deploys API container
  - Configures firewall rules

- **Stage 10:** UI Deployment (10 min)
  - Deploys Streamlit UI to GCP
  - Connects to API
  - Configures external access

---

## ✅ What Gets Deployed

### Local Deployment

**API (http://localhost:8000):**
- 4 models: DistilBERT, Logistic Regression, Linear SVM, Toxicity
- Dynamic model switching (zero downtime)
- Interactive API docs at `/docs`
- Health checks at `/health`

**UI (http://localhost:8501):**
- Chat-style interface
- Model selection
- Real-time predictions
- Probability visualizations

### Cloud Deployment

**API (http://YOUR_VM_IP:8000):**
- Same as local, accessible globally
- Auto-restart on failure
- Persistent storage on GCS

**UI (http://YOUR_VM_IP:8501):**
- Same as local, accessible globally
- Connected to cloud API

---

## 🔧 Advanced Options

### Dry Run (Preview)

```bash
# Preview what will be executed without running
python deploy-master-controller.py --dry-run --profile quick
```

### Custom Configuration

```bash
# Use custom transformer config
python deploy-master-controller.py --profile quick --config config/config_transformer_custom.yaml
```

### Verbose Logging

```bash
# Enable debug logging
python deploy-master-controller.py --profile quick --verbose
```

---

## 📈 Expected Results

### Quick Profile (1 epoch)
- **Total Time:** ~5 minutes
- **Accuracy:** 80-85%
- **Models:** 4 (DistilBERT, LogReg, SVM, Toxicity)
- **Docker Images:** 2 (API ~2GB, UI ~1GB)

### Full Profile (15 epochs)
- **Total Time:** ~30 minutes
- **Accuracy:** 90-93%
- **Models:** 4 (all production-ready)
- **Docker Images:** 2 (same size)

### Cloud Profile (10 epochs)
- **Total Time:** ~25-30 minutes (local) + 25 min (cloud deployment)
- **Accuracy:** 90-93%
- **Result:** Live API accessible globally

---

## 🐛 Troubleshooting

### Deployment Failed

```bash
# Check logs
cat .deployment/logs/deployment.log

# Resume from last successful stage
python deploy-master-controller.py --resume
```

### Stage-Specific Failure

```bash
# Re-run failed stage with force
python deploy-master-controller.py --stage 3 --force

# Skip problematic stage
python deploy-master-controller.py --skip-toxicity
```

### Docker Issues

```bash
# Rebuild Docker images
python deploy-master-controller.py --stage 6 --force

# Check Docker status
docker ps
docker logs nlp-api
docker logs nlp-ui
```

### Cloud Deployment Issues

```bash
# Check GCP authentication
gcloud auth list
gcloud config get-value project

# Re-run cloud stages
python deploy-master-controller.py --stage 8 --force
python deploy-master-controller.py --stage 9 --force
```

---

## 📁 Output Structure

After deployment, you'll have:

```
.deployment/
├── checkpoints/
│   ├── stage0_complete.flag
│   ├── stage1_complete.flag
│   └── ... (one per stage)
├── logs/
│   └── deployment.log
├── deployment_state.json
├── deployment_metrics.json
└── deployment_report.md

models/
├── baselines/
│   ├── logistic_regression_tfidf.joblib
│   └── linear_svm_tfidf.joblib
├── transformer/
│   └── distilbert/
│       ├── model.safetensors
│       ├── config.json
│       └── ...
└── toxicity_multi_head/
    └── ...

Docker containers:
- nlp-api (port 8000)
- nlp-ui (port 8501)
```

---

## 🎉 Success Indicators

### Local Deployment Success

```bash
# Check API
curl http://localhost:8000/health
# Should return: {"status":"ok","model_loaded":true,...}

# Check UI
# Open browser: http://localhost:8501
# Should show chat interface

# Check containers
docker ps
# Should show nlp-api and nlp-ui running
```

### Cloud Deployment Success

```bash
# Check API
curl http://YOUR_VM_IP:8000/health
# Should return: {"status":"ok","model_loaded":true,...}

# Check UI
# Open browser: http://YOUR_VM_IP:8501
# Should show chat interface

# Check VM
gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a
# Should show status: RUNNING
```

---

## 📚 Additional Resources

- **Full Documentation:** `SETUP AND RUN NOW.md`
- **README:** `README.md`
- **API Documentation:** http://localhost:8000/docs (after deployment)
- **Multi-Model Guide:** `docs/MULTI_MODEL_DOCKER_GUIDE.md`
- **Docker Guide:** `docs/DOCKER_GUIDE.md`

---

## 🤝 Support

If you encounter issues:

1. Check logs: `.deployment/logs/deployment.log`
2. Review stage output for errors
3. Use `--resume` to continue from last successful stage
4. Use `--force` to re-run problematic stages
5. Open an issue on GitHub with logs

---

**Built with ❤️ for automated ML deployment**
