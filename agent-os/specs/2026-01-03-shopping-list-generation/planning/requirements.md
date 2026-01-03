# Spec Requirements: Shopping List Generation

## Initial Description
Shopping List Generation - Generer une liste de courses consolidee a partir du planning hebdomadaire. Regrouper les ingredients par categorie, agreger les quantites pour les ingredients en double, et fournir une interface checklist. Effort: M. Depend de #5 Weekly Meal Planning (termine).

Context from roadmap:
- Feature #8 in the ForkIt app
- Depends on Weekly Meal Planning (#5) which is complete
- Need to aggregate ingredients from all recipes in the weekly meal plan
- Group by category (legumes, viandes, epicerie, etc.)
- Provide checkable list UI

## Requirements Discussion

### First Round Questions

**Q1:** Looking at the design mockup, I see the "Liste de courses" shows items with checkboxes and what appears to be quantities. I assume the list should be generated from the current week's meal plan only. Is that correct, or should users be able to select a specific week or date range?
**Answer:** Current week only - The list is generated from the current week's meal plan displayed in the Planning tab.

**Q2:** For ingredient aggregation, I assume we should combine identical ingredients across all meals (e.g., 2 onions from Recipe A + 1 onion from Recipe B = 3 onions). Should we also try to aggregate similar ingredients (e.g., "chicken breast" and "poulet" if TheMealDB returns inconsistent naming)?
**Answer:** Simple aggregation - Combine identical ingredients by exact name (case-insensitive). Don't try to match similar names like "chicken breast" and "poulet" - keep it simple for MVP.

**Q3:** The design mockup shows items grouped in what looks like a flat list. I assume we should group ingredients by category (Legumes, Viandes, Epicerie, Produits laitiers, etc.). Since TheMealDB doesn't provide category metadata for ingredients, should we use a static mapping table, default to "Autres", or skip categorization?
**Answer:** Static category mapping - Use a static mapping table for common ingredients to categories (Legumes, Viandes, Poissons, Produits laitiers, Epicerie, Boissons, Surgeles). Default uncategorized to "Autres".

**Q4:** For portion adjustment, the Weekly Meal Planning stores `portions` per slot. I assume the shopping list should multiply ingredient quantities by the portion count for each meal. Is that correct?
**Answer:** Yes, multiply by portions - Use the portions count from each meal slot to adjust quantities.

**Q5:** Regarding checked item persistence, I assume checked items should be stored in Supabase (not just local storage) so the list syncs across devices. Is that acceptable?
**Answer:** Supabase persistence - Store checked items in Supabase for cross-device sync. Create a `shopping_list_items` table.

**Q6:** For the "clear/reset" functionality, should both "clear checked" and "regenerate" options exist, or just one?
**Answer:** Both options:
- "Tout decocher" - Uncheck all items
- "Regenerer" - Re-fetch from meal plan, losing check states

**Q7:** Should the shopping list automatically regenerate when the user modifies their meal plan (add/remove/replace recipes), or should it require a manual "refresh" action?
**Answer:** Manual refresh - List does NOT auto-regenerate when meal plan changes. User must manually regenerate.

**Q8:** Is there anything specific you want to exclude from this feature?
**Answer:** Exclude for now (future features):
- Export/share list
- Manual item addition
- Quantity editing
- Multi-week shopping

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Meal Planning Components - Path: `mobile/components/meal-planning/`
- Feature: Meal Planning Store - Path: `mobile/stores/meal-planning.ts` (Zustand store pattern)
- Feature: Meal Slots Service - Path: `backend/app/services/meal_slots_service.py` (service pattern)
- Feature: Meal Slots Routes - Path: `backend/app/routes/meal_slots.py` (route pattern)

### Follow-up Questions
No follow-up questions needed - all requirements clearly answered.

## Visual Assets

### Files Provided:
No visual files found in the planning/visuals folder.

### Visual Insights:
Visual references exist in the design-system.md which describes the "Liste de courses" tab:
- Tab bar with "Liste de courses" as the third tab
- Shopping cart icon (shopping-cart from Feather icons)
- Follows the same styling patterns as other tabs (card containers, rounded corners, shadows)
- Checkbox-style list items for marking items as purchased

## Requirements Summary

### Functional Requirements
- Generate shopping list from current week's meal plan only
- Aggregate identical ingredients by exact name match (case-insensitive)
- Multiply ingredient quantities by portion count from each meal slot
- Group ingredients by category using static mapping table:
  - Legumes
  - Viandes
  - Poissons
  - Produits laitiers
  - Epicerie
  - Boissons
  - Surgeles
  - Autres (default for unmapped ingredients)
- Provide checkable list UI with persistent check states
- Store checked items in Supabase (`shopping_list_items` table) for cross-device sync
- Provide "Tout decocher" action to uncheck all items
- Provide "Regenerer" action to re-fetch list from meal plan (loses check states)
- Manual regeneration only - no auto-update when meal plan changes

### Reusability Opportunities
- Meal planning component patterns from `mobile/components/meal-planning/`
- Zustand store pattern from `mobile/stores/meal-planning.ts`
- Backend service pattern from `backend/app/services/meal_slots_service.py`
- Backend route pattern from `backend/app/routes/meal_slots.py`

### Scope Boundaries
**In Scope:**
- Shopping list generation from current week's meal plan
- Ingredient aggregation by exact name (case-insensitive)
- Portion-based quantity adjustment
- Category grouping with static mapping
- Checkable list UI
- Supabase persistence for check states
- "Tout decocher" and "Regenerer" actions

**Out of Scope:**
- Export/share list functionality
- Manual item addition
- Quantity editing by user
- Multi-week shopping list
- Auto-regeneration on meal plan changes
- Similar ingredient matching/fuzzy matching

### Technical Considerations
- Create new `shopping_list_items` table in Supabase
- Leverage existing meal_slots table structure from Weekly Meal Planning feature
- Use TheMealDB ingredient data already fetched for recipes
- Static ingredient-to-category mapping table (can be in code or database)
- Follow existing patterns from meal-planning components and stores
- Integrate with existing authentication for user-scoped data
