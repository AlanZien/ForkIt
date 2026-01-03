"""Tests for shopping list Pydantic models."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.models.shopping_list import (
    IngredientCategory,
    ShoppingListItemCreate,
    ShoppingListItemResponse,
    ShoppingListGenerateResponse,
    CategoryGroupResponse,
)


class TestIngredientCategory:
    """Tests for IngredientCategory enum."""

    def test_category_enum_has_eight_categories(self):
        """Test that there are exactly 8 categories including AUTRES."""
        categories = list(IngredientCategory)
        assert len(categories) == 8

    def test_category_values(self):
        """Test that all expected categories exist with correct values."""
        expected = {
            "LEGUMES": "legumes",
            "VIANDES": "viandes",
            "POISSONS": "poissons",
            "PRODUITS_LAITIERS": "produits_laitiers",
            "EPICERIE": "epicerie",
            "BOISSONS": "boissons",
            "SURGELES": "surgeles",
            "AUTRES": "autres",
        }
        for name, value in expected.items():
            assert hasattr(IngredientCategory, name)
            assert getattr(IngredientCategory, name).value == value


class TestShoppingListItemCreate:
    """Tests for ShoppingListItemCreate model validation."""

    def test_valid_item_creation(self):
        """Test creating a valid shopping list item."""
        # Monday date
        monday = date(2026, 1, 5)  # This is a Monday
        item = ShoppingListItemCreate(
            ingredient_name="Tomates",
            quantity="500g",
            category=IngredientCategory.LEGUMES,
            week_start=monday,
        )
        assert item.ingredient_name == "Tomates"
        assert item.quantity == "500g"
        assert item.category == IngredientCategory.LEGUMES
        assert item.week_start == monday

    def test_week_start_must_be_monday(self):
        """Test that week_start validation rejects non-Monday dates."""
        # Tuesday date
        tuesday = date(2026, 1, 6)
        with pytest.raises(ValidationError) as exc_info:
            ShoppingListItemCreate(
                ingredient_name="Tomates",
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                week_start=tuesday,
            )
        assert "week_start must be a Monday" in str(exc_info.value)

    def test_ingredient_name_required(self):
        """Test that ingredient_name is required."""
        monday = date(2026, 1, 5)
        with pytest.raises(ValidationError) as exc_info:
            ShoppingListItemCreate(
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                week_start=monday,
            )
        assert "ingredient_name" in str(exc_info.value)

    def test_ingredient_name_min_length(self):
        """Test that ingredient_name must have at least 1 character."""
        monday = date(2026, 1, 5)
        with pytest.raises(ValidationError) as exc_info:
            ShoppingListItemCreate(
                ingredient_name="",
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                week_start=monday,
            )
        assert "ingredient_name" in str(exc_info.value)


class TestShoppingListItemResponse:
    """Tests for ShoppingListItemResponse model."""

    def test_valid_response(self):
        """Test creating a valid response model."""
        now = datetime.now()
        monday = date(2026, 1, 5)
        response = ShoppingListItemResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            user_id="user-123",
            ingredient_name="Tomates",
            quantity="500g",
            category=IngredientCategory.LEGUMES,
            is_checked=False,
            week_start=monday,
            created_at=now,
            updated_at=now,
        )
        assert response.id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.is_checked is False

    def test_is_checked_defaults_behavior(self):
        """Test that is_checked field must be explicitly set (no default in response)."""
        now = datetime.now()
        monday = date(2026, 1, 5)
        # Response model requires is_checked to be set
        with pytest.raises(ValidationError):
            ShoppingListItemResponse(
                id="550e8400-e29b-41d4-a716-446655440000",
                user_id="user-123",
                ingredient_name="Tomates",
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                # is_checked missing
                week_start=monday,
                created_at=now,
                updated_at=now,
            )


class TestCategoryGroupResponse:
    """Tests for CategoryGroupResponse model."""

    def test_valid_category_group(self):
        """Test creating a valid category group response."""
        now = datetime.now()
        monday = date(2026, 1, 5)
        items = [
            ShoppingListItemResponse(
                id="item-1",
                user_id="user-123",
                ingredient_name="Tomates",
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                is_checked=False,
                week_start=monday,
                created_at=now,
                updated_at=now,
            ),
            ShoppingListItemResponse(
                id="item-2",
                user_id="user-123",
                ingredient_name="Oignons",
                quantity="3",
                category=IngredientCategory.LEGUMES,
                is_checked=True,
                week_start=monday,
                created_at=now,
                updated_at=now,
            ),
        ]
        group = CategoryGroupResponse(
            category=IngredientCategory.LEGUMES,
            items=items,
            item_count=2,
        )
        assert group.category == IngredientCategory.LEGUMES
        assert len(group.items) == 2
        assert group.item_count == 2


class TestShoppingListGenerateResponse:
    """Tests for ShoppingListGenerateResponse model."""

    def test_valid_generate_response(self):
        """Test creating a valid generate response."""
        now = datetime.now()
        monday = date(2026, 1, 5)
        items = [
            ShoppingListItemResponse(
                id="item-1",
                user_id="user-123",
                ingredient_name="Tomates",
                quantity="500g",
                category=IngredientCategory.LEGUMES,
                is_checked=False,
                week_start=monday,
                created_at=now,
                updated_at=now,
            ),
        ]
        response = ShoppingListGenerateResponse(
            items=items,
            week_start=monday,
            generated_at=now,
        )
        assert len(response.items) == 1
        assert response.week_start == monday
        assert response.generated_at == now
