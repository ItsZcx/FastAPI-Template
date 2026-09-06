# Quickstart

> 🎯 **Goal**: get the whole stack (API **and** PostgreSQL) running with Docker in a couple of minutes, with zero local Python setup.

## 1. Prerequisites

* [Docker](https://www.docker.com/) with Docker Compose (modern Docker Desktop includes it).
* Optionally [Poetry](https://python-poetry.org/) only if you want IDE/package support locally (see [Local Development](local_development.md)).

## 2. Install dependencies with Poetry

> Setup of the virtual environment and dependencies is optional but recommended. Step 2 can be skipped if you only plan to use Docker.

```bash
poetry install
```

This creates the project virtualenv and installs all runtime **and** dev dependencies (Ruff, pytest, pre-commit).

## 3. Create your `.env`

Copy the example file and adjust values:

```bash
cp .env.example .env
```

> ⚠️ **Important** — `AUTH_SECRET_KEY` is required to sign tokens. Generate a real one:
>
> ```bash
> openssl rand -hex 32
> ```
>
> See [Configuration](configuration.md) for every variable.

## 4. Run the stack with Docker

```bash
docker compose up -d
```

This builds and starts:

| Container          | Role                    | Exposed port |
| ------------------ | ----------------------- | ------------ |
| `fastapi`          | the FastAPI application | `8080`       |
| `fastapi-postgres` | PostgreSQL 16           | `5432`       |

## 5. Verify it is running

```bash
curl http://localhost:8080/healthz   # -> {"status":"ok"}
curl http://localhost:8080/readyz    # -> {"status":"ready"} (pinge PostgreSQL)
```

You can open the interactive API at <http://localhost:8080/docs> (Swagger UI) or <http://localhost:8080/redoc>.

## 6. Stop everything

```bash
docker compose down        # keeps the database volume
docker compose down -v     # also deletes the PostgreSQL data volume
```

Follow the logs while running with:

```bash
docker compose logs --follow -t
```

## ✅ What's next

* Create a user and log in — see [Authentication](../architecture/auth.md).
* Run the test suite — see [Testing](../architecture/testing.md).
* Start building your own API — read the [Project Structure](../architecture/project_structure.md) and [Conventions](../architecture/conventions.md).
