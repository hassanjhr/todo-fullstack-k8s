# Tasks: Advanced Task Management with Distributed Architecture

**Input**: Design documents from `/specs/005-advanced-features-dapr-kafka/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/tasks-v2-api.md ✅ | quickstart.md ✅
**Feature Branch**: `005-advanced-features-dapr-kafka`
**Date**: 2026-03-31

**Tests**: Not requested — no test tasks generated per spec. Add `/sp.tasks --tdd` to regenerate with test tasks.

**Organization**: Tasks grouped by User Story (US1→US6) in priority order (P1→P4). Each story is independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable — different files, no dependencies on incomplete tasks in same phase
- **[Story]**: User story label (US1–US6) from spec.md
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new runtime dependencies, Dapr component directory, Kafka local dev config, and environment variable templates. No business logic — pure project scaffolding.

- [X] T001 Add `python-dateutil>=2.9`, `apscheduler>=3.10`, `dapr>=1.13` to `backend/requirements.txt`
- [X] T002 Create directory `dapr/components/` at repository root
- [X] T003 [P] Create `docker-compose.kafka.yml` at repository root with Zookeeper (confluentinc/cp-zookeeper:7.6.0 port 2181) and Kafka (confluentinc/cp-kafka:7.6.0 port 9092, KAFKA_AUTO_CREATE_TOPICS_ENABLE=true, PLAINTEXT advertised listener)
- [X] T004 [P] Add `DAPR_ENABLED=false`, `DAPR_HTTP_PORT=3500`, `DAPR_PUBSUB_NAME=taskpubsub`, `REMINDER_POLL_INTERVAL=300` to `backend/.env.example`
- [X] T005 [P] Add `dapr/secrets.json` to `backend/.gitignore` and root `.gitignore`
- [X] T006 Create `dapr/secrets.json.template` at repository root with keys `jwt-secret`, `database-url`, `kafka-brokers` (values as placeholder strings, never real credentials)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database migrations for all new entities + extended task columns + SQLModel model classes. All user story phases depend on this.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Migrations

- [X] T007 Create `backend/migrations/003_extend_tasks_table.sql` — ALTER TABLE tasks ADD COLUMNS: `priority VARCHAR(10) NOT NULL DEFAULT 'medium'`, `due_date TIMESTAMPTZ`, `recurrence_rule TEXT`, `series_id UUID`, `parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL`, `is_paused BOOLEAN NOT NULL DEFAULT false`; ADD CONSTRAINT `chk_priority CHECK (priority IN ('high','medium','low'))`; CREATE EXTENSION pg_trgm; CREATE INDEX `idx_task_search_gin` ON tasks USING GIN((title || ' ' || COALESCE(description,'')) gin_trgm_ops); CREATE INDEX `idx_task_priority` ON tasks(user_id, priority); CREATE INDEX `idx_task_due_date` ON tasks(user_id, due_date) WHERE due_date IS NOT NULL; CREATE INDEX `idx_task_cursor` ON tasks(user_id, created_at DESC, id DESC)
- [X] T008 Create `backend/migrations/004_create_reminders_table.sql` — CREATE TABLE reminders with columns: id UUID PK, task_id UUID FK tasks CASCADE, user_id UUID FK users CASCADE, offset_minutes INTEGER CHECK(>0), trigger_at TIMESTAMPTZ NOT NULL, status VARCHAR(20) DEFAULT 'pending' CHECK(IN('pending','sent','cancelled')), created_at TIMESTAMPTZ DEFAULT now(); CREATE INDEX idx_reminder_trigger ON reminders(trigger_at) WHERE status='pending'; CREATE INDEX idx_reminder_task ON reminders(task_id)
- [X] T009 [P] Create `backend/migrations/005_create_tags_table.sql` — CREATE TABLE tags with columns: id UUID PK, user_id UUID FK users CASCADE, name VARCHAR(50) NOT NULL CHECK(name ~ '^[a-zA-Z0-9\\-]+$'), color VARCHAR(7), created_at TIMESTAMPTZ DEFAULT now(); ADD UNIQUE(user_id, name); CREATE INDEX idx_tag_user_name ON tags(user_id, name)
- [X] T010 [P] Create `backend/migrations/006_create_task_tags_table.sql` — CREATE TABLE task_tags with columns: task_id UUID FK tasks CASCADE, tag_id UUID FK tags CASCADE, added_at TIMESTAMPTZ DEFAULT now(); PRIMARY KEY(task_id, tag_id); CREATE INDEX idx_task_tags_tag ON task_tags(tag_id); CREATE INDEX idx_task_tags_task ON task_tags(task_id)
- [X] T011 [P] Create `backend/migrations/007_create_recurrence_series_table.sql` — CREATE TABLE recurrence_series with columns: id UUID PK, user_id UUID FK users CASCADE, original_task_id UUID FK tasks, recurrence_rule TEXT NOT NULL, base_title VARCHAR(200) NOT NULL, base_description TEXT, base_priority VARCHAR(10) NOT NULL DEFAULT 'medium' CHECK(IN('high','medium','low')), is_active BOOLEAN NOT NULL DEFAULT true, created_at TIMESTAMPTZ DEFAULT now(); CREATE INDEX idx_series_user ON recurrence_series(user_id)
- [X] T012 Run all 5 new migrations via `backend/scripts/run_migrations.py` and verify each migration applies without error

### SQLModel Models

- [X] T013 Extend `backend/src/models/task.py` — add fields to Task class: `priority: str = Field(default='medium')`, `due_date: Optional[datetime] = Field(default=None)`, `recurrence_rule: Optional[str] = Field(default=None)`, `series_id: Optional[UUID] = Field(default=None, foreign_key='recurrence_series.id')`, `parent_task_id: Optional[UUID] = Field(default=None, foreign_key='tasks.id')`, `is_paused: bool = Field(default=False)`; preserve all existing fields unchanged
- [X] T014 Create `backend/src/models/reminder.py` — Reminder SQLModel class with all columns from migration 004; include `__tablename__ = "reminders"`
- [X] T015 [P] Create `backend/src/models/tag.py` — Tag SQLModel class with all columns from migration 005; include `__tablename__ = "tags"`
- [X] T016 [P] Create `backend/src/models/task_tag.py` — TaskTag SQLModel class with all columns from migration 006; include `__tablename__ = "task_tags"`
- [X] T017 [P] Create `backend/src/models/recurrence_series.py` — RecurrenceSeries SQLModel class with all columns from migration 007; include `__tablename__ = "recurrence_series"`
- [X] T018 Update `backend/src/models/__init__.py` — add imports for Reminder, Tag, TaskTag, RecurrenceSeries
- [X] T019 Create `backend/src/services/event_publisher.py` — stub with `publish_task_event(event_type: str, task_data: dict) -> None`; reads `DAPR_ENABLED` from env; if False, logs and returns; if True, POST to `http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/tasks` with CloudEvents envelope `{"specversion":"1.0","type":event_type,"source":"todo-backend","data":task_data}`; catch all exceptions and log without raising (graceful degradation)
- [X] T020 Update `backend/src/main.py` — import and register Reminder, Tag, TaskTag, RecurrenceSeries in SQLModel metadata create_all; do not break existing startup logic

**Checkpoint**: Database has all 5 new migrations applied. All 6 SQLModel classes exist. EventPublisher stub is available. User story implementation can now begin.

---

## Phase 3: User Story 1 — Task Priorities & Organization (Priority: P1) 🎯 MVP

**Goal**: Users can assign priority (High/Medium/Low) and tags to tasks, filter by priority and tags, and sort by priority. Fully functional independently of due dates and recurrence.

**Independent Test**: Create 3 tasks with priorities High/Medium/Low and tags ["work","urgent"], ["personal"], ["work"]. Verify: (1) filter by priority=high returns only high task; (2) filter by tag=work returns 2 tasks; (3) sort by priority desc returns High first; (4) task defaults to medium when no priority given.

### Backend — Schemas

- [X] T021 Extend `backend/src/schemas/task.py` — add `priority: str = 'medium'` and `tags: list[str] = []` to TaskCreateRequest; add `priority: str`, `tags: list[str]`, `is_overdue: bool` to TaskResponse; add Pydantic validator on priority to accept only `high|medium|low`; keep all existing fields
- [X] T022 Create `backend/src/schemas/tag.py` — TagCreateRequest (name: str max_length=50, color: Optional[str]), TagResponse (id, name, color, task_count: int), TagListResponse (tags: list[TagResponse])

### Backend — Tags Route

- [X] T023 Create `backend/src/api/routes/tags.py` — GET /api/{user_id}/tags returns TagListResponse (query tags WHERE user_id=authenticated_user.id, include task_count via subquery); POST /api/{user_id}/tags creates new Tag (validate name regex `^[a-zA-Z0-9\-]+$`, enforce unique via DB constraint, return 409 on duplicate); DELETE /api/{user_id}/tags/{tag_id} deletes tag and cascades to task_tags; all routes use `get_current_user` dep and verify user_id match

### Backend — Extended Task Routes (Priority + Tags)

- [X] T024 Extend POST `/api/{user_id}/tasks` in `backend/src/api/routes/tasks.py` — accept `priority` (default 'medium') and `tags: list[str]`; for each tag string: get-or-create Tag for this user (upsert on unique(user_id,name)), then insert TaskTag row; after task commit, call `event_publisher.publish_task_event('task.created', {...})`
- [X] T025 Extend GET `/api/{user_id}/tasks` in `backend/src/api/routes/tasks.py` — add query params: `priority: Optional[list[str]]` (filter WHERE task.priority IN priorities), `tags: Optional[list[str]]` (JOIN task_tags/tags WHERE tag.name IN tags AND tag.user_id=user_id, AND logic: task must have ALL specified tags), `sort_by: str = 'created_at'` (accepts created_at|priority|title), `sort_order: str = 'desc'`; priority sort order: high=1, medium=2, low=3; use `selectinload` for tags to avoid N+1; keep existing response structure, add tags list and priority to each task
- [X] T026 Extend PATCH `/api/{user_id}/tasks/{task_id}` in `backend/src/api/routes/tasks.py` — accept `priority: Optional[str]` and `tags: Optional[list[str]]`; on tags update: delete existing TaskTag rows for this task, create new ones via get-or-create Tag; call `event_publisher.publish_task_event('task.updated', {...})`
- [X] T027 Register tags router in `backend/src/main.py` — `app.include_router(tags_router, prefix="/api")`; verify no route conflicts with existing routes

### Frontend — Types & API

- [X] T028 Update `frontend/types/task.ts` — add `priority: 'high' | 'medium' | 'low'`, `tags: string[]`, `is_overdue: boolean` fields to Task interface
- [X] T029 [P] Create `frontend/types/tag.ts` — export Tag interface (id, name, color, task_count), TagCreatePayload interface
- [X] T030 [P] Create `frontend/lib/api/tags.ts` — `getTags(userId)` GET /api/{userId}/tags; `createTag(userId, payload)` POST; `deleteTag(userId, tagId)` DELETE; mirror pattern of existing `frontend/lib/api/tasks.ts`
- [X] T031 Update `frontend/lib/api/tasks.ts` — pass `priority` and `tags` in createTask and updateTask payloads; add `priority` and `tags` query params to getTasks function signature

### Frontend — UI Components

- [X] T032 Update `frontend/components/tasks/TaskItem.tsx` — add priority badge (color-coded pill: red=high, yellow=medium, gray=low) and tag chips (rounded pills with tag name) below task title; use Tailwind CSS classes
- [X] T033 Update `frontend/components/tasks/TaskForm.tsx` — add priority `<select>` field (High/Medium/Low, default Medium) and tags input (comma-separated text input that splits on comma/enter into tag string array); validate tag names client-side (alphanumeric + hyphens only)
- [X] T034 [P] Create `frontend/components/tasks/TaskFilter.tsx` — renders priority multi-checkbox (High/Medium/Low) and tag multi-select (fetches user's tags via getTags); calls onChange callback with {priority: string[], tags: string[]} filter state; uses Tailwind collapsible panel
- [X] T035 Update `frontend/app/dashboard/page.tsx` — import and render TaskFilter above TaskList; manage filter state with useState; pass filter params to getTasks API call; add "Clear filters" button that resets state

**Checkpoint**: US1 fully functional. Users can create tasks with priority and tags, filter/sort by them. All tag routes secured. Deploy or demo this story independently.

---

## Phase 4: User Story 4 — Search, Filter & Sort (Priority: P2)

**Goal**: Users can search tasks by keyword, combine multiple filters simultaneously (status + priority + tag + due date range), and sort by multiple fields. Cursor-based pagination for large lists.

**Depends on**: Phase 3 (US1) — tag and priority filters need those attributes to exist.

**Independent Test**: Create 10+ tasks with varied titles/priorities/tags. Search "meeting" — verify only matching tasks returned. Apply priority=high AND tag=work — verify compound AND filter. Sort by title asc — verify alphabetical order. Scroll to end of list — verify next_cursor returned and next page loads.

### Backend — Search + Compound Filter + Cursor Pagination

- [X] T036 Extend GET `/api/{user_id}/tasks` in `backend/src/api/routes/tasks.py` — add query params: `q: Optional[str]` (ILIKE search on title + description using pg_trgm index: `WHERE (title ILIKE '%q%' OR description ILIKE '%q%')`), `status: str = 'all'` (filter all|completed|pending|overdue — overdue = due_date < now AND NOT is_completed), `sort_by` extend to also accept `due_date`, `cursor: Optional[str]` (base64 JSON of {created_at, id}), `limit: int = 20` (max 100); implement cursor WHERE clause: `(created_at < cursor.created_at) OR (created_at = cursor.created_at AND id < cursor.id)`; fetch limit+1 rows to determine has_more; return PaginatedTaskResponse with `next_cursor` (base64 encoded last item) and `has_more`
- [X] T037 Add cursor encode/decode helper functions in `backend/src/api/routes/tasks.py` — `encode_cursor(created_at, id) -> str` (base64 JSON), `decode_cursor(cursor_str) -> tuple` (returns created_at datetime, id UUID); handle malformed cursor with 400 error

### Frontend — Search + Sort Controls + Infinite Scroll

- [X] T038 Create `frontend/components/tasks/TaskSearch.tsx` — `<input>` with 300ms debounce using `useEffect` + `setTimeout`/`clearTimeout`; calls `onSearch(query: string)` prop when debounce fires; shows spinner while searching; clear button (×) when query is non-empty
- [X] T039 Update `frontend/components/tasks/TaskFilter.tsx` — add status toggle buttons (All / Pending / Completed / Overdue) and sort_by select (Created / Due Date / Priority / Title) + sort_order toggle (↑ ↓); expand onChange to include {status, sort_by, sort_order} alongside existing priority/tags
- [X] T040 Update `frontend/components/tasks/TaskList.tsx` — replace current list rendering with infinite scroll: use `IntersectionObserver` on a sentinel div at list bottom; when sentinel visible and `has_more=true`, fetch next page with `cursor=next_cursor`; append results to existing list; show loading spinner while fetching
- [X] T041 Update `frontend/lib/api/tasks.ts` — extend getTasks params to accept `q`, `status`, `sort_by`, `sort_order`, `cursor`, `limit`; serialize all as URL query params; return full PaginatedTaskResponse shape including `next_cursor` and `has_more`
- [X] T042 Update `frontend/app/dashboard/page.tsx` — add TaskSearch component above TaskFilter; wire search query state into getTasks; reset cursor/list when q or filters change (avoid stale pagination)

**Checkpoint**: US4 fully functional. Full-text search, compound filters, multi-field sort, and infinite scroll all work. Verify US1 filters still work within this extended GET /tasks.

---

## Phase 5: User Story 2 — Due Dates & Reminders (Priority: P2)

**Goal**: Users can assign due dates to tasks, set reminder offsets (e.g., 1 hour before), see overdue tasks highlighted, and receive in-app reminders at the correct time via Dapr event.

**Independent Test**: Create a task with due_date=now+2min, reminder offset=1min. Wait ~1min — verify reminder fires (status=sent, Dapr event published). Mark task complete — verify reminder status=cancelled. Filter by "overdue" — verify only past-due incomplete tasks appear.

### Backend — Schemas

- [X] T043 Extend `backend/src/schemas/task.py` — add `due_date: Optional[datetime]` to TaskCreateRequest and TaskUpdateRequest; add `due_date: Optional[datetime]`, `is_overdue: bool` (computed: `due_date < now AND NOT is_completed`), `reminders: list[ReminderResponse] = []` to TaskResponse (load via selectinload); ensure TaskResponse serializes is_overdue as computed field
- [X] T044 Create `backend/src/schemas/reminder.py` — ReminderCreateRequest (offset_minutes: int with validator ≥1), ReminderResponse (id, offset_minutes, trigger_at, status)

### Backend — Reminders Route

- [X] T045 Create `backend/src/api/routes/reminders.py` — POST `/api/{user_id}/tasks/{task_id}/reminders`: validate task exists + user owns it, validate task has due_date (return 400 if not), compute trigger_at = due_date - timedelta(minutes=offset_minutes), insert Reminder row with status='pending', return ReminderResponse 201; DELETE `/api/{user_id}/tasks/{task_id}/reminders/{reminder_id}`: verify ownership, delete row, return 204; add Dapr subscriber endpoint POST `/notifications/reminder`: accept CloudEvents reminder payload, mark reminder status='sent', log; add GET `/dapr/subscribe` returning subscription config for 'reminders' topic
- [X] T046 Extend PATCH `/api/{user_id}/tasks/{task_id}` in `backend/src/api/routes/tasks.py` — when `is_completed=True`: UPDATE all reminders for this task SET status='cancelled'; when `due_date` changes: recalculate all pending reminder trigger_at values (trigger_at = new_due_date - timedelta(minutes=reminder.offset_minutes)); call publish_task_event('task.completed') on completion

### Backend — Reminder Scheduler (APScheduler)

- [X] T047 Create `backend/src/services/reminder_service.py` — instantiate `BackgroundScheduler(timezone=utc)`; define `check_due_reminders()` async function: query `SELECT * FROM reminders WHERE trigger_at <= now() AND status='pending'`, for each: call `event_publisher.publish_task_event('task.reminder', {task_id, user_id, task_title, trigger_at})`; add job with `trigger='interval', seconds=REMINDER_POLL_INTERVAL, max_instances=1, replace_existing=True`; expose `start_scheduler()` and `stop_scheduler()` functions
- [X] T048 Update `backend/src/main.py` — in FastAPI lifespan context manager (`@asynccontextmanager`): call `start_scheduler()` on startup and `stop_scheduler()` on shutdown; register reminders router (`app.include_router(reminders_router, prefix="/api")`); register `/dapr/subscribe` route

### Frontend — Due Date UI

- [X] T049 Update `frontend/types/task.ts` — add `due_date: string | null`, `is_overdue: boolean`, `reminders: Reminder[]` to Task interface
- [X] T050 [P] Create `frontend/types/reminder.ts` — Reminder interface (id, offset_minutes, trigger_at, status), ReminderCreatePayload interface (offset_minutes: number)
- [X] T051 [P] Create `frontend/lib/api/reminders.ts` — `createReminder(userId, taskId, payload)` POST /api/{userId}/tasks/{taskId}/reminders; `deleteReminder(userId, taskId, reminderId)` DELETE; mirror auth header pattern from existing client.ts
- [X] T052 Update `frontend/components/tasks/TaskForm.tsx` — add optional `<input type="datetime-local">` for due date; add ReminderForm section (renders when due_date is set); serialize due_date as ISO-8601 string in API payload
- [X] T053 Create `frontend/components/tasks/ReminderForm.tsx` — renders list of current reminders with delete button; "+ Add Reminder" button opens dropdown with preset offsets (15 min / 1 hr / 24 hrs / custom integer input); calls createReminder API on add, deleteReminder on remove; show trigger_at computed time for user reference
- [X] T054 Update `frontend/components/tasks/TaskItem.tsx` — show due date below title (formatted as "Due: Mar 31, 9:00 AM"); apply red text color and warning icon when `is_overdue=true`; show reminder count badge if reminders.length > 0

**Checkpoint**: US2 fully functional. Due dates visible, overdue indicator working, APScheduler polling, reminder events firing via Dapr. US1 unaffected.

---

## Phase 6: User Story 3 — Recurring Tasks (Priority: P3)

**Goal**: Users can create tasks that repeat on a schedule. Completing one instance auto-creates the next. Users can edit/delete "this only" or "all future" instances. Recurrence can be paused.

**Depends on**: Phase 5 (US2) — recurring tasks use due_date for scheduling next instance.

**Independent Test**: Create task with FREQ=WEEKLY;BYDAY=MO. Complete it — verify new task created for next Monday with same title/priority/tags. Edit with scope=all_future, change title — verify all future instances updated. Delete with scope=this_only — verify only current instance deleted. Pause series — verify no new instances spawned.

### Backend — Schemas

- [X] T055 Extend `backend/src/schemas/task.py` — add to TaskCreateRequest: `recurrence_rule: Optional[str]` (validated as valid RRULE string using `rrulestr(rule, dtstart=datetime.utcnow())`); add to TaskResponse: `recurrence_rule: Optional[str]`, `series_id: Optional[UUID]`, `is_paused: bool`, `next_due_date: Optional[datetime]` (computed: `rrulestr(recurrence_rule).after(datetime.utcnow())` if rule exists); add to TaskUpdateRequest: `recurrence_rule: Optional[str]`, `is_paused: Optional[bool]`, `update_scope: str = 'this_only'` (accepts this_only|all_future); add `delete_scope: str` to task delete query param

### Backend — Recurrence Service

- [X] T056 Create `backend/src/services/task_service.py` — implement `spawn_next_recurrence(task: Task, session: AsyncSession) -> Task`: parse task.recurrence_rule with `rrulestr(rule, dtstart=task.due_date or datetime.utcnow())`, get next occurrence after now via `rule.after(datetime.utcnow())`, create new Task with same title/description/priority/tags/recurrence_rule/series_id/parent_task_id=task.id, set due_date=next_occurrence; for each reminder of original task: create new Reminder for new task with same offset_minutes, trigger_at=next_occurrence - timedelta(minutes=offset); return new task
- [X] T057 Add `handle_bulk_update(series_id: UUID, fields: dict, from_task_id: UUID, session: AsyncSession)` to `backend/src/services/task_service.py` — find all incomplete Tasks WHERE series_id=series_id AND created_at >= (SELECT created_at FROM tasks WHERE id=from_task_id); update each with provided fields; also update RecurrenceSeries base fields if title/description/priority/recurrence_rule changed
- [X] T058 Add `handle_bulk_delete(series_id: UUID, from_task_id: UUID, session: AsyncSession)` to `backend/src/services/task_service.py` — delete all Tasks WHERE series_id=series_id AND is_completed=false AND created_at >= (SELECT created_at FROM tasks WHERE id=from_task_id); if no tasks remain in series, set recurrence_series.is_active=false

### Backend — Extended Task Routes (Recurrence)

- [X] T059 Extend POST `/api/{user_id}/tasks` in `backend/src/api/routes/tasks.py` — if recurrence_rule provided: validate RRULE string (catch rrulestr exception, return 422 on invalid); create RecurrenceSeries row with base_title/base_description/base_priority/recurrence_rule; set task.series_id = new series id
- [X] T060 Extend PATCH `/api/{user_id}/tasks/{task_id}` in `backend/src/api/routes/tasks.py` — when `is_completed=True` AND task has recurrence_rule AND NOT is_paused: call `task_service.spawn_next_recurrence(task, session)`; when `update_scope='all_future'`: call `task_service.handle_bulk_update(series_id, changed_fields, task_id, session)`; when `is_paused` toggles to True: update RecurrenceSeries.is_active=false; when toggled to False: update RecurrenceSeries.is_active=true
- [X] T061 Extend DELETE `/api/{user_id}/tasks/{task_id}` in `backend/src/api/routes/tasks.py` — add `delete_scope: str = 'this_only'` query param; if `all_future`: call `task_service.handle_bulk_delete(series_id, task_id, session)`; if `this_only`: delete only this task; publish `task.deleted` event via event_publisher

### Frontend — Recurrence UI

- [X] T062 Update `frontend/types/task.ts` — add `recurrence_rule: string | null`, `series_id: string | null`, `is_paused: boolean`, `next_due_date: string | null` to Task interface
- [X] T063 Create `frontend/components/tasks/RecurrenceForm.tsx` — frequency selector radio/select (None / Daily / Weekdays / Weekly / Monthly / Custom RRULE); Weekly shows day-of-week checkboxes (Mon–Sun); Monthly shows day-of-month input; Custom shows raw RRULE text input with validation; outputs RRULE string via onChange prop; shows "Next occurrence: {date}" preview using rrule.js or computed from API
- [X] T064 Update `frontend/components/tasks/TaskForm.tsx` — add RecurrenceForm section below due date; include recurrence_rule in API payload; add is_paused toggle switch for existing recurring tasks
- [X] T065 Update `frontend/components/tasks/TaskItem.tsx` — show recurrence badge ("↻ Daily", "↻ Weekly", etc.) parsed from recurrence_rule; show next_due_date if set; add pause/resume button for recurring tasks (calls PATCH {is_paused: !task.is_paused})
- [X] T066 Update `frontend/components/tasks/TaskList.tsx` — on task edit/delete for recurring tasks, show scope selection modal ("Update this task only" / "Update all future tasks") before calling API; pass update_scope/delete_scope in API payload; use a simple `window.confirm` dialog or inline modal component

**Checkpoint**: US3 fully functional. Recurring tasks spawn next instances, bulk edit/delete works, pause/resume works. US1 + US2 still functional.

---

## Phase 7: User Story 5 — Event-Driven Architecture via Kafka (Priority: P4)

**Goal**: All task lifecycle events (create, update, complete, delete, reminder) are published to Kafka via Dapr pub/sub. System degrades gracefully when Kafka is unavailable. Dead-letter handling for failed events.

**Depends on**: Phase 2 (event_publisher stub exists). Phases 3–6 wire event calls.

**Independent Test**: Start Kafka (docker compose up), run backend with Dapr sidecar (dapr run). Create a task — verify `task.created` event on `tasks` topic using kafka-console-consumer. Stop Kafka, create a task — verify API returns 200 (no error), DLQ log entry appears. Check Dapr metrics endpoint shows pubsub latency.

### Backend — Event Publisher (Full Implementation)

- [X] T067 Complete `backend/src/services/event_publisher.py` — implement full publish logic: build CloudEvents 1.0 envelope `{specversion:"1.0", type:event_type, source:"todo-backend", id:str(uuid4()), time:datetime.utcnow().isoformat()+"Z", datacontenttype:"application/json", data:{...task_data, user_id:..., timestamp:...}}`; POST to `http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}` with `Content-Type: application/cloudevents+json`; implement retry: attempt up to 3 times with 1s backoff; on all retries exhausted: POST to dead-letter topic (`tasks-dlq`) as final attempt; log all publish attempts with correlation_id and event_type; never raise exceptions to caller
- [X] T068 Add `publish_reminder_event(task_id, user_id, task_title, trigger_at)` to `backend/src/services/event_publisher.py` — publishes to `reminders` topic with event_type `task.reminder`; called from reminder_service.check_due_reminders()
- [X] T069 Verify all 5 event publish call sites are wired: POST /tasks → task.created in `backend/src/api/routes/tasks.py`; PATCH /tasks → task.updated in tasks.py; PATCH is_completed=True → task.completed in tasks.py; DELETE /tasks → task.deleted in tasks.py; reminder poll → task.reminder in `backend/src/services/reminder_service.py`

### Dapr Components

- [X] T070 Create `dapr/components/pubsub-kafka.yaml` — Component spec: name=taskpubsub, type=pubsub.kafka, version=v1; metadata: brokers=localhost:9092 (local dev), consumerGroup=todo-chatbot, authType=none; add retry policy (maxRetries: 3, duration: 1s) and dead letter topic (deadLetterTopic: tasks-dlq) in component spec
- [X] T071 [P] Create `dapr/components/secretstore-local.yaml` — Component spec: name=localsecrets, type=secretstores.local.file, version=v1; metadata: secretsFile=./dapr/secrets.json, nestedSeparator=:

**Checkpoint**: US5 fully functional. Events flow to Kafka via Dapr. Graceful degradation verified with Kafka stopped. Existing task operations unaffected.

---

## Phase 8: User Story 6 — Dapr Distributed Runtime (Priority: P4)

**Goal**: All inter-service communication routes through Dapr sidecars. Secrets injected via Dapr secrets store. Dapr sidecar annotations added to Kubernetes deployment. Health/readiness endpoints expose Dapr lifecycle signals.

**Depends on**: Phase 7 (Dapr components created).

**Independent Test**: Deploy with `dapr run --app-id todo-backend --components-path ../dapr/components`. Verify: (1) GET http://localhost:3500/v1.0/healthz returns 200; (2) secrets loaded from dapr/secrets.json (not .env); (3) task event appears on Kafka topic; (4) Dapr traces visible in Zipkin at http://localhost:9411.

### Backend — Dapr Secrets Integration

- [X] T072 Update `backend/src/config.py` — add `DAPR_ENABLED: bool = False`, `DAPR_HTTP_PORT: int = 3500`, `DAPR_PUBSUB_NAME: str = 'taskpubsub'`, `REMINDER_POLL_INTERVAL: int = 300` to Settings Pydantic model; implement `get_secret(key: str) -> str` helper: if DAPR_ENABLED, GET `http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/localsecrets/{key}`, return value; else fall back to os.environ[key]
- [X] T073 Update `backend/src/config.py` — replace direct `os.environ` reads for `JWT_SECRET` and `DATABASE_URL` with calls to `get_secret('jwt-secret')` and `get_secret('database-url')` when DAPR_ENABLED=true
- [X] T074 Add GET `/healthz/ready` endpoint to `backend/src/main.py` — return `{"status": "ok", "dapr_enabled": settings.DAPR_ENABLED}`; used as Dapr readiness probe target

### Kubernetes Helm Chart

- [X] T075 Update `todo-chatbot/templates/deployment.yaml` — add Dapr annotations to backend pod spec: `dapr.io/enabled: "true"`, `dapr.io/app-id: "todo-backend"`, `dapr.io/app-port: "8000"`, `dapr.io/dapr-http-port: "3500"`; gate these annotations on `{{ .Values.dapr.enabled }}`
- [X] T076 Create `todo-chatbot/templates/dapr-components.yaml` — Kubernetes manifest for Dapr Component CRD (pubsub.kafka) with broker address from `{{ .Values.kafka.brokers }}`; Kubernetes secretstore component referencing `todo-secrets` K8s secret; gated on `{{ .Values.dapr.enabled }}`
- [X] T077 Update `todo-chatbot/values.yaml` — add `dapr: {enabled: false}` and `kafka: {brokers: "localhost:9092"}` sections with comments; default dapr.enabled=false so existing deployments are unaffected

**Checkpoint**: US6 fully functional. Dapr sidecar handles pub/sub and secrets. K8s Helm chart supports Dapr deployment. Local dev still works without Dapr via DAPR_ENABLED=false.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, configuration cleanup, documentation, and final integration validation.

- [X] T078 [P] Security review — verify ALL new route handlers in `backend/src/api/routes/tags.py`, `backend/src/api/routes/reminders.py`, and extended handlers in `backend/src/api/routes/tasks.py` use `current_user: User = Depends(get_current_user)` and verify `current_user.id == user_id` before any DB operation; return 403 on mismatch
- [X] T079 [P] Verify tag name sanitization end-to-end in `backend/src/schemas/tag.py` — add Pydantic `@validator('name')` that applies `^[a-zA-Z0-9\-]+$` regex (max 50 chars); confirm DB constraint also enforces this as defence-in-depth
- [X] T080 [P] Verify Kafka event payloads in `backend/src/services/event_publisher.py` include only: event_type, task_id, user_id, timestamp, title, priority, tags list, is_completed — confirm no hashed_password, email, or full description included in `task.created`/`task.updated` events
- [X] T081 Update `backend/src/api/routes/tasks.py` — ensure DELETE handler publishes `task.deleted` event AND cancels all pending reminders for deleted task (UPDATE reminders SET status='cancelled' WHERE task_id=task_id AND status='pending') in a single transaction
- [X] T082 Update `backend/.env.example` with all new variables from T004 and `KAFKA_BROKERS=localhost:9092` comment
- [X] T083 [P] Add `dapr/secrets.json` and `dapr/secrets.json.template` entries to root `.gitignore`; verify no secrets committed to repository
- [X] T084 Run `quickstart.md` validation end-to-end: install deps (T001), start Kafka (T003), run migrations (T012), start backend with dapr run (Phase 7), create task via API and verify event on Kafka topic, verify reminder fires, verify filter/search works

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)              → no dependencies, start immediately
Phase 2 (Foundational)       → requires Phase 1 (new deps in requirements.txt)
Phase 3 (US1 - P1)           → requires Phase 2 (migration 003 + Task model)
Phase 4 (US4 - P2)           → requires Phase 3 (tag/priority filters)
Phase 5 (US2 - P2)           → requires Phase 2 (migration 004 + Reminder model)
Phase 6 (US3 - P3)           → requires Phase 5 (due_date for recurrence scheduling)
Phase 7 (US5 - P4)           → requires Phase 2 (event_publisher stub) + Phases 3–6 (call sites)
Phase 8 (US6 - P4)           → requires Phase 7 (Dapr components exist)
Phase 9 (Polish)             → requires all phases complete
```

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 only — first to implement, unblocked immediately
- **US4 (P2)**: Depends on US1 (needs tag/priority columns for compound filters)
- **US2 (P2)**: Depends on Phase 2 only — can run parallel to US1/US4
- **US3 (P3)**: Depends on US2 (due_date required for next-occurrence calculation)
- **US5 (P4)**: Depends on Phases 3–6 (wires into all task operation handlers)
- **US6 (P4)**: Depends on US5 (Dapr components created in US5)

### Within Each User Story

- Backend schemas → Backend routes → Frontend types → Frontend API → Frontend UI
- Models before services; services before routes

### Parallel Opportunities

- **Phase 1**: T003, T004, T005 can run in parallel (different files)
- **Phase 2 Migrations**: T008, T009, T010, T011 can run in parallel (independent SQL files)
- **Phase 2 Models**: T014, T015, T016, T017 can run in parallel (independent model files)
- **Phase 3**: T029, T030 (types); T034 (TagFilter) while T032, T033 are written (different components)
- **US1 frontend (T028–T035)** can run parallel to **US2 backend (T043–T048)** once Phase 2 is done
- **Phase 9**: T078, T079, T080, T083 are all parallel (different files, independent checks)

---

## Parallel Example: User Story 1 (P1)

```bash
# After Phase 2 complete, launch in parallel:

# Backend group (different files, no deps on each other):
Task T022: Create backend/src/schemas/tag.py
Task T023: Create backend/src/api/routes/tags.py

# Then sequentially:
Task T021: Extend backend/src/schemas/task.py (priority + tags)
Task T024: Extend POST /tasks in backend/src/api/routes/tasks.py
Task T025: Extend GET /tasks in backend/src/api/routes/tasks.py
Task T026: Extend PATCH /tasks in backend/src/api/routes/tasks.py
Task T027: Register tags router in backend/src/main.py

# Frontend group (parallel after T028):
Task T029: Create frontend/types/tag.ts
Task T030: Create frontend/lib/api/tags.ts
Task T031: Update frontend/lib/api/tasks.ts

# Then UI:
Task T032: Update TaskItem.tsx
Task T033: Update TaskForm.tsx
Task T034: Create TaskFilter.tsx
Task T035: Wire into dashboard page.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — ~17 tasks)

1. Complete **Phase 1** (Setup — T001–T006)
2. Complete **Phase 2** (Foundational — T007–T020)
3. Complete **Phase 3** (US1 Priorities & Tags — T021–T035)
4. **STOP and VALIDATE**: Create tasks with priorities + tags, filter/sort, verify all US1 scenarios
5. Deploy or demo MVP — full priority/tag management is immediately valuable

### Incremental Delivery

| Increment | Phases | Stories Delivered |
|-----------|--------|-------------------|
| MVP | 1 + 2 + 3 | US1: Priority & Tags |
| +Search | +4 | US4: Search, Filter, Sort |
| +Due Dates | +5 | US2: Due Dates & Reminders |
| +Recurring | +6 | US3: Recurring Tasks |
| +Events | +7 | US5: Kafka Event-Driven |
| +Distributed | +8 + 9 | US6: Dapr Runtime |

### Parallel Team Strategy

With 2 developers after Phase 2:

- **Dev A**: Phase 3 (US1 - Priority/Tags) → Phase 4 (US4 - Search)
- **Dev B**: Phase 5 (US2 - Due Dates/Reminders) → Phase 6 (US3 - Recurring)
- Both merge → Phase 7 (US5 Kafka) → Phase 8 (US6 Dapr) together

---

## Summary

| Phase | User Story | Tasks | Agent |
|-------|-----------|-------|-------|
| Phase 1 | Setup | T001–T006 (6) | `fastapi-backend-dev` |
| Phase 2 | Foundational | T007–T020 (14) | `neon-db-manager` |
| Phase 3 | US1 P1 — Priorities & Tags | T021–T035 (15) | `neon-db-manager` + `fastapi-backend-dev` + `nextjs-ui-builder` |
| Phase 4 | US4 P2 — Search/Filter/Sort | T036–T042 (7) | `fastapi-backend-dev` + `nextjs-ui-builder` |
| Phase 5 | US2 P2 — Due Dates & Reminders | T043–T054 (12) | `fastapi-backend-dev` + `nextjs-ui-builder` |
| Phase 6 | US3 P3 — Recurring Tasks | T055–T066 (12) | `fastapi-backend-dev` + `nextjs-ui-builder` |
| Phase 7 | US5 P4 — Kafka Events | T067–T071 (5) | `fastapi-backend-dev` |
| Phase 8 | US6 P4 — Dapr Runtime | T072–T077 (6) | `fastapi-backend-dev` |
| Phase 9 | Polish | T078–T084 (7) | `auth-security-handler` + `fastapi-backend-dev` |
| **Total** | | **T001–T084 (84 tasks)** | |

---

## Notes

- `[P]` tasks = different files, no intra-phase dependencies — safe to parallelize
- `[Story]` label maps each task to its user story for traceability
- Each user story has an **Independent Test** — stop and validate at each phase checkpoint
- Reminder delivery tolerance is ±5min in MVP (APScheduler 5-min poll) vs ±2min in spec SC-005 — acceptable trade-off documented in research.md
- Dapr is optional locally (`DAPR_ENABLED=false`) — never blocks local development
- All new routes must inherit existing `get_current_user` dependency — never bypass auth
