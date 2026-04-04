---
id: "0006"
title: "T012 T084 Migrations and E2E Validation"
stage: green
date: 2026-04-02
surface: agent
model: claude-sonnet-4-6
feature: 005-advanced-features-dapr-kafka
branch: 005-advanced-features-dapr-kafka
user: hassanjhr
command: continue remaining tasks
labels: ["migrations", "validation", "smoke-test", "bugfix", "timezone", "reminders", "due_date"]
links:
  spec: specs/005-advanced-features-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/routes/tasks.py
  - backend/src/api/routes/reminders.py
  - backend/src/services/reminder_service.py
tests:
  - "Smoke test suite: 22/22 passed (health, auth, priority CRUD, tag filter, search, reminder, overdue, recurrence, event publisher, sort, default priority, OpenAPI docs)"
---

## Prompt

now continue with complete the all tasks remaining

## Response snapshot

Completed the 2 remaining tasks:

**T012** — Ran `backend/scripts/run_migrations.py` against Neon DB. All 5 migrations (003–007) confirmed applied. Schema verified: 10 tables, 28 indexes.

**T084** — End-to-end validation. Backend started without Dapr (`DAPR_ENABLED=false`). Discovered and fixed 3 timezone bugs before final 22/22 smoke test pass.

Bugs fixed:
1. `tasks.py:319` — `due_date` from Pydantic is tz-aware; DB column is `TIMESTAMP WITHOUT TIME ZONE`. Fix: `due_date.replace(tzinfo=None)` before INSERT.
2. `tasks.py:113` — `_to_task_response` used `datetime.utcnow()` (naive) to compare with `task.due_date` from DB (tz-aware TIMESTAMPTZ). Fix: use `datetime.now(timezone.utc)` and normalize `due_date` to tz-aware for comparison.
3. `reminders.py:60` — `trigger_at` computed from `task.due_date` (tz-aware) inserted into `TIMESTAMP WITHOUT TIME ZONE` column. Fix: `due_naive = task.due_date.replace(tzinfo=None)`.

Dapr/Kafka not validated live (Docker/Dapr CLI not in WSL env); event publisher verified to degrade gracefully.

## Outcome

- ✅ Impact: T012 and T084 complete; all 84 tasks in 005 feature now done; 3 timezone bugs fixed in production code
- 🧪 Tests: 22/22 smoke tests passing end-to-end against live Neon DB
- 📁 Files: tasks.py, reminders.py, reminder_service.py patched; tasks.md T012/T084 marked complete
- 🔁 Next prompts: Create PR for branch 005-advanced-features-dapr-kafka; Docker/Dapr live Kafka validation when Docker Desktop WSL integration enabled
- 🧠 Reflection: SQLModel maps all `datetime` fields as `TIMESTAMP WITHOUT TIME ZONE` regardless of DB schema TIMESTAMPTZ — consistently use UTC-naive datetimes in Python when storing, and UTC-aware only for comparisons

## Evaluation notes (flywheel)

- Failure modes observed: Timezone mixin between SQLModel (naive) and PostgreSQL TIMESTAMPTZ (aware) caused 3 separate 500 errors; pip install slow on Windows FS (/mnt/e/) — solved by venv on Linux FS
- Graders run and results (PASS/FAIL): Smoke test suite — 22 PASS, 0 FAIL
- Prompt variant (if applicable): none
- Next experiment: Add `sa_column=Column(TIMESTAMP(timezone=True))` to all datetime fields in SQLModel to match TIMESTAMPTZ DB columns
