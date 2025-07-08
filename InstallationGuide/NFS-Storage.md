# NFS Server + Kubernetes NFS Provisioner Setup

This guide describes how to set up an NFS server on Ubuntu and deploy the Kubernetes NFS external provisioner as a dynamic storage class.

---

## Setup NFS Server (**On Storage Machine**)

Install NFS server and client packages:

```bash
sudo apt update
sudo apt install -y nfs-kernel-server nfs-common
```

Start the NFS server service:

```bash
sudo systemctl start nfs-kernel-server.service
```

### Export a shared directory

Edit `/etc/exports` to add the export:

```bash
sudo nano /etc/exports
```

Append the following line:

```
/nfs-disk *(rw,sync,no_subtree_check,no_root_squash)
```

Create and set permissions for the shared directory:

```bash
sudo mkdir /nfs-disk
sudo chmod 777 /nfs-disk
```

Export the directory and restart the service:

```bash
sudo exportfs -a
sudo systemctl restart nfs-kernel-server.service
```

---

## Setup NFS Client (**on each Node**)

Install the NFS client package:

```bash
sudo apt update
sudo apt install -y nfs-common
```

---

## Deploy NFS Subdir External Provisioner in Kubernetes

Add the Helm repository:

```bash
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update
```

Install the provisioner with your NFS server’s IP and export path:

```bash
helm install nfs-subdir-external-provisioner \
  nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --set nfs.server=<NFS server’s IP> \
  --set nfs.path=/nfs-disk
```

---

## Set NFS as Default StorageClass

Patch the `nfs-client` storage class to be the default:

```bash
kubectl patch storageclass nfs-client \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

---
