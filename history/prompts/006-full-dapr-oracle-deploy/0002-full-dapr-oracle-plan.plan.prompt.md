---
id: "0002"
title: "Full Dapr Oracle Deploy Plan"
stage: plan
date: "2026-04-06"
surface: agent
model: claude-sonnet-4-6
feature: "006-full-dapr-oracle-deploy"
branch: "006-full-dapr-oracle-deploy"
user: hassanjhr
command: "/sp.plan"
labels: ["dapr", "oracle-oke", "minikube", "kafka", "github-actions", "monitoring", "helm", "kubernetes"]
links:
  spec: "specs/006-full-dapr-oracle-deploy/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/006-full-dapr-oracle-deploy/plan.md
  - specs/006-full-dapr-oracle-deploy/research.md
  - specs/006-full-dapr-oracle-deploy/data-model.md
  - specs/006-full-dapr-oracle-deploy/quickstart.md
  - specs/006-full-dapr-oracle-deploy/contracts/dapr-apis.md
tests: []
---

## Prompt

```text
/sp.plan
```

## Response

Generated full implementation plan for `006-full-dapr-oracle-deploy` covering:

**Phase 1** — All 5 Dapr building blocks:
- Pub/Sub (Kafka, already exists) — verified working
- State Store (Redis via `dapr init --kubernetes`) — new component YAML
- Cron Binding (`reminder-cron`) — new component YAML + backend `dapr_bindings.py` handler
- Secrets (`k8ssecrets` via `secretstores.kubernetes`) — already in chart, wire to backend startup
- Service Invocation (Dapr sidecar on frontend pod, route API calls via `localhost:3500/v1.0/invoke/todo-backend/...`)

**Phase 2** — Helm chart OKE-ready (LoadBalancer service, GHCR image repos, ARM pull policy)

**Phase 3** — GitHub Actions CI/CD (`deploy.yml`) — build → push GHCR → `dapr init --kubernetes` (idempotent) → `helm upgrade` → `kubectl rollout status`

**Phase 4** — Monitoring: `kube-prometheus-stack` + Dapr metrics scrape config + Grafana dashboard

**ADR suggestions raised**:
- `dapr-service-invocation-routing`
- `kafka-in-cluster-vs-managed`

Artifacts:
- `specs/006-full-dapr-oracle-deploy/plan.md`
- `specs/006-full-dapr-oracle-deploy/research.md`
- `specs/006-full-dapr-oracle-deploy/data-model.md`
- `specs/006-full-dapr-oracle-deploy/quickstart.md`
- `specs/006-full-dapr-oracle-deploy/contracts/dapr-apis.md`
