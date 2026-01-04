"""Meal slot models for weekly meal planning feature."""

from datetime import date as date_type
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class MealType(str, Enum):
    """Enumeration of meal types."""

    DEJEUNER = "dejeuner"
    DINER = "diner"


class MealSlotCreate(BaseModel):
    """Request model for creating a meal slot."""

    slot_date: date_type = Field(..., description="The date of the meal (YYYY-MM-DD)")
    meal_type: MealType = Field(..., description="Type of meal: dejeuner or diner")
    recipe_id: str = Field(..., min_length=1, max_length=20)
    recipe_name: str = Field(..., min_length=1, max_length=255)
    recipe_thumbnail: str | None = Field(None, max_length=500)
    portions: int | None = Field(None, ge=1, le=20)

    @field_validator("slot_date")
    @classmethod
    def date_not_in_past(cls, v: date_type) -> date_type:
        """Validate that date is not in the past."""
        today = date_type.today()
        if v < today:
            raise ValueError("Cannot create slots for past dates")
        return v


class MealSlotUpdate(BaseModel):
    """Request model for updating a meal slot."""

    recipe_id: str | None = Field(None, min_length=1, max_length=20)
    recipe_name: str | None = Field(None, min_length=1, max_length=255)
    recipe_thumbnail: str | None = Field(None, max_length=500)
    portions: int | None = Field(None, ge=1, le=20)


class MealSlotResponse(BaseModel):
    """Response model for a single meal slot."""

    id: str
    user_id: str
    slot_date: date_type
    meal_type: MealType
    recipe_id: str
    recipe_name: str
    recipe_thumbnail: str | None
    portions: int
    created_at: datetime
    updated_at: datetime


class WeekSlotsResponse(BaseModel):
    """Response model for a week of meal slots."""

    slots: list[MealSlotResponse]
    week_start: date_type
    week_end: date_type


class RecentRecipeResponse(BaseModel):
    """Response model for a recent recipe."""

    recipe_id: str
    recipe_name: str
    recipe_thumbnail: str | None
    last_used: datetime
