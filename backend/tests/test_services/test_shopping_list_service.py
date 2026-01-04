"""Tests for shopping list service."""

import pytest

from app.models.shopping_list import IngredientCategory
from app.services.shopping_list_service import (
    ShoppingListService,
    INGREDIENT_CATEGORIES,
    _CATEGORY_LOOKUP,
)


class TestIngredientNormalization:
    """Tests for ingredient name normalization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_normalize_lowercase(self):
        """Test case-insensitive normalization."""
        assert self.service._normalize_ingredient_name("Onion") == "onion"
        assert self.service._normalize_ingredient_name("CHICKEN") == "chicken"
        assert self.service._normalize_ingredient_name("ToMaTo") == "tomato"

    def test_normalize_strips_whitespace(self):
        """Test whitespace stripping."""
        assert self.service._normalize_ingredient_name("  onion  ") == "onion"
        assert self.service._normalize_ingredient_name("\tchicken\n") == "chicken"

    def test_normalize_combined(self):
        """Test combined normalization."""
        assert self.service._normalize_ingredient_name("  ONION  ") == "onion"


class TestQuantityParsing:
    """Tests for quantity parsing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_parse_integer(self):
        """Test parsing simple integers."""
        value, unit = self.service._parse_quantity("2")
        assert value == 2.0
        assert unit == ""

    def test_parse_decimal(self):
        """Test parsing decimals."""
        value, unit = self.service._parse_quantity("1.5")
        assert value == 1.5
        assert unit == ""

    def test_parse_fraction(self):
        """Test parsing fractions."""
        value, unit = self.service._parse_quantity("1/2")
        assert value == 0.5
        assert unit == ""

        value, unit = self.service._parse_quantity("3/4")
        assert value == 0.75
        assert unit == ""

    def test_parse_with_unit_grams(self):
        """Test parsing with gram unit."""
        value, unit = self.service._parse_quantity("200g")
        assert value == 200.0
        assert unit == "g"

    def test_parse_with_unit_cups(self):
        """Test parsing with cups unit."""
        value, unit = self.service._parse_quantity("2 cups")
        assert value == 2.0
        assert unit == "cups"

    def test_parse_fraction_with_unit(self):
        """Test parsing fraction with unit."""
        value, unit = self.service._parse_quantity("1/2 cup")
        assert value == 0.5
        assert unit == "cup"

    def test_parse_mixed_number(self):
        """Test parsing mixed numbers like 1 1/2."""
        value, unit = self.service._parse_quantity("1 1/2 cups")
        assert value == 1.5
        assert unit == "cups"

    def test_parse_empty(self):
        """Test parsing empty string."""
        value, unit = self.service._parse_quantity("")
        assert value is None
        assert unit == ""

    def test_parse_text_only(self):
        """Test parsing text without number."""
        value, unit = self.service._parse_quantity("pinch")
        assert value is None
        assert unit == "pinch"


class TestQuantitySumming:
    """Tests for quantity summing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_sum_same_unit(self):
        """Test summing quantities with same unit."""
        result = self.service._sum_quantities(["2 cups", "1 cups"])
        assert result == "3 cups"

    def test_sum_no_unit(self):
        """Test summing quantities without unit."""
        result = self.service._sum_quantities(["2", "1"])
        assert result == "3"

    def test_sum_incompatible_concatenates(self):
        """Test that incompatible quantities are concatenated."""
        result = self.service._sum_quantities(["2 cups", "100g"])
        assert "2 cups" in result
        assert "100g" in result
        assert ", " in result

    def test_sum_single_quantity(self):
        """Test summing single quantity returns as-is."""
        result = self.service._sum_quantities(["2 cups"])
        assert result == "2 cups"

    def test_sum_empty_list(self):
        """Test summing empty list."""
        result = self.service._sum_quantities([])
        assert result == ""


class TestPortionMultiplication:
    """Tests for portion multiplication."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_multiply_by_one(self):
        """Test multiplying by 1 returns original."""
        result = self.service._multiply_quantity("2 cups", 1)
        assert result == "2 cups"

    def test_multiply_integer(self):
        """Test multiplying integer quantity."""
        result = self.service._multiply_quantity("2", 3)
        assert result == "6"

    def test_multiply_with_unit(self):
        """Test multiplying quantity with unit."""
        result = self.service._multiply_quantity("200g", 2)
        assert result == "400 g"

    def test_multiply_fraction(self):
        """Test multiplying fractional quantity."""
        result = self.service._multiply_quantity("1/2 cup", 2)
        assert result == "1 cup"


class TestIngredientExtraction:
    """Tests for extracting ingredients from TheMealDB response."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_extract_ingredients(self):
        """Test extracting ingredients from meal data."""
        meal_data = {
            "strIngredient1": "Chicken",
            "strMeasure1": "500g",
            "strIngredient2": "Onion",
            "strMeasure2": "1",
            "strIngredient3": "",
            "strMeasure3": "",
            "strIngredient4": None,
            "strMeasure4": None,
        }
        result = self.service._extract_ingredients_from_meal(meal_data)
        assert len(result) == 2
        assert ("Chicken", "500g") in result
        assert ("Onion", "1") in result

    def test_extract_strips_whitespace(self):
        """Test that ingredient names are stripped."""
        meal_data = {
            "strIngredient1": "  Chicken  ",
            "strMeasure1": "  500g  ",
        }
        result = self.service._extract_ingredients_from_meal(meal_data)
        assert result[0] == ("Chicken", "500g")

    def test_extract_empty_meal(self):
        """Test extracting from meal with no ingredients."""
        meal_data = {}
        result = self.service._extract_ingredients_from_meal(meal_data)
        assert result == []


class TestCategoryMapping:
    """Tests for ingredient category mapping."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingListService()

    def test_category_mapping_vegetables_french(self):
        """Test French vegetable ingredients map to LEGUMES."""
        assert self.service._get_category("tomate") == IngredientCategory.LEGUMES
        assert self.service._get_category("oignon") == IngredientCategory.LEGUMES
        assert self.service._get_category("carotte") == IngredientCategory.LEGUMES

    def test_category_mapping_vegetables_english(self):
        """Test English vegetable ingredients map to LEGUMES."""
        assert self.service._get_category("tomato") == IngredientCategory.LEGUMES
        assert self.service._get_category("onion") == IngredientCategory.LEGUMES
        assert self.service._get_category("carrot") == IngredientCategory.LEGUMES

    def test_category_mapping_meats(self):
        """Test meat ingredients map to VIANDES."""
        assert self.service._get_category("chicken") == IngredientCategory.VIANDES
        assert self.service._get_category("beef") == IngredientCategory.VIANDES
        assert self.service._get_category("poulet") == IngredientCategory.VIANDES

    def test_category_mapping_fish(self):
        """Test fish ingredients map to POISSONS."""
        assert self.service._get_category("salmon") == IngredientCategory.POISSONS
        assert self.service._get_category("shrimp") == IngredientCategory.POISSONS
        assert self.service._get_category("saumon") == IngredientCategory.POISSONS

    def test_category_mapping_dairy(self):
        """Test dairy ingredients map to PRODUITS_LAITIERS."""
        # Use specific dairy items not shared with other categories
        assert (
            self.service._get_category("butter")
            == IngredientCategory.PRODUITS_LAITIERS
        )
        assert (
            self.service._get_category("cheese")
            == IngredientCategory.PRODUITS_LAITIERS
        )
        assert (
            self.service._get_category("eggs") == IngredientCategory.PRODUITS_LAITIERS
        )
        assert (
            self.service._get_category("yogurt")
            == IngredientCategory.PRODUITS_LAITIERS
        )

    def test_category_mapping_unknown_defaults_to_autres(self):
        """Test unknown ingredients default to AUTRES."""
        assert self.service._get_category("xyz123unknown") == IngredientCategory.AUTRES
        assert self.service._get_category("random food") == IngredientCategory.AUTRES

    def test_category_mapping_case_insensitive(self):
        """Test category mapping is case insensitive."""
        assert self.service._get_category("CHICKEN") == IngredientCategory.VIANDES
        assert self.service._get_category("Chicken") == IngredientCategory.VIANDES
        assert self.service._get_category("chicken") == IngredientCategory.VIANDES

    def test_category_mapping_compound_ingredients(self):
        """Test compound ingredients are matched via substring."""
        assert (
            self.service._get_category("chicken breast") == IngredientCategory.VIANDES
        )
        assert (
            self.service._get_category("fresh tomatoes") == IngredientCategory.LEGUMES
        )


class TestIngredientCategoriesDict:
    """Tests for INGREDIENT_CATEGORIES dictionary."""

    def test_all_categories_present(self):
        """Test all 8 categories are in the mapping."""
        expected_categories = {
            IngredientCategory.LEGUMES,
            IngredientCategory.VIANDES,
            IngredientCategory.POISSONS,
            IngredientCategory.PRODUITS_LAITIERS,
            IngredientCategory.EPICERIE,
            IngredientCategory.BOISSONS,
            IngredientCategory.SURGELES,
        }
        actual_categories = set(INGREDIENT_CATEGORIES.keys())
        # AUTRES is not in the mapping as it's the default
        assert expected_categories.issubset(actual_categories)

    def test_lookup_dict_populated(self):
        """Test the lookup dictionary is populated."""
        assert len(_CATEGORY_LOOKUP) > 0
        assert "chicken" in _CATEGORY_LOOKUP
        assert "tomato" in _CATEGORY_LOOKUP
