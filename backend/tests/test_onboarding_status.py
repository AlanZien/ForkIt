"""Tests for onboarding status endpoints.

Tests for Task Group 1: Backend Database & API for Onboarding Status
- Test GET /api/profile/onboarding-status returns false for new users
- Test GET /api/profile/onboarding-status returns true after completion
- Test PUT /api/profile/onboarding-completed sets flag to true
- Test endpoints require authentication (401 without token)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.auth import UserResponse
from app.routes.auth import get_current_user
from app.routes.profile import get_preferences_service
from app.models.preferences import OnboardingStatusResponse


# Create mock authenticated user
def get_mock_auth_user():
    """Return mock authenticated user."""
    return UserResponse(
        id="test-user-id-123",
        name="Test User",
        email="test@example.com",
        email_verified=True,
        created_at=datetime.now(timezone.utc),
    )


class TestOnboardingStatusEndpoints:
    """Test onboarding status API endpoints."""

    def test_get_onboarding_status_returns_false_for_new_users(self):
        """Test GET /api/profile/onboarding-status returns false for new users.

        Given: Authenticated user with no onboarding record
        When: GET /api/profile/onboarding-status
        Then: Returns { onboarding_completed: false }
        """
        # Create mock service
        mock_service = MagicMock()
        mock_service.get_onboarding_status.return_value = OnboardingStatusResponse(
            onboarding_completed=False
        )

        # Override dependencies
        app.dependency_overrides[get_current_user] = get_mock_auth_user
        app.dependency_overrides[get_preferences_service] = lambda: mock_service

        try:
            client = TestClient(app)
            response = client.get(
                "/api/profile/onboarding-status",
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            assert response.json() == {"onboarding_completed": False}
            mock_service.get_onboarding_status.assert_called_once_with("test-user-id-123")
        finally:
            app.dependency_overrides.clear()

    def test_get_onboarding_status_returns_true_after_completion(self):
        """Test GET /api/profile/onboarding-status returns true after completion.

        Given: Authenticated user with onboarding_completed=true in database
        When: GET /api/profile/onboarding-status
        Then: Returns { onboarding_completed: true }
        """
        # Create mock service
        mock_service = MagicMock()
        mock_service.get_onboarding_status.return_value = OnboardingStatusResponse(
            onboarding_completed=True
        )

        # Override dependencies
        app.dependency_overrides[get_current_user] = get_mock_auth_user
        app.dependency_overrides[get_preferences_service] = lambda: mock_service

        try:
            client = TestClient(app)
            response = client.get(
                "/api/profile/onboarding-status",
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            assert response.json() == {"onboarding_completed": True}
        finally:
            app.dependency_overrides.clear()

    def test_put_onboarding_completed_sets_flag_to_true(self):
        """Test PUT /api/profile/onboarding-completed sets flag to true.

        Given: Authenticated user
        When: PUT /api/profile/onboarding-completed
        Then: Upserts onboarding_completed=true and returns { onboarding_completed: true }
        """
        # Create mock service
        mock_service = MagicMock()
        mock_service.complete_onboarding.return_value = OnboardingStatusResponse(
            onboarding_completed=True
        )

        # Override dependencies
        app.dependency_overrides[get_current_user] = get_mock_auth_user
        app.dependency_overrides[get_preferences_service] = lambda: mock_service

        try:
            client = TestClient(app)
            response = client.put(
                "/api/profile/onboarding-completed",
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            assert response.json() == {"onboarding_completed": True}

            # Verify service method was called
            mock_service.complete_onboarding.assert_called_once_with("test-user-id-123")
        finally:
            app.dependency_overrides.clear()

    def test_get_onboarding_status_requires_authentication(self):
        """Test GET /api/profile/onboarding-status requires authentication.

        Given: No authentication token
        When: GET /api/profile/onboarding-status
        Then: Returns 401 Unauthorized
        """
        # Clear any overrides to test actual authentication
        app.dependency_overrides.clear()

        client = TestClient(app)
        response = client.get("/api/profile/onboarding-status")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_put_onboarding_completed_requires_authentication(self):
        """Test PUT /api/profile/onboarding-completed requires authentication.

        Given: No authentication token
        When: PUT /api/profile/onboarding-completed
        Then: Returns 401 Unauthorized
        """
        # Clear any overrides to test actual authentication
        app.dependency_overrides.clear()

        client = TestClient(app)
        response = client.put("/api/profile/onboarding-completed")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
