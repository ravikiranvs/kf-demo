# Kubernetes Deployment using Kubespray

## Overview

This document describes how to deploy a **multi-node Kubernetes cluster** using **Kubespray**.
Kubespray uses **Ansible** to provision and manage Kubernetes clusters in a repeatable and production-ready manner.

---

## Prerequisites

### Infrastructure Requirements

* Ubuntu-based Linux nodes
* Minimum 2 nodes recommended:

  * Control Plane node(s)
  * Worker node(s)
* SSH access to all nodes
* A non-root user with sudo privileges on all nodes
* Outbound internet access from all nodes

---

## Step 1: Prepare the Host System

On the machine where Kubespray will be executed (often the control plane node):

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl openssh-client
```

---

## Step 2: Configure Passwordless SSH Access

Kubespray relies on Ansible, which requires **passwordless SSH** connectivity from the deployment host to all Kubernetes nodes.

### Generate an SSH Key (if not already present)

```bash
ls ~/.ssh/id_ed25519 || ssh-keygen -t ed25519
```

Accept default values and leave the passphrase empty unless your security policy requires otherwise.

### Copy SSH Key to All Nodes

Replace the placeholders with your environment values:

```bash
ssh-copy-id <ssh_user>@<control_plane_ip>
ssh-copy-id <ssh_user>@<worker_node_ip>
```

Repeat this for **all control plane and worker nodes**.

### Verify SSH Connectivity

```bash
ssh <ssh_user>@<node_ip> hostname
```

Ensure login succeeds without a password prompt.

---

## Step 3: Clone Kubespray Repository

See all Kubespray releases [here](https://github.com/kubernetes-sigs/kubespray/releases). Each release targets a different version of Kubernetes and other components.

```bash
cd ~
git clone https://github.com/kubernetes-sigs/kubespray.git --branch release-2.28
cd kubespray
```

---

## Step 4: Create Cluster Inventory

Kubespray uses an Ansible inventory to define the cluster topology.

### Create a Custom Inventory

```bash
cp -rf inventory/sample inventory/mycluster
```

### Define Inventory File

Edit `inventory/mycluster/inventory.ini` and replace placeholders as required:

```ini
[all]
<control_plane_node_name> ansible_host=<control_plane_ip> ip=<control_plane_ip>
<worker_node_name>        ansible_host=<worker_node_ip>        ip=<worker_node_ip>

[kube_control_plane]
<control_plane_node_name>

[etcd]
<control_plane_node_name>

[kube_node]
<control_plane_node_name>
<worker_node_name>

[calico_rr]

[k8s_cluster:children]
kube_control_plane
kube_node
calico_rr
```

### Notes

* For production clusters, use **multiple control plane and etcd nodes**
* Control plane nodes can also act as workers if required
* Default CNI used by Kubespray is **Calico**

---

## Step 5: Set Up Python Virtual Environment

Kubespray requires specific Python dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 6: Deploy the Kubernetes Cluster

Run the Kubespray Ansible playbook:

```bash
ansible-playbook \
  -i inventory/mycluster/inventory.ini \
  cluster.yml \
  --user <ssh_user> \
  --become \
  --ask-become-pass
```

### Important Notes

* You will be prompted for the sudo password
* Deployment time varies based on node count and network speed
* Ensure firewalls allow Kubernetes-required ports

---

## Step 7: Configure kubectl Access

After a successful deployment, configure `kubectl` on the control plane node:

```bash
mkdir -p ~/.kube
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
```

### Verify Cluster Health

```bash
kubectl get nodes
kubectl get pods -A
```

---

## Step 8: Enable kubectl Bash Completion

```bash
sudo apt install -y bash-completion
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 9: Install Helm

Install Helm using the official installation script:

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4
chmod 700 get_helm.sh
./get_helm.sh
```

Verify installation:

```bash
helm version
```
