# KubeRay Operator with Grafana Dashboards

This guide describes how to deploy the **KubeRay Operator** and monitor Ray clusters using **Prometheus** and **Grafana dashboards**.

---

## Install KubeRay Operator

### Add Helm repo

```bash
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
```

### Create config file

**⚠️Important**: Add a list of namespaces where Kuberay clusters can be created (the `watchNamespace` section).

```bash
cat <<EOF > kuberay-operator-local.yaml
service:
  type: NodePort
singleNamespaceInstall: true
watchNamespace:
  - <user-namespace-1>
  - <user-namespace-2>
EOF
```

### Install operator (v1.3.0)
**⚠️Important**: Change the version number if needed.

```bash
helm install kuberay-operator \
  kuberay/kuberay-operator \
  --version 1.3.0 \
  --namespace kuberay-operator \
  --create-namespace \
  -f kuberay-operator-local.yaml
```

---

## Enable Monitoring

### Create PodMonitors

Deploy PodMonitors for Ray head and worker pods to allow Prometheus to scrape metrics.

#### Ray Head PodMonitor

*Know the prometheus release id*
```bash
kubectl get prometheus -n prometheus -o yaml | grep release:
```
**replace the `<id>` with output from the above command.**

```bash
cat <<EOF > ray-head-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: ray-head-monitor
  namespace: prometheus
  labels:
    release: kube-prometheus-stack-<id>
spec:
  jobLabel: ray-head
  namespaceSelector:
    matchNames: [demo-ns]
  selector:
    matchLabels:
      ray.io/node-type: head
  podMetricsEndpoints:
    - port: metrics
      relabelings:
        - action: replace
          sourceLabels: [__meta_kubernetes_pod_label_ray_io_cluster]
          targetLabel: ray_io_cluster
    - port: as-metrics
      relabelings:
        - action: replace
          sourceLabels: [__meta_kubernetes_pod_label_ray_io_cluster]
          targetLabel: ray_io_cluster
    - port: dash-metrics
      relabelings:
        - action: replace
          sourceLabels: [__meta_kubernetes_pod_label_ray_io_cluster]
          targetLabel: ray_io_cluster
EOF
```

#### Ray Worker PodMonitor

*Know the prometheus release id*
```bash
kubectl get prometheus -n prometheus -o yaml | grep release:
```
**replace the `<id>` with output from the above command.**

```bash
cat <<EOF > ray-workers-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: ray-workers-monitor
  namespace: prometheus
  labels:
    release: kube-prometheus-stack-<id>
spec:
  jobLabel: ray-workers
  namespaceSelector:
    matchNames: [demo-ns]
  selector:
    matchLabels:
      ray.io/node-type: worker
  podMetricsEndpoints:
    - port: metrics
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_label_ray_io_cluster]
          targetLabel: ray_io_cluster
EOF
```

Apply them:

```bash
kubectl apply -f ray-head-monitor.yaml
kubectl apply -f ray-workers-monitor.yaml
```

---

## Import Grafana Dashboards

Run the provided helper script to automatically load Ray dashboards:

### Create and execute script

```bash
cat <<EOF > create_ray_dashboards.sh
#!/usr/bin/env bash

REPO_URL="https://github.com/ray-project/kuberay.git"
CLONE_DIR="kuberay_grafana"
TARGET_DIR="config/grafana"
NAMESPACE="prometheus"

echo "🔄 Cloning Ray KubeRay repo..."
git clone --depth 1 "$REPO_URL" "$CLONE_DIR" || { echo "❌ Failed to clone repo."; exit 1; }

echo "📂 Searching for *_grafana_dashboard.json files in $CLONE_DIR/$TARGET_DIR"
FOUND_FILES=$(find "$CLONE_DIR/$TARGET_DIR" -type f -name "*_grafana_dashboard.json" || true)

if [ -z "$FOUND_FILES" ]; then
  echo "⚠️ No *_grafana_dashboard.json files found."
  rm -rf "$CLONE_DIR"
  exit 0
fi

echo "📄 Files found:"
echo "$FOUND_FILES"

echo
echo "🚀 Creating ConfigMaps..."
echo "$FOUND_FILES" | while read -r file; do
  [ -z "$file" ] && continue

  filename=$(basename "$file")
  name=$(echo "${filename%_grafana_dashboard.json}" | tr '[:upper:]' '[:lower:]' | tr '_' '-')
  cm_name="${name}-grafana-dashboard"

  echo "➡️ Creating ConfigMap: $cm_name from file: $filename"

  kubectl -n "$NAMESPACE" create configmap "$cm_name" \
    --from-file="$filename"="$file" \
    --dry-run=client -o yaml | \
    awk '
      /^metadata:/ {
        print;
        print "  labels:";
        print "    grafana_dashboard: \"1\"";
        next
      }
      { print }
    ' | kubectl apply -f - || {
      echo "❌ Failed to create ConfigMap for $filename"
    }
done

echo "🧹 Cleaning up..."
rm -rf "$CLONE_DIR"

echo "✅ All dashboard ConfigMaps have been created."
EOF
```

```bash
bash create_ray_dashboards.sh
```

---