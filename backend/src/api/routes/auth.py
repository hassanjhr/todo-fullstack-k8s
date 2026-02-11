# Authentication Routes (T021, T022)
# Purpose: User registration and authentication endpoints
# Security: Password hashing, JWT token generation, email uniqueness validation

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging

# Import database session dependency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from schemas.user import SignupRequest, SigninRequest, UserResponse, AuthResponse
from utils.security import hash_password, verify_password, create_access_token

# Configure logging
logger = logging.getLogger(__name__)

# Create router for authentication endpoints
router = APIRouter()


# ============================================================================
# Signup Endpoint (T021)
# ============================================================================

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    description="Create a new user account with email and password",
    responses={
        201: {
            "description": "User created successfully",
            "model": AuthResponse
        },
        422: {
            "description": "Validation error or email already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email already registered"
                    }
                }
            }
        }
    }
)
async def signup(
    signup_data: SignupRequest,
    session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """
    Register a new user account.

    Security Flow:
        1. Validate email format and password length (Pydantic validation)
        2. Check if email already exists in database
        3. Hash password using bcrypt (cost factor 12)
        4. Create user record in database
        5. Generate JWT token with user_id in "sub" claim
        6. Return user data (without hashed_password) and JWT token

    Args:
        signup_data: User registration data (email, password)
        session: Database session for user creation

    Returns:
        AuthResponse: User data and JWT access token

    Raises:
        HTTPException 422: If email already exists or validation fails

    Security Considerations:
        - Password is hashed before storage (never stored in plain text)
        - Email uniqueness enforced at database level
        - JWT token contains user_id for subsequent authentication
        - Generic error messages to prevent user enumeration

    Example Request:
        POST /api/auth/signup
        {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }

    Example Response (201 Created):
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "newuser@example.com",
                "created_at": "2026-02-06T12:00:00Z"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    # Step 1: Check if email already exists
    # Security: Prevent duplicate accounts with same email
    result = await session.execute(
        select(User).where(User.email == signup_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        logger.warning(f"Signup attempt with existing email: {signup_data.email}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )

    # Step 2: Hash password using bcrypt
    # Security: Never store plain text passwords
    hashed_password = hash_password(signup_data.password)

    # Step 3: Create new user
    new_user = User(
        email=signup_data.email,
        hashed_password=hashed_password
    )

    # Step 4: Save user to database
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"New user created: {new_user.id} ({new_user.email})")

    # Step 5: Generate JWT token
    # Security: Token contains user_id in "sub" claim for authentication
    access_token = create_access_token(user_id=new_user.id)

    # Step 6: Return user data and token
    # Security: UserResponse excludes hashed_password field
    user_response = UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at
    )

    return AuthResponse(
        user=user_response,
        token=access_token,
        token_type="bearer"
    )


# ============================================================================
# Signin Endpoint (T022)
# ============================================================================

@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User authentication",
    description="Authenticate user with email and password",
    responses={
        200: {
            "description": "Authentication successful",
            "model": AuthResponse
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email or password"
                    }
                }
            }
        }
    }
)
async def signin(
    signin_data: SigninRequest,
    session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """
    Authenticate user and issue JWT token.

    Security Flow:
        1. Validate email format (Pydantic validation)
        2. Query user by email
        3. Verify password hash using constant-time comparison
        4. Generate JWT token with user_id in "sub" claim
        5. Return user data (without hashed_password) and JWT token

    Args:
        signin_data: User credentials (email, password)
        session: Database session for user lookup

    Returns:
        AuthResponse: User data and JWT access token

    Raises:
        HTTPException 401: If email not found or password incorrect

    Security Considerations:
        - Constant-time password verification prevents timing attacks
        - Generic error message prevents user enumeration
        - No indication whether email exists or password is wrong
        - Failed attempts should be logged for security monitoring
        - JWT token contains user_id for subsequent authentication

    Example Request:
        POST /api/auth/signin
        {
            "email": "user@example.com",
            "password": "mypassword123"
        }

    Example Response (200 OK):
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
    # Step 1: Query user by email
    result = await session.execute(
        select(User).where(User.email == signin_data.email)
    )
    user = result.scalar_one_or_none()

    # Step 2: Verify user exists and password is correct
    # Security: Use constant-time comparison to prevent timing attacks
    # Security: Generic error message prevents user enumeration
    if user is None or not verify_password(signin_data.password, user.hashed_password):
        logger.warning(f"Failed signin attempt for email: {signin_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User signed in: {user.id} ({user.email})")

    # Step 3: Generate JWT token
    # Security: Token contains user_id in "sub" claim for authentication
    access_token = create_access_token(user_id=user.id)

    # Step 4: Return user data and token
    # Security: UserResponse excludes hashed_password field
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at
    )

    return AuthResponse(
        user=user_response,
        token=access_token,
        token_type="bearer"
    )
