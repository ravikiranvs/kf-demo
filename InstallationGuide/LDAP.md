# LDAP Setup & Integration with Kubeflow Dex

This guide documents how to deploy an OpenLDAP server in Kubernetes, load user data, and integrate it with Kubeflow authentication through Dex.

---

### Deploy LDAP ConfigMap

Define a `ConfigMap` containing LDIF entries to add email addresses for users:

```bash
cat <<EOF > ldap-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ldap-custom-users
data:
  users.ldif: |
    dn: cn=user1,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user1@coe.com

    dn: cn=user2,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user2@coe.com

    dn: cn=user3,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user3@coe.com

    dn: cn=user4,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user4@coe.com

    dn: cn=user5,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user5@coe.com

    dn: cn=user6,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user6@coe.com

    dn: cn=user7,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user7@coe.com

    dn: cn=user8,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user8@coe.com

    dn: cn=user9,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user9@coe.com

    dn: cn=user10,ou=users,dc=coe,dc=org
    changetype: modify
    add: mail
    mail: user10@coe.com
EOF
```

```bash
kubectl -n ldap apply -f ldap-config.yaml
```

This creates a `ConfigMap` named `ldap-custom-users` with 10 users and their emails.

---

### Deploy OpenLDAP

Create the OpenLDAP Deployment:

This runs the `bitnami/openldap` image with:

* Admin DN: `cn=dell,dc=coe,dc=org`
* Admin Password: `dell1234`
* Users: `user1` to `user10` (password: `dell1234`)

*You can change these configurations if needed.*

```bash
cat <<EOF > ldap.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openldap
  labels:
    app: openldap
spec:
  selector:
    matchLabels:
      app: openldap
  template:
    metadata:
      labels:
        app: openldap
    spec:
      containers:
        - name: openldap
          image: bitnami/openldap:latest
          env:
            - name: LDAP_ADMIN_USERNAME
              value: "dell"
            - name: LDAP_ADMIN_PASSWORD
              value: "dell1234"
            - name: LDAP_USERS
              value: "user1,user2,user3,user4,user5,user6,user7,user8,user9,user10"
            - name: LDAP_PASSWORDS
              value: "dell1234,dell1234,dell1234,dell1234,dell1234,dell1234,dell1234,dell1234,dell1234,dell1234"
            - name: LDAP_ROOT
              value: "dc=coe,dc=org"
            - name: LDAP_ADMIN_DN
              value: "cn=dell,dc=coe,dc=org"
            - name: LDAP_PORT_NUMBER
              value: "389"
          ports:
            - containerPort: 389
              name: ldap

      volumes:
        - name: ldif-volume
          configMap:
            name: ldap-custom-users
EOF
```

```bash
kubectl -n ldap apply -f ldap.yaml
```

---

### Expose LDAP Service

Create a Kubernetes `Service` to expose LDAP on the default port 389:

```bash
cat <<EOF > ldap-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: openldap
  labels:
    app: openldap
spec:
  type: ClusterIP
  ports:
    - port: 389
      targetPort: ldap
      protocol: TCP
      name: ldap
  selector:
    app: openldap
EOF
```

```bash
kubectl -n ldap apply -f ldap-svc.yaml
```

The LDAP service is now accessible at:
`openldap.ldap.svc.cluster.local:389`

---

### Run a `Job` to add users

Run a `Job` to apply the custom LDIF file and add users and their emails:

```bash
cat <<EOF > ldap-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ldap-user-loader
  namespace: ldap
spec:
  template:
    spec:
      containers:
        - name: email-modifier
          image: bitnami/openldap:latest
          command:
            - /bin/bash
            - -c
            - |
              echo "Waiting for LDAP to be ready..."
              until ldapwhoami -x -H ldap://openldap.ldap.svc.cluster.local:389 -D "cn=dell,dc=coe,dc=org" -w dell1234; do
                sleep 5
              done
              echo "LDAP is ready, applying LDIF..."
              ldapmodify -x -H ldap://openldap.ldap.svc.cluster.local:389 -D "cn=dell,dc=coe,dc=org" -w dell1234 -f /ldifs/users.ldif
              echo "LDIF applied, exiting."
          volumeMounts:
            - name: ldif-volume
              mountPath: /ldifs
      restartPolicy: Never
      volumes:
        - name: ldif-volume
          configMap:
            name: ldap-custom-users
  backoffLimit: 2
EOF
```

```bash
kubectl -n ldap apply -f ldap-job.yaml
```

This waits for LDAP to become ready, then applies the LDIF in `ldap-config.yaml`.

---

### Integrate LDAP with Dex

Define the Dex LDAP connector configuration in `ldap-connector.yaml` and apply it to Dex:

*Remember to change any configuration below if changed during the Deployment of OpenLDAP*

```bash
cat <<EOF > ldap-connector.yaml
- type: ldap
  # Required field for connector id.
  id: ldap
  # Required field for connector name.
  name: LDAP
  config:
    # Host and optional port of the LDAP server in the form "host:port".
    # If the port is not supplied, it will be guessed based on "insecureNoSSL",
    # and "startTLS" flags. 389 for insecure or StartTLS connections, 636
    # otherwise.
    host: openldap.ldap.svc.cluster.local:389

    # Following field is required if the LDAP host is not using TLS (port 389).
    # Because this option inherently leaks passwords to anyone on the same network
    # as dex, THIS OPTION MAY BE REMOVED WITHOUT WARNING IN A FUTURE RELEASE.
    #
    insecureNoSSL: true

    # If a custom certificate isn't provide, this option can be used to turn on
    # TLS certificate checks. As noted, it is insecure and shouldn't be used outside
    # of explorative phases.
    #
    insecureSkipVerify: true

    # When connecting to the server, connect using the ldap:// protocol then issue
    # a StartTLS command. If unspecified, connections will use the ldaps:// protocol
    #
    # startTLS: true

    # Path to a trusted root certificate file. Default: use the host's root CA.
    # rootCA: /etc/dex/ldap.ca

    # A raw certificate file can also be provided inline.
    # rootCAData: ( base64 encoded PEM file )

    # The DN and password for an application service account. The connector uses
    # these credentials to search for users and groups. Not required if the LDAP
    # server provides access for anonymous auth.
    # Please note that if the bind password contains a `$`, it has to be saved in an
    # environment variable which should be given as the value to `bindPW`.
    bindDN: cn=dell,dc=coe,dc=org
    bindPW: dell1234

    # The attribute to display in the provided password prompt. If unset, will
    # display "Username"
    usernamePrompt: Username

    # User search maps a username and password entered by a user to a LDAP entry.
    userSearch:
      # BaseDN to start the search from. It will translate to the query
      # "(&(objectClass=person)(uid=<username>))".
      baseDN: ou=Users,dc=coe,dc=org
      # Optional filter to apply when searching the directory.
      filter: "(objectClass=person)"

      # username attribute used for comparing user entries. This will be translated
      # and combined with the other filter as "(<attr>=<username>)".
      username: uid
      # The following three fields are direct mappings of attributes on the user entry.
      # String representation of the user.
      idAttr: uid
      # Required. Attribute to map to Email.
      emailAttr: mail
      # Maps to display name of users. No default value.
      nameAttr: cn
      # Maps to preferred username of users. No default value.
      preferredUsernameAttr: uid

    # Group search queries for groups given a user entry.
    groupSearch:
      # BaseDN to start the search from. It will translate to the query
      # "(&(objectClass=group)(member=<user uid>))".
      baseDN: ou=Groups,dc=coe,dc=org
      # Optional filter to apply when searching the directory.
      filter: "(objectClass=groupOfNames)"

      # Following list contains field pairs that are used to match a user to a group. It adds an additional
      # requirement to the filter that an attribute in the group must match the user's
      # attribute value.
      userMatchers:
      - userAttr: dn
        groupAttr: member

      # Represents group name.
      nameAttr: cn
EOF
```

```bash
juju config dex-auth connectors=@ldap-connector.yaml
```

---

### *(Optional) Disable Automatic Profile Creation*

If you want to disable automatic profile creation in Kubeflow:

```bash
juju config kubeflow-dashboard registration-flow=false
```

---