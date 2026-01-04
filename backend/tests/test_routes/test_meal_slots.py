"""Tests for meal slots API routes."""

from datetime import date, datetime, timedelta
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


def get_next_monday() -> date:
    """Get the next Monday date (or today if Monday)."""
    today = date.today()
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0 and today.weekday() != 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def get_current_monday() -> date:
    """Get the Monday of the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


def get_valid_slot_date() -> date:
    """Get a valid date for creating slots (today or future)."""
    return date.today()


def build_select_chain(mock_query, levels=3):
    """Build a mock chain for select queries with variable depth."""
    chain = mock_query.select.return_value
    for _ in range(levels):
        chain = chain.eq.return_value
    return chain


def build_week_slots_chain(mock_query):
    """Build mock chain for get_week_slots."""
    chain = mock_query.select.return_value
    chain = chain.eq.return_value
    chain = chain.gte.return_value
    chain = chain.lte.return_value
    chain = chain.order.return_value
    chain = chain.order.return_value
    return chain


class TestGetWeekSlots:
    """Tests for GET /api/meal-slots."""

    def test_get_week_slots_returns_empty_list(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET week slots returns empty list for new user."""
        # Given: User is authenticated with no slots
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = build_week_slots_chain(mock_query)
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.get(
                    f"/api/meal-slots?week_start={week_start}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 200 with empty slots array
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slots"] == []
        assert data["week_start"] == week_start

    def test_get_week_slots_returns_slots_within_range(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET week slots returns slots within the date range."""
        # Given: User has 2 slots for the week
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        week_start = get_current_monday()
        slots_data = [
            {
                "id": "slot-1",
                "user_id": mock_auth_user.id,
                "date": week_start.isoformat(),
                "meal_type": "dejeuner",
                "recipe_id": "52772",
                "recipe_name": "Teriyaki Chicken",
                "recipe_thumbnail": "https://example.com/img.jpg",
                "portions": 4,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "id": "slot-2",
                "user_id": mock_auth_user.id,
                "date": week_start.isoformat(),
                "meal_type": "diner",
                "recipe_id": "52773",
                "recipe_name": "Salmon Teriyaki",
                "recipe_thumbnail": "https://example.com/img2.jpg",
                "portions": 2,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        ]

        mock_query = MagicMock()
        chain = build_week_slots_chain(mock_query)
        chain.execute.return_value = MagicMock(data=slots_data)

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    f"/api/meal-slots?week_start={week_start.isoformat()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 200 with 2 slots
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["slots"]) == 2
        assert data["slots"][0]["recipe_id"] == "52772"
        assert data["slots"][1]["recipe_id"] == "52773"

    def test_get_week_slots_returns_401_without_auth(self, mock_supabase_client):
        """Test GET week slots returns 401 without authentication."""
        # Given: No authentication token

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                week_start = get_current_monday().isoformat()
                response = client.get(f"/api/meal-slots?week_start={week_start}")

        # Then: Status 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_week_slots_returns_400_for_invalid_week_start(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET week slots returns 400 when week_start is not a Monday."""
        # Given: User is authenticated but week_start is Tuesday
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                # Get a Tuesday (Monday + 1 day)
                tuesday = get_current_monday() + timedelta(days=1)
                response = client.get(
                    f"/api/meal-slots?week_start={tuesday.isoformat()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 400 with error message
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Monday" in response.json()["detail"]


class TestCreateSlot:
    """Tests for POST /api/meal-slots."""

    def test_create_slot_returns_201_with_slot(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test creating a new meal slot returns 201."""
        # Given: User is authenticated
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        slot_date = get_next_monday()
        new_slot = {
            "id": "slot-new",
            "user_id": mock_auth_user.id,
            "date": slot_date.isoformat(),
            "meal_type": "dejeuner",
            "recipe_id": "52772",
            "recipe_name": "Teriyaki Chicken",
            "recipe_thumbnail": "https://example.com/img.jpg",
            "portions": 4,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        call_count = [0]

        def table_side_effect(table_name):
            mock_query = MagicMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: check existing (get_slot)
                chain = build_select_chain(mock_query, levels=3)
                chain.execute.return_value = MagicMock(data=[])
            else:
                # Second call: insert
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=[new_slot]
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/meal-slots",
                    json={
                        "slot_date": slot_date.isoformat(),
                        "meal_type": "dejeuner",
                        "recipe_id": "52772",
                        "recipe_name": "Teriyaki Chicken",
                        "recipe_thumbnail": "https://example.com/img.jpg",
                        "portions": 4,
                    },
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 201 Created
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["recipe_id"] == "52772"
        assert data["portions"] == 4

    def test_create_slot_returns_409_for_duplicate(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test creating a duplicate slot returns 409 Conflict."""
        # Given: User already has slot for this date/meal_type
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        slot_date = get_next_monday()
        existing_slot = {
            "id": "slot-existing",
            "user_id": mock_auth_user.id,
            "date": slot_date.isoformat(),
            "meal_type": "dejeuner",
            "recipe_id": "52999",
            "recipe_name": "Existing Recipe",
            "recipe_thumbnail": None,
            "portions": 2,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_query = MagicMock()
        chain = build_select_chain(mock_query, levels=3)
        chain.execute.return_value = MagicMock(data=[existing_slot])

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/meal-slots",
                    json={
                        "slot_date": slot_date.isoformat(),
                        "meal_type": "dejeuner",
                        "recipe_id": "52772",
                        "recipe_name": "New Recipe",
                    },
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_create_slot_returns_401_without_auth(self, mock_supabase_client):
        """Test creating slot without auth returns 401."""
        # Given: No authentication token

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.post(
                    "/api/meal-slots",
                    json={
                        "slot_date": get_next_monday().isoformat(),
                        "meal_type": "dejeuner",
                        "recipe_id": "52772",
                        "recipe_name": "Test Recipe",
                    },
                )

        # Then: Status 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateSlot:
    """Tests for PUT /api/meal-slots/{date}/{meal_type}."""

    def test_update_slot_returns_200_with_updated_slot(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test updating a slot returns 200 with updated data."""
        # Given: User has existing slot
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        slot_date = get_current_monday()
        existing_slot = {
            "id": "slot-1",
            "user_id": mock_auth_user.id,
            "date": slot_date.isoformat(),
            "meal_type": "dejeuner",
            "recipe_id": "52772",
            "recipe_name": "Teriyaki Chicken",
            "recipe_thumbnail": "https://example.com/img.jpg",
            "portions": 4,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        updated_slot = {**existing_slot, "portions": 6}

        call_count = [0]

        def table_side_effect(table_name):
            mock_query = MagicMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: get_slot
                chain = build_select_chain(mock_query, levels=3)
                chain.execute.return_value = MagicMock(data=[existing_slot])
            else:
                # Second call: update
                chain = mock_query.update.return_value
                chain = chain.eq.return_value.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[updated_slot])

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    f"/api/meal-slots/{slot_date.isoformat()}/dejeuner",
                    json={"portions": 6},
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 200 with updated portions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["portions"] == 6

    def test_update_slot_returns_404_for_nonexistent(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test updating nonexistent slot returns 404."""
        # Given: No slot exists for this date/meal_type
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = build_select_chain(mock_query, levels=3)
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.put(
                    f"/api/meal-slots/{get_current_monday().isoformat()}/dejeuner",
                    json={"portions": 6},
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteSlot:
    """Tests for DELETE /api/meal-slots/{date}/{meal_type}."""

    def test_delete_slot_returns_204_on_success(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test deleting a slot returns 204 No Content."""
        # Given: User has existing slot
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        slot_date = get_current_monday()
        existing_slot = {
            "id": "slot-1",
            "user_id": mock_auth_user.id,
            "date": slot_date.isoformat(),
            "meal_type": "dejeuner",
            "recipe_id": "52772",
            "recipe_name": "Teriyaki Chicken",
            "recipe_thumbnail": None,
            "portions": 4,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        call_count = [0]

        def table_side_effect(table_name):
            mock_query = MagicMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: get_slot
                chain = build_select_chain(mock_query, levels=3)
                chain.execute.return_value = MagicMock(data=[existing_slot])
            else:
                # Second call: delete
                chain = mock_query.delete.return_value
                chain = chain.eq.return_value.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[])

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.delete(
                    f"/api/meal-slots/{slot_date.isoformat()}/dejeuner",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 204 No Content
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_slot_returns_404_for_nonexistent(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test deleting nonexistent slot returns 404."""
        # Given: No slot exists
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        chain = build_select_chain(mock_query, levels=3)
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.delete(
                    f"/api/meal-slots/{get_current_monday().isoformat()}/dejeuner",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetRecentRecipes:
    """Tests for GET /api/meal-slots/recent."""

    def test_get_recent_returns_200_with_recipes(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET recent recipes returns list of recent unique recipes."""
        # Given: User has added recipes to slots
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        recent_data = [
            {
                "recipe_id": "52772",
                "recipe_name": "Teriyaki Chicken",
                "recipe_thumbnail": "https://example.com/img.jpg",
                "created_at": datetime.now().isoformat(),
            },
            {
                "recipe_id": "52773",
                "recipe_name": "Salmon Teriyaki",
                "recipe_thumbnail": "https://example.com/img2.jpg",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            },
        ]

        mock_query = MagicMock()
        chain = mock_query.select.return_value.eq.return_value.order.return_value
        chain.execute.return_value = MagicMock(data=recent_data)

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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/meal-slots/recent",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 200 with recipes
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["recipe_id"] == "52772"

    def test_get_recent_returns_empty_for_new_user(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test GET recent returns empty list for user with no slots."""
        # Given: User has no slots
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
                import app.services.meal_slots_service

                importlib.reload(app.services.auth_service)
                importlib.reload(app.services.meal_slots_service)
                importlib.reload(app.main)

                from app.main import app

                client = TestClient(app)
                response = client.get(
                    "/api/meal-slots/recent",
                    headers={"Authorization": "Bearer mock.token"},
                )

        # Then: Status 200 with empty array
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
