"""Authentication service.

Handles all authentication operations with Supabase Auth.
"""

import logging
from datetime import datetime

from app.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.supabase import get_supabase_admin, get_supabase_client

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Base authentication error with generic message."""

    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class EmailNotVerifiedError(AuthError):
    """Raised when user's email is not verified."""

    def __init__(self):
        super().__init__("Email verification required")


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        """Initialize auth service."""
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin()

    def register(self, data: RegisterRequest) -> UserResponse:
        """Register a new user.

        Args:
            data: Registration request with user details.

        Returns:
            UserResponse with created user info.

        Raises:
            AuthError: If registration fails.
        """
        try:
            response = self.client.auth.sign_up(
                {
                    "email": data.email,
                    "password": data.password,
                    "options": {
                        "data": {
                            "name": data.name,
                        }
                    },
                }
            )

            if not response.user:
                raise AuthError("Registration failed")

            # Handle created_at - may be datetime or string
            created_at = response.user.created_at
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            return UserResponse(
                id=response.user.id,
                name=response.user.user_metadata.get("name"),
                email=response.user.email,
                email_verified=response.user.email_confirmed_at is not None,
                created_at=created_at,
            )

        except AuthError:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise AuthError("Registration failed. Please try again.")

    def login(self, data: LoginRequest) -> LoginResponse:
        """Log in a user.

        Args:
            data: Login request with credentials.

        Returns:
            LoginResponse with tokens and user info.

        Raises:
            AuthError: If login fails.
            EmailNotVerifiedError: If email is not verified.
        """
        try:
            response = self.client.auth.sign_in_with_password(
                {
                    "email": data.email,
                    "password": data.password,
                }
            )

            if not response.user or not response.session:
                raise AuthError("Login failed")

            # Check email verification
            if not response.user.email_confirmed_at:
                raise EmailNotVerifiedError()

            # Handle created_at - may be datetime or string
            created_at = response.user.created_at
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            user = UserResponse(
                id=response.user.id,
                name=response.user.user_metadata.get("name"),
                email=response.user.email,
                email_verified=True,
                created_at=created_at,
            )

            return LoginResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                user=user,
            )

        except EmailNotVerifiedError:
            raise
        except AuthError:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise AuthError("Email or password incorrect")

    def refresh_token(self, refresh_token: str) -> LoginResponse:
        """Refresh access token.

        Args:
            refresh_token: Current refresh token.

        Returns:
            LoginResponse with new tokens.

        Raises:
            AuthError: If refresh fails.
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)

            if not response.user or not response.session:
                raise AuthError("Token refresh failed")

            # Handle created_at - may be datetime or string
            created_at = response.user.created_at
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            user = UserResponse(
                id=response.user.id,
                name=response.user.user_metadata.get("name"),
                email=response.user.email,
                email_verified=response.user.email_confirmed_at is not None,
                created_at=created_at,
            )

            return LoginResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                user=user,
            )

        except AuthError:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthError("Session expired. Please log in again.")

    def request_password_reset(self, email: str) -> None:
        """Request password reset email.

        Always succeeds to prevent email enumeration.

        Args:
            email: User's email address.
        """
        try:
            self.client.auth.reset_password_for_email(email)
        except Exception as e:
            # Log but don't expose error to prevent enumeration
            logger.warning(f"Password reset request error: {e}")
            # Always succeed silently

    def confirm_password_reset(self, user_id: str, new_password: str) -> None:
        """Confirm password reset with new password.

        Args:
            user_id: User's ID.
            new_password: New password to set.

        Raises:
            AuthError: If reset fails.
        """
        try:
            self.admin_client.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password},
            )
        except Exception as e:
            logger.error(f"Password reset confirm error: {e}")
            raise AuthError("Password reset failed. Please try again.")

    def logout(self) -> None:
        """Log out current user."""
        try:
            self.client.auth.sign_out()
        except Exception as e:
            logger.warning(f"Logout error: {e}")
            # Logout errors are non-critical

    def get_user(self, access_token: str) -> UserResponse | None:
        """Get user info from access token.

        Args:
            access_token: JWT access token.

        Returns:
            UserResponse if valid, None otherwise.
        """
        try:
            response = self.client.auth.get_user(access_token)

            if not response.user:
                return None

            # Handle created_at - may be datetime or string
            created_at = response.user.created_at
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            return UserResponse(
                id=response.user.id,
                name=response.user.user_metadata.get("name"),
                email=response.user.email,
                email_verified=response.user.email_confirmed_at is not None,
                created_at=created_at,
            )

        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None

    def resend_verification_email(self, email: str) -> None:
        """Resend verification email.

        Args:
            email: User's email address.
        """
        try:
            self.client.auth.resend(
                {
                    "type": "signup",
                    "email": email,
                }
            )
        except Exception as e:
            logger.warning(f"Resend verification error: {e}")
            # Don't expose errors to prevent enumeration
