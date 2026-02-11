# User SQLModel
# Purpose: Represents an authenticated user account
# Relationships: One User has many Tasks (1:N)

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class User(SQLModel, table=True):
    """
    User entity for authentication and task ownership.

    Fields:
        id: Unique user identifier (UUID)
        email: User's email address (unique, used for login)
        hashed_password: Bcrypt-hashed password (never store plain text)
        created_at: Account creation timestamp

    Security:
        - Never expose hashed_password in API responses
        - Email uniqueness prevents duplicate accounts
        - UUID primary key prevents enumeration attacks

    Indexes:
        - PRIMARY KEY (id): Clustered index
        - UNIQUE INDEX idx_user_email: Fast email lookup for authentication
    """

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    # Primary key: UUID for security (prevents enumeration)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique user identifier"
    )

    # Email: Unique identifier for authentication
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        nullable=False,
        description="User's email address (used for login)"
    )

    # Password: Always hashed with bcrypt (cost factor 12)
    hashed_password: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt-hashed password (never store plain text)"
    )

    # Audit field: Account creation timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp"
    )

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-06T12:00:00Z"
            }
        }
