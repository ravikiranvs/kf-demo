# Harbor Deployment on Kubernetes

This document describes how to deploy **Harbor** on Kubernetes using Helm, configure access credentials, and push/pull images from the Harbor registry.

## Deploy Harbor

*Remember to change the <node-ip> to the IP address of a Kubernetes node. Add the Admin password.*

```bash
helm repo add harbor https://helm.goharbor.io
helm repo update

cat <<EOF > harbor-values.yaml
expose:
  type: nodePort
  tls:
    enabled: false
externalURL: http://<node-ip>:30002
harborAdminPassword: "<password>"
persistence:
  persistentVolumeClaim:
    registry:
      size: 100Gi
EOF

helm install harbor harbor/harbor \
  --namespace harbor \
  --create-namespace \
  -f harbor-values.yaml
```

This will expose Harbor on `http://<node-ip>:30002`

## Create Harbor Pull Secrets for Apps

Create a Kubernetes namespace for your applications:

```bash
kubectl create namespace harbor-apps
```

Create a Docker registry secret:

```bash
kubectl create secret docker-registry harbor-creds \
  --docker-server=<node-ip>:30002 \
  --docker-username=admin \
  --docker-password=<password> \
  --docker-email=unused@example.com \
  -n harbor-apps
```

You can now reference this secret in your Kubernetes deployments (`imagePullSecrets`).

## Download Image in Kubernetes Node

On a Kubernetes node, you can manually pull an image using `ctr`:

```bash
sudo /snap/k8s/current/bin/ctr --debug image pull --plain-http \
  <password>:30002/<harbor-project>/<image-name>:<tag>
```

Replace `<harbor-project>`, `<image-name>`, and `<tag>` as appropriate.

---

## DEV: Docker Developer Setup

For developers pushing/pulling images from Harbor directly with Docker:

### Configure Docker to trust the Harbor registry:

Edit Docker Engine config (e.g. **Docker Desktop → Settings → Docker Engine**), and add your Harbor endpoint to `insecure-registries`:

```json
{
  "insecure-registries": [
    "<node-ip>:30002"
  ]
}
```

Apply & Restart Docker.

### Log in to Harbor:

```bash
docker login <node-ip>:30002
```

### Tag and push images:

```bash
docker tag <image-name>:<tag> <node-ip>:30002/<project-name>/<image-name>:<tag>
docker push <node-ip>:30002/<project-name>/<image-name>:<tag>
```

---

## Adding Image to Kubernetes without Harbor

**On docker client**

```cmd
docker save <image-name>:<tag> -o <image-filename>.tar
```

*Copy the image tar file to each Kubernetes node*


**On each Kubernetes node**
```bash
sudo /snap/k8s/current/bin/ctr -n k8s.io image import <image-filename>.tar
```
---
