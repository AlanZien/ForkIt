# Recipe Browsing Specification

## Overview
La fonctionnalité Recipe Browsing permet aux utilisateurs de ForkIt de parcourir, rechercher et consulter des recettes provenant de l'API TheMealDB.

## Functional Requirements

### FR-001: Liste des catégories
- L'application affiche toutes les catégories de recettes disponibles
- Chaque catégorie affiche son nom et une image miniature
- Les catégories sont présentées dans une liste horizontale scrollable

### FR-002: Navigation par catégorie
- L'utilisateur peut sélectionner une catégorie pour voir ses recettes
- La première catégorie est sélectionnée automatiquement au chargement
- La catégorie sélectionnée est visuellement distincte (bordure teal)

### FR-003: Recherche de recettes
- L'utilisateur peut rechercher des recettes par nom
- La recherche nécessite au moins 2 caractères
- Les résultats s'affichent en grille de 2 colonnes
- Un bouton permet d'effacer la recherche

### FR-004: Liste des recettes
- Les recettes s'affichent en grille de 2 colonnes
- Chaque carte affiche l'image et le nom de la recette
- Le nombre de résultats est affiché

### FR-005: Détails d'une recette
- Navigation vers une page de détails au tap sur une recette
- Affichage de l'image en grand format
- Liste des ingrédients avec quantités
- Instructions de préparation
- Catégorie et origine de la recette

### FR-006: Recette aléatoire
- Endpoint API pour obtenir une recette au hasard
- Utilisable pour des suggestions ou inspiration

## Technical Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── models/recipe.py          # Pydantic models
│   ├── routes/recipes.py         # API endpoints
│   └── services/themealdb.py     # Client API externe
```

### Mobile (React Native)
```
mobile/
├── types/recipe.ts               # TypeScript types
├── services/recipes.ts           # API client
├── stores/recipes.ts             # Zustand store
└── app/
    ├── (tabs)/recipes.tsx        # Recipes list screen
    └── recipe/[id].tsx           # Recipe detail screen
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/recipes/categories | Liste des catégories |
| GET | /api/recipes/category/{name} | Recettes d'une catégorie |
| GET | /api/recipes/search?q={query} | Recherche par nom |
| GET | /api/recipes/{id} | Détails d'une recette |
| GET | /api/recipes/random | Recette aléatoire |

### Data Models

**Category**
```typescript
interface Category {
  id: string;
  name: string;
  thumbnail: string;
  description: string;
}
```

**RecipeSummary**
```typescript
interface RecipeSummary {
  id: string;
  name: string;
  thumbnail: string;
}
```

**Recipe (détails complets)**
```typescript
interface Recipe {
  id: string;
  name: string;
  category: string;
  area: string;
  instructions: string;
  thumbnail: string;
  tags: string[];
  youtube: string | null;
  ingredients: Ingredient[];
  source: string | null;
}
```

## UI/UX Design

### Recipes Screen
- Header: "Recettes"
- Barre de recherche avec icône et placeholder
- Section catégories (scroll horizontal avec chips)
- Grille de recettes (2 colonnes)
- États: loading, empty, error

### Recipe Detail Screen
- Image full-width en haut
- Nom de la recette en titre
- Badges catégorie et origine
- Section "Ingrédients" avec liste
- Section "Instructions" avec texte

### Design Tokens
- Primary color: #14B8A6 (teal)
- Background: #FFFFFF
- Card shadow: rgba(0,0,0,0.1)
- Border radius: 12-16px
- Font sizes: 12/14/16/18/28px

## Non-Functional Requirements

### Performance
- Cache des catégories (ne change pas souvent)
- Debounce sur la recherche (éviter requêtes excessives)
- Images lazy-loaded

### Error Handling
- Messages d'erreur explicites
- État empty state si aucun résultat
- Retry automatique ou bouton retry

### Testing
- Tests unitaires backend (pytest)
- Tests du store Zustand (jest)
- Tests du service API (jest)
