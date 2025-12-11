# ============================================
# GCP VM Deployment - Phase 4: Git Clone & Deploy
# ============================================
# Project: CLOUD-NLP-CLASSIFIER-GCP
# Phase: 4/14 - Git-based Deployment
# Description: Clone repo and deploy with Docker on GCP VM
# ============================================

param(
    [string]$VMName = "nlp-classifier-vm",
    [string]$Zone = "us-central1-a",
    [string]$GitRepo = "https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GCP VM Deployment - Phase 4" -ForegroundColor Cyan
Write-Host "  Git Clone & Docker Deploy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VM: $VMName" -ForegroundColor Yellow
Write-Host "Zone: $Zone" -ForegroundColor Yellow
Write-Host "Git Repo: $GitRepo" -ForegroundColor Yellow
Write-Host "Branch: $Branch" -ForegroundColor Yellow
Write-Host ""

# ============================================
# Step 1: Verify VM is Running
# ============================================
Write-Host "[Step 1/5] Verifying VM status..." -ForegroundColor Cyan

try {
    $vmStatus = gcloud compute instances describe $VMName --zone=$Zone --format="get(status)" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get VM status: $vmStatus"
    }
    
    if ($vmStatus -ne "RUNNING") {
        Write-Host "VM is not running. Starting VM..." -ForegroundColor Yellow
        gcloud compute instances start $VMName --zone=$Zone
        Start-Sleep -Seconds 30
    }
    
    Write-Host "[OK] VM is RUNNING" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to verify VM status: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 2: Clone Repository
# ============================================
Write-Host "[Step 2/5] Cloning repository on VM..." -ForegroundColor Cyan

$cloneCmd = @"
# Remove old clone if exists
rm -rf ~/CLOUD-NLP-CLASSIFIER-GCP

# Clone repository
git clone -b $Branch $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP

# Verify clone
if [ -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[OK] Repository cloned successfully'
    cd ~/CLOUD-NLP-CLASSIFIER-GCP
    echo '[OK] Current directory:'
    pwd
    echo '[OK] Repository contents:'
    ls -lh
else
    echo '[ERROR] Failed to clone repository'
    exit 1
fi
"@

try {
    $cloneOutput = gcloud compute ssh $VMName --zone=$Zone --command="$cloneCmd"
    Write-Host $cloneOutput
    Write-Host "[OK] Repository cloned" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to clone repository: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "1. The repository URL is correct" -ForegroundColor Yellow
    Write-Host "2. The repository is public (or VM has access)" -ForegroundColor Yellow
    Write-Host "3. Git is installed on the VM" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================
# Step 3: Check Docker
# ============================================
Write-Host "[Step 3/5] Verifying Docker installation..." -ForegroundColor Cyan

$dockerCheckCmd = @"
# Check Docker
docker --version
docker-compose --version

# Check Docker is running
sudo systemctl status docker | grep 'Active:' || echo 'Docker service status unknown'
"@

try {
    $dockerOutput = gcloud compute ssh $VMName --zone=$Zone --command="$dockerCheckCmd"
    Write-Host $dockerOutput
    Write-Host "[OK] Docker is ready" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Docker check had issues (may be non-critical)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 4: Build Docker Image
# ============================================
Write-Host "[Step 4/5] Building Docker image on VM..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow

$buildCmd = @"
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Build Docker image
echo '[INFO] Building Docker image...'
docker build -t cloud-nlp-classifier:latest .

# Verify image
if docker images | grep -q 'cloud-nlp-classifier'; then
    echo '[OK] Docker image built successfully'
    docker images | grep 'cloud-nlp-classifier'
else
    echo '[ERROR] Failed to build Docker image'
    exit 1
fi
"@

try {
    Write-Host "Building image (this will take a few minutes)..." -ForegroundColor Gray
    $buildOutput = gcloud compute ssh $VMName --zone=$Zone --command="$buildCmd"
    Write-Host $buildOutput
    Write-Host "[OK] Docker image built" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to build Docker image: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "You can SSH into the VM and check logs:" -ForegroundColor Yellow
    Write-Host "gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor Cyan
    Write-Host "cd ~/CLOUD-NLP-CLASSIFIER-GCP" -ForegroundColor Cyan
    Write-Host "docker build -t cloud-nlp-classifier:latest ." -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# ============================================
# Step 5: Run Container
# ============================================
Write-Host "[Step 5/5] Starting Docker container..." -ForegroundColor Cyan

$runCmd = @"
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Stop and remove old container if exists
docker stop nlp-api 2>/dev/null || true
docker rm nlp-api 2>/dev/null || true

# Run new container
docker run -d \
    --name nlp-api \
    -p 8000:8000 \
    --restart unless-stopped \
    cloud-nlp-classifier:latest

# Wait for container to start
sleep 5

# Check container status
if docker ps | grep -q 'nlp-api'; then
    echo '[OK] Container is running'
    docker ps | grep 'nlp-api'
    
    # Test health endpoint
    echo ''
    echo '[INFO] Testing health endpoint...'
    curl -s http://localhost:8000/health || echo '[WARN] Health check failed (may need more time to start)'
else
    echo '[ERROR] Container failed to start'
    echo '[INFO] Container logs:'
    docker logs nlp-api
    exit 1
fi
"@

try {
    $runOutput = gcloud compute ssh $VMName --zone=$Zone --command="$runCmd"
    Write-Host $runOutput
    Write-Host "[OK] Container started" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to start container: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Summary
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

# Get VM external IP
$externalIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4 Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host "VM External IP: $externalIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  Health: http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  Predict: http://${externalIP}:8000/predict" -ForegroundColor White
Write-Host "  Docs: http://${externalIP}:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Test the API:" -ForegroundColor Cyan
Write-Host "  curl http://${externalIP}:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "SSH into VM:" -ForegroundColor Cyan
Write-Host "  gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  docker logs -f nlp-api" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Phase 4 Complete - API is running!" -ForegroundColor Green
Write-Host ""
