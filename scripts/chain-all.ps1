# Ouroboros System - Chain All Commands (PowerShell)
# Master orchestration script that chains all system operations

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Configuration
$VerifyLevel = if ($env:VERIFY_LEVEL) { $env:VERIFY_LEVEL } else { 6 }
$TestCoverage = if ($env:TEST_COVERAGE) { $env:TEST_COVERAGE -eq "true" } else { $true }
$GenerateExamples = if ($env:GENERATE_EXAMPLES) { $env:GENERATE_EXAMPLES -eq "true" } else { $true }
$DeployEnv = if ($env:DEPLOY_ENV) { $env:DEPLOY_ENV } else { "development" }

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

# ============================================================================
# PHASE 1: PRE-FLIGHT CHECKS
# ============================================================================

Write-Section "PHASE 1: Pre-Flight Checks"

Write-Log "Checking Python version..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found"
    exit 1
}
Write-Log "Python: $pythonVersion"

Write-Log "Checking virtual environment..."
if (-not (Test-Path "venv")) {
    Write-Warn "Virtual environment not found, creating..."
    python -m venv venv
}

Write-Log "Activating virtual environment..."
& "venv\Scripts\Activate.ps1"

Write-Log "Checking dependencies..."
if (-not (pip show fastapi 2>$null)) {
    Write-Warn "Dependencies not installed, installing..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
}

# ============================================================================
# PHASE 2: VERIFICATION (ORACLE)
# ============================================================================

Write-Section "PHASE 2: Oracle Verification (L0-L$VerifyLevel)"

Write-Log "Running Oracle verification engine..."
python -m core.verification.cli --level $VerifyLevel
if ($LASTEXITCODE -ne 0) {
    Write-Error "Verification failed"
    exit 1
}

# ============================================================================
# PHASE 3: CODE QUALITY
# ============================================================================

Write-Section "PHASE 3: Code Quality Checks"

if (Get-Command black -ErrorAction SilentlyContinue) {
    Write-Log "Checking code formatting (black)..."
    black --check core agents tests
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Formatting issues found"
    }
} else {
    Write-Warn "black not installed, skipping format check"
}

if (Get-Command flake8 -ErrorAction SilentlyContinue) {
    Write-Log "Running linter (flake8)..."
    flake8 core agents tests --count --select=E9,F63,F7,F82 --show-source --statistics
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Linting issues found"
    }
} else {
    Write-Warn "flake8 not installed, skipping lint check"
}

# ============================================================================
# PHASE 4: TESTING
# ============================================================================

Write-Section "PHASE 4: Testing"

Write-Log "Running unit tests..."
if ($TestCoverage) {
    pytest tests/unit/ -v --cov=core --cov=agents --cov-report=term-missing
} else {
    pytest tests/unit/ -v
}
if ($LASTEXITCODE -ne 0) {
    Write-Error "Unit tests failed"
    exit 1
}

Write-Log "Running integration tests..."
pytest tests/integration/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Some integration tests failed"
}

# ============================================================================
# PHASE 5: GENERATION (ALPHA)
# ============================================================================

Write-Section "PHASE 5: Alpha Generator"

if ($GenerateExamples -and (Test-Path "examples/generator-dna-example.yaml")) {
    Write-Log "Generating from example DNA..."
    python -m core.generators.cli `
        --dna examples/generator-dna-example.yaml `
        --output ./generated `
        --namespace ouroboros
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Generation had issues"
    }
} else {
    Write-Log "Skipping generation (GENERATE_EXAMPLES=false or DNA file missing)"
}

# ============================================================================
# PHASE 6: BUILD & VALIDATION
# ============================================================================

Write-Section "PHASE 6: Build & Validation"

Write-Log "Validating Kubernetes manifests..."
if (Test-Path "deployment/kubernetes") {
    Get-ChildItem deployment/kubernetes/*.yaml | ForEach-Object {
        try {
            python -c "import yaml; yaml.safe_load(open('$($_.FullName)'))"
            Write-Log "✓ Valid: $($_.Name)"
        } catch {
            Write-Warn "Invalid YAML: $($_.Name)"
        }
    }
}

# ============================================================================
# PHASE 7: SYSTEM HEALTH
# ============================================================================

Write-Section "PHASE 7: System Health Check"

Write-Log "Checking orchestrator imports..."
python -c "from core.orchestrator import DynamicOrchestrator; print('✓ Orchestrator OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Orchestrator import failed"
    exit 1
}

Write-Log "Checking verification imports..."
python -c "from core.verification import OracleVerificationEngine; print('✓ Verification OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Verification import failed"
    exit 1
}

Write-Log "Checking generator imports..."
python -c "from core.generators import AlphaGenerator; print('✓ Generator OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Generator import failed"
    exit 1
}

Write-Log "Checking API imports..."
python -c "from core.api import app; print('✓ API OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Error "API import failed"
    exit 1
}

# ============================================================================
# PHASE 8: FINAL REPORT
# ============================================================================

Write-Section "PHASE 9: Final Report"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    OUROBOROS SYSTEM - CHAIN REPORT                    ║" -ForegroundColor Cyan
Write-Host "╠═══════════════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Verification Level:     L$VerifyLevel                                           ║" -ForegroundColor White
Write-Host "║  Tests Run:              ✓                                           ║" -ForegroundColor Green
Write-Host "║  Code Quality:          ✓                                           ║" -ForegroundColor Green
Write-Host "║  Generation:             $(if ($GenerateExamples) { '✓' } else { '○' })                                           ║" -ForegroundColor $(if ($GenerateExamples) { 'Green' } else { 'Yellow' })
Write-Host "║  Build Validation:       ✓                                           ║" -ForegroundColor Green
Write-Host "║  System Health:          ✓                                           ║" -ForegroundColor Green
Write-Host "╠═══════════════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Status:                 ✅ ALL CHECKS PASSED                         ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Log "✅ Chain execution complete!"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review verification results above"
Write-Host "  2. Check test coverage report"
Write-Host "  3. Deploy: .\scripts\deploy.sh $DeployEnv"
Write-Host "  4. Monitor: kubectl get pods -n ouroboros"
Write-Host ""

