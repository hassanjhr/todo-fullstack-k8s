---
id: 006
title: Implement GET Single Task Endpoint with Ownership Verification
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-fullstack-app
branch: 001-todo-fullstack-app
user: hassanjhr
command: /sp.implement
labels: ["backend", "api", "fastapi", "security", "user-story-5", "T049"]
links:
  spec: specs/001-todo-fullstack-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/routes/tasks.py
  - specs/001-todo-fullstack-app/tasks.md
tests:
  - Manual testing required: Test GET /api/{user_id}/tasks/{task_id} with valid JWT token
  - Manual testing required: Test 404 response for non-existent task
  - Manual testing required: Test 403 response for user_id mismatch
  - Manual testing required: Test 404 response when accessing another user's task
---

## Prompt

Implement Phase 7 User Story 5 backend single task detail task (T049):

**Context**: Building Todo Full-Stack Web Application. User Stories 1-4 are complete. Now implementing User Story 5: View Single Task Details.

**Your Task**:
T049: Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py with ownership verification

**Reference Documents**:
- Spec: specs/001-todo-fullstack-app/spec.md
- Data model: specs/001-todo-fullstack-app/data-model.md

**User Story 5 Requirements**:
Authenticated users must be able to view full details of a single task including all fields and timestamps.

**GET /api/{user_id}/tasks/{task_id} Endpoint Requirements**:
- Protected endpoint (requires JWT authentication)
- Verify user_id in URL matches authenticated user_id (403 if mismatch)
- Query task by task_id with ownership verification
- Return 404 if task not found or doesn't belong to user
- Return complete task object with all fields
- Status codes: 200 OK (success), 401 Unauthorized (no token), 403 Forbidden (user_id mismatch), 404 Not Found (task doesn't exist or not owner)

**Response Format**:
Return TaskResponse with all fields:
- id (UUID)
- user_id (UUID)
- title (string)
- description (string | null)
- is_completed (boolean)
- created_at (datetime)
- updated_at (datetime)

**Security Requirements**:
- Same ownership verification pattern as other task endpoints
- Verify task belongs to authenticated user
- Return 404 for non-existent or other users' tasks (prevents enumeration)

**Output File**:
- backend/src/api/routes/tasks.py (updated with GET single task endpoint)

After completing this task, mark T049 as [X] in specs/001-todo-fullstack-app/tasks.md

## Response snapshot

Successfully implemented GET /api/{user_id}/tasks/{task_id} endpoint with the following features:

**Implementation Details**:
1. Added new endpoint at line 142-247 in backend/src/api/routes/tasks.py
2. Endpoint positioned logically after GET /tasks (list) and before POST /tasks (create)
3. Function name: `get_single_task()`
4. Route: `/{user_id}/tasks/{task_id}`
5. HTTP Method: GET
6. Response Model: TaskResponse
7. Status Code: 200 OK (success)

**Security Implementation**:
- JWT authentication via `get_current_user` dependency
- User ID verification via `verify_user_access()` function (403 if mismatch)
- Ownership verification in database query: `Task.user_id == current_user.id`
- Returns 404 for non-existent tasks (prevents enumeration attacks)
- Returns 404 for tasks belonging to other users (prevents information disclosure)

**Query Logic**:
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == current_user.id  # Ownership check
)
```

**Response Handling**:
- Returns complete TaskResponse with all fields (id, user_id, title, description, is_completed, created_at, updated_at)
- Uses Pydantic model validation: `TaskResponse.model_validate(task)`
- Includes comprehensive logging for debugging

**OpenAPI Documentation**:
- Summary: "Get single task"
- Description: "Retrieve full details of a single task (authenticated user must own the task)"
- Response examples for 200, 401, 403, 404 status codes
- Comprehensive docstring with security flow, args, returns, raises, and examples

**Task Tracking**:
- Marked T049 as completed [X] in specs/001-todo-fullstack-app/tasks.md

## Outcome

- ✅ Impact: Implemented GET single task endpoint for User Story 5, enabling users to view full task details with proper ownership verification
- 🧪 Tests: Manual testing required (4 test scenarios: valid request, non-existent task, user_id mismatch, other user's task)
- 📁 Files: Modified 2 files (backend/src/api/routes/tasks.py, specs/001-todo-fullstack-app/tasks.md)
- 🔁 Next prompts: Implement T050 (frontend task detail page), T051 (add click handler to TaskItem), T052 (API integration in detail page)
- 🧠 Reflection: Implementation follows established security patterns from existing endpoints (update, delete, toggle completion). Consistent error handling and logging. Ready for frontend integration.

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation followed existing patterns successfully
- Graders run and results (PASS/FAIL): Manual testing pending
- Prompt variant (if applicable): Standard implementation prompt with clear requirements
- Next experiment (smallest change to try): Consider adding query parameter for field selection (partial response) in future optimization
