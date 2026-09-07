# Technology Stack

This page lists the technologies, tools, and runtime requirements the template adopts. Read it before you copy the template into a real product.

## Runtime and languages

* **Python** `>=3.10`. CI and Docker run 3.10. Local development often uses a newer interpreter that uv fetches.
* **uv** `0.12.x` for dependency resolution, environments, and running commands. The project is a non-package application declared with a PEP 621 `[project]` table. There is no build backend, so uv installs dependencies without packaging the repo.

## Web framework and APIs

* **FastAPI**, latest `0.x`, currently `0.141`. It provides OpenAPI documentation, pydantic-driven validation, and async support.
* **Uvicorn** is the application server, used locally and in Docker.
* **Pydantic v2** and `pydantic-settings`. Pydantic provides request and response models. `pydantic-settings` loads configuration from `.env`.

## Data layer

* **SQLAlchemy** 2.0 with the classic `Column` mapping style.
* **Alembic** 1.13 for migrations.
* **PostgreSQL** 16.2, from the `postgres:16.2-alpine` Docker image.
* **psycopg2-binary** is the driver.

## Application libraries

| Purpose               | Library                                        | Notes                                                    |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Authentication tokens | [PyJWT](https://pyjwt.readthedocs.io/)         | HMAC-signed JSON Web Tokens                              |
| Password hashing      | stdlib `hashlib`                               | PBKDF2-HMAC-SHA256, 600k iterations, no extra dependency |
| Rate limiting         | [slowapi](https://github.com/laurentS/slowapi) | in-memory backend                                        |
| Structured logging    | [structlog](https://www.structlog.org/)        | console and JSON renderers                               |
| Extras                | FastAPI `[standard]`                           | httpx, jinja2, python-multipart, and more                |

## Development and quality tooling

| Purpose                | Tool                                         | Notes                                         |
| ---------------------- | -------------------------------------------- | --------------------------------------------- |
| Linting and formatting | [Ruff](https://docs.astral.sh/ruff/) `0.6.x` | configured for 3.10, 120-char lines, auto-fix |
| Testing                | [pytest](https://docs.pytest.org/) `9.x`     | against a throwaway PostgreSQL test database  |
| Pre-commit             | [pre-commit](https://pre-commit.com/)        | runs Ruff on every commit                     |
| CI                     | GitHub Actions                               | see [Deployment](deployment.md)               |

## Containerisation and deployment

`compose.yaml` runs two services:

* `fastapi`, built from the `Dockerfile`. It serves the app on host port `8080`.
* `postgres`, PostgreSQL 16 on host port `5432`.

The base image is `python:3.10-alpine3.20`. The Dockerfile installs `uv==0.12.10` and installs dependencies from `uv.lock` with `uv sync --no-dev --frozen`.

## Compatibility matrix

| Component  | Constraint | Notes                              |
| ---------- | ---------- | ---------------------------------- |
| Python     | `>=3.10`   | CI and Docker run 3.10             |
| FastAPI    | `>=0.141`  | `fastapi[standard]`, tracks latest |
| SQLAlchemy | `2.0.x`    | classic `Column` models            |
| Alembic    | `1.13+`    |                                    |
| Pydantic   | `2.9+`     | `ConfigDict` style                 |
| structlog  | `26.x`     |                                    |
| slowapi    | `0.1.x`    |                                    |
| PyJWT      | `2.13+`    |                                    |
| pytest     | `9.x`      |                                    |
| Ruff       | `0.6.x`    |                                    |
| pre-commit | `4.x`      |                                    |
| starlette  | `>=0.46`   | via FastAPI                        |

The lock file pins the exact versions. Run `uv tree` to see them.

To refresh dependencies within the ranges above, run `uv sync --upgrade` or `uv lock --upgrade`. If a major library jumps a version, run `uv run pytest` and `uv run ruff` before committing.

## Notes

The template avoids frameworks the original author did not need. There is no async SQLAlchemy and no Redis cache. The in-memory rate limiter and sync SQLAlchemy keep the dependency surface small.
