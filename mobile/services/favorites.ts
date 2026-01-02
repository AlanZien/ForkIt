/**
 * Favorites API Service
 *
 * Handles API calls for user favorites (requires authentication).
 *
 * Endpoints:
 * - GET /api/favorites - Get all user favorites
 * - POST /api/favorites - Add a favorite
 * - DELETE /api/favorites/{recipe_id} - Remove a favorite
 * - GET /api/favorites/{recipe_id} - Check if recipe is favorite
 */

import type {
  Favorite,
  FavoriteCreate,
  FavoriteListResponse,
  FavoriteStatus,
} from '../types/favorite';
import { api } from './api';

/**
 * Get all favorites for current user
 */
export async function getFavorites(): Promise<FavoriteListResponse> {
  return api.get<FavoriteListResponse>('/api/favorites');
}

/**
 * Add a recipe to favorites
 */
export async function addFavorite(data: FavoriteCreate): Promise<Favorite> {
  return api.post<Favorite>('/api/favorites', data);
}

/**
 * Remove a recipe from favorites
 */
export async function removeFavorite(recipeId: string): Promise<void> {
  await api.delete<void>(`/api/favorites/${recipeId}`);
}

/**
 * Check if a recipe is in favorites
 */
export async function checkFavorite(recipeId: string): Promise<FavoriteStatus> {
  return api.get<FavoriteStatus>(`/api/favorites/${recipeId}`);
}
