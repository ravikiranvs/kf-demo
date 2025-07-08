# Kubeflow + MLflow on Kubernetes using JUJU

This guide describes how to set up **JUJU** on Kubernetes, deploy **Kubeflow**, integrate **MLflow**, and configure required resources and dashboard links.

---

## Install JUJU

Install JUJU (client) on your machine:

```bash
sudo snap install juju --channel=3.6/stable
mkdir -p ~/.local/share
```

---

## System Configuration (on all Kubernetes nodes)

Increase `inotify` limits (required by JUJU):

```bash
sudo sysctl fs.inotify.max_user_instances=1280
sudo sysctl fs.inotify.max_user_watches=655360
```

Make it persistent across reboots:

```bash
sudo nano /etc/sysctl.conf
```

Add at the end:

```
fs.inotify.max_user_instances=1280
fs.inotify.max_user_watches=655360
```

---

## Bootstrap JUJU on Kubernetes

### Register your Kubernetes cluster

```bash
kubectl config view --raw | juju add-k8s coe-k8s --client
```

### Bootstrap a JUJU controller

```bash
juju bootstrap coe-k8s k8ctrl
```

---

## Deploy Kubeflow

### Create a model

```bash
juju add-model kubeflow
```

### Deploy Kubeflow

```bash
juju deploy kubeflow --trust
```

### Configure components

**You can change the <u>user</u> and <u>password</u>**
```bash
juju config istio-ingressgateway gateway_service_type="NodePort"
juju config dex-auth static-username=dell
juju config dex-auth static-password=dell1234
```

Watch status:

```bash
juju status --watch 5s
```

Check ingress gateway service:

```bash
kubectl -n kubeflow get svc istio-ingressgateway-workload -o wide
```

---

## Deploy MLflow

Deploy MLflow:

```bash
juju deploy mlflow --trust
juju status --watch 5s
```

Get MinIO credentials:

```bash
juju run mlflow-server/0 get-minio-credentials
```

Sample output:

```
access-key: minio
secret-access-key: <YOUR_SECRET_ACCESS_KEY>
```

---

## Deploy and integrate Resource Dispatcher

```bash
juju deploy resource-dispatcher --trust
juju status --watch 5s
```

Relate components:

```bash
juju relate mlflow-server:secrets resource-dispatcher:secrets
juju relate mlflow-server:pod-defaults resource-dispatcher:pod-defaults
juju integrate mlflow-minio:object-storage kserve-controller:object-storage
```

Configure MinIO secret key (replace with actual value from earlier step):

```bash
juju config minio secret-key=<YOUR_SECRET_ACCESS_KEY>
juju status --watch 5s
```
---

## Dashboard Links

Integrate dashboard links for MLflow:

```bash
juju integrate mlflow-server:ingress istio-pilot:ingress
juju integrate mlflow-server:dashboard-links kubeflow-dashboard:links
```

---


## First Login to Kubeflow & Automatic Namespace Creation

After deploying Kubeflow and configuring the Istio ingress gateway with **basic auth**, you can log in to the Kubeflow dashboard and automatically create a per-user namespace.

---

### Access the Kubeflow Dashboard

Get the NodePort and IP of the Istio ingress gateway:

```bash
kubectl -n kubeflow get svc istio-ingressgateway-workload -o wide
```

Look for a line like:

```
istio-ingressgateway-workload   NodePort   IP   80:<HTTP-PORT>/TCP,443:<HTTPS-PORT>/TCP
```

Then open in your browser:

```
http://<HEAD-NODE-IP>:<HTTP(S)-PORT>/
```

---

### Login

When prompted for credentials, enter the ones you configured earlier:

```
Username: dell
Password: dell1234
```

---

### Automatic Namespace Creation

Kubeflow supports **multi-tenancy** by creating a unique namespace for each user upon first login.

* When you log in, the Kubeflow backend will automatically create a **Profile** and a corresponding namespace. **You are prompted for the <u>Namespace</u> name**.
* This namespace is configured with appropriate permissions so that the user can run pipelines, deploy notebooks, and use MLflow without interfering with other users.

You can verify that the namespace was created:

```bash
kubectl get ns
```

And you can list Profiles:

```bash
kubectl get profiles
```

---

Here is a clean and clear **Markdown section** you can add to your documentation:

---

## Create MLflow's MinIO Secret in the New Profile Namespace

To enable to access the MinIO object storage from with-in the new Namespace, you need to create an S3-compatible secret and a service account.

---

### Create the MinIO S3 Secret

Run the following command, replacing `<new-ns>` with the name of the new namespace and `<AWS_SECRET_ACCESS_KEY>` with the actual secret key you obtained earlier:

```bash
kubectl create secret generic s3-secret \
  --namespace <new-ns> \
  --from-literal=AWS_ACCESS_KEY_ID=minio \
  --from-literal=AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> \
  --from-literal=AWS_S3_ENDPOINT=http://mlflow-minio.kubeflow:9000
```

---

### Add KServe Annotations to the Secret

These annotations allow KServe to discover and use the MinIO endpoint correctly:

```bash
kubectl patch secret s3-secret -n <new-ns> --type='merge' -p='
{
  "metadata": {
    "annotations": {
      "serving.kserve.io/s3-endpoint": "mlflow-minio.kubeflow:9000",
      "serving.kserve.io/s3-usehttps": "0"
    }
  }
}'
```

---

### 3Create a ServiceAccount Using the Secret

Save the following YAML manifest as `serviceaccount-s3.yaml` after correcting the `namespace`:

```yaml
cat <<EOF > serviceaccount-s3.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kserve-controller-s3
  namespace: <new-ns>
secrets:
  - name: s3-secret
EOF
```

Apply it:

```bash
kubectl apply -f serviceaccount-s3.yaml
```

---

### Verify

The secret and service account should now exist in the namespace:

```bash
kubectl get secret s3-secret -n <new-ns>
kubectl get serviceaccount kserve-controller-s3 -n <new-ns>
```

---