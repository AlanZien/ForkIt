"""Tests for preferences service - TDD approach.

These tests mock Supabase to test the preferences service logic.
Following test-plan.md specifications for API Backend tests 21-50.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from app.models.preferences import (
    AllergyType,
    DietaryType,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)


class MockSupabaseResponse:
    """Mock Supabase query response."""

    def __init__(self, data: list | dict | None = None, error: dict | None = None):
        self.data = data if data is not None else []
        self.error = error


# Create a mock for supabase module before importing the service
mock_supabase_module = MagicMock()
sys.modules["supabase"] = mock_supabase_module


class TestGetPreferences:
    """Tests for get_preferences method.

    Corresponds to test-plan.md tests 21-30 (GET /api/profile/preferences).
    """

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_get_preferences_returns_all_user_preferences(self, mock_get_client):
        """Test that get_preferences returns all preferences for a user.

        Given: User authenticated with user_id = "user-123"
               User has 2 dietary preferences, 3 allergies, 5 excluded, 3 preferred, portions=4
        When: get_preferences(user_id)
        Then: Returns UserPreferencesResponse with all data
        Requirement: spec.md "Architecture API Backend > GET /api/profile/preferences"
        Test-plan: test_get_preferences_authenticated_success (#21)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        # Setup mock Supabase client
        mock_client = MagicMock()

        # Mock dietary preferences query
        dietary_data = [
            {"dietary_type": "vegetarian"},
            {"dietary_type": "no_pork"},
        ]
        mock_dietary_query = MagicMock()
        mock_dietary_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=dietary_data)
        )

        # Mock allergies query
        allergy_data = [
            {"allergy_type": "gluten"},
            {"allergy_type": "lactose"},
            {"allergy_type": "peanuts"},
        ]
        mock_allergy_query = MagicMock()
        mock_allergy_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=allergy_data)
        )

        # Mock excluded ingredients query
        excluded_data = [
            {"ingredient_name": "tomate"},
            {"ingredient_name": "oignon"},
            {"ingredient_name": "ail"},
            {"ingredient_name": "poivron"},
            {"ingredient_name": "aubergine"},
        ]
        mock_excluded_query = MagicMock()
        mock_excluded_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=excluded_data)
        )

        # Mock preferred ingredients query
        preferred_data = [
            {"ingredient_name": "basilic"},
            {"ingredient_name": "thym"},
            {"ingredient_name": "romarin"},
        ]
        mock_preferred_query = MagicMock()
        mock_preferred_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=preferred_data)
        )

        # Mock user settings query
        settings_data = [{"portions_count": 4}]
        mock_settings_query = MagicMock()
        mock_settings_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=settings_data)
        )

        # Configure table calls
        def table_side_effect(table_name):
            table_mocks = {
                "user_dietary_preferences": mock_dietary_query,
                "user_allergies": mock_allergy_query,
                "user_excluded_ingredients": mock_excluded_query,
                "user_preferred_ingredients": mock_preferred_query,
                "user_settings": mock_settings_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        result = service.get_preferences(user_id)

        assert isinstance(result, UserPreferencesResponse)
        assert len(result.dietary_preferences) == 2
        assert DietaryType.VEGETARIAN in result.dietary_preferences
        assert DietaryType.NO_PORK in result.dietary_preferences
        assert len(result.allergies) == 3
        assert AllergyType.GLUTEN in result.allergies
        assert len(result.excluded_ingredients) == 5
        assert "tomate" in result.excluded_ingredients
        assert len(result.preferred_ingredients) == 3
        assert "basilic" in result.preferred_ingredients
        assert result.portions_count == 4

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_get_preferences_new_user_returns_defaults(self, mock_get_client):
        """Test that new user without preferences gets default values.

        Given: User authenticated without any preferences configured
        When: get_preferences(user_id)
        Then: Returns UserPreferencesResponse with empty lists and default portions_count
        Requirement: spec.md "Architecture API Backend > GET preferences"
        Test-plan: test_get_preferences_new_user_returns_empty_defaults (#24)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        # All queries return empty data
        mock_query = MagicMock()
        mock_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )
        mock_client.table.return_value = mock_query
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        result = service.get_preferences(user_id)

        assert result.dietary_preferences == []
        assert result.allergies == []
        assert result.excluded_ingredients == []
        assert result.preferred_ingredients == []
        assert result.portions_count == 2  # Default value from service

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_get_preferences_with_partial_data(self, mock_get_client):
        """Test that partial data (only allergies) is handled correctly.

        Given: User with only allergies (no dietary preferences or ingredients)
        When: get_preferences(user_id)
        Then: Returns allergies + empty arrays for the rest
        Requirement: spec.md "Architecture API Backend"
        Test-plan: test_get_preferences_with_partial_data (#30)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        # Setup individual table mocks
        mock_dietary_query = MagicMock()
        mock_dietary_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        mock_allergy_query = MagicMock()
        mock_allergy_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[{"allergy_type": "gluten"}])
        )

        mock_excluded_query = MagicMock()
        mock_excluded_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        mock_preferred_query = MagicMock()
        mock_preferred_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        mock_settings_query = MagicMock()
        mock_settings_query.select.return_value.eq.return_value.execute.return_value = (
            MockSupabaseResponse(data=[])
        )

        def table_side_effect(table_name):
            table_mocks = {
                "user_dietary_preferences": mock_dietary_query,
                "user_allergies": mock_allergy_query,
                "user_excluded_ingredients": mock_excluded_query,
                "user_preferred_ingredients": mock_preferred_query,
                "user_settings": mock_settings_query,
            }
            return table_mocks.get(table_name, MagicMock())

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        result = service.get_preferences(user_id)

        assert result.dietary_preferences == []
        assert len(result.allergies) == 1
        assert AllergyType.GLUTEN in result.allergies
        assert result.excluded_ingredients == []
        assert result.preferred_ingredients == []


class TestUpdatePreferences:
    """Tests for update_preferences method.

    Corresponds to test-plan.md tests 31-50 (PUT /api/profile/preferences).
    """

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_update_preferences_full_payload_success(self, mock_get_client):
        """Test that full payload update succeeds.

        Given: User authenticated with valid complete preferences payload
        When: update_preferences(user_id, data)
        Then: All preferences updated in database and returned
        Requirement: spec.md "Architecture API Backend > PUT /api/profile/preferences"
        Test-plan: test_update_preferences_full_payload_success (#31)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        def table_side_effect(table_name):
            mock_query = MagicMock()
            mock_query.delete.return_value.eq.return_value.execute.return_value = (
                MockSupabaseResponse(data=[])
            )
            mock_query.insert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            mock_query.upsert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        data = UserPreferencesUpdate(
            dietary_preferences=[DietaryType.VEGETARIAN],
            allergies=[AllergyType.GLUTEN],
            excluded_ingredients=["tomate"],
            preferred_ingredients=["basilic"],
            portions_count=3,
        )

        result = service.update_preferences(user_id, data)

        assert isinstance(result, UserPreferencesResponse)
        assert DietaryType.VEGETARIAN in result.dietary_preferences
        assert AllergyType.GLUTEN in result.allergies
        assert "tomate" in result.excluded_ingredients
        assert "basilic" in result.preferred_ingredients
        assert result.portions_count == 3

    def test_update_dietary_preferences_vegan_incompatibility_pescetarian(self):
        """Test that VEGAN + PESCETARIAN raises incompatibility error.

        Given: Payload with dietary_preferences: ["vegan", "pescetarian"]
        When: Creating UserPreferencesUpdate
        Then: Raises ValidationError
        Requirement: spec.md "Gestion des regimes > Vegetalien incompatible avec Pescetarien"
        Test-plan: test_update_dietary_preferences_incompatibility_vegetalien_pescetarien (#33)
        """
        from pydantic import ValidationError

        # This validation happens at the Pydantic model level
        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[DietaryType.VEGAN, DietaryType.PESCETARIAN],
                allergies=[],
                excluded_ingredients=[],
                preferred_ingredients=[],
                portions_count=2,
            )

        errors = exc_info.value.errors()
        assert any("incompatible" in str(e).lower() for e in errors)

    def test_update_dietary_preferences_vegan_incompatibility_no_beef(self):
        """Test that VEGAN + NO_BEEF raises incompatibility error.

        Given: Payload with dietary_preferences: ["vegan", "no_beef"]
        When: Creating UserPreferencesUpdate
        Then: Raises ValidationError
        Requirement: spec.md "Gestion des regimes > Vegetalien incompatible avec Sans boeuf"
        Test-plan: test_update_dietary_preferences_incompatibility_vegetalien_sans_boeuf (#34)
        """
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[DietaryType.VEGAN, DietaryType.NO_BEEF],
                allergies=[],
                excluded_ingredients=[],
                preferred_ingredients=[],
                portions_count=2,
            )

        errors = exc_info.value.errors()
        assert any("incompatible" in str(e).lower() for e in errors)

    def test_update_dietary_preferences_vegan_incompatibility_no_pork(self):
        """Test that VEGAN + NO_PORK raises incompatibility error.

        Given: Payload with dietary_preferences: ["vegan", "no_pork"]
        When: Creating UserPreferencesUpdate
        Then: Raises ValidationError
        Requirement: spec.md "Gestion des regimes > Vegetalien incompatible avec Sans porc"
        Test-plan: test_update_dietary_preferences_incompatibility_vegetalien_sans_porc (#35)
        """
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[DietaryType.VEGAN, DietaryType.NO_PORK],
                allergies=[],
                excluded_ingredients=[],
                preferred_ingredients=[],
                portions_count=2,
            )

        errors = exc_info.value.errors()
        assert any("incompatible" in str(e).lower() for e in errors)

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_update_dietary_preferences_halal_kosher_allowed_with_warning(
        self, mock_get_client
    ):
        """Test that HALAL + KOSHER is allowed but returns a warning.

        Given: Payload with dietary_preferences: ["halal", "kosher"]
        When: update_preferences(user_id, data)
        Then: Status 200 (allowed), response includes warning message
        Requirement: spec.md "Gestion des regimes > Halal + Casher: avertissement non-bloquant"
        Test-plan: test_update_dietary_preferences_halal_casher_warning_but_allowed (#36)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        def table_side_effect(table_name):
            mock_query = MagicMock()
            mock_query.delete.return_value.eq.return_value.execute.return_value = (
                MockSupabaseResponse(data=[])
            )
            mock_query.insert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            mock_query.upsert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        data = UserPreferencesUpdate(
            dietary_preferences=[DietaryType.HALAL, DietaryType.KOSHER],
            allergies=[],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=2,
        )

        result = service.update_preferences(user_id, data)

        # Should succeed but include warning
        assert DietaryType.HALAL in result.dietary_preferences
        assert DietaryType.KOSHER in result.dietary_preferences
        assert result.warning is not None
        assert "coherence" in result.warning.lower() or "combination" in result.warning.lower()

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_update_ingredients_normalization(self, mock_get_client):
        """Test that ingredients are normalized (lowercase, trim) before storage.

        Given: Payload with excluded_ingredients: ["  TOMATE  ", "Oignon"]
        When: update_preferences(user_id, data)
        Then: Ingredients stored as ["tomate", "oignon"]
        Requirement: spec.md "Gestion des ingredients > Normalisation automatique: trim() + lowercase"
        Test-plan: test_update_ingredients_normalization (#42)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        def table_side_effect(table_name):
            mock_query = MagicMock()
            mock_query.delete.return_value.eq.return_value.execute.return_value = (
                MockSupabaseResponse(data=[])
            )
            mock_query.insert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            mock_query.upsert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        # Note: Normalization happens in Pydantic model, so we pass raw values
        data = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=["  TOMATE  ", "Oignon"],
            preferred_ingredients=[],
            portions_count=2,
        )

        result = service.update_preferences(user_id, data)

        # Verify the result contains normalized values
        assert "tomate" in result.excluded_ingredients
        assert "oignon" in result.excluded_ingredients

    @patch("app.services.preferences_service.get_supabase_admin")
    def test_update_empty_payload_clears_preferences(self, mock_get_client):
        """Test that empty payload clears all preferences.

        Given: User with existing preferences
        When: update_preferences with empty arrays
        Then: All preferences cleared, returns defaults
        Requirement: spec.md "Architecture API Backend > Payload complet"
        Test-plan: test_update_empty_payload_clears_preferences (#45)
        """
        from app.services.preferences_service import PreferencesService

        user_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_client = MagicMock()

        def table_side_effect(table_name):
            mock_query = MagicMock()
            mock_query.delete.return_value.eq.return_value.execute.return_value = (
                MockSupabaseResponse(data=[])
            )
            mock_query.insert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            mock_query.upsert.return_value.execute.return_value = MockSupabaseResponse(
                data=[]
            )
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_get_client.return_value = mock_client

        service = PreferencesService()
        data = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=1,
        )

        result = service.update_preferences(user_id, data)

        assert result.dietary_preferences == []
        assert result.allergies == []
        assert result.excluded_ingredients == []
        assert result.preferred_ingredients == []
        assert result.portions_count == 1


class TestValidateDietaryIncompatibilities:
    """Tests for dietary incompatibility validation logic.

    Corresponds to task 2.5: Implementer la validation des incompatibilites metier
    """

    def test_vegan_disables_pescetarian_no_beef_no_pork(self):
        """Test that VEGAN is incompatible with PESCETARIAN, NO_BEEF, NO_PORK.

        Given: VEGAN selected
        When: Attempting to add PESCETARIAN, NO_BEEF, or NO_PORK
        Then: ValidationError raised
        Requirement: spec.md "Si VEGAN: desactiver automatiquement PESCETARIAN, NO_BEEF, NO_PORK"
        """
        from pydantic import ValidationError

        incompatible_combinations = [
            [DietaryType.VEGAN, DietaryType.PESCETARIAN],
            [DietaryType.VEGAN, DietaryType.NO_BEEF],
            [DietaryType.VEGAN, DietaryType.NO_PORK],
            [DietaryType.VEGAN, DietaryType.PESCETARIAN, DietaryType.NO_BEEF],
        ]

        for combo in incompatible_combinations:
            with pytest.raises(ValidationError):
                UserPreferencesUpdate(
                    dietary_preferences=combo,
                    allergies=[],
                    excluded_ingredients=[],
                    preferred_ingredients=[],
                    portions_count=2,
                )

    def test_vegetarian_with_pescetarian_allowed(self):
        """Test that VEGETARIAN + PESCETARIAN is allowed.

        Given: VEGETARIAN selected
        When: Adding PESCETARIAN
        Then: Both are accepted (no incompatibility)
        """
        data = UserPreferencesUpdate(
            dietary_preferences=[DietaryType.VEGETARIAN, DietaryType.PESCETARIAN],
            allergies=[],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=2,
        )

        assert DietaryType.VEGETARIAN in data.dietary_preferences
        assert DietaryType.PESCETARIAN in data.dietary_preferences

    def test_halal_and_kosher_combination(self):
        """Test that HALAL + KOSHER is allowed (non-blocking warning).

        Given: HALAL selected
        When: Adding KOSHER
        Then: Both are accepted (warning handled by service, not model)
        """
        data = UserPreferencesUpdate(
            dietary_preferences=[DietaryType.HALAL, DietaryType.KOSHER],
            allergies=[],
            excluded_ingredients=[],
            preferred_ingredients=[],
            portions_count=2,
        )

        assert DietaryType.HALAL in data.dietary_preferences
        assert DietaryType.KOSHER in data.dietary_preferences


class TestIngredientsLimit:
    """Tests for ingredient limit validation.

    Corresponds to test-plan.md tests 37-38.
    """

    def test_excluded_ingredients_limit_30(self):
        """Test that more than 30 excluded ingredients raises error.

        Given: 31 excluded ingredients
        When: Creating UserPreferencesUpdate
        Then: ValidationError with message about 30 max
        Requirement: spec.md "Gestion des ingredients > Limite stricte de 30 tags"
        Test-plan: test_update_excluded_ingredients_exceeds_30_limit (#37)
        """
        from pydantic import ValidationError

        ingredients_31 = [f"ingredient_{i}" for i in range(31)]

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[],
                allergies=[],
                excluded_ingredients=ingredients_31,
                preferred_ingredients=[],
                portions_count=2,
            )

        assert any("30" in str(e) for e in exc_info.value.errors())

    def test_preferred_ingredients_limit_30(self):
        """Test that more than 30 preferred ingredients raises error.

        Given: 31 preferred ingredients
        When: Creating UserPreferencesUpdate
        Then: ValidationError with message about 30 max
        Requirement: spec.md "Gestion des ingredients > Limite stricte de 30 tags"
        Test-plan: test_update_preferred_ingredients_exceeds_30_limit (#38)
        """
        from pydantic import ValidationError

        ingredients_31 = [f"ingredient_{i}" for i in range(31)]

        with pytest.raises(ValidationError) as exc_info:
            UserPreferencesUpdate(
                dietary_preferences=[],
                allergies=[],
                excluded_ingredients=[],
                preferred_ingredients=ingredients_31,
                portions_count=2,
            )

        assert any("30" in str(e) for e in exc_info.value.errors())

    def test_exactly_30_ingredients_each_category_allowed(self):
        """Test that exactly 30 ingredients per category is allowed.

        Given: 30 excluded AND 30 preferred ingredients
        When: Creating UserPreferencesUpdate
        Then: Validation passes
        """
        excluded_30 = [f"excluded_{i}" for i in range(30)]
        preferred_30 = [f"preferred_{i}" for i in range(30)]

        data = UserPreferencesUpdate(
            dietary_preferences=[],
            allergies=[],
            excluded_ingredients=excluded_30,
            preferred_ingredients=preferred_30,
            portions_count=2,
        )

        assert len(data.excluded_ingredients) == 30
        assert len(data.preferred_ingredients) == 30
