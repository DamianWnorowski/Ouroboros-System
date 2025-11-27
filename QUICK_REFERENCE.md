# Ouroboros System - Quick Reference

## 🚀 Essential Commands

### Setup
```bash
make onboard              # Complete automated setup
make health               # Quick health check
```

### Development
```bash
make chain-all            # Full system validation
make test                 # Run tests
make verify               # Run verification
make format               # Format code
make lint                 # Lint code
```

### Operations
```bash
make start                # Start orchestrator
make start-api            # Start API server
make stop                 # Stop services
```

### Deployment
```bash
make docker-build         # Build Docker image
make docker-push          # Push to registry
./scripts/deploy.sh       # Deploy to K8s
```

## 📍 Key Files

### Configuration
- `.env` - Environment variables (create from `.env.example`)
- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration

### Core Systems
- `core/orchestrator.py` - Dynamic orchestrator
- `core/api.py` - REST API
- `core/verification/oracle.py` - Oracle engine
- `core/generators/alpha.py` - Alpha generator

### Scripts
- `scripts/onboard.sh` - Onboarding
- `scripts/health-check.sh` - Health check
- `scripts/chain-all.sh` - Master chain
- `scripts/auto-chain.py` - AI chaining

## 🔗 API Endpoints

```
GET  /                    # System info
GET  /health              # Health check
GET  /agents              # List agents
GET  /agents/{id}         # Agent details
POST /verify              # Run verification
GET  /metrics             # Prometheus metrics
```

## 🎯 Verification Levels

```
--level 0  # Existence only
--level 1  # + Syntax
--level 2  # + Schema
--level 3  # + Semantic
--level 4  # + Cross-ref
--level 5  # + Simulation
--level 6  # + Reverse engineering (full)
```

## 🐳 Docker Commands

```bash
docker build -t ouroboros/orchestrator .
docker run -p 8000:8000 ouroboros/orchestrator
docker-compose up -d
docker-compose logs -f
```

## ☸️ Kubernetes Commands

```bash
kubectl apply -f deployment/kubernetes/
kubectl get pods -n ouroboros
kubectl logs -f <pod-name> -n ouroboros
kubectl port-forward svc/ouroboros-orchestrator 8000:80 -n ouroboros
```

## 📚 Documentation Quick Links

- [Quick Start](QUICK_START_GUIDE.md)
- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Oracle Integration](ORACLE_INTEGRATION.md)
- [Alpha Generator](ALPHA_GENERATOR_INTEGRATION.md)

## 🔧 Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Verification Fails
```bash
python -m core.verification.cli --level 0  # Start with L0
```

### Docker Issues
```bash
docker-compose build --no-cache
docker-compose down -v  # Clean volumes
```

## 📊 Health Check

```bash
# Quick check
make health

# Detailed
python -m core.verification.cli --level 3
```

---

*Quick Reference - Essential commands and links*

