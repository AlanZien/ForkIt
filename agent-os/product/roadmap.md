# Product Roadmap

## Development Phases

1. [x] **Authentication System** - Implement user registration, login, and session management with Supabase Auth, including email/password authentication and secure token handling. `M`

2. [x] **User Profile & Preferences** - Create profile screen allowing users to set dietary preferences (vegetarien, sans porc, halal, etc.), allergies (gluten, lactose, fruits a coque, etc.), and excluded/preferred ingredients. Data persisted in Supabase. `M`

3. [x] **Recipe Browsing** - Integrate TheMealDB API to display a searchable, filterable recipe catalog. Include recipe cards with images, titles, and basic info. Implement recipe detail view with ingredients and instructions. `M`

4. [x] **Recipe Favorites** - Allow users to mark recipes as favorites, persist favorites in Supabase, and display a dedicated "Mes favoris" section in the recipe library. `S`

5. [x] **Weekly Meal Planning** - Build the weekly planning interface (Lundi-Dimanche) with dejeuner/diner slots. Users can add recipes to specific meal slots via a selection modal. Planning data saved per user in Supabase. `L`

6. [x] **Automatic Shopping List** - Generate a consolidated shopping list from the weekly meal plan. Group ingredients by category, aggregate quantities for duplicate ingredients, and provide a checkable list interface. `M`

7. [x] **Recipe Filtering by Preferences** - Filter recipe search results and suggestions based on user's dietary preferences and allergies. Exclude recipes containing allergens or incompatible ingredients. `M`

8. [ ] **AI-Powered Menu Suggestions** - Implement weekly menu suggestions that consider user preferences, past selections, and variety. Display as actionable suggestions that can be applied to the planning calendar. `L`

9. [ ] **Personal Recipe Management** - Allow users to create, edit, and delete their own recipes. Personal recipes appear alongside API recipes in search and can be added to meal plans. `M` *(en cours)*

10. [x] **Portion Adjustment** - Add household size setting to user profile. Automatically adjust ingredient quantities in shopping list based on number of portions needed. `S`

11. [x] **Onboarding Flow** - Create guided first-use experience walking new users through profile setup, preference selection, and first weekly plan creation. `S`

12. [ ] **Offline Support** - Cache favorite recipes and current week's meal plan for offline access. Sync changes when connection restored. `M`

> Notes
> - Order reflects technical dependencies: auth -> profile -> recipes -> planning -> shopping list -> advanced features
> - Each item represents end-to-end functionality (mobile UI + backend API + database)
> - POC uses TheMealDB; production may migrate to proprietary recipe database
> - Effort estimates: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks)
