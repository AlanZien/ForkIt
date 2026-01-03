"""Tests for shopping list API routes."""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, AsyncMock

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


def get_current_monday() -> date:
    """Get the Monday of the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


class TestGetShoppingList:
    """Tests for GET /api/shopping-list."""

    def test_get_shopping_list_returns_empty_for_new_user(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET shopping list returns empty for user with no items."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.select.return_value
        chain = chain.eq.return_value.eq.return_value.order.return_value
        chain = chain.order.return_value
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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.get(
                    f"/api/shopping-list?week_start={week_start}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["categories"] == []
        assert data["total_items"] == 0

    def test_get_shopping_list_returns_401_without_auth(self, mock_supabase_client):
        """Test GET shopping list returns 401 without authentication."""
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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.get(f"/api/shopping-list?week_start={week_start}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_shopping_list_returns_400_for_invalid_week_start(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET shopping list returns 400 when week_start is not a Monday."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        mock_supabase_client.table.return_value = MagicMock()

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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                tuesday = get_current_monday() + timedelta(days=1)
                response = client.get(
                    f"/api/shopping-list?week_start={tuesday.isoformat()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Monday" in response.json()["detail"]


class TestToggleItemCheck:
    """Tests for PUT /api/shopping-list/items/{id}/check."""

    def test_toggle_item_returns_200_with_updated_item(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test toggling an item returns 200 with updated state."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        item_id = "item-123"
        now = datetime.now(timezone.utc).isoformat()
        existing_item = {
            "id": item_id,
            "user_id": mock_auth_user.id,
            "ingredient_name": "Tomato",
            "quantity": "2",
            "category": "legumes",
            "is_checked": False,
            "week_start": get_current_monday().isoformat(),
            "created_at": now,
            "updated_at": now,
        }
        updated_item = {**existing_item, "is_checked": True}

        call_count = [0]

        def table_side_effect(table_name):
            mock_query = MagicMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: select existing item
                chain = mock_query.select.return_value
                chain = chain.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[existing_item])
            else:
                # Second call: update
                chain = mock_query.update.return_value
                chain = chain.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[updated_item])

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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    f"/api/shopping-list/items/{item_id}/check",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_checked"] is True

    def test_toggle_item_returns_404_for_nonexistent(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test toggling nonexistent item returns 404."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = mock_query.select.return_value
        chain = chain.eq.return_value.eq.return_value
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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    "/api/shopping-list/items/nonexistent-id/check",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUncheckAll:
    """Tests for PUT /api/shopping-list/uncheck-all."""

    def test_uncheck_all_returns_200_with_count(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test uncheck all returns 200 with count of unchecked items."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        # First call: count checked items
        chain = mock_query.select.return_value
        chain = chain.eq.return_value.eq.return_value.eq.return_value
        chain.execute.return_value = MagicMock(data=[], count=3)

        # Second call: update
        update_chain = mock_query.update.return_value
        update_chain = update_chain.eq.return_value.eq.return_value.eq.return_value
        update_chain.execute.return_value = MagicMock(data=[])

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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.put(
                    f"/api/shopping-list/uncheck-all?week_start={week_start}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data


class TestDeleteShoppingList:
    """Tests for DELETE /api/shopping-list."""

    def test_delete_shopping_list_returns_204(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test deleting shopping list returns 204 No Content."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        # First call: count
        chain = mock_query.select.return_value
        chain = chain.eq.return_value.eq.return_value
        chain.execute.return_value = MagicMock(data=[], count=5)

        # Second call: delete
        delete_chain = mock_query.delete.return_value
        delete_chain = delete_chain.eq.return_value.eq.return_value
        delete_chain.execute.return_value = MagicMock(data=[])

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
                import app.services.shopping_list_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.shopping_list_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.delete(
                    f"/api/shopping-list?week_start={week_start}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_204_NO_CONTENT
