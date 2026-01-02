/**
 * Tests for favorites store
 *
 * Tests favorites state management with Zustand
 */

import { useFavoritesStore } from '../../stores/favorites';
import * as favoritesService from '../../services/favorites';

// Mock favorites service
jest.mock('../../services/favorites', () => ({
  getFavorites: jest.fn(),
  addFavorite: jest.fn(),
  removeFavorite: jest.fn(),
  checkFavorite: jest.fn(),
}));

// Mock data
const mockFavorite = {
  id: 'fav-123',
  recipe_id: '52771',
  recipe_name: 'Spicy Arrabiata Penne',
  recipe_thumbnail: 'https://example.com/pasta.jpg',
  created_at: '2026-01-02T10:00:00Z',
};

const mockFavorite2 = {
  id: 'fav-456',
  recipe_id: '52772',
  recipe_name: 'Teriyaki Chicken',
  recipe_thumbnail: 'https://example.com/chicken.jpg',
  created_at: '2026-01-02T11:00:00Z',
};

describe('useFavoritesStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useFavoritesStore.setState({
      favorites: [],
      favoriteIds: new Set(),
      isLoading: false,
      isUpdating: false,
      error: null,
    });
    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useFavoritesStore.getState();

      expect(state.favorites).toEqual([]);
      expect(state.favoriteIds.size).toBe(0);
      expect(state.isLoading).toBe(false);
      expect(state.isUpdating).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('fetchFavorites', () => {
    it('should set loading state during fetch', async () => {
      (favoritesService.getFavorites as jest.Mock).mockResolvedValue({
        favorites: [mockFavorite],
        count: 1,
      });

      const fetchPromise = useFavoritesStore.getState().fetchFavorites();

      expect(useFavoritesStore.getState().isLoading).toBe(true);

      await fetchPromise;

      expect(useFavoritesStore.getState().isLoading).toBe(false);
    });

    it('should update favorites on success', async () => {
      (favoritesService.getFavorites as jest.Mock).mockResolvedValue({
        favorites: [mockFavorite, mockFavorite2],
        count: 2,
      });

      await useFavoritesStore.getState().fetchFavorites();

      const state = useFavoritesStore.getState();
      expect(state.favorites).toEqual([mockFavorite, mockFavorite2]);
      expect(state.favoriteIds.has('52771')).toBe(true);
      expect(state.favoriteIds.has('52772')).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should handle empty favorites', async () => {
      (favoritesService.getFavorites as jest.Mock).mockResolvedValue({
        favorites: [],
        count: 0,
      });

      await useFavoritesStore.getState().fetchFavorites();

      const state = useFavoritesStore.getState();
      expect(state.favorites).toEqual([]);
      expect(state.favoriteIds.size).toBe(0);
    });

    it('should handle error', async () => {
      (favoritesService.getFavorites as jest.Mock).mockRejectedValue(
        new Error('Network error')
      );

      await useFavoritesStore.getState().fetchFavorites();

      const state = useFavoritesStore.getState();
      expect(state.favorites).toEqual([]);
      expect(state.error).toBe('Network error');
      expect(state.isLoading).toBe(false);
    });
  });

  describe('addFavorite', () => {
    it('should set updating state during add', async () => {
      (favoritesService.addFavorite as jest.Mock).mockResolvedValue(mockFavorite);

      const addPromise = useFavoritesStore.getState().addFavorite({
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
        recipe_thumbnail: 'https://example.com/pasta.jpg',
      });

      expect(useFavoritesStore.getState().isUpdating).toBe(true);

      await addPromise;

      expect(useFavoritesStore.getState().isUpdating).toBe(false);
    });

    it('should add favorite to state on success', async () => {
      (favoritesService.addFavorite as jest.Mock).mockResolvedValue(mockFavorite);

      await useFavoritesStore.getState().addFavorite({
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
        recipe_thumbnail: 'https://example.com/pasta.jpg',
      });

      const state = useFavoritesStore.getState();
      expect(state.favorites).toContainEqual(mockFavorite);
      expect(state.favoriteIds.has('52771')).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should prepend new favorite to list', async () => {
      useFavoritesStore.setState({
        favorites: [mockFavorite2],
        favoriteIds: new Set(['52772']),
      });

      (favoritesService.addFavorite as jest.Mock).mockResolvedValue(mockFavorite);

      await useFavoritesStore.getState().addFavorite({
        recipe_id: '52771',
        recipe_name: 'Spicy Arrabiata Penne',
      });

      const state = useFavoritesStore.getState();
      expect(state.favorites[0]).toEqual(mockFavorite);
      expect(state.favorites[1]).toEqual(mockFavorite2);
    });

    it('should handle error and throw', async () => {
      (favoritesService.addFavorite as jest.Mock).mockRejectedValue(
        new Error('Duplicate favorite')
      );

      await expect(
        useFavoritesStore.getState().addFavorite({
          recipe_id: '52771',
          recipe_name: 'Spicy Arrabiata Penne',
        })
      ).rejects.toThrow('Duplicate favorite');

      const state = useFavoritesStore.getState();
      expect(state.error).toBe('Duplicate favorite');
      expect(state.isUpdating).toBe(false);
    });
  });

  describe('removeFavorite', () => {
    beforeEach(() => {
      useFavoritesStore.setState({
        favorites: [mockFavorite, mockFavorite2],
        favoriteIds: new Set(['52771', '52772']),
      });
    });

    it('should set updating state during remove', async () => {
      (favoritesService.removeFavorite as jest.Mock).mockResolvedValue(undefined);

      const removePromise = useFavoritesStore.getState().removeFavorite('52771');

      expect(useFavoritesStore.getState().isUpdating).toBe(true);

      await removePromise;

      expect(useFavoritesStore.getState().isUpdating).toBe(false);
    });

    it('should remove favorite from state on success', async () => {
      (favoritesService.removeFavorite as jest.Mock).mockResolvedValue(undefined);

      await useFavoritesStore.getState().removeFavorite('52771');

      const state = useFavoritesStore.getState();
      expect(state.favorites).toHaveLength(1);
      expect(state.favorites[0].recipe_id).toBe('52772');
      expect(state.favoriteIds.has('52771')).toBe(false);
      expect(state.favoriteIds.has('52772')).toBe(true);
    });

    it('should handle error and throw', async () => {
      (favoritesService.removeFavorite as jest.Mock).mockRejectedValue(
        new Error('Server error')
      );

      await expect(
        useFavoritesStore.getState().removeFavorite('52771')
      ).rejects.toThrow('Server error');

      const state = useFavoritesStore.getState();
      expect(state.error).toBe('Server error');
      expect(state.isUpdating).toBe(false);
      // State should remain unchanged on error
      expect(state.favorites).toHaveLength(2);
    });
  });

  describe('isFavorite', () => {
    beforeEach(() => {
      useFavoritesStore.setState({
        favorites: [mockFavorite],
        favoriteIds: new Set(['52771']),
      });
    });

    it('should return true for favorite recipe', () => {
      const result = useFavoritesStore.getState().isFavorite('52771');

      expect(result).toBe(true);
    });

    it('should return false for non-favorite recipe', () => {
      const result = useFavoritesStore.getState().isFavorite('99999');

      expect(result).toBe(false);
    });
  });

  describe('reset', () => {
    it('should reset entire store to initial state', () => {
      useFavoritesStore.setState({
        favorites: [mockFavorite],
        favoriteIds: new Set(['52771']),
        isLoading: true,
        isUpdating: true,
        error: 'Some error',
      });

      useFavoritesStore.getState().reset();

      const state = useFavoritesStore.getState();
      expect(state.favorites).toEqual([]);
      expect(state.favoriteIds.size).toBe(0);
      expect(state.isLoading).toBe(false);
      expect(state.isUpdating).toBe(false);
      expect(state.error).toBeNull();
    });
  });
});
