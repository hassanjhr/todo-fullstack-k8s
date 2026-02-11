# Database Connection and Session Management
# Purpose: Configure Neon PostgreSQL connection with asyncpg driver
# Provides async session management for SQLModel operations

from sqlmodel import SQLModel, create_engine
# from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
# from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure asyncpg driver is used
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    # Convert postgresql:// to postgresql+asyncpg://
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
# Configuration for Neon Serverless PostgreSQL:
# - pool_pre_ping: Verify connections before using (handles serverless cold starts)
# - echo: Log SQL statements (disable in production)
# - pool_size: Connection pool size (Neon handles pooling, keep modest)
# - max_overflow: Additional connections beyond pool_size
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Verify connection health before use
    pool_size=5,  # Base connection pool size
    max_overflow=10,  # Allow up to 15 total connections
)

# Create async session factory
# expire_on_commit=False: Prevent lazy loading issues with async sessions
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialize database tables.

    Note: In production, use Alembic migrations instead.
    This function is useful for development/testing.
    """
    async with engine.begin() as conn:
        # Create all tables defined in SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.exec(select(Item))
            return result.all()

    Yields:
        AsyncSession: Database session for async operations
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """
    Close database connection pool.

    Call this during application shutdown to gracefully close connections.
    """
    await engine.dispose()
