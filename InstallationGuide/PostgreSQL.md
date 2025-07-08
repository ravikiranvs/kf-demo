# PostgreSQL + pgAdmin Deployment on Kubernetes

This guide explains how to deploy **PostgreSQL** and **pgAdmin4** on a Kubernetes cluster using Helm charts from Bitnami and Runix.

### Install PostgreSQL

**Change the Superuser password: `<su-password>`**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add runix https://helm.runix.net
helm repo update


helm install fs-postgres bitnami/postgresql \
  --set auth.postgresPassword=<su-password> \
  --set primary.persistence.size=8Gi \
  --namespace postgres \
  --create-namespace
```

---

### Install pgAdmin4

Install pgAdmin4 (release name: `fs-pgadmin`) using the Runix chart.

This will deploy pgAdmin4 with:
* Login email: `user`
* Login password: `password`
* NodePort service for external access
* 8Gi of persistent storage

**Change the configuration as required.**

```bash
helm install fs-pgadmin runix/pgadmin4 \
  --set serviceAccount.create=true \
  --set env.email=user \
  --set env.password=password \
  --set service.type=NodePort \
  --set persistentVolume.size=8Gi \
  --namespace postgres
```

---

## Access pgAdmin4

Once deployed, you can access the pgAdmin4 web interface:

```bash
kubectl get svc -n postgres fs-pgadmin
```

Look for the `NodePort` value (e.g., `30080`) and open in your browser:

```
http://<node-ip>:<nodeport>
```

---
