"""Tests for security utilities - TDD approach.

These tests define the expected behavior of the security module.
They should be written BEFORE the implementation.
"""

from datetime import timedelta

import pytest


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_hash_password_creates_unique_hashes(self):
        """Test that hashing the same password twice creates different hashes."""
        from app.utils.security import hash_password

        password = "MySecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to unique salt
        assert hash1 != hash2
        # Both should be valid bcrypt hashes (start with $2b$)
        assert hash1.startswith("$2b$")
        assert hash2.startswith("$2b$")

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        from app.utils.security import hash_password

        password = "TestPassword123"
        result = hash_password(password)

        assert isinstance(result, str)
        assert len(result) == 60  # bcrypt hash length

    def test_verify_password_with_correct_password(self):
        """Test that verify_password returns True for correct password."""
        from app.utils.security import hash_password, verify_password

        password = "CorrectPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        from app.utils.security import hash_password, verify_password

        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_empty_password(self):
        """Test that verify_password handles empty password gracefully."""
        from app.utils.security import hash_password, verify_password

        password = "SomePassword123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Tests for JWT token functionality."""

    def test_create_access_token_contains_user_id(self):
        """Test that access token contains the user_id in sub claim."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == user_id

    def test_create_access_token_contains_expiration(self):
        """Test that access token contains exp claim."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert "exp" in payload
        assert "iat" in payload
        # exp should be in the future
        assert payload["exp"] > payload["iat"]

    def test_create_access_token_with_custom_expiry(self):
        """Test that access token respects custom expiry time."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id, expires_delta=timedelta(minutes=5))
        payload = decode_token(token)

        # Should expire in approximately 5 minutes
        time_diff = payload["exp"] - payload["iat"]
        assert 290 <= time_diff <= 310  # Allow small variance (4:50 - 5:10)

    def test_create_refresh_token_contains_user_id(self):
        """Test that refresh token contains the user_id."""
        from app.utils.security import create_refresh_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == user_id

    def test_create_refresh_token_has_longer_expiry(self):
        """Test that refresh token has longer expiry than access token."""
        from app.utils.security import (
            create_access_token,
            create_refresh_token,
            decode_token,
        )

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        access_expiry = access_payload["exp"] - access_payload["iat"]
        refresh_expiry = refresh_payload["exp"] - refresh_payload["iat"]

        # Refresh token should have much longer expiry
        assert refresh_expiry > access_expiry

    def test_decode_token_with_valid_token(self):
        """Test that decode_token works with valid token."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id

    def test_decode_token_with_expired_token(self):
        """Test that decode_token raises exception for expired token."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        # Create token that expires immediately
        token = create_access_token(user_id, expires_delta=timedelta(seconds=-1))

        with pytest.raises(Exception) as exc_info:
            decode_token(token)

        # Should raise an exception related to token expiration
        assert (
            "expired" in str(exc_info.value).lower()
            or "exp" in str(exc_info.value).lower()
        )

    def test_decode_token_with_invalid_token(self):
        """Test that decode_token raises exception for invalid token."""
        from app.utils.security import decode_token

        invalid_token = "this.is.not.a.valid.jwt.token"

        with pytest.raises(Exception):
            decode_token(invalid_token)

    def test_decode_token_with_tampered_token(self):
        """Test that decode_token raises exception for tampered token."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id)

        # Tamper with the token by changing a character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(Exception):
            decode_token(tampered_token)


class TestTokenTypes:
    """Tests for token type differentiation."""

    def test_access_token_has_access_type(self):
        """Test that access token has type 'access'."""
        from app.utils.security import create_access_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload.get("type") == "access"

    def test_refresh_token_has_refresh_type(self):
        """Test that refresh token has type 'refresh'."""
        from app.utils.security import create_refresh_token, decode_token

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload.get("type") == "refresh"
