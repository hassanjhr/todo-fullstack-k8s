# Task API Routes (Extended: 005-advanced-features-dapr-kafka)
# Purpose: CRUD endpoints for task management with priority, tags, search, filter, sort,
#          cursor-based pagination, and Dapr event publishing.
# Security: JWT authentication required, user data isolation enforced

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import or_, and_, case, delete as sa_delete
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
import base64
import json
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from models.task import Task
from models.tag import Tag
from models.task_tag import TaskTag
from models.reminder import Reminder
from models.recurrence_series import RecurrenceSeries
from schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
    ReminderInTask,
)
from api.deps import get_current_user, verify_user_access
from services import event_publisher

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# Cursor helpers (T037)
# ============================================================================

def encode_cursor(created_at: datetime, task_id: UUID) -> str:
    payload = {"created_at": created_at.isoformat(), "id": str(task_id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor_str: str) -> tuple[datetime, UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode()).decode()
        payload = json.loads(raw)
        return datetime.fromisoformat(payload["created_at"]), UUID(payload["id"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination cursor",
        )


# ============================================================================
# Internal helpers
# ============================================================================

async def _get_or_create_tag(name: str, user_id: UUID, session: AsyncSession) -> Tag:
    """Upsert a tag by name for a given user. Flushes but does not commit."""
    stmt = select(Tag).where(Tag.user_id == user_id, Tag.name == name)
    result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag is None:
        tag = Tag(user_id=user_id, name=name, created_at=datetime.utcnow())
        session.add(tag)
        await session.flush()
    return tag


async def _sync_task_tags(
    task_id: UUID, tag_names: List[str], user_id: UUID, session: AsyncSession
) -> None:
    """
    Replace all TaskTag rows for a task with rows derived from tag_names.
    Creates missing Tag records via _get_or_create_tag.
    """
    # Delete existing associations
    del_stmt = sa_delete(TaskTag).where(TaskTag.task_id == task_id)
    await session.execute(del_stmt)

    # Re-create from new tag list
    for name in tag_names:
        tag = await _get_or_create_tag(name, user_id, session)
        session.add(TaskTag(task_id=task_id, tag_id=tag.id))


async def _batch_load_tags(task_ids: List[UUID], session: AsyncSession) -> dict[UUID, List[str]]:
    """Fetch tag names for a list of task IDs in one query. Returns {task_id: [tag_names]}."""
    if not task_ids:
        return {}
    stmt = (
        select(TaskTag.task_id, Tag.name)
        .join(Tag, Tag.id == TaskTag.tag_id)
        .where(TaskTag.task_id.in_(task_ids))
    )
    result = await session.execute(stmt)
    tags_by_task: dict[UUID, List[str]] = {}
    for task_id, tag_name in result.all():
        tags_by_task.setdefault(task_id, []).append(tag_name)
    return tags_by_task


def _to_task_response(task: Task, tag_names: List[str]) -> TaskResponse:
    """Convert a Task ORM object + resolved tag names into a TaskResponse."""
    now = datetime.now(timezone.utc)
    # task.due_date from DB (TIMESTAMPTZ) is tz-aware; compare against tz-aware now
    due = task.due_date
    if due is not None and due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    is_overdue = (
        due is not None
        and due < now
        and not task.is_completed
    )
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        priority=task.priority,
        tags=tag_names,
        due_date=task.due_date,
        is_overdue=is_overdue,
        recurrence_rule=task.recurrence_rule,
        series_id=task.series_id,
        is_paused=task.is_paused,
        next_due_date=None,   # Populated in Phase 6 (recurring tasks)
        reminders=[],          # Populated in Phase 5 (reminders)
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


# ============================================================================
# GET /api/{user_id}/tasks — List tasks with filters, sort, cursor pagination
# (T025, T036, T037)
# ============================================================================

@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's tasks",
    description=(
        "Retrieve tasks with optional full-text search, priority/tag/status filters, "
        "sort control, and cursor-based pagination."
    ),
)
async def get_tasks(
    user_id: UUID,
    q: Optional[str] = Query(default=None, description="Full-text search on title and description"),
    priority: Optional[List[str]] = Query(default=None, description="Filter by priority (high|medium|low)"),
    tags: Optional[List[str]] = Query(default=None, description="Filter by tag names (AND logic)"),
    task_status: str = Query(default="all", alias="status", description="all|completed|pending|overdue"),
    sort_by: str = Query(default="created_at", description="created_at|priority|title|due_date"),
    sort_order: str = Query(default="desc", description="asc|desc"),
    cursor: Optional[str] = Query(default=None, description="Opaque pagination cursor"),
    limit: int = Query(default=20, ge=1, le=100, description="Page size (max 100)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskListResponse:
    verify_user_access(user_id, current_user)

    stmt = select(Task).where(Task.user_id == current_user.id)

    # --- Full-text search ---
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(Task.title.ilike(term), Task.description.ilike(term))
        )

    # --- Priority filter ---
    if priority:
        valid = [p for p in priority if p in ("high", "medium", "low")]
        if valid:
            stmt = stmt.where(Task.priority.in_(valid))

    # --- Tag filter (AND logic: task must have ALL requested tags) ---
    if tags:
        for tag_name in tags:
            tag_subq = (
                select(TaskTag.task_id)
                .join(Tag, Tag.id == TaskTag.tag_id)
                .where(Tag.name == tag_name, Tag.user_id == current_user.id)
                .scalar_subquery()
            )
            stmt = stmt.where(Task.id.in_(tag_subq))

    # --- Status filter ---
    now = datetime.now(timezone.utc)
    if task_status == "completed":
        stmt = stmt.where(Task.is_completed == True)  # noqa: E712
    elif task_status == "pending":
        stmt = stmt.where(Task.is_completed == False)  # noqa: E712
    elif task_status == "overdue":
        stmt = stmt.where(Task.is_completed == False, Task.due_date < now)  # noqa: E712

    # --- Cursor (always anchored to (created_at, id)) ---
    if cursor:
        cur_created_at, cur_id = decode_cursor(cursor)
        stmt = stmt.where(
            or_(
                Task.created_at < cur_created_at,
                and_(Task.created_at == cur_created_at, Task.id < cur_id),
            )
        )

    # --- Sort ---
    priority_rank = case(
        (Task.priority == "high", 1),
        (Task.priority == "medium", 2),
        (Task.priority == "low", 3),
        else_=4,
    )
    asc_flag = sort_order.lower() == "asc"

    if sort_by == "priority":
        primary_order = priority_rank if asc_flag else priority_rank.desc()
    elif sort_by == "title":
        primary_order = Task.title.asc() if asc_flag else Task.title.desc()
    elif sort_by == "due_date":
        primary_order = Task.due_date.asc() if asc_flag else Task.due_date.desc()
    else:  # created_at (default)
        primary_order = Task.created_at.asc() if asc_flag else Task.created_at.desc()

    # Always add (created_at DESC, id DESC) as tie-breaker for stable cursor pagination
    stmt = stmt.order_by(primary_order, Task.created_at.desc(), Task.id.desc())
    stmt = stmt.limit(limit + 1)

    result = await session.execute(stmt)
    tasks = list(result.scalars().all())

    has_more = len(tasks) > limit
    if has_more:
        tasks = tasks[:limit]

    next_cursor: Optional[str] = None
    if has_more and tasks:
        last = tasks[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    tags_by_task = await _batch_load_tags([t.id for t in tasks], session)
    task_responses = [_to_task_response(t, tags_by_task.get(t.id, [])) for t in tasks]

    return TaskListResponse(tasks=task_responses, next_cursor=next_cursor, has_more=has_more)


# ============================================================================
# GET /api/{user_id}/tasks/{task_id} — Get single task
# ============================================================================

@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single task",
)
async def get_single_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    verify_user_access(user_id, current_user)

    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    tags_by_task = await _batch_load_tags([task.id], session)
    return _to_task_response(task, tags_by_task.get(task.id, []))


# ============================================================================
# POST /api/{user_id}/tasks — Create task (T024)
# ============================================================================

@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    verify_user_access(user_id, current_user)

    # Validate RRULE if provided (T059)
    if task_data.recurrence_rule:
        try:
            from dateutil.rrule import rrulestr
            rrulestr(task_data.recurrence_rule, dtstart=datetime.utcnow())
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid recurrence_rule: must be a valid RFC 5545 RRULE string",
            )

    now = datetime.utcnow()
    # Normalize due_date to UTC-naive (DB column is TIMESTAMP WITHOUT TIME ZONE)
    due_date_naive = task_data.due_date.replace(tzinfo=None) if task_data.due_date else None
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        is_completed=False,
        priority=task_data.priority,
        due_date=due_date_naive,
        recurrence_rule=task_data.recurrence_rule,
        created_at=now,
        updated_at=now,
    )
    session.add(new_task)
    await session.flush()  # Assigns new_task.id without committing

    # Create RecurrenceSeries if recurrence_rule provided (T059)
    if task_data.recurrence_rule:
        series = RecurrenceSeries(
            user_id=current_user.id,
            original_task_id=new_task.id,
            recurrence_rule=task_data.recurrence_rule,
            base_title=task_data.title,
            base_description=task_data.description,
            base_priority=task_data.priority,
            is_active=True,
            created_at=now,
        )
        session.add(series)
        await session.flush()
        new_task.series_id = series.id
        session.add(new_task)

    # Create tag associations
    resolved_tags: List[str] = []
    for tag_name in task_data.tags:
        tag = await _get_or_create_tag(tag_name, current_user.id, session)
        session.add(TaskTag(task_id=new_task.id, tag_id=tag.id))
        resolved_tags.append(tag_name)

    await session.commit()
    await session.refresh(new_task)

    logger.info(f"Task {new_task.id} created for user {current_user.id}")

    # Publish event (non-blocking, graceful degradation)
    event_publisher.publish_task_event(
        "task.created",
        {
            "task_id": str(new_task.id),
            "user_id": str(current_user.id),
            "title": new_task.title,
            "priority": new_task.priority,
            "tags": resolved_tags,
        },
    )

    return _to_task_response(new_task, resolved_tags)


# ============================================================================
# PUT /api/{user_id}/tasks/{task_id} — Update task fields
# ============================================================================

@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    verify_user_access(user_id, current_user)

    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Apply updates (only non-None values)
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.is_completed is not None:
        task.is_completed = task_data.is_completed
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date.replace(tzinfo=None)
    if task_data.recurrence_rule is not None:
        task.recurrence_rule = task_data.recurrence_rule
    if task_data.is_paused is not None:
        task.is_paused = task_data.is_paused
    task.updated_at = datetime.utcnow()

    # When marking complete, cancel all pending reminders (T046)
    if task_data.is_completed is True:
        cancel_stmt = select(Reminder).where(
            Reminder.task_id == task.id,
            Reminder.status == "pending",
        )
        cancel_result = await session.execute(cancel_stmt)
        for r in cancel_result.scalars().all():
            r.status = "cancelled"
            session.add(r)

    # When due_date changes, recalculate trigger_at for pending reminders (T046)
    if task_data.due_date is not None and task_data.due_date.replace(tzinfo=None) != task.due_date:
        new_due = task_data.due_date.replace(tzinfo=None)
        recalc_stmt = select(Reminder).where(
            Reminder.task_id == task.id,
            Reminder.status == "pending",
        )
        recalc_result = await session.execute(recalc_stmt)
        from datetime import timedelta
        for r in recalc_result.scalars().all():
            r.trigger_at = new_due - timedelta(minutes=r.offset_minutes)
            session.add(r)

    # Sync tags if provided (T026)
    resolved_tags: Optional[List[str]] = None
    if task_data.tags is not None:
        await _sync_task_tags(task.id, task_data.tags, current_user.id, session)
        resolved_tags = task_data.tags

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Spawn next recurrence on completion (T060)
    if task_data.is_completed is True and task.recurrence_rule and not task.is_paused:
        from services import task_service
        # Need a new session state after commit
        new_instance = await task_service.spawn_next_recurrence(task, session)
        if new_instance:
            await session.commit()

    # Handle bulk update for "all future" scope (T060)
    elif task_data.update_scope == "all_future" and task.series_id:
        from services import task_service
        changed_fields = {
            k: v for k, v in task_data.model_dump(exclude_unset=True).items()
            if k not in ("update_scope", "tags") and v is not None
        }
        await task_service.handle_bulk_update(
            str(task.series_id), changed_fields, str(task_id), session
        )
        await session.commit()

    # Handle is_paused toggling RecurrenceSeries active state (T060)
    if task_data.is_paused is not None and task.series_id:
        series_stmt = select(RecurrenceSeries).where(RecurrenceSeries.id == task.series_id)
        series_result = await session.execute(series_stmt)
        series = series_result.scalar_one_or_none()
        if series:
            series.is_active = not task_data.is_paused
            session.add(series)
            await session.commit()

    # Load current tags for response if we didn't replace them
    if resolved_tags is None:
        tags_by_task = await _batch_load_tags([task.id], session)
        resolved_tags = tags_by_task.get(task.id, [])

    logger.info(f"Task {task_id} updated for user {current_user.id}")

    event_publisher.publish_task_event(
        "task.updated",
        {
            "task_id": str(task.id),
            "user_id": str(current_user.id),
            "title": task.title,
            "priority": task.priority,
        },
    )

    return _to_task_response(task, resolved_tags)


# ============================================================================
# DELETE /api/{user_id}/tasks/{task_id} — Delete task
# ============================================================================

@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    delete_scope: str = Query(default="this_only", description="this_only|all_future"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    verify_user_access(user_id, current_user)

    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Handle all_future bulk delete (T061)
    if delete_scope == "all_future" and task.series_id:
        from services import task_service
        await task_service.handle_bulk_delete(str(task.series_id), str(task_id), session)
        await session.commit()
        event_publisher.publish_task_event(
            "task.deleted",
            {"task_id": str(task_id), "user_id": str(current_user.id), "scope": "all_future"},
        )
        return None

    # Cancel pending reminders before delete (T081)
    cancel_stmt = select(Reminder).where(
        Reminder.task_id == task.id,
        Reminder.status == "pending",
    )
    cancel_result = await session.execute(cancel_stmt)
    for r in cancel_result.scalars().all():
        r.status = "cancelled"
        session.add(r)

    await session.delete(task)
    await session.commit()

    event_publisher.publish_task_event(
        "task.deleted",
        {"task_id": str(task_id), "user_id": str(current_user.id)},
    )
    logger.info(f"Task {task_id} deleted for user {current_user.id}")
    return None


# ============================================================================
# PATCH /api/{user_id}/tasks/{task_id}/complete — Toggle completion
# ============================================================================

@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion",
)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    verify_user_access(user_id, current_user)

    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    tags_by_task = await _batch_load_tags([task.id], session)

    event_type = "task.completed" if task.is_completed else "task.reopened"
    event_publisher.publish_task_event(
        event_type,
        {"task_id": str(task.id), "user_id": str(current_user.id)},
    )

    logger.info(f"Task {task_id} completion toggled to {task.is_completed}")
    return _to_task_response(task, tags_by_task.get(task.id, []))
