# Neo4j Helm Chart Deployment Guide

This guide provides step-by-step instructions for deploying a Neo4j Community Edition cluster on Kubernetes using Helm and a custom configuration file.

## Deploying Neo4j with Helm

First, create a configuration file (named `neo4j-values.yaml`) for your Neo4j deployment. This file defines resources, storage, plugins, and service details.

**Note:** Replace `<password>` with a secure password of your choice.

```bash
cat  neo4j-values.yaml
neo4j:
  name: "neo4j-cluster"
  password: "<password>"
  edition: "community"
  resources:
    cpu: "0.5"
    memory: "2Gi"
    nvidia.com/gpu: 1
volumes:
  data:
    mode: "defaultStorageClass"
    defaultStorageClass:
      accessModes:
        - ReadWriteOnce
      requests:
        storage: 10Gi
config:
  dbms.security.procedures.unrestricted: "apoc.meta.*,apoc.coll.*,apoc.load.*"
services:
  neo4j:
    enabled: true
    spec:
      type: NodePort
    ports:
      http:
        enabled: true
        port: 80
        targetPort: 7474
        name: http
      https:
        enabled: false
      bolt:
        enabled: true
        port: 7687
        targetPort: 7687
        name: tcp-bolt
env:
  NEO4J_PLUGINS: '["apoc"]'
  NEO4J_dbms_directories_import: /var/lib/neo4j/import
  NEO4J_dbms_security_procedures_unrestricted: "apoc.*"
EOF
```

With your configuration file ready, deploy Neo4j into a new namespace (`neo4j`) using Helm:

```bash
helm install neo4j-release neo4j/neo4j --namespace neo4j --create-namespace -f neo4j-values.yaml
```

## Accessing Neo4j

- The HTTP interface is available on the assigned node's external IP at port `80`.
- The Bolt protocol is accessible on port `7687`.
- Find the NodePort assigned by running:
  ```bash
  kubectl get service -n neo4j
  ```

---
