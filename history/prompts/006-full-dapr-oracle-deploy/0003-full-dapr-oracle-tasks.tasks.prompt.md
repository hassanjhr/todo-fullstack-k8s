---
id: "0003"
title: "Full Dapr Oracle Deploy Tasks"
stage: tasks
date: "2026-04-06"
surface: agent
model: claude-sonnet-4-6
feature: "006-full-dapr-oracle-deploy"
branch: "006-full-dapr-oracle-deploy"
user: hassanjhr
command: "/sp.tasks"
labels: ["dapr", "oracle-oke", "minikube", "kafka", "github-actions", "monitoring", "tasks"]
links:
  spec: "specs/006-full-dapr-oracle-deploy/spec.md"
  plan: "specs/006-full-dapr-oracle-deploy/plan.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/006-full-dapr-oracle-deploy/tasks.md
tests: []
---

## Prompt

```text
/sp.tasks
```

## Response

Generated `tasks.md` for `006-full-dapr-oracle-deploy` with **56 tasks** across 7 phases:

- **Phase 1** (T001–T006): Setup — local Dapr component YAMLs, directory structure
- **Phase 2** (T007–T019): Foundational — backend cron handler, Helm chart Dapr components (statestore + cron binding), frontend Dapr service invocation wiring
- **Phase 3** (T020–T025): US1 Minikube — verify all 5 Dapr building blocks, verification script
- **Phase 4** (T026–T033): US2 Oracle OKE — LoadBalancer service, GHCR image repos, OKE provisioning guide
- **Phase 5** (T034–T040): US3 CI/CD — GitHub Actions `deploy.yml` + `ci.yml`, docs
- **Phase 6** (T041–T046): US4 Monitoring — kube-prometheus-stack config, Dapr metrics scrape, alert rules
- **Phase 7** (T047–T056): Polish — idempotent reminder service, .gitignore, README, E2E verification

MVP scope: Phases 1–3 (US1 Minikube, all 5 Dapr building blocks).
