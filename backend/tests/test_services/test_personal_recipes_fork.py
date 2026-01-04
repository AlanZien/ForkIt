"""Tests for PersonalRecipesService fork functionality - TDD approach.

These tests cover the fork_recipe method and ingredient/instruction parsing.
Following test-plan.md specifications for tests 52-58.
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.personal_recipe import (
    PersonalRecipeResponse,
)


class MockSupabaseResponse:
    """Mock Supabase query response."""

    def __init__(
        self, data: list | dict | None = None, error: dict | None = None
    ):
        self.data = data if data is not None else []
        self.error = error


# Create a mock for supabase module before importing the service
mock_supabase_module = MagicMock()
sys.modules["supabase"] = mock_supabase_module


# Sample TheMealDB API response for testing
SAMPLE_THEMEALDB_RECIPE = {
    "idMeal": "52772",
    "strMeal": "Teriyaki Chicken Casserole",
    "strCategory": "Chicken",
    "strArea": "Japanese",
    "strInstructions": (
        "Preheat oven to 350 F.\n"
        "Spray a 9x13-inch baking pan with non-stick spray.\n"
        "Combine soy sauce, brown sugar, and ginger in a small saucepan."
    ),
    "strMealThumb": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
    "strIngredient1": "soy sauce",
    "strIngredient2": "water",
    "strIngredient3": "brown sugar",
    "strIngredient4": "garlic",
    "strIngredient5": "ginger",
    "strIngredient6": "",
    "strIngredient7": "",
    "strIngredient8": "",
    "strIngredient9": "",
    "strIngredient10": "",
    "strIngredient11": "",
    "strIngredient12": "",
    "strIngredient13": "",
    "strIngredient14": "",
    "strIngredient15": "",
    "strIngredient16": "",
    "strIngredient17": "",
    "strIngredient18": "",
    "strIngredient19": "",
    "strIngredient20": "",
    "strMeasure1": "3/4 cup",
    "strMeasure2": "1/2 cup",
    "strMeasure3": "1/4 cup",
    "strMeasure4": "3 cloves",
    "strMeasure5": "1 tsp",
    "strMeasure6": "",
    "strMeasure7": "",
    "strMeasure8": "",
    "strMeasure9": "",
    "strMeasure10": "",
    "strMeasure11": "",
    "strMeasure12": "",
    "strMeasure13": "",
    "strMeasure14": "",
    "strMeasure15": "",
    "strMeasure16": "",
    "strMeasure17": "",
    "strMeasure18": "",
    "strMeasure19": "",
    "strMeasure20": "",
}

# Complex ingredient formats for edge case testing
SAMPLE_COMPLEX_INGREDIENTS_RECIPE = {
    "idMeal": "99998",
    "strMeal": "Test Recipe Complex",
    "strCategory": "Test",
    "strArea": "Test",
    "strInstructions": "Step 1. Do this.\nStep 2. Do that.",
    "strMealThumb": "https://example.com/image.jpg",
    "strIngredient1": "Salt",
    "strIngredient2": "Sugar",
    "strIngredient3": "Flour",
    "strIngredient4": "Parsley",
    "strIngredient5": "Butter",
    "strIngredient6": "",
    "strIngredient7": "",
    "strIngredient8": "",
    "strIngredient9": "",
    "strIngredient10": "",
    "strIngredient11": "",
    "strIngredient12": "",
    "strIngredient13": "",
    "strIngredient14": "",
    "strIngredient15": "",
    "strIngredient16": "",
    "strIngredient17": "",
    "strIngredient18": "",
    "strIngredient19": "",
    "strIngredient20": "",
    "strMeasure1": "to taste",
    "strMeasure2": "1/2 cup",
    "strMeasure3": "200g",
    "strMeasure4": "Some",
    "strMeasure5": "2 tbsp",
    "strMeasure6": "",
    "strMeasure7": "",
    "strMeasure8": "",
    "strMeasure9": "",
    "strMeasure10": "",
    "strMeasure11": "",
    "strMeasure12": "",
    "strMeasure13": "",
    "strMeasure14": "",
    "strMeasure15": "",
    "strMeasure16": "",
    "strMeasure17": "",
    "strMeasure18": "",
    "strMeasure19": "",
    "strMeasure20": "",
}


class TestForkRecipeSuccess:
    """Tests for successful fork_recipe operations.

    Test 52: test_fork_recipe_success
    """

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_success_creates_personal_recipe(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe with valid TheMealDB ID creates personal recipe.

        Given: Authenticated user
               TheMealDB recipe with id "52772" exists
        When: fork_recipe(user_id, "52772")
        Then: New personal recipe created with data from TheMealDB recipe
              source_recipe_id is set to "52772"
              user_id is set to authenticated user
        Requirement: spec.md "POST /api/personal-recipes/fork/{api_recipe_id}"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "52772"
        created_recipe_id = "new-recipe-uuid"

        # Mock TheMealDB API response
        mock_themealdb.get_by_id = AsyncMock(
            return_value={"meals": [SAMPLE_THEMEALDB_RECIPE]}
        )

        mock_client = MagicMock()

        # Mock personal_recipes insert
        recipe_data = {
            "id": created_recipe_id,
            "user_id": user_id,
            "title": "Teriyaki Chicken Casserole",
            "image_url": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
            "servings": 4,
            "prep_time_minutes": None,
            "cook_time_minutes": None,
            "tags": ["Chicken", "Japanese"],
            "source_recipe_id": "52772",
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T10:00:00+00:00",
        }
        mock_recipe_insert = MagicMock()
        mock_recipe_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[recipe_data])
        )

        # Mock ingredients insert
        ingredients_data = [
            {
                "id": f"ing-{i}",
                "recipe_id": created_recipe_id,
                "name": name,
                "quantity": qty,
                "unit": unit,
                "note": note,
                "sort_order": i,
            }
            for i, (name, qty, unit, note) in enumerate([
                ("soy sauce", 0.75, "cup", None),
                ("water", 0.5, "cup", None),
                ("brown sugar", 0.25, "cup", None),
                ("garlic", 3.0, "cloves", None),
                ("ginger", 1.0, "tsp", None),
            ])
        ]
        mock_ingredients_insert = MagicMock()
        mock_ingredients_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=ingredients_data)
        )

        # Mock steps insert
        steps_data = [
            {
                "id": f"step-{i}",
                "recipe_id": created_recipe_id,
                "step_number": i + 1,
                "instruction": instr,
            }
            for i, instr in enumerate([
                "Preheat oven to 350 F.",
                "Spray a 9x13-inch baking pan with non-stick spray.",
                "Combine soy sauce, brown sugar, and ginger in a small saucepan.",
            ])
        ]
        mock_steps_insert = MagicMock()
        mock_steps_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=steps_data)
        )

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_insert,
                "personal_recipe_ingredients": mock_ingredients_insert,
                "personal_recipe_steps": mock_steps_insert,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = await service.fork_recipe(user_id, api_recipe_id)

        assert isinstance(result, PersonalRecipeResponse)
        assert result.id == created_recipe_id
        assert result.user_id == user_id
        assert result.title == "Teriyaki Chicken Casserole"
        assert result.source_recipe_id == "52772"
        assert (
            result.image_url
            == "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg"
        )

        # Verify TheMealDB was called
        mock_themealdb.get_by_id.assert_called_once_with(api_recipe_id)


class TestForkRecipeIngredientParsing:
    """Tests for ingredient parsing during fork.

    Test 53: test_fork_recipe_parses_ingredients_structure
    Test 54: test_fork_recipe_ingredient_parsing_edge_cases
    """

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_parses_ingredients_structure(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe parses TheMealDB ingredients into structured format.

        Given: TheMealDB recipe with ingredients like "250g flour", "2 eggs"
        When: fork_recipe(user_id, api_recipe_id)
        Then: Ingredients are parsed into structured format:
              {name: "flour", quantity: 250, unit: "g"}
        Requirement: spec.md "Parse TheMealDB ingredient format into structured"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "52772"
        created_recipe_id = "new-recipe-uuid"

        # Mock TheMealDB API response
        mock_themealdb.get_by_id = AsyncMock(
            return_value={"meals": [SAMPLE_THEMEALDB_RECIPE]}
        )

        mock_client = MagicMock()
        inserted_ingredients = []

        # Recipe insert mock
        recipe_data = {
            "id": created_recipe_id,
            "user_id": user_id,
            "title": "Teriyaki Chicken Casserole",
            "image_url": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
            "servings": 4,
            "prep_time_minutes": None,
            "cook_time_minutes": None,
            "tags": ["Chicken", "Japanese"],
            "source_recipe_id": "52772",
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T10:00:00+00:00",
        }
        mock_recipe_insert = MagicMock()
        mock_recipe_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[recipe_data])
        )

        # Capture inserted ingredients
        def capture_ingredients(data):
            inserted_ingredients.extend(data)
            return MagicMock(
                execute=lambda: MockSupabaseResponse(
                    data=[{**ing, "id": f"ing-{i}"} for i, ing in enumerate(data)]
                )
            )

        mock_ingredients_insert = MagicMock()
        mock_ingredients_insert.insert.side_effect = capture_ingredients

        # Steps insert mock
        mock_steps_insert = MagicMock()
        mock_steps_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_insert,
                "personal_recipe_ingredients": mock_ingredients_insert,
                "personal_recipe_steps": mock_steps_insert,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        await service.fork_recipe(user_id, api_recipe_id)

        # Verify ingredients were parsed correctly
        assert len(inserted_ingredients) == 5

        # Check "3/4 cup" of "soy sauce"
        soy_sauce = inserted_ingredients[0]
        assert soy_sauce["name"] == "soy sauce"
        assert soy_sauce["quantity"] == 0.75  # 3/4 parsed as fraction
        assert soy_sauce["unit"] == "cup"

        # Check "1/2 cup" of "water"
        water = inserted_ingredients[1]
        assert water["name"] == "water"
        assert water["quantity"] == 0.5
        assert water["unit"] == "cup"

        # Check "1 tsp" of "ginger"
        ginger = inserted_ingredients[4]
        assert ginger["name"] == "ginger"
        assert ginger["quantity"] == 1.0
        assert ginger["unit"] == "tsp"

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_ingredient_parsing_edge_cases(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe handles complex ingredient formats.

        Given: TheMealDB recipe with complex ingredients:
               "Salt to taste", "1/2 cup sugar", "200g flour", "Some parsley"
        When: fork_recipe(user_id, api_recipe_id)
        Then: Ingredients are parsed best-effort:
              "to taste" -> quantity=1, unit="", note="to taste"
              "1/2 cup" -> quantity=0.5, unit="cup"
              "200g" -> quantity=200, unit="g"
              "Some" -> quantity=1, unit="", note="Some"
        Requirement: spec.md "use best-effort parsing"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "99998"
        created_recipe_id = "new-recipe-uuid"

        # Mock TheMealDB API response with complex ingredients
        mock_themealdb.get_by_id = AsyncMock(
            return_value={"meals": [SAMPLE_COMPLEX_INGREDIENTS_RECIPE]}
        )

        mock_client = MagicMock()
        inserted_ingredients = []

        # Recipe insert mock
        recipe_data = {
            "id": created_recipe_id,
            "user_id": user_id,
            "title": "Test Recipe Complex",
            "image_url": "https://example.com/image.jpg",
            "servings": 4,
            "prep_time_minutes": None,
            "cook_time_minutes": None,
            "tags": ["Test", "Test"],
            "source_recipe_id": "99998",
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T10:00:00+00:00",
        }
        mock_recipe_insert = MagicMock()
        mock_recipe_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[recipe_data])
        )

        # Capture inserted ingredients
        def capture_ingredients(data):
            inserted_ingredients.extend(data)
            return MagicMock(
                execute=lambda: MockSupabaseResponse(
                    data=[{**ing, "id": f"ing-{i}"} for i, ing in enumerate(data)]
                )
            )

        mock_ingredients_insert = MagicMock()
        mock_ingredients_insert.insert.side_effect = capture_ingredients

        # Steps insert mock
        mock_steps_insert = MagicMock()
        mock_steps_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_insert,
                "personal_recipe_ingredients": mock_ingredients_insert,
                "personal_recipe_steps": mock_steps_insert,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        await service.fork_recipe(user_id, api_recipe_id)

        # Verify edge cases are handled
        assert len(inserted_ingredients) == 5

        # "to taste" -> best-effort fallback
        salt = inserted_ingredients[0]
        assert salt["name"] == "Salt"
        assert salt["quantity"] == 1.0
        assert salt["unit"] == ""
        assert salt["note"] == "to taste"

        # "1/2 cup" -> parsed correctly
        sugar = inserted_ingredients[1]
        assert sugar["name"] == "Sugar"
        assert sugar["quantity"] == 0.5
        assert sugar["unit"] == "cup"

        # "200g" -> parsed without space
        flour = inserted_ingredients[2]
        assert flour["name"] == "Flour"
        assert flour["quantity"] == 200.0
        assert flour["unit"] == "g"

        # "Some" -> best-effort fallback
        parsley = inserted_ingredients[3]
        assert parsley["name"] == "Parsley"
        assert parsley["quantity"] == 1.0
        assert parsley["unit"] == ""
        assert parsley["note"] == "Some"

        # "2 tbsp" -> parsed correctly
        butter = inserted_ingredients[4]
        assert butter["name"] == "Butter"
        assert butter["quantity"] == 2.0
        assert butter["unit"] == "tbsp"


class TestForkRecipeImageUrl:
    """Tests for image URL handling during fork.

    Test 55: test_fork_recipe_copies_image_url
    """

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_copies_image_url(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe copies strMealThumb as image_url.

        Given: TheMealDB recipe with strMealThumb image URL
        When: fork_recipe(user_id, api_recipe_id)
        Then: image_url is set to TheMealDB strMealThumb URL
        Requirement: spec.md "Duplicate TheMealDB recipe as personal recipe"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "52772"
        created_recipe_id = "new-recipe-uuid"
        expected_image_url = (
            "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg"
        )

        # Mock TheMealDB API response
        mock_themealdb.get_by_id = AsyncMock(
            return_value={"meals": [SAMPLE_THEMEALDB_RECIPE]}
        )

        mock_client = MagicMock()
        inserted_recipe = []

        # Capture inserted recipe data
        def capture_recipe(data):
            inserted_recipe.append(data)
            response_data = {
                **data,
                "id": created_recipe_id,
                "created_at": "2026-01-03T10:00:00+00:00",
                "updated_at": "2026-01-03T10:00:00+00:00",
            }
            return MagicMock(
                execute=lambda: MockSupabaseResponse(data=[response_data])
            )

        mock_recipe_insert = MagicMock()
        mock_recipe_insert.insert.side_effect = capture_recipe

        # Other mocks
        mock_ingredients_insert = MagicMock()
        mock_ingredients_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )
        mock_steps_insert = MagicMock()
        mock_steps_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_insert,
                "personal_recipe_ingredients": mock_ingredients_insert,
                "personal_recipe_steps": mock_steps_insert,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = await service.fork_recipe(user_id, api_recipe_id)

        # Verify image_url was set
        assert inserted_recipe[0]["image_url"] == expected_image_url
        assert result.image_url == expected_image_url


class TestForkRecipeNotFound:
    """Tests for fork_recipe with invalid API recipe ID.

    Test 56: test_fork_recipe_api_recipe_not_found_returns_404
    """

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_api_recipe_not_found_raises_exception(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe raises exception when API recipe not found.

        Given: TheMealDB recipe with id "99999" does not exist
        When: fork_recipe(user_id, "99999")
        Then: Raises RecipeNotFoundError
        Requirement: spec.md "Fetch original recipe from TheMealDB API"
        """
        from app.services.personal_recipes_service import (
            PersonalRecipesService,
            RecipeNotFoundError,
        )

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "99999"

        # Mock TheMealDB API response - recipe not found
        mock_themealdb.get_by_id = AsyncMock(return_value={"meals": None})

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()

        with pytest.raises(RecipeNotFoundError) as exc_info:
            await service.fork_recipe(user_id, api_recipe_id)

        assert "99999" in str(exc_info.value)


class TestForkRecipeAPIError:
    """Tests for fork_recipe when TheMealDB API is unavailable.

    Test 58: test_fork_recipe_themealdb_api_error_returns_503
    """

    @pytest.mark.asyncio
    @patch("app.services.personal_recipes_service.get_supabase_admin")
    @patch("app.services.personal_recipes_service.themealdb_client")
    async def test_fork_recipe_api_error_raises_exception(
        self, mock_themealdb, mock_get_client
    ):
        """Test fork_recipe raises exception when TheMealDB API fails.

        Given: Authenticated user
               TheMealDB API is unavailable
        When: fork_recipe(user_id, "52772")
        Then: Raises ExternalAPIError
        Requirement: spec.md "Fetch original recipe from TheMealDB API"
        """
        from app.services.personal_recipes_service import (
            ExternalAPIError,
            PersonalRecipesService,
        )

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        api_recipe_id = "52772"

        # Mock TheMealDB API error
        mock_themealdb.get_by_id = AsyncMock(
            side_effect=Exception("Connection refused")
        )

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()

        with pytest.raises(ExternalAPIError) as exc_info:
            await service.fork_recipe(user_id, api_recipe_id)

        assert "unavailable" in str(exc_info.value).lower()


class TestIngredientParser:
    """Unit tests for the ingredient parsing helper functions."""

    def test_parse_measure_simple_number_and_unit(self):
        """Test parsing "2 cups" format."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("2 cups")
        assert qty == 2.0
        assert unit == "cups"
        assert note is None

    def test_parse_measure_fraction(self):
        """Test parsing "1/2 cup" format."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("1/2 cup")
        assert qty == 0.5
        assert unit == "cup"
        assert note is None

    def test_parse_measure_mixed_fraction(self):
        """Test parsing "1 1/2 cups" format."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("1 1/2 cups")
        assert qty == 1.5
        assert unit == "cups"
        assert note is None

    def test_parse_measure_no_space(self):
        """Test parsing "200g" format (no space between number and unit)."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("200g")
        assert qty == 200.0
        assert unit == "g"
        assert note is None

    def test_parse_measure_to_taste(self):
        """Test parsing "to taste" format (unparseable)."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("to taste")
        assert qty == 1.0
        assert unit == ""
        assert note == "to taste"

    def test_parse_measure_just_text(self):
        """Test parsing "Some" format (unparseable)."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("Some")
        assert qty == 1.0
        assert unit == ""
        assert note == "Some"

    def test_parse_measure_three_quarter(self):
        """Test parsing "3/4 cup" format."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("3/4 cup")
        assert qty == 0.75
        assert unit == "cup"
        assert note is None

    def test_parse_measure_cloves(self):
        """Test parsing "3 cloves" format."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("3 cloves")
        assert qty == 3.0
        assert unit == "cloves"
        assert note is None

    def test_parse_measure_empty_string(self):
        """Test parsing empty string."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("")
        assert qty == 1.0
        assert unit == ""
        assert note is None

    def test_parse_measure_whitespace_only(self):
        """Test parsing whitespace only."""
        from app.services.personal_recipes_service import _parse_measure

        qty, unit, note = _parse_measure("   ")
        assert qty == 1.0
        assert unit == ""
        assert note is None


class TestInstructionParser:
    """Unit tests for the instruction parsing helper functions."""

    def test_parse_instructions_newline_split(self):
        """Test splitting instructions by newlines."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "Step one.\nStep two.\nStep three."
        steps = _parse_instructions(text)
        assert len(steps) == 3
        assert steps[0] == "Step one."
        assert steps[1] == "Step two."
        assert steps[2] == "Step three."

    def test_parse_instructions_removes_empty_lines(self):
        """Test that empty lines are removed."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "Step one.\n\nStep two.\n\n\nStep three."
        steps = _parse_instructions(text)
        assert len(steps) == 3

    def test_parse_instructions_trims_whitespace(self):
        """Test that whitespace is trimmed from steps."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "  Step one.  \n  Step two.  "
        steps = _parse_instructions(text)
        assert steps[0] == "Step one."
        assert steps[1] == "Step two."

    def test_parse_instructions_numbered_pattern(self):
        """Test splitting instructions with numbered patterns like '1. Do this'."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "1. Do this. 2. Do that. 3. Finish."
        steps = _parse_instructions(text)
        assert len(steps) == 3
        assert steps[0] == "Do this."
        assert steps[1] == "Do that."
        assert steps[2] == "Finish."

    def test_parse_instructions_handles_carriage_returns(self):
        """Test handling of carriage returns."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "Step one.\r\nStep two.\r\nStep three."
        steps = _parse_instructions(text)
        assert len(steps) == 3

    def test_parse_instructions_single_step(self):
        """Test single instruction without newlines."""
        from app.services.personal_recipes_service import _parse_instructions

        text = "Just do this one thing."
        steps = _parse_instructions(text)
        assert len(steps) == 1
        assert steps[0] == "Just do this one thing."
