---
id: "0003"
title: Advanced Features Dapr Kafka Task Breakdown
stage: tasks
date: 2026-03-31
surface: agent
model: claude-sonnet-4-6
feature: 005-advanced-features-dapr-kafka
branch: 005-advanced-features-dapr-kafka
user: hassanjhr
command: /sp.tasks
labels: ["tasks", "advanced-features", "kafka", "dapr", "priorities", "tags", "search", "recurring-tasks", "due-dates", "reminders"]
links:
  spec: specs/005-advanced-features-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-advanced-features-dapr-kafka/tasks.md
tests:
  - Format validation: all 84 tasks follow [checkbox][ID][P?][Story?][description with path] format
  - All user stories have Independent Test criteria defined
  - Phase dependency order verified (US3 after US2, US4 after US1)
---

## Prompt

now you can generate tasks based on th planning.

## Response snapshot

Generated `specs/005-advanced-features-dapr-kafka/tasks.md` with 84 tasks across 9 phases:

- **Phase 1** (T001–T006, 6 tasks): Setup — dependencies, Dapr dirs, Kafka compose, .env.example
- **Phase 2** (T007–T020, 14 tasks): Foundational — 5 DB migrations + 6 SQLModel models + event_publisher stub
- **Phase 3** (T021–T035, 15 tasks): US1 P1 — Priorities & Tags (backend schemas, tags CRUD route, extended task routes, frontend types/API/UI)
- **Phase 4** (T036–T042, 7 tasks): US4 P2 — Search/Filter/Sort + cursor pagination
- **Phase 5** (T043–T054, 12 tasks): US2 P2 — Due Dates, Reminders, APScheduler
- **Phase 6** (T055–T066, 12 tasks): US3 P3 — Recurring Tasks (recurrence service, bulk update/delete, RecurrenceForm UI)
- **Phase 7** (T067–T071, 5 tasks): US5 P4 — Kafka event publisher (full), Dapr pubsub component
- **Phase 8** (T072–T077, 6 tasks): US6 P4 — Dapr secrets integration, K8s Helm chart Dapr annotations
- **Phase 9** (T078–T084, 7 tasks): Polish — security review, tag sanitization, event PII check, gitignore, e2e validation

Agent assignments: neon-db-manager (Phase 2), fastapi-backend-dev (Phases 3–8 backend), nextjs-ui-builder (Phases 3–6 frontend), auth-security-handler (Phase 9)

## Outcome

- ✅ Impact: 84 atomized tasks covering all 29 FRs from spec; organized by user story for independent delivery
- 🧪 Tests: Not generated (not requested in spec); Independent Test criteria defined per story
- 📁 Files: specs/005-advanced-features-dapr-kafka/tasks.md
- 🔁 Next prompts: `/sp.implement` to execute tasks, `/sp.adr kafka-dapr-distributed-runtime` to document architecture decision
- 🧠 Reflection: US4 (Search) depends on US1 (tags/priority) so Phase 4 correctly follows Phase 3. US3 (Recurring) depends on US2 (due_date) for next-occurrence scheduling, so Phase 6 follows Phase 5. US5+US6 (Dapr/Kafka) are P4 infrastructure concerns that build on all prior phases.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.sh has CRLF issue (same pattern as other scripts); worked fully with agent-native tools
- Graders run and results (PASS/FAIL): Format validation PASS — all 84 tasks follow required checklist format; phase dependency graph verified
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Fix CRLF in all .specify/scripts/bash/*.sh files using `sed -i 's/\r//' *.sh`
