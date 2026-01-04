/**
 * User Preferences Types for Mobile
 *
 * Types matching backend models from backend/app/models/preferences.py
 */

/**
 * Dietary preference types.
 * 7 dietary types as specified in spec.md
 */
export type DietaryType =
  | 'vegetarian'
  | 'vegan'
  | 'no_pork'
  | 'no_beef'
  | 'pescetarian'
  | 'halal'
  | 'kosher';

/**
 * Allergy types.
 * 11 allergen types as specified in spec.md
 */
export type AllergyType =
  | 'gluten'
  | 'lactose'
  | 'tree_nuts'
  | 'peanuts'
  | 'eggs'
  | 'fish'
  | 'shellfish'
  | 'soy'
  | 'sesame'
  | 'mustard'
  | 'celery';

/**
 * User preferences response from API
 * Matches UserPreferencesResponse from backend
 */
export interface UserPreferences {
  dietary_preferences: DietaryType[];
  allergies: AllergyType[];
  excluded_ingredients: string[];
  preferred_ingredients: string[];
  portions_count: number;
  warning?: string | null;
}

/**
 * User preferences update request
 * Matches UserPreferencesUpdate from backend
 */
export interface UserPreferencesUpdate {
  dietary_preferences: DietaryType[];
  allergies: AllergyType[];
  excluded_ingredients: string[];
  preferred_ingredients: string[];
  portions_count: number;
}

/**
 * Default empty preferences for new users
 */
export const DEFAULT_PREFERENCES: UserPreferences = {
  dietary_preferences: [],
  allergies: [],
  excluded_ingredients: [],
  preferred_ingredients: [],
  portions_count: 2,
  warning: null,
};

/**
 * Labels for dietary types (French)
 */
export const DIETARY_LABELS: Record<DietaryType, string> = {
  vegetarian: 'Vegetarien',
  vegan: 'Vegetalien',
  no_pork: 'Sans porc',
  no_beef: 'Sans boeuf',
  pescetarian: 'Pescetarien',
  halal: 'Halal',
  kosher: 'Casher',
};

/**
 * Labels for allergy types (French)
 */
export const ALLERGY_LABELS: Record<AllergyType, string> = {
  gluten: 'Gluten',
  lactose: 'Lactose',
  tree_nuts: 'Fruits a coque',
  peanuts: 'Arachides',
  eggs: 'Oeufs',
  fish: 'Poisson',
  shellfish: 'Fruits de mer',
  soy: 'Soja',
  sesame: 'Sesame',
  mustard: 'Moutarde',
  celery: 'Celeri',
};

/**
 * Dietary types that are incompatible with vegan
 */
export const VEGAN_INCOMPATIBLE: DietaryType[] = ['pescetarian', 'no_beef', 'no_pork'];

/**
 * All available dietary types
 */
export const ALL_DIETARY_TYPES: DietaryType[] = [
  'vegetarian',
  'vegan',
  'no_pork',
  'no_beef',
  'pescetarian',
  'halal',
  'kosher',
];

/**
 * All available allergy types
 */
export const ALL_ALLERGY_TYPES: AllergyType[] = [
  'gluten',
  'lactose',
  'tree_nuts',
  'peanuts',
  'eggs',
  'fish',
  'shellfish',
  'soy',
  'sesame',
  'mustard',
  'celery',
];
