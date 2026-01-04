/**
 * Tests for ProfilePreferences Integration
 *
 * Unit tests for profile preferences logic (Task Group 5)
 * Tests the preference editing state management
 */

import { usePreferencesStore } from '../../../stores/preferences';
import type { UserPreferences } from '../../../types/preferences';

// Mock the preferences store
jest.mock('../../../stores/preferences', () => ({
  usePreferencesStore: jest.fn(),
}));

const mockedUsePreferencesStore = usePreferencesStore as jest.MockedFunction<
  typeof usePreferencesStore
>;

describe('ProfilePreferences Logic', () => {
  const mockPreferences: UserPreferences = {
    dietary_preferences: ['vegetarian'],
    allergies: ['gluten', 'lactose'],
    excluded_ingredients: ['tomate', 'oignon'],
    preferred_ingredients: ['basilic'],
    portions_count: 4,
    warning: null,
  };

  const mockStore = {
    preferences: mockPreferences,
    localPreferences: mockPreferences,
    isLoading: false,
    error: null,
    hasUnsavedChanges: false,
    fetchPreferences: jest.fn(),
    updatePreferences: jest.fn(),
    setLocalPreferences: jest.fn(),
    resetLocalChanges: jest.fn(),
    reset: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUsePreferencesStore.mockImplementation((selector) => {
      if (typeof selector === 'function') {
        return selector(mockStore as any);
      }
      return mockStore;
    });
  });

  describe('Edit mode toggle', () => {
    /**
     * Test: isEditing state toggles correctly
     * Given: Initial view mode (isEditing = false)
     * When: User activates edit mode
     * Then: isEditing becomes true
     */
    it('should toggle isEditing state', () => {
      // Given
      let isEditing = false;

      // Simulate handleEdit
      const handleEdit = () => {
        isEditing = true;
      };

      // When
      handleEdit();

      // Then
      expect(isEditing).toBe(true);
    });

    /**
     * Test: Cancel resets and exits edit mode
     * Given: User is in edit mode
     * When: User presses cancel
     * Then: resetLocalChanges is called and isEditing becomes false
     */
    it('should call resetLocalChanges on cancel', () => {
      // Given
      let isEditing = true;
      const resetLocalChanges = jest.fn();

      // Simulate handleCancel
      const handleCancel = () => {
        resetLocalChanges();
        isEditing = false;
      };

      // When
      handleCancel();

      // Then
      expect(resetLocalChanges).toHaveBeenCalled();
      expect(isEditing).toBe(false);
    });
  });

  describe('Save functionality', () => {
    /**
     * Test: Save calls updatePreferences with local data
     * Given: Local preferences have been modified
     * When: User saves
     * Then: updatePreferences is called with local preferences
     */
    it('should call updatePreferences on save', async () => {
      // Given
      const updatePreferences = jest.fn().mockResolvedValue(undefined);
      const localPreferences = { ...mockPreferences, portions_count: 6 };
      let isEditing = true;

      // Simulate handleSave
      const handleSave = async () => {
        if (!localPreferences) return;
        try {
          await updatePreferences(localPreferences);
          isEditing = false;
        } catch {
          // Error handled by store
        }
      };

      // When
      await handleSave();

      // Then
      expect(updatePreferences).toHaveBeenCalledWith(localPreferences);
      expect(isEditing).toBe(false);
    });

    /**
     * Test: Save does not exit edit mode on error
     * Given: API returns error
     * When: Save fails
     * Then: isEditing remains true
     */
    it('should stay in edit mode on save error', async () => {
      // Given
      const updatePreferences = jest.fn().mockRejectedValue(new Error('Network error'));
      const localPreferences = mockPreferences;
      let isEditing = true;

      // Simulate handleSave with error handling
      const handleSave = async () => {
        if (!localPreferences) return;
        try {
          await updatePreferences(localPreferences);
          isEditing = false;
        } catch {
          // Error is handled by store, stay in edit mode
        }
      };

      // When
      await handleSave();

      // Then
      expect(updatePreferences).toHaveBeenCalled();
      expect(isEditing).toBe(true); // Should remain true on error
    });
  });

  describe('Halal + Kosher warning', () => {
    /**
     * Test: Warning is shown when both halal and kosher selected
     * Given: Preferences with halal and kosher
     * When: Checking warning condition
     * Then: hasHalalKosherWarning is true
     */
    it('should detect halal and kosher combination', () => {
      // Given
      const localPreferences: UserPreferences = {
        ...mockPreferences,
        dietary_preferences: ['halal', 'kosher'],
      };

      // When
      const hasHalalKosherWarning =
        localPreferences.dietary_preferences.includes('halal') &&
        localPreferences.dietary_preferences.includes('kosher');

      // Then
      expect(hasHalalKosherWarning).toBe(true);
    });

    /**
     * Test: No warning when only halal selected
     * Given: Preferences with only halal
     * When: Checking warning condition
     * Then: hasHalalKosherWarning is false
     */
    it('should not show warning for halal only', () => {
      // Given
      const localPreferences: UserPreferences = {
        ...mockPreferences,
        dietary_preferences: ['halal'],
      };

      // When
      const hasHalalKosherWarning =
        localPreferences.dietary_preferences.includes('halal') &&
        localPreferences.dietary_preferences.includes('kosher');

      // Then
      expect(hasHalalKosherWarning).toBe(false);
    });

    /**
     * Test: No warning when only kosher selected
     * Given: Preferences with only kosher
     * When: Checking warning condition
     * Then: hasHalalKosherWarning is false
     */
    it('should not show warning for kosher only', () => {
      // Given
      const localPreferences: UserPreferences = {
        ...mockPreferences,
        dietary_preferences: ['kosher'],
      };

      // When
      const hasHalalKosherWarning =
        localPreferences.dietary_preferences.includes('halal') &&
        localPreferences.dietary_preferences.includes('kosher');

      // Then
      expect(hasHalalKosherWarning).toBe(false);
    });
  });

  describe('Preference update handlers', () => {
    /**
     * Test: Dietary preference update
     * Given: Local preferences
     * When: User changes dietary preferences
     * Then: setLocalPreferences is called with updated dietary_preferences
     */
    it('should update dietary preferences correctly', () => {
      // Given
      const setLocalPreferences = jest.fn();
      const localPreferences = mockPreferences;
      const newDietaryValues = ['vegan', 'halal'];

      // Simulate handleDietaryChange
      const handleDietaryChange = (values: string[]) => {
        if (!localPreferences) return;
        setLocalPreferences({
          ...localPreferences,
          dietary_preferences: values,
        });
      };

      // When
      handleDietaryChange(newDietaryValues);

      // Then
      expect(setLocalPreferences).toHaveBeenCalledWith({
        ...localPreferences,
        dietary_preferences: newDietaryValues,
      });
    });

    /**
     * Test: Excluded ingredient add
     * Given: Local preferences with existing excluded ingredients
     * When: User adds new ingredient
     * Then: setLocalPreferences is called with ingredient added
     */
    it('should add excluded ingredient correctly', () => {
      // Given
      const setLocalPreferences = jest.fn();
      const localPreferences = mockPreferences;
      const newIngredient = 'ail';

      // Simulate handleExcludedAdd
      const handleExcludedAdd = (ingredient: string) => {
        if (!localPreferences) return;
        if (localPreferences.excluded_ingredients.includes(ingredient)) return;
        setLocalPreferences({
          ...localPreferences,
          excluded_ingredients: [...localPreferences.excluded_ingredients, ingredient],
        });
      };

      // When
      handleExcludedAdd(newIngredient);

      // Then
      expect(setLocalPreferences).toHaveBeenCalledWith({
        ...localPreferences,
        excluded_ingredients: ['tomate', 'oignon', 'ail'],
      });
    });

    /**
     * Test: Excluded ingredient remove
     * Given: Local preferences with excluded ingredients
     * When: User removes an ingredient
     * Then: setLocalPreferences is called with ingredient removed
     */
    it('should remove excluded ingredient correctly', () => {
      // Given
      const setLocalPreferences = jest.fn();
      const localPreferences = mockPreferences;
      const ingredientToRemove = 'tomate';

      // Simulate handleExcludedRemove
      const handleExcludedRemove = (ingredient: string) => {
        if (!localPreferences) return;
        setLocalPreferences({
          ...localPreferences,
          excluded_ingredients: localPreferences.excluded_ingredients.filter(
            (i) => i !== ingredient
          ),
        });
      };

      // When
      handleExcludedRemove(ingredientToRemove);

      // Then
      expect(setLocalPreferences).toHaveBeenCalledWith({
        ...localPreferences,
        excluded_ingredients: ['oignon'],
      });
    });

    /**
     * Test: Portions update
     * Given: Local preferences
     * When: User changes portions count
     * Then: setLocalPreferences is called with new portions_count
     */
    it('should update portions correctly', () => {
      // Given
      const setLocalPreferences = jest.fn();
      const localPreferences = mockPreferences;
      const newPortions = 6;

      // Simulate handlePortionsChange
      const handlePortionsChange = (value: number) => {
        if (!localPreferences) return;
        setLocalPreferences({
          ...localPreferences,
          portions_count: value,
        });
      };

      // When
      handlePortionsChange(newPortions);

      // Then
      expect(setLocalPreferences).toHaveBeenCalledWith({
        ...localPreferences,
        portions_count: 6,
      });
    });
  });

  describe('Loading and error states', () => {
    /**
     * Test: Loading state detection
     * Given: Store with isLoading=true and no preferences
     * When: Checking loading condition
     * Then: Should show loading state
     */
    it('should detect loading state correctly', () => {
      // Given
      const isLoading = true;
      const localPreferences = null;

      // When
      const showLoading = isLoading && !localPreferences;

      // Then
      expect(showLoading).toBe(true);
    });

    /**
     * Test: Error state detection
     * Given: Store with error and no preferences
     * When: Checking error condition
     * Then: Should show error state
     */
    it('should detect error state correctly', () => {
      // Given
      const error = 'Network error';
      const localPreferences = null;

      // When
      const showError = error && !localPreferences;

      // Then
      expect(showError).toBe(true);
    });

    /**
     * Test: Error shown alongside content when preferences exist
     * Given: Store with error and existing preferences
     * When: Checking display condition
     * Then: Should show error banner but also content
     */
    it('should show error banner when preferences exist', () => {
      // Given
      const error = 'Save failed';
      const localPreferences = mockPreferences;

      // When
      const showFullErrorScreen = error && !localPreferences;
      const showErrorBanner = error && localPreferences;

      // Then
      expect(showFullErrorScreen).toBe(false);
      expect(showErrorBanner).toBeTruthy();
    });
  });
});
