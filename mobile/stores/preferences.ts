/**
 * Preferences Store using Zustand
 *
 * Manages user preferences state, local modifications, and API sync.
 * Follows the pattern established in stores/auth.ts
 *
 * State:
 * - preferences: Server-saved preferences (source of truth)
 * - localPreferences: Local modifications before save
 * - isLoading: Loading state for API calls
 * - error: Error message from last failed operation
 * - hasUnsavedChanges: Flag for save button state
 *
 * Actions:
 * - fetchPreferences: Load preferences from API
 * - updatePreferences: Save preferences to API
 * - setLocalPreferences: Update local state (before save)
 * - resetLocalChanges: Revert to saved preferences
 * - reset: Reset entire store state
 */

import { create } from 'zustand';
import type { UserPreferences, UserPreferencesUpdate } from '../types/preferences';
import * as preferencesService from '../services/preferences';

/**
 * Deep equality check for preferences objects
 */
function preferencesAreEqual(a: UserPreferences | null, b: UserPreferences | null): boolean {
  if (a === null && b === null) return true;
  if (a === null || b === null) return false;

  return (
    a.portions_count === b.portions_count &&
    JSON.stringify(a.dietary_preferences.sort()) === JSON.stringify(b.dietary_preferences.sort()) &&
    JSON.stringify(a.allergies.sort()) === JSON.stringify(b.allergies.sort()) &&
    JSON.stringify(a.excluded_ingredients.sort()) === JSON.stringify(b.excluded_ingredients.sort()) &&
    JSON.stringify(a.preferred_ingredients.sort()) === JSON.stringify(b.preferred_ingredients.sort())
  );
}

interface PreferencesState {
  // State
  preferences: UserPreferences | null;
  localPreferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;

  // Actions
  fetchPreferences: () => Promise<void>;
  updatePreferences: (data: UserPreferencesUpdate) => Promise<void>;
  setLocalPreferences: (preferences: UserPreferences) => void;
  resetLocalChanges: () => void;
  reset: () => void;
}

const initialState = {
  preferences: null,
  localPreferences: null,
  isLoading: false,
  error: null,
  hasUnsavedChanges: false,
};

export const usePreferencesStore = create<PreferencesState>((set, get) => ({
  // Initial state
  ...initialState,

  /**
   * Fetch preferences from API
   * Updates both preferences and localPreferences on success
   */
  fetchPreferences: async () => {
    set({ isLoading: true, error: null });

    try {
      const preferences = await preferencesService.getPreferences();

      set({
        preferences,
        localPreferences: preferences,
        isLoading: false,
        hasUnsavedChanges: false,
        error: null,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
      });
    }
  },

  /**
   * Update preferences on the server
   * On success, updates both preferences and localPreferences
   * On error, preserves localPreferences for retry
   */
  updatePreferences: async (data: UserPreferencesUpdate) => {
    set({ isLoading: true, error: null });

    try {
      const updatedPreferences = await preferencesService.updatePreferences(data);

      set({
        preferences: updatedPreferences,
        localPreferences: updatedPreferences,
        isLoading: false,
        hasUnsavedChanges: false,
        error: null,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
        // Preserve local preferences for retry
      });
    }
  },

  /**
   * Update local preferences (before saving)
   * Calculates hasUnsavedChanges by comparing with saved preferences
   */
  setLocalPreferences: (localPreferences: UserPreferences) => {
    const { preferences } = get();
    const hasUnsavedChanges = !preferencesAreEqual(preferences, localPreferences);

    set({
      localPreferences,
      hasUnsavedChanges,
    });
  },

  /**
   * Reset local changes to saved preferences
   * Does not call API - just reverts to last saved state
   */
  resetLocalChanges: () => {
    const { preferences } = get();

    set({
      localPreferences: preferences,
      hasUnsavedChanges: false,
    });
  },

  /**
   * Reset entire store to initial state
   */
  reset: () => {
    set(initialState);
  },
}));
