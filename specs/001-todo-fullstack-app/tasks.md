---

description: "Task list for Todo Full-Stack Web Application implementation"
---

# Tasks: Todo Full-Stack Web Application

**Input**: Design documents from `/specs/001-todo-fullstack-app/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Manual testing approach - no automated test tasks included

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Frontend uses Next.js 16+ App Router structure
- Backend uses FastAPI with modular structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (src/, tests/, requirements.txt, .env.example, README.md)
- [ ] T002 Create frontend directory structure (src/app/, src/components/, src/lib/, package.json, .env.local.example, README.md)
- [ ] T003 [P] Initialize Python virtual environment and install FastAPI dependencies in backend/requirements.txt
- [ ] T004 [P] Initialize Next.js project with TypeScript and TailwindCSS in frontend/
- [ ] T005 [P] Create root .env.example with shared configuration template
- [ ] T006 [P] Create root README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Configure Neon PostgreSQL connection in backend/src/database.py with asyncpg driver
- [X] T008 Create database tables using SQL migration script (users and tasks tables with indexes)
- [X] T009 [P] Create User SQLModel in backend/src/models/user.py with id, email, hashed_password, created_at
- [X] T010 [P] Create Task SQLModel in backend/src/models/task.py with id, user_id (FK), title, description, is_completed, created_at, updated_at
- [X] T011 [P] Implement password hashing utilities in backend/src/utils/security.py using passlib/bcrypt
- [X] T012 [P] Implement JWT token creation and verification utilities in backend/src/utils/security.py using python-jose
- [X] T013 Create JWT authentication dependency in backend/src/api/deps.py (get_current_user function)
- [X] T014 [P] Configure CORS middleware in backend/src/main.py for frontend origin
- [X] T015 [P] Create FastAPI application entry point in backend/src/main.py with basic configuration
- [X] T016 [P] Create environment configuration loader in backend/src/config.py
- [X] T017 [P] Configure Better Auth in frontend/src/lib/auth.ts with JWT plugin
- [X] T018 [P] Create API client utility in frontend/src/lib/api.ts with JWT token injection
- [X] T019 [P] Create TypeScript types in frontend/src/lib/types.ts for User and Task entities

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and sign in securely with JWT authentication

**Independent Test**: User can visit the app, create account with email/password, sign in, receive JWT token, and access dashboard

### Implementation for User Story 1

- [X] T020 [P] [US1] Create User Pydantic schemas in backend/src/schemas/user.py (SignupRequest, SigninRequest, UserResponse, AuthResponse)
- [X] T021 [US1] Implement signup endpoint POST /api/auth/signup in backend/src/api/routes/auth.py
- [X] T022 [US1] Implement signin endpoint POST /api/auth/signin in backend/src/api/routes/auth.py
- [X] T023 [US1] Register auth routes in backend/src/main.py
- [X] T024 [P] [US1] Create signup page in frontend/src/app/(auth)/signup/page.tsx with form and validation
- [X] T025 [P] [US1] Create signin page in frontend/src/app/(auth)/signin/page.tsx with form and validation
- [X] T026 [P] [US1] Create root layout in frontend/src/app/layout.tsx with Better Auth provider
- [X] T027 [P] [US1] Create landing page in frontend/src/app/page.tsx with navigation to signup/signin
- [X] T028 [US1] Create AuthGuard component in frontend/src/components/AuthGuard.tsx for protected routes
- [X] T029 [US1] Create protected dashboard layout in frontend/src/app/(protected)/layout.tsx with AuthGuard

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P2)

**Goal**: Enable authenticated users to create new tasks and view their task list

**Independent Test**: Authenticated user can click "Add Task", enter title/description, save, and see task appear in list showing only their tasks

### Implementation for User Story 2

- [X] T030 [P] [US2] Create Task Pydantic schemas in backend/src/schemas/task.py (TaskCreateRequest, TaskResponse)
- [X] T031 [US2] Implement GET /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py with user_id filtering
- [X] T032 [US2] Implement POST /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py with user_id validation
- [X] T033 [US2] Register task routes in backend/src/main.py
- [X] T034 [P] [US2] Create dashboard page in frontend/src/app/(protected)/dashboard/page.tsx with task list display
- [X] T035 [P] [US2] Create TaskList component in frontend/src/components/TaskList.tsx to display tasks
- [X] T036 [P] [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx for individual task display
- [X] T037 [P] [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx for create/edit with validation
- [X] T038 [US2] Integrate API calls in dashboard page to fetch and create tasks with JWT token

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update and Delete Tasks (Priority: P3)

**Goal**: Enable authenticated users to edit task details and delete tasks

**Independent Test**: Authenticated user can click "Edit" on task, modify title/description, save changes, and see updated task. Can also delete tasks permanently.

### Implementation for User Story 3

- [X] T039 [P] [US3] Add TaskUpdateRequest schema to backend/src/schemas/task.py
- [X] T040 [US3] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py with ownership verification
- [X] T041 [US3] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py with ownership verification
- [X] T042 [P] [US3] Add edit mode to TaskForm component in frontend/src/components/TaskForm.tsx
- [X] T043 [P] [US3] Add edit and delete buttons to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T044 [US3] Implement update and delete API calls in dashboard page with JWT token and error handling

**Checkpoint**: All CRUD operations should now be independently functional

---

## Phase 6: User Story 4 - Toggle Task Completion (Priority: P3)

**Goal**: Enable authenticated users to mark tasks as complete/incomplete

**Independent Test**: Authenticated user can click checkbox/toggle next to task to mark complete (with visual change), click again to mark incomplete

### Implementation for User Story 4

- [X] T045 [US4] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/src/api/routes/tasks.py to toggle is_completed
- [X] T046 [P] [US4] Add completion toggle checkbox to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T047 [P] [US4] Add completed styling (strikethrough) to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T048 [US4] Implement toggle completion API call in TaskItem component with optimistic UI update

**Checkpoint**: Task completion tracking should work independently

---

## Phase 7: User Story 5 - View Single Task Details (Priority: P4)

**Goal**: Enable authenticated users to view full details of a single task

**Independent Test**: Authenticated user can click on task in list to navigate to detail page showing full information (title, description, dates, status, action buttons)

### Implementation for User Story 5

- [X] T049 [US5] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py with ownership verification
- [X] T050 [P] [US5] Create task detail page in frontend/src/app/(protected)/tasks/[id]/page.tsx
- [X] T051 [P] [US5] Add click handler to TaskItem component to navigate to detail page
- [X] T052 [US5] Implement API call to fetch single task in detail page with JWT token and error handling

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T053 [P] Add loading states to all API calls in frontend components
- [X] T054 [P] Add error handling and error messages to all frontend forms
- [X] T055 [P] Add empty state message to TaskList component when no tasks exist
- [X] T056 [P] Implement 401 redirect to signin page when JWT token expires
- [X] T057 [P] Add responsive styling for mobile devices (320px minimum width) using TailwindCSS
- [X] T058 [P] Add signout functionality to dashboard layout
- [X] T059 [P] Update backend README.md with API documentation and setup instructions
- [X] T060 [P] Update frontend README.md with component documentation and setup instructions
- [X] T061 Validate all environment variables are documented in .env.example files
- [ ] T062 Manual testing: Test complete authentication flow (signup, signin, signout, token expiration)
- [ ] T063 Manual testing: Test all CRUD operations with multiple users to verify data isolation
- [ ] T064 Manual testing: Test responsive design on desktop and mobile viewports

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
- User stories can then proceed in parallel (if staffed)
- Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for authentication context
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US2 for task creation
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Requires US2 for task display
- **User Story 5 (P4)**: Can start after Foundational (Phase 2) - Requires US2 for task data

### Within Each User Story

- Backend schemas before endpoints
- Backend endpoints before frontend integration
- Frontend components can be built in parallel
- API integration after both backend and frontend components exist

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, user stories can be worked on in parallel by different agents
- Within each user story, tasks marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch backend schemas and frontend components in parallel:
Task: "Create Task Pydantic schemas in backend/src/schemas/task.py"
Task: "Create TaskList component in frontend/src/components/TaskList.tsx"
Task: "Create TaskItem component in frontend/src/components/TaskItem.tsx"
Task: "Create TaskForm component in frontend/src/components/TaskForm.tsx"

# Then implement endpoints and integration sequentially:
Task: "Implement GET /api/{user_id}/tasks endpoint"
Task: "Implement POST /api/{user_id}/tasks endpoint"
Task: "Integrate API calls in dashboard page"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test authentication flow independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Agent Assignment Strategy

**Phase 2 (Foundational)**:
- T007-T010: `neon-db-manager` (database and models)
- T011-T016: `fastapi-backend-dev` (backend infrastructure)
- T017-T019: `nextjs-ui-builder` (frontend infrastructure)

**Phase 3 (User Story 1 - Authentication)**:
- T020-T023: `auth-security-handler` (authentication endpoints)
- T024-T029: `nextjs-ui-builder` (authentication UI)

**Phase 4 (User Story 2 - Create and View Tasks)**:
- T030-T033: `fastapi-backend-dev` (task API endpoints)
- T034-T038: `nextjs-ui-builder` (task UI components)

**Phase 5 (User Story 3 - Update and Delete)**:
- T039-T041: `fastapi-backend-dev` (update/delete endpoints)
- T042-T044: `nextjs-ui-builder` (edit/delete UI)

**Phase 6 (User Story 4 - Toggle Completion)**:
- T045: `fastapi-backend-dev` (completion toggle endpoint)
- T046-T048: `nextjs-ui-builder` (completion toggle UI)

**Phase 7 (User Story 5 - View Details)**:
- T049: `fastapi-backend-dev` (single task endpoint)
- T050-T052: `nextjs-ui-builder` (task detail page)

**Phase 8 (Polish)**:
- T053-T064: Mixed agents based on task domain

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
