# Phase 9: Performance Validation Script
# Comprehensive performance testing for all 3 models

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 9: Performance Validation      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8000"
$CONTAINER_NAME = "nlp-api-perf-test"
$START_TIME = Get-Date

# Test configurations
$MODELS = @("distilbert", "logistic_regression", "linear_svm")
$TEST_TEXTS = @(
    "I hate you and everyone like you",
    "The weather is nice today",
    "You are so stupid and worthless",
    "I went to the store yesterday",
    "This product is amazing and I love it",
    "Terrible service, never coming back",
    "Just a normal day at work",
    "You're the worst person ever"
)

$RESULTS = @{}

# Function to wait for container to be healthy
function Wait-ContainerHealthy {
    param([string]$ContainerName, [int]$MaxWaitSeconds = 60)
    
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
    }
    
    Write-Host "[ERROR] Container did not become healthy" -ForegroundColor Red
    return $false
}

# Function to make prediction
function Invoke-Prediction {
    param([string]$Text)
    
    try {
        $body = @{ text = $Text } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$API_URL/predict" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        return @{
            Success = $true
            InferenceTime = $response.inference_time_ms
            Label = $response.predicted_label
            Confidence = $response.confidence
        }
    } catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# Function to switch model
function Switch-Model {
    param([string]$ModelName)
    
    try {
        $body = @{ model_name = $ModelName } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$API_URL/models/switch" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        Start-Sleep -Seconds 2  # Allow model to fully load
        return $true
    } catch {
        Write-Host "[ERROR] Failed to switch to $ModelName : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to get container stats
function Get-ContainerStats {
    param([string]$ContainerName)
    
    try {
        $stats = docker stats $ContainerName --no-stream --format "{{.MemUsage}},{{.CPUPerc}}" 2>$null
        if ($stats) {
            $parts = $stats -split ","
            return @{
                Memory = $parts[0]
                CPU = $parts[1]
            }
        }
    } catch {
        return $null
    }
    return $null
}

# Function to calculate percentiles
function Get-Percentile {
    param(
        [array]$Values,
        [int]$Percentile
    )
    
    $sorted = $Values | Sort-Object
    $index = [math]::Ceiling(($Percentile / 100.0) * $sorted.Count) - 1
    if ($index -lt 0) { $index = 0 }
    return $sorted[$index]
}

# Function to run latency test
function Test-Latency {
    param(
        [string]$ModelName,
        [int]$Iterations = 100
    )
    
    Write-Host "`n[TEST] Latency Test for $ModelName ($Iterations iterations)" -ForegroundColor Cyan
    
    $latencies = @()
    $successCount = 0
    $failCount = 0
    
    for ($i = 1; $i -le $Iterations; $i++) {
        $text = $TEST_TEXTS[($i - 1) % $TEST_TEXTS.Count]
        $result = Invoke-Prediction -Text $text
        
        if ($result.Success) {
            $latencies += $result.InferenceTime
            $successCount++
        } else {
            $failCount++
        }
        
        if ($i % 20 -eq 0) {
            Write-Host "  Progress: $i/$Iterations requests completed" -ForegroundColor Gray
        }
    }
    
    if ($latencies.Count -gt 0) {
        $p50 = Get-Percentile -Values $latencies -Percentile 50
        $p95 = Get-Percentile -Values $latencies -Percentile 95
        $p99 = Get-Percentile -Values $latencies -Percentile 99
        $avg = ($latencies | Measure-Object -Average).Average
        $min = ($latencies | Measure-Object -Minimum).Minimum
        $max = ($latencies | Measure-Object -Maximum).Maximum
        
        Write-Host "[OK] Latency Test Complete" -ForegroundColor Green
        Write-Host "  Success: $successCount | Failed: $failCount" -ForegroundColor Gray
        Write-Host "  Min: $([math]::Round($min, 2))ms | Max: $([math]::Round($max, 2))ms" -ForegroundColor Gray
        Write-Host "  Avg: $([math]::Round($avg, 2))ms" -ForegroundColor Gray
        Write-Host "  p50: $([math]::Round($p50, 2))ms | p95: $([math]::Round($p95, 2))ms | p99: $([math]::Round($p99, 2))ms" -ForegroundColor Gray
        
        return @{
            Success = $true
            SuccessCount = $successCount
            FailCount = $failCount
            Min = $min
            Max = $max
            Avg = $avg
            P50 = $p50
            P95 = $p95
            P99 = $p99
            Latencies = $latencies
        }
    } else {
        Write-Host "[ERROR] All requests failed" -ForegroundColor Red
        return @{
            Success = $false
            SuccessCount = 0
            FailCount = $failCount
        }
    }
}

# Function to run throughput test
function Test-Throughput {
    param(
        [string]$ModelName,
        [int]$DurationSeconds = 30,
        [int]$ConcurrentRequests = 10
    )
    
    Write-Host "`n[TEST] Throughput Test for $ModelName ($DurationSeconds seconds, $ConcurrentRequests concurrent)" -ForegroundColor Cyan
    
    $jobs = @()
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($DurationSeconds)
    
    # Create concurrent jobs
    for ($i = 1; $i -le $ConcurrentRequests; $i++) {
        $job = Start-Job -ScriptBlock {
            param($ApiUrl, $TestTexts, $EndTime)
            
            $count = 0
            $errors = 0
            
            while ((Get-Date) -lt $EndTime) {
                try {
                    $text = $TestTexts[$count % $TestTexts.Count]
                    $body = @{ text = $text } | ConvertTo-Json
                    $response = Invoke-RestMethod -Uri "$ApiUrl/predict" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
                    $count++
                } catch {
                    $errors++
                }
            }
            
            return @{
                Count = $count
                Errors = $errors
            }
        } -ArgumentList $API_URL, $TEST_TEXTS, $endTime
        
        $jobs += $job
    }
    
    # Wait for all jobs to complete
    Write-Host "  Running throughput test..." -ForegroundColor Gray
    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job
    
    $totalRequests = ($results | Measure-Object -Property Count -Sum).Sum
    $totalErrors = ($results | Measure-Object -Property Errors -Sum).Sum
    $actualDuration = ((Get-Date) - $startTime).TotalSeconds
    $throughput = $totalRequests / $actualDuration
    
    Write-Host "[OK] Throughput Test Complete" -ForegroundColor Green
    Write-Host "  Total Requests: $totalRequests" -ForegroundColor Gray
    Write-Host "  Errors: $totalErrors" -ForegroundColor Gray
    Write-Host "  Duration: $([math]::Round($actualDuration, 2))s" -ForegroundColor Gray
    Write-Host "  Throughput: $([math]::Round($throughput, 2)) req/s" -ForegroundColor Gray
    
    return @{
        Success = $true
        TotalRequests = $totalRequests
        TotalErrors = $totalErrors
        Duration = $actualDuration
        Throughput = $throughput
    }
}

# Function to run memory test
function Test-Memory {
    param([string]$ModelName)
    
    Write-Host "`n[TEST] Memory Test for $ModelName" -ForegroundColor Cyan
    
    $memoryReadings = @()
    
    # Take 5 memory readings over 10 seconds
    for ($i = 1; $i -le 5; $i++) {
        $stats = Get-ContainerStats -ContainerName $CONTAINER_NAME
        if ($stats) {
            $memoryReadings += $stats.Memory
            Write-Host "  Reading $i/5: Memory = $($stats.Memory), CPU = $($stats.CPU)" -ForegroundColor Gray
        }
        if ($i -lt 5) {
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "[OK] Memory Test Complete" -ForegroundColor Green
    
    return @{
        Success = $true
        Readings = $memoryReadings
    }
}

# ============================================
# Main Test Execution
# ============================================

Write-Host "`n[SETUP] Starting Docker container..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null | Out-Null
docker rm $CONTAINER_NAME 2>$null | Out-Null
docker run -d -p 8000:8000 --name $CONTAINER_NAME cloud-nlp-classifier:latest | Out-Null

if (-not (Wait-ContainerHealthy -ContainerName $CONTAINER_NAME)) {
    Write-Host "[ERROR] Container failed to start. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "`n[INFO] Container ready. Starting performance tests..." -ForegroundColor Green

# Test each model
foreach ($model in $MODELS) {
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "Performance Testing: $model" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    
    # Switch to model
    Write-Host "`n[SETUP] Switching to $model..." -ForegroundColor Yellow
    if (-not (Switch-Model -ModelName $model)) {
        Write-Host "[ERROR] Failed to switch to $model. Skipping." -ForegroundColor Red
        continue
    }
    Write-Host "[OK] Switched to $model" -ForegroundColor Green
    
    # Initialize results for this model
    $RESULTS[$model] = @{}
    
    # Test 1: Latency (100 requests)
    $latencyResult = Test-Latency -ModelName $model -Iterations 100
    $RESULTS[$model]["Latency"] = $latencyResult
    
    # Test 2: Throughput (30 seconds, 10 concurrent)
    $throughputResult = Test-Throughput -ModelName $model -DurationSeconds 30 -ConcurrentRequests 10
    $RESULTS[$model]["Throughput"] = $throughputResult
    
    # Test 3: Memory Usage
    $memoryResult = Test-Memory -ModelName $model
    $RESULTS[$model]["Memory"] = $memoryResult
}

# ============================================
# Generate Summary Report
# ============================================

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Phase 9: Performance Summary" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[SUMMARY] Latency Comparison:" -ForegroundColor Cyan
Write-Host ("{0,-20} {1,10} {2,10} {3,10} {4,10}" -f "Model", "Avg (ms)", "p50 (ms)", "p95 (ms)", "p99 (ms)") -ForegroundColor White
Write-Host ("-" * 60) -ForegroundColor Gray

foreach ($model in $MODELS) {
    if ($RESULTS[$model]["Latency"].Success) {
        $lat = $RESULTS[$model]["Latency"]
        Write-Host ("{0,-20} {1,10:F2} {2,10:F2} {3,10:F2} {4,10:F2}" -f `
            $model, $lat.Avg, $lat.P50, $lat.P95, $lat.P99) -ForegroundColor Gray
    }
}

Write-Host "`n[SUMMARY] Throughput Comparison:" -ForegroundColor Cyan
Write-Host ("{0,-20} {1,15} {2,10} {3,15}" -f "Model", "Throughput", "Errors", "Total Requests") -ForegroundColor White
Write-Host ("-" * 60) -ForegroundColor Gray

foreach ($model in $MODELS) {
    if ($RESULTS[$model]["Throughput"].Success) {
        $thr = $RESULTS[$model]["Throughput"]
        Write-Host ("{0,-20} {1,12:F2} req/s {2,7} {3,12}" -f `
            $model, $thr.Throughput, $thr.TotalErrors, $thr.TotalRequests) -ForegroundColor Gray
    }
}

Write-Host "`n[SUMMARY] Memory Usage:" -ForegroundColor Cyan
foreach ($model in $MODELS) {
    if ($RESULTS[$model]["Memory"].Success) {
        $mem = $RESULTS[$model]["Memory"]
        Write-Host "  $model : $($mem.Readings -join ', ')" -ForegroundColor Gray
    }
}

# Calculate overall statistics
$totalDuration = ((Get-Date) - $START_TIME).TotalMinutes
Write-Host "`n[INFO] Total Test Duration: $([math]::Round($totalDuration, 2)) minutes" -ForegroundColor Cyan

# Cleanup
Write-Host "`n[CLEANUP] Stopping and removing container..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null | Out-Null
docker rm $CONTAINER_NAME 2>$null | Out-Null
Write-Host "[OK] Cleanup complete" -ForegroundColor Green

# Save results to JSON
$resultsJson = $RESULTS | ConvertTo-Json -Depth 10
$resultsJson | Out-File -FilePath "performance_results.json" -Encoding UTF8
Write-Host "`n[INFO] Results saved to performance_results.json" -ForegroundColor Cyan

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "[SUCCESS] Phase 9: Performance Validation Complete!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "`nReview the results above and update END_TO_END_TEST_PROGRESS.md" -ForegroundColor Yellow
