# Quickstart

Get the whole stack (API and PostgreSQL) running with Docker. No local Python setup needed.

## Prerequisites

* [Docker](https://www.docker.com/) with Docker Compose. Docker Desktop includes it.
* [uv](https://docs.astral.sh/uv/) only if you want local virtualenv and package support. See [Local Development](local_development.md).

## Install dependencies with uv

This step is optional if you only plan to use Docker.

```bash
uv sync
```

This creates the project's `.venv` and installs the runtime and dev dependencies (Ruff, pytest, pre-commit).

## Create your `.env`

```bash
cp .env.example .env
```

Set `AUTH_SECRET_KEY` to a real value. It signs the JWT tokens.

```bash
openssl rand -hex 32
```

See [Configuration](configuration.md) for every variable.

## Run the stack with Docker

```bash
docker compose up -d
```

This builds and starts two containers:

| Container          | Role                     | Exposed port |
| ------------------ | ------------------------ | ------------ |
| `fastapi`          | The FastAPI application. | `8080`       |
| `fastapi-postgres` | PostgreSQL 16.           | `5432`       |

## Verify it runs

```bash
curl http://localhost:8080/healthz   # -> {"status":"ok"}
curl http://localhost:8080/readyz    # -> {"status":"ready"} (pings PostgreSQL)
```

Open the interactive API at <http://localhost:8080/docs> (Swagger UI) or <http://localhost:8080/redoc>.

## Stop the stack

```bash
docker compose down        # keeps the database volume
docker compose down -v     # also deletes the PostgreSQL data volume
```

Follow the logs while it runs:

```bash
docker compose logs --follow -t
```

## What's next

* Create a user and log in. See [Authentication](../architecture/auth.md).
* Run the test suite. See [Testing](../architecture/testing.md).
* Start building your own API. Read [Project Structure](../architecture/project_structure.md) and [Conventions](../architecture/conventions.md).
