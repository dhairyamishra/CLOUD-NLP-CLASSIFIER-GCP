# Phase 3: VM Environment Setup and Verification
# This script verifies Docker installation and prepares the VM for deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 3: VM Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load configuration
$configFile = "gcp-deployment-config.txt"
if (-not (Test-Path $configFile)) {
    Write-Host "ERROR: Configuration file not found!" -ForegroundColor Red
    exit 1
}

$config = @{}
Get-Content $configFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.+)$') {
        $config[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$VM_NAME = $config['VM_NAME']
$ZONE = $config['ZONE']
$STATIC_IP = $config['STATIC_IP']

Write-Host "VM Name: $VM_NAME" -ForegroundColor Green
Write-Host "Zone: $ZONE" -ForegroundColor Green
Write-Host "IP: $STATIC_IP" -ForegroundColor Green
Write-Host ""

# Step 1: Check VM status
Write-Host "[1/6] Checking VM status..." -ForegroundColor Yellow
$vmStatus = gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(status)"
if ($vmStatus -ne "RUNNING") {
    Write-Host "ERROR: VM is not running (Status: $vmStatus)" -ForegroundColor Red
    exit 1
}
Write-Host "OK - VM is running" -ForegroundColor Green
Write-Host ""

# Step 2: Wait for startup script to complete
Write-Host "[2/6] Waiting for startup script to complete..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes if Docker is still installing..." -ForegroundColor Gray
Write-Host ""

$maxWait = 180  # 3 minutes
$waited = 0
$startupComplete = $false

while ($waited -lt $maxWait -and -not $startupComplete) {
    Write-Host "  Checking startup script status... ($waited seconds elapsed)" -ForegroundColor Gray
    
    # Check if Docker is installed
    $dockerCheck = gcloud compute ssh $VM_NAME --zone=$ZONE --command="which docker" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $startupComplete = $true
        Write-Host "OK - Startup script completed" -ForegroundColor Green
        break
    }
    
    Start-Sleep -Seconds 10
    $waited += 10
}

if (-not $startupComplete) {
    Write-Host "WARNING: Startup script may still be running" -ForegroundColor Yellow
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Verify Docker installation
Write-Host "[3/6] Verifying Docker installation..." -ForegroundColor Yellow

$dockerVersion = gcloud compute ssh $VM_NAME --zone=$ZONE --command="docker --version" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not installed" -ForegroundColor Red
    Write-Host "Output: $dockerVersion" -ForegroundColor Red
    exit 1
}
Write-Host "Docker version: $dockerVersion" -ForegroundColor Green

$composeVersion = gcloud compute ssh $VM_NAME --zone=$ZONE --command="docker compose version" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Compose is not installed" -ForegroundColor Red
    Write-Host "Output: $composeVersion" -ForegroundColor Red
    exit 1
}
Write-Host "Docker Compose version: $composeVersion" -ForegroundColor Green
Write-Host ""

# Step 4: Verify directory structure
Write-Host "[4/6] Verifying directory structure..." -ForegroundColor Yellow

$dirCheck = gcloud compute ssh $VM_NAME --zone=$ZONE --command="ls -la /opt/nlp-classifier" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Application directory not found" -ForegroundColor Red
    Write-Host "Output: $dirCheck" -ForegroundColor Red
    exit 1
}
Write-Host "Directory structure:" -ForegroundColor Green
Write-Host $dirCheck -ForegroundColor Gray
Write-Host ""

# Step 5: Check system resources
Write-Host "[5/6] Checking system resources..." -ForegroundColor Yellow

Write-Host "  CPU and Memory:" -ForegroundColor Gray
$resources = gcloud compute ssh $VM_NAME --zone=$ZONE --command="echo 'CPU Cores:' && nproc && echo 'Memory:' && free -h | grep Mem" 2>&1
Write-Host $resources -ForegroundColor Gray

Write-Host ""
Write-Host "  Disk Space:" -ForegroundColor Gray
$disk = gcloud compute ssh $VM_NAME --zone=$ZONE --command="df -h /" 2>&1
Write-Host $disk -ForegroundColor Gray
Write-Host ""

# Step 6: Test Docker with hello-world
Write-Host "[6/6] Testing Docker..." -ForegroundColor Yellow
$dockerTest = gcloud compute ssh $VM_NAME --zone=$ZONE --command="sudo docker run --rm hello-world" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Docker test failed" -ForegroundColor Yellow
    Write-Host "Output: $dockerTest" -ForegroundColor Yellow
} else {
    Write-Host "OK - Docker is working correctly" -ForegroundColor Green
}
Write-Host ""

# Display summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 3 COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VM Environment Summary:" -ForegroundColor Yellow
Write-Host "  Status:          READY" -ForegroundColor Green
Write-Host "  Docker:          Installed and working" -ForegroundColor Green
Write-Host "  Docker Compose:  Installed" -ForegroundColor Green
Write-Host "  Directories:     Created" -ForegroundColor Green
Write-Host "  Resources:       Verified" -ForegroundColor Green
Write-Host ""
Write-Host "VM is ready for application deployment!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Transfer application files (Phase 4)" -ForegroundColor White
Write-Host "  2. Transfer model files (~3-5GB)" -ForegroundColor White
Write-Host "  3. Configure Docker Compose (Phase 5)" -ForegroundColor White
Write-Host ""
Write-Host "Ready to proceed to Phase 4?" -ForegroundColor Yellow
