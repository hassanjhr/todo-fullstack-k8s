# Research: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-app
**Date**: 2026-02-06
**Purpose**: Technology validation and best practices research for implementation planning

## Overview

This document captures research findings and technology decisions for the Todo Full-Stack Web Application. All decisions align with constitutional principles and specification requirements.

---

## 1. Better Auth JWT Configuration for Next.js 16+ App Router

### Decision

Use Better Auth v1.x with JWT plugin configured for Next.js 16+ App Router with the following setup:
- JWT tokens stored in httpOnly cookies (not localStorage)
- Token expiration set to 24 hours (configurable via environment variable)
- Automatic token refresh on API calls
- Session management via Better Auth's built-in session handling

### Rationale

- **Security**: httpOnly cookies prevent XSS attacks by making tokens inaccessible to JavaScript
- **App Router Compatibility**: Better Auth v1.x has native support for Next.js 13+ App Router with Server Components
- **Developer Experience**: Better Auth provides pre-built UI components and hooks for authentication flows
- **JWT Standard**: Industry-standard token format compatible with FastAPI backend verification

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|-------------|------|------|------------------|
| NextAuth.js | Mature ecosystem, wide adoption | Heavier, more complex setup | Better Auth is lighter and JWT-focused |
| Custom JWT implementation | Full control, minimal dependencies | Security risks, reinventing the wheel | Violates production realism principle |
| Auth0 / Firebase Auth | Managed service, enterprise features | Third-party dependency, cost | Spec requires Better Auth specifically |

### Implementation Notes

- Configure Better Auth in `frontend/src/lib/auth.ts`
- Set JWT secret in `.env.local` (must match backend secret)
- Use Better Auth's `useSession()` hook for client-side auth state
- Implement Server Actions for signin/signup flows

---

## 2. FastAPI JWT Verification Middleware Patterns

### Decision

Implement JWT verification using FastAPI dependency injection with `python-jose` library:
- Create a `get_current_user` dependency that extracts and verifies JWT from Authorization header
- Use FastAPI's `Depends()` to inject authenticated user into route handlers
- Implement custom exception handlers for 401 (invalid token) and 403 (insufficient permissions)

### Rationale

- **FastAPI Native**: Dependency injection is FastAPI's recommended pattern for authentication
- **Reusability**: Single dependency function used across all protected endpoints
- **Type Safety**: Returns typed User object for use in route handlers
- **Error Handling**: Centralized exception handling for consistent error responses

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|-------------|------|------|------------------|
| Middleware-based verification | Runs on every request | Less flexible, harder to exclude routes | Dependency injection is more idiomatic |
| PyJWT library | Lightweight | Less feature-complete than python-jose | python-jose includes additional crypto utilities |
| Third-party auth library (e.g., FastAPI-Users) | Full-featured | Heavy, opinionated | Spec requires custom JWT implementation |

### Implementation Notes

- Install `python-jose[cryptography]` and `passlib[bcrypt]`
- Create `backend/src/api/deps.py` with `get_current_user` dependency
- Verify JWT signature using shared secret from environment variable
- Extract `user_id` from JWT payload and validate against database
- Return 401 for expired/invalid tokens, 403 for authorization failures

---

## 3. SQLModel with Neon PostgreSQL Best Practices

### Decision

Use SQLModel with async PostgreSQL driver (asyncpg) for Neon Serverless PostgreSQL:
- Define User and Task models as SQLModel classes with proper relationships
- Use Alembic for database migrations (optional for basic implementation)
- Configure connection pooling for Neon's serverless architecture
- Implement user_id filtering at the query level (not application logic)

### Rationale

- **Type Safety**: SQLModel combines Pydantic validation with SQLAlchemy ORM
- **Async Support**: asyncpg provides better performance for I/O-bound operations
- **Neon Compatibility**: Neon recommends asyncpg for serverless PostgreSQL
- **Security**: Query-level filtering prevents accidental data leaks

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|-------------|------|------|------------------|
| Raw SQL with psycopg2 | Full control, no ORM overhead | Manual query building, SQL injection risk | Violates production realism principle |
| SQLAlchemy Core | Lighter than ORM | No Pydantic integration | SQLModel provides better DX |
| Prisma (via Prisma Client Python) | Great DX, type-safe | Immature Python support | SQLModel is more mature for Python |

### Implementation Notes

- Define models in `backend/src/models/user.py` and `backend/src/models/task.py`
- Task model includes `user_id` foreign key with `ondelete="CASCADE"`
- Use SQLModel's `select()` with `.where(Task.user_id == current_user.id)` for filtering
- Configure Neon connection string in `.env` with SSL mode enabled
- Use connection pooling with `create_async_engine(pool_size=5, max_overflow=10)`

---

## 4. CORS Configuration for Next.js + FastAPI

### Decision

Configure FastAPI CORS middleware to allow requests from Next.js frontend:
- Allow specific origin (e.g., `http://localhost:3000` for development)
- Allow credentials (required for httpOnly cookies)
- Allow specific HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Allow Authorization header

### Rationale

- **Security**: Explicit origin whitelist prevents unauthorized cross-origin requests
- **Cookie Support**: `allow_credentials=True` required for httpOnly cookies
- **Production Ready**: Environment-based origin configuration for dev/staging/prod

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|-------------|------|------|------------------|
| Allow all origins (`*`) | Simple, no configuration | Major security vulnerability | Violates security by default principle |
| Proxy through Next.js | No CORS issues | Complex setup, single point of failure | Unnecessary complexity |
| Same-origin deployment | No CORS needed | Limits deployment flexibility | Spec requires separate services |

### Implementation Notes

- Install `fastapi[all]` which includes CORS middleware
- Configure in `backend/src/main.py`:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
      allow_headers=["Authorization", "Content-Type"],
  )
  ```
- Set `FRONTEND_URL` in `.env` for each environment

---

## 5. Environment Variable Management Across Frontend and Backend

### Decision

Use separate `.env` files for frontend and backend with shared secrets:
- **Frontend**: `.env.local` for Next.js (NEXT_PUBLIC_ prefix for client-side vars)
- **Backend**: `.env` for FastAPI (loaded via python-dotenv)
- **Shared Secrets**: JWT_SECRET must be identical in both environments
- **Documentation**: Provide `.env.example` templates with clear instructions

### Rationale

- **Security**: Separate files prevent accidental exposure of backend secrets to frontend
- **Framework Conventions**: Follows Next.js and FastAPI standard practices
- **Developer Experience**: Clear separation makes configuration easier to understand

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|-------------|------|------|------------------|
| Single root `.env` file | Simpler, one source of truth | Risk of exposing backend secrets to frontend | Security risk |
| Environment-specific files (.env.dev, .env.prod) | Clear environment separation | More files to manage | Overkill for basic implementation |
| Secret management service (e.g., Vault) | Enterprise-grade security | Complex setup, external dependency | Overkill for hackathon project |

### Implementation Notes

**Frontend `.env.local`**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same-as-backend-jwt-secret>
BETTER_AUTH_URL=http://localhost:3000
```

**Backend `.env`**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname
JWT_SECRET=<same-as-frontend-better-auth-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
FRONTEND_URL=http://localhost:3000
```

**Critical**: JWT_SECRET / BETTER_AUTH_SECRET must be identical for token verification to work.

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend Framework | Next.js | 16+ | React-based web framework with App Router |
| Frontend Language | TypeScript | 5.x | Type-safe JavaScript |
| Frontend Styling | TailwindCSS | 3.x | Utility-first CSS framework |
| Authentication (Frontend) | Better Auth | 1.x | JWT-based authentication library |
| Backend Framework | FastAPI | 0.110+ | Modern Python web framework |
| Backend Language | Python | 3.11+ | Backend programming language |
| ORM | SQLModel | 0.0.14+ | Pydantic + SQLAlchemy integration |
| Database | Neon PostgreSQL | Latest | Serverless PostgreSQL |
| Database Driver | asyncpg | 0.29+ | Async PostgreSQL driver |
| JWT Library | python-jose | 3.3+ | JWT encoding/decoding |
| Password Hashing | passlib | 1.7+ | Password hashing utilities |
| HTTP Client | fetch API | Native | Frontend API client |

---

## Security Considerations

1. **JWT Secret Management**: Use strong, randomly generated secrets (minimum 32 characters)
2. **Password Hashing**: Use bcrypt with cost factor 12 (passlib default)
3. **HTTPS in Production**: All production deployments must use HTTPS
4. **Token Expiration**: 24-hour expiration balances security and UX
5. **httpOnly Cookies**: Prevents XSS attacks on JWT tokens
6. **CORS Whitelist**: Explicit origin whitelist prevents unauthorized access
7. **SQL Injection Prevention**: SQLModel parameterized queries prevent SQL injection
8. **User Data Isolation**: Database-level filtering prevents cross-user data access

---

## Performance Considerations

1. **Connection Pooling**: Neon connection pool (5 connections, 10 max overflow)
2. **Async I/O**: asyncpg and FastAPI async endpoints for better concurrency
3. **JWT Verification Caching**: Consider caching decoded JWTs for repeated requests (optional)
4. **Database Indexing**: Index user_id column on tasks table for fast filtering
5. **Frontend Code Splitting**: Next.js automatic code splitting for faster page loads

---

## Development Workflow

1. **Local Development**:
   - Frontend: `npm run dev` (port 3000)
   - Backend: `uvicorn src.main:app --reload` (port 8000)
   - Database: Neon cloud instance (no local PostgreSQL required)

2. **Environment Setup**:
   - Copy `.env.example` to `.env` (backend) and `.env.local` (frontend)
   - Generate JWT secret: `openssl rand -hex 32`
   - Configure Neon database URL
   - Ensure JWT secrets match between frontend and backend

3. **Testing Strategy**:
   - Backend: pytest for API endpoint testing
   - Frontend: Manual testing for authentication and CRUD flows
   - Integration: Test JWT token flow end-to-end

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| JWT secret mismatch | Authentication fails | Medium | Clear documentation, validation script |
| CORS misconfiguration | API calls blocked | Medium | Test from frontend during setup |
| Neon connection issues | Database unavailable | Low | Connection pooling, retry logic |
| User data leak | Security breach | Low | Query-level filtering, integration tests |
| Token expiration UX | User frustration | Medium | Clear error messages, auto-redirect to signin |

---

## Next Steps

1. Generate `data-model.md` with User and Task entity definitions
2. Generate `contracts/` with OpenAPI specifications for API endpoints
3. Generate `quickstart.md` with step-by-step setup instructions
4. Update agent context with technology stack
5. Proceed to `/sp.tasks` for implementation task breakdown
