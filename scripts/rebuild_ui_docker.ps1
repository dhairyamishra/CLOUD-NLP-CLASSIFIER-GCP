# PowerShell script to rebuild and restart Streamlit UI Docker container
# This script ensures all models are included and properly loaded

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Rebuild Streamlit UI Docker Container" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if models exist locally
Write-Host "Step 1: Checking for trained models..." -ForegroundColor Yellow
python scripts\check_models.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "WARNING: Some models are missing!" -ForegroundColor Red
    Write-Host "It's recommended to train all models before building Docker image." -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Stopping existing container..." -ForegroundColor Yellow
docker-compose -f docker-compose.ui.yml down

Write-Host ""
Write-Host "Step 3: Rebuilding Docker image (no cache)..." -ForegroundColor Yellow
docker-compose -f docker-compose.ui.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Starting container..." -ForegroundColor Yellow
docker-compose -f docker-compose.ui.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 5: Waiting for container to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Step 6: Checking container logs..." -ForegroundColor Yellow
docker logs nlp-ui-dev

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the Streamlit UI at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
Write-Host "  docker logs -f nlp-ui-dev" -ForegroundColor White
Write-Host ""
Write-Host "To stop the container:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.ui.yml down" -ForegroundColor White
Write-Host ""
