# Requirements: Portion Adjustment

## Feature Overview
Enable users to adjust portion sizes when viewing recipes and planning meals. Ingredient quantities should scale accordingly in the recipe detail view. Meal slots should default to the user's household size but allow per-slot overrides.

## User Needs
1. **See scaled ingredients** - When viewing a recipe, users want to see ingredient quantities adjusted for their household size
2. **Flexible portions per meal** - Different meals may need different portions (guests, leftovers, etc.)
3. **Smart defaults** - Portions should default to user's saved preference to minimize clicks

## Functional Requirements

### FR1: Recipe Detail Portions Selector
- Add stepper control (- N +) below recipe title in recipe detail view
- Default value: user's `portions_count` from preferences (or 2 if not set)
- Range: 1-20 portions
- Position: between title/meta section and ingredients section

### FR2: Scaled Ingredient Display
- Display adjusted quantities in real-time as user changes portions
- Use `_multiply_quantity` logic from shopping_list_service.py
- Keep original units (no unit conversion)
- Handle non-numeric measures gracefully (show unchanged)

### FR3: Meal Slot Creation Default
- When creating a meal slot, pre-fill portions from user's `portions_count`
- Already supported: MealSlotCreate accepts optional `portions` field
- Pass portions to createSlot API call

### FR4: Meal Slot Edit
- Add "Edit portions" action to SlotActionMenu
- Show modal with portions stepper and confirm button
- Call updateSlot API with new portions
- Show warning that shopping list may need regeneration

## Non-Functional Requirements
- Portion calculations happen client-side (no API calls for scaling)
- Stepper should be touch-friendly (48px min touch target per design system)
- Optimistic updates for slot edits (existing pattern in meal-planning store)

## Constraints
- Recipe original portions unknown (TheMealDB does not provide this)
- Assume all recipes are for 1 portion as base
- No AI-based intelligent scaling
- No unit conversion (1000g stays 1000g, not 1kg)

## Dependencies
- User preferences store (portions_count)
- Meal planning store (updateSlot action)
- Existing PortionSelector component from preferences

## Acceptance Criteria
1. Recipe detail shows portions selector defaulting to user preference
2. Ingredient quantities update immediately when portions change
3. New meal slots use user's portions_count as default
4. Existing slots can have portions edited via action menu
5. Shopping list warning shown when editing slot portions
