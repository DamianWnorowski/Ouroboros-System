# Ouroboros System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment

```bash
# Clone repository (if not already done)
git clone https://github.com/DamianWnorowski/Ouroboros-System.git
cd Ouroboros-System

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Run Oracle verification
python -m core.verification.cli --level 3

# Should show verification report with mostly ✅ passes
```

### Step 3: Run Core System

```bash
# Start orchestrator
python -m core.orchestrator

# Should start and show:
# - Agent discovery
# - Health monitoring
# - Self-healing loop
```

### Step 4: Test Generation

```bash
# Generate from example DNA
python -m core.generators.cli \
  --dna examples/generator-dna-example.yaml \
  --output ./generated

# Check generated files
ls generated/
```

### Step 5: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=agents
```

---

## 🐳 Docker Quick Start

```bash
# Build image
docker build -t ouroboros/orchestrator:latest .

# Run container
docker run -p 8000:8000 ouroboros/orchestrator:latest

# Or use docker-compose
docker-compose up -d
```

---

## ☸️ Kubernetes Quick Start

```bash
# Create namespace
kubectl apply -f deployment/kubernetes/namespace.yaml

# Deploy
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods -n ouroboros
```

---

## 🔧 Common Tasks

### Create a New Agent

```python
# agents/my_agent.py
from agents.base_agent import BaseAgent, AgentConfig

class MyAgent(BaseAgent):
    __agent__ = True
    __capabilities__ = {'my_capability'}
    
    async def initialize(self):
        self.status = "active"
    
    async def execute(self, task):
        return {"result": "success"}
    
    async def health_check(self):
        return 1.0
```

### Run Verification

```bash
# Full verification (all levels)
python -m core.verification.cli

# Specific level
python -m core.verification.cli --level 3

# Export JSON
python -m core.verification.cli --json results.json
```

### Generate a Generator

```bash
# Create DNA file (see examples/generator-dna-example.yaml)
# Then generate
python -m core.generators.cli --dna my-generator.yaml
```

### Use Worktrees

```powershell
# Load functions
. .\worktree-functions.ps1

# Create worktree
New-Worktree -BranchName "feature-name"

# List worktrees
Show-Worktrees

# Remove worktree
Remove-Worktree -BranchName "feature-name"
```

---

## 📊 System Status

Check system health:

```bash
# Verification report
python -m core.verification.cli

# Orchestrator status (when running)
curl http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd C:\Users\Ouroboros\Ouroboros-System

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Verification Failures
```bash
# Check specific level
python -m core.verification.cli --level 0  # Just existence
python -m core.verification.cli --level 1  # Syntax
```

### Docker Issues
```bash
# Rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs orchestrator
```

---

## 📚 Next Steps

1. **Read Documentation**
   - `README.md` - Overview
   - `PROJECT_STATUS.md` - Current status
   - `docs/` - Detailed guides

2. **Explore Examples**
   - `examples/generator-dna-example.yaml` - Generator DNA
   - `tests/` - Test examples

3. **Extend System**
   - Create your first agent
   - Add custom generators
   - Extend verification

---

*Quick Start Guide - Get up and running fast!*

