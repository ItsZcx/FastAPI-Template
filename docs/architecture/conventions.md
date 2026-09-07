# Conventions

This page records the rules of the codebase. Some are enforced by tooling; the rest are judgment calls a reviewer looks for. Following them keeps contributions uniform.

The repo enforces the toolable parts automatically with Ruff and CI. The rest are conventions.

## Git commit style

This repo uses Conventional Commits with a type prefix.

```
<type>(<scope>): short description
```

Examples from the history:

| Message                                             | Type meaning                     |
| --------------------------------------------------- | -------------------------------- |
| `feat: add template auth`                           | new feature                      |
| `fix: Docker errors x2`                             | bug fix                          |
| `docs(api): update README with usage examples`      | documentation change, with scope |
| `feat: manage env variables with pydantic-settings` | new feature                      |

Common types are `feat`, `fix`, `refactor`, `style`, `test`, `docs`, `chore`, and `infra`. A scope such as `auth`, `db`, or `docker` is optional and names the area changed.

## Import style

Ruff `isort` enforces this.

* One import per line, in alphabetical order.
* Standard library, third-party, and first-party imports are grouped. Ruff sorts them.

```python
from starlette import status

from src.core.database import db_dependency
from src.package.models import Todos
```

## Pydantic v2

Use v2 style, not the deprecated v1 style.

* Use `model_config = ConfigDict(...)`, not `class Config`.
* For read models backed by ORM objects, use `ConfigDict(from_attributes=True)`.
* Provide example payloads through `json_schema_extra` so Swagger shows real values.
* Read request data with `.model_dump()`, never v1 `.dict()`.

Example:

```python
class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

## SQLAlchemy style

* Declare models classic-style with `Column(...)`, inheriting `Base` from `src.core.database`, not a bare import from SQLAlchemy.
* Use the `db_dependency` typed session in endpoints. Do not hand-roll a session.
* Unique fields get `unique=True`. Fields used for list lookups get `index=True`.
* Timestamps use `DateTime(timezone=True)` with `server_default=func.now()` and `onupdate`.

## Naming and types

* The project targets Python 3.10. Use modern syntax such as `str | None`, `list[Todo]`, and `Annotated[...]`.
* Type-annotate function signatures. The codebase uses `Annotated` heavily for dependencies, such as `db_dependency` and `current_user_dependency`.
* Follow Python naming. Modules are lowercase, functions are `snake_case`, and models and schemas are `PascalCase`.

## Error handling

Custom domain errors are small classes raised in `service.py` and mapped to HTTP status codes in one place.

* Auth raises `AuthError` subclasses and maps them centrally in `src/main.py`. See [Health Checks & Error Handling](health_and_errors.md).
* Simpler endpoints may raise `HTTPException` directly, as the `package/` example does. Large domains should prefer explicit exceptions.

## Endpoint conventions

* A router's prefix and tag set the URL and Swagger group:
  ```python
  router = APIRouter(prefix="/todos", tags=["Todos"])
  ```
* Use status codes from `starlette`, such as `status.HTTP_204_NO_CONTENT`.
* Return read models through `response_model=...` so hashed and password fields never leak.

## Code formatting

Ruff reads these settings from `pyproject.toml`:

* `target-version = "py310"`
* `line-length = 120`
* Double quotes, 4-space indentation, LF line endings
* `fix = true`. Running `ruff check .` auto-fixes many lints.
* `[tool.ruff.lint.isort] force-single-line = true`
* `extend-exclude = [".venv", ".env", "alembic"]`. Alembic migration files are not linted, but keep them tidy anyway.

```bash
uv run ruff check .         # report and autofix
uv run ruff format .        # format files
```

## Test conventions

* Tests live under `tests/`, mirroring `src`: `tests/auth/`, `tests/package/`, and `tests/test_health.py`.
* Use the shared `client` and `db` fixtures from `tests/conftest.py`.
* Test real endpoints rather than patching units. Assert on exact `starlette.status` codes.

See [Testing](testing.md) for the full policy.

## Before you open a pull request

```bash
uv run pre-commit run --all-files   # if pre-commit installed
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Merge code that passes CI: lint, format, and tests. Docs are reviewed like code, so typo-only diffs fail too.
