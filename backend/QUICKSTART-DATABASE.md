# Database Layer Implementation - Quick Reference

## Files Created (T007-T010)

### Database Connection
- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/src/database.py`
- **Purpose**: Async database connection with Neon PostgreSQL using asyncpg driver
- **Key Functions**: `get_session()`, `init_db()`, `close_db()`

### SQLModel Definitions
- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/src/models/user.py`
- **Model**: `User` with id, email, hashed_password, created_at

- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/src/models/task.py`
- **Model**: `Task` with id, user_id (FK), title, description, is_completed, created_at, updated_at

- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/src/models/__init__.py`
- **Purpose**: Package exports for User and Task models

### Database Migrations
- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/migrations/001_create_users_table.sql`
- **Creates**: users table with UUID PK, unique email index

- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/migrations/002_create_tasks_table.sql`
- **Creates**: tasks table with FK to users, indexes on user_id and (user_id, created_at)

### Migration Runner
- **File**: `/mnt/e/GenAI Govenor/Quater_4-official/hackathon_2/hackathon_2_phase_2/backend/scripts/run_migrations.py`
- **Purpose**: Automated migration execution
- **Usage**: `python scripts/run_migrations.py`

## Quick Start

### 1. Set Environment Variables
```bash
# In backend/.env
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python scripts/run_migrations.py
```

### 4. Verify Schema
```bash
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d users"  # Describe users table
psql $DATABASE_URL -c "\d tasks"  # Describe tasks table
```

## Usage in FastAPI Endpoints

```python
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.database import get_session
from backend.src.models import User, Task

@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    # Query with user_id filtering for data isolation
    result = await session.exec(
        select(Task).where(Task.user_id == user_id)
    )
    return result.all()
```

## Security Notes

1. **Always filter by user_id**: `WHERE Task.user_id == authenticated_user_id`
2. **Never expose hashed_password** in API responses
3. **Use UUID primary keys** to prevent enumeration
4. **Foreign key CASCADE** ensures data consistency

## Next Tasks (Phase 2 Remaining)

- T011: Password hashing utilities
- T012: JWT token utilities
- T013: JWT authentication dependency
- T014-T016: FastAPI configuration
- T017-T019: Frontend infrastructure
