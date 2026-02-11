# Implementation Plan: Frontend Application & Full-Stack Integration

**Branch**: `003-frontend-integration` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a complete Next.js frontend application that integrates with existing FastAPI backend (Spec-1) and Better Auth authentication system (Spec-2). The frontend provides user registration, authentication, and task management capabilities through a clean, responsive UI. All user interactions are secured with JWT tokens, and the application enforces strict route protection and user data isolation at the UI level.

## Technical Context

**Language/Version**: TypeScript/JavaScript with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 18+, Tailwind CSS (styling), Fetch API (HTTP client)
**Storage**: N/A (frontend consumes backend API, no local data persistence beyond auth tokens)
**Testing**: Jest + React Testing Library (component testing), Playwright (E2E testing)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) - responsive design for mobile (320px+), tablet, and desktop (1920px+)
**Project Type**: Web frontend (single-page application with Next.js App Router)
**Performance Goals**:
- Page load < 2 seconds on 3G connection
- Time to Interactive (TTI) < 3 seconds
- First Contentful Paint (FCP) < 1.5 seconds
- API response handling < 100ms (UI feedback)
**Constraints**:
- Must integrate with existing FastAPI backend without backend modifications
- JWT token must be included in all authenticated API requests
- Must handle 401/403/404/422/500 error responses gracefully
- Responsive design required (320px - 1920px)
- No business logic duplication from backend
**Scale/Scope**:
- 4 pages (landing/redirect, signup, signin, dashboard)
- 6-8 reusable components (forms, task items, loading states, error states)
- 5 API integration points (signup, signin, signout, task CRUD)
- Single user session management
- ~15-20 source files total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Spec-First Development**
- [x] Feature has complete spec.md with acceptance criteria, API contracts, and data models
- [x] No implementation has begun before spec approval

**II. Security by Default**
- [x] All API endpoints will require JWT authentication (enforced by backend, frontend includes token in headers)
- [x] JWT verification strategy documented (backend verifies, frontend stores and transmits token securely)
- [x] User identity extraction from JWT (not request body) confirmed (backend responsibility, frontend trusts backend)
- [x] User data isolation strategy defined (backend filters by user_id from JWT, frontend displays only returned data)

**III. User Data Isolation**
- [x] Database models include user_id foreign keys where applicable (backend responsibility, already implemented in Spec-1)
- [x] Query filtering by authenticated user_id documented (backend responsibility, frontend consumes filtered results)
- [x] No cross-user data access paths identified (frontend only displays data returned by backend API)

**IV. Reproducibility**
- [x] Plan references spec.md and will generate tasks.md
- [x] Significant architectural decisions identified for ADR documentation (token storage strategy, route protection approach, API client architecture)
- [x] Implementation will be traceable through PHRs

**V. Automation-First**
- [x] Appropriate Claude Code agents identified for each domain:
  - `nextjs-ui-builder` for all frontend UI components, pages, and layouts
  - `auth-security-handler` for authentication flow integration and token management
  - `fastapi-backend-dev` for API integration patterns (if backend changes needed)
- [x] No manual coding planned

**VI. Production Realism**
- [x] Using Neon PostgreSQL (not in-memory/SQLite) - backend dependency, already implemented
- [x] Using Better Auth with JWT (not hardcoded users) - backend dependency, already implemented
- [x] Using FastAPI with REST conventions (not mock endpoints) - backend dependency, already implemented
- [x] Using Next.js 16+ App Router (not static HTML) - frontend implementation
- [x] Proper error handling with HTTP status codes planned (401, 403, 404, 422, 500)
- [x] Environment-based configuration (.env) planned (NEXT_PUBLIC_API_URL)

**Constitution Compliance Status**: ✅ PASSED - All constitutional requirements met

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-integration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.md # Backend API contract reference
│   └── types.ts         # TypeScript type definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/              # Route group for authentication pages
│   │   ├── signup/
│   │   │   └── page.tsx     # User registration page
│   │   └── signin/
│   │       └── page.tsx     # User login page
│   ├── dashboard/
│   │   ├── page.tsx         # Protected task dashboard (main app)
│   │   └── layout.tsx       # Dashboard-specific layout with auth guard
│   ├── layout.tsx           # Root layout (global styles, providers)
│   ├── page.tsx             # Landing page (redirect logic)
│   └── globals.css          # Global styles (Tailwind imports)
├── components/
│   ├── auth/
│   │   ├── AuthForm.tsx     # Reusable form for signup/signin
│   │   └── SignOutButton.tsx # Logout button component
│   ├── tasks/
│   │   ├── TaskForm.tsx     # Task creation form
│   │   ├── TaskList.tsx     # Task list container
│   │   └── TaskItem.tsx     # Individual task item with edit/delete
│   ├── ui/
│   │   ├── LoadingSpinner.tsx # Loading state indicator
│   │   ├── ErrorMessage.tsx   # Error display component
│   │   └── Button.tsx         # Reusable button component
│   └── layout/
│       ├── Header.tsx       # App header with navigation
│       └── Container.tsx    # Content container wrapper
├── lib/
│   ├── api/
│   │   ├── client.ts        # Base API client with fetch wrapper
│   │   ├── auth.ts          # Auth API calls (signup, signin, signout)
│   │   └── tasks.ts         # Task API calls (CRUD operations)
│   ├── auth/
│   │   ├── token.ts         # Token storage and retrieval
│   │   ├── context.tsx      # Auth context provider
│   │   └── hooks.ts         # useAuth, useRequireAuth hooks
│   └── utils/
│       ├── validation.ts    # Form validation helpers
│       └── errors.ts        # Error handling utilities
├── types/
│   ├── user.ts              # User type definitions
│   ├── task.ts              # Task type definitions
│   └── api.ts               # API response/error types
├── middleware.ts            # Next.js middleware for route protection
├── .env.local               # Environment variables (gitignored)
├── .env.example             # Environment variable template
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts

backend/                     # Existing backend (Spec-1, Spec-2)
├── [existing structure]     # No changes to backend for this feature
```

**Structure Decision**: Web application structure (Option 2) with Next.js App Router conventions. The frontend is a separate service that communicates with the existing backend via REST API. The App Router structure uses:
- Route groups `(auth)` for authentication pages
- Nested layouts for auth guards
- Colocation of related components
- Separation of concerns: components (UI), lib (business logic), types (contracts)

## Complexity Tracking

**Status**: ✅ No constitutional violations detected

All constitutional principles are satisfied:
- Spec-first development followed
- Security enforced through backend integration
- User data isolation maintained by backend
- Full reproducibility through artifacts
- Automation-first with Claude Code agents
- Production-grade technologies used

No complexity justifications required.

## Architecture Overview

### High-Level Strategy

Build a minimal but complete frontend focused on hackathon demo readiness with:
1. **Authentication-first flow**: Users must authenticate before accessing any features
2. **Clean service layer**: Centralized API client for all backend communication
3. **Strict route protection**: Unauthenticated users redirected to signin
4. **User isolation at UI level**: Frontend only displays data returned by backend (backend enforces filtering)

### Key Architectural Decisions

**Decision 1: Token Storage Strategy**
- **Chosen**: Memory-based storage with React Context
- **Rationale**: Simpler implementation for hackathon demo, avoids cookie complexity
- **Alternative Considered**: HTTP-only cookies (more secure but requires backend cookie handling)
- **Trade-off**: Memory storage requires re-authentication on page refresh initially, but we'll implement session persistence via localStorage for token (with appropriate security warnings)

**Decision 2: Route Protection Approach**
- **Chosen**: Next.js middleware + client-side auth guards
- **Rationale**: Middleware provides server-side protection, client guards provide UX
- **Alternative Considered**: Layout-based guards only (less secure)
- **Trade-off**: Dual protection adds slight complexity but ensures security

**Decision 3: API Client Architecture**
- **Chosen**: Centralized fetch wrapper with automatic token injection
- **Rationale**: DRY principle, consistent error handling, easy to maintain
- **Alternative Considered**: Direct fetch calls in components (harder to maintain)
- **Trade-off**: Additional abstraction layer but significantly better maintainability

**Decision 4: State Management**
- **Chosen**: React Context for auth state, local component state for UI
- **Rationale**: Simple, built-in, sufficient for small app scope
- **Alternative Considered**: Redux/Zustand (overkill for this scope)
- **Trade-off**: Context re-renders can be less optimized but acceptable for this scale

## Component Design

### Page Components

**1. Landing Page (`app/page.tsx`)**
- Purpose: Entry point with redirect logic
- Behavior: Redirect authenticated users to /dashboard, unauthenticated to /signin
- Dependencies: Auth context

**2. Signup Page (`app/(auth)/signup/page.tsx`)**
- Purpose: User registration
- Features: Email/password form, validation, error display
- API: POST /auth/signup
- Success: Redirect to /signin with success message

**3. Signin Page (`app/(auth)/signin/page.tsx`)**
- Purpose: User authentication
- Features: Email/password form, validation, error display
- API: POST /auth/signin
- Success: Store token, redirect to /dashboard

**4. Dashboard Page (`app/dashboard/page.tsx`)**
- Purpose: Main application - task management
- Features: Task list, create form, edit/delete actions
- Protection: Requires authentication
- APIs: GET /tasks, POST /tasks, PUT /tasks/:id, DELETE /tasks/:id

### Reusable Components

**Authentication Components**
- `AuthForm`: Shared form for signup/signin with validation
- `SignOutButton`: Logout button with confirmation

**Task Components**
- `TaskForm`: Task creation/edit form with validation
- `TaskList`: Container for task items with loading/empty states
- `TaskItem`: Individual task with title, completion toggle, edit/delete

**UI Components**
- `LoadingSpinner`: Consistent loading indicator
- `ErrorMessage`: Standardized error display
- `Button`: Reusable button with variants (primary, secondary, danger)
- `Header`: App header with navigation and signout
- `Container`: Content wrapper for consistent spacing

## API Integration Strategy

### Centralized API Client

**Base Client (`lib/api/client.ts`)**
```typescript
// Pseudo-code structure
class ApiClient {
  baseURL: string (from env)

  async request(endpoint, options) {
    - Get token from auth context
    - Add Authorization header if token exists
    - Make fetch request
    - Handle response (success/error)
    - Parse JSON
    - Return data or throw error
  }

  get(endpoint) { return request(endpoint, { method: 'GET' }) }
  post(endpoint, data) { return request(endpoint, { method: 'POST', body: data }) }
  put(endpoint, data) { return request(endpoint, { method: 'PUT', body: data }) }
  delete(endpoint) { return request(endpoint, { method: 'DELETE' }) }
}
```

**Auth API (`lib/api/auth.ts`)**
- `signup(email, password)`: POST /auth/signup
- `signin(email, password)`: POST /auth/signin → returns { token, user }
- `signout()`: Clear local token (backend may have logout endpoint)

**Task API (`lib/api/tasks.ts`)**
- `getTasks()`: GET /tasks → returns Task[]
- `createTask(title)`: POST /tasks → returns Task
- `updateTask(id, updates)`: PUT /tasks/:id → returns Task
- `deleteTask(id)`: DELETE /tasks/:id → returns success

### Error Handling Strategy

**HTTP Status Code Mapping**
- `401 Unauthorized`: Clear token, redirect to /signin
- `403 Forbidden`: Show "Access denied" message
- `404 Not Found`: Show "Resource not found" message
- `422 Unprocessable Entity`: Show validation errors from backend
- `500 Internal Server Error`: Show "Something went wrong, please try again"
- Network errors: Show "Connection failed, check your internet"

**Error Display**
- Form errors: Inline below input fields
- API errors: Toast notification or error banner
- Critical errors: Full-page error state with retry option

## Authentication Flow

### Signup Flow
1. User navigates to /signup
2. User enters email and password
3. Frontend validates input (format, required fields)
4. Frontend sends POST /auth/signup to backend
5. Backend creates user, returns success
6. Frontend redirects to /signin with success message

### Signin Flow
1. User navigates to /signin
2. User enters email and password
3. Frontend validates input
4. Frontend sends POST /auth/signin to backend
5. Backend validates credentials, generates JWT token
6. Backend returns { token, user: { id, email } }
7. Frontend stores token in auth context and localStorage
8. Frontend redirects to /dashboard

### Session Persistence
1. On app load, check localStorage for token
2. If token exists, set in auth context
3. Middleware validates token on protected routes
4. If token invalid/expired, clear and redirect to /signin

### Signout Flow
1. User clicks signout button
2. Frontend clears token from context and localStorage
3. Frontend redirects to /signin
4. (Optional) Call backend signout endpoint if exists

## Route Protection Strategy

### Next.js Middleware (`middleware.ts`)
```typescript
// Pseudo-code
export function middleware(request) {
  const token = request.cookies.get('token') || request.headers.get('authorization')
  const isAuthPage = request.url.includes('/signin') || request.url.includes('/signup')
  const isProtectedPage = request.url.includes('/dashboard')

  if (isProtectedPage && !token) {
    return redirect('/signin')
  }

  if (isAuthPage && token) {
    return redirect('/dashboard')
  }

  return next()
}
```

### Client-Side Auth Guard (`lib/auth/hooks.ts`)
```typescript
// Pseudo-code
function useRequireAuth() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/signin')
    }
  }, [user, loading])

  return { user, loading }
}
```

### Protected Layout (`app/dashboard/layout.tsx`)
```typescript
// Pseudo-code
export default function DashboardLayout({ children }) {
  const { user, loading } = useRequireAuth()

  if (loading) return <LoadingSpinner />
  if (!user) return null // Redirect handled by hook

  return (
    <div>
      <Header user={user} />
      {children}
    </div>
  )
}
```

## Task Management Flow

### Fetch Tasks (Dashboard Load)
1. Dashboard page mounts
2. Call `getTasks()` API
3. Show loading spinner
4. On success: Display tasks in TaskList
5. On error: Show error message with retry button
6. If empty: Show "No tasks yet" message with create prompt

### Create Task
1. User enters task title in TaskForm
2. User submits form
3. Frontend validates (title required, not empty)
4. Call `createTask(title)` API
5. Show loading state on button
6. On success: Add task to list immediately (optimistic update)
7. On error: Show error message, don't add to list

### Update Task
1. User edits task title or toggles completion
2. Call `updateTask(id, updates)` API
3. Optimistically update UI
4. On success: Keep updated state
5. On error: Revert to previous state, show error

### Delete Task
1. User clicks delete button
2. Show confirmation dialog
3. If confirmed, call `deleteTask(id)` API
4. Optimistically remove from UI
5. On success: Keep removed
6. On error: Re-add to list, show error

## UI/UX Design Principles

### Visual Design
- **Clean and minimal**: Focus on functionality, not decoration
- **Consistent spacing**: Use Tailwind spacing scale (4px increments)
- **Clear hierarchy**: Headings, body text, and actions clearly distinguished
- **Accessible colors**: Sufficient contrast ratios (WCAG AA minimum)

### Loading States
- **Skeleton screens**: For initial page loads
- **Spinners**: For button actions and small updates
- **Disabled states**: Prevent double-submission during API calls
- **Progress indicators**: For multi-step processes

### Error States
- **Inline validation**: Show errors below form fields
- **Error messages**: Clear, actionable, user-friendly language
- **Retry options**: Allow users to retry failed operations
- **Fallback UI**: Graceful degradation when features fail

### Responsive Design
- **Mobile-first**: Design for 320px width, scale up
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Touch targets**: Minimum 44x44px for mobile
- **Readable text**: Minimum 16px font size on mobile

## Environment Configuration

### Required Environment Variables

**`.env.local`** (development, gitignored)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**`.env.example`** (template, committed)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production**
```
NEXT_PUBLIC_API_URL=https://api.production-domain.com
```

### Configuration Usage
- API base URL: `process.env.NEXT_PUBLIC_API_URL`
- Prefix with `NEXT_PUBLIC_` to expose to browser
- Never commit `.env.local` to git
- Document all required variables in `.env.example`

## Implementation Phases

### Phase 1: Project Setup & Structure
- Initialize Next.js project with TypeScript
- Configure Tailwind CSS
- Set up project structure (folders, files)
- Create environment configuration
- Install dependencies

### Phase 2: Authentication Foundation
- Implement auth context and hooks
- Create token storage utilities
- Build AuthForm component
- Create signup page
- Create signin page
- Implement signout functionality

### Phase 3: Route Protection
- Implement Next.js middleware
- Create auth guard hooks
- Set up protected layouts
- Add redirect logic to landing page

### Phase 4: API Integration Layer
- Build centralized API client
- Implement auth API functions
- Implement task API functions
- Add error handling utilities
- Test API integration with backend

### Phase 5: Task Management UI
- Create TaskForm component
- Create TaskList component
- Create TaskItem component
- Build dashboard page
- Implement CRUD operations
- Add optimistic updates

### Phase 6: UI Polish & Responsiveness
- Create reusable UI components (Button, LoadingSpinner, ErrorMessage)
- Build Header and Container components
- Implement responsive layouts
- Add loading and error states
- Style all components with Tailwind
- Test on multiple screen sizes

### Phase 7: Integration Testing & Demo Prep
- Test full user flow (signup → signin → CRUD → signout)
- Verify error handling for all edge cases
- Test with backend API
- Fix any integration issues
- Prepare demo script
- Document any known issues

## Definition of Done

### Functional Completeness
- [ ] User can sign up with email and password
- [ ] User can sign in with valid credentials
- [ ] User can view their task dashboard after signin
- [ ] User can create new tasks
- [ ] User can view all their tasks
- [ ] User can update task titles
- [ ] User can toggle task completion status
- [ ] User can delete tasks
- [ ] User can sign out
- [ ] Unauthenticated users are redirected to signin
- [ ] Authenticated users cannot access signin/signup pages

### Technical Requirements
- [ ] Frontend runs independently (`npm run dev`)
- [ ] Backend integration fully functional (all API calls work)
- [ ] JWT token included in all authenticated requests
- [ ] Error responses handled gracefully (401, 403, 404, 422, 500)
- [ ] Loading states displayed during API operations
- [ ] Form validation works correctly
- [ ] Responsive design works on mobile, tablet, desktop (320px - 1920px)
- [ ] No console errors in browser
- [ ] Environment variables configured correctly

### Demo Readiness
- [ ] Clean, professional UI suitable for judges
- [ ] Smooth user experience with no broken functionality
- [ ] Clear error messages (no raw error codes)
- [ ] Fast and responsive (meets performance goals)
- [ ] Can complete full demo flow without issues
- [ ] Documentation complete (README with setup instructions)

### Security & Best Practices
- [ ] JWT tokens stored securely (not in URLs or logs)
- [ ] Passwords not stored in browser storage
- [ ] User IDs not trusted from client side
- [ ] All user inputs validated
- [ ] XSS prevention implemented
- [ ] HTTPS enforced in production (configuration)

## Risk Assessment

### High-Priority Risks

**Risk 1: Backend API Compatibility**
- **Description**: Frontend assumptions about API contracts may not match backend implementation
- **Mitigation**: Review backend API documentation (Spec-1, Spec-2) before implementation
- **Contingency**: Create adapter layer if API contracts differ

**Risk 2: Token Storage Security**
- **Description**: localStorage token storage vulnerable to XSS attacks
- **Mitigation**: Implement proper input sanitization, consider HTTP-only cookies
- **Contingency**: Document security limitations, plan cookie migration

**Risk 3: Session Persistence Complexity**
- **Description**: Maintaining auth state across page refreshes may be complex
- **Mitigation**: Use proven patterns (localStorage + context), test thoroughly
- **Contingency**: Simplify to require re-login on refresh if needed

### Medium-Priority Risks

**Risk 4: Responsive Design Edge Cases**
- **Description**: Layout may break on unusual screen sizes or orientations
- **Mitigation**: Test on multiple devices and screen sizes
- **Contingency**: Focus on common breakpoints (mobile, tablet, desktop)

**Risk 5: Error Handling Completeness**
- **Description**: May not handle all possible backend error scenarios
- **Mitigation**: Implement generic error handler for unexpected cases
- **Contingency**: Show generic error message for unhandled errors

## Dependencies & Integration Points

### External Dependencies
- **Backend API** (Spec-1): Must be running and accessible at configured URL
- **Authentication Service** (Spec-2): JWT token generation must be functional
- **Neon Database**: Backend must have working database connection

### Integration Contracts

**Auth Endpoints** (from Spec-2)
- `POST /auth/signup`: Create new user
  - Request: `{ email: string, password: string }`
  - Response: `{ message: string }` or error
- `POST /auth/signin`: Authenticate user
  - Request: `{ email: string, password: string }`
  - Response: `{ token: string, user: { id: number, email: string } }`

**Task Endpoints** (from Spec-1)
- `GET /tasks`: Fetch user's tasks
  - Headers: `Authorization: Bearer <token>`
  - Response: `Task[]`
- `POST /tasks`: Create task
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ title: string }`
  - Response: `Task`
- `PUT /tasks/:id`: Update task
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ title?: string, completed?: boolean }`
  - Response: `Task`
- `DELETE /tasks/:id`: Delete task
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ message: string }`

**Task Type**
```typescript
interface Task {
  id: number
  title: string
  completed: boolean
  user_id: number
  created_at: string
  updated_at: string
}
```

**User Type**
```typescript
interface User {
  id: number
  email: string
}
```

## Success Metrics

### Performance Metrics
- Page load time < 2 seconds
- API response handling < 100ms (UI feedback)
- Time to Interactive < 3 seconds
- First Contentful Paint < 1.5 seconds

### Functional Metrics
- 100% of user stories completed (7/7)
- 100% of functional requirements met (20/20)
- 100% of security requirements met (10/10)
- Zero critical bugs in demo

### Quality Metrics
- Zero console errors
- All forms validated correctly
- All error states handled gracefully
- Responsive on all target screen sizes (320px - 1920px)
