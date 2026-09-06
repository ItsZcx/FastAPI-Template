# FastAPI Template

A **production-oriented FastAPI template** that ships with the cross-cutting concerns most backends need, so you can start writing domain logic immediately instead of re-soldering infrastructure.

## 🚀 What you get

* 💻 A consistent, domain-first **project structure** with `src/core/` for shared infrastructure.
* 🔐 **JWT authentication** with basic user management (`register` / `login` / `/me`).
* 🚦 **Rate limiting** with slowapi on sensitive endpoints.
* 🌐 **CORS & security headers** driven by environment variables.
* 🪵 **Structured logging** with structlog — human-readable in dev, JSON in production, plus per-request `X-Request-ID`.
* 🩺 **Health checks** — `/healthz` (liveness) and `/readyz` (real DB readiness probe).
* 📄 **Cursor pagination** via a reusable `Page[T]` envelope.
* 🗄️ **PostgreSQL + Alembic migrations**, bundled with Poetry and Docker.
* ✅ **Testing** with pytest against an isolated PostgreSQL test database and per-test rollback.
* 🛡️ **Quality gates** — Ruff, pre-commit, and a GitHub Actions CI pipeline.

## 📘 Documentation Index

We recommend reading the docs on the official **GitBook** site. If you prefer, you can navigate all pages from the left-hand menu. A few recommended starting points:

* 🧰 [Technology Stack](developer-manual/technology_stack.md) — the tools and versions this template uses and why.
* 🚀 [Quickstart](developer-manual/quickstart.md) — spin the whole stack up with Docker in minutes.
* 💻 [Local Development](developer-manual/local_development.md) — run it locally with Poetry.
* ⚙️ [Configuration](developer-manual/configuration.md) — every environment variable, explained.
* 🏗️ [Project Structure](architecture/project_structure.md) — how the repository is organised and the rules to follow.
* 🧪 [Testing](architecture/testing.md) — how to run and write the test suite.

If you are **starting a new project from this template**, read the [Quickstart](developer-manual/quickstart.md) and then the [Architecture](architecture/project_structure.md) sections.
