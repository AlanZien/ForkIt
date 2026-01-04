# Test Plan: Personal Recipe Management

## Metadata
- **Feature**: Personal Recipe Management
- **Spec**: agent-os/specs/2026-01-03-personal-recipe-management/spec.md
- **Requirements**: agent-os/specs/2026-01-03-personal-recipe-management/planning/requirements.md
- **Created**: 2026-01-03
- **Status**: Planning Complete

## Test Summary

| Layer | Critical | High | Medium | Low | Total |
|-------|----------|------|--------|-----|-------|
| Database | 8 | 6 | 4 | 2 | 20 |
| API | 12 | 14 | 8 | 4 | 38 |
| UI | 6 | 12 | 10 | 4 | 32 |
| **Total** | **26** | **32** | **22** | **10** | **90** |

**Coverage Targets:**
- Critical paths: 100%
- High priority: 100%
- Medium priority: 80%
- Low priority: Deferred

---

## Database Layer

### personal_recipes Table (10 tests)

#### 1. test_personal_recipe_creation_with_all_fields
**Priority:** Critical
**Given:**
- Authenticated user with ID "user-123"
- Valid recipe data: title="Ma Recette", servings=4, prep_time=15, cook_time=30, tags=["rapide", "facile"], image_url=null
**When:** INSERT into personal_recipes table
**Then:**
- Record is created with auto-generated UUID id
- user_id is set to "user-123"
- created_at and updated_at are set to current timestamp
- All fields are persisted correctly
**Related Requirement:** spec.md "Database Schema for Personal Recipes"

#### 2. test_personal_recipe_creation_with_minimal_fields
**Priority:** Critical
**Given:**
- Authenticated user with ID "user-123"
- Minimal recipe data: title="Simple Recipe", servings=2
**When:** INSERT into personal_recipes table with nullable fields as NULL
**Then:**
- Record is created successfully
- prep_time_minutes, cook_time_minutes, tags, image_url, source_recipe_id are NULL
**Related Requirement:** spec.md "Database Schema for Personal Recipes"

#### 3. test_personal_recipe_user_id_foreign_key_constraint
**Priority:** Critical
**Given:**
- No authenticated user or invalid user_id "nonexistent-user"
**When:** INSERT into personal_recipes with invalid user_id
**Then:**
- Database returns foreign key constraint violation error
- No record is created
**Related Requirement:** spec.md "user_id FK to auth.users"

#### 4. test_personal_recipe_rls_select_own_recipes_only
**Priority:** Critical
**Given:**
- User A has 3 personal recipes
- User B has 2 personal recipes
- User A is authenticated
**When:** SELECT * FROM personal_recipes (with RLS)
**Then:**
- Only User A's 3 recipes are returned
- User B's recipes are not visible
**Related Requirement:** spec.md "RLS with policies for SELECT restricted to owner"

#### 5. test_personal_recipe_rls_update_own_recipe
**Priority:** Critical
**Given:**
- User A owns recipe with id "recipe-1"
- User A is authenticated
**When:** UPDATE personal_recipes SET title="New Title" WHERE id="recipe-1"
**Then:**
- Update succeeds
- title is changed to "New Title"
- updated_at is refreshed
**Related Requirement:** spec.md "RLS with policies for UPDATE restricted to owner"

#### 6. test_personal_recipe_rls_update_other_user_recipe_fails
**Priority:** Critical
**Given:**
- User A owns recipe with id "recipe-1"
- User B is authenticated
**When:** UPDATE personal_recipes SET title="Hacked" WHERE id="recipe-1"
**Then:**
- Update is silently ignored (0 rows affected) due to RLS
- Recipe title remains unchanged
**Related Requirement:** spec.md "RLS with policies for UPDATE restricted to owner"

#### 7. test_personal_recipe_rls_delete_own_recipe
**Priority:** Critical
**Given:**
- User A owns recipe with id "recipe-1"
- User A is authenticated
**When:** DELETE FROM personal_recipes WHERE id="recipe-1"
**Then:**
- Delete succeeds
- Recipe is removed from database
**Related Requirement:** spec.md "RLS with policies for DELETE restricted to owner"

#### 8. test_personal_recipe_rls_delete_other_user_recipe_fails
**Priority:** Critical
**Given:**
- User A owns recipe with id "recipe-1"
- User B is authenticated
**When:** DELETE FROM personal_recipes WHERE id="recipe-1"
**Then:**
- Delete is silently ignored (0 rows affected) due to RLS
- Recipe still exists in database
**Related Requirement:** spec.md "RLS with policies for DELETE restricted to owner"

#### 9. test_personal_recipe_updated_at_trigger
**Priority:** High
**Given:**
- Recipe exists with updated_at = "2026-01-01 10:00:00"
**When:** UPDATE personal_recipes SET title="Updated Title"
**Then:**
- updated_at is automatically set to current timestamp
- created_at remains unchanged
**Related Requirement:** spec.md "updated_at trigger function pattern"

#### 10. test_personal_recipe_source_recipe_id_nullable
**Priority:** Medium
**Given:**
- User creates recipe from scratch (not forked)
**When:** INSERT with source_recipe_id = NULL
**Then:**
- Record is created successfully
- source_recipe_id is NULL
**Related Requirement:** spec.md "source_recipe_id (nullable, for forked recipes)"

---

### personal_recipe_ingredients Table (5 tests)

#### 11. test_ingredient_creation_with_all_fields
**Priority:** High
**Given:**
- Personal recipe exists with id "recipe-1"
- Ingredient data: name="Farine", quantity=250, unit="g", note="type 55", sort_order=1
**When:** INSERT into personal_recipe_ingredients
**Then:**
- Ingredient is created with auto-generated UUID
- All fields are persisted correctly
**Related Requirement:** spec.md "personal_recipe_ingredients table"

#### 12. test_ingredient_recipe_id_foreign_key_constraint
**Priority:** High
**Given:**
- No recipe exists with id "nonexistent-recipe"
**When:** INSERT ingredient with recipe_id="nonexistent-recipe"
**Then:**
- Database returns foreign key constraint violation error
**Related Requirement:** spec.md "recipe_id (FK)"

#### 13. test_ingredients_cascade_delete_on_recipe_deletion
**Priority:** Critical
**Given:**
- Recipe "recipe-1" exists with 5 ingredients
- User is authenticated as owner
**When:** DELETE FROM personal_recipes WHERE id="recipe-1"
**Then:**
- Recipe is deleted
- All 5 associated ingredients are automatically deleted (CASCADE)
**Related Requirement:** spec.md "DELETE with cascade to ingredients/steps"

#### 14. test_ingredient_sort_order_uniqueness_per_recipe
**Priority:** Medium
**Given:**
- Recipe "recipe-1" with ingredient at sort_order=1
**When:** INSERT another ingredient with same sort_order=1 for same recipe
**Then:**
- INSERT succeeds (no unique constraint on sort_order)
- Application layer handles ordering
**Related Requirement:** spec.md "sort_order" field

#### 15. test_ingredient_note_nullable
**Priority:** Low
**Given:**
- Ingredient without a note
**When:** INSERT with note=NULL
**Then:**
- Ingredient is created successfully
**Related Requirement:** spec.md "note (nullable)"

---

### personal_recipe_steps Table (5 tests)

#### 16. test_step_creation_with_instruction
**Priority:** High
**Given:**
- Personal recipe exists with id "recipe-1"
- Step data: step_number=1, instruction="Prechauffer le four a 180C"
**When:** INSERT into personal_recipe_steps
**Then:**
- Step is created with auto-generated UUID
- step_number and instruction are persisted
**Related Requirement:** spec.md "personal_recipe_steps table"

#### 17. test_step_recipe_id_foreign_key_constraint
**Priority:** High
**Given:**
- No recipe exists with id "nonexistent-recipe"
**When:** INSERT step with recipe_id="nonexistent-recipe"
**Then:**
- Database returns foreign key constraint violation error
**Related Requirement:** spec.md "recipe_id (FK)"

#### 18. test_steps_cascade_delete_on_recipe_deletion
**Priority:** Critical
**Given:**
- Recipe "recipe-1" exists with 8 steps
- User is authenticated as owner
**When:** DELETE FROM personal_recipes WHERE id="recipe-1"
**Then:**
- Recipe is deleted
- All 8 associated steps are automatically deleted (CASCADE)
**Related Requirement:** spec.md "DELETE with cascade to ingredients/steps"

#### 19. test_step_number_ordering
**Priority:** Medium
**Given:**
- Recipe with steps 1, 2, 3
**When:** SELECT steps ORDER BY step_number
**Then:**
- Steps are returned in correct order
**Related Requirement:** spec.md "step_number"

#### 20. test_step_instruction_text_length
**Priority:** Low
**Given:**
- Step with very long instruction (2000+ characters)
**When:** INSERT into personal_recipe_steps
**Then:**
- Insert succeeds (TEXT type has no limit)
**Related Requirement:** spec.md "instruction"

---

## API Layer

### POST /api/personal-recipes (8 tests)

#### 21. test_create_recipe_success_returns_201
**Priority:** Critical
**Given:**
- Authenticated user with valid token
- Request body:
```json
{
  "title": "Tarte aux pommes",
  "servings": 6,
  "prep_time_minutes": 30,
  "cook_time_minutes": 45,
  "tags": ["dessert", "automne"],
  "ingredients": [
    {"name": "Pommes", "quantity": 4, "unit": "pieces", "note": "Golden"},
    {"name": "Pate feuilletee", "quantity": 1, "unit": "rouleau"}
  ],
  "steps": [
    {"step_number": 1, "instruction": "Eplucher les pommes"},
    {"step_number": 2, "instruction": "Derouler la pate"}
  ]
}
```
**When:** POST /api/personal-recipes with body
**Then:**
- Status: 201 Created
- Response body contains created recipe with id, user_id, created_at
- Recipe is persisted in database with ingredients and steps
**Related Requirement:** spec.md "POST /api/personal-recipes"

#### 22. test_create_recipe_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token provided
- Valid recipe data in body
**When:** POST /api/personal-recipes
**Then:**
- Status: 401 Unauthorized
- Body: {"detail": "Not authenticated"}
**Related Requirement:** spec.md "User-owned CRUD service"

#### 23. test_create_recipe_missing_title_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body missing required "title" field
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error for "title"
**Related Requirement:** spec.md "Validate required fields: title"

#### 24. test_create_recipe_missing_servings_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body with title but missing "servings" field
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error for "servings"
**Related Requirement:** spec.md "Validate required fields: servings (1-20)"

#### 25. test_create_recipe_servings_out_of_range_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body with servings=25 (above max of 20)
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error: "servings must be between 1 and 20"
**Related Requirement:** spec.md "servings (1-20)"

#### 26. test_create_recipe_servings_zero_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body with servings=0
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error: "servings must be at least 1"
**Related Requirement:** spec.md "servings (1-20)"

#### 27. test_create_recipe_empty_ingredients_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body with ingredients=[]
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error: "at least one ingredient required"
**Related Requirement:** spec.md "at least one ingredient"

#### 28. test_create_recipe_empty_steps_returns_422
**Priority:** High
**Given:**
- Authenticated user
- Request body with steps=[]
**When:** POST /api/personal-recipes
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error: "at least one instruction step required"
**Related Requirement:** spec.md "at least one instruction step"

---

### GET /api/personal-recipes (4 tests)

#### 29. test_list_recipes_returns_user_recipes_only
**Priority:** Critical
**Given:**
- Authenticated user has 5 personal recipes
- Other users have 10 recipes combined
**When:** GET /api/personal-recipes
**Then:**
- Status: 200 OK
- Response body contains exactly 5 recipes
- All recipes belong to authenticated user
**Related Requirement:** spec.md "GET /api/personal-recipes - List all user's personal recipes"

#### 30. test_list_recipes_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token provided
**When:** GET /api/personal-recipes
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "User-owned CRUD service"

#### 31. test_list_recipes_empty_list
**Priority:** Medium
**Given:**
- Authenticated user with no personal recipes
**When:** GET /api/personal-recipes
**Then:**
- Status: 200 OK
- Response body: [] (empty array)
**Related Requirement:** spec.md "GET /api/personal-recipes"

#### 32. test_list_recipes_ordered_by_created_at_desc
**Priority:** Medium
**Given:**
- Authenticated user with 3 recipes created at different times
**When:** GET /api/personal-recipes
**Then:**
- Status: 200 OK
- Recipes are ordered by created_at descending (newest first)
**Related Requirement:** spec.md "GET /api/personal-recipes"

---

### GET /api/personal-recipes/{id} (5 tests)

#### 33. test_get_recipe_with_ingredients_and_steps
**Priority:** Critical
**Given:**
- Authenticated user owns recipe "recipe-1" with 4 ingredients and 6 steps
**When:** GET /api/personal-recipes/recipe-1
**Then:**
- Status: 200 OK
- Response contains recipe details with nested ingredients array (4 items)
- Response contains nested steps array (6 items)
- Steps are ordered by step_number
- Ingredients are ordered by sort_order
**Related Requirement:** spec.md "GET /api/personal-recipes/{id} - Get single recipe with ingredients and steps"

#### 34. test_get_recipe_not_found_returns_404
**Priority:** High
**Given:**
- Authenticated user
- Recipe "nonexistent-id" does not exist
**When:** GET /api/personal-recipes/nonexistent-id
**Then:**
- Status: 404 Not Found
- Body: {"detail": "Recipe not found"}
**Related Requirement:** spec.md "GET /api/personal-recipes/{id}"

#### 35. test_get_other_user_recipe_returns_404
**Priority:** Critical
**Given:**
- User A owns recipe "recipe-1"
- User B is authenticated
**When:** GET /api/personal-recipes/recipe-1 (as User B)
**Then:**
- Status: 404 Not Found (recipe is invisible due to RLS)
**Related Requirement:** spec.md "RLS with policies for SELECT restricted to owner"

#### 36. test_get_recipe_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token
**When:** GET /api/personal-recipes/recipe-1
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "User-owned CRUD service"

#### 37. test_get_recipe_includes_source_recipe_id_for_forked
**Priority:** Medium
**Given:**
- Authenticated user owns forked recipe with source_recipe_id="themealdb-12345"
**When:** GET /api/personal-recipes/{forked-recipe-id}
**Then:**
- Status: 200 OK
- Response includes source_recipe_id: "themealdb-12345"
**Related Requirement:** spec.md "source_recipe_id (nullable, for forked recipes)"

---

### PUT /api/personal-recipes/{id} (8 tests)

#### 38. test_update_recipe_success
**Priority:** Critical
**Given:**
- Authenticated user owns recipe "recipe-1"
- Update body with new title="Updated Title", servings=8
**When:** PUT /api/personal-recipes/recipe-1
**Then:**
- Status: 200 OK
- Recipe title and servings are updated
- updated_at is refreshed
- Other fields remain unchanged
**Related Requirement:** spec.md "PUT /api/personal-recipes/{id}"

#### 39. test_update_recipe_replace_ingredients
**Priority:** High
**Given:**
- Authenticated user owns recipe with 3 ingredients
- Update body with 2 new ingredients
**When:** PUT /api/personal-recipes/{id}
**Then:**
- Status: 200 OK
- Old 3 ingredients are deleted
- New 2 ingredients are created
- Response shows 2 ingredients
**Related Requirement:** spec.md "PUT /api/personal-recipes/{id}"

#### 40. test_update_recipe_replace_steps
**Priority:** High
**Given:**
- Authenticated user owns recipe with 5 steps
- Update body with 7 new steps
**When:** PUT /api/personal-recipes/{id}
**Then:**
- Status: 200 OK
- Old 5 steps are deleted
- New 7 steps are created with correct step_number ordering
**Related Requirement:** spec.md "PUT /api/personal-recipes/{id}"

#### 41. test_update_other_user_recipe_returns_404
**Priority:** Critical
**Given:**
- User A owns recipe "recipe-1"
- User B is authenticated
**When:** PUT /api/personal-recipes/recipe-1 (as User B)
**Then:**
- Status: 404 Not Found
- Recipe remains unchanged
**Related Requirement:** spec.md "validate ownership via user_id"

#### 42. test_update_recipe_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token
**When:** PUT /api/personal-recipes/recipe-1
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "User-owned CRUD service"

#### 43. test_update_recipe_invalid_servings_returns_422
**Priority:** High
**Given:**
- Authenticated user owns recipe
- Update body with servings=-1
**When:** PUT /api/personal-recipes/{id}
**Then:**
- Status: 422 Unprocessable Entity
- Body contains validation error
**Related Requirement:** spec.md "servings (1-20)"

#### 44. test_update_recipe_not_found_returns_404
**Priority:** High
**Given:**
- Authenticated user
- Recipe "nonexistent-id" does not exist
**When:** PUT /api/personal-recipes/nonexistent-id
**Then:**
- Status: 404 Not Found
**Related Requirement:** spec.md "PUT /api/personal-recipes/{id}"

#### 45. test_update_recipe_partial_update
**Priority:** Medium
**Given:**
- Authenticated user owns recipe with all fields set
- Update body with only title change
**When:** PUT /api/personal-recipes/{id}
**Then:**
- Status: 200 OK
- Only title is updated
- prep_time, cook_time, tags remain unchanged
**Related Requirement:** spec.md "PUT /api/personal-recipes/{id}"

---

### DELETE /api/personal-recipes/{id} (6 tests)

#### 46. test_delete_recipe_success
**Priority:** Critical
**Given:**
- Authenticated user owns recipe "recipe-1" with ingredients and steps
**When:** DELETE /api/personal-recipes/recipe-1
**Then:**
- Status: 204 No Content
- Recipe is deleted from database
- All associated ingredients are deleted
- All associated steps are deleted
**Related Requirement:** spec.md "DELETE /api/personal-recipes/{id}"

#### 47. test_delete_other_user_recipe_returns_404
**Priority:** Critical
**Given:**
- User A owns recipe "recipe-1"
- User B is authenticated
**When:** DELETE /api/personal-recipes/recipe-1 (as User B)
**Then:**
- Status: 404 Not Found
- Recipe still exists in database
**Related Requirement:** spec.md "validate ownership via user_id"

#### 48. test_delete_recipe_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token
**When:** DELETE /api/personal-recipes/recipe-1
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "User-owned CRUD service"

#### 49. test_delete_recipe_not_found_returns_404
**Priority:** High
**Given:**
- Authenticated user
- Recipe "nonexistent-id" does not exist
**When:** DELETE /api/personal-recipes/nonexistent-id
**Then:**
- Status: 404 Not Found
**Related Requirement:** spec.md "DELETE /api/personal-recipes/{id}"

#### 50. test_delete_recipe_in_active_meal_plan_with_warning
**Priority:** High
**Given:**
- Authenticated user owns recipe "recipe-1"
- Recipe is referenced in a meal_slot for date 2026-01-10
**When:** DELETE /api/personal-recipes/recipe-1
**Then:**
- Status: 200 OK with warning
- Response: {"warning": "Recipe was in meal plan for 2026-01-10"}
- OR Status: 409 Conflict with option to force delete
**Related Requirement:** spec.md "warn if recipe is in active meal plans"

#### 51. test_delete_recipe_cascades_to_meal_slots
**Priority:** Medium
**Given:**
- Authenticated user owns recipe "recipe-1"
- Recipe is referenced in meal_slots
**When:** DELETE /api/personal-recipes/recipe-1 with force=true
**Then:**
- Recipe is deleted
- Meal slots referencing recipe have recipe_id set to NULL or are deleted
**Related Requirement:** spec.md "DELETE with cascade"

---

### POST /api/personal-recipes/fork/{api_recipe_id} (7 tests)

#### 52. test_fork_recipe_success
**Priority:** Critical
**Given:**
- Authenticated user
- TheMealDB recipe with id "52772" exists
**When:** POST /api/personal-recipes/fork/52772
**Then:**
- Status: 201 Created
- New personal recipe created with data from TheMealDB recipe
- source_recipe_id is set to "52772"
- user_id is set to authenticated user
**Related Requirement:** spec.md "POST /api/personal-recipes/fork/{api_recipe_id}"

#### 53. test_fork_recipe_parses_ingredients_structure
**Priority:** Critical
**Given:**
- TheMealDB recipe with ingredients like "250g flour", "2 eggs"
**When:** POST /api/personal-recipes/fork/{api_recipe_id}
**Then:**
- Ingredients are parsed into structured format:
  - {name: "flour", quantity: 250, unit: "g"}
  - {name: "eggs", quantity: 2, unit: "pieces"}
**Related Requirement:** spec.md "Parse TheMealDB ingredient format into structured"

#### 54. test_fork_recipe_ingredient_parsing_edge_cases
**Priority:** High
**Given:**
- TheMealDB recipe with complex ingredients:
  - "Salt to taste"
  - "1/2 cup sugar"
  - "Some parsley"
**When:** POST /api/personal-recipes/fork/{api_recipe_id}
**Then:**
- Ingredients are parsed best-effort:
  - {name: "Salt", quantity: null, unit: null, note: "to taste"}
  - {name: "sugar", quantity: 0.5, unit: "cup"}
  - {name: "parsley", quantity: null, unit: null, note: "Some"}
**Related Requirement:** spec.md "use best-effort parsing"

#### 55. test_fork_recipe_copies_image_url
**Priority:** High
**Given:**
- TheMealDB recipe with strMealThumb image URL
**When:** POST /api/personal-recipes/fork/{api_recipe_id}
**Then:**
- image_url is set to TheMealDB strMealThumb URL
**Related Requirement:** spec.md "Duplicate TheMealDB recipe as personal recipe"

#### 56. test_fork_recipe_api_recipe_not_found_returns_404
**Priority:** High
**Given:**
- TheMealDB recipe with id "99999" does not exist
**When:** POST /api/personal-recipes/fork/99999
**Then:**
- Status: 404 Not Found
- Body: {"detail": "API recipe not found"}
**Related Requirement:** spec.md "Fetch original recipe from TheMealDB API"

#### 57. test_fork_recipe_without_auth_returns_401
**Priority:** Critical
**Given:**
- No authentication token
**When:** POST /api/personal-recipes/fork/52772
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "User-owned CRUD service"

#### 58. test_fork_recipe_themealdb_api_error_returns_503
**Priority:** Medium
**Given:**
- Authenticated user
- TheMealDB API is unavailable
**When:** POST /api/personal-recipes/fork/52772
**Then:**
- Status: 503 Service Unavailable
- Body: {"detail": "External API unavailable"}
**Related Requirement:** spec.md "Fetch original recipe from TheMealDB API"

---

### Unified Search Integration (4 tests)

#### 59. test_search_returns_both_personal_and_api_recipes
**Priority:** Critical
**Given:**
- Authenticated user has personal recipe "Tarte maison"
- TheMealDB has recipe "Tarte Tatin"
- Search query: "tarte"
**When:** GET /api/recipes/search?q=tarte
**Then:**
- Status: 200 OK
- Results contain both recipes
- Personal recipe has source: "personal"
- API recipe has source: "api"
**Related Requirement:** spec.md "Unified Search Integration"

#### 60. test_search_personal_recipes_case_insensitive
**Priority:** High
**Given:**
- Authenticated user has personal recipe "POULET ROTI"
- Search query: "poulet roti" (lowercase)
**When:** GET /api/recipes/search?q=poulet%20roti
**Then:**
- Status: 200 OK
- Personal recipe "POULET ROTI" is included in results
**Related Requirement:** spec.md "case-insensitive ILIKE"

#### 61. test_search_personal_recipes_only_own
**Priority:** Critical
**Given:**
- User A has personal recipe "Secret Recipe"
- User B is authenticated and searches "secret"
**When:** GET /api/recipes/search?q=secret (as User B)
**Then:**
- User A's "Secret Recipe" is NOT in results
**Related Requirement:** spec.md "RLS with policies for SELECT restricted to owner"

#### 62. test_search_empty_query_returns_recent_recipes
**Priority:** Low
**Given:**
- Authenticated user with personal recipes
**When:** GET /api/recipes/search?q=
**Then:**
- Status: 200 OK
- Returns recent/popular recipes (behavior defined by implementation)
**Related Requirement:** spec.md "Unified Search Integration"

---

### Image Upload (4 tests)

#### 63. test_upload_recipe_image_success
**Priority:** High
**Given:**
- Authenticated user
- Valid JPEG image file (500KB)
**When:** POST /api/personal-recipes/{id}/image with multipart file upload
**Then:**
- Status: 200 OK
- Image is stored in Supabase Storage bucket "recipe-images"
- Recipe image_url is updated to Storage URL
- File path includes user_id for scoping
**Related Requirement:** spec.md "Supabase Storage bucket recipe-images"

#### 64. test_upload_recipe_image_exceeds_size_limit_returns_413
**Priority:** High
**Given:**
- Authenticated user
- Image file larger than 5MB
**When:** POST /api/personal-recipes/{id}/image
**Then:**
- Status: 413 Payload Too Large
- Body: {"detail": "Image size exceeds 5MB limit"}
**Related Requirement:** spec.md "Limit image size to 5MB"

#### 65. test_upload_recipe_image_invalid_format_returns_400
**Priority:** Medium
**Given:**
- Authenticated user
- Non-image file (e.g., .pdf, .txt)
**When:** POST /api/personal-recipes/{id}/image
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "Invalid image format. Allowed: JPEG, PNG, WebP"}
**Related Requirement:** spec.md "Image Upload and Storage"

#### 66. test_upload_recipe_image_other_user_recipe_returns_404
**Priority:** High
**Given:**
- User A owns recipe "recipe-1"
- User B is authenticated
**When:** POST /api/personal-recipes/recipe-1/image (as User B)
**Then:**
- Status: 404 Not Found
**Related Requirement:** spec.md "user-scoped access"

---

## UI Layer

### Recipe Creation Screen (12 tests)

#### 67. test_create_screen_renders_all_form_sections
**Priority:** Critical
**Given:**
- User navigates to /recipe/create
**When:** Screen renders
**Then:**
- "Basic Info" section visible with title, servings, prep time, cook time inputs
- "Ingredients" section visible with add button
- "Instructions" section visible with add button
- Image picker button visible
- Save button visible
**Related Requirement:** spec.md "Recipe Creation Screen"

#### 68. test_create_screen_title_input_validation
**Priority:** High
**Given:**
- User on recipe creation screen
**When:** User leaves title empty and taps Save
**Then:**
- Validation error displayed: "Le titre est requis"
- Form is not submitted
**Related Requirement:** spec.md "Validate required fields: title"

#### 69. test_create_screen_servings_numeric_stepper
**Priority:** High
**Given:**
- User on recipe creation screen
- Servings default value is 4
**When:** User taps "+" button twice
**Then:**
- Servings value displays "6"
**Related Requirement:** spec.md "servings (numeric stepper)"

#### 70. test_create_screen_servings_min_max_limits
**Priority:** High
**Given:**
- User on recipe creation screen
**When:** User tries to set servings below 1 or above 20
**Then:**
- Stepper is clamped to min=1, max=20
- Validation error shows if manually typed out of range
**Related Requirement:** spec.md "servings (1-20)"

#### 71. test_create_screen_add_ingredient_row
**Priority:** Critical
**Given:**
- User on recipe creation screen with 1 ingredient row
**When:** User taps "Ajouter un ingredient" button
**Then:**
- New ingredient row appears with empty fields
- Row has name, quantity, unit, note inputs
- Total ingredient count is 2
**Related Requirement:** spec.md "Ingredients section: dynamic list with add/remove"

#### 72. test_create_screen_remove_ingredient_row
**Priority:** High
**Given:**
- User on recipe creation screen with 3 ingredient rows
**When:** User taps remove button on second ingredient
**Then:**
- Second ingredient row is removed
- Total ingredient count is 2
**Related Requirement:** spec.md "dynamic list with add/remove"

#### 73. test_create_screen_ingredient_unit_dropdown
**Priority:** High
**Given:**
- User on recipe creation screen
**When:** User taps unit field for an ingredient
**Then:**
- Dropdown/picker shows unit options: g, kg, ml, L, c. a soupe, c. a cafe, pieces, etc.
**Related Requirement:** spec.md "unit (dropdown/picker)"

#### 74. test_create_screen_add_instruction_step
**Priority:** Critical
**Given:**
- User on recipe creation screen with 1 step
**When:** User taps "Ajouter une etape" button
**Then:**
- New step row appears with empty instruction field
- Step is auto-numbered as "2"
**Related Requirement:** spec.md "Instructions section: numbered steps with add/remove"

#### 75. test_create_screen_instruction_auto_numbering
**Priority:** High
**Given:**
- User on recipe creation screen with steps 1, 2, 3
**When:** User removes step 2
**Then:**
- Remaining steps are renumbered to 1, 2
**Related Requirement:** spec.md "auto-number displayed"

#### 76. test_create_screen_image_picker_options
**Priority:** High
**Given:**
- User on recipe creation screen
**When:** User taps image picker button
**Then:**
- Action sheet shows options: "Prendre une photo", "Choisir dans la galerie", "Annuler"
**Related Requirement:** spec.md "Image picker button with camera/gallery options"

#### 77. test_create_screen_image_preview_display
**Priority:** High
**Given:**
- User on recipe creation screen
- User has selected an image
**When:** Image is selected
**Then:**
- Image preview is displayed in form
- Replace/remove image button appears
**Related Requirement:** spec.md "show preview or placeholder"

#### 78. test_create_screen_submit_success_navigation
**Priority:** Critical
**Given:**
- User has filled all required fields (title, servings, 1+ ingredient, 1+ step)
**When:** User taps "Enregistrer" button
**Then:**
- Loading indicator shows
- On success: navigation to recipe detail or list
- Toast/snackbar: "Recette creee avec succes"
**Related Requirement:** spec.md "Recipe Creation Screen"

---

### Recipe Edit Screen (6 tests)

#### 79. test_edit_screen_pre_populates_form
**Priority:** Critical
**Given:**
- User navigates to /recipe/edit/recipe-1
- Recipe has title="Ma Tarte", servings=6, 3 ingredients, 5 steps
**When:** Screen renders
**Then:**
- Title input shows "Ma Tarte"
- Servings shows 6
- 3 ingredient rows pre-filled
- 5 step rows pre-filled
**Related Requirement:** spec.md "pre-populate with existing recipe data"

#### 80. test_edit_screen_update_success
**Priority:** Critical
**Given:**
- User on edit screen for recipe-1
- User changes title to "Ma Super Tarte"
**When:** User taps "Enregistrer les modifications"
**Then:**
- API PUT request is made
- On success: navigation back
- Toast: "Modifications enregistrees"
**Related Requirement:** spec.md "Recipe Edit Screen"

#### 81. test_edit_screen_validation_errors_display
**Priority:** High
**Given:**
- User on edit screen
- User clears title field
**When:** User taps save
**Then:**
- Validation error displayed under title field
- Form is not submitted
**Related Requirement:** spec.md "handle validation errors"

#### 82. test_edit_screen_delete_button
**Priority:** High
**Given:**
- User on edit screen for recipe-1
**When:** User taps "Supprimer la recette" button
**Then:**
- Confirmation dialog appears: "Voulez-vous vraiment supprimer cette recette?"
**Related Requirement:** spec.md "Delete personal recipes with confirmation"

#### 83. test_edit_screen_delete_confirmation
**Priority:** Critical
**Given:**
- User sees delete confirmation dialog
**When:** User taps "Supprimer"
**Then:**
- API DELETE request is made
- On success: navigation to recipe list
- Toast: "Recette supprimee"
**Related Requirement:** spec.md "Recipe Deletion"

#### 84. test_edit_screen_delete_cancel
**Priority:** Medium
**Given:**
- User sees delete confirmation dialog
**When:** User taps "Annuler"
**Then:**
- Dialog closes
- User remains on edit screen
- No API request made
**Related Requirement:** spec.md "Delete personal recipes with confirmation"

---

### Personal Recipe Badge Display (4 tests)

#### 85. test_recipe_card_shows_badge_for_personal_recipe
**Priority:** High
**Given:**
- Recipe list contains personal recipe with source="personal"
**When:** List renders
**Then:**
- Recipe card displays "Ma recette" badge
- Badge uses accent colors (#FEF3C7 bg, #92400E text)
- Badge positioned in top-left corner
**Related Requirement:** spec.md "Visual Badge for Personal Recipes"

#### 86. test_recipe_card_no_badge_for_api_recipe
**Priority:** High
**Given:**
- Recipe list contains API recipe with source="api"
**When:** List renders
**Then:**
- Recipe card does NOT display "Ma recette" badge
**Related Requirement:** spec.md "visually distinguish personal recipes"

#### 87. test_search_results_mixed_badges
**Priority:** Medium
**Given:**
- Search results contain 2 personal recipes and 3 API recipes
**When:** Results render
**Then:**
- Only 2 recipe cards have "Ma recette" badge
- 3 API recipe cards have no badge
**Related Requirement:** spec.md "Visual Badge for Personal Recipes"

#### 88. test_recipe_detail_shows_personal_indicator
**Priority:** Medium
**Given:**
- User views detail of personal recipe
**When:** Detail screen renders
**Then:**
- "Ma recette" indicator visible (badge or icon)
**Related Requirement:** spec.md "Visual Badge for Personal Recipes"

---

### Fork Action (6 tests)

#### 89. test_api_recipe_detail_shows_fork_button
**Priority:** High
**Given:**
- Authenticated user views API recipe detail
**When:** Detail screen renders
**Then:**
- "Dupliquer" button or fork icon is visible
**Related Requirement:** spec.md "Fork Action in Recipe Detail"

#### 90. test_fork_button_hidden_for_unauthenticated
**Priority:** Medium
**Given:**
- Unauthenticated user views API recipe detail
**When:** Detail screen renders
**Then:**
- Fork button is not visible
**Related Requirement:** spec.md "for authenticated users"

#### 91. test_fork_button_hidden_for_personal_recipe
**Priority:** Medium
**Given:**
- User views their own personal recipe detail
**When:** Detail screen renders
**Then:**
- Fork button is not visible (already personal)
**Related Requirement:** spec.md "Fork Action in Recipe Detail"

#### 92. test_fork_action_navigates_to_edit
**Priority:** Critical
**Given:**
- Authenticated user on API recipe detail
**When:** User taps "Dupliquer" button
**Then:**
- Loading indicator shows
- Fork API is called
- On success: navigation to edit screen with forked recipe
**Related Requirement:** spec.md "navigate to edit screen with forked recipe pre-populated"

#### 93. test_fork_action_shows_confirmation_toast
**Priority:** High
**Given:**
- User successfully forks a recipe
**When:** Fork completes
**Then:**
- Toast/snackbar shows: "Recette dupliquee dans vos recettes personnelles"
**Related Requirement:** spec.md "Show toast/snackbar confirmation"

#### 94. test_fork_action_error_handling
**Priority:** Medium
**Given:**
- User taps fork button
- API returns error (e.g., network failure)
**When:** Fork fails
**Then:**
- Error toast displayed: "Erreur lors de la duplication"
- User remains on recipe detail
**Related Requirement:** spec.md "Fork Action"

---

### Form Validation Display (4 tests)

#### 95. test_inline_validation_error_styling
**Priority:** Medium
**Given:**
- User submits form with validation errors
**When:** Errors are returned
**Then:**
- Error messages displayed in red below invalid fields
- Invalid input fields have red border
**Related Requirement:** spec.md "Show validation errors display"

#### 96. test_clear_validation_error_on_input_change
**Priority:** Medium
**Given:**
- Validation error displayed for title field
**When:** User starts typing in title field
**Then:**
- Error message clears
- Input border returns to normal
**Related Requirement:** spec.md "Validation errors display"

#### 97. test_multiple_validation_errors_display
**Priority:** Low
**Given:**
- User submits form with multiple errors (empty title, 0 servings, no ingredients)
**When:** Form validates
**Then:**
- All error messages are displayed simultaneously
**Related Requirement:** spec.md "Validation errors display"

#### 98. test_scroll_to_first_error
**Priority:** Low
**Given:**
- User submits form with error in field scrolled off-screen
**When:** Validation fails
**Then:**
- Screen scrolls to first field with error
**Related Requirement:** spec.md "Validation errors display"

---

## Integration Tests (Optional)

### End-to-End Flow: Create Recipe (2 tests)

#### 99. test_e2e_create_recipe_full_flow
**Priority:** Critical
**Given:**
- Authenticated user on home screen
**When:**
1. Navigate to "Mes Recettes"
2. Tap "Creer une recette"
3. Fill title: "Gateau au chocolat"
4. Set servings: 8
5. Add ingredient: "Chocolat", 200, "g"
6. Add ingredient: "Oeufs", 3, "pieces"
7. Add step: "Faire fondre le chocolat"
8. Add step: "Battre les oeufs"
9. Tap "Enregistrer"
**Then:**
- Success toast appears
- Recipe appears in "Mes Recettes" list with "Ma recette" badge
- Recipe can be viewed with correct details
**Related Requirement:** spec.md "Recipe Creation"

#### 100. test_e2e_fork_and_edit_recipe_flow
**Priority:** Critical
**Given:**
- Authenticated user viewing TheMealDB recipe
**When:**
1. Tap "Dupliquer"
2. Wait for fork completion
3. Edit title to add "(ma version)"
4. Remove 1 ingredient
5. Tap "Enregistrer les modifications"
**Then:**
- Modified recipe saved
- Recipe appears in "Mes Recettes" with updated title
- source_recipe_id preserved for traceability
**Related Requirement:** spec.md "Fork Recipe Feature"

---

## Test Dependencies

Document execution order requirements:
- Database layer tests must pass before API layer tests
- API layer tests must pass before UI layer tests
- Test 1-20 (Database) must pass before Test 21-66 (API)
- Test 21-28 (Create) should pass before Test 29-51 (List/Get/Update/Delete)
- Test 52-58 (Fork) requires TheMealDB API access or mocking
- Image upload tests (63-66) require Supabase Storage configured

---

## Test Data Requirements

### Test User Accounts
- User A: test-user-a@example.com (owns multiple recipes)
- User B: test-user-b@example.com (for RLS testing)
- Unauthenticated state testing

### Sample Personal Recipes
- Recipe with all fields populated
- Recipe with minimal fields (title + servings only)
- Recipe with many ingredients (10+) and steps (15+)
- Forked recipe with source_recipe_id set

### TheMealDB Mock Data
- Recipe ID 52772 (Beef Wellington) for fork tests
- Invalid ID 99999 for not found tests
- Recipe with complex ingredient formats for parsing tests

### Test Images
- Valid JPEG image (500KB) for upload success
- Large image (6MB) for size limit test
- Non-image file (PDF) for format validation test

---

## Out of Scope

Tests explicitly NOT included in this plan:
- Performance/load testing (recipe creation under high load)
- Accessibility audit (VoiceOver/TalkBack support)
- Browser compatibility (mobile-only app)
- Offline mode for personal recipes (out of scope per spec)
- URL import functionality (excluded from v1)
- Video instructions (excluded from v1)
- Nutritional calculation (excluded from v1)
- Public sharing/community features (excluded from v1)
- Comments, likes, social interactions (excluded from v1)
- Family sharing (planned for v1.1/v2)
