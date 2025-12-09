# PowerShell script to run FastAPI server locally

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Yellow
Write-Host "  - API: http://localhost:8000" -ForegroundColor Green
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Run FastAPI server with uvicorn
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

if ($LASTEXITCODE -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Server stopped successfully" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Server stopped with errors" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
