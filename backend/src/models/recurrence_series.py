from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class RecurrenceSeries(SQLModel, table=True):
    """
    RecurrenceSeries — groups recurring task instances under a common series.

    Stores the authoritative RRULE and base attributes used when spawning
    new task instances. Referenced by tasks.series_id.
    """

    __tablename__ = "recurrence_series"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    original_task_id: UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        description="First task instance in this series"
    )
    recurrence_rule: str = Field(
        nullable=False,
        description="RFC 5545 RRULE string (authoritative copy for this series)"
    )
    base_title: str = Field(
        max_length=200,
        nullable=False,
        description="Title applied to all spawned instances"
    )
    base_description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Description applied to all spawned instances"
    )
    base_priority: str = Field(
        default="medium",
        nullable=False,
        description="Priority applied to all spawned instances"
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="False when series is paused or fully deleted"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
