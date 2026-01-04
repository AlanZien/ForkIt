# Specification: Weekly Meal Planning

## Goal

Enable users to plan their weekly meals by assigning recipes to lunch and dinner slots across a 7-day week (Monday-Sunday), with data persisted in Supabase and portions stored per slot based on household size.

## User Stories

- As a user, I want to view my weekly meal plan with 14 slots (2 per day) so that I can see what I have planned for the week
- As a user, I want to add recipes to meal slots from my favorites, search, or recent recipes so that I can quickly fill my plan

## Specific Requirements

**Weekly Calendar View**
- Display 7-day week from Lundi (Monday) to Dimanche (Sunday)
- Each day shows 2 meal slots: Dejeuner (lunch) and Diner (dinner)
- Week navigation arrows to move between weeks (current week + up to 4 weeks ahead)
- Empty slots display a "+" button to add a recipe
- Filled slots display recipe thumbnail, name, and portion count

**Week Navigation**
- Current week is default view on screen load
- Previous/Next week buttons in header
- Disable "Previous" button when on current week
- Disable "Next" button when 4 weeks ahead from current week
- Week is identified by its Monday date (ISO week format)

**Recipe Selection Modal**
- Opens when user taps empty slot or "Replace" action on filled slot
- Three tabs: "Favoris" (favorites), "Recherche" (search), "Recents" (recent)
- Favorites tab: Reuse favorites list from existing FavoritesService
- Search tab: Reuse TheMealDB search from existing RecipesService
- Recent tab: Display last 10 recipes user has added to any slot
- Single recipe selection closes modal and assigns to slot

**Meal Slot Card Component**
- Two states: empty and filled
- Empty state: Dashed border, "+" icon, meal type label (Dejeuner/Diner)
- Filled state: Recipe image (56x56), recipe name (truncated), portion badge
- Filled slot actions via long-press menu or swipe: "Voir" (view), "Remplacer" (replace), "Supprimer" (delete)

**Slot Actions**
- View: Navigate to recipe detail screen (existing /recipe/[id] route)
- Replace: Open recipe selection modal, replace current recipe on selection
- Delete: Clear slot with confirmation dialog, remove from database

**Portion Management**
- Default portions from user profile preferences.portions_count
- Store portions per individual slot in database
- Optional: Allow adjusting portions via stepper (+/-) in edit mode
- Portions displayed as badge on meal slot card

**Data Persistence (Supabase)**
- New table: meal_slots with user_id, date, meal_type, recipe_id, recipe_name, recipe_thumbnail, portions
- User can only access their own meal_slots (RLS policy)
- Fetch week data on navigation (7 days of slots in one query)
- Optimistic UI updates with rollback on error

## Visual Design

No visual mockups provided. Follow design-system.md specifications:
- Use "Planning Card" style from design system (white background, 1px border, 12px radius)
- Primary color (#14B8A6) for active states and buttons
- Use existing Ionicons for actions (calendar, plus, trash, refresh icons)
- Touch-friendly slot cards (minimum 48px height per slot)
- Horizontal scrollable week view or vertical stacked days layout

## Existing Code to Leverage

**backend/app/services/favorites_service.py**
- Follow same service class pattern with Supabase client initialization
- Use identical CRUD operation patterns (select, insert, delete with user_id filter)
- Copy error handling and response mapping approach

**backend/app/routes/favorites.py**
- Use same dependency injection pattern (get_current_user, get_service)
- Follow identical route structure with /api prefix
- Use same status codes (200, 201, 204, 400, 401)

**mobile/stores/favorites.ts**
- Follow Zustand store pattern with initialState, loading states, error handling
- Use same async action structure with try/catch and state updates
- Implement optimistic updates with rollback pattern

**mobile/services/api.ts**
- Use existing ApiClient with automatic token refresh
- Follow same endpoint calling pattern (api.get, api.post, api.delete)
- Reuse for all meal planning API calls

**mobile/types/favorite.ts**
- Follow same type structure for MealSlot, MealSlotCreate, MealSlotResponse
- Match naming conventions (snake_case for API fields)

## Out of Scope

- Drag and drop to reorder/move recipes between slots
- Weekly planning templates to save and reuse
- Multiple recipes per single slot (combo meals)
- Breakfast slot (only lunch and dinner)
- Custom week start day (fixed Monday start)
- Planning beyond 4 weeks into the future
- Shopping list generation from meal plan (separate feature)
- AI-powered meal suggestions (separate feature)
- Meal plan sharing with other users
- Recurring meal patterns (same meal every week)
