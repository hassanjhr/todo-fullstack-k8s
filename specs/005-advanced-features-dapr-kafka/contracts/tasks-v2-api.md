# API Contract: Advanced Task Management v2

**Feature**: 005-advanced-features-dapr-kafka
**Date**: 2026-03-31
**Base Path**: `/api/{user_id}`
**Auth**: All endpoints require `Authorization: Bearer <JWT>` header

---

## Common Types

### TaskPriority
`"high" | "medium" | "low"`

### TaskStatus Filter
`"all" | "completed" | "pending" | "overdue"`

### DueDateFilter
`"today" | "this_week" | "overdue" | "custom"`

### SortField
`"created_at" | "due_date" | "priority" | "title"`

### SortOrder
`"asc" | "desc"`

### PaginatedTaskResponse
```json
{
  "tasks": [TaskResponse],
  "next_cursor": "string | null",
  "has_more": "boolean",
  "total_count": "integer (approximate)"
}
```

### TaskResponse (Extended)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string | null",
  "is_completed": "boolean",
  "priority": "high | medium | low",
  "tags": ["string"],
  "due_date": "ISO-8601 datetime | null",
  "is_overdue": "boolean",
  "recurrence_rule": "RRULE string | null",
  "series_id": "uuid | null",
  "is_paused": "boolean",
  "next_due_date": "ISO-8601 datetime | null",
  "reminders": [ReminderResponse],
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime"
}
```

### ReminderResponse
```json
{
  "id": "uuid",
  "offset_minutes": "integer",
  "trigger_at": "ISO-8601 datetime",
  "status": "pending | sent | cancelled"
}
```

---

## Task Endpoints

### GET `/api/{user_id}/tasks`
Retrieve tasks with optional search, filters, sort, and pagination.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | No | — | Full-text search query (min 1 char) |
| `status` | TaskStatus | No | `all` | Filter by completion status |
| `priority` | string[] | No | — | Filter by priority (repeatable: `?priority=high&priority=medium`) |
| `tags` | string[] | No | — | Filter by tags (AND logic, repeatable) |
| `due_date_filter` | DueDateFilter | No | — | Preset date range filter |
| `due_date_from` | ISO-8601 | No | — | Custom range start (requires `due_date_to`) |
| `due_date_to` | ISO-8601 | No | — | Custom range end (requires `due_date_from`) |
| `sort_by` | SortField | No | `created_at` | Sort field |
| `sort_order` | SortOrder | No | `desc` | Sort direction |
| `cursor` | string | No | — | Pagination cursor (from `next_cursor` in previous response) |
| `limit` | integer | No | `20` | Page size (1–100) |

**Response: 200**
```json
{
  "tasks": [TaskResponse],
  "next_cursor": "base64-cursor | null",
  "has_more": true,
  "total_count": 142
}
```

**Errors**: `400` (invalid filter params), `401`, `403`

---

### POST `/api/{user_id}/tasks`
Create a new task (with optional due date, tags, recurrence).

**Request Body**:
```json
{
  "title": "string (required, max 200)",
  "description": "string | null (max 2000)",
  "priority": "high | medium | low (default: medium)",
  "tags": ["string (max 50 chars each)"],
  "due_date": "ISO-8601 datetime | null",
  "recurrence_rule": "RRULE string | null",
  "reminders": [
    {
      "offset_minutes": "integer (>0, e.g. 60 = 1hr before)"
    }
  ]
}
```

**Response: 201** → `TaskResponse`

**Errors**: `400` (validation), `401`, `403`, `422` (invalid RRULE)

---

### GET `/api/{user_id}/tasks/{task_id}`
Retrieve a single task with full details including reminders and tags.

**Response: 200** → `TaskResponse`

**Errors**: `401`, `403`, `404`

---

### PATCH `/api/{user_id}/tasks/{task_id}`
Partial update a task. For recurring tasks, `update_scope` controls breadth of change.

**Request Body**:
```json
{
  "title": "string | null",
  "description": "string | null",
  "is_completed": "boolean | null",
  "priority": "high | medium | low | null",
  "tags": ["string"] | null,
  "due_date": "ISO-8601 datetime | null",
  "recurrence_rule": "RRULE string | null",
  "is_paused": "boolean | null",
  "update_scope": "this_only | all_future (default: this_only)"
}
```

**Behaviour**:
- If `is_completed: true` and task has a `recurrence_rule` (and `is_paused: false`), server spawns next instance.
- If `update_scope: all_future`, updates `recurrence_series` and all future (incomplete) instances.

**Response: 200** → `TaskResponse`

**Errors**: `400`, `401`, `403`, `404`, `422`

---

### DELETE `/api/{user_id}/tasks/{task_id}`
Delete a task. For recurring tasks, `delete_scope` controls breadth.

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `delete_scope` | `this_only \| all_future` | `this_only` | For recurring tasks |

**Response: 204** No content.

**Errors**: `401`, `403`, `404`

---

## Reminder Endpoints

### POST `/api/{user_id}/tasks/{task_id}/reminders`
Add a reminder to a task.

**Request Body**:
```json
{
  "offset_minutes": "integer (>0)"
}
```

**Validation**: Task must have a `due_date`. `trigger_at` computed as `due_date - offset_minutes`.

**Response: 201** → `ReminderResponse`

**Errors**: `400` (task has no due_date), `401`, `403`, `404`

---

### DELETE `/api/{user_id}/tasks/{task_id}/reminders/{reminder_id}`
Remove a reminder.

**Response: 204** No content.

**Errors**: `401`, `403`, `404`

---

## Tag Endpoints

### GET `/api/{user_id}/tags`
List all tags belonging to the authenticated user.

**Response: 200**
```json
{
  "tags": [
    {
      "id": "uuid",
      "name": "string",
      "color": "#HEX | null",
      "task_count": "integer"
    }
  ]
}
```

---

### POST `/api/{user_id}/tags`
Create a new tag.

**Request Body**:
```json
{
  "name": "string (max 50, alphanumeric + hyphens)",
  "color": "#HEX | null"
}
```

**Response: 201** → tag object

**Errors**: `400` (invalid name), `409` (duplicate name for user)

---

### DELETE `/api/{user_id}/tags/{tag_id}`
Delete a tag. Tag is removed from all tasks automatically (CASCADE on `task_tags`).

**Response: 204**

**Errors**: `401`, `403`, `404`

---

## Dapr Pub/Sub Event Contract

### Published Events (Backend → Kafka via Dapr)

**Topic**: `tasks`

| Event Type | Trigger | Key Payload Fields |
|------------|---------|-------------------|
| `task.created` | POST /tasks | task_id, user_id, title, priority, tags, due_date |
| `task.updated` | PATCH /tasks/{id} | task_id, user_id, changed_fields, update_scope |
| `task.completed` | PATCH is_completed=true | task_id, user_id, completed_at |
| `task.deleted` | DELETE /tasks/{id} | task_id, user_id, delete_scope |

**Topic**: `reminders`

| Event Type | Trigger | Key Payload Fields |
|------------|---------|-------------------|
| `task.reminder` | APScheduler fires | task_id, user_id, task_title, trigger_at |

### Subscribed Events (Dapr → Notification Handler)

**Endpoint**: `POST /dapr/subscribe` → subscribes to `reminders` topic

```json
[
  {
    "pubsubname": "taskpubsub",
    "topic": "reminders",
    "route": "/notifications/reminder"
  }
]
```

**Notification handler**: `POST /notifications/reminder`
- Marks reminder `status = sent`
- Stores in-app notification (future: UI polling endpoint)

---

## Error Response Schema

```json
{
  "detail": "string (human-readable message)",
  "error_code": "string (machine-readable, e.g. TASK_NOT_FOUND)",
  "field_errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid JWT |
| 403 | Authenticated but not authorized for this resource |
| 404 | Resource not found (user-scoped) |
| 409 | Conflict (e.g., duplicate tag name) |
| 422 | Unprocessable entity (e.g., invalid RRULE string) |
| 500 | Internal server error |
