# ForkIt 🍴

Application mobile de planification de repas familiaux.

## Stack Technique

- **Mobile**: React Native + Expo
- **Backend**: FastAPI (Python)
- **Base de données**: Supabase (PostgreSQL + Auth)

## Structure du Projet

```
ForkIt/
├── backend/          # API FastAPI
├── mobile/           # App React Native/Expo
├── agent-os/         # Specs et documentation
└── .env.example      # Template de configuration
```

## Installation

### 1. Configuration

```bash
# Copier le template de configuration
cp .env.example .env

# Éditer avec tes valeurs Supabase et Notion
nano .env
```

### 2. Backend

```bash
cd backend

# Installer les dépendances (avec uv)
uv sync

# Lancer le serveur de développement
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Mobile

```bash
cd mobile

# Installer les dépendances
npm install

# Lancer Expo
npx expo start
```

## Tests

```bash
# Backend
cd backend
uv run pytest

# Avec couverture
uv run pytest --cov=app
```

## Variables d'Environnement

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | URL de ton projet Supabase |
| `SUPABASE_ANON_KEY` | Clé anonyme Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Clé service (backend uniquement) |
| `JWT_SECRET` | Secret pour signer les JWT (généré auto en dev) |
| `NOTION_TOKEN` | Token d'intégration Notion (optionnel) |

## Déploiement

### Docker (Backend)

```bash
cd backend
docker build -t forkit-api .
docker run -p 8000:8000 --env-file ../.env forkit-api
```

## Licence

Privé - Tous droits réservés
