# Security Utilities
# Purpose: Password hashing and JWT token management
# Security: Uses bcrypt for password hashing and HS256 for JWT signing

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

# Import settings for JWT configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


# Password Hashing Configuration
# Using bcrypt with cost factor 12 (industry standard for security)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# ============================================================================
# Password Hashing Functions (T011)
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt-hashed password (60 characters)

    Security:
        - Uses bcrypt algorithm with cost factor 12
        - Automatically generates salt
        - Resistant to rainbow table attacks
        - Computationally expensive to brute force

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(len(hashed))  # 60 characters
        60
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt-hashed password from database

    Returns:
        bool: True if password matches, False otherwise

    Security:
        - Constant-time comparison to prevent timing attacks
        - Handles invalid hash formats gracefully

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Invalid hash format or verification error
        return False


# ============================================================================
# JWT Token Functions (T012)
# ============================================================================

def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authenticated user.

    Args:
        user_id: User's unique identifier (UUID)
        expires_delta: Optional custom expiration time (default: from settings)

    Returns:
        str: Encoded JWT token

    Token Payload:
        - sub: User ID (subject claim)
        - exp: Expiration timestamp
        - iat: Issued at timestamp
        - type: Token type ("access")

    Security:
        - Signed with HS256 algorithm
        - Secret key from environment variable
        - Expiration enforced (default: 24 hours)

    Example:
        >>> from uuid import uuid4
        >>> user_id = uuid4()
        >>> token = create_access_token(user_id)
        >>> print(len(token) > 100)  # JWT tokens are long strings
        True
    """
    # Calculate expiration time
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.get_jwt_expiration_seconds())

    expire = datetime.utcnow() + expires_delta

    # Create token payload
    to_encode = {
        "sub": str(user_id),  # Subject: user ID (convert UUID to string)
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at time
        "type": "access"  # Token type
    }

    # Encode and sign token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Optional[Dict[str, Any]]: Decoded token payload if valid, None if invalid

    Validation:
        - Verifies signature using secret key
        - Checks expiration time
        - Validates token structure

    Raises:
        None: Returns None instead of raising exceptions for invalid tokens

    Example:
        >>> token = create_access_token(uuid4())
        >>> payload = verify_token(token)
        >>> print("sub" in payload)
        True
        >>> print("exp" in payload)
        True
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Validate token type
        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        # Token is invalid, expired, or malformed
        return None
    except Exception:
        # Unexpected error during verification
        return None


def extract_user_id_from_token(token: str) -> Optional[UUID]:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        Optional[UUID]: User ID if token is valid, None otherwise

    Security:
        - Verifies token before extracting user ID
        - Returns None for invalid tokens
        - Converts string user_id back to UUID

    Example:
        >>> from uuid import uuid4
        >>> user_id = uuid4()
        >>> token = create_access_token(user_id)
        >>> extracted_id = extract_user_id_from_token(token)
        >>> print(extracted_id == user_id)
        True
    """
    payload = verify_token(token)

    if payload is None:
        return None

    # Extract user_id from "sub" claim
    user_id_str = payload.get("sub")

    if user_id_str is None:
        return None

    try:
        # Convert string back to UUID
        return UUID(user_id_str)
    except (ValueError, AttributeError):
        # Invalid UUID format
        return None


# ============================================================================
# Token Validation Helpers
# ============================================================================

def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.

    Args:
        token: JWT token string

    Returns:
        bool: True if expired or invalid, False if still valid

    Example:
        >>> token = create_access_token(uuid4())
        >>> print(is_token_expired(token))
        False
    """
    payload = verify_token(token)

    if payload is None:
        return True

    exp = payload.get("exp")

    if exp is None:
        return True

    # Check if expiration time has passed
    return datetime.utcnow() > datetime.fromtimestamp(exp)
