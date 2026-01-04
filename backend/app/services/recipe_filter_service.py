"""Recipe filtering service based on user preferences.

Filters recipes based on dietary preferences, allergies, and excluded ingredients.
"""

from app.models.preferences import AllergyType, DietaryType, UserPreferencesResponse
from app.models.recipe import Recipe
from app.services.ingredient_mappings import (
    ALLERGEN_KEYWORDS,
    DIETARY_EXCLUSIONS,
    EXCEPTIONS,
)


class RecipeFilterService:
    """Service for filtering recipes based on user preferences.

    Provides static methods to filter recipe lists based on:
    - Dietary preferences (vegetarian, vegan, halal, etc.)
    - Allergies (gluten, lactose, peanuts, etc.)
    - Manually excluded ingredients
    """

    @staticmethod
    def filter_recipes(
        recipes: list[Recipe],
        preferences: UserPreferencesResponse,
    ) -> list[Recipe]:
        """Filter recipes based on user preferences.

        Applies all filters cumulatively - a recipe must pass all filters.

        Args:
            recipes: List of recipes to filter.
            preferences: User's dietary preferences and restrictions.

        Returns:
            List of recipes compatible with all user preferences.
        """
        if not recipes:
            return []

        # If no preferences set, return all recipes
        if (
            not preferences.dietary_preferences
            and not preferences.allergies
            and not preferences.excluded_ingredients
        ):
            return recipes

        filtered: list[Recipe] = []

        for recipe in recipes:
            if RecipeFilterService._is_recipe_compatible(recipe, preferences):
                filtered.append(recipe)

        return filtered

    @staticmethod
    def _is_recipe_compatible(
        recipe: Recipe,
        preferences: UserPreferencesResponse,
    ) -> bool:
        """Check if a recipe is compatible with user preferences.

        Args:
            recipe: Recipe to check.
            preferences: User's preferences.

        Returns:
            True if recipe passes all filters, False otherwise.
        """
        # Get normalized ingredient names
        ingredient_names = [ing.name.lower() for ing in recipe.ingredients]

        # Check dietary preferences
        if preferences.dietary_preferences:
            if not RecipeFilterService._matches_dietary(
                ingredient_names, preferences.dietary_preferences
            ):
                return False

        # Check allergies
        if preferences.allergies:
            if not RecipeFilterService._matches_allergies(
                ingredient_names, preferences.allergies
            ):
                return False

        # Check excluded ingredients
        if preferences.excluded_ingredients:
            if not RecipeFilterService._matches_excluded(
                ingredient_names, preferences.excluded_ingredients
            ):
                return False

        return True

    @staticmethod
    def _matches_dietary(
        ingredient_names: list[str],
        dietary_preferences: list[DietaryType],
    ) -> bool:
        """Check if recipe matches dietary preferences.

        Args:
            ingredient_names: Normalized ingredient names from recipe.
            dietary_preferences: User's dietary preferences.

        Returns:
            True if recipe is compatible, False if it contains excluded ingredients.
        """
        for pref in dietary_preferences:
            excluded = DIETARY_EXCLUSIONS.get(pref, [])
            for ingredient in ingredient_names:
                for excluded_item in excluded:
                    contains = RecipeFilterService._ingredient_contains
                    if contains(ingredient, excluded_item):
                        return False
        return True

    @staticmethod
    def _matches_allergies(
        ingredient_names: list[str],
        allergies: list[AllergyType],
    ) -> bool:
        """Check if recipe matches allergy restrictions.

        Args:
            ingredient_names: Normalized ingredient names from recipe.
            allergies: User's allergies.

        Returns:
            True if recipe is safe, False if it contains allergens.
        """
        for allergy in allergies:
            keywords = ALLERGEN_KEYWORDS.get(allergy, [])
            for ingredient in ingredient_names:
                # Check if this ingredient is an exception
                if RecipeFilterService._is_exception(ingredient, allergy.value):
                    continue

                for keyword in keywords:
                    if RecipeFilterService._ingredient_contains(ingredient, keyword):
                        return False
        return True

    @staticmethod
    def _matches_excluded(
        ingredient_names: list[str],
        excluded_ingredients: list[str],
    ) -> bool:
        """Check if recipe contains manually excluded ingredients.

        Args:
            ingredient_names: Normalized ingredient names from recipe.
            excluded_ingredients: User's excluded ingredients.

        Returns:
            True if recipe is safe, False if it contains excluded ingredients.
        """
        for excluded in excluded_ingredients:
            excluded_lower = excluded.lower()
            for ingredient in ingredient_names:
                if RecipeFilterService._ingredient_contains(ingredient, excluded_lower):
                    return False
        return True

    @staticmethod
    def _ingredient_contains(ingredient: str, keyword: str) -> bool:
        """Check if ingredient contains a keyword (partial match).

        Performs case-insensitive partial matching.

        Args:
            ingredient: Ingredient name (already lowercase).
            keyword: Keyword to search for.

        Returns:
            True if ingredient contains keyword.
        """
        return keyword.lower() in ingredient

    @staticmethod
    def _is_exception(ingredient: str, allergy: str) -> bool:
        """Check if ingredient is an exception for this allergy.

        Args:
            ingredient: Ingredient name (lowercase).
            allergy: Allergy type value.

        Returns:
            True if ingredient should be excluded from allergen detection.
        """
        for exception_ingredient, exception_allergies in EXCEPTIONS.items():
            if exception_ingredient in ingredient:
                if allergy in exception_allergies:
                    return True
        return False
