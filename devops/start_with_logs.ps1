# ==========================================================
# MetricGuard - Docker Startup with Log File Output
# ==========================================================
#
# This script runs all MetricGuard Docker services and saves
# all container output to a dedicated log file:
#
#   devops/docker_logs.txt
#
# Usage:
#   cd devops
#   .\start_with_logs.ps1
#
# ==========================================================

$LogFile = Join-Path $PSScriptRoot "docker_logs.txt"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  MetricGuard - Docker Compose (with logging)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Log file: $LogFile" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop all containers." -ForegroundColor DarkGray
Write-Host ""

# Run docker compose and tee output to both console and log file
docker compose -f docker/docker-compose.yml up --build 2>&1 | Tee-Object -FilePath $LogFile
