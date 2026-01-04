# Spec Requirements: Onboarding Flow

## Initial Description

Onboarding Flow - Create guided first-use experience walking new users through profile setup, preference selection, and first weekly plan creation.

Key elements:
1. Welcome screen - app intro, value proposition
2. Dietary preferences selection (vegetarien, vegan, sans porc, halal)
3. Allergies selection (gluten, lactose, fruits a coque, crustaces, oeufs)
4. Household size (nombre de personnes pour ajuster les portions)
5. Final "Ready" screen with CTA to planning or browse recipes
6. Store onboarding_completed flag in user_preferences
7. Conditional navigation - redirect to onboarding if not completed

Effort: S (small, 2-3 days)

## Requirements Discussion

### First Round Questions

**Q1:** I notice there's already an `onboarding.tsx` screen that shows a 3-slide intro carousel *before* authentication. Your request is for a *post-registration* profile setup flow. I assume we're creating a **new separate flow** (e.g., "profile-setup" or "first-time-setup") that runs after registration and before accessing the main app. Is that correct, or should we repurpose/extend the existing onboarding screen?
**Answer:** Correct - this is a **new separate post-registration flow**. The existing onboarding.tsx is a pre-auth intro carousel. We're creating a new profile-setup flow that runs after registration.

**Q2:** For the flow structure, I'm thinking a **multi-step wizard** approach with 4-5 screens: Step 1: Welcome/Value proposition, Step 2: Dietary preferences selection, Step 3: Allergies selection, Step 4: Household size (portions), Step 5: "Ready to go" with CTA. Should each step be its own screen with forward/back navigation, or would you prefer a single scrollable page with sections?
**Answer:** Use **multi-step wizard with separate screens** and forward/back navigation. 5 steps as described: Step 1: Welcome, Step 2: Dietary preferences, Step 3: Allergies, Step 4: Household size, Step 5: Ready with CTA.

**Q3:** The existing `ProfilePreferences` component has dietary types (`vegetarian`, `vegan`, `no_pork`, `no_beef`, `pescetarian`, `halal`, `kosher`) and 11 allergy types. Your raw idea mentions French labels (vegetarien, vegan, sans porc, halal) and fewer allergies (gluten, lactose, fruits a coque, crustaces, oeufs). I assume we should use the **complete existing preference types** for consistency with the profile screen. Is that correct?
**Answer:** Yes, use the **complete existing preference types** from the ProfilePreferences component for consistency.

**Q4:** For the "skippable but encouraged" requirement, I'm assuming: Each step has a "Skip" or "Later" option (text link), the final screen has "Complete Setup" primary button + "Skip for now" secondary, if skipped users can complete preferences later via Profile screen, we track `onboarding_completed` separately from preferences being filled. Is this the right approach?
**Answer:** Yes, the skippable approach is correct: Each step has "Passer" (Skip) option, Final screen: primary "Commencer" + secondary "Passer", Track `onboarding_completed` separately.

**Q5:** For conditional navigation, I assume: After successful registration, redirect to this new profile-setup flow, check `onboarding_completed` flag on app launch (if authenticated but not completed, redirect to setup), the flag is stored in `user_preferences` table in Supabase (backend needs a new field). Should the redirect happen every login until completed, or only on first login after registration?
**Answer:** Redirect **every login until completed** to encourage completion. Flag stored in `user_preferences` table.

**Q6:** For the final "Ready" screen CTA, you mentioned "Plan your week" or "Browse recipes". I assume we show **two buttons** - one primary action and one secondary alternative. Which action should be primary (default emphasis)?
**Answer:** Primary action: **"Planifier ma semaine"** (core value of the app). Secondary: "Explorer les recettes".

**Q7:** Should we include the **excluded/preferred ingredients** input in the onboarding flow, or keep it simple with just dietary preferences, allergies, and household size? The full ProfilePreferences component includes these fields, but they might add friction to the first-time experience.
**Answer:** Keep it **simple** - just dietary preferences, allergies, and household size. No excluded/preferred ingredients in onboarding (can be added later in Profile).

### Existing Code to Reference

**Similar Features Identified:**
- Feature: ProfilePreferences - Path: `mobile/components/profile/ProfilePreferences.tsx` - ChipSelector pattern for preferences
- Feature: PortionSelector - Path: `mobile/components/profile/PortionSelector.tsx` - household size selector
- Feature: Preferences Store - Path: `mobile/stores/preferences.ts` - Zustand store pattern
- Feature: Preferences Types - Path: `mobile/types/preferences.ts` - Type definitions
- Feature: Pre-auth Onboarding - Path: `mobile/app/onboarding.tsx` - Reference for screen layout structure (different flow)

### Follow-up Questions

No follow-up questions needed - all requirements are clear.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Guidance:
Proceed with the established design system:
- Primary color: Teal #14B8A6
- Follow existing screen patterns from ProfilePreferences and onboarding.tsx
- Maintain consistency with current app styling

## Requirements Summary

### Functional Requirements
- Create a new 5-step post-registration profile setup wizard
- Step 1 (Welcome): App value proposition and introduction
- Step 2 (Dietary Preferences): Selection using ChipSelector with complete dietary types from existing system
- Step 3 (Allergies): Selection using ChipSelector with complete allergy types from existing system
- Step 4 (Household Size): Number of persons selector using PortionSelector component pattern
- Step 5 (Ready): Final screen with dual CTAs
- Each step must have forward/back navigation between screens
- Each step must have "Passer" (Skip) option to move forward without selection
- Final screen shows primary button "Commencer" and secondary "Passer"
- Store `onboarding_completed` flag in `user_preferences` table
- Redirect authenticated users to profile setup every login until completed
- Save preferences to backend as user progresses or on completion

### User Interface Requirements
- Multi-step wizard with separate screens per step
- Progress indicator showing current step (1-5)
- Back button to return to previous step (except Step 1)
- Skip option on each step (text link style)
- Final screen buttons:
  - Primary: "Planifier ma semaine" (navigates to weekly planning)
  - Secondary: "Explorer les recettes" (navigates to recipe browsing)
- French language labels throughout

### Reusability Opportunities
- Reuse ChipSelector component from ProfilePreferences for dietary and allergy selection
- Reuse PortionSelector component for household size
- Follow Zustand store pattern from preferences.ts
- Use existing preference type definitions from types/preferences.ts
- Reference onboarding.tsx for screen layout structure

### Scope Boundaries

**In Scope:**
- 5-step profile setup wizard (Welcome, Dietary, Allergies, Household, Ready)
- Navigation between steps (forward/back)
- Skip functionality per step
- Backend integration for saving preferences
- Backend integration for onboarding_completed flag
- Conditional navigation based on onboarding completion status
- Integration with existing preference types and components

**Out of Scope:**
- Excluded/preferred ingredients (too much friction for onboarding)
- Modification of existing pre-auth onboarding carousel
- First weekly plan auto-generation (just navigation to planning screen)
- Push notification preferences
- Advanced profile fields

### Technical Considerations
- New screen(s) in `mobile/app/` directory (e.g., `profile-setup.tsx` or folder with step screens)
- New `onboarding_completed` field in `user_preferences` table (Supabase migration needed)
- Backend endpoint to update onboarding_completed flag
- Modify `mobile/app/index.tsx` to check onboarding_completed and redirect accordingly
- Use existing preferences store for state management
- Reuse existing API endpoints for saving dietary preferences and allergies
- Follow Expo Router navigation patterns
