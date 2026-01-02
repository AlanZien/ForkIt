# Task Breakdown: Recipe Browsing

## Overview
Total Tasks: 18
Priority: P1 (Core Feature)
Status: **COMPLETED**

## Task List

---

### Backend Layer

#### Task Group 1: TheMealDB Client & Models
**Dependencies:** None
**Estimated Effort:** 2 hours

- [x] 1.0 Complete TheMealDB integration
  - [x] 1.1 Create `backend/app/services/themealdb.py`
    - Implement async HTTP client with httpx
    - Methods: search_by_name, get_by_id, get_random, list_categories, filter_by_category
    - Base URL: https://www.themealdb.com/api/json/v1/1/
  - [x] 1.2 Create `backend/app/models/recipe.py`
    - Category, RecipeSummary, Recipe models
    - CategoryListResponse, RecipeListResponse, RecipeDetailResponse
    - Ingredient model with measure
    - from_api_response class method for Recipe

**Acceptance Criteria:**
- TheMealDB client handles all required endpoints
- Models properly map API response to Pydantic models

---

#### Task Group 2: Recipe API Routes
**Dependencies:** Task Group 1
**Estimated Effort:** 2 hours

- [x] 2.0 Complete Recipe API endpoints
  - [x] 2.1 Create `backend/app/routes/recipes.py`
    - GET /api/recipes/categories
    - GET /api/recipes/category/{category_name}
    - GET /api/recipes/search?q={query}
    - GET /api/recipes/{recipe_id}
    - GET /api/recipes/random
  - [x] 2.2 Register router in main.py
  - [x] 2.3 Write tests `backend/tests/test_routes/test_recipes.py`
    - Test each endpoint success case
    - Test search with query validation
    - Test 404 for invalid recipe ID

**Acceptance Criteria:**
- All endpoints return correct response models
- Tests pass with mocked TheMealDB client

---

### Mobile Layer

#### Task Group 3: Types & Service
**Dependencies:** Task Group 2
**Estimated Effort:** 1-2 hours

- [x] 3.0 Complete mobile types and service
  - [x] 3.1 Create `mobile/types/recipe.ts`
    - Category, RecipeSummary, Recipe interfaces
    - Ingredient interface
    - API response types
  - [x] 3.2 Create `mobile/services/recipes.ts`
    - getCategories, getRecipesByCategory, searchRecipes
    - getRecipeById, getRandomRecipe
    - Use PUBLIC_API_URL (no auth required)
  - [x] 3.3 Write tests `mobile/__tests__/services/recipes.test.ts`

**Acceptance Criteria:**
- TypeScript types match backend models
- Service handles API calls correctly

---

#### Task Group 4: Zustand Store
**Dependencies:** Task Group 3
**Estimated Effort:** 1-2 hours

- [x] 4.0 Complete recipes store
  - [x] 4.1 Create `mobile/stores/recipes.ts`
    - State: recipes, categories, selectedRecipe, searchQuery, selectedCategory
    - Loading states: isLoading, isCategoriesLoading, isDetailsLoading
    - Error state
  - [x] 4.2 Implement actions
    - fetchCategories, searchRecipes, fetchRecipesByCategory
    - fetchRecipeDetails, fetchRandomRecipe
    - clearSearch, clearSelectedRecipe, reset
  - [x] 4.3 Write tests `mobile/__tests__/stores/recipes.test.ts`

**Acceptance Criteria:**
- Store manages all recipe browsing state
- Actions handle loading and error states

---

#### Task Group 5: Recipes Screen UI
**Dependencies:** Task Group 4
**Estimated Effort:** 3-4 hours

- [x] 5.0 Complete Recipes screen
  - [x] 5.1 Create `mobile/app/(tabs)/recipes.tsx`
    - Header with title "Recettes"
    - Search bar with icon and clear button
    - Categories horizontal scroll with chips
    - Recipe grid (2 columns) with cards
  - [x] 5.2 Implement interactions
    - Category selection (toggle, auto-select first)
    - Search on submit (min 2 chars)
    - Recipe card press navigates to detail
  - [x] 5.3 Implement states
    - Loading indicator
    - Empty state with icon and message
    - Error message display

**Acceptance Criteria:**
- UI matches design tokens
- All interactions work correctly
- States handled properly

---

#### Task Group 6: Recipe Detail Screen
**Dependencies:** Task Group 5
**Estimated Effort:** 2-3 hours

- [x] 6.0 Complete Recipe detail screen
  - [x] 6.1 Create `mobile/app/recipe/[id].tsx`
    - Dynamic route with recipe ID
    - Full-width recipe image
    - Recipe name as title
    - Category and area badges
  - [x] 6.2 Display recipe content
    - Ingredients list with measures
    - Instructions text
    - YouTube link if available
  - [x] 6.3 Navigation
    - Back button
    - Loading state while fetching
    - Error handling

**Acceptance Criteria:**
- Detail screen displays all recipe info
- Navigation works from list and back

---

## Final Test Report

| Layer | Tests | Status |
|-------|-------|--------|
| Backend Routes | 8 | PASS |
| Mobile Service | 6 | PASS |
| Mobile Store | 10 | PASS |
| **Total** | **24** | **PASS** |

---

## Files Created

### Backend
- `backend/app/services/themealdb.py`
- `backend/app/models/recipe.py`
- `backend/app/routes/recipes.py`
- `backend/tests/test_routes/test_recipes.py`

### Mobile
- `mobile/types/recipe.ts`
- `mobile/services/recipes.ts`
- `mobile/stores/recipes.ts`
- `mobile/app/(tabs)/recipes.tsx`
- `mobile/app/recipe/[id].tsx`
- `mobile/__tests__/services/recipes.test.ts`
- `mobile/__tests__/stores/recipes.test.ts`

## Files Modified
- `backend/app/main.py` - Added recipes router
