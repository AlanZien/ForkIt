/**
 * Onboarding Store using Zustand
 *
 * Manages the onboarding wizard state for the 5-step profile setup flow.
 * Follows the pattern established in stores/preferences.ts
 *
 * State:
 * - currentStep: Current step in the wizard (1-5)
 * - dietaryPreferences: Selected dietary preferences
 * - allergies: Selected allergies
 * - portions: Number of portions (1-12)
 * - isLoading: Loading state for API calls
 * - error: Error message from last failed operation
 *
 * Actions:
 * - nextStep: Move to next step (max 5)
 * - prevStep: Move to previous step (min 1)
 * - setDietaryPreferences: Update dietary preferences
 * - setAllergies: Update allergies
 * - setPortions: Update portions count
 * - completeOnboarding: Save preferences and mark onboarding complete
 * - reset: Reset entire store state
 */

import { create } from 'zustand';
import type { DietaryType, AllergyType } from '../types/preferences';
import * as onboardingService from '../services/onboarding';
import * as preferencesService from '../services/preferences';

interface OnboardingState {
  // State
  currentStep: number;
  dietaryPreferences: DietaryType[];
  allergies: AllergyType[];
  portions: number;
  isLoading: boolean;
  error: string | null;

  // Actions
  nextStep: () => void;
  prevStep: () => void;
  setDietaryPreferences: (preferences: DietaryType[]) => void;
  setAllergies: (allergies: AllergyType[]) => void;
  setPortions: (portions: number) => void;
  completeOnboarding: () => Promise<void>;
  reset: () => void;
}

const MIN_PORTIONS = 1;
const MAX_PORTIONS = 12;
const MIN_STEP = 1;
const MAX_STEP = 5;
const DEFAULT_PORTIONS = 2;

const initialState = {
  currentStep: 1,
  dietaryPreferences: [] as DietaryType[],
  allergies: [] as AllergyType[],
  portions: DEFAULT_PORTIONS,
  isLoading: false,
  error: null,
};

export const useOnboardingStore = create<OnboardingState>((set, get) => ({
  // Initial state
  ...initialState,

  /**
   * Move to next step (max 5)
   */
  nextStep: () => {
    set((state) => ({
      currentStep: Math.min(state.currentStep + 1, MAX_STEP),
    }));
  },

  /**
   * Move to previous step (min 1)
   */
  prevStep: () => {
    set((state) => ({
      currentStep: Math.max(state.currentStep - 1, MIN_STEP),
    }));
  },

  /**
   * Update dietary preferences
   */
  setDietaryPreferences: (preferences: DietaryType[]) => {
    set({ dietaryPreferences: preferences });
  },

  /**
   * Update allergies
   */
  setAllergies: (allergies: AllergyType[]) => {
    set({ allergies });
  },

  /**
   * Update portions (constrained to 1-12)
   */
  setPortions: (portions: number) => {
    const constrainedPortions = Math.min(Math.max(portions, MIN_PORTIONS), MAX_PORTIONS);
    set({ portions: constrainedPortions });
  },

  /**
   * Complete onboarding:
   * 1. Save preferences to API
   * 2. Mark onboarding as completed
   */
  completeOnboarding: async () => {
    set({ isLoading: true, error: null });

    try {
      const { dietaryPreferences, allergies, portions } = get();

      // Save preferences first
      await preferencesService.updatePreferences({
        dietary_preferences: dietaryPreferences,
        allergies: allergies,
        excluded_ingredients: [],
        preferred_ingredients: [],
        portions_count: portions,
      });

      // Mark onboarding as completed
      await onboardingService.completeOnboarding();

      set({
        isLoading: false,
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
   * Reset entire store to initial state
   */
  reset: () => {
    set(initialState);
  },
}));
