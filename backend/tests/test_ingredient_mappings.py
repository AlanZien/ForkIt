"""Tests for ingredient mappings - Groupe 1.

Test plan: TM-001 to TM-008
Tests DIETARY_EXCLUSIONS, ALLERGEN_KEYWORDS, and EXCEPTIONS dictionaries.
"""

import pytest

from app.models.preferences import AllergyType, DietaryType
from app.services.ingredient_mappings import (
    ALLERGEN_KEYWORDS,
    DIETARY_EXCLUSIONS,
    EXCEPTIONS,
)


class TestDietaryExclusions:
    """Tests for DIETARY_EXCLUSIONS mapping (TM-001 to TM-004)."""

    def test_dietary_exclusions_vegetarian_contains_meat_ingredients(self) -> None:
        """TM-001: Vegetarian excludes meat ingredients."""
        exclusions = DIETARY_EXCLUSIONS[DietaryType.VEGETARIAN]

        # Must contain common meats
        required_meats = [
            "chicken",
            "beef",
            "pork",
            "lamb",
            "duck",
            "turkey",
            "veal",
            "bacon",
            "ham",
        ]
        for meat in required_meats:
            assert meat in exclusions, f"Missing meat: {meat}"

        # All ingredients should be lowercase
        for ingredient in exclusions:
            assert ingredient == ingredient.lower(), f"Not lowercase: {ingredient}"

        assert len(exclusions) > 0

    def test_dietary_exclusions_vegan_contains_all_animal_products(self) -> None:
        """TM-002: Vegan excludes all animal products."""
        exclusions = DIETARY_EXCLUSIONS[DietaryType.VEGAN]

        # Must contain meats
        meats = ["chicken", "beef", "pork", "lamb"]
        for meat in meats:
            assert meat in exclusions, f"Missing meat: {meat}"

        # Must contain dairy
        dairy = ["milk", "cheese", "cream", "butter", "yogurt"]
        for item in dairy:
            assert item in exclusions, f"Missing dairy: {item}"

        # Must contain eggs and honey
        assert "egg" in exclusions
        assert "honey" in exclusions

        # Total at least 15 ingredients
        assert len(exclusions) >= 15

    def test_dietary_exclusions_halal_excludes_pork_and_alcohol(self) -> None:
        """TM-003: Halal excludes pork derivatives and alcohol."""
        exclusions = DIETARY_EXCLUSIONS[DietaryType.HALAL]

        # Pork derivatives
        pork_items = ["pork", "bacon", "ham", "lard", "pancetta", "prosciutto"]
        for item in pork_items:
            assert item in exclusions, f"Missing pork item: {item}"

        # Alcohol
        alcohol_items = ["wine", "beer", "alcohol"]
        for item in alcohol_items:
            assert item in exclusions, f"Missing alcohol: {item}"

    def test_dietary_exclusions_all_seven_types_defined(self) -> None:
        """TM-004: All 7 dietary types have exclusion lists."""
        dietary_types = [
            DietaryType.VEGETARIAN,
            DietaryType.VEGAN,
            DietaryType.NO_PORK,
            DietaryType.NO_BEEF,
            DietaryType.PESCETARIAN,
            DietaryType.HALAL,
            DietaryType.KOSHER,
        ]

        assert len(DIETARY_EXCLUSIONS) == 7

        for dtype in dietary_types:
            assert dtype in DIETARY_EXCLUSIONS, f"Missing type: {dtype}"
            assert len(DIETARY_EXCLUSIONS[dtype]) > 0, f"Empty list for: {dtype}"


class TestAllergenKeywords:
    """Tests for ALLERGEN_KEYWORDS mapping (TM-005 to TM-007)."""

    def test_allergen_keywords_gluten_contains_wheat_derivatives(self) -> None:
        """TM-005: Gluten allergy keywords include wheat derivatives."""
        keywords = ALLERGEN_KEYWORDS[AllergyType.GLUTEN]

        required = ["wheat", "flour", "bread", "pasta", "semolina", "couscous", "barley", "rye"]
        for item in required:
            assert item in keywords, f"Missing gluten keyword: {item}"

        assert len(keywords) >= 8

    def test_allergen_keywords_lactose_contains_dairy_products(self) -> None:
        """TM-006: Lactose allergy keywords include dairy products."""
        keywords = ALLERGEN_KEYWORDS[AllergyType.LACTOSE]

        required = ["milk", "cheese", "cream", "butter", "yogurt", "whey"]
        for item in required:
            assert item in keywords, f"Missing dairy keyword: {item}"

        assert len(keywords) >= 6

    def test_allergen_keywords_all_eleven_types_defined(self) -> None:
        """TM-007: All 11 allergy types have keyword lists."""
        allergy_types = [
            AllergyType.GLUTEN,
            AllergyType.LACTOSE,
            AllergyType.TREE_NUTS,
            AllergyType.PEANUTS,
            AllergyType.EGGS,
            AllergyType.FISH,
            AllergyType.SHELLFISH,
            AllergyType.SOY,
            AllergyType.SESAME,
            AllergyType.MUSTARD,
            AllergyType.CELERY,
        ]

        assert len(ALLERGEN_KEYWORDS) == 11

        for atype in allergy_types:
            assert atype in ALLERGEN_KEYWORDS, f"Missing allergy: {atype}"
            assert len(ALLERGEN_KEYWORDS[atype]) > 0, f"Empty list for: {atype}"


class TestExceptions:
    """Tests for EXCEPTIONS mapping (TM-008)."""

    def test_exceptions_prevents_false_positives(self) -> None:
        """TM-008: Exceptions handle false positives correctly."""
        # Coconut milk is not dairy
        assert "coconut milk" in EXCEPTIONS
        assert "lactose" in EXCEPTIONS["coconut milk"]

        # Coconut cream is not dairy
        assert "coconut cream" in EXCEPTIONS
        assert "lactose" in EXCEPTIONS["coconut cream"]

        # Eggplant is not eggs
        assert "eggplant" in EXCEPTIONS
        assert "eggs" in EXCEPTIONS["eggplant"]
