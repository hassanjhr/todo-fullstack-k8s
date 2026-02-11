# Database Migrations

This directory contains SQL migration scripts for the Todo Full-Stack Web Application database schema.

## Migration Files

- `001_create_users_table.sql` - Creates users table with UUID primary key and email uniqueness
- `002_create_tasks_table.sql` - Creates tasks table with foreign key to users and performance indexes

## Running Migrations

### Option 1: Manual Execution (Development)

Connect to your Neon PostgreSQL database and run migrations in order:

```bash
# Set your DATABASE_URL
export DATABASE_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

# Run migrations using psql
psql $DATABASE_URL -f migrations/001_create_users_table.sql
psql $DATABASE_URL -f migrations/002_create_tasks_table.sql
```

### Option 2: Using Python Script (Recommended)

```bash
# From backend directory
python -m scripts.run_migrations
```

### Option 3: Using Alembic (Production)

For production environments, consider using Alembic for migration management:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Generate migration from SQLModel
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head
```

## Migration Order

**CRITICAL**: Migrations must be run in numerical order:

1. `001_create_users_table.sql` - Creates users table (no dependencies)
2. `002_create_tasks_table.sql` - Creates tasks table (depends on users table)

## Rollback

Each migration includes a commented-out DOWN migration section. To rollback:

1. Uncomment the DOWN migration section
2. Run the SQL script
3. Re-comment the DOWN section

**Example**:
```sql
-- Rollback 002_create_tasks_table.sql
BEGIN;
DROP TABLE IF EXISTS tasks CASCADE;
COMMIT;
```

## Verification

After running migrations, verify the schema:

```sql
-- List all tables
\dt

-- Describe users table
\d users

-- Describe tasks table
\d tasks

-- List all indexes
\di
```

Expected output:
- Tables: `users`, `tasks`
- Indexes: `idx_user_email`, `idx_task_user_id`, `idx_task_user_created`
- Foreign key: `tasks.user_id` → `users.id` with ON DELETE CASCADE

## Schema Diagram

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
│ user_id (FK)    │◄─── Foreign Key to User.id (ON DELETE CASCADE)
│ title           │
│ description     │
│ is_completed    │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Troubleshooting

### Error: "extension uuid-ossp does not exist"

Neon PostgreSQL should have this extension available. If not, contact Neon support or use `gen_random_uuid()` instead:

```sql
-- Alternative UUID generation
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Error: "relation users does not exist"

You must run `001_create_users_table.sql` before `002_create_tasks_table.sql`.

### Error: "permission denied to create extension"

Ensure your database user has sufficient privileges. Neon databases typically have extensions pre-enabled.

## Next Steps

After running migrations:

1. Verify schema with `\d users` and `\d tasks`
2. Test connection from backend application
3. Run backend tests to validate database operations
4. Proceed with implementing API endpoints
