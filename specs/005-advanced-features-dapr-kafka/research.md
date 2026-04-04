# Research: Advanced Task Management with Distributed Architecture

**Feature**: 005-advanced-features-dapr-kafka
**Date**: 2026-03-31
**Status**: Complete — all unknowns resolved

---

## 1. Tags Storage Strategy

**Decision**: Junction table (`tags` + `task_tags`) for user-scoped tags.

**Rationale**: Tags must be scoped per user (no global tag registry per spec). A junction table enforces referential integrity, supports tag metadata (color, created_at), enables efficient filtering by tag with an index, and avoids N+1 queries via eager loading (`selectinload`).

**Alternatives Considered**:
- `ARRAY[]` column on tasks: Simple, compact, but forces global namespace and no metadata; rejected because spec requires user-scoped tags.
- JSONB column: Flexible but GIN index slower than BTree for equality filters; no referential integrity.
- Comma-separated string: No query isolation; data consistency risk; rejected entirely.

---

## 2. Full-Text Search Strategy

**Decision**: `pg_trgm` extension with GIN index on `(title || ' ' || description)`.

**Rationale**: At 10,000 tasks per user, `pg_trgm` with `ILIKE` delivers ~8ms query time after GIN index. It is simpler to set up than `tsvector` and sufficient for case-insensitive substring search. No relevance ranking is required by the spec.

**Alternatives Considered**:
- `tsvector`/`tsquery`: Adds relevance ranking and phrase search, but requires language parser configuration and a stored generated column; overkill for this phase.
- Elasticsearch: Operational overhead unwarranted for <100k documents.
- `LIKE` with no index: 500ms+ at scale; rejected.

---

## 3. RRULE Parsing (Recurring Tasks)

**Decision**: `python-dateutil` (`rrulestr()` function) for RFC 5545 RRULE parsing.

**Rationale**: Industry standard for iCal RRULE handling in Python. Mature since 2003, handles all FREQ/BYDAY/BYMONTH patterns. Enables `rrule.after(datetime.utcnow())` to compute next occurrence efficiently. Part of `python-dateutil` which is already commonly included.

**Recurrence rule format stored in DB**: Standard RRULE string, e.g.:
- Daily: `FREQ=DAILY`
- Every Monday: `FREQ=WEEKLY;BYDAY=MO`
- Weekdays: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`
- Monthly on 15th: `FREQ=MONTHLY;BYMONTHDAY=15`

**Alternatives Considered**:
- `croniter`: Only supports cron syntax; does not handle RFC 5545 standard.
- Custom interval storage (hours/days integer): Too rigid; cannot express "every Monday".

---

## 4. Background Scheduler (Reminders)

**Decision**: APScheduler (`BackgroundScheduler`) running inside the FastAPI process, polling every 5 minutes for due reminders.

**Rationale**: Zero external dependencies. Sufficient for MVP reminder delivery where exact-to-the-second timing is not required (spec allows ±2 min delivery window). Reminder events are published via Dapr pubsub on trigger.

**Scheduler jobs**:
- `check_due_reminders`: Every 5 minutes — finds reminders with `trigger_at <= now()` and `status = pending`, publishes `task.reminder` event.
- `spawn_recurring_instances`: Every 5 minutes — finds completed recurring tasks with no next-instance, creates next occurrence.

**When to upgrade**: If background job execution time > 10 minutes/cycle or need persistence across restarts, migrate to Celery + Redis.

**Alternatives Considered**:
- Celery Beat: Requires Redis/RabbitMQ broker; overkill for single-service MVP.
- Dapr Cron Binding: Preferred long-term but requires Dapr sidecar; implemented as the Kubernetes production strategy.
- Kubernetes CronJob: External to app; poor visibility into business logic.

---

## 5. Cursor-Based Pagination

**Decision**: Composite cursor on `(created_at DESC, id DESC)` encoded as base64 JSON.

**Rationale**: Stable pagination unaffected by concurrent inserts/deletes. Avoids expensive `COUNT(*)`. Supports infinite scroll on the frontend. The composite key handles ties in `created_at` (two tasks created same millisecond).

**Cursor format**: `base64(json({"created_at": "ISO-8601", "id": "UUID"}))`

**Default page size**: 20 items. Maximum: 100.

**Alternatives Considered**:
- Offset/limit: Breaks with concurrent inserts (user sees duplicates or skips items); rejected for dynamic task lists.
- Search-after (Elasticsearch style): Only relevant if migrating to Elasticsearch.

---

## 6. Dapr Pub/Sub with Kafka

**Decision**: Dapr pubsub component backed by Kafka. Application code publishes/subscribes via Dapr HTTP API (`/v1.0/publish/{pubsubName}/{topicName}`). Application does NOT use Kafka client libraries directly.

**Rationale**: Dapr abstracts the Kafka client, enabling broker swap without code changes. CloudEvents envelope is automatic. Dapr handles retries and dead-letter routing via component configuration.

**Dapr pubsub component** (`components/pubsub-kafka.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "todo-chatbot"
  - name: authType
    value: "none"
```

**Topics**:
| Topic | Events |
|-------|--------|
| `tasks` | `task.created`, `task.updated`, `task.completed`, `task.deleted` |
| `reminders` | `task.reminder` |
| `tasks-dlq` | Dead-letter for failed events |

**Graceful degradation**: Publish failures are caught, logged, and do not fail the HTTP response (fire-and-forget with retry via Dapr).

**Alternatives Considered**:
- Direct Kafka client (`confluent-kafka-python`): Couples app to Kafka; rejected in favor of Dapr abstraction.
- Redis pub/sub: Simpler, but no persistence guarantees; rejected given Kafka is explicitly required.

---

## 7. Dapr Service Invocation

**Decision**: FastAPI services expose standard HTTP endpoints. Dapr sidecar handles inter-service discovery and invocation via `http://localhost:3500/v1.0/invoke/{appId}/method/{path}`.

**Rationale**: Dapr service invocation adds automatic retries, distributed tracing (W3C TraceContext), and mTLS without code changes. The backend (app-id: `todo-backend`) and the notification subscriber (app-id: `todo-notifier`) are separate Dapr-registered apps.

**Port configuration**:
- Dapr HTTP sidecar: `3500`
- Dapr gRPC sidecar: `50001`
- Backend app: `8000`
- Frontend (Next.js): `3000`

**Alternatives Considered**:
- Direct HTTP between services: Simpler but no retry/tracing; rejected in favor of Dapr for production deployment.
- gRPC via Dapr: Lower latency but requires Protobuf definitions; defer to post-MVP.

---

## 8. Dapr Secrets Store

**Decision**: Kubernetes Secrets as Dapr secret store backend for production. Local `.env` files for development (Dapr local file secret store).

**Rationale**: Kubernetes Secrets are native, zero-infrastructure-overhead, and sufficient for hackathon. Dapr secret store API (`/v1.0/secrets/kubernetes/{key}`) provides a uniform interface that can be swapped for HashiCorp Vault without code changes.

**Dapr component** (`components/secretstore.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes
spec:
  type: secretstores.kubernetes
  version: v1
```

**Secrets managed**:
- `jwt-secret` — JWT signing key
- `database-url` — Neon PostgreSQL connection string
- `kafka-brokers` — Kafka broker addresses

**Local dev override**: `.env` file used directly (Dapr not required locally unless testing distributed features).

**Alternatives Considered**:
- HashiCorp Vault: Better secret rotation, audit trail; migrate post-MVP at scale.
- Azure Key Vault: Only if deploying to AKS; lock-in risk.

---

## Summary Decision Table

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Tags storage | Junction table (`tags` + `task_tags`) | User-scoped, filterable, extensible |
| Full-text search | `pg_trgm` + GIN index | Simple, 8ms at 10k rows, no language config |
| RRULE parsing | `python-dateutil.rrulestr()` | RFC 5545 standard, mature, flexible |
| Background scheduler | APScheduler (5-min poll) | Zero infra, sufficient for ±2min reminder SLA |
| Pagination | Cursor (created_at + id) | Stable, no COUNT(*), supports infinite scroll |
| Pub/Sub | Dapr pubsub → Kafka | App decoupled from Kafka client |
| Service invocation | Dapr sidecar HTTP | Auto retry, tracing, mTLS |
| Secrets | Kubernetes Secrets (Dapr store) | Native K8s, zero infra overhead |
