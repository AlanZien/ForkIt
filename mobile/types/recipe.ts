/**
 * Recipe Types
 *
 * TypeScript types for recipe data from TheMealDB API.
 */

export interface Ingredient {
  name: string;
  measure: string;
}

export interface RecipeSummary {
  id: string;
  name: string;
  thumbnail: string;
}

export interface Recipe {
  id: string;
  name: string;
  category: string | null;
  area: string | null;
  instructions: string | null;
  thumbnail: string | null;
  tags: string | null;
  youtube: string | null;
  source: string | null;
  ingredients: Ingredient[];
}

export interface Category {
  id: string;
  name: string;
  thumbnail: string;
  description: string;
}

export interface RecipeListResponse {
  recipes: RecipeSummary[];
}

export interface RecipeDetailResponse {
  recipe: Recipe | null;
}

export interface CategoryListResponse {
  categories: Category[];
}
