# Kubernetes Deployment

Complete manifests for deploying EAC3 Converter to Kubernetes.

## Prerequisites

- Kubernetes cluster with admin access
- Docker registry access

## Configuration

Adjust the configurations files based on your cluster.

## Deploy

```bash
# Rename templates files

# Apply all manifests
kubectl apply -f .

# Check status
kubectl get pods -n eac3-converter
kubectl logs -f deployment/eac3-converter -n eac3-converter
```
