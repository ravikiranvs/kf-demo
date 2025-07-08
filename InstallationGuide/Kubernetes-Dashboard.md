# Kubeflow Dashboard Creation

This guide describes how to deploy the **Kubernetes Dashboard** (commonly used with Kubeflow) and configure an admin user for access.

We use the [Kubernetes Dashboard Helm Chart](https://github.com/kubernetes/dashboard) and set up a ServiceAccount with `cluster-admin` privileges.


### Install the Dashboard

```bash
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
helm repo update
helm upgrade --install kubernetes-dashboard \
  kubernetes-dashboard/kubernetes-dashboard \
  --create-namespace \
  --namespace kubernetes-dashboard
```

This will deploy the Dashboard and related resources.

---

### Create an Admin ServiceAccount

Create a ServiceAccount (`admin-user`) in the `kubernetes-dashboard` namespace.

```bash
cat <<EOF > dashboard-adminuser.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
EOF

kubectl apply -f dashboard-adminuser.yaml
```


Grant `cluster-admin` privileges to the `admin-user`.

```bash
cat <<EOF > dashboard-adminuser-role-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOF

kubectl apply -f dashboard-adminuser-role-binding.yaml
```

#### Create a Token Secret

Explicitly create a ServiceAccount token secret for `admin-user`.

```bash
cat <<EOF > dashboard-adminuser-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/service-account.name: "admin-user"
type: kubernetes.io/service-account-token
EOF


kubectl apply -f dashboard-adminuser-secret.yaml
```

#### Expose the Dashboard

By default, the Dashboard is not exposed externally.
Patch the service to use a `NodePort` on port `32443` (HTTPS):

```bash
kubectl -n kubernetes-dashboard patch svc kubernetes-dashboard-kong-proxy \
  -p '{"spec": {"type": "NodePort", "ports": [{"name": "kong-proxy-tls", "port": 443, "targetPort": 8443, "nodePort": 32443, "protocol": "TCP"}]}}'
```

---

## Usage

Access the dashboard at:
`https://<node-ip>:32443`

#### Get the Login Token

Retrieve the ServiceAccount token to log into the Dashboard:

```bash
kubectl get secret admin-user -n kubernetes-dashboard -o jsonpath="{.data.token}" | base64 -d
```

Copy the output token and paste it into the Dashboard login screen.

---