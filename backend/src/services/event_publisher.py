"""
Event Publisher Service
Feature: 005-advanced-features-dapr-kafka

Publishes task lifecycle events to Kafka via Dapr pub/sub building block.
Falls back gracefully when DAPR_ENABLED=false (local development).
"""

import logging
import os
import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def _get_dapr_config() -> tuple[bool, int, str]:
    """Read Dapr configuration from environment."""
    enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"
    http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
    pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "taskpubsub")
    return enabled, http_port, pubsub_name


def _build_cloud_event(event_type: str, data: dict) -> dict:
    """Build a CloudEvents 1.0 compliant envelope."""
    return {
        "specversion": "1.0",
        "type": event_type,
        "source": "todo-backend",
        "id": str(uuid4()),
        "time": datetime.now(timezone.utc).isoformat(),
        "datacontenttype": "application/json",
        "data": data,
    }


def publish_task_event(event_type: str, task_data: dict, topic: str = "tasks") -> None:
    """
    Publish a task lifecycle event to Kafka via Dapr pub/sub.

    Args:
        event_type: CloudEvents type e.g. 'task.created', 'task.completed'
        task_data: Event payload dict (must NOT contain sensitive PII beyond user_id)
        topic: Kafka topic name (default: 'tasks')

    Behavior:
        - DAPR_ENABLED=false: Logs event and returns (no-op, safe for local dev)
        - DAPR_ENABLED=true: POSTs CloudEvent to Dapr sidecar with 3 retries
        - All exceptions caught and logged — never propagates to caller (graceful degradation)
    """
    enabled, http_port, pubsub_name = _get_dapr_config()

    if not enabled:
        logger.debug(
            f"[EventPublisher] DAPR_ENABLED=false — skipping event {event_type} "
            f"for task {task_data.get('task_id', 'unknown')}"
        )
        return

    correlation_id = str(uuid4())
    cloud_event = _build_cloud_event(event_type, task_data)
    url = f"http://localhost:{http_port}/v1.0/publish/{pubsub_name}/{topic}"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.post(
                url,
                content=json.dumps(cloud_event),
                headers={
                    "Content-Type": "application/cloudevents+json",
                    "X-Correlation-ID": correlation_id,
                },
                timeout=5.0,
            )
            if response.status_code in (200, 204):
                logger.info(
                    f"[EventPublisher] Published {event_type} | correlation={correlation_id}"
                )
                return
            else:
                logger.warning(
                    f"[EventPublisher] Attempt {attempt}/{max_retries} — "
                    f"Dapr returned {response.status_code} for {event_type}"
                )
        except Exception as exc:
            logger.warning(
                f"[EventPublisher] Attempt {attempt}/{max_retries} failed for "
                f"{event_type}: {exc}"
            )

    # All retries exhausted — send to dead-letter topic
    try:
        dlq_url = f"http://localhost:{http_port}/v1.0/publish/{pubsub_name}/tasks-dlq"
        httpx.post(
            dlq_url,
            content=json.dumps(cloud_event),
            headers={"Content-Type": "application/cloudevents+json"},
            timeout=5.0,
        )
        logger.error(
            f"[EventPublisher] All retries exhausted for {event_type} — "
            f"sent to tasks-dlq | correlation={correlation_id}"
        )
    except Exception as dlq_exc:
        logger.error(
            f"[EventPublisher] DLQ publish also failed for {event_type}: {dlq_exc}"
        )


def publish_reminder_event(
    task_id: str,
    user_id: str,
    task_title: str,
    trigger_at: datetime,
) -> None:
    """
    Publish a task.reminder event to the reminders topic.

    Called by the APScheduler reminder polling job when a reminder is due.
    """
    publish_task_event(
        event_type="task.reminder",
        task_data={
            "task_id": str(task_id),
            "user_id": str(user_id),
            "task_title": task_title,
            "trigger_at": trigger_at.isoformat(),
        },
        topic="reminders",
    )
