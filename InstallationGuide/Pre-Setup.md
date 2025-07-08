# Pre-requisites

This document describes the necessary tools and configurations you need to set up before proceeding to the next steps.

---

## Install Important Network Tools

Install basic networking utilities such as `ifconfig`, `netstat`, and others using the `net-tools` package.

```bash
sudo apt install -y net-tools
```

---

## Enable SSH

To enable remote access to your system over SSH:

### Install OpenSSH Server

```bash
sudo apt install openssh-server
```

### Check SSH Service Status

Verify if the SSH service is running:

```bash
sudo systemctl status ssh
```

### Enable SSH if Disabled

If SSH is not enabled, you can enable it to start at boot:

```bash
sudo systemctl enable ssh
```

---

Once these steps are complete, your system will have the required networking tools installed and SSH access enabled.

---