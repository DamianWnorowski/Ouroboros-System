# Quick health check script (PowerShell)

$allOk = $true

python -m core.verification.cli --level 2 --quiet
if ($LASTEXITCODE -ne 0) { $allOk = $false }

python -c "from core.orchestrator import DynamicOrchestrator; print('✅ Orchestrator OK')"
if ($LASTEXITCODE -ne 0) { $allOk = $false }

python -c "from core.verification import OracleVerificationEngine; print('✅ Verification OK')"
if ($LASTEXITCODE -ne 0) { $allOk = $false }

python -c "from core.generators import AlphaGenerator; print('✅ Generator OK')"
if ($LASTEXITCODE -ne 0) { $allOk = $false }

python -c "from core.api import app; print('✅ API OK')"
if ($LASTEXITCODE -ne 0) { $allOk = $false }

if ($allOk) {
    Write-Host "✅ All systems healthy" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Some systems unhealthy" -ForegroundColor Red
    exit 1
}

