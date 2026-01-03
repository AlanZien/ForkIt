/**
 * Shopping List Store using Zustand
 *
 * Manages shopping list state with optimistic updates and rollback.
 *
 * State:
 * - items: Map of shopping list items keyed by id
 * - isLoading: Loading state for list fetch
 * - isGenerating: Loading state for list generation
 * - error: Error message from last failed operation
 * - lastGeneratedAt: Timestamp of last generation
 * - currentWeekStart: ISO date string of current week's Monday
 *
 * Actions:
 * - generateList: Generate list from meal plan
 * - fetchList: Load list from API
 * - toggleItem: Toggle item check state (optimistic)
 * - uncheckAll: Uncheck all items
 * - getItemsByCategory: Get items grouped by category
 * - reset: Clear store state
 */

import { create } from 'zustand';
import type {
  ShoppingListItem,
  CategoryGroup,
  IngredientCategory,
} from '../types/shopping-list';
import { CATEGORY_ORDER } from '../types/shopping-list';
import * as shoppingListService from '../services/shopping-list';
import { getWeekStart, formatDateISO } from '../utils/date';

interface ShoppingListState {
  // State
  items: Map<string, ShoppingListItem>;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
  lastGeneratedAt: string | null;
  currentWeekStart: string;

  // Actions
  generateList: (weekStart?: string) => Promise<void>;
  fetchList: (weekStart?: string) => Promise<void>;
  toggleItem: (id: string) => Promise<void>;
  uncheckAll: () => Promise<void>;
  getItemsByCategory: () => CategoryGroup[];
  reset: () => void;
}

const getInitialWeekStart = (): string => {
  return formatDateISO(getWeekStart(new Date()));
};

const initialState = {
  items: new Map<string, ShoppingListItem>(),
  isLoading: false,
  isGenerating: false,
  error: null,
  lastGeneratedAt: null,
  currentWeekStart: getInitialWeekStart(),
};

export const useShoppingListStore = create<ShoppingListState>((set, get) => ({
  ...initialState,

  /**
   * Generate a new shopping list from the meal plan
   * @param weekStart - Optional week start date (defaults to currentWeekStart)
   */
  generateList: async (weekStart?: string) => {
    const targetWeek = weekStart || get().currentWeekStart;
    set({ isGenerating: true, error: null, currentWeekStart: targetWeek });

    try {
      const response = await shoppingListService.generateList(targetWeek);
      const itemsMap = new Map<string, ShoppingListItem>();

      for (const item of response.items) {
        itemsMap.set(item.id, item);
      }

      set({
        items: itemsMap,
        isGenerating: false,
        lastGeneratedAt: response.generated_at,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isGenerating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Fetch the current shopping list from API
   * @param weekStart - Optional week start date (defaults to currentWeekStart)
   */
  fetchList: async (weekStart?: string) => {
    const targetWeek = weekStart || get().currentWeekStart;
    set({ isLoading: true, error: null, currentWeekStart: targetWeek });

    try {
      const response = await shoppingListService.getList(targetWeek);
      const itemsMap = new Map<string, ShoppingListItem>();

      for (const category of response.categories) {
        for (const item of category.items) {
          itemsMap.set(item.id, item);
        }
      }

      set({
        items: itemsMap,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        isLoading: false,
        error: message,
      });
    }
  },

  /**
   * Toggle an item's checked state (optimistic update)
   */
  toggleItem: async (id: string) => {
    const currentItem = get().items.get(id);
    if (!currentItem) {
      throw new Error('Item not found');
    }

    const previousItems = new Map(get().items);

    // Optimistic update
    const updatedItem: ShoppingListItem = {
      ...currentItem,
      is_checked: !currentItem.is_checked,
      updated_at: new Date().toISOString(),
    };

    set((state) => {
      const newItems = new Map(state.items);
      newItems.set(id, updatedItem);
      return { items: newItems, error: null };
    });

    try {
      const serverItem = await shoppingListService.toggleItem(id);
      set((state) => {
        const newItems = new Map(state.items);
        newItems.set(id, serverItem);
        return { items: newItems };
      });
    } catch (error) {
      // Rollback on error
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        items: previousItems,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Uncheck all items in the current week's list
   */
  uncheckAll: async () => {
    const { currentWeekStart } = get();
    const previousItems = new Map(get().items);

    // Optimistic update: uncheck all items locally
    set((state) => {
      const newItems = new Map<string, ShoppingListItem>();
      for (const [id, item] of state.items) {
        newItems.set(id, {
          ...item,
          is_checked: false,
          updated_at: new Date().toISOString(),
        });
      }
      return { items: newItems, error: null };
    });

    try {
      await shoppingListService.uncheckAll(currentWeekStart);
    } catch (error) {
      // Rollback on error
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        items: previousItems,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Get items grouped by category in display order
   */
  getItemsByCategory: () => {
    const { items } = get();
    const categoryMap = new Map<IngredientCategory, ShoppingListItem[]>();

    // Group items by category
    for (const item of items.values()) {
      const category = item.category;
      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(item);
    }

    // Build category groups in display order
    const groups: CategoryGroup[] = [];
    for (const category of CATEGORY_ORDER) {
      const categoryItems = categoryMap.get(category);
      if (categoryItems && categoryItems.length > 0) {
        // Sort items alphabetically within category
        categoryItems.sort((a, b) =>
          a.ingredient_name.toLowerCase().localeCompare(b.ingredient_name.toLowerCase())
        );
        groups.push({
          category,
          items: categoryItems,
          item_count: categoryItems.length,
        });
      }
    }

    return groups;
  },

  /**
   * Reset entire store to initial state
   */
  reset: () => {
    set({
      ...initialState,
      items: new Map<string, ShoppingListItem>(),
      currentWeekStart: getInitialWeekStart(),
    });
  },
}));
