# Team Model Organization Guide

## Overview

The deployment system now supports organizing models by team member using the `-ModelPrefix` parameter. This allows multiple team members to store their trained models in the same GCS bucket without conflicts.

## Bucket Structure

```
gs://nlp-classifier-models/
├── DPM-MODELS/              ← Your models (default)
│   ├── MODEL_VERSION.json
│   └── models/
│       ├── baselines/
│       ├── toxicity_multi_head/
│       └── transformer/
├── JOHN-MODELS/             ← John's models
│   ├── MODEL_VERSION.json
│   └── models/
│       ├── baselines/
│       └── ...
├── SARAH-MODELS/            ← Sarah's models
│   ├── MODEL_VERSION.json
│   └── models/
│       └── ...
└── TEAM-PRODUCTION/         ← Production models
    ├── MODEL_VERSION.json
    └── models/
        └── ...
```

## Usage

### Default (DPM-MODELS)

```powershell
# Uses default prefix: DPM-MODELS
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Result:** Models stored at `gs://nlp-classifier-models/DPM-MODELS/`

---

### Custom Prefix for Team Members

```powershell
# John's models
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "JOHN-MODELS"

# Sarah's models
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "SARAH-MODELS"

# Production models
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "TEAM-PRODUCTION"
```

---

## Benefits

### 1. Isolated Development
- Each team member has their own model space
- No risk of overwriting someone else's models
- Independent versioning per team member

### 2. Easy Comparison
```powershell
# Compare different team member models
gcloud storage ls gs://nlp-classifier-models/DPM-MODELS/models/
gcloud storage ls gs://nlp-classifier-models/JOHN-MODELS/models/
```

### 3. Production Promotion
```powershell
# Copy best models to production
gcloud storage cp -r \
  gs://nlp-classifier-models/DPM-MODELS/models/ \
  gs://nlp-classifier-models/TEAM-PRODUCTION/models/
```

---

## Naming Conventions

### Recommended Prefix Format

**Individual Development:**
- `{NAME}-MODELS` (e.g., `DPM-MODELS`, `JOHN-MODELS`)

**Team Environments:**
- `TEAM-DEV` - Development environment
- `TEAM-STAGING` - Staging environment
- `TEAM-PRODUCTION` - Production environment

**Experiments:**
- `EXPERIMENT-{NAME}` (e.g., `EXPERIMENT-BERT-LARGE`)

---

## Version Management

Each prefix has its own `MODEL_VERSION.json`:

```
DPM-MODELS/MODEL_VERSION.json      → version: 1.2.0
JOHN-MODELS/MODEL_VERSION.json     → version: 1.1.0
TEAM-PRODUCTION/MODEL_VERSION.json → version: 1.0.0
```

This allows:
- Independent versioning per team member
- Different model versions in different environments
- Clear tracking of who trained what

---

## Example Workflow

### Scenario: Team Development

**Step 1: DPM trains new models**
```powershell
# Train models locally
python run_transformer.py

# Update version to 1.2.0
# Edit MODEL_VERSION.json

# Deploy to DPM-MODELS
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
# Bucket: gs://nlp-classifier-models/DPM-MODELS/
```

**Step 2: John trains alternative models**
```powershell
# Train with different hyperparameters
python run_transformer.py --learning-rate 2e-5

# Update version to 1.1.0
# Edit MODEL_VERSION.json

# Deploy to JOHN-MODELS
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "JOHN-MODELS"
# Bucket: gs://nlp-classifier-models/JOHN-MODELS/
```

**Step 3: Compare Results**
```powershell
# Test DPM's models
curl http://35.232.76.140:8000/predict -d '{"text": "test"}'

# Switch to John's models (redeploy VM with different prefix)
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "JOHN-MODELS"

# Test John's models
curl http://35.232.76.140:8000/predict -d '{"text": "test"}'
```

**Step 4: Promote Best Models to Production**
```powershell
# DPM's models performed better, promote to production
gcloud storage cp -r \
  gs://nlp-classifier-models/DPM-MODELS/ \
  gs://nlp-classifier-models/TEAM-PRODUCTION/

# Deploy production
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "TEAM-PRODUCTION"
```

---

## Checking Current Models

### List All Team Prefixes
```powershell
gcloud storage ls gs://nlp-classifier-models/
```

**Output:**
```
gs://nlp-classifier-models/DPM-MODELS/
gs://nlp-classifier-models/JOHN-MODELS/
gs://nlp-classifier-models/SARAH-MODELS/
gs://nlp-classifier-models/TEAM-PRODUCTION/
```

### Check Version for Each Prefix
```powershell
# DPM's version
gcloud storage cat gs://nlp-classifier-models/DPM-MODELS/MODEL_VERSION.json

# John's version
gcloud storage cat gs://nlp-classifier-models/JOHN-MODELS/MODEL_VERSION.json

# Production version
gcloud storage cat gs://nlp-classifier-models/TEAM-PRODUCTION/MODEL_VERSION.json
```

---

## Cost Considerations

### Storage Costs
- Each prefix stores ~770 MB (optimized) or ~12 GB (full)
- Multiple prefixes multiply storage costs
- Example: 3 team members × 770 MB = 2.3 GB total

**Recommendation:** Use `-NoCheckpoints` to minimize storage

### Cleanup Old Prefixes
```powershell
# Delete old experimental models
gcloud storage rm -r gs://nlp-classifier-models/EXPERIMENT-OLD/
```

---

## Best Practices

### 1. Use Descriptive Prefixes
```powershell
# Good
-ModelPrefix "DPM-MODELS"
-ModelPrefix "TEAM-PRODUCTION"
-ModelPrefix "EXPERIMENT-ROBERTA"

# Avoid
-ModelPrefix "TEST"
-ModelPrefix "MODELS"
-ModelPrefix "ABC"
```

### 2. Document Your Prefix
Keep a team document tracking:
- Who owns which prefix
- What experiments are in each prefix
- Which prefix is currently in production

### 3. Regular Cleanup
```powershell
# List all prefixes
gcloud storage ls gs://nlp-classifier-models/

# Remove unused ones
gcloud storage rm -r gs://nlp-classifier-models/OLD-PREFIX/
```

### 4. Version Consistently
- Each prefix should have its own `MODEL_VERSION.json`
- Update versions when uploading new models
- Use semantic versioning (MAJOR.MINOR.PATCH)

---

## Troubleshooting

### "Models not found" Error
**Cause:** Wrong prefix specified  
**Solution:** Check which prefix was used during upload
```powershell
gcloud storage ls gs://nlp-classifier-models/
```

### Accidentally Uploaded to Wrong Prefix
**Solution:** Copy to correct prefix and delete old one
```powershell
# Copy to correct location
gcloud storage cp -r \
  gs://nlp-classifier-models/WRONG-PREFIX/ \
  gs://nlp-classifier-models/CORRECT-PREFIX/

# Delete wrong location
gcloud storage rm -r gs://nlp-classifier-models/WRONG-PREFIX/
```

### Multiple Team Members Sharing Same Prefix
**Issue:** Models getting overwritten  
**Solution:** Each team member should use their own prefix
```powershell
# DPM
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "DPM-MODELS"

# John
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "JOHN-MODELS"
```

---

## Summary

**Key Points:**
- Use `-ModelPrefix` to organize models by team member
- Default prefix is `DPM-MODELS`
- Each prefix has independent versioning
- Prevents model conflicts between team members
- Easy to compare and promote models

**Quick Command:**
```powershell
# Deploy with your prefix
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "YOUR-NAME-MODELS"
```

**Bucket Path:**
```
gs://nlp-classifier-models/{YOUR-PREFIX}/models/
```
