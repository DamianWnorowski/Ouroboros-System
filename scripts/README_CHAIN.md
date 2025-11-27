# Chain All Commands - Quick Reference

## 🚀 Quick Start

```bash
# Run full chain (all phases)
./scripts/chain-all.sh          # Linux/Mac
.\scripts\chain-all.ps1          # Windows

# Auto-recursive AI
python scripts/auto-chain.py
```

## 📋 What Gets Chained

1. ✅ Pre-flight checks
2. ✅ Oracle verification (L0-L6)
3. ✅ Code quality (format, lint)
4. ✅ Unit & integration tests
5. ✅ Alpha generator
6. ✅ Build validation
7. ✅ System health check
8. ✅ Final report

## 🎯 Common Chains

### Full Chain
```bash
./scripts/chain-all.sh
```

### Quick Check
```bash
python -m core.verification.cli --level 2
pytest tests/unit/ -v
```

### Pre-Deploy
```bash
./scripts/chain-all.sh
./scripts/deploy.sh production
```

## 📊 Output

Chain scripts provide:
- ✅ Phase-by-phase progress
- ✅ Success/failure indicators
- ✅ Final fitness score
- ✅ Next steps guidance

---

*See CHAIN_ALL_COMMANDS.md for complete documentation*

