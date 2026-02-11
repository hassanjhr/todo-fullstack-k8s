# User Pydantic Schemas (T020)
# Purpose: Request and response models for user authentication
# Security: Never expose hashed_password in response schemas

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Literal


# ============================================================================
# Request Schemas (Input Validation)
# ============================================================================

class SignupRequest(BaseModel):
    """
    Request schema for user registration.

    Fields:
        email: Valid email address (validated by EmailStr)
        password: Plain text password (minimum 8 characters)

    Validation:
        - Email format validated by Pydantic EmailStr
        - Password minimum length enforced (8 characters)
        - Password cannot be empty or whitespace only

    Security:
        - Password is validated but never logged or stored in plain text
        - Password will be hashed with bcrypt before database storage

    Example:
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
    """
    email: EmailStr = Field(
        ...,
        description="User's email address (must be valid email format)",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User's password (minimum 8 characters)",
        examples=["securepassword123"]
    )

    @field_validator('password')
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        """
        Validate password is not empty or whitespace only.

        Security: Prevents weak passwords that pass length check but are only spaces.
        """
        if not v or not v.strip():
            raise ValueError('Password cannot be empty or whitespace only')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "mypassword123"
            }
        }


class SigninRequest(BaseModel):
    """
    Request schema for user authentication.

    Fields:
        email: User's email address
        password: User's plain text password

    Validation:
        - Email format validated by EmailStr
        - Password required (no minimum length for signin)

    Security:
        - Credentials verified against hashed password in database
        - Failed attempts should return generic error message
        - No indication whether email exists or password is wrong

    Example:
        {
            "email": "user@example.com",
            "password": "mypassword123"
        }
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        description="User's password",
        examples=["mypassword123"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "mypassword123"
            }
        }


# ============================================================================
# Response Schemas (Output Serialization)
# ============================================================================

class UserResponse(BaseModel):
    """
    Response schema for user data.

    Fields:
        id: User's unique identifier (UUID)
        email: User's email address
        created_at: Account creation timestamp

    Security:
        - NEVER includes hashed_password field
        - Only exposes non-sensitive user information
        - Safe to return in API responses

    Example:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-02-06T12:00:00Z"
        }
    """
    id: UUID = Field(
        ...,
        description="User's unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    email: str = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp (UTC)",
        examples=["2026-02-06T12:00:00Z"]
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-06T12:00:00.000Z"
            }
        }


class AuthResponse(BaseModel):
    """
    Response schema for authentication endpoints (signup, signin).

    Fields:
        user: User information (UserResponse)
        token: JWT access token
        token_type: Token type (always "bearer")

    Security:
        - Token should be stored securely on frontend (httpOnly cookie or secure storage)
        - Token must be included in Authorization header for protected endpoints
        - Token contains user_id in "sub" claim for authentication

    Usage:
        Frontend should store token and include in subsequent requests:
        Authorization: Bearer <token>

    Example:
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-06T12:00:00Z"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    user: UserResponse = Field(
        ...,
        description="Authenticated user information"
    )

    token: str = Field(
        ...,
        description="JWT access token for authentication",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Token type (always 'bearer' for JWT)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "created_at": "2026-02-06T12:00:00.000Z"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MDk4MjcyMDAsImlhdCI6MTcwOTc0MDgwMCwidHlwZSI6ImFjY2VzcyJ9.signature",
                "token_type": "bearer"
            }
        }
