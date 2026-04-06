# Feature Specification: Full Dapr Deployment — Minikube (Local) & Oracle Cloud OKE

**Feature Branch**: `006-full-dapr-oracle-deploy`  
**Created**: 2026-04-06  
**Status**: Draft  

---

## Overview

Deploy the Todo Full-Stack application with the **complete Dapr building-block suite** (Pub/Sub, State, Bindings/Cron, Secrets, Service Invocation) on two targets:

- **Part B — Local**: Minikube (development/testing)
- **Part C — Cloud**: Oracle Cloud Infrastructure OKE (Oracle Kubernetes Engine) — production-ready, Always Free tier eligible

Additionally, establish a full CI/CD pipeline, monitoring, and logging for the cloud environment.

---

## User Scenarios & Testing

### User Story 1 — Local Dapr Stack on Minikube (Priority: P1)

A developer starts Minikube and deploys the entire application with all Dapr building blocks active — Pub/Sub (Kafka), State Store, Cron Bindings, Secrets, and Service Invocation — without any cloud credentials or external dependencies.

**Why this priority**: Enables local development, debugging, and testing of all Dapr features before cloud deployment.

**Independent Test**: Developer runs `minikube start` and `helm upgrade --set dapr.enabled=true`, then verifies all Dapr components load and a task creation event appears in the Kafka topic.

**Acceptance Scenarios**:

1. **Given** Minikube is running and Dapr is installed on the cluster, **When** the Helm chart is deployed with `dapr.enabled=true`, **Then** all pods reach `Running` state and Dapr sidecar is injected into the backend pod.
2. **Given** the app is deployed, **When** a user creates a task, **Then** a Pub/Sub event is published to the `tasks` Kafka topic inside the cluster.
3. **Given** the app is deployed, **When** the cron binding fires, **Then** the reminder scheduler runs automatically on the configured interval.
4. **Given** the app is deployed, **When** the backend requests a secret (JWT key, DB URL), **Then** Dapr retrieves it from the configured secret store without hardcoding values.
5. **Given** the app is deployed, **When** one internal service calls another, **Then** the call routes through Dapr Service Invocation (mTLS enforced).

---

### User Story 2 — Cloud Deployment on Oracle OKE (Priority: P2)

An operator provisions a Kubernetes cluster on Oracle Cloud (OKE), deploys the application with all Dapr building blocks active, Kafka running via a cloud-compatible broker, and the system is accessible over the internet.

**Why this priority**: The production target. All local work feeds into this deployment path.

**Independent Test**: Operator runs the deployment pipeline against OKE, then accesses the frontend via the OKE load balancer IP/hostname and creates a task — verifying the event flows through Kafka and is processed by the backend.

**Acceptance Scenarios**:

1. **Given** an OKE cluster exists, **When** Dapr is initialized on the cluster and the Helm chart is applied, **Then** all Dapr components (pubsub, state, binding, secrets, service invocation) register successfully.
2. **Given** the app is running on OKE, **When** a task is created, **Then** the Pub/Sub event reaches the Kafka broker (cloud or in-cluster) and is consumed.
3. **Given** secrets are stored in OCI Vault or Kubernetes Secrets, **When** the backend starts, **Then** it reads all required secrets through the Dapr Secrets building block.
4. **Given** the OKE deployment is live, **When** the public load balancer URL is visited, **Then** the frontend loads and is fully functional.

---

### User Story 3 — CI/CD Pipeline via GitHub Actions (Priority: P3)

A developer pushes code to `main` and the pipeline automatically builds Docker images, runs tests, and deploys the updated application to OKE — without any manual steps.

**Why this priority**: Automates the release process, reducing human error and enabling consistent deployments.

**Independent Test**: Developer merges a PR to `main`, observes the GitHub Actions workflow run, and verifies that the new version is deployed to OKE within the pipeline run.

**Acceptance Scenarios**:

1. **Given** code is pushed to `main`, **When** GitHub Actions triggers, **Then** Docker images are built, tagged, and pushed to a container registry.
2. **Given** images are pushed, **When** the deploy job runs, **Then** `helm upgrade` is executed against OKE with the new image tags.
3. **Given** a deployment fails, **When** the pipeline detects the failure, **Then** the workflow marks the run as failed and no broken version is promoted.
4. **Given** secrets (OCI credentials, registry tokens), **When** the pipeline needs them, **Then** they are read from GitHub Actions Secrets — never hardcoded in the workflow file.

---

### User Story 4 — Monitoring and Logging (Priority: P4)

An operator can view real-time metrics and logs from the running application and Dapr sidecar on OKE, and receives an alert when the backend becomes unhealthy.

**Why this priority**: Observability is required for production readiness and incident response.

**Independent Test**: Operator opens the monitoring dashboard and sees request rate, error rate, and Dapr component health metrics for the last 24 hours.

**Acceptance Scenarios**:

1. **Given** the app is running on OKE, **When** the operator opens the monitoring dashboard, **Then** they see pod health, request counts, and error rates.
2. **Given** a pod crashes, **When** the alerting threshold is breached, **Then** an alert is triggered (email or webhook).
3. **Given** a task creation request fails, **When** the operator searches logs, **Then** the full error trace is visible with timestamp and request ID.

---

### Edge Cases

- What happens when the Kafka broker (in-cluster or cloud) is unreachable on startup? Backend must start successfully and log the connection failure; Pub/Sub events should retry or queue.
- What happens when an OCI Vault secret is rotated? Backend must pick up the new value on next Dapr secret resolution without a pod restart.
- What happens if the OKE node pool has insufficient resources for all Dapr sidecars? Deployment must fail gracefully with a clear error, not a silent hang.
- What happens during a rolling update in CI/CD? Old pods must continue serving traffic until new pods pass readiness probes.
- What happens if `dapr init --kubernetes` is run on a cluster where Dapr is already installed? The operation must be idempotent (upgrade, not duplicate install).

---

## Requirements

### Functional Requirements

**Part B — Minikube (Local)**

- **FR-001**: Dapr MUST be installed on Minikube using `dapr init --kubernetes`.
- **FR-002**: The Helm chart MUST deploy Kafka + Zookeeper inside the cluster when `dapr.enabled=true`.
- **FR-003**: Dapr Pub/Sub building block MUST publish task events to the in-cluster Kafka broker.
- **FR-004**: Dapr State Store building block MUST be configured (Redis, already running via `dapr init`).
- **FR-005**: Dapr Bindings (cron) building block MUST trigger the reminder scheduler on a configurable interval.
- **FR-006**: Dapr Secrets building block MUST supply JWT secret and database URL to the backend from Kubernetes Secrets.
- **FR-007**: Dapr Service Invocation MUST be used for any inter-service calls within the cluster (mTLS by default).
- **FR-008**: All five Dapr building blocks MUST be verified healthy via `dapr dashboard` or `kubectl get components`.

**Part C — Oracle OKE (Cloud)**

- **FR-009**: An OKE cluster MUST be provisioned using Oracle Cloud Always Free tier (or low-cost ARM nodes).
- **FR-010**: Dapr MUST be installed on OKE using `dapr init --kubernetes`.
- **FR-011**: Kafka MUST run as an in-cluster deployment on OKE (same Helm-managed Zookeeper + Kafka, or replaced with a lightweight alternative if resource-constrained).
- **FR-012**: All five Dapr building blocks MUST be active on OKE with the same configuration as Minikube.
- **FR-013**: The application MUST be accessible via an OKE Load Balancer or NodePort with a public IP.
- **FR-014**: Secrets MUST be stored in Kubernetes Secrets on OKE (or OCI Vault if available) and accessed via Dapr Secrets building block.

**CI/CD**

- **FR-015**: A GitHub Actions workflow MUST build and push Docker images to a container registry on every push to `main`.
- **FR-016**: The workflow MUST deploy to OKE via `helm upgrade --install` after a successful image build.
- **FR-017**: The workflow MUST use GitHub Actions Secrets for all credentials (OCI kubeconfig, registry credentials).
- **FR-018**: The workflow MUST fail fast and block the deploy job if the build or tests fail.

**Monitoring & Logging**

- **FR-019**: Application logs MUST be aggregated and searchable (Kubernetes-native: `kubectl logs` + optional log forwarding).
- **FR-020**: Pod health metrics MUST be visible via a monitoring solution compatible with OKE (Prometheus + Grafana, or OCI Monitoring).
- **FR-021**: Dapr sidecar metrics MUST be exposed and scraped by the monitoring stack.

### Security Requirements

- **SR-001**: No credentials, tokens, or secrets MUST be hardcoded in Helm values, Dockerfiles, or GitHub Actions workflow files.
- **SR-002**: All secrets MUST be injected at runtime via Dapr Secrets building block or Kubernetes Secret refs.
- **SR-003**: Dapr mTLS MUST be enabled between all services (default when Dapr is installed on K8s).
- **SR-004**: The OKE cluster MUST NOT expose the Kubernetes API server publicly (use kubeconfig via GitHub Actions Secret).
- **SR-005**: Container images MUST run as non-root users.

### Key Entities

- **Dapr Component**: A YAML manifest declaring a building block (pubsub, state, binding, secretstore, serviceInvocation config) scoped to a Kubernetes namespace.
- **OKE Cluster**: Oracle-managed Kubernetes control plane with worker node pool (ARM or AMD, Always Free eligible).
- **GitHub Actions Workflow**: YAML pipeline file in `.github/workflows/` that builds, tests, and deploys on push to `main`.
- **Helm Release**: A named Helm deployment (`todo-chatbot`) applied to a Kubernetes namespace, parameterized via `values.yaml` and `--set` overrides.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All five Dapr building blocks (Pub/Sub, State, Bindings/Cron, Secrets, Service Invocation) report `Running` status on both Minikube and OKE after deployment.
- **SC-002**: A task creation on the deployed app results in a Kafka event verifiable within 5 seconds.
- **SC-003**: A push to `main` triggers a full CI/CD pipeline run that completes deployment to OKE within 15 minutes.
- **SC-004**: Zero secrets appear in plaintext in any Git-tracked file, workflow log, or Helm chart value.
- **SC-005**: The application frontend is reachable via public URL on OKE within 5 minutes of deployment completion.
- **SC-006**: Pod logs for the last 24 hours are retrievable via the monitoring stack with a single query.
- **SC-007**: Rolling deployments via CI/CD result in zero downtime (new pods healthy before old pods terminate).

---

## Assumptions

- Oracle Cloud Always Free tier is available to the user (2 AMD micro VMs or ARM Ampere nodes).
- Dapr version: 1.17.x (already installed locally — same version used on Minikube/OKE).
- Kafka: In-cluster deployment using `confluentinc/cp-kafka:7.6.0` (already in the Helm chart). If OKE resources are insufficient, Redpanda or a lightweight alternative may be used.
- Container registry: GitHub Container Registry (GHCR) is used for CI/CD image storage (free for public repos, included with GitHub).
- Monitoring: Prometheus + Grafana via `kube-prometheus-stack` Helm chart (simplest OKE-compatible option). OCI Monitoring is out of scope unless required.
- The existing Helm chart (`todo-chatbot/`) is the single deployment artifact — no new chart is created.
- Oracle Cloud CLI (`oci`) and `kubectl` configured locally for initial OKE provisioning; subsequent deploys are fully automated via GitHub Actions.

---

## Out of Scope

- Azure AKS, Google GKE, or any non-Oracle cloud provider.
- Confluent Cloud, Redpanda Cloud, or any external managed Kafka (in-cluster Kafka is used unless explicitly changed).
- Custom Dapr components beyond the five building blocks listed.
- Multi-region or multi-cluster deployments.
- Database migration to Oracle (Neon PostgreSQL remains the database).
- Mobile or desktop application changes.
