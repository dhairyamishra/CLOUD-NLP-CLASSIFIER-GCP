# GCP Deployment Script - Usage Options

## Quick Reference

### Standard Deployment (Optimized - Recommended)
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```
**Uploads:** ~770 MB (final models only)  
**Time:** ~2-3 minutes upload  
**Includes:** Production-ready models only  
**Excludes:** Training checkpoints  

---

### Full Deployment (With Checkpoints)
```powershell
.\scripts\gcp-complete-deployment.ps1
```
**Uploads:** ~12 GB (all files including checkpoints)  
**Time:** ~15-20 minutes upload  
**Includes:** Everything (final models + all checkpoints)  
**Use Case:** If you need checkpoint history for debugging/analysis  

---

## Detailed Options

### Available Flags

| Flag | Description | Default |
|------|-------------|---------|
| `-NoCheckpoints` | Skip checkpoint directories, upload only final models | `false` |
| `-SkipModelUpload` | Skip model upload entirely (use existing GCS models) | `false` |
| `-SkipVMCreation` | Skip VM creation (use existing VM) | `false` |
| `-ProjectId` | GCP Project ID | `mnist-k8s-pipeline` |
| `-VMName` | VM instance name | `nlp-classifier-vm` |
| `-Zone` | GCP zone | `us-central1-a` |
| `-Region` | GCP region | `us-central1` |
| `-BucketName` | GCS bucket name | `nlp-classifier-models` |
| `-ModelPrefix` | Prefix folder in bucket (for team organization) | `DPM-MODELS` |
| `-GitRepo` | GitHub repository URL | `https://github.com/...` |
| `-Branch` | Git branch to deploy | `main` (auto-detected) |
| `-ModelsPath` | Local models directory | `C:\...\models` |

---

## Usage Examples

### 1. First-Time Deployment (Optimized)
```powershell
# Upload only production models, create VM, deploy
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

### 2. First-Time Deployment (Full)
```powershell
# Upload everything including checkpoints
.\scripts\gcp-complete-deployment.ps1
```

### 3. Re-Deploy (Skip Upload)
```powershell
# Use existing models in GCS, just redeploy code
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

### 4. Update Code Only
```powershell
# Skip both model upload and VM creation
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload -SkipVMCreation
```

### 5. Custom Configuration
```powershell
# Custom project and bucket
.\scripts\gcp-complete-deployment.ps1 `
    -NoCheckpoints `
    -ProjectId "my-project" `
    -BucketName "my-models-bucket" `
    -VMName "my-nlp-vm"
```

### 6. Team Member with Different Prefix
```powershell
# Use different prefix for team organization
.\scripts\gcp-complete-deployment.ps1 `
    -NoCheckpoints `
    -ModelPrefix "JOHN-MODELS"
# Models will be stored at: gs://nlp-classifier-models/JOHN-MODELS/
```

---

## What Gets Uploaded?

### With `-NoCheckpoints` (Optimized - 770 MB)

```
models/
├── baselines/
│   ├── logistic_regression.joblib          [INCLUDED] (~500 KB)
│   ├── linear_svm.joblib                   [INCLUDED] (~400 KB)
│   └── labels.json                         [INCLUDED]
├── toxicity_multi_head/
│   ├── config.json                         [INCLUDED]
│   ├── model.safetensors                   [INCLUDED] (~256 MB)
│   ├── tokenizer.json                      [INCLUDED]
│   ├── labels.json                         [INCLUDED]
│   └── checkpoint-XXX/                     [EXCLUDED]
├── transformer/
│   ├── distilbert/
│   │   ├── config.json                     [INCLUDED]
│   │   ├── model.safetensors               [INCLUDED] (~256 MB)
│   │   ├── tokenizer.json                  [INCLUDED]
│   │   ├── labels.json                     [INCLUDED]
│   │   └── checkpoint-XXX/                 [EXCLUDED]
│   └── distilbert_fullscale/
│       ├── config.json                     [INCLUDED]
│       ├── model.safetensors               [INCLUDED] (~256 MB)
│       ├── tokenizer.json                  [INCLUDED]
│       ├── labels.json                     [INCLUDED]
│       └── checkpoint-XXX/                 [EXCLUDED]
```

**Total:** ~770 MB

---

### Without `-NoCheckpoints` (Full - 12 GB)

```
models/
├── baselines/                              [INCLUDED] (~900 KB)
├── toxicity_multi_head/
│   ├── Final model files                   [INCLUDED] (~256 MB)
│   └── checkpoint-XXX/                     [INCLUDED] (multiple checkpoints)
├── transformer/
│   ├── distilbert/
│   │   ├── Final model files               [INCLUDED] (~256 MB)
│   │   └── checkpoint-XXX/                 [INCLUDED] (~4 GB total)
│   └── distilbert_fullscale/
│       ├── Final model files               [INCLUDED] (~256 MB)
│       └── checkpoint-XXX/                 [INCLUDED] (~7.5 GB total)
```

**Total:** ~12 GB

---

## Performance Comparison

| Mode | Upload Size | Upload Time | GCS Cost/Month | Use Case |
|------|-------------|-------------|----------------|----------|
| **Optimized** (`-NoCheckpoints`) | ~770 MB | ~2-3 min | ~$0.02 | Production deployment (recommended) |
| **Full** (default) | ~12 GB | ~15-20 min | ~$0.30 | Debug/analysis with checkpoints |

---

## Deployment Flow

### Phase 1: Setup Cloud Storage
1. Create GCS bucket (if not exists)
2. Upload models based on `-NoCheckpoints` flag
3. Verify uploads

### Phase 2: Setup Compute VM
1. Check if VM exists
2. Create VM if needed (unless `-SkipVMCreation`)
3. Verify VM is running

### Phase 3: Deploy Application
1. Clone repository (auto-detect branch)
2. Download models from GCS
3. Build Docker image
4. Start container
5. Test API endpoints

---

## Troubleshooting

### Upload is too slow
```powershell
# Use optimized mode
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

### Models already in GCS
```powershell
# Skip upload, just deploy
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

### VM already exists
```powershell
# Skip VM creation
.\scripts\gcp-complete-deployment.ps1 -SkipVMCreation
```

### Need to clean up and start fresh
```powershell
# Delete bucket
gcloud storage rm -r gs://nlp-classifier-models

# Delete VM
gcloud compute instances delete nlp-classifier-vm --zone=us-central1-a

# Run fresh deployment
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

---

## Cost Optimization Tips

### 1. Use `-NoCheckpoints` for Production
- Saves ~11 GB of storage
- Reduces upload time by 80%
- Lower GCS storage costs

### 2. Skip Uploads When Possible
```powershell
# Models already uploaded? Skip it
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

### 3. Stop VM When Not in Use
```powershell
# Stop VM (saves ~$0.07/hour)
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a

# Start when needed
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
```

### 4. Use Preemptible VMs (Future Enhancement)
- 80% cheaper than regular VMs
- Good for testing/development

---

## Recommended Workflows

### Production Deployment
```powershell
# First time
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Updates (code changes only)
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload -SkipVMCreation
```

### Development/Testing
```powershell
# With checkpoints for debugging
.\scripts\gcp-complete-deployment.ps1

# Quick iterations
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

### Cost-Conscious
```powershell
# Minimal uploads
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Stop VM when done
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a
```

---

## Summary

**For most users, use:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

This gives you:
- Fast uploads (~2-3 min vs 15-20 min)
- Lower costs (~$0.02/month vs $0.30/month)
- All production-ready models
- Everything the API needs to run

**Only use full mode if:**
- You need checkpoint history for analysis
- You're debugging training issues
- You want to resume training from checkpoints
