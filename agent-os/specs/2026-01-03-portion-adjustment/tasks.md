# Task Breakdown: Portion Adjustment

## Overview
Total Tasks: 12
Effort: S (Small)

## Task List

### Utility Layer

#### Task Group 1: Quantity Scaling Utility
**Dependencies:** None

- [x] 1.0 Complete quantity scaling utility
  - [x] 1.1 Write scaleQuantity utility tests
    - Test fraction parsing: "1/2", "1/4", "3/4"
    - Test mixed numbers: "1 1/2", "2 1/4"
    - Test decimals with units: "200g", "2 cups", "1.5 tbsp"
    - Test non-parseable values return unchanged
    - Test multiplication for portions > 1
    - Expected: 6-8 unit tests
  - [x] 1.2 Create scaleQuantity utility function
    - Location: `mobile/utils/scale-quantity.ts`
    - Port `_parse_quantity` logic from `backend/app/services/shopping_list_service.py` (lines 709-760)
    - Port `_multiply_quantity` logic (lines 840-859)
    - Signature: `scaleQuantity(measure: string, portions: number): string`
    - Handle: fractions, mixed numbers, decimals with/without units
    - Return original measure if parsing fails
  - [x] 1.3 Add formatQuantity helper
    - Format floats: whole numbers as int, else 1 decimal
    - Combine value + unit with proper spacing
  - [x] 1.4 Verify utility tests pass
    - Run tests for scale-quantity utility
    - Expected: All unit tests passing

**Acceptance Criteria:**
- scaleQuantity correctly handles all numeric formats
- Non-parseable measures returned unchanged
- All unit tests pass

---

### Recipe Detail Integration

#### Task Group 2: Recipe Detail Portions UI
**Dependencies:** Task Group 1

- [x] 2.0 Complete recipe detail portions feature
  - [x] 2.1 Write RecipeDetailScreen portions tests
    - Test PortionSelector renders with user preference default
    - Test fallback to 2 when no preference
    - Test ingredient quantities update on portion change
    - Expected: 3-4 component tests
  - [x] 2.2 Add PortionSelector to RecipeDetailScreen
    - Import existing `PortionSelector` from `mobile/components/preferences/PortionSelector.tsx`
    - Position: between title/meta section and ingredients section
    - Local state: `portions` initialized from `preferences?.portions_count || 2`
    - Props: `value={portions}`, `onChange={setPortions}`, `min={1}`, `max={20}`
    - Add "Portions" label above selector
  - [x] 2.3 Integrate scaleQuantity in ingredients display
    - Import `scaleQuantity` utility
    - Map over ingredients, scale each measure by current portions
    - Replace static measure display with scaled value
  - [x] 2.4 Verify recipe detail tests pass
    - Expected: All component tests passing
    - Manual verification: changing portions updates ingredient quantities

**Acceptance Criteria:**
- PortionSelector visible in recipe detail view
- Default value matches user preference (or 2)
- Ingredient quantities update in real-time
- No API calls when adjusting portions

---

### Meal Slot Editing

#### Task Group 3: Edit Portions Modal & Menu Integration
**Dependencies:** Task Group 1

- [x] 3.0 Complete meal slot portions editing
  - [x] 3.1 Write EditPortionsModal tests
    - Test modal renders with current slot portions
    - Test confirm calls updateSlot with new portions
    - Test cancel closes without changes
    - Test info message displays
    - Expected: 4 tests
  - [x] 3.2 Create EditPortionsModal component
    - Location: `mobile/components/meal-planning/EditPortionsModal.tsx`
    - Follow SlotActionMenu bottom sheet pattern
    - Props: `visible`, `onClose`, `onConfirm`, `currentPortions`
    - Include PortionSelector with state
    - Confirm and Cancel buttons
    - Info message: "La liste de courses devra etre regeneree"
  - [x] 3.3 Add "Modifier les portions" to SlotActionMenu
    - Add `onEditPortions` callback prop to SlotActionMenuProps
    - Add new ActionItem between "Remplacer" and "Supprimer"
    - Icon: `create-outline`, iconColor: `#8B5CF6` (purple)
    - Label: "Modifier les portions"
  - [x] 3.4 Wire up EditPortionsModal in planning.tsx
    - Add state: `editPortionsModalVisible`, `selectedSlotForEdit`
    - Handle `onEditPortions` from SlotActionMenu
    - On confirm: call `updateSlot(date, mealType, { portions: newValue })`
    - Close modal after update
  - [x] 3.5 Verify meal slot editing tests pass
    - Expected: All EditPortionsModal tests passing
    - Manual verification: editing portions updates slot

**Acceptance Criteria:**
- "Modifier les portions" action visible in SlotActionMenu
- EditPortionsModal opens with current slot portions
- Confirm updates slot via updateSlot action
- Info message warns about shopping list

---

### Verification

#### Task Group 4: Final Validation
**Dependencies:** Task Groups 1-3

- [x] 4.0 Validate complete feature
  - [x] 4.1 Verify meal slot creation default portions
    - Confirm `handleRecipeSelect` in planning.tsx passes `portions: preferences?.portions_count || 2`
    - Verify new slots created with correct default portions
    - No changes needed if already working
  - [x] 4.2 Run all portion-related tests
    - Run utility tests (Task Group 1)
    - Run component tests (Task Groups 2-3)
    - Expected: All tests passing
  - [x] 4.3 Manual end-to-end verification
    - Recipe detail: adjust portions, verify scaled ingredients
    - New slot: verify portions default to preference
    - Existing slot: edit portions via menu, verify update

**Acceptance Criteria:**
- All automated tests pass
- Recipe detail portions selector works correctly
- Meal slot creation uses user's default portions
- Meal slot edit flow works end-to-end

---

## Execution Order

Recommended implementation sequence:
1. **Utility Layer** (Task Group 1) - Core scaling logic, no dependencies
2. **Recipe Detail** (Task Group 2) - Uses utility from Group 1
3. **Meal Slot Editing** (Task Group 3) - Independent of Group 2, uses utility
4. **Final Validation** (Task Group 4) - Validates all groups

## Files to Create/Modify

| File | Action | Task Group |
|------|--------|------------|
| `mobile/utils/scale-quantity.ts` | Create | 1 |
| `mobile/utils/__tests__/scale-quantity.test.ts` | Create | 1 |
| `mobile/app/(tabs)/recipes/[id].tsx` | Modify | 2 |
| `mobile/components/meal-planning/EditPortionsModal.tsx` | Create | 3 |
| `mobile/components/meal-planning/SlotActionMenu.tsx` | Modify | 3 |
| `mobile/app/(tabs)/planning.tsx` | Modify | 3 |

## Existing Code to Reuse

- **PortionSelector**: `mobile/components/preferences/PortionSelector.tsx` - Use directly
- **SlotActionMenu pattern**: `mobile/components/meal-planning/SlotActionMenu.tsx` - Follow for EditPortionsModal
- **updateSlot action**: `mobile/stores/meal-planning.ts` - Already supports portions
- **Python quantity logic**: `backend/app/services/shopping_list_service.py` lines 709-760, 840-859
