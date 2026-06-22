<#
.SYNOPSIS
MetricGuard Unified Demo Startup Script

.DESCRIPTION
This script sets up the local environment, automatically launches the FastAPI Backend 
Server, the MetricGuard background Agent, and opens the API documentation in the browser.
It gracefully handles stopping both background jobs on exit.
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting MetricGuard Demo Environment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Activate Virtual Environment if available
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] Activating Virtual Environment..." -ForegroundColor Green
    . .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[1/4] Virtual Environment (.venv) not found. Relying on global python." -ForegroundColor Yellow
}

# 2. Start the Backend API Server
Write-Host "[2/4] Starting FastAPI Backend Server on port 8000..." -ForegroundColor Green
$backendJob = Start-Job -Name "MetricGuard-Backend" -ScriptBlock {
    $ProjectRoot = $using:ProjectRoot
    Set-Location $ProjectRoot
    $env:PYTHONPATH = "src"
    if (Test-Path ".venv\Scripts\python.exe") {
        & .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    } else {
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    }
}

# Wait for backend to initialize
Start-Sleep -Seconds 3

# 3. Start the Background Collection Agent
Write-Host "[3/4] Starting MetricGuard Collection Agent..." -ForegroundColor Green
$agentJob = Start-Job -Name "MetricGuard-Agent" -ScriptBlock {
    $ProjectRoot = $using:ProjectRoot
    Set-Location $ProjectRoot
    if (Test-Path ".venv\Scripts\python.exe") {
        & .venv\Scripts\python.exe agent/main.py
    } else {
        python agent/main.py
    }
}

# 4. Open Browser to API Docs
Write-Host "[4/4] Opening API Docs in browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/docs"

Write-Host "`n✅ Environment is Live! Monitoring logs..." -ForegroundColor Cyan
Write-Host "Press CTRL+C at any time to shut down the servers safely.`n" -ForegroundColor Yellow

try {
    # Keep script running to maintain jobs
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nShutting down MetricGuard Demo Environment..." -ForegroundColor Yellow
    Stop-Job -Name "MetricGuard-Backend" -ErrorAction SilentlyContinue
    Remove-Job -Name "MetricGuard-Backend" -ErrorAction SilentlyContinue
    
    Stop-Job -Name "MetricGuard-Agent" -ErrorAction SilentlyContinue
    Remove-Job -Name "MetricGuard-Agent" -ErrorAction SilentlyContinue
    Write-Host "Shutdown complete." -ForegroundColor Green
}
