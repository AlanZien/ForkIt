/**
 * Onboarding API Service
 *
 * Handles API calls for onboarding status management.
 * Uses the existing Supabase client for auth.
 *
 * Endpoints:
 * - GET /api/profile/onboarding-status
 * - PUT /api/profile/onboarding-completed
 */

import { supabase } from './supabase';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Onboarding status response
 */
export interface OnboardingStatus {
  onboarding_completed: boolean;
}

/**
 * Get auth headers with current session token
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error('Not authenticated');
  }

  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`,
  };
}

/**
 * Get user's onboarding status
 *
 * @returns Promise<OnboardingStatus> - The user's onboarding status
 * @throws Error if not authenticated or network error
 */
export async function getOnboardingStatus(): Promise<OnboardingStatus> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_URL}/api/profile/onboarding-status`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not authenticated');
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Mark user's onboarding as completed
 *
 * @returns Promise<void>
 * @throws Error if not authenticated or network error
 */
export async function completeOnboarding(): Promise<void> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_URL}/api/profile/onboarding-completed`, {
    method: 'PUT',
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not authenticated');
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }
}
