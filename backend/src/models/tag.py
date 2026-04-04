from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Tag(SQLModel, table=True):
    """
    Tag entity — user-scoped label for tasks.

    Tags are namespaced per user: no global tag registry. Tag names must be
    alphanumeric + hyphens (max 50 chars). UNIQUE(user_id, name) enforced at DB level.
    """

    __tablename__ = "tags"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Tag owner"
    )
    name: str = Field(
        max_length=50,
        nullable=False,
        description="Tag label (alphanumeric + hyphens only)"
    )
    color: Optional[str] = Field(
        default=None,
        max_length=7,
        nullable=True,
        description="Optional hex color code e.g. #FF5733"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
