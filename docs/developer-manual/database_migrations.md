# Database & Migrations

This template uses **PostgreSQL**, accessed through **SQLAlchemy 2.0** (classic `Column` models) and migrated with **Alembic**.

## 🔌 Connection & session management

`src/core/database.py` is the single place to reason about the database:

* **`engine`** — created from `DB_URL` with production-friendly pooling:
  * `pool_size=5`
  * `max_overflow=10`
  * `pool_pre_ping=True` (prunes stale connections before use)
* **`SessionLocal`** — a `sessionmaker` bound to that engine.
* **`Base`** — the declarative base every SQLAlchemy model inherits from.
* **`get_db()`** — a FastAPI dependency that yields a session and always closes it.
* **`db_dependency`** — an `Annotated` alias so endpoints declare `db: db_dependency` and get a cleanly managed session.

```python
# src/package/router.py (example)
@router.get("", status_code=status.HTTP_200_OK)
def get_items(db: db_dependency, ...):
    return ...
```

> 💡 Endpoints should **not** construct sessions manually — always take `db: db_dependency`. It guarantees the session is closed even if handler raises.

## ⚙️ Alembic

### How env.py is configured

`alembic/env.py`:

1. Loads `.env` and reads **`ALEMBIC_DB_URL`** directly from the environment (never `.ini`).
2. Imports the app's `Base` **and every installed model** (even if unused) so autogenerate can see all tables.
3. Sets `target_metadata = Base.metadata`.

> ⚠️ **Reminder for new models**: whenever you add a model file, import it in `alembic/env.py` too — otherwise Alembic won't discover the new table during autogenerate.

### Common commands

```bash
# print current revision
poetry run alembic current

# show available heads
poetry run alembic heads

# create a new migration from model changes (DB MUST be running)
poetry run alembic revision --autogenerate -m "describe the change"

# apply all pending migrations
poetry run alembic upgrade head

# roll back one step
poetry run alembic downgrade -1
```

### Migration history in this repo

| Revision | Description |
| --- | --- |
| `df768aa6da3d` | Creates the `todos` table (reference/example migration) |
| `5b3d4c2e1f0a` | Creates the `users` table (head) |

New revisions chain onto the head (`down_revision = "5b3d4c2e1f0a"`).

### Start a brand-new project

The shipped migrations are a useful reference but not production history. For a clean slate:

```bash
rm -rf alembic/ alembic.ini
poetry run alembic init alembic
```

Then reconfigure `alembic/env.py` to load `ALEMBIC_DB_URL`, import your models, and set `target_metadata`. The rules above still apply.

## 🧱 Writing a model

Models follow the **classic style** (they read like SQL DDL) and import `Base` from `src.core.database`.

```python
# src/package/models.py
from sqlalchemy import Column, Integer, String
from src.core.database import Base


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
```

Reference implementation milestones:

* `users` are unique by `email` and `username`, and carry `created_at` / `updated_at` timestamps (see `src/auth/models.py`).
* `todos` are the simplest possible example (see `src/package/models.py`).

## ✅ Recommended workflow

1. Change the model(s) in `src/<package>/models.py`.
2. Make sure the model is imported by `alembic/env.py`.
3. `poetry run alembic revision --autogenerate -m "what changed"`.
4. **Review** the generated migration in `alembic/versions/…`.
5. `poetry run alembic upgrade head`.

> ⚠️ Always start the PostgreSQL container before running any migration command.
