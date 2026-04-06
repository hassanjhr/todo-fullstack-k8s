# Tasks: Full Dapr Deployment — Minikube & Oracle OKE

**Branch**: `006-full-dapr-oracle-deploy`  
**Input**: `specs/006-full-dapr-oracle-deploy/plan.md`, `spec.md`, `data-model.md`, `contracts/dapr-apis.md`  
**Total Tasks**: 56  
**User Stories**: 4 (US1 Minikube, US2 Oracle OKE, US3 CI/CD, US4 Monitoring)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[US#]**: User story this task belongs to
- All paths are absolute from repo root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new directories, local Dapr component files, and configuration scaffolding before Helm chart work begins.

- [ ] T001 Create `k8s/monitoring/` directory and `.gitkeep` placeholder
- [ ] T002 [P] Create `dapr/components/statestore.yaml` — local Redis state store component (host: localhost:6379, type: state.redis v1)
- [ ] T003 [P] Create `dapr/components/reminder-cron.yaml` — local cron binding component (type: bindings.cron v1, schedule: "@every 5m")
- [ ] T004 [P] Create `dapr/components-docker/statestore.yaml` — Docker-internal Redis state store (host: redis:6379)
- [ ] T005 [P] Create `dapr/components-docker/reminder-cron.yaml` — Docker cron binding (same schedule as local)
- [ ] T006 Update `backend/.env.example` — add DAPR_ENABLED, DAPR_HTTP_PORT, DAPR_PUBSUB_NAME, DAPR_STATE_STORE_NAME, REMINDER_POLL_INTERVAL

**Checkpoint**: Local Dapr component files ready; directory structure in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend cron handler, Helm chart Dapr component updates, and frontend Dapr wiring. MUST complete before any user story can be verified end-to-end.

⚠️ **CRITICAL**: No user story can be fully tested until this phase is complete.

- [ ] T007 Create `backend/src/api/routes/dapr_bindings.py` — FastAPI router with `POST /reminder-cron` endpoint that calls `process_due_reminders(db)` from `reminder_service.py`
- [ ] T008 Update `backend/src/main.py` — import and register `dapr_bindings.router` with prefix `""` (no prefix, Dapr binding calls root path `/reminder-cron`)
- [ ] T009 Update `backend/src/config.py` — add `DAPR_STATE_STORE_NAME: str = "statestore"` and `DAPR_SECRETS_STORE_NAME: str = "k8ssecrets"` to Settings class
- [ ] T010 Update `todo-chatbot/templates/dapr-components.yaml` — add statestore component (type: state.redis, redisHost: redis-master:6379, actorStateStore: true, scopes: [todo-backend])
- [ ] T011 Update `todo-chatbot/templates/dapr-components.yaml` — add reminder-cron binding component (type: bindings.cron, schedule from `.Values.dapr.cronSchedule`, scopes: [todo-backend])
- [ ] T012 Update `todo-chatbot/templates/dapr-components.yaml` — add scopes: [todo-backend] to existing `taskpubsub` and `k8ssecrets` components
- [ ] T013 Update `todo-chatbot/templates/deployment.yaml` — add Dapr sidecar annotations to frontend pod template: `dapr.io/enabled`, `dapr.io/app-id: "todo-frontend"`, `dapr.io/app-port: "3000"`, `dapr.io/metrics-port: "9091"` (conditional on `.Values.dapr.enabled`)
- [ ] T014 Update `todo-chatbot/templates/deployment.yaml` — add `dapr.io/enable-metrics: "true"` and `dapr.io/metrics-port: "9090"` to backend pod annotations (conditional on `.Values.dapr.enabled`)
- [ ] T015 Update `todo-chatbot/values.yaml` — add `dapr.cronSchedule: "@every 5m"` and `dapr.enableMetrics: true` fields under existing `dapr:` block
- [ ] T016 Create `frontend/lib/api/dapr-client.ts` — utility that returns base API URL: if `NEXT_PUBLIC_DAPR_ENABLED=true` returns `http://localhost:3500/v1.0/invoke/todo-backend/method`, else returns `NEXT_PUBLIC_API_URL`
- [ ] T017 Update `frontend/lib/api/tasks.ts`, `reminders.ts`, `tags.ts` — replace hardcoded `process.env.NEXT_PUBLIC_API_URL` with `getApiBaseUrl()` from `dapr-client.ts`
- [ ] T018 [P] Update `frontend/.env.local` — add `NEXT_PUBLIC_DAPR_ENABLED=false` (local dev default) and `NEXT_PUBLIC_DAPR_SIDECAR_URL=http://localhost:3500`
- [ ] T019 [P] Update `frontend/.env.example` — same new vars as T018

**Checkpoint**: Backend handles `/reminder-cron`, Helm chart has all 5 Dapr components, frontend API calls are Dapr-aware. Foundation ready for all user stories.

---

## Phase 3: User Story 1 — Local Dapr Stack on Minikube (Priority: P1) 🎯 MVP

**Goal**: `minikube start` → `helm upgrade --set dapr.enabled=true` → all 5 Dapr building blocks active and verified.

**Independent Test**: `kubectl get components` shows taskpubsub, statestore, reminder-cron, k8ssecrets. `kubectl get pods` shows `2/2 Running` for backend (app + sidecar). Task creation produces Kafka event. Cron fires every 5 min.

### Implementation

- [ ] T020 [US1] Verify `todo-chatbot/templates/kafka.yaml` — confirm healthcheck uses `kafka-topics --bootstrap-server localhost:9092 --list` (already correct; confirm no ARM incompatibility)
- [ ] T021 [US1] Update `todo-chatbot/templates/service.yaml` — ensure `NodePort` is default, add `type: {{ .Values.backend.service.type | default "NodePort" }}` and same for frontend (needed for US2 LoadBalancer toggle)
- [ ] T022 [US1] Create `specs/006-full-dapr-oracle-deploy/minikube-verify.sh` — bash script that runs all Minikube verification steps: `kubectl get components`, `kubectl get pods`, task creation curl, Kafka topic check
- [ ] T023 [US1] Update `specs/006-full-dapr-oracle-deploy/quickstart.md` — add exact `dapr init --kubernetes` output expectations and verification commands for all 5 building blocks
- [ ] T024 [US1] Update `todo-chatbot/values.yaml` — add `backend.service.type: NodePort` and `frontend.service.type: NodePort` as explicit defaults (enables clean override for OKE in US2)
- [ ] T025 [US1] Update `CLAUDE.md` Active Technologies section — add Dapr 1.17.x on Kubernetes, Kafka in-cluster, full building block list

**Checkpoint**: `helm upgrade --set dapr.enabled=true` on Minikube deploys all pods with Dapr sidecars. All 5 Dapr components register. `/reminder-cron` fires on schedule. Kafka receives task events.

---

## Phase 4: User Story 2 — Oracle OKE Cloud Deployment (Priority: P2)

**Goal**: OKE cluster provisioned, app deployed via Helm with LoadBalancer, all 5 Dapr building blocks running, public URL accessible.

**Independent Test**: `kubectl get svc todo-chatbot-frontend` shows `EXTERNAL-IP`. Frontend accessible at `http://<EXTERNAL-IP>:3000`. `kubectl get components` shows all 5 Dapr components. Task creation produces Kafka event on OKE cluster.

### Implementation

- [ ] T026 [US2] Update `todo-chatbot/values.yaml` — add `frontend.service.type: NodePort` default, add OKE override comment block: `# OKE: --set frontend.service.type=LoadBalancer`
- [ ] T027 [US2] Update `todo-chatbot/templates/service.yaml` — frontend service type uses `.Values.frontend.service.type | default "NodePort"` (from T021, ensure applied to both backend and frontend services)
- [ ] T028 [P] [US2] Update `todo-chatbot/values.yaml` — add GHCR image repo fields: `backend.image.repository: ghcr.io/hassanjhr/todo-backend` and `frontend.image.repository: ghcr.io/hassanjhr/todo-frontend` with `pullPolicy: Always` for cloud deployments
- [ ] T029 [P] [US2] Verify `backend/Dockerfile` — confirm multi-stage build, non-root user (`USER nobody`), and produces a working image. Add `--platform=linux/arm64` comment for OKE ARM builds.
- [ ] T030 [P] [US2] Verify `frontend/Dockerfile` — confirm Next.js standalone output (`output: 'standalone'` in `next.config.js`), non-root user, ARM64 compatible base image (`node:20-alpine`).
- [ ] T031 [US2] Create `k8s/oke/README.md` — step-by-step OKE cluster provisioning guide: OCI Console → OKE Quick Create → ARM Ampere A1.Flex shape → download kubeconfig → configure kubectl
- [ ] T032 [US2] Create `k8s/oke/create-secrets.sh` — helper script: `kubectl create secret generic todo-backend-secrets --from-literal=...` for JWT, DB URL, Kafka brokers on OKE
- [ ] T033 [US2] Update `todo-chatbot/templates/dapr-components.yaml` — update `k8ssecrets` component: add `namespace: {{ .Release.Namespace }}` to ensure it reads from app namespace, not dapr-system

**Checkpoint**: Running `helm upgrade --set dapr.enabled=true --set frontend.service.type=LoadBalancer --set backend.image.repository=ghcr.io/hassanjhr/todo-backend` on OKE deploys full stack with public LoadBalancer IP.

---

## Phase 5: User Story 3 — CI/CD via GitHub Actions (Priority: P3)

**Goal**: Push to `main` → images built → pushed to GHCR → deployed to OKE automatically, zero manual steps.

**Independent Test**: Merge a PR to `main`, observe GitHub Actions `deploy.yml` workflow run in GitHub UI, verify new image tag deployed to OKE within 15 minutes.

### Implementation

- [ ] T034 [US3] Create `.github/workflows/deploy.yml` — full pipeline: trigger on push to main; Job 1 (build-and-push): checkout, docker/login-action (GHCR), docker/build-push-action for backend and frontend with `latest` + `sha` tags; Job 2 (deploy, needs: build-and-push): setup kubectl from `OKE_KUBECONFIG` secret, install Dapr CLI, `dapr init --kubernetes --wait || dapr upgrade --kubernetes --wait`, `helm upgrade --install` with all `--set` overrides, `kubectl rollout status`
- [ ] T035 [US3] Update `.github/workflows/deploy.yml` — add `permissions: contents: read, packages: write` to build job for GHCR push authorization
- [ ] T036 [US3] Create `.github/workflows/deploy.yml` — add environment protection: deploy job runs only on `main` branch; add `if: github.ref == 'refs/heads/main'` guard
- [ ] T037 [P] [US3] Create `.github/workflows/ci.yml` — lightweight CI-only workflow: trigger on PRs; runs `pytest` for backend and `npm run build` for frontend; does NOT deploy; blocks merge on failure
- [ ] T038 [P] [US3] Create `backend/tests/test_dapr_bindings.py` — unit test for `/reminder-cron` endpoint: mock `process_due_reminders`, assert 200 response
- [ ] T039 [US3] Create `docs/github-secrets.md` — document all required GitHub Secrets: `OKE_KUBECONFIG` (base64 kubeconfig), `DATABASE_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY` with description and how to set each
- [ ] T040 [US3] Update `README.md` root — add CI/CD section: how to set up GitHub Secrets, how the pipeline works, how to monitor deployments in GitHub Actions UI

**Checkpoint**: GitHub Actions workflows created. Push to `main` triggers deploy. PR triggers CI checks only.

---

## Phase 6: User Story 4 — Monitoring & Logging (Priority: P4)

**Goal**: Prometheus + Grafana running on OKE, Dapr sidecar metrics scraped, pod health visible in dashboard.

**Independent Test**: `kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80` → open Grafana → import Dapr dashboard (ID 14746) → see Dapr component health and request rate metrics for the last 24 hours.

### Implementation

- [ ] T041 [US4] Create `k8s/monitoring/prometheus-values.yaml` — kube-prometheus-stack Helm values: Grafana admin password placeholder, Grafana service type LoadBalancer, Prometheus additionalScrapeConfigs for Dapr sidecar metrics (port 9090), retention 7d, persistent storage disabled (Always Free — no block volume)
- [ ] T042 [US4] Create `k8s/monitoring/README.md` — install instructions: `helm repo add prometheus-community`, `helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f k8s/monitoring/prometheus-values.yaml`; Grafana access; import dashboard ID 14746
- [ ] T043 [US4] Update `todo-chatbot/templates/deployment.yaml` — add `prometheus.io/scrape: "true"`, `prometheus.io/port: "9090"`, `prometheus.io/path: "/metrics"` pod annotations to backend when `dapr.enabled=true` (enables Prometheus auto-discovery)
- [ ] T044 [US4] Update `todo-chatbot/templates/deployment.yaml` — same Prometheus annotations for frontend pod (metrics port 9091) when `dapr.enabled=true`
- [ ] T045 [US4] Create `k8s/monitoring/alerts/pod-restart-alert.yaml` — PrometheusRule manifest: alert fires when pod restart count > 3 in 10 minutes; severity: warning
- [ ] T046 [US4] Update `specs/006-full-dapr-oracle-deploy/quickstart.md` — add Monitoring section: install commands, port-forward command, Grafana dashboard import steps, expected metrics visible

**Checkpoint**: `kubectl get pods -n monitoring` shows Prometheus, Grafana, AlertManager running. Dapr sidecar metrics visible in Grafana.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T047 [P] Update root `README.md` — add feature 006 section: Part B Minikube steps, Part C Oracle OKE steps, CI/CD setup, monitoring setup
- [ ] T048 [P] Update `backend/src/services/reminder_service.py` — make `process_due_reminders` idempotent: check `reminder.is_sent` flag before processing to prevent duplicate sends when cron fires and legacy poll both run
- [ ] T049 [P] Update `backend/src/api/routes/__init__.py` — verify `dapr_bindings` router is exported correctly
- [ ] T050 [P] Update `docker-compose.local.yml` — add `redis` service (port 6379) so Dapr state store works in full local Docker stack (matches `dapr/components-docker/statestore.yaml`)
- [ ] T051 Update `.gitignore` — add `kubeconfig.yaml`, `*.kubeconfig`, `k8s/oke/kubeconfig*` to prevent accidental credential commits
- [ ] T052 Update `todo-chatbot/Chart.yaml` — bump `appVersion` to `006` and `version` to `0.6.0`
- [ ] T053 [P] Create `specs/006-full-dapr-oracle-deploy/e2e-checklist.md` — end-to-end verification checklist: all 9 items from quickstart.md verification section, formatted as checkboxes
- [ ] T054 Run full Minikube deployment verification: `kubectl get components` (5 components), `kubectl get pods` (2/2), create task via frontend → verify Kafka topic, wait 5 min → verify `/reminder-cron` called in backend logs
- [ ] T055 Commit all changes and push branch `006-full-dapr-oracle-deploy`
- [ ] T056 Update PR description with deployment instructions for reviewer

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately. T002–T005 fully parallel.
- **Phase 2 (Foundational)**: Depends on Phase 1. T007–T019 mostly parallel after T007. T008 depends on T007.
- **Phase 3 (US1 Minikube)**: Depends on Phase 2 complete. T020–T025 mostly parallel.
- **Phase 4 (US2 OKE)**: Depends on Phase 2 complete. T026–T033 mostly parallel. Can run alongside Phase 3.
- **Phase 5 (US3 CI/CD)**: Depends on Phase 4 (needs GHCR image repos set). T034–T040.
- **Phase 6 (US4 Monitoring)**: Depends on Phase 4 (needs Dapr metrics annotations). T041–T046.
- **Phase 7 (Polish)**: Depends on all story phases complete. T047–T056.

### User Story Dependencies

- **US1 (Minikube)**: After Phase 2. No dependencies on US2/US3/US4.
- **US2 (OKE)**: After Phase 2. No dependencies on US1 (parallel possible).
- **US3 (CI/CD)**: After US2 complete (needs image repos and OKE cluster).
- **US4 (Monitoring)**: After US2 complete (needs Dapr metrics annotations in deployed pods).

### Within Each Phase

- Helm chart tasks (T010–T015): can run in parallel (different sections of different files)
- Frontend tasks (T016–T019): T016 before T017 (client before callers)
- CI/CD tasks (T034–T040): T034 is foundation, T035–T036 amend it, T037 is independent

---

## Parallel Execution Examples

### Phase 2 (Foundational)

```bash
# Run in parallel:
Task T007: Create backend/src/api/routes/dapr_bindings.py
Task T010: Update dapr-components.yaml (statestore)
Task T011: Update dapr-components.yaml (cron)
Task T013: Update deployment.yaml (frontend sidecar)
Task T016: Create frontend/lib/api/dapr-client.ts

# Then sequentially:
Task T008: Register router in main.py  (after T007)
Task T017: Update frontend API files    (after T016)
```

### Phase 3 + 4 (US1 + US2 in parallel)

```bash
# US1 track:
T020 → T021 → T022 → T023 → T024 → T025

# US2 track (simultaneously):
T026 → T027 → T028 → T029 → T030 → T031 → T032 → T033
```

---

## Implementation Strategy

### MVP First (US1 — Minikube only)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational — all 5 Dapr components wired)
3. Complete Phase 3 (US1 — Minikube verification)
4. **STOP and VALIDATE**: `kubectl get components` = 5 running, pods 2/2, Kafka event confirmed
5. Demo Minikube deployment with full Dapr building blocks

### Incremental Delivery

1. Phase 1 + 2 → Foundation with all 5 Dapr blocks ✓
2. Phase 3 → Minikube demo ready ✓
3. Phase 4 → OKE deployment ready ✓
4. Phase 5 → Automated CI/CD ✓
5. Phase 6 → Monitoring dashboard ✓
6. Phase 7 → Polished, documented, E2E verified ✓

---

## Notes

- All 5 Dapr building blocks are **required** (not optional) per FR-001 through FR-008
- `process_due_reminders` must be idempotent (T048) — cron binding and legacy poll can both trigger it
- Frontend Dapr service invocation is opt-in via `NEXT_PUBLIC_DAPR_ENABLED=true` — defaults to false for local dev
- OKE Always Free ARM Ampere: all images (`cp-kafka:7.6.0`, `daprio/dapr:1.17.x`, `python:3.11-slim`, `node:20-alpine`) have confirmed ARM64 builds
- Dapr `statestore` Redis component uses `redis-master:6379` — this is the service name installed by `dapr init --kubernetes`
- Never commit `kubeconfig.yaml` — added to `.gitignore` in T051
