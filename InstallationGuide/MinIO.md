# MinIO Deployment on Kubernetes (Helm)

## Overview

This document describes how to deploy **MinIO**, an S3-compatible object storage system, on Kubernetes using the **official MinIO Helm chart**.

This setup is suitable for:

* Development and PoC environments
* Internal AI platforms (e.g., MLflow, Kubeflow, artifact storage)
* Standalone MinIO deployments using Kubernetes Persistent Volumes

> Note: This guide covers **standalone MinIO**. Distributed / HA MinIO requires a different configuration and is not covered here.

---

## Step 1: Add MinIO Helm Repository

```bash
helm repo add minio https://charts.min.io/
helm repo update
```

---

## Step 2: Create MinIO Helm Values File

Create a values file to control the MinIO deployment.

```bash
cat << 'EOF' > minio-helm-values.yaml
mode: standalone

replicas: 1

# Root credentials (change these)
rootUser: <minio_root_user>
rootPassword: <minio_root_password>

persistence:
  enabled: true
  size: 10Gi

resources:
  requests:
    memory: 512Mi
    cpu: 250m

service:
  type: NodePort
  port: 9000
  nodePort: <nodeport_api>

consoleService:
  type: NodePort
  port: 9001
  nodePort: <nodeport_console>

environment:
  MINIO_BROWSER: "on"

securityContext:
  enabled: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
EOF
```

### Configuration Notes

* **mode: standalone**
  Deploys a single-node MinIO instance.

* **rootUser / rootPassword**
  Replace with secure credentials or integrate with Kubernetes Secrets for production use.

* **persistence.size**
  Storage size requested from the default StorageClass.

* **NodePort services**
  Used for simplicity and direct access.
  For production, consider **Ingress** or **LoadBalancer** instead.

---

## Step 3: Deploy MinIO Using Helm

Install MinIO into a dedicated namespace:

```bash
helm install \
  --namespace minio \
  --create-namespace \
  --generate-name \
  -f minio-helm-values.yaml \
  minio/minio
```

Verify installation:

```bash
helm list -n minio
kubectl get pods -n minio
kubectl get svc -n minio
```

---

## Step 4: Access MinIO

### MinIO API Endpoint

```
http://<node_ip>:<nodeport_api>
```

Example:

```
http://<k8s-node-ip>:30900
```

### MinIO Console (Web UI)

```
http://<node_ip>:<nodeport_console>
```

Example:

```
http://<k8s-node-ip>:30901
```

Login using the configured **rootUser** and **rootPassword**.

---

## Step 5: Validate Persistent Storage

Confirm the PersistentVolumeClaim is bound:

```bash
kubectl get pvc -n minio
```

---

## Security Considerations for Production

* Do **not** hardcode credentials for production
* Use:

  * Kubernetes Secrets
  * External secret managers (Vault, AWS Secrets Manager, etc.)
* Restrict NodePort exposure using:
  * Firewall rules
  * NetworkPolicies
* Prefer Ingress with TLS for production access
