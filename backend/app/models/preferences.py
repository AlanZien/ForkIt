"""User Preferences Pydantic models.

Defines request/response schemas for user dietary preferences, allergies,
excluded/preferred ingredients, and portions settings.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class DietaryType(str, Enum):
    """Dietary preference types.

    7 dietary types as specified in spec.md:
    - Vegetarian, Vegan, No Pork, No Beef, Pescetarian, Halal, Kosher
    """

    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    NO_PORK = "no_pork"
    NO_BEEF = "no_beef"
    PESCETARIAN = "pescetarian"
    HALAL = "halal"
    KOSHER = "kosher"


class AllergyType(str, Enum):
    """Allergy types.

    11 allergen types as specified in spec.md:
    Gluten, Lactose, Tree Nuts, Peanuts, Eggs, Fish,
    Shellfish, Soy, Sesame, Mustard, Celery
    """

    GLUTEN = "gluten"
    LACTOSE = "lactose"
    TREE_NUTS = "tree_nuts"
    PEANUTS = "peanuts"
    EGGS = "eggs"
    FISH = "fish"
    SHELLFISH = "shellfish"
    SOY = "soy"
    SESAME = "sesame"
    MUSTARD = "mustard"
    CELERY = "celery"


def normalize_ingredient(value: str) -> str:
    """Normalize ingredient name: trim whitespace and convert to lowercase.

    Args:
        value: Raw ingredient name input.

    Returns:
        Normalized ingredient name (trimmed and lowercased).
    """
    return value.strip().lower()


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


class UserDietaryPreference(BaseModel):
    """User dietary preference model for database records.

    Represents a single dietary preference for a user.
    Stored in user_dietary_preferences table.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    dietary_type: DietaryType
    created_at: datetime = Field(default_factory=utc_now)


class UserAllergy(BaseModel):
    """User allergy model for database records.

    Represents a single allergy for a user.
    Stored in user_allergies table.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    allergy_type: AllergyType
    created_at: datetime = Field(default_factory=utc_now)


class UserExcludedIngredient(BaseModel):
    """User excluded ingredient model for database records.

    Represents a single excluded ingredient for a user.
    Stored in user_excluded_ingredients table.
    Ingredient name is automatically normalized (trimmed + lowercased).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    ingredient_name: str
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("ingredient_name")
    @classmethod
    def normalize_and_validate_ingredient_name(cls, v: str) -> str:
        """Normalize ingredient name and validate it's not empty.

        Applies trim() + lowercase normalization.
        Raises ValueError if result is empty.
        """
        normalized = normalize_ingredient(v)
        if not normalized:
            raise ValueError("Ingredient name cannot be empty")
        return normalized


class UserPreferredIngredient(BaseModel):
    """User preferred ingredient model for database records.

    Represents a single preferred ingredient for a user.
    Stored in user_preferred_ingredients table.
    Ingredient name is automatically normalized (trimmed + lowercased).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    ingredient_name: str
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("ingredient_name")
    @classmethod
    def normalize_and_validate_ingredient_name(cls, v: str) -> str:
        """Normalize ingredient name and validate it's not empty.

        Applies trim() + lowercase normalization.
        Raises ValueError if result is empty.
        """
        normalized = normalize_ingredient(v)
        if not normalized:
            raise ValueError("Ingredient name cannot be empty")
        return normalized


class UserSettings(BaseModel):
    """User settings model for portions count.

    Stored as a column in the users table.
    """

    user_id: str
    portions_count: Annotated[int, Field(ge=1, le=20)] = 2


class UserPreferencesResponse(BaseModel):
    """API response model for user preferences.

    Returns all user preferences in a single response.
    Used by GET /api/profile/preferences endpoint.
    """

    dietary_preferences: list[DietaryType] = Field(default_factory=list)
    allergies: list[AllergyType] = Field(default_factory=list)
    excluded_ingredients: list[str] = Field(default_factory=list)
    preferred_ingredients: list[str] = Field(default_factory=list)
    portions_count: int = 2
    warning: str | None = None


class UserPreferencesUpdate(BaseModel):
    """API request model for updating user preferences.

    Validates and normalizes all preference data before update.
    Used by PUT /api/profile/preferences endpoint.
    """

    dietary_preferences: list[DietaryType] = Field(default_factory=list)
    allergies: list[AllergyType] = Field(default_factory=list)
    excluded_ingredients: list[str] = Field(default_factory=list)
    preferred_ingredients: list[str] = Field(default_factory=list)
    portions_count: Annotated[int, Field(ge=1, le=20)] = 2

    @field_validator("excluded_ingredients", "preferred_ingredients", mode="before")
    @classmethod
    def normalize_and_deduplicate_ingredients(cls, v: list[str]) -> list[str]:
        """Normalize, filter empty strings, and deduplicate ingredient lists.

        Applies:
        - trim() + lowercase normalization
        - Filters out empty strings
        - Removes duplicates (preserving order)
        """
        if not v:
            return []

        seen: set[str] = set()
        result: list[str] = []

        for item in v:
            normalized = normalize_ingredient(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)

        return result

    @field_validator("excluded_ingredients", "preferred_ingredients")
    @classmethod
    def validate_ingredients_limit(cls, v: list[str]) -> list[str]:
        """Validate that ingredient list doesn't exceed 30 items.

        Requirement: spec.md "Gestion des ingredients > Limite stricte de 30 tags"
        """
        if len(v) > 30:
            raise ValueError("Maximum 30 ingredients allowed per category")
        return v

    @model_validator(mode="after")
    def validate_dietary_incompatibilities(self) -> "UserPreferencesUpdate":
        """Validate dietary preference incompatibilities.

        Requirement: spec.md "Gestion des regimes > Vegetalien incompatible avec..."

        Raises:
            ValueError: If incompatible dietary preferences are selected.
        """
        if DietaryType.VEGAN in self.dietary_preferences:
            incompatible = {
                DietaryType.PESCETARIAN,
                DietaryType.NO_BEEF,
                DietaryType.NO_PORK,
            }
            conflicts = incompatible.intersection(set(self.dietary_preferences))
            if conflicts:
                conflict_names = [c.value.replace("_", " ").title() for c in conflicts]
                raise ValueError(
                    f"Vegan is incompatible with: {', '.join(conflict_names)}"
                )

        return self
