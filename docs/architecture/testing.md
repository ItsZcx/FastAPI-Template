# Testing

> 🎯 **Policy**: every endpoint change must remain covered by a passing, isolated test. CI enforces `ruff` + `pytest` on every push & PR.

## 🧪 Test stack

* **Framework**: pytest
* **HTTP client**: FastAPI `TestClient` (shipped with `fastapi[standard]`)
* **Database**: a dedicated PostgreSQL **test** database, created automatically from `TEST_DB_URL`

> ✅ Aligning tests with PostgreSQL (the same engine as production) avoids "works on SQLite, breaks on PG". The infra cost is dockerized anyway.

## 🗂️ Layout

`tests/` mirrors `src/` so it is obvious which module a test exercises:

```
tests/
├── conftest.py            # shared fixtures
├── test_health.py
├── auth/
│   └── test_auth.py       # register/login/me/user management + errors
└── package/
    └── test_todos.py      # CRUD + cursor pagination + a rate-limit test
```

## 🚀 Running the suite

```bash
docker compose up -d postgres   # the test DB reuses this PostgreSQL
uv run pytest               # all tests
uv run pytest -q            # quiet
uv run pytest tests/auth    # a single directory
```

> pytest orchestrates **database creation** for you, so you don't `createdb` manually. Set `TEST_DB_URL` (`.env`/env) only if you want a different name/location.

## 🧩 What `tests/conftest.py` gives you (fixtures)

| Fixture                | Scope             | Purpose                                                                                      |
| ---------------------- | ----------------- | -------------------------------------------------------------------------------------------- |
| `create_test_database` | session (autouse) | connects to the admin `DB_URL` and issues `CREATE DATABASE <test_db>` if missing             |
| `engine`               | session           | bound to the test DB; runs `create_all` at start and `drop_all` at end                       |
| `db`                   | function          | a session joined into an **outer transaction**; rolled back after each test → full isolation |
| `client`               | function          | a `TestClient` whose `get_db` dependency yields the `db` fixture                             |
| `reset_rate_limiter`   | autouse           | calls `limiter.reset()` so rate-limited endpoints behave per test                            |

### How isolation works

* The test database is dropped & recreated per session (`Base.metadata.create_all/drop_all`), so state never leaks between runs.
* Within a test, every change is made on a connection wrapped in a transaction, then **rolled back** afterwards. You get a fresh DB every test without slow per-test table recreation.

> 💡 `client` restores `app.dependency_overrides` after every test, so fixtures and rate-limits stay clean across a large suite.

## ✍️ Writing a test

Prefer **behavioural** tests that hit real HTTP endpoints. Import the `client` fixture and use `starlette.status` constants:

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

For `db`-level or dependency-level tests, inject the `db` fixture in the same way.

## 🤖 CI integration

`.github/workflows/ci.yml` runs the **exact same suite** against a `postgres:16` service container on every push and PR, after Ruff lint/format. If a test depends on Docker networking or timing, it will surface there.

## 📈 Coverage

The template does not enforce a numeric coverage gate — the priority is meaningful coverage of auth (happy paths **and** failure modes) plus the health/pagination behaviours. To measure locally:

```bash
uv run pytest --cov=src                                  # if you add pytest-cov
uv run pytest --cov=src --cov-report=term-missing
```

## ✅ When to add a test

* You add or change an endpoint, a schema validator, a service rule, or the error mapping.
* You adjust a rate limit or pagination cursor.
* You touch `conftest.py` fixtures or database constants.

> Add tests in the **same PR** as the feature; CI will block merges that don't. When copying `src/package/` for your new domain, also copy its test file and stub in the corresponding expectations.
