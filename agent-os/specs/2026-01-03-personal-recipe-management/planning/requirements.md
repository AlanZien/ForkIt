# Spec Requirements: Personal Recipe Management

## Initial Description

Allow users to create, edit, and delete their own recipes. Personal recipes appear alongside API recipes in search and can be added to meal plans.

## Requirements Discussion

### First Round Questions

**Q1:** I assume personal recipes will follow a similar data structure to TheMealDB recipes (title, image, ingredients with quantities, instructions). Is that correct, or do you want to add/remove fields (e.g., prep time, cooking time, difficulty level, servings, categories/tags)?

**Answer:** Base structure similar to TheMealDB, plus useful fields for family app. V1 fields: Title, Image (optional), Ingredients (structured), Instructions (steps), Servings (required), Total time or prep+cook (optional but useful), Tags/categories (optional). Rationale: compatible with meal planning + shopping list generation.

**Q2:** For recipe images, I'm thinking users can upload a photo from their device or take a new photo. Should we also support "no image" with a placeholder, or is an image required?

**Answer:** NOT required, support "no image" + placeholder. Rationale: required image creates friction and blocks quick recipe creation.

**Q3:** I assume ingredients will be entered as a list with name + quantity + unit (e.g., "Flour, 250, grams"). Is that correct, or would you prefer a simpler free-text format per ingredient (e.g., "250g flour")?

**Answer:** Semi-structured input: name, quantity (numeric), unit (dropdown list), optional note field (e.g., "well ripe", "to taste"). Rationale: essential for clean shopping list generation.

**Q4:** For recipe instructions, I'm thinking a simple multi-line text field. Should we support step-by-step numbered instructions (separate input per step), or is a single text block sufficient for the MVP?

**Answer:** Numbered steps, one field per step. Rationale: better readability, easy to check off while cooking, enables future features (timer per step).

**Q5:** I assume personal recipes should be private to the user who created them (not shared publicly). Is that correct, or do you envision a "family sharing" feature where household members can see each other's recipes?

**Answer:** Private by default. Family sharing planned for v1.1/v2 (not v1). Rationale: sharing requires household/members/permissions model - don't build it just for recipes.

**Q6:** When displaying recipes in search results and the recipe list, I'm thinking personal recipes will be visually distinguished with a small badge or icon (e.g., "My Recipe" tag). Is that desirable, or should they blend seamlessly with API recipes?

**Answer:** YES, visually distinguish with discreet badge: "Ma recette" or user icon. Rationale: avoids confusion between external source vs personal.

**Q7:** Should users be able to duplicate/import an API recipe as a starting point for their own modified version (e.g., "Fork this recipe")?

**Answer:** YES, allowed and recommended. Behavior: duplicate API recipe as personal recipe, can modify everything, optionally keep "source" field for internal traceability. Rationale: speeds up recipe creation, very common use case (adapt to tastes/kids).

**Q8:** Is there anything you explicitly want to EXCLUDE from this feature for now (e.g., recipe sharing, nutritional information calculation, video instructions, recipe import from URL)?

**Answer:** Explicit exclusions for v1: Import from URL (scraping), Videos, Full nutritional calculation, Public sharing / community, Comments/likes, Receipt scanning / drive integrations. Rationale: high complexity, secondary value compared to core (planning + shopping).

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

None required - user provided comprehensive answers to all questions.

## Visual Assets

### Files Provided:

No visual assets provided.

### Visual Insights:

N/A - No visual files to analyze.

## Requirements Summary

### Functional Requirements

**Recipe Creation:**
- Create personal recipes with the following fields:
  - Title (required)
  - Image (optional, with placeholder for missing images)
  - Servings (required, numeric)
  - Prep time (optional)
  - Cook time (optional)
  - Tags/categories (optional)
  - Ingredients list (structured)
  - Instructions (step-by-step)
- Support image upload from device gallery or camera
- Display placeholder image when no image is provided

**Ingredient Input:**
- Semi-structured ingredient entry:
  - Name (text, required)
  - Quantity (numeric, required)
  - Unit (dropdown selection, required)
  - Note (text, optional - e.g., "well ripe", "to taste")
- Add/remove ingredients dynamically
- Ingredient format compatible with shopping list generation

**Instructions Input:**
- Numbered step-by-step instructions
- One input field per step
- Add/remove steps dynamically
- Auto-numbering of steps

**Recipe Editing:**
- Edit any field of a personal recipe
- Update image (replace or remove)
- Reorder ingredients and steps
- Save changes with validation

**Recipe Deletion:**
- Delete personal recipes with confirmation
- Handle deletion of recipes already in meal plans (warn or cascade)

**Recipe Display:**
- Personal recipes appear in search results alongside API recipes
- Visual distinction with discreet badge ("Ma recette" or user icon)
- Personal recipes can be added to meal plans (same as API recipes)
- Personal recipe detail view with all fields

**Fork Recipe Feature:**
- Duplicate any API recipe as a personal recipe
- All fields become editable
- Optional "source" field for internal traceability (original recipe ID)
- "Fork" action accessible from recipe detail view

**Privacy:**
- All personal recipes are private to the creating user
- No sharing functionality in v1

### Reusability Opportunities

- Recipe detail view structure (for form layout inspiration)
- Favorites CRUD pattern (user-owned resource in Supabase)
- Meal plan backend patterns (user-owned data with relationships)
- Recipe card component (for displaying personal recipes in lists)

### Scope Boundaries

**In Scope:**
- Full CRUD for personal recipes
- Structured ingredient and step-by-step instruction input
- Image upload (optional) with placeholder
- Servings, prep time, cook time, tags fields
- "Fork recipe" feature to duplicate API recipes
- Visual badge to distinguish personal recipes
- Personal recipes in search results and meal plan integration
- Source field for forked recipes (traceability)

**Out of Scope:**
- Recipe import from URL (web scraping)
- Video instructions
- Nutritional information calculation
- Public sharing / community features
- Comments and likes
- Receipt scanning
- Drive/cloud integrations
- Family sharing (planned for v1.1/v2)

### Technical Considerations

- **Database:** Supabase table for personal recipes with RLS (Row Level Security) for user privacy
- **Image Storage:** Supabase Storage bucket for recipe images
- **API Compatibility:** Personal recipe structure must be compatible with existing recipe display components and meal plan integration
- **Shopping List Integration:** Ingredient structure (name, quantity, unit) must support aggregation for shopping list generation
- **Search Integration:** Personal recipes must be searchable alongside TheMealDB recipes
- **Offline Support:** Consider caching personal recipes for offline access (future consideration)
- **Localization:** Badge text "Ma recette" suggests French localization - ensure i18n compatibility
