# Kubeflow Trainer Deployment and Access Configuration

This guide explains how to deploy the **Kubeflow Trainer components**, configure the necessary RBAC for access to Trainer CRDs, and run training jobs.

We install the Trainer Manager and Runtimes overlays from the upstream repository, then grant the `default-editor` ServiceAccount in a target namespace permissions to use Trainer CRDs.

---

### Deploy Trainer Manager

Install the Trainer Manager components:

```bash
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/manager?ref=master"
```

Verify pods are running in the `kubeflow-system` namespace:

```bash
kubectl get pods -n kubeflow-system
```

---

### Deploy Trainer Runtimes

Install the Trainer Runtimes components:

```bash
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/runtimes?ref=master"
```

---

### Configure RBAC

By default, the ServiceAccount `default-editor` in your user namespace (`<user-ns>`) does not have access to Trainer CRDs.
We grant it the necessary permissions:

#### Create `ClusterRole` with access to Trainer CRDs

```bash
cat <<EOF > trainer-crd-access.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: trainer-crd-access
rules:
- apiGroups: ["trainer.kubeflow.org"]
  resources: ["clustertrainingruntimes", "trainingruntimes", "trainjobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
EOF

kubectl apply -f trainer-crd-access.yaml
```

---

#### Bind `default-editor` to the `ClusterRole`

**Change `<user-ns>` to the namespace where the training jobs will be created.**

```bash
cat <<EOF > default-editor-trainer-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: default-editor-trainer-binding
subjects:
- kind: ServiceAccount
  name: default-editor
  namespace: <user-ns>
roleRef:
  kind: ClusterRole
  name: trainer-crd-access
  apiGroup: rbac.authorization.k8s.io
EOF

kubectl apply -f default-editor-trainer-binding.yaml
```

---