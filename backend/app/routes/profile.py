"""Profile API routes.

Defines user profile and preferences endpoints for the ForkIt API.
"""

from fastapi import APIRouter, Depends, status

from app.models.auth import UserResponse
from app.models.preferences import UserPreferencesResponse, UserPreferencesUpdate
from app.routes.auth import get_current_user
from app.services.preferences_service import PreferencesService

router = APIRouter(prefix="/api/profile", tags=["profile"])


def get_preferences_service() -> PreferencesService:
    """Dependency to get preferences service instance."""
    return PreferencesService()


@router.get("/preferences", response_model=UserPreferencesResponse)
def get_preferences(
    current_user: UserResponse = Depends(get_current_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
) -> UserPreferencesResponse:
    """Get current user's preferences.

    Args:
        current_user: Current authenticated user.
        preferences_service: Preferences service instance.

    Returns:
        User's dietary preferences, allergies, ingredients, and portions.
    """
    return preferences_service.get_preferences(current_user.id)


@router.put("/preferences", response_model=UserPreferencesResponse)
def update_preferences(
    data: UserPreferencesUpdate,
    current_user: UserResponse = Depends(get_current_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
) -> UserPreferencesResponse:
    """Update current user's preferences.

    Performs a full replacement of all preferences.
    Validates dietary incompatibilities and ingredient limits via Pydantic.

    Args:
        data: New preferences data.
        current_user: Current authenticated user.
        preferences_service: Preferences service instance.

    Returns:
        Updated preferences with optional warning for halal+kosher combination.
    """
    return preferences_service.update_preferences(current_user.id, data)
