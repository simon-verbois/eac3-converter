# EAC3 Converter - Kubernetes Deployment

Ce dossier contient les manifests Kubernetes pour déployer l'application EAC3 Converter.

## Prérequis

1. **Cluster Kubernetes** avec accès admin
2. **Registry Docker** (Docker Hub, ECR, GCR, etc.)
3. **Image buildée et poussée** :
   ```bash
   docker build -t your-registry/eac3-converter:latest .
   docker push your-registry/eac3-converter:latest
   ```

## Configuration requise

### 1. Modifier l'image dans `deployment.yaml`
Remplacez `your-registry/eac3-converter:latest` par votre image.

### 2. Modifier le chemin hostPath dans `deployment.yaml`
Remplacez `/path/to/your/input/data` par le chemin réel vers vos données d'entrée sur le noeud K8s.

### 3. Ajuster la StorageClass dans `pvc-cache.yaml`
Modifiez `storageClassName: standard` selon votre cluster.

## Déploiement

```bash
# Appliquer tous les manifests
kubectl apply -f k8s-manifest/

# Ou appliquer un par un
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc-cache.yaml
kubectl apply -f deployment.yaml
```

## Vérification

```bash
# Vérifier le déploiement
kubectl get pods -n eac3-converter
kubectl logs -f deployment/eac3-converter -n eac3-converter

# Vérifier les volumes
kubectl get pvc -n eac3-converter
```

## Configuration

Le ConfigMap contient la configuration complète. Pour modifier :
1. Éditez `configmap.yaml`
2. Redéployez : `kubectl apply -f configmap.yaml`
3. Redémarrez le pod : `kubectl rollout restart deployment/eac3-converter -n eac3-converter`

## Correspondance avec Docker Compose

| Docker Compose | Kubernetes |
|---|---|
| `build: .` | Image pré-buildée |
| `./test_data:/app/input` | hostPath volume |
| `./cache:/app/cache` | PersistentVolumeClaim |
| `./config:/app/config` | ConfigMap |
| `cpus: '0.5'` | `cpu: "500m"` |
| `pgrep -f main.py` | livenessProbe + readinessProbe |
| `network_mode: none` | Isolation par défaut |

## Dépannage

- **Pod en CrashLoopBackOff** : Vérifiez les logs et les volumes
- **ImagePullBackOff** : Vérifiez l'accès au registry
- **Volume non monté** : Vérifiez les chemins hostPath et permissions
