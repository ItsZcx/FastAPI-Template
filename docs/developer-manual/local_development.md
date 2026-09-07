# Local Development

Run the API on your host machine, outside Docker, with uv. This gives you fast iteration and IDE support.

## Prerequisites

* [uv](https://docs.astral.sh/uv/). uv installs and manages the Python version.
* A running PostgreSQL instance. Start the database container:

```bash
docker compose up -d postgres
```

## Install uv

The Docker image and CI install uv for you. For local work, run one of these:

```bash
# macOS or Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or run `pip install uv`. Restart your shell afterward so `uv` is on your `PATH`.

## Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock`, creates a `.venv`, and installs the runtime and dev dependencies (Ruff, pytest, pre-commit).

## Configure `.env`

```bash
cp .env.example .env
```

For host-local development, point the database URLs at `localhost` instead of the in-container hostname:

```bash
DB_URL=postgresql://postgres:1234@localhost:5432/postgres
ALEMBIC_DB_URL=postgresql://postgres:1234@localhost:5432/postgres
```

Inside Docker the database is `fastapi-postgres`. On your host it is `localhost`. Alembic runs on the host, so it always wants the `localhost` URL.

See [Configuration](configuration.md) for every variable.

## Apply database migrations

PostgreSQL must be running.

```bash
uv run alembic upgrade head
```

See [Database & Migrations](database_migrations.md).

## Run the development server

```bash
uv run uvicorn src.main:app --reload --port 8080
```

`--reload` gives you hot reload while you edit. You can also run `uv run fastapi run src/main.py --reload --port 8080`, which is what the Docker image uses.

## Verify

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/docs        # Swagger UI
```

`uv run` runs a command inside the project's `.venv`, so you rarely need to activate it. For an interactive shell, run `uv shell`, or `source .venv/bin/activate` on Unix, or `.venv\Scripts\activate` on Windows.

## Quality gates

Run these before pushing.

```bash
uv run ruff check .         # lint
uv run ruff format .        # format
uv run ruff format --check .   # verify formatting only (CI)
uv run pytest -q            # tests
```

If you install pre-commit, formatting runs on every commit:

```bash
uv run pre-commit install
```

## Managing dependencies

```bash
uv add <package>                        # add a runtime dependency
uv add --group dev <package>            # add a dev dependency
uv sync --upgrade                       # refresh versions within bounds
uv lock                                 # re-resolve and update the lock file
```

The Docker image and CI pin uv to `0.12.10`. Use the same version locally so the lock file stays compatible.
