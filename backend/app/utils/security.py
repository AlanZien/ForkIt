"""Security utilities for authentication.

Provides password hashing and JWT token management.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string (60 characters, bcrypt format).
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Bcrypt hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    if not plain_password:
        return False
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        user_id: User ID to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT access token string.
    """
    now = datetime.now(UTC)

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_expiry_minutes)

    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token.

    Args:
        user_id: User ID to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(UTC)

    if expires_delta is None:
        expires_delta = timedelta(days=settings.jwt_refresh_expiry_days)

    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, str | int]:
    """Decode and verify a JWT token.

    Args:
        token: JWT token string to decode.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.ExpiredSignatureError: If token has expired.
        jwt.InvalidTokenError: If token is invalid.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
