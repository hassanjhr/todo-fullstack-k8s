"""MCP tool functions wrapping existing task CRUD operations.

Each tool receives a user_id (injected by the runner, not the agent),
validates ownership, and returns structured results. Tools do NOT
access the database directly from the agent — they use SQLModel queries
identical to the existing tasks.py route handlers.
"""

import logging
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.task import Task

logger = logging.getLogger(__name__)


async def create_task(
    session: AsyncSession, user_id: UUID, title: str, description: str | None = None
) -> dict:
    """Create a new task for the user."""
    logger.info(f"[MCP] create_task: user={user_id}, title={title}")
    now = datetime.utcnow()
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        is_completed=False,
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return {
        "task_id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
    }


async def list_tasks(session: AsyncSession, user_id: UUID) -> dict:
    """List all tasks for the user."""
    logger.info(f"[MCP] list_tasks: user={user_id}")
    result = await session.execute(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return {
        "tasks": [
            {
                "task_id": str(t.id),
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed,
            }
            for t in tasks
        ],
        "count": len(tasks),
    }


async def get_task(session: AsyncSession, user_id: UUID, task_id: str) -> dict:
    """Get a single task by ID (validates ownership)."""
    logger.info(f"[MCP] get_task: user={user_id}, task_id={task_id}")
    try:
        tid = UUID(task_id)
    except ValueError:
        return {"error": "Invalid task_id format"}

    result = await session.execute(
        select(Task).where(Task.id == tid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": "Task not found"}
    return {
        "task_id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
    }


async def update_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """Update a task's title and/or description."""
    logger.info(f"[MCP] update_task: user={user_id}, task_id={task_id}")
    try:
        tid = UUID(task_id)
    except ValueError:
        return {"error": "Invalid task_id format"}

    result = await session.execute(
        select(Task).where(Task.id == tid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": "Task not found"}

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.flush()
    await session.refresh(task)
    return {
        "task_id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
    }


async def delete_task(session: AsyncSession, user_id: UUID, task_id: str) -> dict:
    """Delete a task (validates ownership)."""
    logger.info(f"[MCP] delete_task: user={user_id}, task_id={task_id}")
    try:
        tid = UUID(task_id)
    except ValueError:
        return {"error": "Invalid task_id format"}

    result = await session.execute(
        select(Task).where(Task.id == tid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": "Task not found"}

    await session.delete(task)
    await session.flush()
    return {"deleted": True, "task_id": task_id}


async def toggle_task(session: AsyncSession, user_id: UUID, task_id: str) -> dict:
    """Toggle a task's completion status."""
    logger.info(f"[MCP] toggle_task: user={user_id}, task_id={task_id}")
    try:
        tid = UUID(task_id)
    except ValueError:
        return {"error": "Invalid task_id format"}

    result = await session.execute(
        select(Task).where(Task.id == tid, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": "Task not found"}

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.flush()
    await session.refresh(task)
    return {
        "task_id": str(task.id),
        "title": task.title,
        "is_completed": task.is_completed,
    }
