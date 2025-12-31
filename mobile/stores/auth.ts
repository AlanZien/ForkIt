/**
 * Authentication store using Zustand
 *
 * Manages authentication state, tokens, and biometric preferences
 */

import { create } from 'zustand';
import type { User, Session } from '@supabase/supabase-js';
import { supabase } from '../services/supabase';
import {
  saveTokens,
  clearTokens,
  saveBiometricPreference,
  getBiometricPreference,
  clearBiometricPreference,
} from '../services/secureStorage';

interface AuthState {
  // State
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  emailVerified: boolean;
  biometricEnabled: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
  refreshSession: () => Promise<void>;
  setBiometric: (enabled: boolean) => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Initial state
  user: null,
  session: null,
  isAuthenticated: false,
  isLoading: true,
  emailVerified: false,
  biometricEnabled: false,

  /**
   * Log in with email and password
   */
  login: async (email: string, password: string) => {
    set({ isLoading: true });

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      if (data.session) {
        await saveTokens(data.session.access_token, data.session.refresh_token);
      }

      const emailVerified = !!data.user?.email_confirmed_at;

      set({
        user: data.user,
        session: data.session,
        isAuthenticated: true,
        emailVerified,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  /**
   * Register a new user
   */
  register: async (name: string, email: string, password: string) => {
    set({ isLoading: true });

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { name },
        },
      });

      if (error) throw error;

      // After registration, user needs to verify email
      set({
        user: data.user,
        session: data.session,
        isAuthenticated: false, // Not authenticated until email verified
        emailVerified: false,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  /**
   * Log out and clear all auth data
   */
  logout: async () => {
    set({ isLoading: true });

    try {
      await supabase.auth.signOut();
      await clearTokens();
      await clearBiometricPreference();

      set({
        user: null,
        session: null,
        isAuthenticated: false,
        emailVerified: false,
        biometricEnabled: false,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  /**
   * Check existing session on app launch
   */
  checkSession: async () => {
    set({ isLoading: true });

    try {
      const { data, error } = await supabase.auth.getSession();

      if (error) throw error;

      if (data.session) {
        const emailVerified = !!data.session.user?.email_confirmed_at;
        const biometricEnabled = await getBiometricPreference();

        set({
          user: data.session.user,
          session: data.session,
          isAuthenticated: emailVerified,
          emailVerified,
          biometricEnabled,
          isLoading: false,
        });
      } else {
        set({
          user: null,
          session: null,
          isAuthenticated: false,
          emailVerified: false,
          isLoading: false,
        });
      }
    } catch (error) {
      set({
        user: null,
        session: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  /**
   * Refresh the current session
   */
  refreshSession: async () => {
    try {
      const { data, error } = await supabase.auth.refreshSession();

      if (error) throw error;

      if (data.session) {
        await saveTokens(data.session.access_token, data.session.refresh_token);

        set({
          session: data.session,
          user: data.session.user,
        });
      }
    } catch (error) {
      // On refresh failure, logout
      await get().logout();
    }
  },

  /**
   * Enable or disable biometric authentication
   */
  setBiometric: async (enabled: boolean) => {
    await saveBiometricPreference(enabled);
    set({ biometricEnabled: enabled });
  },

  /**
   * Set loading state
   */
  setLoading: (isLoading: boolean) => set({ isLoading }),
}));
