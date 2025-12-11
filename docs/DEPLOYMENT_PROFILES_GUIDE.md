# Deployment Profiles Guide

**Date:** 2025-12-11  
**Feature:** Deployment Profile Selection  
**Status:** ✅ IMPLEMENTED

---

## 📋 **Overview**

The master controller now supports **3 deployment profiles** that let you choose between fast testing and production-quality training:

- **Quick** - Fast testing (3-5 min GPU, 15-20 min CPU)
- **Full** - Production quality (15-25 min GPU, 60-90 min CPU)
- **Cloud** - GCP-optimized (10-15 min on GCP GPU)

---

## 🎯 **Profile Comparison**

| Feature | Quick | Full | Cloud |
|---------|-------|------|-------|
| **Epochs** | 3 | 15 | 10 |
| **Max Seq Length** | 128 | 256 | 256 |
| **Batch Size** | 32 | 32 | 64 |
| **Learning Rate** | 5e-5 | 3e-5 | 2e-5 |
| **Gradient Accum** | 1 | 2 | 1 |
| **Early Stopping** | 2 epochs | 3 epochs | 3 epochs |
| **Expected Accuracy** | 85-88% | 90-93% | 90-93% |
| **GPU Time** | 3-5 min | 15-25 min | 10-15 min |
| **CPU Time** | 15-20 min | 60-90 min | 45-60 min |
| **Best For** | Testing, CI/CD | Production | GCP deployment |

---

## 🚀 **Usage**

### **Quick Profile** (Default)
```bash
# Fast testing - 3-5 minutes on GPU
python deploy-master-controller.py --profile quick

# With auto mode
python deploy-master-controller.py --mode auto --target local --profile quick

# Skip toxicity to save even more time
python deploy-master-controller.py --profile quick --skip-toxicity
```

**Use When:**
- Testing the pipeline
- Rapid iteration
- CI/CD pipelines
- Development

**Expected Results:**
- Accuracy: 85-88%
- F1 Score: 0.82-0.85
- Training Time: 3-5 min (GPU) or 15-20 min (CPU)

---

### **Full Profile**
```bash
# Production-quality training
python deploy-master-controller.py --profile full

# With auto mode
python deploy-master-controller.py --mode auto --target local --profile full
```

**Use When:**
- Production deployment
- Maximum accuracy needed
- Final model training
- Benchmarking

**Expected Results:**
- Accuracy: 90-93%
- F1 Score: 0.88-0.91
- Training Time: 15-25 min (GPU) or 60-90 min (CPU)

---

### **Cloud Profile**
```bash
# GCP-optimized training
python deploy-master-controller.py --profile cloud

# With cloud deployment
python deploy-master-controller.py --mode auto --target cloud --profile cloud --gcp-project mnist-k8s-pipeline
```

**Use When:**
- Training on GCP GPU VMs
- Cloud deployment
- Larger batch sizes (64)
- Cost-optimized training

**Expected Results:**
- Accuracy: 90-93%
- F1 Score: 0.88-0.91
- Training Time: 10-15 min (GCP GPU)

---

## 📁 **Config Files**

Each profile uses a specific config file:

| Profile | Config File | Location |
|---------|-------------|----------|
| Quick | `config_transformer_quick.yaml` | `config/` |
| Full | `config_transformer.yaml` | `config/` |
| Cloud | `config_transformer_cloud.yaml` | `config/` |

---

## 🔧 **How It Works**

### **1. Profile Selection**
```bash
python deploy-master-controller.py --profile quick
```

### **2. Stage 3 Uses Profile Config**
When Stage 3 (Transformer Training) runs:
- Reads the profile from command line
- Selects the appropriate config file
- Passes `--config <file>` to transformer_training.py
- Displays profile info in logs

### **3. Output**
```
[INFO] Stage 3: Transformer Training
[INFO] Using quick profile: Quick deployment for testing (3-5 min GPU, 15-20 min CPU)
[INFO] Config: config/config_transformer_quick.yaml
[INFO] Expected: 85-88% accuracy
[INFO] Training DistilBERT transformer...
```

---

## 📊 **Profile Details**

### **Quick Profile** (`config_transformer_quick.yaml`)

**Key Settings:**
```yaml
model:
  max_seq_length: 128  # Shorter sequences

training:
  num_train_epochs: 3  # Only 3 epochs
  learning_rate: 5.0e-5  # Higher LR for faster convergence
  gradient_accumulation_steps: 1  # No accumulation
  
  early_stopping:
    patience: 2  # Aggressive early stopping
```

**Optimized For:**
- Fast iteration
- Quick validation
- Resource-constrained environments

---

### **Full Profile** (`config_transformer.yaml`)

**Key Settings:**
```yaml
model:
  max_seq_length: 256  # Full context

training:
  num_train_epochs: 15  # More epochs
  learning_rate: 3.0e-5  # Lower LR for better convergence
  gradient_accumulation_steps: 2  # Effective batch = 64
  
  early_stopping:
    patience: 3  # More patience
```

**Optimized For:**
- Production quality
- Maximum accuracy
- Final model training

---

### **Cloud Profile** (`config_transformer_cloud.yaml`)

**Key Settings:**
```yaml
model:
  max_seq_length: 256  # Full context

training:
  train_batch_size: 64  # Larger batch for GPU
  num_train_epochs: 10  # Balanced
  learning_rate: 2.0e-5  # Cloud-optimized
  fp16: true  # Mixed precision enabled
  
  early_stopping:
    patience: 3
```

**Optimized For:**
- GCP GPU VMs (T4/V100/A100)
- Cost-efficient training
- Cloud deployment

---

## 💡 **Recommendations**

### **Development Workflow:**
1. **Start with Quick** - Test your pipeline (3-5 min)
2. **Validate with Full** - Ensure production quality (15-25 min)
3. **Deploy with Cloud** - Use GCP for final training (10-15 min)

### **Time Savings:**
- Quick vs Full: **~75% faster** (3-5 min vs 15-25 min on GPU)
- Quick vs Full: **~70% faster** (15-20 min vs 60-90 min on CPU)

### **Cost Savings (GCP):**
- Quick on T4: ~$0.05 (3-5 min)
- Full on T4: ~$0.20 (15-25 min)
- Cloud on T4: ~$0.15 (10-15 min)

---

## 🎯 **Examples**

### **Example 1: Quick Local Test**
```bash
# Test the entire pipeline in ~20 minutes (CPU)
python deploy-master-controller.py --mode auto --target local --profile quick --skip-toxicity
```

**Timeline:**
- Stage 0: Environment Setup - 10s
- Stage 1: Data Preprocessing - 10s
- Stage 2: Baseline Training - 3 min
- Stage 3: Transformer (Quick) - 15-20 min
- Stage 5: API Testing - 30s
- Stage 6: Docker Build - 10 min
- Stage 7: Testing - 3 min
- **Total: ~32 minutes**

---

### **Example 2: Production Deployment**
```bash
# Full production-quality deployment
python deploy-master-controller.py --mode auto --target local --profile full
```

**Timeline:**
- Stages 0-2: ~3 min
- Stage 3: Transformer (Full) - 60-90 min
- Stage 4: Toxicity - 30 min
- Stages 5-7: ~15 min
- **Total: ~110 minutes**

---

### **Example 3: Cloud Deployment**
```bash
# Deploy to GCP with cloud-optimized config
python deploy-master-controller.py --mode auto --target cloud --profile cloud --gcp-project mnist-k8s-pipeline
```

**Timeline:**
- Stages 0-2: ~3 min
- Stage 3: Transformer (Cloud) - 10-15 min (on GCP GPU)
- Stage 4: Toxicity - 10 min (on GCP GPU)
- Stages 5-7: ~15 min
- Stages 8-10: ~25 min (GCS upload + deployment)
- **Total: ~65 minutes**

---

## 🔍 **Dry Run with Profiles**

Test different profiles without execution:

```bash
# Preview quick profile
python deploy-master-controller.py --dry-run --profile quick

# Preview full profile
python deploy-master-controller.py --dry-run --profile full

# Preview cloud profile
python deploy-master-controller.py --dry-run --profile cloud
```

---

## 📝 **Implementation Details**

### **Files Modified:**
1. `deploy-master-controller.py` - Added profile support
2. `config/config_transformer_quick.yaml` - Created quick config

### **Code Changes:**
- Added `DEPLOYMENT_PROFILES` dictionary
- Added `--profile` CLI argument
- Modified `execute_stage_3()` to accept profile parameter
- Updated help text with profile examples
- Added profile info to deployment logs

### **Backward Compatibility:**
- ✅ Default profile is "quick"
- ✅ Existing commands still work
- ✅ No breaking changes

---

## ✅ **Testing**

```bash
# Test help
python deploy-master-controller.py --help

# Test dry run with each profile
python deploy-master-controller.py --dry-run --profile quick
python deploy-master-controller.py --dry-run --profile full
python deploy-master-controller.py --dry-run --profile cloud

# Test Stage 3 with quick profile
python deploy-master-controller.py --stage 3 --force --profile quick
```

---

**Last Updated:** 2025-12-11 05:51 AM EST  
**Status:** ✅ Ready for use!
