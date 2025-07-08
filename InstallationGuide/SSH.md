# Enable TLS/SSH for Kubeflow

This guide describes how to enable **TLS for Kubeflow Istio ingress** by generating a self-signed certificate and configuring Kubeflow components to use it.

---

### Create an OpenSSL configuration

Create a file named `openssl.cnf` with your cluster IPs and organization details:

**Important**: Update the `dn` section and `IP.x` fields to match your environment.

```bash
cat <<EOF > openssl.cnf
[req]
default_bits       = 4096
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[dn]
C  = IN
ST = Karnataka
L  = Bengaluru
O  = COE
OU = KubeFlow
CN = 172.18.52.185

[req_ext]
subjectAltName = @alt_names

[alt_names]
IP.1 = 172.18.52.185
IP.2 = 100.91.9.53
EOF
```


### Generate TLS key and certificate

```bash
openssl req -x509 -nodes -days 3650 -newkey rsa:4096 \
  -keyout kubeflow.key -out kubeflow.crt \
  -config openssl.cnf
```

This creates:

* `kubeflow.key` — private key
* `kubeflow.crt` — self-signed certificate


### Add SSH to Kubeflow

#### Add the certificate and key as a Juju secret:

```bash
juju add-secret istio-tls-secret \
  tls-crt="$(cat kubeflow.crt)" \
  tls-key="$(cat kubeflow.key)"
```

Take note of the secret ID returned, e.g.: `secret:d0qopqnmp25c762shtrg`

#### Grant secret access to Istio Pilot

```bash
juju grant-secret istio-tls-secret istio-pilot
```

#### Configure Kubeflow's Istio Pilot to use the secret

```bash
juju config istio-pilot tls-secret-id=secret:<your-secret-id>
```

Replace `<your-secret-id>` with the actual secret ID noted earlier.

---

#### Configure OIDC Gatekeeper with CA bundle

```bash
juju config oidc-gatekeeper ca-bundle="$(cat kubeflow.crt)"
```

---