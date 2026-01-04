"""Tests for RecipeFilterService - Groupe 2.

Test plan: TS-001 to TS-014
Tests filtering by dietary preferences, allergies, and excluded ingredients.
"""

import pytest

from app.models.preferences import AllergyType, DietaryType, UserPreferencesResponse
from app.models.recipe import Ingredient, Recipe
from app.services.recipe_filter_service import RecipeFilterService


def make_recipe(id: str, name: str, ingredients: list[str]) -> Recipe:
    """Helper to create test recipes."""
    return Recipe(
        id=id,
        name=name,
        ingredients=[Ingredient(name=ing, measure="") for ing in ingredients],
    )


def make_preferences(
    dietary: list[DietaryType] | None = None,
    allergies: list[AllergyType] | None = None,
    excluded: list[str] | None = None,
) -> UserPreferencesResponse:
    """Helper to create test preferences."""
    return UserPreferencesResponse(
        dietary_preferences=dietary or [],
        allergies=allergies or [],
        excluded_ingredients=excluded or [],
        preferred_ingredients=[],
        portions_count=2,
    )


class TestFilterByDietaryPreferences:
    """Tests for dietary preference filtering (TS-001 to TS-004)."""

    def test_filter_recipes_vegetarian_excludes_meat_recipes(self) -> None:
        """TS-001: Vegetarian filtering excludes meat."""
        recipes = [
            make_recipe("1", "Vegetable Curry", ["rice", "vegetables", "tofu"]),
            make_recipe("2", "Chicken Stir Fry", ["chicken breast", "rice", "vegetables"]),
            make_recipe("3", "Pasta Primavera", ["pasta", "tomato sauce", "cheese"]),
        ]
        preferences = make_preferences(dietary=[DietaryType.VEGETARIAN])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 2
        result_ids = [r.id for r in result]
        assert "1" in result_ids  # Vegetable Curry
        assert "3" in result_ids  # Pasta Primavera
        assert "2" not in result_ids  # Chicken excluded

    def test_filter_recipes_vegan_excludes_all_animal_products(self) -> None:
        """TS-002: Vegan filtering excludes all animal products."""
        recipes = [
            make_recipe("1", "Tofu Rice", ["rice", "vegetables", "tofu"]),
            make_recipe("2", "Cheese Pasta", ["pasta", "cheese", "tomato"]),
            make_recipe("3", "Simple Salad", ["salad", "olive oil", "lemon"]),
            make_recipe("4", "Pancakes", ["pancakes", "milk", "egg"]),
        ]
        preferences = make_preferences(dietary=[DietaryType.VEGAN])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 2
        result_ids = [r.id for r in result]
        assert "1" in result_ids  # Tofu Rice
        assert "3" in result_ids  # Simple Salad
        assert "2" not in result_ids  # Cheese excluded
        assert "4" not in result_ids  # Milk and egg excluded

    def test_filter_recipes_halal_excludes_pork_and_alcohol(self) -> None:
        """TS-003: Halal filtering excludes pork and alcohol."""
        recipes = [
            make_recipe("1", "Chicken Rice", ["chicken", "rice", "vegetables"]),
            make_recipe("2", "Bacon Eggs", ["bacon", "eggs", "toast"]),
            make_recipe("3", "Beef Bourguignon", ["beef", "red wine", "mushrooms"]),
        ]
        preferences = make_preferences(dietary=[DietaryType.HALAL])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Chicken Rice only

    def test_filter_recipes_pescetarian_allows_fish_excludes_meat(self) -> None:
        """TS-004: Pescetarian allows fish but excludes land meat."""
        recipes = [
            make_recipe("1", "Grilled Salmon", ["salmon", "lemon", "dill"]),
            make_recipe("2", "Shrimp Pasta", ["shrimp", "garlic", "pasta"]),
            make_recipe("3", "Chicken Salad", ["chicken", "vegetables"]),
        ]
        preferences = make_preferences(dietary=[DietaryType.PESCETARIAN])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 2
        result_ids = [r.id for r in result]
        assert "1" in result_ids  # Salmon OK
        assert "2" in result_ids  # Shrimp OK
        assert "3" not in result_ids  # Chicken excluded


class TestFilterByAllergies:
    """Tests for allergy filtering (TS-005 to TS-008)."""

    def test_filter_recipes_gluten_allergy_excludes_wheat_products(self) -> None:
        """TS-005: Gluten allergy excludes wheat products."""
        recipes = [
            make_recipe("1", "Chicken Rice", ["rice", "chicken", "vegetables"]),
            make_recipe("2", "Spaghetti", ["pasta", "tomato sauce", "cheese"]),
            make_recipe("3", "Fish Crumbs", ["bread crumbs", "fish", "lemon"]),
        ]
        preferences = make_preferences(allergies=[AllergyType.GLUTEN])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Chicken Rice only

    def test_filter_recipes_lactose_allergy_excludes_dairy(self) -> None:
        """TS-006: Lactose allergy excludes dairy products."""
        recipes = [
            make_recipe("1", "Grilled Chicken", ["chicken", "olive oil", "herbs"]),
            make_recipe("2", "Creamy Pasta", ["pasta", "cream", "parmesan"]),
            make_recipe("3", "Greek Salad", ["salad", "feta cheese", "olives"]),
        ]
        preferences = make_preferences(allergies=[AllergyType.LACTOSE])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Grilled Chicken only

    def test_filter_recipes_peanut_allergy_excludes_peanuts(self) -> None:
        """TS-007: Peanut allergy excludes peanuts."""
        recipes = [
            make_recipe("1", "Pad Thai", ["pad thai", "shrimp", "peanuts"]),
            make_recipe("2", "Tofu Stir Fry", ["stir fry", "tofu", "sesame oil"]),
        ]
        preferences = make_preferences(allergies=[AllergyType.PEANUTS])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "2"  # Tofu Stir Fry only

    def test_filter_recipes_multiple_allergies_cumulative(self) -> None:
        """TS-008: Multiple allergies filter cumulatively."""
        recipes = [
            make_recipe("1", "Plain Rice", ["rice", "vegetables", "tofu"]),
            make_recipe("2", "Pasta", ["pasta", "tomato"]),  # gluten
            make_recipe("3", "Milk Salad", ["salad", "milk dressing"]),  # lactose
            make_recipe("4", "Bread Butter", ["bread", "butter"]),  # both
        ]
        preferences = make_preferences(allergies=[AllergyType.GLUTEN, AllergyType.LACTOSE])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Plain Rice only


class TestFilterByExcludedIngredients:
    """Tests for excluded ingredients filtering (TS-009 to TS-010)."""

    def test_filter_recipes_excluded_ingredients_removes_matching(self) -> None:
        """TS-009: Excluded ingredients remove matching recipes."""
        recipes = [
            make_recipe("1", "Chicken Rice", ["chicken", "rice", "broccoli"]),
            make_recipe("2", "Garlic Pasta", ["pasta", "garlic", "olive oil"]),
            make_recipe("3", "Fish Garlic", ["fish", "garlic", "lemon"]),
        ]
        preferences = make_preferences(excluded=["garlic"])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Chicken Rice only

    def test_filter_recipes_excluded_ingredients_partial_match(self) -> None:
        """TS-010: Partial matching works for excluded ingredients."""
        recipes = [
            make_recipe("1", "Garlic Chicken", ["Garlic Powder", "chicken", "rice"]),
            make_recipe("2", "Plain Pasta", ["pasta", "tomato", "basil"]),
        ]
        preferences = make_preferences(excluded=["garlic"])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "2"  # Plain Pasta only


class TestEdgeCases:
    """Tests for edge cases (TS-011 to TS-014)."""

    def test_filter_recipes_empty_list_returns_empty(self) -> None:
        """TS-011: Empty recipe list returns empty list."""
        preferences = make_preferences(dietary=[DietaryType.VEGETARIAN])

        result = RecipeFilterService.filter_recipes([], preferences)

        assert result == []

    def test_filter_recipes_no_preferences_returns_all(self) -> None:
        """TS-012: No preferences returns all recipes."""
        recipes = [
            make_recipe("1", "Recipe A", ["chicken", "beef"]),
            make_recipe("2", "Recipe B", ["milk", "cheese"]),
            make_recipe("3", "Recipe C", ["pasta", "peanuts"]),
        ]
        preferences = make_preferences()  # Empty preferences

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 3

    def test_filter_recipes_case_insensitive_matching(self) -> None:
        """TS-013: Matching is case-insensitive."""
        recipes = [
            make_recipe("1", "Upper Case", ["CHICKEN BREAST", "Rice", "VeGetAbles"]),
            make_recipe("2", "Lower Case", ["pasta", "TOMATO", "cheese"]),
        ]
        preferences = make_preferences(dietary=[DietaryType.VEGETARIAN])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "2"  # CHICKEN detected despite case

    def test_filter_recipes_exception_coconut_milk_not_lactose(self) -> None:
        """TS-014: Coconut milk is not flagged as lactose."""
        recipes = [
            make_recipe("1", "Thai Curry", ["curry", "coconut milk", "vegetables"]),
            make_recipe("2", "Cream Pasta", ["pasta", "cow milk", "cheese"]),
        ]
        preferences = make_preferences(allergies=[AllergyType.LACTOSE])

        result = RecipeFilterService.filter_recipes(recipes, preferences)

        assert len(result) == 1
        assert result[0].id == "1"  # Thai Curry with coconut milk is OK
