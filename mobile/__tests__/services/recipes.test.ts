/**
 * Tests for Recipes API Service
 *
 * Tests recipe API calls (public endpoints, no auth required)
 */

import {
  searchRecipes,
  getRecipeById,
  getRandomRecipe,
  getCategories,
  getRecipesByCategory,
} from '../../services/recipes';

// Mock fetch
global.fetch = jest.fn();

// Mock data
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

const mockCategory = {
  id: '1',
  name: 'Beef',
  thumbnail: 'https://example.com/beef.png',
  description: 'Beef recipes',
};

describe('Recipes Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockReset();
  });

  describe('searchRecipes', () => {
    it('should make GET request with encoded query', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipes: [mockRecipeSummary] }),
      });

      const result = await searchRecipes('pasta & cheese');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/recipes/search?q=pasta%20%26%20cheese'),
        expect.objectContaining({
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(result.recipes).toEqual([mockRecipeSummary]);
    });

    it('should throw error on failed search', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal server error' }),
      });

      await expect(searchRecipes('test')).rejects.toThrow('Internal server error');
    });

    it('should handle empty results', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipes: [] }),
      });

      const result = await searchRecipes('nonexistent');

      expect(result.recipes).toEqual([]);
    });
  });

  describe('getRecipeById', () => {
    it('should fetch recipe details by ID', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipe: mockRecipe }),
      });

      const result = await getRecipeById('52771');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/recipes/52771'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.recipe).toEqual(mockRecipe);
    });

    it('should throw "Recipe not found" on 404', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      });

      await expect(getRecipeById('99999')).rejects.toThrow('Recipe not found');
    });

    it('should throw error with detail on other errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Database error' }),
      });

      await expect(getRecipeById('52771')).rejects.toThrow('Database error');
    });
  });

  describe('getRandomRecipe', () => {
    it('should fetch random recipe', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipe: mockRecipe }),
      });

      const result = await getRandomRecipe();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/recipes/random'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.recipe).toEqual(mockRecipe);
    });

    it('should throw error on failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 503,
        json: () => Promise.resolve({ detail: 'Service unavailable' }),
      });

      await expect(getRandomRecipe()).rejects.toThrow('Service unavailable');
    });
  });

  describe('getCategories', () => {
    it('should fetch all categories', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ categories: [mockCategory] }),
      });

      const result = await getCategories();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/recipes/categories'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.categories).toEqual([mockCategory]);
    });

    it('should throw error on failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({}),
      });

      await expect(getCategories()).rejects.toThrow('API Error: 500');
    });
  });

  describe('getRecipesByCategory', () => {
    it('should fetch recipes by category with encoded name', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipes: [mockRecipeSummary] }),
      });

      const result = await getRecipesByCategory('Beef & Lamb');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/recipes/category/Beef%20%26%20Lamb'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.recipes).toEqual([mockRecipeSummary]);
    });

    it('should throw error on failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Category not found' }),
      });

      await expect(getRecipesByCategory('InvalidCategory')).rejects.toThrow(
        'Category not found'
      );
    });

    it('should handle empty category results', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ recipes: [] }),
      });

      const result = await getRecipesByCategory('EmptyCategory');

      expect(result.recipes).toEqual([]);
    });
  });

  describe('error handling', () => {
    it('should handle JSON parse failure gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('Invalid JSON')),
      });

      await expect(searchRecipes('test')).rejects.toThrow('API Error: 500');
    });
  });
});
