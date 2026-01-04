# Specification: Recipe Favorites

## Overview

**Feature:** Recipe Favorites
**Priority:** P1
**Effort:** S (2-3 days)
**Date:** 2026-01-02

Permettre aux utilisateurs de marquer des recettes comme favorites, persister ces favoris dans Supabase, et afficher une section dediee "Mes favoris".

---

## User Stories

### US-1: Ajouter une recette aux favoris
**En tant qu'** utilisateur connecte
**Je veux** pouvoir marquer une recette comme favorite
**Afin de** la retrouver facilement plus tard

### US-2: Retirer une recette des favoris
**En tant qu'** utilisateur connecte
**Je veux** pouvoir retirer une recette de mes favoris
**Afin de** garder ma liste de favoris pertinente

### US-3: Voir mes recettes favorites
**En tant qu'** utilisateur connecte
**Je veux** voir toutes mes recettes favorites dans une section dediee
**Afin de** acceder rapidement a mes recettes preferees

---

## Architecture Technique

### Base de donnees (Supabase)

#### Table: user_favorites
```sql
CREATE TABLE user_favorites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  recipe_id VARCHAR(20) NOT NULL,  -- TheMealDB ID (e.g., "52772")
  recipe_name VARCHAR(255) NOT NULL,  -- Cache pour affichage rapide
  recipe_thumbnail VARCHAR(500),  -- URL image pour affichage liste
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(user_id, recipe_id)
);

-- Index pour requetes utilisateur
CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);

-- RLS Policies
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own favorites"
  ON user_favorites FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own favorites"
  ON user_favorites FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites"
  ON user_favorites FOR DELETE
  USING (auth.uid() = user_id);
```

### Backend API

#### Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/favorites` | Liste des favoris de l'utilisateur | Required |
| POST | `/api/favorites` | Ajouter un favori | Required |
| DELETE | `/api/favorites/{recipe_id}` | Retirer un favori | Required |
| GET | `/api/favorites/{recipe_id}` | Verifier si favori | Required |

#### Models (Pydantic)

```python
# backend/app/models/favorite.py

class FavoriteCreate(BaseModel):
    recipe_id: str
    recipe_name: str
    recipe_thumbnail: str | None = None

class FavoriteResponse(BaseModel):
    id: str
    recipe_id: str
    recipe_name: str
    recipe_thumbnail: str | None
    created_at: datetime

class FavoriteListResponse(BaseModel):
    favorites: list[FavoriteResponse]
    count: int

class FavoriteStatus(BaseModel):
    is_favorite: bool
```

#### Service

```python
# backend/app/services/favorites_service.py

class FavoritesService:
    def get_favorites(self, user_id: str) -> list[FavoriteResponse]
    def add_favorite(self, user_id: str, data: FavoriteCreate) -> FavoriteResponse
    def remove_favorite(self, user_id: str, recipe_id: str) -> bool
    def is_favorite(self, user_id: str, recipe_id: str) -> bool
```

### Mobile

#### Types TypeScript

```typescript
// mobile/types/favorite.ts

interface Favorite {
  id: string;
  recipe_id: string;
  recipe_name: string;
  recipe_thumbnail: string | null;
  created_at: string;
}

interface FavoriteListResponse {
  favorites: Favorite[];
  count: number;
}
```

#### Service

```typescript
// mobile/services/favorites.ts

export const favoritesService = {
  getFavorites: () => Promise<Favorite[]>,
  addFavorite: (recipe: Recipe) => Promise<Favorite>,
  removeFavorite: (recipeId: string) => Promise<void>,
  isFavorite: (recipeId: string) => Promise<boolean>,
}
```

#### Store (Zustand)

```typescript
// mobile/stores/favorites.ts

interface FavoritesState {
  favorites: Favorite[];
  favoriteIds: Set<string>;  // Pour lookup rapide
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchFavorites: () => Promise<void>;
  addFavorite: (recipe: Recipe) => Promise<void>;
  removeFavorite: (recipeId: string) => Promise<void>;
  isFavorite: (recipeId: string) => boolean;  // Sync check
  reset: () => void;
}
```

---

## UI/UX

### Bouton Favori (Heart Icon)

**Emplacement:**
- Carte recette (grille) - coin superieur droit
- Ecran detail recette - header

**Etats:**
- Non-favori: Coeur vide (outline), couleur gris
- Favori: Coeur plein, couleur rouge/teal
- Loading: Indicateur pendant l'action

**Interaction:**
- Tap toggle le statut favori
- Feedback haptic sur iOS
- Animation scale sur le coeur

### Section Favoris

**Acces:**
- Nouvel onglet "Favoris" dans la tab bar, OU
- Section en haut de l'ecran Recettes

**Design recommande:** Section dans l'ecran Recettes
- Bandeau horizontal scrollable en haut
- Affiche les 5 derniers favoris avec miniature
- Lien "Voir tous" vers liste complete

**Ecran Liste Favoris:**
- Grille identique aux recettes
- Message vide si aucun favori
- Pull-to-refresh

---

## Edge Cases

1. **Recette deja en favori** - Ignorer silencieusement ou retourner existant
2. **Suppression recette inexistante** - Retourner succes (idempotent)
3. **Utilisateur non connecte** - Rediriger vers login
4. **Limite de favoris** - Pas de limite pour MVP
5. **Offline** - Afficher favoris caches, queue les modifications

---

## Tests

### Backend
- Test ajout favori success
- Test ajout favori duplique
- Test liste favoris vide
- Test liste favoris avec donnees
- Test suppression favori
- Test suppression favori inexistant
- Test verification is_favorite true/false
- Test RLS (user ne peut voir que ses favoris)

### Mobile
- Test service API calls
- Test store state management
- Test bouton toggle
- Test affichage liste
- Test etat vide

---

## Dependencies

- Authentication System (user_id)
- Recipe Browsing (Recipe model, recipe detail screen)
- Supabase (database, RLS)
