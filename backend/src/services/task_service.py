"""
Task Service
Feature: 005-advanced-features-dapr-kafka

Handles recurring task business logic:
  - spawn_next_recurrence: create next instance when a recurring task is completed
  - handle_bulk_update: update all future instances in a series
  - handle_bulk_delete: delete all future instances in a series
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from dateutil.rrule import rrulestr

from models.task import Task
from models.reminder import Reminder
from models.task_tag import TaskTag
from models.tag import Tag
from models.recurrence_series import RecurrenceSeries

logger = logging.getLogger(__name__)


async def spawn_next_recurrence(task: Task, session: AsyncSession) -> Optional[Task]:
    """
    When a recurring task is completed, create the next task instance based on the RRULE.

    Steps:
    1. Parse the RRULE anchored to task.due_date (or now if no due_date)
    2. Find next occurrence after now
    3. Clone the task with new due_date = next occurrence
    4. Clone reminders with recalculated trigger_at values
    5. Clone task tags
    Returns the new Task, or None if no future occurrence exists.
    """
    if not task.recurrence_rule or task.is_paused:
        return None

    anchor = task.due_date or datetime.now(timezone.utc)
    try:
        rule = rrulestr(task.recurrence_rule, dtstart=anchor)
    except Exception as exc:
        logger.warning(f"Invalid RRULE '{task.recurrence_rule}' on task {task.id}: {exc}")
        return None

    now = datetime.now(timezone.utc)
    # Make anchor timezone-aware if naive
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)

    next_occurrence = rule.after(now)
    if next_occurrence is None:
        logger.info(f"No future occurrence for task {task.id}")
        return None

    # Ensure timezone-aware
    if next_occurrence.tzinfo is None:
        next_occurrence = next_occurrence.replace(tzinfo=timezone.utc)

    new_task = Task(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=False,
        priority=task.priority,
        due_date=next_occurrence,
        recurrence_rule=task.recurrence_rule,
        series_id=task.series_id,
        parent_task_id=task.id,
        is_paused=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(new_task)
    await session.flush()  # Get new_task.id

    # Clone reminders
    reminder_stmt = select(Reminder).where(
        Reminder.task_id == task.id,
        Reminder.status.in_(["pending", "sent"]),
    )
    reminder_result = await session.execute(reminder_stmt)
    original_reminders = reminder_result.scalars().all()

    for r in original_reminders:
        new_reminder = Reminder(
            task_id=new_task.id,
            user_id=task.user_id,
            offset_minutes=r.offset_minutes,
            trigger_at=next_occurrence - timedelta(minutes=r.offset_minutes),
            status="pending",
            created_at=datetime.utcnow(),
        )
        session.add(new_reminder)

    # Clone task tags
    tags_stmt = select(TaskTag, Tag.name).join(Tag, Tag.id == TaskTag.tag_id).where(TaskTag.task_id == task.id)
    tags_result = await session.execute(tags_stmt)
    for task_tag, _ in tags_result.all():
        session.add(TaskTag(task_id=new_task.id, tag_id=task_tag.tag_id))

    logger.info(f"Spawned next recurrence for task {task.id} → {new_task.id} (due {next_occurrence})")
    return new_task


async def handle_bulk_update(
    series_id: str,
    fields: dict,
    from_task_id: str,
    session: AsyncSession,
) -> int:
    """
    Update all incomplete future tasks in a series starting from from_task_id.

    Returns the number of tasks updated.
    """
    # Get the anchor created_at
    anchor_stmt = select(Task.created_at).where(Task.id == from_task_id)
    anchor_result = await session.execute(anchor_stmt)
    anchor_created_at = anchor_result.scalar_one_or_none()

    if anchor_created_at is None:
        return 0

    stmt = select(Task).where(
        Task.series_id == series_id,
        Task.is_completed == False,  # noqa: E712
        Task.created_at >= anchor_created_at,
    )
    result = await session.execute(stmt)
    tasks = result.scalars().all()

    updated = 0
    for t in tasks:
        for field, value in fields.items():
            if hasattr(t, field):
                setattr(t, field, value)
        t.updated_at = datetime.utcnow()
        session.add(t)
        updated += 1

    # Update RecurrenceSeries base fields if applicable
    series_update_keys = {"title", "description", "priority", "recurrence_rule"}
    series_fields = {k: v for k, v in fields.items() if k in series_update_keys}
    if series_fields:
        series_stmt = select(RecurrenceSeries).where(RecurrenceSeries.id == series_id)
        series_result = await session.execute(series_stmt)
        series = series_result.scalar_one_or_none()
        if series:
            if "title" in series_fields:
                series.base_title = series_fields["title"]
            if "description" in series_fields:
                series.base_description = series_fields["description"]
            if "priority" in series_fields:
                series.base_priority = series_fields["priority"]
            if "recurrence_rule" in series_fields:
                series.recurrence_rule = series_fields["recurrence_rule"]
            session.add(series)

    logger.info(f"Bulk-updated {updated} tasks in series {series_id}")
    return updated


async def handle_bulk_delete(
    series_id: str,
    from_task_id: str,
    session: AsyncSession,
) -> int:
    """
    Delete all incomplete future tasks in a series starting from from_task_id.
    If no tasks remain, mark the series as inactive.

    Returns the number of tasks deleted.
    """
    anchor_stmt = select(Task.created_at).where(Task.id == from_task_id)
    anchor_result = await session.execute(anchor_stmt)
    anchor_created_at = anchor_result.scalar_one_or_none()

    if anchor_created_at is None:
        return 0

    stmt = select(Task).where(
        Task.series_id == series_id,
        Task.is_completed == False,  # noqa: E712
        Task.created_at >= anchor_created_at,
    )
    result = await session.execute(stmt)
    tasks = result.scalars().all()

    for t in tasks:
        await session.delete(t)

    deleted = len(tasks)

    # Check if any tasks remain in the series
    remaining_stmt = select(Task).where(
        Task.series_id == series_id,
        Task.is_completed == False,  # noqa: E712
    )
    remaining_result = await session.execute(remaining_stmt)
    remaining = remaining_result.scalars().all()

    if not remaining:
        series_stmt = select(RecurrenceSeries).where(RecurrenceSeries.id == series_id)
        series_result = await session.execute(series_stmt)
        series = series_result.scalar_one_or_none()
        if series:
            series.is_active = False
            session.add(series)

    logger.info(f"Bulk-deleted {deleted} tasks from series {series_id}")
    return deleted
