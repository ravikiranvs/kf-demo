# Welcome to the Kubeflow Deployment Guide

This guide is designed to help you set up and deploy an AI platform with a scalable and flexible way to deploy and manage machine learning workloads.

## Environment Setup

Before you begin, make sure you have the following environment setup:

* Multiple machines with GPU.
* Ubuntu 24.04 LTS installed on the machienes.

## Prerequisites

Before you start deploying the AI platform, make sure you have the following prerequisites met:

* [Pre-requisites](Pre-Setup.md)

## AI Platform Deployment

The following guides provide detailed information on deploying and configuring individual every component of the AI Platform:

* [Kubernetes Cluster Setup + kubectl + helm](./Kubernetes.md)
* [NVIDIA GPU Operator Helm Deployment](./GPU-Operator.md)
* [Prometheus and Grafana + NVIDIA DCGM Exporter Monitoring Stack](./Prometheus-Grafana.md)
* [NFS Server + Kubernetes NFS Provisioner Setup](./NFS-Storage.md)
* [Kubeflow](./Kubeflow.md)
* [Milvus Deployment on Kubernetes](./Milvus.md)
* [KServe Model Web App Deployment](./KServe-Models-Web-App.md)
* [KServe Metrics](./KServe-Metrics.md)
* [LDAP Setup & Integration with Kubeflow Dex](./LDAP.md)
* [Kubeflow Monitoring](./Kubeflow-Monitoring.md)
* [Billing and Chargeback](./OpenCost.md)
* [KubeRay Operator with Grafana Dashboards](KubeRay.md)

### Optional Components

* [SSH for Kubeflow](./SSH.md)
* [Kubernetes Dashboard](./Kubernetes-Dashboard.md)
