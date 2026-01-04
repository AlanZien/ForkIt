/**
 * Personal Recipe Types
 *
 * TypeScript types for user's personal recipes.
 */

/** Ingredient for personal recipe creation/update */
export interface IngredientInput {
  name: string;
  quantity: number;
  unit: string;
  note?: string | null;
}

/** Ingredient response from API */
export interface IngredientResponse {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  note: string | null;
  sort_order: number;
}

/** Instruction step for creation/update */
export interface InstructionStepInput {
  instruction: string;
}

/** Instruction step response from API */
export interface InstructionStepResponse {
  id: string;
  step_number: number;
  instruction: string;
}

/** Data for creating a new personal recipe */
export interface PersonalRecipeCreate {
  title: string;
  image_url?: string | null;
  servings: number;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  tags?: string[] | null;
  ingredients: IngredientInput[];
  steps: InstructionStepInput[];
}

/** Data for updating a personal recipe (all fields optional) */
export interface PersonalRecipeUpdate {
  title?: string;
  image_url?: string | null;
  servings?: number;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  tags?: string[] | null;
  ingredients?: IngredientInput[];
  steps?: InstructionStepInput[];
}

/** Full personal recipe response */
export interface PersonalRecipeResponse {
  id: string;
  user_id: string;
  title: string;
  image_url: string | null;
  servings: number;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  tags: string[] | null;
  source_recipe_id: string | null;
  created_at: string;
  updated_at: string;
  ingredients: IngredientResponse[];
  steps: InstructionStepResponse[];
}

/** Summary for list views */
export interface PersonalRecipeSummary {
  id: string;
  title: string;
  image_url: string | null;
  source: 'personal';
}

/** List response from API */
export interface PersonalRecipeListResponse {
  recipes: PersonalRecipeSummary[];
  count: number;
}

/** Image upload response */
export interface ImageUploadResponse {
  url: string;
  filename: string;
}

/** Unified search result item */
export interface UnifiedRecipeSummary {
  id: string;
  name: string;
  thumbnail: string;
  source: 'personal' | 'api';
}

/** Unified search response */
export interface UnifiedSearchResponse {
  recipes: UnifiedRecipeSummary[];
  personal_count: number;
  api_count: number;
}

/** Common unit options for ingredient input */
export const UNIT_OPTIONS = [
  { label: 'g', value: 'g' },
  { label: 'kg', value: 'kg' },
  { label: 'ml', value: 'ml' },
  { label: 'L', value: 'L' },
  { label: 'c. a cafe', value: 'tsp' },
  { label: 'c. a soupe', value: 'tbsp' },
  { label: 'tasse', value: 'cup' },
  { label: 'piece', value: 'piece' },
  { label: 'pincee', value: 'pinch' },
  { label: 'au gout', value: 'to taste' },
] as const;
