# Kubernetes Deployment Guide

## Quick Deploy

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets (from template)
kubectl create secret generic ouroboros-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=jwt-secret='...' \
  --namespace=ouroboros

# Deploy config
kubectl apply -f configmap.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Optional: Ingress
kubectl apply -f ingress.yaml
```

## Files

- `namespace.yaml` - Namespace definition
- `configmap.yaml` - Configuration
- `secrets.yaml.template` - Secrets template (DO NOT commit actual secrets)
- `deployment.yaml` - Application deployment
- `service.yaml` - Service definition
- `ingress.yaml` - Ingress (optional)

## Secrets Management

**Never commit actual secrets!**

Use the template to create secrets:
```bash
kubectl create secret generic ouroboros-secrets \
  --from-literal=key=value \
  --namespace=ouroboros
```

Or use external secret management:
- GCP Secret Manager
- AWS Secrets Manager
- HashiCorp Vault

## Health Checks

```bash
# Check pods
kubectl get pods -n ouroboros

# Check services
kubectl get services -n ouroboros

# Check logs
kubectl logs -f deployment/ouroboros-orchestrator -n ouroboros

# Port forward for local access
kubectl port-forward svc/ouroboros-orchestrator 8000:80 -n ouroboros
```

## Scaling

```bash
# Scale deployment
kubectl scale deployment ouroboros-orchestrator --replicas=3 -n ouroboros

# Auto-scaling (requires metrics server)
kubectl autoscale deployment ouroboros-orchestrator \
  --min=2 --max=10 --cpu-percent=80 \
  --namespace=ouroboros
```

## Updates

```bash
# Update image
kubectl set image deployment/ouroboros-orchestrator \
  orchestrator=ouroboros/orchestrator:new-tag \
  --namespace=ouroboros

# Rollout status
kubectl rollout status deployment/ouroboros-orchestrator -n ouroboros

# Rollback if needed
kubectl rollout undo deployment/ouroboros-orchestrator -n ouroboros
```

---

*Kubernetes Deployment Guide*

