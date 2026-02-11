---
id: 5
title: Implement PATCH endpoint for toggle task completion
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-fullstack-app
branch: 002-backend-api-db
user: developer
command: T045 implementation
labels: ["backend", "api", "fastapi", "task-completion", "user-story-4"]
links:
  spec: specs/001-todo-fullstack-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/routes/tasks.py
  - specs/001-todo-fullstack-app/tasks.md
tests:
  - Manual testing required for PATCH /api/{user_id}/tasks/{task_id}/complete endpoint
---

## Prompt

Implement Phase 6 User Story 4 backend toggle completion task (T045):

**Context**: Building Todo Full-Stack Web Application. User Story 3 (Update/Delete) is complete. Now implementing User Story 4: Toggle Task Completion.

**Your Task**:
T045: Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/src/api/routes/tasks.py to toggle is_completed

**Reference Documents**:
- Spec: specs/001-todo-fullstack-app/spec.md
- Data model: specs/001-todo-fullstack-app/data-model.md

**User Story 4 Requirements**:
Authenticated users must be able to mark tasks as complete/incomplete with a simple toggle action.

**PATCH /api/{user_id}/tasks/{task_id}/complete Endpoint Requirements**:
- Protected endpoint (requires JWT authentication)
- Verify user_id in URL matches authenticated user_id (403 if mismatch)
- Query task by task_id with ownership verification
- Return 404 if task not found or doesn't belong to user
- Toggle is_completed field (True → False, False → True)
- Update updated_at timestamp automatically
- Return updated task with 200 OK status
- Status codes: 200 OK (success), 401 Unauthorized (no token), 403 Forbidden (user_id mismatch), 404 Not Found (task doesn't exist or not owner)

**Toggle Logic**:
```python
# Simple toggle - flip the boolean value
task.is_completed = not task.is_completed
task.updated_at = datetime.utcnow()
```

**Security Requirements**:
- Same ownership verification as update/delete endpoints
- Verify task belongs to authenticated user
- Return 404 for non-existent or other users' tasks

**Output File**:
- backend/src/api/routes/tasks.py (updated with PATCH endpoint)

After completing this task, mark T045 as [X] in specs/001-todo-fullstack-app/tasks.md

## Response snapshot

Successfully implemented the PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/src/api/routes/tasks.py with the following features:

**Implementation Details**:
1. Created new PATCH endpoint at route "/{user_id}/tasks/{task_id}/complete"
2. Implemented JWT authentication via get_current_user dependency
3. Added user_id verification using verify_user_access helper
4. Implemented ownership verification by querying with both task_id and current_user.id
5. Implemented toggle logic: task.is_completed = not task.is_completed
6. Automatic updated_at timestamp update
7. Returns 200 OK with updated TaskResponse on success
8. Returns appropriate error codes: 401 (no token), 403 (user_id mismatch), 404 (task not found/not owner)

**Security Features**:
- JWT token required for authentication
- user_id in URL must match authenticated user (prevents cross-user access)
- Task query filtered by current_user.id (prevents toggling other users' tasks)
- Returns 404 for non-existent tasks (prevents task ID enumeration)
- Comprehensive logging for security audit trail

**Code Quality**:
- Comprehensive docstring with security flow, args, returns, raises, examples
- Consistent with existing endpoint patterns (update/delete)
- Type hints for all parameters
- OpenAPI documentation with response examples
- Follows FastAPI best practices

**Files Modified**:
- backend/src/api/routes/tasks.py: Added toggle_task_completion function (lines 494-619)
- specs/001-todo-fullstack-app/tasks.md: Marked T045 as completed [X]

## Outcome

- ✅ Impact: PATCH endpoint for toggling task completion status implemented with full security and ownership verification
- 🧪 Tests: Manual testing required - test with valid JWT token, verify toggle behavior, test ownership verification, test error cases (401, 403, 404)
- 📁 Files: Modified backend/src/api/routes/tasks.py (added 126 lines), updated specs/001-todo-fullstack-app/tasks.md
- 🔁 Next prompts: Implement T046-T048 (frontend toggle UI components and API integration)
- 🧠 Reflection: Implementation follows established patterns from update/delete endpoints, ensuring consistency across the API. Toggle logic is simple and idempotent.

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation follows proven patterns from previous endpoints
- Graders run and results (PASS/FAIL): Manual testing pending
- Prompt variant (if applicable): Standard implementation prompt with clear requirements
- Next experiment (smallest change to try): Test endpoint with curl/Postman to verify toggle behavior and security
