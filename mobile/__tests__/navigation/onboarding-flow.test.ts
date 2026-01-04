/**
 * Navigation Integration Tests for Onboarding Flow
 *
 * Tests for Task Group 4: Navigation Integration
 * - Test getOnboardingStatus service returns correct format
 * - Test completeOnboarding service function exists
 * - Test onboarding store navigation actions exist
 */

import * as onboardingService from '../../services/onboarding';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock supabase
jest.mock('../../services/supabase', () => ({
  supabase: {
    auth: {
      getSession: jest.fn().mockResolvedValue({
        data: {
          session: {
            access_token: 'mock-token',
          },
        },
      }),
    },
  },
}));

describe('Onboarding Flow Navigation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Test 1: getOnboardingStatus returns correct response format
   */
  describe('getOnboardingStatus service', () => {
    it('should return onboarding_completed boolean', async () => {
      // Given: API returns success response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ onboarding_completed: false }),
      });

      // When: Call getOnboardingStatus
      const result = await onboardingService.getOnboardingStatus();

      // Then: Result should have correct shape
      expect(result).toHaveProperty('onboarding_completed');
      expect(typeof result.onboarding_completed).toBe('boolean');
    });

    it('should throw error when not authenticated', async () => {
      // Given: API returns 401
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Not authenticated' }),
      });

      // When/Then: Should throw error
      await expect(onboardingService.getOnboardingStatus()).rejects.toThrow(
        'Not authenticated'
      );
    });
  });

  /**
   * Test 2: completeOnboarding service function exists and works
   */
  describe('completeOnboarding service', () => {
    it('should complete successfully on 200 response', async () => {
      // Given: API returns success
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ onboarding_completed: true }),
      });

      // When: Call completeOnboarding
      await onboardingService.completeOnboarding();

      // Then: Should not throw
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should throw error on failure', async () => {
      // Given: API returns error
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      });

      // When/Then: Should throw error
      await expect(onboardingService.completeOnboarding()).rejects.toThrow(
        'Server error'
      );
    });
  });

  /**
   * Test 3: Onboarding store has required navigation actions
   */
  describe('Onboarding store navigation actions', () => {
    it('should have nextStep and prevStep actions', () => {
      const { useOnboardingStore } = require('../../stores/onboarding');
      const store = useOnboardingStore.getState();

      expect(typeof store.nextStep).toBe('function');
      expect(typeof store.prevStep).toBe('function');
      expect(typeof store.completeOnboarding).toBe('function');
      expect(typeof store.reset).toBe('function');
    });
  });
});
