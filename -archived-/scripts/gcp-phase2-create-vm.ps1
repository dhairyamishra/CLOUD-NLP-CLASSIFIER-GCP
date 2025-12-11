# Phase 2: Create and Configure VM
# This script creates a GCP Compute Engine VM with Docker pre-installed

# Enable verbose logging
$VerbosePreference = "Continue"
$DebugPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Create and Configure VM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verbose logging enabled" -ForegroundColor Gray
Write-Host ""

# Load configuration from Phase 1
$configFile = "gcp-deployment-config.txt"
if (-not (Test-Path $configFile)) {
    Write-Host "ERROR: Configuration file not found!" -ForegroundColor Red
    Write-Host "Please run Phase 1 first: .\scripts\gcp-phase1-setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Parse configuration
Write-Host "Reading configuration from $configFile..." -ForegroundColor Gray
$config = @{}
Get-Content $configFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.+)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $config[$key] = $value
        Write-Host "  Loaded: $key = $value" -ForegroundColor DarkGray
    }
}

$PROJECT_ID = $config['PROJECT_ID']
$REGION = $config['REGION']
$ZONE = $config['ZONE']
$STATIC_IP = $config['STATIC_IP']
$VM_NAME = $config['VM_NAME']
$MACHINE_TYPE = $config['MACHINE_TYPE']
$BOOT_DISK_SIZE = $config['BOOT_DISK_SIZE']

Write-Host ""
Write-Host "Configuration loaded:" -ForegroundColor Green
Write-Host "  Project:      $PROJECT_ID" -ForegroundColor Gray
Write-Host "  VM Name:      $VM_NAME" -ForegroundColor Gray
Write-Host "  Machine Type: $MACHINE_TYPE" -ForegroundColor Gray
Write-Host "  Disk Size:    $BOOT_DISK_SIZE" -ForegroundColor Gray
Write-Host "  Static IP:    $STATIC_IP" -ForegroundColor Gray
Write-Host ""

# Step 1: Check if VM already exists
Write-Host "[1/4] Checking if VM already exists..." -ForegroundColor Yellow
Write-Host "  Running: gcloud compute instances describe $VM_NAME --zone=$ZONE" -ForegroundColor DarkGray
$existingVM = gcloud compute instances describe $VM_NAME --zone=$ZONE 2>&1
Write-Host "  Exit code: $LASTEXITCODE" -ForegroundColor DarkGray
if ($LASTEXITCODE -eq 0) {
    Write-Host "WARNING: VM '$VM_NAME' already exists!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Delete existing VM and create new one" -ForegroundColor White
    Write-Host "  2. Skip VM creation and use existing VM" -ForegroundColor White
    Write-Host "  3. Cancel" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Enter choice (1/2/3)"
    
    if ($choice -eq "1") {
        Write-Host "Deleting existing VM..." -ForegroundColor Yellow
        gcloud compute instances delete $VM_NAME --zone=$ZONE --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to delete VM" -ForegroundColor Red
            exit 1
        }
        Write-Host "OK - VM deleted" -ForegroundColor Green
    }
    elseif ($choice -eq "2") {
        Write-Host "OK - Using existing VM" -ForegroundColor Green
        Write-Host ""
        Write-Host "VM External IP: $STATIC_IP" -ForegroundColor Cyan
        Write-Host "SSH Command: gcloud compute ssh $VM_NAME --zone=$ZONE" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Phase 2 skipped - proceed to Phase 3" -ForegroundColor Yellow
        exit 0
    }
    else {
        Write-Host "Cancelled by user" -ForegroundColor Yellow
        exit 0
    }
}
else {
    Write-Host "OK - No existing VM found" -ForegroundColor Green
}
Write-Host ""

# Step 2: Create firewall rules
Write-Host "[2/4] Creating firewall rules..." -ForegroundColor Yellow

# Check and create firewall rules
$firewallRules = @(
    @{Name="allow-nlp-api"; Port="8000"; Description="Allow NLP API traffic"},
    @{Name="allow-nlp-ui"; Port="8501"; Description="Allow NLP UI traffic"},
    @{Name="allow-http"; Port="80"; Description="Allow HTTP traffic"},
    @{Name="allow-https"; Port="443"; Description="Allow HTTPS traffic"}
)

foreach ($rule in $firewallRules) {
    $ruleName = $rule.Name
    $rulePort = $rule.Port
    $ruleDesc = $rule.Description
    
    Write-Host "  Checking firewall rule: $ruleName" -ForegroundColor DarkGray
    $existing = gcloud compute firewall-rules describe $ruleName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - $ruleName already exists (port $rulePort)" -ForegroundColor Gray
    }
    else {
        Write-Host "  - Creating $ruleName for port $rulePort..." -ForegroundColor Gray
        Write-Host "    Command: gcloud compute firewall-rules create $ruleName --allow=tcp:$rulePort --target-tags=$ruleName" -ForegroundColor DarkGray
        gcloud compute firewall-rules create $ruleName `
            --allow="tcp:$rulePort" `
            --source-ranges="0.0.0.0/0" `
            --target-tags="$ruleName" `
            --description="$ruleDesc" `
            --quiet
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    WARNING: Failed to create firewall rule $ruleName" -ForegroundColor Yellow
        }
        else {
            Write-Host "    SUCCESS: Firewall rule created" -ForegroundColor DarkGreen
        }
    }
}
Write-Host "OK - Firewall rules configured" -ForegroundColor Green
Write-Host ""

# Step 3: Create VM with startup script
Write-Host "[3/4] Creating VM instance..." -ForegroundColor Yellow
Write-Host "This will take 2-3 minutes..." -ForegroundColor Gray
Write-Host ""

# Create startup script
$startupScript = @'
#!/bin/bash
set -e

echo "=== VM Startup Script ==="
echo "Installing Docker and dependencies..."

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin

# Create app user
useradd -m -s /bin/bash appuser || true
usermod -aG docker appuser

# Create application directory
mkdir -p /opt/nlp-classifier/{models,logs,data}
chown -R appuser:appuser /opt/nlp-classifier

# Install useful tools
apt-get install -y git curl wget vim htop

echo "=== Startup script completed ==="
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker compose version)"
'@

# Save startup script to temp file
$tempStartupScript = [System.IO.Path]::GetTempFileName()
Write-Host "Saving startup script to: $tempStartupScript" -ForegroundColor DarkGray
$startupScript | Out-File -FilePath $tempStartupScript -Encoding UTF8
Write-Host "Startup script saved ($((Get-Item $tempStartupScript).Length) bytes)" -ForegroundColor DarkGray
Write-Host ""

# Create VM
Write-Host "Creating VM with command:" -ForegroundColor DarkGray
Write-Host "  gcloud compute instances create $VM_NAME" -ForegroundColor DarkGray
Write-Host "    --zone=$ZONE" -ForegroundColor DarkGray
Write-Host "    --machine-type=$MACHINE_TYPE" -ForegroundColor DarkGray
Write-Host "    --image-family=ubuntu-2204-lts" -ForegroundColor DarkGray
Write-Host "    --boot-disk-size=$BOOT_DISK_SIZE" -ForegroundColor DarkGray
Write-Host "    --boot-disk-type=pd-ssd" -ForegroundColor DarkGray
Write-Host "    --address=$STATIC_IP" -ForegroundColor DarkGray
Write-Host "    --tags=http-server,https-server,allow-nlp-api,allow-nlp-ui" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Executing VM creation..." -ForegroundColor Yellow

$vmTags = "http-server,https-server,allow-nlp-api,allow-nlp-ui"
gcloud compute instances create $VM_NAME `
    --zone="$ZONE" `
    --machine-type="$MACHINE_TYPE" `
    --image-family="ubuntu-2204-lts" `
    --image-project="ubuntu-os-cloud" `
    --boot-disk-size="$BOOT_DISK_SIZE" `
    --boot-disk-type="pd-ssd" `
    --address="$STATIC_IP" `
    --tags=$vmTags `
    --metadata-from-file="startup-script=$tempStartupScript"

Write-Host "VM creation command completed with exit code: $LASTEXITCODE" -ForegroundColor DarkGray

# Clean up temp file
Write-Host "Cleaning up temporary startup script..." -ForegroundColor DarkGray
Remove-Item $tempStartupScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create VM" -ForegroundColor Red
    exit 1
}

Write-Host "OK - VM created successfully!" -ForegroundColor Green
Write-Host ""

# Step 4: Wait for VM to be ready
Write-Host "[4/4] Waiting for VM to be ready..." -ForegroundColor Yellow
Write-Host "Waiting for startup script to complete (2-3 minutes)..." -ForegroundColor Gray

# Wait for SSH to be ready
$maxAttempts = 30
$attempt = 0
$sshReady = $false

while ($attempt -lt $maxAttempts -and -not $sshReady) {
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    $result = gcloud compute ssh $VM_NAME --zone=$ZONE --command="echo 'SSH Ready'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $sshReady = $true
        Write-Host "OK - SSH connection established" -ForegroundColor Green
    }
    else {
        Start-Sleep -Seconds 10
    }
}

if (-not $sshReady) {
    Write-Host "WARNING: SSH connection timeout" -ForegroundColor Yellow
    Write-Host "VM may still be starting up. Try connecting manually in a few minutes." -ForegroundColor Yellow
}

Write-Host ""

# Display summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 2 COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VM Details:" -ForegroundColor Yellow
Write-Host "  Name:        $VM_NAME" -ForegroundColor White
Write-Host "  Zone:        $ZONE" -ForegroundColor White
Write-Host "  External IP: $STATIC_IP" -ForegroundColor Cyan
Write-Host "  Machine:     $MACHINE_TYPE (2 vCPU, 8GB RAM)" -ForegroundColor White
Write-Host "  Disk:        $BOOT_DISK_SIZE SSD" -ForegroundColor White
Write-Host ""
Write-Host "Access URLs (after deployment):" -ForegroundColor Yellow
Write-Host "  API:  http://$STATIC_IP:8000" -ForegroundColor Cyan
Write-Host "  UI:   http://$STATIC_IP:8501" -ForegroundColor Cyan
Write-Host "  Docs: http://$STATIC_IP:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "SSH Command:" -ForegroundColor Yellow
Write-Host "  gcloud compute ssh $VM_NAME --zone=$ZONE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Firewall Rules Created:" -ForegroundColor Yellow
Write-Host "  - Port 22:   SSH (default)" -ForegroundColor White
Write-Host "  - Port 80:   HTTP" -ForegroundColor White
Write-Host "  - Port 443:  HTTPS" -ForegroundColor White
Write-Host "  - Port 8000: API" -ForegroundColor White
Write-Host "  - Port 8501: UI" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Wait 2-3 minutes for startup script to complete" -ForegroundColor White
Write-Host "  2. SSH into VM to verify Docker installation" -ForegroundColor White
Write-Host "  3. Proceed to Phase 3: Setup VM Environment" -ForegroundColor White
Write-Host ""
Write-Host "Ready to proceed to Phase 3?" -ForegroundColor Yellow
