# KServe Model Web App Deployment

This guide explains how to deploy the **KServe Models Web App** as part of a Kubeflow deployment, configure it securely, and integrate it into the Kubeflow dashboard.

### Clone the manifests repository

First, clone the Kubeflow manifests repository:

```bash
git clone https://github.com/kubeflow/manifests.git
cd manifests/apps/kserve/
```

### Configure the web app

Edit the `kustomization.yaml` for the models web app overlay. Located here:
`models-web-app/overlays/kubeflow/kustomization.yaml`

Add or update the following configuration:

```yaml
  - APP_DISABLE_AUTH=False
  - APP_SECURE_COOKIES=True
  - CSRF_SAMESITE=Strict
```

These settings ensure that:

* Authentication is enabled (`APP_DISABLE_AUTH=False`)
* Secure cookies are enforced
* CSRF protection uses `Strict` same-site policy

### Deploy the models web app

Apply the overlay using `kubectl`:

```bash
kubectl apply -k models-web-app/overlays/kubeflow
```

### Add a link to the Kubeflow dashboard

Create a YAML file named `kserve-model-webapp-link.yaml` with the link information:

```yaml
cat <<EOF > kserve-model-webapp-link.yaml
- text: Endpoints
  link: /_/kserve-endpoints/
  icon: cloud-done
EOF
```

Then, configure the Kubeflow dashboard to include this link:

```bash
juju config kubeflow-dashboard additional-external-links=@kserve-model-webapp-link.yaml
```

## Result

After completing the steps above:

* The KServe Models Web App is deployed and integrated into Kubeflow.
* The Kubeflow dashboard will show an **Endpoints** link with a cloud icon.

---