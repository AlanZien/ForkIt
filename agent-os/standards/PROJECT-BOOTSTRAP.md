# Project Bootstrap - ForkIt

**Version**: 1.0 | **Use for**: Initial project setup from scratch | **Token-Optimized**

## Stack Overview

- **Backend**: FastAPI + Python 3.11+
- **Mobile**: React Native + Expo 50+
- **Database**: Supabase (PostgreSQL + Auth)
- **Deployment**: Railway (backend), EAS (mobile)

## Backend Setup (FastAPI)

### 1. Initialize Project

```bash
# Create project directory
mkdir backend && cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-dotenv supabase pydantic[email] pydantic-settings bcrypt python-jose[cryptography] slowapi httpx

# Create requirements.txt
pip freeze > requirements.txt
```

### 2. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Settings & env vars
│   ├── database.py       # Supabase client
│   ├── models/           # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/          # API endpoints
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── utils/            # Helpers
│       ├── __init__.py
│       └── security.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### 3. Initial Files

**app/config.py**
```python
import secrets
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    app_name: str = "ForkIt API"
    debug: bool = False

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str = ""

    # Security
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # CORS - MUST be configured for production
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    @field_validator("jwt_secret", mode="before")
    @classmethod
    def generate_jwt_secret(cls, v: str) -> str:
        """Auto-generate secure JWT secret if not provided."""
        if not v:
            return secrets.token_urlsafe(64)
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors(cls, v):
        """Prevent wildcard CORS in production."""
        if isinstance(v, str):
            v = [origin.strip() for origin in v.split(",")]
        if "*" in v:
            raise ValueError("CORS wildcard '*' is not allowed. Specify explicit origins.")
        return v

    class Config:
        env_file = ".env"

settings = Settings()
```

**app/database.py**
```python
from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
```

**app/main.py**
```python
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routers import auth

# Logging - level based on debug mode
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ForkIt API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in prod
    redoc_url="/redoc" if settings.debug else None,
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - uses validated origins from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "ForkIt API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**app/rate_limit.py**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Rate limit constants - adjust per endpoint sensitivity
AUTH_RATE_LIMIT = "5/minute"      # Login, register
STRICT_RATE_LIMIT = "3/minute"   # Password reset, email verification
API_RATE_LIMIT = "60/minute"     # General API endpoints
```

**.env.example**
```bash
# Debug mode - set to false in production
DEBUG=true

# Supabase - get from https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT - leave empty to auto-generate, or set 64+ char secret
JWT_SECRET=

# CORS - comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
```

**.gitignore**
```
venv/
__pycache__/
*.pyc
.env
.pytest_cache/
htmlcov/
.coverage
```

### 4. Run Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs available at:
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

## Mobile Setup (React Native + Expo)

### 1. Initialize Project

```bash
# Create Expo project
npx create-expo-app@latest mobile --template blank-typescript

cd mobile

# Install dependencies
npx expo install expo-router expo-secure-store expo-image-picker
npm install zustand axios react-native-paper

# Install dev dependencies
npm install -D @types/react @types/react-native jest @testing-library/react-native
```

### 2. Project Structure

```
mobile/
├── app/                  # Expo Router screens
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/
│   │   ├── _layout.tsx
│   │   └── index.tsx
│   └── _layout.tsx
├── components/           # Reusable components
│   └── ui/
│       ├── Button.tsx
│       └── Input.tsx
├── services/             # API calls
│   └── api.ts
├── stores/               # Zustand stores
│   └── authStore.ts
├── constants/            # Theme, colors
│   └── theme.ts
├── hooks/                # Custom hooks
│   └── useAuth.ts
├── utils/                # Helper functions
│   └── validators.ts
├── __tests__/
├── app.json
├── package.json
├── tsconfig.json
└── .env.example
```

### 3. Initial Files

**app.json**
```json
{
  "expo": {
    "name": "ForkIt",
    "slug": "forkit",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "scheme": "forkit",
    "plugins": [
      "expo-router",
      "expo-secure-store"
    ],
    "platforms": ["ios", "android"],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourcompany.forkit"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourcompany.forkit"
    }
  }
}
```

**services/api.ts**
```typescript
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// Storage abstraction for cross-platform support
const storage = {
  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    }
    return SecureStore.getItemAsync(key);
  },
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      console.warn('[Storage] Using localStorage on web - not secure for tokens');
      localStorage.setItem(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },
  async deleteItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const token = await storage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: await this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: await this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: await this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: await this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }
}

export const api = new ApiClient(API_URL);
export { storage };
```

**constants/theme.ts**
```typescript
export const COLORS = {
  primary: '#FF6B6B',
  secondary: '#4ECDC4',
  background: '#FFFFFF',
  text: '#1F2937',
  border: '#E5E7EB',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};
```

**.env.example**
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000/api
```

### 4. Run Development

```bash
# Start Expo dev server
npx expo start

# Options:
# - Press 'i' for iOS simulator
# - Press 'a' for Android emulator
# - Scan QR code with Expo Go app for physical device
```

## Supabase Setup

### 1. Create Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your project URL and anon key

### 2. Database Schema

Create initial tables in SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### 3. Environment Variables

Add to backend `.env`:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...your-anon-key
```

Add to mobile `.env`:
```bash
EXPO_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...your-anon-key
```

## Testing Setup

### Backend (Pytest)

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Create pytest.ini
cat > pytest.ini << EOF
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
EOF

# Run tests
pytest
pytest --cov=app --cov-report=html
```

### Mobile (Jest)

```bash
cd mobile

# Install test dependencies
npm install -D jest @testing-library/react-native @testing-library/jest-native

# Run tests
npm test
npm test -- --coverage
```

## Git Setup

```bash
# Initialize git
git init

# Create .gitignore
cat > .gitignore << EOF
# Dependencies
node_modules/
venv/

# Environment
.env
.env.local

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Testing
coverage/
htmlcov/
.coverage

# Build
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# Initial commit
git add .
git commit -m "Initial project setup

- FastAPI backend with basic structure
- React Native + Expo mobile app
- Supabase database configuration
- Testing setup (Pytest + Jest)

🤖 Generated with Claude Code"
```

## Docker Setup

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml** (development)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./backend/app:/app/app  # Hot reload in dev
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Mandatory Tests per Feature

Each feature implementation MUST include these tests:

### Backend (minimum)
```
tests/
├── test_[feature].py           # API integration tests
└── test_services/
    └── test_[feature]_service.py  # Service unit tests
```

### Mobile (minimum)
```
__tests__/
├── stores/
│   └── [feature].test.ts       # Zustand store tests
└── services/
    └── [feature].test.ts       # API service tests
```

### Test Requirements
- [ ] **Happy path**: Main success scenario works
- [ ] **Auth required**: Endpoints return 401 without token
- [ ] **Validation**: Invalid input returns appropriate errors
- [ ] **Error handling**: Service failures are handled gracefully

## First Feature Checklist

After bootstrap, implement authentication:

- [ ] Backend: Auth endpoints (register, login, logout) with rate limiting
- [ ] Backend: JWT token generation & validation
- [ ] Backend: Password hashing with bcrypt
- [ ] Mobile: Login & Register screens
- [ ] Mobile: Auth state management (Zustand)
- [ ] Mobile: Secure token storage (SecureStore)
- [ ] **Tests: Backend auth service + API tests**
- [ ] **Tests: Mobile auth store + API tests**
- [ ] Supabase: RLS policies for user data

---

**Token Count**: ~2000 tokens | **Use once** at project start
