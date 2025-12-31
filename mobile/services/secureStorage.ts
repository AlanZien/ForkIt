/**
 * Secure Storage Service
 *
 * Uses expo-secure-store for sensitive data (tokens, biometric preferences)
 * Tokens are stored in iOS Keychain / Android Keystore
 */

import * as SecureStore from 'expo-secure-store';

// Storage keys
const KEYS = {
  ACCESS_TOKEN: 'sb-access-token',
  REFRESH_TOKEN: 'sb-refresh-token',
  BIOMETRIC_ENABLED: 'biometricEnabled',
} as const;

/**
 * Save authentication tokens securely
 */
export async function saveTokens(
  accessToken: string,
  refreshToken: string
): Promise<void> {
  await Promise.all([
    SecureStore.setItemAsync(KEYS.ACCESS_TOKEN, accessToken),
    SecureStore.setItemAsync(KEYS.REFRESH_TOKEN, refreshToken),
  ]);
}

/**
 * Retrieve stored tokens
 */
export async function getTokens(): Promise<{
  accessToken: string | null;
  refreshToken: string | null;
}> {
  const [accessToken, refreshToken] = await Promise.all([
    SecureStore.getItemAsync(KEYS.ACCESS_TOKEN),
    SecureStore.getItemAsync(KEYS.REFRESH_TOKEN),
  ]);

  return { accessToken, refreshToken };
}

/**
 * Clear all authentication tokens
 */
export async function clearTokens(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(KEYS.ACCESS_TOKEN),
    SecureStore.deleteItemAsync(KEYS.REFRESH_TOKEN),
  ]);
}

/**
 * Save biometric preference
 */
export async function saveBiometricPreference(enabled: boolean): Promise<void> {
  await SecureStore.setItemAsync(KEYS.BIOMETRIC_ENABLED, enabled ? 'true' : 'false');
}

/**
 * Get biometric preference
 */
export async function getBiometricPreference(): Promise<boolean> {
  const value = await SecureStore.getItemAsync(KEYS.BIOMETRIC_ENABLED);
  return value === 'true';
}

/**
 * Clear biometric preference
 */
export async function clearBiometricPreference(): Promise<void> {
  await SecureStore.deleteItemAsync(KEYS.BIOMETRIC_ENABLED);
}

/**
 * Clear all secure storage (tokens + preferences)
 */
export async function clearAll(): Promise<void> {
  await Promise.all([
    clearTokens(),
    clearBiometricPreference(),
  ]);
}
