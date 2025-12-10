#!/usr/bin/env pwsh
# PowerShell script to train toxicity classification model

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Toxicity Model Training Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if data exists
if (-not (Test-Path "data\toxicity\train.csv")) {
    Write-Host "❌ Training data not found at data\toxicity\train.csv" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download the dataset first:" -ForegroundColor Yellow
    Write-Host "  python scripts\download_dataset.py --dataset toxicity" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Training data found" -ForegroundColor Green
Write-Host ""

# Check if config exists
if (-not (Test-Path "config\config_toxicity.yaml")) {
    Write-Host "❌ Config file not found at config\config_toxicity.yaml" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Config file found" -ForegroundColor Green
Write-Host ""

# Parse command line arguments
$epochs = $null
$mode = "local"

for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--epochs") {
        $epochs = $args[$i + 1]
        $i++
    }
    elseif ($args[$i] -eq "--mode") {
        $mode = $args[$i + 1]
        $i++
    }
}

# Build command
$cmd = "python -m src.models.train_toxicity"

if ($epochs) {
    $cmd += " --epochs $epochs"
    Write-Host "🔧 Training for $epochs epochs" -ForegroundColor Yellow
}
else {
    Write-Host "🔧 Training with default epochs (3)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting training..." -ForegroundColor Cyan
Write-Host "Command: $cmd" -ForegroundColor Gray
Write-Host ""

# Run training
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "✅ Training completed successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Model saved to: models\toxicity_multi_head" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test the model: python scripts\test_toxicity_model.py" -ForegroundColor White
    Write-Host "  2. Integrate with API: Update src\api\server.py" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "❌ Training failed!" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    exit 1
}
