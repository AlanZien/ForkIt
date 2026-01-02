/**
 * Tests for secureStorage service
 *
 * Tests secure token storage with platform-specific behavior
 */

import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import {
  saveTokens,
  getTokens,
  clearTokens,
  saveBiometricPreference,
  getBiometricPreference,
  clearBiometricPreference,
  clearAll,
} from '../../services/secureStorage';

// Mock react-native Platform
jest.mock('react-native', () => ({
  Platform: {
    OS: 'ios', // Default to iOS for tests
  },
}));

// Mock expo-secure-store
jest.mock('expo-secure-store', () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

// Mock localStorage for web tests
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(global, 'localStorage', { value: localStorageMock });

// Mock console.warn to check for web warnings
const originalWarn = console.warn;
let consoleWarnMock: jest.SpyInstance;

describe('secureStorage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    consoleWarnMock = jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleWarnMock.mockRestore();
  });

  describe('on iOS/Android (native)', () => {
    beforeAll(() => {
      (Platform as any).OS = 'ios';
    });

    describe('saveTokens', () => {
      it('should save both tokens to SecureStore', async () => {
        await saveTokens('access-token', 'refresh-token');

        expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
          'sb-access-token',
          'access-token'
        );
        expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
          'sb-refresh-token',
          'refresh-token'
        );
      });
    });

    describe('getTokens', () => {
      it('should retrieve both tokens from SecureStore', async () => {
        (SecureStore.getItemAsync as jest.Mock)
          .mockResolvedValueOnce('access-token')
          .mockResolvedValueOnce('refresh-token');

        const result = await getTokens();

        expect(result).toEqual({
          accessToken: 'access-token',
          refreshToken: 'refresh-token',
        });
      });

      it('should return null for missing tokens', async () => {
        (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

        const result = await getTokens();

        expect(result).toEqual({
          accessToken: null,
          refreshToken: null,
        });
      });
    });

    describe('clearTokens', () => {
      it('should delete both tokens from SecureStore', async () => {
        await clearTokens();

        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('sb-access-token');
        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('sb-refresh-token');
      });
    });

    describe('saveBiometricPreference', () => {
      it('should save true as "true" string', async () => {
        await saveBiometricPreference(true);

        expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
          'biometricEnabled',
          'true'
        );
      });

      it('should save false as "false" string', async () => {
        await saveBiometricPreference(false);

        expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
          'biometricEnabled',
          'false'
        );
      });
    });

    describe('getBiometricPreference', () => {
      it('should return true when stored value is "true"', async () => {
        (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('true');

        const result = await getBiometricPreference();

        expect(result).toBe(true);
      });

      it('should return false when stored value is "false"', async () => {
        (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('false');

        const result = await getBiometricPreference();

        expect(result).toBe(false);
      });

      it('should return false when no value stored', async () => {
        (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

        const result = await getBiometricPreference();

        expect(result).toBe(false);
      });
    });

    describe('clearBiometricPreference', () => {
      it('should delete biometric preference', async () => {
        await clearBiometricPreference();

        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('biometricEnabled');
      });
    });

    describe('clearAll', () => {
      it('should clear tokens and biometric preference', async () => {
        await clearAll();

        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('sb-access-token');
        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('sb-refresh-token');
        expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('biometricEnabled');
      });
    });
  });

  describe('on web', () => {
    beforeAll(() => {
      (Platform as any).OS = 'web';
    });

    afterAll(() => {
      (Platform as any).OS = 'ios';
    });

    describe('saveTokens', () => {
      it('should save tokens to localStorage on web', async () => {
        await saveTokens('access-token', 'refresh-token');

        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'sb-access-token',
          'access-token'
        );
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'sb-refresh-token',
          'refresh-token'
        );
      });

      it('should log a warning about localStorage security', async () => {
        await saveTokens('token', 'refresh');

        expect(consoleWarnMock).toHaveBeenCalledWith(
          expect.stringContaining('localStorage')
        );
      });
    });

    describe('getTokens', () => {
      it('should retrieve tokens from localStorage on web', async () => {
        localStorageMock.getItem
          .mockReturnValueOnce('access-token')
          .mockReturnValueOnce('refresh-token');

        const result = await getTokens();

        expect(result).toEqual({
          accessToken: 'access-token',
          refreshToken: 'refresh-token',
        });
      });
    });

    describe('clearTokens', () => {
      it('should remove tokens from localStorage on web', async () => {
        await clearTokens();

        expect(localStorageMock.removeItem).toHaveBeenCalledWith('sb-access-token');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('sb-refresh-token');
      });
    });
  });
});
