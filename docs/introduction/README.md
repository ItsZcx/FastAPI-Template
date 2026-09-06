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
* Read the [Developer Manual → Technology Stack](/developer-manual) to understand the tools this template adopts.
* Skip straight to the [Architecture](/architecture) section to see how the code is organised and why.

### 🚀 Starting a new project from the template
* Begin with the [Developer Manual → Quickstart](/developer-manual) to spin up the stack in minutes.
* Then read [Architecture → Project Structure](/architecture) and [Architecture → Conventions](/architecture) so your new code follows the same rules.

### 💻 Running it on your own machine
* The [Developer Manual](/developer-manual) covers local development, configuration (every env variable), and database migrations.

### 🧪 Working on the code / quality
* The [Architecture → Testing](/architecture) page explains the test suite and policy.
* The [Contributing](/contributing) page lays out the conventions and process for proposing changes.

### 🛠️ Helping or contributing back
* The [Contributing](/contributing) section is the place to start.

> 💡 **New to the repo?** If you only read one more page, make it [Architecture → Conventions](/architecture/conventions.md) — formatting, imports, and the Pydantic/SQLAlchemy style are all there.
