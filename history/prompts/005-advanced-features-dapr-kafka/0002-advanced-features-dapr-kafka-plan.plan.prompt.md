---
id: "0002"
title: Advanced Features Dapr Kafka Implementation Plan
stage: plan
date: 2026-03-31
surface: agent
model: claude-sonnet-4-6
feature: 005-advanced-features-dapr-kafka
branch: 005-advanced-features-dapr-kafka
user: hassanjhr
command: /sp.plan
labels: ["plan", "advanced-features", "kafka", "dapr", "priorities", "tags", "search", "recurring-tasks", "due-dates", "reminders", "architecture"]
links:
  spec: specs/005-advanced-features-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-advanced-features-dapr-kafka/plan.md
  - specs/005-advanced-features-dapr-kafka/research.md
  - specs/005-advanced-features-dapr-kafka/data-model.md
  - specs/005-advanced-features-dapr-kafka/contracts/tasks-v2-api.md
  - specs/005-advanced-features-dapr-kafka/quickstart.md
tests:
  - Constitution Check — all 6 principles pass (I through VI)
---

## Prompt

now you can generate plan based on the spec.

## Response snapshot

Generated full implementation plan for `005-advanced-features-dapr-kafka` including:

**Phase 0 (Research — research.md)**:
- 8 architectural decisions resolved: tags (junction table), search (pg_trgm + GIN), RRULE (python-dateutil), scheduler (APScheduler), pagination (cursor), Dapr pubsub (Kafka), service invocation (Dapr HTTP), secrets (K8s Secrets via Dapr)

**Phase 1 (Design — data-model.md, contracts/, quickstart.md)**:
- 5 new DB entities: `tasks` (extended), `reminders`, `tags`, `task_tags`, `recurrence_series`
- 5 new migration files: 003–007
- Full API contract: GET/POST/PATCH/DELETE tasks v2, reminders CRUD, tags CRUD, Dapr event schema
- Quickstart: Dapr CLI setup, Kafka Docker Compose, local dev commands, K8s deployment steps

**plan.md** contains:
- Technical context (Python 3.11+, Dapr 1.13+, Kafka, APScheduler, python-dateutil)
- Constitution Check ✅ (all 6 principles pass)
- 7-phase implementation breakdown with agent assignments
- Dependency ordering (DB → Backend → Recurrence → Events → Auth → Frontend → Infra)
- Risks & mitigations table
- Full project source structure layout

## Outcome

- ✅ Impact: Complete architectural plan covering 29 FRs across 7 implementation phases
- 🧪 Tests: Constitution Check — all 6 principles PASS; no gate violations
- 📁 Files: plan.md, research.md, data-model.md, contracts/tasks-v2-api.md, quickstart.md
- 🔁 Next prompts: `/sp.tasks` to generate atomized task breakdown, `/sp.adr kafka-dapr-distributed-runtime` to document architecture decision
- 🧠 Reflection: Dapr is introduced as optional (DAPR_ENABLED flag) to maintain local dev ergonomics while enabling full distributed architecture in K8s. APScheduler chosen over Celery to avoid external broker dependency for reminder polling MVP.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.sh CRLF issue (same as before); all artifacts created via agent-native tools
- Graders run and results (PASS/FAIL): Constitution Check — PASS (all 6 principles)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Fix CRLF in .specify scripts to unblock shell-based setup
