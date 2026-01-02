"""Tests for favorites API routes."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class MockUser:
    """Mock user object."""

    def __init__(
        self,
        id: str = "550e8400-e29b-41d4-a716-446655440000",
        email: str = "test@example.com",
    ):
        self.id = id
        self.email = email
        self.email_confirmed_at = "2025-01-01T00:00:00Z"
        self.user_metadata = {"name": "Test User"}
        self.created_at = "2025-01-01T00:00:00Z"


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client."""
    return MagicMock()


@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user."""
    return MockUser()


def setup_auth_mock(mock_client, mock_user):
    """Setup auth mock to return the mock user."""
    mock_user_response = MagicMock()
    mock_user_response.user = mock_user
    mock_client.auth.get_user.return_value = mock_user_response


class TestGetFavorites:
    """Tests for GET /api/favorites."""

    def test_get_favorites_returns_empty_list(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET favorites returns empty list for new user."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.select.return_value.eq.return_value.order.return_value
        chain.execute.return_value = MagicMock(data=[])

        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/favorites",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["favorites"] == []
        assert data["count"] == 0

    def test_get_favorites_returns_user_favorites(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET favorites returns list of favorites."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        favorites_data = [
            {
                "id": "fav-1",
                "recipe_id": "52772",
                "recipe_name": "Teriyaki Chicken",
                "recipe_thumbnail": "https://example.com/img.jpg",
                "created_at": datetime.now().isoformat(),
            },
        ]

        mock_query = MagicMock()
        chain = mock_query.select.return_value.eq.return_value.order.return_value
        chain.execute.return_value = MagicMock(data=favorites_data)

        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/favorites",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["favorites"][0]["recipe_id"] == "52772"


class TestAddFavorite:
    """Tests for POST /api/favorites."""

    def test_add_favorite_creates_new(self, mock_supabase_client, mock_auth_user):
        """Test adding a new favorite."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        new_favorite = {
            "id": "fav-new",
            "recipe_id": "52772",
            "recipe_name": "Teriyaki Chicken",
            "recipe_thumbnail": "https://example.com/img.jpg",
            "created_at": datetime.now().isoformat(),
        }

        # Setup mock for check existing (empty) then insert
        call_count = [0]

        def table_side_effect(table_name):
            mock_query = MagicMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: check existing
                chain = mock_query.select.return_value.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[])
            else:
                # Second call: insert
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=[new_favorite]
                )

            return mock_query

        mock_supabase_client.table.side_effect = table_side_effect

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/favorites",
                    json={
                        "recipe_id": "52772",
                        "recipe_name": "Teriyaki Chicken",
                        "recipe_thumbnail": "https://example.com/img.jpg",
                    },
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["recipe_id"] == "52772"


class TestRemoveFavorite:
    """Tests for DELETE /api/favorites/{recipe_id}."""

    def test_remove_favorite_success(self, mock_supabase_client, mock_auth_user):
        """Test removing a favorite."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.delete.return_value.eq.return_value.eq.return_value
        chain.execute.return_value = MagicMock(data=[])

        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.delete(
                    "/api/favorites/52772",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCheckFavorite:
    """Tests for GET /api/favorites/{recipe_id}."""

    def test_check_favorite_true(self, mock_supabase_client, mock_auth_user):
        """Test checking favorite returns true when exists."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.select.return_value.eq.return_value.eq.return_value
        chain.execute.return_value = MagicMock(data=[{"id": "fav-1"}])

        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/favorites/52772",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_favorite"] is True

    def test_check_favorite_false(self, mock_supabase_client, mock_auth_user):
        """Test checking favorite returns false when not exists."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.select.return_value.eq.return_value.eq.return_value
        chain.execute.return_value = MagicMock(data=[])

        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                import importlib

                import app.main
                import app.services.auth_service
                import app.services.favorites_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.favorites_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/favorites/52772",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_favorite"] is False
