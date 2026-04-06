"""
Reminder Scheduler Service
Feature: 005-advanced-features-dapr-kafka

Polls the reminders table every REMINDER_POLL_INTERVAL seconds.
For each pending reminder whose trigger_at <= now(), publishes a
task.reminder event via Dapr pub/sub and marks the reminder as sent.
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def check_due_reminders() -> None:
    """
    Synchronous polling job executed by APScheduler.

    Queries for pending reminders past their trigger_at time and publishes
    reminder events via the event_publisher. Runs in the scheduler's thread pool.
    """
    # Import here to avoid circular imports at module load time
    from services.event_publisher import publish_reminder_event

    # Defer the async DB call by running a new event loop in the job thread
    import asyncio

    async def _run() -> None:
        from database import get_session
        from models.reminder import Reminder
        from models.task import Task
        from sqlmodel import select

        now = datetime.utcnow()  # naive UTC to match TIMESTAMP WITHOUT TIME ZONE stored in DB

        async for session in get_session():
            stmt = (
                select(Reminder, Task.title)
                .join(Task, Task.id == Reminder.task_id)
                .where(
                    Reminder.status == "pending",
                    Reminder.trigger_at <= now,
                )
            )
            result = await session.execute(stmt)
            rows = result.all()

            if not rows:
                return

            for reminder, task_title in rows:
                try:
                    publish_reminder_event(
                        task_id=str(reminder.task_id),
                        user_id=str(reminder.user_id),
                        task_title=task_title or "",
                        trigger_at=reminder.trigger_at,
                    )
                    reminder.status = "sent"
                    session.add(reminder)
                    logger.info(f"Reminder {reminder.id} processed for task {reminder.task_id}")
                except Exception as exc:
                    logger.error(f"Failed to process reminder {reminder.id}: {exc}")

            await session.commit()

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"check_due_reminders job failed: {exc}")


def start_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.info("Reminder scheduler already running")
        return

    poll_interval = int(os.getenv("REMINDER_POLL_INTERVAL", "300"))

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        check_due_reminders,
        trigger="interval",
        seconds=poll_interval,
        max_instances=1,
        replace_existing=True,
        id="check_due_reminders",
    )
    _scheduler.start()
    logger.info(f"Reminder scheduler started (interval={poll_interval}s)")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Reminder scheduler stopped")


async def check_due_reminders_async(session) -> None:
    """
    Async version of check_due_reminders for use by the Dapr cron binding handler.
    Idempotent: checks reminder.status == 'pending' before processing to prevent
    duplicate sends when both the cron binding and the legacy poll scheduler run.
    """
    from src.services.event_publisher import publish_reminder_event
    from src.models.reminder import Reminder
    from src.models.task import Task
    from sqlmodel import select

    now = datetime.utcnow()

    stmt = (
        select(Reminder, Task.title)
        .join(Task, Task.id == Reminder.task_id)
        .where(
            Reminder.status == "pending",
            Reminder.trigger_at <= now,
        )
    )
    result = await session.execute(stmt)
    rows = result.all()

    if not rows:
        logger.info("check_due_reminders_async: no pending reminders due")
        return

    for reminder, task_title in rows:
        try:
            publish_reminder_event(
                task_id=str(reminder.task_id),
                user_id=str(reminder.user_id),
                task_title=task_title or "",
                trigger_at=reminder.trigger_at,
            )
            reminder.status = "sent"
            session.add(reminder)
            logger.info(f"Reminder {reminder.id} processed for task {reminder.task_id}")
        except Exception as exc:
            logger.error(f"Failed to process reminder {reminder.id}: {exc}")

    await session.commit()
