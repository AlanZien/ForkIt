/**
 * Meal Slots API Service
 *
 * Handles API calls for weekly meal planning (requires authentication).
 *
 * Endpoints:
 * - GET /api/meal-slots?week_start={date} - Get week's meal slots
 * - POST /api/meal-slots - Create/replace a meal slot
 * - PUT /api/meal-slots/{date}/{meal_type} - Update a meal slot
 * - DELETE /api/meal-slots/{date}/{meal_type} - Delete a meal slot
 * - GET /api/meal-slots/recent - Get recent recipes
 */

import type {
  MealSlot,
  MealSlotCreate,
  MealSlotUpdate,
  MealType,
  WeekSlotsResponse,
  RecentRecipesResponse,
} from '../types/meal-slot';
import { api } from './api';

/**
 * Get meal slots for a specific week
 * @param weekStart - ISO date string for the Monday of the week (YYYY-MM-DD)
 */
export async function getWeekSlots(weekStart: string): Promise<WeekSlotsResponse> {
  return api.get<WeekSlotsResponse>(`/api/meal-slots?week_start=${weekStart}`);
}

/**
 * Create or replace a meal slot
 * @param data - Meal slot creation data
 */
export async function createSlot(data: MealSlotCreate): Promise<MealSlot> {
  return api.post<MealSlot>('/api/meal-slots', data);
}

/**
 * Update an existing meal slot
 * @param date - ISO date string (YYYY-MM-DD)
 * @param mealType - 'dejeuner' or 'diner'
 * @param data - Update data (portions, recipe)
 */
export async function updateSlot(
  date: string,
  mealType: MealType,
  data: MealSlotUpdate
): Promise<MealSlot> {
  return api.put<MealSlot>(`/api/meal-slots/${date}/${mealType}`, data);
}

/**
 * Delete a meal slot
 * @param date - ISO date string (YYYY-MM-DD)
 * @param mealType - 'dejeuner' or 'diner'
 */
export async function deleteSlot(date: string, mealType: MealType): Promise<void> {
  await api.delete<void>(`/api/meal-slots/${date}/${mealType}`);
}

/**
 * Get recent recipes used in meal planning
 * Returns last 10 unique recipes ordered by last usage
 */
export async function getRecentRecipes(): Promise<RecentRecipesResponse> {
  return api.get<RecentRecipesResponse>('/api/meal-slots/recent');
}
