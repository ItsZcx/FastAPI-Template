# Conventions

This page records the **rules of the codebase** — the ones enforced by tooling and the conventions the maintainer expects. Following them keeps contributions uniform.

> ✅ The repo enforces the *toolable* parts automatically with **Ruff** (lint + format) and in **CI**. The rest are judgment calls a reviewer will look for.

## ⌨️ Git commit style

This repository uses **Conventional Commits** with a type prefix (found in `git log` and encouraged for contributors):

```
<type>(<scope>): short description
```

Examples actually present in the history and their meaning:

| Message                                             | Type meaning                      |
| --------------------------------------------------- | --------------------------------- |
| `feat: add template auth`                           | new feature                       |
| `fix: Docker errors x2`                             | bug fix                           |
| `docs(api): update README with usage examples`      | documentation change (with scope) |
| `feat: manage env variables with pydantic-settings` | new feature                       |

Common types: `feat`, `fix`, `refactor`, `style`, `test`, `docs`, `chore`, `infra`. Scope (e.g. `auth`, `db`, `docker`) is optional and clarifies the area changed.

## 🧹 Import style (enforced by Ruff `isort`)

* One import per line, alphabetically ordered.
* Within a package, standard library / third-party / first-party are grouped (Ruff handles ordering).

```python
from starlette import status

from src.core.database import db_dependency
from src.package.models import Todos
```

## 🐦 Pydantic v2 (not the deprecated v1 style)

* Use `model_config = ConfigDict(...)` — **not** `class Config`.
* For read models backed by ORM objects use `ConfigDict(from_attributes=True)`.
* Provide example payloads via `json_schema_extra` so Swagger shows realistic values.
* Read request data with `.model_dump()` (never v1 `.dict()`).

Example (from `src/package/schemas.py`):

```python
class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

## 🐘 SQLAlchemy style

* Models are declared **classic-style** with `Column(...)` and inherit `Base` from `src.core.database` (not a bare import from SQLAlchemy).
* Use `db_dependency` typed sessions in endpoints; never hand-roll a session.
* Unique fields get `unique=True`; list lookups commonly get `index=True`.
* Timestamps use `DateTime(timezone=True)` with `server_default=func.now()` and `onupdate`.

## 🗂️ Naming & types

* `python = "^3.10"` — feel free to use modern syntax (`str | None`, `list[Todo]`, `Annotated[...]`).
* Type-annotate function signatures; the codebase leans into `Annotated` for dependencies (e.g. `db_dependency`, `current_user_dependency`).
* Follow Python naming: modules lowercase, functions `snake_case`, models/schemas/classes `PascalCase`.

## 🧩 Error handling

Custom domain errors are small classes raised in `service.py` and mapped to HTTP in **one place**.

* Auth uses `AuthError` subclasses and maps them centrally in `src/main.py` (see [Health Checks & Error Handling](health_and_errors.md)).
* Simpler endpoints may raise `HTTPException` directly (the `package/` example does), but large domains should prefer explicit exceptions.

## 📍 Endpoint conventions

* Router prefix + tag set the URL and Swagger grouping:
  ```python
  router = APIRouter(prefix="/todos", tags=["Todos"])
  ```
* Use `status.HTTP_204_NO_CONTENT` etc. from `starlette` for response codes.
* Read models are returned through `response_model=...` so hashed/password fields never leak.

## 📄 Code formatting (Ruff)

Key `pyproject.toml` [ruff] settings you inherit:

* `target-version = "py310"`
* `line-length = 120`
* double quotes; space indentation (4); LF endings
* `fix = true` — running `ruff check .` can auto-fix many lints
* `[tool.ruff.lint.isort] force-single-line = true`
* `extend-exclude = [".venv", ".env", "alembic"]` — Alembic versions are conventionally **not** linted, but keep them neat anyway.

```bash
poetry run ruff check .         # report + autofix
poetry run ruff format .        # format files
```

## 🧪 Test conventions

* Tests live under `tests/` mirroring the `src` layout (`tests/auth/`, `tests/package/`, `tests/test_health.py`).
* Use the shared fixtures `client` / `db` from `tests/conftest.py`.
* Prefer hitting real endpoints over unit patching for behaviour; assert on exact status codes (`starlette.status`).

> See [Testing](testing.md) for the full policy.

## ✔️ Before you open a PR

```bash
poetry run pre-commit run --all-files   # if pre-commit installed
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

Ensure your branch merges only code that passes CI (lint + format + tests). Typo-only diffs fail too — the docs are reviewed just like code.
