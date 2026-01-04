# CI/CD & DevOps Standards - ForkIt

**Version**: 1.0 | **Stack**: GitHub Actions + Docker + Railway/Fly.io | **Token-Optimized**

## Docker Setup

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Mobile Dockerfile (for EAS Build)
```dockerfile
# mobile/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Expo environment
ENV EXPO_NO_DOTENV=1
ENV NODE_ENV=production

CMD ["npx", "expo", "start"]
```

### Docker Compose (Development)
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./backend/app:/app/app
    command: uvicorn app.main:app --reload --host 0.0.0.0

  mobile:
    build: ./mobile
    ports:
      - "19000:19000"
      - "19001:19001"
      - "19002:19002"
    volumes:
      - ./mobile:/app
      - /app/node_modules
    environment:
      - EXPO_DEVTOOLS_LISTEN_ADDRESS=0.0.0.0
```

## GitHub Actions Workflows

### Backend CI/CD (Multi-Environment)
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI/CD

on:
  push:
    branches: [main, staging, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main, staging]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run Ruff (linting)
        run: uv run ruff check app/

      - name: Run Ruff (formatting)
        run: uv run ruff format --check app/

      - name: Run MyPy (type checking)
        run: uv run mypy app/

  # Deploy to Development
  deploy-dev:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: development

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Development
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend-dev
        env:
          DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
          SUPABASE_URL: ${{ secrets.DEV_SUPABASE_URL }}
          JWT_SECRET: ${{ secrets.DEV_JWT_SECRET }}

  # Deploy to Staging
  deploy-staging:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Staging
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend-staging
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
          SUPABASE_URL: ${{ secrets.STAGING_SUPABASE_URL }}
          JWT_SECRET: ${{ secrets.STAGING_JWT_SECRET }}

  # Deploy to Production (requires manual approval)
  deploy-prod:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.yourproject.com

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Production
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend-prod
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
          SUPABASE_URL: ${{ secrets.PROD_SUPABASE_URL }}
          JWT_SECRET: ${{ secrets.PROD_JWT_SECRET }}

      - name: Run smoke tests
        run: |
          curl --fail https://api.yourproject.com/health || exit 1
```

### Mobile CI/CD
```yaml
# .github/workflows/mobile-ci.yml
name: Mobile CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'mobile/**'
  pull_request:
    branches: [main]
    paths:
      - 'mobile/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: mobile/package-lock.json

      - name: Install dependencies
        run: |
          cd mobile
          npm ci

      - name: Run TypeScript check
        run: |
          cd mobile
          npx tsc --noEmit

      - name: Run tests
        run: |
          cd mobile
          npm test

      - name: Run ESLint
        run: |
          cd mobile
          npx eslint . --ext .ts,.tsx

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - name: Install dependencies
        run: |
          cd mobile
          npm ci

      - name: Build Android
        run: |
          cd mobile
          eas build --platform android --non-interactive --no-wait

      - name: Build iOS
        run: |
          cd mobile
          eas build --platform ios --non-interactive --no-wait
```

### Security Scan
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  backend-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit (Python security)
        run: |
          pip install bandit
          cd backend
          bandit -r app/

      - name: Run pip-audit
        run: |
          pip install pip-audit
          cd backend
          pip-audit

  mobile-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run npm audit
        run: |
          cd mobile
          npm audit --audit-level=moderate

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
```

## Environment Management

**For complete environment configuration, see:** `@agent-os/standards/global/environments.md`

### Environment Strategy

This project uses a **3-environment strategy**:

| Environment | Git Branch | Purpose | Deployment |
|-------------|-----------|---------|------------|
| **Development** | `develop` | Active development | Auto on push |
| **Staging** | `staging` | Pre-production testing | Auto on PR merge |
| **Production** | `main` | Live production | Manual approval |

**See full branching strategy:** `@agent-os/standards/global/git-workflow.md`

---

### GitHub Secrets by Environment

#### Development Secrets
Required for `develop` branch CI/CD:
- `DEV_DATABASE_URL` - Development database URL
- `DEV_SUPABASE_URL` - Dev Supabase project URL
- `DEV_SUPABASE_ANON_KEY` - Dev Supabase anon key
- `DEV_SUPABASE_SERVICE_KEY` - Dev Supabase service key
- `DEV_JWT_SECRET` - Development JWT secret (32+ chars)

#### Staging Secrets
Required for `staging` branch CI/CD:
- `STAGING_DATABASE_URL` - Staging database URL
- `STAGING_SUPABASE_URL` - Staging Supabase project URL
- `STAGING_SUPABASE_ANON_KEY` - Staging Supabase anon key
- `STAGING_SUPABASE_SERVICE_KEY` - Staging Supabase service key
- `STAGING_JWT_SECRET` - Staging JWT secret (32+ chars)

#### Production Secrets
Required for `main` branch CI/CD:
- `PROD_DATABASE_URL` - Production database URL
- `PROD_SUPABASE_URL` - Production Supabase project URL
- `PROD_SUPABASE_ANON_KEY` - Production Supabase anon key
- `PROD_SUPABASE_SERVICE_KEY` - Production Supabase service key
- `PROD_JWT_SECRET` - Production JWT secret (64+ chars, rotated monthly)
- `RAILWAY_TOKEN` - Railway deployment token (production)

#### Shared Secrets
Used across all environments:
- `EXPO_TOKEN` - Expo EAS token
- `APPLE_TEAM_ID` - Apple Developer Team ID
- `GOOGLE_SERVICES_JSON` - Base64 encoded google-services.json
- `SENTRY_AUTH_TOKEN` - Sentry authentication token

---

### Environment Files

**Project root contains:**
- `.env.dev.example` - Development environment template
- `.env.staging.example` - Staging environment template
- `.env.prod.example` - Production environment template

**Actual environment files (NEVER commit):**
```bash
.env.dev       # Local development config
.env.staging   # Staging config (CI/CD only)
.env.prod      # Production config (CI/CD only, or secrets manager)
```

**See `.env.*.example` files for complete configuration options.**

## Deployment Strategies

### Backend Deployment (Railway)
```yaml
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Alternative: Fly.io
```toml
# fly.toml
app = "forkit-api"
primary_region = "cdg"

[build]
  dockerfile = "backend/Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[env]
  PORT = "8000"

[[services.http_checks]]
  interval = "10s"
  timeout = "2s"
  grace_period = "5s"
  method = "GET"
  path = "/health"
```

### Mobile Deployment (EAS)
```json
// mobile/eas.json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "autoIncrement": true,
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.forkit.app"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      },
      "android": {
        "serviceAccountKeyPath": "./google-play-service-account.json",
        "track": "production"
      }
    }
  }
}
```

## Monitoring & Logging

### Backend Logging
```python
# app/utils/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter for production
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# Use in main.py
from app.utils.logging_config import setup_logging

logger = setup_logging()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request_started", extra={
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host
    })

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info("request_completed", extra={
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2)
    })

    return response
```

### Error Tracking (Sentry)
```python
# Backend - Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if not settings.debug:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.environment
    )
```

```typescript
// Mobile - Sentry integration
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  environment: __DEV__ ? 'development' : 'production',
  tracesSampleRate: 0.2,
  enableAutoSessionTracking: true,
});

export default Sentry.wrap(App);
```

## Performance Monitoring

```yaml
# Add Lighthouse CI for mobile web performance
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: treosh/lighthouse-ci-action@v10
        with:
          urls: |
            https://staging.forkit.app
          uploadArtifacts: true
```

## Database Migrations

```bash
# Using Alembic for backend migrations
# backend/alembic.ini configuration

# Run migrations in CI/CD
- name: Run migrations
  run: |
    cd backend
    alembic upgrade head
```

## Best Practices Checklist

### CI/CD
- [ ] Tests run on every PR
- [ ] Linting enforced before merge
- [ ] Code coverage tracked (min 80%)
- [ ] Security scans weekly
- [ ] Automated deployments to staging
- [ ] Manual approval for production
- [ ] Rollback strategy defined

### Docker
- [ ] Multi-stage builds for optimization
- [ ] Non-root user in containers
- [ ] Health checks configured
- [ ] Secrets via environment variables
- [ ] .dockerignore excludes unnecessary files

### Deployment
- [ ] Zero-downtime deployments
- [ ] Database migrations automated
- [ ] Environment variables validated
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented

### Monitoring
- [ ] Application logs structured (JSON)
- [ ] Error tracking with Sentry
- [ ] Performance monitoring active
- [ ] Uptime monitoring configured
- [ ] Alert thresholds defined

---

**Token Count**: ~1000 tokens | **Reusable for**: All projects
