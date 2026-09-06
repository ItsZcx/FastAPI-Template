# Local Development

> 🎯 **Goal**: run the API on your host machine (outside Docker) with Poetry for fast iteration and IDE support.

## ✅ Prerequisites

* [Python](https://www.python.org/) 3.10+
* [Poetry](https://python-poetry.org/) 2.x
* A running PostgreSQL instance. The easiest path is to start only the database container:

```bash
docker compose up -d postgres
```

## 1. Install dependencies

```bash
poetry install
```

## 2. Configure `.env`

Create your environment file (see [Configuration](configuration.md)):

```bash
cp .env.example .env
```

For **host-local** development, point the database URLs at `localhost` instead of the in-container hostname:

```bash
DB_URL=postgresql://postgres:1234@localhost:5432/postgres
ALEMBIC_DB_URL=postgresql://postgres:1234@localhost:5432/postgres
```

> ℹ️ Inside Docker the host service is reachable as `fastapi-postgres`; when you run the app on your host it is `localhost`. Alembic runs on the host, so it always wants the `localhost` URL.

## 3. Apply database migrations

Migrations are managed with Alembic (PostgreSQL must be running):

```bash
poetry run alembic upgrade head
```

See [Database & Migrations](database_migrations.md) for full details.

## 4. Run the development server

```bash
poetry run uvicorn src.main:app --reload --port 8080
```

The `--reload` flag gives you hot reload while editing.

> Alternatively `poetry run fastapi run src/main.py --reload --port 8080` — the Docker image uses the `fastapi` CLI.

## 5. Verify

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/docs        # Swagger UI
```

## 🧹 Quality gates (run these before pushing)

```bash
poetry run ruff check .         # lint
poetry run ruff format .        # format
poetry run ruff format --check .   # (CI) verify formatting only
poetry run pytest -q            # tests
```

If you installed pre-commit, formatting is also enforced automatically on commit:

```bash
poetry run pre-commit install
```

> On **Windows** (PowerShell), wrap these commands or use `poetry shell` first. `host.docker.internal` can substitute for `localhost` only in edge Docker-on-Windows setups; the Compose setup here avoids that need.

## 📦 Managing dependencies

```bash
poetry add <package>                # add a runtime dependency
poetry add --group=dev <package>    # add a dev dependency (ruff, pytest, pre-commit)
poetry update                       # refresh the lock file
```

> ⚠️ **Poetry version note**: this repository uses a Poetry **2.x** lock file. Keep the image pin (`poetry==2.3.2` in the `Dockerfile`) and the CI pin in sync with the tool you use locally, or you may hit lock-file parse errors.
