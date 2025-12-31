# Spec Requirements: Authentication System

## Initial Description

Authentication System - Implement user registration, login, and session management with Supabase Auth, including email/password authentication and secure token handling.

## Requirements Discussion

### First Round Questions

**Q1:** Onboarding Flow - Should onboarding be shown only on first launch or before every login?
**Answer:** Onboarding shown ONLY on first launch (or after voluntary reset). Flow: Onboarding (first launch only) -> Login/Register -> Main App. Flag stored locally to track if user has seen onboarding.

**Q2:** Email Verification - Is email verification required before full app access?
**Answer:** REQUIRED before full app access. Account can be created immediately but access is limited until verified. Dedicated "Verify your email" screen with resend link option.

**Q3:** Password Reset - Is a "Forgot password" flow with reset link required?
**Answer:** YES - "Forgot password" flow with reset link is REQUIRED. Standard production-grade feature.

**Q4:** Registration Fields - What fields are collected at signup vs post-signup?
**Answer:** Collected at signup: Name, Email, Password, Password confirmation. EXCLUDED from signup: Dietary preferences, allergies, other preferences. These are collected post-signup via dedicated profile configuration flow.

**Q5:** Session & Token Management - How should sessions be handled?
**Answer:** Tokens stored via Expo SecureStore. Automatic refresh via Supabase client. Persistent session until explicit logout. NO expiration based on inactivity.

**Q6:** Biometric Authentication - Should Face ID / Touch ID be supported?
**Answer:** YES - supported as OPTIONAL feature. Initial login via email/password required. Biometrics used as quick unlock for subsequent app opens. Enable/disable via settings.

**Q7:** Error Handling & Security - How should authentication errors be displayed?
**Answer:** Generic error messages (don't reveal if email exists). Example: "Email or password incorrect". Rate limiting ENABLED on backend.

**Q8:** Session Expiration During Usage - What happens if session expires while using app?
**Answer:** Silent refresh in background. On failure: redirect to Login screen. Clear message indicating session expired.

**Q9:** Experimental Features - Are there features to implement behind feature flags?
**Answer:** YES - The following features should be implemented via feature flags (non-blocking, can be disabled without impact):
- Social login (Google, Apple)
- Multi-factor authentication (2FA)
- Account deletion flow
- Advanced password policies

**Q10:** Visual Assets - Are there design mockups available?
**Answer:** No additional visuals provided for this spec. Create screens based on existing design system mockups in `agent-os/product/design-references/`.

### Existing Code to Reference

No similar existing features identified for reference (this is the foundational authentication system).

### Follow-up Questions

None required - user provided comprehensive answers to all questions.

## Visual Assets

### Files Provided:
No visual files were added to `agent-os/specs/2025-12-31-authentication-system/planning/visuals/`.

### Design Reference Analysis:
The existing design reference (`agent-os/product/design-references/Image PNG.png`) contains mockups for:

**Onboarding Screen:**
- App logo with teal decorative blob background
- "Yummy" branding with tagline "Let's cook good food"
- Three feature highlights with icons:
  - Planning hebdomadaire (weekly planning)
  - Liste de courses automatique (automatic shopping list)
  - Suggestions personnalisees (personalized suggestions)
- Primary teal "Get Started" button
- Secondary "Se connecter" (Login) link
- Footer note about data storage

**Registration Screen (Creer un compte):**
- "Retour" (Back) navigation
- Title: "Creer un compte" with subtitle "Rejoignez Yummy gratuitement"
- Form fields: Nom, Email, Mot de passe, Confirmer le mot de passe
- "Minimum 8 caracteres" password hint
- Primary teal "Creer mon compte" button
- Footer link: "Vous avez deja un compte? Se connecter"

**Login Screen (Bon retour!):**
- "Retour" (Back) navigation
- Title: "Bon retour!" with subtitle "Connectez-vous a votre compte Yummy"
- Form fields: Email, Mot de passe
- Primary teal "Se connecter" button
- "Mot de passe oublie?" link (Forgot password)
- Footer link: "Pas encore de compte? Creer un compte"
- Info note about demo mode

**Profile Screen:**
- User icon with "Modifier" (Edit) button
- "Informations personnelles" section with Name field
- "Regimes alimentaires" (Dietary regimes) section with chips: Vegetarien, Vegetalien, Sans porc, Sans boeuf, Pescetarien, Halal, Casher
- "Allergies et Intolerances" section with chips: Gluten, Lactose, Fruits a coque, Arachides, Oeufs, Poisson, Fruits de mer, Soja
- "Preferences d'ingredients" section for excluded/preferred ingredients
- "Se deconnecter" (Logout) link in coral/destructive color

### Visual Insights:
- Clean, minimal design with generous whitespace
- Teal (#14B8A6) as primary action color
- Form inputs with light gray background (#F9FAFB)
- Rounded corners (16px) on buttons and cards
- System font stack for typography
- Decorative gradient blobs for visual interest on key screens
- French language interface throughout
- Touch-friendly 48px minimum height for inputs and buttons

## Requirements Summary

### Functional Requirements

**Onboarding:**
- Display onboarding carousel on first app launch only
- Store "hasSeenOnboarding" flag in AsyncStorage
- Show app value propositions (planning, shopping list, suggestions)
- Provide "Get Started" CTA leading to registration
- Provide "Se connecter" link for existing users

**Registration:**
- Collect: Name, Email, Password, Password confirmation
- Validate password minimum 8 characters
- Send verification email upon registration
- Create account immediately but limit access until verified
- Show "Verify your email" screen post-registration
- Provide "Resend verification email" functionality

**Login:**
- Email/password authentication via Supabase Auth
- Generic error messages ("Email or password incorrect")
- "Forgot password" link triggering reset flow
- Link to registration for new users

**Password Reset:**
- "Forgot password" flow initiated from login screen
- Send password reset link via email
- Dedicated password reset screen/deep link handling

**Email Verification:**
- Dedicated "Verify your email" screen
- Block full app access until email verified
- "Resend verification email" button
- Handle verification deep links

**Session Management:**
- Store tokens securely via Expo SecureStore
- Automatic token refresh via Supabase client
- Persistent sessions (no inactivity timeout)
- Session only ends on explicit logout
- Silent background refresh during app usage
- On refresh failure: redirect to login with "Session expired" message

**Biometric Authentication (Optional):**
- Support Face ID / Touch ID as quick unlock
- Require initial email/password login first
- Toggle enable/disable in settings
- Use biometrics for subsequent app opens (when enabled)

**Logout:**
- Clear all tokens from SecureStore
- Clear session state
- Redirect to login screen
- Disable biometric quick unlock until next full login

### Reusability Opportunities

- Design tokens and components from `agent-os/product/design-system.md`
- Color palette, typography, spacing already defined
- Button, Input, Card component patterns established
- Existing mockups provide exact visual reference

### Scope Boundaries

**In Scope:**
- Onboarding flow (first launch detection, carousel, navigation)
- User registration with email/password
- Email verification flow with resend capability
- User login with email/password
- Password reset flow
- Session management with secure token storage
- Automatic token refresh
- Biometric authentication (Face ID / Touch ID) as optional feature
- Logout functionality
- Rate limiting on backend endpoints
- Generic error messages for security

**Out of Scope:**
- Dietary preferences collection (handled in separate profile flow)
- Allergy information collection (handled in separate profile flow)
- User profile editing beyond initial setup
- Recipe browsing and planning features
- Shopping list functionality

**Feature-Flagged (Experimental - Non-blocking):**
- Social login (Google Sign-In, Apple Sign-In)
- Multi-factor authentication (2FA)
- Account deletion flow
- Advanced password policies (complexity rules, breach detection)

### Technical Considerations

**Backend (FastAPI + Supabase):**
- Supabase Auth for authentication
- Rate limiting middleware on auth endpoints
- Generic error responses (no email enumeration)
- Email templates for verification and password reset

**Frontend (React Native + Expo):**
- Expo SecureStore for token storage
- AsyncStorage for onboarding flag
- expo-local-authentication for biometrics
- Deep linking for email verification and password reset
- Supabase JS client for auth operations

**Security:**
- HTTPS only
- Secure token storage (never in AsyncStorage)
- No sensitive data in logs
- Rate limiting to prevent brute force
- Generic error messages

**Navigation Flow:**
```
App Launch
    |
    v
[Check hasSeenOnboarding]
    |
    +-- First Launch --> Onboarding --> Login/Register
    |
    +-- Returning User --> [Check Session]
                               |
                               +-- Valid Session --> [Check Biometrics Enabled]
                               |                          |
                               |                          +-- Yes --> Biometric Prompt --> Main App
                               |                          |
                               |                          +-- No --> Main App
                               |
                               +-- No Session --> Login Screen
```

**Screens Required:**
1. Onboarding (carousel with 3 slides)
2. Login
3. Register
4. Verify Email (post-registration)
5. Forgot Password (enter email)
6. Reset Password (from email link)
7. Biometric Settings (within app settings)
