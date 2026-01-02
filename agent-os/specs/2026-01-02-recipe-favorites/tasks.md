# Task Breakdown: Recipe Favorites

## Overview
Total Tasks: 12
Priority: P1
Status: **COMPLETED**

---

## Task List

### Database Layer

#### Task Group 1: Supabase Schema
**Dependencies:** None

- [x] 1.1 Create migration `supabase/migrations/20260102_create_user_favorites.sql`
  - Table user_favorites with columns: id, user_id, recipe_id, recipe_name, recipe_thumbnail, created_at
  - Unique constraint on (user_id, recipe_id)
  - Index on user_id
  - RLS policies for SELECT, INSERT, DELETE

**Acceptance Criteria:**
- Migration SQL ready for Supabase dashboard
- RLS prevents cross-user access

---

### Backend Layer

#### Task Group 2: Models & Service
**Dependencies:** Task Group 1

- [x] 2.1 Create `backend/app/models/favorite.py`
  - FavoriteCreate, FavoriteResponse, FavoriteListResponse, FavoriteStatus

- [x] 2.2 Create `backend/app/services/favorites_service.py`
  - get_favorites(user_id)
  - add_favorite(user_id, data)
  - remove_favorite(user_id, recipe_id)
  - is_favorite(user_id, recipe_id)

**Acceptance Criteria:**
- Models match spec
- Service handles all CRUD operations

---

#### Task Group 3: API Routes
**Dependencies:** Task Group 2

- [x] 3.1 Create `backend/app/routes/favorites.py`
  - GET /api/favorites
  - POST /api/favorites
  - DELETE /api/favorites/{recipe_id}
  - GET /api/favorites/{recipe_id}

- [x] 3.2 Register router in main.py

- [x] 3.3 Write tests `backend/tests/test_routes/test_favorites.py`
  - Test all endpoints
  - Test auth required
  - Test edge cases

**Acceptance Criteria:**
- All endpoints functional
- Tests pass with mocked Supabase (6/6 tests passing)

---

### Mobile Layer

#### Task Group 4: Types & Service
**Dependencies:** Task Group 3

- [x] 4.1 Create `mobile/types/favorite.ts`
  - Favorite, FavoriteListResponse interfaces

- [x] 4.2 Create `mobile/services/favorites.ts`
  - getFavorites, addFavorite, removeFavorite, checkFavorite

- [x] 4.3 Write tests `mobile/__tests__/services/favorites.test.ts`

**Acceptance Criteria:**
- Types match backend models
- Service handles API calls with auth (12/12 tests passing)

---

#### Task Group 5: Zustand Store
**Dependencies:** Task Group 4

- [x] 5.1 Create `mobile/stores/favorites.ts`
  - State: favorites, favoriteIds (Set), isLoading, isUpdating, error
  - Actions: fetchFavorites, addFavorite, removeFavorite, isFavorite (sync)

- [x] 5.2 Write tests `mobile/__tests__/stores/favorites.test.ts`

**Acceptance Criteria:**
- Store manages favorites state
- favoriteIds Set for O(1) lookup (15/15 tests passing)

---

#### Task Group 6: UI Components
**Dependencies:** Task Group 5

- [x] 6.1 Create `mobile/components/recipes/FavoriteButton.tsx`
  - Heart icon (outline/filled)
  - Toggle on press
  - Loading state
  - Size variants (small, medium, large)
  - Variant styles (default, overlay)

- [x] 6.2 Add FavoriteButton to recipe card (`app/(tabs)/recipes.tsx`)
  - Position: top-right corner over image
  - Show current state from store

- [x] 6.3 Add FavoriteButton to recipe detail (`app/recipe/[id].tsx`)
  - Position: top-right corner over hero image
  - Larger size than card version

- [x] 6.4 Add Favorites section to Recipes screen
  - Favorites toggle button in header with badge
  - Full favorites list view when toggled
  - Empty state if no favorites

**Acceptance Criteria:**
- Button works on both screens
- Visual feedback on toggle
- Favorites section visible when user has favorites

---

## Files Summary

### New Files
- `supabase/migrations/20260102_create_user_favorites.sql`
- `backend/app/models/favorite.py`
- `backend/app/services/favorites_service.py`
- `backend/app/routes/favorites.py`
- `backend/tests/test_routes/test_favorites.py`
- `mobile/types/favorite.ts`
- `mobile/services/favorites.ts`
- `mobile/stores/favorites.ts`
- `mobile/components/recipes/FavoriteButton.tsx`
- `mobile/__tests__/services/favorites.test.ts`
- `mobile/__tests__/stores/favorites.test.ts`

### Modified Files
- `backend/app/main.py` (add favorites router)
- `mobile/services/api.ts` (handle 204 No Content)
- `mobile/app/(tabs)/recipes.tsx` (add FavoriteButton + favorites toggle)
- `mobile/app/recipe/[id].tsx` (add FavoriteButton)

---

## Test Results

| Component | Tests | Status |
|-----------|-------|--------|
| Backend Routes | 6 | PASS |
| Mobile Service | 12 | PASS |
| Mobile Store | 15 | PASS |
| **Total** | **33** | **PASS** |

---

## Completion Notes

Feature completed on 2026-01-02. All tasks implemented:
- Database migration with RLS policies
- Full backend API with authentication
- Mobile service layer with API client
- Zustand store with optimistic UI updates
- FavoriteButton component with variants
- Integration in recipes list and detail screens
- Favorites toggle view with badge count
