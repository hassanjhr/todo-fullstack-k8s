from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID


class TaskTag(SQLModel, table=True):
    """
    TaskTag — many-to-many junction between tasks and tags.

    Composite PK (task_id, tag_id). Both FKs cascade on delete.
    """

    __tablename__ = "task_tags"
    __table_args__ = {"extend_existing": True}

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False
    )
    tag_id: UUID = Field(
        foreign_key="tags.id",
        primary_key=True,
        nullable=False
    )
    added_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
