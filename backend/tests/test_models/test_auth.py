"""Tests for auth Pydantic models - TDD approach.

These tests define the expected validation behavior of auth models.
"""

import pytest
from pydantic import ValidationError


class TestRegisterRequest:
    """Tests for RegisterRequest model validation."""

    def test_valid_register_request(self):
        """Test that valid data passes validation."""
        from app.models.auth import RegisterRequest

        data = RegisterRequest(
            name="John Doe",
            email="john@example.com",
            password="SecurePass123!",
            password_confirmation="SecurePass123!",
        )

        assert data.name == "John Doe"
        assert data.email == "john@example.com"
        assert data.password == "SecurePass123!"

    def test_password_min_8_chars(self):
        """Test that password must be at least 8 characters."""
        from app.models.auth import RegisterRequest

        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                name="John Doe",
                email="john@example.com",
                password="short",
                password_confirmation="short",
            )

        errors = exc_info.value.errors()
        assert any("8" in str(e) or "length" in str(e).lower() for e in errors)

    def test_email_format_validation(self):
        """Test that email must be valid format."""
        from app.models.auth import RegisterRequest

        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                name="John Doe",
                email="invalid-email",
                password="SecurePass123!",
                password_confirmation="SecurePass123!",
            )

        errors = exc_info.value.errors()
        assert any("email" in str(e).lower() for e in errors)

    def test_password_confirmation_must_match(self):
        """Test that password confirmation must match password."""
        from app.models.auth import RegisterRequest

        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                name="John Doe",
                email="john@example.com",
                password="SecurePass123!",
                password_confirmation="DifferentPass456!",
            )

        errors = exc_info.value.errors()
        assert any(
            "match" in str(e).lower() or "confirmation" in str(e).lower()
            for e in errors
        )

    def test_name_is_required(self):
        """Test that name is required."""
        from app.models.auth import RegisterRequest

        with pytest.raises(ValidationError):
            RegisterRequest(
                email="john@example.com",
                password="SecurePass123!",
                password_confirmation="SecurePass123!",
            )

    def test_name_is_sanitized(self):
        """Test that name is sanitized against injection."""
        from app.models.auth import RegisterRequest

        data = RegisterRequest(
            name="<script>alert('xss')</script>",
            email="john@example.com",
            password="SecurePass123!",
            password_confirmation="SecurePass123!",
        )

        # Should be sanitized - no HTML tags
        assert "<script>" not in data.name
        assert "</script>" not in data.name


class TestLoginRequest:
    """Tests for LoginRequest model validation."""

    def test_valid_login_request(self):
        """Test that valid data passes validation."""
        from app.models.auth import LoginRequest

        data = LoginRequest(
            email="john@example.com",
            password="SecurePass123!",
        )

        assert data.email == "john@example.com"
        assert data.password == "SecurePass123!"

    def test_email_is_required(self):
        """Test that email is required."""
        from app.models.auth import LoginRequest

        with pytest.raises(ValidationError):
            LoginRequest(password="SecurePass123!")

    def test_password_is_required(self):
        """Test that password is required."""
        from app.models.auth import LoginRequest

        with pytest.raises(ValidationError):
            LoginRequest(email="john@example.com")

    def test_email_format_validation(self):
        """Test that email must be valid format."""
        from app.models.auth import LoginRequest

        with pytest.raises(ValidationError):
            LoginRequest(
                email="invalid-email",
                password="SecurePass123!",
            )


class TestPasswordResetConfirm:
    """Tests for PasswordResetConfirm model validation."""

    def test_valid_password_reset_confirm(self):
        """Test that valid data passes validation."""
        from app.models.auth import PasswordResetConfirm

        data = PasswordResetConfirm(
            token="some-reset-token",
            new_password="NewSecurePass123!",
            new_password_confirmation="NewSecurePass123!",
        )

        assert data.token == "some-reset-token"
        assert data.new_password == "NewSecurePass123!"

    def test_password_confirmation_must_match(self):
        """Test that password confirmation must match."""
        from app.models.auth import PasswordResetConfirm

        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="some-reset-token",
                new_password="NewSecurePass123!",
                new_password_confirmation="DifferentPass456!",
            )

        errors = exc_info.value.errors()
        assert any(
            "match" in str(e).lower() or "confirmation" in str(e).lower()
            for e in errors
        )

    def test_new_password_min_8_chars(self):
        """Test that new password must be at least 8 characters."""
        from app.models.auth import PasswordResetConfirm

        with pytest.raises(ValidationError):
            PasswordResetConfirm(
                token="some-reset-token",
                new_password="short",
                new_password_confirmation="short",
            )


class TestPasswordResetRequest:
    """Tests for PasswordResetRequest model validation."""

    def test_valid_password_reset_request(self):
        """Test that valid data passes validation."""
        from app.models.auth import PasswordResetRequest

        data = PasswordResetRequest(email="john@example.com")
        assert data.email == "john@example.com"

    def test_email_format_validation(self):
        """Test that email must be valid format."""
        from app.models.auth import PasswordResetRequest

        with pytest.raises(ValidationError):
            PasswordResetRequest(email="invalid-email")


class TestUserResponse:
    """Tests for UserResponse model."""

    def test_user_response_fields(self):
        """Test that UserResponse has all required fields."""
        from datetime import datetime

        from app.models.auth import UserResponse

        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="John Doe",
            email="john@example.com",
            email_verified=True,
            created_at=datetime.now(),
        )

        assert user.id == "550e8400-e29b-41d4-a716-446655440000"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.email_verified is True


class TestLoginResponse:
    """Tests for LoginResponse model."""

    def test_login_response_fields(self):
        """Test that LoginResponse has all required fields."""
        from datetime import datetime

        from app.models.auth import LoginResponse, UserResponse

        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="John Doe",
            email="john@example.com",
            email_verified=True,
            created_at=datetime.now(),
        )

        response = LoginResponse(
            access_token="access.token.here",
            refresh_token="refresh.token.here",
            user=user,
        )

        assert response.access_token == "access.token.here"
        assert response.refresh_token == "refresh.token.here"
        assert response.user.email == "john@example.com"


class TestRefreshTokenRequest:
    """Tests for RefreshTokenRequest model."""

    def test_refresh_token_request(self):
        """Test that RefreshTokenRequest has refresh_token field."""
        from app.models.auth import RefreshTokenRequest

        data = RefreshTokenRequest(refresh_token="some.refresh.token")
        assert data.refresh_token == "some.refresh.token"

    def test_refresh_token_is_required(self):
        """Test that refresh_token is required."""
        from app.models.auth import RefreshTokenRequest

        with pytest.raises(ValidationError):
            RefreshTokenRequest()
