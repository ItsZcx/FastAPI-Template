# FastAPI Template

A **production-oriented FastAPI template** for building modern backends quickly. It wires together uv, SQLAlchemy, Alembic, PostgreSQL, and Docker, and pre-integrates the cross-cutting features most APIs need so you can focus on your domain logic.

> 📚 **Documentation**: the full, always-up-to-date docs live on **GitBook** → **[https://zcx.gitbook.io/fastapi-template](https://zcx.gitbook.io/fastapi-template)**. The source for those docs is in [`docs/`](./docs) in this repository (mapped onto the site by `docs/gitbook-docs.yaml`).

## ✨ Highlights

- 🔐 **JWT authentication** — user management (`register` / `login` / `/me`)
- 🚦 **Rate limiting** — slowapi on login/register
- 🪵 **Structured logging** — structlog (console or JSON) with per-request `X-Request-ID`
- 🌐 **CORS & security headers** — env-driven
- 🩺 **Health checks** — `/healthz` (liveness) and `/readyz` (DB readiness)
- 📄 **Cursor pagination** — reusable `Page[T]` envelope
- 🗄️ **PostgreSQL + Alembic** migrations, bundled with uv and Docker
- 🛡️ **Quality gates** — `src/core/` structure, Ruff, pre-commit, GitHub Actions CI
- 🧪 **Testing** — pytest against an isolated PostgreSQL test database

## 🏗️ Structure at a glance

```
├── src/                 # application source
│   ├── main.py          # app wiring (middleware, routers, error handlers)
│   ├── pagination.py    # cursor pagination + Page[T]
│   ├── core/            # cross-cutting: config, database, logging, middleware, rate limits
│   ├── auth/            # authentication + user management
│   ├── health/          # /healthz & /readyz probes
│   └── package/         # copy-paste example package (todos)
├── docs/                # GitBook documentation (gated by docs/gitbook-docs.yaml)
├── tests/               # pytest suite (mirrors src)
├── alembic/             # database migrations
└── compose.yaml         # Docker services: fastapi + postgres
```

## 🚀 Quickstart (Docker)

```bash
# 0. install uv (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. install runtime & dev dependencies
uv sync

# 2. create your environment file
cp .env.example .env
# set AUTH_SECRET_KEY (e.g. `openssl rand -hex 32`)

# 3. run the API + PostgreSQL
docker compose up -d

# 4. verify / explore
curl http://localhost:8080/healthz   # {"status":"ok"}
open http://localhost:8080/docs      # Swagger UI
```

For local (non-Docker) development, environment variables, database migrations, and the test suite, head to the **[GitBook docs → Developer Manual](https://zcx.gitbook.io/fastapi-template)**.

## 📖 Where to find what

| Need | Go to |
| --- | --- |
| Full documentation | [zcx.gitbook.io/fastapi-template](https://zcx.gitbook.io/fastapi-template) |
| Setup, config, migrations | **Intro → Developer Manual** (Quickstart, Local Development, Configuration) |
| How the code is organised & its conventions | **Architecture** (Project Structure, Conventions, Auth, Pagination, Testing) |
| Report/contribute | **Contributing** section of the docs + issues/PRs |

## 🧰 Tech stack

[Python](https://www.python.org/) 3.10+ · [FastAPI](https://fastapi.dev/) · [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 · [Alembic](https://alembic.sqlalchemy.org/) · [PostgreSQL](https://www.postgresql.org/) · [uv](https://docs.astral.sh/uv/) · [Docker](https://www.docker.com/) · [Pydantic v2](https://docs.pydantic.dev/) · [PyJWT](https://pyjwt.readthedocs.io/) · [structlog](https://www.structlog.org/) · [slowapi](https://github.com/laurentS/slowapi) · [Ruff](https://docs.astral.sh/ruff/) · [pytest](https://docs.pytest.org/)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
