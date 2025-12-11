# Kubernetes Deployment

Complete manifests for deploying EAC3 Converter to Kubernetes.

## Prerequisites

- Kubernetes cluster with admin access
- Docker registry access
- Built and pushed image:
  ```bash
  docker build -t your-registry/eac3-converter:latest .
  docker push your-registry/eac3-converter:latest
  ```

## Setup

1. **Update image** in `deployment.yaml`
2. **Update hostPath** in `deployment.yaml` for your input data
3. **Adjust StorageClass** in `pvc-cache.yaml` if needed

## Deploy

```bash
# Apply all manifests
kubectl apply -f .

# Check status
kubectl get pods -n eac3-converter
kubectl logs -f deployment/eac3-converter -n eac3-converter
```

## Configuration

Modify `configmap.yaml` and redeploy:
```bash
kubectl apply -f configmap.yaml
kubectl rollout restart deployment/eac3-converter -n eac3-converter
```

## Troubleshooting

- **CrashLoopBackOff**: Check logs and volume mounts
- **ImagePullBackOff**: Verify registry access
- **Volume issues**: Check hostPath permissions
