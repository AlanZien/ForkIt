/**
 * Tests for Preferences Store
 *
 * TDD Tests for Zustand preferences store (Task Group 4)
 * Corresponds to test-plan.md tests 79-82
 */

import { usePreferencesStore } from '../../stores/preferences';
import * as preferencesService from '../../services/preferences';
import type { UserPreferences } from '../../types/preferences';

// Mock the preferences service
jest.mock('../../services/preferences');

const mockedPreferencesService = preferencesService as jest.Mocked<typeof preferencesService>;

// Test data
const mockPreferences: UserPreferences = {
  dietary_preferences: ['vegetarian'],
  allergies: ['gluten', 'lactose'],
  excluded_ingredients: ['tomate', 'oignon'],
  preferred_ingredients: ['basilic'],
  portions_count: 4,
  warning: null,
};

const mockPreferencesWithWarning: UserPreferences = {
  ...mockPreferences,
  dietary_preferences: ['halal', 'kosher'],
  warning: 'Verifiez la coherence de cette combinaison',
};

describe('usePreferencesStore', () => {
  // Reset store state before each test
  beforeEach(() => {
    const store = usePreferencesStore.getState();
    store.reset();
    jest.clearAllMocks();
  });

  describe('Initial state', () => {
    it('should have correct initial state', () => {
      // Given: Store is initialized
      const state = usePreferencesStore.getState();

      // Then: Initial state should be empty/default
      expect(state.preferences).toBeNull();
      expect(state.localPreferences).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.hasUnsavedChanges).toBe(false);
    });
  });

  /**
   * Test 79: test_preferences_store_fetch_preferences_action
   * Priority: High
   * Given: Store preferences initialized
   * When: Call fetchPreferences()
   * Then: API GET called, state updated with received data
   */
  describe('fetchPreferences', () => {
    it('should call API GET and update state with received data', async () => {
      // Given: Store initialized, API returns preferences
      mockedPreferencesService.getPreferences.mockResolvedValueOnce(mockPreferences);

      // When: fetchPreferences is called
      await usePreferencesStore.getState().fetchPreferences();

      // Then: API was called and state was updated
      expect(mockedPreferencesService.getPreferences).toHaveBeenCalledTimes(1);

      const state = usePreferencesStore.getState();
      expect(state.preferences).toEqual(mockPreferences);
      expect(state.localPreferences).toEqual(mockPreferences);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.hasUnsavedChanges).toBe(false);
    });

    it('should set isLoading to true while fetching', async () => {
      // Given: Slow API response
      let resolvePromise: (value: UserPreferences) => void;
      const slowPromise = new Promise<UserPreferences>((resolve) => {
        resolvePromise = resolve;
      });
      mockedPreferencesService.getPreferences.mockReturnValueOnce(slowPromise);

      // When: fetchPreferences is called (not awaited)
      const fetchPromise = usePreferencesStore.getState().fetchPreferences();

      // Then: isLoading should be true
      expect(usePreferencesStore.getState().isLoading).toBe(true);

      // Cleanup: resolve and await
      resolvePromise!(mockPreferences);
      await fetchPromise;

      expect(usePreferencesStore.getState().isLoading).toBe(false);
    });

    it('should handle API errors gracefully', async () => {
      // Given: API returns an error
      const errorMessage = 'Network error';
      mockedPreferencesService.getPreferences.mockRejectedValueOnce(new Error(errorMessage));

      // When: fetchPreferences is called
      await usePreferencesStore.getState().fetchPreferences();

      // Then: Error state should be set
      const state = usePreferencesStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.isLoading).toBe(false);
      expect(state.preferences).toBeNull();
    });
  });

  /**
   * Test 80: test_preferences_store_update_preferences_action
   * Priority: High
   * Given: Store with locally modified preferences
   * When: Call updatePreferences(data)
   * Then: API PUT called, state updated on success
   */
  describe('updatePreferences', () => {
    it('should call API PUT and update state on success', async () => {
      // Given: Store with local preferences
      usePreferencesStore.getState().setLocalPreferences(mockPreferences);

      const updatedPreferences: UserPreferences = {
        ...mockPreferences,
        portions_count: 6,
      };
      mockedPreferencesService.updatePreferences.mockResolvedValueOnce(updatedPreferences);

      // When: updatePreferences is called
      await usePreferencesStore.getState().updatePreferences(updatedPreferences);

      // Then: API was called and state was updated
      expect(mockedPreferencesService.updatePreferences).toHaveBeenCalledWith(updatedPreferences);

      const state = usePreferencesStore.getState();
      expect(state.preferences).toEqual(updatedPreferences);
      expect(state.localPreferences).toEqual(updatedPreferences);
      expect(state.hasUnsavedChanges).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should preserve warning from API response', async () => {
      // Given: API returns preferences with warning
      mockedPreferencesService.updatePreferences.mockResolvedValueOnce(mockPreferencesWithWarning);

      // When: updatePreferences is called
      await usePreferencesStore.getState().updatePreferences(mockPreferencesWithWarning);

      // Then: Warning should be preserved in state
      const state = usePreferencesStore.getState();
      expect(state.preferences?.warning).toBe('Verifiez la coherence de cette combinaison');
    });

    it('should set isLoading during update', async () => {
      // Given: Slow API response
      let resolvePromise: (value: UserPreferences) => void;
      const slowPromise = new Promise<UserPreferences>((resolve) => {
        resolvePromise = resolve;
      });
      mockedPreferencesService.updatePreferences.mockReturnValueOnce(slowPromise);

      // When: updatePreferences is called (not awaited)
      const updatePromise = usePreferencesStore.getState().updatePreferences(mockPreferences);

      // Then: isLoading should be true
      expect(usePreferencesStore.getState().isLoading).toBe(true);

      // Cleanup
      resolvePromise!(mockPreferences);
      await updatePromise;
    });
  });

  /**
   * Test 81: test_preferences_store_reset_local_changes_action
   * Priority: High
   * Given: Store with unsaved local modifications
   * When: Call resetLocalChanges()
   * Then: State returns to initially loaded values, no API call
   */
  describe('resetLocalChanges', () => {
    it('should restore initial values without calling API', async () => {
      // Given: Store with fetched preferences and local changes
      mockedPreferencesService.getPreferences.mockResolvedValueOnce(mockPreferences);

      await usePreferencesStore.getState().fetchPreferences();

      // Make local changes
      const modifiedPreferences: UserPreferences = {
        ...mockPreferences,
        portions_count: 10,
        excluded_ingredients: ['tomate', 'oignon', 'ail'],
      };

      usePreferencesStore.getState().setLocalPreferences(modifiedPreferences);

      // Verify local changes were made
      expect(usePreferencesStore.getState().localPreferences?.portions_count).toBe(10);
      expect(usePreferencesStore.getState().hasUnsavedChanges).toBe(true);

      // Clear mock to verify no new calls
      mockedPreferencesService.getPreferences.mockClear();
      mockedPreferencesService.updatePreferences.mockClear();

      // When: resetLocalChanges is called
      usePreferencesStore.getState().resetLocalChanges();

      // Then: State should be restored, no API calls made
      const state = usePreferencesStore.getState();
      expect(state.localPreferences).toEqual(mockPreferences);
      expect(state.hasUnsavedChanges).toBe(false);
      expect(mockedPreferencesService.getPreferences).not.toHaveBeenCalled();
      expect(mockedPreferencesService.updatePreferences).not.toHaveBeenCalled();
    });

    it('should handle reset when no initial preferences exist', () => {
      // Given: Store with no fetched preferences but local changes
      const modifiedPreferences: UserPreferences = {
        ...mockPreferences,
        portions_count: 5,
      };

      usePreferencesStore.getState().setLocalPreferences(modifiedPreferences);

      // When: resetLocalChanges is called
      usePreferencesStore.getState().resetLocalChanges();

      // Then: localPreferences should be null (matching initial preferences)
      const state = usePreferencesStore.getState();
      expect(state.localPreferences).toBeNull();
      expect(state.hasUnsavedChanges).toBe(false);
    });
  });

  /**
   * Test 82: test_preferences_store_handles_api_error
   * Priority: Medium
   * Given: API error during updatePreferences
   * When: API returns error
   * Then: error state updated, loading false, local preferences preserved
   */
  describe('API error handling', () => {
    it('should preserve local preferences on update error', async () => {
      // Given: Store with local preferences and API that will fail
      const localPrefs: UserPreferences = {
        ...mockPreferences,
        portions_count: 8,
      };

      usePreferencesStore.getState().setLocalPreferences(localPrefs);

      const errorMessage = 'Server error: 500';
      mockedPreferencesService.updatePreferences.mockRejectedValueOnce(new Error(errorMessage));

      // When: updatePreferences fails
      await usePreferencesStore.getState().updatePreferences(localPrefs);

      // Then: Error set, loading false, local preferences preserved
      const state = usePreferencesStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.isLoading).toBe(false);
      expect(state.localPreferences).toEqual(localPrefs);
      // Saved preferences should not be updated on error
      expect(state.preferences).toBeNull();
    });

    it('should clear error on successful subsequent request', async () => {
      // Given: Store with previous error
      mockedPreferencesService.getPreferences.mockRejectedValueOnce(new Error('First error'));

      await usePreferencesStore.getState().fetchPreferences();

      expect(usePreferencesStore.getState().error).toBe('First error');

      // When: Successful request is made
      mockedPreferencesService.getPreferences.mockResolvedValueOnce(mockPreferences);

      await usePreferencesStore.getState().fetchPreferences();

      // Then: Error should be cleared
      const state = usePreferencesStore.getState();
      expect(state.error).toBeNull();
      expect(state.preferences).toEqual(mockPreferences);
    });
  });

  describe('setLocalPreferences', () => {
    it('should update local preferences and set hasUnsavedChanges', async () => {
      // Given: Store with initial preferences
      mockedPreferencesService.getPreferences.mockResolvedValueOnce(mockPreferences);

      await usePreferencesStore.getState().fetchPreferences();

      // When: Local preferences are modified
      const modifiedPreferences: UserPreferences = {
        ...mockPreferences,
        dietary_preferences: ['vegan'],
        portions_count: 3,
      };

      usePreferencesStore.getState().setLocalPreferences(modifiedPreferences);

      // Then: Local preferences updated, hasUnsavedChanges true
      const state = usePreferencesStore.getState();
      expect(state.localPreferences).toEqual(modifiedPreferences);
      expect(state.hasUnsavedChanges).toBe(true);
      // Original preferences unchanged
      expect(state.preferences).toEqual(mockPreferences);
    });

    it('should set hasUnsavedChanges to false when local equals saved', async () => {
      // Given: Store with preferences
      mockedPreferencesService.getPreferences.mockResolvedValueOnce(mockPreferences);

      await usePreferencesStore.getState().fetchPreferences();

      // Make changes
      usePreferencesStore.getState().setLocalPreferences({
        ...mockPreferences,
        portions_count: 10,
      });

      expect(usePreferencesStore.getState().hasUnsavedChanges).toBe(true);

      // When: Reset to same as saved
      usePreferencesStore.getState().setLocalPreferences(mockPreferences);

      // Then: hasUnsavedChanges should be false
      expect(usePreferencesStore.getState().hasUnsavedChanges).toBe(false);
    });
  });
});
