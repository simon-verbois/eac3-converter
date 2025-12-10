# EAC3 Converter - Kubernetes Deployment

This folder contains the Kubernetes manifests to deploy the EAC3 Converter application.

## Prerequisites

1. **Kubernetes cluster** with admin access
2. **Docker registry** (Docker Hub, ECR, GCR, etc.)
3. **Built and pushed image**:
   ```bash
   docker build -t your-registry/eac3-converter:latest .
   docker push your-registry/eac3-converter:latest
   ```

## Required Configuration

### 1. Update the image in `deployment.yaml`
Replace `your-registry/eac3-converter:latest` with your image.

### 2. Update the hostPath in `deployment.yaml`
Replace `/path/to/your/input/data` with the actual path to your input data on the K8s node.

### 3. Adjust StorageClass in `pvc-cache.yaml`
Modify `storageClassName: standard` according to your cluster.

## Deployment

```bash
# Apply all manifests
kubectl apply -f k8s-manifest/

# Or apply one by one
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc-cache.yaml
kubectl apply -f deployment.yaml
```

## Verification

```bash
# Check deployment
kubectl get pods -n eac3-converter
kubectl logs -f deployment/eac3-converter -n eac3-converter

# Check volumes
kubectl get pvc -n eac3-converter
```

## Configuration

The ConfigMap contains the complete configuration. To modify:
1. Edit `configmap.yaml`
2. Redeploy: `kubectl apply -f configmap.yaml`
3. Restart the pod: `kubectl rollout restart deployment/eac3-converter -n eac3-converter`

## Docker Compose to Kubernetes Mapping

| Docker Compose | Kubernetes |
|---|---|
| `build: .` | Pre-built image |
| `./test_data:/app/input` | hostPath volume |
| `./cache:/app/cache` | PersistentVolumeClaim |
| `./config:/app/config` | ConfigMap |
| `cpus: '0.5'` | `cpu: "500m"` |
| `pgrep -f main.py` | livenessProbe + readinessProbe |
| `network_mode: none` | Default isolation |

## Troubleshooting

- **Pod in CrashLoopBackOff**: Check logs and volumes
- **ImagePullBackOff**: Check registry access
- **Volume not mounted**: Check hostPath paths and permissions
