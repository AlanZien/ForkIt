"""Service for managing user personal recipes.

This service handles CRUD operations for personal recipes,
including nested ingredients and instruction steps.
Also supports forking recipes from TheMealDB API.
"""

import re

from app.models.personal_recipe import (
    IngredientCreate,
    IngredientResponse,
    InstructionStepCreate,
    InstructionStepResponse,
    PersonalRecipeCreate,
    PersonalRecipeResponse,
    PersonalRecipeSummary,
    PersonalRecipeUpdate,
)
from app.services.supabase import get_supabase_admin
from app.services.themealdb import themealdb_client


class RecipeNotFoundError(Exception):
    """Raised when a recipe is not found in TheMealDB API."""

    pass


class ExternalAPIError(Exception):
    """Raised when TheMealDB API is unavailable or returns an error."""

    pass


def _parse_fraction(text: str) -> float | None:
    """Parse a fraction string like '1/2' or '3/4' to float.

    Args:
        text: Fraction string

    Returns:
        Float value or None if not a valid fraction
    """
    if "/" in text:
        parts = text.split("/")
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                return None
    return None


def _parse_measure(measure: str) -> tuple[float, str, str | None]:
    """Parse a TheMealDB measure string into quantity, unit, and optional note.

    Handles formats:
    - "2 cups" -> (2.0, "cups", None)
    - "1/2 cup" -> (0.5, "cup", None)
    - "1 1/2 cups" -> (1.5, "cups", None)
    - "200g" -> (200.0, "g", None)
    - "to taste" -> (1.0, "", "to taste")
    - "Some" -> (1.0, "", "Some")
    - "" -> (1.0, "", None)

    Args:
        measure: The measure string from TheMealDB

    Returns:
        Tuple of (quantity, unit, note)
    """
    measure = measure.strip()

    # Handle empty or whitespace
    if not measure:
        return (1.0, "", None)

    # Pattern for "200g" (number directly followed by unit, no space)
    no_space_pattern = r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)$"
    no_space_match = re.match(no_space_pattern, measure)
    if no_space_match:
        qty = float(no_space_match.group(1))
        unit = no_space_match.group(2)
        return (qty, unit, None)

    # Pattern for mixed fractions "1 1/2 cups"
    mixed_fraction_pattern = r"^(\d+)\s+(\d+/\d+)\s+(.+)$"
    mixed_match = re.match(mixed_fraction_pattern, measure)
    if mixed_match:
        whole = float(mixed_match.group(1))
        fraction_val = _parse_fraction(mixed_match.group(2))
        if fraction_val is not None:
            qty = whole + fraction_val
            unit = mixed_match.group(3).strip()
            return (qty, unit, None)

    # Pattern for simple fractions "1/2 cup" or "3/4 cup"
    fraction_pattern = r"^(\d+/\d+)\s+(.+)$"
    fraction_match = re.match(fraction_pattern, measure)
    if fraction_match:
        fraction_val = _parse_fraction(fraction_match.group(1))
        if fraction_val is not None:
            unit = fraction_match.group(2).strip()
            return (fraction_val, unit, None)

    # Pattern for "2 cups" or "3 cloves"
    simple_pattern = r"^(\d+(?:\.\d+)?)\s+(.+)$"
    simple_match = re.match(simple_pattern, measure)
    if simple_match:
        qty = float(simple_match.group(1))
        unit = simple_match.group(2).strip()
        return (qty, unit, None)

    # Unparseable - best-effort fallback
    return (1.0, "", measure)


def _parse_instructions(instructions: str) -> list[str]:
    """Parse TheMealDB instructions into individual steps.

    Handles:
    - Newline-separated instructions
    - Numbered patterns like "1. Do this. 2. Do that."
    - Carriage returns

    Args:
        instructions: Raw instruction text from TheMealDB

    Returns:
        List of instruction strings, trimmed and non-empty
    """
    if not instructions:
        return []

    # Normalize line endings
    text = instructions.replace("\r\n", "\n").replace("\r", "\n")

    # First try splitting by newlines
    lines = text.split("\n")
    steps = [line.strip() for line in lines if line.strip()]

    # If we got meaningful steps from newlines, return them
    if len(steps) > 1:
        return steps

    # If single block, try numbered pattern "1. ... 2. ... 3. ..."
    # Pattern matches: digit(s) followed by period, with content after
    numbered_pattern = r"\d+\.\s*"
    parts = re.split(numbered_pattern, text)

    # Filter out empty parts and trim
    steps = [part.strip() for part in parts if part.strip()]

    return steps


class PersonalRecipesService:
    """Service for CRUD operations on user personal recipes."""

    # Table names as class attributes
    TABLE_RECIPES = "personal_recipes"
    TABLE_INGREDIENTS = "personal_recipe_ingredients"
    TABLE_STEPS = "personal_recipe_steps"

    # Default servings for forked recipes (TheMealDB doesn't provide this)
    DEFAULT_SERVINGS = 4

    def __init__(self) -> None:
        """Initialize the personal recipes service."""
        self.client = get_supabase_admin()

    def create_recipe(
        self, user_id: str, data: PersonalRecipeCreate
    ) -> PersonalRecipeResponse:
        """Create a new personal recipe with ingredients and steps.

        Args:
            user_id: The user's UUID
            data: Recipe creation data with nested ingredients and steps

        Returns:
            The created recipe with all nested data
        """
        # Insert the recipe
        recipe_data = {
            "user_id": user_id,
            "title": data.title,
            "image_url": data.image_url,
            "servings": data.servings,
            "prep_time_minutes": data.prep_time_minutes,
            "cook_time_minutes": data.cook_time_minutes,
            "tags": data.tags,
            "source_recipe_id": None,  # Set during fork operation
        }

        response = (
            self.client.table(self.TABLE_RECIPES)
            .insert(recipe_data)
            .execute()
        )

        recipe = response.data[0]
        recipe_id = recipe["id"]

        # Insert ingredients with sort_order (0-indexed)
        ingredients_data = [
            {
                "recipe_id": recipe_id,
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "unit": ingredient.unit,
                "note": ingredient.note,
                "sort_order": idx,
            }
            for idx, ingredient in enumerate(data.ingredients)
        ]

        ingredients_response = (
            self.client.table(self.TABLE_INGREDIENTS)
            .insert(ingredients_data)
            .execute()
        )

        # Insert steps with step_number (1-indexed)
        steps_data = [
            {
                "recipe_id": recipe_id,
                "step_number": idx + 1,
                "instruction": step.instruction,
            }
            for idx, step in enumerate(data.steps)
        ]

        steps_response = (
            self.client.table(self.TABLE_STEPS)
            .insert(steps_data)
            .execute()
        )

        # Build and return the response
        return PersonalRecipeResponse(
            id=str(recipe["id"]),
            user_id=recipe["user_id"],
            title=recipe["title"],
            image_url=recipe.get("image_url"),
            servings=recipe["servings"],
            prep_time_minutes=recipe.get("prep_time_minutes"),
            cook_time_minutes=recipe.get("cook_time_minutes"),
            tags=recipe.get("tags"),
            source_recipe_id=recipe.get("source_recipe_id"),
            created_at=recipe["created_at"],
            updated_at=recipe["updated_at"],
            ingredients=[
                IngredientResponse(
                    id=str(ing["id"]),
                    name=ing["name"],
                    quantity=ing["quantity"],
                    unit=ing["unit"],
                    note=ing.get("note"),
                    sort_order=ing["sort_order"],
                )
                for ing in ingredients_response.data
            ],
            steps=[
                InstructionStepResponse(
                    id=str(step["id"]),
                    step_number=step["step_number"],
                    instruction=step["instruction"],
                )
                for step in steps_response.data
            ],
        )

    def _create_recipe_with_source(
        self,
        user_id: str,
        data: PersonalRecipeCreate,
        source_recipe_id: str,
    ) -> PersonalRecipeResponse:
        """Create a personal recipe with source_recipe_id set.

        Internal method used by fork_recipe to preserve the original recipe ID.

        Args:
            user_id: The user's UUID
            data: Recipe creation data
            source_recipe_id: The original TheMealDB recipe ID

        Returns:
            The created recipe with all nested data
        """
        # Insert the recipe with source_recipe_id
        recipe_data = {
            "user_id": user_id,
            "title": data.title,
            "image_url": data.image_url,
            "servings": data.servings,
            "prep_time_minutes": data.prep_time_minutes,
            "cook_time_minutes": data.cook_time_minutes,
            "tags": data.tags,
            "source_recipe_id": source_recipe_id,
        }

        response = (
            self.client.table(self.TABLE_RECIPES)
            .insert(recipe_data)
            .execute()
        )

        recipe = response.data[0]
        recipe_id = recipe["id"]

        # Insert ingredients with sort_order (0-indexed)
        ingredients_data = [
            {
                "recipe_id": recipe_id,
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "unit": ingredient.unit,
                "note": ingredient.note,
                "sort_order": idx,
            }
            for idx, ingredient in enumerate(data.ingredients)
        ]

        ingredients_response = (
            self.client.table(self.TABLE_INGREDIENTS)
            .insert(ingredients_data)
            .execute()
        )

        # Insert steps with step_number (1-indexed)
        steps_data = [
            {
                "recipe_id": recipe_id,
                "step_number": idx + 1,
                "instruction": step.instruction,
            }
            for idx, step in enumerate(data.steps)
        ]

        steps_response = (
            self.client.table(self.TABLE_STEPS)
            .insert(steps_data)
            .execute()
        )

        # Build and return the response
        return PersonalRecipeResponse(
            id=str(recipe["id"]),
            user_id=recipe["user_id"],
            title=recipe["title"],
            image_url=recipe.get("image_url"),
            servings=recipe["servings"],
            prep_time_minutes=recipe.get("prep_time_minutes"),
            cook_time_minutes=recipe.get("cook_time_minutes"),
            tags=recipe.get("tags"),
            source_recipe_id=recipe.get("source_recipe_id"),
            created_at=recipe["created_at"],
            updated_at=recipe["updated_at"],
            ingredients=[
                IngredientResponse(
                    id=str(ing["id"]),
                    name=ing["name"],
                    quantity=ing["quantity"],
                    unit=ing["unit"],
                    note=ing.get("note"),
                    sort_order=ing["sort_order"],
                )
                for ing in ingredients_response.data
            ],
            steps=[
                InstructionStepResponse(
                    id=str(step["id"]),
                    step_number=step["step_number"],
                    instruction=step["instruction"],
                )
                for step in steps_response.data
            ],
        )

    async def fork_recipe(
        self, user_id: str, api_recipe_id: str
    ) -> PersonalRecipeResponse:
        """Fork a recipe from TheMealDB API as a personal recipe.

        Fetches the recipe from TheMealDB, transforms it to the personal recipe
        format, and stores it with source_recipe_id set for traceability.

        Args:
            user_id: The user's UUID
            api_recipe_id: The TheMealDB recipe ID

        Returns:
            The created personal recipe

        Raises:
            RecipeNotFoundError: If the recipe doesn't exist in TheMealDB
            ExternalAPIError: If TheMealDB API is unavailable
        """
        # Fetch recipe from TheMealDB API
        try:
            response = await themealdb_client.get_by_id(api_recipe_id)
        except Exception as e:
            raise ExternalAPIError(
                f"TheMealDB API unavailable: {e}"
            ) from e

        meals = response.get("meals")
        if not meals:
            raise RecipeNotFoundError(
                f"Recipe with ID '{api_recipe_id}' not found in TheMealDB"
            )

        meal = meals[0]

        # Transform TheMealDB format to PersonalRecipeCreate
        ingredients = self._parse_themealdb_ingredients(meal)
        steps = self._parse_themealdb_instructions(meal)

        # Build tags from category and area
        tags = []
        if meal.get("strCategory"):
            tags.append(meal["strCategory"])
        if meal.get("strArea"):
            tags.append(meal["strArea"])

        recipe_data = PersonalRecipeCreate(
            title=meal.get("strMeal", "Untitled Recipe"),
            image_url=meal.get("strMealThumb"),
            servings=self.DEFAULT_SERVINGS,
            prep_time_minutes=None,
            cook_time_minutes=None,
            tags=tags if tags else None,
            ingredients=ingredients,
            steps=steps,
        )

        # Create the recipe with source_recipe_id
        return self._create_recipe_with_source(
            user_id=user_id,
            data=recipe_data,
            source_recipe_id=api_recipe_id,
        )

    def _parse_themealdb_ingredients(
        self, meal: dict
    ) -> list[IngredientCreate]:
        """Parse TheMealDB ingredient fields into structured ingredients.

        TheMealDB uses strIngredient1-20 and strMeasure1-20 fields.

        Args:
            meal: The TheMealDB meal object

        Returns:
            List of IngredientCreate objects
        """
        ingredients = []

        for i in range(1, 21):
            ingredient_key = f"strIngredient{i}"
            measure_key = f"strMeasure{i}"

            ingredient_name = meal.get(ingredient_key, "")
            measure = meal.get(measure_key, "")

            # Skip empty ingredients
            if not ingredient_name or not ingredient_name.strip():
                continue

            # Parse the measure
            quantity, unit, note = _parse_measure(measure)

            ingredients.append(
                IngredientCreate(
                    name=ingredient_name.strip(),
                    quantity=quantity,
                    unit=unit,
                    note=note,
                )
            )

        return ingredients

    def _parse_themealdb_instructions(
        self, meal: dict
    ) -> list[InstructionStepCreate]:
        """Parse TheMealDB instructions into structured steps.

        Args:
            meal: The TheMealDB meal object

        Returns:
            List of InstructionStepCreate objects
        """
        instructions_text = meal.get("strInstructions", "")
        steps = _parse_instructions(instructions_text)

        # Ensure at least one step (required by model validation)
        if not steps:
            steps = ["Prepare the recipe according to the original instructions."]

        return [
            InstructionStepCreate(instruction=step)
            for step in steps
        ]

    def get_recipes(self, user_id: str) -> list[PersonalRecipeSummary]:
        """Get all personal recipes for a user.

        Args:
            user_id: The user's UUID

        Returns:
            List of recipe summaries (without nested data)
        """
        response = (
            self.client.table(self.TABLE_RECIPES)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [
            PersonalRecipeSummary(
                id=str(recipe["id"]),
                title=recipe["title"],
                image_url=recipe.get("image_url"),
                source="personal",
            )
            for recipe in response.data
        ]

    def search_recipes(
        self, user_id: str, query: str
    ) -> list[PersonalRecipeSummary]:
        """Search personal recipes by title (case-insensitive).

        Args:
            user_id: The user's UUID
            query: Search query string

        Returns:
            List of matching recipe summaries with source="personal"
        """
        response = (
            self.client.table(self.TABLE_RECIPES)
            .select("*")
            .eq("user_id", user_id)
            .ilike("title", f"%{query}%")
            .order("created_at", desc=True)
            .execute()
        )

        return [
            PersonalRecipeSummary(
                id=str(recipe["id"]),
                title=recipe["title"],
                image_url=recipe.get("image_url"),
                source="personal",
            )
            for recipe in response.data
        ]

    def get_recipe_by_id(
        self, user_id: str, recipe_id: str
    ) -> PersonalRecipeResponse | None:
        """Get a single personal recipe by ID with all nested data.

        Args:
            user_id: The user's UUID (for ownership validation)
            recipe_id: The recipe's UUID

        Returns:
            The recipe with ingredients and steps, or None if not found
        """
        # Query recipe with user_id check (RLS backup)
        recipe_response = (
            self.client.table(self.TABLE_RECIPES)
            .select("*")
            .eq("id", recipe_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not recipe_response.data:
            return None

        recipe = recipe_response.data[0]

        # Fetch ingredients ordered by sort_order
        ingredients_response = (
            self.client.table(self.TABLE_INGREDIENTS)
            .select("*")
            .eq("recipe_id", recipe_id)
            .order("sort_order")
            .execute()
        )

        # Fetch steps ordered by step_number
        steps_response = (
            self.client.table(self.TABLE_STEPS)
            .select("*")
            .eq("recipe_id", recipe_id)
            .order("step_number")
            .execute()
        )

        return PersonalRecipeResponse(
            id=str(recipe["id"]),
            user_id=recipe["user_id"],
            title=recipe["title"],
            image_url=recipe.get("image_url"),
            servings=recipe["servings"],
            prep_time_minutes=recipe.get("prep_time_minutes"),
            cook_time_minutes=recipe.get("cook_time_minutes"),
            tags=recipe.get("tags"),
            source_recipe_id=recipe.get("source_recipe_id"),
            created_at=recipe["created_at"],
            updated_at=recipe["updated_at"],
            ingredients=[
                IngredientResponse(
                    id=str(ing["id"]),
                    name=ing["name"],
                    quantity=ing["quantity"],
                    unit=ing["unit"],
                    note=ing.get("note"),
                    sort_order=ing["sort_order"],
                )
                for ing in ingredients_response.data
            ],
            steps=[
                InstructionStepResponse(
                    id=str(step["id"]),
                    step_number=step["step_number"],
                    instruction=step["instruction"],
                )
                for step in steps_response.data
            ],
        )

    def update_recipe(
        self, user_id: str, recipe_id: str, data: PersonalRecipeUpdate
    ) -> PersonalRecipeResponse | None:
        """Update an existing personal recipe.

        Args:
            user_id: The user's UUID (for ownership validation)
            recipe_id: The recipe's UUID
            data: Update data with optional fields

        Returns:
            The updated recipe with all nested data, or None if not found/not owned
        """
        # Verify ownership first
        ownership_response = (
            self.client.table(self.TABLE_RECIPES)
            .select("id, user_id")
            .eq("id", recipe_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not ownership_response.data:
            return None

        # Build update payload with only non-None fields
        update_payload = {}
        if data.title is not None:
            update_payload["title"] = data.title
        if data.image_url is not None:
            update_payload["image_url"] = data.image_url
        if data.servings is not None:
            update_payload["servings"] = data.servings
        if data.prep_time_minutes is not None:
            update_payload["prep_time_minutes"] = data.prep_time_minutes
        if data.cook_time_minutes is not None:
            update_payload["cook_time_minutes"] = data.cook_time_minutes
        if data.tags is not None:
            update_payload["tags"] = data.tags

        # Update recipe if there are fields to update
        if update_payload:
            self.client.table(self.TABLE_RECIPES).update(update_payload).eq(
                "id", recipe_id
            ).execute()

        # Handle ingredients replacement if provided
        if data.ingredients is not None:
            # Delete existing ingredients
            self.client.table(self.TABLE_INGREDIENTS).delete().eq(
                "recipe_id", recipe_id
            ).execute()

            # Insert new ingredients with sort_order
            ingredients_data = [
                {
                    "recipe_id": recipe_id,
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                    "note": ingredient.note,
                    "sort_order": idx,
                }
                for idx, ingredient in enumerate(data.ingredients)
            ]

            self.client.table(self.TABLE_INGREDIENTS).insert(
                ingredients_data
            ).execute()

        # Handle steps replacement if provided
        if data.steps is not None:
            # Delete existing steps
            self.client.table(self.TABLE_STEPS).delete().eq(
                "recipe_id", recipe_id
            ).execute()

            # Insert new steps with step_number
            steps_data = [
                {
                    "recipe_id": recipe_id,
                    "step_number": idx + 1,
                    "instruction": step.instruction,
                }
                for idx, step in enumerate(data.steps)
            ]

            self.client.table(self.TABLE_STEPS).insert(steps_data).execute()

        # Return the updated recipe
        return self.get_recipe_by_id(user_id, recipe_id)

    def delete_recipe(self, user_id: str, recipe_id: str) -> bool:
        """Delete a personal recipe.

        Args:
            user_id: The user's UUID (for ownership validation)
            recipe_id: The recipe's UUID

        Returns:
            True if deleted, False if not found or not owned
        """
        # Verify ownership first
        ownership_response = (
            self.client.table(self.TABLE_RECIPES)
            .select("id, user_id")
            .eq("id", recipe_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not ownership_response.data:
            return False

        # Delete recipe (cascade handles ingredients and steps)
        self.client.table(self.TABLE_RECIPES).delete().eq("id", recipe_id).execute()

        return True
