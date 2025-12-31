# Tech Stack - ForkIt

## Frontend (Mobile)

### Framework
- **Expo** - React Native development platform for iOS and Android
- **React Native** - Cross-platform mobile UI framework

### Navigation
- **Expo Router** - File-based routing for React Native

### State Management
- **TanStack Query (React Query)** - Server state management, caching, and synchronization
- **Zustand** - Lightweight client state management for local UI state

### UI Components
- **NativeWind** - Tailwind CSS for React Native
- **Custom components** - Built following the design system specifications

### Forms & Validation
- **React Hook Form** - Performant form handling
- **Zod** - Schema validation for forms and API responses

## Backend

### API Framework
- **FastAPI** (Python) - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and serialization

### Database & Auth
- **Supabase** - Backend-as-a-Service providing:
  - PostgreSQL database
  - Authentication (email/password)
  - Row Level Security (RLS)
  - Real-time subscriptions
  - Storage (for recipe images)

### External APIs
- **TheMealDB API** - Recipe data source for POC phase
  - Free tier: www.themealdb.com/api.php
  - Provides: recipes, ingredients, categories, images

## Development Tools

### Package Management
- **pnpm** - Fast, disk space efficient package manager (frontend)
- **uv** - Fast Python package manager (backend)

### Code Quality
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting
- **Ruff** - Python linting and formatting
- **TypeScript** - Type safety for frontend code
- **mypy** - Python type checking

### Testing
- **Vitest** - Unit testing for frontend
- **React Native Testing Library** - Component testing
- **pytest** - Python testing framework
- **pytest-asyncio** - Async test support

### Version Control
- **Git** - Source control
- **GitHub** - Repository hosting and CI/CD

## Infrastructure

### Deployment
- **Expo EAS** - Build and deployment for mobile apps
- **Supabase Cloud** - Managed database and auth hosting
- **Railway** or **Fly.io** - FastAPI backend hosting

### Monitoring
- **Sentry** - Error tracking and performance monitoring
- **Supabase Dashboard** - Database and auth analytics

## Architecture Overview

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|   Expo / RN      |---->|    FastAPI       |---->|    Supabase      |
|   Mobile App     |     |    Backend       |     |    (PostgreSQL)  |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
        |                        |
        |                        v
        |                +------------------+
        |                |                  |
        +--------------->|   TheMealDB API  |
                         |   (Recipes)      |
                         |                  |
                         +------------------+
```

## Key Technical Decisions

1. **Expo over bare React Native**: Simplified build process, OTA updates, easier development workflow
2. **FastAPI over Node.js**: Strong typing with Pydantic, async support, Python ecosystem for potential ML features
3. **Supabase over Firebase**: PostgreSQL flexibility, better pricing, open-source foundation
4. **TheMealDB for POC**: Free, comprehensive recipe database; can migrate to proprietary data later
5. **TanStack Query for server state**: Excellent caching, background refetching, optimistic updates for seamless UX
