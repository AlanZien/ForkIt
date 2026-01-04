# Task Breakdown: Personal Recipe Management

## Overview
Total Tasks: 42
Estimated Complexity: High (Multi-table database, Storage, Full CRUD API, Multi-screen Mobile UI)

## Task List

### Database Layer

#### Task Group 1: Database Schema and Migrations
**Dependencies:** None
**Estimated Duration:** 1-2 hours
**Reference Pattern:** `supabase/migrations/20260103_create_meal_slots.sql`
**Status:** COMPLETED

- [x] 1.0 Complete database schema for personal recipes
  - [x] 1.1 Write database layer tests
    - Test personal_recipes table CRUD operations
    - Test personal_recipe_ingredients relationships
    - Test personal_recipe_steps relationships
    - Test RLS policies (owner-only access)
    - Test cascade delete behavior
    - Expected: 6-8 tests covering schema and RLS
    - **Actual: 20 tests covering all schema aspects**
  - [x] 1.2 Create migration file `20260104_create_personal_recipes.sql`
    - Create `personal_recipes` table:
      - id (UUID, PK, default gen_random_uuid())
      - user_id (UUID, FK to auth.users, NOT NULL, ON DELETE CASCADE)
      - title (VARCHAR 255, NOT NULL)
      - image_url (VARCHAR 500, nullable)
      - servings (INTEGER, NOT NULL, CHECK 1-20)
      - prep_time_minutes (INTEGER, nullable)
      - cook_time_minutes (INTEGER, nullable)
      - tags (TEXT[], nullable)
      - source_recipe_id (VARCHAR 20, nullable - for forked recipes)
      - created_at (TIMESTAMPTZ, default NOW())
      - updated_at (TIMESTAMPTZ, default NOW())
  - [x] 1.3 Create `personal_recipe_ingredients` table in same migration
    - id (UUID, PK)
    - recipe_id (UUID, FK to personal_recipes, ON DELETE CASCADE)
    - name (VARCHAR 255, NOT NULL)
    - quantity (NUMERIC, NOT NULL)
    - unit (VARCHAR 50, NOT NULL)
    - note (VARCHAR 255, nullable)
    - sort_order (INTEGER, NOT NULL)
    - UNIQUE constraint on (recipe_id, sort_order)
  - [x] 1.4 Create `personal_recipe_steps` table in same migration
    - id (UUID, PK)
    - recipe_id (UUID, FK to personal_recipes, ON DELETE CASCADE)
    - step_number (INTEGER, NOT NULL)
    - instruction (TEXT, NOT NULL)
    - UNIQUE constraint on (recipe_id, step_number)
  - [x] 1.5 Add indexes for performance
    - idx_personal_recipes_user_id ON personal_recipes(user_id)
    - idx_personal_recipes_title ON personal_recipes(user_id, title)
    - idx_personal_recipe_ingredients_recipe ON personal_recipe_ingredients(recipe_id)
    - idx_personal_recipe_steps_recipe ON personal_recipe_steps(recipe_id)
  - [x] 1.6 Enable RLS and create policies
    - Enable RLS on all 3 tables
    - SELECT policy: auth.uid() = user_id (via join for child tables)
    - INSERT policy: auth.uid() = user_id
    - UPDATE policy: auth.uid() = user_id
    - DELETE policy: auth.uid() = user_id
  - [x] 1.7 Create updated_at trigger function
    - Reuse pattern from meal_slots migration
    - Apply trigger to personal_recipes table
  - [x] 1.8 Add table comments
    - Document purpose of each table and key columns
  - [x] 1.9 Verify database layer tests pass
    - Run migration against test database
    - Verify all RLS policies work correctly
    - Expected: 6-8 tests passing
    - **Actual: 20/20 tests passing**

**Acceptance Criteria:**
- Migration runs successfully without errors
- All 3 tables created with correct schema
- RLS policies restrict access to owner only
- Cascade delete works (deleting recipe removes ingredients/steps)
- Indexes created for query performance
- Tests validate CRUD and RLS behavior

**Implementation Notes:**
- Migration file: `supabase/migrations/20260104_create_personal_recipes.sql`
- Test file: `backend/tests/test_database/test_personal_recipes_schema.py`
- All 20 database tests pass (tests 1-20 from test-plan.md)

---

#### Task Group 2: Supabase Storage Bucket
**Dependencies:** None (can run in parallel with Task Group 1)
**Estimated Duration:** 30 minutes
**Status:** COMPLETED

- [x] 2.0 Complete storage bucket setup
  - [x] 2.1 Create `recipe-images` storage bucket
    - Create bucket via Supabase dashboard or migration
    - Set public: false (authenticated access only)
    - Max file size: 5MB
  - [x] 2.2 Configure storage RLS policies
    - SELECT: authenticated users can read their own images
    - INSERT: authenticated users can upload to their folder (user_id prefix)
    - UPDATE: authenticated users can update their own images
    - DELETE: authenticated users can delete their own images
  - [x] 2.3 Document storage URL pattern
    - Pattern: `recipe-images/{user_id}/{recipe_id}/{filename}`
    - Note in code comments for service implementation

**Acceptance Criteria:**
- Bucket exists and is accessible
- Only authenticated users can access images
- Users can only access their own images (RLS)
- File size limit enforced

**Implementation Notes:**
- Migration file: `supabase/migrations/20260104_create_recipe_images_bucket.sql`
- Bucket created with `public: false` for authenticated access only
- File size limit: 5MB (5242880 bytes)
- Allowed MIME types: image/jpeg, image/png, image/webp
- RLS policies use `storage.foldername(name)[1]` to extract user_id from path
- Full storage URL pattern documented in migration comments

---

### Backend Layer

#### Task Group 3: Pydantic Models
**Dependencies:** Task Group 1 (schema understanding)
**Estimated Duration:** 1 hour
**Reference Pattern:** `backend/app/models/favorite.py`
**Status:** COMPLETED

- [x] 3.0 Complete Pydantic models for personal recipes
  - [x] 3.1 Write model validation tests
    - Test PersonalRecipeCreate validation (required fields, ranges)
    - Test IngredientCreate validation
    - Test InstructionStepCreate validation
    - Test PersonalRecipeResponse serialization
    - Expected: 5-6 tests covering validation logic
    - **Actual: 46 tests covering all models and validation**
  - [x] 3.2 Create `backend/app/models/personal_recipe.py`
    - IngredientCreate model:
      - name: str (min_length=1, max_length=255)
      - quantity: float (gt=0)
      - unit: str (max_length=50)
      - note: str | None (max_length=255)
    - InstructionStepCreate model:
      - instruction: str (min_length=1)
  - [x] 3.3 Create PersonalRecipeCreate model
    - title: str (min_length=1, max_length=255)
    - image_url: str | None (max_length=500)
    - servings: int (ge=1, le=20)
    - prep_time_minutes: int | None (ge=0)
    - cook_time_minutes: int | None (ge=0)
    - tags: list[str] | None
    - ingredients: list[IngredientCreate] (min_length=1)
    - steps: list[InstructionStepCreate] (min_length=1)
  - [x] 3.4 Create PersonalRecipeUpdate model
    - All fields optional for partial updates
    - Use same validation rules as Create
  - [x] 3.5 Create response models
    - IngredientResponse (with id, sort_order)
    - InstructionStepResponse (with id, step_number)
    - PersonalRecipeResponse (full recipe with nested ingredients/steps)
    - PersonalRecipeListResponse (list + count, without nested details)
    - PersonalRecipeSummary (for search results: id, title, image_url, source)
  - [x] 3.6 Verify model tests pass
    - Expected: 5-6 tests passing
    - **Actual: 46/46 tests passing**
    - Validation errors raised for invalid data

**Acceptance Criteria:**
- All models have proper Field validators
- Required fields enforced
- Numeric ranges validated (servings 1-20, times >= 0)
- List minimum lengths enforced (1 ingredient, 1 step)
- Response models serialize datetime correctly

**Implementation Notes:**
- Model file: `backend/app/models/personal_recipe.py`
- Test file: `backend/tests/test_models/test_personal_recipe_models.py`
- All 46 model tests pass
- Models follow existing favorite.py pattern with Field validators
- PersonalRecipeSummary uses Literal["personal", "api"] for source field

---

#### Task Group 4: PersonalRecipesService
**Dependencies:** Task Group 1, Task Group 3
**Estimated Duration:** 2-3 hours
**Reference Pattern:** `backend/app/services/favorites_service.py`
**Status:** COMPLETED

- [x] 4.0 Complete PersonalRecipesService implementation
  - [x] 4.1 Write service layer tests
    - Test create_recipe with valid data
    - Test create_recipe validates ownership
    - Test get_recipes returns user's recipes only
    - Test get_recipe_by_id with valid/invalid ID
    - Test get_recipe_by_id ownership check
    - Test update_recipe with valid data
    - Test update_recipe ownership validation
    - Test delete_recipe success
    - Test delete_recipe ownership validation
    - Expected: 8-10 tests with mocked Supabase
    - **Actual: 14 tests covering all CRUD operations**
  - [x] 4.2 Create `backend/app/services/personal_recipes_service.py`
    - Class PersonalRecipesService
    - __init__: initialize Supabase client via get_supabase_admin()
    - Define table names as class attributes
  - [x] 4.3 Implement create_recipe method
    - Accept user_id and PersonalRecipeCreate
    - Insert into personal_recipes table
    - Insert ingredients with sort_order (enumerate)
    - Insert steps with step_number (enumerate starting at 1)
    - Return PersonalRecipeResponse with nested data
    - Use transaction pattern if available, else sequential inserts
  - [x] 4.4 Implement get_recipes method
    - Accept user_id
    - Query personal_recipes WHERE user_id matches
    - Order by created_at DESC
    - Return list of PersonalRecipeSummary (no nested data for list view)
  - [x] 4.5 Implement get_recipe_by_id method
    - Accept user_id and recipe_id
    - Query personal_recipes with ingredients and steps
    - Validate user_id matches (RLS backup)
    - Return PersonalRecipeResponse or None
    - Order ingredients by sort_order, steps by step_number
  - [x] 4.6 Implement update_recipe method
    - Accept user_id, recipe_id, PersonalRecipeUpdate
    - Verify ownership first
    - Update personal_recipes fields (only non-None)
    - If ingredients provided: delete existing, insert new
    - If steps provided: delete existing, insert new
    - Update updated_at timestamp
    - Return updated PersonalRecipeResponse
  - [x] 4.7 Implement delete_recipe method
    - Accept user_id and recipe_id
    - Verify ownership
    - Delete from personal_recipes (cascade handles children)
    - Return success boolean
  - [x] 4.8 Verify service tests pass
    - Expected: 8-10 tests passing
    - **Actual: 14/14 tests passing**
    - All CRUD operations work correctly

**Acceptance Criteria:**
- All CRUD operations implemented
- Ownership validation on all operations
- Nested ingredients/steps handled correctly
- Proper ordering maintained (sort_order, step_number)
- Transaction-like behavior for create/update
- Tests pass with mocked Supabase client

**Implementation Notes:**
- Service file: `backend/app/services/personal_recipes_service.py`
- Test file: `backend/tests/test_services/test_personal_recipes_service.py`
- All 14 service tests pass
- Service follows existing favorites_service.py pattern
- Uses get_supabase_admin() for client initialization
- Table names as class attributes: TABLE_RECIPES, TABLE_INGREDIENTS, TABLE_STEPS

---

#### Task Group 5: Fork Recipe Service
**Dependencies:** Task Group 4
**Estimated Duration:** 1-2 hours
**Status:** COMPLETED

- [x] 5.0 Complete fork recipe functionality
  - [x] 5.1 Write fork service tests
    - Test fork_recipe with valid TheMealDB ID
    - Test fork_recipe ingredient parsing
    - Test fork_recipe stores source_recipe_id
    - Test fork_recipe with invalid API recipe ID
    - Expected: 4-5 tests
    - **Actual: 22 tests covering fork, ingredient parsing, and instruction parsing**
  - [x] 5.2 Add fork_recipe method to PersonalRecipesService
    - Accept user_id and api_recipe_id (TheMealDB ID)
    - Fetch recipe from TheMealDB API (reuse existing themealdb_client)
    - Transform TheMealDB format to PersonalRecipeCreate
  - [x] 5.3 Implement ingredient parsing
    - Parse TheMealDB strIngredient1-20 and strMeasure1-20
    - Extract quantity (numeric) and unit from strMeasure
    - Handle formats: "200g", "2 cups", "1/2 tsp", "to taste"
    - Best-effort parsing: if unparseable, use quantity=1, unit="", note=full_text
  - [x] 5.4 Transform instructions
    - Split strInstructions by newlines or numbered patterns
    - Clean up each step (trim whitespace, remove empty)
    - Create InstructionStepCreate for each
  - [x] 5.5 Store forked recipe
    - Set source_recipe_id = original TheMealDB ID
    - Set image_url from strMealThumb
    - Call _create_recipe_with_source with transformed data
    - Return PersonalRecipeResponse
  - [x] 5.6 Verify fork tests pass
    - Expected: 4-5 tests passing
    - **Actual: 22/22 tests passing**
    - Ingredient parsing handles common formats

**Acceptance Criteria:**
- Fork creates personal copy of API recipe
- source_recipe_id tracks original
- Ingredients parsed into structured format
- Instructions split into numbered steps
- Works with various TheMealDB recipe formats

**Implementation Notes:**
- Service file: `backend/app/services/personal_recipes_service.py`
- Test file: `backend/tests/test_services/test_personal_recipes_fork.py`
- All 22 fork tests pass (tests 52-58 from test-plan.md plus additional parser tests)
- Added helper functions: `_parse_measure()`, `_parse_instructions()`, `_parse_fraction()`
- Added custom exceptions: `RecipeNotFoundError`, `ExternalAPIError`
- Uses existing `themealdb_client` from `app.services.themealdb`
- Ingredient parsing handles:
  - Simple formats: "2 cups", "3 cloves"
  - Fractions: "1/2 cup", "3/4 tsp"
  - Mixed fractions: "1 1/2 cups"
  - No-space formats: "200g", "500ml"
  - Unparseable formats: "to taste", "Some" (fallback to quantity=1, unit="", note=text)
- Instruction parsing handles:
  - Newline-separated steps
  - Numbered patterns: "1. Do this. 2. Do that."
  - Carriage returns normalization
  - Empty line removal and whitespace trimming

---

#### Task Group 6: API Routes
**Dependencies:** Task Group 4, Task Group 5
**Estimated Duration:** 2 hours
**Reference Pattern:** `backend/app/routes/favorites.py`
**Status:** COMPLETED

- [x] 6.0 Complete API routes for personal recipes
  - [x] 6.1 Write API integration tests
    - Test POST /api/personal-recipes (201 created)
    - Test POST /api/personal-recipes validation errors (422)
    - Test POST /api/personal-recipes unauthenticated (401)
    - Test GET /api/personal-recipes list (200)
    - Test GET /api/personal-recipes/{id} (200)
    - Test GET /api/personal-recipes/{id} not found (404)
    - Test GET /api/personal-recipes/{id} other user's recipe (404)
    - Test PUT /api/personal-recipes/{id} (200)
    - Test DELETE /api/personal-recipes/{id} (204)
    - Test POST /api/personal-recipes/fork/{api_recipe_id} (201)
    - Expected: 10-12 tests
    - **Actual: 28 tests covering all endpoints and edge cases**
  - [x] 6.2 Create `backend/app/routes/personal_recipes.py`
    - Router with prefix="/api/personal-recipes", tags=["personal-recipes"]
    - Dependency for service: get_personal_recipes_service()
    - Dependency for auth: get_current_user
  - [x] 6.3 Implement POST / (create recipe)
    - Accept PersonalRecipeCreate body
    - Return PersonalRecipeResponse, status 201
    - Handle validation errors (422)
  - [x] 6.4 Implement GET / (list recipes)
    - Return PersonalRecipeListResponse
    - Include count field
  - [x] 6.5 Implement GET /{recipe_id} (get single recipe)
    - Return PersonalRecipeResponse with nested data
    - Return 404 if not found or not owned
  - [x] 6.6 Implement PUT /{recipe_id} (update recipe)
    - Accept PersonalRecipeUpdate body
    - Return updated PersonalRecipeResponse
    - Return 404 if not found or not owned
  - [x] 6.7 Implement DELETE /{recipe_id} (delete recipe)
    - Return 204 No Content on success
    - Return 404 if not found or not owned
  - [x] 6.8 Implement POST /fork/{api_recipe_id}
    - Call fork_recipe service method
    - Return PersonalRecipeResponse, status 201
    - Return 404 if API recipe not found
    - Return 503 if TheMealDB API unavailable
  - [x] 6.9 Register router in main.py
    - Import and include router in app
  - [x] 6.10 Verify API tests pass
    - Expected: 10-12 tests passing
    - **Actual: 28/28 tests passing**
    - All endpoints return correct status codes

**Acceptance Criteria:**
- All CRUD endpoints functional
- Proper HTTP status codes (201, 200, 204, 404, 422, 401, 503)
- Authentication required on all endpoints
- Ownership enforced (404 for other users' recipes)
- Fork endpoint creates personal copy

**Implementation Notes:**
- Routes file: `backend/app/routes/personal_recipes.py`
- Test file: `backend/tests/test_routes/test_personal_recipes_routes.py`
- All 28 API route tests pass
- Router registered in main.py with other routers
- Follows favorites.py pattern for route structure
- Uses class name check for exception handling (robustness during testing)
- Endpoints:
  - POST /api/personal-recipes - Create recipe (201)
  - GET /api/personal-recipes - List recipes (200)
  - GET /api/personal-recipes/{id} - Get single recipe (200, 404)
  - PUT /api/personal-recipes/{id} - Update recipe (200, 404, 422)
  - DELETE /api/personal-recipes/{id} - Delete recipe (204, 404)
  - POST /api/personal-recipes/fork/{api_recipe_id} - Fork recipe (201, 404, 503)

---

#### Task Group 7: Unified Search Integration
**Dependencies:** Task Group 4
**Estimated Duration:** 1-2 hours
**Status:** COMPLETED

- [x] 7.0 Complete unified search integration
  - [x] 7.1 Write unified search tests
    - Test search returns personal recipes matching query
    - Test search returns API recipes matching query
    - Test search merges results with source field
    - Test search respects user ownership for personal
    - Expected: 4-5 tests
  - [x] 7.2 Add search_personal_recipes method to service
    - Accept user_id and search query
    - Use ILIKE for case-insensitive title search
    - Return PersonalRecipeSummary list with source="personal"
  - [x] 7.3 Modify existing search endpoint OR create unified endpoint
    - Option B: Create `/api/recipes/unified-search`
    - Merge TheMealDB results (source="api") with personal (source="personal")
    - Personal recipes first, then API results
  - [x] 7.4 Add source field to search response
    - Added UnifiedRecipeSummary model with source field
    - Added UnifiedSearchResponse model with personal_count and api_count
  - [x] 7.5 Verify unified search tests pass

**Acceptance Criteria:**
- Search finds personal recipes by title (case-insensitive)
- Search results include source field
- Personal and API recipes merged correctly
- Only user's own personal recipes included

**Implementation Notes:**
- Created `/api/recipes/unified-search` endpoint in recipes.py
- Added `search_recipes` method to PersonalRecipesService
- Created `UnifiedRecipeSummary` and `UnifiedSearchResponse` models
- Personal recipes returned first, then API recipes

---

#### Task Group 8: Image Upload Endpoint
**Dependencies:** Task Group 2
**Estimated Duration:** 1 hour
**Status:** COMPLETED

- [x] 8.0 Complete image upload functionality
  - [x] 8.1 Write image upload tests
    - Test POST /api/personal-recipes/upload-image success
    - Test POST /api/personal-recipes/upload-image file too large
    - Test POST /api/personal-recipes/upload-image invalid type
  - [x] 8.2 Create image upload endpoint
    - POST /api/personal-recipes/upload-image
    - Accept multipart/form-data with image file
    - Validate file type (jpg, png, webp)
    - Validate file size (max 5MB)
  - [x] 8.3 Implement storage upload
    - Generate unique filename: {uuid}.{extension}
    - Upload to: recipe-images/{user_id}/{filename}
    - Return public URL for image
  - [x] 8.4 Verify image upload tests pass

**Acceptance Criteria:**
- Images uploaded to correct storage path
- File type validation (images only)
- File size validation (5MB max)
- Returns usable URL for recipe creation

**Implementation Notes:**
- Added `upload_recipe_image` endpoint to personal_recipes.py
- Added `python-multipart` dependency for file upload support
- Created `ImageUploadResponse` model
- Validates content type and file size before upload

---

### Mobile Layer

#### Task Group 9: API Service Layer (Mobile)
**Dependencies:** Task Group 6 (API must be ready)
**Estimated Duration:** 1-2 hours

- [ ] 9.0 Complete mobile API service for personal recipes
  - [ ] 9.1 Create `mobile/services/personalRecipes.ts`
    - Import axios/fetch client from existing pattern
    - Define TypeScript interfaces matching backend models
  - [ ] 9.2 Implement CRUD API calls
    - getPersonalRecipes(): PersonalRecipeSummary[]
    - getPersonalRecipe(id): PersonalRecipeResponse
    - createPersonalRecipe(data): PersonalRecipeResponse
    - updatePersonalRecipe(id, data): PersonalRecipeResponse
    - deletePersonalRecipe(id): void
  - [ ] 9.3 Implement fork API call
    - forkRecipe(apiRecipeId): PersonalRecipeResponse
  - [ ] 9.4 Implement image upload
    - uploadRecipeImage(file): Promise<string> (returns URL)
    - Handle multipart/form-data
    - Integrate with expo-image-picker result
  - [ ] 9.5 Add error handling
    - Handle 401 (redirect to login)
    - Handle 404 (recipe not found)
    - Handle 422 (validation errors - show messages)
    - Handle network errors

**Acceptance Criteria:**
- All API calls work with backend
- TypeScript types match backend models
- Proper error handling and user feedback
- Image upload works with device files

---

#### Task Group 10: Recipe Form Components
**Dependencies:** Task Group 9
**Estimated Duration:** 3-4 hours
**Reference Pattern:** `mobile/components/ui/Input.tsx`, `mobile/components/ui/Button.tsx`

- [ ] 10.0 Complete recipe form components
  - [ ] 10.1 Write form component tests
    - Test IngredientInput renders correctly
    - Test IngredientInput add/remove functionality
    - Test InstructionStepInput add/remove/reorder
    - Test RecipeForm validation
    - Expected: 4-6 tests
  - [ ] 10.2 Create `mobile/components/recipe/IngredientInput.tsx`
    - Props: ingredients[], onChange, errors
    - Row layout: name (TextInput), quantity (numeric TextInput), unit (Picker/Dropdown), note (TextInput)
    - Add button to append new ingredient
    - Remove button (X) on each row
    - Validation: highlight empty required fields
  - [ ] 10.3 Create unit dropdown data
    - Common units: g, kg, ml, L, tsp, tbsp, cup, piece, pinch, to taste
    - Localized labels (French): g, kg, ml, L, c. a cafe, c. a soupe, tasse, piece, pincee, au gout
  - [ ] 10.4 Create `mobile/components/recipe/InstructionStepInput.tsx`
    - Props: steps[], onChange, errors
    - Each step: step number (auto), instruction (TextInput multiline)
    - Add button to append new step
    - Remove button on each step
    - Auto-renumber when step removed
  - [ ] 10.5 Create `mobile/components/recipe/ImagePicker.tsx`
    - Props: imageUrl, onChange
    - Show current image preview or placeholder
    - "Ajouter une photo" button
    - On press: show ActionSheet (Camera / Galerie / Annuler)
    - Use expo-image-picker for both options
    - Compress/resize image before setting
  - [ ] 10.6 Create `mobile/components/recipe/RecipeForm.tsx`
    - Composite form with sections:
      - Basic Info: title, servings (stepper), prep_time, cook_time
      - Image: ImagePicker component
      - Tags: multi-select chips (optional)
      - Ingredients: IngredientInput component
      - Instructions: InstructionStepInput component
    - Props: initialData?, onSubmit, isLoading, errors
    - Form state management (useState or react-hook-form)
    - Client-side validation before submit
  - [ ] 10.7 Create `mobile/components/recipe/ServingsStepper.tsx`
    - Props: value, onChange, min=1, max=20
    - Display: - [value] +
    - Disable - at min, + at max
  - [ ] 10.8 Create `mobile/components/recipe/TagsSelector.tsx`
    - Props: selected[], onChange
    - Predefined tags: Rapide, Vegetarien, Sans gluten, Dessert, etc.
    - Chip/pill style, toggle selection
  - [ ] 10.9 Verify form component tests pass
    - Expected: 4-6 tests passing

**Acceptance Criteria:**
- All form components render correctly
- Dynamic add/remove for ingredients and steps
- Image picker works with camera and gallery
- Form validates required fields
- Reusable for both create and edit screens

---

#### Task Group 11: Recipe Creation Screen
**Dependencies:** Task Group 10
**Estimated Duration:** 2-3 hours

- [ ] 11.0 Complete recipe creation screen
  - [ ] 11.1 Write creation screen tests
    - Test screen renders form
    - Test form submission calls API
    - Test validation errors displayed
    - Test navigation after success
    - Expected: 3-4 tests
  - [ ] 11.2 Create `mobile/app/recipe/create.tsx`
    - Screen title: "Nouvelle recette"
    - Render RecipeForm component
    - Handle form submission
  - [ ] 11.3 Implement form submission
    - Validate form data
    - If image selected: upload image first, get URL
    - Call createPersonalRecipe API
    - Show loading state during submission
  - [ ] 11.4 Handle success
    - Show success toast: "Recette creee avec succes"
    - Navigate to recipe detail OR back to list
  - [ ] 11.5 Handle errors
    - Display validation errors inline on form
    - Display API errors as alert/toast
    - Keep form data on error (don't clear)
  - [ ] 11.6 Add navigation entry point
    - Add "+" button or "Creer une recette" in appropriate location
    - Likely in recipe list screen or tab bar
  - [ ] 11.7 Verify creation screen tests pass
    - Expected: 3-4 tests passing

**Acceptance Criteria:**
- Form renders with all sections
- Image upload works before recipe creation
- Validation prevents invalid submissions
- Success navigates away with confirmation
- Errors displayed without losing form data

---

#### Task Group 12: Recipe Edit Screen
**Dependencies:** Task Group 10, Task Group 11
**Estimated Duration:** 1-2 hours

- [ ] 12.0 Complete recipe edit screen
  - [ ] 12.1 Write edit screen tests
    - Test screen loads existing recipe data
    - Test form pre-populated correctly
    - Test update submission
    - Expected: 2-3 tests
  - [ ] 12.2 Create `mobile/app/recipe/edit/[id].tsx`
    - Screen title: "Modifier la recette"
    - Fetch recipe by ID on mount
    - Show loading state while fetching
  - [ ] 12.3 Pre-populate form
    - Transform PersonalRecipeResponse to form state
    - Pass initialData to RecipeForm
  - [ ] 12.4 Implement update submission
    - Call updatePersonalRecipe API
    - Handle image change (upload new if changed)
    - Show loading state
  - [ ] 12.5 Handle success and errors
    - Success: toast + navigate back
    - Errors: display inline
  - [ ] 12.6 Add delete functionality
    - "Supprimer" button (danger variant)
    - Confirmation dialog before delete
    - Call deletePersonalRecipe API
    - Navigate to list on success
  - [ ] 12.7 Verify edit screen tests pass
    - Expected: 2-3 tests passing

**Acceptance Criteria:**
- Existing recipe data loads correctly
- Form pre-populated with all fields
- Update saves changes
- Delete with confirmation works
- Navigation flows are correct

---

#### Task Group 13: Personal Recipe Detail View
**Dependencies:** Task Group 9
**Estimated Duration:** 1-2 hours

- [ ] 13.0 Complete personal recipe detail view
  - [ ] 13.1 Identify existing recipe detail component/screen
    - Check if recipe/[id].tsx exists for API recipes
    - Plan reuse or extension for personal recipes
  - [ ] 13.2 Adapt detail view for personal recipes
    - If personal recipe (source="personal"): fetch from personal API
    - Display structured ingredients (quantity + unit + name)
    - Display numbered steps
    - Display prep/cook time, servings, tags
  - [ ] 13.3 Add edit button for owned recipes
    - "Modifier" button visible only for personal recipes
    - Navigate to edit screen on press
  - [ ] 13.4 Add "Ma recette" badge on detail view
    - Small badge near title or thumbnail
    - Same styling as list badge

**Acceptance Criteria:**
- Personal recipe detail displays all fields
- Edit button visible and functional
- Badge identifies personal recipe
- Consistent with API recipe detail styling

---

#### Task Group 14: Visual Badge Component
**Dependencies:** None (can run in parallel)
**Estimated Duration:** 30 minutes

- [ ] 14.0 Complete "Ma recette" badge component
  - [ ] 14.1 Create `mobile/components/recipe/PersonalBadge.tsx`
    - Small pill/badge component
    - Text: "Ma recette"
    - Colors: background #FEF3C7, text #92400E (from spec)
    - Size: small, non-intrusive
  - [ ] 14.2 Position badge on recipe cards
    - Absolute position: top-left corner of thumbnail
    - Small margin from edges
    - Semi-transparent or solid background

**Acceptance Criteria:**
- Badge renders with correct colors
- Badge positioned correctly on cards
- Visually distinguishes personal from API recipes

---

#### Task Group 15: Recipe Card Integration
**Dependencies:** Task Group 14
**Estimated Duration:** 1 hour

- [ ] 15.0 Integrate personal recipes into existing recipe lists
  - [ ] 15.1 Identify existing RecipeCard component
    - Check mobile/components for recipe card/list item
  - [ ] 15.2 Add source prop to RecipeCard
    - Props: source?: "personal" | "api"
    - Conditionally render PersonalBadge if source="personal"
  - [ ] 15.3 Update recipe list screens
    - Search results: display mixed results with badges
    - Favorites: if any personal recipes, show badge
    - Meal plan: show badge on personal recipe slots
  - [ ] 15.4 Handle recipe card tap
    - If personal: navigate to personal recipe detail
    - If API: navigate to API recipe detail
    - Use source field to determine routing

**Acceptance Criteria:**
- Personal recipes show badge in all list contexts
- Tap navigates to correct detail view
- Visual consistency across all recipe displays

---

#### Task Group 16: Fork Action Integration
**Dependencies:** Task Group 9
**Estimated Duration:** 1 hour

- [ ] 16.0 Complete fork action on API recipe detail
  - [ ] 16.1 Add fork button to API recipe detail screen
    - Button: "Dupliquer" or fork icon
    - Visible only for authenticated users
    - Position: action bar or header
  - [ ] 16.2 Implement fork action handler
    - On press: call forkRecipe(apiRecipeId) service
    - Show loading state
  - [ ] 16.3 Handle fork success
    - Show toast: "Recette dupliquee dans vos recettes personnelles"
    - Navigate to edit screen with forked recipe
    - Allow user to customize immediately
  - [ ] 16.4 Handle fork errors
    - Display error toast
    - Stay on current screen

**Acceptance Criteria:**
- Fork button visible on API recipe details
- Fork creates personal copy
- User navigated to edit forked recipe
- Success confirmation displayed

---

### Integration & Testing

#### Task Group 17: End-to-End Integration Testing
**Dependencies:** All previous task groups
**Estimated Duration:** 2-3 hours

- [ ] 17.0 Validate complete feature integration
  - [ ] 17.1 Test complete create flow
    - Create recipe with all fields
    - Verify in database
    - Verify in recipe list
    - Verify detail view
  - [ ] 17.2 Test complete edit flow
    - Edit existing recipe
    - Change image, ingredients, steps
    - Verify updates persisted
  - [ ] 17.3 Test complete delete flow
    - Delete recipe
    - Verify removed from database
    - Verify removed from lists
  - [ ] 17.4 Test fork flow
    - Fork API recipe
    - Verify personal copy created
    - Verify source_recipe_id set
    - Edit forked recipe
  - [ ] 17.5 Test unified search
    - Search term matching personal recipe
    - Verify personal recipe in results
    - Verify badge displayed
  - [ ] 17.6 Test meal plan integration
    - Add personal recipe to meal slot
    - Verify displays correctly
    - Verify shopping list includes ingredients

**Acceptance Criteria:**
- All user flows work end-to-end
- Data persists correctly
- UI updates reflect data changes
- No regressions in existing features

---

#### Task Group 18: Final Test Validation
**Dependencies:** Task Group 17
**Estimated Duration:** 1-2 hours

- [ ] 18.0 Complete test validation and cleanup
  - [ ] 18.1 Run complete backend test suite
    - pytest backend/tests/
    - Verify no regressions
    - Expected: All tests passing
  - [ ] 18.2 Run complete mobile test suite
    - npm test in mobile/
    - Verify no regressions
    - Expected: All tests passing
  - [ ] 18.3 Review test coverage
    - Check coverage report
    - Identify gaps in critical paths
    - Add missing tests if below 80%
  - [ ] 18.4 Manual QA checklist
    - [ ] Create recipe with all fields
    - [ ] Create recipe with minimal fields
    - [ ] Edit recipe, change each field
    - [ ] Delete recipe
    - [ ] Fork API recipe
    - [ ] Search finds personal recipes
    - [ ] Badge displays correctly
    - [ ] Meal plan integration works
    - [ ] Image upload works (camera + gallery)
  - [ ] 18.5 Documentation
    - Update API documentation if exists
    - Add comments to complex code
    - Ensure consistent code style (ruff, eslint)

**Acceptance Criteria:**
- 100% of tests pass
- Test coverage >= 80% on new code
- Manual QA checklist completed
- No lint errors
- Feature ready for deployment

---

## Execution Order

Recommended implementation sequence for optimal efficiency:

### Phase 1: Foundation (Parallel)
1. **Task Group 1**: Database Schema (required first) - COMPLETED
2. **Task Group 2**: Storage Bucket (can parallel with 1) - COMPLETED

### Phase 2: Backend Core (Sequential)
3. **Task Group 3**: Pydantic Models - COMPLETED
4. **Task Group 4**: PersonalRecipesService - COMPLETED
5. **Task Group 5**: Fork Service - COMPLETED
6. **Task Group 6**: API Routes - COMPLETED
7. **Task Group 7**: Unified Search
8. **Task Group 8**: Image Upload

### Phase 3: Mobile Foundation (After backend)
9. **Task Group 9**: Mobile API Service
10. **Task Group 14**: Badge Component (can parallel with 9)

### Phase 4: Mobile UI (Sequential)
11. **Task Group 10**: Form Components
12. **Task Group 11**: Create Screen
13. **Task Group 12**: Edit Screen
14. **Task Group 13**: Detail View
15. **Task Group 15**: Card Integration
16. **Task Group 16**: Fork Action

### Phase 5: Validation
17. **Task Group 17**: E2E Testing
18. **Task Group 18**: Final Validation

---

## Dependency Graph

```
[1: Database] ----+
                  |---> [3: Models] ---> [4: Service] ---> [5: Fork] ---> [6: Routes]
[2: Storage] ----+                                                            |
                                                                              v
                                                                    [7: Search] + [8: Image Upload]
                                                                              |
                                                                              v
                                                                    [9: Mobile API Service]
                                                                              |
[14: Badge] ---------------------------------------------------------------+  |
                                                                           |  |
                                                                           v  v
                                                              [10: Form Components]
                                                                       |
                                                                       v
                                                              [11: Create Screen]
                                                                       |
                                                                       v
                                                              [12: Edit Screen]
                                                                       |
                                                                       v
                                                    [13: Detail] + [15: Cards] + [16: Fork UI]
                                                                       |
                                                                       v
                                                              [17: E2E Testing]
                                                                       |
                                                                       v
                                                              [18: Final Validation]
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Complex ingredient parsing from TheMealDB | Best-effort parsing with fallback; accept imperfect parsing |
| Image upload performance on mobile | Compress/resize client-side before upload; limit to 5MB |
| Form complexity (dynamic lists) | Use proven patterns; consider react-hook-form for state |
| RLS policy errors | Test policies thoroughly in isolation before integration |
| Meal plan integration conflicts | Check for recipe usage before delete; warn user |

---

## Notes

- **test-plan.md exists**: Test counts follow test-plan.md specifications
- **Pattern references**: Follow existing FavoritesService, meal_slots migration, UI components
- **Localization**: UI text in French (Ma recette, Dupliquer, etc.)
- **Out of scope**: URL import, videos, nutritional calc, sharing, comments (per spec)
