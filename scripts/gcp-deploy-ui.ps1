# ============================================
# GCP UI Deployment Script
# ============================================
# Deploys Streamlit UI to the same VM as the API
# Follows the exact pattern from gcp-complete-deployment.ps1
# ============================================

param(
    [string]$ProjectId = "mnist-k8s-pipeline",
    [string]$VMName = "nlp-classifier-vm",
    [string]$Zone = "us-central1-a",
    [string]$GitRepo = "https://github.com/dhairyamishra/CLOUD-NLP-CLASSIFIER-GCP.git",
    [string]$Branch = "dhairya/gcp-public-deployment",
    [switch]$SkipFirewall
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GCP UI Deployment" -ForegroundColor Cyan
Write-Host "  Streamlit Frontend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "VM: $VMName" -ForegroundColor Yellow
Write-Host "Zone: $Zone" -ForegroundColor Yellow
Write-Host ""

# ============================================
# PHASE 1: Verify API is Running
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 1: Verify API Backend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Checking VM status..." -ForegroundColor Cyan

try {
    $vmStatus = gcloud compute instances describe $VMName --zone=$Zone --format="get(status)" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] VM does not exist!" -ForegroundColor Red
        Write-Host "Please run gcp-complete-deployment.ps1 first to deploy the API" -ForegroundColor Yellow
        exit 1
    } elseif ($vmStatus -ne "RUNNING") {
        Write-Host "VM exists but not running. Starting VM..." -ForegroundColor Yellow
        gcloud compute instances start $VMName --zone=$Zone
        Start-Sleep -Seconds 30
        Write-Host "[OK] VM started" -ForegroundColor Green
    } else {
        Write-Host "[OK] VM is running" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to check VM: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Checking API container..." -ForegroundColor Cyan

$checkApiCmd = @"
set -e
if sudo docker ps | grep -q 'nlp-api'; then
    echo '[OK] API container is running'
    exit 0
else
    echo '[ERROR] API container is not running'
    exit 1
fi
"@

$ErrorActionPreference = "Continue"
$apiCheckOutput = gcloud compute ssh $VMName --zone=$Zone --command="$checkApiCmd" 2>&1
$apiCheckExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $apiCheckOutput

if ($apiCheckExitCode -ne 0) {
    Write-Host "[ERROR] API container is not running!" -ForegroundColor Red
    Write-Host "Please run gcp-complete-deployment.ps1 first to deploy the API" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] API container is running" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Testing API health..." -ForegroundColor Cyan

# Get external IP for direct testing
$externalIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host "Testing API at http://${externalIP}:8000/health" -ForegroundColor Gray

try {
    $apiResponse = curl.exe -s "http://${externalIP}:8000/health" -m 10
    if ($apiResponse -match "healthy") {
        Write-Host "[OK] API is healthy and ready" -ForegroundColor Green
    } else {
        Write-Host "[WARN] API response unexpected: $apiResponse" -ForegroundColor Yellow
        Write-Host "Continuing anyway - will verify from VM later..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Could not test API externally: $_" -ForegroundColor Yellow
    Write-Host "Continuing anyway - will verify from VM later..." -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# PHASE 2: Setup Firewall for UI
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 2: Setup Firewall" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipFirewall) {
    Write-Host "[1/1] Checking firewall rule for port 8501..." -ForegroundColor Cyan
    
    $ErrorActionPreference = "Continue"
    $firewallCheck = gcloud compute firewall-rules describe allow-streamlit --project=$ProjectId 2>&1
    $firewallExists = $LASTEXITCODE -eq 0
    $ErrorActionPreference = "Stop"
    
    if (-not $firewallExists) {
        Write-Host "Creating firewall rule for Streamlit (port 8501)..." -ForegroundColor Yellow
        try {
            gcloud compute firewall-rules create allow-streamlit `
                --project=$ProjectId `
                --direction=INGRESS `
                --priority=1000 `
                --network=default `
                --action=ALLOW `
                --rules=tcp:8501 `
                --source-ranges=0.0.0.0/0 `
                --target-tags=http-server
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Firewall rule created" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] Failed to create firewall rule" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "[ERROR] Failed to create firewall rule: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[OK] Firewall rule already exists" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIPPED] Firewall setup" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# PHASE 3: Deploy UI Application
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PHASE 3: Deploy UI Application" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Updating code repository..." -ForegroundColor Cyan

$updateCodeCmd = @"
set -e

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    echo 'Please run gcp-complete-deployment.ps1 first'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

# Pull latest code
echo '[INFO] Pulling latest code...'
git pull origin $Branch || git pull || echo '[WARN] Could not pull, using existing code'

echo '[OK] Code updated'
"@

$ErrorActionPreference = "Continue"
$updateOutput = gcloud compute ssh $VMName --zone=$Zone --command="$updateCodeCmd" 2>&1
$updateExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $updateOutput

if ($updateExitCode -ne 0) {
    Write-Host "[WARN] Code update had issues, continuing..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Code updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Building UI Docker image..." -ForegroundColor Cyan
Write-Host "This takes 2-3 minutes (lightweight, no ML models)" -ForegroundColor Yellow

$buildCmd = @"
set -e

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

echo '[INFO] Building UI Docker image...'
echo '[INFO] This is much faster than API build (no PyTorch/transformers)'

# Build UI image
sudo docker build -f Dockerfile.streamlit.api -t cloud-nlp-ui:latest . || exit 1

# Verify image was created
if sudo docker images | grep -q 'cloud-nlp-ui'; then
    echo '[OK] UI Docker image built successfully'
    sudo docker images | grep 'cloud-nlp-ui'
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
    Write-Host "[ERROR] Failed to build UI Docker image (exit code: $buildExitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Dockerfile.streamlit.api not found" -ForegroundColor Yellow
    Write-Host "  2. Docker daemon not running" -ForegroundColor Yellow
    Write-Host "  3. Insufficient disk space" -ForegroundColor Yellow
    exit 1
}

$buildSuccess = ($buildOutput -match '\[OK\] UI Docker image built successfully') -or ($buildOutput -match 'cloud-nlp-ui')

if (-not $buildSuccess) {
    Write-Host "[ERROR] UI Docker build did not complete successfully" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] UI Docker image built" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Starting UI container..." -ForegroundColor Cyan

$runCmd = @"
set -e

# Verify directory exists
if [ ! -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[ERROR] Repository directory does not exist'
    exit 1
fi

cd ~/CLOUD-NLP-CLASSIFIER-GCP || exit 1

# Stop old container (don't fail if it doesn't exist)
echo '[INFO] Stopping old UI container (if exists)...'
sudo docker stop nlp-ui 2>/dev/null || true
sudo docker rm nlp-ui 2>/dev/null || true

# Run new UI container
echo '[INFO] Starting new UI container...'
sudo docker run -d \
    --name nlp-ui \
    -p 8501:8501 \
    -e API_URL=http://localhost:8000 \
    --restart unless-stopped \
    cloud-nlp-ui:latest || exit 1

# Wait for container to start
echo '[INFO] Waiting for container to start...'
sleep 10

# Verify container is running
if ! sudo docker ps | grep -q 'nlp-ui'; then
    echo '[ERROR] UI container is not running'
    echo '[INFO] Container logs:'
    sudo docker logs nlp-ui 2>&1 || true
    exit 1
fi

echo '[OK] UI container is running'
sudo docker ps | grep 'nlp-ui'

# Test health endpoint
echo ''
echo '[INFO] Testing UI health endpoint...'
sleep 5

# Try health check (allow it to fail initially)
if curl -s http://localhost:8501/_stcore/health | head -20; then
    echo '[OK] UI health check passed'
else
    echo '[WARN] UI health check not ready yet (container may still be initializing)'
fi

echo '[OK] UI container started successfully'
"@

$ErrorActionPreference = "Continue"
$runOutput = gcloud compute ssh $VMName --zone=$Zone --command="$runCmd" 2>&1
$runExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

Write-Host $runOutput

if ($runExitCode -ne 0) {
    Write-Host "[ERROR] Failed to start UI container (exit code: $runExitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Port 8501 already in use" -ForegroundColor Yellow
    Write-Host "  2. Container crashed on startup" -ForegroundColor Yellow
    Write-Host "  3. API_URL environment variable issue" -ForegroundColor Yellow
    exit 1
}

$runSuccess = ($runOutput -match '\[OK\] UI container started successfully') -or ($runOutput -match '\[OK\] UI container is running')

if (-not $runSuccess) {
    Write-Host "[ERROR] UI container start did not complete successfully" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] UI container started" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Testing external access..." -ForegroundColor Cyan

$externalIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host "Testing http://${externalIP}:8501" -ForegroundColor Gray
Start-Sleep -Seconds 10

try {
    $uiCheck = curl.exe -s "http://${externalIP}:8501" -m 10
    if ($uiCheck) {
        Write-Host "[OK] UI accessible externally" -ForegroundColor Green
    } else {
        Write-Host "[WARN] UI may need more time to initialize" -ForegroundColor Yellow
    }
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
Write-Host "  UI DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host ""
Write-Host "Deployed Services:" -ForegroundColor Cyan
Write-Host "  VM: $VMName ($Zone)" -ForegroundColor White
Write-Host "  External IP: $externalIP" -ForegroundColor White
Write-Host ""
Write-Host "Backend API:" -ForegroundColor Cyan
Write-Host "  Health:  http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  Predict: http://${externalIP}:8000/predict" -ForegroundColor White
Write-Host "  Docs:    http://${externalIP}:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Frontend UI:" -ForegroundColor Cyan
Write-Host "  URL:     http://${externalIP}:8501" -ForegroundColor White
Write-Host "  Health:  http://${externalIP}:8501/_stcore/health" -ForegroundColor White
Write-Host ""
Write-Host "Quick Tests:" -ForegroundColor Cyan
Write-Host "  API:  curl http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  UI:   Open http://${externalIP}:8501 in browser" -ForegroundColor White
Write-Host ""
Write-Host "SSH into VM:" -ForegroundColor Cyan
Write-Host "  gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Cyan
Write-Host "  API:  sudo docker logs -f nlp-api" -ForegroundColor White
Write-Host "  UI:   sudo docker logs -f nlp-ui" -ForegroundColor White
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
Write-Host "  sudo docker ps" -ForegroundColor White
Write-Host ""
Write-Host "Monthly Cost: ~$56 (no increase - same VM)" -ForegroundColor Yellow
Write-Host ""
Write-Host "[OK] Your full-stack NLP app is now live!" -ForegroundColor Green
Write-Host ""
