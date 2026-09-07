# Technology Stack

This page documents the technologies, tools, and runtime requirements used by this template, so you know what you are adopting before you copy it into a real product.

## 🧰 Runtime & Languages

* **Language**: [Python](https://www.python.org/) `>=3.10`\
  The template targets modern Python. It runs on 3.10+ (the CI and Docker images use 3.10; local development often uses a newer interpreter that uv fetches automatically).
* **Package manager**: [uv](https://docs.astral.sh/uv/) `0.12.x`\
  Used for dependency resolution, environments, and running commands. The project is a **non-package application** declared with a PEP 621 `[project]` table (no build backend, so `uv` installs dependencies without packaging the repo).

## 🖥️ Web Framework & APIs

* **Framework**: [FastAPI](https://fastapi.dev/) (latest `0.x`, currently `0.141`)\
  Chosen for automatic OpenAPI documentation, pydantic-driven validation, and async support when needed.
* **ASGI**: [Uvicorn](https://www.uvicorn.org/)\
  The application server used both locally and inside Docker.
* **Typing layer**: [Pydantic v2](https://docs.pydantic.dev/) / `pydantic-settings`\
  Pydantic provides request/response models; `pydantic-settings` loads configuration from `.env`.

## 🗄️ Data Layer

* **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) `2.0` (`2.0.35`) using the **classic** `Column` mapping style.
* **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) `1.13`.
* **Database**: [PostgreSQL](https://www.postgresql.org/) `16.2` (Docker image `postgres:16.2-alpine`).
* **Driver**: `psycopg2-binary`.

## 🧩 Application Libraries

| Purpose               | Library                                        | Notes                                                    |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Authentication tokens | [PyJWT](https://pyjwt.readthedocs.io/)         | HMAC-signed JSON Web Tokens                              |
| Password hashing      | stdlib `hashlib`                               | PBKDF2-HMAC-SHA256, 600k iterations, no extra dependency |
| Rate limiting         | [slowapi](https://github.com/laurentS/slowapi) | in-memory backend                                        |
| Structured logging    | [structlog](https://www.structlog.org/)        | console & JSON renderers                                 |
| Magic                 | FastAPI `[standard]` extras                    | httpx, jinja2, python-multipart, etc.                    |

## 🛠️ Development & Quality Tooling

| Purpose              | Tool                                         | Notes                                         |
| -------------------- | -------------------------------------------- | --------------------------------------------- |
| Linting & formatting | [Ruff](https://docs.astral.sh/ruff/) `0.6.x` | configured for 3.10, 120 char lines, auto-fix |
| Testing              | [pytest](https://docs.pytest.org/) `9.x`     | against a throwaway PostgreSQL test database  |
| Pre-commit           | [pre-commit](https://pre-commit.com/)        | runs Ruff on every commit                     |
| CI                   | GitHub Actions                               | see [Deployment](deployment.md)               |

## ☁️ Containerisation & Deployment

* **Docker** `compose.yaml` runs two services:
  * `fastapi` — built from the `Dockerfile`, serves the app on host port `8080`.
  * `postgres` — PostgreSQL 16, host port `5432`.
* Official image bases: `python:3.10-alpine3.20`.
* uv manager pin: the Dockerfile installs `uv==0.12.10` and installs deps from the committed `uv.lock` (`uv sync --no-dev --frozen`).

## ✅ Compatibility matrix

| Component  | Constraint / resolved | Notes                   |
| ---------- | --------------------- | ----------------------- |
| Python     | `>=3.10`              | CI + Docker use 3.10    |
| FastAPI    | `>=0.141`            | `fastapi[standard]`, latest |
| SQLAlchemy | `2.0.x`              | classic `Column` models |
| Alembic    | `1.13+`               |                         |
| Pydantic   | `2.9+`                | `ConfigDict` era        |
| structlog  | `26.x`                |                         |
| slowapi    | `0.1.x`               |                         |
| PyJWT      | `2.13+`               |                         |
| pytest     | `9.x`                 |                          |
| Ruff       | `0.6.x`               |                          |
| pre-commit | `4.x`                 |                          |
| starlette  | `>=0.46` (via FastAPI) | ASGI toolkit            |

> ℹ️ Precise locked versions are pinned in `uv.lock`. View them with `uv tree`.

> 💡 **Keeping it evergreen**: run `uv sync --upgrade` (or `uv lock --upgrade`) to refresh dependencies within the ranges above. If a major library (FastAPI, Pydantic, SQLAlchemy) jumps a version, re-run `uv run pytest` and `uv run ruff` to catch breaking changes before committing.

## 📌 Notes

* This template avoids frameworks the original author did not need (no async SQLAlchemy, no Redis cache by default). The in-memory rate limiter and sync SQLAlchemy keep the dependency surface small.
* The document will evolve alongside the repository.
