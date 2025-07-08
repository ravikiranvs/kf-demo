# Milvus Deployment on Kubernetes

This guide walks you through deploying **Milvus standalone** with GPU support using Helm.

---

## Add Milvus Helm Repository

Add the official Milvus Helm chart repo and update:

```bash
helm repo add milvus https://zilliztech.github.io/milvus-helm/
helm repo update
```

---

## Configuration

Create a custom Helm values file to request and limit GPU resources:

```bash
cat <<EOF > milvus-config-values.yaml
standalone:
  resources:
    requests:
      nvidia.com/gpu: "1"
    limits:
      nvidia.com/gpu: "1"
EOF
```

---

## Deploy Milvus Standalone

Install Milvus standalone with MinIO in standalone mode, single-replica etcd, and no Pulsar:

```bash
helm install standalone-milvus milvus/milvus \
  --set cluster.enabled=false \
  --set etcd.replicaCount=1 \
  --set minio.mode=standalone \
  --set pulsarv3.enabled=false \
  --namespace milvus \
  --create-namespace \
  -f milvus-config-values.yaml
```

---

## (Optional) Expose Milvus Service UI

```bash
kubectl -n milvus patch service standalone-milvus \
  -p '{
    "spec": {
      "type": "NodePort",
      "ports": [
        {
          "name": "milvus",
          "port": 19530,
          "protocol": "TCP",
          "targetPort": "milvus"
        },
        {
          "name": "metrics",
          "port": 9091,
          "protocol": "TCP",
          "targetPort": "metrics",
          "nodePort": 32202
        }
      ]
    }
  }'
```

---