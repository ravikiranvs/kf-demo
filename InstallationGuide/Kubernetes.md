# Kubernetes Cluster Setup + kubectl + helm

This document describes the steps to install and configure a Kubernetes cluster using `snap` on Ubuntu/Linux.

It covers:
* Setting up the **Head Node (Control Plane)**
* Setting up **Compute Nodes (Workers)**
* Joining compute nodes to the cluster
* Installing **kubectl** and **helm** on your workstation
* Enabling **kubectl bash-completion**

---

## Install Kubernetes

### Head Node (Control Plane)

```bash
# Install Kubernetes
sudo snap install k8s --classic --channel=1.32-classic/stable

# Bootstrap your control plane node
sudo k8s bootstrap
```

---

### Compute Node (Worker)

```bash
# Install Kubernetes
sudo snap install k8s --classic --channel=1.32-classic/stable
```

---

## Add Compute Node to the Cluster

### On the Head Node

**⚠️Important Note: Ensure the correct time is set on all nodes.⚠️**

```bash
# Check cluster status
sudo k8s status

# Generate a join token for the compute node
# Replace <Name_Of_Node> with the hostname of the compute node
sudo k8s get-join-token <Name_Of_Node> --worker

# Example: sudo k8s get-join-token coe-genai-node002 --worker
```

---

### On the Compute Node

Use the token generated from the previous step to join the cluster:

```bash
# Replace <join-token> with the token you received
sudo k8s join-cluster <join-token>
```

---

## Install kubectl and helm

You can use `kubectl` to interact with your Kubernetes cluster, and `helm` to manage packages.

### Install kubectl

```bash
sudo snap install kubectl --classic
```

### Configure kubeconfig

You need to set up your kubeconfig file so `kubectl` can talk to your cluster:

```bash
mkdir -p ~/.kube
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown $(whoami):$(whoami) ~/.kube/config
export KUBECONFIG=~/.kube/config
```

---

### Install helm

```bash
sudo snap install helm --classic
```

---

### Enable kubectl auto-completion

```bash
sudo apt install bash-completion
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

---