# Oracle Verification Engine

## PHANTOM GENESIS: Recursive Verification & Reverse Engineering System

**System**: IntegrityForge | **Codename**: Oracle

> "The system that verifies itself, recursively, infinitely, maximally"

---

## Overview

The Oracle Verification Engine provides multi-level recursive verification of the Ouroboros System architecture, ensuring integrity at every level from file existence to full reverse engineering.

## Verification Levels

### L0: Existence Check
- Verifies that expected files and directories exist
- Basic file system validation

### L1: Syntax Validation
- Validates Python syntax (compiles without errors)
- Validates YAML/JSON syntax
- Ensures files are parseable

### L2: Schema Compliance
- Verifies Kubernetes manifests have required fields
- Checks configuration file structure
- Validates data schemas

### L3: Semantic Validation
- Analyzes imports and dependencies
- Checks for logical consistency
- Validates content makes sense

### L4: Cross-Reference
- Verifies referenced modules exist
- Validates relationships between components
- Checks dependency chains

### L5: Simulation
- Tests that components can be imported
- Verifies modules can generate outputs
- Ensures runtime capability

### L6: Reverse Engineering
- Reconstructs architecture map
- Generates statistics
- Creates integrity report

---

## Usage

### Command Line

```bash
# Run full verification (all levels)
python -m core.verification.cli

# Verify specific level
python -m core.verification.cli --level 3

# Export to JSON
python -m core.verification.cli --json results.json

# Verify specific path
python -m core.verification.cli --path /path/to/project
```

### Python API

```python
from core.verification import OracleVerificationEngine

# Initialize engine
engine = OracleVerificationEngine('/path/to/project')

# Run verification
results = await engine.verify_all(max_level=6)

# Generate report
report = engine.generate_report()
print(report)

# Export JSON
json_data = engine.export_json('results.json')
```

### Integration with Orchestrator

```python
from core.orchestrator import DynamicOrchestrator
from core.verification import OracleVerificationEngine

async def verify_system():
    # Run verification
    engine = OracleVerificationEngine('.')
    results = await engine.verify_all()
    
    # Check for failures
    failures = [r for r in results if r.status == 'fail']
    if failures:
        print(f"Found {len(failures)} verification failures")
        return False
    
    return True
```

---

## Report Format

The verification report shows:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║              PHANTOM GENESIS: ORACLE VERIFICATION REPORT                  ║
║              System: IntegrityForge | Codename: Oracle                    ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Total: X | ✅ Pass: Y | ⚠️ Warn: Z | ❌ Fail: W                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  L0: EXISTENCE                                                             ║
║    ✅ core/orchestrator.py: File exists                                   ║
║  L1: SYNTAX                                                                ║
║    ✅ core/orchestrator.py: Valid Python syntax                           ║
║  ...                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## Configuration

### Expected Paths (L0)

The engine checks for these paths by default:

- `core/orchestrator.py`
- `core/verification/oracle.py`
- `agents/base_agent.py`
- `tests/conftest.py`
- `deployment/kubernetes/`
- `Dockerfile`
- `requirements.txt`
- `README.md`

### Custom Verification

Extend `OracleVerificationEngine` to add custom verification:

```python
class CustomOracle(OracleVerificationEngine):
    async def _verify_custom(self):
        # Your custom verification logic
        self.results.append(VerificationResult(
            component='custom',
            type='system',
            level=7,  # Custom level
            status='pass',
            message='Custom check passed',
        ))
```

---

## Integration

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/verify.yml
- name: Run Oracle Verification
  run: |
    python -m core.verification.cli --level 6 --json verification-results.json
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: oracle-verify
      name: Oracle Verification
      entry: python -m core.verification.cli --level 3
      language: system
      pass_filenames: false
```

---

## Statistics

The engine generates architecture statistics:

- Total files
- Total lines of code
- Number of providers/generators
- Average lines per file
- Maximum complexity
- Coverage metrics

---

## Best Practices

1. **Run regularly**: Include in CI/CD pipeline
2. **Start low**: Begin with L0-L2, then increase
3. **Fix failures**: Address L0-L2 failures first
4. **Monitor trends**: Track verification results over time
5. **Customize**: Extend for project-specific checks

---

## Troubleshooting

### Common Issues

**"File missing" errors (L0)**
- Ensure all expected files exist
- Check file paths are correct

**"Syntax error" (L1)**
- Fix Python/YAML syntax errors
- Check file encoding (should be UTF-8)

**"Schema violation" (L2)**
- Add missing required fields
- Validate YAML structure

---

*Oracle Verification Engine - Ensuring system integrity at every level*

