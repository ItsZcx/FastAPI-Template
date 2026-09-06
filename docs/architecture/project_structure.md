# Project Structure

> 🎯 **Goal**: understand exactly where code lives, why the folders exist, and the "package" rules that keep a FastAPI app consistent as it grows.

## 🌳 The big idea

The layout is based on [zhanymkanov/fastapi-best-practices → consistent & predictable structure](https://github.com/zhanymkanov/fastapi-best-practices#1-project-structure-consistent--predictable), adapted to uv + Docker. The motto:

> **Every domain gets its own folder; everything reusable lives in `core`; the module that "does a thing" also owns its models, schemas and endpoints.**

## 🗂️ Repository layout

```
fastapi-template
├── .github/workflows/ci.yml      # CI: ruff + pytest against PostgreSQL
├── .pre-commit-config.yaml       # pre-commit: ruff lint + format
├── alembic/                      # migration scripts + env.py + versions/
├── alembic.ini                   # Alembic entry configuration
├── compose.yaml                  # Docker services: fastapi + postgres
├── Dockerfile                    # API image (runtime deps only)
├── .dockerignore                 # files excluded from the Docker build context
├── docs/                         # this GitBook documentation site
├── src/                          # source of the application
├── tests/                        # pytest suite (mirrors src package layout)
├── .env.example                  # documented env variables
├── pyproject.toml                # uv manifest + Ruff + pytest config
├── uv.lock
└── README.md
```

## 📂 Inside `src/`

```
src/
├── main.py            # builds the FastAPI app: middleware, routers, error handlers
├── pagination.py      # reusable cursor pagination + Page[T]
├── __init__.py
├── core/              # cross-cutting concerns (see Core Cross-cutting guide)
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   ├── middleware.py
│   ├── rate_limit.py
│   ├── exceptions.py
│   └── schema.py
├── health/            # /healthz & /readyz probes
├── auth/              # domain package — user management + JWT auth
├── package/           # example (copy-paste) package — a CRUD "todos" API
└── aws/               # (scaffold) blank package for an external-service client
```

## 🧩 The package convention

Each **domain** folder consistently declares up to eight responsibilities:

| File              | What it holds                                            |
| ----------------- | -------------------------------------------------------- |
| `config.py`       | package-local environment configuration (extends `core`) |
| `dependencies.py` | FastAPI dependencies / guards for this router            |
| `exceptions.py`   | package-specific exceptions                              |
| `models.py`       | SQLAlchemy database models                               |
| `router.py`       | the FastAPI `APIRouter` with all endpoints               |
| `schemas.py`      | Pydantic request/response models                         |
| `service.py`      | business logic (what the endpoints orchestrate)          |
| `utils.py`        | non-business helper functions (pure functions)           |

> 🔍 The reference implementation lives in the **`auth`** package; **`package`** is a minimal CRUD example (`todos`) that is the easiest to copy when adding a new domain.

### Rules that keep it predictable

1. Keep **global/common** modules at `src/` top level:
   `src/pagination.py`, glue in `src/main.py`, and cross-cutting shared code under `src/core/`.
2. When crossing package boundaries, import with an **explicit module name**:
   ```python
   from src.auth import config as auth_config
   from src.core.database import db_dependency
   from src.pagination import Page
   ```
   (same-package siblings can import normally.)
3. `router.py` stays thin: it reads requests, calls `service.py`, and returns schemas.
4. `models.py`/`schemas.py` are **separate** — never confuse the DB row with the wire shape.

## 🔄 Scope rules (trade-offs)

The `aws/` package is empty on purpose. Its comments show the intended shape for **external-service communication** (`client.py` for the remote client, `constants.py`, `schemas.py`, `config.py`, `utils.py`, `exceptions.py`).

> Clear separation of `core/` (shared) vs a domain package (e.g. `auth/`) prevents "kitchen-sink" imports between unrelated endpoints. Copy `package/`, rename it, and you get a working skeleton in minutes.

## 🧠 Where each concern the docs describe lives

| "How do I..."                     | Look here                                           |
| --------------------------------- | --------------------------------------------------- |
| Add a new route protected by auth | `src/<package>/router.py` + `dependencies.py`       |
| Model a new table                 | `src/<package>/models.py` then a migration          |
| Tune logging / rate limits / CORS | `src/core/*`                                        |
| Understand how the app starts     | read `src/main.py` and the docs you are reading now |
| Write a JSON API envelope         | `src/pagination.py` and `schemas.py`                |

> 📁 Not listed here but referenced all over: `alembic/` and `docs/` (this site), `tests/` and `pyproject.toml` (covered in [Conventions](conventions.md) and [Testing](testing.md)).
