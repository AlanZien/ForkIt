/**
 * Secure Storage Service
 *
 * Uses expo-secure-store for sensitive data (tokens, biometric preferences)
 * Tokens are stored in iOS Keychain / Android Keystore
 * Falls back to localStorage on web
 */

import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

// Storage keys
const KEYS = {
  ACCESS_TOKEN: 'sb-access-token',
  REFRESH_TOKEN: 'sb-refresh-token',
  BIOMETRIC_ENABLED: 'biometricEnabled',
} as const;

/**
 * Platform-safe storage helpers
 */
async function setItem(key: string, value: string): Promise<void> {
  if (Platform.OS === 'web') {
    localStorage.setItem(key, value);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

async function getItem(key: string): Promise<string | null> {
  if (Platform.OS === 'web') {
    return localStorage.getItem(key);
  }
  return SecureStore.getItemAsync(key);
}

async function removeItem(key: string): Promise<void> {
  if (Platform.OS === 'web') {
    localStorage.removeItem(key);
    return;
  }
  await SecureStore.deleteItemAsync(key);
}

/**
 * Save authentication tokens securely
 */
export async function saveTokens(
  accessToken: string,
  refreshToken: string
): Promise<void> {
  await Promise.all([
    setItem(KEYS.ACCESS_TOKEN, accessToken),
    setItem(KEYS.REFRESH_TOKEN, refreshToken),
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
    getItem(KEYS.ACCESS_TOKEN),
    getItem(KEYS.REFRESH_TOKEN),
  ]);

  return { accessToken, refreshToken };
}

/**
 * Clear all authentication tokens
 */
export async function clearTokens(): Promise<void> {
  await Promise.all([
    removeItem(KEYS.ACCESS_TOKEN),
    removeItem(KEYS.REFRESH_TOKEN),
  ]);
}

/**
 * Save biometric preference
 */
export async function saveBiometricPreference(enabled: boolean): Promise<void> {
  await setItem(KEYS.BIOMETRIC_ENABLED, enabled ? 'true' : 'false');
}

/**
 * Get biometric preference
 */
export async function getBiometricPreference(): Promise<boolean> {
  const value = await getItem(KEYS.BIOMETRIC_ENABLED);
  return value === 'true';
}

/**
 * Clear biometric preference
 */
export async function clearBiometricPreference(): Promise<void> {
  await removeItem(KEYS.BIOMETRIC_ENABLED);
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
