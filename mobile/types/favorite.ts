/**
 * Favorite Types
 *
 * TypeScript types for user favorites feature.
 */

export interface Favorite {
  id: string;
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail: string | null;
  created_at: string;
}

export interface FavoriteCreate {
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail?: string | null;
}

export interface FavoriteListResponse {
  favorites: Favorite[];
  count: number;
}

export interface FavoriteStatus {
  is_favorite: boolean;
}
