/**
 * Tests for Onboarding Store
 *
 * Tests for Task Group 2: Onboarding Store
 * - Test initial state has step=1, selections empty
 * - Test setDietaryPreferences updates state correctly
 * - Test setAllergies updates state correctly
 * - Test setPortions updates state correctly
 * - Test nextStep increments step (max 5)
 * - Test prevStep decrements step (min 1)
 * - Test reset clears all state
 * - Test completeOnboarding calls API and navigates
 */

import { useOnboardingStore } from '../../stores/onboarding';
import * as onboardingService from '../../services/onboarding';
import * as preferencesService from '../../services/preferences';

// Mock the onboarding service
jest.mock('../../services/onboarding');

// Mock the preferences service
jest.mock('../../services/preferences');

// Mock expo-router
jest.mock('expo-router', () => ({
  router: {
    replace: jest.fn(),
  },
}));

const mockedOnboardingService = onboardingService as jest.Mocked<typeof onboardingService>;
const mockedPreferencesService = preferencesService as jest.Mocked<typeof preferencesService>;

describe('useOnboardingStore', () => {
  // Reset store state before each test
  beforeEach(() => {
    const store = useOnboardingStore.getState();
    store.reset();
    jest.clearAllMocks();
  });

  /**
   * Test 1: Initial state has step=1, selections empty
   */
  describe('Initial state', () => {
    it('should have correct initial state with step=1 and empty selections', () => {
      // Given: Store is initialized
      const state = useOnboardingStore.getState();

      // Then: Initial state should be correct
      expect(state.currentStep).toBe(1);
      expect(state.dietaryPreferences).toEqual([]);
      expect(state.allergies).toEqual([]);
      expect(state.portions).toBe(2);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  /**
   * Test 2: setDietaryPreferences updates state correctly
   */
  describe('setDietaryPreferences', () => {
    it('should update dietary preferences correctly', () => {
      // Given: Store initialized
      const store = useOnboardingStore.getState();

      // When: Set dietary preferences
      store.setDietaryPreferences(['vegetarian', 'vegan']);

      // Then: State should be updated
      const state = useOnboardingStore.getState();
      expect(state.dietaryPreferences).toEqual(['vegetarian', 'vegan']);
    });

    it('should allow empty dietary preferences', () => {
      // Given: Store with preferences
      useOnboardingStore.getState().setDietaryPreferences(['vegetarian']);

      // When: Clear preferences
      useOnboardingStore.getState().setDietaryPreferences([]);

      // Then: Preferences should be empty
      expect(useOnboardingStore.getState().dietaryPreferences).toEqual([]);
    });
  });

  /**
   * Test 3: setAllergies updates state correctly
   */
  describe('setAllergies', () => {
    it('should update allergies correctly', () => {
      // Given: Store initialized
      const store = useOnboardingStore.getState();

      // When: Set allergies
      store.setAllergies(['gluten', 'lactose', 'tree_nuts']);

      // Then: State should be updated
      const state = useOnboardingStore.getState();
      expect(state.allergies).toEqual(['gluten', 'lactose', 'tree_nuts']);
    });
  });

  /**
   * Test 4: setPortions updates state correctly
   */
  describe('setPortions', () => {
    it('should update portions correctly', () => {
      // Given: Store initialized
      const store = useOnboardingStore.getState();

      // When: Set portions
      store.setPortions(4);

      // Then: State should be updated
      expect(useOnboardingStore.getState().portions).toBe(4);
    });

    it('should respect minimum of 1', () => {
      // Given: Store initialized
      const store = useOnboardingStore.getState();

      // When: Try to set portions below minimum
      store.setPortions(0);

      // Then: Portions should be at minimum
      expect(useOnboardingStore.getState().portions).toBe(1);
    });

    it('should respect maximum of 12', () => {
      // Given: Store initialized
      const store = useOnboardingStore.getState();

      // When: Try to set portions above maximum
      store.setPortions(15);

      // Then: Portions should be at maximum
      expect(useOnboardingStore.getState().portions).toBe(12);
    });
  });

  /**
   * Test 5: nextStep increments step (max 5)
   */
  describe('nextStep', () => {
    it('should increment step', () => {
      // Given: Store at step 1
      expect(useOnboardingStore.getState().currentStep).toBe(1);

      // When: Call nextStep
      useOnboardingStore.getState().nextStep();

      // Then: Step should be 2
      expect(useOnboardingStore.getState().currentStep).toBe(2);
    });

    it('should not exceed step 5', () => {
      // Given: Store at step 5
      const store = useOnboardingStore.getState();
      store.nextStep(); // 2
      store.nextStep(); // 3
      store.nextStep(); // 4
      store.nextStep(); // 5
      expect(useOnboardingStore.getState().currentStep).toBe(5);

      // When: Try to go past step 5
      useOnboardingStore.getState().nextStep();

      // Then: Step should remain 5
      expect(useOnboardingStore.getState().currentStep).toBe(5);
    });
  });

  /**
   * Test 6: prevStep decrements step (min 1)
   */
  describe('prevStep', () => {
    it('should decrement step', () => {
      // Given: Store at step 3
      const store = useOnboardingStore.getState();
      store.nextStep();
      store.nextStep();
      expect(useOnboardingStore.getState().currentStep).toBe(3);

      // When: Call prevStep
      useOnboardingStore.getState().prevStep();

      // Then: Step should be 2
      expect(useOnboardingStore.getState().currentStep).toBe(2);
    });

    it('should not go below step 1', () => {
      // Given: Store at step 1
      expect(useOnboardingStore.getState().currentStep).toBe(1);

      // When: Try to go below step 1
      useOnboardingStore.getState().prevStep();

      // Then: Step should remain 1
      expect(useOnboardingStore.getState().currentStep).toBe(1);
    });
  });

  /**
   * Test 7: reset clears all state
   */
  describe('reset', () => {
    it('should clear all state to initial values', () => {
      // Given: Store with modified state
      const store = useOnboardingStore.getState();
      store.setDietaryPreferences(['vegetarian']);
      store.setAllergies(['gluten']);
      store.setPortions(6);
      store.nextStep();
      store.nextStep();

      expect(useOnboardingStore.getState().currentStep).toBe(3);
      expect(useOnboardingStore.getState().dietaryPreferences).toEqual(['vegetarian']);

      // When: Reset store
      useOnboardingStore.getState().reset();

      // Then: State should be initial
      const state = useOnboardingStore.getState();
      expect(state.currentStep).toBe(1);
      expect(state.dietaryPreferences).toEqual([]);
      expect(state.allergies).toEqual([]);
      expect(state.portions).toBe(2);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  /**
   * Test 8: completeOnboarding calls API
   */
  describe('completeOnboarding', () => {
    it('should call API and set loading state', async () => {
      // Given: Store with selections
      const store = useOnboardingStore.getState();
      store.setDietaryPreferences(['vegetarian']);
      store.setAllergies(['gluten']);
      store.setPortions(4);

      // Mock both services
      mockedPreferencesService.updatePreferences.mockResolvedValueOnce({
        dietary_preferences: ['vegetarian'],
        allergies: ['gluten'],
        excluded_ingredients: [],
        preferred_ingredients: [],
        portions_count: 4,
      });
      mockedOnboardingService.completeOnboarding.mockResolvedValueOnce(undefined);

      // When: Complete onboarding
      await useOnboardingStore.getState().completeOnboarding();

      // Then: API should be called and loading should be handled
      expect(mockedPreferencesService.updatePreferences).toHaveBeenCalledTimes(1);
      expect(mockedOnboardingService.completeOnboarding).toHaveBeenCalledTimes(1);
      expect(useOnboardingStore.getState().isLoading).toBe(false);
    });

    it('should handle API errors gracefully', async () => {
      // Given: API that will fail
      const errorMessage = 'Network error';
      mockedPreferencesService.updatePreferences.mockRejectedValueOnce(
        new Error(errorMessage)
      );

      // When: Complete onboarding fails
      await useOnboardingStore.getState().completeOnboarding();

      // Then: Error should be set
      const state = useOnboardingStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.isLoading).toBe(false);
    });

    it('should set isLoading during API call', async () => {
      // Given: Slow API
      let resolvePromise: () => void;
      const slowPromise = new Promise<void>((resolve) => {
        resolvePromise = resolve;
      });

      // Mock preferences to resolve immediately
      mockedPreferencesService.updatePreferences.mockResolvedValueOnce({
        dietary_preferences: [],
        allergies: [],
        excluded_ingredients: [],
        preferred_ingredients: [],
        portions_count: 2,
      });
      // Mock onboarding to be slow
      mockedOnboardingService.completeOnboarding.mockReturnValueOnce(slowPromise);

      // When: Start completing onboarding
      const completePromise = useOnboardingStore.getState().completeOnboarding();

      // Then: isLoading should be true
      expect(useOnboardingStore.getState().isLoading).toBe(true);

      // Cleanup
      resolvePromise!();
      await completePromise;
      expect(useOnboardingStore.getState().isLoading).toBe(false);
    });
  });
});
