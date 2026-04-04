---
id: "0004"
title: Phase 2 Migrations Models Event Publisher
stage: green
date: 2026-03-31
surface: agent
model: claude-sonnet-4-6
feature: 005-advanced-features-dapr-kafka
branch: 005-advanced-features-dapr-kafka
user: hassanjhr
command: sp.implement
labels: ["database", "migrations", "sqlmodel", "dapr", "kafka", "event-publisher"]
links:
  spec: specs/005-advanced-features-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/migrations/003_extend_tasks_table.sql
  - backend/migrations/004_create_reminders_table.sql
  - backend/migrations/005_create_tags_table.sql
  - backend/migrations/006_create_task_tags_table.sql
  - backend/migrations/007_create_recurrence_series_table.sql
  - backend/src/models/task.py
  - backend/src/models/reminder.py
  - backend/src/models/tag.py
  - backend/src/models/task_tag.py
  - backend/src/models/recurrence_series.py
  - backend/src/models/__init__.py
  - backend/src/main.py
  - backend/src/services/__init__.py
  - backend/src/services/event_publisher.py
tests:
  - none
---

## Prompt

You are implementing Phase 2 of feature 005-advanced-features-dapr-kafka for a FastAPI + SQLModel + Neon PostgreSQL project.

**Repository root**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_5`

## Your job: Create 5 SQL migration files + 5 new SQLModel model files + update existing files.

Tasks T007–T020 covering:
- T007: backend/migrations/003_extend_tasks_table.sql — pg_trgm, 6 new columns (priority, due_date, recurrence_rule, series_id, parent_task_id, is_paused), constraints, GIN + composite indexes
- T008: backend/migrations/004_create_reminders_table.sql — reminders table with partial index on pending status
- T009: backend/migrations/005_create_tags_table.sql — user-scoped tags with UNIQUE(user_id, name)
- T010: backend/migrations/006_create_task_tags_table.sql — many-to-many junction table
- T011: backend/migrations/007_create_recurrence_series_table.sql — recurrence series with RRULE storage
- T013: Extend backend/src/models/task.py — add 6 advanced feature fields after updated_at
- T014: Create backend/src/models/reminder.py
- T015: Create backend/src/models/tag.py
- T016: Create backend/src/models/task_tag.py
- T017: Create backend/src/models/recurrence_series.py
- T018: Update backend/src/models/__init__.py — add 4 new model exports
- T019: Create backend/src/services/event_publisher.py — Dapr pub/sub with CloudEvents 1.0, 3-retry + DLQ, graceful no-op when DAPR_ENABLED=false
- T020: Update backend/src/main.py — import 4 new models so SQLModel metadata registers them

## Response snapshot

All 14 files created or updated successfully:

**5 SQL migrations** written to backend/migrations/ (003–007), covering: pg_trgm extension, tasks table ALTER with 6 columns and chk_priority constraint, 4 GIN/composite/partial indexes; reminders table with partial index on pending status; user-scoped tags table with UNIQUE constraint; task_tags junction table with composite PK; recurrence_series table.

**5 new SQLModel models** created in backend/src/models/: Reminder, Tag, TaskTag, RecurrenceSeries — all with extend_existing=True and proper FK references.

**Task model extended** — 6 new fields appended after updated_at, no existing fields modified. `Optional` import was already present.

**models/__init__.py** updated — 4 new classes exported in __all__.

**services/ package created** — backend/src/services/__init__.py + event_publisher.py with publish_task_event (3-retry, DLQ fallback, DAPR_ENABLED guard) and publish_reminder_event helpers.

**main.py updated** — 4 new model imports added after existing router imports so SQLModel create_all registers all tables.

## Outcome

- Impact: Phase 2 database layer complete — all schema objects, SQLModel entities, and Dapr event publishing infrastructure in place for advanced features (priority, due dates, recurrence, reminders, tags, Kafka events)
- Tests: none run (migrations require live DB credentials; unit tests out of scope for this task)
- Files: 14 files created/modified (5 migrations, 5 new models, 2 updated existing files, 2 new service files)
- Next prompts: T021+ — API route extensions for priority/due_date filtering, reminder CRUD, tag CRUD, recurrence series management, APScheduler polling job
- Reflection: Ordering matters — RecurrenceSeries must be imported before Task references series_id FK, handled correctly by SQLModel's lazy FK resolution via string references

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add validator on Task.priority to enforce enum values at Pydantic layer in addition to DB CHECK constraint
