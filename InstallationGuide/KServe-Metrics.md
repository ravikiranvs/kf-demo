# KServe and vLLM Metrics Setup

This guide provides steps to enable **metrics collection** for KServe and vLLM in a Kubeflow environment using Prometheus and Grafana.

---

## Configure ServiceMonitor for vLLM Metrics

Create a **ServiceMonitor** for KServe metrics collection by Prometheus.

*Know the prometheus release id*
```bash
kubectl get prometheus -n prometheus -o yaml | grep release:
```
**replace the `<id>` with output from the above command.**

```bash
cat <<EOF > vllm-service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: vllm-service-monitor
  namespace: prometheus
  labels:
    release: kube-prometheus-stack-<id>
spec:
  endpoints:
    - interval: 15s
      port: http
  namespaceSelector:
    any: true
  selector:
    matchLabels:
      networking.internal.knative.dev/serviceType: Private
EOF

kubectl apply -f vllm-service-monitor.yaml
```

This configuration:

* Scrapes metrics from services labeled as `networking.internal.knative.dev/serviceType=Private`
* Targets the default `http` port

---

### Import Grafana dashboard for vLLM

To visualize vLLM metrics in Grafana, use the provided `vLLM.json` dashboard definition with the helper script:

Refer to [Prometheus-Grafana.md](./Prometheus-Grafana.md) for the creation of `create_single_dashboard.sh` script.

```bash
bash create_single_dashboard.sh vLLM.json
```

This script creates a Grafana dashboard for vLLM metrics based on `vLLM.json`.

---


## Configure ServiceMonitor for KServe Metrics

Create a **ServiceMonitor** for KServe metrics collection by Prometheus.

*Know the prometheus release id*
```bash
kubectl get prometheus -n prometheus -o yaml | grep release:
```
**replace the `<id>` with output from the above command.**

```bash
cat <<EOF > kserve-service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kserve-service-monitor
  namespace: prometheus
  labels:
    release: kube-prometheus-stack-<id>
spec:
  endpoints:
    - interval: 15s
      port: http-usermetric
  namespaceSelector:
    any: true
  selector:
    matchLabels:
      networking.internal.knative.dev/serviceType: Private
EOF

kubectl apply -f kserve-service-monitor.yaml
```

This targets the `http-usermetric` port for KServe-specific metrics.

---

### Import Grafana dashboard for vLLM

To visualize KServe metrics in Grafana, use the provided `KServe_Dash.json` dashboard definition with the helper script:

Again, refer to [Prometheus-Grafana.md](./Prometheus-Grafana.md) for the creation of `create_single_dashboard.sh` script.

```bash
bash create_single_dashboard.sh KServe_Dash.json
```

This script creates a Grafana dashboard for KServe metrics based on `KServe_Dash.json`.


---

