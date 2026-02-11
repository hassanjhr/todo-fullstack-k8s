#!/usr/bin/env python3
"""
Database Migration Runner
Purpose: Execute SQL migration scripts against Neon PostgreSQL database
Usage: python run_migrations.py
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set")
    print("Please set DATABASE_URL in your .env file")
    sys.exit(1)

# Convert to asyncpg format if needed
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def run_migration(conn: asyncpg.Connection, migration_file: Path) -> None:
    """
    Execute a single migration file.

    Args:
        conn: Database connection
        migration_file: Path to SQL migration file
    """
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_file.name}")
    print(f"{'='*60}")

    # Read migration SQL
    sql = migration_file.read_text()

    # Remove DOWN migration comments (everything after "-- DOWN Migration")
    if "-- DOWN Migration" in sql:
        sql = sql.split("-- DOWN Migration")[0]

    try:
        # Execute migration
        await conn.execute(sql)
        print(f"✓ Migration {migration_file.name} completed successfully")
    except Exception as e:
        print(f"✗ Migration {migration_file.name} failed: {e}")
        raise


async def main():
    """Main migration runner"""
    print("Database Migration Runner")
    print("=" * 60)

    # Get migrations directory
    migrations_dir = Path(__file__).parent.parent / "migrations"

    if not migrations_dir.exists():
        print(f"ERROR: Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    # Get all migration files in order
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        sys.exit(0)

    print(f"Found {len(migration_files)} migration(s)")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}")

    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    try:
        # Run migrations in order
        for migration_file in migration_files:
            await run_migration(conn, migration_file)

        print(f"\n{'='*60}")
        print("✓ All migrations completed successfully")
        print(f"{'='*60}")

        # Verify schema
        print("\nVerifying schema...")
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        print(f"Tables created: {', '.join([t['table_name'] for t in tables])}")

        # Check indexes
        indexes = await conn.fetch("""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY indexname
        """)

        print(f"Indexes created: {', '.join([i['indexname'] for i in indexes])}")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)
    finally:
        await conn.close()
        print("\nDatabase connection closed")


if __name__ == "__main__":
    asyncio.run(main())
