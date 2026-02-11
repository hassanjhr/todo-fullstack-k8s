# Backend Scripts

This directory contains utility scripts for backend operations.

## Available Scripts

### run_migrations.py

Executes SQL migration scripts against Neon PostgreSQL database.

**Usage:**
```bash
# From backend directory
python scripts/run_migrations.py
```

**Prerequisites:**
- DATABASE_URL environment variable must be set in .env file
- asyncpg package must be installed (included in requirements.txt)

**What it does:**
1. Connects to Neon PostgreSQL database
2. Runs all migration files in `migrations/` directory in numerical order
3. Verifies schema creation (tables and indexes)
4. Reports success or failure for each migration

**Output:**
- Lists all migrations found
- Shows connection status
- Displays migration execution results
- Verifies created tables and indexes

**Error Handling:**
- Exits with error if DATABASE_URL is not set
- Stops on first migration failure
- Provides detailed error messages

## Adding New Scripts

When adding new scripts to this directory:

1. Use descriptive filenames (e.g., `seed_database.py`, `backup_db.py`)
2. Include docstrings explaining purpose and usage
3. Add error handling for common failure cases
4. Update this README with script documentation
5. Make scripts executable: `chmod +x script_name.py`

## Environment Variables

Scripts in this directory may require:

- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT operations
- `API_URL` - Backend API URL (for testing scripts)

Ensure these are set in your `.env` file before running scripts.
