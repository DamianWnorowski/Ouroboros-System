# Ouroboros System - Chain All Commands

## Master Command Chaining Reference

Complete guide for chaining and combining all Ouroboros System operations.

---

## 🚀 Quick Start

### Run Full Chain (Recommended)
```bash
# Linux/Mac
./scripts/chain-all.sh

# Windows
.\scripts\chain-all.ps1

# Or use Makefile
make all
```

### Auto-Recursive Chain AI
```bash
# Automatically chains all commands intelligently
python scripts/auto-chain.py

# With options
python scripts/auto-chain.py --max-iterations 3 --fitness-threshold 0.95
```

---

## 📋 Available Command Chains

### 1. **Full System Chain** (Recommended)
Runs all phases in optimal order:
```bash
./scripts/chain-all.sh
```

**Phases:**
1. Pre-flight checks
2. Oracle verification (L0-L6)
3. Code quality checks
4. Unit & integration tests
5. Alpha generator
6. Build validation
7. System health check
8. Final report

### 2. **Quick Health Check Chain**
```bash
# Verification only
python -m core.verification.cli --level 3

# Health check
python -c "from core.orchestrator import DynamicOrchestrator; print('OK')"
```

### 3. **Development Chain**
```bash
# Format code
make format

# Run tests
make test

# Verify
make verify
```

### 4. **Pre-Deployment Chain**
```bash
# Full verification
python -m core.verification.cli --level 6

# Run all tests
pytest tests/ -v --cov=core --cov=agents

# Build Docker
docker build -t ouroboros/orchestrator:latest .

# Validate K8s
kubectl apply --dry-run=client -f deployment/kubernetes/
```

### 5. **Continuous Integration Chain**
```bash
# What CI runs
make lint      # Code quality
make test      # Tests
make verify    # Verification
make ci        # All checks
```

---

## 🔗 Command Dependencies

### Execution Order
1. **Always start with pre-flight** (Python, dependencies)
2. **Run verification** before tests
3. **Run tests** before generation
4. **Check health** after all operations
5. **Generate report** at the end

### Prerequisites
- Python 3.11+
- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)

---

## 🎯 Command Combinations

### "Is everything working?"
```bash
./scripts/chain-all.sh
```

### "Quick check"
```bash
python -m core.verification.cli --level 2
pytest tests/unit/ -v
```

### "Full validation"
```bash
python -m core.verification.cli --level 6
pytest tests/ -v --cov
python -m core.generators.cli --dna examples/generator-dna-example.yaml
```

### "Before commit"
```bash
make format
make lint
make test
```

### "Before deployment"
```bash
./scripts/chain-all.sh
./scripts/deploy.sh production
```

---

## 📊 Chain Phases

### Phase 1: Pre-Flight
- ✅ Python version check
- ✅ Virtual environment
- ✅ Dependencies

### Phase 2: Verification (Oracle)
- ✅ L0: Existence
- ✅ L1: Syntax
- ✅ L2: Schema
- ✅ L3: Semantic
- ✅ L4: Cross-reference
- ✅ L5: Simulation
- ✅ L6: Reverse engineering

### Phase 3: Code Quality
- ✅ Formatting (black)
- ✅ Linting (flake8)
- ✅ Type checking (mypy)

### Phase 4: Testing
- ✅ Unit tests
- ✅ Integration tests
- ✅ Coverage report

### Phase 5: Generation (Alpha)
- ✅ DNA loading
- ✅ Code generation
- ✅ File validation

### Phase 6: Build Validation
- ✅ Dockerfile
- ✅ Kubernetes manifests
- ✅ Configuration files

### Phase 7: System Health
- ✅ Import checks
- ✅ Module validation
- ✅ API readiness

### Phase 8: Final Report
- ✅ Summary generation
- ✅ Status report
- ✅ Next steps

---

## 🤖 Auto-Recursive Chain AI

The `auto-chain.py` script intelligently:
- Analyzes system state
- Selects optimal command order
- Adapts based on results
- Calculates fitness score
- Stops when threshold reached

### Usage
```bash
# Basic
python scripts/auto-chain.py

# Custom
python scripts/auto-chain.py \
  --max-iterations 5 \
  --fitness-threshold 0.95 \
  --json
```

### Features
- Automatic dependency resolution
- Error recovery
- Fitness-based stopping
- JSON output support
- Iterative improvement

---

## 📈 Fitness Calculation

System fitness is calculated from:
- Verification results (30%)
- Test results (30%)
- Generation success (20%)
- Error count (20%)

**Thresholds:**
- < 0.6: Needs attention
- 0.6-0.8: Good
- 0.8-0.95: Excellent
- ≥ 0.95: Production ready

---

## 🔧 Configuration

### Environment Variables
```bash
export VERIFY_LEVEL=6           # Verification depth
export TEST_COVERAGE=true       # Include coverage
export GENERATE_EXAMPLES=true   # Run generation
export DEPLOY_ENV=production    # Deployment environment
```

### Makefile Targets
```bash
make all          # Full chain
make ci           # CI checks
make test         # Tests only
make verify       # Verification only
make format       # Format code
make lint         # Lint code
```

---

## 📝 Examples

### Example 1: Daily Development
```bash
# Morning
./scripts/chain-all.sh

# During development
make format
make test

# Before commit
make ci
```

### Example 2: Pre-Release
```bash
# Full validation
./scripts/chain-all.sh

# Build
make docker-build

# Deploy
./scripts/deploy.sh production
```

### Example 3: Continuous Monitoring
```bash
# Auto-recursive with monitoring
python scripts/auto-chain.py --max-iterations 10
```

---

## 🎓 Best Practices

1. **Always run pre-flight first**
2. **Fix verification issues before tests**
3. **Run full chain before deployment**
4. **Use auto-chain for automation**
5. **Monitor fitness scores**
6. **Review reports after chains**

---

## 🐛 Troubleshooting

### Chain Fails Early
- Check Python version
- Verify dependencies
- Check virtual environment

### Verification Fails
- Fix syntax errors first
- Address schema issues
- Check file existence

### Tests Fail
- Run individual tests
- Check test data
- Verify imports

### Generation Fails
- Check DNA file format
- Verify templates
- Check output directory

---

## 📚 Related Documentation

- `INDEX.md` - Complete navigation
- `QUICK_START_GUIDE.md` - Getting started
- `PROJECT_STATUS.md` - System status
- `Makefile` - Available targets

---

*Chain All Commands - Master orchestration for Ouroboros System*

