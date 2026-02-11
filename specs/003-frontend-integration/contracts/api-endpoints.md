# API Endpoints Contract

**Feature**: 003-frontend-integration
**Date**: 2026-02-07
**Backend Reference**: Spec-1 (Task API), Spec-2 (Authentication)

## Overview

This document defines the API contract between the Next.js frontend and the FastAPI backend. All endpoints follow RESTful conventions with JSON request/response bodies.

**Base URL**: Configured via `NEXT_PUBLIC_API_URL` environment variable
- Development: `http://localhost:8000`
- Production: `https://api.production-domain.com`

**Authentication**: JWT Bearer token in Authorization header
- Format: `Authorization: Bearer <token>`
- Required for all endpoints except signup and signin

---

## Authentication Endpoints

### POST /auth/signup

**Purpose**: Register a new user account

**Authentication**: None (public endpoint)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response** (201 Created):
```json
{
  "message": "User created successfully"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "detail": "Invalid email format"
}
```

422 Unprocessable Entity - Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Email already registered",
      "type": "value_error"
    }
  ]
}
```

**Frontend Handling**:
- On success: Redirect to /signin with success message
- On 422: Display validation errors inline
- On other errors: Show generic error message

---

### POST /auth/signin

**Purpose**: Authenticate user and receive JWT token

**Authentication**: None (public endpoint)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response** (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Error Responses**:

401 Unauthorized - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

422 Unprocessable Entity - Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Frontend Handling**:
- On success: Store token in localStorage and auth context, redirect to /dashboard
- On 401: Display "Invalid email or password" message
- On 422: Display validation errors inline
- On other errors: Show generic error message

---

### POST /auth/signout (Optional)

**Purpose**: Invalidate user session (if backend implements token blacklisting)

**Authentication**: Required (Bearer token)

**Request**: Empty body

**Success Response** (200 OK):
```json
{
  "message": "Signed out successfully"
}
```

**Error Responses**:

401 Unauthorized - Invalid/expired token:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Frontend Handling**:
- Always clear token from localStorage and context (even if endpoint fails)
- Redirect to /signin
- If endpoint doesn't exist (404), ignore and proceed with client-side signout

**Note**: This endpoint may not be implemented in backend. Frontend should handle signout client-side by clearing token regardless.

---

## Task Management Endpoints

### GET /tasks

**Purpose**: Fetch all tasks belonging to the authenticated user

**Authentication**: Required (Bearer token)

**Request**: No body

**Query Parameters**: None (backend filters by authenticated user_id from JWT)

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-07T10:30:00Z",
    "updated_at": "2026-02-07T10:30:00Z"
  },
  {
    "id": 2,
    "title": "Review pull requests",
    "completed": true,
    "user_id": 1,
    "created_at": "2026-02-06T14:20:00Z",
    "updated_at": "2026-02-07T09:15:00Z"
  }
]
```

**Empty Response** (200 OK):
```json
[]
```

**Error Responses**:

401 Unauthorized - Invalid/expired token:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Frontend Handling**:
- On success: Display tasks in TaskList component
- On empty array: Show "No tasks yet" message
- On 401: Clear token, redirect to /signin
- On other errors: Show error message with retry button

---

### POST /tasks

**Purpose**: Create a new task for the authenticated user

**Authentication**: Required (Bearer token)

**Request**:
```json
{
  "title": "New task title"
}
```

**Success Response** (201 Created):
```json
{
  "id": 3,
  "title": "New task title",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-07T11:00:00Z",
  "updated_at": "2026-02-07T11:00:00Z"
}
```

**Error Responses**:

401 Unauthorized - Invalid/expired token:
```json
{
  "detail": "Invalid authentication credentials"
}
```

422 Unprocessable Entity - Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Frontend Handling**:
- On success: Add task to list immediately (optimistic update)
- On 401: Clear token, redirect to /signin
- On 422: Display validation errors inline
- On other errors: Show error message, don't add to list

---

### PUT /tasks/{task_id}

**Purpose**: Update an existing task (title or completion status)

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `task_id` (integer): ID of the task to update

**Request** (partial update):
```json
{
  "title": "Updated task title",
  "completed": true
}
```

**Note**: Both fields are optional. Send only the fields you want to update.

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated task title",
  "completed": true,
  "user_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T11:05:00Z"
}
```

**Error Responses**:

401 Unauthorized - Invalid/expired token:
```json
{
  "detail": "Invalid authentication credentials"
}
```

403 Forbidden - Task belongs to different user:
```json
{
  "detail": "Not authorized to update this task"
}
```

404 Not Found - Task doesn't exist:
```json
{
  "detail": "Task not found"
}
```

422 Unprocessable Entity - Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Frontend Handling**:
- On success: Update task in list (keep optimistic update)
- On 401: Clear token, redirect to /signin
- On 403/404: Show error message, revert optimistic update
- On 422: Display validation errors, revert optimistic update
- On other errors: Show error message, revert optimistic update

---

### DELETE /tasks/{task_id}

**Purpose**: Delete a task

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `task_id` (integer): ID of the task to delete

**Request**: No body

**Success Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

**Alternative Success Response** (204 No Content):
- No response body

**Error Responses**:

401 Unauthorized - Invalid/expired token:
```json
{
  "detail": "Invalid authentication credentials"
}
```

403 Forbidden - Task belongs to different user:
```json
{
  "detail": "Not authorized to delete this task"
}
```

404 Not Found - Task doesn't exist:
```json
{
  "detail": "Task not found"
}
```

**Frontend Handling**:
- On success: Remove task from list (keep optimistic removal)
- On 401: Clear token, redirect to /signin
- On 403/404: Show error message, re-add task to list
- On other errors: Show error message, re-add task to list

---

## Error Response Format

### Standard Error Structure

All error responses follow this format:

```json
{
  "detail": "Error message" | [validation_error_objects]
}
```

### Validation Error Structure (422)

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Human-readable error message",
      "type": "error_type"
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Frontend Action |
|------|---------|----------------|
| 200 | OK | Process response data |
| 201 | Created | Process response data |
| 204 | No Content | Success, no data to process |
| 400 | Bad Request | Show error message |
| 401 | Unauthorized | Clear token, redirect to /signin |
| 403 | Forbidden | Show "Access denied" message |
| 404 | Not Found | Show "Not found" message |
| 422 | Unprocessable Entity | Display validation errors |
| 500 | Internal Server Error | Show "Something went wrong" |
| 503 | Service Unavailable | Show "Service temporarily unavailable" |

---

## Request Headers

### Required Headers (All Requests)

```
Content-Type: application/json
```

### Required Headers (Authenticated Requests)

```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

### Optional Headers

```
Accept: application/json
User-Agent: TodoApp-Frontend/1.0
```

---

## CORS Configuration

**Backend Requirements**:
- Allow origin: Frontend URL (e.g., `http://localhost:3000` for dev)
- Allow methods: GET, POST, PUT, DELETE, OPTIONS
- Allow headers: Content-Type, Authorization
- Allow credentials: true (if using cookies)

**Frontend Configuration**:
- No special CORS configuration needed
- Browser handles CORS automatically
- Ensure backend CORS is properly configured

---

## Rate Limiting

**Backend Responsibility**: Implement rate limiting to prevent abuse

**Expected Limits** (example):
- Authentication endpoints: 5 requests per minute per IP
- Task endpoints: 100 requests per minute per user

**Frontend Handling**:
- If 429 (Too Many Requests) received: Show "Too many requests, please try again later"
- Implement exponential backoff for retries

---

## API Versioning

**Current Version**: v1 (implicit, no version in URL)

**Future Versioning**:
- If API changes significantly, use `/api/v2/` prefix
- Frontend should support version configuration
- Maintain backward compatibility when possible

---

## Testing Endpoints

### Health Check (Optional)

**GET /health**

**Purpose**: Verify backend is running

**Authentication**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-02-07T11:00:00Z"
}
```

**Frontend Usage**:
- Check backend availability before critical operations
- Display connection status in UI
- Implement retry logic for failed health checks

---

## Security Considerations

### Token Handling

- Never send token in URL query parameters
- Always use Authorization header
- Clear token immediately on 401 response
- Implement token refresh if backend supports it

### Request Validation

- Validate all inputs client-side before sending
- Sanitize user input to prevent XSS
- Trust backend validation as source of truth
- Never bypass backend validation

### HTTPS

- Use HTTPS in production (configured at deployment level)
- Reject mixed content (HTTP resources on HTTPS page)
- Implement Content Security Policy headers

---

## Integration Checklist

- [ ] Backend API is running and accessible
- [ ] CORS is configured to allow frontend origin
- [ ] All endpoints return expected response formats
- [ ] Error responses follow standard format
- [ ] JWT tokens are generated correctly
- [ ] Token validation works on protected endpoints
- [ ] User data isolation is enforced (backend filters by user_id)
- [ ] Environment variables are configured correctly
- [ ] Network errors are handled gracefully
- [ ] Rate limiting is implemented (backend)

---

## Conclusion

This API contract defines all integration points between the frontend and backend. The frontend must handle all specified error cases gracefully and provide clear user feedback. The backend is responsible for authentication, authorization, and data validation.
