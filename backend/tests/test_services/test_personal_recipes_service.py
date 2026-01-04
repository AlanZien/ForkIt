"""Tests for PersonalRecipesService - TDD approach.

These tests mock Supabase to test the personal recipes service logic.
Following test-plan.md specifications and tasks.md Task Group 4 requirements.
"""

import sys
from unittest.mock import MagicMock, patch

from app.models.personal_recipe import (
    IngredientCreate,
    InstructionStepCreate,
    PersonalRecipeCreate,
    PersonalRecipeResponse,
    PersonalRecipeSummary,
    PersonalRecipeUpdate,
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


class TestCreateRecipe:
    """Tests for create_recipe method.

    Task 4.3: Implement create_recipe method.
    """

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_create_recipe_with_valid_data_returns_response(
        self, mock_get_client
    ):
        """Test create_recipe with valid data returns PersonalRecipeResponse.

        Given: Authenticated user with user_id = "user-123"
               Valid recipe data with title, servings, 2 ingredients, 2 steps
        When: create_recipe(user_id, data)
        Then: Returns PersonalRecipeResponse with generated id and nested data
        Requirement: spec.md "POST /api/personal-recipes"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-uuid-123"

        mock_client = MagicMock()

        # Mock personal_recipes insert
        recipe_data = {
            "id": recipe_id,
            "user_id": user_id,
            "title": "Tarte aux pommes",
            "image_url": None,
            "servings": 6,
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "tags": ["dessert", "automne"],
            "source_recipe_id": None,
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
                "id": "ing-1",
                "recipe_id": recipe_id,
                "name": "Pommes",
                "quantity": 4.0,
                "unit": "pieces",
                "note": "Golden",
                "sort_order": 0,
            },
            {
                "id": "ing-2",
                "recipe_id": recipe_id,
                "name": "Pate feuilletee",
                "quantity": 1.0,
                "unit": "rouleau",
                "note": None,
                "sort_order": 1,
            },
        ]
        mock_ingredients_insert = MagicMock()
        mock_ingredients_insert.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=ingredients_data)
        )

        # Mock steps insert
        steps_data = [
            {
                "id": "step-1",
                "recipe_id": recipe_id,
                "step_number": 1,
                "instruction": "Eplucher les pommes",
            },
            {
                "id": "step-2",
                "recipe_id": recipe_id,
                "step_number": 2,
                "instruction": "Derouler la pate",
            },
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
        create_data = PersonalRecipeCreate(
            title="Tarte aux pommes",
            servings=6,
            prep_time_minutes=30,
            cook_time_minutes=45,
            tags=["dessert", "automne"],
            ingredients=[
                IngredientCreate(
                    name="Pommes", quantity=4, unit="pieces", note="Golden"
                ),
                IngredientCreate(
                    name="Pate feuilletee", quantity=1, unit="rouleau"
                ),
            ],
            steps=[
                InstructionStepCreate(instruction="Eplucher les pommes"),
                InstructionStepCreate(instruction="Derouler la pate"),
            ],
        )

        result = service.create_recipe(user_id, create_data)

        assert isinstance(result, PersonalRecipeResponse)
        assert result.id == recipe_id
        assert result.user_id == user_id
        assert result.title == "Tarte aux pommes"
        assert result.servings == 6
        assert len(result.ingredients) == 2
        assert len(result.steps) == 2
        assert result.ingredients[0].name == "Pommes"
        assert result.ingredients[0].sort_order == 0
        assert result.steps[0].step_number == 1

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_create_recipe_assigns_sort_order_and_step_numbers(
        self, mock_get_client
    ):
        """Test that create_recipe assigns correct sort_order and step_number.

        Given: Recipe with 3 ingredients and 3 steps
        When: create_recipe(user_id, data)
        Then: Ingredients have sort_order 0, 1, 2; steps have step_number 1, 2, 3
        Requirement: tasks.md "Insert ingredients with sort_order (enumerate)"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-uuid-123"

        mock_client = MagicMock()

        # Track inserted data
        inserted_ingredients = []
        inserted_steps = []

        # Mock personal_recipes insert
        recipe_data = {
            "id": recipe_id,
            "user_id": user_id,
            "title": "Test Recipe",
            "image_url": None,
            "servings": 4,
            "prep_time_minutes": None,
            "cook_time_minutes": None,
            "tags": None,
            "source_recipe_id": None,
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T10:00:00+00:00",
        }
        mock_recipe_query = MagicMock()
        mock_recipe_query.insert.return_value.execute.return_value = (
            MockSupabaseResponse(data=[recipe_data])
        )

        # Mock ingredients insert to capture data
        def capture_ingredients(data):
            inserted_ingredients.extend(data)
            return MagicMock(
                execute=lambda: MockSupabaseResponse(
                    data=[
                        {**ing, "id": f"ing-{i}"}
                        for i, ing in enumerate(data)
                    ]
                )
            )

        mock_ingredients_query = MagicMock()
        mock_ingredients_query.insert.side_effect = capture_ingredients

        # Mock steps insert to capture data
        def capture_steps(data):
            inserted_steps.extend(data)
            return MagicMock(
                execute=lambda: MockSupabaseResponse(
                    data=[
                        {**step, "id": f"step-{i}"}
                        for i, step in enumerate(data)
                    ]
                )
            )

        mock_steps_query = MagicMock()
        mock_steps_query.insert.side_effect = capture_steps

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_query,
                "personal_recipe_ingredients": mock_ingredients_query,
                "personal_recipe_steps": mock_steps_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        create_data = PersonalRecipeCreate(
            title="Test Recipe",
            servings=4,
            ingredients=[
                IngredientCreate(name="Ing A", quantity=1, unit="g"),
                IngredientCreate(name="Ing B", quantity=2, unit="ml"),
                IngredientCreate(name="Ing C", quantity=3, unit="pieces"),
            ],
            steps=[
                InstructionStepCreate(instruction="Step one"),
                InstructionStepCreate(instruction="Step two"),
                InstructionStepCreate(instruction="Step three"),
            ],
        )

        service.create_recipe(user_id, create_data)

        # Verify sort_order for ingredients (0-indexed)
        assert inserted_ingredients[0]["sort_order"] == 0
        assert inserted_ingredients[1]["sort_order"] == 1
        assert inserted_ingredients[2]["sort_order"] == 2

        # Verify step_number for steps (1-indexed)
        assert inserted_steps[0]["step_number"] == 1
        assert inserted_steps[1]["step_number"] == 2
        assert inserted_steps[2]["step_number"] == 3


class TestGetRecipes:
    """Tests for get_recipes method.

    Task 4.4: Implement get_recipes method.
    """

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipes_returns_user_recipes_only(self, mock_get_client):
        """Test that get_recipes returns only the user's recipes.

        Given: User A has 3 personal recipes
               Database contains recipes from other users too
        When: get_recipes(user_id)
        Then: Returns list of 3 PersonalRecipeSummary for user A only
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        recipes_data = [
            {
                "id": "recipe-1",
                "user_id": user_id,
                "title": "Recipe One",
                "image_url": "https://example.com/img1.jpg",
                "servings": 4,
                "prep_time_minutes": 15,
                "cook_time_minutes": 30,
                "tags": None,
                "source_recipe_id": None,
                "created_at": "2026-01-03T10:00:00+00:00",
                "updated_at": "2026-01-03T10:00:00+00:00",
            },
            {
                "id": "recipe-2",
                "user_id": user_id,
                "title": "Recipe Two",
                "image_url": None,
                "servings": 2,
                "prep_time_minutes": None,
                "cook_time_minutes": 20,
                "tags": ["quick"],
                "source_recipe_id": None,
                "created_at": "2026-01-02T10:00:00+00:00",
                "updated_at": "2026-01-02T10:00:00+00:00",
            },
            {
                "id": "recipe-3",
                "user_id": user_id,
                "title": "Recipe Three",
                "image_url": None,
                "servings": 6,
                "prep_time_minutes": 45,
                "cook_time_minutes": None,
                "tags": None,
                "source_recipe_id": "themealdb-12345",
                "created_at": "2026-01-01T10:00:00+00:00",
                "updated_at": "2026-01-01T10:00:00+00:00",
            },
        ]

        mock_query = MagicMock()
        mock_select = mock_query.select.return_value
        mock_eq = mock_select.eq.return_value
        mock_order = mock_eq.order.return_value
        mock_order.execute.return_value = MockSupabaseResponse(
            data=recipes_data
        )
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.get_recipes(user_id)

        assert len(result) == 3
        assert all(isinstance(r, PersonalRecipeSummary) for r in result)
        assert result[0].id == "recipe-1"
        assert result[0].title == "Recipe One"
        assert result[0].image_url == "https://example.com/img1.jpg"
        assert result[0].source == "personal"

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipes_orders_by_created_at_desc(self, mock_get_client):
        """Test that get_recipes orders results by created_at descending.

        Given: User has recipes created at different times
        When: get_recipes(user_id)
        Then: Supabase query uses order("created_at", desc=True)
        Requirement: tasks.md "Order by created_at DESC"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()
        mock_query = MagicMock()
        mock_order = MagicMock()
        mock_order.execute.return_value = MockSupabaseResponse(data=[])
        mock_query.select.return_value.eq.return_value.order.return_value = (
            mock_order
        )

        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        service.get_recipes(user_id)

        # Verify order was called with correct parameters
        mock_query.select.return_value.eq.return_value.order.assert_called_once_with(
            "created_at", desc=True
        )

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipes_empty_list_for_new_user(self, mock_get_client):
        """Test that get_recipes returns empty list for user with no recipes.

        Given: User with no personal recipes
        When: get_recipes(user_id)
        Then: Returns empty list
        Requirement: spec.md "GET /api/personal-recipes"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()
        mock_query = MagicMock()
        mock_select = mock_query.select.return_value
        mock_eq = mock_select.eq.return_value
        mock_order = mock_eq.order.return_value
        mock_order.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.get_recipes(user_id)

        assert result == []


class TestGetRecipeById:
    """Tests for get_recipe_by_id method.

    Task 4.5: Implement get_recipe_by_id method.
    """

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipe_by_id_returns_full_recipe(self, mock_get_client):
        """Test get_recipe_by_id returns full recipe with nested data.

        Given: User owns recipe "recipe-1" with 2 ingredients and 3 steps
        When: get_recipe_by_id(user_id, recipe_id)
        Then: Returns PersonalRecipeResponse with nested ingredients and steps
        Requirement: spec.md "GET /api/personal-recipes/{id} - Get single recipe"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-1"

        mock_client = MagicMock()

        recipe_data = {
            "id": recipe_id,
            "user_id": user_id,
            "title": "Ma Tarte",
            "image_url": "https://example.com/tarte.jpg",
            "servings": 8,
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "tags": ["dessert"],
            "source_recipe_id": None,
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T10:00:00+00:00",
        }

        ingredients_data = [
            {
                "id": "ing-1",
                "recipe_id": recipe_id,
                "name": "Farine",
                "quantity": 250.0,
                "unit": "g",
                "note": None,
                "sort_order": 0,
            },
            {
                "id": "ing-2",
                "recipe_id": recipe_id,
                "name": "Beurre",
                "quantity": 125.0,
                "unit": "g",
                "note": "froid",
                "sort_order": 1,
            },
        ]

        steps_data = [
            {
                "id": "step-1",
                "recipe_id": recipe_id,
                "step_number": 1,
                "instruction": "Melanger la farine",
            },
            {
                "id": "step-2",
                "recipe_id": recipe_id,
                "step_number": 2,
                "instruction": "Ajouter le beurre",
            },
            {
                "id": "step-3",
                "recipe_id": recipe_id,
                "step_number": 3,
                "instruction": "Former la pate",
            },
        ]

        # Mock recipe query
        mock_recipe_query = MagicMock()
        mock_sel = mock_recipe_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(
            data=[recipe_data]
        )

        # Mock ingredients query
        mock_ingredients_query = MagicMock()
        mock_ing_sel = mock_ingredients_query.select.return_value
        mock_ing_eq = mock_ing_sel.eq.return_value
        mock_ing_order = mock_ing_eq.order.return_value
        mock_ing_order.execute.return_value = MockSupabaseResponse(
            data=ingredients_data
        )

        # Mock steps query
        mock_steps_query = MagicMock()
        mock_steps_sel = mock_steps_query.select.return_value
        mock_steps_eq = mock_steps_sel.eq.return_value
        mock_steps_order = mock_steps_eq.order.return_value
        mock_steps_order.execute.return_value = MockSupabaseResponse(
            data=steps_data
        )

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_query,
                "personal_recipe_ingredients": mock_ingredients_query,
                "personal_recipe_steps": mock_steps_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.get_recipe_by_id(user_id, recipe_id)

        assert result is not None
        assert isinstance(result, PersonalRecipeResponse)
        assert result.id == recipe_id
        assert result.title == "Ma Tarte"
        assert len(result.ingredients) == 2
        assert len(result.steps) == 3
        assert result.ingredients[0].name == "Farine"
        assert result.ingredients[0].sort_order == 0
        assert result.steps[0].step_number == 1

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipe_by_id_not_found_returns_none(self, mock_get_client):
        """Test that get_recipe_by_id returns None for non-existent recipe.

        Given: Recipe "nonexistent-id" does not exist
        When: get_recipe_by_id(user_id, "nonexistent-id")
        Then: Returns None
        Requirement: spec.md "GET /api/personal-recipes/{id}"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "nonexistent-id"

        mock_client = MagicMock()
        mock_query = MagicMock()
        mock_sel = mock_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.get_recipe_by_id(user_id, recipe_id)

        assert result is None

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_get_recipe_by_id_other_user_returns_none(self, mock_get_client):
        """Test that get_recipe_by_id returns None for other user's recipe.

        Given: User A owns recipe "recipe-1"
               User B tries to access it
        When: get_recipe_by_id(user_b_id, "recipe-1")
        Then: Returns None (due to user_id filter)
        Requirement: tasks.md "Validate user_id matches (RLS backup)"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_b_id = "user-b-uuid"
        recipe_id = "recipe-1"

        mock_client = MagicMock()
        mock_query = MagicMock()
        # Query returns empty because user_id doesn't match
        mock_sel = mock_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.get_recipe_by_id(user_b_id, recipe_id)

        assert result is None


class TestUpdateRecipe:
    """Tests for update_recipe method.

    Task 4.6: Implement update_recipe method.
    """

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_update_recipe_updates_fields_and_returns_response(
        self, mock_get_client
    ):
        """Test update_recipe updates fields and returns updated response.

        Given: User owns recipe "recipe-1"
               Update data with new title and servings
        When: update_recipe(user_id, recipe_id, update_data)
        Then: Returns updated PersonalRecipeResponse
        Requirement: spec.md "PUT /api/personal-recipes/{id}"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-1"

        mock_client = MagicMock()

        # Recipe data for both ownership check and final get_recipe_by_id
        updated_recipe_data = {
            "id": recipe_id,
            "user_id": user_id,
            "title": "Updated Title",
            "image_url": None,
            "servings": 8,
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "tags": None,
            "source_recipe_id": None,
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T11:00:00+00:00",
        }

        # Mock for personal_recipes table - handles multiple operations
        mock_recipe_query = MagicMock()
        # For ownership check: .select().eq().eq().execute()
        mock_sel = mock_recipe_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(
            data=[updated_recipe_data]
        )
        # For update: .update().eq().execute()
        mock_upd = mock_recipe_query.update.return_value
        mock_upd_eq = mock_upd.eq.return_value
        mock_upd_eq.execute.return_value = MockSupabaseResponse(
            data=[updated_recipe_data]
        )

        # Mock ingredients query (empty for this test)
        mock_ingredients_query = MagicMock()
        mock_ing_sel = mock_ingredients_query.select.return_value
        mock_ing_eq = mock_ing_sel.eq.return_value
        mock_ing_order = mock_ing_eq.order.return_value
        mock_ing_order.execute.return_value = MockSupabaseResponse(data=[])

        # Mock steps query (empty for this test)
        mock_steps_query = MagicMock()
        mock_steps_sel = mock_steps_query.select.return_value
        mock_steps_eq = mock_steps_sel.eq.return_value
        mock_steps_order = mock_steps_eq.order.return_value
        mock_steps_order.execute.return_value = MockSupabaseResponse(data=[])

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_query,
                "personal_recipe_ingredients": mock_ingredients_query,
                "personal_recipe_steps": mock_steps_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        update_data = PersonalRecipeUpdate(title="Updated Title", servings=8)

        result = service.update_recipe(user_id, recipe_id, update_data)

        assert result is not None
        assert isinstance(result, PersonalRecipeResponse)
        assert result.title == "Updated Title"
        assert result.servings == 8

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_update_recipe_replaces_ingredients_when_provided(
        self, mock_get_client
    ):
        """Test update_recipe deletes old and inserts new ingredients.

        Given: Recipe with 3 existing ingredients
               Update with 2 new ingredients
        When: update_recipe(user_id, recipe_id, update_data)
        Then: Old ingredients deleted, new ingredients inserted
        Requirement: tasks.md "If ingredients provided: delete existing, insert new"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-1"

        mock_client = MagicMock()

        # Track operations
        delete_called = {"ingredients": False}
        insert_called = {"ingredients": False}

        # Recipe data
        recipe_data = {
            "id": recipe_id,
            "user_id": user_id,
            "title": "Test",
            "image_url": None,
            "servings": 4,
            "prep_time_minutes": None,
            "cook_time_minutes": None,
            "tags": None,
            "source_recipe_id": None,
            "created_at": "2026-01-03T10:00:00+00:00",
            "updated_at": "2026-01-03T11:00:00+00:00",
        }

        # Mock for personal_recipes table
        mock_recipe_query = MagicMock()
        mock_sel = mock_recipe_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(
            data=[recipe_data]
        )

        # New ingredients data
        new_ingredients_data = [
            {
                "id": "new-ing-1",
                "recipe_id": recipe_id,
                "name": "New Ing 1",
                "quantity": 1.0,
                "unit": "g",
                "note": None,
                "sort_order": 0,
            },
            {
                "id": "new-ing-2",
                "recipe_id": recipe_id,
                "name": "New Ing 2",
                "quantity": 2.0,
                "unit": "ml",
                "note": None,
                "sort_order": 1,
            },
        ]

        # Mock ingredients operations
        mock_ingredients_query = MagicMock()

        def mock_ing_delete():
            delete_called["ingredients"] = True
            return MagicMock(
                eq=lambda *args: MagicMock(
                    execute=lambda: MockSupabaseResponse(data=[])
                )
            )

        def mock_ing_insert(data):
            insert_called["ingredients"] = True
            return MagicMock(
                execute=lambda: MockSupabaseResponse(
                    data=new_ingredients_data
                )
            )

        mock_ingredients_query.delete.side_effect = mock_ing_delete
        mock_ingredients_query.insert.side_effect = mock_ing_insert
        # For get_recipe_by_id at the end
        mock_ing_sel = mock_ingredients_query.select.return_value
        mock_ing_eq = mock_ing_sel.eq.return_value
        mock_ing_order = mock_ing_eq.order.return_value
        mock_ing_order.execute.return_value = MockSupabaseResponse(
            data=new_ingredients_data
        )

        # Mock steps query (empty)
        mock_steps_query = MagicMock()
        mock_steps_sel = mock_steps_query.select.return_value
        mock_steps_eq = mock_steps_sel.eq.return_value
        mock_steps_order = mock_steps_eq.order.return_value
        mock_steps_order.execute.return_value = MockSupabaseResponse(data=[])

        def table_side_effect(table_name):
            table_mocks = {
                "personal_recipes": mock_recipe_query,
                "personal_recipe_ingredients": mock_ingredients_query,
                "personal_recipe_steps": mock_steps_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        update_data = PersonalRecipeUpdate(
            ingredients=[
                IngredientCreate(name="New Ing 1", quantity=1, unit="g"),
                IngredientCreate(name="New Ing 2", quantity=2, unit="ml"),
            ]
        )

        result = service.update_recipe(user_id, recipe_id, update_data)

        assert delete_called["ingredients"] is True
        assert insert_called["ingredients"] is True
        assert len(result.ingredients) == 2

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_update_recipe_not_owned_returns_none(self, mock_get_client):
        """Test that update_recipe returns None for unowned recipe.

        Given: User B tries to update User A's recipe
        When: update_recipe(user_b_id, recipe_id, update_data)
        Then: Returns None (ownership check fails)
        Requirement: tasks.md "Verify ownership first"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_b_id = "user-b-uuid"
        recipe_id = "recipe-1"

        mock_client = MagicMock()
        mock_query = MagicMock()
        # Ownership check returns empty
        mock_sel = mock_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        update_data = PersonalRecipeUpdate(title="Hacked Title")

        result = service.update_recipe(user_b_id, recipe_id, update_data)

        assert result is None


class TestDeleteRecipe:
    """Tests for delete_recipe method.

    Task 4.7: Implement delete_recipe method.
    """

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_delete_recipe_success_returns_true(self, mock_get_client):
        """Test that delete_recipe returns True on success.

        Given: User owns recipe "recipe-1"
        When: delete_recipe(user_id, recipe_id)
        Then: Returns True, recipe is deleted
        Requirement: spec.md "DELETE /api/personal-recipes/{id}"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "recipe-1"

        mock_client = MagicMock()

        # Mock for personal_recipes table
        mock_recipe_query = MagicMock()
        # For ownership check: .select().eq().eq().execute()
        mock_sel = mock_recipe_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(
            data=[{"id": recipe_id, "user_id": user_id}]
        )
        # For delete: .delete().eq().execute()
        mock_del = mock_recipe_query.delete.return_value
        mock_del_eq = mock_del.eq.return_value
        mock_del_eq.execute.return_value = MockSupabaseResponse(
            data=[{"id": recipe_id}]
        )

        mock_client.table.return_value = mock_recipe_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.delete_recipe(user_id, recipe_id)

        assert result is True

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_delete_recipe_not_owned_returns_false(self, mock_get_client):
        """Test that delete_recipe returns False for unowned recipe.

        Given: User B tries to delete User A's recipe
        When: delete_recipe(user_b_id, recipe_id)
        Then: Returns False (ownership check fails)
        Requirement: tasks.md "Verify ownership"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_b_id = "user-b-uuid"
        recipe_id = "recipe-1"

        mock_client = MagicMock()
        mock_query = MagicMock()
        # Ownership check returns empty
        mock_sel = mock_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.delete_recipe(user_b_id, recipe_id)

        assert result is False

    @patch("app.services.personal_recipes_service.get_supabase_admin")
    def test_delete_recipe_not_found_returns_false(self, mock_get_client):
        """Test that delete_recipe returns False for non-existent recipe.

        Given: Recipe "nonexistent-id" does not exist
        When: delete_recipe(user_id, "nonexistent-id")
        Then: Returns False
        Requirement: spec.md "DELETE /api/personal-recipes/{id}"
        """
        from app.services.personal_recipes_service import PersonalRecipesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"
        recipe_id = "nonexistent-id"

        mock_client = MagicMock()
        mock_query = MagicMock()
        # Recipe not found
        mock_sel = mock_query.select.return_value
        mock_eq1 = mock_sel.eq.return_value
        mock_eq2 = mock_eq1.eq.return_value
        mock_eq2.execute.return_value = MockSupabaseResponse(data=[])
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PersonalRecipesService()
        result = service.delete_recipe(user_id, recipe_id)

        assert result is False
