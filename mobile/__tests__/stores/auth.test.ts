/**
 * Tests for auth store
 *
 * Tests authentication state management with Zustand
 */

import { useAuthStore } from '../../stores/auth';
import { supabase } from '../../services/supabase';
import * as secureStorage from '../../services/secureStorage';

// Mock supabase
jest.mock('../../services/supabase', () => ({
  supabase: {
    auth: {
      signInWithPassword: jest.fn(),
      signUp: jest.fn(),
      signOut: jest.fn(),
      getSession: jest.fn(),
      refreshSession: jest.fn(),
    },
  },
}));

// Mock secureStorage
jest.mock('../../services/secureStorage', () => ({
  saveTokens: jest.fn(),
  clearTokens: jest.fn(),
  saveBiometricPreference: jest.fn(),
  getBiometricPreference: jest.fn(),
  clearBiometricPreference: jest.fn(),
}));

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: false,
      emailVerified: false,
      biometricEnabled: false,
    });
    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.session).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
      expect(state.emailVerified).toBe(false);
      expect(state.biometricEnabled).toBe(false);
    });
  });

  describe('login', () => {
    it('should set loading state during login', async () => {
      const mockUser = { id: 'user-123', email: 'test@test.com', email_confirmed_at: '2024-01-01' };
      const mockSession = { access_token: 'token', refresh_token: 'refresh' };

      (supabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      const loginPromise = useAuthStore.getState().login('test@test.com', 'password');

      // Check loading state is set
      expect(useAuthStore.getState().isLoading).toBe(true);

      await loginPromise;

      expect(useAuthStore.getState().isLoading).toBe(false);
    });

    it('should update state on successful login', async () => {
      const mockUser = { id: 'user-123', email: 'test@test.com', email_confirmed_at: '2024-01-01' };
      const mockSession = { access_token: 'token', refresh_token: 'refresh' };

      (supabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      await useAuthStore.getState().login('test@test.com', 'password');

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.session).toEqual(mockSession);
      expect(state.isAuthenticated).toBe(true);
      expect(state.emailVerified).toBe(true);
    });

    it('should save tokens on successful login', async () => {
      const mockSession = { access_token: 'token', refresh_token: 'refresh' };

      (supabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        data: { user: { id: '1' }, session: mockSession },
        error: null,
      });

      await useAuthStore.getState().login('test@test.com', 'password');

      expect(secureStorage.saveTokens).toHaveBeenCalledWith('token', 'refresh');
    });

    it('should throw error on failed login', async () => {
      (supabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        data: { user: null, session: null },
        error: new Error('Invalid credentials'),
      });

      await expect(
        useAuthStore.getState().login('test@test.com', 'wrong')
      ).rejects.toThrow('Invalid credentials');

      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe('register', () => {
    it('should not set isAuthenticated after registration (email verification required)', async () => {
      const mockUser = { id: 'user-123', email: 'test@test.com' };

      (supabase.auth.signUp as jest.Mock).mockResolvedValue({
        data: { user: mockUser, session: null },
        error: null,
      });

      await useAuthStore.getState().register('Test User', 'test@test.com', 'password');

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(false);
      expect(state.emailVerified).toBe(false);
    });

    it('should throw error on failed registration', async () => {
      (supabase.auth.signUp as jest.Mock).mockResolvedValue({
        data: { user: null, session: null },
        error: new Error('Email already exists'),
      });

      await expect(
        useAuthStore.getState().register('Test', 'existing@test.com', 'password')
      ).rejects.toThrow('Email already exists');
    });
  });

  describe('logout', () => {
    it('should clear all auth state', async () => {
      // Set initial authenticated state
      useAuthStore.setState({
        user: { id: '1' } as any,
        session: { access_token: 'token' } as any,
        isAuthenticated: true,
        emailVerified: true,
        biometricEnabled: true,
      });

      (supabase.auth.signOut as jest.Mock).mockResolvedValue({});

      await useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.session).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.emailVerified).toBe(false);
      expect(state.biometricEnabled).toBe(false);
    });

    it('should clear tokens and biometric preference', async () => {
      (supabase.auth.signOut as jest.Mock).mockResolvedValue({});

      await useAuthStore.getState().logout();

      expect(secureStorage.clearTokens).toHaveBeenCalled();
      expect(secureStorage.clearBiometricPreference).toHaveBeenCalled();
    });
  });

  describe('checkSession', () => {
    it('should restore session if exists', async () => {
      const mockSession = {
        user: { id: '1', email_confirmed_at: '2024-01-01' },
        access_token: 'token',
      };

      (supabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: mockSession },
        error: null,
      });
      (secureStorage.getBiometricPreference as jest.Mock).mockResolvedValue(true);

      await useAuthStore.getState().checkSession();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.emailVerified).toBe(true);
      expect(state.biometricEnabled).toBe(true);
    });

    it('should reset state if no session', async () => {
      (supabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: null },
        error: null,
      });

      await useAuthStore.getState().checkSession();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
    });
  });

  describe('setBiometric', () => {
    it('should save biometric preference', async () => {
      await useAuthStore.getState().setBiometric(true);

      expect(secureStorage.saveBiometricPreference).toHaveBeenCalledWith(true);
      expect(useAuthStore.getState().biometricEnabled).toBe(true);
    });
  });

  describe('setLoading', () => {
    it('should update loading state', () => {
      useAuthStore.getState().setLoading(true);
      expect(useAuthStore.getState().isLoading).toBe(true);

      useAuthStore.getState().setLoading(false);
      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });
});
