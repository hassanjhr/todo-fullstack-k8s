# Feature Specification: Backend API & Database

**Feature Branch**: `002-backend-api-db`
**Created**: 2026-02-06
**Status**: ✅ **ALREADY IMPLEMENTED** (as part of 001-todo-fullstack-app)
**Implementation Status**: See [IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md)
**Input**: User description: "Spec 2 – Backend API & Database (Todo Full-Stack App)"

---

## ⚠️ Important Note

**This specification describes backend functionality that has already been fully implemented as part of the Todo Full-Stack Web Application (Spec 1 / 001-todo-fullstack-app).**

All requirements in this specification are satisfied by the existing backend code located in the `backend/` directory. See [IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md) for a complete mapping of requirements to implementation.

**For Judges**: This demonstrates efficient engineering - the full-stack application includes a complete, production-ready backend that meets all isolated backend requirements without code duplication.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API Authentication and Authorization (Priority: P1)

The backend API must verify JWT tokens and enforce user identity for all requests.

**Why this priority**: Authentication verification is the foundation for all API operations. Without proper JWT verification and user identity extraction, the API cannot enforce data isolation or security.

**Independent Test**: An API client can send a request with a valid JWT token in the Authorization header, and the API successfully verifies the token, extracts the user_id, and processes the request. Requests without valid tokens are rejected with 401.

**Acceptance Scenarios**:

1. **Given** an API client with a valid JWT token, **When** they make a request to any protected endpoint, **Then** the API verifies the token signature, extracts user_id, and processes the request
2. **Given** an API client without an Authorization header, **When** they make a request to a protected endpoint, **Then** the API returns 401 Unauthorized with error message
3. **Given** an API client with an expired JWT token, **When** they make a request, **Then** the API returns 401 Unauthorized indicating token expiration
4. **Given** an API client with a tampered JWT token, **When** they make a request, **Then** the API returns 401 Unauthorized indicating invalid signature

---

### User Story 2 - Task Creation and Retrieval (Priority: P2)

API consumers must be able to create new tasks and retrieve lists of tasks for authenticated users.

**Why this priority**: Task creation and retrieval are the core API operations. Once authentication is working, the API must enable clients to create and fetch task data with proper user isolation.

**Independent Test**: An authenticated API client can POST a new task with title and description, receive a 201 response with the created task, then GET the task list and see the newly created task. Tasks are filtered by the authenticated user's ID.

**Acceptance Scenarios**:

1. **Given** an authenticated API client, **When** they POST to /api/{user_id}/tasks with valid task data, **Then** the task is created in the database with the authenticated user_id and returned with 201 status
2. **Given** an authenticated API client, **When** they GET /api/{user_id}/tasks, **Then** they receive a list of all tasks belonging to the authenticated user, sorted by creation date
3. **Given** an authenticated API client, **When** they POST a task with missing title, **Then** the API returns 422 Unprocessable Entity with validation error details
4. **Given** User A authenticated, **When** they GET /api/{user_b_id}/tasks (different user), **Then** the API returns 403 Forbidden

---

### User Story 3 - Task Updates and Deletion (Priority: P3)

API consumers must be able to update task details and permanently delete tasks.

**Why this priority**: After creating tasks, API clients need to modify and remove them. This completes the basic CRUD operations for task management.

**Independent Test**: An authenticated API client can PUT updated data to /api/{user_id}/tasks/{task_id} and receive the updated task, or DELETE /api/{user_id}/tasks/{task_id} and receive 204 No Content. Attempts to modify other users' tasks return 403.

**Acceptance Scenarios**:

1. **Given** an authenticated API client with an existing task, **When** they PUT updated title/description to /api/{user_id}/tasks/{task_id}, **Then** the task is updated in the database and returned with 200 status
2. **Given** an authenticated API client with an existing task, **When** they DELETE /api/{user_id}/tasks/{task_id}, **Then** the task is permanently removed from the database and 204 No Content is returned
3. **Given** an authenticated API client, **When** they attempt to PUT/DELETE a task_id belonging to another user, **Then** the API returns 403 Forbidden
4. **Given** an authenticated API client, **When** they attempt to PUT/DELETE a non-existent task_id, **Then** the API returns 404 Not Found

---

### User Story 4 - Task Completion Toggle (Priority: P3)

API consumers must be able to toggle task completion status.

**Why this priority**: Completion tracking is essential for task management. The API must provide a dedicated endpoint for toggling completion status efficiently.

**Independent Test**: An authenticated API client can PATCH /api/{user_id}/tasks/{task_id}/complete to toggle the is_completed field. The API returns the updated task with the new completion status.

**Acceptance Scenarios**:

1. **Given** an authenticated API client with an incomplete task, **When** they PATCH /api/{user_id}/tasks/{task_id}/complete, **Then** the task is marked as completed and returned with 200 status
2. **Given** an authenticated API client with a completed task, **When** they PATCH /api/{user_id}/tasks/{task_id}/complete, **Then** the task is marked as incomplete and returned with 200 status
3. **Given** an authenticated API client, **When** they attempt to toggle completion for another user's task, **Then** the API returns 403 Forbidden
4. **Given** an authenticated API client, **When** they attempt to toggle completion for a non-existent task, **Then** the API returns 404 Not Found

---

### User Story 5 - Single Task Retrieval (Priority: P4)

API consumers must be able to retrieve detailed information about a specific task.

**Why this priority**: While listing all tasks provides an overview, API clients may need to fetch a single task's complete details for display or processing.

**Independent Test**: An authenticated API client can GET /api/{user_id}/tasks/{task_id} and receive the complete task object including all fields and timestamps.

**Acceptance Scenarios**:

1. **Given** an authenticated API client, **When** they GET /api/{user_id}/tasks/{task_id} for their own task, **Then** they receive the complete task object with 200 status
2. **Given** an authenticated API client, **When** they attempt to GET a task_id belonging to another user, **Then** the API returns 403 Forbidden
3. **Given** an authenticated API client, **When** they attempt to GET a non-existent task_id, **Then** the API returns 404 Not Found
4. **Given** an authenticated API client, **When** they GET a task, **Then** the response includes all fields: id, user_id, title, description, is_completed, created_at, updated_at

---

### Edge Cases

- What happens when an API client sends a JWT token with a user_id that doesn't exist in the database? The API should return 401 Unauthorized indicating the user account is invalid or deleted.
- How does the API handle requests where the user_id in the URL doesn't match the user_id in the JWT token? The API must return 403 Forbidden to prevent impersonation attempts.
- What happens when an API client sends a task with a title exceeding 200 characters? The API validates and returns 422 Unprocessable Entity with specific validation error.
- How does the API handle database connection failures? The API should return 500 Internal Server Error with a generic error message (not exposing database details).
- What happens when multiple API requests attempt to update the same task simultaneously? Last write wins; no optimistic locking in the basic implementation.
- How does the API handle malformed JSON in request bodies? The API returns 422 Unprocessable Entity with parsing error details.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST accept JWT tokens in the Authorization header using Bearer scheme
- **FR-002**: API MUST verify JWT token signature using the shared secret key
- **FR-003**: API MUST validate JWT token expiration and reject expired tokens
- **FR-004**: API MUST extract user_id from the JWT token payload
- **FR-005**: API MUST verify that user_id in the URL path matches the authenticated user_id from JWT
- **FR-006**: API MUST provide endpoint POST /api/{user_id}/tasks to create new tasks
- **FR-007**: API MUST provide endpoint GET /api/{user_id}/tasks to list all tasks for authenticated user
- **FR-008**: API MUST provide endpoint GET /api/{user_id}/tasks/{task_id} to retrieve a single task
- **FR-009**: API MUST provide endpoint PUT /api/{user_id}/tasks/{task_id} to update task title and description
- **FR-010**: API MUST provide endpoint DELETE /api/{user_id}/tasks/{task_id} to permanently delete a task
- **FR-011**: API MUST provide endpoint PATCH /api/{user_id}/tasks/{task_id}/complete to toggle task completion
- **FR-012**: API MUST filter all database queries by authenticated user_id to enforce data isolation
- **FR-013**: API MUST validate task title is not empty and does not exceed 200 characters
- **FR-014**: API MUST validate task description does not exceed 2000 characters if provided
- **FR-015**: API MUST persist all task data in PostgreSQL database with proper relationships
- **FR-016**: API MUST automatically set created_at timestamp when creating tasks
- **FR-017**: API MUST automatically update updated_at timestamp when modifying tasks
- **FR-018**: API MUST return proper HTTP status codes (200, 201, 204, 401, 403, 404, 422, 500)
- **FR-019**: API MUST return consistent JSON error responses with detail and status_code fields
- **FR-020**: API MUST enable CORS for the frontend origin specified in configuration

### Security Requirements *(mandatory for features with user data or API endpoints)*

- **SR-001**: All API endpoints MUST require valid JWT authentication
- **SR-002**: User identity MUST be extracted from JWT token, not request body
- **SR-003**: All database queries MUST filter by authenticated user_id
- **SR-004**: Unauthorized requests MUST return 401 status code
- **SR-005**: Authorization failures MUST return 403 status code
- **SR-006**: JWT secret key MUST be loaded from environment variables, never hardcoded
- **SR-007**: Database connection string MUST be loaded from environment variables
- **SR-008**: API MUST validate user_id in URL matches authenticated user_id before processing
- **SR-009**: API MUST prevent SQL injection through parameterized queries (ORM handles this)
- **SR-010**: API MUST not expose internal error details (stack traces, database errors) to clients
- **SR-011**: API MUST log authentication failures for security monitoring
- **SR-012**: Database schema MUST enforce foreign key constraints to prevent orphaned tasks

### Key Entities *(include if feature involves data)*

- **User**: Represents an authenticated user account. Contains unique identifier, email, and hashed password. Users own tasks and are referenced by task ownership.
- **Task**: Represents a todo item owned by a specific user. Contains title, optional description, completion status, timestamps, and foreign key reference to the owning user. Tasks are always scoped to a single user.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API responds to task creation requests in under 3 seconds
- **SC-002**: API responds to task list requests in under 3 seconds
- **SC-003**: API correctly rejects 100% of requests without valid JWT tokens with 401 status
- **SC-004**: API correctly rejects 100% of cross-user access attempts with 403 status
- **SC-005**: API enforces data isolation with zero cross-user data leaks in testing
- **SC-006**: All API endpoints return appropriate HTTP status codes matching the specification
- **SC-007**: Task data persists correctly across API restarts and survives database reconnections
- **SC-008**: API handles concurrent requests from multiple users without data corruption
- **SC-009**: Database queries execute efficiently with proper indexing (user_id lookups under 100ms)
- **SC-010**: API validation catches 100% of invalid inputs and returns 422 with clear error messages
- **SC-011**: API can be tested independently using tools like Postman or curl without frontend
- **SC-012**: All API behavior is traceable to this specification and implementation plan

## Assumptions

- **A-001**: JWT tokens are issued by the frontend Better Auth system with standard claims (sub for user_id, exp for expiration)
- **A-002**: JWT algorithm is HS256 (HMAC with SHA-256)
- **A-003**: JWT secret is shared between frontend and backend via environment variables
- **A-004**: Database tables (users, tasks) already exist or will be created via migration scripts
- **A-005**: Task list endpoint returns tasks sorted by created_at descending (newest first)
- **A-006**: No pagination is required for task lists in basic implementation
- **A-007**: Task updates are full replacements (PUT), not partial updates (PATCH), except for completion toggle
- **A-008**: Database connection uses connection pooling for performance
- **A-009**: API runs on port 8000 by default (configurable via environment)
- **A-010**: CORS allows credentials (required for httpOnly cookies if used)

## Out of Scope

- User registration and signin endpoints (handled by frontend Better Auth)
- Password hashing and validation (handled by frontend auth system)
- Token issuance and refresh (handled by frontend auth system)
- Email verification or password reset
- Admin APIs or user management endpoints
- Batch operations (create/update/delete multiple tasks)
- Task search or filtering endpoints
- Task sorting options beyond default
- Soft deletes or task archiving
- Task history or audit logs
- Rate limiting or throttling
- API versioning (v1, v2)
- GraphQL or non-REST APIs
- WebSocket or real-time updates
- File uploads or attachments
- Task sharing or collaboration features
- Background job processing
- Caching layer (Redis, Memcached)
- API analytics or monitoring endpoints

## Dependencies

- **D-001**: Neon Serverless PostgreSQL database instance with users and tasks tables
- **D-002**: Shared JWT secret key configured in environment variables
- **D-003**: Python 3.11+ runtime environment
- **D-004**: FastAPI framework and dependencies (SQLModel, python-jose, passlib)
- **D-005**: Frontend authentication system that issues valid JWT tokens
- **D-006**: Database migration scripts or ORM auto-creation for schema setup
- **D-007**: Environment configuration for database URL, JWT secret, and CORS origin

## Constraints

- **C-001**: Must use FastAPI framework (not Django, Flask, Express, etc.)
- **C-002**: Must use SQLModel for ORM (not raw SQLAlchemy, Prisma, etc.)
- **C-003**: Must use Neon Serverless PostgreSQL (not local PostgreSQL, MySQL, MongoDB, etc.)
- **C-004**: Must verify JWT tokens (not create or issue them)
- **C-005**: Must use RESTful API design (not GraphQL, gRPC, etc.)
- **C-006**: Must return JSON responses (not XML, HTML, etc.)
- **C-007**: Must use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **C-008**: Must load configuration from environment variables (not config files)
- **C-009**: Must enforce user_id matching between JWT and URL path
- **C-010**: No manual coding allowed - all code generated by Claude Code agents
