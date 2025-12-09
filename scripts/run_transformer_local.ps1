# PowerShell script to run transformer training locally

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Transformer Training Pipeline" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Run transformer training
python -m src.models.transformer_training

if ($LASTEXITCODE -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Transformer Training Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Transformer Training Failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
