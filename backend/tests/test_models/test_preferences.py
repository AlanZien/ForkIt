"""Tests for preferences Pydantic models - TDD approach.

These tests define the expected validation behavior of preferences models.
Following test-plan.md specifications for Database Layer tests 1-20.
"""

import pytest
from pydantic import ValidationError


class TestDietaryType:
    """Tests for DietaryType enum validation."""

    def test_dietary_type_enum_has_all_required_values(self):
        """Test that DietaryType enum has all 7 required diet types.

        Given: DietaryType enum definition
        When: Checking enum values
        Then: Contains VEGETARIAN, VEGAN, NO_PORK, NO_BEEF, PESCETARIAN, HALAL, KOSHER
        Requirement: spec.md "Gestion des regimes alimentaires > 7 regimes"
        """
        from app.models.preferences import DietaryType

        expected_values = {
            "VEGETARIAN",
            "VEGAN",
            "NO_PORK",
            "NO_BEEF",
            "PESCETARIAN",
            "HALAL",
            "KOSHER",
        }
        actual_values = {e.name for e in DietaryType}
        assert actual_values == expected_values

    def test_dietary_type_enum_values_are_lowercase(self):
        """Test that DietaryType enum values are lowercase for DB storage.

        Given: DietaryType enum
        When: Checking enum values (not names)
        Then: Values are lowercase strings matching spec
        """
        from app.models.preferences import DietaryType

        assert DietaryType.VEGETARIAN.value == "vegetarian"
        assert DietaryType.VEGAN.value == "vegan"
        assert DietaryType.NO_PORK.value == "no_pork"
        assert DietaryType.NO_BEEF.value == "no_beef"
        assert DietaryType.PESCETARIAN.value == "pescetarian"
        assert DietaryType.HALAL.value == "halal"
        assert DietaryType.KOSHER.value == "kosher"


class TestAllergyType:
    """Tests for AllergyType enum validation."""

    def test_allergy_type_enum_has_all_required_values(self):
        """Test that AllergyType enum has all 11 required allergy types.

        Given: AllergyType enum definition
        When: Checking enum values
        Then: Contains all 11 allergies from spec
        Requirement: spec.md "Gestion des allergies > 10 allergenes principaux"
        """
        from app.models.preferences import AllergyType

        expected_values = {
            "GLUTEN",
            "LACTOSE",
            "TREE_NUTS",
            "PEANUTS",
            "EGGS",
            "FISH",
            "SHELLFISH",
            "SOY",
            "SESAME",
            "MUSTARD",
            "CELERY",
        }
        actual_values = {e.name for e in AllergyType}
        assert actual_values == expected_values

    def test_allergy_type_enum_values_are_lowercase(self):
        """Test that AllergyType enum values are lowercase for DB storage."""
        from app.models.preferences import AllergyType

        assert AllergyType.GLUTEN.value == "gluten"
        assert AllergyType.LACTOSE.value == "lactose"
        assert AllergyType.TREE_NUTS.value == "tree_nuts"
        assert AllergyType.PEANUTS.value == "peanuts"
        assert AllergyType.EGGS.value == "eggs"
        assert AllergyType.FISH.value == "fish"
        assert AllergyType.SHELLFISH.value == "shellfish"
        assert AllergyType.SOY.value == "soy"
        assert AllergyType.SESAME.value == "sesame"
        assert AllergyType.MUSTARD.value == "mustard"
        assert AllergyType.CELERY.value == "celery"


class TestUserDietaryPreference:
    """Tests for UserDietaryPreference model validation."""

    def test_valid_dietary_preference_creation(self):
        """Test that valid dietary preference data passes validation.

        Given: Valid user_id and dietary_type
        When: Creating UserDietaryPreference
        Then: Model is created successfully with all fields
        Requirement: spec.md "Schema de base de donnees > user_dietary_preferences"
        """
        from app.models.preferences import DietaryType, UserDietaryPreference

        pref = UserDietaryPreference(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            dietary_type=DietaryType.VEGETARIAN,
        )

        assert pref.user_id == "550e8400-e29b-41d4-a716-446655440000"
        assert pref.dietary_type == DietaryType.VEGETARIAN
        assert pref.id is not None  # UUID auto-generated

    def test_dietary_preference_requires_user_id(self):
        """Test that user_id is required.

        Given: Missing user_id
        When: Creating UserDietaryPreference
        Then: ValidationError is raised
        """
        from app.models.preferences import DietaryType, UserDietaryPreference

        with pytest.raises(ValidationError):
            UserDietaryPreference(dietary_type=DietaryType.VEGETARIAN)

    def test_dietary_preference_requires_dietary_type(self):
        """Test that dietary_type is required.

        Given: Missing dietary_type
        When: Creating UserDietaryPreference
        Then: ValidationError is raised
        """
        from app.models.preferences import UserDietaryPreference

        with pytest.raises(ValidationError):
            UserDietaryPreference(user_id="550e8400-e29b-41d4-a716-446655440000")

    def test_dietary_preference_invalid_enum_value(self):
        """Test that invalid dietary_type raises validation error.

        Given: dietary_type = "invalid_diet" (not in enum)
        When: Creating UserDietaryPreference
        Then: ValidationError is raised
        Requirement: spec.md "Gestion des regimes > 7 regimes"
        """
        from app.models.preferences import UserDietaryPreference

        with pytest.raises(ValidationError):
            UserDietaryPreference(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                dietary_type="invalid_diet",
            )


class TestUserAllergy:
    """Tests for UserAllergy model validation."""

    def test_valid_allergy_creation(self):
        """Test that valid allergy data passes validation.

        Given: Valid user_id and allergy_type
        When: Creating UserAllergy
        Then: Model is created successfully
        Requirement: spec.md "Gestion des allergies"
        """
        from app.models.preferences import AllergyType, UserAllergy

        allergy = UserAllergy(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            allergy_type=AllergyType.GLUTEN,
        )

        assert allergy.user_id == "550e8400-e29b-41d4-a716-446655440000"
        assert allergy.allergy_type == AllergyType.GLUTEN
        assert allergy.id is not None

    def test_allergy_requires_user_id(self):
        """Test that user_id is required."""
        from app.models.preferences import AllergyType, UserAllergy

        with pytest.raises(ValidationError):
            UserAllergy(allergy_type=AllergyType.GLUTEN)

    def test_allergy_invalid_enum_value(self):
        """Test that invalid allergy_type raises validation error."""
        from app.models.preferences import UserAllergy

        with pytest.raises(ValidationError):
            UserAllergy(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                allergy_type="invalid_allergy",
            )


class TestUserExcludedIngredient:
    """Tests for UserExcludedIngredient model validation."""

    def test_valid_excluded_ingredient_creation(self):
        """Test that valid excluded ingredient data passes validation.

        Given: Valid user_id and ingredient_name
        When: Creating UserExcludedIngredient
        Then: Model is created successfully
        """
        from app.models.preferences import UserExcludedIngredient

        ingredient = UserExcludedIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="tomate",
        )

        assert ingredient.user_id == "550e8400-e29b-41d4-a716-446655440000"
        assert ingredient.ingredient_name == "tomate"

    def test_excluded_ingredient_normalization_trim(self):
        """Test that ingredient_name is trimmed.

        Given: Saisie: "  Tomate  " (avec espaces)
        When: Creating UserExcludedIngredient
        Then: Stockage normalise sans espaces
        Requirement: spec.md "Gestion des ingredients > Normalisation automatique"
        """
        from app.models.preferences import UserExcludedIngredient

        ingredient = UserExcludedIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="  tomate  ",
        )

        assert ingredient.ingredient_name == "tomate"

    def test_excluded_ingredient_normalization_lowercase(self):
        """Test that ingredient_name is converted to lowercase.

        Given: Saisie: "TOMATE"
        When: Creating UserExcludedIngredient
        Then: Stockage normalise: "tomate" (lowercase)
        Requirement: spec.md "Gestion des ingredients > Normalisation automatique"
        """
        from app.models.preferences import UserExcludedIngredient

        ingredient = UserExcludedIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="TOMATE",
        )

        assert ingredient.ingredient_name == "tomate"

    def test_excluded_ingredient_full_normalization(self):
        """Test trim + lowercase combined.

        Given: Saisie: "  TOMATE  "
        When: Creating UserExcludedIngredient
        Then: Stockage: "tomate"
        """
        from app.models.preferences import UserExcludedIngredient

        ingredient = UserExcludedIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="  TOMATE  ",
        )

        assert ingredient.ingredient_name == "tomate"

    def test_excluded_ingredient_requires_user_id(self):
        """Test that user_id is required."""
        from app.models.preferences import UserExcludedIngredient

        with pytest.raises(ValidationError):
            UserExcludedIngredient(ingredient_name="tomate")

    def test_excluded_ingredient_requires_ingredient_name(self):
        """Test that ingredient_name is required."""
        from app.models.preferences import UserExcludedIngredient

        with pytest.raises(ValidationError):
            UserExcludedIngredient(
                user_id="550e8400-e29b-41d4-a716-446655440000",
            )

    def test_excluded_ingredient_empty_name_rejected(self):
        """Test that empty ingredient name is rejected.

        Given: ingredient_name = "" or "   "
        When: Creating UserExcludedIngredient
        Then: ValidationError is raised
        Requirement: spec.md "Gestion des ingredients > Validation"
        """
        from app.models.preferences import UserExcludedIngredient

        with pytest.raises(ValidationError):
            UserExcludedIngredient(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                ingredient_name="",
            )

        with pytest.raises(ValidationError):
            UserExcludedIngredient(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                ingredient_name="   ",
            )


class TestUserPreferredIngredient:
    """Tests for UserPreferredIngredient model validation."""

    def test_valid_preferred_ingredient_creation(self):
        """Test that valid preferred ingredient data passes validation.

        Given: Valid user_id and ingredient_name "Basilic"
        When: Creating UserPreferredIngredient
        Then: Stockage normalise: "basilic"
        Requirement: spec.md "Gestion des ingredients > Tables separees"
        """
        from app.models.preferences import UserPreferredIngredient

        ingredient = UserPreferredIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="Basilic",
        )

        assert ingredient.ingredient_name == "basilic"

    def test_preferred_ingredient_normalization(self):
        """Test that preferred ingredient is normalized (trim + lowercase)."""
        from app.models.preferences import UserPreferredIngredient

        ingredient = UserPreferredIngredient(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            ingredient_name="  BASILIC  ",
        )

        assert ingredient.ingredient_name == "basilic"


class TestPortionsCount:
    """Tests for portions_count validation."""

    def test_portions_count_valid_range(self):
        """Test that valid portions_count (1-20) is accepted.

        Given: portions_count in range 1-20
        When: Creating UserSettings
        Then: Value is accepted
        Requirement: spec.md "Nombre de portions > Validation: 1-20"
        """
        from app.models.preferences import UserSettings

        settings = UserSettings(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            portions_count=4,
        )

        assert settings.portions_count == 4

    def test_portions_count_minimum_value(self):
        """Test that portions_count = 1 is valid (minimum)."""
        from app.models.preferences import UserSettings

        settings = UserSettings(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            portions_count=1,
        )

        assert settings.portions_count == 1

    def test_portions_count_maximum_value(self):
        """Test that portions_count = 20 is valid (maximum)."""
        from app.models.preferences import UserSettings

        settings = UserSettings(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            portions_count=20,
        )

        assert settings.portions_count == 20

    def test_portions_count_below_minimum_rejected(self):
        """Test that portions_count < 1 is rejected.

        Given: portions_count = 0
        When: Creating UserSettings
        Then: ValidationError with message about range 1-20
        Requirement: spec.md "Nombre de portions > Validation: minimum 1"
        """
        from app.models.preferences import UserSettings

        with pytest.raises(ValidationError) as exc_info:
            UserSettings(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                portions_count=0,
            )

        errors = exc_info.value.errors()
        assert any(
            "1" in str(e) or "greater" in str(e).lower() or "minimum" in str(e).lower()
            for e in errors
        )

    def test_portions_count_above_maximum_rejected(self):
        """Test that portions_count > 20 is rejected.

        Given: portions_count = 21 or 25
        When: Creating UserSettings
        Then: ValidationError with message about range 1-20
        Requirement: spec.md "Nombre de portions > Validation: maximum 20"
        """
        from app.models.preferences import UserSettings

        with pytest.raises(ValidationError) as exc_info:
            UserSettings(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                portions_count=21,
            )

        errors = exc_info.value.errors()
        assert any(
            "20" in str(e) or "less" in str(e).lower() or "maximum" in str(e).lower()
            for e in errors
        )

    def test_portions_count_default_value(self):
        """Test that portions_count defaults to 2.

        Given: No portions_count specified
        When: Creating UserSettings
        Then: Default value is 2
        Requirement: tasks.md "default: 2"
        """
        from app.models.preferences import UserSettings

        settings = UserSettings(
            user_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert settings.portions_count == 2


class TestUserPreferencesResponse:
    """Tests for UserPreferencesResponse model (API response)."""

    def test_preferences_response_with_all_fields(self):
        """Test complete preferences response structure.

        Given: Complete user preferences data
        When: Creating UserPreferencesResponse
        Then: All fields are correctly populated
        Requirement: spec.md "Architecture API Backend > GET /api/profile/preferences"
        """
        from app.models.preferences import (
            AllergyType,
            DietaryType,
            UserPreferencesResponse,
        )

        response = UserPreferencesResponse(
            dietary_preferences=[DietaryType.VEGETARIAN, DietaryType.NO_PORK],
            allergies=[AllergyType.GLUTEN, AllergyType.LACTOSE],
            excluded_ingredients=["tomate", "oignon"],
            preferred_ingredients=["basilic", "thym"],
            portions_count=4,
        )

        assert len(response.dietary_preferences) == 2
        assert DietaryType.VEGETARIAN in response.dietary_preferences
        assert len(response.allergies) == 2
        assert AllergyType.GLUTEN in response.allergies
        assert response.excluded_ingredients == ["tomate", "oignon"]
        assert response.preferred_ingredients == ["basilic", "thym"]
        assert response.portions_count == 4

    def test_preferences_response_empty_defaults(self):
        """Test preferences response with empty/default values.

        Given: New user without preferences
        When: Creating UserPreferencesResponse with defaults
        Then: Empty lists and default portions_count
        Requirement: spec.md "GET preferences > New user returns empty defaults"
        """
        from app.models.preferences import UserPreferencesResponse

        response = UserPreferencesResponse(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=2,
        )

        assert response.dietary_preferences == []
        assert response.allergies == []
        assert response.excluded_ingredients == []
        assert response.preferred_ingredients == []
        assert response.portions_count == 2


class TestUserPreferencesUpdate:
    """Tests for UserPreferencesUpdate model (API request)."""

    def test_preferences_update_valid_payload(self):
        """Test valid preferences update payload.

        Given: Valid complete preferences payload
        When: Creating UserPreferencesUpdate
        Then: All fields validated correctly
        Requirement: spec.md "Architecture API Backend > PUT /api/profile/preferences"
        """
        from app.models.preferences import (
            AllergyType,
            DietaryType,
            UserPreferencesUpdate,
        )

        update = UserPreferencesUpdate(
            dietary_preferences=[DietaryType.VEGETARIAN],
            allergies=[AllergyType.GLUTEN],
            excluded_ingredients=["tomate"],
            preferred_ingredients=["basilic"],
            portions_count=3,
        )

        assert len(update.dietary_preferences) == 1
        assert update.portions_count == 3

    def test_preferences_update_excluded_ingredients_limit_30(self):
        """Test that excluded ingredients are limited to 30.

        Given: excluded_ingredients with 31 items
        When: Creating UserPreferencesUpdate
        Then: ValidationError with message about 30 max
        Requirement: spec.md "Gestion des ingredients > Limite stricte de 30 tags"
        """
        from app.models.preferences import UserPreferencesUpdate

        # Create list of 31 ingredients
        ingredients_31 = [f"ingredient_{i}" for i in range(31)]

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[],
                allergies=[],
                excluded_ingredients=ingredients_31,
                preferred_ingredients=[],
                portions_count=2,
            )

        errors = exc_info.value.errors()
        assert any("30" in str(e) for e in errors)

    def test_preferences_update_preferred_ingredients_limit_30(self):
        """Test that preferred ingredients are limited to 30.

        Given: preferred_ingredients with 31 items
        When: Creating UserPreferencesUpdate
        Then: ValidationError with message about 30 max
        Requirement: spec.md "Gestion des ingredients > Limite stricte de 30 tags"
        """
        from app.models.preferences import UserPreferencesUpdate

        # Create list of 31 ingredients
        ingredients_31 = [f"ingredient_{i}" for i in range(31)]

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[],
                allergies=[],
                excluded_ingredients=[],
                preferred_ingredients=ingredients_31,
                portions_count=2,
            )

        errors = exc_info.value.errors()
        assert any("30" in str(e) for e in errors)

    def test_preferences_update_30_ingredients_each_allowed(self):
        """Test that 30 ingredients in each category is allowed.

        Given: 30 excluded AND 30 preferred ingredients
        When: Creating UserPreferencesUpdate
        Then: Validation passes (separate limits)
        Requirement: spec.md "Gestion des ingredients > 30 tags maximum par categorie"
        """
        from app.models.preferences import UserPreferencesUpdate

        excluded_30 = [f"excluded_{i}" for i in range(30)]
        preferred_30 = [f"preferred_{i}" for i in range(30)]

        update = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=excluded_30,
            preferred_ingredients=preferred_30,
            portions_count=2,
        )

        assert len(update.excluded_ingredients) == 30
        assert len(update.preferred_ingredients) == 30

    def test_preferences_update_ingredients_normalized(self):
        """Test that ingredients are normalized on update.

        Given: excluded_ingredients: ["  TOMATE  ", "Oignon"]
        When: Creating UserPreferencesUpdate
        Then: Ingredients normalized: ["tomate", "oignon"]
        Requirement: spec.md "Gestion des ingredients > Normalisation automatique"
        """
        from app.models.preferences import UserPreferencesUpdate

        update = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=["  TOMATE  ", "Oignon"],
            preferred_ingredients=["  BASILIC  "],
            portions_count=2,
        )

        assert update.excluded_ingredients == ["tomate", "oignon"]
        assert update.preferred_ingredients == ["basilic"]

    def test_preferences_update_duplicate_ingredients_deduplicated(self):
        """Test that duplicate ingredients are deduplicated.

        Given: excluded_ingredients: ["tomate", "tomate", "TOMATE"]
        When: Creating UserPreferencesUpdate
        Then: Stocke un seul "tomate"
        Requirement: spec.md "Gestion des ingredients > Normalisation"
        """
        from app.models.preferences import UserPreferencesUpdate

        update = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=["tomate", "tomate", "TOMATE"],
            preferred_ingredients=[],
            portions_count=2,
        )

        assert update.excluded_ingredients == ["tomate"]

    def test_preferences_update_empty_strings_filtered(self):
        """Test that empty strings are filtered from ingredients.

        Given: excluded_ingredients: ["", "  ", "tomate"]
        When: Creating UserPreferencesUpdate
        Then: Only "tomate" is kept
        Requirement: spec.md "Gestion des ingredients > Validation"
        """
        from app.models.preferences import UserPreferencesUpdate

        update = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=["", "  ", "tomate"],
            preferred_ingredients=[],
            portions_count=2,
        )

        assert update.excluded_ingredients == ["tomate"]
