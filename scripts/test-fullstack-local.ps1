# ============================================
# Local Full-Stack Testing Script
# ============================================
# Tests API + UI together using docker-compose
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Full-Stack Local Test" -ForegroundColor Cyan
Write-Host "  API + UI with Docker Compose" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if docker-compose is available
Write-Host "[1/6] Checking Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>&1
    Write-Host "[OK] Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker Compose not found" -ForegroundColor Red
    Write-Host "Please install Docker Desktop or docker-compose" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Stop any existing containers
Write-Host "[2/6] Cleaning up old containers..." -ForegroundColor Cyan
try {
    docker-compose -f docker-compose.fullstack.yml down 2>&1 | Out-Null
    Write-Host "[OK] Cleanup complete" -ForegroundColor Green
} catch {
    Write-Host "[WARN] No containers to clean up" -ForegroundColor Yellow
}

Write-Host ""

# Build and start services
Write-Host "[3/6] Building and starting services..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes for first build..." -ForegroundColor Yellow
Write-Host ""

try {
    docker-compose -f docker-compose.fullstack.yml up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to start services" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Services started" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to start services: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Wait for services to be ready
Write-Host "[4/6] Waiting for services to be ready..." -ForegroundColor Cyan
Write-Host "Waiting 30 seconds for initialization..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host ""

# Test API
Write-Host "[5/6] Testing API..." -ForegroundColor Cyan
$apiHealthy = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        $apiResponse = curl.exe -s http://localhost:8000/health
        if ($apiResponse -match "ok") {
            Write-Host "[OK] API is healthy" -ForegroundColor Green
            $apiHealthy = $true
            break
        }
    } catch {
        Write-Host "[WARN] API not ready yet (attempt $i/3)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

if (-not $apiHealthy) {
    Write-Host "[ERROR] API failed to start" -ForegroundColor Red
    Write-Host ""
    Write-Host "API Logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.fullstack.yml logs api
    exit 1
}

Write-Host ""

# Test UI
Write-Host "[6/6] Testing UI..." -ForegroundColor Cyan
$uiHealthy = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        $uiResponse = curl.exe -s http://localhost:8501/_stcore/health
        if ($uiResponse) {
            Write-Host "[OK] UI is healthy" -ForegroundColor Green
            $uiHealthy = $true
            break
        }
    } catch {
        Write-Host "[WARN] UI not ready yet (attempt $i/3)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

if (-not $uiHealthy) {
    Write-Host "[ERROR] UI failed to start" -ForegroundColor Red
    Write-Host ""
    Write-Host "UI Logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.fullstack.yml logs ui
    exit 1
}

Write-Host ""

# Show container status
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SERVICES READY!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.fullstack.yml ps
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  API:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  UI:   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Quick Tests:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:8000/health" -ForegroundColor White
Write-Host "  curl http://localhost:8501/_stcore/health" -ForegroundColor White
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.fullstack.yml logs -f" -ForegroundColor White
Write-Host "  docker-compose -f docker-compose.fullstack.yml logs -f api" -ForegroundColor White
Write-Host "  docker-compose -f docker-compose.fullstack.yml logs -f ui" -ForegroundColor White
Write-Host ""
Write-Host "Stop Services:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.fullstack.yml down" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Full-stack test complete!" -ForegroundColor Green
Write-Host ""
