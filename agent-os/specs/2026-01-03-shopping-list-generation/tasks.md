# Task Breakdown: Shopping List Generation

## Overview
Total Tasks: 32 tasks across 6 task groups
Estimated Effort: Medium (M)
Dependencies: Weekly Meal Planning (#5) - Complete

## Task List

### Backend - Database & Models

#### Task Group 1: Database Schema and Pydantic Models
**Dependencies:** None
**Pattern Reference:** `backend/app/models/meal_slot.py`

- [x] 1.0 Complete database layer for shopping list
  - [x] 1.1 Write database layer tests
    - Test ShoppingListItem model validation (required fields, constraints)
    - Test category enum values (8 categories + Autres)
    - Test week_start must be a Monday
    - Test is_checked defaults to False
    - Expected: 4 tests covering model validation
  - [x] 1.2 Create Pydantic models in `backend/app/models/shopping_list.py`
    - `IngredientCategory` enum: LEGUMES, VIANDES, POISSONS, PRODUITS_LAITIERS, EPICERIE, BOISSONS, SURGELES, AUTRES
    - `ShoppingListItemCreate`: ingredient_name, quantity, category, week_start
    - `ShoppingListItemResponse`: id, user_id, ingredient_name, quantity, category, is_checked, week_start, created_at, updated_at
    - `ShoppingListGenerateResponse`: items list, week_start, generated_at
    - `CategoryGroupResponse`: category, items list, item_count
  - [x] 1.3 Create Supabase migration for `shopping_list_items` table
    - Fields: id (uuid PK), user_id (uuid FK to auth.users), ingredient_name (text), quantity (text), category (text), is_checked (boolean default false), week_start (date), created_at (timestamptz), updated_at (timestamptz)
    - Unique constraint: (user_id, ingredient_name, week_start)
    - Indexes: user_id, week_start, (user_id, week_start)
    - Location: `supabase/migrations/YYYYMMDD_create_shopping_list_items.sql`
  - [x] 1.4 Add RLS policies for shopping_list_items table
    - SELECT: users can only read their own items (auth.uid() = user_id)
    - INSERT: users can only insert for themselves
    - UPDATE: users can only update their own items
    - DELETE: users can only delete their own items
  - [x] 1.5 Verify database layer tests pass
    - Run model validation tests
    - Verify migration applies successfully
    - Expected: 10/10 tests passing

**Acceptance Criteria:**
- All Pydantic models validate correctly
- Migration creates table with proper constraints
- RLS policies enforce user isolation
- Unique constraint prevents duplicate ingredients per week

---

### Backend - Services & Business Logic

#### Task Group 2: Ingredient Aggregation Service
**Dependencies:** Task Group 1
**Pattern Reference:** `backend/app/services/meal_slots_service.py`

- [x] 2.0 Complete ingredient aggregation logic
  - [x] 2.1 Write ingredient aggregation tests
    - Test case-insensitive exact matching ("Onion" == "onion")
    - Test quantity parsing: integers ("2"), decimals ("1.5"), fractions ("1/2"), units ("200g", "2 cups")
    - Test quantity summing for same ingredients (2 + 1 = 3)
    - Test concatenation when quantities cannot be summed ("2 cups, 100g")
    - Test portion multiplication (quantity * portions)
    - Test empty ingredient filtering (skip strIngredient with empty/null values)
    - Expected: 6 tests covering aggregation logic
  - [x] 2.2 Create `backend/app/services/shopping_list_service.py` with aggregation methods
    - `_normalize_ingredient_name(name: str) -> str`: lowercase, strip whitespace
    - `_parse_quantity(measure: str) -> tuple[float | None, str]`: extract numeric value and unit
    - `_can_sum_quantities(q1: tuple, q2: tuple) -> bool`: check if same unit type
    - `_sum_quantities(quantities: list[tuple]) -> str`: sum compatible quantities or concatenate
    - `_multiply_quantity(measure: str, portions: int) -> str`: scale by portions
  - [x] 2.3 Implement ingredient extraction from TheMealDB response
    - Parse strIngredient1-20 and strMeasure1-20
    - Filter out empty/None ingredients
    - Return list of (ingredient_name, measure) tuples
    - Handle malformed API responses gracefully
  - [x] 2.4 Verify aggregation tests pass
    - Run only aggregation-specific tests
    - Expected: 21/21 tests passing (expanded test coverage)

**Acceptance Criteria:**
- Case-insensitive matching works correctly
- Quantities parse and sum when compatible
- Non-compatible quantities concatenate gracefully
- Portions correctly multiply quantities

---

#### Task Group 3: Category Mapping and Shopping List Service
**Dependencies:** Task Group 2
**Pattern Reference:** `backend/app/services/meal_slots_service.py`, `backend/app/utils/ingredient_mappings.py`

- [x] 3.0 Complete category mapping and list generation
  - [x] 3.1 Write category mapping and service tests
    - Test ingredient-to-category mapping (tomate -> LEGUMES, poulet -> VIANDES)
    - Test unknown ingredients default to AUTRES
    - Test generate_list fetches current week slots
    - Test generate_list calls TheMealDB for each recipe
    - Test items sorted by category then alphabetically
    - Test delete_list removes all items for user's current week
    - Test uncheck_all resets all is_checked to false
    - Expected: 7 tests covering service operations
  - [x] 3.2 Create `INGREDIENT_CATEGORIES` static mapping dictionary
    - LEGUMES: tomate, oignon, carotte, poivron, courgette, aubergine, haricot, salade, concombre, pomme de terre, ail, champignon, epinard, brocoli, chou, etc.
    - VIANDES: poulet, boeuf, porc, agneau, veau, canard, dinde, lapin, saucisse, bacon, jambon, etc.
    - POISSONS: saumon, thon, cabillaud, crevette, moule, crabe, homard, sardine, maquereau, etc.
    - PRODUITS_LAITIERS: lait, beurre, creme, fromage, yaourt, oeuf, etc.
    - EPICERIE: riz, pates, farine, sucre, sel, poivre, huile, vinaigre, moutarde, sauce soja, etc.
    - BOISSONS: eau, vin, biere, jus, cafe, the, etc.
    - SURGELES: glace, petits pois surgeles, etc.
    - Handle English ingredient names from TheMealDB (chicken, beef, milk, etc.)
  - [x] 3.3 Implement `_get_category(ingredient_name: str) -> IngredientCategory`
    - Normalize ingredient name (lowercase, strip)
    - Check against INGREDIENT_CATEGORIES mapping
    - Use substring matching for compound ingredients ("chicken breast" -> VIANDES)
    - Return AUTRES for unmapped ingredients
  - [x] 3.4 Implement `generate_list(user_id: str, week_start: date) -> list[ShoppingListItemResponse]`
    - Use `MealSlotsService.get_week_slots()` to fetch current week
    - For each slot, call `themealdb_client.get_by_id(recipe_id)`
    - Extract and aggregate ingredients with portion multiplication
    - Map ingredients to categories
    - Clear existing items for week (DELETE)
    - Insert new items to Supabase
    - Return items sorted by category, then alphabetically
  - [x] 3.5 Implement `get_list(user_id: str, week_start: date) -> list[ShoppingListItemResponse]`
    - Query shopping_list_items for user_id and week_start
    - Return sorted by category, then alphabetically
  - [x] 3.6 Implement `toggle_item(user_id: str, item_id: str) -> ShoppingListItemResponse`
    - Fetch item, verify ownership
    - Toggle is_checked value
    - Update in Supabase
    - Return updated item
  - [x] 3.7 Implement `uncheck_all(user_id: str, week_start: date) -> int`
    - Update all items for user/week to is_checked = false
    - Return count of updated items
  - [x] 3.8 Implement `delete_list(user_id: str, week_start: date) -> int`
    - Delete all items for user/week
    - Return count of deleted items
  - [x] 3.9 Verify service tests pass
    - Run service layer tests
    - Expected: 34/34 tests passing (combined model+service tests)

**Acceptance Criteria:**
- All ingredients mapped to correct categories
- Unknown ingredients go to AUTRES
- List generates correctly from meal slots
- CRUD operations work with proper user isolation
- Items sorted by category then alphabetically

---

### Backend - API Routes

#### Task Group 4: Shopping List API Endpoints
**Dependencies:** Task Group 3
**Pattern Reference:** `backend/app/routes/meal_slots.py`

- [x] 4.0 Complete API routes layer
  - [x] 4.1 Write API endpoint tests
    - Test POST /api/shopping-list/generate returns 201 with generated items
    - Test POST /api/shopping-list/generate requires authentication (401)
    - Test GET /api/shopping-list returns current week items
    - Test PUT /api/shopping-list/items/{id}/check toggles item (200)
    - Test PUT /api/shopping-list/items/{id}/check with invalid id (404)
    - Test PUT /api/shopping-list/uncheck-all unchecks all items (200)
    - Test DELETE /api/shopping-list clears list (204)
    - Test endpoints filter by authenticated user only
    - Expected: 7 tests covering all endpoints
  - [x] 4.2 Create `backend/app/routes/shopping_list.py` with router
    - Router prefix: `/api/shopping-list`
    - Tags: `["shopping-list"]`
    - Dependency: `get_current_user` for all endpoints
  - [x] 4.3 Implement `POST /api/shopping-list/generate`
    - Authenticate user
    - Calculate current week_start (Monday)
    - Call `ShoppingListService.generate_list()`
    - Return 201 with `ShoppingListGenerateResponse`
  - [x] 4.4 Implement `GET /api/shopping-list`
    - Query param: `week_start` (optional, defaults to current week)
    - Return items grouped by category using `CategoryGroupResponse`
  - [x] 4.5 Implement `PUT /api/shopping-list/items/{item_id}/check`
    - Path param: `item_id` (uuid)
    - Toggle is_checked state
    - Return updated `ShoppingListItemResponse`
    - Return 404 if item not found or not owned by user
  - [x] 4.6 Implement `PUT /api/shopping-list/uncheck-all`
    - Query param: `week_start` (optional, defaults to current week)
    - Return count of unchecked items
  - [x] 4.7 Implement `DELETE /api/shopping-list`
    - Query param: `week_start` (optional, defaults to current week)
    - Return 204 No Content
  - [x] 4.8 Register router in `backend/app/main.py`
    - Import shopping_list router
    - Add to app with `app.include_router()`
  - [x] 4.9 Verify API tests pass
    - Run API endpoint tests
    - Expected: 7/7 tests passing

**Acceptance Criteria:**
- All endpoints return correct status codes
- Authentication enforced on all endpoints
- User isolation working correctly
- Response formats match Pydantic models

---

### Mobile - Store & Services

#### Task Group 5: Zustand Store and API Service
**Dependencies:** Task Group 4
**Pattern Reference:** `mobile/stores/meal-planning.ts`, `mobile/services/meal-slots.ts`

- [x] 5.0 Complete mobile state management layer
  - [x] 5.1 Write store and service tests
    - Test generateList calls API and updates state
    - Test toggleItem uses optimistic update with rollback
    - Test uncheckAll updates all items to unchecked
    - Test getItemsByCategory returns grouped items
    - Test error handling sets error state
    - Expected: 5 tests covering store operations
  - [x] 5.2 Create `mobile/types/shopping-list.ts`
    - `ShoppingListItem`: id, user_id, ingredient_name, quantity, category, is_checked, week_start, created_at, updated_at
    - `CategoryGroup`: category, items, item_count
    - `IngredientCategory` type: union of category strings
  - [x] 5.3 Create `mobile/services/shopping-list.ts`
    - `generateList()`: POST /api/shopping-list/generate
    - `getList(weekStart?: string)`: GET /api/shopping-list
    - `toggleItem(itemId: string)`: PUT /api/shopping-list/items/{id}/check
    - `uncheckAll(weekStart?: string)`: PUT /api/shopping-list/uncheck-all
    - `deleteList(weekStart?: string)`: DELETE /api/shopping-list
    - Use `apiClient` with auth token
    - Handle token refresh on 401
  - [x] 5.4 Create `mobile/stores/shopping-list.ts` Zustand store
    - State: items (Map<string, ShoppingListItem>), isLoading, isGenerating, error, lastGeneratedAt
    - Action: `generateList()` - call API, populate items Map, set lastGeneratedAt
    - Action: `fetchList(weekStart?)` - get current list from API
    - Action: `toggleItem(id)` - optimistic update, call API, rollback on error
    - Action: `uncheckAll()` - update all items locally, call API
    - Action: `getItemsByCategory()` - return items grouped by category
    - Action: `reset()` - clear store state
  - [x] 5.5 Implement optimistic updates with rollback pattern
    - Store previous state before API call
    - Update state immediately for responsiveness
    - Rollback to previous state on error
    - Follow pattern from `meal-planning.ts`
  - [x] 5.6 Verify store tests pass
    - Run mobile store tests
    - Expected: TypeScript compiles without errors

**Acceptance Criteria:**
- Store correctly manages shopping list state
- Optimistic updates provide responsive UI
- Error handling with rollback works correctly
- Items correctly grouped by category

---

### Mobile - UI Components

#### Task Group 6: Shopping List Screen and Components
**Dependencies:** Task Group 5
**Pattern Reference:** `mobile/components/meal-planning/`, `mobile/app/(tabs)/planning.tsx`

- [x] 6.0 Complete UI layer
  - [x] 6.1 Write UI component tests
    - Test ShoppingListItem renders ingredient name and quantity
    - Test ShoppingListItem checkbox toggles on press
    - Test checked item shows strikethrough style
    - Test CategorySection collapses/expands on header press
    - Test empty state shows "Generez votre liste" CTA
    - Test "Regenerer" button triggers confirmation dialog
    - Expected: 6 tests covering component behavior
  - [x] 6.2 Update tab navigation in `mobile/app/(tabs)/_layout.tsx`
    - Add "Courses" tab at position 4
    - Icon: shopping-cart from Feather icons
    - Label: "Courses"
  - [x] 6.3 Create `mobile/components/shopping-list/ShoppingListItem.tsx`
    - Props: item (ShoppingListItem), onToggle (function)
    - Layout: checkbox left, ingredient name center, quantity right
    - Checked state: strikethrough text, muted color (#9CA3AF)
    - Unchecked state: normal text (#1F2937)
    - Checkbox uses primary color (#14B8A6) when checked
    - TouchableOpacity wraps entire row for tap handling
  - [x] 6.4 Create `mobile/components/shopping-list/CategorySection.tsx`
    - Props: category (string), items (ShoppingListItem[]), onToggleItem (function)
    - Collapsible section with animated expand/collapse
    - Header: category name (H4 style), item count badge, chevron icon
    - Content: list of ShoppingListItem components
    - Default state: expanded
  - [x] 6.5 Create `mobile/components/shopping-list/EmptyState.tsx`
    - Centered layout with illustration/icon
    - Title: "Aucune liste de courses"
    - Subtitle: "Generez une liste a partir de votre planning"
    - CTA Button: "Generer ma liste" (primary style)
    - OnPress: call generateList()
  - [x] 6.6 Create `mobile/components/shopping-list/ListHeader.tsx`
    - Display: "Liste de courses" title
    - Subtitle: "Semaine du {week_start}" or lastGeneratedAt timestamp
    - Action buttons row:
      - "Tout decocher" (ghost button, left)
      - "Regenerer" (secondary button, coral color, right)
  - [x] 6.7 Create `mobile/components/shopping-list/index.ts`
    - Export all shopping list components
  - [x] 6.8 Implement `mobile/app/(tabs)/shopping.tsx` screen
    - Use useShoppingListStore hook
    - Fetch list on mount using useFocusEffect
    - Show EmptyState when items.size === 0 and not loading
    - Show loading spinner during generation/fetch
    - Render ListHeader at top
    - Render CategorySection for each category with items
    - Category order: Legumes, Viandes, Poissons, Produits laitiers, Epicerie, Boissons, Surgeles, Autres
    - Pull-to-refresh to regenerate list
  - [x] 6.9 Implement confirmation dialog for regeneration
    - Title: "Regenerer la liste ?"
    - Message: "Cette action effacera les elements coches."
    - Actions: "Annuler" (cancel), "Regenerer" (confirm)
    - Use Alert.alert() from React Native
  - [x] 6.10 Apply styling following design system
    - Card containers: white bg, 12px rounded corners, subtle border
    - Category headers: H4 (16px semibold, #1F2937)
    - Item text: body (16px regular)
    - Checked items: #9CA3AF with strikethrough
    - Checkbox: #14B8A6 when checked
    - Regenerer button: coral #FF8A65
    - Tout decocher: ghost style, primary color text
  - [x] 6.11 Implement responsive layout
    - Safe area handling for all screen sizes
    - ScrollView with proper keyboard avoiding
    - Consistent padding (16px horizontal)
  - [x] 6.12 Verify UI tests pass
    - Run component tests
    - Expected: TypeScript compiles without errors

**Acceptance Criteria:**
- Shopping tab appears in navigation
- Items display with correct styling
- Check/uncheck animations smooth
- Categories collapsible
- Empty state shows when no items
- Regeneration confirms before clearing

---

### Integration & Testing

#### Task Group 7: End-to-End Testing and Final Validation
**Dependencies:** Task Groups 1-6

- [x] 7.0 Validate complete feature implementation
  - [x] 7.1 Run complete backend test suite
    - Run all shopping list tests (Groups 1-4)
    - Expected: 51 tests passing
    - Verify no regressions in existing tests
  - [x] 7.2 Run complete mobile test suite
    - Run TypeScript compilation check
    - Expected: No TypeScript errors
    - Verify no regressions in existing code
  - [ ] 7.3 Manual integration testing checklist
    - [ ] Create meal plan with 3+ recipes for current week
    - [ ] Generate shopping list from Courses tab
    - [ ] Verify all ingredients appear with correct quantities
    - [ ] Verify ingredients grouped by correct categories
    - [ ] Check off several items, verify persistence
    - [ ] Switch device/browser, verify checked state synced
    - [ ] Use "Tout decocher", verify all items unchecked
    - [ ] Use "Regenerer", confirm dialog appears
    - [ ] Confirm regeneration, verify new list with all unchecked
    - [ ] Modify meal plan, verify list does NOT auto-update
    - [ ] Regenerate after meal plan change, verify updated list
  - [ ] 7.4 Edge case testing
    - [ ] Empty meal plan - verify empty state displays
    - [ ] Single recipe - verify list generates correctly
    - [ ] Same recipe multiple times - verify quantities aggregate
    - [ ] Recipe with 4+ portions - verify quantity multiplication
    - [ ] Unknown ingredients - verify they appear in "Autres"
    - [ ] Network error during generation - verify error handling
    - [ ] Token expiry during operation - verify refresh and retry
  - [ ] 7.5 Performance validation
    - [ ] List generation < 3 seconds for 7 recipes
    - [ ] Toggle item response < 200ms (optimistic)
    - [ ] Smooth animations at 60fps
  - [ ] 7.6 Generate final test report
    - Document total test count
    - List any deferred tests with justification
    - Confirm feature ready for deployment

**Acceptance Criteria:**
- All automated tests pass
- Manual testing checklist complete
- Edge cases handled gracefully
- Performance targets met
- No regressions in existing features

---

## Execution Order

Recommended implementation sequence:

```
1. Task Group 1: Database Schema & Models (backend foundation)
   |
2. Task Group 2: Ingredient Aggregation Service (core logic)
   |
3. Task Group 3: Category Mapping & Shopping List Service (complete backend service)
   |
4. Task Group 4: API Routes (expose backend functionality)
   |
5. Task Group 5: Zustand Store & API Service (mobile state management)
   |
6. Task Group 6: UI Components (user interface)
   |
7. Task Group 7: Integration & Testing (validation)
```

## Files to Create

### Backend
- `backend/app/models/shopping_list.py` - Pydantic models [DONE]
- `backend/app/services/shopping_list_service.py` - Business logic [DONE]
- `backend/app/routes/shopping_list.py` - API endpoints [DONE]
- `supabase/migrations/20260103_create_shopping_list_items.sql` - Database migration [DONE]
- `backend/tests/test_models/test_shopping_list.py` - Model tests [DONE]
- `backend/tests/test_services/test_shopping_list_service.py` - Service tests [DONE]
- `backend/tests/test_routes/test_shopping_list.py` - API tests [DONE]

### Mobile
- `mobile/types/shopping-list.ts` - TypeScript types [DONE]
- `mobile/services/shopping-list.ts` - API client [DONE]
- `mobile/stores/shopping-list.ts` - Zustand store [DONE]
- `mobile/components/shopping-list/ShoppingListItem.tsx` - Item component [DONE]
- `mobile/components/shopping-list/CategorySection.tsx` - Collapsible category [DONE]
- `mobile/components/shopping-list/EmptyState.tsx` - Empty state display [DONE]
- `mobile/components/shopping-list/ListHeader.tsx` - Header with actions [DONE]
- `mobile/components/shopping-list/index.ts` - Component exports [DONE]
- Update: `mobile/app/(tabs)/shopping.tsx` - Main screen [DONE]

## Test Summary

| Task Group | Test Count | Focus Area |
|------------|------------|------------|
| Group 1 | 10 | Model validation, migration |
| Group 2 | 21 | Quantity parsing, aggregation |
| Group 3 | 13 | Category mapping, service CRUD |
| Group 4 | 7 | API endpoints, auth |
| Group 5 | TypeScript | Store actions, optimistic updates |
| Group 6 | TypeScript | UI rendering, interactions |
| **Total** | **51** | Full backend test coverage |
