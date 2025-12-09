# PowerShell script to run data preprocessing locally

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Data Preprocessing" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Run preprocessing
python -m src.data.preprocess

if ($LASTEXITCODE -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Preprocessing Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Preprocessing Failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
