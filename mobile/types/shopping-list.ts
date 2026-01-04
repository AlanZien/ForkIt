/**
 * Shopping List Types
 *
 * TypeScript types for the shopping list generation feature.
 */

/**
 * Ingredient category for grouping
 */
export type IngredientCategory =
  | 'legumes'
  | 'viandes'
  | 'poissons'
  | 'produits_laitiers'
  | 'epicerie'
  | 'boissons'
  | 'surgeles'
  | 'autres';

/**
 * Display names for categories (French)
 */
export const CATEGORY_LABELS: Record<IngredientCategory, string> = {
  legumes: 'Legumes',
  viandes: 'Viandes',
  poissons: 'Poissons',
  produits_laitiers: 'Produits laitiers',
  epicerie: 'Epicerie',
  boissons: 'Boissons',
  surgeles: 'Surgeles',
  autres: 'Autres',
};

/**
 * Order of categories for display
 */
export const CATEGORY_ORDER: IngredientCategory[] = [
  'legumes',
  'viandes',
  'poissons',
  'produits_laitiers',
  'epicerie',
  'boissons',
  'surgeles',
  'autres',
];

/**
 * Shopping list item from API
 */
export interface ShoppingListItem {
  id: string;
  user_id: string;
  ingredient_name: string;
  quantity: string;
  category: IngredientCategory;
  is_checked: boolean;
  week_start: string;
  created_at: string;
  updated_at: string;
}

/**
 * Category group with items
 */
export interface CategoryGroup {
  category: IngredientCategory;
  items: ShoppingListItem[];
  item_count: number;
}

/**
 * Response for GET /api/shopping-list
 */
export interface ShoppingListResponse {
  categories: CategoryGroup[];
  week_start: string;
  total_items: number;
  checked_count: number;
}

/**
 * Response for POST /api/shopping-list/generate
 */
export interface ShoppingListGenerateResponse {
  items: ShoppingListItem[];
  week_start: string;
  generated_at: string;
}

/**
 * Response for PUT /api/shopping-list/uncheck-all
 */
export interface UncheckAllResponse {
  count: number;
  message: string;
}
