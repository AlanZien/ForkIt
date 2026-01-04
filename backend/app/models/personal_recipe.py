"""Personal recipe models for the personal recipe management feature.

This module contains Pydantic models for creating, updating, and responding
to personal recipe operations.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    """Request model for creating an ingredient."""

    name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    note: str | None = Field(None, max_length=255)


class InstructionStepCreate(BaseModel):
    """Request model for creating an instruction step."""

    instruction: str = Field(..., min_length=1)


class PersonalRecipeCreate(BaseModel):
    """Request model for creating a personal recipe."""

    title: str = Field(..., min_length=1, max_length=255)
    image_url: str | None = Field(None, max_length=500)
    servings: int = Field(..., ge=1, le=20)
    prep_time_minutes: int | None = Field(None, ge=0)
    cook_time_minutes: int | None = Field(None, ge=0)
    tags: list[str] | None = None
    ingredients: list[IngredientCreate] = Field(..., min_length=1)
    steps: list[InstructionStepCreate] = Field(..., min_length=1)


class PersonalRecipeUpdate(BaseModel):
    """Request model for updating a personal recipe.

    All fields are optional for partial updates. However, if ingredients or
    steps are provided, they must have at least one item.
    """

    title: str | None = Field(None, min_length=1, max_length=255)
    image_url: str | None = Field(None, max_length=500)
    servings: int | None = Field(None, ge=1, le=20)
    prep_time_minutes: int | None = Field(None, ge=0)
    cook_time_minutes: int | None = Field(None, ge=0)
    tags: list[str] | None = None
    ingredients: list[IngredientCreate] | None = Field(None, min_length=1)
    steps: list[InstructionStepCreate] | None = Field(None, min_length=1)


class IngredientResponse(BaseModel):
    """Response model for an ingredient."""

    id: str
    name: str
    quantity: float
    unit: str
    note: str | None
    sort_order: int


class InstructionStepResponse(BaseModel):
    """Response model for an instruction step."""

    id: str
    step_number: int
    instruction: str


class PersonalRecipeResponse(BaseModel):
    """Response model for a full personal recipe with nested data."""

    id: str
    user_id: str
    title: str
    image_url: str | None
    servings: int
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    tags: list[str] | None
    source_recipe_id: str | None
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientResponse]
    steps: list[InstructionStepResponse]


class PersonalRecipeSummary(BaseModel):
    """Summary model for search results.

    Used in unified search to identify the source of the recipe.
    """

    id: str
    title: str
    image_url: str | None
    source: Literal["personal", "api"]


class PersonalRecipeListResponse(BaseModel):
    """Response model for list of personal recipes."""

    recipes: list[PersonalRecipeSummary]
    count: int
