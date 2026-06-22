# ==========================================================
# MetricGuard - Docker Startup with Log File Output
# ==========================================================
#
# This script runs all MetricGuard Docker services and saves
# all container output to a dedicated log file:
#
#   logs/docker_logs.txt
#
# Usage:
#   .\scripts\start_with_logs.ps1
#
# ==========================================================

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $ProjectRoot "logs"
# Ensure logs directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$LogFile = Join-Path $LogDir "docker_logs.txt"
$ComposeFile = Join-Path $ProjectRoot "docker\docker-compose.yml"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  MetricGuard - Docker Compose (with logging)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Log file: $LogFile" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop all containers." -ForegroundColor DarkGray
Write-Host ""

# Run docker compose and tee output to both console and log file
docker compose -f $ComposeFile up --build 2>&1 | Tee-Object -FilePath $LogFile
