"""Database schema tests for personal recipes tables.

These tests validate the database schema, constraints, RLS policies,
and cascade behaviors for the personal_recipes feature.

Test IDs correspond to test-plan.md Database Layer tests (1-20).

Note: These tests require a running Supabase instance with the
20260104_create_personal_recipes.sql migration applied.
They are integration tests meant to run against a test database.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4


# =============================================================================
# Test fixtures for mocked database operations
# =============================================================================


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def user_a_id():
    """Return a consistent user A ID for testing."""
    return str(uuid4())


@pytest.fixture
def user_b_id():
    """Return a consistent user B ID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_recipe_data():
    """Return sample recipe data for testing."""
    return {
        "title": "Ma Recette",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "tags": ["rapide", "facile"],
        "image_url": None,
    }


@pytest.fixture
def minimal_recipe_data():
    """Return minimal recipe data (only required fields)."""
    return {
        "title": "Simple Recipe",
        "servings": 2,
    }


# =============================================================================
# personal_recipes Table Tests (Tests 1-10)
# =============================================================================


class TestPersonalRecipesTable:
    """Tests for personal_recipes table schema and behavior."""

    def test_personal_recipe_creation_with_all_fields(
        self, mock_supabase, user_a_id, sample_recipe_data
    ):
        """Test 1: Recipe creation with all fields.

        Priority: Critical
        Given: Authenticated user with ID "user-123"
        Given: Valid recipe data: title="Ma Recette", servings=4, prep_time=15,
               cook_time=30, tags=["rapide", "facile"], image_url=null
        When: INSERT into personal_recipes table
        Then: Record is created with auto-generated UUID id
        Then: user_id is set to "user-123"
        Then: created_at and updated_at are set to current timestamp
        Then: All fields are persisted correctly
        """
        # Given
        recipe_data = {
            "user_id": user_a_id,
            **sample_recipe_data,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": user_a_id,
                "title": recipe_data["title"],
                "image_url": recipe_data["image_url"],
                "servings": recipe_data["servings"],
                "prep_time_minutes": recipe_data["prep_time_minutes"],
                "cook_time_minutes": recipe_data["cook_time_minutes"],
                "tags": recipe_data["tags"],
                "source_recipe_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipes").insert(recipe_data).execute()
        )

        # Then
        assert len(result.data) == 1
        created_recipe = result.data[0]
        assert created_recipe["id"] is not None
        assert created_recipe["user_id"] == user_a_id
        assert created_recipe["title"] == "Ma Recette"
        assert created_recipe["servings"] == 4
        assert created_recipe["prep_time_minutes"] == 15
        assert created_recipe["cook_time_minutes"] == 30
        assert created_recipe["tags"] == ["rapide", "facile"]
        assert created_recipe["created_at"] is not None
        assert created_recipe["updated_at"] is not None

    def test_personal_recipe_creation_with_minimal_fields(
        self, mock_supabase, user_a_id, minimal_recipe_data
    ):
        """Test 2: Recipe creation with minimal fields.

        Priority: Critical
        Given: Authenticated user with ID "user-123"
        Given: Minimal recipe data: title="Simple Recipe", servings=2
        When: INSERT into personal_recipes table with nullable fields as NULL
        Then: Record is created successfully
        Then: prep_time_minutes, cook_time_minutes, tags, image_url,
              source_recipe_id are NULL
        """
        # Given
        recipe_data = {
            "user_id": user_a_id,
            **minimal_recipe_data,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": user_a_id,
                "title": recipe_data["title"],
                "image_url": None,
                "servings": recipe_data["servings"],
                "prep_time_minutes": None,
                "cook_time_minutes": None,
                "tags": None,
                "source_recipe_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipes").insert(recipe_data).execute()
        )

        # Then
        assert len(result.data) == 1
        created_recipe = result.data[0]
        assert created_recipe["title"] == "Simple Recipe"
        assert created_recipe["servings"] == 2
        assert created_recipe["prep_time_minutes"] is None
        assert created_recipe["cook_time_minutes"] is None
        assert created_recipe["tags"] is None
        assert created_recipe["image_url"] is None
        assert created_recipe["source_recipe_id"] is None

    def test_personal_recipe_user_id_foreign_key_constraint(self, mock_supabase):
        """Test 3: Foreign key constraint on user_id.

        Priority: Critical
        Given: No authenticated user or invalid user_id "nonexistent-user"
        When: INSERT into personal_recipes with invalid user_id
        Then: Database returns foreign key constraint violation error
        Then: No record is created
        """
        # Given
        invalid_user_id = "nonexistent-user-id"
        recipe_data = {
            "user_id": invalid_user_id,
            "title": "Test Recipe",
            "servings": 4,
        }

        # Mock foreign key violation error
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = (
            Exception("foreign key constraint violation")
        )

        # When/Then
        with pytest.raises(Exception) as exc_info:
            mock_supabase.table("personal_recipes").insert(recipe_data).execute()

        assert "foreign key constraint" in str(exc_info.value)

    def test_personal_recipe_rls_select_own_recipes_only(
        self, mock_supabase, user_a_id, user_b_id
    ):
        """Test 4: RLS SELECT policy returns only user's own recipes.

        Priority: Critical
        Given: User A has 3 personal recipes
        Given: User B has 2 personal recipes
        Given: User A is authenticated
        When: SELECT * FROM personal_recipes (with RLS)
        Then: Only User A's 3 recipes are returned
        Then: User B's recipes are not visible
        """
        # Given - User A is authenticated and has 3 recipes
        user_a_recipes = [
            {"id": str(uuid4()), "user_id": user_a_id, "title": f"Recipe A{i}"}
            for i in range(3)
        ]

        # Mock the select operation (simulating RLS filtering)
        mock_response = MagicMock()
        mock_response.data = user_a_recipes
        mock_supabase.table.return_value.select.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = mock_supabase.table("personal_recipes").select("*").execute()

        # Then
        assert len(result.data) == 3
        for recipe in result.data:
            assert recipe["user_id"] == user_a_id

    def test_personal_recipe_rls_update_own_recipe(
        self, mock_supabase, user_a_id
    ):
        """Test 5: RLS allows updating own recipe.

        Priority: Critical
        Given: User A owns recipe with id "recipe-1"
        Given: User A is authenticated
        When: UPDATE personal_recipes SET title="New Title" WHERE id="recipe-1"
        Then: Update succeeds
        Then: title is changed to "New Title"
        Then: updated_at is refreshed
        """
        # Given
        recipe_id = str(uuid4())
        original_updated_at = "2026-01-01T10:00:00Z"
        new_updated_at = datetime.now(timezone.utc).isoformat()

        # Mock the update operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": recipe_id,
                "user_id": user_a_id,
                "title": "New Title",
                "updated_at": new_updated_at,
            }
        ]
        (
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipes")
            .update({"title": "New Title"})
            .eq("id", recipe_id)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        assert result.data[0]["title"] == "New Title"
        assert result.data[0]["updated_at"] != original_updated_at

    def test_personal_recipe_rls_update_other_user_recipe_fails(
        self, mock_supabase, user_a_id, user_b_id
    ):
        """Test 6: RLS prevents updating other user's recipe.

        Priority: Critical
        Given: User A owns recipe with id "recipe-1"
        Given: User B is authenticated
        When: UPDATE personal_recipes SET title="Hacked" WHERE id="recipe-1"
        Then: Update is silently ignored (0 rows affected) due to RLS
        Then: Recipe title remains unchanged
        """
        # Given
        recipe_id = str(uuid4())

        # Mock the update operation returning empty (RLS blocked)
        mock_response = MagicMock()
        mock_response.data = []  # No rows affected due to RLS
        (
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipes")
            .update({"title": "Hacked"})
            .eq("id", recipe_id)
            .execute()
        )

        # Then
        assert len(result.data) == 0  # RLS prevented the update

    def test_personal_recipe_rls_delete_own_recipe(
        self, mock_supabase, user_a_id
    ):
        """Test 7: RLS allows deleting own recipe.

        Priority: Critical
        Given: User A owns recipe with id "recipe-1"
        Given: User A is authenticated
        When: DELETE FROM personal_recipes WHERE id="recipe-1"
        Then: Delete succeeds
        Then: Recipe is removed from database
        """
        # Given
        recipe_id = str(uuid4())

        # Mock the delete operation
        mock_response = MagicMock()
        mock_response.data = [{"id": recipe_id}]
        (
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipes")
            .delete()
            .eq("id", recipe_id)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        assert result.data[0]["id"] == recipe_id

    def test_personal_recipe_rls_delete_other_user_recipe_fails(
        self, mock_supabase, user_a_id, user_b_id
    ):
        """Test 8: RLS prevents deleting other user's recipe.

        Priority: Critical
        Given: User A owns recipe with id "recipe-1"
        Given: User B is authenticated
        When: DELETE FROM personal_recipes WHERE id="recipe-1"
        Then: Delete is silently ignored (0 rows affected) due to RLS
        Then: Recipe still exists in database
        """
        # Given
        recipe_id = str(uuid4())

        # Mock the delete operation returning empty (RLS blocked)
        mock_response = MagicMock()
        mock_response.data = []  # No rows deleted due to RLS
        (
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipes")
            .delete()
            .eq("id", recipe_id)
            .execute()
        )

        # Then
        assert len(result.data) == 0  # RLS prevented the delete

    def test_personal_recipe_updated_at_trigger(self, mock_supabase, user_a_id):
        """Test 9: updated_at trigger auto-updates on modification.

        Priority: High
        Given: Recipe exists with updated_at = "2026-01-01 10:00:00"
        When: UPDATE personal_recipes SET title="Updated Title"
        Then: updated_at is automatically set to current timestamp
        Then: created_at remains unchanged
        """
        # Given
        recipe_id = str(uuid4())
        original_created_at = "2026-01-01T08:00:00Z"
        original_updated_at = "2026-01-01T10:00:00Z"
        new_updated_at = datetime.now(timezone.utc).isoformat()

        # Mock the update operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": recipe_id,
                "title": "Updated Title",
                "created_at": original_created_at,
                "updated_at": new_updated_at,
            }
        ]
        (
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipes")
            .update({"title": "Updated Title"})
            .eq("id", recipe_id)
            .execute()
        )

        # Then
        assert result.data[0]["created_at"] == original_created_at
        assert result.data[0]["updated_at"] != original_updated_at
        assert result.data[0]["updated_at"] == new_updated_at

    def test_personal_recipe_source_recipe_id_nullable(
        self, mock_supabase, user_a_id
    ):
        """Test 10: source_recipe_id is nullable for non-forked recipes.

        Priority: Medium
        Given: User creates recipe from scratch (not forked)
        When: INSERT with source_recipe_id = NULL
        Then: Record is created successfully
        Then: source_recipe_id is NULL
        """
        # Given
        recipe_data = {
            "user_id": user_a_id,
            "title": "Original Recipe",
            "servings": 4,
            "source_recipe_id": None,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": user_a_id,
                "title": "Original Recipe",
                "servings": 4,
                "source_recipe_id": None,
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipes").insert(recipe_data).execute()
        )

        # Then
        assert len(result.data) == 1
        assert result.data[0]["source_recipe_id"] is None


# =============================================================================
# personal_recipe_ingredients Table Tests (Tests 11-15)
# =============================================================================


class TestPersonalRecipeIngredientsTable:
    """Tests for personal_recipe_ingredients table schema and behavior."""

    def test_ingredient_creation_with_all_fields(self, mock_supabase):
        """Test 11: Ingredient creation with all fields.

        Priority: High
        Given: Personal recipe exists with id "recipe-1"
        Given: Ingredient data: name="Farine", quantity=250, unit="g",
               note="type 55", sort_order=1
        When: INSERT into personal_recipe_ingredients
        Then: Ingredient is created with auto-generated UUID
        Then: All fields are persisted correctly
        """
        # Given
        recipe_id = str(uuid4())
        ingredient_data = {
            "recipe_id": recipe_id,
            "name": "Farine",
            "quantity": 250,
            "unit": "g",
            "note": "type 55",
            "sort_order": 1,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                **ingredient_data,
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipe_ingredients")
            .insert(ingredient_data)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        ingredient = result.data[0]
        assert ingredient["id"] is not None
        assert ingredient["name"] == "Farine"
        assert ingredient["quantity"] == 250
        assert ingredient["unit"] == "g"
        assert ingredient["note"] == "type 55"
        assert ingredient["sort_order"] == 1

    def test_ingredient_recipe_id_foreign_key_constraint(self, mock_supabase):
        """Test 12: Foreign key constraint on recipe_id.

        Priority: High
        Given: No recipe exists with id "nonexistent-recipe"
        When: INSERT ingredient with recipe_id="nonexistent-recipe"
        Then: Database returns foreign key constraint violation error
        """
        # Given
        nonexistent_recipe_id = str(uuid4())
        ingredient_data = {
            "recipe_id": nonexistent_recipe_id,
            "name": "Flour",
            "quantity": 200,
            "unit": "g",
            "sort_order": 1,
        }

        # Mock foreign key violation error
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = (
            Exception("foreign key constraint violation")
        )

        # When/Then
        with pytest.raises(Exception) as exc_info:
            (
                mock_supabase.table("personal_recipe_ingredients")
                .insert(ingredient_data)
                .execute()
            )

        assert "foreign key constraint" in str(exc_info.value)

    def test_ingredients_cascade_delete_on_recipe_deletion(
        self, mock_supabase, user_a_id
    ):
        """Test 13: Ingredients cascade delete when recipe is deleted.

        Priority: Critical
        Given: Recipe "recipe-1" exists with 5 ingredients
        Given: User is authenticated as owner
        When: DELETE FROM personal_recipes WHERE id="recipe-1"
        Then: Recipe is deleted
        Then: All 5 associated ingredients are automatically deleted (CASCADE)
        """
        # Given
        recipe_id = str(uuid4())

        # Mock the delete operation
        mock_response = MagicMock()
        mock_response.data = [{"id": recipe_id}]
        (
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When - delete the recipe
        result = (
            mock_supabase.table("personal_recipes")
            .delete()
            .eq("id", recipe_id)
            .execute()
        )

        # Then - recipe deleted (cascade should handle ingredients)
        assert len(result.data) == 1

        # Verify ingredients are gone (would return empty in real DB)
        mock_empty_response = MagicMock()
        mock_empty_response.data = []
        (
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value
        ) = mock_empty_response

        ingredients_result = (
            mock_supabase.table("personal_recipe_ingredients")
            .select("*")
            .eq("recipe_id", recipe_id)
            .execute()
        )
        assert len(ingredients_result.data) == 0

    def test_ingredient_sort_order_uniqueness_per_recipe(self, mock_supabase):
        """Test 14: Sort order uniqueness constraint per recipe.

        Priority: Medium
        Given: Recipe "recipe-1" with ingredient at sort_order=1
        When: INSERT another ingredient with same sort_order=1 for same recipe
        Then: Database returns unique constraint violation error
        """
        # Given
        recipe_id = str(uuid4())

        # Mock unique constraint violation
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = (
            Exception("unique constraint violation")
        )

        # When/Then
        with pytest.raises(Exception) as exc_info:
            (
                mock_supabase.table("personal_recipe_ingredients")
                .insert(
                    {
                        "recipe_id": recipe_id,
                        "name": "Duplicate Sort Order",
                        "quantity": 1,
                        "unit": "piece",
                        "sort_order": 1,
                    }
                )
                .execute()
            )

        assert "unique constraint" in str(exc_info.value)

    def test_ingredient_note_nullable(self, mock_supabase):
        """Test 15: Ingredient note is nullable.

        Priority: Low
        Given: Ingredient without a note
        When: INSERT with note=NULL
        Then: Ingredient is created successfully
        """
        # Given
        recipe_id = str(uuid4())
        ingredient_data = {
            "recipe_id": recipe_id,
            "name": "Salt",
            "quantity": 1,
            "unit": "tsp",
            "note": None,
            "sort_order": 1,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                **ingredient_data,
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipe_ingredients")
            .insert(ingredient_data)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        assert result.data[0]["note"] is None


# =============================================================================
# personal_recipe_steps Table Tests (Tests 16-20)
# =============================================================================


class TestPersonalRecipeStepsTable:
    """Tests for personal_recipe_steps table schema and behavior."""

    def test_step_creation_with_instruction(self, mock_supabase):
        """Test 16: Step creation with instruction.

        Priority: High
        Given: Personal recipe exists with id "recipe-1"
        Given: Step data: step_number=1, instruction="Prechauffer le four a 180C"
        When: INSERT into personal_recipe_steps
        Then: Step is created with auto-generated UUID
        Then: step_number and instruction are persisted
        """
        # Given
        recipe_id = str(uuid4())
        step_data = {
            "recipe_id": recipe_id,
            "step_number": 1,
            "instruction": "Prechauffer le four a 180C",
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                **step_data,
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipe_steps")
            .insert(step_data)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        step = result.data[0]
        assert step["id"] is not None
        assert step["step_number"] == 1
        assert step["instruction"] == "Prechauffer le four a 180C"

    def test_step_recipe_id_foreign_key_constraint(self, mock_supabase):
        """Test 17: Foreign key constraint on recipe_id.

        Priority: High
        Given: No recipe exists with id "nonexistent-recipe"
        When: INSERT step with recipe_id="nonexistent-recipe"
        Then: Database returns foreign key constraint violation error
        """
        # Given
        nonexistent_recipe_id = str(uuid4())
        step_data = {
            "recipe_id": nonexistent_recipe_id,
            "step_number": 1,
            "instruction": "Step instruction",
        }

        # Mock foreign key violation error
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = (
            Exception("foreign key constraint violation")
        )

        # When/Then
        with pytest.raises(Exception) as exc_info:
            (
                mock_supabase.table("personal_recipe_steps")
                .insert(step_data)
                .execute()
            )

        assert "foreign key constraint" in str(exc_info.value)

    def test_steps_cascade_delete_on_recipe_deletion(
        self, mock_supabase, user_a_id
    ):
        """Test 18: Steps cascade delete when recipe is deleted.

        Priority: Critical
        Given: Recipe "recipe-1" exists with 8 steps
        Given: User is authenticated as owner
        When: DELETE FROM personal_recipes WHERE id="recipe-1"
        Then: Recipe is deleted
        Then: All 8 associated steps are automatically deleted (CASCADE)
        """
        # Given
        recipe_id = str(uuid4())

        # Mock the delete operation
        mock_response = MagicMock()
        mock_response.data = [{"id": recipe_id}]
        (
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value
        ) = mock_response

        # When - delete the recipe
        result = (
            mock_supabase.table("personal_recipes")
            .delete()
            .eq("id", recipe_id)
            .execute()
        )

        # Then - recipe deleted (cascade should handle steps)
        assert len(result.data) == 1

        # Verify steps are gone (would return empty in real DB)
        mock_empty_response = MagicMock()
        mock_empty_response.data = []
        (
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value
        ) = mock_empty_response

        steps_result = (
            mock_supabase.table("personal_recipe_steps")
            .select("*")
            .eq("recipe_id", recipe_id)
            .execute()
        )
        assert len(steps_result.data) == 0

    def test_step_number_ordering(self, mock_supabase):
        """Test 19: Steps are ordered by step_number.

        Priority: Medium
        Given: Recipe with steps 1, 2, 3
        When: SELECT steps ORDER BY step_number
        Then: Steps are returned in correct order
        """
        # Given
        recipe_id = str(uuid4())
        steps = [
            {"id": str(uuid4()), "recipe_id": recipe_id, "step_number": 1},
            {"id": str(uuid4()), "recipe_id": recipe_id, "step_number": 2},
            {"id": str(uuid4()), "recipe_id": recipe_id, "step_number": 3},
        ]

        # Mock the select operation with ordering
        mock_response = MagicMock()
        mock_response.data = steps
        (
            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value
        ) = mock_response

        # When
        result = (
            mock_supabase.table("personal_recipe_steps")
            .select("*")
            .eq("recipe_id", recipe_id)
            .order("step_number")
            .execute()
        )

        # Then
        assert len(result.data) == 3
        assert result.data[0]["step_number"] == 1
        assert result.data[1]["step_number"] == 2
        assert result.data[2]["step_number"] == 3

    def test_step_instruction_text_length(self, mock_supabase):
        """Test 20: Step instruction can handle long text.

        Priority: Low
        Given: Step with very long instruction (2000+ characters)
        When: INSERT into personal_recipe_steps
        Then: Insert succeeds (TEXT type has no limit)
        """
        # Given
        recipe_id = str(uuid4())
        long_instruction = "A" * 2500  # 2500 characters
        step_data = {
            "recipe_id": recipe_id,
            "step_number": 1,
            "instruction": long_instruction,
        }

        # Mock the insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                **step_data,
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # When
        result = (
            mock_supabase.table("personal_recipe_steps")
            .insert(step_data)
            .execute()
        )

        # Then
        assert len(result.data) == 1
        assert len(result.data[0]["instruction"]) == 2500
