# Database and Migrations

The template uses PostgreSQL through SQLAlchemy 2.0 with classic `Column` models, migrated with Alembic.

## Connection and session management

`src/core/database.py` is the single place to manage the database.

* `engine` is created from `DB_URL` with production-friendly pooling. It sets `pool_size=5`, `max_overflow=10`, and `pool_pre_ping=True`, which prunes stale connections before use.
* `SessionLocal` is a `sessionmaker` bound to that engine.
* `Base` is the declarative base that every SQLAlchemy model inherits from.
* `get_db()` is a FastAPI dependency that yields a session and closes it.
* `db_dependency` is an `Annotated` alias. Endpoints declare `db: db_dependency` and get a managed session.

```python
# src/package/router.py (example)
@router.get("", status_code=status.HTTP_200_OK)
def get_items(db: db_dependency, ...):
    return ...
```

Do not construct sessions manually in an endpoint. Take `db: db_dependency` instead. It closes the session even when the handler raises.

## Alembic

### How env.py is configured

`alembic/env.py` does three things.

1. Loads `.env` and reads `ALEMBIC_DB_URL` directly from the environment. It never reads `.ini`.
2. Auto-discovers models. It scans `src/` and imports every `<package>/models.py`, which registers each table on `Base` for autogenerate.
3. Sets `target_metadata = Base.metadata`.

New models are picked up automatically. Drop a `models.py` in a package under `src/` and Alembic sees it. You do not edit `alembic/env.py`.

### Common commands

```bash
# print current revision
uv run alembic current

# show available heads
uv run alembic heads

# create a migration from model changes (the database must be running)
uv run alembic revision --autogenerate -m "describe the change"

# apply pending migrations
uv run alembic upgrade head

# roll back one step
uv run alembic downgrade -1
```

### Migration history in this repo

| Revision       | Description                                     |
| -------------- | ----------------------------------------------- |
| `df768aa6da3d` | Creates the `todos` table. Reference migration. |
| `5b3d4c2e1f0a` | Creates the `users` table. Current head.        |

New revisions chain onto the head with `down_revision = "5b3d4c2e1f0a"`.

### Start a new project

The shipped migrations are a reference, not production history. For a clean slate:

```bash
rm -rf alembic/ alembic.ini
uv run alembic init alembic
```

Then edit `alembic/env.py` to load `ALEMBIC_DB_URL` and set `target_metadata = Base.metadata`. To keep the same auto-discovery, copy the `_discover_and_import_models()` helper from this repo's `alembic/env.py`. Otherwise, import each model module yourself.

## Write a model

Models use the classic style and import `Base` from `src.core.database`.

```python
# src/package/models.py
from sqlalchemy import Column, Integer, String
from src.core.database import Base


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
```

Two models show the style in the repo:

* `users` is unique by `email` and `username` and carries `created_at` and `updated_at` timestamps. See `src/auth/models.py`.
* `todos` is the simplest example. See `src/package/models.py`.

## Recommended workflow

1. Change the models in `src/<package>/models.py`. `alembic/env.py` discovers them automatically.
2. Run `uv run alembic revision --autogenerate -m "what changed"`.
3. Review the generated migration in `alembic/versions/`.
4. Run `uv run alembic upgrade head`.

Start the PostgreSQL container before running any migration command.
