# Prometheus + NVIDIA DCGM Exporter Monitoring Stack

This repository/document describes how to deploy the **Prometheus + Grafana stack** using Helm, and integrate it with NVIDIA DCGM exporter metrics in Kubernetes.

It covers installation, configuration, and dashboard setup.

---

## Installation

### Add and update Prometheus Helm repo

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

---

### Install Prometheus + Grafana stack

Default Grafana login that can be changed below:

* **Username:** `admin`
* **Password:** `prom-operator`

```bash
cat <<EOF > grafana-custom-values.yaml 
grafana:
  grafana.ini:
    security:
      allow_embedding: true
    auth.anonymous:
      enabled: true
      org_role: Viewer
EOF

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n prometheus \
  --create-namespace \
  --set prometheus.service.type=NodePort \
  --set prometheus.service.nodePort=30090 \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.service.type=NodePort \
  --set grafana.service.nodePort=31529 \
  --set grafana.adminUser=admin \
  --set grafana.adminPassword=prom-operator \
  -f grafana-custom-values.yaml

# Set NodePort for Grafana
kubectl get svc -n prometheus

# replace the <id> with output from the above command.
kubectl patch service kube-prometheus-stack-<id>-grafana -n prometheus -p '{"spec": {"type": "NodePort"}}'
```

---

## Enable NVIDIA GPU metrics

Deploy a `ServiceMonitor` to scrape metrics from the NVIDIA DCGM exporter.

Create the service monitor yaml:

```sh
cat <<EOF > gpu-operator-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: gpu-operator-servicemonitor
  labels:
    monitor: prometheus
spec:
  selector:
    matchLabels:
      app: nvidia-dcgm-exporter
  namespaceSelector:
    matchNames:
      - gpu-operator
  endpoints:
    - port: gpu-metrics
      interval: 100ms
EOF
```

Apply it:

```bash
kubectl apply -f gpu-operator-servicemonitor.yaml -n prometheus
```

---

## Access Grafana

The Grafana service gets a random NodePort. Find it:

```bash
kubectl get svc -n prometheus
```


Then open Grafana in your browser at:

```
http://<node-ip>:<node-port>
```

And log in with the credentials above.

---

### Script: Create ConfigMap for Grafana Dashboard


```bash
cat <<EOF > create_single_dashboard.sh
#!/usr/bin/env bash

if [ "\$#" -ne 1 ]; then
  echo "Usage: \$0 /path/to/dashboard.json"
  exit 1
fi

JSON_FILE="\$1"
NAMESPACE="prometheus"

if [ ! -f "\$JSON_FILE" ]; then
  echo "❌ File not found: \$JSON_FILE"
  exit 1
fi

FILENAME=\$(basename "\$JSON_FILE")
NAME=\$(echo "\${FILENAME%.json}" | tr '[:upper:]' '[:lower:]' | tr '_' '-')
CM_NAME="\${NAME}-grafana-dashboard"

echo "➡️ Creating ConfigMap: \$CM_NAME from file: \$FILENAME"

kubectl -n "\$NAMESPACE" create configmap "\$CM_NAME" \\
  --from-file="\$FILENAME"="\$JSON_FILE" \\
  --dry-run=client -o yaml | \\
  awk '
    /^metadata:/ {
      print;
      print "  labels:";
      print "    grafana_dashboard: \\"1\\"";
      next
    }
    { print }
  ' | kubectl apply -f -

echo "✅ ConfigMap \$CM_NAME created in namespace '\$NAMESPACE'."
EOF
```

Run it with your dashboard file [`DCGM_DASH.json`](./DCGM_DASH.json):

```bash
bash create_single_dashboard.sh DCGM_DASH.json
```

---
