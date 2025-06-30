## Deploy the fine-tuned checkpoint

Use the Endpoints Tab on the KubeFlow dashboard to deploy the LLM.

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: qwen-cypher
spec:
  predictor:
    serviceAccountName: kserve-controller-s3
    model:
      modelFormat:
        name: huggingface
      args:
        - --model_name=qwen-cypher-instruct
        - --model_id=Qwen/Qwen2.5-Coder-1.5B
      storageUri: s3://mlflow-models/qwen2.5-cypher/exported-model/
      env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: s3-secret
              key: AWS_ACCESS_KEY_ID
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: s3-secret
              key: AWS_SECRET_ACCESS_KEY
        - name: MLFLOW_S3_ENDPOINT_URL
          valueFrom:
            secretKeyRef:
              name: s3-secret
              key: AWS_S3_ENDPOINT
        - name: MLFLOW_TRACKING_URI
          value: http://mlflow-server.kubeflow.svc.cluster.local:5000
      resources:
        limits:
          cpu: "6"
          memory: 24Gi
          nvidia.com/gpu: "1"
        requests:
          cpu: "6"
          memory: 24Gi
          nvidia.com/gpu: "1"
```

Once successfully created node down the hostname from the `URL external` from the `OVERVIEW` tab without the protocall.

Ex: `URL external` = http://qwen-cypher.demo-ns.10.64.140.43.nip.io then `HOST` = *qwen-cypher.demo-ns.10.64.140.43.nip.io*

## Testing

### Create a token:

`kubectl create token default-editor -n <user-ns> --audience=istio-ingressgateway.istio-system.svc.cluster.local --duration=24h`

### API Call

```bash
curl --insecure -v http(s)://{KubeFlow_HOST}:{KubeFlow_PORT}/openai/v1/completions \
-H "content-type: application/json" -H "Host: <HOST>" \
-H "Authorization: Bearer <TOKEN>" \
-d '{
  "model": "qwen-cypher-instruct",
  "prompt": "## Schema:\nNode properties:\n- **Country**\n- `location`: POINT\n- `code`: STRING Example: \"AFG\"\n- `name`: STRING Example: \"Afghanistan\"\n- `tld`: STRING Example: \"AF\"\n- **Filing**\n- `begin`: DATE_TIME Min: 2000-02-08T00:00:00Z, Max: 2017-09-05T00:00:00Z\n- `end`: DATE_TIME Min: 2000-02-08T00:00:00Z, Max: 2017-11-03T00:00:00Z\n- `originator_bank_id`: STRING Example: \"cimb-bank-berhad\"\n- `sar_id`: STRING Example: \"3297\"\n- `beneficiary_bank`: STRING Example: \"Barclays Bank Plc\"\n- `filer_org_name_id`: STRING Example: \"the-bank-of-new-york-mellon-corp\"\n- `originator_bank_country`: STRING Example: \"Singapore\"\n- `beneficiary_bank_country`: STRING Example: \"United Kingdom\"\n- `filer_org_name`: STRING Example: \"The Bank of New York Mellon Corp.\"\n- `originator_iso`: STRING Example: \"SGP\"\n- `beneficiary_bank_id`: STRING Example: \"barclays-bank-plc-london-england-gbr\"\n- `origin_lat`: STRING Example: \"1.3667\"\n- `origin_lng`: STRING Example: \"103.8\"\n- `end_date_format`: STRING Example: \"2015-09-25T00:00:00Z\"\n- `begin_date_format`: STRING Example: \"2015-03-25T00:00:00Z\"\n- `originator_bank`: STRING Example: \"CIMB Bank Berhad\"\n- `beneficiary_lat`: STRING Example: \"54\"\n- `beneficiary_iso`: STRING Example: \"GBR\"\n- `beneficiary_lng`: STRING Example: \"-2\"\n- `begin_date`: STRING Example: \"Mar 25, 2015\"\n- `id`: STRING Example: \"223254\"\n- `end_date`: STRING Example: \"Sep 25, 2015\"\n- `amount`: INTEGER Min: 1.18, Max: 2721000000\n- `number`: INTEGER Min: 1, Max: 174\n- **Entity**\n- `id`: STRING Example: \"the-bank-of-new-york-mellon-corp\"\n- `location`: POINT\n- `name`: STRING Example: \"The Bank of New York Mellon Corp.\"\n- `country`: STRING Example: \"CHN\"\nRelationship properties:\n\nThe relationships:\n(:Filing)-[:BENEFITS]->(:Entity)\n(:Filing)-[:CONCERNS]->(:Entity)\n(:Filing)-[:ORIGINATOR]->(:Entity)\n(:Entity)-[:FILED]->(:Filing)\n(:Entity)-[:COUNTRY]->(:Country)\n\n## Question:\nWhich 3 countries have the most entities linked as beneficiaries in filings?\n\nCypher:",
  "stream": false,
  "max_tokens": 300
}'
```
