# Local Development

> 🎯 **Goal**: run the API on your host machine (outside Docker) with uv for fast iteration and IDE support.

## ✅ Prerequisites

* [uv](https://docs.astral.sh/uv/) (Python 3.10+ is installed and managed by uv as needed)
* A running PostgreSQL instance. The easiest path is to start only the database container:

```bash
docker compose up -d postgres
```

## 1. Install uv

If you haven't already (the Docker image and CI install it for you):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatively `pip install uv`. Restart your shell (or re-source your profile) afterward to put `uv` on your `PATH`.

## 2. Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` + `uv.lock`, creates a `.venv`, and installs the runtime **and** dev (Ruff, pytest, pre-commit) dependencies.

## 3. Configure `.env`

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

## 4. Apply database migrations

Migrations are managed with Alembic (PostgreSQL must be running):

```bash
uv run alembic upgrade head
```

See [Database & Migrations](database_migrations.md) for full details.

## 5. Run the development server

```bash
uv run uvicorn src.main:app --reload --port 8080
```

The `--reload` flag gives you hot reload while editing.

> Alternatively `uv run fastapi run src/main.py --reload --port 8080` — the Docker image uses the `fastapi` CLI.

## 6. Verify

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/docs        # Swagger UI
```

> ℹ️ `uv run` executes a command inside the project's `.venv`, so you rarely need to `activate` it. To run an interactive shell you can `uv shell` (or `source .venv/bin/activate` on Unix / `.venv\Scripts\activate` on Windows).

## 🧹 Quality gates (run these before pushing)

```bash
uv run ruff check .         # lint
uv run ruff format .        # format
uv run ruff format --check .   # (CI) verify formatting only
uv run pytest -q            # tests
```

If you installed pre-commit, formatting is also enforced automatically on commit:

```bash
uv run pre-commit install
```

## 📦 Managing dependencies

```bash
uv add <package>                        # add a runtime dependency
uv add --group dev <package>            # add a dev dependency (ruff, pytest, pre-commit)
uv sync --upgrade                       # refresh versions within bounds
uv lock                                 # re-resolve & update the lock file
```

> ⚠️ **uv version note**: the Docker image (`uv==0.12.10`) and CI (`astral-sh/setup-uv`, pinned `0.12.10`) should match a version you use locally so the lock file stays compatible.
