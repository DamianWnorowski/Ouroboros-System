#!/bin/bash
# Deployment script for Ouroboros System

set -e

ENVIRONMENT=${1:-production}
NAMESPACE=${2:-ouroboros}

echo "🚀 Deploying Ouroboros System to $ENVIRONMENT..."

# Build Docker image
echo "Building Docker image..."
docker build -t ouroboros/orchestrator:latest .

# Tag for registry (if needed)
# docker tag ouroboros/orchestrator:latest registry.example.com/ouroboros/orchestrator:latest
# docker push registry.example.com/ouroboros/orchestrator:latest

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/deployment.yaml
kubectl apply -f deployment/kubernetes/service.yaml

# Wait for deployment
echo "Waiting for deployment..."
kubectl rollout status deployment/ouroboros-orchestrator -n $NAMESPACE --timeout=5m

# Check status
echo "Deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "✅ Deployment complete!"

