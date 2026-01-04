/**
 * Meal Planning Store using Zustand
 *
 * Manages weekly meal planning state with optimistic updates and rollback.
 *
 * State:
 * - slots: Map of meal slots keyed by "{date}_{meal_type}"
 * - currentWeekStart: ISO date string of current week's Monday
 * - recentRecipes: Last 10 unique recipes used
 * - isLoading: Loading state for week fetch
 * - isUpdating: Loading state for slot operations
 * - error: Error message from last failed operation
 *
 * Actions:
 * - fetchWeek: Load week slots from API
 * - addSlot: Create/replace a meal slot (optimistic)
 * - updateSlot: Update slot portions/recipe (optimistic)
 * - removeSlot: Delete a slot (optimistic)
 * - fetchRecentRecipes: Load recent recipes
 * - navigateWeek: Change current week
 * - canNavigatePrev/Next: Check navigation boundaries
 * - getSlot: Get slot from map
 * - reset: Clear store
 */

import { create } from 'zustand';
import type {
  MealSlot,
  MealSlotCreate,
  MealSlotUpdate,
  MealType,
  RecentRecipe,
} from '../types/meal-slot';
import * as mealSlotsService from '../services/meal-slots';
import {
  getWeekStart,
  formatDateISO,
  addWeeks,
  isCurrentWeek,
  isWithinRange,
  generateSlotKey,
} from '../utils/date';

interface MealPlanningState {
  // State
  slots: Map<string, MealSlot>;
  currentWeekStart: string;
  recentRecipes: RecentRecipe[];
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;

  // Actions
  fetchWeek: (weekStart?: string) => Promise<void>;
  addSlot: (data: MealSlotCreate) => Promise<void>;
  updateSlot: (date: string, mealType: MealType, data: MealSlotUpdate) => Promise<void>;
  removeSlot: (date: string, mealType: MealType) => Promise<void>;
  fetchRecentRecipes: () => Promise<void>;
  navigateWeek: (direction: 'prev' | 'next') => void;
  canNavigatePrev: () => boolean;
  canNavigateNext: () => boolean;
  getSlot: (date: string, mealType: MealType) => MealSlot | undefined;
  reset: () => void;
}

const getInitialWeekStart = (): string => {
  return formatDateISO(getWeekStart(new Date()));
};

const initialState = {
  slots: new Map<string, MealSlot>(),
  currentWeekStart: getInitialWeekStart(),
  recentRecipes: [] as RecentRecipe[],
  isLoading: false,
  isUpdating: false,
  error: null,
};

export const useMealPlanningStore = create<MealPlanningState>((set, get) => ({
  ...initialState,

  /**
   * Fetch meal slots for a specific week
   * @param weekStart - Optional week start date (defaults to currentWeekStart)
   */
  fetchWeek: async (weekStart?: string) => {
    const targetWeek = weekStart || get().currentWeekStart;
    set({ isLoading: true, error: null, currentWeekStart: targetWeek });

    try {
      const response = await mealSlotsService.getWeekSlots(targetWeek);
      const slotsMap = new Map<string, MealSlot>();

      for (const slot of response.slots) {
        const key = generateSlotKey(slot.slot_date, slot.meal_type);
        slotsMap.set(key, slot);
      }

      set({
        slots: slotsMap,
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
   * Add or replace a meal slot (optimistic update)
   */
  addSlot: async (data: MealSlotCreate) => {
    const key = generateSlotKey(data.slot_date, data.meal_type);
    const previousSlots = new Map(get().slots);

    // Optimistic update: add temporary slot
    const tempSlot: MealSlot = {
      id: `temp_${Date.now()}`,
      user_id: '',
      slot_date: data.slot_date,
      meal_type: data.meal_type,
      recipe_id: data.recipe_id,
      recipe_name: data.recipe_name,
      recipe_thumbnail: data.recipe_thumbnail || null,
      portions: data.portions || 2,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    set((state) => {
      const newSlots = new Map(state.slots);
      newSlots.set(key, tempSlot);
      return { slots: newSlots, isUpdating: true, error: null };
    });

    try {
      const newSlot = await mealSlotsService.createSlot(data);
      set((state) => {
        const newSlots = new Map(state.slots);
        newSlots.set(key, newSlot);
        return { slots: newSlots, isUpdating: false };
      });
    } catch (error) {
      // Rollback on error
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        slots: previousSlots,
        isUpdating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Update an existing meal slot (optimistic update)
   */
  updateSlot: async (date: string, mealType: MealType, data: MealSlotUpdate) => {
    const key = generateSlotKey(date, mealType);
    const currentSlot = get().slots.get(key);

    if (!currentSlot) {
      throw new Error('Slot not found');
    }

    const previousSlots = new Map(get().slots);

    // Optimistic update
    const updatedSlot: MealSlot = {
      ...currentSlot,
      ...(data.recipe_id && { recipe_id: data.recipe_id }),
      ...(data.recipe_name && { recipe_name: data.recipe_name }),
      ...(data.recipe_thumbnail !== undefined && { recipe_thumbnail: data.recipe_thumbnail }),
      ...(data.portions !== undefined && { portions: data.portions }),
      updated_at: new Date().toISOString(),
    };

    set((state) => {
      const newSlots = new Map(state.slots);
      newSlots.set(key, updatedSlot);
      return { slots: newSlots, isUpdating: true, error: null };
    });

    try {
      const serverSlot = await mealSlotsService.updateSlot(date, mealType, data);
      set((state) => {
        const newSlots = new Map(state.slots);
        newSlots.set(key, serverSlot);
        return { slots: newSlots, isUpdating: false };
      });
    } catch (error) {
      // Rollback on error
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        slots: previousSlots,
        isUpdating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Remove a meal slot (optimistic update)
   */
  removeSlot: async (date: string, mealType: MealType) => {
    const key = generateSlotKey(date, mealType);
    const previousSlots = new Map(get().slots);

    // Optimistic delete
    set((state) => {
      const newSlots = new Map(state.slots);
      newSlots.delete(key);
      return { slots: newSlots, isUpdating: true, error: null };
    });

    try {
      await mealSlotsService.deleteSlot(date, mealType);
      set({ isUpdating: false });
    } catch (error) {
      // Rollback on error
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({
        slots: previousSlots,
        isUpdating: false,
        error: message,
      });
      throw error;
    }
  },

  /**
   * Fetch recent recipes used in meal planning
   */
  fetchRecentRecipes: async () => {
    try {
      const response = await mealSlotsService.getRecentRecipes();
      set({ recentRecipes: response.recipes });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({ error: message });
    }
  },

  /**
   * Navigate to previous or next week
   */
  navigateWeek: (direction: 'prev' | 'next') => {
    const { currentWeekStart, canNavigatePrev, canNavigateNext, fetchWeek } = get();

    if (direction === 'prev' && !canNavigatePrev()) {
      return;
    }
    if (direction === 'next' && !canNavigateNext()) {
      return;
    }

    const currentDate = new Date(currentWeekStart);
    const newWeekStart = addWeeks(currentDate, direction === 'next' ? 1 : -1);
    const newWeekStartStr = formatDateISO(newWeekStart);

    fetchWeek(newWeekStartStr);
  },

  /**
   * Check if can navigate to previous week
   * Cannot go before current week
   */
  canNavigatePrev: () => {
    return !isCurrentWeek(get().currentWeekStart);
  },

  /**
   * Check if can navigate to next week
   * Cannot go beyond 4 weeks from current week
   */
  canNavigateNext: () => {
    const { currentWeekStart } = get();
    const currentDate = new Date(currentWeekStart);
    const nextWeekStart = addWeeks(currentDate, 1);
    return isWithinRange(formatDateISO(nextWeekStart), 4);
  },

  /**
   * Get a specific slot from the map
   */
  getSlot: (date: string, mealType: MealType) => {
    const key = generateSlotKey(date, mealType);
    return get().slots.get(key);
  },

  /**
   * Reset entire store to initial state
   */
  reset: () => {
    set({
      ...initialState,
      slots: new Map<string, MealSlot>(),
      currentWeekStart: getInitialWeekStart(),
    });
  },
}));
