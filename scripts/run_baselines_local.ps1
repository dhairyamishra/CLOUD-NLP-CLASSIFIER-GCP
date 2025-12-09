# PowerShell script to run baseline model training locally

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Training Baseline Models" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Run baseline training
python -m src.models.train_baselines

if ($LASTEXITCODE -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Baseline Training Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Baseline Training Failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
