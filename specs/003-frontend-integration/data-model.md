# Data Model: Frontend Application & Full-Stack Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-07
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data models used in the frontend application. Since this is a frontend-only feature, the data models are TypeScript type definitions that mirror the backend API contracts. The backend (Spec-1, Spec-2) owns the actual data models and database schema.

## Frontend Type Definitions

### User Entity

**Purpose**: Represents an authenticated user in the application

**TypeScript Definition**:
```typescript
interface User {
  id: number;           // Unique user identifier (from backend)
  email: string;        // User's email address
}
```

**Source**: Backend authentication service (Spec-2)

**Usage**:
- Stored in auth context after successful signin
- Displayed in header/navigation
- Used for user-specific UI elements

**Validation Rules** (enforced by backend):
- `id`: Positive integer, unique
- `email`: Valid email format, unique

**Notes**:
- Password is never stored or transmitted to frontend after authentication
- Additional user fields (name, avatar) can be added in future iterations

---

### Task Entity

**Purpose**: Represents a todo item owned by a user

**TypeScript Definition**:
```typescript
interface Task {
  id: number;           // Unique task identifier
  title: string;        // Task description/title
  completed: boolean;   // Completion status
  user_id: number;      // Owner's user ID (for reference only)
  created_at: string;   // ISO 8601 timestamp
  updated_at: string;   // ISO 8601 timestamp
}
```

**Source**: Backend task service (Spec-1)

**Usage**:
- Displayed in task list on dashboard
- Updated through task CRUD operations
- Filtered by backend (user_id) before reaching frontend

**Validation Rules** (enforced by backend):
- `id`: Positive integer, unique
- `title`: Non-empty string, max length TBD by backend
- `completed`: Boolean (true/false)
- `user_id`: Must match authenticated user
- `created_at`: ISO 8601 format
- `updated_at`: ISO 8601 format

**Frontend Validation**:
- `title`: Required, non-empty, trimmed

**State Transitions**:
- Created: `completed = false`
- Toggled: `completed = !completed`
- Updated: `updated_at` changes
- Deleted: Removed from list

**Notes**:
- `user_id` is included in response but not used for authorization (backend handles this)
- Timestamps are display-only (formatted for user)

---

### Authentication Token (JWT)

**Purpose**: Represents a user's authenticated session

**TypeScript Definition**:
```typescript
interface AuthToken {
  token: string;        // JWT token string
  expiresAt?: number;   // Optional expiration timestamp (if provided by backend)
}
```

**Source**: Backend authentication service (Spec-2)

**Usage**:
- Stored in localStorage and auth context
- Included in Authorization header for all authenticated API requests
- Cleared on signout or 401 response

**Format**: JWT (JSON Web Token)
- Header: Algorithm and token type
- Payload: User claims (user_id, email, expiration)
- Signature: Verified by backend

**Security Considerations**:
- Never logged to console in production
- Never included in URLs
- Cleared immediately on signout
- Validated by backend on every request

**Notes**:
- Frontend treats token as opaque string
- Backend is responsible for token generation and validation
- Token expiration handled by backend (frontend responds to 401)

---

### API Response Types

**Purpose**: Type-safe wrappers for API responses

**Success Response**:
```typescript
interface ApiResponse<T> {
  data: T;              // Response payload
  status: number;       // HTTP status code
}
```

**Error Response**:
```typescript
interface ApiError {
  message: string;      // User-friendly error message
  status: number;       // HTTP status code
  details?: Record<string, string[]>; // Validation errors (422)
}
```

**Usage**:
- Returned by API client functions
- Handled by error handling utilities
- Displayed to users through UI components

**Error Status Codes**:
- `401`: Unauthorized (invalid/expired token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error (backend error)

---

### Form Input Types

**Purpose**: Type-safe form data structures

**Signup Form**:
```typescript
interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string; // Frontend-only validation
}
```

**Signin Form**:
```typescript
interface SigninFormData {
  email: string;
  password: string;
}
```

**Task Form**:
```typescript
interface TaskFormData {
  title: string;
}
```

**Task Update**:
```typescript
interface TaskUpdateData {
  title?: string;       // Optional: only if title changed
  completed?: boolean;  // Optional: only if completion toggled
}
```

**Usage**:
- Form component state
- Validation before API submission
- Transformed to API request format

---

## Data Flow Diagrams

### Authentication Flow

```
User Input (email, password)
  ↓
SigninFormData
  ↓
API Client: POST /auth/signin
  ↓
Backend Validation & JWT Generation
  ↓
ApiResponse<{ token: string, user: User }>
  ↓
Auth Context (store token & user)
  ↓
localStorage (persist token)
  ↓
Dashboard (authenticated state)
```

### Task Creation Flow

```
User Input (title)
  ↓
TaskFormData
  ↓
Frontend Validation (required, non-empty)
  ↓
API Client: POST /tasks (with Authorization header)
  ↓
Backend Validation & Database Insert
  ↓
ApiResponse<Task>
  ↓
Task List State (add new task)
  ↓
UI Update (display new task)
```

### Task Update Flow

```
User Action (edit title or toggle completion)
  ↓
TaskUpdateData
  ↓
Optimistic UI Update (immediate feedback)
  ↓
API Client: PUT /tasks/:id (with Authorization header)
  ↓
Backend Validation & Database Update
  ↓
ApiResponse<Task> (success) or ApiError (failure)
  ↓
Keep Update (success) or Revert (failure)
  ↓
UI State Finalized
```

---

## Validation Rules Summary

### Frontend Validation (Client-Side)

**Purpose**: Immediate user feedback, reduce unnecessary API calls

**Email Validation**:
- Required field
- Valid email format (regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
- Trimmed whitespace

**Password Validation**:
- Required field
- Minimum length (TBD by backend, assume 8 characters)
- No whitespace trimming (passwords can have spaces)

**Task Title Validation**:
- Required field
- Non-empty after trimming
- Maximum length (TBD by backend, assume 255 characters)

**Confirm Password Validation** (signup only):
- Must match password field
- Frontend-only validation

### Backend Validation (Server-Side)

**Purpose**: Security, data integrity, business rules enforcement

**All Validations**:
- Email uniqueness (signup)
- Password strength requirements
- Task title length limits
- User ownership verification
- Token validity and expiration

**Frontend Response**:
- Display backend validation errors from 422 responses
- Trust backend as source of truth
- Never bypass backend validation

---

## State Management Strategy

### Global State (Auth Context)

**Stored Data**:
- `user: User | null` - Current authenticated user
- `token: string | null` - JWT authentication token
- `loading: boolean` - Auth initialization state

**Operations**:
- `signin(email, password)` - Authenticate and store token
- `signout()` - Clear token and user
- `loadToken()` - Initialize from localStorage

**Persistence**:
- Token stored in localStorage
- User derived from token (or fetched from backend)
- Cleared on signout or 401 response

### Local State (Component-Level)

**Task List State**:
- `tasks: Task[]` - Array of user's tasks
- `loading: boolean` - Fetch/operation in progress
- `error: string | null` - Error message if operation failed

**Form State**:
- Form field values
- Validation errors
- Submission state (loading, success, error)

**UI State**:
- Modal open/closed
- Dropdown expanded/collapsed
- Loading spinners
- Error messages

---

## Type Safety Benefits

### Compile-Time Checks

- Catch type mismatches before runtime
- Autocomplete in IDE for better DX
- Refactoring safety (rename, move)
- Documentation through types

### Runtime Safety

- Validate API responses match expected types
- Type guards for discriminated unions
- Null/undefined checks enforced

### Example Type Guards

```typescript
function isApiError(response: unknown): response is ApiError {
  return (
    typeof response === 'object' &&
    response !== null &&
    'message' in response &&
    'status' in response
  );
}

function isTask(data: unknown): data is Task {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'title' in data &&
    'completed' in data
  );
}
```

---

## Future Considerations

### Potential Enhancements

**User Model**:
- Add `name` field for display
- Add `avatar_url` for profile pictures
- Add `created_at` for account age

**Task Model**:
- Add `description` for detailed notes
- Add `due_date` for deadlines
- Add `priority` for task ordering
- Add `tags` for categorization

**Pagination**:
- Add `PaginatedResponse<T>` type
- Add `page`, `limit`, `total` fields
- Implement infinite scroll or pagination UI

**Optimistic Updates**:
- Add `optimistic: boolean` flag to tasks
- Show pending state during API calls
- Revert on failure with error indication

---

## Conclusion

All frontend data models are defined as TypeScript interfaces that mirror backend API contracts. The frontend does not own any data models - it consumes and displays data from the backend. Type safety ensures correct usage throughout the application.

**Key Principles**:
- Backend is source of truth for all data
- Frontend validates for UX, backend validates for security
- Types ensure compile-time safety
- State management keeps UI in sync with backend
