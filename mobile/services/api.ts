/**
 * API client for ForkIt backend
 *
 * Handles authenticated requests with automatic token refresh.
 */

import { getTokens, saveTokens } from './secureStorage';
import { supabase } from './supabase';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private isRefreshing = false;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const { accessToken } = await getTokens();
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    return headers;
  }

  private async refreshToken(): Promise<boolean> {
    if (this.isRefreshing) return false;

    this.isRefreshing = true;
    try {
      const { data, error } = await supabase.auth.refreshSession();
      if (error || !data.session) {
        return false;
      }
      await saveTokens(data.session.access_token, data.session.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      this.isRefreshing = false;
    }
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    retried = false
  ): Promise<T> {
    const headers = await this.getAuthHeaders();
    const options: RequestInit = {
      method,
      headers,
    };

    if (data !== undefined) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);

    // Handle 401 - try to refresh token and retry once
    if (response.status === 401 && !retried) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        return this.request<T>(method, endpoint, data, true);
      }
    }

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    // Handle 204 No Content responses
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>('GET', endpoint);
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }

  /**
   * Upload a file using multipart/form-data
   */
  async uploadFile<T>(endpoint: string, file: FormData): Promise<T> {
    const { accessToken } = await getTokens();
    const headers: Record<string, string> = {};

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: file,
    });

    if (response.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        const newHeaders: Record<string, string> = {};
        const tokens = await getTokens();
        if (tokens.accessToken) {
          newHeaders['Authorization'] = `Bearer ${tokens.accessToken}`;
        }
        const retryResponse = await fetch(`${this.baseUrl}${endpoint}`, {
          method: 'POST',
          headers: newHeaders,
          body: file,
        });
        if (!retryResponse.ok) {
          throw new Error(`API Error: ${retryResponse.status}`);
        }
        return retryResponse.json();
      }
    }

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
}

export const api = new ApiClient(API_URL);
