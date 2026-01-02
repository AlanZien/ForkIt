"""API routes for recipe favorites."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth import UserResponse
from app.models.favorite import (
    FavoriteCreate,
    FavoriteListResponse,
    FavoriteResponse,
    FavoriteStatus,
)
from app.routes.auth import get_current_user
from app.services.favorites_service import FavoritesService

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


def get_favorites_service() -> FavoritesService:
    """Dependency to get favorites service instance."""
    return FavoritesService()


@router.get("", response_model=FavoriteListResponse)
async def get_favorites(
    current_user: UserResponse = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> FavoriteListResponse:
    """Get all favorites for the current user."""
    user_id = current_user.id
    favorites = service.get_favorites(user_id)

    return FavoriteListResponse(favorites=favorites, count=len(favorites))


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    data: FavoriteCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> FavoriteResponse:
    """Add a recipe to favorites."""
    user_id = current_user.id

    try:
        return service.add_favorite(user_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add favorite: {e!s}",
        ) from e


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    recipe_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> None:
    """Remove a recipe from favorites."""
    user_id = current_user.id
    service.remove_favorite(user_id, recipe_id)


@router.get("/{recipe_id}", response_model=FavoriteStatus)
async def check_favorite(
    recipe_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service),
) -> FavoriteStatus:
    """Check if a recipe is in favorites."""
    user_id = current_user.id
    is_fav = service.is_favorite(user_id, recipe_id)

    return FavoriteStatus(is_favorite=is_fav)
