# PowerShell script to run Streamlit UI locally (Windows)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cloud NLP Classifier - Streamlit UI  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if streamlit is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    $streamlitVersion = python -m streamlit --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Streamlit not found"
    }
    Write-Host "✓ Streamlit is installed: $streamlitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Streamlit is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing Streamlit..." -ForegroundColor Yellow
    pip install streamlit>=1.28.0 plotly>=5.17.0
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install Streamlit" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Streamlit installed successfully" -ForegroundColor Green
}

Write-Host ""

# Check if models exist
Write-Host "Checking for trained models..." -ForegroundColor Yellow

$modelsExist = $false

if (Test-Path "models\baselines\logistic_regression_tfidf.joblib") {
    Write-Host "✓ Logistic Regression model found" -ForegroundColor Green
    $modelsExist = $true
}

if (Test-Path "models\baselines\linear_svm_tfidf.joblib") {
    Write-Host "✓ Linear SVM model found" -ForegroundColor Green
    $modelsExist = $true
}

if (Test-Path "models\transformer\distilbert\pytorch_model.bin") {
    Write-Host "✓ DistilBERT transformer model found" -ForegroundColor Green
    $modelsExist = $true
}

if (-not $modelsExist) {
    Write-Host ""
    Write-Host "⚠ WARNING: No trained models found!" -ForegroundColor Yellow
    Write-Host "Please train models first:" -ForegroundColor Yellow
    Write-Host "  python run_baselines.py" -ForegroundColor Cyan
    Write-Host "  python run_transformer.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The UI will start but may not work without models." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit UI..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The UI will open in your browser at:" -ForegroundColor Yellow
Write-Host "  http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
streamlit run src\ui\streamlit_app.py --server.port 8501

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Streamlit failed to start" -ForegroundColor Red
    exit 1
}
