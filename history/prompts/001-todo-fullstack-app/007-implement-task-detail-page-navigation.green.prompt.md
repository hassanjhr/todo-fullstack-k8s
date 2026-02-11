---
id: 007
title: Implement Task Detail Page and Navigation
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-fullstack-app
branch: 002-backend-api-db
user: hassanjhr
command: /sp.implement
labels: ["frontend", "nextjs", "task-detail", "navigation", "user-story-5"]
links:
  spec: specs/001-todo-fullstack-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/(protected)/tasks/[id]/page.tsx
  - frontend/src/components/TaskItem.tsx
  - specs/001-todo-fullstack-app/tasks.md
tests:
  - Manual testing: Navigate to task detail page from dashboard
  - Manual testing: Verify all task fields display correctly
  - Manual testing: Test error handling (404, 403, network errors)
  - Manual testing: Test back navigation to dashboard
  - Manual testing: Test action buttons (edit, delete, toggle completion)
  - Manual testing: Verify keyboard navigation (Enter key on task card)
---

## Prompt

Implement Phase 7 User Story 5 frontend task detail tasks (T050-T052):

**Context**: Building Todo Full-Stack Web Application. Backend single task endpoint (T049) is complete. Now implementing frontend UI for viewing single task details.

**Your Tasks**:
1. T050: Create task detail page in frontend/src/app/(protected)/tasks/[id]/page.tsx
2. T051: Add click handler to TaskItem component to navigate to detail page
3. T052: Implement API call to fetch single task in detail page with JWT token and error handling

**Reference Documents**:
- Spec: specs/001-todo-fullstack-app/spec.md

**User Story 5 Requirements**:
Authenticated users must be able to view full details of a single task including all fields and timestamps.

**Task Detail Page Requirements** (T050):
- Client Component (uses useState, useEffect for data fetching)
- Dynamic route using Next.js App Router: /tasks/[id]
- Fetch task on component mount using getTask() from lib/api.ts
- Display all task fields: Title, Description, Completion status, Created at, Updated at
- Show loading state while fetching
- Show error state if task not found (404) or access denied (403)
- Back button to return to dashboard
- Edit and Delete buttons (reuse existing handlers)
- Responsive layout with TailwindCSS

**TaskItem Click Handler Requirements** (T051):
- Add onClick handler to TaskItem component
- Navigate to /tasks/{task.id} when task is clicked
- Use Next.js useRouter for navigation
- Make entire task card clickable (not just title)
- Exclude buttons from click area (edit, delete, checkbox should not trigger navigation)
- Add cursor-pointer styling to indicate clickability
- Accessible keyboard navigation (Enter key)

**API Integration Requirements** (T052):
- Use getTask(userId, taskId) from lib/api.ts
- Extract userId from getCurrentUser() in lib/auth.ts
- Extract taskId from URL params (useParams hook)
- Include JWT token automatically (handled by api.ts)
- Handle errors: 401 (redirect to signin), 403 (access denied), 404 (not found), network errors

## Response snapshot

Successfully implemented User Story 5 frontend tasks (T050-T052) for task detail page and navigation:

**T050: Task Detail Page Created**
- File: `/frontend/src/app/(protected)/tasks/[id]/page.tsx`
- Client Component using useState, useEffect, useParams, useRouter
- Dynamic route pattern: `/tasks/[id]`
- Fetches task data on mount using getTask(userId, taskId)
- Displays all task fields with proper formatting:
  - Title (h1 with strikethrough if completed)
  - Completion badge (green badge for completed tasks)
  - Description (with null handling)
  - Created timestamp (relative + absolute format)
  - Updated timestamp (relative + absolute format)
  - Status indicator
- Loading state with skeleton UI
- Error handling for 404, 403, 401, and network errors
- Back button navigation to dashboard
- Action buttons: Toggle completion, Edit, Delete
- Responsive layout with semantic HTML (article, section, header)
- Accessibility: proper heading hierarchy, ARIA labels, keyboard navigation

**T051: TaskItem Click Handler Added**
- File: `/frontend/src/components/TaskItem.tsx` (updated)
- Added useRouter import from next/navigation
- Implemented handleTaskClick() to navigate to `/tasks/${task.id}`
- Implemented handleTaskKeyDown() for Enter key navigation
- Made entire task card clickable with onClick and onKeyDown handlers
- Added tabIndex={0} and role="button" for accessibility
- Added cursor-pointer and focus ring styling
- Prevented navigation on button clicks using e.stopPropagation():
  - Checkbox click (handleToggleComplete)
  - Edit button click (handleEdit)
  - Delete button click (handleDelete)
- Updated ARIA label to indicate clickability

**T052: API Integration Implemented**
- API call: getTask(userId, taskId) from lib/api.ts
- User ID extracted from getCurrentUser() in useEffect
- Task ID extracted from useParams() hook
- JWT token automatically included via authenticatedFetch in api.ts
- Error handling:
  - 401: Redirects to signin (handled by API client)
  - 403: Shows "Access denied" message with back button
  - 404: Shows "Task not found" message with back button
  - Network errors: Shows error message with retry button
- Loading state management with isLoading flag
- Error state management with error string

**Date Formatting**:
- Implemented formatDateTime(): Full date format (e.g., "February 7, 2026 at 1:30 PM")
- Implemented formatRelativeTime(): Relative format (e.g., "2 hours ago", "Yesterday")
- Both formats displayed for created_at and updated_at timestamps

**Navigation Flow**:
1. User clicks task card in dashboard
2. Navigate to /tasks/{id}
3. Fetch task details with loading state
4. Display full task information
5. User can toggle completion, edit, delete, or go back

**Component Architecture**:
- Server Component: None (detail page requires client-side interactivity)
- Client Component: TaskDetailPage (uses hooks for data fetching and navigation)
- Updated Component: TaskItem (added navigation functionality)

**Accessibility Features**:
- Semantic HTML: article, section, header, dl/dt/dd for metadata
- Proper heading hierarchy: h1 for title, h2 for sections
- ARIA labels for all interactive elements
- Keyboard navigation: Enter key on task card, Tab navigation for buttons
- Focus management: Focus ring on task card, visible focus indicators
- Time elements with datetime attributes and title tooltips

**Tasks Completed**:
- [X] T050: Create task detail page
- [X] T051: Add click handler to TaskItem
- [X] T052: Implement API call with error handling
- Updated specs/001-todo-fullstack-app/tasks.md to mark tasks complete

## Outcome

- ✅ Impact: User Story 5 fully implemented - users can now click on tasks to view full details including all fields, timestamps, and perform actions (edit, delete, toggle completion)
- 🧪 Tests: Manual testing required - navigate from dashboard to task detail, verify all fields display, test error states (404, 403), test back navigation, test action buttons, verify keyboard navigation
- 📁 Files: Created 1 new file (task detail page), modified 2 files (TaskItem component, tasks.md)
- 🔁 Next prompts: Test the complete flow end-to-end, implement Phase 8 polish tasks (loading states, error handling, responsive design, signout functionality)
- 🧠 Reflection: Successfully implemented task detail page with comprehensive error handling and accessibility features. Navigation pattern follows Next.js App Router conventions with dynamic routes. Click handler implementation properly prevents event bubbling to avoid navigation conflicts with action buttons.

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation followed Next.js App Router best practices
- Graders run and results (PASS/FAIL): Manual testing pending
- Prompt variant (if applicable): Standard implementation prompt with detailed requirements
- Next experiment (smallest change to try): Test the implementation with real backend API, verify error handling with different HTTP status codes, test responsive design on mobile devices
