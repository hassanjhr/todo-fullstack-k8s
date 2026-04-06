# Research: Full Dapr Deployment — Minikube & Oracle OKE

**Feature**: `006-full-dapr-oracle-deploy`  
**Date**: 2026-04-06  
**Phase**: 0 — Research & Decision Log

---

## Decision 1: Dapr Building Blocks Strategy on Kubernetes

### 1a. Pub/Sub — Kafka (in-cluster)

**Decision**: Use `confluentinc/cp-kafka:7.6.0` + Zookeeper already in `todo-chatbot/templates/kafka.yaml`. Dapr component `taskpubsub` already defined in `dapr-components.yaml`.

**Rationale**: Already implemented locally. Same images work on K8s. Kafka pod gets `kafka:9092` as internal DNS — no change needed.

**Alternatives considered**:
- Redpanda: lighter (~256MB vs ~512MB), KRaft (no Zookeeper), but adds an unfamiliar image. Not needed — OKE ARM has 24GB RAM.
- Confluent Cloud: external dependency, costs money, requires network egress. Excluded per spec.

---

### 1b. State Store — Redis (auto-installed by Dapr)

**Decision**: `dapr init --kubernetes` automatically installs Redis as the default state store and creates a `statestore` Dapr component in the `dapr-system` namespace. Add an explicit `statestore.yaml` component in the `todo-chatbot` namespace to use it from the app namespace.

**Rationale**: Redis is already running as part of Dapr's self-hosted and K8s init. No additional deployment needed — just a namespace-scoped component manifest.

**How the backend uses it**: Task completion events or session caching can be stored via `dapr.io/state/statestore` HTTP API calls from the backend.

---

### 1c. Bindings — Cron (new)

**Decision**: Add a new Dapr `bindings.cron` component (`reminder-cron`) that calls the backend on a schedule. The backend exposes `POST /reminder-cron` as the binding input handler. This replaces the poll-based `reminder_service.py` scheduler on K8s.

**Rationale**: Cron binding is Dapr-native, no external scheduler needed. The backend handler endpoint follows Dapr binding naming convention: `POST /{binding-name}`.

**Component config**:
```yaml
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "@every 5m"   # configurable via values.yaml
```

---

### 1d. Secrets — Kubernetes Secret Store (Dapr)

**Decision**: Use `secretstores.kubernetes` Dapr component (already in `dapr-components.yaml` as `k8ssecrets`). Backend reads `jwt-secret`, `database-url`, `kafka-brokers` via Dapr Secrets API instead of env vars. For Minikube, K8s Secrets hold the values. For OKE, same K8s Secrets (OCI Vault is out of scope for this phase).

**How it works**:
```
Backend → GET http://localhost:3500/v1.0/secrets/k8ssecrets/jwt-secret
       ← { "jwt-secret": "..." }
```

**Rationale**: K8s Secrets + Dapr Secrets building block gives a clean abstraction layer. Secrets never touch env vars or Helm values in plaintext.

---

### 1e. Service Invocation — Frontend → Backend via Dapr

**Decision**: Add Dapr sidecar to the **frontend** pod as well. Frontend calls backend through its local Dapr sidecar: `http://localhost:3500/v1.0/invoke/todo-backend/method/api/tasks` instead of `http://todo-backend-svc:8000/api/tasks`. Dapr handles mTLS, retries, and load balancing automatically.

**Rationale**: Demonstrates the Service Invocation building block without introducing a new microservice. Frontend already calls backend REST endpoints — routing them through Dapr is a configuration change, not a code rewrite.

**Alternatives considered**:
- Split backend into two microservices: over-engineering for this project scope.
- Skip service invocation: violates FR-007.

---

## Decision 2: Oracle OKE Cluster Configuration

**Decision**: Oracle Cloud Always Free — **ARM Ampere A1** node pool.

| Spec | Value |
|------|-------|
| Shape | VM.Standard.A1.Flex |
| Nodes | 2 |
| OCPU per node | 2 |
| RAM per node | 12 GB |
| Total RAM | 24 GB |
| OKE control plane | Free (Always Free OKE) |
| Load Balancer | 1x 10 Mbps flexible (Always Free) |

**Rationale**: ARM Ampere is the best value on OCI Always Free (4 OCPU + 24GB total vs AMD micro 1 OCPU + 1GB). All Docker images used (`cp-kafka`, `daprio/dapr`, Python/Node) have ARM64 builds available.

**OKE provisioning steps** (manual one-time, then automated):
1. OCI Console → OKE → Create Cluster (Quick Create)
2. Select ARM Ampere A1.Flex nodes (2 OCPU, 12GB each)
3. Download kubeconfig → store as GitHub Secret `OKE_KUBECONFIG`

---

## Decision 3: Container Registry — GHCR

**Decision**: GitHub Container Registry (`ghcr.io/hassanjhr/todo-backend`, `ghcr.io/hassanjhr/todo-frontend`).

**Rationale**: Free for public repos, no external account needed beyond GitHub, native GitHub Actions integration (`GITHUB_TOKEN` auto-available in workflows, no extra secret needed for push).

**Image tagging strategy**: `latest` for main branch + `sha-{commit}` for traceability.

---

## Decision 4: CI/CD Pipeline Structure

**Decision**: Single GitHub Actions workflow file (`.github/workflows/deploy.yml`) with two jobs:

```
Job 1: build-and-push
  - Checkout code
  - Log in to GHCR (GITHUB_TOKEN)
  - Build + push backend image
  - Build + push frontend image
  - Output: image tags

Job 2: deploy (needs: build-and-push)
  - Set up kubectl with OKE kubeconfig (from secret OKE_KUBECONFIG)
  - Install/upgrade Dapr on OKE (dapr init --kubernetes --wait, idempotent)
  - helm upgrade --install todo-chatbot ./todo-chatbot
    --set backend.image.tag=${{ github.sha }}
    --set frontend.image.tag=${{ github.sha }}
    --set dapr.enabled=true
    --set env.DATABASE_URL=${{ secrets.DATABASE_URL }}
    --set env.JWT_SECRET_KEY=${{ secrets.JWT_SECRET_KEY }}
    --set env.OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
  - kubectl rollout status deployment/...
```

**Trigger**: `push` to `main` branch only. PRs do not trigger deploy.

**Secrets required in GitHub**:
| Secret | Value |
|--------|-------|
| `OKE_KUBECONFIG` | Base64-encoded kubeconfig for OKE cluster |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET_KEY` | JWT signing secret |
| `OPENAI_API_KEY` | OpenAI API key |

---

## Decision 5: Monitoring Stack

**Decision**: `kube-prometheus-stack` Helm chart (Prometheus Operator + Grafana + AlertManager).

**Deployment**: Separate namespace `monitoring`. Deployed once via Helm, not managed by the app Helm chart.

**Dapr metrics**: Enable via pod annotation `dapr.io/enable-metrics: "true"` and `dapr.io/metrics-port: "9090"` in deployment.yaml. Prometheus auto-scrapes via `ServiceMonitor`.

**Key dashboards**: Dapr System Dashboard (community Grafana dashboard ID 14746) + Kubernetes cluster overview.

**Alerting**: AlertManager webhook to email or Slack (optional, out of scope for basic setup — alert rules defined but notification channel left as TODO).

**Rationale**: `kube-prometheus-stack` is the standard K8s monitoring solution, works on OKE ARM, and has native Dapr support. OCI Monitoring requires OCI-specific agents and is more complex.

---

## Decision 6: Dapr Component Namespace Scoping

**Decision**: All Dapr components deployed to the **`default` namespace** (same as app). Components use `scopes` field to restrict to `todo-backend` app-id only.

**Rationale**: Simpler than creating a dedicated namespace for this project. Scoping by app-id ensures components don't affect other apps in the same namespace.

---

## Unknowns Resolved

| Unknown | Resolution |
|---------|-----------|
| Will ARM images work for all services? | Yes — confluentinc/cp-kafka 7.6.0+ has ARM64, daprio/dapr 1.17.x has ARM64, Python/Node base images have ARM64 |
| OKE Always Free still available? | As of 2026, OCI ARM Ampere A1 is Always Free (4 OCPU + 24GB total per tenancy) |
| Does Dapr cron binding work on K8s without sidecars? | No — requires Dapr sidecar on the backend pod, which is already enabled when `dapr.enabled=true` |
| Frontend Docker image size for CI/CD? | Next.js standalone output + multi-stage build keeps image ~200MB. Already in existing Dockerfile. |
| Helm chart image pull from GHCR on OKE? | OKE nodes pull from GHCR directly. For private repos: add `imagePullSecrets` with GHCR PAT. For public repo: no secret needed. |
