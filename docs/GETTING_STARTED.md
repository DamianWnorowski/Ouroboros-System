# Getting Started with Ouroboros System

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/DamianWnorowski/Ouroboros-System.git
cd Ouroboros-System
```

### Step 2: Run Onboarding
```bash
# Linux/Mac
./scripts/onboard.sh

# Windows
.\scripts\onboard.ps1

# Or use Makefile
make onboard
```

### Step 3: Verify Installation
```bash
# Quick health check
make health

# Or full verification
make verify
```

### Step 4: Start System
```bash
# Start orchestrator
make start

# Or start API
make start-api
```

---

## 📋 Detailed Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file (see `README_ENV_SETUP.md`):
```bash
# Minimum required
CONSUL_HOST=localhost
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password
REDIS_HOST=localhost
JWT_SECRET=your_secret_min_32_chars
ENVIRONMENT=development
```

### 3. Verify System

```bash
# Run full chain
make chain-all

# Or individual checks
make verify
make test
make health
```

---

## 🎯 First Steps

### 1. Explore the System
```bash
# Run verification to see system status
python -m core.verification.cli

# Check available commands
make help
```

### 2. Run Examples
```bash
# Agent example
python examples/agent_example.py

# Verification example
python examples/verification_example.py

# Generator example
python examples/generator_example.py
```

### 3. Create Your First Agent
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

---

## 🐳 Docker Quick Start

```bash
# Build
docker build -t ouroboros/orchestrator:latest .

# Run
docker run -p 8000:8000 ouroboros/orchestrator:latest

# Or use compose
docker-compose up -d
```

---

## ☸️ Kubernetes Quick Start

```bash
# Deploy
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods -n ouroboros

# Port forward
kubectl port-forward svc/ouroboros-orchestrator 8000:80 -n ouroboros
```

---

## 📚 Learning Resources

1. **README.md** - System overview
2. **QUICK_START_GUIDE.md** - Quick reference
3. **INDEX.md** - Complete navigation
4. **examples/** - Code examples
5. **docs/** - Detailed documentation

---

## 🔧 Common Tasks

### Development
```bash
make format      # Format code
make lint        # Lint code
make test        # Run tests
make verify      # Run verification
```

### Deployment
```bash
make docker-build    # Build image
./scripts/deploy.sh  # Deploy to K8s
```

### Monitoring
```bash
# Start monitoring stack
docker-compose up prometheus grafana -d

# Access
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

---

## 🆘 Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Verification Failures
```bash
# Check specific level
python -m core.verification.cli --level 0  # Just existence
```

### Docker Issues
```bash
# Rebuild
docker-compose build --no-cache
```

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file created
- [ ] Verification passes
- [ ] Tests pass
- [ ] System starts successfully

---

*Getting Started - Your first steps with Ouroboros System*

