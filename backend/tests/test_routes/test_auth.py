"""Tests for auth API endpoints - TDD approach.

These tests use FastAPI TestClient to test the auth endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient


# Create mock classes before importing app
class MockUser:
    """Mock user object."""

    def __init__(
        self,
        id: str = "550e8400-e29b-41d4-a716-446655440000",
        email: str = "test@example.com",
        email_confirmed_at: str | None = "2025-01-01T00:00:00Z",
        user_metadata: dict | None = None,
        created_at: str = "2025-01-01T00:00:00Z",
    ):
        self.id = id
        self.email = email
        self.email_confirmed_at = email_confirmed_at
        self.user_metadata = user_metadata or {"name": "Test User"}
        self.created_at = created_at


class MockSession:
    """Mock session object."""

    def __init__(
        self,
        access_token: str = "mock.access.token",
        refresh_token: str = "mock.refresh.token",
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token


class MockAuthResponse:
    """Mock auth response."""

    def __init__(self, user: MockUser | None = None, session: MockSession | None = None):
        self.user = user
        self.session = session


@pytest.fixture
def mock_supabase():
    """Create mock Supabase client."""
    mock_client = MagicMock()
    mock_admin = MagicMock()
    return mock_client, mock_admin


@pytest.fixture
def client(mock_supabase):
    """Create test client with mocked dependencies."""
    mock_client, mock_admin = mock_supabase

    with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
        with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
            from app.main import app

            yield TestClient(app)


class TestRegisterEndpoint:
    """Tests for POST /api/auth/register."""

    def test_register_returns_201_on_success(self, mock_supabase):
        """Test successful registration returns 201."""
        mock_client, mock_admin = mock_supabase
        mock_user = MockUser(email="newuser@example.com")
        mock_client.auth.sign_up.return_value = MockAuthResponse(user=mock_user)

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/register",
                    json={
                        "name": "New User",
                        "email": "newuser@example.com",
                        "password": "SecurePass123!",
                        "password_confirmation": "SecurePass123!",
                    },
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"

    def test_register_returns_400_on_validation_error(self, mock_supabase):
        """Test registration with invalid data returns 400."""
        mock_client, mock_admin = mock_supabase

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/register",
                    json={
                        "name": "New User",
                        "email": "invalid-email",
                        "password": "short",
                        "password_confirmation": "short",
                    },
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_returns_400_on_password_mismatch(self, mock_supabase):
        """Test registration with mismatched passwords returns 422."""
        mock_client, mock_admin = mock_supabase

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/register",
                    json={
                        "name": "New User",
                        "email": "newuser@example.com",
                        "password": "SecurePass123!",
                        "password_confirmation": "DifferentPass123!",
                    },
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLoginEndpoint:
    """Tests for POST /api/auth/login."""

    def test_login_returns_200_with_tokens(self, mock_supabase):
        """Test successful login returns 200 with tokens."""
        mock_client, mock_admin = mock_supabase
        mock_user = MockUser(email="user@example.com")
        mock_session = MockSession()
        mock_client.auth.sign_in_with_password.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/login",
                    json={
                        "email": "user@example.com",
                        "password": "SecurePass123!",
                    },
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "user@example.com"

    def test_login_returns_401_on_invalid_credentials(self, mock_supabase):
        """Test login with invalid credentials returns 401."""
        mock_client, mock_admin = mock_supabase
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/login",
                    json={
                        "email": "user@example.com",
                        "password": "WrongPassword!",
                    },
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_returns_403_on_unverified_email(self, mock_supabase):
        """Test login with unverified email returns 403."""
        mock_client, mock_admin = mock_supabase
        mock_user = MockUser(email="unverified@example.com", email_confirmed_at=None)
        mock_session = MockSession()
        mock_client.auth.sign_in_with_password.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/login",
                    json={
                        "email": "unverified@example.com",
                        "password": "SecurePass123!",
                    },
                )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "verification" in response.json()["detail"].lower()


class TestRefreshEndpoint:
    """Tests for POST /api/auth/refresh."""

    def test_refresh_returns_new_access_token(self, mock_supabase):
        """Test refresh returns new access token."""
        mock_client, mock_admin = mock_supabase
        mock_user = MockUser()
        mock_session = MockSession(access_token="new.access.token")
        mock_client.auth.refresh_session.return_value = MockAuthResponse(
            user=mock_user, session=mock_session
        )

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/refresh",
                    json={"refresh_token": "old.refresh.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "new.access.token"


class TestLogoutEndpoint:
    """Tests for POST /api/auth/logout."""

    def test_logout_clears_session(self, mock_supabase):
        """Test logout clears session."""
        mock_client, mock_admin = mock_supabase
        mock_client.auth.sign_out.return_value = None

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post("/api/auth/logout")

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestPasswordResetEndpoint:
    """Tests for password reset endpoints."""

    def test_password_reset_request_sends_email(self, mock_supabase):
        """Test password reset request triggers email."""
        mock_client, mock_admin = mock_supabase
        mock_client.auth.reset_password_for_email.return_value = None

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/password-reset",
                    json={"email": "user@example.com"},
                )

        assert response.status_code == status.HTTP_200_OK
        mock_client.auth.reset_password_for_email.assert_called_once()

    def test_password_reset_for_nonexistent_email_returns_success(self, mock_supabase):
        """Test password reset for unknown email returns success (prevents enumeration)."""
        mock_client, mock_admin = mock_supabase
        mock_client.auth.reset_password_for_email.return_value = None

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/password-reset",
                    json={"email": "nonexistent@example.com"},
                )

        # Should always return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK


class TestMeEndpoint:
    """Tests for GET /api/auth/me."""

    def test_me_returns_current_user(self, mock_supabase):
        """Test /me returns current user info."""
        mock_client, mock_admin = mock_supabase
        mock_user = MockUser(email="user@example.com")
        mock_response = MagicMock()
        mock_response.user = mock_user
        mock_client.auth.get_user.return_value = mock_response

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/auth/me",
                    headers={"Authorization": "Bearer mock.access.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user@example.com"

    def test_me_returns_401_without_token(self, mock_supabase):
        """Test /me returns 401 without auth header."""
        mock_client, mock_admin = mock_supabase

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.get("/api/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestResendVerificationEndpoint:
    """Tests for POST /api/auth/resend-verification."""

    def test_resend_verification_sends_email(self, mock_supabase):
        """Test resend verification triggers email."""
        mock_client, mock_admin = mock_supabase
        mock_client.auth.resend.return_value = None

        with patch("app.services.auth_service.get_supabase_client", return_value=mock_client):
            with patch("app.services.auth_service.get_supabase_admin", return_value=mock_admin):
                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/auth/resend-verification",
                    json={"email": "user@example.com"},
                )

        assert response.status_code == status.HTTP_200_OK
