# Specification: Shopping List Generation

## Goal
Generate a consolidated shopping list from the current week's meal plan, grouping ingredients by category with aggregated quantities, and provide a checkable list UI with cross-device persistence.

## User Stories
- As a user, I want to generate a shopping list from my weekly meal plan so that I can buy all ingredients needed for my planned meals
- As a user, I want to check off items as I shop so that I can track my progress in the store

## Specific Requirements

**Shopping List Generation Endpoint**
- Create `POST /api/shopping-list/generate` endpoint to generate list from current week's meal slots
- Fetch all meal slots for the authenticated user's current week using existing `MealSlotsService.get_week_slots()`
- For each meal slot, fetch recipe details from TheMealDB using `themealdb_client.get_by_id(recipe_id)`
- Extract ingredients and measures from TheMealDB response (strIngredient1-20, strMeasure1-20)
- Multiply quantities by the `portions` field from each meal slot
- Return generated list with items grouped by category

**Ingredient Aggregation Logic**
- Combine identical ingredients using case-insensitive exact string matching
- Sum quantities for matching ingredients (e.g., "2 onions" + "1 onion" = "3 onions")
- Handle mixed quantity formats gracefully (keep original format strings when aggregation not possible)
- Parse common quantity patterns: "2", "2 cups", "200g", "1/2 cup"
- When quantities cannot be parsed/combined, concatenate as comma-separated string

**Ingredient Category Mapping**
- Create static `INGREDIENT_CATEGORIES` mapping dictionary in `backend/app/services/shopping_list_service.py`
- Categories: Legumes, Viandes, Poissons, Produits laitiers, Epicerie, Boissons, Surgeles, Autres
- Map common ingredients to categories (leverage patterns from existing `ingredient_mappings.py`)
- Default unmapped ingredients to "Autres" category
- Return items sorted by category, then alphabetically within category

**Shopping List Persistence Schema**
- Create `shopping_list_items` Supabase table with columns: id (uuid), user_id (uuid FK), ingredient_name (text), quantity (text), category (text), is_checked (boolean), week_start (date), created_at, updated_at
- Add RLS policies: users can only access their own items
- Enable unique constraint on (user_id, ingredient_name, week_start) to prevent duplicates
- Store `week_start` (Monday date) to scope items to a specific week

**Check State Persistence API**
- Create `PUT /api/shopping-list/items/{item_id}/check` endpoint to toggle checked state
- Create `PUT /api/shopping-list/uncheck-all` endpoint for "Tout decocher" action
- Create `DELETE /api/shopping-list` endpoint to clear list before regeneration
- All endpoints require authentication and filter by `user_id`

**Regeneration Flow**
- "Regenerer" action: DELETE existing items for current week, then POST generate
- Regeneration intentionally loses all check states (per requirements)
- No automatic regeneration when meal plan changes - manual only
- Show confirmation dialog before regeneration to warn about losing check states

**Shopping List Store (Zustand)**
- Create `mobile/stores/shopping-list.ts` following `meal-planning.ts` patterns
- State: items (Map keyed by id), isLoading, isGenerating, error
- Actions: generateList(), toggleItem(id), uncheckAll(), getItemsByCategory()
- Use optimistic updates with rollback for check/uncheck operations
- Include `lastGeneratedAt` timestamp to show when list was generated

**Shopping List Screen UI**
- Add "Courses" tab to bottom navigation (shopping-cart icon, position 4)
- Create `mobile/app/(tabs)/shopping.tsx` screen
- Display items grouped by category with collapsible sections
- Show category header with item count (e.g., "Legumes (5)")
- Each item row: checkbox, ingredient name, quantity on right

**Shopping List Item Component**
- Create `mobile/components/shopping-list/ShoppingListItem.tsx`
- Checkbox left-aligned, tapping anywhere on row toggles check
- Checked items show strikethrough text and muted color
- Smooth animation on check/uncheck transition
- Haptic feedback on toggle (use Expo Haptics)

## Visual Design

Visual design follows the existing design system patterns:
- Card containers with white background, rounded corners (12px), subtle border
- Category headers use H4 typography (16px, semibold, #1F2937)
- Item text uses body typography (16px, regular)
- Checked items: text color #9CA3AF, strikethrough decoration
- Checkbox uses primary color (#14B8A6) when checked
- "Regenerer" button: secondary style (coral #FF8A65)
- "Tout decocher" button: ghost style (text only, primary color)
- Empty state with illustration and "Generez votre liste" CTA

## Existing Code to Leverage

**MealSlotsService pattern**
- Follow same service class structure with `__init__` using `get_supabase_admin()`
- Use same query patterns for user-scoped data access
- Apply same validation and error handling patterns
- Leverage `get_week_slots()` to fetch current week's meal data

**TheMealDB Client**
- Use existing `themealdb_client.get_by_id(meal_id)` to fetch recipe details
- Parse strIngredient1-20 and strMeasure1-20 from response
- Follow async/await patterns established in client

**Ingredient Mappings Structure**
- Reference `DIETARY_EXCLUSIONS` and `ALLERGEN_KEYWORDS` dict structure for category mapping
- Use similar pattern: `Dict[CategoryType, List[str]]` for ingredient-to-category lookup
- Can reuse ingredient name lists as reference for categorization

**Meal Planning Store Pattern**
- Follow Zustand store structure from `meal-planning.ts`
- Implement optimistic updates with rollback
- Use same error handling and loading state patterns
- Follow `generateSlotKey` pattern for Map-based item storage

**MealSlotCard Component Pattern**
- Follow similar component structure for ShoppingListItem
- Use same styling approach with StyleSheet.create
- Apply same accessibility patterns (accessibilityRole, accessibilityLabel)

## Out of Scope
- Export or share shopping list functionality
- Manual addition of custom items not from recipes
- Editing quantities after list generation
- Multi-week shopping list spanning multiple weeks
- Automatic list regeneration when meal plan changes
- Fuzzy/similar ingredient matching (e.g., "chicken" vs "poulet")
- Ingredient substitution suggestions
- Price estimation or store integration
- Offline-first with background sync
- Reordering items within categories
