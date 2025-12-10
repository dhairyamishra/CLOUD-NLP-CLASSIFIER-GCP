# Model Versioning Guide

## Overview

The deployment script now includes intelligent model versioning to avoid unnecessary uploads. Models are only uploaded when the version changes, saving time and bandwidth.

## How It Works

### 1. Version File: `MODEL_VERSION.json`

Located in the project root, this file tracks:
- Overall version number (semantic versioning: MAJOR.MINOR.PATCH)
- Individual model versions
- Last update timestamps
- File lists for each model

### 2. Version Comparison

When you run the deployment script:

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

The script will:
1. Read local `MODEL_VERSION.json`
2. Check remote version in GCS bucket
3. Compare versions:
   - **Same version** → Skip upload, proceed to deployment
   - **Different version** → Upload models and update remote version
   - **No remote version** → Upload all models

### 3. Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (model architecture change, incompatible API)
- **MINOR**: New features (new model added, improved accuracy)
- **PATCH**: Bug fixes (training fixes, minor improvements)

## Usage Examples

### Scenario 1: First Deployment
```powershell
# No remote version exists, will upload all models
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
[2/3] Checking model versions...
Local model version: 1.0.0
No remote version found, will upload all models

[2/3] Uploading models to GCS...
Mode: OPTIMIZED (final models only, ~770 MB)
...
[OK] Models uploaded to GCS
[OK] Version file uploaded
```

---

### Scenario 2: Re-Deploy (No Changes)
```powershell
# Models haven't changed, version is still 1.0.0
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
[2/3] Checking model versions...
Local model version: 1.0.0
Remote model version: 1.0.0
[SKIP] Model versions match (1.0.0), skipping upload
[SKIP] Models already up-to-date in GCS
```

**Result:** Skips upload, saves ~2-3 minutes!

---

### Scenario 3: Model Update (Version Changed)
```powershell
# You retrained models and updated MODEL_VERSION.json to 1.1.0
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
[2/3] Checking model versions...
Local model version: 1.1.0
Remote model version: 1.0.0
[UPDATE] Local version (1.1.0) is different from remote (1.0.0)
Will upload updated models...

[2/3] Uploading models to GCS...
...
[OK] Models uploaded to GCS
[OK] Version file uploaded
```

**Result:** Uploads new models, overwrites old version

---

## When to Update Version

### Update PATCH (1.0.0 → 1.0.1)
- Fixed a bug in training script
- Minor accuracy improvement
- Updated preprocessing
- Fixed tokenization issue

### Update MINOR (1.0.0 → 1.1.0)
- Retrained models with better hyperparameters
- Added a new model type
- Significant accuracy improvement
- Added new features to existing models

### Update MAJOR (1.0.0 → 2.0.0)
- Changed model architecture (e.g., BERT → RoBERTa)
- Breaking API changes
- Incompatible with previous version
- Complete model redesign

---

## How to Update Version

### Step 1: Edit `MODEL_VERSION.json`

```json
{
  "version": "1.1.0",  // ← Update this
  "last_updated": "2025-12-10T12:30:00-05:00",  // ← Update timestamp
  "models": {
    "baselines": {
      "version": "1.1.0",  // ← Update individual model version
      "last_updated": "2025-12-10T12:30:00-05:00"
    },
    ...
  }
}
```

### Step 2: Run Deployment

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

The script will detect the version change and upload the new models.

---

## Version Checking Logic

```
┌─────────────────────────────────────────┐
│  Read Local MODEL_VERSION.json          │
│  version: 1.1.0                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Check Remote Version in GCS            │
│  gcloud storage cat gs://bucket/...     │
└──────────────┬──────────────────────────┘
               │
               ▼
         ┌─────────┐
         │ Compare │
         └────┬────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────┐         ┌──────────┐
│ Same   │         │ Different│
│ Version│         │ Version  │
└───┬────┘         └────┬─────┘
    │                   │
    ▼                   ▼
┌────────┐         ┌──────────┐
│ SKIP   │         │ UPLOAD   │
│ Upload │         │ Models   │
└────────┘         └──────────┘
```

---

## Benefits

### Time Savings
- **First upload**: ~2-3 minutes (with `-NoCheckpoints`)
- **Subsequent deploys**: ~5 seconds (version check only)
- **Savings**: 95%+ time reduction when models haven't changed

### Bandwidth Savings
- Avoids uploading ~770 MB when not needed
- Reduces GCS API calls
- Lower costs for frequent deployments

### Safety
- Always know which version is deployed
- Easy rollback (change version number)
- Clear audit trail of model updates

---

## Advanced Usage

### Force Upload (Ignore Version)
If you need to force upload even with same version:

```powershell
# Option 1: Skip model upload check entirely
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload

# Option 2: Delete remote version file first
gcloud storage rm gs://nlp-classifier-models/MODEL_VERSION.json

# Then run normal deployment
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

### Check Current Remote Version
```powershell
gcloud storage cat gs://nlp-classifier-models/MODEL_VERSION.json
```

### Rollback to Previous Version
1. Update `MODEL_VERSION.json` to previous version
2. Restore old model files to `models/` directory
3. Run deployment:
   ```powershell
   .\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
   ```

---

## Troubleshooting

### "No local MODEL_VERSION.json found"
**Cause:** Version file is missing or gitignored  
**Solution:** Ensure `MODEL_VERSION.json` exists in project root

### "Could not parse remote version"
**Cause:** Remote version file is corrupted  
**Solution:** Delete remote version and re-upload:
```powershell
gcloud storage rm gs://nlp-classifier-models/MODEL_VERSION.json
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

### Version Check Takes Too Long
**Cause:** Network latency to GCS  
**Solution:** Use `-SkipModelUpload` if you know models are current

---

## Best Practices

1. **Always update version** when retraining models
2. **Use semantic versioning** consistently
3. **Document changes** in version file notes
4. **Test locally** before updating version
5. **Keep version file in git** for tracking
6. **Update timestamps** when changing versions

---

## Example Workflow

### Typical Development Cycle

```bash
# 1. Retrain models
python run_transformer.py

# 2. Test locally
python scripts/client_example.py

# 3. Update version
# Edit MODEL_VERSION.json: 1.0.0 → 1.1.0

# 4. Deploy to GCP
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
# Output: [UPDATE] Local version (1.1.0) is different...
# Uploads new models

# 5. Test deployment
curl http://35.232.76.140:8000/health

# 6. Subsequent deploys (code changes only)
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
# Output: [SKIP] Model versions match (1.1.0)
# Skips upload, saves time!
```

---

## Summary

Model versioning provides:
- Intelligent upload skipping
- Time and bandwidth savings
- Clear version tracking
- Easy rollback capability
- Audit trail for deployments

**Remember:** Update `MODEL_VERSION.json` whenever you retrain or modify models!
