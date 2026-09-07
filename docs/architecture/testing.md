# Testing

Every endpoint change must stay covered by an isolated, passing test. CI enforces Ruff and pytest on every push and pull request.

## Test stack

* pytest.
* FastAPI `TestClient`, shipped with `fastapi[standard]`.
* A dedicated PostgreSQL test database, created from `TEST_DB_URL`.

Tests run against PostgreSQL, the same engine as production, so "works on SQLite" problems do not appear. The infrastructure is dockerized.

## Layout

`tests/` mirrors `src/`, so it is obvious which module a test exercises:

```
tests/
├── conftest.py            # shared fixtures
├── test_health.py
├── auth/
│   └── test_auth.py       # register, login, me, user management, and errors
└── package/
    └── test_todos.py      # CRUD, cursor pagination, and a rate-limit test
```

## Run the suite

```bash
docker compose up -d postgres   # the test DB reuses this PostgreSQL
uv run pytest               # all tests
uv run pytest -q            # quiet
uv run pytest tests/auth    # a single directory
```

Against the newest FastAPI stack you may see two deprecation warnings:

1. `StarletteDeprecationWarning`: "Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead."
2. `DeprecationWarning`: "The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead."

Both come from starlette's `TestClient`, not from this code, and are left visible. The app itself starts and runs without warnings. The warnings go away once starlette updates `TestClient` to use `httpx2` and `anyio.from_thread`.

pytest creates the test database for you. Set `TEST_DB_URL` in `.env` or the environment only to change the name or location.

## What `tests/conftest.py` provides

| Fixture                | Scope            | Purpose                                                                             |
| ---------------------- | ---------------- | ----------------------------------------------------------------------------------- |
| `create_test_database` | session, autouse | connects to the admin `DB_URL` and runs `CREATE DATABASE` if the test DB is missing |
| `engine`               | session          | bound to the test DB, runs `create_all` at start and `drop_all` at end              |
| `db`                   | function         | a session joined into an outer transaction, rolled back after each test             |
| `client`               | function         | a `TestClient` whose `get_db` dependency yields the `db` fixture                    |
| `reset_rate_limiter`   | autouse          | calls `limiter.reset()` so rate-limited endpoints behave per test                   |

### How isolation works

The test database is dropped and recreated each session with `Base.metadata.create_all` and `drop_all`, so state never leaks between runs.

Within a test, every change runs on a connection wrapped in a transaction, then rolls back. You get a fresh database each test without recreating tables.

`client` restores `app.dependency_overrides` after each test, so fixtures and rate limits stay clean.

## Write a test

Prefer behavioural tests that hit real HTTP endpoints. Import the `client` fixture and use `starlette.status` constants:

```python
from starlette import status

def test_register(client):
    resp = client.post("/auth/register", json={
        "email": "user@example.com", "username": "johndoe", "password": "supersecret123",
    })
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["email"] == "user@example.com"
    assert "hashed_password" not in body
```

For database-level or dependency-override tests, inject the `db` fixture the same way.

## CI integration

`.github/workflows/ci.yml` runs the same suite against a `postgres:16` service container on every push and pull request, after Ruff lint and format. Tests that depend on Docker networking or timing surface there.

## Coverage

The template enforces no numeric coverage gate. The priority is meaningful coverage of auth, happy paths and failure modes, plus the health and pagination behaviours. To measure locally:

```bash
uv run pytest --cov=src                                  # if you add pytest-cov
uv run pytest --cov=src --cov-report=term-missing
```

## When to add a test

* You add or change an endpoint, a schema validator, a service rule, or the error mapping.
* You adjust a rate limit or pagination cursor.
* You touch `conftest.py` fixtures or database constants.

Add tests in the same pull request as the feature. CI blocks merges that lack them. When you copy `src/package/` for a new domain, copy its test file and stub the matching expectations.
