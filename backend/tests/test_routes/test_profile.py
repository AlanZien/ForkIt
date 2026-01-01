"""Tests for profile API endpoints - TDD approach.

These tests use FastAPI TestClient to test the profile/preferences endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models.preferences import (
    AllergyType,
    DietaryType,
    UserPreferencesResponse,
)


# Create mock classes for authentication
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


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user."""
    return MockUser(id="550e8400-e29b-41d4-a716-446655440000", email="test@example.com")


@pytest.fixture
def mock_preferences_response():
    """Create a mock preferences response."""
    return UserPreferencesResponse(
        dietary_preferences=[DietaryType.VEGETARIAN],
        allergies=[AllergyType.GLUTEN, AllergyType.LACTOSE],
        excluded_ingredients=["cilantro", "olives"],
        preferred_ingredients=["tomato", "basil"],
        portions_count=4,
        warning=None,
    )


def create_table_mock_for_get(mock_client, mock_auth_user):
    """Setup table mock for GET preferences."""
    # Mock preferences service responses
    mock_dietary_response = MagicMock()
    mock_dietary_response.data = [{"dietary_type": "vegetarian"}]

    mock_allergy_response = MagicMock()
    mock_allergy_response.data = [{"allergy_type": "gluten"}, {"allergy_type": "lactose"}]

    mock_excluded_response = MagicMock()
    mock_excluded_response.data = [{"ingredient_name": "cilantro"}]

    mock_preferred_response = MagicMock()
    mock_preferred_response.data = [{"ingredient_name": "tomato"}]

    mock_settings_response = MagicMock()
    mock_settings_response.data = [{"portions_count": 4}]

    def table_side_effect(table_name):
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()

        if table_name == "user_dietary_preferences":
            mock_eq.execute.return_value = mock_dietary_response
        elif table_name == "user_allergies":
            mock_eq.execute.return_value = mock_allergy_response
        elif table_name == "user_excluded_ingredients":
            mock_eq.execute.return_value = mock_excluded_response
        elif table_name == "user_preferred_ingredients":
            mock_eq.execute.return_value = mock_preferred_response
        elif table_name == "user_settings":
            mock_eq.execute.return_value = mock_settings_response

        mock_select.eq.return_value = mock_eq
        mock_table.select.return_value = mock_select
        return mock_table

    mock_client.table.side_effect = table_side_effect


def create_table_mock_for_update(mock_client):
    """Setup table mock for PUT preferences (update operations)."""
    mock_delete_chain = MagicMock()
    mock_delete_chain.eq.return_value.execute.return_value = MagicMock()

    mock_insert_chain = MagicMock()
    mock_insert_chain.execute.return_value = MagicMock()

    mock_upsert_chain = MagicMock()
    mock_upsert_chain.execute.return_value = MagicMock()

    def table_side_effect(table_name):
        mock_table = MagicMock()
        mock_table.delete.return_value = mock_delete_chain
        mock_table.insert.return_value = mock_insert_chain
        mock_table.upsert.return_value = mock_upsert_chain
        return mock_table

    mock_client.table.side_effect = table_side_effect


class TestGetPreferencesEndpoint:
    """Tests for GET /api/profile/preferences."""

    def test_get_preferences_returns_200_with_preferences(self, mock_supabase_client, mock_auth_user):
        """Test GET /api/profile/preferences returns 200 with user preferences."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        # Setup table mocking for preferences
        create_table_mock_for_get(mock_client, mock_auth_user)

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                # Force reimport to use patched modules
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "dietary_preferences" in data
        assert "allergies" in data
        assert "excluded_ingredients" in data
        assert "preferred_ingredients" in data
        assert "portions_count" in data
        assert data["dietary_preferences"] == ["vegetarian"]
        assert data["allergies"] == ["gluten", "lactose"]

    def test_get_preferences_returns_401_without_auth(self, mock_supabase_client):
        """Test GET /api/profile/preferences returns 401 without authentication."""
        mock_client = mock_supabase_client

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get("/api/profile/preferences")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()

    def test_get_preferences_returns_401_with_invalid_token(self, mock_supabase_client):
        """Test GET /api/profile/preferences returns 401 with invalid token."""
        mock_client = mock_supabase_client

        # Mock auth to return None (invalid token)
        mock_client.auth.get_user.return_value = MagicMock(user=None)

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer invalid.token"},
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdatePreferencesEndpoint:
    """Tests for PUT /api/profile/preferences."""

    def test_put_preferences_updates_correctly(self, mock_supabase_client, mock_auth_user):
        """Test PUT /api/profile/preferences updates preferences correctly."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        # Setup table mocking for update operations
        create_table_mock_for_update(mock_client)

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                    json={
                        "dietary_preferences": ["vegetarian", "halal"],
                        "allergies": ["gluten"],
                        "excluded_ingredients": ["cilantro", "olives"],
                        "preferred_ingredients": ["tomato"],
                        "portions_count": 4,
                    },
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["dietary_preferences"] == ["vegetarian", "halal"]
        assert data["allergies"] == ["gluten"]
        assert data["excluded_ingredients"] == ["cilantro", "olives"]
        assert data["preferred_ingredients"] == ["tomato"]
        assert data["portions_count"] == 4

    def test_put_preferences_returns_422_on_incompatibilities(self, mock_supabase_client, mock_auth_user):
        """Test PUT /api/profile/preferences returns 422 when dietary incompatibilities detected."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                # Vegan + Pescetarian is incompatible
                response = client.put(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                    json={
                        "dietary_preferences": ["vegan", "pescetarian"],
                        "allergies": [],
                        "excluded_ingredients": [],
                        "preferred_ingredients": [],
                        "portions_count": 2,
                    },
                )

        # Pydantic validation should catch this
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_put_preferences_returns_422_on_too_many_ingredients(self, mock_supabase_client, mock_auth_user):
        """Test PUT /api/profile/preferences returns 422 when more than 30 ingredients."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        # Create list of 31 ingredients
        too_many_ingredients = [f"ingredient_{i}" for i in range(31)]

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                    json={
                        "dietary_preferences": [],
                        "allergies": [],
                        "excluded_ingredients": too_many_ingredients,
                        "preferred_ingredients": [],
                        "portions_count": 2,
                    },
                )

        # Pydantic validation should catch the 30 ingredient limit
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_put_preferences_returns_401_without_auth(self, mock_supabase_client):
        """Test PUT /api/profile/preferences returns 401 without authentication."""
        mock_client = mock_supabase_client

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/profile/preferences",
                    json={
                        "dietary_preferences": ["vegetarian"],
                        "allergies": [],
                        "excluded_ingredients": [],
                        "preferred_ingredients": [],
                        "portions_count": 2,
                    },
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_preferences_returns_warning_for_halal_kosher(self, mock_supabase_client, mock_auth_user):
        """Test PUT /api/profile/preferences returns warning when halal + kosher selected."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        # Setup table mocking for update operations
        create_table_mock_for_update(mock_client)

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                    json={
                        "dietary_preferences": ["halal", "kosher"],
                        "allergies": [],
                        "excluded_ingredients": [],
                        "preferred_ingredients": [],
                        "portions_count": 2,
                    },
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["warning"] is not None
        assert "coherence" in data["warning"].lower() or "combination" in data["warning"].lower()

    def test_put_preferences_normalizes_ingredients(self, mock_supabase_client, mock_auth_user):
        """Test PUT /api/profile/preferences normalizes ingredient names (lowercase, trim)."""
        mock_client = mock_supabase_client

        # Mock auth user response
        mock_user_response = MagicMock()
        mock_user_response.user = mock_auth_user
        mock_client.auth.get_user.return_value = mock_user_response

        # Setup table mocking for update operations
        create_table_mock_for_update(mock_client)

        with patch("app.services.supabase.get_supabase_client", return_value=mock_client):
            with patch("app.services.supabase.get_supabase_admin", return_value=mock_client):
                import importlib
                import app.services.auth_service
                import app.services.preferences_service
                import app.main
                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.preferences_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/profile/preferences",
                    headers={"Authorization": "Bearer mock.access.token"},
                    json={
                        "dietary_preferences": [],
                        "allergies": [],
                        "excluded_ingredients": ["  CILANTRO  ", "Olives  "],
                        "preferred_ingredients": ["  TOMATO", "basil  "],
                        "portions_count": 2,
                    },
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Ingredients should be normalized to lowercase and trimmed
        assert data["excluded_ingredients"] == ["cilantro", "olives"]
        assert data["preferred_ingredients"] == ["tomato", "basil"]
