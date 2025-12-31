"""Authentication Pydantic models.

Defines request/response schemas for authentication endpoints.
"""

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, model_validator


def sanitize_string(value: str) -> str:
    """Remove potentially dangerous characters from input.

    Removes HTML tags and common injection patterns.
    """
    # Remove HTML tags
    value = re.sub(r"<[^>]*>", "", value)
    # Remove potential SQL injection characters (but keep common punctuation)
    value = re.sub(r"[;'\"\-\-]", "", value)
    return value.strip()


class RegisterRequest(BaseModel):
    """User registration request."""

    name: str
    email: EmailStr
    password: str
    password_confirmation: str

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name to prevent injection attacks."""
        return sanitize_string(v)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "RegisterRequest":
        """Validate that password confirmation matches password."""
        if self.password != self.password_confirmation:
            raise ValueError("Password confirmation does not match password")
        return self


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    token: str
    new_password: str
    new_password_confirmation: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "PasswordResetConfirm":
        """Validate that password confirmation matches password."""
        if self.new_password != self.new_password_confirmation:
            raise ValueError("Password confirmation does not match password")
        return self


class UserResponse(BaseModel):
    """User response model."""

    id: str
    name: str | None
    email: str
    email_verified: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """Login response with tokens and user info."""

    access_token: str
    refresh_token: str
    user: UserResponse
