# Master Controller Quick Start Guide

**Version:** 1.0.0  
**Last Updated:** 2025-12-11  
**Status:** Phase 1 Complete ✅  
**Language:** Python 3.10+

---

## 🚀 Quick Start

### **1. First-Time Deployment (Interactive)**
```bash
# Clone and navigate to repo
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP

# Run master controller
python deploy-master-controller.py
```
**What it does:**
- Guides you through each stage
- Shows progress and estimates
- Asks for confirmation at each step
- Best for first-time users

---

### **2. Automated Local Deployment**
```bash
python deploy-master-controller.py --mode auto --target local
```
**What it does:**
- Runs stages 0-7 automatically
- No user interaction required
- Completes in 25-60 minutes (depending on CPU/GPU)
- Best for CI/CD pipelines

**Stages executed:**
- ✅ Stage 0: Environment Setup
- ✅ Stage 1: Data Preprocessing
- ✅ Stage 2: Baseline Training
- ✅ Stage 3: Transformer Training
- ✅ Stage 4: Toxicity Training
- ✅ Stage 5: Local API Testing
- ✅ Stage 6: Docker Build
- ✅ Stage 7: Full Stack Testing

---

### **3. Automated Cloud Deployment**
```bash
python deploy-master-controller.py --mode auto --target cloud --gcp-project mnist-k8s-pipeline
```
**What it does:**
- Runs all stages 0-10
- Deploys to GCP VM
- Completes in 45-85 minutes
- Best for production deployment

**Additional stages:**
- ✅ Stage 8: GCS Upload
- ✅ Stage 9: GCP Deployment
- ✅ Stage 10: UI Deployment

---

### **4. Resume from Interruption**
```bash
python deploy-master-controller.py --resume
```
**What it does:**
- Loads previous deployment state
- Continues from last completed stage
- Skips already-completed stages
- Best for recovering from failures

---

### **5. Preview (Dry Run)**
```bash
python deploy-master-controller.py --dry-run
```
**What it does:**
- Shows deployment plan
- Lists all stages with estimates
- No actual execution
- Best for planning

---

## 📋 Common Scenarios

### **Scenario 1: Quick Local Testing (Skip Toxicity)**
```bash
python deploy-master-controller.py --mode auto --target local --skip-toxicity
```
**Time saved:** ~20-40 minutes  
**Use case:** Testing without toxicity model

---

### **Scenario 2: Re-train Specific Model**
```bash
# Re-train transformer only
python deploy-master-controller.py --stage 3 --force

# Re-train baselines only
python deploy-master-controller.py --stage 2 --force
```
**Use case:** Model improvements or hyperparameter tuning

---

### **Scenario 3: Deploy to Cloud (Skip UI)**
```bash
python deploy-master-controller.py --mode auto --target cloud --gcp-project mnist-k8s-pipeline --skip-ui
```
**Time saved:** ~10-15 minutes  
**Use case:** API-only deployment

---

### **Scenario 4: Clean Start**
```bash
python deploy-master-controller.py --clean
```
**What it does:**
- Removes `.deployment/` directory
- Clears all checkpoints and state
- Starts fresh from Stage 0
**Use case:** Troubleshooting or fresh deployment

---

## 🎯 All Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | String | interactive | Execution mode: interactive or auto |
| `--target` | String | local | Deployment target: local, cloud, or both |
| `--resume` | Flag | False | Resume from last checkpoint |
| `--stage` | Int | None | Run specific stage only (0-10) |
| `--dry-run` | Flag | False | Preview without execution |
| `--skip-stages` | Int[] | [] | Array of stages to skip |
| `--force` | Flag | False | Force re-run of completed stages |
| `--verbose` | Flag | False | Enable verbose logging |
| `--skip-toxicity` | Flag | False | Skip Stage 4 (toxicity training) |
| `--skip-ui` | Flag | False | Skip Stage 10 (UI deployment) |
| `--gcp-project` | String | "" | GCP project ID |
| `--gcp-zone` | String | us-central1-a | GCP zone |
| `--clean` | Flag | False | Clean previous deployment state |

---

## 📊 Stage Overview

| Stage | Name | Duration | Required For |
|-------|------|----------|--------------|
| 0 | Environment Setup | 2-5 min | All |
| 1 | Data Preprocessing | 2-5 min | All |
| 2 | Baseline Training | 3-5 min | All |
| 3 | Transformer Training | 15-30 min (CPU)<br>3-5 min (GPU) | All |
| 4 | Toxicity Training | 20-40 min (CPU)<br>5-10 min (GPU) | All (Optional) |
| 5 | Local API Testing | 2-3 min | All |
| 6 | Docker Build | 10-15 min | All |
| 7 | Full Stack Testing | 3-5 min | All |
| 8 | GCS Upload | 2-3 min | Cloud |
| 9 | GCP Deployment | 20-25 min | Cloud |
| 10 | UI Deployment | 10-15 min | Cloud (Optional) |

---

## 🔍 Checking Status

### **View Deployment State**
```bash
python -m json.tool .deployment/deployment_state.json
```

### **View Logs**
```bash
tail -50 .deployment/logs/deployment.log
# Or on Windows:
Get-Content .deployment/logs/deployment.log -Tail 50
```

### **Check Completed Stages**
```bash
ls .deployment/checkpoints/
# Or on Windows:
dir .deployment\checkpoints\
```

### **View Metrics**
```bash
python -m json.tool .deployment/deployment_metrics.json
```

---

## ⚠️ Prerequisites

Before running the master controller, ensure you have:

### **For Local Deployment:**
- ✅ Python 3.10+ installed
- ✅ Docker installed and running
- ✅ 10GB+ free disk space

### **For Cloud Deployment:**
- ✅ All local prerequisites
- ✅ gcloud CLI installed
- ✅ gcloud authenticated: `gcloud auth login`
- ✅ GCP project configured: `gcloud config set project YOUR_PROJECT_ID`
- ✅ Billing enabled on GCP project

---

## 🛠️ Troubleshooting

### **Problem: Prerequisites check fails**
```bash
# Check Python version
python --version

# Check Docker
docker --version
docker ps

# Check gcloud (for cloud deployment)
gcloud --version
gcloud auth list
```

### **Problem: Stage fails**
```bash
# View logs
tail -100 .deployment/logs/deployment.log

# Re-run specific stage
python deploy-master-controller.py --stage X --force

# Resume from checkpoint
python deploy-master-controller.py --resume
```

### **Problem: Deployment stuck**
```bash
# Check current stage
python -c "import json; print(json.load(open('.deployment/deployment_state.json'))['current_stage'])"

# Clean and restart
python deploy-master-controller.py --clean
```

### **Problem: Out of disk space**
```bash
# Check disk space
df -h  # Linux/Mac
# Or on Windows:
Get-PSDrive C | Select-Object Used,Free

# Clean Docker
docker system prune -a

# Clean deployment artifacts
rm -rf .deployment  # Linux/Mac
# Or on Windows:
Remove-Item .deployment -Recurse -Force
```

---

## 📁 Output Structure

After running the master controller:

```
CLOUD-NLP-CLASSIFIER-GCP/
├── .deployment/                    ⭐ NEW
│   ├── checkpoints/
│   │   ├── stage0_complete.flag
│   │   ├── stage1_complete.flag
│   │   └── ... (one per completed stage)
│   ├── logs/
│   │   └── deployment.log
│   ├── deployment_state.json
│   ├── deployment_metrics.json
│   └── deployment_report.md
├── venv/                           ⭐ Created by Stage 0
├── data/
│   └── processed/                  ⭐ Created by Stage 1
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
├── models/
│   ├── baselines/                  ⭐ Created by Stage 2
│   ├── transformer/                ⭐ Created by Stage 3
│   └── toxicity_multi_head/        ⭐ Created by Stage 4
└── ... (existing files)
```

---

## 🎉 Success Indicators

### **Local Deployment Success:**
- ✅ All stages 0-7 complete
- ✅ Docker containers running
- ✅ API accessible at `http://localhost:8000`
- ✅ UI accessible at `http://localhost:8501`
- ✅ All 4 models functional

### **Cloud Deployment Success:**
- ✅ All stages 0-10 complete
- ✅ Models uploaded to GCS
- ✅ VM running and healthy
- ✅ API accessible at `http://<VM_IP>:8000`
- ✅ UI accessible at `http://<VM_IP>:8501`

---

## 📚 Additional Resources

- **Full Documentation:** `docs/PHASE1_MASTER_CONTROLLER_IMPLEMENTATION.md`
- **Master Plan:** `MASTER_CONTROLLER_PLAN.md`
- **Setup Guide:** `SETUP AND RUN NOW.md`
- **Project README:** `README.md`

---

## 🚀 Next Steps After Deployment

### **Local Deployment:**
1. Test API: `curl http://localhost:8000/health`
2. Test predictions: `python scripts/client_example.py`
3. Open UI: `http://localhost:8501`
4. Run tests: `pytest -q`

### **Cloud Deployment:**
1. Test API: `curl http://<VM_IP>:8000/health`
2. Test predictions: `curl -X POST http://<VM_IP>:8000/predict -H "Content-Type: application/json" -d '{"text": "test"}'`
3. Open UI: `http://<VM_IP>:8501`
4. View logs: `gcloud compute ssh nlp-classifier-vm --zone=us-central1-a -- sudo docker logs -f nlp-api`

---

## 💡 Tips

1. **Use `--dry-run` first** to preview the deployment plan
2. **Use `--skip-toxicity`** to save 20-40 minutes during testing
3. **Use `--resume`** if deployment is interrupted
4. **Use `--force`** to re-run specific stages
5. **Check logs** at `.deployment/logs/deployment.log` if something fails
6. **Use `--clean`** for a fresh start if things get messy
7. **Use `--help`** to see all available options

---

## 📞 Support

If you encounter issues:
1. Check logs: `.deployment/logs/deployment.log`
2. Check state: `.deployment/deployment_state.json`
3. Review documentation: `docs/PHASE1_MASTER_CONTROLLER_IMPLEMENTATION.md`
4. Check existing scripts work individually (e.g., `.\scripts\run_preprocess_local.ps1`)

---

**Happy Deploying! 🚀**
