"""Tests for Recipe API filtering integration - Groupe 3.

Test plan: TI-001 to TI-011
Tests API endpoints with authentication and filtering.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.auth import UserResponse
from app.models.preferences import AllergyType, DietaryType, UserPreferencesResponse
from app.routes.auth import get_optional_user
from app.routes.recipes import get_preferences_service

client = TestClient(app)


@pytest.fixture
def mock_vegetarian_user():
    """Mock authenticated vegetarian user."""
    return UserResponse(
        id="user-123",
        name="Test User",
        email="test@example.com",
        email_verified=True,
        created_at=datetime.now(),
    )


@pytest.fixture
def mock_vegetarian_preferences():
    """Mock vegetarian preferences."""
    return UserPreferencesResponse(
        dietary_preferences=[DietaryType.VEGETARIAN],
        allergies=[],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2,
    )


@pytest.fixture
def mock_strict_preferences():
    """Mock strict preferences (vegan + gluten + lactose)."""
    return UserPreferencesResponse(
        dietary_preferences=[DietaryType.VEGAN],
        allergies=[AllergyType.GLUTEN, AllergyType.LACTOSE],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2,
    )


@pytest.fixture
def mock_empty_preferences():
    """Mock empty preferences."""
    return UserPreferencesResponse(
        dietary_preferences=[],
        allergies=[],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2,
    )


def make_meal_response(id: str, name: str, ingredients: list[str]) -> dict:
    """Create mock TheMealDB meal response."""
    meal = {
        "idMeal": id,
        "strMeal": name,
        "strMealThumb": f"https://example.com/{id}.jpg",
        "strCategory": "Test",
        "strArea": "Test",
        "strInstructions": "Test instructions",
    }
    for i, ing in enumerate(ingredients, 1):
        meal[f"strIngredient{i}"] = ing
        meal[f"strMeasure{i}"] = "1 cup"
    return meal


class TestSearchEndpoint:
    """Tests for /search endpoint (TI-001 to TI-003)."""

    @patch("app.services.themealdb.themealdb_client.search_by_name")
    def test_search_authenticated_user_filters_by_preferences(
        self,
        mock_search,
        mock_vegetarian_user,
        mock_vegetarian_preferences,
    ):
        """TI-001: Authenticated user gets filtered results."""
        # Setup dependency overrides
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = mock_vegetarian_preferences

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        mock_search.return_value = {
            "meals": [
                make_meal_response("1", "Vegetable Curry", ["rice", "vegetables"]),
                make_meal_response("2", "Chicken Curry", ["chicken", "rice"]),
                make_meal_response("3", "Tofu Stir Fry", ["tofu", "vegetables"]),
            ]
        }

        try:
            response = client.get("/api/recipes/search?q=curry")

            assert response.status_code == 200
            data = response.json()
            # Should have 2 recipes (vegetable curry and tofu stir fry)
            # Chicken curry should be filtered out
            assert len(data["recipes"]) == 2
            recipe_names = [r["name"] for r in data["recipes"]]
            assert "Chicken Curry" not in recipe_names
        finally:
            app.dependency_overrides.clear()

    @patch("app.services.themealdb.themealdb_client.search_by_name")
    def test_search_unauthenticated_returns_all_recipes(self, mock_search):
        """TI-002: Unauthenticated user gets all results."""
        mock_search.return_value = {
            "meals": [
                make_meal_response("1", "Vegetable Curry", ["rice", "vegetables"]),
                make_meal_response("2", "Chicken Curry", ["chicken", "rice"]),
                make_meal_response("3", "Beef Stew", ["beef", "potatoes"]),
            ]
        }

        response = client.get("/api/recipes/search?q=food")

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 3

    @patch("app.services.themealdb.themealdb_client.search_by_name")
    def test_search_authenticated_no_matching_recipes_returns_empty(
        self,
        mock_search,
        mock_vegetarian_user,
        mock_strict_preferences,
    ):
        """TI-003: Strict preferences can result in empty list."""
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = mock_strict_preferences

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        # All recipes contain allergens
        mock_search.return_value = {
            "meals": [
                make_meal_response("1", "Pasta", ["pasta", "cheese"]),  # gluten+lactose
                make_meal_response("2", "Bread", ["bread", "butter"]),  # gluten+lactose
            ]
        }

        try:
            response = client.get("/api/recipes/search?q=pasta")

            assert response.status_code == 200
            data = response.json()
            assert len(data["recipes"]) == 0
        finally:
            app.dependency_overrides.clear()


class TestRandomEndpoint:
    """Tests for /random endpoint (TI-004 to TI-007)."""

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_random_authenticated_returns_compatible_recipe(
        self,
        mock_random,
        mock_vegetarian_user,
        mock_vegetarian_preferences,
    ):
        """TI-004: Authenticated user gets compatible random recipe."""
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = mock_vegetarian_preferences

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        # Return vegetarian recipe on first try
        mock_random.return_value = {
            "meals": [make_meal_response("1", "Veggie Pasta", ["pasta", "tomato"])]
        }

        try:
            response = client.get("/api/recipes/random")

            assert response.status_code == 200
            data = response.json()
            assert data["recipe"] is not None
            assert data["recipe"]["name"] == "Veggie Pasta"
            assert mock_random.call_count == 1
        finally:
            app.dependency_overrides.clear()

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_random_retries_on_incompatible_recipe(
        self,
        mock_random,
        mock_vegetarian_user,
        mock_vegetarian_preferences,
    ):
        """TI-005: Random endpoint retries on incompatible recipe."""
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = mock_vegetarian_preferences

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        # First 2 calls return meat, 3rd returns vegetarian
        mock_random.side_effect = [
            {"meals": [make_meal_response("1", "Chicken", ["chicken", "rice"])]},
            {"meals": [make_meal_response("2", "Beef", ["beef", "potatoes"])]},
            {"meals": [make_meal_response("3", "Veggie", ["tofu", "rice"])]},
        ]

        try:
            response = client.get("/api/recipes/random")

            assert response.status_code == 200
            data = response.json()
            assert data["recipe"] is not None
            assert data["recipe"]["name"] == "Veggie"
            assert mock_random.call_count == 3
        finally:
            app.dependency_overrides.clear()

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_random_max_10_attempts_returns_null(
        self,
        mock_random,
        mock_vegetarian_user,
        mock_strict_preferences,
    ):
        """TI-006: Returns null after 10 failed attempts."""
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = mock_strict_preferences

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        # All attempts return incompatible recipes
        mock_random.return_value = {
            "meals": [make_meal_response("1", "Pasta", ["pasta", "cheese"])]
        }

        try:
            response = client.get("/api/recipes/random")

            assert response.status_code == 200
            data = response.json()
            assert data["recipe"] is None
            assert mock_random.call_count == 10
        finally:
            app.dependency_overrides.clear()

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_random_unauthenticated_no_retry_logic(self, mock_random):
        """TI-007: Unauthenticated user gets first random recipe."""
        mock_random.return_value = {
            "meals": [make_meal_response("1", "Chicken Curry", ["chicken", "rice"])]
        }

        response = client.get("/api/recipes/random")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe"] is not None
        assert data["recipe"]["name"] == "Chicken Curry"
        assert mock_random.call_count == 1


class TestCategoryEndpoint:
    """Tests for /category/{name} endpoint (TI-008 to TI-009)."""

    @patch("app.services.themealdb.themealdb_client.get_by_id")
    @patch("app.services.themealdb.themealdb_client.filter_by_category")
    def test_category_authenticated_filters_recipes(
        self,
        mock_filter,
        mock_get_by_id,
        mock_vegetarian_user,
    ):
        """TI-008: Authenticated user gets filtered category results."""
        mock_service = MagicMock()
        mock_service.get_preferences.return_value = UserPreferencesResponse(
            dietary_preferences=[],
            allergies=[AllergyType.GLUTEN],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=2,
        )

        def override_user():
            return mock_vegetarian_user

        def override_prefs():
            return mock_service

        app.dependency_overrides[get_optional_user] = override_user
        app.dependency_overrides[get_preferences_service] = override_prefs

        # Category returns summaries
        mock_filter.return_value = {
            "meals": [
                {"idMeal": "1", "strMeal": "Pasta 1", "strMealThumb": "url1"},
                {"idMeal": "2", "strMeal": "Rice Dish", "strMealThumb": "url2"},
            ]
        }

        # Detail calls return full recipes
        mock_get_by_id.side_effect = [
            {"meals": [make_meal_response("1", "Pasta 1", ["pasta", "tomato"])]},
            {"meals": [make_meal_response("2", "Rice Dish", ["rice", "vegetables"])]},
        ]

        try:
            response = client.get("/api/recipes/category/Pasta")

            assert response.status_code == 200
            data = response.json()
            # Pasta should be filtered out (gluten), only rice dish remains
            assert len(data["recipes"]) == 1
            assert data["recipes"][0]["name"] == "Rice Dish"
        finally:
            app.dependency_overrides.clear()

    @patch("app.services.themealdb.themealdb_client.filter_by_category")
    def test_category_unauthenticated_returns_all(self, mock_filter):
        """TI-009: Unauthenticated user gets all category results."""
        mock_filter.return_value = {
            "meals": [
                {"idMeal": "1", "strMeal": "Chicken 1", "strMealThumb": "url1"},
                {"idMeal": "2", "strMeal": "Chicken 2", "strMealThumb": "url2"},
            ]
        }

        response = client.get("/api/recipes/category/Chicken")

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 2


class TestGetOptionalUser:
    """Tests for get_optional_user dependency (TI-010 to TI-011)."""

    @patch("app.routes.auth.get_auth_service")
    def test_get_optional_user_with_valid_token_returns_user(self, mock_auth_service):
        """TI-010: Valid token returns user."""
        mock_service = MagicMock()
        mock_service.get_user.return_value = UserResponse(
            id="user-123",
            name="Test User",
            email="test@example.com",
            email_verified=True,
            created_at=datetime.now(),
        )
        mock_auth_service.return_value = mock_service

        result = get_optional_user(
            authorization="Bearer valid-token",
            auth_service=mock_service,
        )

        assert result is not None
        assert result.id == "user-123"

    def test_get_optional_user_without_token_returns_none(self):
        """TI-011: No token returns None without error."""
        mock_service = MagicMock()

        result = get_optional_user(
            authorization=None,
            auth_service=mock_service,
        )

        assert result is None
