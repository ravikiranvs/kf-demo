# NVIDIA GPU Operator Helm Deployment

This repository provides instructions for deploying the **NVIDIA GPU Operator** on your Kubernetes cluster using Helm.

The NVIDIA GPU Operator enables GPU management, monitoring, and workloads on Kubernetes clusters.

---

### Add the NVIDIA Helm repository

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
````

### Install the NVIDIA GPU Operator

Deploy the GPU Operator into its own namespace (`gpu-operator`):

```bash
helm install --wait --generate-name \
  -n gpu-operator --create-namespace \
  nvidia/gpu-operator
```

> Notes:
>
> * `--wait` ensures Helm waits until all resources are ready.
> * `--generate-name` automatically generates a release name.

### Verify the deployment

Check the status of all pods in the `gpu-operator` namespace. They should eventually show `Running` or `Completed`:

```bash
kubectl get all -n gpu-operator
```

---