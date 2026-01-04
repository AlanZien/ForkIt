# Specification: Onboarding Flow

## Goal
Create a 5-step post-registration profile setup wizard that guides new users through dietary preferences, allergies, and household size configuration before accessing the main app.

## User Stories
- As a new user, I want to configure my dietary preferences and allergies during first login so that the app personalizes my recipe recommendations from the start.
- As a returning user who skipped setup, I want to be prompted to complete onboarding until I finish so that I receive the full personalized experience.

## Specific Requirements

**Step 1: Welcome Screen**
- Display ForkIt logo with teal background circle (#14B8A6)
- Show welcome heading "Bienvenue sur ForkIt"
- Display value proposition text explaining personalized meal planning
- Primary button "Commencer" to proceed to Step 2
- No back button on first step
- Progress indicator showing step 1 of 5

**Step 2: Dietary Preferences Selection**
- Heading: "Vos regimes alimentaires"
- Subheading explaining selections will personalize recipes
- Display ChipSelector with all 7 dietary types from `ALL_DIETARY_TYPES`
- Use French labels from `DIETARY_LABELS` (Vegetarien, Vegetalien, Sans porc, etc.)
- Multi-select enabled (users can select multiple options)
- "Suivant" button to proceed, "Passer" link to skip
- Back button to return to Welcome step

**Step 3: Allergies Selection**
- Heading: "Vos allergies"
- Subheading explaining allergy selections filter out unsafe recipes
- Display ChipSelector with all 11 allergy types from `ALL_ALLERGY_TYPES`
- Use French labels from `ALLERGY_LABELS` (Gluten, Lactose, Fruits a coque, etc.)
- Multi-select enabled
- "Suivant" button to proceed, "Passer" link to skip
- Back button to return to Dietary step

**Step 4: Household Size (Portions)**
- Heading: "Nombre de personnes"
- Subheading explaining portions adjustment for recipes
- Display PortionSelector with +/- buttons
- Min: 1, Max: 12, Default: 2
- "Suivant" button to proceed, "Passer" link to skip
- Back button to return to Allergies step

**Step 5: Ready Screen**
- Heading: "Vous etes pret !"
- Subheading confirming setup is complete
- Display icon or illustration (checkmark or celebration)
- Primary button: "Planifier ma semaine" (navigates to Planning tab)
- Secondary button: "Explorer les recettes" (navigates to Recipes tab)
- Back button to return to Portions step
- Set `onboarding_completed` flag to true on completion

**Progress Indicator**
- Display at top of each step showing current position (1-5)
- Use dots style similar to existing onboarding.tsx carousel
- Active dot uses teal color (#14B8A6), inactive uses gray (#E5E7EB)
- Active dot is wider (24px) than inactive (8px) for visual emphasis

**Navigation Logic**
- Create new route group `(profile-setup)` in Expo Router
- Modify `app/index.tsx` to check `onboarding_completed` flag after authentication
- If authenticated but `onboarding_completed` is false, redirect to profile-setup flow
- Redirect happens on every app launch until user completes or skips final step
- On final step completion (either CTA), navigate to appropriate tab and set flag

**Backend: onboarding_completed Flag**
- Add `onboarding_completed` boolean column to `user_settings` table (default: false)
- Create new endpoint `GET /api/profile/onboarding-status` returning `{onboarding_completed: boolean}`
- Create new endpoint `PUT /api/profile/onboarding-completed` to set flag to true
- Extend existing preferences service to include onboarding status checks

## Existing Code to Leverage

**ChipSelector Component (mobile/components/preferences/ChipSelector.tsx)**
- Reusable multi-select chip component with teal active state
- Accepts generic type for options, labels record, selectedValues array
- Already styled per design system with proper accessibility attributes
- Use directly for dietary preferences and allergies selection steps

**PortionSelector Component (mobile/components/preferences/PortionSelector.tsx)**
- Numeric +/- selector with min/max bounds
- Styled with teal buttons and proper disabled states
- Use directly for household size step with min=1, max=12

**Types and Constants (mobile/types/preferences.ts)**
- `ALL_DIETARY_TYPES`, `ALL_ALLERGY_TYPES` arrays for chip options
- `DIETARY_LABELS`, `ALLERGY_LABELS` records for French translations
- `DietaryType`, `AllergyType` TypeScript types for type safety
- `DEFAULT_PREFERENCES` for initial state values

**Preferences Store (mobile/stores/preferences.ts)**
- Zustand store with `fetchPreferences` and `updatePreferences` actions
- Use `setLocalPreferences` for tracking wizard state locally
- Call `updatePreferences` on step completion to save incrementally

**Onboarding Screen Layout (mobile/app/(auth)/onboarding.tsx)**
- Reference for screen layout structure with SafeAreaView
- Progress dots pattern: `styles.dot`, `styles.dotActive`, `styles.pagination`
- Footer button layout pattern with primary and link buttons
- FlatList carousel pattern (not needed, but styling reference)

## Out of Scope
- Excluded/preferred ingredients input (too much friction, available in Profile screen later)
- Modification of existing pre-auth onboarding carousel (separate flow)
- Auto-generation of first weekly meal plan
- Push notification preferences setup
- Account settings or profile photo
- Social login integration during onboarding
- Analytics tracking for onboarding completion rate
- A/B testing different onboarding flows
- Tutorial tooltips or coach marks
- Onboarding completion email notification
