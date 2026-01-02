/**
 * Tests for recipes store
 *
 * Tests recipe browsing state management with Zustand
 */

import { useRecipesStore } from '../../stores/recipes';
import * as recipesService from '../../services/recipes';

// Mock recipes service
jest.mock('../../services/recipes', () => ({
  getCategories: jest.fn(),
  searchRecipes: jest.fn(),
  getRecipesByCategory: jest.fn(),
  getRecipeById: jest.fn(),
  getRandomRecipe: jest.fn(),
}));

// Mock data
const mockCategory = {
  id: '1',
  name: 'Beef',
  thumbnail: 'https://example.com/beef.png',
  description: 'Beef recipes',
};

const mockRecipeSummary = {
  id: '52771',
  name: 'Spicy Arrabiata Penne',
  thumbnail: 'https://example.com/pasta.jpg',
};

const mockRecipe = {
  id: '52771',
  name: 'Spicy Arrabiata Penne',
  category: 'Vegetarian',
  area: 'Italian',
  instructions: 'Cook the pasta...',
  thumbnail: 'https://example.com/pasta.jpg',
  tags: 'Pasta,Spicy',
  youtube: 'https://youtube.com/watch?v=123',
  source: 'https://example.com',
  ingredients: [
    { name: 'Penne', measure: '500g' },
    { name: 'Olive oil', measure: '2 tbsp' },
  ],
};

describe('useRecipesStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useRecipesStore.setState({
      recipes: [],
      categories: [],
      selectedRecipe: null,
      searchQuery: '',
      selectedCategory: null,
      isLoading: false,
      isCategoriesLoading: false,
      isDetailsLoading: false,
      error: null,
    });
    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useRecipesStore.getState();

      expect(state.recipes).toEqual([]);
      expect(state.categories).toEqual([]);
      expect(state.selectedRecipe).toBeNull();
      expect(state.searchQuery).toBe('');
      expect(state.selectedCategory).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.isCategoriesLoading).toBe(false);
      expect(state.isDetailsLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('fetchCategories', () => {
    it('should set loading state during fetch', async () => {
      (recipesService.getCategories as jest.Mock).mockResolvedValue({
        categories: [mockCategory],
      });

      const fetchPromise = useRecipesStore.getState().fetchCategories();

      expect(useRecipesStore.getState().isCategoriesLoading).toBe(true);

      await fetchPromise;

      expect(useRecipesStore.getState().isCategoriesLoading).toBe(false);
    });

    it('should update categories on success', async () => {
      (recipesService.getCategories as jest.Mock).mockResolvedValue({
        categories: [mockCategory],
      });

      await useRecipesStore.getState().fetchCategories();

      const state = useRecipesStore.getState();
      expect(state.categories).toEqual([mockCategory]);
      expect(state.error).toBeNull();
    });

    it('should handle error', async () => {
      (recipesService.getCategories as jest.Mock).mockRejectedValue(
        new Error('Network error')
      );

      await useRecipesStore.getState().fetchCategories();

      const state = useRecipesStore.getState();
      expect(state.categories).toEqual([]);
      expect(state.error).toBe('Network error');
      expect(state.isCategoriesLoading).toBe(false);
    });
  });

  describe('searchRecipes', () => {
    it('should set loading and search query', async () => {
      (recipesService.searchRecipes as jest.Mock).mockResolvedValue({
        recipes: [mockRecipeSummary],
      });

      const searchPromise = useRecipesStore.getState().searchRecipes('pasta');

      expect(useRecipesStore.getState().isLoading).toBe(true);
      expect(useRecipesStore.getState().searchQuery).toBe('pasta');

      await searchPromise;

      expect(useRecipesStore.getState().isLoading).toBe(false);
    });

    it('should clear selected category when searching', async () => {
      useRecipesStore.setState({ selectedCategory: 'Beef' });

      (recipesService.searchRecipes as jest.Mock).mockResolvedValue({
        recipes: [],
      });

      await useRecipesStore.getState().searchRecipes('pasta');

      expect(useRecipesStore.getState().selectedCategory).toBeNull();
    });

    it('should update recipes on success', async () => {
      (recipesService.searchRecipes as jest.Mock).mockResolvedValue({
        recipes: [mockRecipeSummary],
      });

      await useRecipesStore.getState().searchRecipes('pasta');

      const state = useRecipesStore.getState();
      expect(state.recipes).toEqual([mockRecipeSummary]);
      expect(state.error).toBeNull();
    });

    it('should handle error', async () => {
      (recipesService.searchRecipes as jest.Mock).mockRejectedValue(
        new Error('Search failed')
      );

      await useRecipesStore.getState().searchRecipes('pasta');

      const state = useRecipesStore.getState();
      expect(state.recipes).toEqual([]);
      expect(state.error).toBe('Search failed');
    });
  });

  describe('fetchRecipesByCategory', () => {
    it('should set loading and selected category', async () => {
      (recipesService.getRecipesByCategory as jest.Mock).mockResolvedValue({
        recipes: [mockRecipeSummary],
      });

      const fetchPromise = useRecipesStore.getState().fetchRecipesByCategory('Beef');

      expect(useRecipesStore.getState().isLoading).toBe(true);
      expect(useRecipesStore.getState().selectedCategory).toBe('Beef');

      await fetchPromise;
    });

    it('should clear search query when fetching by category', async () => {
      useRecipesStore.setState({ searchQuery: 'pasta' });

      (recipesService.getRecipesByCategory as jest.Mock).mockResolvedValue({
        recipes: [],
      });

      await useRecipesStore.getState().fetchRecipesByCategory('Beef');

      expect(useRecipesStore.getState().searchQuery).toBe('');
    });

    it('should update recipes on success', async () => {
      (recipesService.getRecipesByCategory as jest.Mock).mockResolvedValue({
        recipes: [mockRecipeSummary],
      });

      await useRecipesStore.getState().fetchRecipesByCategory('Vegetarian');

      const state = useRecipesStore.getState();
      expect(state.recipes).toEqual([mockRecipeSummary]);
      expect(recipesService.getRecipesByCategory).toHaveBeenCalledWith('Vegetarian');
    });

    it('should handle error', async () => {
      (recipesService.getRecipesByCategory as jest.Mock).mockRejectedValue(
        new Error('Category not found')
      );

      await useRecipesStore.getState().fetchRecipesByCategory('Invalid');

      const state = useRecipesStore.getState();
      expect(state.recipes).toEqual([]);
      expect(state.error).toBe('Category not found');
    });
  });

  describe('fetchRecipeDetails', () => {
    it('should set details loading state', async () => {
      (recipesService.getRecipeById as jest.Mock).mockResolvedValue({
        recipe: mockRecipe,
      });

      const fetchPromise = useRecipesStore.getState().fetchRecipeDetails('52771');

      expect(useRecipesStore.getState().isDetailsLoading).toBe(true);

      await fetchPromise;

      expect(useRecipesStore.getState().isDetailsLoading).toBe(false);
    });

    it('should update selected recipe on success', async () => {
      (recipesService.getRecipeById as jest.Mock).mockResolvedValue({
        recipe: mockRecipe,
      });

      await useRecipesStore.getState().fetchRecipeDetails('52771');

      const state = useRecipesStore.getState();
      expect(state.selectedRecipe).toEqual(mockRecipe);
      expect(state.error).toBeNull();
    });

    it('should handle error', async () => {
      (recipesService.getRecipeById as jest.Mock).mockRejectedValue(
        new Error('Recipe not found')
      );

      await useRecipesStore.getState().fetchRecipeDetails('99999');

      const state = useRecipesStore.getState();
      expect(state.selectedRecipe).toBeNull();
      expect(state.error).toBe('Recipe not found');
    });
  });

  describe('fetchRandomRecipe', () => {
    it('should update selected recipe on success', async () => {
      (recipesService.getRandomRecipe as jest.Mock).mockResolvedValue({
        recipe: mockRecipe,
      });

      await useRecipesStore.getState().fetchRandomRecipe();

      const state = useRecipesStore.getState();
      expect(state.selectedRecipe).toEqual(mockRecipe);
      expect(state.isDetailsLoading).toBe(false);
    });

    it('should handle error', async () => {
      (recipesService.getRandomRecipe as jest.Mock).mockRejectedValue(
        new Error('Failed to get random recipe')
      );

      await useRecipesStore.getState().fetchRandomRecipe();

      const state = useRecipesStore.getState();
      expect(state.error).toBe('Failed to get random recipe');
      expect(state.isDetailsLoading).toBe(false);
    });
  });

  describe('clearSearch', () => {
    it('should reset search-related state', () => {
      useRecipesStore.setState({
        searchQuery: 'pasta',
        selectedCategory: 'Beef',
        recipes: [mockRecipeSummary],
        error: 'Some error',
      });

      useRecipesStore.getState().clearSearch();

      const state = useRecipesStore.getState();
      expect(state.searchQuery).toBe('');
      expect(state.selectedCategory).toBeNull();
      expect(state.recipes).toEqual([]);
      expect(state.error).toBeNull();
    });
  });

  describe('clearSelectedRecipe', () => {
    it('should clear selected recipe', () => {
      useRecipesStore.setState({ selectedRecipe: mockRecipe });

      useRecipesStore.getState().clearSelectedRecipe();

      expect(useRecipesStore.getState().selectedRecipe).toBeNull();
    });
  });

  describe('reset', () => {
    it('should reset entire store to initial state', () => {
      useRecipesStore.setState({
        recipes: [mockRecipeSummary],
        categories: [mockCategory],
        selectedRecipe: mockRecipe,
        searchQuery: 'pasta',
        selectedCategory: 'Beef',
        isLoading: true,
        isCategoriesLoading: true,
        isDetailsLoading: true,
        error: 'Some error',
      });

      useRecipesStore.getState().reset();

      const state = useRecipesStore.getState();
      expect(state.recipes).toEqual([]);
      expect(state.categories).toEqual([]);
      expect(state.selectedRecipe).toBeNull();
      expect(state.searchQuery).toBe('');
      expect(state.selectedCategory).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.isCategoriesLoading).toBe(false);
      expect(state.isDetailsLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });
});
