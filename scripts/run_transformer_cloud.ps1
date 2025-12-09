# PowerShell script to run transformer training with cloud configuration
# This can be used for local testing of cloud configs or on Windows-based cloud VMs

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Transformer Training - Cloud Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Parse arguments
param(
    [string]$Config = "config/config_transformer_cloud.yaml",
    [string]$Mode = "cloud",
    [string]$OutputDir = "models/transformer/distilbert_cloud",
    [switch]$Fp16 = $false,
    [int]$Epochs = $null,
    [int]$BatchSize = $null
)

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "Continuing without virtual environment..." -ForegroundColor Yellow
}

# Check GPU availability
Write-Host ""
Write-Host "Checking GPU availability..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $gpuInfo -ForegroundColor Green
    }
} catch {
    Write-Host "No NVIDIA GPU detected. Training will use CPU." -ForegroundColor Yellow
}
Write-Host ""

# Build command
$cmd = "python -m src.models.transformer_training"
$cmd += " --config `"$Config`""
$cmd += " --mode $Mode"
$cmd += " --output-dir `"$OutputDir`""

if ($Fp16) {
    $cmd += " --fp16"
}

if ($null -ne $Epochs) {
    $cmd += " --epochs $Epochs"
}

if ($null -ne $BatchSize) {
    $cmd += " --batch-size $BatchSize"
}

# Display configuration
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Config file: $Config" -ForegroundColor White
Write-Host "  Training mode: $Mode" -ForegroundColor White
Write-Host "  Output directory: $OutputDir" -ForegroundColor White
Write-Host "  FP16: $Fp16" -ForegroundColor White
if ($null -ne $Epochs) {
    Write-Host "  Epochs: $Epochs" -ForegroundColor White
}
if ($null -ne $BatchSize) {
    Write-Host "  Batch size: $BatchSize" -ForegroundColor White
}
Write-Host ""

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Start training
Write-Host "Starting training..." -ForegroundColor Green
Write-Host "Command: $cmd" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Execute training
Invoke-Expression $cmd

# Check result
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Training completed successfully!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Model saved to: $OutputDir" -ForegroundColor Cyan
    
    # Display training info if available
    $infoPath = Join-Path $OutputDir "training_info.json"
    if (Test-Path $infoPath) {
        Write-Host ""
        Write-Host "Training Summary:" -ForegroundColor Cyan
        Get-Content $infoPath | ConvertFrom-Json | ConvertTo-Json -Depth 10
    }
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Training failed! Check logs for details." -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit 1
}
