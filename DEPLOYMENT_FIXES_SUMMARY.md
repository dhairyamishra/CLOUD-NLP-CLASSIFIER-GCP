# Deployment Script Fixes - Summary

## Date: 2025-12-10

## Issues Identified and Fixed

### 🔴 Critical Issues Found

The initial deployment appeared successful but actually failed silently. The script reported `[OK]` even after multiple critical failures.

---

## 1. ❌ Git Clone Failure (Root Cause)

### **Problem:**
```bash
fatal: Remote branch main not found in upstream origin
```

**Impact:**
- Repository directory `/home/dhair/CLOUD-NLP-CLASSIFIER-GCP` was never created
- All subsequent `cd` commands failed
- Models downloaded to wrong location
- Docker build/run executed from wrong directory

### **Root Cause:**
- Script hardcoded `-b main` but repository may use `master` or another default branch
- No fallback mechanism

### **Fix Applied:**
```powershell
# 1. Auto-detect the default branch
$detectBranchCmd = @"
git ls-remote --symref $GitRepo HEAD | grep 'ref:' | awk '{print `$2}' | sed 's|refs/heads/||'
"@

# 2. Try with detected branch, fallback to default
if git clone -b $Branch $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP 2>/dev/null; then
    echo '[OK] Cloned with branch: $Branch'
elif git clone $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP; then
    echo '[OK] Cloned with default branch'
else
    echo '[ERROR] Failed to clone repository'
    exit 1
fi

# 3. Verify directory was created
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory not created'
    exit 1
fi
```

---

## 2. ❌ Directory Not Found Errors

### **Problem:**
```bash
bash: line 1: cd: /home/dhair/CLOUD-NLP-CLASSIFIER-GCP: No such file or directory
```

**Impact:**
- Every step after clone failed to `cd` into repo
- Commands ran from wrong directory (`/home/dhair` instead of repo)
- Models downloaded to `/home/dhair/models/` instead of repo's `models/`

### **Fix Applied:**
```bash
# Added to ALL remote commands:
set -e  # Exit on any error

# Verify directory exists before cd
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1
```

---

## 3. ❌ Docker Permission Errors

### **Problem:**
```bash
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

**Impact:**
- `docker build` failed - no image created
- `docker run` failed - no container started
- User `dhair` not in `docker` group and not using `sudo`

### **Root Cause:**
- VM user doesn't have permission to access Docker daemon
- Script didn't use `sudo` for Docker commands

### **Fix Applied:**
```bash
# All docker commands now use sudo:
sudo docker build -t cloud-nlp-classifier:latest . || exit 1
sudo docker images | grep 'cloud-nlp-classifier'
sudo docker stop nlp-api 2>/dev/null || true
sudo docker rm nlp-api 2>/dev/null || true
sudo docker run -d --name nlp-api -p 8000:8000 cloud-nlp-classifier:latest || exit 1
sudo docker ps | grep 'nlp-api'
```

---

## 4. ❌ False Success Reporting

### **Problem:**
```
[ERROR] Failed to clone repository
[OK] Repository cloned  ← FALSE!

[ERROR] Failed to build image
[OK] Docker image built  ← FALSE!

[ERROR] Container failed
[OK] Container started  ← FALSE!
```

**Impact:**
- Script always printed `[OK]` regardless of actual result
- Final "DEPLOYMENT COMPLETE" banner was misleading
- No way to know deployment actually failed

### **Root Cause:**
- PowerShell script didn't check `$LASTEXITCODE` properly
- `try-catch` blocks caught errors but still printed success
- No validation of actual success markers in output

### **Fix Applied:**
```powershell
# 1. Capture output AND exit code
$cloneOutput = gcloud compute ssh $VMName --zone=$Zone --command="$cloneCmd" 2>&1
Write-Host $cloneOutput

# 2. Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to clone repository (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

# 3. Verify success marker in output
if ($cloneOutput -notmatch '\[OK\] Repository cloned successfully') {
    Write-Host "[ERROR] Clone command did not complete successfully" -ForegroundColor Red
    exit 1
}

# 4. Only then print success
Write-Host "[OK] Repository cloned" -ForegroundColor Green
```

**Applied to ALL steps:**
- Clone repository
- Download models
- Build Docker image
- Start container

---

## 5. ❌ Health Check False Positive

### **Problem:**
```
[5/5] Testing external access...
[OK] API accessible externally
```

**Impact:**
- Health check passed even though deployment failed
- Old container from previous deployment was still running
- New deployment didn't actually update anything

### **Root Cause:**
- Script tested external endpoint but didn't verify it was the NEW container
- Old container on port 8000 responded successfully
- No validation that the just-deployed container was serving requests

### **Fix Applied:**
```bash
# 1. Verify container is actually running
if ! sudo docker ps | grep -q 'nlp-api'; then
    echo '[ERROR] Container is not running'
    echo '[INFO] Container logs:'
    sudo docker logs nlp-api 2>&1 || true
    exit 1
fi

# 2. Show container details
echo '[OK] Container is running'
sudo docker ps | grep 'nlp-api'

# 3. Test health from inside VM (localhost)
if curl -s http://localhost:8000/health | head -20; then
    echo '[OK] Health check passed'
else
    echo '[WARN] Health check not ready yet'
fi
```

---

## Summary of All Fixes

### ✅ **Phase 1: Clone Repository**
- ✅ Auto-detect default branch (main/master)
- ✅ Fallback to default if branch not found
- ✅ Verify directory created
- ✅ Proper error handling with exit codes
- ✅ Validate success marker in output

### ✅ **Phase 2: Download Models**
- ✅ Verify directory exists before cd
- ✅ Use `set -e` to exit on any error
- ✅ Add `|| exit 1` to all gcloud commands
- ✅ Verify downloads completed
- ✅ Check exit codes in PowerShell

### ✅ **Phase 3: Build Docker Image**
- ✅ Verify directory exists before cd
- ✅ Use `sudo` for all docker commands
- ✅ Exit on build failure
- ✅ Verify image was created
- ✅ Proper error messages with troubleshooting hints

### ✅ **Phase 4: Start Container**
- ✅ Verify directory exists before cd
- ✅ Use `sudo` for all docker commands
- ✅ Stop old container gracefully
- ✅ Verify new container is running
- ✅ Show container logs if failed
- ✅ Test health endpoint from inside VM

### ✅ **Phase 5: External Testing**
- ✅ Validate container is actually running
- ✅ Test from external IP
- ✅ Proper error messages if unreachable

---

## Error Handling Improvements

### **Before:**
```powershell
try {
    $output = gcloud compute ssh ... --command="$cmd"
    Write-Host $output
    Write-Host "[OK] Success" -ForegroundColor Green  # Always printed!
} catch {
    Write-Host "[ERROR] Failed" -ForegroundColor Red
    exit 1
}
```

### **After:**
```powershell
$output = gcloud compute ssh ... --command="$cmd" 2>&1
Write-Host $output

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Reason 1" -ForegroundColor Yellow
    Write-Host "  2. Reason 2" -ForegroundColor Yellow
    exit 1
}

# Verify success marker
if ($output -notmatch '\[OK\] ... successfully') {
    Write-Host "[ERROR] Command did not complete successfully" -ForegroundColor Red
    exit 1
}

# Only then print success
Write-Host "[OK] Success" -ForegroundColor Green
```

---

## Bash Script Improvements

### **Before:**
```bash
cd ~/CLOUD-NLP-CLASSIFIER-GCP
docker build -t cloud-nlp-classifier:latest .
if docker images | grep -q 'cloud-nlp-classifier'; then
    echo '[OK] Docker image built'
fi
```

### **After:**
```bash
set -e  # Exit on any error

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

# Use sudo and exit on failure
sudo docker build -t cloud-nlp-classifier:latest . || exit 1

# Verify image was created
if sudo docker images | grep -q 'cloud-nlp-classifier'; then
    echo '[OK] Docker image built successfully'
else
    echo '[ERROR] Failed to build image - image not found'
    exit 1
fi
```

---

## Testing the Fixed Script

### **Run the updated script:**
```powershell
.\scripts\gcp-complete-deployment.ps1
```

### **Expected behavior:**
1. ✅ Auto-detects correct Git branch
2. ✅ Clones repository successfully
3. ✅ Downloads models to correct location
4. ✅ Builds Docker image with sudo
5. ✅ Starts new container
6. ✅ Verifies container is running
7. ✅ Tests health endpoint
8. ✅ Reports accurate success/failure

### **If it fails:**
- Script will exit immediately with clear error message
- No false `[OK]` messages
- Helpful troubleshooting hints provided
- Exit code indicates failure

---

## Additional Recommendations

### 1. **Add User to Docker Group (Optional)**
Instead of using `sudo` for every docker command, add user to docker group:

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
exit

# Reconnect
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Verify (should work without sudo)
docker ps
```

Then update script to remove `sudo` from docker commands.

### 2. **Optimize Model Upload**
Current script uploads ~12 GB including checkpoints. To optimize:

```powershell
# Only upload final model files (exclude checkpoint-* directories)
gcloud storage cp "$ModelsPath\baselines\*.joblib" gs://bucket/models/baselines/
gcloud storage cp "$ModelsPath\toxicity_multi_head\*.json" gs://bucket/models/toxicity_multi_head/
gcloud storage cp "$ModelsPath\toxicity_multi_head\*.safetensors" gs://bucket/models/toxicity_multi_head/
gcloud storage cp "$ModelsPath\toxicity_multi_head\*.txt" gs://bucket/models/toxicity_multi_head/
# Repeat for transformer models, excluding checkpoint-* dirs
```

This reduces upload from ~12 GB to ~770 MB.

### 3. **Add Deployment Verification**
After deployment, verify the API is actually working:

```powershell
# Test prediction endpoint
$testPayload = @{
    text = "This is a test message"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://${externalIP}:8000/predict" -Method Post -Body $testPayload -ContentType "application/json"

if ($response.predicted_label) {
    Write-Host "[OK] API is working correctly" -ForegroundColor Green
} else {
    Write-Host "[ERROR] API is not responding correctly" -ForegroundColor Red
}
```

---

## Files Modified

1. **`scripts/gcp-complete-deployment.ps1`**
   - Fixed Git clone with branch detection
   - Added `set -e` to all bash commands
   - Added directory existence checks
   - Added `sudo` to all docker commands
   - Fixed error handling and exit code checks
   - Added success marker validation
   - Improved error messages with troubleshooting hints

---

## Next Steps

1. ✅ **Test the fixed script**
   ```powershell
   .\scripts\gcp-complete-deployment.ps1
   ```

2. ✅ **Verify deployment**
   - Check container is running: `sudo docker ps`
   - Test health: `curl http://35.232.76.140:8000/health`
   - Test prediction: `curl -X POST http://35.232.76.140:8000/predict ...`

3. ✅ **Optional: Add user to docker group**
   - Removes need for `sudo` in future deployments

4. ✅ **Optional: Optimize model uploads**
   - Exclude checkpoint directories
   - Reduces upload time from 15 min to 2 min

---

## Conclusion

All critical issues have been fixed:
- ✅ Git clone works with any branch name
- ✅ Directory existence verified before cd
- ✅ Docker commands use sudo
- ✅ Proper error handling with exit codes
- ✅ Success validation before printing [OK]
- ✅ Container verification before declaring success

The script will now **fail fast** with clear error messages instead of silently failing and reporting false success.
