# Data Model: Advanced Task Management with Distributed Architecture

**Feature**: 005-advanced-features-dapr-kafka
**Date**: 2026-03-31
**Database**: Neon Serverless PostgreSQL

---

## Entity Relationship Overview

```
users (existing)
  │
  ├─── tasks (extended)
  │      ├── priority: enum(high, medium, low)  [NEW]
  │      ├── due_date: timestamptz               [NEW]
  │      ├── recurrence_rule: text               [NEW]
  │      ├── series_id: uuid FK recurrence_series[NEW]
  │      ├── is_paused: boolean                  [NEW]
  │      └── parent_task_id: uuid FK tasks       [NEW]
  │
  ├─── reminders (NEW)
  │      ├── task_id FK tasks
  │      ├── offset_minutes: int
  │      ├── trigger_at: timestamptz
  │      └── status: enum(pending, sent, cancelled)
  │
  ├─── tags (NEW)
  │      └── name, color (user-scoped)
  │
  ├─── task_tags (NEW junction)
  │      ├── task_id FK tasks
  │      └── tag_id FK tags
  │
  └─── recurrence_series (NEW)
         ├── recurrence_rule: text (RRULE)
         └── original_task_id FK tasks
```

---

## 1. `tasks` Table — Extended

Extends the existing tasks table with new columns. No breaking changes to existing columns.

### New Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `priority` | `VARCHAR(10)` | NOT NULL | `'medium'` | Task priority: `high`, `medium`, `low` |
| `due_date` | `TIMESTAMPTZ` | NULL | — | Optional due date and time (UTC) |
| `recurrence_rule` | `TEXT` | NULL | — | RFC 5545 RRULE string (e.g., `FREQ=DAILY`) |
| `series_id` | `UUID` | NULL | — | FK → `recurrence_series.id`; groups recurring instances |
| `parent_task_id` | `UUID` | NULL | — | FK → `tasks.id`; self-ref for recurring instance chain |
| `is_paused` | `BOOLEAN` | NOT NULL | `false` | Pauses recurrence spawning without deletion |

### Constraints & Indexes (new)

```sql
-- Priority check constraint
ALTER TABLE tasks ADD CONSTRAINT chk_priority
  CHECK (priority IN ('high', 'medium', 'low'));

-- Indexes for filter/sort operations
CREATE INDEX idx_task_priority ON tasks(user_id, priority);
CREATE INDEX idx_task_due_date ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_task_series ON tasks(series_id) WHERE series_id IS NOT NULL;

-- Full-text search (pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_task_search_gin
  ON tasks USING GIN ((title || ' ' || COALESCE(description, '')) gin_trgm_ops);

-- Composite cursor index for pagination
CREATE INDEX idx_task_cursor ON tasks(user_id, created_at DESC, id DESC);
```

### Migration: `003_extend_tasks_table.sql`

```sql
ALTER TABLE tasks
  ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium',
  ADD COLUMN due_date TIMESTAMPTZ,
  ADD COLUMN recurrence_rule TEXT,
  ADD COLUMN series_id UUID,
  ADD COLUMN parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  ADD COLUMN is_paused BOOLEAN NOT NULL DEFAULT false;

ALTER TABLE tasks ADD CONSTRAINT chk_priority
  CHECK (priority IN ('high', 'medium', 'low'));
```

---

## 2. `reminders` Table — New

Stores scheduled reminder offsets for tasks. Multiple reminders per task are supported.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NOT NULL | `uuid_generate_v4()` | PK |
| `task_id` | `UUID` | NOT NULL | — | FK → `tasks.id` ON DELETE CASCADE |
| `user_id` | `UUID` | NOT NULL | — | FK → `users.id` ON DELETE CASCADE (denormalized for fast queries) |
| `offset_minutes` | `INTEGER` | NOT NULL | — | Minutes before due date (e.g., 60 = 1 hour before) |
| `trigger_at` | `TIMESTAMPTZ` | NOT NULL | — | Absolute timestamp when reminder fires (`due_date - offset`) |
| `status` | `VARCHAR(20)` | NOT NULL | `'pending'` | `pending`, `sent`, `cancelled` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Creation timestamp |

### Constraints

```sql
CREATE TABLE reminders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  offset_minutes INTEGER NOT NULL CHECK (offset_minutes > 0),
  trigger_at TIMESTAMPTZ NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'sent', 'cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reminder_trigger ON reminders(trigger_at) WHERE status = 'pending';
CREATE INDEX idx_reminder_task ON reminders(task_id);
CREATE INDEX idx_reminder_user ON reminders(user_id);
```

### Migration: `004_create_reminders_table.sql`

---

## 3. `tags` Table — New

User-scoped tag definitions. Each user has their own tag namespace.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NOT NULL | `uuid_generate_v4()` | PK |
| `user_id` | `UUID` | NOT NULL | — | FK → `users.id` ON DELETE CASCADE |
| `name` | `VARCHAR(50)` | NOT NULL | — | Tag label (alphanumeric + hyphens) |
| `color` | `VARCHAR(7)` | NULL | — | Hex color code (e.g., `#FF5733`) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Creation timestamp |

### Constraints

```sql
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL CHECK (name ~ '^[a-zA-Z0-9\-]+$'),
  color VARCHAR(7),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, name)  -- No duplicate tag names per user
);

CREATE INDEX idx_tag_user_name ON tags(user_id, name);
```

### Migration: `005_create_tags_table.sql`

---

## 4. `task_tags` Table — New (Junction)

Many-to-many join between tasks and tags.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `task_id` | `UUID` | NOT NULL | FK → `tasks.id` ON DELETE CASCADE |
| `tag_id` | `UUID` | NOT NULL | FK → `tags.id` ON DELETE CASCADE |
| `added_at` | `TIMESTAMPTZ` | NOT NULL | When tag was applied to task |

### Constraints

```sql
CREATE TABLE task_tags (
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
CREATE INDEX idx_task_tags_task ON task_tags(task_id);
```

### Migration: `006_create_task_tags_table.sql`

---

## 5. `recurrence_series` Table — New

Groups recurring task instances under a common series. Enables bulk edits and deletes of future occurrences.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NOT NULL | `uuid_generate_v4()` | PK, referenced by `tasks.series_id` |
| `user_id` | `UUID` | NOT NULL | — | FK → `users.id` ON DELETE CASCADE |
| `original_task_id` | `UUID` | NOT NULL | — | FK → `tasks.id` — the first task in the series |
| `recurrence_rule` | `TEXT` | NOT NULL | — | RFC 5545 RRULE string (authoritative copy) |
| `base_title` | `VARCHAR(200)` | NOT NULL | — | Title used for all generated instances |
| `base_description` | `TEXT` | NULL | — | Description used for all generated instances |
| `base_priority` | `VARCHAR(10)` | NOT NULL | `'medium'` | Priority copied to all instances |
| `is_active` | `BOOLEAN` | NOT NULL | `true` | False when series is globally paused or ended |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | When series was created |

### Constraints

```sql
CREATE TABLE recurrence_series (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  original_task_id UUID NOT NULL REFERENCES tasks(id),
  recurrence_rule TEXT NOT NULL,
  base_title VARCHAR(200) NOT NULL,
  base_description TEXT,
  base_priority VARCHAR(10) NOT NULL DEFAULT 'medium'
    CHECK (base_priority IN ('high', 'medium', 'low')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_series_user ON recurrence_series(user_id);
```

### Migration: `007_create_recurrence_series_table.sql`

---

## 6. TaskEvent Schema (Kafka — Not a DB Table)

Events published to Kafka via Dapr pubsub. Follows CloudEvents 1.0 envelope.

```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "<correlation-uuid>",
  "time": "2026-03-31T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task.created",
    "task_id": "<uuid>",
    "user_id": "<uuid>",
    "title": "Buy groceries",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-04-01T09:00:00Z",
    "is_completed": false,
    "timestamp": "2026-03-31T12:00:00Z"
  }
}
```

**Event types**: `task.created`, `task.updated`, `task.completed`, `task.deleted`, `task.reminder`

**Topics**:
- `tasks` → lifecycle events
- `reminders` → reminder trigger events
- `tasks-dlq` → dead-letter queue

---

## SQLModel Python Models Summary

| Model Class | Table | Status |
|-------------|-------|--------|
| `User` | `users` | Existing — no changes |
| `Task` | `tasks` | Existing — ADD new columns via migration |
| `Reminder` | `reminders` | New |
| `Tag` | `tags` | New |
| `TaskTag` | `task_tags` | New (junction) |
| `RecurrenceSeries` | `recurrence_series` | New |

---

## State Transitions

### Task Priority
```
(none) → medium  [default on create]
medium ↔ high ↔ low  [user can change at any time]
```

### Reminder Status
```
pending → sent      [scheduler fires, Dapr event published]
pending → cancelled [task completed or deleted]
```

### Recurrence Series
```
is_active: true → false  [user pauses series or deletes all future]
```
