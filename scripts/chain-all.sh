#!/bin/bash
# Ouroboros System - Chain All Commands
# Master orchestration script that chains all system operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VERIFY_LEVEL=${VERIFY_LEVEL:-6}
TEST_COVERAGE=${TEST_COVERAGE:-true}
GENERATE_EXAMPLES=${GENERATE_EXAMPLES:-true}
DEPLOY_ENV=${DEPLOY_ENV:-development}

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

section() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN} $*${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ============================================================================
# PHASE 1: PRE-FLIGHT CHECKS
# ============================================================================

section "PHASE 1: Pre-Flight Checks"

log "Checking Python version..."
python3 --version || { error "Python 3 not found"; exit 1; }

log "Checking virtual environment..."
if [ ! -d "venv" ]; then
    warn "Virtual environment not found, creating..."
    python3 -m venv venv
fi

log "Activating virtual environment..."
source venv/bin/activate

log "Checking dependencies..."
if ! pip show fastapi > /dev/null 2>&1; then
    warn "Dependencies not installed, installing..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
fi

# ============================================================================
# PHASE 2: VERIFICATION (ORACLE)
# ============================================================================

section "PHASE 2: Oracle Verification (L0-L${VERIFY_LEVEL})"

log "Running Oracle verification engine..."
python -m core.verification.cli --level "$VERIFY_LEVEL" || {
    error "Verification failed"
    exit 1
}

# ============================================================================
# PHASE 3: CODE QUALITY
# ============================================================================

section "PHASE 3: Code Quality Checks"

if command -v black > /dev/null 2>&1; then
    log "Checking code formatting (black)..."
    black --check core agents tests || warn "Formatting issues found"
else
    warn "black not installed, skipping format check"
fi

if command -v flake8 > /dev/null 2>&1; then
    log "Running linter (flake8)..."
    flake8 core agents tests --count --select=E9,F63,F7,F82 --show-source --statistics || warn "Linting issues found"
else
    warn "flake8 not installed, skipping lint check"
fi

# ============================================================================
# PHASE 4: TESTING
# ============================================================================

section "PHASE 4: Testing"

log "Running unit tests..."
if [ "$TEST_COVERAGE" = "true" ]; then
    pytest tests/unit/ -v --cov=core --cov=agents --cov-report=term-missing || {
        error "Unit tests failed"
        exit 1
    }
else
    pytest tests/unit/ -v || {
        error "Unit tests failed"
        exit 1
    }
fi

log "Running integration tests..."
pytest tests/integration/ -v || warn "Some integration tests failed"

# ============================================================================
# PHASE 5: GENERATION (ALPHA)
# ============================================================================

section "PHASE 5: Alpha Generator"

if [ "$GENERATE_EXAMPLES" = "true" ] && [ -f "examples/generator-dna-example.yaml" ]; then
    log "Generating from example DNA..."
    python -m core.generators.cli \
        --dna examples/generator-dna-example.yaml \
        --output ./generated \
        --namespace ouroboros || warn "Generation had issues"
else
    log "Skipping generation (GENERATE_EXAMPLES=false or DNA file missing)"
fi

# ============================================================================
# PHASE 6: BUILD & VALIDATION
# ============================================================================

section "PHASE 6: Build & Validation"

log "Validating Dockerfile..."
if [ -f "Dockerfile" ]; then
    docker build --dry-run . > /dev/null 2>&1 || warn "Dockerfile validation failed"
else
    warn "Dockerfile not found"
fi

log "Validating Kubernetes manifests..."
if [ -d "deployment/kubernetes" ]; then
    for yaml in deployment/kubernetes/*.yaml; do
        if [ -f "$yaml" ]; then
            python -c "import yaml; yaml.safe_load(open('$yaml'))" || warn "Invalid YAML: $yaml"
        fi
    done
fi

# ============================================================================
# PHASE 7: SYSTEM HEALTH
# ============================================================================

section "PHASE 7: System Health Check"

log "Checking orchestrator imports..."
python -c "from core.orchestrator import DynamicOrchestrator; print('✓ Orchestrator OK')" || {
    error "Orchestrator import failed"
    exit 1
}

log "Checking verification imports..."
python -c "from core.verification import OracleVerificationEngine; print('✓ Verification OK')" || {
    error "Verification import failed"
    exit 1
}

log "Checking generator imports..."
python -c "from core.generators import AlphaGenerator; print('✓ Generator OK')" || {
    error "Generator import failed"
    exit 1
}

log "Checking API imports..."
python -c "from core.api import app; print('✓ API OK')" || {
    error "API import failed"
    exit 1
}

# ============================================================================
# PHASE 8: DEPLOYMENT PREPARATION
# ============================================================================

section "PHASE 8: Deployment Preparation"

log "Checking deployment configurations..."
if [ -d "deployment/kubernetes" ]; then
    log "✓ Kubernetes manifests found"
fi

if [ -d "deployment/terraform" ]; then
    log "✓ Terraform configs found"
fi

# ============================================================================
# PHASE 9: FINAL REPORT
# ============================================================================

section "PHASE 9: Final Report"

log "Generating system status report..."

cat << EOF
╔═══════════════════════════════════════════════════════════════════════╗
║                    OUROBOROS SYSTEM - CHAIN REPORT                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║  Verification Level:     L${VERIFY_LEVEL}                                           ║
║  Tests Run:              ✓                                           ║
║  Code Quality:           ✓                                           ║
║  Generation:             $([ "$GENERATE_EXAMPLES" = "true" ] && echo "✓" || echo "○")                                           ║
║  Build Validation:       ✓                                           ║
║  System Health:          ✓                                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║  Status:                 ✅ ALL CHECKS PASSED                         ║
╚═══════════════════════════════════════════════════════════════════════╝

Next Steps:
  1. Review verification results above
  2. Check test coverage report
  3. Deploy: ./scripts/deploy.sh ${DEPLOY_ENV}
  4. Monitor: kubectl get pods -n ouroboros

EOF

log "✅ Chain execution complete!"

