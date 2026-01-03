# Spec Requirements: Weekly Meal Planning

## Initial Description

**Weekly Meal Planning** - Build the weekly planning interface (Lundi-Dimanche) with dejeuner/diner slots. Users can add recipes to specific meal slots via a selection modal. Planning data saved per user in Supabase. Effort: L

## Requirements Discussion

### First Round Questions

**Q1:** Week structure - Should the week be fixed (Monday to Sunday) or allow user customization of start day?
**Answer:** Fixed week from Monday (Lundi) to Sunday (Dimanche). No user customization needed for v1.

**Q2:** Meals per day - Should we include all three meals (breakfast, lunch, dinner) or focus on lunch and dinner only?
**Answer:** Lunch (dejeuner) and dinner (diner) only. No breakfast in v1.

**Q3:** Recipes per slot - Can users assign multiple recipes to a single meal slot, or is it one recipe per slot?
**Answer:** Single recipe per meal slot (1 recipe max per slot).

**Q4:** Recipe selection method - How should users select recipes for a slot?
**Answer:** Users can select recipes from three sources:
- Favorites (Mes favoris)
- Search (recherche)
- Recent recipes (recently viewed/used recipes)

**Q5:** Planning horizon - How far in advance can users plan meals?
**Answer:** Limited to 4 weeks maximum into the future. Users cannot plan beyond 4 weeks ahead.

**Q6:** Slot actions - What actions can users perform on a filled meal slot?
**Answer:** Three actions available:
- View recipe details (voir)
- Replace with different recipe (remplacer)
- Delete/clear the slot (supprimer)

**Q7:** Portion management - How should portions be handled per slot?
**Answer:** Portions are stored per slot, based on household size from user profile. This enables accurate shopping list generation later.

**Q8:** What should explicitly be excluded from v1 scope?
**Answer:** Out of scope for v1:
- Drag & drop to move recipes between slots
- Planning templates (weekly templates to reuse)
- Multi-recipe per slot (combo meals)

### Existing Code to Reference

No similar existing features identified for reference during requirements gathering.

Note: The codebase likely has existing patterns from:
- Recipe Favorites feature (for favorite recipe selection UI)
- Recipe Browsing feature (for recipe search and display)

These should be explored by the spec-writer for reusable components.

### Follow-up Questions

No follow-up questions were needed. All requirements were clearly specified in the initial response.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - no visual files were found in the planning/visuals/ folder.

## Requirements Summary

### Functional Requirements

**Weekly Calendar Interface:**
- Display a 7-day week view (Lundi through Dimanche)
- Each day shows 2 meal slots: Dejeuner (lunch) and Diner (dinner)
- Total of 14 meal slots per week
- Week navigation limited to current week + 4 weeks ahead

**Recipe Selection Modal:**
- Triggered when user taps an empty slot or "replace" on filled slot
- Three tabs/sections for recipe selection:
  - Favorites: Display user's saved favorite recipes
  - Search: Search TheMealDB/recipe catalog
  - Recent: Show recently viewed or used recipes
- Single recipe selection per modal interaction

**Slot Management:**
- Empty slot: Tap to open recipe selection modal
- Filled slot displays:
  - Recipe thumbnail/image
  - Recipe name
  - Portion count
- Filled slot actions (via swipe or menu):
  - View: Navigate to full recipe detail
  - Replace: Open recipe selection modal
  - Delete: Clear the slot (with confirmation)

**Portion Handling:**
- Default portions based on user's household size (from profile)
- Portions stored per individual slot
- Ability to adjust portions per slot (for shopping list accuracy)

**Data Persistence:**
- All meal plan data saved to Supabase per user
- Weekly plans identifiable by week start date
- Support for partial week planning (not all slots required)

### Reusability Opportunities

Based on existing roadmap features that should be implemented before this:
- Recipe card component from Recipe Browsing feature
- Favorite toggle/display from Recipe Favorites feature
- User profile/household size from User Profile & Preferences
- Recipe detail navigation patterns

### Scope Boundaries

**In Scope:**
- Weekly calendar view (Mon-Sun, fixed)
- Lunch + Dinner slots only (2 per day, 14 per week)
- Recipe selection modal with favorites, search, recent tabs
- View/Replace/Delete actions on filled slots
- Portion storage per slot
- Navigation up to 4 weeks ahead
- Supabase persistence of meal plans

**Out of Scope:**
- Drag & drop reordering of meals
- Weekly planning templates
- Multiple recipes per slot
- Breakfast slot
- Custom week start day
- Planning beyond 4 weeks
- Shopping list generation (separate roadmap item)
- AI-powered suggestions (separate roadmap item)

### Technical Considerations

**Frontend (React Native with Expo Router):**
- New screen: Weekly planning calendar view
- New modal: Recipe selection with tabbed interface
- New components: Meal slot card, Week navigator
- State management for current week and planned meals

**Backend (FastAPI):**
- New endpoints for CRUD operations on meal plans
- Endpoints for fetching recent recipes
- Query patterns for week-based data retrieval

**Database (Supabase):**
- New table: `meal_plans` or similar
- Schema to support: user_id, date, meal_type (lunch/dinner), recipe_id, portions
- Indexes on user_id and date for efficient week queries

**Integration Points:**
- Recipe Favorites: Access user's favorited recipes
- Recipe Browsing: Search functionality reuse
- User Profile: Household size for default portions
- Future: Shopping List will read from meal plans
