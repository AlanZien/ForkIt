"""Tests for personal recipes API routes.

Tests are based on test-plan.md tests 21-58 covering:
- POST /api/personal-recipes (create)
- GET /api/personal-recipes (list)
- GET /api/personal-recipes/{id} (get single)
- PUT /api/personal-recipes/{id} (update)
- DELETE /api/personal-recipes/{id} (delete)
- POST /api/personal-recipes/fork/{api_recipe_id} (fork)
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

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


@pytest.fixture
def mock_auth_user_b():
    """Create a second mock authenticated user for RLS tests."""
    return MockUser(
        id="660e8400-e29b-41d4-a716-446655440001",
        email="testb@example.com",
    )


def setup_auth_mock(mock_client, mock_user):
    """Setup auth mock to return the mock user."""
    mock_user_response = MagicMock()
    mock_user_response.user = mock_user
    mock_client.auth.get_user.return_value = mock_user_response


def reload_app_modules():
    """Reload app modules to pick up mocked dependencies."""
    import importlib

    import app.main
    import app.services.auth_service
    import app.services.personal_recipes_service

    importlib.reload(app.services.auth_service)
    importlib.reload(app.services.personal_recipes_service)
    importlib.reload(app.main)

    from app.main import app

    return TestClient(app)


def create_sample_recipe_data():
    """Create sample recipe data for tests."""
    return {
        "title": "Tarte aux pommes",
        "servings": 6,
        "prep_time_minutes": 30,
        "cook_time_minutes": 45,
        "tags": ["dessert", "automne"],
        "ingredients": [
            {"name": "Pommes", "quantity": 4, "unit": "pieces", "note": "Golden"},
            {"name": "Pate feuilletee", "quantity": 1, "unit": "rouleau"},
        ],
        "steps": [
            {"instruction": "Eplucher les pommes"},
            {"instruction": "Derouler la pate"},
        ],
    }


def create_sample_recipe_response(user_id: str, recipe_id: str | None = None):
    """Create sample recipe response from DB."""
    if recipe_id is None:
        recipe_id = str(uuid4())
    now = datetime.now().isoformat()
    return {
        "id": recipe_id,
        "user_id": user_id,
        "title": "Tarte aux pommes",
        "image_url": None,
        "servings": 6,
        "prep_time_minutes": 30,
        "cook_time_minutes": 45,
        "tags": ["dessert", "automne"],
        "source_recipe_id": None,
        "created_at": now,
        "updated_at": now,
    }


def create_sample_ingredients_response(recipe_id: str):
    """Create sample ingredients response from DB."""
    return [
        {
            "id": str(uuid4()),
            "recipe_id": recipe_id,
            "name": "Pommes",
            "quantity": 4,
            "unit": "pieces",
            "note": "Golden",
            "sort_order": 0,
        },
        {
            "id": str(uuid4()),
            "recipe_id": recipe_id,
            "name": "Pate feuilletee",
            "quantity": 1,
            "unit": "rouleau",
            "note": None,
            "sort_order": 1,
        },
    ]


def create_sample_steps_response(recipe_id: str):
    """Create sample steps response from DB."""
    return [
        {
            "id": str(uuid4()),
            "recipe_id": recipe_id,
            "step_number": 1,
            "instruction": "Eplucher les pommes",
        },
        {
            "id": str(uuid4()),
            "recipe_id": recipe_id,
            "step_number": 2,
            "instruction": "Derouler la pate",
        },
    ]


# =============================================================================
# POST /api/personal-recipes Tests (Tests 21-28)
# =============================================================================


class TestCreatePersonalRecipe:
    """Tests for POST /api/personal-recipes."""

    def test_create_recipe_success_returns_201(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 21: POST /api/personal-recipes returns 201 with valid data."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        recipe_id = str(uuid4())
        recipe_response = create_sample_recipe_response(mock_auth_user.id, recipe_id)
        ingredients_response = create_sample_ingredients_response(recipe_id)
        steps_response = create_sample_steps_response(recipe_id)

        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == "personal_recipes":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=[recipe_response]
                )
            elif table_name == "personal_recipe_ingredients":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=ingredients_response
                )
            elif table_name == "personal_recipe_steps":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=steps_response
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
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=create_sample_recipe_data(),
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == recipe_id
        assert data["user_id"] == mock_auth_user.id
        assert data["title"] == "Tarte aux pommes"
        assert "created_at" in data

    def test_create_recipe_without_auth_returns_401(self, mock_supabase_client):
        """Test 22: POST /api/personal-recipes without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=create_sample_recipe_data(),
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_recipe_missing_title_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 23: POST with missing title returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        del data["title"]

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_missing_servings_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 24: POST with missing servings returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        del data["servings"]

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_servings_out_of_range_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 25: POST with servings above max returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        data["servings"] = 25

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_servings_zero_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 26: POST with servings=0 returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        data["servings"] = 0

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_empty_ingredients_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 27: POST with empty ingredients returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        data["ingredients"] = []

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_empty_steps_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 28: POST with empty steps returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        data = create_sample_recipe_data()
        data["steps"] = []

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post(
                    "/api/personal-recipes",
                    json=data,
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# GET /api/personal-recipes Tests (Tests 29-32)
# =============================================================================


class TestListPersonalRecipes:
    """Tests for GET /api/personal-recipes."""

    def test_list_recipes_returns_user_recipes_only(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 29: GET /api/personal-recipes returns user's recipes only."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        recipes_data = [
            create_sample_recipe_response(mock_auth_user.id, str(uuid4()))
            for _ in range(5)
        ]

        mock_query = MagicMock()
        sel = mock_query.select.return_value
        chain = sel.eq.return_value.order.return_value
        chain.execute.return_value = MagicMock(data=recipes_data)
        mock_supabase_client.table.return_value = mock_query

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.get(
                    "/api/personal-recipes",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 5
        assert len(data["recipes"]) == 5

    def test_list_recipes_without_auth_returns_401(self, mock_supabase_client):
        """Test 30: GET /api/personal-recipes without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.get("/api/personal-recipes")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_recipes_empty_list(self, mock_supabase_client, mock_auth_user):
        """Test 31: GET returns empty list for new user."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        mock_query = MagicMock()
        sel = mock_query.select.return_value
        chain = sel.eq.return_value.order.return_value
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
                client = reload_app_modules()
                response = client.get(
                    "/api/personal-recipes",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["recipes"] == []
        assert data["count"] == 0


# =============================================================================
# GET /api/personal-recipes/{id} Tests (Tests 33-37)
# =============================================================================


class TestGetPersonalRecipe:
    """Tests for GET /api/personal-recipes/{id}."""

    def test_get_recipe_with_ingredients_and_steps(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 33: GET /{id} returns recipe with nested data."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        recipe_id = str(uuid4())
        recipe_response = create_sample_recipe_response(mock_auth_user.id, recipe_id)
        ingredients_response = create_sample_ingredients_response(recipe_id)
        steps_response = create_sample_steps_response(recipe_id)

        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == "personal_recipes":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[recipe_response])
            elif table_name == "personal_recipe_ingredients":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.order.return_value
                chain.execute.return_value = MagicMock(data=ingredients_response)
            elif table_name == "personal_recipe_steps":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.order.return_value
                chain.execute.return_value = MagicMock(data=steps_response)
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
                client = reload_app_modules()
                response = client.get(
                    f"/api/personal-recipes/{recipe_id}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == recipe_id
        assert len(data["ingredients"]) == 2
        assert len(data["steps"]) == 2

    def test_get_recipe_not_found_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 34: GET /{id} returns 404 for nonexistent recipe."""
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
                client = reload_app_modules()
                response = client.get(
                    f"/api/personal-recipes/{uuid4()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Recipe not found"

    def test_get_other_user_recipe_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 35: GET other user's recipe returns 404 (RLS)."""
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
                client = reload_app_modules()
                response = client.get(
                    f"/api/personal-recipes/{uuid4()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_recipe_without_auth_returns_401(self, mock_supabase_client):
        """Test 36: GET /{id} without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.get(f"/api/personal-recipes/{uuid4()}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# PUT /api/personal-recipes/{id} Tests (Tests 38-45)
# =============================================================================


class TestUpdatePersonalRecipe:
    """Tests for PUT /api/personal-recipes/{id}."""

    def test_update_recipe_success(self, mock_supabase_client, mock_auth_user):
        """Test 38: PUT /{id} updates recipe successfully."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        recipe_id = str(uuid4())
        recipe_response = create_sample_recipe_response(mock_auth_user.id, recipe_id)
        recipe_response["title"] = "Updated Title"
        recipe_response["servings"] = 8
        ingredients_response = create_sample_ingredients_response(recipe_id)
        steps_response = create_sample_steps_response(recipe_id)

        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == "personal_recipes":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[recipe_response])
                upd = mock_query.update.return_value
                upd.eq.return_value.execute.return_value = MagicMock(
                    data=[recipe_response]
                )
            elif table_name == "personal_recipe_ingredients":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.order.return_value
                chain.execute.return_value = MagicMock(data=ingredients_response)
            elif table_name == "personal_recipe_steps":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.order.return_value
                chain.execute.return_value = MagicMock(data=steps_response)
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
                client = reload_app_modules()
                response = client.put(
                    f"/api/personal-recipes/{recipe_id}",
                    json={"title": "Updated Title", "servings": 8},
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_other_user_recipe_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 41: PUT other user's recipe returns 404."""
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
                client = reload_app_modules()
                response = client.put(
                    f"/api/personal-recipes/{uuid4()}",
                    json={"title": "Hacked"},
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_recipe_without_auth_returns_401(self, mock_supabase_client):
        """Test 42: PUT /{id} without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.put(
                    f"/api/personal-recipes/{uuid4()}",
                    json={"title": "Updated"},
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_recipe_invalid_servings_returns_422(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 43: PUT with invalid servings returns 422."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.put(
                    f"/api/personal-recipes/{uuid4()}",
                    json={"servings": -1},
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_recipe_not_found_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 44: PUT nonexistent recipe returns 404."""
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
                client = reload_app_modules()
                response = client.put(
                    f"/api/personal-recipes/{uuid4()}",
                    json={"title": "Updated"},
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# DELETE /api/personal-recipes/{id} Tests (Tests 46-51)
# =============================================================================


class TestDeletePersonalRecipe:
    """Tests for DELETE /api/personal-recipes/{id}."""

    def test_delete_recipe_success(self, mock_supabase_client, mock_auth_user):
        """Test 46: DELETE /{id} deletes recipe."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        recipe_id = str(uuid4())
        recipe_response = create_sample_recipe_response(mock_auth_user.id, recipe_id)

        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == "personal_recipes":
                sel = mock_query.select.return_value
                chain = sel.eq.return_value.eq.return_value
                chain.execute.return_value = MagicMock(data=[recipe_response])
                dlt = mock_query.delete.return_value
                dlt.eq.return_value.execute.return_value = MagicMock(data=[])
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
                client = reload_app_modules()
                response = client.delete(
                    f"/api/personal-recipes/{recipe_id}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_other_user_recipe_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 47: DELETE other user's recipe returns 404."""
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
                client = reload_app_modules()
                response = client.delete(
                    f"/api/personal-recipes/{uuid4()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_recipe_without_auth_returns_401(self, mock_supabase_client):
        """Test 48: DELETE /{id} without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.delete(f"/api/personal-recipes/{uuid4()}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_recipe_not_found_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 49: DELETE nonexistent recipe returns 404."""
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
                client = reload_app_modules()
                response = client.delete(
                    f"/api/personal-recipes/{uuid4()}",
                    headers={"Authorization": "Bearer mock.token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# POST /api/personal-recipes/fork/{api_recipe_id} Tests (Tests 52-58)
# =============================================================================


class TestForkPersonalRecipe:
    """Tests for POST /api/personal-recipes/fork/{api_recipe_id}."""

    def test_fork_recipe_success(self, mock_supabase_client, mock_auth_user):
        """Test 52: POST /fork/{id} forks recipe from TheMealDB."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        recipe_id = str(uuid4())
        api_recipe_id = "52772"

        recipe_response = create_sample_recipe_response(mock_auth_user.id, recipe_id)
        recipe_response["source_recipe_id"] = api_recipe_id
        recipe_response["title"] = "Teriyaki Chicken"
        ingredients_response = create_sample_ingredients_response(recipe_id)
        steps_response = create_sample_steps_response(recipe_id)

        themealdb_response = {
            "meals": [
                {
                    "idMeal": api_recipe_id,
                    "strMeal": "Teriyaki Chicken",
                    "strMealThumb": "https://example.com/img.jpg",
                    "strCategory": "Chicken",
                    "strArea": "Japanese",
                    "strInstructions": "Step 1.\nStep 2.",
                    "strIngredient1": "Chicken",
                    "strMeasure1": "500g",
                    "strIngredient2": "Soy sauce",
                    "strMeasure2": "3 tbsp",
                }
            ]
        }

        def table_side_effect(table_name):
            mock_query = MagicMock()
            if table_name == "personal_recipes":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=[recipe_response]
                )
            elif table_name == "personal_recipe_ingredients":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=ingredients_response
                )
            elif table_name == "personal_recipe_steps":
                mock_query.insert.return_value.execute.return_value = MagicMock(
                    data=steps_response
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
                with patch(
                    "app.services.themealdb.themealdb_client.get_by_id",
                    new_callable=AsyncMock,
                    return_value=themealdb_response,
                ):
                    client = reload_app_modules()
                    response = client.post(
                        f"/api/personal-recipes/fork/{api_recipe_id}",
                        headers={"Authorization": "Bearer mock.token"},
                    )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["source_recipe_id"] == api_recipe_id

    def test_fork_recipe_api_recipe_not_found_returns_404(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 56: POST /fork/{id} returns 404 if recipe not found."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)
        themealdb_response = {"meals": None}

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                with patch(
                    "app.services.themealdb.themealdb_client.get_by_id",
                    new_callable=AsyncMock,
                    return_value=themealdb_response,
                ):
                    client = reload_app_modules()
                    response = client.post(
                        "/api/personal-recipes/fork/99999",
                        headers={"Authorization": "Bearer mock.token"},
                    )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_fork_recipe_without_auth_returns_401(self, mock_supabase_client):
        """Test 57: POST /fork/{id} without auth returns 401."""
        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                client = reload_app_modules()
                response = client.post("/api/personal-recipes/fork/52772")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fork_recipe_themealdb_api_error_returns_503(
        self, mock_supabase_client, mock_auth_user
    ):
        """Test 58: POST /fork/{id} returns 503 on API error."""
        setup_auth_mock(mock_supabase_client, mock_auth_user)

        with patch(
            "app.services.supabase.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "app.services.supabase.get_supabase_admin",
                return_value=mock_supabase_client,
            ):
                with patch(
                    "app.services.themealdb.themealdb_client.get_by_id",
                    new_callable=AsyncMock,
                    side_effect=Exception("API unavailable"),
                ):
                    client = reload_app_modules()
                    response = client.post(
                        "/api/personal-recipes/fork/52772",
                        headers={"Authorization": "Bearer mock.token"},
                    )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
