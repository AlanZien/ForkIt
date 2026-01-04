"""Favorite models for recipe favorites feature."""

from datetime import datetime

from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    """Request model for creating a favorite."""

    recipe_id: str = Field(..., min_length=1, max_length=20)
    recipe_name: str = Field(..., min_length=1, max_length=255)
    recipe_thumbnail: str | None = Field(None, max_length=500)


class FavoriteResponse(BaseModel):
    """Response model for a single favorite."""

    id: str
    recipe_id: str
    recipe_name: str
    recipe_thumbnail: str | None
    created_at: datetime


class FavoriteListResponse(BaseModel):
    """Response model for list of favorites."""

    favorites: list[FavoriteResponse]
    count: int


class FavoriteStatus(BaseModel):
    """Response model for favorite status check."""

    is_favorite: bool
