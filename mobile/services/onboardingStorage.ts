/**
 * Onboarding Storage Service
 *
 * Uses AsyncStorage for non-sensitive onboarding flag
 * This data doesn't need secure storage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const ONBOARDING_KEY = 'hasSeenOnboarding';

/**
 * Check if user has seen onboarding
 */
export async function hasSeenOnboarding(): Promise<boolean> {
  const value = await AsyncStorage.getItem(ONBOARDING_KEY);
  return value === 'true';
}

/**
 * Mark onboarding as seen
 */
export async function setOnboardingSeen(): Promise<void> {
  await AsyncStorage.setItem(ONBOARDING_KEY, 'true');
}

/**
 * Reset onboarding flag (for testing)
 */
export async function resetOnboarding(): Promise<void> {
  await AsyncStorage.removeItem(ONBOARDING_KEY);
}
