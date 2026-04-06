# Data Model: Full Dapr Deployment — Minikube & Oracle OKE

**Feature**: `006-full-dapr-oracle-deploy`  
**Date**: 2026-04-06

> No new database tables. All entities in this feature are Kubernetes/Dapr configuration artifacts.

---

## Kubernetes & Dapr Entities

### 1. Dapr Component Manifests (K8s CRDs)

Five Dapr component YAML files deployed to the cluster namespace:

| Component Name | Type | Building Block | Scope |
|----------------|------|----------------|-------|
| `taskpubsub` | `pubsub.kafka` | Pub/Sub | todo-backend |
| `statestore` | `state.redis` | State Store | todo-backend |
| `reminder-cron` | `bindings.cron` | Cron Binding | todo-backend |
| `k8ssecrets` | `secretstores.kubernetes` | Secrets | todo-backend |
| *(mTLS is automatic)* | built-in | Service Invocation | all |

**Fields per component**:
- `metadata.name` — component name referenced in Dapr API calls
- `spec.type` — Dapr component type
- `spec.version` — always `v1`
- `spec.metadata[]` — key-value config (brokers, schedule, etc.)
- `scopes[]` — list of Dapr app-ids that can use this component

---

### 2. Kubernetes Secret

One K8s Secret per environment (Minikube / OKE):

```
Secret name: todo-chatbot-backend-secret
Namespace:   default
```

| Key | Description |
|-----|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET_KEY` | JWT signing secret |
| `JWT_ALGORITHM` | HS256 |
| `JWT_EXPIRATION_HOURS` | 24 |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | gpt-4o |
| `DAPR_ENABLED` | "true" |
| `DAPR_HTTP_PORT` | "3500" |
| `DAPR_PUBSUB_NAME` | "taskpubsub" |
| `REMINDER_POLL_INTERVAL` | "300" |

> Dapr Secrets building block reads `JWT_SECRET_KEY` and `DATABASE_URL` from the K8s Secret named `todo-chatbot-backend-secret` via `k8ssecrets` component.

---

### 3. Helm Release Configuration

```
Chart:    todo-chatbot/
Release:  todo-chatbot
Target:   default namespace
```

**New values added for this feature**:

```yaml
dapr:
  enabled: true
  cronSchedule: "@every 5m"     # cron binding interval

kafka:
  brokers: "kafka:9092"          # K8s internal DNS

frontend:
  daprEnabled: true              # enables sidecar on frontend pod
  daprAppId: "todo-frontend"

monitoring:
  enabled: false                 # kube-prometheus-stack deployed separately
```

---

### 4. GitHub Actions Workflow State

```
File: .github/workflows/deploy.yml
Trigger: push to main
```

**Job flow**:
```
build-and-push
  └── outputs: backend_tag, frontend_tag (= github.sha)

deploy (needs: build-and-push)
  └── inputs: backend_tag, frontend_tag, OKE_KUBECONFIG (secret)
```

**No persistent state** — each run is stateless. Helm release state lives in the K8s cluster (Helm secrets).

---

### 5. Monitoring Stack (separate Helm release)

```
Chart:    kube-prometheus-stack
Release:  monitoring
Namespace: monitoring
```

Key configuration:
- `prometheus.serviceMonitor` — scrapes Dapr sidecar metrics port 9090
- `grafana.adminPassword` — stored as GitHub Secret or set via `--set`
- `alertmanager.config` — basic alert rules for pod restarts and high error rate

---

## Source File Layout

```
.github/
└── workflows/
    └── deploy.yml                         # NEW: CI/CD pipeline

todo-chatbot/
├── templates/
│   ├── kafka.yaml                         # EXISTS: Zookeeper + Kafka K8s deployment
│   ├── dapr-components.yaml               # UPDATE: add statestore + cron binding components
│   ├── deployment.yaml                    # UPDATE: add Dapr annotations to frontend pod
│   └── secret.yaml                        # EXISTS: backend secret (already updated)
└── values.yaml                            # UPDATE: add cronSchedule, frontend daprEnabled

backend/
└── src/
    └── api/
        └── routes/
            └── dapr_bindings.py           # NEW: POST /reminder-cron handler

dapr/
├── components/                            # EXISTS: local dev components
│   ├── statestore.yaml                    # NEW: local state store component
│   └── reminder-cron.yaml                 # NEW: local cron binding component
└── components-docker/                     # EXISTS: Docker compose components

k8s/
└── monitoring/
    └── prometheus-values.yaml             # NEW: kube-prometheus-stack config
```
