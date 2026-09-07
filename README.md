# FastAPI Template

A production-oriented FastAPI template for building modern backends. It wires together uv, SQLAlchemy, Alembic, PostgreSQL, and Docker, and pre-integrates the cross-cutting features most APIs need, so you can focus on your domain logic.

The full, always-current documentation lives on GitBook at [https://zcx.gitbook.io/fastapi-template](https://zcx.gitbook.io/fastapi-template). Its source is in [`docs/`](./docs), mapped onto the site by `docs/gitbook-docs.yaml`.

## Highlights

- JWT authentication and basic user management with `register`, `login`, and `/me`.
- Rate limiting with slowapi on login and register.
- Structured logging with structlog, console or JSON, with a per-request `X-Request-ID`.
- Environment-driven CORS and security headers.
- Health checks: `/healthz` for liveness and `/readyz` for a database probe.
- Cursor pagination with a reusable `Page[T]` envelope.
- PostgreSQL and Alembic migrations, bundled with uv and Docker.
- Quality gates: a `src/core/` structure, Ruff, pre-commit, and a GitHub Actions CI pipeline.
- Testing with pytest against an isolated PostgreSQL test database.

## Structure at a glance

```
├── src/                 # application source
│   ├── main.py          # app wiring: middleware, routers, error handlers
│   ├── pagination.py    # cursor pagination and Page[T]
│   ├── core/            # config, database, logging, middleware, rate limits
│   ├── auth/            # authentication and user management
│   ├── health/          # /healthz and /readyz probes
│   └── package/         # copy-paste example package, todos
├── docs/                # GitBook documentation, gated by docs/gitbook-docs.yaml
├── tests/               # pytest suite, mirrors src
├── alembic/             # database migrations
└── compose.yaml         # Docker services: fastapi and postgres
```

## Quickstart

```bash
# 0. install uv (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. install runtime and dev dependencies
uv sync

# 2. create your environment file
cp .env.example .env
# set AUTH_SECRET_KEY, e.g. `openssl rand -hex 32`

# 3. run the API and PostgreSQL
docker compose up -d

# 4. verify and explore
curl http://localhost:8080/healthz   # {"status":"ok"}
open http://localhost:8080/docs      # Swagger UI
```

For local development, environment variables, database migrations, and the test suite, read the [Developer Manual](https://zcx.gitbook.io/fastapi-template).

## Where to find what

| Need                                          | Go to                                                                      |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| Full documentation                            | [zcx.gitbook.io/fastapi-template](https://zcx.gitbook.io/fastapi-template) |
| Setup, config, migrations                     | Developer Manual: Quickstart, Local Development, Configuration             |
| How the code is organised and its conventions | Architecture: Project Structure, Conventions, Auth, Pagination, Testing    |
| Reporting and contributing                    | Contributing, plus issues and pull requests                                |

## Tech stack

[Python](https://www.python.org/) 3.10+ · [FastAPI](https://fastapi.dev/) · [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 · [Alembic](https://alembic.sqlalchemy.org/) · [PostgreSQL](https://www.postgresql.org/) · [uv](https://docs.astral.sh/uv/) · [Docker](https://www.docker.com/) · [Pydantic v2](https://docs.pydantic.dev/) · [PyJWT](https://pyjwt.readthedocs.io/) · [structlog](https://www.structlog.org/) · [slowapi](https://github.com/laurentS/slowapi) · [Ruff](https://docs.astral.sh/ruff/) · [pytest](https://docs.pytest.org/)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
