/**
 * Tests for Favorites API Service
 *
 * Tests favorite API calls (requires authentication)
 */

import {
  getFavorites,
  addFavorite,
  removeFavorite,
  checkFavorite,
} from '../../services/favorites';

// Mock the api module
jest.mock('../../services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  },
}));

import { api } from '../../services/api';

// Mock data
const mockFavorite = {
  id: 'fav-123',
  recipe_id: '52771',
  recipe_name: 'Spicy Arrabiata Penne',
  recipe_thumbnail: 'https://example.com/pasta.jpg',
  created_at: '2026-01-02T10:00:00Z',
};

describe('Favorites Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getFavorites', () => {
    it('should fetch all favorites', async () => {
      const mockResponse = {
        favorites: [mockFavorite],
        count: 1,
      };
      (api.get as jest.Mock).mockResolvedValue(mockResponse);

      const result = await getFavorites();

      expect(api.get).toHaveBeenCalledWith('/api/favorites');
      expect(result).toEqual(mockResponse);
    });

    it('should return empty list when no favorites', async () => {
      const mockResponse = { favorites: [], count: 0 };
      (api.get as jest.Mock).mockResolvedValue(mockResponse);

      const result = await getFavorites();

      expect(result.favorites).toEqual([]);
      expect(result.count).toBe(0);
    });

    it('should throw on API error', async () => {
      (api.get as jest.Mock).mockRejectedValue(new Error('API Error: 401'));

      await expect(getFavorites()).rejects.toThrow('API Error: 401');
    });
  });

  describe('addFavorite', () => {
    it('should add a recipe to favorites', async () => {
      (api.post as jest.Mock).mockResolvedValue(mockFavorite);

      const result = await addFavorite({
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
        recipe_thumbnail: 'https://example.com/pasta.jpg',
      });

      expect(api.post).toHaveBeenCalledWith('/api/favorites', {
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
        recipe_thumbnail: 'https://example.com/pasta.jpg',
      });
      expect(result).toEqual(mockFavorite);
    });

    it('should handle favorite without thumbnail', async () => {
      const favoriteNoThumb = { ...mockFavorite, recipe_thumbnail: null };
      (api.post as jest.Mock).mockResolvedValue(favoriteNoThumb);

      const result = await addFavorite({
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
      });

      expect(result.recipe_thumbnail).toBeNull();
    });

    it('should throw on duplicate favorite', async () => {
      (api.post as jest.Mock).mockRejectedValue(new Error('API Error: 400'));

      await expect(
        addFavorite({
          recipe_id: '52771',
          recipe_name: 'Spicy Arrabiata Penne',
        })
      ).rejects.toThrow('API Error: 400');
    });
  });

  describe('removeFavorite', () => {
    it('should remove a recipe from favorites', async () => {
      (api.delete as jest.Mock).mockResolvedValue(undefined);

      await removeFavorite('52771');

      expect(api.delete).toHaveBeenCalledWith('/api/favorites/52771');
    });

    it('should succeed even if favorite does not exist (idempotent)', async () => {
      (api.delete as jest.Mock).mockResolvedValue(undefined);

      await expect(removeFavorite('nonexistent')).resolves.toBeUndefined();
    });

    it('should throw on API error', async () => {
      (api.delete as jest.Mock).mockRejectedValue(new Error('API Error: 500'));

      await expect(removeFavorite('52771')).rejects.toThrow('API Error: 500');
    });
  });

  describe('checkFavorite', () => {
    it('should return true when recipe is favorite', async () => {
      (api.get as jest.Mock).mockResolvedValue({ is_favorite: true });

      const result = await checkFavorite('52771');

      expect(api.get).toHaveBeenCalledWith('/api/favorites/52771');
      expect(result.is_favorite).toBe(true);
    });

    it('should return false when recipe is not favorite', async () => {
      (api.get as jest.Mock).mockResolvedValue({ is_favorite: false });

      const result = await checkFavorite('99999');

      expect(result.is_favorite).toBe(false);
    });

    it('should throw on API error', async () => {
      (api.get as jest.Mock).mockRejectedValue(new Error('API Error: 401'));

      await expect(checkFavorite('52771')).rejects.toThrow('API Error: 401');
    });
  });
});
