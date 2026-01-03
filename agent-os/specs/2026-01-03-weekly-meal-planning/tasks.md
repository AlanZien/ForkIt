# Task Breakdown: Weekly Meal Planning

## Overview

**Feature**: Weekly Meal Planning - Enable users to plan their weekly meals with 14 slots (lunch/dinner per day, Monday-Sunday)

**Total Tasks**: 35 sub-tasks across 5 task groups

**Effort Estimate**: Large (L)

**Dependencies**:
- Recipe Favorites feature (completed)
- Recipe Browsing feature (completed)
- User Profile feature (completed)

## Task List

---

### Database Layer

#### Task Group 1: Database Schema and Migration
**Dependencies:** None
**Estimated Effort:** S

- [x] 1.0 Complete database layer for meal_slots table
  - [x] 1.1 Create Supabase migration for meal_slots table
    - Table name: `meal_slots`
    - Fields:
      - `id` (uuid, primary key, default gen_random_uuid())
      - `user_id` (uuid, not null, references auth.users)
      - `date` (date, not null) - the day of the meal
      - `meal_type` (text, not null) - 'dejeuner' or 'diner'
      - `recipe_id` (text, not null) - TheMealDB recipe ID
      - `recipe_name` (text, not null)
      - `recipe_thumbnail` (text, nullable)
      - `portions` (integer, not null, default 2)
      - `created_at` (timestamptz, default now())
      - `updated_at` (timestamptz, default now())
    - Indexes:
      - `idx_meal_slots_user_date` on (user_id, date)
      - `idx_meal_slots_user_recipe` on (user_id, recipe_id)
    - Unique constraint: `uq_meal_slots_user_date_type` on (user_id, date, meal_type)
  - [x] 1.2 Create RLS policies for meal_slots
    - Enable RLS on table
    - SELECT policy: user can only read their own slots
    - INSERT policy: user can only insert their own slots
    - UPDATE policy: user can only update their own slots
    - DELETE policy: user can only delete their own slots
  - [x] 1.3 Create trigger for updated_at
    - Auto-update `updated_at` on row modification
  - [x] 1.4 Verify migration runs successfully
    - Apply migration to Supabase
    - Verify table structure matches spec
    - Test RLS policies work correctly

**Acceptance Criteria:**
- meal_slots table exists with correct schema
- RLS policies enforce user isolation
- Unique constraint prevents duplicate slots for same user/date/meal_type
- Indexes optimize week-range queries

---

### Backend API Layer

#### Task Group 2: Pydantic Models and Service Layer
**Dependencies:** Task Group 1
**Estimated Effort:** M

- [x] 2.0 Complete backend models and service for meal planning
  - [x] 2.1 Create Pydantic models in `backend/app/models/meal_slot.py`
    - `MealType` enum: 'dejeuner', 'diner'
    - `MealSlotCreate`: recipe_id, recipe_name, recipe_thumbnail, date, meal_type, portions (optional)
    - `MealSlotUpdate`: recipe_id, recipe_name, recipe_thumbnail, portions (all optional)
    - `MealSlotResponse`: id, user_id, date, meal_type, recipe_id, recipe_name, recipe_thumbnail, portions, created_at, updated_at
    - `WeekSlotsResponse`: slots (list), week_start (date), week_end (date)
    - `RecentRecipeResponse`: recipe_id, recipe_name, recipe_thumbnail, last_used (datetime)
    - Follow pattern from: `backend/app/models/favorite.py`
  - [x] 2.2 Create MealSlotsService in `backend/app/services/meal_slots_service.py`
    - `__init__`: Initialize Supabase client, table = "meal_slots"
    - `get_week_slots(user_id, week_start_date)`: Fetch 7 days of slots
    - `get_slot(user_id, date, meal_type)`: Get single slot
    - `create_slot(user_id, data: MealSlotCreate)`: Create or replace slot
    - `update_slot(user_id, date, meal_type, data: MealSlotUpdate)`: Update portions or recipe
    - `delete_slot(user_id, date, meal_type)`: Remove slot
    - `get_recent_recipes(user_id, limit=10)`: Get last 10 unique recipes used
    - Follow pattern from: `backend/app/services/favorites_service.py`
  - [x] 2.3 Add validation logic
    - Validate date is not in the past (today allowed)
    - Validate date is within 4 weeks from current week
    - Validate meal_type is 'dejeuner' or 'diner'
    - Validate portions is between 1 and 20

**Acceptance Criteria:**
- All Pydantic models validate input correctly
- Service methods follow established patterns
- Week queries return 0-14 slots efficiently
- Recent recipes are unique and ordered by last_used

---

#### Task Group 3: API Routes
**Dependencies:** Task Group 2
**Estimated Effort:** M

- [x] 3.0 Complete API routes for meal planning
  - [x] 3.1 Write API route tests in `backend/tests/test_routes/test_meal_slots.py`
    - Test: GET /api/meal-slots?week_start={date} returns empty list for new user
    - Test: GET /api/meal-slots?week_start={date} returns slots within date range
    - Test: POST /api/meal-slots creates slot and returns 201
    - Test: POST /api/meal-slots with existing date/meal_type replaces slot
    - Test: PUT /api/meal-slots/{date}/{meal_type} updates portions
    - Test: DELETE /api/meal-slots/{date}/{meal_type} returns 204
    - Test: GET /api/meal-slots/recent returns last 10 recipes
    - Test: All endpoints return 401 without auth
    - Test: Validation errors return 400 with clear message
    - Follow test pattern from: `backend/tests/test_routes/test_favorites.py`
    - Expected: 9 tests covering CRUD and edge cases
  - [x] 3.2 Create routes in `backend/app/routes/meal_slots.py`
    - Router prefix: `/api/meal-slots`
    - `GET /` - Get week slots (query param: week_start as ISO date)
    - `POST /` - Create/replace slot
    - `PUT /{date}/{meal_type}` - Update slot (date format: YYYY-MM-DD)
    - `DELETE /{date}/{meal_type}` - Delete slot
    - `GET /recent` - Get recent recipes
    - All routes require authentication via `get_current_user`
    - Follow pattern from: `backend/app/routes/favorites.py`
  - [x] 3.3 Register router in main.py
    - Import meal_slots router
    - Include router in app
  - [x] 3.4 Verify API route tests pass
    - Run: `pytest backend/tests/test_routes/test_meal_slots.py -v`
    - Expected: 13/13 tests passing ✅
    - All endpoints return correct status codes

**Acceptance Criteria:**
- All 9 API tests pass
- Endpoints follow RESTful conventions
- Proper error handling with meaningful messages
- Authentication enforced on all routes

---

### Mobile Frontend Layer

#### Task Group 4: Mobile Types, Service, and Store
**Dependencies:** Task Group 3
**Estimated Effort:** M

- [x] 4.0 Complete mobile data layer for meal planning
  - [x] 4.1 Create TypeScript types in `mobile/types/meal-slot.ts`
    - `MealType`: 'dejeuner' | 'diner'
    - `MealSlot`: id, user_id, date, meal_type, recipe_id, recipe_name, recipe_thumbnail, portions, created_at, updated_at
    - `MealSlotCreate`: recipe_id, recipe_name, recipe_thumbnail, date, meal_type, portions?
    - `MealSlotUpdate`: recipe_id?, recipe_name?, recipe_thumbnail?, portions?
    - `WeekSlotsResponse`: slots, week_start, week_end
    - `RecentRecipe`: recipe_id, recipe_name, recipe_thumbnail, last_used
    - Follow pattern from: `mobile/types/favorite.ts`
  - [x] 4.2 Create API service in `mobile/services/meal-slots.ts`
    - `getWeekSlots(weekStart: string)`: GET /api/meal-slots?week_start={date}
    - `createSlot(data: MealSlotCreate)`: POST /api/meal-slots
    - `updateSlot(date: string, mealType: MealType, data: MealSlotUpdate)`: PUT /api/meal-slots/{date}/{meal_type}
    - `deleteSlot(date: string, mealType: MealType)`: DELETE /api/meal-slots/{date}/{meal_type}
    - `getRecentRecipes()`: GET /api/meal-slots/recent
    - Use existing `api` client from: `mobile/services/api.ts`
  - [x] 4.3 Create Zustand store in `mobile/stores/meal-planning.ts`
    - State:
      - `slots`: Map<string, MealSlot> (key: "{date}_{meal_type}")
      - `currentWeekStart`: string (ISO date of Monday)
      - `recentRecipes`: RecentRecipe[]
      - `isLoading`: boolean
      - `isUpdating`: boolean
      - `error`: string | null
    - Actions:
      - `fetchWeek(weekStart: string)`: Load week slots
      - `addSlot(data: MealSlotCreate)`: Optimistic add with rollback
      - `updateSlot(date, mealType, data)`: Optimistic update with rollback
      - `removeSlot(date, mealType)`: Optimistic delete with rollback
      - `fetchRecentRecipes()`: Load recent recipes
      - `navigateWeek(direction: 'prev' | 'next')`: Change week
      - `canNavigatePrev()`: Check if can go to previous week
      - `canNavigateNext()`: Check if within 4-week limit
      - `getSlot(date, mealType)`: Get slot from map
      - `reset()`: Clear store
    - Helpers:
      - `getWeekStart(date: Date)`: Calculate Monday of given week
      - `generateSlotKey(date, mealType)`: Create map key
    - Follow pattern from: `mobile/stores/favorites.ts`
  - [x] 4.4 Add week date utilities in `mobile/utils/date.ts`
    - `getWeekStart(date: Date)`: Get Monday of the week
    - `getWeekEnd(date: Date)`: Get Sunday of the week
    - `formatDateISO(date: Date)`: Format as YYYY-MM-DD
    - `addWeeks(date: Date, weeks: number)`: Add/subtract weeks
    - `isCurrentWeek(weekStart: string)`: Check if current week
    - `isWithinRange(weekStart: string, maxWeeks: number)`: Check within limit
    - `getDayName(date: Date, locale: string)`: Get localized day name (Lundi, Mardi, etc.)

**Acceptance Criteria:**
- Types match backend API responses
- API service handles all CRUD operations
- Store manages optimistic updates with rollback
- Week navigation logic is correct
- Date utilities handle French locale

---

#### Task Group 5: Mobile UI Components and Screens
**Dependencies:** Task Group 4
**Estimated Effort:** L

- [x] 5.0 Complete mobile UI for meal planning
  - [x] 5.1 Create MealSlotCard component in `mobile/components/meal-planning/MealSlotCard.tsx`
    - Props: slot (MealSlot | null), date, mealType, onPress, onLongPress
    - Empty state:
      - Dashed border (1px, gray-300)
      - "+" icon centered (Ionicons: add-outline)
      - Meal type label below (Dejeuner/Diner)
      - Touch feedback on press
    - Filled state:
      - Recipe thumbnail (56x56, rounded)
      - Recipe name (truncated to 2 lines)
      - Portion badge (top-right corner, primary color)
      - Touch feedback on press
    - Long-press triggers context menu
    - Minimum height: 72px
    - Follow design-system.md specifications
  - [x] 5.2 Create DayColumn component in `mobile/components/meal-planning/DayColumn.tsx`
    - Props: date, slots (dejeuner, diner), onSlotPress, onSlotLongPress
    - Display day name (Lundi, Mardi, etc.) as header
    - Display date (e.g., "3 Jan") below day name
    - Two MealSlotCard components stacked vertically
    - Highlight today with different background
  - [x] 5.3 Create WeekNavigator component in `mobile/components/meal-planning/WeekNavigator.tsx`
    - Props: currentWeekStart, onPrevious, onNext, canGoPrev, canGoNext
    - Left arrow button (disabled when canGoPrev=false)
    - Week label: "Semaine du {day} {month}" (e.g., "Semaine du 6 Jan")
    - Right arrow button (disabled when canGoNext=false)
    - Use Ionicons: chevron-back, chevron-forward
  - [x] 5.4 Create RecipeSelectionModal component in `mobile/components/meal-planning/RecipeSelectionModal.tsx`
    - Props: visible, onClose, onSelect(recipe), selectedDate, selectedMealType
    - Modal with slide-up animation
    - Header: "Choisir une recette" with close button
    - Three tabs: "Favoris", "Recherche", "Recents"
    - Favoris tab:
      - Reuse favorites from useFavoritesStore
      - Display as scrollable list
    - Recherche tab:
      - Search input with debounce (300ms)
      - Results from TheMealDB via RecipesService
      - Display as scrollable list
    - Recents tab:
      - Display from useMealPlanningStore.recentRecipes
      - Show last_used date for each
    - Recipe item: thumbnail (48x48), name, tap to select
    - Selection closes modal and calls onSelect
  - [x] 5.5 Create SlotActionMenu component in `mobile/components/meal-planning/SlotActionMenu.tsx`
    - Props: visible, onClose, onView, onReplace, onDelete, recipeName
    - Bottom sheet or action sheet style
    - Options:
      - "Voir la recette" (navigate to detail)
      - "Remplacer" (open selection modal)
      - "Supprimer" (with confirmation)
    - Delete shows confirmation dialog: "Supprimer {recipeName} ?"
  - [x] 5.6 Create WeekView component in `mobile/components/meal-planning/WeekView.tsx`
    - Props: none (uses store directly)
    - Horizontal ScrollView of 7 DayColumn components
    - OR Vertical FlatList of days (depending on design choice)
    - Loading state: Skeleton placeholders
    - Error state: Error message with retry button
    - Empty week message: "Aucun repas planifie cette semaine"
  - [x] 5.7 Create Planning screen in `mobile/app/(tabs)/planning.tsx`
    - Screen layout:
      - Header with WeekNavigator
      - WeekView taking remaining space
    - On mount: fetch current week slots
    - On week navigation: fetch new week slots
    - State management via useMealPlanningStore
    - Handle slot press: open RecipeSelectionModal
    - Handle slot long-press: open SlotActionMenu
    - Recipe selection: call addSlot or updateSlot
    - View action: navigate to /recipe/{id}
  - [x] 5.8 Add Planning tab to tab navigator
    - Update `mobile/app/(tabs)/_layout.tsx`
    - Add "Planning" tab between existing tabs
    - Icon: Ionicons "calendar-outline"
    - Label: "Planning"
  - [x] 5.9 Style components following design system
    - Use colors from design-system.md:
      - Primary: #14B8A6 (teal)
      - Background: #F9FAFB
      - Card: white with 1px border, 12px radius
    - Touch targets minimum 44x44
    - Consistent spacing (8px, 12px, 16px, 24px)
    - French typography for labels

**Acceptance Criteria:**
- Weekly calendar displays 7 days with 2 slots each
- Empty slots show "+" and meal type label
- Filled slots show recipe info and portion badge
- Week navigation works with proper boundary checks
- Recipe selection modal has 3 functional tabs
- Long-press menu provides View/Replace/Delete actions
- Delete requires confirmation
- Optimistic UI updates feel responsive
- Loading and error states handled gracefully
- Tab appears in navigation

---

### Testing and Validation

#### Task Group 6: Integration Testing and Final Validation
**Dependencies:** Task Groups 1-5
**Estimated Effort:** M

- [ ] 6.0 Complete integration testing and validation
  - [ ] 6.1 Write service layer tests in `backend/tests/test_services/test_meal_slots_service.py`
    - Test: get_week_slots returns empty for new user
    - Test: get_week_slots returns only slots within date range
    - Test: create_slot creates new slot
    - Test: create_slot replaces existing slot for same date/meal_type
    - Test: update_slot modifies portions correctly
    - Test: delete_slot removes slot
    - Test: get_recent_recipes returns unique recipes ordered by last_used
    - Test: validation rejects past dates
    - Test: validation rejects dates beyond 4 weeks
    - Expected: 9 tests
  - [ ] 6.2 Run full backend test suite
    - Run: `pytest backend/tests -v`
    - Ensure no regressions in existing tests
    - All meal_slots tests pass
  - [ ] 6.3 Manual E2E testing checklist
    - [ ] Fresh user sees empty planning screen
    - [ ] Can add recipe to empty slot via Favoris tab
    - [ ] Can add recipe to empty slot via Recherche tab
    - [ ] Can add recipe to empty slot via Recents tab
    - [ ] Filled slot displays recipe thumbnail, name, portions
    - [ ] Long-press on filled slot shows action menu
    - [ ] "Voir" navigates to recipe detail
    - [ ] "Remplacer" opens modal and replaces recipe
    - [ ] "Supprimer" shows confirmation then removes slot
    - [ ] Week navigation arrows work correctly
    - [ ] Cannot navigate before current week
    - [ ] Cannot navigate beyond 4 weeks ahead
    - [ ] Portions display correctly from user profile default
    - [ ] Data persists after app restart
    - [ ] Optimistic updates feel instant
    - [ ] Error rollback works (disable network and retry)
  - [ ] 6.4 Performance verification
    - Week load time < 500ms on good connection
    - No visible lag on slot interactions
    - Smooth scrolling through week days

**Acceptance Criteria:**
- All service tests pass (9/9)
- All route tests pass (9/9)
- Full backend suite passes with no regressions
- E2E manual testing checklist complete
- Performance targets met

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Database Schema** (Day 1)
   - Create migration and apply to Supabase
   - Verify RLS policies work correctly

2. **Task Group 2: Backend Models and Service** (Day 1-2)
   - Create Pydantic models
   - Implement service layer with all methods

3. **Task Group 3: API Routes** (Day 2)
   - Write tests first (TDD approach)
   - Implement routes to pass tests
   - Verify all 9 tests pass

4. **Task Group 4: Mobile Data Layer** (Day 2-3)
   - Create types matching API
   - Implement API service
   - Build Zustand store with optimistic updates
   - Create date utilities

5. **Task Group 5: Mobile UI** (Day 3-4)
   - Start with MealSlotCard component
   - Build DayColumn and WeekNavigator
   - Create RecipeSelectionModal with tabs
   - Implement SlotActionMenu with confirmation
   - Compose WeekView
   - Create Planning screen
   - Add tab to navigation

6. **Task Group 6: Testing and Validation** (Day 5)
   - Write service tests
   - Run full test suite
   - Complete E2E testing checklist
   - Performance verification

---

## Files to Create/Modify

### New Files (Backend)
- `backend/app/models/meal_slot.py`
- `backend/app/services/meal_slots_service.py`
- `backend/app/routes/meal_slots.py`
- `backend/tests/test_routes/test_meal_slots.py`
- `backend/tests/test_services/test_meal_slots_service.py`
- `supabase/migrations/YYYYMMDDHHMMSS_create_meal_slots.sql`

### Modified Files (Backend)
- `backend/app/main.py` (add router)

### New Files (Mobile)
- `mobile/types/meal-slot.ts`
- `mobile/services/meal-slots.ts`
- `mobile/stores/meal-planning.ts`
- `mobile/utils/date.ts`
- `mobile/components/meal-planning/MealSlotCard.tsx`
- `mobile/components/meal-planning/DayColumn.tsx`
- `mobile/components/meal-planning/WeekNavigator.tsx`
- `mobile/components/meal-planning/RecipeSelectionModal.tsx`
- `mobile/components/meal-planning/SlotActionMenu.tsx`
- `mobile/components/meal-planning/WeekView.tsx`
- `mobile/app/(tabs)/planning.tsx`

### Modified Files (Mobile)
- `mobile/app/(tabs)/_layout.tsx` (add tab)

---

## Reference Patterns

| Pattern | Reference File |
|---------|---------------|
| Pydantic models | `backend/app/models/favorite.py` |
| Service class | `backend/app/services/favorites_service.py` |
| API routes | `backend/app/routes/favorites.py` |
| Route tests | `backend/tests/test_routes/test_favorites.py` |
| TypeScript types | `mobile/types/favorite.ts` |
| API service | `mobile/services/favorites.ts` |
| Zustand store | `mobile/stores/favorites.ts` |
| API client | `mobile/services/api.ts` |
