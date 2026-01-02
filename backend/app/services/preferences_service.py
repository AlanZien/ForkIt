"""Preferences service.

Handles all user preferences operations with Supabase.
"""

import logging
from typing import Any, cast

from app.models.preferences import (
    AllergyType,
    DietaryType,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)
from app.services.supabase import get_supabase_admin

logger = logging.getLogger(__name__)


class PreferencesError(Exception):
    """Base preferences error with generic message."""

    def __init__(self, message: str = "Preferences operation failed"):
        self.message = message
        super().__init__(self.message)


class PreferencesValidationError(PreferencesError):
    """Raised when preferences validation fails."""

    def __init__(self, message: str = "Preferences validation failed"):
        super().__init__(message)


class PreferencesService:
    """Service for user preferences operations."""

    def __init__(self) -> None:
        """Initialize preferences service."""
        self.client = get_supabase_admin()

    def get_preferences(self, user_id: str) -> UserPreferencesResponse:
        """Get all preferences for a user.

        Args:
            user_id: User's UUID.

        Returns:
            UserPreferencesResponse with all user preferences.

        Raises:
            PreferencesError: If database operation fails.
        """
        try:
            # Fetch dietary preferences
            dietary_response = (
                self.client.table("user_dietary_preferences")
                .select("dietary_type")
                .eq("user_id", user_id)
                .execute()
            )
            dietary_data = cast(list[dict[str, Any]], dietary_response.data)
            dietary_preferences = [
                DietaryType(item["dietary_type"]) for item in dietary_data
            ]

            # Fetch allergies
            allergy_response = (
                self.client.table("user_allergies")
                .select("allergy_type")
                .eq("user_id", user_id)
                .execute()
            )
            allergy_data = cast(list[dict[str, Any]], allergy_response.data)
            allergies = [AllergyType(item["allergy_type"]) for item in allergy_data]

            # Fetch excluded ingredients
            excluded_response = (
                self.client.table("user_excluded_ingredients")
                .select("ingredient_name")
                .eq("user_id", user_id)
                .execute()
            )
            excluded_data = cast(list[dict[str, Any]], excluded_response.data)
            excluded_ingredients: list[str] = [
                item["ingredient_name"] for item in excluded_data
            ]

            # Fetch preferred ingredients
            preferred_response = (
                self.client.table("user_preferred_ingredients")
                .select("ingredient_name")
                .eq("user_id", user_id)
                .execute()
            )
            preferred_data = cast(list[dict[str, Any]], preferred_response.data)
            preferred_ingredients: list[str] = [
                item["ingredient_name"] for item in preferred_data
            ]

            # Fetch user settings (portions_count)
            settings_response = (
                self.client.table("user_settings")
                .select("portions_count")
                .eq("user_id", user_id)
                .execute()
            )
            settings_data = cast(list[dict[str, Any]], settings_response.data)
            portions_count: int = (
                settings_data[0]["portions_count"]
                if settings_data
                else 2  # Default value
            )

            return UserPreferencesResponse(
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                excluded_ingredients=excluded_ingredients,
                preferred_ingredients=preferred_ingredients,
                portions_count=portions_count,
            )

        except Exception as e:
            logger.error(f"Get preferences error: {e}")
            raise PreferencesError("Failed to retrieve preferences")

    def update_preferences(
        self, user_id: str, data: UserPreferencesUpdate
    ) -> UserPreferencesResponse:
        """Update all preferences for a user.

        Performs a full replace of all preferences (delete old, insert new).
        Validates dietary incompatibilities before saving.

        Args:
            user_id: User's UUID.
            data: New preferences data (already validated by Pydantic).

        Returns:
            UserPreferencesResponse with updated preferences and optional warning.

        Raises:
            PreferencesValidationError: If validation fails.
            PreferencesError: If database operation fails.
        """
        try:
            warning = self._check_halal_kosher_warning(data.dietary_preferences)

            # Delete existing dietary preferences
            self.client.table("user_dietary_preferences").delete().eq(
                "user_id", user_id
            ).execute()

            # Insert new dietary preferences
            if data.dietary_preferences:
                dietary_records = [
                    {"user_id": user_id, "dietary_type": pref.value}
                    for pref in data.dietary_preferences
                ]
                self.client.table("user_dietary_preferences").insert(
                    dietary_records
                ).execute()

            # Delete existing allergies
            self.client.table("user_allergies").delete().eq(
                "user_id", user_id
            ).execute()

            # Insert new allergies
            if data.allergies:
                allergy_records = [
                    {"user_id": user_id, "allergy_type": allergy.value}
                    for allergy in data.allergies
                ]
                self.client.table("user_allergies").insert(allergy_records).execute()

            # Delete existing excluded ingredients
            self.client.table("user_excluded_ingredients").delete().eq(
                "user_id", user_id
            ).execute()

            # Insert new excluded ingredients (already normalized by Pydantic)
            if data.excluded_ingredients:
                excluded_records = [
                    {"user_id": user_id, "ingredient_name": ing}
                    for ing in data.excluded_ingredients
                ]
                self.client.table("user_excluded_ingredients").insert(
                    excluded_records
                ).execute()

            # Delete existing preferred ingredients
            self.client.table("user_preferred_ingredients").delete().eq(
                "user_id", user_id
            ).execute()

            # Insert new preferred ingredients (already normalized by Pydantic)
            if data.preferred_ingredients:
                preferred_records = [
                    {"user_id": user_id, "ingredient_name": ing}
                    for ing in data.preferred_ingredients
                ]
                self.client.table("user_preferred_ingredients").insert(
                    preferred_records
                ).execute()

            # Upsert user settings
            self.client.table("user_settings").upsert(
                {"user_id": user_id, "portions_count": data.portions_count},
                on_conflict="user_id",
            ).execute()

            return UserPreferencesResponse(
                dietary_preferences=data.dietary_preferences,
                allergies=data.allergies,
                excluded_ingredients=data.excluded_ingredients,
                preferred_ingredients=data.preferred_ingredients,
                portions_count=data.portions_count,
                warning=warning,
            )

        except PreferencesValidationError:
            raise
        except Exception as e:
            logger.error(f"Update preferences error: {e}")
            raise PreferencesError("Failed to update preferences")

    def _check_halal_kosher_warning(
        self, dietary_preferences: list[DietaryType]
    ) -> str | None:
        """Check if HALAL and KOSHER are both selected and return warning.

        Args:
            dietary_preferences: List of dietary preferences.

        Returns:
            Warning message if HALAL + KOSHER, None otherwise.
        """
        if (
            DietaryType.HALAL in dietary_preferences
            and DietaryType.KOSHER in dietary_preferences
        ):
            return "Verify the coherence of this combination"
        return None
