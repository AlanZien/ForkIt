"""Tests for recipe API routes."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Mock data for TheMealDB responses
MOCK_MEAL = {
    "idMeal": "52771",
    "strMeal": "Spicy Arrabiata Penne",
    "strCategory": "Vegetarian",
    "strArea": "Italian",
    "strInstructions": "Bring a large pot of water to a boil.",
    "strMealThumb": "https://www.themealdb.com/images/media/meals/ustsqw1468250014.jpg",
    "strTags": "Pasta,Curry",
    "strYoutube": "https://www.youtube.com/watch?v=1IszT_guI08",
    "strSource": "https://example.com",
    "strIngredient1": "penne rigate",
    "strIngredient2": "olive oil",
    "strIngredient3": "",
    "strMeasure1": "1 pound",
    "strMeasure2": "1/4 cup",
    "strMeasure3": "",
}

MOCK_CATEGORY = {
    "idCategory": "1",
    "strCategory": "Beef",
    "strCategoryThumb": "https://www.themealdb.com/images/category/beef.png",
    "strCategoryDescription": "Beef is the culinary name for meat from cattle.",
}


class TestSearchRecipes:
    """Tests for GET /api/recipes/search endpoint."""

    @patch("app.services.themealdb.themealdb_client.search_by_name")
    def test_search_recipes_returns_results(self, mock_search: AsyncMock):
        """Test search returns matching recipes."""
        mock_search.return_value = {"meals": [MOCK_MEAL]}

        response = client.get("/api/recipes/search?q=pasta")

        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["id"] == "52771"
        assert data["recipes"][0]["name"] == "Spicy Arrabiata Penne"
        mock_search.assert_called_once_with("pasta")

    @patch("app.services.themealdb.themealdb_client.search_by_name")
    def test_search_recipes_returns_empty_list(self, mock_search: AsyncMock):
        """Test search returns empty list when no matches."""
        mock_search.return_value = {"meals": None}

        response = client.get("/api/recipes/search?q=nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["recipes"] == []

    def test_search_requires_query_parameter(self):
        """Test search requires q parameter."""
        response = client.get("/api/recipes/search")

        assert response.status_code == 422


class TestGetRandomRecipe:
    """Tests for GET /api/recipes/random endpoint."""

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_get_random_returns_recipe(self, mock_random: AsyncMock):
        """Test random returns a recipe."""
        mock_random.return_value = {"meals": [MOCK_MEAL]}

        response = client.get("/api/recipes/random")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe"] is not None
        assert data["recipe"]["id"] == "52771"
        assert len(data["recipe"]["ingredients"]) == 2

    @patch("app.services.themealdb.themealdb_client.get_random")
    def test_get_random_handles_empty_response(self, mock_random: AsyncMock):
        """Test random handles empty response."""
        mock_random.return_value = {"meals": None}

        response = client.get("/api/recipes/random")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe"] is None


class TestGetCategories:
    """Tests for GET /api/recipes/categories endpoint."""

    @patch("app.services.themealdb.themealdb_client.list_categories")
    def test_get_categories_returns_list(self, mock_categories: AsyncMock):
        """Test categories returns list."""
        mock_categories.return_value = {"categories": [MOCK_CATEGORY]}

        response = client.get("/api/recipes/categories")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "Beef"

    @patch("app.services.themealdb.themealdb_client.list_categories")
    def test_get_categories_handles_empty(self, mock_categories: AsyncMock):
        """Test categories handles empty response."""
        mock_categories.return_value = {"categories": None}

        response = client.get("/api/recipes/categories")

        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == []


class TestGetRecipesByCategory:
    """Tests for GET /api/recipes/category/{name} endpoint."""

    @patch("app.services.themealdb.themealdb_client.filter_by_category")
    def test_get_by_category_returns_recipes(self, mock_filter: AsyncMock):
        """Test get by category returns recipes."""
        mock_filter.return_value = {
            "meals": [
                {
                    "idMeal": "52771",
                    "strMeal": "Spicy Arrabiata Penne",
                    "strMealThumb": "https://example.com/thumb.jpg",
                }
            ]
        }

        response = client.get("/api/recipes/category/Vegetarian")

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 1
        mock_filter.assert_called_once_with("Vegetarian")


class TestGetRecipeById:
    """Tests for GET /api/recipes/{id} endpoint."""

    @patch("app.services.themealdb.themealdb_client.get_by_id")
    def test_get_by_id_returns_recipe(self, mock_get: AsyncMock):
        """Test get by ID returns full recipe."""
        mock_get.return_value = {"meals": [MOCK_MEAL]}

        response = client.get("/api/recipes/52771")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe"]["id"] == "52771"
        assert data["recipe"]["name"] == "Spicy Arrabiata Penne"
        assert data["recipe"]["category"] == "Vegetarian"
        assert data["recipe"]["area"] == "Italian"
        assert len(data["recipe"]["ingredients"]) == 2

    @patch("app.services.themealdb.themealdb_client.get_by_id")
    def test_get_by_id_not_found(self, mock_get: AsyncMock):
        """Test get by ID returns 404 when not found."""
        mock_get.return_value = {"meals": None}

        response = client.get("/api/recipes/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Recipe not found"


class TestRecipeModelParsing:
    """Tests for Recipe model parsing from API response."""

    @patch("app.services.themealdb.themealdb_client.get_by_id")
    def test_ingredients_parsed_correctly(self, mock_get: AsyncMock):
        """Test ingredients are parsed from numbered fields."""
        meal_data = {
            **MOCK_MEAL,
            "strIngredient1": "Tomatoes",
            "strIngredient2": "Garlic",
            "strIngredient3": "Basil",
            "strIngredient4": "",
            "strMeasure1": "400g",
            "strMeasure2": "2 cloves",
            "strMeasure3": "Fresh",
            "strMeasure4": "",
        }
        mock_get.return_value = {"meals": [meal_data]}

        response = client.get("/api/recipes/52771")

        data = response.json()
        ingredients = data["recipe"]["ingredients"]
        assert len(ingredients) == 3
        assert ingredients[0] == {"name": "Tomatoes", "measure": "400g"}
        assert ingredients[1] == {"name": "Garlic", "measure": "2 cloves"}
        assert ingredients[2] == {"name": "Basil", "measure": "Fresh"}

    @patch("app.services.themealdb.themealdb_client.get_by_id")
    def test_empty_ingredients_skipped(self, mock_get: AsyncMock):
        """Test empty ingredient fields are skipped."""
        meal_data = {
            **MOCK_MEAL,
            "strIngredient1": "Pasta",
            "strIngredient2": "  ",  # whitespace only
            "strIngredient3": None,
            "strMeasure1": "500g",
            "strMeasure2": "",
            "strMeasure3": None,
        }
        mock_get.return_value = {"meals": [meal_data]}

        response = client.get("/api/recipes/52771")

        data = response.json()
        ingredients = data["recipe"]["ingredients"]
        assert len(ingredients) == 1
        assert ingredients[0]["name"] == "Pasta"
