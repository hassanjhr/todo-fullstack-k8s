# Data Model: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-app
**Date**: 2026-02-06
**Purpose**: Define database entities, relationships, and validation rules

## Overview

This document defines the data model for the Todo Full-Stack Web Application. The model enforces user data isolation through foreign key relationships and query-level filtering.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ email (unique)  │
│ hashed_password │
│ created_at      │
└─────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│      Task       │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │◄─── Foreign Key to User.id
│ title           │
│ description     │
│ is_completed    │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

**Relationship**: One User has many Tasks (1:N)
**Cascade**: Deleting a User deletes all their Tasks (CASCADE)

---

## Entity: User

### Purpose
Represents an authenticated user account. Users own tasks and can only access their own data.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never store plain text) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### Validation Rules

- **email**: Must be valid email format (validated by Pydantic EmailStr)
- **email**: Must be unique across all users
- **hashed_password**: Minimum 8 characters before hashing (validated at API level)
- **hashed_password**: Hashed using bcrypt with cost factor 12

### Indexes

- `PRIMARY KEY (id)` - Clustered index on id
- `UNIQUE INDEX idx_user_email ON users(email)` - Fast email lookup for authentication

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Security Considerations

- **Never expose hashed_password** in API responses
- **Email uniqueness** prevents duplicate accounts
- **Password hashing** uses bcrypt (industry standard)
- **UUID primary key** prevents enumeration attacks

---

## Entity: Task

### Purpose
Represents a todo item owned by a specific user. Tasks are always scoped to a single user.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique task identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL, ON DELETE CASCADE | Owner of this task |
| `title` | VARCHAR(200) | NOT NULL | Task title (required) |
| `description` | TEXT | NULL | Optional task description |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp |

### Validation Rules

- **title**: Required, non-empty, maximum 200 characters
- **description**: Optional, maximum 2000 characters if provided
- **user_id**: Must reference an existing user (enforced by foreign key)
- **is_completed**: Defaults to false for new tasks

### Indexes

- `PRIMARY KEY (id)` - Clustered index on id
- `INDEX idx_task_user_id ON tasks(user_id)` - Fast filtering by user_id (critical for data isolation)
- `INDEX idx_task_user_created ON tasks(user_id, created_at DESC)` - Optimized for user's task list sorted by creation date

### Foreign Key Constraints

- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`
  - **ON DELETE CASCADE**: When a user is deleted, all their tasks are automatically deleted
  - **Rationale**: Prevents orphaned tasks and ensures data consistency

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional, for ORM convenience)
    # user: Optional["User"] = Relationship(back_populates="tasks")
```

### Security Considerations

- **user_id filtering**: ALL queries MUST filter by authenticated user's user_id
- **Foreign key constraint**: Prevents tasks from referencing non-existent users
- **Index on user_id**: Ensures fast filtering without performance degradation
- **No public tasks**: Tasks are always private to the owning user

---

## Data Isolation Strategy

### Query-Level Filtering

**Critical**: All task queries MUST include `WHERE user_id = <authenticated_user_id>` to enforce data isolation.

**Example Queries**:

```python
# ✅ CORRECT: Filter by authenticated user_id
tasks = session.exec(
    select(Task).where(Task.user_id == current_user.id)
).all()

# ❌ INCORRECT: No user_id filter (exposes all tasks)
tasks = session.exec(select(Task)).all()
```

### API Endpoint Verification

All task endpoints MUST:
1. Extract user_id from verified JWT token
2. Verify URL user_id parameter matches authenticated user_id
3. Filter database queries by authenticated user_id
4. Return 403 Forbidden if user_id mismatch detected

**Example Endpoint Logic**:

```python
@router.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Verify user_id in URL matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Query with user_id filter
    tasks = await session.exec(
        select(Task).where(Task.user_id == current_user.id)
    )
    return tasks.all()
```

---

## Database Migrations

### Initial Schema Creation

**Migration 001: Create users table**
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_user_email ON users(email);
```

**Migration 002: Create tasks table**
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_user_id ON tasks(user_id);
CREATE INDEX idx_task_user_created ON tasks(user_id, created_at DESC);
```

### Migration Tool

**Option 1**: Alembic (recommended for production)
- Full migration history
- Automatic migration generation from SQLModel changes
- Rollback support

**Option 2**: Manual SQL scripts (acceptable for hackathon)
- Simple, no additional dependencies
- Run scripts directly against Neon database
- Sufficient for basic implementation

---

## Sample Data

### Test Users

```json
[
  {
    "email": "alice@example.com",
    "password": "password123",
    "hashed_password": "$2b$12$..."
  },
  {
    "email": "bob@example.com",
    "password": "password123",
    "hashed_password": "$2b$12$..."
  }
]
```

### Test Tasks (for Alice)

```json
[
  {
    "user_id": "<alice_uuid>",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": false
  },
  {
    "user_id": "<alice_uuid>",
    "title": "Finish project report",
    "description": null,
    "is_completed": true
  }
]
```

### Test Tasks (for Bob)

```json
[
  {
    "user_id": "<bob_uuid>",
    "title": "Call dentist",
    "description": "Schedule annual checkup",
    "is_completed": false
  }
]
```

**Expected Behavior**: Alice can only see her 2 tasks, Bob can only see his 1 task.

---

## Performance Considerations

1. **Indexing**: user_id index ensures O(log n) lookup for user's tasks
2. **Composite Index**: (user_id, created_at DESC) optimizes sorted task lists
3. **Connection Pooling**: Neon connection pool handles concurrent queries
4. **Async Queries**: asyncpg enables non-blocking database operations

---

## Validation Summary

| Entity | Field | Validation | Enforced By |
|--------|-------|------------|-------------|
| User | email | Valid email format | Pydantic EmailStr |
| User | email | Unique | Database UNIQUE constraint |
| User | password | Minimum 8 characters | API validation (before hashing) |
| Task | title | Required, max 200 chars | Pydantic Field validation |
| Task | description | Optional, max 2000 chars | Pydantic Field validation |
| Task | user_id | Must reference existing user | Database FOREIGN KEY |
| Task | user_id | Must match authenticated user | API endpoint logic |

---

## Next Steps

1. Generate API contracts in `contracts/` directory
2. Implement SQLModel definitions in `backend/src/models/`
3. Create database migration scripts
4. Implement query-level filtering in API endpoints
