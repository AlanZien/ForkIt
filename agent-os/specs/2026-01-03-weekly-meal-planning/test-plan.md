# Test Plan: Weekly Meal Planning

## Metadata
- **Feature**: Weekly Meal Planning
- **Spec**: agent-os/specs/2026-01-03-weekly-meal-planning/spec.md
- **Requirements**: agent-os/specs/2026-01-03-weekly-meal-planning/planning/requirements.md
- **Created**: 2026-01-03
- **Status**: Planning Complete

## Test Summary

| Layer | Critical | High | Medium | Low | Total |
|-------|----------|------|--------|-----|-------|
| Database | 6 | 4 | 2 | 0 | 12 |
| API | 8 | 10 | 6 | 2 | 26 |
| Mobile UI | 6 | 12 | 8 | 4 | 30 |
| Integration | 4 | 2 | 2 | 0 | 8 |
| **Total** | **24** | **28** | **18** | **6** | **76** |

**Coverage Targets:**
- Critical paths: 100%
- High priority: 100%
- Medium priority: 80%
- Low priority: Deferred

---

## Database Layer (12 tests)

### meal_slots Table Schema (4 tests)

#### 1. test_meal_slots_table_exists_with_correct_columns
**Priority:** Critical
**Given:** Database migration has been applied
**When:** Querying the meal_slots table schema
**Then:**
- Table `meal_slots` exists
- Columns: `id` (uuid, primary key), `user_id` (uuid, not null), `date` (date, not null), `meal_type` (varchar, not null), `recipe_id` (varchar, not null), `recipe_name` (varchar, not null), `recipe_thumbnail` (varchar), `portions` (integer, not null), `created_at` (timestamp), `updated_at` (timestamp)
**Related Requirement:** spec.md "Data Persistence (Supabase)"

#### 2. test_meal_slots_unique_constraint_user_date_meal_type
**Priority:** Critical
**Given:** Database migration has been applied
**When:** Attempting to insert two slots with same user_id, date, and meal_type
**Then:** Database raises unique constraint violation error
**Related Requirement:** spec.md "Single recipe per slot"

#### 3. test_meal_slots_meal_type_check_constraint
**Priority:** High
**Given:** Database migration has been applied
**When:** Attempting to insert slot with meal_type = 'breakfast'
**Then:** Database raises check constraint violation (only 'dejeuner' or 'diner' allowed)
**Related Requirement:** spec.md "Each day shows 2 meal slots: Dejeuner and Diner"

#### 4. test_meal_slots_portions_check_constraint
**Priority:** High
**Given:** Database migration has been applied
**When:** Attempting to insert slot with portions = 0 or portions = 25
**Then:** Database raises check constraint violation (1-20 allowed)
**Related Requirement:** spec.md "Portion Management"

### Row Level Security (4 tests)

#### 5. test_rls_user_can_only_read_own_slots
**Priority:** Critical
**Given:**
- User A has 3 meal slots
- User B has 2 meal slots
**When:** User A queries all meal_slots
**Then:** Only User A's 3 slots are returned
**Related Requirement:** spec.md "User can only access their own meal_slots (RLS policy)"

#### 6. test_rls_user_can_only_insert_own_slots
**Priority:** Critical
**Given:** User A is authenticated
**When:** User A inserts a meal slot with user_id = User B's ID
**Then:** RLS policy blocks the insert or user_id is forced to User A
**Related Requirement:** spec.md "RLS policy"

#### 7. test_rls_user_can_only_update_own_slots
**Priority:** Critical
**Given:**
- User A has slot with id = 'slot-1'
- User B is authenticated
**When:** User B attempts to update slot 'slot-1'
**Then:** Update fails or returns 0 affected rows
**Related Requirement:** spec.md "RLS policy"

#### 8. test_rls_user_can_only_delete_own_slots
**Priority:** Critical
**Given:**
- User A has slot with id = 'slot-1'
- User B is authenticated
**When:** User B attempts to delete slot 'slot-1'
**Then:** Delete fails or returns 0 affected rows
**Related Requirement:** spec.md "RLS policy"

### Indexes and Performance (2 tests)

#### 9. test_index_exists_on_user_id_and_date
**Priority:** High
**Given:** Database migration has been applied
**When:** Querying database indexes on meal_slots
**Then:** Composite index on (user_id, date) exists for efficient week queries
**Related Requirement:** requirements.md "Indexes on user_id and date for efficient week queries"

#### 10. test_week_query_performance
**Priority:** Medium
**Given:** User has 100 meal slots across 10 weeks
**When:** Querying slots for a specific week (7 days)
**Then:** Query executes in < 100ms using index scan
**Related Requirement:** requirements.md "Week-based data retrieval"

### Data Integrity (2 tests)

#### 11. test_cascade_delete_on_user_deletion
**Priority:** High
**Given:** User A has 5 meal slots
**When:** User A's account is deleted
**Then:** All 5 meal slots are cascade deleted
**Related Requirement:** spec.md "Data Persistence"

#### 12. test_updated_at_auto_updates_on_modification
**Priority:** Medium
**Given:** Meal slot created at time T1
**When:** Slot is updated at time T2
**Then:** updated_at column is automatically set to T2
**Related Requirement:** spec.md "Data Persistence"

---

## API Layer (26 tests)

### GET /api/meal-slots (Week Fetch) (6 tests)

#### 13. test_get_week_slots_returns_200_with_slots
**Priority:** Critical
**Given:**
- User is authenticated
- User has 5 slots for week starting 2026-01-06
**When:** GET /api/meal-slots?week_start=2026-01-06
**Then:**
- Status: 200 OK
- Body: Array of 5 MealSlotResponse objects
- Each object has: id, date, meal_type, recipe_id, recipe_name, recipe_thumbnail, portions
**Related Requirement:** spec.md "Fetch week data on navigation"

#### 14. test_get_week_slots_returns_empty_array_for_no_slots
**Priority:** High
**Given:**
- User is authenticated
- User has no slots for week starting 2026-01-13
**When:** GET /api/meal-slots?week_start=2026-01-13
**Then:**
- Status: 200 OK
- Body: Empty array []
**Related Requirement:** spec.md "Support for partial week planning"

#### 15. test_get_week_slots_returns_401_without_auth
**Priority:** Critical
**Given:** No authentication token provided
**When:** GET /api/meal-slots?week_start=2026-01-06
**Then:**
- Status: 401 Unauthorized
- Body: {"detail": "Not authenticated"}
**Related Requirement:** spec.md "User can only access their own meal_slots"

#### 16. test_get_week_slots_returns_400_for_invalid_week_start
**Priority:** High
**Given:** User is authenticated
**When:** GET /api/meal-slots?week_start=2026-01-07 (Tuesday, not Monday)
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "week_start must be a Monday"}
**Related Requirement:** spec.md "Week is identified by its Monday date"

#### 17. test_get_week_slots_returns_400_for_past_week
**Priority:** High
**Given:**
- User is authenticated
- Current date is 2026-01-06
**When:** GET /api/meal-slots?week_start=2025-12-30 (past week)
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "Cannot access past weeks"}
**Related Requirement:** spec.md "Disable Previous button when on current week"

#### 18. test_get_week_slots_returns_400_for_beyond_4_weeks
**Priority:** High
**Given:**
- User is authenticated
- Current week starts 2026-01-06
**When:** GET /api/meal-slots?week_start=2026-02-10 (5 weeks ahead)
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "Cannot access beyond 4 weeks ahead"}
**Related Requirement:** spec.md "Up to 4 weeks ahead"

### POST /api/meal-slots (Create Slot) (8 tests)

#### 19. test_create_slot_returns_201_with_slot
**Priority:** Critical
**Given:**
- User is authenticated
- Request body: {"date": "2026-01-06", "meal_type": "dejeuner", "recipe_id": "52772", "recipe_name": "Teriyaki Chicken", "recipe_thumbnail": "https://...", "portions": 4}
**When:** POST /api/meal-slots
**Then:**
- Status: 201 Created
- Body: MealSlotResponse with generated id and all fields
- Slot persisted in database with user_id
**Related Requirement:** spec.md "Recipe Selection Modal"

#### 20. test_create_slot_returns_401_without_auth
**Priority:** Critical
**Given:** No authentication token
**When:** POST /api/meal-slots with valid body
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "RLS policy"

#### 21. test_create_slot_returns_400_for_past_date
**Priority:** High
**Given:**
- User is authenticated
- Current date is 2026-01-06
- Request body with date: "2026-01-05" (yesterday)
**When:** POST /api/meal-slots
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "Cannot create slots for past dates"}
**Related Requirement:** spec.md "Current week is default view"

#### 22. test_create_slot_returns_400_for_beyond_4_weeks
**Priority:** High
**Given:**
- User is authenticated
- Current date is 2026-01-06
- Request body with date: "2026-02-10" (5+ weeks ahead)
**When:** POST /api/meal-slots
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "Cannot create slots beyond 4 weeks"}
**Related Requirement:** spec.md "4 weeks ahead limit"

#### 23. test_create_slot_returns_400_for_invalid_meal_type
**Priority:** High
**Given:**
- User is authenticated
- Request body with meal_type: "breakfast"
**When:** POST /api/meal-slots
**Then:**
- Status: 400 Bad Request
- Body: {"detail": "meal_type must be 'dejeuner' or 'diner'"}
**Related Requirement:** spec.md "Dejeuner and Diner only"

#### 24. test_create_slot_returns_409_for_duplicate_slot
**Priority:** Critical
**Given:**
- User is authenticated
- User already has slot for date 2026-01-06, meal_type "dejeuner"
**When:** POST /api/meal-slots with same date and meal_type
**Then:**
- Status: 409 Conflict
- Body: {"detail": "Slot already exists for this date and meal type"}
**Related Requirement:** spec.md "Single recipe per slot"

#### 25. test_create_slot_returns_422_for_invalid_portions
**Priority:** Medium
**Given:**
- User is authenticated
- Request body with portions: 0 or portions: 25
**When:** POST /api/meal-slots
**Then:**
- Status: 422 Unprocessable Entity
- Body: {"detail": "portions must be between 1 and 20"}
**Related Requirement:** spec.md "Portion Management"

#### 26. test_create_slot_uses_default_portions_when_not_provided
**Priority:** Medium
**Given:**
- User is authenticated with profile.portions_count = 4
- Request body without portions field
**When:** POST /api/meal-slots
**Then:**
- Status: 201 Created
- Created slot has portions = 4
**Related Requirement:** spec.md "Default portions from user profile"

### PUT /api/meal-slots/{slot_id} (Replace Slot) (5 tests)

#### 27. test_update_slot_returns_200_with_updated_slot
**Priority:** Critical
**Given:**
- User is authenticated
- User has slot with id "slot-1"
- Request body: {"recipe_id": "52773", "recipe_name": "New Recipe", ...}
**When:** PUT /api/meal-slots/slot-1
**Then:**
- Status: 200 OK
- Body: Updated MealSlotResponse
- Database reflects changes
**Related Requirement:** spec.md "Replace: Open recipe selection modal"

#### 28. test_update_slot_returns_401_without_auth
**Priority:** Critical
**Given:** No authentication token
**When:** PUT /api/meal-slots/slot-1
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "RLS policy"

#### 29. test_update_slot_returns_404_for_nonexistent_slot
**Priority:** High
**Given:** User is authenticated
**When:** PUT /api/meal-slots/nonexistent-id
**Then:**
- Status: 404 Not Found
- Body: {"detail": "Meal slot not found"}
**Related Requirement:** spec.md "Slot Actions"

#### 30. test_update_slot_returns_403_for_other_user_slot
**Priority:** Critical
**Given:**
- User A is authenticated
- Slot "slot-1" belongs to User B
**When:** PUT /api/meal-slots/slot-1
**Then:**
- Status: 403 Forbidden or 404 Not Found (per RLS)
**Related Requirement:** spec.md "RLS policy"

#### 31. test_update_slot_allows_portions_update
**Priority:** Medium
**Given:**
- User is authenticated
- User has slot with portions = 4
- Request body: {"portions": 6}
**When:** PUT /api/meal-slots/slot-1
**Then:**
- Status: 200 OK
- Slot portions updated to 6
**Related Requirement:** spec.md "Allow adjusting portions"

### DELETE /api/meal-slots/{slot_id} (Delete Slot) (4 tests)

#### 32. test_delete_slot_returns_204_on_success
**Priority:** Critical
**Given:**
- User is authenticated
- User has slot with id "slot-1"
**When:** DELETE /api/meal-slots/slot-1
**Then:**
- Status: 204 No Content
- Slot removed from database
**Related Requirement:** spec.md "Delete: Clear slot"

#### 33. test_delete_slot_returns_401_without_auth
**Priority:** Critical
**Given:** No authentication token
**When:** DELETE /api/meal-slots/slot-1
**Then:**
- Status: 401 Unauthorized
**Related Requirement:** spec.md "RLS policy"

#### 34. test_delete_slot_returns_404_for_nonexistent_slot
**Priority:** High
**Given:** User is authenticated
**When:** DELETE /api/meal-slots/nonexistent-id
**Then:**
- Status: 404 Not Found
**Related Requirement:** spec.md "Slot Actions"

#### 35. test_delete_slot_returns_403_for_other_user_slot
**Priority:** Critical
**Given:**
- User A is authenticated
- Slot "slot-1" belongs to User B
**When:** DELETE /api/meal-slots/slot-1
**Then:**
- Status: 403 Forbidden or 404 Not Found (per RLS)
**Related Requirement:** spec.md "RLS policy"

### GET /api/meal-slots/recent (Recent Recipes) (3 tests)

#### 36. test_get_recent_returns_200_with_recipes
**Priority:** High
**Given:**
- User is authenticated
- User has added 15 recipes to slots over time
**When:** GET /api/meal-slots/recent
**Then:**
- Status: 200 OK
- Body: Array of 10 most recent unique recipes
- Ordered by most recently added
**Related Requirement:** spec.md "Recent tab: Display last 10 recipes"

#### 37. test_get_recent_returns_empty_for_new_user
**Priority:** Medium
**Given:**
- User is authenticated
- User has never added any slots
**When:** GET /api/meal-slots/recent
**Then:**
- Status: 200 OK
- Body: Empty array []
**Related Requirement:** spec.md "Recent recipes"

#### 38. test_get_recent_excludes_duplicates
**Priority:** Medium
**Given:**
- User has added same recipe "52772" to 5 different slots
**When:** GET /api/meal-slots/recent
**Then:**
- Recipe "52772" appears only once in response
**Related Requirement:** spec.md "Last 10 recipes user has added"

---

## Mobile UI Layer (30 tests)

### MealSlotCard Component (8 tests)

#### 39. test_meal_slot_card_empty_renders_plus_icon
**Priority:** Critical
**Given:** MealSlotCard with slot = null, mealType = "dejeuner"
**When:** Component renders
**Then:**
- Shows dashed border
- Displays "+" icon
- Shows "Dejeuner" label
**Related Requirement:** spec.md "Empty state: Dashed border, + icon"

#### 40. test_meal_slot_card_filled_renders_recipe_info
**Priority:** Critical
**Given:** MealSlotCard with slot = {recipe_name: "Teriyaki Chicken", recipe_thumbnail: "https://...", portions: 4}
**When:** Component renders
**Then:**
- Shows recipe image (56x56)
- Shows recipe name (truncated if long)
- Shows portion badge "4"
**Related Requirement:** spec.md "Filled state: Recipe image, name, portion badge"

#### 41. test_meal_slot_card_empty_calls_onAdd_on_press
**Priority:** Critical
**Given:** MealSlotCard with slot = null, onAdd = jest.fn()
**When:** User taps the card
**Then:** onAdd callback is invoked
**Related Requirement:** spec.md "Opens when user taps empty slot"

#### 42. test_meal_slot_card_filled_shows_action_menu_on_long_press
**Priority:** High
**Given:** MealSlotCard with filled slot
**When:** User long-presses the card
**Then:** Action menu appears with "Voir", "Remplacer", "Supprimer" options
**Related Requirement:** spec.md "Filled slot actions via long-press menu"

#### 43. test_meal_slot_card_action_view_navigates_to_recipe
**Priority:** High
**Given:** MealSlotCard with slot.recipe_id = "52772", action menu open
**When:** User taps "Voir"
**Then:** router.push("/recipe/52772") is called
**Related Requirement:** spec.md "View: Navigate to recipe detail screen"

#### 44. test_meal_slot_card_action_replace_calls_onReplace
**Priority:** High
**Given:** MealSlotCard with slot, onReplace = jest.fn()
**When:** User taps "Remplacer" in action menu
**Then:** onReplace callback is invoked with slot
**Related Requirement:** spec.md "Replace: Open recipe selection modal"

#### 45. test_meal_slot_card_action_delete_shows_confirmation
**Priority:** High
**Given:** MealSlotCard with slot
**When:** User taps "Supprimer" in action menu
**Then:** Confirmation dialog appears with "Confirmer" and "Annuler" buttons
**Related Requirement:** spec.md "Delete: Clear slot with confirmation dialog"

#### 46. test_meal_slot_card_minimum_height_48px
**Priority:** Low
**Given:** MealSlotCard (empty or filled)
**When:** Component renders
**Then:** Card has minimum height of 48px
**Related Requirement:** spec.md "Touch-friendly slot cards (minimum 48px)"

### WeekNavigator Component (6 tests)

#### 47. test_week_navigator_displays_current_week_by_default
**Priority:** Critical
**Given:** WeekNavigator mounts on 2026-01-08 (Wednesday)
**When:** Component renders
**Then:**
- Header shows "06 Jan - 12 Jan 2026" (current week)
- Week starts from Monday
**Related Requirement:** spec.md "Current week is default view"

#### 48. test_week_navigator_previous_button_disabled_on_current_week
**Priority:** High
**Given:** WeekNavigator showing current week
**When:** Component renders
**Then:** Previous week button is disabled (not pressable, visually grayed)
**Related Requirement:** spec.md "Disable Previous button when on current week"

#### 49. test_week_navigator_next_button_navigates_forward
**Priority:** High
**Given:** WeekNavigator showing current week
**When:** User taps next week button
**Then:**
- Week advances by 7 days
- onWeekChange callback called with new week start date
**Related Requirement:** spec.md "Next week buttons in header"

#### 50. test_week_navigator_next_button_disabled_at_4_weeks_ahead
**Priority:** High
**Given:** WeekNavigator showing week 4 weeks ahead
**When:** Component renders
**Then:** Next week button is disabled
**Related Requirement:** spec.md "Disable Next button when 4 weeks ahead"

#### 51. test_week_navigator_allows_4_weeks_navigation
**Priority:** Medium
**Given:** WeekNavigator showing current week
**When:** User taps next button 4 times
**Then:** Successfully navigates to week 4, then next button disabled
**Related Requirement:** spec.md "Up to 4 weeks ahead"

#### 52. test_week_navigator_previous_enables_after_forward_navigation
**Priority:** Medium
**Given:** WeekNavigator showing week 2 ahead
**When:** Component renders
**Then:** Previous button is enabled and navigates back
**Related Requirement:** spec.md "Previous/Next week buttons"

### RecipeSelectionModal Component (8 tests)

#### 53. test_recipe_selection_modal_renders_three_tabs
**Priority:** Critical
**Given:** RecipeSelectionModal is open
**When:** Component renders
**Then:** Shows 3 tabs: "Favoris", "Recherche", "Recents"
**Related Requirement:** spec.md "Three tabs"

#### 54. test_recipe_selection_modal_favorites_tab_shows_favorites
**Priority:** Critical
**Given:**
- RecipeSelectionModal open
- User has 5 favorite recipes
**When:** "Favoris" tab is selected
**Then:** Displays 5 recipe cards from favorites
**Related Requirement:** spec.md "Favorites tab: Reuse favorites list"

#### 55. test_recipe_selection_modal_search_tab_performs_search
**Priority:** High
**Given:** RecipeSelectionModal open, "Recherche" tab selected
**When:** User types "chicken" and submits
**Then:**
- Loading indicator shows
- Recipe results from TheMealDB appear
**Related Requirement:** spec.md "Search tab: Reuse TheMealDB search"

#### 56. test_recipe_selection_modal_recents_tab_shows_recent_recipes
**Priority:** High
**Given:**
- RecipeSelectionModal open
- User has 8 recent recipes
**When:** "Recents" tab is selected
**Then:** Displays 8 recent recipe cards
**Related Requirement:** spec.md "Recent tab"

#### 57. test_recipe_selection_modal_selection_closes_modal
**Priority:** Critical
**Given:** RecipeSelectionModal open with recipes displayed
**When:** User taps on a recipe
**Then:**
- Modal closes
- onSelect callback invoked with selected recipe
**Related Requirement:** spec.md "Single recipe selection closes modal"

#### 58. test_recipe_selection_modal_close_button_works
**Priority:** Medium
**Given:** RecipeSelectionModal open
**When:** User taps close/X button
**Then:** Modal closes without selection
**Related Requirement:** spec.md "Recipe Selection Modal"

#### 59. test_recipe_selection_modal_empty_favorites_shows_message
**Priority:** Medium
**Given:** RecipeSelectionModal open, user has no favorites
**When:** "Favoris" tab selected
**Then:** Shows empty state message "Aucun favori"
**Related Requirement:** spec.md "Favorites tab"

#### 60. test_recipe_selection_modal_empty_recents_shows_message
**Priority:** Medium
**Given:** RecipeSelectionModal open, user has no recent recipes
**When:** "Recents" tab selected
**Then:** Shows empty state message "Aucune recette recente"
**Related Requirement:** spec.md "Recent tab"

### WeeklyPlanningScreen (6 tests)

#### 61. test_weekly_planning_screen_renders_14_slots
**Priority:** Critical
**Given:** WeeklyPlanningScreen mounts
**When:** Screen renders
**Then:** Displays 14 meal slots (7 days x 2 meals)
**Related Requirement:** spec.md "Total of 14 meal slots per week"

#### 62. test_weekly_planning_screen_fetches_slots_on_mount
**Priority:** Critical
**Given:** WeeklyPlanningScreen mounts
**When:** useEffect runs
**Then:** fetchWeekSlots called with current week start date
**Related Requirement:** spec.md "Fetch week data on navigation"

#### 63. test_weekly_planning_screen_refetches_on_week_change
**Priority:** High
**Given:** WeeklyPlanningScreen showing current week
**When:** User navigates to next week
**Then:** fetchWeekSlots called with new week start date
**Related Requirement:** spec.md "Fetch week data on navigation"

#### 64. test_weekly_planning_screen_shows_loading_state
**Priority:** Medium
**Given:** WeeklyPlanningScreen, slots are loading
**When:** Component renders
**Then:** Shows loading indicator/skeleton
**Related Requirement:** spec.md "Optimistic UI updates"

#### 65. test_weekly_planning_screen_shows_error_state
**Priority:** Medium
**Given:** WeeklyPlanningScreen, API call failed
**When:** Error state is active
**Then:** Shows error message with retry button
**Related Requirement:** spec.md "Rollback on error"

#### 66. test_weekly_planning_screen_days_labeled_correctly
**Priority:** Low
**Given:** WeeklyPlanningScreen renders
**When:** Examining day labels
**Then:** Days show "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"
**Related Requirement:** spec.md "Lundi through Dimanche"

### MealPlanningStore (Zustand) (6 tests)

#### 67. test_store_fetch_week_slots_updates_state
**Priority:** Critical
**Given:** Empty store
**When:** fetchWeekSlots("2026-01-06") called
**Then:**
- loading becomes true then false
- slots state updated with API response
- error is null
**Related Requirement:** spec.md "State management"

#### 68. test_store_add_slot_optimistic_update
**Priority:** Critical
**Given:** Store with empty slots
**When:** addSlot(slotData) called
**Then:**
- Slot immediately added to state (optimistic)
- API call made
- If successful, slot ID updated from response
**Related Requirement:** spec.md "Optimistic UI updates"

#### 69. test_store_add_slot_rollback_on_error
**Priority:** Critical
**Given:** Store, API will fail
**When:** addSlot(slotData) called and API fails
**Then:**
- Optimistic slot is removed from state
- error state is set
**Related Requirement:** spec.md "Rollback on error"

#### 70. test_store_delete_slot_optimistic_update
**Priority:** High
**Given:** Store with slot "slot-1"
**When:** deleteSlot("slot-1") called
**Then:**
- Slot immediately removed from state
- API call made
- If error, slot restored to state
**Related Requirement:** spec.md "Optimistic UI updates with rollback"

#### 71. test_store_replace_slot_updates_recipe
**Priority:** High
**Given:** Store with slot containing recipe A
**When:** replaceSlot("slot-1", newRecipeData) called
**Then:**
- Slot recipe updated to new recipe
- API call made
**Related Requirement:** spec.md "Replace: swap recipe"

#### 72. test_store_clears_on_logout
**Priority:** Low
**Given:** Store with meal slots data
**When:** Auth logout occurs
**Then:** Store is reset to initial state
**Related Requirement:** spec.md "Data Persistence"

---

## Integration/E2E Tests (8 tests)

### Full User Flow (4 tests)

#### 73. test_e2e_user_adds_recipe_to_empty_slot
**Priority:** Critical
**Given:**
- User is logged in
- Weekly planning screen is displayed
- Monday Dejeuner slot is empty
**When:**
1. User taps empty slot
2. Recipe selection modal opens
3. User selects "Favoris" tab
4. User taps on favorite recipe
**Then:**
- Modal closes
- Slot shows selected recipe with thumbnail and name
- Recipe persisted in database
**Related Requirement:** spec.md "Add recipes to meal slots"

#### 74. test_e2e_user_replaces_existing_recipe
**Priority:** Critical
**Given:**
- User has "Recipe A" in Monday Dejeuner slot
**When:**
1. User long-presses the slot
2. User taps "Remplacer"
3. User searches for "Recipe B"
4. User selects "Recipe B"
**Then:**
- Slot now shows "Recipe B"
- Database updated
**Related Requirement:** spec.md "Replace with different recipe"

#### 75. test_e2e_user_deletes_planned_meal
**Priority:** Critical
**Given:**
- User has recipe in Tuesday Diner slot
**When:**
1. User long-presses the slot
2. User taps "Supprimer"
3. User confirms deletion
**Then:**
- Slot becomes empty (shows "+")
- Recipe removed from database
**Related Requirement:** spec.md "Delete/clear the slot"

#### 76. test_e2e_user_navigates_between_weeks
**Priority:** High
**Given:**
- User has different recipes planned for week 1 and week 2
**When:**
1. User views week 1 (sees Recipe A)
2. User taps next week
3. User views week 2 (sees Recipe B)
4. User taps previous week
**Then:**
- Each week displays its own correct recipes
- Data is consistent
**Related Requirement:** spec.md "Week navigation"

### Offline/Error Scenarios (2 tests)

#### 77. test_e2e_optimistic_rollback_on_network_error
**Priority:** High
**Given:**
- User is on weekly planning screen
- Network connection fails after UI update
**When:** User adds recipe to slot
**Then:**
- Recipe briefly appears (optimistic)
- Error message displayed
- Slot reverts to empty state
**Related Requirement:** spec.md "Optimistic UI updates with rollback"

#### 78. test_e2e_handles_expired_token_gracefully
**Priority:** Medium
**Given:**
- User's auth token expires mid-session
**When:** User tries to add recipe to slot
**Then:**
- Token refresh attempted
- If successful, operation completes
- If failed, user redirected to login
**Related Requirement:** spec.md "Reuse existing ApiClient with automatic token refresh"

### Data Consistency (2 tests)

#### 79. test_e2e_recent_recipes_updated_after_adding_slot
**Priority:** Medium
**Given:**
- User has 5 recent recipes
- Recipe "New Recipe" is not in recents
**When:** User adds "New Recipe" to a slot
**Then:**
- "New Recipe" appears in Recents tab
- Recents limited to 10 items
**Related Requirement:** spec.md "Last 10 recipes user has added"

#### 80. test_e2e_slots_persist_after_app_restart
**Priority:** Low
**Given:**
- User has 3 recipes planned for the week
**When:** User closes and reopens app
**Then:**
- All 3 planned recipes still visible
- Data loaded from Supabase
**Related Requirement:** spec.md "Data persisted in Supabase"

---

## Test Dependencies

1. **Database layer tests** must pass before API layer tests (schema must exist)
2. **API layer tests** must pass before Mobile UI tests (endpoints must work)
3. **MealSlotCard component tests** before WeeklyPlanningScreen tests
4. **MealPlanningStore tests** before integration tests
5. **Authentication system** must be functional for all authenticated tests

## Test Data Requirements

### Test Users
- User A: test_user_a@example.com with 5 favorites, profile.portions_count = 4
- User B: test_user_b@example.com for RLS cross-user tests

### Test Recipes
- Recipe 52772: "Teriyaki Chicken Casserole" with thumbnail
- Recipe 52773: "Honey Teriyaki Salmon" with thumbnail
- Recipe 52774: "Beef Stroganoff" with thumbnail

### Test Meal Slots
- Pre-populated slots for week 2026-01-06 for User A
- Empty week 2026-01-13 for empty state tests

### Mock API Responses
- TheMealDB search results for "chicken"
- Favorites list from existing FavoritesService
- Recent recipes list (10 items)

## Out of Scope

Tests explicitly NOT included in this plan:
- **Performance/load testing** - Requires dedicated infrastructure
- **Drag and drop** - Explicitly out of scope per spec
- **Weekly templates** - Explicitly out of scope per spec
- **Breakfast slot** - Explicitly out of scope per spec
- **Planning beyond 4 weeks** - Explicitly out of scope per spec
- **Multi-recipe per slot** - Explicitly out of scope per spec
- **Shopping list generation** - Separate feature per spec
- **Browser compatibility** - Mobile app only
- **iPad/tablet specific layouts** - Deferred
