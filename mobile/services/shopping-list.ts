/**
 * Shopping List API Service
 *
 * Handles API calls for shopping list generation and management.
 *
 * Endpoints:
 * - POST /api/shopping-list/generate - Generate list from meal plan
 * - GET /api/shopping-list - Get current week's shopping list
 * - PUT /api/shopping-list/items/{id}/check - Toggle item check state
 * - PUT /api/shopping-list/uncheck-all - Uncheck all items
 * - DELETE /api/shopping-list - Clear shopping list
 */

import type {
  ShoppingListResponse,
  ShoppingListGenerateResponse,
  ShoppingListItem,
  UncheckAllResponse,
} from '../types/shopping-list';
import { api } from './api';

/**
 * Generate a shopping list from the current week's meal plan
 * @param weekStart - Optional ISO date string for the Monday of the week
 */
export async function generateList(
  weekStart?: string
): Promise<ShoppingListGenerateResponse> {
  const query = weekStart ? `?week_start=${weekStart}` : '';
  return api.post<ShoppingListGenerateResponse>(
    `/api/shopping-list/generate${query}`,
    {}
  );
}

/**
 * Get the shopping list for a specific week
 * @param weekStart - Optional ISO date string for the Monday of the week
 */
export async function getList(weekStart?: string): Promise<ShoppingListResponse> {
  const query = weekStart ? `?week_start=${weekStart}` : '';
  return api.get<ShoppingListResponse>(`/api/shopping-list${query}`);
}

/**
 * Toggle the checked state of a shopping list item
 * @param itemId - UUID of the item to toggle
 */
export async function toggleItem(itemId: string): Promise<ShoppingListItem> {
  return api.put<ShoppingListItem>(`/api/shopping-list/items/${itemId}/check`, {});
}

/**
 * Uncheck all items in the shopping list
 * @param weekStart - Optional ISO date string for the Monday of the week
 */
export async function uncheckAll(weekStart?: string): Promise<UncheckAllResponse> {
  const query = weekStart ? `?week_start=${weekStart}` : '';
  return api.put<UncheckAllResponse>(`/api/shopping-list/uncheck-all${query}`, {});
}

/**
 * Delete all items in the shopping list for a week
 * @param weekStart - Optional ISO date string for the Monday of the week
 */
export async function deleteList(weekStart?: string): Promise<void> {
  const query = weekStart ? `?week_start=${weekStart}` : '';
  await api.delete<void>(`/api/shopping-list${query}`);
}
