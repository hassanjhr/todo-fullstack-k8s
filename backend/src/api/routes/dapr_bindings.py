# Dapr Binding Handlers
# Feature: 006-full-dapr-oracle-deploy
# Purpose: Handles incoming Dapr binding triggers (cron, etc.)
# Note: No JWT required — these endpoints are called by the Dapr sidecar internally

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dapr Bindings"])


@router.post("/reminder-cron")
async def handle_reminder_cron(db: AsyncSession = Depends(get_session)):
    """
    Dapr cron binding handler — called by Dapr sidecar on configured schedule.

    Processes all pending reminders whose trigger_at time has passed.
    This replaces the APScheduler poll-based approach when running on Kubernetes
    with Dapr enabled (DAPR_ENABLED=true).

    The binding name 'reminder-cron' in the Dapr component YAML maps to this
    endpoint path: POST /reminder-cron

    Returns:
        200 OK — reminders processed (Dapr will not retry)
        500    — processing failed (Dapr will retry based on component config)
    """
    logger.info("Dapr cron binding fired: processing due reminders")
    try:
        from src.services.reminder_service import check_due_reminders_async
        await check_due_reminders_async(db)
        logger.info("Dapr cron binding: reminder processing complete")
        return {"status": "ok"}
    except Exception as exc:
        logger.error(f"Dapr cron binding: reminder processing failed: {exc}")
        raise
