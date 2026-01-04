# API Contracts Synchronization

**Version**: 1.0 | **Applies to**: Backend ↔ Mobile type alignment

## Purpose

Ensure type definitions between backend (Python/Pydantic) and mobile (TypeScript) remain synchronized to prevent runtime errors from field mismatches.

## The Problem

Type mismatches between backend and frontend cause silent failures:

```python
# Backend: backend/app/models/meal_slots.py
class MealSlotCreate(BaseModel):
    slot_date: str  # Backend uses "slot_date"
    meal_type: str
```

```typescript
// Mobile: mobile/types/meal-slot.ts
interface MealSlotCreate {
  date: string;  // Mobile used "date" - MISMATCH!
  meal_type: string;
}
```

Result: 422 Unprocessable Content errors at runtime.

## Best Practices

### 1. Single Source of Truth

The **backend Pydantic models** are the source of truth. Mobile types must mirror them exactly.

### 2. Naming Conventions

| Convention | Example |
|------------|---------|
| Use snake_case for API fields | `slot_date`, `meal_type`, `recipe_id` |
| Match field names exactly | Backend `user_id` = Mobile `user_id` |
| Document date formats | ISO 8601: `YYYY-MM-DD` |

### 3. Type Mapping

| Python Type | TypeScript Type |
|-------------|-----------------|
| `str` | `string` |
| `int` | `number` |
| `float` | `number` |
| `bool` | `boolean` |
| `list[T]` | `T[]` |
| `Optional[T]` | `T \| null` |
| `datetime` | `string` (ISO format) |
| `UUID` | `string` |

### 4. Validation Checklist

When creating new API endpoints:

- [ ] Define Pydantic model in `backend/app/models/`
- [ ] Create matching TypeScript interface in `mobile/types/`
- [ ] Field names match exactly (copy-paste recommended)
- [ ] Optional fields marked with `?` in TypeScript
- [ ] Run `./scripts/verify-standards.sh` to check alignment

### 5. Common Mistakes to Avoid

```typescript
// ❌ WRONG: Different field names
interface MealSlot {
  date: string;        // Backend uses slot_date
  type: string;        // Backend uses meal_type
}

// ✅ CORRECT: Exact match
interface MealSlot {
  slot_date: string;
  meal_type: string;
}
```

```typescript
// ❌ WRONG: Missing nullable annotation
interface Recipe {
  thumbnail: string;   // Backend: Optional[str] can be null
}

// ✅ CORRECT: Nullable properly typed
interface Recipe {
  thumbnail: string | null;
}
```

## Implementation Pattern

### Backend Model

```python
# backend/app/models/example.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemCreate(BaseModel):
    """Request model for creating an item"""
    name: str
    description: Optional[str] = None
    quantity: int
    is_active: bool = True

class ItemResponse(BaseModel):
    """Response model for an item"""
    id: str
    name: str
    description: Optional[str]
    quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Mobile Types

```typescript
// mobile/types/item.ts

/**
 * Request type for creating an item
 * Mirrors: backend/app/models/example.py::ItemCreate
 */
export interface ItemCreate {
  name: string;
  description?: string | null;
  quantity: number;
  is_active?: boolean;  // defaults to true on backend
}

/**
 * Response type for an item
 * Mirrors: backend/app/models/example.py::ItemResponse
 */
export interface ItemResponse {
  id: string;
  name: string;
  description: string | null;
  quantity: number;
  is_active: boolean;
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}
```

## Automated Type Generation

ForkIt uses automatic type generation from backend Pydantic models to TypeScript.

### Generate Types

```bash
# Generate TypeScript types from Pydantic models
python scripts/sync-api-types.py

# Check if types are in sync (for CI)
python scripts/sync-api-types.py --check
```

### Generated Files

Types are generated to `mobile/types/generated/`:

```
mobile/types/generated/
├── index.ts           # Re-exports all types
├── auth.ts            # From backend/app/models/auth.py
├── favorite.ts        # From backend/app/models/favorite.py
├── meal-slot.ts       # From backend/app/models/meal_slot.py
├── personal-recipe.ts # From backend/app/models/personal_recipe.py
├── preferences.ts     # From backend/app/models/preferences.py
├── recipe.ts          # From backend/app/models/recipe.py
└── shopping-list.ts   # From backend/app/models/shopping_list.py
```

### Usage in Mobile

```typescript
// Import generated types
import { FavoriteCreate, FavoriteResponse } from '@/types/generated';

// Use in API calls
const addFavorite = async (data: FavoriteCreate): Promise<FavoriteResponse> => {
  const response = await api.post('/favorites', data);
  return response.data;
};
```

### CI Integration

The `verify-standards.sh` script automatically checks type sync:

```bash
./scripts/verify-standards.sh        # Check (fails if out of sync)
./scripts/verify-standards.sh --fix  # Regenerate types
```

### When to Regenerate

Run `python scripts/sync-api-types.py` after:
- Adding new Pydantic models
- Modifying existing model fields
- Changing field types or optionality

---

**Token Count**: ~600 tokens | **Critical for**: Any feature with API communication
