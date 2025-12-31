"""Tests for auth service - TDD approach.

These tests mock Supabase to test the auth service logic.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.auth import LoginRequest, RegisterRequest


class MockUser:
    """Mock Supabase user object."""

    def __init__(
        self,
        id: str = "550e8400-e29b-41d4-a716-446655440000",
        email: str = "test@example.com",
        email_confirmed_at: str | None = None,
        user_metadata: dict | None = None,
        created_at: str = "2025-01-01T00:00:00Z",
    ):
        self.id = id
        self.email = email
        self.email_confirmed_at = email_confirmed_at
        self.user_metadata = user_metadata or {}
        self.created_at = created_at


class MockSession:
    """Mock Supabase session object."""

    def __init__(
        self,
        access_token: str = "mock.access.token",
        refresh_token: str = "mock.refresh.token",
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token


class MockAuthResponse:
    """Mock Supabase auth response."""

    def __init__(self, user: MockUser | None = None, session: MockSession | None = None):
        self.user = user
        self.session = session


class TestRegister:
    """Tests for user registration."""

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_register_creates_user_in_supabase(self, mock_get_client, mock_get_admin):
        """Test that register calls Supabase sign_up."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        mock_user = MockUser(
            email="newuser@example.com",
            user_metadata={"name": "New User"},
        )
        mock_client.auth.sign_up.return_value = MockAuthResponse(user=mock_user)
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        data = RegisterRequest(
            name="New User",
            email="newuser@example.com",
            password="SecurePass123!",
            password_confirmation="SecurePass123!",
        )

        result = service.register(data)

        mock_client.auth.sign_up.assert_called_once()
        assert result.email == "newuser@example.com"

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_register_with_duplicate_email_returns_generic_error(self, mock_get_client, mock_get_admin):
        """Test that duplicate email returns generic error."""
        from app.services.auth_service import AuthService, AuthError

        mock_client = MagicMock()
        mock_client.auth.sign_up.side_effect = Exception("User already registered")
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        data = RegisterRequest(
            name="New User",
            email="existing@example.com",
            password="SecurePass123!",
            password_confirmation="SecurePass123!",
        )

        with pytest.raises(AuthError) as exc_info:
            service.register(data)

        # Error message should be generic, not revealing email existence
        assert "already registered" not in str(exc_info.value).lower()


class TestLogin:
    """Tests for user login."""

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_login_with_valid_credentials_returns_tokens(self, mock_get_client, mock_get_admin):
        """Test that valid login returns tokens."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        mock_user = MockUser(
            email="user@example.com",
            email_confirmed_at="2025-01-01T00:00:00Z",
            user_metadata={"name": "Test User"},
        )
        mock_session = MockSession()
        mock_client.auth.sign_in_with_password.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        data = LoginRequest(
            email="user@example.com",
            password="SecurePass123!",
        )

        result = service.login(data)

        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.user.email == "user@example.com"

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_login_with_invalid_credentials_returns_generic_error(self, mock_get_client, mock_get_admin):
        """Test that invalid credentials return generic error."""
        from app.services.auth_service import AuthService, AuthError

        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception(
            "Invalid login credentials"
        )
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        data = LoginRequest(
            email="user@example.com",
            password="WrongPassword!",
        )

        with pytest.raises(AuthError) as exc_info:
            service.login(data)

        # Error should be generic
        error_msg = str(exc_info.value).lower()
        assert "invalid" not in error_msg or "credentials" not in error_msg

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_login_with_unverified_email_raises_error(self, mock_get_client, mock_get_admin):
        """Test that unverified email raises appropriate error."""
        from app.services.auth_service import AuthService, EmailNotVerifiedError

        mock_client = MagicMock()
        mock_user = MockUser(
            email="unverified@example.com",
            email_confirmed_at=None,  # Not verified
            user_metadata={"name": "Unverified User"},
        )
        mock_session = MockSession()
        mock_client.auth.sign_in_with_password.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        data = LoginRequest(
            email="unverified@example.com",
            password="SecurePass123!",
        )

        with pytest.raises(EmailNotVerifiedError):
            service.login(data)


class TestRefreshToken:
    """Tests for token refresh."""

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_refresh_token_returns_new_access_token(self, mock_get_client, mock_get_admin):
        """Test that refresh token returns new access token."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        mock_user = MockUser(email="user@example.com")
        mock_session = MockSession(
            access_token="new.access.token",
            refresh_token="new.refresh.token",
        )
        mock_client.auth.refresh_session.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        result = service.refresh_token("old.refresh.token")

        assert result.access_token == "new.access.token"


class TestPasswordReset:
    """Tests for password reset."""

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_password_reset_sends_email(self, mock_get_client, mock_get_admin):
        """Test that password reset triggers email send."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        mock_client.auth.reset_password_for_email.return_value = None
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        # Should not raise any exception
        service.request_password_reset("user@example.com")

        mock_client.auth.reset_password_for_email.assert_called_once()

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_password_reset_for_nonexistent_email_returns_success(self, mock_get_client, mock_get_admin):
        """Test that password reset for unknown email doesn't reveal info."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        # Even for non-existent emails, Supabase returns success
        mock_client.auth.reset_password_for_email.return_value = None
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        # Should not raise any exception (prevents email enumeration)
        service.request_password_reset("nonexistent@example.com")

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_password_reset_confirm_updates_password(self, mock_get_client, mock_get_admin):
        """Test that password reset confirm updates password."""
        from app.services.auth_service import AuthService

        mock_admin = MagicMock()
        mock_admin.auth.admin.update_user_by_id.return_value = MagicMock()
        mock_get_client.return_value = MagicMock()
        mock_get_admin.return_value = mock_admin

        service = AuthService()
        # Should not raise any exception
        service.confirm_password_reset(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            new_password="NewSecurePass123!",
        )


class TestLogout:
    """Tests for logout."""

    @patch("app.services.auth_service.get_supabase_admin")
    @patch("app.services.auth_service.get_supabase_client")
    def test_logout_calls_signout(self, mock_get_client, mock_get_admin):
        """Test that logout calls Supabase sign_out."""
        from app.services.auth_service import AuthService

        mock_client = MagicMock()
        mock_client.auth.sign_out.return_value = None
        mock_get_client.return_value = mock_client
        mock_get_admin.return_value = MagicMock()

        service = AuthService()
        service.logout()

        mock_client.auth.sign_out.assert_called_once()
