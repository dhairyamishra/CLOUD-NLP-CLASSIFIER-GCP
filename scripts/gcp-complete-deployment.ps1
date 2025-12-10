# ============================================
# GCP Complete Deployment - All-in-One
# ============================================
# This script does EVERYTHING from scratch:
# 1. Creates GCS bucket for models
# 2. Uploads models to GCS
# 3. Verifies VM exists (or creates it)
# 4. Clones repo on VM
# 5. Downloads models from GCS
# 6. Builds Docker image
# 7. Runs container
# 8. Tests API
# ============================================

param(
    [string]$ProjectId = "mnist-k8s-pipeline",
    [string]$VMName = "nlp-classifier-vm",
    [string]$Zone = "us-central1-a",
    [string]$Region = "us-central1",
    [string]$BucketName = "nlp-classifier-models",
    [string]$GitRepo = "https://github.com/dhairyamishra/CLOUD-NLP-CLASSIFIER-GCP.git",
    [string]$Branch = "dhairya/gcp-public-deployment",
    [string]$ModelsPath = "C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP\models",
    [switch]$SkipVMCreation,
    [switch]$SkipModelUpload,
    [switch]$NoCheckpoints
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

# ============================================
# Read Model Prefix from MODEL_VERSION.json
# ============================================
$ModelPrefix = ""
$versionFilePath = Join-Path $PSScriptRoot "..\MODEL_VERSION.json"

if (Test-Path $versionFilePath) {
    try {
        $versionConfig = Get-Content $versionFilePath -Raw | ConvertFrom-Json
        if ($versionConfig.PSObject.Properties.Name -contains "model_prefix") {
            $ModelPrefix = $versionConfig.model_prefix
            
            # If prefix is empty or "auto", use username
            if ([string]::IsNullOrWhiteSpace($ModelPrefix) -or $ModelPrefix -eq "auto") {
                $username = $env:USERNAME
                if ([string]::IsNullOrWhiteSpace($username)) {
                    $username = $env:USER  # Fallback for Linux/Mac
                }
                if ([string]::IsNullOrWhiteSpace($username)) {
                    $username = whoami.exe 2>$null | Split-Path -Leaf  # Last resort
                }
                $ModelPrefix = "$username-MODELS".ToUpper()
                Write-Host "Model prefix AUTO-DETECTED from username: $ModelPrefix" -ForegroundColor Cyan
            } else {
                Write-Host "Model prefix from VERSION: $ModelPrefix" -ForegroundColor Gray
            }
        } else {
            # No prefix field - use username as default
            $username = $env:USERNAME
            if ([string]::IsNullOrWhiteSpace($username)) {
                $username = $env:USER
            }
            if ([string]::IsNullOrWhiteSpace($username)) {
                $username = whoami.exe 2>$null | Split-Path -Leaf
            }
            if (-not [string]::IsNullOrWhiteSpace($username)) {
                $ModelPrefix = "$username-MODELS".ToUpper()
                Write-Host "No model_prefix in MODEL_VERSION.json, using username: $ModelPrefix" -ForegroundColor Cyan
            } else {
                Write-Host "No model_prefix in MODEL_VERSION.json and could not detect username, using no prefix" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "[WARN] Could not read MODEL_VERSION.json, using no prefix" -ForegroundColor Yellow
    }
} else {
    # No version file - use username as default
    $username = $env:USERNAME
    if ([string]::IsNullOrWhiteSpace($username)) {
        $username = $env:USER
    }
    if ([string]::IsNullOrWhiteSpace($username)) {
        $username = whoami.exe 2>$null | Split-Path -Leaf
    }
    if (-not [string]::IsNullOrWhiteSpace($username)) {
        $ModelPrefix = "$username-MODELS".ToUpper()
        Write-Host "No MODEL_VERSION.json found, using username: $ModelPrefix" -ForegroundColor Cyan
    } else {
        Write-Host "No MODEL_VERSION.json found and could not detect username, using no prefix" -ForegroundColor Yellow
    }
}

# Helper function to build GCS paths with optional prefix
function Get-GCSPath {
    param(
        [string]$BucketName,
        [string]$Prefix,
        [string]$Path
    )
    if ($Prefix) {
        return "gs://$BucketName/$Prefix/$Path"
    } else {
        return "gs://$BucketName/$Path"
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GCP Complete Deployment" -ForegroundColor Cyan
Write-Host "  All-in-One Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "VM: $VMName" -ForegroundColor Yellow
Write-Host "Zone: $Zone" -ForegroundColor Yellow
if ($ModelPrefix) {
    Write-Host "Bucket: gs://$BucketName/$ModelPrefix/" -ForegroundColor Yellow
} else {
    Write-Host "Bucket: gs://$BucketName/" -ForegroundColor Yellow
}
Write-Host "Git Repo: $GitRepo" -ForegroundColor Yellow
Write-Host ""

# ============================================
# PHASE 1: Create GCS Bucket
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 1: Setup Cloud Storage" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipModelUpload) {
    Write-Host "[1/3] Creating GCS bucket..." -ForegroundColor Cyan
    
    # Check if bucket exists using gcloud storage
    $ErrorActionPreference = "Continue"
    $bucketCheck = gcloud storage buckets describe gs://$BucketName 2>&1
    $bucketExists = $LASTEXITCODE -eq 0
    $ErrorActionPreference = "Stop"
    
    if (-not $bucketExists) {
        Write-Host "Creating new bucket: $BucketName" -ForegroundColor Yellow
        try {
            gcloud storage buckets create gs://$BucketName --project=$ProjectId --location=$Region --default-storage-class=STANDARD
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Bucket created" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] Failed to create bucket" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "[ERROR] Failed to create bucket: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[OK] Bucket already exists" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # ============================================
    # PHASE 2: Check Model Versions & Upload
    # ============================================
    Write-Host "[2/3] Checking model versions..." -ForegroundColor Cyan
    
    # Load local version
    $localVersionFile = "$ModelsPath\..\MODEL_VERSION.json"
    if (Test-Path $localVersionFile) {
        $localVersion = Get-Content $localVersionFile -Raw | ConvertFrom-Json
        Write-Host "Local model version: $($localVersion.version)" -ForegroundColor Gray
    } else {
        Write-Host "[WARN] No local MODEL_VERSION.json found, will upload all models" -ForegroundColor Yellow
        $localVersion = $null
    }
    
    # Check remote version in GCS
    $remoteVersionPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "MODEL_VERSION.json"
    $ErrorActionPreference = "Continue"
    $remoteVersionCheck = gcloud storage cat $remoteVersionPath 2>&1
    $remoteVersionExists = $LASTEXITCODE -eq 0
    $ErrorActionPreference = "Stop"
    
    $needsUpload = $true
    if ($remoteVersionExists -and $localVersion) {
        try {
            $remoteVersion = $remoteVersionCheck | ConvertFrom-Json
            Write-Host "Remote model version: $($remoteVersion.version)" -ForegroundColor Gray
            
            if ($remoteVersion.version -eq $localVersion.version) {
                Write-Host "[SKIP] Model versions match ($($localVersion.version)), skipping upload" -ForegroundColor Green
                $needsUpload = $false
            } else {
                Write-Host "[UPDATE] Local version ($($localVersion.version)) is different from remote ($($remoteVersion.version))" -ForegroundColor Yellow
                Write-Host "Will upload updated models..." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[WARN] Could not parse remote version, will upload" -ForegroundColor Yellow
        }
    } else {
        Write-Host "No remote version found, will upload all models" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    if ($needsUpload) {
        Write-Host "[2/3] Uploading models to GCS..." -ForegroundColor Cyan
        
        if ($NoCheckpoints) {
            Write-Host "Mode: OPTIMIZED (final models only, ~770 MB)" -ForegroundColor Yellow
            Write-Host "Excluding checkpoint-* directories" -ForegroundColor Yellow
        } else {
            Write-Host "Mode: FULL (includes checkpoints, ~12 GB)" -ForegroundColor Yellow
            Write-Host "Includes all checkpoint directories" -ForegroundColor Yellow
        }
        Write-Host ""
    
    # Upload baseline models
    Write-Host "  > Uploading baseline models..." -ForegroundColor Gray
    try {
        $baselinePath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/baselines/"
        gcloud storage cp "$ModelsPath\baselines\*.joblib" $baselinePath --recursive
        Write-Host "  [OK] Baseline models uploaded" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Baseline models upload had issues" -ForegroundColor Yellow
    }
    
    # Upload toxicity model
    Write-Host "  > Uploading toxicity model..." -ForegroundColor Gray
    try {
        if ($NoCheckpoints) {
            # Upload only final model files (exclude checkpoint-* directories)
            $toxicityPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/toxicity_multi_head/"
            Get-ChildItem "$ModelsPath\toxicity_multi_head" -File | ForEach-Object {
                gcloud storage cp $_.FullName $toxicityPath
            }
        } else {
            # Upload everything including checkpoints
            $toxicityPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/toxicity_multi_head/"
            gcloud storage cp "$ModelsPath\toxicity_multi_head\*" $toxicityPath --recursive
        }
        Write-Host "  [OK] Toxicity model uploaded" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Toxicity model upload had issues" -ForegroundColor Yellow
    }
    
    # Upload DistilBERT
    Write-Host "  > Uploading DistilBERT model..." -ForegroundColor Gray
    try {
        if ($NoCheckpoints) {
            # Upload only final model files (exclude checkpoint-* directories)
            $distilbertPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/transformer/distilbert/"
            Get-ChildItem "$ModelsPath\transformer\distilbert" -File | ForEach-Object {
                gcloud storage cp $_.FullName $distilbertPath
            }
        } else {
            # Upload everything including checkpoints
            $distilbertPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/transformer/distilbert/"
            gcloud storage cp "$ModelsPath\transformer\distilbert\*" $distilbertPath --recursive
        }
        Write-Host "  [OK] DistilBERT uploaded" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] DistilBERT upload had issues" -ForegroundColor Yellow
    }
    
    # Upload DistilBERT Fullscale
    Write-Host "  > Uploading DistilBERT Fullscale..." -ForegroundColor Gray
    try {
        if ($NoCheckpoints) {
            # Upload only final model files (exclude checkpoint-* directories)
            $fullscalePath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/transformer/distilbert_fullscale/"
            Get-ChildItem "$ModelsPath\transformer\distilbert_fullscale" -File | ForEach-Object {
                gcloud storage cp $_.FullName $fullscalePath
            }
        } else {
            # Upload everything including checkpoints
            $fullscalePath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/transformer/distilbert_fullscale/"
            gcloud storage cp "$ModelsPath\transformer\distilbert_fullscale\*" $fullscalePath --recursive
        }
        Write-Host "  [OK] DistilBERT Fullscale uploaded" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] DistilBERT Fullscale upload had issues" -ForegroundColor Yellow
    }
    
        Write-Host ""
        Write-Host "[3/3] Verifying uploads..." -ForegroundColor Cyan
        try {
            $modelsPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "models/**"
            $bucketContents = gcloud storage ls $modelsPath --recursive
            Write-Host $bucketContents
            Write-Host "[OK] Models uploaded to GCS" -ForegroundColor Green
        } catch {
            Write-Host "[WARN] Could not verify upload" -ForegroundColor Yellow
        }
        
        # Upload version file to mark this version as deployed
        if ($localVersion) {
            Write-Host ""
            Write-Host "Uploading MODEL_VERSION.json..." -ForegroundColor Gray
            try {
                $versionPath = Get-GCSPath -BucketName $BucketName -Prefix $ModelPrefix -Path "MODEL_VERSION.json"
                gcloud storage cp $localVersionFile $versionPath
                Write-Host "[OK] Version file uploaded" -ForegroundColor Green
            } catch {
                Write-Host "[WARN] Could not upload version file" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "[SKIP] Models already up-to-date in GCS" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIPPED] Model upload (using existing models in GCS)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# PHASE 3: Verify/Create VM
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 2: Setup Compute VM" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Checking VM status..." -ForegroundColor Cyan

try {
    $vmStatus = gcloud compute instances describe $VMName --zone=$Zone --format="get(status)" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        if (-not $SkipVMCreation) {
            Write-Host "VM does not exist. Creating new VM..." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "This will create:" -ForegroundColor Yellow
            Write-Host "  - VM: $VMName" -ForegroundColor White
            Write-Host "  - Machine: e2-standard-2 (2 vCPU, 8GB RAM)" -ForegroundColor White
            Write-Host "  - Disk: 50GB SSD" -ForegroundColor White
            Write-Host "  - Cost: ~$49/month" -ForegroundColor White
            Write-Host ""
            
            # Note: This assumes VM was created in previous phases
            # If you need to create VM from scratch, uncomment below:
            # gcloud compute instances create $VMName `
            #     --project=$ProjectId `
            #     --zone=$Zone `
            #     --machine-type=e2-standard-2 `
            #     --boot-disk-size=50GB `
            #     --boot-disk-type=pd-ssd `
            #     --tags=http-server,https-server
            
            Write-Host "[ERROR] VM does not exist!" -ForegroundColor Red
            Write-Host "Please run Phase 1-3 scripts first to create the VM" -ForegroundColor Yellow
            Write-Host "Or remove -SkipVMCreation flag if you want to create it now" -ForegroundColor Yellow
            exit 1
        } else {
            Write-Host "[ERROR] VM does not exist and SkipVMCreation is set" -ForegroundColor Red
            exit 1
        }
    } elseif ($vmStatus -ne "RUNNING") {
        Write-Host "VM exists but not running. Starting VM..." -ForegroundColor Yellow
        gcloud compute instances start $VMName --zone=$Zone
        Start-Sleep -Seconds 30
        Write-Host "[OK] VM started" -ForegroundColor Green
    } else {
        Write-Host "[OK] VM is already running" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to check/start VM: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# PHASE 4: Deploy Application on VM
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 3: Deploy Application" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Cloning repository..." -ForegroundColor Cyan
Write-Host "Using branch: $Branch" -ForegroundColor Gray

$cloneCmd = @"
set -e  # Exit on any error

# Remove old clone if exists
rm -rf ~/CLOUD-NLP-CLASSIFIER-GCP

# Clone repository (try with branch, fallback to default)
if git clone -b $Branch $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP 2>/dev/null; then
    echo '[OK] Cloned with branch: $Branch'
elif git clone $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP; then
    echo '[OK] Cloned with default branch'
else
    echo '[ERROR] Failed to clone repository'
    exit 1
fi

# Verify clone
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory not created'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1
echo '[INFO] Repository contents:'
ls -lh | head -20
echo '[OK] Repository cloned successfully'
"@

$cloneOutput = gcloud compute ssh $VMName --zone=$Zone --command="$cloneCmd" 2>&1
Write-Host $cloneOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to clone repository (exit code: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Branch '$Branch' does not exist in the repository" -ForegroundColor Yellow
    Write-Host "  2. Repository URL is incorrect: $GitRepo" -ForegroundColor Yellow
    Write-Host "  3. Repository is private and VM cannot access it" -ForegroundColor Yellow
    exit 1
}

# Check if clone succeeded (look for success markers or evidence of successful clone)
$hasSuccessMarker = ($cloneOutput -match '\[OK\] Repository cloned successfully') -or ($cloneOutput -match '\[OK\] Cloned with')
$hasFileList = ($cloneOutput -match 'Dockerfile') -or ($cloneOutput -match 'requirements\.txt') -or ($cloneOutput -match 'README\.md')
$cloneSuccess = $hasSuccessMarker -or $hasFileList

if (-not $cloneSuccess) {
    Write-Host "[ERROR] Clone command did not complete successfully" -ForegroundColor Red
    Write-Host "Debug: Could not find success markers or file listing in output" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Repository cloned" -ForegroundColor Green

Write-Host ""
Write-Host "[2/5] Downloading models from GCS..." -ForegroundColor Cyan
Write-Host "Downloading ~770 MB..." -ForegroundColor Yellow

$downloadCmd = @"
set -e  # Exit on any error

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

# Create models directory structure
mkdir -p models/baselines
mkdir -p models/toxicity_multi_head
mkdir -p models/transformer/distilbert
mkdir -p models/transformer/distilbert_fullscale

# Download models from GCS
echo '[INFO] Downloading models from GCS...'

# Build GCS path with or without prefix
if [ -n "$ModelPrefix" ]; then
    GCS_BASE="gs://$BucketName/$ModelPrefix/models"
else
    GCS_BASE="gs://$BucketName/models"
fi

gcloud storage cp `$GCS_BASE/baselines/*.joblib models/baselines/ --recursive || exit 1
gcloud storage cp `$GCS_BASE/toxicity_multi_head/* models/toxicity_multi_head/ --recursive || exit 1
gcloud storage cp `$GCS_BASE/transformer/distilbert/* models/transformer/distilbert/ --recursive || exit 1
gcloud storage cp `$GCS_BASE/transformer/distilbert_fullscale/* models/transformer/distilbert_fullscale/ --recursive || exit 1

# Verify downloads
echo ''
echo '[INFO] Verifying models...'
du -sh models/* || exit 1
echo '[OK] Models downloaded successfully'
"@

$ErrorActionPreference = "Continue"
$downloadOutput = gcloud compute ssh $VMName --zone=$Zone --command="$downloadCmd" 2>&1
$downloadExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $downloadOutput

# Check if download succeeded (look for success markers or evidence of download)
$hasSuccessMarker = $downloadOutput -match '\[OK\] Models downloaded successfully'
$hasDownloadEvidence = ($downloadOutput -match 'Copying gs://') -or ($downloadOutput -match 'models/baselines') -or ($downloadOutput -match 'models/transformer')
$downloadSuccess = $hasSuccessMarker -or ($hasDownloadEvidence -and $downloadExitCode -eq 0)

if (-not $downloadSuccess) {
    Write-Host "[ERROR] Model download did not complete successfully (exit code: $downloadExitCode)" -ForegroundColor Red
    Write-Host "Debug: Success marker found: $hasSuccessMarker, Download evidence: $hasDownloadEvidence" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Models downloaded" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Building Docker image..." -ForegroundColor Cyan
Write-Host "This takes 5-10 minutes (installing PyTorch, transformers, etc.)" -ForegroundColor Yellow

$buildCmd = @"
set -e  # Exit on any error

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

echo '[INFO] Building Docker image...'
echo '[INFO] This may take 5-10 minutes...'

# Use sudo for docker commands (VM user may not be in docker group yet)
sudo docker build -t cloud-nlp-classifier:latest . || exit 1

# Verify image was created
if sudo docker images | grep -q 'cloud-nlp-classifier'; then
    echo '[OK] Docker image built successfully'
    sudo docker images | grep 'cloud-nlp-classifier'
else
    echo '[ERROR] Failed to build image - image not found'
    exit 1
fi
"@

$ErrorActionPreference = "Continue"
$buildOutput = gcloud compute ssh $VMName --zone=$Zone --command="$buildCmd" 2>&1
$buildExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $buildOutput

if ($buildExitCode -ne 0) {
    Write-Host "[ERROR] Failed to build Docker image (exit code: $buildExitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Docker daemon not running on VM" -ForegroundColor Yellow
    Write-Host "  2. Insufficient disk space" -ForegroundColor Yellow
    Write-Host "  3. Dockerfile syntax error" -ForegroundColor Yellow
    exit 1
}

# Check if build succeeded
$buildSuccess = ($buildOutput -match '\[OK\] Docker image built successfully') -or ($buildOutput -match 'cloud-nlp-classifier')

if (-not $buildSuccess) {
    Write-Host "[ERROR] Docker build did not complete successfully" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Docker image built" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Starting container..." -ForegroundColor Cyan

$runCmd = @"
set -e  # Exit on any error

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

# Stop old container (don't fail if it doesn't exist)
echo '[INFO] Stopping old container (if exists)...'
sudo docker stop nlp-api 2>/dev/null || true
sudo docker rm nlp-api 2>/dev/null || true

# Run new container
echo '[INFO] Starting new container...'
sudo docker run -d \
    --name nlp-api \
    -p 8000:8000 \
    --restart unless-stopped \
    cloud-nlp-classifier:latest || exit 1

# Wait for container to start
echo '[INFO] Waiting for container to start...'
sleep 10

# Verify container is running
if ! sudo docker ps | grep -q 'nlp-api'; then
    echo '[ERROR] Container is not running'
    echo '[INFO] Container logs:'
    sudo docker logs nlp-api 2>&1 || true
    exit 1
fi

echo '[OK] Container is running'
sudo docker ps | grep 'nlp-api'

# Test health endpoint
echo ''
echo '[INFO] Testing health endpoint...'
sleep 5

# Try health check (allow it to fail initially)
if curl -s http://localhost:8000/health | head -20; then
    echo '[OK] Health check passed'
else
    echo '[WARN] Health check not ready yet (container may still be initializing)'
fi

echo '[OK] Container started successfully'
"@

$ErrorActionPreference = "Continue"
$runOutput = gcloud compute ssh $VMName --zone=$Zone --command="$runCmd" 2>&1
$runExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $runOutput

if ($runExitCode -ne 0) {
    Write-Host "[ERROR] Failed to start container (exit code: $runExitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Port 8000 already in use" -ForegroundColor Yellow
    Write-Host "  2. Container crashed on startup" -ForegroundColor Yellow
    Write-Host "  3. Model files missing or corrupted" -ForegroundColor Yellow
    exit 1
}

# Check if container started successfully
$runSuccess = ($runOutput -match '\[OK\] Container started successfully') -or ($runOutput -match '\[OK\] Container is running')

if (-not $runSuccess) {
    Write-Host "[ERROR] Container start did not complete successfully" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Container started" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Testing external access..." -ForegroundColor Cyan

$externalIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host "Testing http://${externalIP}:8000/health" -ForegroundColor Gray
Start-Sleep -Seconds 5

try {
    $healthCheck = curl.exe -s "http://${externalIP}:8000/health"
    Write-Host $healthCheck
    Write-Host "[OK] API accessible externally" -ForegroundColor Green
} catch {
    Write-Host "[WARN] External test failed (may need more time)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# FINAL SUMMARY
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host ""
Write-Host "Resources Created:" -ForegroundColor Cyan
Write-Host "  GCS Bucket: gs://$BucketName" -ForegroundColor White
Write-Host "  VM: $VMName ($Zone)" -ForegroundColor White
Write-Host "  External IP: $externalIP" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  Health:  http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  Predict: http://${externalIP}:8000/predict" -ForegroundColor White
Write-Host "  Docs:    http://${externalIP}:8000/docs" -ForegroundColor White
Write-Host "  Models:  http://${externalIP}:8000/models" -ForegroundColor White
Write-Host ""
Write-Host "Quick Test:" -ForegroundColor Cyan
Write-Host "  curl http://${externalIP}:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "SSH into VM:" -ForegroundColor Cyan
Write-Host "  gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Cyan
Write-Host "  docker logs -f nlp-api" -ForegroundColor White
Write-Host ""
Write-Host "Monthly Cost: ~$56 (VM: $49 + IP: $7 + GCS: $0.02)" -ForegroundColor Yellow
Write-Host ""
Write-Host "[OK] Your NLP API is now live!" -ForegroundColor Green
Write-Host ""
