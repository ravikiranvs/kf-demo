# OpenCost Deployment

This guide describes how to deploy and configure **OpenCost** to monitor Kubernetes cluster costs with custom pricing and Prometheus integration.

---

## Deploy OpenCost

### Configuration for OpenCost

Create a file named `open-cost-local.yaml` with the following content:

* Sets custom pricing for CPU, RAM, storage, and GPU.
* Configures OpenCost to use an internal Prometheus service in the `prometheus` namespace.

To find the prometheus service name execute the below command:

```bash
kubectl -n prometheus get svc | grep NodePort |grep -Eo 'kube-prometheus-stack-[0-9]+-prometheus'
```
*Example Output: kube-prometheus-stack-1745-prometheus*

```bash
cat <<EOF > open-cost-local.yaml
opencost:
  customPricing:
    enabled: true
    costModel:
      description: Modified prices based on your internal pricing
      CPU: 1.25
      RAM: 0.50
      storage: 0.25
      GPU: 10.0
  prometheus:
    internal:
      serviceName: <prometheus-service-name>
      namespaceName: prometheus
      port: 9090
      scheme: http

service:
  type: NodePort

networkPolicies:
  prometheus:
    namespace: prometheus
EOF
```

---

### Install OpenCost

Run the following Helm command:

```bash
helm install opencost \
  --repo https://opencost.github.io/opencost-helm-chart \
  opencost \
  --namespace opencost \
  --create-namespace \
  -f open-cost-local.yaml
```

This deploys OpenCost with the specified configuration and exposes it as a NodePort service.

---

## Update OpenCost (optional)

If you change your `open-cost-local.yaml`, apply the updates with:

```bash
helm upgrade opencost \
  --repo https://opencost.github.io/opencost-helm-chart \
  opencost \
  --namespace opencost \
  -f open-cost-local.yaml
```

---

## Access OpenCost

After deployment:

* Run `kubectl get svc -n opencost` to find the NodePort for the `opencost` service.
* Access the OpenCost dashboard at:
  `http://<node-ip>:<node-port>`

---