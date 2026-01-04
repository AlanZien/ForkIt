# Specification: Authentication System

## Goal

Implement a secure user authentication system for the ForkIt meal planning app, enabling user registration, login, email verification, password reset, and session management with optional biometric quick-unlock, using Supabase Auth as the backend provider.

## User Stories

- As a new user, I want to register with my name, email, and password so that I can create an account and start planning meals.
- As a returning user, I want to quickly log in with my credentials or biometrics so that I can access my personalized meal plans without friction.

## Specific Requirements

**Onboarding Flow**
- Display onboarding carousel on first app launch only (3 slides showcasing weekly planning, automatic shopping lists, personalized suggestions)
- Store `hasSeenOnboarding` flag in AsyncStorage to persist first-launch state
- "Get Started" button navigates to Registration screen
- "Se connecter" link navigates to Login screen for existing users
- Check AsyncStorage flag on app launch; bypass onboarding if already seen

**User Registration**
- Collect: Name (full name), Email, Password, Password confirmation
- Validate password minimum 8 characters client-side and server-side
- Use Supabase Auth `signUp` with email confirmation enabled
- Create account immediately in pending state; require email verification for full access
- Navigate to "Verify Email" screen after successful registration
- Handle duplicate email with generic error ("Unable to create account. Please try again.")

**Email Verification**
- Dedicated "Verify your email" screen shown post-registration
- Display user's email address with instructions to check inbox
- "Resend verification email" button with rate limiting (max 3 per hour)
- Handle deep link from verification email to confirm and redirect to main app
- Poll or listen for email confirmation status to auto-navigate on verification
- Block access to main app features until `email_confirmed_at` is set

**User Login**
- Email/password authentication via Supabase Auth `signInWithPassword`
- Generic error messages only ("Email or password incorrect") to prevent enumeration
- "Mot de passe oublie?" link to initiate password reset flow
- Check email verification status; redirect unverified users to verification screen
- On success: store session tokens and navigate to main app

**Password Reset**
- "Forgot password" link on Login screen opens password reset screen
- User enters email; call Supabase Auth `resetPasswordForEmail`
- Show confirmation message regardless of email existence (prevent enumeration)
- Handle deep link from reset email; show password reset form
- Validate new password (min 8 characters) and confirm match
- Clear existing sessions after password change

**Session Management**
- Store access and refresh tokens securely via Expo SecureStore (not AsyncStorage)
- Configure Supabase client with `autoRefreshToken: true` and `persistSession: true`
- Sessions persist until explicit logout (no inactivity timeout)
- Silent background token refresh during app usage
- On refresh failure: clear tokens, redirect to Login with "Session expired" message
- Token storage keys: `sb-access-token`, `sb-refresh-token`

**Biometric Authentication (Optional Feature)**
- Support Face ID (iOS) and fingerprint (Android) via `expo-local-authentication`
- Require initial email/password login before enabling biometrics
- Store biometric preference in SecureStore (`biometricEnabled`)
- On app open with valid session + biometrics enabled: prompt for biometric auth
- Fallback to password if biometric fails 3 times
- Toggle setting in app settings screen
- Disable biometric quick-unlock on logout; require full re-login to re-enable

**Logout Functionality**
- Clear all tokens from SecureStore (`sb-access-token`, `sb-refresh-token`)
- Clear biometric preference flag
- Call Supabase Auth `signOut` to invalidate server session
- Reset auth state in Zustand store
- Navigate to Login screen

## Visual Design

**`agent-os/product/design-references/Image PNG.png`**
- Onboarding screen: App logo with teal blob background, "Let's cook good food" tagline, three feature highlights with icons, primary teal "Get Started" button (48px height), secondary "Se connecter" text link
- Registration screen: "Retour" back navigation, "Creer un compte" title with subtitle, four form fields (Nom, Email, Mot de passe, Confirmer) with #F9FAFB background, password hint text in muted gray, primary "Creer mon compte" button, footer link to login
- Login screen: Back navigation, "Bon retour!" title with subtitle, two form fields (Email, Mot de passe), primary "Se connecter" button, "Mot de passe oublie?" link below button, footer link to registration
- Form inputs: 48px height, #F9FAFB background, 14px border radius, 1px border with rgba(0,0,0,0.08)
- Primary buttons: #14B8A6 background, white text, 16px border radius, full width
- Text links: #14B8A6 color for primary actions, standard foreground for secondary

## Existing Code to Leverage

**`mobile/stores/auth.ts` - Zustand Auth Store**
- Existing store structure with `user`, `isLoading`, `setUser`, `setLoading` actions
- Extend with additional state: `isAuthenticated`, `emailVerified`, `biometricEnabled`
- Add actions: `login`, `logout`, `checkSession`, `setBiometric`

**`mobile/services/supabase.ts` - Supabase Client**
- Already configured with `autoRefreshToken: true` and `persistSession: true`
- Update storage from AsyncStorage to SecureStore for token persistence
- Add auth state change listener subscription

**`mobile/constants/theme.ts` - Design Tokens**
- Use existing `colors`, `spacing`, `borderRadius`, `typography` tokens
- Apply `colors.primary` (#14B8A6) for buttons and links
- Apply `colors.inputBackground` (#F9FAFB) for form fields
- Apply `borderRadius.md` (14px) for inputs, `borderRadius.lg` (16px) for buttons

**`backend/app/services/supabase.py` - Backend Supabase Clients**
- `get_supabase_client()` for public auth operations
- `get_supabase_admin()` for admin operations (user management, verification status checks)

**`backend/app/config.py` - Backend Configuration**
- Extend with `jwt_secret`, `rate_limit_requests`, `rate_limit_window` settings
- Supabase URL and keys already configured

## Out of Scope

- Social login providers (Google, Apple Sign-In) - feature-flagged for future
- Multi-factor authentication (2FA) - feature-flagged for future
- Account deletion flow - feature-flagged for future
- Advanced password policies (complexity rules, breach detection) - feature-flagged for future
- Dietary preferences and allergy collection - separate profile configuration spec
- User profile editing beyond initial registration fields
- Recipe browsing, meal planning, and shopping list features
- Push notification configuration
- Analytics and tracking implementation
- Admin panel or backoffice features
