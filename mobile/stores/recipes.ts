/**
 * Recipes Store using Zustand
 *
 * Manages recipe browsing state including search, categories, and details.
 *
 * State:
 * - recipes: Current list of recipes (search results or category)
 * - categories: Available recipe categories
 * - selectedRecipe: Currently viewed recipe details
 * - searchQuery: Current search query
 * - selectedCategory: Currently selected category
 * - isLoading: Loading state for API calls
 * - error: Error message from last failed operation
 *
 * Actions:
 * - fetchCategories: Load all categories
 * - searchRecipes: Search recipes by name
 * - fetchRecipesByCategory: Load recipes for a category
 * - fetchRecipeDetails: Load full recipe details
 * - fetchRandomRecipe: Get a random recipe
 * - clearSearch: Reset search state
 * - reset: Reset entire store
 */

import { create } from 'zustand';
import type { Category, Recipe, RecipeSummary, UnifiedRecipeSummary } from '../types/recipe';
import * as recipesService from '../services/recipes';

interface RecipesState {
  // State
  recipes: RecipeSummary[];
  unifiedResults: UnifiedRecipeSummary[];
  categories: Category[];
  selectedRecipe: Recipe | null;
  searchQuery: string;
  selectedCategory: string | null;
  isLoading: boolean;
  isCategoriesLoading: boolean;
  isDetailsLoading: boolean;
  error: string | null;
  isUnifiedSearch: boolean;
  personalCount: number;
  apiCount: number;

  // Actions
  fetchCategories: () => Promise<void>;
  searchRecipes: (query: string) => Promise<void>;
  unifiedSearchRecipes: (query: string) => Promise<void>;
  fetchRecipesByCategory: (category: string) => Promise<void>;
  fetchRecipeDetails: (id: string) => Promise<void>;
  fetchRandomRecipe: () => Promise<void>;
  clearSearch: () => void;
  clearSelectedRecipe: () => void;
  reset: () => void;
}

const initialState = {
  recipes: [],
  unifiedResults: [],
  categories: [],
  selectedRecipe: null,
  searchQuery: '',
  selectedCategory: null,
  isLoading: false,
  isCategoriesLoading: false,
  isDetailsLoading: false,
  error: null,
  isUnifiedSearch: false,
  personalCount: 0,
  apiCount: 0,
};

export const useRecipesStore = create<RecipesState>((set) => ({
  ...initialState,

  /**
   * Fetch all recipe categories
   */
  fetchCategories: async () => {
    set({ isCategoriesLoading: true, error: null });

    try {
      const response = await recipesService.getCategories();
      set({
        categories: response.categories,
        isCategoriesLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isCategoriesLoading: false,
        error: message,
      });
    }
  },

  /**
   * Search recipes by name
   */
  searchRecipes: async (query: string) => {
    set({ isLoading: true, error: null, searchQuery: query, selectedCategory: null, isUnifiedSearch: false });

    try {
      const response = await recipesService.searchRecipes(query);
      set({
        recipes: response.recipes,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
        recipes: [],
      });
    }
  },

  /**
   * Unified search across personal and API recipes
   */
  unifiedSearchRecipes: async (query: string) => {
    set({
      isLoading: true,
      error: null,
      searchQuery: query,
      selectedCategory: null,
      isUnifiedSearch: true,
    });

    try {
      const response = await recipesService.unifiedSearchRecipes(query);
      set({
        unifiedResults: response.recipes,
        personalCount: response.personal_count,
        apiCount: response.api_count,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
        unifiedResults: [],
        personalCount: 0,
        apiCount: 0,
      });
    }
  },

  /**
   * Fetch recipes by category
   */
  fetchRecipesByCategory: async (category: string) => {
    set({ isLoading: true, error: null, selectedCategory: category, searchQuery: '' });

    try {
      const response = await recipesService.getRecipesByCategory(category);
      set({
        recipes: response.recipes,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
        recipes: [],
      });
    }
  },

  /**
   * Fetch full recipe details by ID
   */
  fetchRecipeDetails: async (id: string) => {
    set({ isDetailsLoading: true, error: null });

    try {
      const response = await recipesService.getRecipeById(id);
      set({
        selectedRecipe: response.recipe,
        isDetailsLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isDetailsLoading: false,
        error: message,
        selectedRecipe: null,
      });
    }
  },

  /**
   * Fetch a random recipe
   */
  fetchRandomRecipe: async () => {
    set({ isDetailsLoading: true, error: null });

    try {
      const response = await recipesService.getRandomRecipe();
      set({
        selectedRecipe: response.recipe,
        isDetailsLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isDetailsLoading: false,
        error: message,
      });
    }
  },

  /**
   * Clear search and reset to initial recipe list
   */
  clearSearch: () => {
    set({
      searchQuery: '',
      selectedCategory: null,
      recipes: [],
      unifiedResults: [],
      error: null,
      isUnifiedSearch: false,
      personalCount: 0,
      apiCount: 0,
    });
  },

  /**
   * Clear selected recipe
   */
  clearSelectedRecipe: () => {
    set({ selectedRecipe: null });
  },

  /**
   * Reset entire store
   */
  reset: () => {
    set(initialState);
  },
}));
