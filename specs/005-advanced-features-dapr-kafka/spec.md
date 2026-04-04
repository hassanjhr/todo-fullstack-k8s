# Feature Specification: Advanced Task Management with Distributed Architecture

**Feature Branch**: `005-advanced-features-dapr-kafka`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Advanced Features: Implement all Advanced Level features (Recurring Tasks, Due Dates & Reminders), Implement Intermediate Level features (Priorities, Tags, Search, Filter, Sort), Add event-driven architecture with Kafka, Implement Dapr for distributed application runtime"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Task Priorities & Organization (Priority: P1)

As a user, I want to assign priorities and tags to my tasks so I can organize my work by importance and category. I want to be able to filter and sort tasks by these properties to quickly find what matters most right now.

**Why this priority**: Priorities and tags are the foundational organizational layer for all downstream features. They unlock filtering, sorting, and advanced views. Without them, users cannot differentiate urgency or group related tasks.

**Independent Test**: Can be fully tested by creating tasks with different priority levels (High, Medium, Low) and tags, then verifying filtered/sorted views return correct results independently of due dates or recurrence.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a task and assign priority "High" and tags ["work", "urgent"], **Then** the task is saved with those properties and appears in filtered views for "High" priority and "work" tag.
2. **Given** a task list with mixed priorities, **When** the user sorts by priority descending, **Then** High priority tasks appear first, followed by Medium, then Low.
3. **Given** tasks with multiple tags, **When** the user filters by tag "work", **Then** only tasks containing that tag are shown.
4. **Given** a task without a priority set, **When** it is created, **Then** it defaults to "Medium" priority.

---

### User Story 2 — Due Dates & Reminders (Priority: P2)

As a user, I want to assign due dates to my tasks and receive reminders before they are due so I never miss a deadline. Reminders should be configurable per task.

**Why this priority**: Due dates and reminders drive timely task completion and are a core expectation for any modern task management tool. They depend on the base task model being stable (P1 prerequisites met).

**Independent Test**: Can be fully tested by creating a task with a due date, setting a reminder offset, and verifying the reminder notification is queued and delivered at the correct time.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a task with a due date of "tomorrow at 9 AM", **Then** the task is saved with that due date visible in the task list.
2. **Given** a task with a due date, **When** the user sets a reminder for "1 hour before", **Then** a reminder event is scheduled and the user is notified 1 hour before the due date.
3. **Given** a list of tasks, **When** the user filters by "due today", **Then** only tasks with a due date of today are returned, sorted by due time ascending.
4. **Given** a task whose due date has passed and it is not completed, **Then** it is visually marked as overdue.
5. **Given** a task is marked complete, **When** it had a pending reminder, **Then** the reminder is cancelled.

---

### User Story 3 — Recurring Tasks (Priority: P3)

As a user, I want to create tasks that repeat on a schedule (daily, weekly, monthly, or custom) so I don't have to manually recreate regular obligations.

**Why this priority**: Recurring tasks build on top of due dates (P2) and require a scheduling mechanism. They provide significant productivity value but are additive rather than foundational.

**Independent Test**: Can be fully tested by creating a recurring task, completing one instance, and verifying that the next instance is automatically created on schedule.

**Acceptance Scenarios**:

1. **Given** a user creates a task with recurrence "every Monday", **When** that task is marked complete, **Then** a new identical task is created for the following Monday.
2. **Given** a recurring task with recurrence "daily", **When** the user views the task, **Then** they can see the recurrence schedule and the next due date.
3. **Given** a recurring task, **When** the user edits it, **Then** they are prompted whether to update "this instance only" or "all future occurrences".
4. **Given** a recurring task, **When** the user deletes it, **Then** they are prompted to delete "this instance only" or "all future occurrences".
5. **Given** a task with recurrence "weekdays" and today is Friday, **When** it is completed, **Then** the next instance is created for Monday.

---

### User Story 4 — Search, Filter & Sort (Priority: P2)

As a user, I want to search tasks by keyword and apply multiple filters (status, priority, tag, due date range) and sort criteria simultaneously so I can quickly surface the tasks I need.

**Why this priority**: Search and advanced filtering are high-value features for users with large task lists. They depend on P1 priority/tag attributes existing.

**Independent Test**: Can be fully tested by searching for a keyword across task titles and descriptions, verifying only matching tasks appear, and combining with one filter to validate compound queries.

**Acceptance Scenarios**:

1. **Given** a user types "meeting" in the search bar, **When** results are returned, **Then** only tasks whose title or description contains "meeting" (case-insensitive) are shown.
2. **Given** a user applies filters for priority "High" AND tag "work", **When** the filtered list renders, **Then** only tasks matching both criteria are shown.
3. **Given** a user sorts by due date ascending, **When** tasks with no due date exist, **Then** tasks without due dates appear at the end.
4. **Given** a search query with no matching results, **When** the user searches, **Then** an empty state with a helpful message is shown.
5. **Given** a user applies multiple filters, **When** they clear all filters, **Then** the full unfiltered task list is restored.

---

### User Story 5 — Event-Driven Notifications via Kafka (Priority: P4)

As a system operator, I want all significant task events (task created, updated, completed, reminder triggered) to be published to an event bus so downstream services (notification service, audit log, analytics) can react independently without coupling to the core API.

**Why this priority**: Kafka integration is an architectural enhancement that decouples services. It is not visible to end users in isolation but enables reminders, audit trails, and future integrations. Depends on all core task features (P1–P3) being functional first.

**Independent Test**: Can be tested by creating/updating a task and verifying the corresponding event message appears on the correct Kafka topic with the expected schema.

**Acceptance Scenarios**:

1. **Given** a task is created, **When** the system processes the creation, **Then** a `task.created` event is published to the `tasks` Kafka topic containing task ID, user ID, title, priority, tags, and due date.
2. **Given** a task is marked complete, **When** the system processes the update, **Then** a `task.completed` event is published with task ID, user ID, and completion timestamp.
3. **Given** a reminder is due, **When** the scheduler triggers, **Then** a `task.reminder` event is published and consumed by the notification service to alert the user.
4. **Given** a Kafka broker is temporarily unavailable, **When** events are published, **Then** the API continues to function and events are retried or queued until the broker recovers.

---

### User Story 6 — Dapr-Powered Distributed Runtime (Priority: P4)

As a developer/operator, I want all inter-service communication, state management, pub/sub messaging, and secret management to be handled via Dapr sidecars so that the application is portable, observable, and resilient across environments.

**Why this priority**: Dapr provides the distributed runtime infrastructure that underpins Kafka pub/sub abstraction, secret injection, and service invocation. It is an infrastructure concern that complements P4 Kafka integration.

**Independent Test**: Can be tested by deploying the application with Dapr sidecars active and verifying that service-to-service calls route through Dapr, pub/sub messages are delivered via the Dapr pubsub component, and secrets are injected via Dapr secrets store.

**Acceptance Scenarios**:

1. **Given** the backend services are deployed with Dapr sidecars, **When** the frontend calls the task API, **Then** Dapr handles service invocation with automatic retries and tracing.
2. **Given** Dapr is configured with the Kafka pubsub component, **When** a task event is published, **Then** Dapr routes the event to subscribing services without direct Kafka client code in the application.
3. **Given** application secrets (DB URL, JWT secret), **When** services start, **Then** Dapr injects secrets from the configured secrets store, eliminating hardcoded environment variables.
4. **Given** a service instance fails, **When** Dapr detects the failure, **Then** requests are retried according to the configured retry policy.

---

### Edge Cases

- What happens when a user assigns a due date in the past? (System should warn but allow it; task immediately marked overdue)
- How does the system handle a recurring task whose next occurrence falls on a date that already has a manual task with the same title?
- What happens when a user deletes a tag that is referenced by existing tasks? (Tags are removed from tasks; tasks remain intact)
- What happens when search returns more than 1000 results? (Pagination applies; first page returned with cursor)
- How does the system behave when the Kafka broker is down? (API continues; event publishing fails gracefully, with retry/dead-letter queue)
- What happens when a reminder fires for a task that was deleted? (Event is discarded; no notification sent)
- What if a recurring task is paused? (No new instances are created until recurrence is re-enabled)

---

## Requirements *(mandatory)*

### Functional Requirements

#### Priorities & Tags (Intermediate)
- **FR-001**: System MUST allow users to assign a priority level (High, Medium, Low) to each task; default is Medium.
- **FR-002**: System MUST allow users to create, assign, and remove custom tags on tasks.
- **FR-003**: System MUST allow users to filter tasks by one or more tags simultaneously.
- **FR-004**: System MUST allow users to filter tasks by priority level.
- **FR-005**: System MUST allow users to sort tasks by priority (High → Low or Low → High).

#### Search, Filter & Sort (Intermediate)
- **FR-006**: System MUST provide full-text search across task titles and descriptions (case-insensitive).
- **FR-007**: System MUST support compound filtering: any combination of status, priority, tag, and due date range simultaneously.
- **FR-008**: System MUST support sorting by: due date (asc/desc), priority (asc/desc), creation date (asc/desc), and title (alphabetical).
- **FR-009**: System MUST return paginated results for all list and search endpoints.
- **FR-010**: System MUST allow users to clear all active filters and return to the default unfiltered view.

#### Due Dates & Reminders (Advanced)
- **FR-011**: System MUST allow users to assign an optional due date and time to any task.
- **FR-012**: System MUST visually distinguish overdue tasks (due date passed, task not complete).
- **FR-013**: System MUST allow users to set one or more reminders per task, defined as an offset before the due date (e.g., 15 min, 1 hour, 1 day).
- **FR-014**: System MUST cancel pending reminders when a task is marked complete or deleted.
- **FR-015**: System MUST allow users to filter tasks by due date ranges (today, this week, overdue, custom range).

#### Recurring Tasks (Advanced)
- **FR-016**: System MUST allow users to configure task recurrence: daily, weekly (specific day), monthly (specific date), weekdays, or custom interval.
- **FR-017**: System MUST automatically create the next task instance when a recurring task is marked complete, using the same title, description, priority, and tags.
- **FR-018**: System MUST display the recurrence schedule and next due date on recurring tasks.
- **FR-019**: System MUST allow users to edit a recurring task with scope options: "this instance only" or "all future occurrences".
- **FR-020**: System MUST allow users to delete a recurring task with scope options: "this instance only" or "all future occurrences".
- **FR-021**: System MUST allow users to pause/resume recurrence without deleting the task.

#### Event-Driven Architecture (Kafka)
- **FR-022**: System MUST publish events to Kafka for all significant task lifecycle changes: `task.created`, `task.updated`, `task.completed`, `task.deleted`, `task.reminder`.
- **FR-023**: Each Kafka event MUST include: event type, task ID, user ID, timestamp, and relevant payload fields.
- **FR-024**: System MUST continue normal API operations if the Kafka broker is temporarily unavailable (graceful degradation).
- **FR-025**: System MUST implement dead-letter handling for events that fail to publish after the configured retry limit.

#### Dapr Distributed Runtime
- **FR-026**: All inter-service communication MUST be routed through Dapr service invocation.
- **FR-027**: All pub/sub messaging (Kafka events) MUST be published and consumed via the Dapr pubsub building block.
- **FR-028**: Application secrets MUST be injected at runtime via the Dapr secrets building block, not hardcoded in environment files.
- **FR-029**: System MUST expose Dapr-compatible health and readiness endpoints for sidecar lifecycle management.

### Security Requirements

- **SR-001**: All API endpoints MUST require valid JWT authentication.
- **SR-002**: User identity MUST be extracted from the JWT token; never from the request body.
- **SR-003**: All database queries MUST filter by the authenticated user's ID (no cross-user data access).
- **SR-004**: Unauthorized requests MUST return 401; authorization failures MUST return 403.
- **SR-005**: Kafka events MUST include user ID for audit purposes but MUST NOT include sensitive PII beyond what is necessary.
- **SR-006**: Dapr secrets store MUST be used for all credentials (database URL, JWT secret, Kafka credentials).
- **SR-007**: Tag names MUST be sanitized to prevent injection attacks (max 50 characters, alphanumeric + hyphens).

### Key Entities

- **Task** (extended): Existing task entity extended with `priority` (enum: High/Medium/Low), `tags` (list of strings), `due_date` (nullable datetime), `recurrence_rule` (nullable, iCal RRULE format), `parent_task_id` (nullable, links recurring instances to a series), `is_paused` (boolean for recurrence).
- **Reminder**: Represents a scheduled notification offset for a task — linked to a task, stores offset duration, delivery status, and trigger timestamp.
- **Tag**: A user-defined label string associated with one or more tasks. Tags are stored per-user (no global tag registry).
- **TaskEvent**: Represents a domain event published to Kafka — event type, task snapshot, user ID, timestamp, correlation ID.
- **RecurrenceSeries**: Groups recurring task instances under a common series ID, enabling bulk edit/delete of future occurrences.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priority and at least one tag to a task within 10 seconds of opening the task form.
- **SC-002**: Search results for any keyword query are displayed in under 1 second for task lists up to 10,000 tasks per user.
- **SC-003**: Filtered and sorted task lists reflect changes within 500 milliseconds of applying filter/sort criteria.
- **SC-004**: Recurring task instances are automatically created within 60 seconds of the triggering task being marked complete.
- **SC-005**: Reminder notifications are delivered within 2 minutes of the scheduled reminder time under normal load.
- **SC-006**: 100% of task lifecycle events (create, update, complete, delete, reminder) are published to the event bus with no data loss under normal operating conditions.
- **SC-007**: The system continues to accept and process task operations with no user-visible errors when the event bus is temporarily unavailable (graceful degradation verified).
- **SC-008**: All inter-service calls are observable via distributed tracing with end-to-end trace context propagated through Dapr.
- **SC-009**: Zero application credentials (database, JWT, Kafka) are stored in environment files when running on Dapr-enabled infrastructure.
- **SC-010**: Users can complete the "create recurring task with due date and reminder" workflow in under 3 minutes on first use.

---

## Assumptions

- Reminder delivery is in-app (UI notification) for this phase; email/SMS delivery is out of scope.
- Tags are free-form strings scoped per user; there is no shared global tag taxonomy.
- Recurrence rules follow the iCal RRULE standard (RFC 5545) for maximum flexibility and tooling compatibility.
- Dapr will be used in self-hosted mode for local development and Kubernetes mode for production deployment.
- Kafka is the underlying transport for Dapr pubsub component; the Dapr abstraction means application code is not directly coupled to Kafka client libraries.
- The existing PostgreSQL (Neon) database is used for persistent state; Dapr state store is used for ephemeral/distributed state where appropriate.
- Pagination uses cursor-based pagination for performance with large result sets.
- The notification service that consumes `task.reminder` Kafka events is considered in-scope only as a Dapr subscriber endpoint; the UI delivery mechanism builds on existing WebSocket/polling patterns.

---

## Out of Scope

- Email or SMS reminder notifications (in-app only for this phase).
- Shared/collaborative tasks between multiple users.
- Global shared tag library across users.
- Analytics dashboard or reporting on task completion trends.
- Kafka cluster provisioning (assumes an existing Kafka instance is available).
- Dapr control plane installation (assumes Dapr is pre-installed in the target environment).
- Mobile push notifications.
- Calendar integrations (Google Calendar, Outlook).
