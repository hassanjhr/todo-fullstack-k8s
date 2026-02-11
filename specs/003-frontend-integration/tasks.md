# Tasks: Frontend Application & Full-Stack Integration

**Input**: Design documents from `/specs/003-frontend-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` directory with Next.js App Router structure
- All source files under `frontend/`
- Components in `frontend/components/`
- Pages in `frontend/app/`
- Utilities in `frontend/lib/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Next.js 16+ project with TypeScript and Tailwind CSS in frontend/ directory
- [x] T002 Configure TypeScript with strict mode in frontend/tsconfig.json
- [x] T003 [P] Configure Tailwind CSS in frontend/tailwind.config.js
- [x] T004 [P] Create environment configuration files frontend/.env.local and frontend/.env.example
- [x] T005 Create project directory structure per plan.md (app/, components/, lib/, types/)
- [x] T006 [P] Configure Next.js in frontend/next.config.js
- [x] T007 [P] Set up global styles with Tailwind imports in frontend/app/globals.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Copy TypeScript type definitions from contracts/types.ts to frontend/types/index.ts
- [x] T009 [P] Create User type definition in frontend/types/user.ts
- [x] T010 [P] Create Task type definition in frontend/types/task.ts
- [x] T011 [P] Create API response types in frontend/types/api.ts
- [x] T012 Implement base API client with fetch wrapper in frontend/lib/api/client.ts
- [x] T013 [P] Implement error handling utilities in frontend/lib/utils/errors.ts
- [x] T014 [P] Implement form validation utilities in frontend/lib/utils/validation.ts
- [x] T015 Create root layout with providers in frontend/app/layout.tsx
- [x] T016 Create landing page with redirect logic in frontend/app/page.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with email and password

**Independent Test**: Navigate to /signup, enter valid email and password, submit form, verify account creation and redirect to /signin with success message

### Implementation for User Story 1

- [x] T017 [P] [US1] Create AuthForm component in frontend/components/auth/AuthForm.tsx
- [x] T018 [P] [US1] Implement auth API client functions in frontend/lib/api/auth.ts
- [x] T019 [US1] Create signup page in frontend/app/(auth)/signup/page.tsx
- [x] T020 [US1] Add client-side validation for email format in AuthForm
- [x] T021 [US1] Add client-side validation for password requirements in AuthForm
- [x] T022 [US1] Implement error display for validation failures in AuthForm
- [x] T023 [US1] Handle backend error responses (422, 400) in signup flow
- [x] T024 [US1] Implement success message and redirect to /signin after signup

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User Authentication (Priority: P1)

**Goal**: Enable registered users to sign in and access their task dashboard with persistent sessions

**Independent Test**: Use credentials from registered account, sign in, verify redirect to /dashboard, refresh page and verify session persists, try accessing /dashboard without auth and verify redirect to /signin

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement token storage utilities in frontend/lib/auth/token.ts
- [x] T026 [P] [US2] Create auth context provider in frontend/lib/auth/context.tsx
- [x] T027 [P] [US2] Create auth hooks (useAuth, useRequireAuth) in frontend/lib/auth/hooks.ts
- [x] T028 [US2] Create signin page in frontend/app/(auth)/signin/page.tsx
- [x] T029 [US2] Implement signin flow with token storage in auth context
- [x] T030 [US2] Implement session persistence with localStorage
- [x] T031 [US2] Create Next.js middleware for route protection in frontend/middleware.ts
- [x] T032 [US2] Create protected dashboard layout with auth guard in frontend/app/dashboard/layout.tsx
- [x] T033 [US2] Handle 401 Unauthorized responses by clearing token and redirecting to /signin
- [x] T034 [US2] Implement redirect logic for authenticated users accessing /signin or /signup
- [x] T035 [US2] Update root layout to wrap app with AuthProvider in frontend/app/layout.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can signup, signin, and access protected routes

---

## Phase 5: User Story 3 - Task Creation (Priority: P2)

**Goal**: Enable authenticated users to create new tasks

**Independent Test**: Sign in, navigate to /dashboard, enter task title in creation form, submit, verify task appears in list immediately

### Implementation for User Story 3

- [x] T036 [P] [US3] Implement task API client functions in frontend/lib/api/tasks.ts
- [x] T037 [P] [US3] Create TaskForm component in frontend/components/tasks/TaskForm.tsx
- [x] T038 [US3] Create basic dashboard page structure in frontend/app/dashboard/page.tsx
- [x] T039 [US3] Integrate TaskForm into dashboard page
- [x] T040 [US3] Add client-side validation for task title (required, non-empty)
- [x] T041 [US3] Implement createTask API call with Authorization header
- [x] T042 [US3] Handle successful task creation with optimistic UI update
- [x] T043 [US3] Handle task creation errors (401, 422, 500) with user-friendly messages
- [x] T044 [US3] Display success confirmation after task creation

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can signup, signin, and create tasks

---

## Phase 6: User Story 4 - Task Viewing and Management (Priority: P2)

**Goal**: Enable authenticated users to view all their tasks with loading and empty states

**Independent Test**: Sign in, view dashboard, verify all user's tasks are displayed, verify loading indicator during fetch, verify empty state message when no tasks exist

### Implementation for User Story 4

- [x] T045 [P] [US4] Create TaskList component in frontend/components/tasks/TaskList.tsx
- [x] T046 [P] [US4] Create TaskItem component in frontend/components/tasks/TaskItem.tsx
- [x] T047 [US4] Implement getTasks API call in dashboard page
- [x] T048 [US4] Add loading state with spinner during task fetch
- [x] T049 [US4] Display tasks in TaskList component
- [x] T050 [US4] Implement empty state message when no tasks exist
- [x] T051 [US4] Handle task fetch errors (401, 500) with error messages
- [x] T052 [US4] Verify user data isolation (only user's tasks displayed)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can signup, signin, create tasks, and view their task list

---

## Phase 7: User Story 5 - Task Updates (Priority: P2)

**Goal**: Enable authenticated users to update task titles and toggle completion status

**Independent Test**: Sign in, create task, edit task title and save, verify title updates immediately, toggle completion checkbox, verify visual state updates, refresh page and verify changes persist

### Implementation for User Story 5

- [x] T053 [US5] Add edit mode to TaskItem component for title editing
- [x] T054 [US5] Implement updateTask API call for title changes
- [x] T055 [US5] Add completion toggle checkbox to TaskItem component
- [x] T056 [US5] Implement updateTask API call for completion status
- [x] T057 [US5] Implement optimistic UI updates for task changes
- [x] T058 [US5] Handle update failures by reverting to previous state
- [x] T059 [US5] Display error messages for failed updates (401, 403, 404, 422)
- [x] T060 [US5] Add visual feedback for completed vs incomplete tasks

**Checkpoint**: At this point, User Stories 1-5 should all work independently - users can signup, signin, create, view, and update tasks

---

## Phase 8: User Story 6 - Task Deletion (Priority: P3)

**Goal**: Enable authenticated users to delete tasks with confirmation

**Independent Test**: Sign in, create task, click delete button, confirm deletion, verify task removed from list immediately

### Implementation for User Story 6

- [x] T061 [US6] Add delete button to TaskItem component
- [x] T062 [US6] Implement confirmation dialog for task deletion
- [x] T063 [US6] Implement deleteTask API call
- [x] T064 [US6] Implement optimistic UI update (remove from list immediately)
- [x] T065 [US6] Handle deletion failures by re-adding task to list
- [x] T066 [US6] Display error messages for failed deletions (401, 403, 404)
- [x] T067 [US6] Handle cancellation of deletion (task remains in list)

**Checkpoint**: At this point, User Stories 1-6 should all work independently - users have full CRUD functionality for tasks

---

## Phase 9: User Story 7 - Session Management (Priority: P3)

**Goal**: Enable authenticated users to sign out securely

**Independent Test**: Sign in, click signout button, verify redirect to /signin, verify token cleared, try accessing /dashboard and verify redirect to /signin, use back button and verify cannot access protected pages

### Implementation for User Story 7

- [x] T068 [P] [US7] Create SignOutButton component in frontend/components/auth/SignOutButton.tsx
- [x] T069 [US7] Implement signout function in auth context
- [x] T070 [US7] Clear token from localStorage on signout
- [x] T071 [US7] Clear auth state from context on signout
- [x] T072 [US7] Redirect to /signin after signout
- [x] T073 [US7] Verify protected routes redirect to /signin after signout
- [x] T074 [US7] Prevent back button access to protected pages after signout

**Checkpoint**: All user stories should now be independently functional - complete authentication and task management flow

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: UI components and improvements that affect multiple user stories

- [x] T075 [P] Create Button component with variants in frontend/components/ui/Button.tsx
- [x] T076 [P] Create LoadingSpinner component in frontend/components/ui/LoadingSpinner.tsx
- [x] T077 [P] Create ErrorMessage component in frontend/components/ui/ErrorMessage.tsx
- [x] T078 [P] Create Header component with navigation in frontend/components/layout/Header.tsx
- [x] T079 [P] Create Container component for consistent spacing in frontend/components/layout/Container.tsx
- [x] T080 Integrate Header component into dashboard layout
- [x] T081 Integrate SignOutButton into Header component
- [x] T082 Replace inline loading states with LoadingSpinner component
- [x] T083 Replace inline error messages with ErrorMessage component
- [x] T084 Apply responsive design with Tailwind breakpoints (320px - 1920px)
- [x] T085 Test responsive layout on mobile (320px), tablet (768px), and desktop (1920px)
- [x] T086 Ensure all touch targets are minimum 44x44px for mobile
- [x] T087 Verify all forms have proper validation and error display
- [x] T088 Verify all API errors display user-friendly messages (no raw error codes)
- [x] T089 Test full user flow: signup → signin → create task → view tasks → update task → delete task → signout
- [x] T090 Verify no console errors in browser
- [x] T091 Create README.md with setup instructions in frontend/
- [x] T092 Verify environment variables are documented in .env.example

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Registration**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Authentication**: Can start after Foundational (Phase 2) - No dependencies on other stories (but naturally follows US1 in user flow)
- **User Story 3 (P2) - Task Creation**: Depends on US2 (requires authentication) - Can start after US2 complete
- **User Story 4 (P2) - Task Viewing**: Depends on US2 (requires authentication) - Can start after US2 complete, works with US3
- **User Story 5 (P2) - Task Updates**: Depends on US4 (requires tasks to exist) - Can start after US4 complete
- **User Story 6 (P3) - Task Deletion**: Depends on US4 (requires tasks to exist) - Can start after US4 complete
- **User Story 7 (P3) - Session Management**: Depends on US2 (requires authentication) - Can start after US2 complete

### Within Each User Story

- Models/types before services
- Services before components
- Components before pages
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T006, T007 can run in parallel
- **Phase 2 (Foundational)**: T008-T014 can run in parallel (different files)
- **Phase 3 (US1)**: T017, T018 can run in parallel
- **Phase 4 (US2)**: T025, T026, T027 can run in parallel
- **Phase 5 (US3)**: T036, T037 can run in parallel
- **Phase 6 (US4)**: T045, T046 can run in parallel
- **Phase 10 (Polish)**: T075-T079 can run in parallel (different files)
- **User Stories**: After Foundational phase, US1 and US2 can be worked on in parallel by different developers

---

## Parallel Example: User Story 1 (Registration)

```bash
# Launch parallel tasks for User Story 1:
Task T017: "Create AuthForm component in frontend/components/auth/AuthForm.tsx"
Task T018: "Implement auth API client functions in frontend/lib/api/auth.ts"

# Then sequential tasks:
Task T019: "Create signup page in frontend/app/(auth)/signup/page.tsx" (depends on T017, T018)
Task T020-T024: Validation and error handling (sequential)
```

---

## Parallel Example: User Story 2 (Authentication)

```bash
# Launch parallel tasks for User Story 2:
Task T025: "Implement token storage utilities in frontend/lib/auth/token.ts"
Task T026: "Create auth context provider in frontend/lib/auth/context.tsx"
Task T027: "Create auth hooks in frontend/lib/auth/hooks.ts"

# Then sequential tasks:
Task T028: "Create signin page" (depends on T025-T027)
Task T029-T035: Auth flow implementation (sequential)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Authentication)
5. **STOP and VALIDATE**: Test signup and signin flow independently
6. Deploy/demo if ready

**Rationale**: US1 + US2 provide the authentication foundation. Users can register and sign in, which is the entry point for all other features.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP - Auth working!)
3. Add User Story 3 + 4 → Test independently → Deploy/Demo (Can create and view tasks!)
4. Add User Story 5 → Test independently → Deploy/Demo (Can update tasks!)
5. Add User Story 6 + 7 → Test independently → Deploy/Demo (Full CRUD + signout!)
6. Add Polish → Final demo-ready version
7. Each increment adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration)
   - Developer B: User Story 2 (Authentication) - can start in parallel
3. After US1 + US2 complete:
   - Developer A: User Story 3 (Task Creation)
   - Developer B: User Story 4 (Task Viewing)
   - Developer C: User Story 5 (Task Updates)
4. After US3-5 complete:
   - Developer A: User Story 6 (Task Deletion)
   - Developer B: User Story 7 (Session Management)
   - Developer C: Polish (UI components)
5. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 92 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 9 tasks
- Phase 3 (US1 - Registration): 8 tasks
- Phase 4 (US2 - Authentication): 11 tasks
- Phase 5 (US3 - Task Creation): 9 tasks
- Phase 6 (US4 - Task Viewing): 8 tasks
- Phase 7 (US5 - Task Updates): 8 tasks
- Phase 8 (US6 - Task Deletion): 7 tasks
- Phase 9 (US7 - Session Management): 7 tasks
- Phase 10 (Polish): 18 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 + Phase 4 (35 tasks) = Authentication working

**Full Feature**: All 92 tasks = Complete frontend with all user stories

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend paths all under `frontend/` directory
- Next.js App Router structure with `app/` directory
- TypeScript for type safety throughout
- Tailwind CSS for styling
- No tests included (not requested in specification)
- Focus on demo-ready UI with proper error handling and loading states
