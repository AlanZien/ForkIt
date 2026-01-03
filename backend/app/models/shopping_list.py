"""Shopping list models for the shopping list generation feature."""

from datetime import date as date_type
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class IngredientCategory(str, Enum):
    """Enumeration of ingredient categories for shopping list grouping."""

    LEGUMES = "legumes"
    VIANDES = "viandes"
    POISSONS = "poissons"
    PRODUITS_LAITIERS = "produits_laitiers"
    EPICERIE = "epicerie"
    BOISSONS = "boissons"
    SURGELES = "surgeles"
    AUTRES = "autres"


class ShoppingListItemBase(BaseModel):
    """Base model for shopping list item fields."""

    ingredient_name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the ingredient"
    )
    quantity: str = Field(
        ..., min_length=1, max_length=100, description="Quantity with unit"
    )
    category: IngredientCategory = Field(
        ..., description="Category for grouping in shopping list"
    )


class ShoppingListItemCreate(ShoppingListItemBase):
    """Request model for creating a shopping list item."""

    week_start: date_type = Field(
        ..., description="Monday of the week (YYYY-MM-DD)"
    )

    @field_validator("week_start")
    @classmethod
    def week_start_must_be_monday(cls, v: date_type) -> date_type:
        """Validate that week_start is a Monday."""
        if v.weekday() != 0:
            raise ValueError("week_start must be a Monday")
        return v


class ShoppingListItemResponse(BaseModel):
    """Response model for a single shopping list item."""

    id: str
    user_id: str
    ingredient_name: str
    quantity: str
    category: IngredientCategory
    is_checked: bool
    week_start: date_type
    created_at: datetime
    updated_at: datetime


class ShoppingListGenerateResponse(BaseModel):
    """Response model for shopping list generation."""

    items: list[ShoppingListItemResponse]
    week_start: date_type
    generated_at: datetime


class CategoryGroupResponse(BaseModel):
    """Response model for items grouped by category."""

    category: IngredientCategory
    items: list[ShoppingListItemResponse]
    item_count: int


class ShoppingListResponse(BaseModel):
    """Response model for the full shopping list grouped by category."""

    categories: list[CategoryGroupResponse]
    week_start: date_type
    total_items: int
    checked_count: int


class ToggleItemResponse(BaseModel):
    """Response model for toggling an item's checked state."""

    item: ShoppingListItemResponse
    is_checked: bool


class UncheckAllResponse(BaseModel):
    """Response model for unchecking all items."""

    count: int
    message: str
