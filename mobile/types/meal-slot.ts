/**
 * Meal Slot Types
 *
 * TypeScript types for weekly meal planning feature.
 */

/**
 * Meal type - lunch or dinner
 */
export type MealType = 'dejeuner' | 'diner';

/**
 * Meal slot response from API
 */
export interface MealSlot {
  id: string;
  user_id: string;
  slot_date: string;
  meal_type: MealType;
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail: string | null;
  portions: number;
  created_at: string;
  updated_at: string;
}

/**
 * Data for creating a new meal slot
 */
export interface MealSlotCreate {
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail?: string | null;
  slot_date: string;
  meal_type: MealType;
  portions?: number;
}

/**
 * Data for updating an existing meal slot
 */
export interface MealSlotUpdate {
  recipe_id?: string;
  recipe_name?: string;
  recipe_thumbnail?: string | null;
  portions?: number;
}

/**
 * Response for fetching a week's meal slots
 */
export interface WeekSlotsResponse {
  slots: MealSlot[];
  week_start: string;
  week_end: string;
}

/**
 * Recent recipe used in meal planning
 */
export interface RecentRecipe {
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail: string | null;
  last_used: string;
}

/**
 * Response for fetching recent recipes
 */
export interface RecentRecipesResponse {
  recipes: RecentRecipe[];
}
