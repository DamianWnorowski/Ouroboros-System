# Ouroboros System - Onboarding Script (PowerShell)

Write-Host "🐍 Ouroboros System - Onboarding" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "   $pythonVersion" -ForegroundColor Green
Write-Host "✅ Python OK" -ForegroundColor Green
Write-Host ""

# Create venv
Write-Host "2. Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
}
& "venv\Scripts\Activate.ps1"
Write-Host ""

# Install dependencies
Write-Host "3. Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip -q
pip install -r requirements.txt -q
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Run verification
Write-Host "4. Running system verification..." -ForegroundColor Yellow
python -m core.verification.cli --level 3 --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some checks failed (non-critical)" -ForegroundColor Yellow
}
Write-Host ""

# Run tests
Write-Host "5. Running tests..." -ForegroundColor Yellow
pytest tests/unit/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some tests failed" -ForegroundColor Yellow
}
Write-Host ""

# Create .env if needed
Write-Host "6. Environment setup..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Create .env file with required variables" -ForegroundColor Yellow
    Write-Host "   See README_ENV_SETUP.md for guidance" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Onboarding complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Create .env file (see README_ENV_SETUP.md)"
Write-Host "  2. Run: make chain-all"
Write-Host "  3. Start: make start"
Write-Host "  4. Read: QUICK_START_GUIDE.md"
Write-Host ""

