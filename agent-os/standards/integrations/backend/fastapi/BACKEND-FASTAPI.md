# FastAPI Backend Standards - ForkIt

**Version**: 1.0 | **Stack**: FastAPI + Python 3.11+ | **Token-Optimized**

## Architecture

### Project Structure
```
backend/
├── app/
│   ├── main.py              # App entry, CORS, middleware
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Supabase client setup
│   ├── models/              # Pydantic models
│   │   ├── base.py          # BaseModel with Config
│   │   ├── user.py
│   │   └── recipe.py
│   ├── routes/              # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py          # /api/auth/*
│   │   └── recipes.py       # /api/recipes/*
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   └── recipe_service.py
│   └── utils/               # Helpers
│       ├── security.py      # JWT, hashing
│       └── validators.py
├── tests/
│   ├── test_auth.py
│   └── test_recipes.py
├── requirements.txt
└── .env.example
```

### Dependencies
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
supabase==2.3.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
httpx==0.26.0
```

## Core Patterns

### 1. Config Management
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Database Client
```python
# app/database.py
from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)
```

### 3. Pydantic Models
```python
# app/models/base.py
from pydantic import BaseModel, ConfigDict

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# app/models/recipe.py
from datetime import datetime
from typing import Optional

class RecipeBase(BaseModelConfig):
    title: str
    description: Optional[str] = None
    ingredients: list[str]
    steps: list[str]

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
```

### 4. Route Structure
```python
# app/routes/recipes.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.recipe import Recipe, RecipeCreate
from app.services.recipe_service import RecipeService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: RecipeCreate,
    user_id: str = Depends(get_current_user)
):
    return await RecipeService.create(recipe, user_id)

@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    recipe = await RecipeService.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

### 5. Service Layer
```python
# app/services/recipe_service.py
from app.database import supabase
from app.models.recipe import Recipe, RecipeCreate

class RecipeService:
    @staticmethod
    async def create(recipe: RecipeCreate, user_id: str) -> Recipe:
        data = recipe.model_dump()
        data["user_id"] = user_id

        response = supabase.table("recipes").insert(data).execute()
        return Recipe(**response.data[0])

    @staticmethod
    async def get_by_id(recipe_id: str) -> Recipe | None:
        response = supabase.table("recipes").select("*").eq("id", recipe_id).execute()
        return Recipe(**response.data[0]) if response.data else None
```

### 6. Main App
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, recipes

app = FastAPI(title="ForkIt API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(recipes.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Security

### JWT Authentication
```python
# app/utils/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Error Handling

### Custom Exceptions
```python
# app/utils/exceptions.py
from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
```

## Testing

### Test Setup
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Login and return headers with JWT
    response = client.post("/api/auth/login", json={"email": "test@test.com", "password": "test123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Test Example
```python
# tests/test_recipes.py
def test_create_recipe(client, auth_headers):
    recipe_data = {
        "title": "Test Recipe",
        "ingredients": ["ingredient1"],
        "steps": ["step1"]
    }
    response = client.post("/api/recipes/", json=recipe_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Recipe"
```

## Code Quality Rules (OBLIGATOIRE)

### Avant de marquer une tâche comme complète :

**1. Return Types** - Toute fonction doit avoir une annotation de retour
```python
# ❌ Mauvais
async def get_recipe(id: str):
    ...

# ✅ Bon
async def get_recipe(id: str) -> RecipeResponse:
    ...
```

**2. Generic Types** - Toujours spécifier les paramètres de type
```python
# ❌ Mauvais
def parse_data(data: dict) -> Recipe:

# ✅ Bon
def parse_data(data: dict[str, Any]) -> Recipe:
```

**3. Variable Naming** - Éviter la réutilisation de variables avec des types différents
```python
# ❌ Mauvais (mypy error)
for recipe in personal_recipes:  # PersonalRecipe
    ...
for recipe in api_recipes:  # Recipe (type différent!)
    ...

# ✅ Bon
for personal_recipe in personal_recipes:
    ...
for api_recipe in api_recipes:
    ...
```

### Commandes de validation (exécuter AVANT commit)

```bash
# 1. Lint check - zéro erreur
ruff check app/

# 2. Format check - code formaté
ruff format app/

# 3. Type check - zéro erreur (sauf modules ignorés)
mypy app/

# 4. Tests - tous passent
pytest tests/
```

### Configuration requise (pyproject.toml)

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = false
disallow_untyped_calls = false
```

---

## Best Practices

1. **Async by Default** - All route handlers and service methods use `async/await`
2. **Type Hints** - Always use type annotations
3. **Pydantic Models** - Validation via Pydantic, not manual checks
4. **Service Layer** - Business logic in services, not routes
5. **Environment Variables** - Never hardcode secrets, use `.env`
6. **Error Responses** - Consistent HTTP status codes and error messages
7. **API Versioning** - Prefix routes with `/api/v1` for future versions
8. **Dependency Injection** - Use FastAPI's `Depends()` for reusable dependencies
9. **Testing** - Minimum 80% coverage, test happy + error paths
10. **Documentation** - FastAPI auto-generates OpenAPI docs at `/docs`

## Performance

- Use `async` for I/O operations (database, external APIs)
- Implement pagination for list endpoints (limit/offset)
- Add response caching for expensive queries
- Use connection pooling for database (Supabase handles this)

## Deployment

```bash
# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Environment Variables Required**:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `JWT_SECRET`

---

**Token Count**: ~1200 tokens | **Reusable for**: Maison Epigenetic
