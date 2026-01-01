/**
 * Preferences API Service
 *
 * Handles API calls for user preferences management.
 * Uses the existing API client with auth interceptor.
 *
 * Endpoints:
 * - GET /api/profile/preferences
 * - PUT /api/profile/preferences
 */

import type { UserPreferences, UserPreferencesUpdate } from '../types/preferences';
import { supabase } from './supabase';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

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
 * Fetch user preferences from the API
 *
 * @returns Promise<UserPreferences> - The user's preferences
 * @throws Error if not authenticated or network error
 */
export async function getPreferences(): Promise<UserPreferences> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_URL}/api/profile/preferences`, {
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
 * Update user preferences
 *
 * @param data - The preferences data to update
 * @returns Promise<UserPreferences> - The updated preferences
 * @throws Error if not authenticated, validation error, or network error
 */
export async function updatePreferences(data: UserPreferencesUpdate): Promise<UserPreferences> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_URL}/api/profile/preferences`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not authenticated');
    }
    if (response.status === 422) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Validation error');
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}
