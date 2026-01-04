/**
 * Personal Recipes API Service
 *
 * Handles API calls for user's personal recipes (requires authentication).
 *
 * Endpoints:
 * - GET /api/personal-recipes - List all personal recipes
 * - POST /api/personal-recipes - Create a new recipe
 * - GET /api/personal-recipes/{id} - Get recipe details
 * - PUT /api/personal-recipes/{id} - Update a recipe
 * - DELETE /api/personal-recipes/{id} - Delete a recipe
 * - POST /api/personal-recipes/upload-image - Upload recipe image
 * - POST /api/personal-recipes/fork/{api_recipe_id} - Fork an API recipe
 */

import type {
  ImageUploadResponse,
  PersonalRecipeCreate,
  PersonalRecipeListResponse,
  PersonalRecipeResponse,
  PersonalRecipeUpdate,
} from '../types/personal-recipe';
import { api } from './api';

const BASE_PATH = '/api/personal-recipes';

/**
 * Get all personal recipes for current user
 */
export async function getPersonalRecipes(): Promise<PersonalRecipeListResponse> {
  return api.get<PersonalRecipeListResponse>(BASE_PATH);
}

/**
 * Get a single personal recipe by ID
 */
export async function getPersonalRecipe(
  recipeId: string
): Promise<PersonalRecipeResponse> {
  return api.get<PersonalRecipeResponse>(`${BASE_PATH}/${recipeId}`);
}

/**
 * Create a new personal recipe
 */
export async function createPersonalRecipe(
  data: PersonalRecipeCreate
): Promise<PersonalRecipeResponse> {
  return api.post<PersonalRecipeResponse>(BASE_PATH, data);
}

/**
 * Update an existing personal recipe
 */
export async function updatePersonalRecipe(
  recipeId: string,
  data: PersonalRecipeUpdate
): Promise<PersonalRecipeResponse> {
  return api.put<PersonalRecipeResponse>(`${BASE_PATH}/${recipeId}`, data);
}

/**
 * Delete a personal recipe
 */
export async function deletePersonalRecipe(recipeId: string): Promise<void> {
  await api.delete<void>(`${BASE_PATH}/${recipeId}`);
}

/**
 * Upload an image for a recipe
 *
 * @param uri - Local file URI from image picker
 * @param filename - Original filename
 * @param mimeType - MIME type (image/jpeg, image/png, image/webp)
 * @returns Upload response with public URL
 */
export async function uploadRecipeImage(
  uri: string,
  filename: string,
  mimeType: string
): Promise<ImageUploadResponse> {
  const formData = new FormData();

  // React Native requires this specific format for file uploads
  formData.append('file', {
    uri,
    name: filename,
    type: mimeType,
  } as unknown as Blob);

  return api.uploadFile<ImageUploadResponse>(
    `${BASE_PATH}/upload-image`,
    formData
  );
}

/**
 * Fork an API recipe as a personal recipe
 *
 * Creates a copy of a TheMealDB recipe in the user's personal recipes.
 *
 * @param apiRecipeId - The TheMealDB recipe ID to fork
 * @returns Created personal recipe with source_recipe_id set
 */
export async function forkRecipe(
  apiRecipeId: string
): Promise<PersonalRecipeResponse> {
  return api.post<PersonalRecipeResponse>(
    `${BASE_PATH}/fork/${apiRecipeId}`,
    {}
  );
}
