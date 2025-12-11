# Model Prefix from VERSION.json

## Overview

The deployment script now automatically reads the `model_prefix` from `MODEL_VERSION.json`. This ties the prefix to your model configuration, making it easier to manage and preventing accidental uploads to the wrong location.

## How It Works

### 1. Configure Prefix in MODEL_VERSION.json

```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-10T12:00:00-05:00",
  "model_prefix": "DPM-MODELS",  ← Add this field
  "models": {
    ...
  }
}
```

### 2. Run Deployment

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
Model prefix from VERSION: DPM-MODELS
============================================
  GCP Complete Deployment
  All-in-One Setup
============================================

Project: mnist-k8s-pipeline
VM: nlp-classifier-vm
Zone: us-central1-a
Bucket: gs://nlp-classifier-models/DPM-MODELS/  ← Automatically uses prefix from JSON
```

### 3. Models Uploaded to Correct Location

All models automatically go to: `gs://nlp-classifier-models/DPM-MODELS/models/`

---

## Benefits

### 1. Configuration-Driven
- Prefix is part of your model configuration
- No need to remember command-line flags
- Consistent across all deployments

### 2. Version-Tied
- Each model version has its own prefix
- Easy to track which prefix belongs to which version
- Prevents mixing models from different configurations

### 3. No Prefix Option
- If `model_prefix` is not in JSON → No prefix used
- Models go directly to `gs://bucket/models/`
- Backward compatible with existing setups

---

## Usage Examples

### Example 1: DPM's Models

**MODEL_VERSION.json:**
```json
{
  "version": "1.0.0",
  "model_prefix": "DPM-MODELS",
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Result:** `gs://nlp-classifier-models/DPM-MODELS/models/`

---

### Example 2: John's Models

**MODEL_VERSION.json:**
```json
{
  "version": "1.1.0",
  "model_prefix": "JOHN-MODELS",
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Result:** `gs://nlp-classifier-models/JOHN-MODELS/models/`

---

### Example 3: No Prefix (Legacy)

**MODEL_VERSION.json:**
```json
{
  "version": "1.0.0",
  // No model_prefix field
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
No model_prefix in MODEL_VERSION.json, using no prefix
Bucket: gs://nlp-classifier-models/
```

**Result:** `gs://nlp-classifier-models/models/`

---

### Example 4: Production Environment

**MODEL_VERSION.json:**
```json
{
  "version": "2.0.0",
  "model_prefix": "TEAM-PRODUCTION",
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Result:** `gs://nlp-classifier-models/TEAM-PRODUCTION/models/`

---

## Workflow

### Typical Development Cycle

```bash
# 1. Train models locally
python run_transformer.py

# 2. Test locally
python scripts/client_example.py

# 3. Update MODEL_VERSION.json
# Edit version: 1.0.0 → 1.1.0
# Set prefix: "DPM-MODELS"

# 4. Deploy (prefix automatically read from JSON)
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Output shows:
# Model prefix from VERSION: DPM-MODELS
# Bucket: gs://nlp-classifier-models/DPM-MODELS/
```

---

## Team Collaboration

### Each Team Member Has Their Own JSON

**DPM's MODEL_VERSION.json:**
```json
{
  "version": "1.2.0",
  "model_prefix": "DPM-MODELS",
  ...
}
```

**John's MODEL_VERSION.json:**
```json
{
  "version": "1.1.0",
  "model_prefix": "JOHN-MODELS",
  ...
}
```

**Sarah's MODEL_VERSION.json:**
```json
{
  "version": "1.0.5",
  "model_prefix": "SARAH-MODELS",
  ...
}
```

### Everyone Runs Same Command

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

But models go to different locations based on their JSON configuration!

---

## Changing Prefix

### Option 1: Edit MODEL_VERSION.json

```json
{
  "version": "1.0.0",
  "model_prefix": "NEW-PREFIX",  ← Change this
  ...
}
```

Then run deployment - it will use the new prefix.

### Option 2: Remove Prefix

```json
{
  "version": "1.0.0",
  // Remove or comment out model_prefix
  ...
}
```

Models will go to root: `gs://bucket/models/`

---

## Troubleshooting

### "Model prefix from VERSION: " (empty)

**Cause:** `model_prefix` field is empty string in JSON  
**Solution:** Either set a value or remove the field entirely

```json
// Bad
"model_prefix": "",

// Good - with prefix
"model_prefix": "DPM-MODELS",

// Good - no prefix
// Just remove the field
```

### "No model_prefix in MODEL_VERSION.json"

**Cause:** Field doesn't exist in JSON  
**Result:** No prefix will be used (models go to root)  
**Solution:** Add the field if you want a prefix:

```json
{
  "version": "1.0.0",
  "model_prefix": "YOUR-PREFIX",  ← Add this line
  ...
}
```

### "Could not read MODEL_VERSION.json"

**Cause:** JSON file is malformed or doesn't exist  
**Solution:** 
1. Check JSON syntax (use a JSON validator)
2. Ensure file exists in project root
3. Check file permissions

---

## Best Practices

### 1. Always Set a Prefix for Team Projects

```json
{
  "version": "1.0.0",
  "model_prefix": "YOUR-NAME-MODELS",  ← Always set this
  ...
}
```

### 2. Use Descriptive Prefixes

```json
// Good
"model_prefix": "DPM-MODELS"
"model_prefix": "TEAM-PRODUCTION"
"model_prefix": "EXPERIMENT-ROBERTA"

// Avoid
"model_prefix": "TEST"
"model_prefix": "ABC"
```

### 3. Update Prefix When Promoting to Production

```json
// Development
{
  "version": "1.5.0",
  "model_prefix": "DPM-MODELS",
  ...
}

// After testing, promote to production
{
  "version": "2.0.0",
  "model_prefix": "TEAM-PRODUCTION",  ← Changed
  ...
}
```

### 4. Document Your Prefix

Add a note in the JSON:

```json
{
  "version": "1.0.0",
  "model_prefix": "DPM-MODELS",
  "notes": {
    "owner": "Dhairya Mishra",
    "purpose": "Development models",
    "prefix_info": "Personal development space, not for production"
  },
  ...
}
```

---

## Migration from Command-Line Parameter

### Old Way (Manual Parameter)

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints -ModelPrefix "DPM-MODELS"
```

### New Way (From JSON)

**MODEL_VERSION.json:**
```json
{
  "version": "1.0.0",
  "model_prefix": "DPM-MODELS",
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Benefits:**
- No need to remember the flag
- Prefix is versioned with your models
- Consistent across all deployments
- Less error-prone

---

## Summary

**Key Points:**
- Prefix is now read from `MODEL_VERSION.json`
- Add `"model_prefix": "YOUR-PREFIX"` to your JSON
- If field doesn't exist → No prefix used
- Automatic and configuration-driven
- Backward compatible

**Quick Setup:**
1. Edit `MODEL_VERSION.json`
2. Add `"model_prefix": "YOUR-NAME-MODELS"`
3. Run `.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints`
4. Done! Models automatically go to correct location

**No More:**
- ❌ Remembering command-line flags
- ❌ Accidentally uploading to wrong location
- ❌ Inconsistent prefix usage

**Now:**
- ✅ Configuration-driven
- ✅ Automatic prefix from JSON
- ✅ Version-tied organization
- ✅ Team-friendly
