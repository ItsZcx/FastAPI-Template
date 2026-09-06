# FastAPI Template

A production-oriented FastAPI template that integrates Poetry, SQLAlchemy, Alembic, PostgreSQL, and Docker, plus the cross-cutting features every backend needs:

- **Auth** — JWT-based user management (register, login, `/me`)
- **Rate limiting** — slowapi (in-memory) on sensitive endpoints
- **CORS & security headers** — env-driven, conservative defaults
- **Structured logging** — structlog with console/JSON output and request IDs
- **Health checks** — `/healthz` (liveness) and `/readyz` (DB readiness)
- **Cursor pagination** — reusable `Page[T]` envelope + keyset helper
- **Testing** — pytest with an isolated PostgreSQL test database and per-test rollback
- **Pre-commit & CI** — Ruff + GitHub Actions

Docker is set up to run both a FastAPI and PostgreSQL container.

## Table of Contents
- [Project Structure](#project-structure)
- [Template Setup](#template-setup)
- [Features](#features)
    - [Authentication](#authentication)
    - [Health checks](#health-checks)
    - [Pagination](#pagination)
    - [Rate limiting](#rate-limiting)
    - [Logging & request IDs](#logging--request-ids)
    - [CORS & security headers](#cors--security-headers)
- [Testing](#testing)
- [Pre-commit](#pre-commit)
- [CI/CD](#cicd)

## Project Structure

This project structure is based on [project-structure-consistent--predictable](https://github.com/zhanymkanov/fastapi-best-practices#1-project-structure-consistent--predictable) by zhanymkanov, modified to use Poetry and Docker. Cross-cutting concerns live in `src/core/`.

```
fastapi-template
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions: ruff + pytest
├── alembic/
├── src
│   ├── core/                     # cross-cutting concerns
│   │   ├── config.py               # env loading + global settings
│   │   ├── database.py             # engine, session, Base, pooling
│   │   ├── exceptions.py           # global exceptions
│   │   ├── logging.py              # structlog setup (console/JSON)
│   │   ├── middleware.py           # request ID, security headers, CORS
│   │   ├── rate_limit.py           # slowapi limiter
│   │   └── schema.py               # global pydantic models
│   ├── auth                      # package
│   │   ├── config.py               # local configs
│   │   ├── dependencies.py         # auth router dependencies (get_current_user)
│   │   ├── exceptions.py           # package-specific errors
│   │   ├── models.py               # database models
│   │   ├── router.py               # auth endpoints
│   │   ├── schemas.py              # pydantic models
│   │   ├── service.py              # business logic
│   │   └── utils.py                # password hashing + JWT helpers
│   ├── health
│   │   └── router.py               # /healthz and /readyz
│   ├── package                   # copy-paste example package (todos)
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── __init__.py
│   ├── main.py                   # app init: middleware, routers, error handlers
│   └── pagination.py             # cursor pagination + Page[T]
├── tests/
│   ├── auth/
│   ├── package/
│   ├── conftest.py               # test DB, TestClient, rollback fixtures
│   ├── test_health.py
│   └── ...
├── .env.example                  # variables used/needed in .env
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md
```

1. Store all domain directories inside `src`
   1. `src/` — highest level of an app; common infra lives in `src/core/`
   2. `src/main.py` — root of the project, inits the FastAPI app

2. Each package has its own router, schemas, models, etc.
   1. `config.py` — e.g. specific env vars
   2. `dependencies.py` — router dependencies
   3. `exceptions.py` — module-specific exceptions
   4. `models.py` — database models
   5. `router.py` — core of each module with all the endpoints
   6. `schemas.py` — pydantic models
   7. `service.py` — module-specific business logic
   8. `utils.py` — non-business logic functions

3. When a package needs services, dependencies, or configs from another package, import them with an explicit module name:
```python
from src.auth import config as auth_config
from src.notifications import service as notification_service
```

## Template Setup

### 1. Install Dependencies with Poetry
Ensure [Poetry](https://python-poetry.org) is installed.

```bash
poetry install
```

### 2. Set Up Environment Variables with dotenv
Environment variables are handled via a `.env` file. Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Key variables:

| Variable | Purpose |
| --- | --- |
| `DB_URL` | PostgreSQL connection string (in-container hostname is `fastapi-postgres`) |
| `ALEMBIC_DB_URL` | PostgreSQL connection string for Alembic (uses localhost when run from the host) |
| `AUTH_SECRET_KEY` | Secret used to sign JWTs (e.g. `openssl rand -hex 32`) |
| `ENVIRONMENT` | `development` or `production` (enables HSTS in production) |
| `LOG_LEVEL` / `LOG_FORMAT` | Log level and format (`console` or `json`) |
| `CORS_ORIGINS` | Comma-separated allowed origins (empty = CORS disabled) |
| `TEST_DB_URL` | Test database used by pytest |

### 3. Run the Template with Docker

```bash
docker compose up -d
```

To stop (add `--volumes` to remove persistent PostgreSQL data):

```bash
docker compose down
```

### 4. Set Up Alembic Database Migrations
Alembic files are included as references. For a fresh project, remove and reinitialize them:

```bash
rm -rf alembic/ alembic.ini
poetry run alembic init alembic
```

Configure `alembic/env.py` to import **all** models (even if unused) so autogenerate sees them, and set `target_metadata = Base.metadata`. Then create and apply migrations:

```bash
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
```

## Features

### Authentication
Endpoints under `/auth`:

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create a user (email, username, password). Rate-limited. |
| POST | `/auth/login` | Exchange credentials for a Bearer JWT. Rate-limited. |
| GET | `/auth/me` | Return the authenticated user. |
| PATCH | `/auth/me` | Update username/password. |
| DELETE | `/auth/me` | Delete the authenticated user. |

Passwords are hashed with PBKDF2-HMAC-SHA256 (stdlib, 600k iterations, per-user salt). Tokens are signed with `AUTH_SECRET_KEY`.

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"supersecret123"}' | jq -r .access_token)

curl http://localhost:8080/auth/me -H "Authorization: Bearer $TOKEN"
```

### Health checks
- `GET /healthz` — liveness probe (always `{"status": "ok"}`).
- `GET /readyz` — readiness probe; runs `SELECT 1` against PostgreSQL and returns 503 if the DB is unreachable.

### Pagination
`src/pagination.py` provides a generic `Page[T]` envelope and `apply_cursor()` for keyset/cursor pagination over a monotonically increasing field (e.g. `id`). See `GET /todos` for a working example:

```bash
curl 'http://localhost:8080/todos?limit=2'
# {"items": [...], "next_cursor": "Mg=="}
curl 'http://localhost:8080/todos?limit=2&cursor=Mg=='
```

### Rate limiting
`src/core/rate_limit.py` sets up a slowapi `Limiter`. `/auth/login` and `/auth/register` are limited by default. The default backend is **in-memory and per-process** — swap the `key_func` for a Redis-backed implementation if you run multiple workers.

### Logging & request IDs
`src/core/logging.py` configures structlog with two formats:

- `LOG_FORMAT=console` — human-readable output for local development
- `LOG_FORMAT=json` — single-line JSON for log aggregators (Datadog, Loki, CloudWatch, ...)

Every request gets an `X-Request-ID` (propagated if supplied, generated otherwise), echoed on the response and bound into the request's log context:

```python
from src.core.logging import get_logger

logger = get_logger(__name__)
logger.info("something happened", extra_field="value")
```

### CORS & security headers
- **CORS** — set `CORS_ORIGINS` to a comma-separated list of allowed origins (empty disables CORS).
- **Security headers** — every response gets `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy`. `Strict-Transport-Security` is added only when `ENVIRONMENT=production`.

## Testing

Tests run against a dedicated PostgreSQL database (`TEST_DB_URL`), created automatically by `tests/conftest.py`. Each test runs inside a transaction that is rolled back, so tests are isolated.

```bash
# requires the postgres container to be running
docker compose up -d postgres
poetry run pytest
```

## Pre-commit

```bash
poetry run pre-commit install
```

Runs Ruff (lint + format) on every commit.

## CI/CD

`.github/workflows/ci.yml` runs Ruff lint/format checks and pytest against a PostgreSQL service on every push and pull request.
