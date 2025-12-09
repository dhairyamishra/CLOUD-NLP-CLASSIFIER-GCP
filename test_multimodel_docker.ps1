# Phase 8: Multi-Model Docker Testing Script
# Tests all 3 models in Docker containers with different configurations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 8: Multi-Model Docker Testing  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8000"
$TEST_RESULTS = @()
$START_TIME = Get-Date

# Test data
$TEST_TEXTS = @{
    "hate" = "I hate you and everyone like you"
    "normal" = "The weather is nice today"
    "offensive" = "You are so stupid and worthless"
    "neutral" = "I went to the store yesterday"
}

# Function to wait for container to be healthy
function Wait-ContainerHealthy {
    param(
        [string]$ContainerName,
        [int]$MaxWaitSeconds = 60
    )
    
    Write-Host "Waiting for container '$ContainerName' to be healthy..." -ForegroundColor Yellow
    $elapsed = 0
    $interval = 5
    
    while ($elapsed -lt $MaxWaitSeconds) {
        $health = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>$null
        if ($health -eq "healthy") {
            Write-Host "[OK] Container is healthy!" -ForegroundColor Green
            return $true
        }
        
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        Write-Host "   Still waiting... ($elapsed/$MaxWaitSeconds seconds)" -ForegroundColor Gray
    }
    
    Write-Host "[ERROR] Container did not become healthy within $MaxWaitSeconds seconds" -ForegroundColor Red
    return $false
}

# Function to test API endpoint
function Test-APIEndpoint {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    try {
        $url = "$API_URL$Endpoint"
        
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
        } else {
            $jsonBody = $Body | ConvertTo-Json
            $response = Invoke-RestMethod -Uri $url -Method Post -Body $jsonBody -ContentType "application/json" -TimeoutSec 10
        }
        
        return @{
            Success = $true
            Data = $response
        }
    } catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# Function to test prediction
function Test-Prediction {
    param(
        [string]$Text,
        [string]$ExpectedLabel = $null
    )
    
    $startTime = Get-Date
    $result = Test-APIEndpoint -Endpoint "/predict" -Method "POST" -Body @{ text = $Text }
    $duration = (Get-Date) - $startTime
    
    if ($result.Success) {
        $prediction = $result.Data
        return @{
            Success = $true
            Label = $prediction.predicted_label
            Confidence = $prediction.confidence
            InferenceTime = $prediction.inference_time_ms
            ResponseTime = $duration.TotalMilliseconds
            Model = $prediction.model_name
        }
    } else {
        return @{
            Success = $false
            Error = $result.Error
        }
    }
}

# Function to stop and remove container
function Remove-TestContainer {
    param([string]$ContainerName)
    
    Write-Host "Cleaning up container '$ContainerName'..." -ForegroundColor Yellow
    docker stop $ContainerName 2>$null | Out-Null
    docker rm $ContainerName 2>$null | Out-Null
    Write-Host "[OK] Container removed" -ForegroundColor Green
}

# ============================================
# Test 1: Default Model (DistilBERT)
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Test 1: Container with Default Model (DistilBERT)" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$containerName = "nlp-api-test-default"
Remove-TestContainer -ContainerName $containerName

Write-Host "Starting container with default model..." -ForegroundColor Yellow
docker run -d -p 8000:8000 --name $containerName cloud-nlp-classifier:latest | Out-Null

if (Wait-ContainerHealthy -ContainerName $containerName) {
    # Test health endpoint
    Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
    $health = Test-APIEndpoint -Endpoint "/health"
    
    if ($health.Success) {
        Write-Host "[OK] Health check passed" -ForegroundColor Green
        Write-Host "   Current Model: $($health.Data.current_model)" -ForegroundColor Gray
        Write-Host "   Available Models: $($health.Data.available_models -join ', ')" -ForegroundColor Gray
        
        $TEST_RESULTS += @{
            Test = "Default Model - Health Check"
            Status = "PASSED"
            Model = $health.Data.current_model
        }
    } else {
        Write-Host "[ERROR] Health check failed: $($health.Error)" -ForegroundColor Red
        $TEST_RESULTS += @{
            Test = "Default Model - Health Check"
            Status = "FAILED"
            Error = $health.Error
        }
    }
    
    # Test predictions
    Write-Host "`nTesting predictions with DistilBERT..." -ForegroundColor Yellow
    foreach ($key in $TEST_TEXTS.Keys) {
        $text = $TEST_TEXTS[$key]
        Write-Host "   Testing: '$text'" -ForegroundColor Gray
        
        $pred = Test-Prediction -Text $text
        if ($pred.Success) {
            Write-Host "   [OK] Label: $($pred.Label) | Confidence: $([math]::Round($pred.Confidence * 100, 2))% | Inference: $($pred.InferenceTime)ms" -ForegroundColor Green
            
            $TEST_RESULTS += @{
                Test = "Default Model - Prediction ($key)"
                Status = "PASSED"
                Model = $pred.Model
                InferenceTime = $pred.InferenceTime
            }
        } else {
            Write-Host "   [ERROR] Prediction failed: $($pred.Error)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Default Model - Prediction ($key)"
                Status = "FAILED"
                Error = $pred.Error
            }
        }
    }
} else {
    Write-Host "[ERROR] Container failed to start" -ForegroundColor Red
    $TEST_RESULTS += @{
        Test = "Default Model - Container Start"
        Status = "FAILED"
        Error = "Container did not become healthy"
    }
}

Remove-TestContainer -ContainerName $containerName
Start-Sleep -Seconds 3

# ============================================
# Test 2: Logistic Regression Model
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Test 2: Container with Logistic Regression" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$containerName = "nlp-api-test-logreg"
Remove-TestContainer -ContainerName $containerName

Write-Host "Starting container with Logistic Regression..." -ForegroundColor Yellow
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression --name $containerName cloud-nlp-classifier:latest | Out-Null

if (Wait-ContainerHealthy -ContainerName $containerName) {
    # Test health endpoint
    Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
    $health = Test-APIEndpoint -Endpoint "/health"
    
    if ($health.Success) {
        Write-Host "[OK] Health check passed" -ForegroundColor Green
        Write-Host "   Current Model: $($health.Data.current_model)" -ForegroundColor Gray
        
        if ($health.Data.current_model -eq "logistic_regression") {
            Write-Host "   [OK] Correct model loaded!" -ForegroundColor Green
            $TEST_RESULTS += @{
                Test = "Logistic Regression - Model Loading"
                Status = "PASSED"
                Model = $health.Data.current_model
            }
        } else {
            Write-Host "   [ERROR] Wrong model loaded: $($health.Data.current_model)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Logistic Regression - Model Loading"
                Status = "FAILED"
                Error = "Expected logistic_regression, got $($health.Data.current_model)"
            }
        }
    }
    
    # Test predictions
    Write-Host "`nTesting predictions with Logistic Regression..." -ForegroundColor Yellow
    foreach ($key in $TEST_TEXTS.Keys) {
        $text = $TEST_TEXTS[$key]
        Write-Host "   Testing: '$text'" -ForegroundColor Gray
        
        $pred = Test-Prediction -Text $text
        if ($pred.Success) {
            Write-Host "   [OK] Label: $($pred.Label) | Confidence: $([math]::Round($pred.Confidence * 100, 2))% | Inference: $($pred.InferenceTime)ms" -ForegroundColor Green
            
            $TEST_RESULTS += @{
                Test = "Logistic Regression - Prediction ($key)"
                Status = "PASSED"
                Model = $pred.Model
                InferenceTime = $pred.InferenceTime
            }
        } else {
            Write-Host "   [ERROR] Prediction failed: $($pred.Error)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Logistic Regression - Prediction ($key)"
                Status = "FAILED"
                Error = $pred.Error
            }
        }
    }
} else {
    Write-Host "[ERROR] Container failed to start" -ForegroundColor Red
    $TEST_RESULTS += @{
        Test = "Logistic Regression - Container Start"
        Status = "FAILED"
        Error = "Container did not become healthy"
    }
}

Remove-TestContainer -ContainerName $containerName
Start-Sleep -Seconds 3

# ============================================
# Test 3: Linear SVM Model
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Test 3: Container with Linear SVM" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$containerName = "nlp-api-test-svm"
Remove-TestContainer -ContainerName $containerName

Write-Host "Starting container with Linear SVM..." -ForegroundColor Yellow
docker run -d -p 8000:8000 -e DEFAULT_MODEL=linear_svm --name $containerName cloud-nlp-classifier:latest | Out-Null

if (Wait-ContainerHealthy -ContainerName $containerName) {
    # Test health endpoint
    Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
    $health = Test-APIEndpoint -Endpoint "/health"
    
    if ($health.Success) {
        Write-Host "[OK] Health check passed" -ForegroundColor Green
        Write-Host "   Current Model: $($health.Data.current_model)" -ForegroundColor Gray
        
        if ($health.Data.current_model -eq "linear_svm") {
            Write-Host "   [OK] Correct model loaded!" -ForegroundColor Green
            $TEST_RESULTS += @{
                Test = "Linear SVM - Model Loading"
                Status = "PASSED"
                Model = $health.Data.current_model
            }
        } else {
            Write-Host "   [ERROR] Wrong model loaded: $($health.Data.current_model)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Linear SVM - Model Loading"
                Status = "FAILED"
                Error = "Expected linear_svm, got $($health.Data.current_model)"
            }
        }
    }
    
    # Test predictions
    Write-Host "`nTesting predictions with Linear SVM..." -ForegroundColor Yellow
    foreach ($key in $TEST_TEXTS.Keys) {
        $text = $TEST_TEXTS[$key]
        Write-Host "   Testing: '$text'" -ForegroundColor Gray
        
        $pred = Test-Prediction -Text $text
        if ($pred.Success) {
            Write-Host "   [OK] Label: $($pred.Label) | Confidence: $([math]::Round($pred.Confidence * 100, 2))% | Inference: $($pred.InferenceTime)ms" -ForegroundColor Green
            
            $TEST_RESULTS += @{
                Test = "Linear SVM - Prediction ($key)"
                Status = "PASSED"
                Model = $pred.Model
                InferenceTime = $pred.InferenceTime
            }
        } else {
            Write-Host "   [ERROR] Prediction failed: $($pred.Error)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Linear SVM - Prediction ($key)"
                Status = "FAILED"
                Error = $pred.Error
            }
        }
    }
} else {
    Write-Host "[ERROR] Container failed to start" -ForegroundColor Red
    $TEST_RESULTS += @{
        Test = "Linear SVM - Container Start"
        Status = "FAILED"
        Error = "Container did not become healthy"
    }
}

Remove-TestContainer -ContainerName $containerName
Start-Sleep -Seconds 3

# ============================================
# Test 4: Dynamic Model Switching
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Test 4: Dynamic Model Switching" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$containerName = "nlp-api-test-switching"
Remove-TestContainer -ContainerName $containerName

Write-Host "Starting container with default model..." -ForegroundColor Yellow
docker run -d -p 8000:8000 --name $containerName cloud-nlp-classifier:latest | Out-Null

if (Wait-ContainerHealthy -ContainerName $containerName) {
    # Test switching to each model
    $models = @("logistic_regression", "linear_svm", "distilbert")
    
    foreach ($model in $models) {
        Write-Host "`nSwitching to $model..." -ForegroundColor Yellow
        
        $switch = Test-APIEndpoint -Endpoint "/models/switch" -Method "POST" -Body @{ model_name = $model }
        
        if ($switch.Success) {
            Write-Host "[OK] Successfully switched to $model" -ForegroundColor Green
            Write-Host "   Message: $($switch.Data.message)" -ForegroundColor Gray
            
            # Verify the switch
            Start-Sleep -Seconds 2
            $health = Test-APIEndpoint -Endpoint "/health"
            
            if ($health.Success -and $health.Data.current_model -eq $model) {
                Write-Host "   [OK] Model switch verified!" -ForegroundColor Green
                
                # Test a prediction with the new model
                $pred = Test-Prediction -Text $TEST_TEXTS['hate']
                if ($pred.Success) {
                    Write-Host "   [OK] Prediction works: $($pred.Label) | Inference: $($pred.InferenceTime)ms" -ForegroundColor Green
                    
                    $TEST_RESULTS += @{
                        Test = "Dynamic Switching - $model"
                        Status = "PASSED"
                        Model = $model
                        InferenceTime = $pred.InferenceTime
                    }
                } else {
                    Write-Host "   [ERROR] Prediction failed after switch" -ForegroundColor Red
                    $TEST_RESULTS += @{
                        Test = "Dynamic Switching - $model"
                        Status = "FAILED"
                        Error = "Prediction failed after switch"
                    }
                }
            } else {
                Write-Host "   [ERROR] Model switch verification failed" -ForegroundColor Red
                $TEST_RESULTS += @{
                    Test = "Dynamic Switching - $model"
                    Status = "FAILED"
                    Error = "Model not switched correctly"
                }
            }
        } else {
            Write-Host "[ERROR] Failed to switch to $model : $($switch.Error)" -ForegroundColor Red
            $TEST_RESULTS += @{
                Test = "Dynamic Switching - $model"
                Status = "FAILED"
                Error = $switch.Error
            }
        }
    }
} else {
    Write-Host "[ERROR] Container failed to start" -ForegroundColor Red
    $TEST_RESULTS += @{
        Test = "Dynamic Switching - Container Start"
        Status = "FAILED"
        Error = "Container did not become healthy"
    }
}

Remove-TestContainer -ContainerName $containerName

# ============================================
# Test Summary
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Phase 8 Test Summary" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$totalTests = $TEST_RESULTS.Count
$passedTests = ($TEST_RESULTS | Where-Object { $_.Status -eq "PASSED" }).Count
$failedTests = ($TEST_RESULTS | Where-Object { $_.Status -eq "FAILED" }).Count
$successRate = [math]::Round(($passedTests / $totalTests) * 100, 2)

Write-Host "`nTotal Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests [OK]" -ForegroundColor Green
Write-Host "Failed: $failedTests [X]" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -eq 100) { "Green" } else { "Yellow" })

# Calculate average inference times by model
Write-Host "`nAverage Inference Times:" -ForegroundColor Cyan
$modelGroups = $TEST_RESULTS | Where-Object { $_.InferenceTime } | Group-Object -Property Model
foreach ($group in $modelGroups) {
    $avgTime = ($group.Group | Measure-Object -Property InferenceTime -Average).Average
    Write-Host "   $($group.Name): $([math]::Round($avgTime, 2))ms" -ForegroundColor Gray
}

# Show failed tests
if ($failedTests -gt 0) {
    Write-Host "`n[ERROR] Failed Tests:" -ForegroundColor Red
    $TEST_RESULTS | Where-Object { $_.Status -eq "FAILED" } | ForEach-Object {
        Write-Host "   - $($_.Test)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "     Error: $($_.Error)" -ForegroundColor Gray
        }
    }
}

$DURATION = (Get-Date) - $START_TIME
Write-Host "`nTotal Duration: $([math]::Round($DURATION.TotalMinutes, 2)) minutes" -ForegroundColor Cyan

# Final status
Write-Host "`n" + "="*60 -ForegroundColor Cyan
if ($successRate -eq 100) {
    Write-Host "[SUCCESS] Phase 8: PASSED - All multi-model tests successful!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "[WARNING] Phase 8: PARTIAL - Most tests passed but some issues found" -ForegroundColor Yellow
} else {
    Write-Host "[FAILED] Phase 8: FAILED - Significant issues detected" -ForegroundColor Red
}
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[OK] Phase 8 testing complete!" -ForegroundColor Green
Write-Host 'Review the results above and update END_TO_END_TEST_PROGRESS.md' -ForegroundColor Yellow
