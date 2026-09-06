# Technology Stack

This page documents the technologies, tools, and runtime requirements used by this template, so you know what you are adopting before you copy it into a real product.

## 🧰 Runtime & Languages

* **Language**: [Python](https://www.python.org/) `^3.10`\
  The template targets modern Python. It is fully compatible with 3.10+ (the CI image and Docker image use 3.10; the build has also been validated on newer versions).
* **Package manager**: [Poetry](https://python-poetry.org/) `2.x`\
  Used for dependency resolution and virtual environments. The `pyproject.toml` declares a non-package project (`package-mode = false`).

## 🖥️ Web Framework & APIs

* **Framework**: [FastAPI](https://fastapi.dev/) `0.115`\
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
| Linting & formatting | [Ruff](https://docs.astral.sh/ruff/) `0.6.7` | configured for 3.10, 120 char lines, auto-fix |
| Testing              | [pytest](https://docs.pytest.org/) `9.x`     | against a throwaway PostgreSQL test database  |
| Pre-commit           | [pre-commit](https://pre-commit.com/)        | runs Ruff on every commit                     |
| CI                   | GitHub Actions                               | see [Deployment](deployment.md)               |

## ☁️ Containerisation & Deployment

* **Docker** `compose.yaml` runs two services:
  * `fastapi` — built from the `Dockerfile`, serves the app on host port `8080`.
  * `postgres` — PostgreSQL 16, host port `5432`.
* Official image bases: `python:3.10-alpine3.20`.
* Poetry image pin: the Dockerfile installs Poetry `2.x` (the lock file is Poetry 2.x format).

## ✅ Compatibility matrix

| Component  | Version (as authored) | Notes                   |
| ---------- | --------------------- | ----------------------- |
| Python     | `^3.10`               | CI + Docker use 3.10    |
| FastAPI    | `0.115.0`             |                         |
| starlette  | `0.38.5`              |                         |
| SQLAlchemy | `2.0.35`              | classic `Column` models |
| Alembic    | `1.13.2`              |                         |
| Pydantic   | `2.9.2`               | `ConfigDict` era        |
| structlog  | `26.x`                |                         |
| slowapi    | `0.1.10`              |                         |
| PyJWT      | `2.13.0`              |                         |
| pytest     | `9.x`                 |                         |
| Ruff       | `0.6.7`               |                         |

> 💡 **Keeping it evergreen**: run `poetry update` to refresh dependencies, exactly as the README advises. If a major library (FastAPI, Pydantic, SQLAlchemy) jumps a version, re-run `pytest` and `ruff` to catch breaking changes before committing.

## 📌 Notes

* This template avoids frameworks the original author did not need (no async SQLAlchemy, no Redis cache by default). The in-memory rate limiter and sync SQLAlchemy keep the dependency surface small.
* The document will evolve alongside the repository.
