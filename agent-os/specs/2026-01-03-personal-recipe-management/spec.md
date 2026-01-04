# Specification: Personal Recipe Management

## Goal

Allow users to create, edit, and delete their own recipes. Personal recipes appear alongside API recipes in search, display a distinguishing badge, and can be added to meal plans.

## User Stories

- As a user, I want to create my own recipes with structured ingredients and step-by-step instructions so that I can plan meals with family recipes
- As a user, I want to fork (duplicate) an API recipe as a starting point so that I can adapt recipes to my family's tastes

## Specific Requirements

**Database Schema for Personal Recipes**
- Create `personal_recipes` table in Supabase with user ownership (user_id FK to auth.users)
- Fields: id (UUID), user_id, title, image_url (nullable), servings, prep_time_minutes (nullable), cook_time_minutes (nullable), tags (text array), source_recipe_id (nullable, for forked recipes), created_at, updated_at
- Create `personal_recipe_ingredients` table: id, recipe_id (FK), name, quantity (numeric), unit, note (nullable), sort_order
- Create `personal_recipe_steps` table: id, recipe_id (FK), step_number, instruction
- Enable RLS with policies for SELECT/INSERT/UPDATE/DELETE restricted to owner (auth.uid() = user_id)

**Image Upload and Storage**
- Create Supabase Storage bucket `recipe-images` for user-uploaded recipe photos
- Support image upload from device gallery or camera via expo-image-picker
- Store image URL in `image_url` field; display placeholder when null
- Limit image size to 5MB; compress/resize images client-side before upload

**Recipe Creation API**
- POST `/api/personal-recipes` - Create personal recipe with nested ingredients and steps in single request
- Validate required fields: title, servings (1-20), at least one ingredient, at least one instruction step
- Use Pydantic models following existing patterns (PersonalRecipeCreate, IngredientCreate, InstructionStepCreate)
- Service class pattern: PersonalRecipesService with CRUD methods

**Recipe Edit and Delete API**
- GET `/api/personal-recipes` - List all user's personal recipes
- GET `/api/personal-recipes/{id}` - Get single recipe with ingredients and steps
- PUT `/api/personal-recipes/{id}` - Update recipe (validate ownership via user_id)
- DELETE `/api/personal-recipes/{id}` - Delete recipe with cascade to ingredients/steps; warn if recipe is in active meal plans

**Fork Recipe Feature**
- POST `/api/personal-recipes/fork/{api_recipe_id}` - Duplicate TheMealDB recipe as personal recipe
- Fetch original recipe from TheMealDB API, transform to personal recipe structure
- Store `source_recipe_id` field for traceability
- Parse TheMealDB ingredient format into structured (name, quantity, unit) - use best-effort parsing

**Unified Search Integration**
- Modify `/api/recipes/search` or create unified endpoint that searches both TheMealDB and personal recipes
- Personal recipes searched by title (case-insensitive ILIKE)
- Return merged results with `source: "personal"` or `source: "api"` field for distinction

**Recipe Creation Screen (Mobile)**
- New screen `/recipe/create` with multi-section form: Basic Info, Ingredients, Instructions
- Basic Info: title (TextInput), servings (numeric stepper), prep time, cook time, tags (multi-select chips)
- Ingredients section: dynamic list with add/remove; each row has name (TextInput), quantity (numeric), unit (dropdown/picker), note (optional TextInput)
- Instructions section: numbered steps with add/remove/reorder; auto-number displayed
- Image picker button with camera/gallery options; show preview or placeholder

**Recipe Edit Screen (Mobile)**
- Reuse creation form component, pre-populate with existing recipe data
- Route: `/recipe/edit/[id]` for personal recipes
- Show "Enregistrer les modifications" button; handle validation errors

**Visual Badge for Personal Recipes**
- In recipe list/search results, display discreet badge "Ma recette" or user icon on personal recipe cards
- Use accent color (#FEF3C7 background, #92400E text) from design system for badge
- Badge position: top-left corner of recipe card thumbnail

**Fork Action in Recipe Detail**
- Add "Dupliquer" or fork icon button on API recipe detail screen (for authenticated users)
- On tap: call fork endpoint, navigate to edit screen with forked recipe pre-populated
- Show toast/snackbar confirmation: "Recette dupliquee dans vos recettes personnelles"

## Existing Code to Leverage

**FavoritesService Pattern (backend/app/services/favorites_service.py)**
- User-owned CRUD service with Supabase client initialization
- Pattern: service class with table name, get_supabase_admin(), typed response models
- Replicate for PersonalRecipesService with similar structure

**Favorites Models Pattern (backend/app/models/favorite.py)**
- Pydantic BaseModel with Field validators (min_length, max_length)
- Create/Response model separation pattern
- Apply to PersonalRecipeCreate, PersonalRecipeResponse, IngredientCreate, etc.

**Favorites Routes Pattern (backend/app/routes/favorites.py)**
- Router with prefix, tags, dependency injection for service and current user
- CRUD endpoints with proper HTTP status codes (201 for create, 204 for delete)
- Replicate for personal_recipes router

**Meal Slots Migration Pattern (supabase/migrations/20260103_create_meal_slots.sql)**
- Table with user_id FK, RLS enabled, index on user_id
- updated_at trigger function pattern
- Use as template for personal_recipes migration

**UI Components (mobile/components/ui/)**
- Input component with label, error state, hint - reuse for recipe form fields
- Button component with variants (primary, secondary, danger) - reuse for save/delete actions

## Out of Scope

- Recipe import from URL (web scraping complexity)
- Video instructions support
- Nutritional information calculation
- Public sharing or community features
- Comments, likes, or social interactions
- Receipt/invoice scanning
- Drive/cloud integrations for recipes
- Family sharing of personal recipes (planned for v1.1/v2)
- Offline creation/sync of personal recipes
- Ingredient auto-complete or suggestion from existing recipes
