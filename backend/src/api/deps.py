# API Dependencies
# Purpose: Dependency injection functions for FastAPI routes
# Security: JWT authentication and user verification

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional
from uuid import UUID

# Import database session dependency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_session
from models.user import User
from utils.security import extract_user_id_from_token, verify_token


# HTTP Bearer token scheme for Authorization header
# Expects: Authorization: Bearer <token>
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    JWT authentication dependency for protected routes.

    Extracts and verifies JWT token from Authorization header,
    then retrieves the authenticated user from the database.

    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session for user lookup

    Returns:
        User: Authenticated user object from database

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found

    Security Flow:
        1. Extract JWT token from Authorization header (Bearer scheme)
        2. Verify token signature and expiration
        3. Extract user_id from token payload (sub claim)
        4. Query database for user with matching user_id
        5. Return User object if found
        6. Raise 401 if any step fails

    Usage in FastAPI routes:
        @router.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: UUID,
            current_user: User = Depends(get_current_user)
        ):
            # Verify user_id matches authenticated user
            if user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access forbidden")
            # ... rest of endpoint logic

    Example:
        # Request with valid token
        GET /api/tasks
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        # Response: User object returned to endpoint
        # Request with invalid token: 401 Unauthorized
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify token and extract payload
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token payload
    user_id_str = payload.get("sub")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert user_id string to UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: malformed user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query database for user
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """
    Optional JWT authentication dependency for routes that support both authenticated and anonymous access.

    Similar to get_current_user but returns None instead of raising 401 if no token provided.

    Args:
        credentials: Optional HTTP Bearer token from Authorization header
        session: Database session for user lookup

    Returns:
        Optional[User]: Authenticated user object if valid token provided, None otherwise

    Usage:
        @router.get("/api/public-data")
        async def get_public_data(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            if current_user:
                # Return personalized data
                pass
            else:
                # Return public data
                pass
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None


def verify_user_access(user_id: UUID, current_user: User) -> None:
    """
    Verify that the authenticated user has access to resources for the specified user_id.

    This enforces user data isolation by ensuring the user_id in the URL matches
    the authenticated user's ID from the JWT token.

    Args:
        user_id: User ID from URL path parameter
        current_user: Authenticated user from JWT token

    Raises:
        HTTPException 403: If user_id does not match authenticated user's ID

    Security:
        - Prevents users from accessing other users' data
        - Must be called in every endpoint that includes user_id in path
        - Enforces data isolation at API level

    Usage:
        @router.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: UUID,
            current_user: User = Depends(get_current_user)
        ):
            verify_user_access(user_id, current_user)
            # ... rest of endpoint logic
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You can only access your own resources"
        )
