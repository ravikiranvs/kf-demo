# Inferencing With KServe

## Prerequisite

Add the **hugging face** secret:

`kubectl -n <user-ns> create secret generic hf-secret --from-literal=HF_TOKEN=<token>`

## Deploy an LLM

Use the Endpoints Tab on the KubeFlow dashboard to deploy the LLM.

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: huggingface-llama3
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      args:
        - --model_name=llama3
        - --model_id=meta-llama/Llama-3.2-3B-Instruct
      env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-secret
              key: HF_TOKEN
              optional: false
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

Ex: `URL external` = http://huggingface-llama3.demo-ns.10.64.140.43.nip.io then `HOST` = *huggingface-llama3.demo-ns.10.64.140.43.nip.io*

## Testing

### Create a token:

`kubectl create token default-editor -n <user-ns> --audience=istio-ingressgateway.istio-system.svc.cluster.local --duration=24h`

### API Call

```bash
curl -v http://{KubeFlow_HOST}:{KubeFlow_PORT}/openai/v1/completions \
-H "content-type: application/json" -H "Host: <HOST>" \
-H "Authorization: Bearer <TOKEN>" \
-d '{"model": "llama3", "prompt": "Write a poem about colors", "stream":false, "max_tokens": 100}'
```
