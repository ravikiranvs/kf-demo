# Kubeflow Monitoring with COS

This guide describes how to deploy the **Canonical Observability Stack (COS)** for Kubeflow.

---
## 🚀 Deploy COS

### Create and switch to a COS model

```bash
juju add-model cos
juju switch cos
```

---

### Deploy MetalLB (for LoadBalancer IPs)

**Important**: You need to select an IP range that is unused.

```bash
juju deploy metallb --config iprange='<IP-Start>-<IP-End>' --trust
# Example: juju deploy metallb --config iprange='172.18.251.131-172.18.251.145' --trust
```

---

### Deploy COS Lite bundle

Download overlays:

```bash
curl -L https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays/offers-overlay.yaml -O
curl -L https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays/storage-small-overlay.yaml -O

juju deploy cos-lite --trust \
    --overlay ./offers-overlay.yaml \
    --overlay ./storage-small-overlay.yaml
```


### Get COS service URLs

```bash
juju show-unit -m cos catalogue/0 --format json | jq '.[]."relation-info".[]."application-data".url | select (. != null)'
```

You’ll see URLs like:

* "http://`172.18.251.131`/cos-grafana"
* "http://`172.18.251.131`/cos-prometheus-0"
* "http://`172.18.251.131`/cos-alertmanager"

---

### Deploy Grafana Agent in Kubeflow

```bash
juju deploy -m kubeflow grafana-agent-k8s --channel=stable
```

Test connectivity to COS Prometheus:

*COS_PROMETHEUS_IP is found In the Above Step `Get COS service URLs`*

```bash
juju exec --unit grafana-agent-k8s/0 -m kubeflow 'curl -s http://<COS_PROMETHEUS_IP>/cos-prometheus-0/api/v1/status/runtimeinfo'
```

---

## Integrate COS and Kubeflow

In `cos` model:

```bash
juju switch cos
```

```bash
juju offer cos.prometheus:receive-remote-write prometheus-receive-remote-write
juju offer cos.grafana:grafana-dashboard grafana-dashboards
juju offer cos.loki:logging loki-logging

juju consume -m kubeflow cos.prometheus-receive-remote-write
juju consume -m kubeflow cos.grafana-dashboards
juju consume -m kubeflow cos.loki-logging

juju integrate -m kubeflow grafana-agent-k8s:send-remote-write prometheus-receive-remote-write
juju integrate -m kubeflow grafana-agent-k8s:grafana-dashboards-provider grafana-dashboards
juju integrate -m kubeflow grafana-agent-k8s:logging-consumer loki-logging
```

Verify relations:

```bash
juju status -m cos grafana-agent-k8s --relations
```

---

## Integrate with Prometheus

Run in `kubeflow`:

```bash
juju switch kubeflow
```

```bash
juju integrate argo-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate dex-auth:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate envoy:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate istio-ingressgateway:metrics-endpoint grafana-agent-k8s:metrics-endpoint  
juju integrate istio-pilot:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate jupyter-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate katib-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate kfp-api:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate knative-operator:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate knative-eventing:otel-collector knative-operator:otel-collector
juju integrate knative-serving:otel-collector knative-operator:otel-collector
juju integrate kserve-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate kubeflow-profiles:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate metacontroller-operator:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate minio:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate pvcviewer-operator:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate tensorboard-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate training-operator:metrics-endpoint grafana-agent-k8s:metrics-endpoint
```

---

## Integrate with Grafana

Run in `kubeflow`:

```bash
juju switch kubeflow
```

```bash
juju integrate argo-controller:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate dex-auth:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate envoy:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate istio-pilot:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate jupyter-controller:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate katib-controller:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate kfp-api:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate kubeflow-dashboard:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate metacontroller-operator:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate minio:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate pvcviewer-operator:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju integrate training-operator:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
```

---


## Integrate with Loki

Run in `kubeflow`:

```bash
juju switch kubeflow
```

```bash
juju integrate admission-webhook:logging grafana-agent-k8s:logging-provider
juju integrate jupyter-ui:logging grafana-agent-k8s:logging-provider
juju integrate katib-db-manager:logging grafana-agent-k8s:logging-provider
juju integrate katib-ui:logging grafana-agent-k8s:logging-provider
juju integrate kfp-metadata-writer:logging grafana-agent-k8s:logging-provider
juju integrate kfp-persistence:logging grafana-agent-k8s:logging-provider
juju integrate kfp-profile-controller:logging grafana-agent-k8s:logging-provider
juju integrate kfp-schedwf:logging grafana-agent-k8s:logging-provider
juju integrate kfp-ui:logging grafana-agent-k8s:logging-provider
juju integrate kfp-viewer:logging grafana-agent-k8s:logging-provider
juju integrate kfp-viz:logging grafana-agent-k8s:logging-provider
juju integrate kubeflow-dashboard:logging grafana-agent-k8s:logging-provider
juju integrate kubeflow-volumes:logging grafana-agent-k8s:logging-provider
juju integrate mlmd:logging grafana-agent-k8s:logging-provider
juju integrate oidc-gatekeeper:logging grafana-agent-k8s:logging-provider
juju integrate tensorboards-web-app:logging grafana-agent-k8s:logging-provider
juju integrate argo-controller:logging grafana-agent-k8s:logging-provider
juju integrate dex-auth:logging grafana-agent-k8s:logging-provider
juju integrate envoy:logging grafana-agent-k8s:logging-provider
juju integrate jupyter-controller:logging grafana-agent-k8s:logging-provider
juju integrate katib-controller:logging grafana-agent-k8s:logging-provider
juju integrate kfp-api:logging grafana-agent-k8s:logging-provider
juju integrate knative-operator:logging grafana-agent-k8s:logging-provider
juju integrate kserve-controller:logging grafana-agent-k8s:logging-provider
juju integrate kubeflow-profiles:logging grafana-agent-k8s:logging-provider
juju integrate pvcviewer-operator:logging grafana-agent-k8s:logging-provider
juju integrate tensorboard-controller:logging grafana-agent-k8s:logging-provider
```

---

## Access COS dashboards

Get Grafana admin password:

```bash
juju run -m cos-controller:cos grafana/leader get-admin-password
```

Find the NodePort for the Traefik LoadBalancer:

```bash
kubectl -n cos get svc traefik-lb -o=jsonpath="{.spec.ports[0].nodePort}"
```

Access:

* Grafana: `http://<node-ip>:<nodeport>/cos-grafana`
* Prometheus: `http://<node-ip>:<nodeport>/cos-prometheus-0`

---