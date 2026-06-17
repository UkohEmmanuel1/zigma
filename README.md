# Zigma Backend

AI-powered stock/crypto trading platform backend API.

Built with **Django 6.0**, **Django REST Framework**, and **Celery**.

## Architecture

```
zigma_backend/
├── app/                # Django project config (ASGI, WSGI, URLs)
├── apps/
│   ├── ai_engine/      # AI trading signals & predictions
│   ├── market_data/    # Market data ingestion & processing
│   ├── notifications/  # User alerts & notifications
│   ├── shared/         # Shared utilities & common code
│   ├── trading/        # Order execution & trade management
│   ├── users/          # Authentication & user profiles
│   └── wallet/         # Digital wallet & balance management
├── zigma_core/         # Core settings (base/dev) & Celery config
└── requirements/
    └── base.txt        # Python dependencies
```

## Prerequisites

- Python 3.12
- PostgreSQL 16 (production) or SQLite (local development)
- Redis 7 (for Celery task queue)

## Quick Start (Local Development)

```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements\base.txt

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A zigma_core worker --loglevel=info
```

## Docker

```bash
docker-compose up --build
```

Starts PostgreSQL, Redis, Django API (port 8000), and Celery worker.

## Authentication

Zigma uses **Django-native JWT authentication** via `djangorestframework-simplejwt`. All user management (registration, login, password management) is handled entirely by Django — no external auth provider required.

### Auth flow

```
Client                          Django API
  │                                │
  ├── POST /api/v1/auth/register/  │  Create user, return JWT
  ├── POST /api/v1/auth/login/     │  Verify credentials, return JWT
  ├── POST /api/v1/auth/token/refresh/  │  Refresh access token
  ├── GET  /api/v1/auth/me/        │  Return current user (Bearer token)
  ├── POST /api/v1/auth/change-password/ │  Update password (authenticated)
  ├── POST /api/v1/auth/forgot-password/ │  Generate reset token
  └── POST /api/v1/auth/reset-password/  │  Reset password with token
```

### Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register/` | No | Create account, returns JWT |
| `POST` | `/api/v1/auth/login/` | No | Login, returns JWT |
| `POST` | `/api/v1/auth/token/refresh/` | No | Refresh an expired access token |
| `GET` | `/api/v1/auth/me/` | Yes | Return current user `{ id, email }` |
| `POST` | `/api/v1/auth/change-password/` | Yes | Change current password |
| `POST` | `/api/v1/auth/forgot-password/` | No | Get a password reset token |
| `POST` | `/api/v1/auth/reset-password/` | No | Reset password with token |

### User model

The `User` model (`apps/users/models.py`) extends Django's `AbstractBaseUser` and uses **email** as the unique identifier (no username field):

| Field | Type |
|---|---|
| `id` | UUID (auto-generated) |
| `email` | EmailField (unique) |
| `password` | Hashed (handled by Django) |
| `is_active` | Boolean |
| `is_staff` | Boolean |
| `created_at` | DateTime |
| `updated_at` | DateTime |

### JWT configuration

- **Access token**: 1 hour
- **Refresh token**: 7 days
- **Algorithm**: HS256 (signed with Django's `SECRET_KEY`)
- **Auth header**: `Authorization: Bearer <token>`

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | Django secret key (used for JWT signing) |
| `DEBUG` | `False` | Debug mode |
| `USE_LOCAL_DB` | `False` | `True` uses SQLite, `False` uses PostgreSQL |
| `DB_NAME` | `postgres` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DB_HOST` | — | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |

## CI/CD

GitHub Actions runs on push to `main`/`develop` and PRs to `main`:
- Sets up PostgreSQL 16 + Redis 7
- Installs dependencies
- Runs migrations
- Runs tests

## Status

Early development — apps are scaffolded with authentication implemented.
