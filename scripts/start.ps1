# Ouroboros System - Startup Script (PowerShell)

Write-Host "🐍 Starting Ouroboros System..." -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install/update dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run verification
Write-Host "Running system verification..." -ForegroundColor Yellow
python -m core.verification.cli --level 3 --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some verification checks failed" -ForegroundColor Yellow
}

# Start orchestrator
Write-Host "Starting orchestrator..." -ForegroundColor Green
python -m core.orchestrator

