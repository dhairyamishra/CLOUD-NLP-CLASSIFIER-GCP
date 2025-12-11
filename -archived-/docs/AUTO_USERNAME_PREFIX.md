# Automatic Username-Based Prefix

## Overview

The deployment script now automatically detects your username and uses it as the model prefix. This makes team collaboration seamless - everyone just sets `"model_prefix": "auto"` and their models automatically go to their own folder!

## How It Works

### 1. Set Prefix to "auto" in MODEL_VERSION.json

```json
{
  "version": "1.0.0",
  "model_prefix": "auto",  ← Set to "auto"
  "models": { ... }
}
```

### 2. Run Deployment

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

### 3. Username Automatically Detected

**Output:**
```
Model prefix AUTO-DETECTED from username: DHAIRYA-MODELS
============================================
  GCP Complete Deployment
  All-in-One Setup
============================================

Bucket: gs://nlp-classifier-models/DHAIRYA-MODELS/
```

**Result:** Models uploaded to `gs://nlp-classifier-models/DHAIRYA-MODELS/models/`

---

## Username Detection

The script tries multiple methods to get your username:

1. **Windows:** `$env:USERNAME` (e.g., "dhairya")
2. **Linux/Mac:** `$env:USER` (e.g., "dhairya")
3. **Fallback:** `whoami` command

Then converts to uppercase and adds "-MODELS":
- Username: `dhairya` → Prefix: `DHAIRYA-MODELS`
- Username: `john` → Prefix: `JOHN-MODELS`
- Username: `sarah.smith` → Prefix: `SARAH.SMITH-MODELS`

---

## Configuration Options

### Option 1: Auto (Recommended for Teams)

```json
{
  "version": "1.0.0",
  "model_prefix": "auto",  ← Automatically uses your username
  ...
}
```

**Result:** `{USERNAME}-MODELS` (e.g., `DHAIRYA-MODELS`)

---

### Option 2: Custom Prefix

```json
{
  "version": "1.0.0",
  "model_prefix": "DPM-MODELS",  ← Custom prefix
  ...
}
```

**Result:** `DPM-MODELS` (exactly as specified)

---

### Option 3: Empty/No Prefix Field

```json
{
  "version": "1.0.0",
  // No model_prefix field
  ...
}
```

**Result:** Uses username as default → `{USERNAME}-MODELS`

---

### Option 4: Empty String (No Prefix)

```json
{
  "version": "1.0.0",
  "model_prefix": "",  ← Empty string = no prefix
  ...
}
```

**Result:** No prefix, models go to `gs://bucket/models/`

---

## Team Collaboration Example

### Everyone Uses "auto"

**Dhairya's MODEL_VERSION.json:**
```json
{
  "version": "1.2.0",
  "model_prefix": "auto",
  ...
}
```
→ Models go to: `gs://nlp-classifier-models/DHAIRYA-MODELS/`

**John's MODEL_VERSION.json:**
```json
{
  "version": "1.1.0",
  "model_prefix": "auto",
  ...
}
```
→ Models go to: `gs://nlp-classifier-models/JOHN-MODELS/`

**Sarah's MODEL_VERSION.json:**
```json
{
  "version": "1.0.5",
  "model_prefix": "auto",
  ...
}
```
→ Models go to: `gs://nlp-classifier-models/SARAH-MODELS/`

### Everyone Runs Same Command

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**No conflicts!** Each person's models automatically go to their own folder.

---

## GCS Permissions

### Will This Cause Permission Issues?

**No!** GCS permissions are controlled at the **bucket level**, not by folder prefixes.

### How Permissions Work

```
gs://nlp-classifier-models/          ← Bucket (permissions set here)
├── DHAIRYA-MODELS/                  ← Just a folder (no separate permissions)
├── JOHN-MODELS/                     ← Just a folder (no separate permissions)
└── SARAH-MODELS/                    ← Just a folder (no separate permissions)
```

**Key Points:**
- If you have write access to the bucket, you can write to any folder
- Prefixes are just organizational folders, not security boundaries
- All team members with bucket access can read/write all prefixes
- Use IAM roles at bucket level for actual access control

### Recommended IAM Setup

```bash
# Give team members storage admin on the bucket
gcloud storage buckets add-iam-policy-binding gs://nlp-classifier-models \
  --member=user:dhairya@company.com \
  --role=roles/storage.objectAdmin

gcloud storage buckets add-iam-policy-binding gs://nlp-classifier-models \
  --member=user:john@company.com \
  --role=roles/storage.objectAdmin
```

**Everyone can:**
- Upload to their own prefix
- Read from other prefixes (for comparison)
- Copy models between prefixes (for promotion)

---

## Benefits

### 1. Zero Configuration
- Set `"model_prefix": "auto"` once
- Never think about it again
- Works for everyone on the team

### 2. Automatic Organization
- Models automatically organized by person
- No manual coordination needed
- Clear ownership of models

### 3. No Conflicts
- Everyone has their own space
- Can't accidentally overwrite someone else's models
- Safe parallel development

### 4. Easy Collaboration
- Can easily compare models: `gcloud storage ls gs://bucket/DHAIRYA-MODELS/` vs `gs://bucket/JOHN-MODELS/`
- Can copy best models to production
- Clear audit trail of who trained what

---

## Usage Examples

### Scenario 1: New Team Member

**Setup (one time):**
```json
{
  "version": "1.0.0",
  "model_prefix": "auto",
  ...
}
```

**Deploy:**
```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Output:**
```
Model prefix AUTO-DETECTED from username: NEWPERSON-MODELS
Bucket: gs://nlp-classifier-models/NEWPERSON-MODELS/
```

**Done!** No coordination needed with team.

---

### Scenario 2: Comparing Models

```powershell
# List your models
gcloud storage ls gs://nlp-classifier-models/DHAIRYA-MODELS/models/

# List John's models
gcloud storage ls gs://nlp-classifier-models/JOHN-MODELS/models/

# Compare versions
gcloud storage cat gs://nlp-classifier-models/DHAIRYA-MODELS/MODEL_VERSION.json
gcloud storage cat gs://nlp-classifier-models/JOHN-MODELS/MODEL_VERSION.json
```

---

### Scenario 3: Promoting to Production

```powershell
# Your models tested best, promote to production
gcloud storage cp -r \
  gs://nlp-classifier-models/DHAIRYA-MODELS/ \
  gs://nlp-classifier-models/TEAM-PRODUCTION/

# Update production MODEL_VERSION.json
# Change "model_prefix": "auto" to "model_prefix": "TEAM-PRODUCTION"

# Deploy production
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

---

## Troubleshooting

### "Could not detect username"

**Cause:** Script couldn't find username via any method  
**Solution:** Set explicit prefix in MODEL_VERSION.json

```json
{
  "version": "1.0.0",
  "model_prefix": "MY-MODELS",  ← Set explicitly
  ...
}
```

### Username has special characters

**Example:** Username is `sarah.smith@company`  
**Result:** Prefix becomes `SARAH.SMITH@COMPANY-MODELS`

**If you want cleaner prefix:**
```json
{
  "version": "1.0.0",
  "model_prefix": "SARAH-MODELS",  ← Set custom prefix
  ...
}
```

### Want to use different name than username

**Example:** Username is `d.mishra` but you want `DPM-MODELS`

```json
{
  "version": "1.0.0",
  "model_prefix": "DPM-MODELS",  ← Override with custom
  ...
}
```

---

## Best Practices

### 1. Use "auto" for Development

```json
{
  "version": "1.0.0",
  "model_prefix": "auto",  ← Good for personal dev work
  ...
}
```

### 2. Use Custom for Production

```json
{
  "version": "2.0.0",
  "model_prefix": "TEAM-PRODUCTION",  ← Explicit for production
  ...
}
```

### 3. Use Custom for Experiments

```json
{
  "version": "1.0.0",
  "model_prefix": "EXPERIMENT-ROBERTA",  ← Descriptive for experiments
  ...
}
```

### 4. Document in Notes

```json
{
  "version": "1.0.0",
  "model_prefix": "auto",
  "notes": {
    "owner": "Auto-detected from username",
    "purpose": "Personal development models"
  },
  ...
}
```

---

## Summary

**Key Points:**
- Set `"model_prefix": "auto"` to use your username
- Script detects username via `$env:USERNAME`, `$env:USER`, or `whoami`
- Prefix becomes `{USERNAME}-MODELS` (uppercase)
- No GCS permission issues - permissions are at bucket level
- Perfect for team collaboration with zero coordination

**Quick Setup:**
1. Edit MODEL_VERSION.json: `"model_prefix": "auto"`
2. Run: `.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints`
3. Done! Models automatically go to `{YOUR-USERNAME}-MODELS/`

**Benefits:**
- ✅ Zero configuration
- ✅ Automatic organization
- ✅ No conflicts
- ✅ Team-friendly
- ✅ No permission issues
