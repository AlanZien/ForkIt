"""Tests for personal recipe Pydantic models.

These tests validate the PersonalRecipeCreate, PersonalRecipeUpdate,
and response models following the Given-When-Then specifications from test-plan.md.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError


class TestIngredientCreate:
    """Tests for IngredientCreate model validation."""

    def test_valid_ingredient_creation(self):
        """Test creating a valid ingredient with all fields.

        Given: Valid ingredient data with name, quantity, unit, and note
        When: IngredientCreate is instantiated
        Then: All fields are correctly set
        """
        from app.models.personal_recipe import IngredientCreate

        ingredient = IngredientCreate(
            name="Farine",
            quantity=250.0,
            unit="g",
            note="type 55",
        )
        assert ingredient.name == "Farine"
        assert ingredient.quantity == 250.0
        assert ingredient.unit == "g"
        assert ingredient.note == "type 55"

    def test_ingredient_without_note(self):
        """Test that note field is optional.

        Given: Ingredient data without note
        When: IngredientCreate is instantiated
        Then: Ingredient is created with note=None
        """
        from app.models.personal_recipe import IngredientCreate

        ingredient = IngredientCreate(
            name="Oeufs",
            quantity=3,
            unit="pieces",
        )
        assert ingredient.note is None

    def test_ingredient_name_required(self):
        """Test that name is required.

        Given: Ingredient data missing name field
        When: IngredientCreate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                quantity=250.0,
                unit="g",
            )
        assert "name" in str(exc_info.value)

    def test_ingredient_name_min_length(self):
        """Test that name must have at least 1 character.

        Given: Ingredient data with empty name
        When: IngredientCreate is instantiated
        Then: ValidationError is raised for min_length
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="",
                quantity=250.0,
                unit="g",
            )
        assert "name" in str(exc_info.value)

    def test_ingredient_name_max_length(self):
        """Test that name cannot exceed 255 characters.

        Given: Ingredient data with name > 255 characters
        When: IngredientCreate is instantiated
        Then: ValidationError is raised for max_length
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="a" * 256,
                quantity=250.0,
                unit="g",
            )
        assert "name" in str(exc_info.value)

    def test_ingredient_quantity_must_be_positive(self):
        """Test that quantity must be greater than 0.

        Given: Ingredient data with quantity=0
        When: IngredientCreate is instantiated
        Then: ValidationError is raised for gt=0
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="Farine",
                quantity=0,
                unit="g",
            )
        assert "quantity" in str(exc_info.value)

    def test_ingredient_quantity_negative_rejected(self):
        """Test that negative quantity is rejected.

        Given: Ingredient data with negative quantity
        When: IngredientCreate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="Farine",
                quantity=-5,
                unit="g",
            )
        assert "quantity" in str(exc_info.value)

    def test_ingredient_unit_max_length(self):
        """Test that unit cannot exceed 50 characters.

        Given: Ingredient data with unit > 50 characters
        When: IngredientCreate is instantiated
        Then: ValidationError is raised for max_length
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="Farine",
                quantity=250.0,
                unit="u" * 51,
            )
        assert "unit" in str(exc_info.value)

    def test_ingredient_note_max_length(self):
        """Test that note cannot exceed 255 characters.

        Given: Ingredient data with note > 255 characters
        When: IngredientCreate is instantiated
        Then: ValidationError is raised for max_length
        """
        from app.models.personal_recipe import IngredientCreate

        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(
                name="Farine",
                quantity=250.0,
                unit="g",
                note="n" * 256,
            )
        assert "note" in str(exc_info.value)


class TestInstructionStepCreate:
    """Tests for InstructionStepCreate model validation."""

    def test_valid_instruction_step(self):
        """Test creating a valid instruction step.

        Given: Valid instruction data
        When: InstructionStepCreate is instantiated
        Then: Instruction field is correctly set
        """
        from app.models.personal_recipe import InstructionStepCreate

        step = InstructionStepCreate(instruction="Prechauffer le four a 180C")
        assert step.instruction == "Prechauffer le four a 180C"

    def test_instruction_required(self):
        """Test that instruction is required.

        Given: Step data missing instruction field
        When: InstructionStepCreate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import InstructionStepCreate

        with pytest.raises(ValidationError) as exc_info:
            InstructionStepCreate()
        assert "instruction" in str(exc_info.value)

    def test_instruction_min_length(self):
        """Test that instruction must have at least 1 character.

        Given: Step data with empty instruction
        When: InstructionStepCreate is instantiated
        Then: ValidationError is raised for min_length
        """
        from app.models.personal_recipe import InstructionStepCreate

        with pytest.raises(ValidationError) as exc_info:
            InstructionStepCreate(instruction="")
        assert "instruction" in str(exc_info.value)


class TestPersonalRecipeCreate:
    """Tests for PersonalRecipeCreate model validation.

    These tests cover API tests 23-28 from test-plan.md.
    """

    def test_valid_recipe_with_all_fields(self):
        """Test creating a valid recipe with all fields.

        Related: test_create_recipe_success_returns_201
        Given: Complete recipe data with all fields
        When: PersonalRecipeCreate is instantiated
        Then: All fields are correctly set
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        recipe = PersonalRecipeCreate(
            title="Tarte aux pommes",
            image_url="https://example.com/tarte.jpg",
            servings=6,
            prep_time_minutes=30,
            cook_time_minutes=45,
            tags=["dessert", "automne"],
            ingredients=[
                IngredientCreate(
                    name="Pommes", quantity=4, unit="pieces", note="Golden"
                ),
                IngredientCreate(name="Pate feuilletee", quantity=1, unit="rouleau"),
            ],
            steps=[
                InstructionStepCreate(instruction="Eplucher les pommes"),
                InstructionStepCreate(instruction="Derouler la pate"),
            ],
        )
        assert recipe.title == "Tarte aux pommes"
        assert recipe.image_url == "https://example.com/tarte.jpg"
        assert recipe.servings == 6
        assert recipe.prep_time_minutes == 30
        assert recipe.cook_time_minutes == 45
        assert recipe.tags == ["dessert", "automne"]
        assert len(recipe.ingredients) == 2
        assert len(recipe.steps) == 2

    def test_valid_recipe_with_minimal_fields(self):
        """Test creating a recipe with minimal required fields.

        Given: Recipe data with only required fields
        (title, servings, 1 ingredient, 1 step)
        When: PersonalRecipeCreate is instantiated
        Then: Recipe is created with optional fields as None
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        recipe = PersonalRecipeCreate(
            title="Simple Recipe",
            servings=2,
            ingredients=[
                IngredientCreate(name="Ingredient", quantity=1, unit="piece"),
            ],
            steps=[
                InstructionStepCreate(instruction="Do something"),
            ],
        )
        assert recipe.title == "Simple Recipe"
        assert recipe.servings == 2
        assert recipe.image_url is None
        assert recipe.prep_time_minutes is None
        assert recipe.cook_time_minutes is None
        assert recipe.tags is None

    def test_recipe_missing_title_raises_error(self):
        """Test that missing title raises validation error.

        Related: test_create_recipe_missing_title_returns_422 (test 23)
        Given: Recipe data missing required title field
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for title
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                servings=4,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "title" in str(exc_info.value)

    def test_recipe_missing_servings_raises_error(self):
        """Test that missing servings raises validation error.

        Related: test_create_recipe_missing_servings_returns_422 (test 24)
        Given: Recipe data with title but missing servings field
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for servings
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "servings" in str(exc_info.value)

    def test_recipe_servings_above_max_raises_error(self):
        """Test that servings > 20 raises validation error.

        Related: test_create_recipe_servings_out_of_range_returns_422 (test 25)
        Given: Recipe data with servings=25 (above max of 20)
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised with message about range
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=25,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "servings" in str(exc_info.value)

    def test_recipe_servings_zero_raises_error(self):
        """Test that servings=0 raises validation error.

        Related: test_create_recipe_servings_zero_returns_422 (test 26)
        Given: Recipe data with servings=0
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for servings >= 1
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=0,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "servings" in str(exc_info.value)

    def test_recipe_negative_servings_raises_error(self):
        """Test that negative servings raises validation error.

        Given: Recipe data with servings=-1
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=-1,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "servings" in str(exc_info.value)

    def test_recipe_empty_ingredients_raises_error(self):
        """Test that empty ingredients list raises validation error.

        Related: test_create_recipe_empty_ingredients_returns_422 (test 27)
        Given: Recipe data with ingredients=[]
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for min_length=1
        """
        from app.models.personal_recipe import (
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=4,
                ingredients=[],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "ingredients" in str(exc_info.value)

    def test_recipe_empty_steps_raises_error(self):
        """Test that empty steps list raises validation error.

        Related: test_create_recipe_empty_steps_returns_422 (test 28)
        Given: Recipe data with steps=[]
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for min_length=1
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=4,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[],
            )
        assert "steps" in str(exc_info.value)

    def test_recipe_title_min_length(self):
        """Test that title must have at least 1 character.

        Given: Recipe data with empty title
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for min_length
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="",
                servings=4,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "title" in str(exc_info.value)

    def test_recipe_title_max_length(self):
        """Test that title cannot exceed 255 characters.

        Given: Recipe data with title > 255 characters
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for max_length
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="t" * 256,
                servings=4,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "title" in str(exc_info.value)

    def test_recipe_image_url_max_length(self):
        """Test that image_url cannot exceed 500 characters.

        Given: Recipe data with image_url > 500 characters
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for max_length
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=4,
                image_url="https://example.com/" + "a" * 500,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "image_url" in str(exc_info.value)

    def test_recipe_prep_time_negative_raises_error(self):
        """Test that negative prep_time_minutes raises validation error.

        Given: Recipe data with prep_time_minutes=-1
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for ge=0
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=4,
                prep_time_minutes=-1,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "prep_time_minutes" in str(exc_info.value)

    def test_recipe_cook_time_negative_raises_error(self):
        """Test that negative cook_time_minutes raises validation error.

        Given: Recipe data with cook_time_minutes=-5
        When: PersonalRecipeCreate is instantiated
        Then: ValidationError is raised for ge=0
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeCreate(
                title="Test Recipe",
                servings=4,
                cook_time_minutes=-5,
                ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
                steps=[InstructionStepCreate(instruction="Step")],
            )
        assert "cook_time_minutes" in str(exc_info.value)

    def test_recipe_zero_prep_time_allowed(self):
        """Test that prep_time_minutes=0 is allowed.

        Given: Recipe data with prep_time_minutes=0
        When: PersonalRecipeCreate is instantiated
        Then: Recipe is created successfully
        """
        from app.models.personal_recipe import (
            IngredientCreate,
            InstructionStepCreate,
            PersonalRecipeCreate,
        )

        recipe = PersonalRecipeCreate(
            title="Test Recipe",
            servings=4,
            prep_time_minutes=0,
            ingredients=[IngredientCreate(name="Test", quantity=1, unit="g")],
            steps=[InstructionStepCreate(instruction="Step")],
        )
        assert recipe.prep_time_minutes == 0


class TestPersonalRecipeUpdate:
    """Tests for PersonalRecipeUpdate model validation.

    All fields are optional for partial updates.
    """

    def test_update_with_no_fields(self):
        """Test that update model accepts empty data.

        Given: Empty update data
        When: PersonalRecipeUpdate is instantiated
        Then: Model is created with all fields None
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        update = PersonalRecipeUpdate()
        assert update.title is None
        assert update.servings is None
        assert update.ingredients is None
        assert update.steps is None

    def test_update_with_title_only(self):
        """Test partial update with only title.

        Given: Update data with only title field
        When: PersonalRecipeUpdate is instantiated
        Then: Only title is set, other fields are None
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        update = PersonalRecipeUpdate(title="Updated Title")
        assert update.title == "Updated Title"
        assert update.servings is None

    def test_update_with_servings_only(self):
        """Test partial update with only servings.

        Given: Update data with only servings field
        When: PersonalRecipeUpdate is instantiated
        Then: Only servings is set
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        update = PersonalRecipeUpdate(servings=8)
        assert update.servings == 8
        assert update.title is None

    def test_update_servings_validation_still_applies(self):
        """Test that servings validation applies to update model.

        Related: test_update_recipe_invalid_servings_returns_422 (test 43)
        Given: Update data with invalid servings=-1
        When: PersonalRecipeUpdate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeUpdate(servings=-1)
        assert "servings" in str(exc_info.value)

    def test_update_servings_above_max_validation(self):
        """Test that servings > 20 is rejected in update.

        Given: Update data with servings=25
        When: PersonalRecipeUpdate is instantiated
        Then: ValidationError is raised
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeUpdate(servings=25)
        assert "servings" in str(exc_info.value)

    def test_update_with_ingredients(self):
        """Test update with new ingredients list.

        Related: test_update_recipe_replace_ingredients (test 39)
        Given: Update data with new ingredients list
        When: PersonalRecipeUpdate is instantiated
        Then: Ingredients are set correctly
        """
        from app.models.personal_recipe import IngredientCreate, PersonalRecipeUpdate

        update = PersonalRecipeUpdate(
            ingredients=[
                IngredientCreate(name="New Ingredient", quantity=2, unit="cups"),
            ]
        )
        assert len(update.ingredients) == 1
        assert update.ingredients[0].name == "New Ingredient"

    def test_update_with_steps(self):
        """Test update with new steps list.

        Related: test_update_recipe_replace_steps (test 40)
        Given: Update data with new steps list
        When: PersonalRecipeUpdate is instantiated
        Then: Steps are set correctly
        """
        from app.models.personal_recipe import (
            InstructionStepCreate,
            PersonalRecipeUpdate,
        )

        update = PersonalRecipeUpdate(
            steps=[
                InstructionStepCreate(instruction="New step 1"),
                InstructionStepCreate(instruction="New step 2"),
            ]
        )
        assert len(update.steps) == 2

    def test_update_empty_ingredients_allowed(self):
        """Test that empty ingredients list is NOT allowed in update (min_length).

        Given: Update data with empty ingredients list
        When: PersonalRecipeUpdate is instantiated
        Then: ValidationError is raised (if ingredients provided, must have 1+)
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        # Empty list is rejected because if you provide ingredients, need at least 1
        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeUpdate(ingredients=[])
        assert "ingredients" in str(exc_info.value)

    def test_update_empty_steps_allowed(self):
        """Test that empty steps list is NOT allowed in update (min_length).

        Given: Update data with empty steps list
        When: PersonalRecipeUpdate is instantiated
        Then: ValidationError is raised (if steps provided, must have at least 1)
        """
        from app.models.personal_recipe import PersonalRecipeUpdate

        with pytest.raises(ValidationError) as exc_info:
            PersonalRecipeUpdate(steps=[])
        assert "steps" in str(exc_info.value)


class TestIngredientResponse:
    """Tests for IngredientResponse model."""

    def test_valid_ingredient_response(self):
        """Test creating a valid ingredient response.

        Given: Complete ingredient response data
        When: IngredientResponse is instantiated
        Then: All fields including id and sort_order are set
        """
        from app.models.personal_recipe import IngredientResponse

        response = IngredientResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="Farine",
            quantity=250.0,
            unit="g",
            note="type 55",
            sort_order=1,
        )
        assert response.id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.name == "Farine"
        assert response.quantity == 250.0
        assert response.unit == "g"
        assert response.note == "type 55"
        assert response.sort_order == 1

    def test_ingredient_response_note_nullable(self):
        """Test that note can be None in response.

        Given: Ingredient response without note
        When: IngredientResponse is instantiated with note=None
        Then: Response is created successfully
        """
        from app.models.personal_recipe import IngredientResponse

        response = IngredientResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="Oeufs",
            quantity=3,
            unit="pieces",
            note=None,
            sort_order=2,
        )
        assert response.note is None


class TestInstructionStepResponse:
    """Tests for InstructionStepResponse model."""

    def test_valid_step_response(self):
        """Test creating a valid instruction step response.

        Given: Complete step response data
        When: InstructionStepResponse is instantiated
        Then: All fields including id and step_number are set
        """
        from app.models.personal_recipe import InstructionStepResponse

        response = InstructionStepResponse(
            id="550e8400-e29b-41d4-a716-446655440001",
            step_number=1,
            instruction="Prechauffer le four a 180C",
        )
        assert response.id == "550e8400-e29b-41d4-a716-446655440001"
        assert response.step_number == 1
        assert response.instruction == "Prechauffer le four a 180C"


class TestPersonalRecipeResponse:
    """Tests for PersonalRecipeResponse model."""

    def test_valid_recipe_response_with_all_fields(self):
        """Test creating a complete recipe response.

        Given: Complete recipe response data with nested ingredients and steps
        When: PersonalRecipeResponse is instantiated
        Then: All fields are correctly set including nested data
        """
        from app.models.personal_recipe import (
            IngredientResponse,
            InstructionStepResponse,
            PersonalRecipeResponse,
        )

        now = datetime.now()
        response = PersonalRecipeResponse(
            id="recipe-uuid-1",
            user_id="user-uuid-1",
            title="Tarte aux pommes",
            image_url="https://example.com/tarte.jpg",
            servings=6,
            prep_time_minutes=30,
            cook_time_minutes=45,
            tags=["dessert", "automne"],
            source_recipe_id=None,
            created_at=now,
            updated_at=now,
            ingredients=[
                IngredientResponse(
                    id="ing-1",
                    name="Pommes",
                    quantity=4,
                    unit="pieces",
                    note="Golden",
                    sort_order=1,
                ),
            ],
            steps=[
                InstructionStepResponse(
                    id="step-1",
                    step_number=1,
                    instruction="Eplucher les pommes",
                ),
            ],
        )
        assert response.id == "recipe-uuid-1"
        assert response.title == "Tarte aux pommes"
        assert len(response.ingredients) == 1
        assert len(response.steps) == 1
        assert response.source_recipe_id is None

    def test_recipe_response_with_source_recipe_id(self):
        """Test recipe response for forked recipe.

        Related: test_get_recipe_includes_source_recipe_id_for_forked (test 37)
        Given: Response data for forked recipe
        When: PersonalRecipeResponse is instantiated
        Then: source_recipe_id is correctly set
        """
        from app.models.personal_recipe import (
            IngredientResponse,
            InstructionStepResponse,
            PersonalRecipeResponse,
        )

        now = datetime.now()
        response = PersonalRecipeResponse(
            id="forked-recipe-uuid",
            user_id="user-uuid-1",
            title="Forked Recipe",
            image_url=None,
            servings=4,
            prep_time_minutes=None,
            cook_time_minutes=None,
            tags=None,
            source_recipe_id="themealdb-52772",
            created_at=now,
            updated_at=now,
            ingredients=[
                IngredientResponse(
                    id="ing-1",
                    name="Test",
                    quantity=1,
                    unit="g",
                    note=None,
                    sort_order=1,
                ),
            ],
            steps=[
                InstructionStepResponse(
                    id="step-1",
                    step_number=1,
                    instruction="Test",
                ),
            ],
        )
        assert response.source_recipe_id == "themealdb-52772"


class TestPersonalRecipeListResponse:
    """Tests for PersonalRecipeListResponse model."""

    def test_valid_list_response(self):
        """Test creating a list response.

        Given: List of recipe summaries and count
        When: PersonalRecipeListResponse is instantiated
        Then: List and count are correctly set
        """
        from app.models.personal_recipe import (
            PersonalRecipeListResponse,
            PersonalRecipeSummary,
        )

        summaries = [
            PersonalRecipeSummary(
                id="recipe-1",
                title="Recipe 1",
                image_url="https://example.com/1.jpg",
                source="personal",
            ),
            PersonalRecipeSummary(
                id="recipe-2",
                title="Recipe 2",
                image_url=None,
                source="personal",
            ),
        ]
        response = PersonalRecipeListResponse(recipes=summaries, count=2)
        assert len(response.recipes) == 2
        assert response.count == 2

    def test_empty_list_response(self):
        """Test empty list response.

        Related: test_list_recipes_empty_list (test 31)
        Given: Empty recipe list
        When: PersonalRecipeListResponse is instantiated
        Then: Response is created with empty list and count=0
        """
        from app.models.personal_recipe import PersonalRecipeListResponse

        response = PersonalRecipeListResponse(recipes=[], count=0)
        assert len(response.recipes) == 0
        assert response.count == 0


class TestPersonalRecipeSummary:
    """Tests for PersonalRecipeSummary model."""

    def test_valid_summary_for_personal_recipe(self):
        """Test creating a summary for personal recipe.

        Given: Summary data with source="personal"
        When: PersonalRecipeSummary is instantiated
        Then: All fields are set correctly
        """
        from app.models.personal_recipe import PersonalRecipeSummary

        summary = PersonalRecipeSummary(
            id="recipe-1",
            title="My Recipe",
            image_url="https://example.com/recipe.jpg",
            source="personal",
        )
        assert summary.id == "recipe-1"
        assert summary.title == "My Recipe"
        assert summary.image_url == "https://example.com/recipe.jpg"
        assert summary.source == "personal"

    def test_summary_with_api_source(self):
        """Test summary with API source for unified search.

        Related: test_search_returns_both_personal_and_api_recipes (test 59)
        Given: Summary data with source="api"
        When: PersonalRecipeSummary is instantiated
        Then: Source is correctly set to "api"
        """
        from app.models.personal_recipe import PersonalRecipeSummary

        summary = PersonalRecipeSummary(
            id="52772",
            title="API Recipe",
            image_url="https://themealdb.com/images/52772.jpg",
            source="api",
        )
        assert summary.source == "api"

    def test_summary_image_url_nullable(self):
        """Test that image_url is optional in summary.

        Given: Summary data without image_url
        When: PersonalRecipeSummary is instantiated
        Then: Summary is created with image_url=None
        """
        from app.models.personal_recipe import PersonalRecipeSummary

        summary = PersonalRecipeSummary(
            id="recipe-1",
            title="Recipe Without Image",
            image_url=None,
            source="personal",
        )
        assert summary.image_url is None
