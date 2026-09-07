# Project Structure

Understand where code lives, why the folders exist, and the package rules that keep a FastAPI app consistent as it grows.

## The big idea

The layout follows [zhanymkanov's consistent and predictable structure](https://github.com/zhanymkanov/fastapi-best-practices#1-project-structure-consistent--predictable), adapted to uv and Docker. The rule is: each domain gets its own folder, shared code lives in `core`, and the module that does a thing also owns its models, schemas, and endpoints.

## Repository layout

```
fastapi-template
├── .github/workflows/ci.yml      # CI: ruff and pytest against PostgreSQL
├── .pre-commit-config.yaml       # pre-commit: ruff lint and format
├── alembic/                      # migration scripts, env.py, versions/
├── alembic.ini                   # Alembic configuration
├── compose.yaml                  # Docker services: fastapi and postgres
├── Dockerfile                    # API image, runtime deps only
├── .dockerignore                 # files excluded from the Docker build context
├── docs/                         # this GitBook documentation site
├── src/                          # application source
├── tests/                        # pytest suite, mirrors src layout
├── .env.example                  # documented env variables
├── pyproject.toml                # uv manifest plus Ruff and pytest config
├── uv.lock
└── README.md
```

## Inside `src/`

```
src/
├── main.py            # builds the FastAPI app: middleware, routers, error handlers
├── pagination.py      # reusable cursor pagination and Page[T]
├── __init__.py
├── core/              # cross-cutting concerns, see the Core cross-cutting guide
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   ├── middleware.py
│   ├── rate_limit.py
│   ├── exceptions.py
│   └── schema.py
├── health/            # /healthz and /readyz probes
├── auth/              # domain package: user management and JWT auth
├── package/           # copy-paste example: a CRUD todos API
└── aws/               # scaffold for an external-service client
```

## The package convention

Each domain folder declares up to eight responsibilities.

| File              | What it holds                                           |
| ----------------- | ------------------------------------------------------- |
| `config.py`       | package-local environment configuration, extends `core` |
| `dependencies.py` | FastAPI dependencies and guards for this router         |
| `exceptions.py`   | package-specific exceptions                             |
| `models.py`       | SQLAlchemy database models                              |
| `router.py`       | the FastAPI `APIRouter` with all endpoints              |
| `schemas.py`      | Pydantic request and response models                    |
| `service.py`      | business logic the endpoints orchestrate                |
| `utils.py`        | non-business helper functions                           |

The `auth` package is the reference implementation. `package` is a minimal CRUD example for `todos`, easiest to copy when you add a new domain.

### Rules that keep it predictable

1. Keep global and common modules at the `src/` top level. `pagination.py`, the glue in `main.py`, and shared code under `src/core/`.
2. When crossing package boundaries, import with an explicit module name:
   ```python
   from src.auth import config as auth_config
   from src.core.database import db_dependency
   from src.pagination import Page
   ```
   Siblings in the same package import normally.
3. `router.py` stays thin. It reads requests, calls `service.py`, and returns schemas.
4. Keep `models.py` and `schemas.py` separate. The database row is not the wire shape.

## Scope rules

The `aws/` package is empty on purpose. Its comments show the intended shape for external-service communication: `client.py` for the remote client, plus `constants.py`, `schemas.py`, `config.py`, `utils.py`, and `exceptions.py`.

Separating `core/` from a domain package prevents imports between unrelated endpoints. Copy `package/`, rename it, and you have a working skeleton.

## Where a concern lives

| To do this                         | Look here                                       |
| ---------------------------------- | ----------------------------------------------- |
| Add a route protected by auth      | `src/<package>/router.py` and `dependencies.py` |
| Model a new table                  | `src/<package>/models.py`, then a migration     |
| Tune logging, rate limits, or CORS | `src/core/`                                     |
| Understand how the app starts      | `src/main.py`                                   |
| Write a JSON API envelope          | `src/pagination.py` and `schemas.py`            |

The rest of the structure is documented where it is used: `alembic/` and `docs/` here, `tests/` in [Testing](testing.md), and `pyproject.toml` in [Conventions](conventions.md).
