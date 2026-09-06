# Welcome to FastAPI Template 👋

> 🎯 This **Introduction** is the starting point. Use it to figure out **where** to go next — pick the section that matches what you are trying to do.

**FastAPI Template** is a **production-oriented FastAPI boilerplate**. It ships with the cross-cutting concerns most backends need — authentication, logging, rate limiting, health checks, pagination, testing, and CI — so you can start writing domain logic immediately instead of re-soldering infrastructure.

## 🚀 What you get

| Area | What ships out of the box |
| --- | --- |
| 💻 Structure | a consistent, domain-first layout with `src/core/` for shared infrastructure |
| 🔐 Auth | JWT authentication + basic user management (`register` / `login` / `/me`) |
| 🚦 Rate limiting | slowapi on sensitive endpoints |
| 🌐 CORS & headers | environment-driven CORS and security headers |
| 🪵 Logging | structlog — console in dev, JSON in prod, with per-request `X-Request-ID` |
| 🩺 Health | `/healthz` (liveness) and `/readyz` (real DB probe) |
| 📄 Pagination | reusable cursor-pagination `Page[T]` envelope |
| 🗄️ Data | PostgreSQL + Alembic migrations, Poetry and Docker |
| ✅ Quality | pytest suite, Ruff, pre-commit, GitHub Actions CI |

## 🧭 Where to go next

Pick the path that matches what you are doing:

### 👀 Just looking around
* Read the [Technology Stack](developer-manual/technology_stack.md) page to understand the tools this template adopts.
* Skip to the [Project Structure](architecture/project_structure.md) page to see how the code is organised and why.

### 🚀 Starting a new project from the template
* Begin with the [Quickstart](developer-manual/quickstart.md) page to spin up the stack in minutes.
* Then read [Project Structure](architecture/project_structure.md) and [Conventions](architecture/conventions.md) so your new code follows the same rules.

### 💻 Running it on your own machine
* Get set up with [Local Development](developer-manual/local_development.md), configure every env variable in [Configuration](developer-manual/configuration.md), and apply the schema with [Database & Migrations](developer-manual/database_migrations.md).

### 🧪 Working on the code / quality
* The [Testing](architecture/testing.md) page explains the test suite and policy.
* The [Contributing](contributing/contributing.md) page lays out the conventions and process for proposing changes.

### 🛠️ Helping or contributing back
* The [Contributing](contributing/contributing.md) section is the place to start.

> 💡 **New to the repo?** If you only read one more page, make it [Conventions](architecture/conventions.md) — formatting, imports, and the Pydantic/SQLAlchemy style are all there.
