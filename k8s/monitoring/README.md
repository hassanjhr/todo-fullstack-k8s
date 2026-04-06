# Monitoring Setup — Oracle OKE

Prometheus + Grafana via `kube-prometheus-stack`, configured for Oracle OKE Always Free ARM nodes with Dapr sidecar metrics.

## Install

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f k8s/monitoring/prometheus-values.yaml \
  --set grafana.adminPassword="your-secure-password"
```

## Access Grafana

```bash
# Get Load Balancer IP
kubectl get svc -n monitoring monitoring-grafana

# Or port-forward for local access
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
# Open: http://localhost:3001 (admin / change-me-in-production)
```

## Import Dapr Dashboard

1. Open Grafana → Dashboards → Import
2. Enter ID: `14746` → Load
3. Select Prometheus datasource → Import

## Key Metrics

| Metric | Description |
|--------|-------------|
| `dapr_http_server_request_count` | Requests per Dapr component |
| `dapr_component_pubsub_egress_count` | Pub/Sub events published |
| `dapr_component_state_count` | State store operations |
| `kube_pod_container_status_restarts_total` | Pod restart count |

## Alert Rules

Pod restart alert fires when restart count > 3 in 10 minutes (severity: warning).
Configure AlertManager receivers in `prometheus-values.yaml` under `alertmanager.config`.
