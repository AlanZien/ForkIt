/**
 * Biometric Authentication Service
 *
 * Handles Face ID (iOS) and Fingerprint (Android) authentication
 */

import * as LocalAuthentication from 'expo-local-authentication';

export type BiometricType = 'face' | 'fingerprint' | 'iris' | 'none';

interface BiometricSupport {
  supported: boolean;
  types: BiometricType[];
}

/**
 * Check if device supports biometric authentication
 */
export async function checkBiometricSupport(): Promise<BiometricSupport> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();

  if (!hasHardware) {
    return { supported: false, types: [] };
  }

  const isEnrolled = await LocalAuthentication.isEnrolledAsync();

  if (!isEnrolled) {
    return { supported: false, types: [] };
  }

  const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

  const types: BiometricType[] = supportedTypes.map((type) => {
    switch (type) {
      case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
        return 'face';
      case LocalAuthentication.AuthenticationType.FINGERPRINT:
        return 'fingerprint';
      case LocalAuthentication.AuthenticationType.IRIS:
        return 'iris';
      default:
        return 'none';
    }
  }).filter((t): t is BiometricType => t !== 'none');

  return {
    supported: types.length > 0,
    types,
  };
}

/**
 * Get the primary biometric type available
 */
export async function getBiometricType(): Promise<BiometricType> {
  const { supported, types } = await checkBiometricSupport();

  if (!supported || types.length === 0) {
    return 'none';
  }

  // Prefer Face ID over Fingerprint
  if (types.includes('face')) return 'face';
  if (types.includes('fingerprint')) return 'fingerprint';
  if (types.includes('iris')) return 'iris';

  return 'none';
}

/**
 * Prompt for biometric authentication
 */
export async function authenticate(
  promptMessage: string = 'Authentifiez-vous pour continuer'
): Promise<boolean> {
  const { supported } = await checkBiometricSupport();

  if (!supported) {
    return false;
  }

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage,
    cancelLabel: 'Annuler',
    disableDeviceFallback: false, // Allow PIN fallback
    fallbackLabel: 'Utiliser le code',
  });

  return result.success;
}

/**
 * Get user-friendly name for biometric type
 */
export function getBiometricLabel(type: BiometricType): string {
  switch (type) {
    case 'face':
      return 'Face ID';
    case 'fingerprint':
      return 'Touch ID';
    case 'iris':
      return 'Iris';
    default:
      return 'Biométrie';
  }
}
