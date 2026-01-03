# Specification: Portion Adjustment

## Goal
Allow users to adjust portion counts when viewing recipes and editing meal slots, with ingredient quantities scaling in real-time.

## User Stories
- As a user, I want to adjust portions on a recipe so that I can see scaled ingredient quantities for my household size
- As a user, I want my meal slots to default to my household size so that I don't have to adjust portions every time

## Specific Requirements

**Recipe Detail Portions Selector**
- Add PortionSelector component between title section and ingredients section
- Default value comes from user's `portions_count` preference (fallback to 2)
- Local state only - no API call when changing portions
- Label: "Portions" displayed above or beside the stepper
- Use existing PortionSelector from `mobile/components/preferences/PortionSelector.tsx`

**Real-time Ingredient Scaling**
- Create `scaleQuantity(measure: string, portions: number): string` utility function
- Port logic from backend `_multiply_quantity` and `_parse_quantity` methods
- Handle fractions (1/2, 1/4), decimals (1.5), mixed numbers (1 1/2)
- Return original measure unchanged if parsing fails
- Display scaled measures in ingredients list (replace static display)

**Meal Slot Creation with Default Portions**
- In planning.tsx `handleRecipeSelect`, already passes `portions: preferences?.portions_count || 2`
- Verify this is working correctly (no changes needed if already implemented)

**Meal Slot Edit Modal**
- Create `EditPortionsModal` component with PortionSelector
- Show current portions value, allow adjustment, confirm/cancel buttons
- Add "Modifier les portions" action to SlotActionMenu (between "Remplacer" and "Supprimer")
- Call `updateSlot(date, mealType, { portions: newValue })` on confirm
- Show info message: "La liste de courses devra etre regeneree"

**SlotActionMenu Enhancement**
- Add new action item for "Modifier les portions" with icon `create-outline`
- Pass slot portions to EditPortionsModal
- Handle onEditPortions callback from parent

## Visual Design
No mockups provided. Follow existing design patterns:
- PortionSelector already styled per design system (48px buttons, teal primary)
- EditPortionsModal follows SlotActionMenu bottom sheet pattern
- Recipe detail section spacing: 24px horizontal padding, 16-24px vertical gaps

## Existing Code to Leverage

**PortionSelector Component** (`mobile/components/preferences/PortionSelector.tsx`)
- Fully functional stepper with min/max bounds, disabled state
- Props: value, onChange, min, max, disabled, style
- Reuse directly in recipe detail and edit modal

**SlotActionMenu Pattern** (`mobile/components/meal-planning/SlotActionMenu.tsx`)
- Bottom sheet modal with action items
- Use same styling for EditPortionsModal
- ActionItem subcomponent can be extracted if needed

**Meal Planning Store** (`mobile/stores/meal-planning.ts`)
- `updateSlot` action already handles portions updates with optimistic update
- No backend changes needed - PUT /api/meal-slots/{date}/{meal_type} accepts portions

**Shopping List Service** (`backend/app/services/shopping_list_service.py`)
- `_multiply_quantity` method (lines 840-859) - port to TypeScript
- `_parse_quantity` method (lines 709-760) - port to TypeScript
- These handle fraction/decimal parsing and multiplication

## Out of Scope
- Unit conversion (e.g., 1000g to 1kg)
- AI-based intelligent scaling based on ingredient type
- Saving "favorite" portion counts per recipe
- Recipe base portions metadata (TheMealDB does not provide)
- Automatic shopping list regeneration when portions change
- Portion adjustment in shopping list view directly
- Bulk edit portions for multiple slots
- Portions history or undo
- Animation when quantities change
- Portion suggestions based on ingredient type
