/**
 * Recipes API Service
 *
 * Handles API calls for recipe browsing and search.
 * These endpoints are public and don't require authentication.
 *
 * Endpoints:
 * - GET /api/recipes/search?q=...
 * - GET /api/recipes/{id}
 * - GET /api/recipes/random
 * - GET /api/recipes/categories
 * - GET /api/recipes/category/{name}
 */

import type {
  CategoryListResponse,
  RecipeDetailResponse,
  RecipeListResponse,
  UnifiedSearchResponse,
} from '../types/recipe';
import { api } from './api';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Search recipes by name
 */
export async function searchRecipes(query: string): Promise<RecipeListResponse> {
  const response = await fetch(
    `${API_URL}/api/recipes/search?q=${encodeURIComponent(query)}`,
    {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get recipe details by ID
 */
export async function getRecipeById(id: string): Promise<RecipeDetailResponse> {
  const response = await fetch(`${API_URL}/api/recipes/${id}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Recipe not found');
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get a random recipe
 */
export async function getRandomRecipe(): Promise<RecipeDetailResponse> {
  const response = await fetch(`${API_URL}/api/recipes/random`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get all recipe categories
 */
export async function getCategories(): Promise<CategoryListResponse> {
  const response = await fetch(`${API_URL}/api/recipes/categories`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get recipes by category
 */
export async function getRecipesByCategory(
  categoryName: string
): Promise<RecipeListResponse> {
  const response = await fetch(
    `${API_URL}/api/recipes/category/${encodeURIComponent(categoryName)}`,
    {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Unified search across personal and API recipes
 * Requires authentication for personal recipes
 */
export async function unifiedSearchRecipes(
  query: string
): Promise<UnifiedSearchResponse> {
  return api.get<UnifiedSearchResponse>(
    `/api/recipes/unified-search?q=${encodeURIComponent(query)}`
  );
}
