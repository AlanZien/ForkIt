/**
 * Favorites Store using Zustand
 *
 * Manages user favorites state including list, add, remove, and check operations.
 *
 * State:
 * - favorites: List of user's favorite recipes
 * - favoriteIds: Set of recipe IDs for quick lookup
 * - isLoading: Loading state for list operations
 * - isUpdating: Loading state for add/remove operations
 * - error: Error message from last failed operation
 *
 * Actions:
 * - fetchFavorites: Load all user favorites
 * - addFavorite: Add a recipe to favorites
 * - removeFavorite: Remove a recipe from favorites
 * - isFavorite: Check if a recipe is favorite (sync)
 * - reset: Reset entire store
 */

import { create } from 'zustand';
import type { Favorite, FavoriteCreate } from '../types/favorite';
import * as favoritesService from '../services/favorites';

interface FavoritesState {
  // State
  favorites: Favorite[];
  favoriteIds: Set<string>;
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;

  // Actions
  fetchFavorites: () => Promise<void>;
  addFavorite: (data: FavoriteCreate) => Promise<void>;
  removeFavorite: (recipeId: string) => Promise<void>;
  isFavorite: (recipeId: string) => boolean;
  reset: () => void;
}

const initialState = {
  favorites: [] as Favorite[],
  favoriteIds: new Set<string>(),
  isLoading: false,
  isUpdating: false,
  error: null,
};

export const useFavoritesStore = create<FavoritesState>((set, get) => ({
  ...initialState,

  /**
   * Fetch all user favorites
   */
  fetchFavorites: async () => {
    set({ isLoading: true, error: null });

    try {
      const response = await favoritesService.getFavorites();
      const favoriteIds = new Set(response.favorites.map((f) => f.recipe_id));
      set({
        favorites: response.favorites,
        favoriteIds,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
      });
    }
  },

  /**
   * Add a recipe to favorites
   */
  addFavorite: async (data: FavoriteCreate) => {
    set({ isUpdating: true, error: null });

    try {
      const newFavorite = await favoritesService.addFavorite(data);
      set((state) => ({
        favorites: [newFavorite, ...state.favorites],
        favoriteIds: new Set([...state.favoriteIds, data.recipe_id]),
        isUpdating: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isUpdating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Remove a recipe from favorites
   */
  removeFavorite: async (recipeId: string) => {
    set({ isUpdating: true, error: null });

    try {
      await favoritesService.removeFavorite(recipeId);
      set((state) => {
        const newFavoriteIds = new Set(state.favoriteIds);
        newFavoriteIds.delete(recipeId);
        return {
          favorites: state.favorites.filter((f) => f.recipe_id !== recipeId),
          favoriteIds: newFavoriteIds,
          isUpdating: false,
        };
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isUpdating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Check if a recipe is favorite (synchronous)
   */
  isFavorite: (recipeId: string) => {
    return get().favoriteIds.has(recipeId);
  },

  /**
   * Reset entire store
   */
  reset: () => {
    set(initialState);
  },
}));
