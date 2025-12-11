# 🎯 MASTER CONTROLLER SCRIPT - COMPLETE PLANNING DOCUMENT

**Project:** CLOUD-NLP-CLASSIFIER-GCP  
**Script Name:** `deploy-master-controller.ps1`  
**Version:** 1.0.0  
**Last Updated:** 2025-12-11  
**Status:** Planning Phase

---

## 📋 EXECUTIVE SUMMARY

### **Purpose**
Create a single master controller script that automates the entire deployment pipeline from a fresh repository clone to a fully functional production deployment on GCP.

### **Problem Statement**
Currently, deploying the NLP classifier requires:
- Running 7+ separate scripts in sequence
- Manual validation between stages
- Knowledge of which scripts to run when
- No checkpoint/resume capability
- No unified error handling
- No progress tracking

### **Solution**
A comprehensive PowerShell controller script that:
- Orchestrates all deployment stages automatically
- Validates prerequisites and outputs at each stage
- Provides checkpoint/resume functionality
- Offers multiple execution modes (interactive, automated, dry-run)
- Handles errors gracefully with recovery options
- Generates detailed deployment reports

### **Key Metrics**
- **Lines of Code**: ~1,500-2,000
- **Development Time**: 4-6 hours
- **Testing Time**: 2-3 hours
- **Deployment Time Saved**: 50-70% (from manual process)
- **Error Rate Reduction**: 80-90% (automated validation)

---

## 🎯 CORE OBJECTIVES

### **Primary Objectives**

1. **Zero-Configuration Setup** - User clones repo → Runs script → Everything works
2. **Intelligent Checkpoint System** - Save progress, resume from any point
3. **Comprehensive Validation** - Pre-flight checks, post-stage validation
4. **Clear Progress Tracking** - Real-time progress, time estimates, ETA
5. **Flexible Execution Modes** - Interactive, automated, dry-run, stage-specific, resume
6. **Robust Error Handling** - Capture errors, provide troubleshooting, offer retry/skip/abort
7. **Comprehensive Reporting** - Generate deployment summary, capture metrics, export to JSON/Markdown

---

## 🏗️ ARCHITECTURE OVERVIEW

### **Script Structure**
```
deploy-master-controller.ps1
├── [1] Configuration & Constants
├── [2] Helper Functions (logging, progress, checkpoints)
├── [3] Validation Functions (prerequisites, file checks, health checks)
├── [4] Stage Functions (Invoke-Stage0 through Invoke-Stage10)
├── [5] Reporting Functions (reports, metrics, summaries)
├── [6] Main Execution Flow
└── [7] Interactive Menu System
```

### **State Management**
```json
{
  "deployment_id": "deploy-20251211-033426",
  "start_time": "2025-12-11T03:34:26",
  "mode": "Interactive",
  "target": "Local",
  "current_stage": 3,
  "completed_stages": [0, 1, 2],
  "stage_metrics": { ... },
  "errors": [],
  "warnings": []
}
```

---

## 📋 STAGE BREAKDOWN

### **STAGE 0: Environment Setup** ⏱️ 2-5 min
- Check Python 3.10+, Docker, gcloud CLI
- Create virtual environment
- Install requirements.txt
- Create directory structure
- Initialize deployment state

### **STAGE 1: Data Preprocessing** ⏱️ 2-5 min
- Download hate speech dataset (if needed)
- Run `.\scripts\run_preprocess_local.ps1`
- Validate train/val/test splits (19,826 / 2,478 / 2,479 rows)

### **STAGE 2: Baseline Training** ⏱️ 3-5 min
- Run `.\scripts\run_baselines_local.ps1`
- Train TF-IDF + LogReg + SVM
- Validate models exist and accuracy > 85%

### **STAGE 3: Transformer Training** ⏱️ 15-30 min (CPU), 3-5 min (GPU)
- Run `.\scripts\run_transformer_local.ps1`
- Fine-tune DistilBERT
- Validate accuracy > 90%, model size ~250-300 MB

### **STAGE 4: Toxicity Training** ⏱️ 20-40 min (CPU), 5-10 min (GPU)
- Run `.\scripts\run_toxicity_training.ps1`
- Train multi-label classifier (6 categories)
- Validate ROC-AUC > 0.95

### **STAGE 5: Local API Testing** ⏱️ 2-3 min
- Start API: `.\scripts\run_api_local.ps1`
- Test /health, /predict, /models endpoints
- Test model switching
- Validate all models work

### **STAGE 6: Docker Build** ⏱️ 10-15 min
- Build backend: `docker build -t cloud-nlp-classifier:latest .`
- Build UI: `docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .`
- Start containers, test endpoints
- Validate health checks passing

### **STAGE 7: Full Stack Testing** ⏱️ 3-5 min
- Run `.\scripts\test-fullstack-local.ps1`
- Performance benchmarks (latency, memory)
- Integration tests
- Validate all tests pass

### **STAGE 8: GCS Upload** ⏱️ 2-3 min (OPTIONAL)
- Upload models to `gs://nlp-classifier-models/`
- Use MODEL_VERSION.json for versioning
- Upload ~770 MB (with -NoCheckpoints)

### **STAGE 9: GCP Deployment** ⏱️ 20-25 min (OPTIONAL)
- Run `.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints`
- Deploy to VM, build Docker, start container
- Validate external IP accessible

### **STAGE 10: UI Deployment** ⏱️ 10-15 min (OPTIONAL)
- Run `.\scripts\gcp-deploy-ui.ps1`
- Deploy Streamlit UI to VM
- Validate UI accessible at port 8501

---

## 🎮 EXECUTION MODES

### **1. Interactive (Default)**
```powershell
.\deploy-master-controller.ps1
```
- Guided deployment with user control
- Shows menu after each stage
- Best for first-time users

### **2. Fully Automated (Local)**
```powershell
.\deploy-master-controller.ps1 -Mode Auto -Target Local
```
- Runs stages 0-7 automatically
- No user interaction
- Best for CI/CD

### **3. Fully Automated (Cloud)**
```powershell
.\deploy-master-controller.ps1 -Mode Auto -Target Cloud -GcpProject "mnist-k8s-pipeline"
```
- Runs all stages 0-10
- Full production deployment
- Best for automated releases

### **4. Resume from Checkpoint**
```powershell
.\deploy-master-controller.ps1 -Resume
```
- Continue from last completed stage
- Best for interrupted deployments

### **5. Specific Stage Only**
```powershell
.\deploy-master-controller.ps1 -Stage 3
```
- Run single stage
- Best for debugging

### **6. Dry Run**
```powershell
.\deploy-master-controller.ps1 -DryRun
```
- Preview without execution
- Best for planning

---

## 📊 PARAMETERS

```powershell
[CmdletBinding()]
param(
    [ValidateSet('Interactive', 'Auto')]
    [string]$Mode = 'Interactive',
    
    [ValidateSet('Local', 'Cloud', 'Both')]
    [string]$Target = 'Local',
    
    [switch]$Resume,
    
    [ValidateRange(0, 10)]
    [int]$Stage = -1,
    
    [switch]$DryRun,
    
    [int[]]$SkipStages = @(),
    
    [switch]$Force,
    
    [switch]$Verbose,
    
    [switch]$SkipToxicity,
    
    [switch]$SkipUI,
    
    [string]$GcpProject = "",
    
    [string]$GcpZone = "us-central1-a",
    
    [switch]$Clean
)
```

---

## 💡 USAGE EXAMPLES

### **Example 1: First-time setup**
```powershell
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP
.\deploy-master-controller.ps1
```

### **Example 2: Automated local deployment**
```powershell
.\deploy-master-controller.ps1 -Mode Auto -Target Local
```

### **Example 3: Full cloud deployment**
```powershell
.\deploy-master-controller.ps1 -Mode Auto -Target Cloud -GcpProject "mnist-k8s-pipeline"
```

### **Example 4: Resume interrupted deployment**
```powershell
.\deploy-master-controller.ps1 -Resume
```

### **Example 5: Skip toxicity model**
```powershell
.\deploy-master-controller.ps1 -Mode Auto -SkipToxicity
```

### **Example 6: Re-run specific stage**
```powershell
.\deploy-master-controller.ps1 -Stage 3 -Force
```

---

## ⏱️ TIMELINE ESTIMATES

| Configuration | Duration | Stages |
|---------------|----------|--------|
| **Local Only (CPU)** | 45-60 min | 0-7 |
| **Local Only (GPU)** | 25-35 min | 0-7 |
| **Cloud Deployment (CPU)** | 65-85 min | 0-10 |
| **Cloud Deployment (GPU)** | 45-60 min | 0-10 |
| **Skip Toxicity** | -20 min | All |
| **Resume from Stage 6** | 15-20 min | 6-10 |

---

## 📁 FILE STRUCTURE

```
CLOUD-NLP-CLASSIFIER-GCP/
├── deploy-master-controller.ps1          ⭐ NEW
├── .deployment/                          ⭐ NEW
│   ├── checkpoints/
│   │   ├── stage0_complete.flag
│   │   └── ... (stage flags)
│   ├── logs/
│   │   ├── deployment.log
│   │   └── ... (per-stage logs)
│   ├── deployment_state.json
│   ├── deployment_metrics.json
│   └── deployment_report.md
└── (existing files)
```

---

## ✅ SUCCESS CRITERIA

### **Local Deployment Success:**
- All stages 0-7 complete
- Docker containers running
- API accessible at localhost:8000
- UI accessible at localhost:8501
- All 4 models functional

### **Cloud Deployment Success:**
- All stages 0-10 complete
- GCS bucket contains models
- VM running and healthy
- API accessible at external IP
- UI accessible at external IP
- All endpoints responding correctly

---

## 🚨 ERROR RECOVERY

### **Automatic Recovery:**
- Network failures: Retry with exponential backoff
- Transient errors: Auto-retry up to 3 times
- Resource issues: Wait and retry

### **Manual Recovery:**
- Critical failures: Prompt user for action
- Configuration errors: Guide user to fix
- Missing prerequisites: Provide installation instructions

---

## 📝 OUTPUT FILES

After completion:
```
.deployment/
├── deployment_report.md          (Human-readable summary)
├── deployment_state.json         (Machine-readable state)
├── deployment_metrics.json       (Performance metrics)
└── deployment.log               (Detailed logs)
```

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Core Infrastructure** (2 hours)
- Script skeleton
- Parameter parsing
- Helper functions
- Checkpoint system
- State management

### **Phase 2: Stage Functions** (3 hours)
- Implement all 11 stage functions
- Pre-flight validation
- Post-stage validation
- Error handling

### **Phase 3: Execution Modes** (1 hour)
- Interactive menu system
- Automated mode
- Resume functionality
- Dry-run mode

### **Phase 4: Reporting** (1 hour)
- Progress tracking
- Metrics collection
- Report generation
- Summary display

### **Phase 5: Testing** (2-3 hours)
- Test each stage individually
- Test full pipeline
- Test error scenarios
- Test resume functionality

---

## ❓ OPEN QUESTIONS

1. **Should we include a rollback mechanism** to undo deployment if something fails?
2. **Should we add email/Slack notifications** for long-running stages?
3. **Should we include cost estimation** for GCP deployment before proceeding?
4. **Should we add a "quick start" mode** that uses pre-trained models from a public bucket?
5. **Should we include performance benchmarking** as a separate optional stage?

---

## 📊 SUMMARY

This master controller script will:
1. ✅ **Automate 100%** of the deployment process
2. ✅ **Validate** every step before proceeding
3. ✅ **Resume** from any point if interrupted
4. ✅ **Report** detailed progress and metrics
5. ✅ **Handle errors** gracefully with recovery options
6. ✅ **Support** multiple execution modes
7. ✅ **Generate** comprehensive deployment reports

**Total Lines of Code (Estimated):** ~1,500-2,000 lines  
**Development Time:** 4-6 hours  
**Testing Time:** 2-3 hours

**Ready for implementation!** 🚀
