# Reminders API Routes
# Feature: 005-advanced-features-dapr-kafka
# Purpose: CRUD for task reminders + Dapr subscriber endpoint
# Security: JWT required; ownership verified per task and reminder

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime, timedelta, timezone
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from models.task import Task
from models.reminder import Reminder
from schemas.reminder import ReminderCreateRequest, ReminderResponse
from api.deps import get_current_user, verify_user_access

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# POST /api/{user_id}/tasks/{task_id}/reminders — Create reminder
# ============================================================================

@router.post(
    "/{user_id}/tasks/{task_id}/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reminder for a task",
)
async def create_reminder(
    user_id: UUID,
    task_id: UUID,
    reminder_data: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ReminderResponse:
    verify_user_access(user_id, current_user)

    # Verify task exists and user owns it
    task_stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    task_result = await session.execute(task_stmt)
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.due_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task must have a due_date before adding reminders",
        )

    # Normalize due_date to UTC-naive before arithmetic (DB column is TIMESTAMP WITHOUT TIME ZONE)
    due_naive = task.due_date.replace(tzinfo=None) if task.due_date.tzinfo else task.due_date
    trigger_at = due_naive - timedelta(minutes=reminder_data.offset_minutes)

    new_reminder = Reminder(
        task_id=task.id,
        user_id=current_user.id,
        offset_minutes=reminder_data.offset_minutes,
        trigger_at=trigger_at,
        status="pending",
        created_at=datetime.utcnow(),
    )
    session.add(new_reminder)
    await session.commit()
    await session.refresh(new_reminder)

    logger.info(f"Reminder {new_reminder.id} created for task {task_id}")
    return ReminderResponse(
        id=new_reminder.id,
        offset_minutes=new_reminder.offset_minutes,
        trigger_at=new_reminder.trigger_at,
        status=new_reminder.status,
    )


# ============================================================================
# DELETE /api/{user_id}/tasks/{task_id}/reminders/{reminder_id}
# ============================================================================

@router.delete(
    "/{user_id}/tasks/{task_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reminder",
)
async def delete_reminder(
    user_id: UUID,
    task_id: UUID,
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    verify_user_access(user_id, current_user)

    stmt = select(Reminder).where(
        Reminder.id == reminder_id,
        Reminder.task_id == task_id,
        Reminder.user_id == current_user.id,
    )
    result = await session.execute(stmt)
    reminder = result.scalar_one_or_none()

    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    await session.delete(reminder)
    await session.commit()

    logger.info(f"Reminder {reminder_id} deleted")
    return None


# ============================================================================
# POST /notifications/reminder — Dapr subscriber endpoint
# ============================================================================

@router.post(
    "/notifications/reminder",
    status_code=status.HTTP_200_OK,
    summary="Dapr reminder notification subscriber",
    include_in_schema=False,
)
async def handle_reminder_notification(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Receives CloudEvents-wrapped reminder events from Dapr pub/sub.
    Marks the corresponding reminder as 'sent'.
    """
    try:
        payload = await request.json()
        data = payload.get("data", payload)
        task_id_str = data.get("task_id")

        if task_id_str:
            task_id = UUID(task_id_str)
            trigger_at_str = data.get("trigger_at")
            if trigger_at_str:
                trigger_at = datetime.fromisoformat(trigger_at_str)
                # Mark matching pending reminder as sent
                stmt = select(Reminder).where(
                    Reminder.task_id == task_id,
                    Reminder.status == "pending",
                    Reminder.trigger_at <= trigger_at,
                )
                result = await session.execute(stmt)
                reminders = result.scalars().all()
                for r in reminders:
                    r.status = "sent"
                    session.add(r)
                await session.commit()
                logger.info(f"Marked {len(reminders)} reminders as sent for task {task_id}")
    except Exception as exc:
        logger.error(f"Error processing reminder notification: {exc}")
        # Return 200 regardless to prevent Dapr from retrying indefinitely

    return {"status": "SUCCESS"}


# ============================================================================
# GET /dapr/subscribe — Dapr subscription config
# ============================================================================

@router.get(
    "/dapr/subscribe",
    include_in_schema=False,
)
async def dapr_subscribe() -> list:
    """
    Returns Dapr subscription configuration for the pub/sub building block.
    Dapr calls this endpoint on sidecar startup to discover subscriptions.
    """
    return [
        {
            "pubsubname": os.getenv("DAPR_PUBSUB_NAME", "taskpubsub"),
            "topic": "reminders",
            "route": "/notifications/reminder",
        }
    ]
