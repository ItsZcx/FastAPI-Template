# Welcome to FastAPI Template

This **Introduction** is the starting point. Use it to figure out **where** to go next.

**FastAPI Template** is a **production-oriented FastAPI boilerplate**. It ships the cross-cutting concerns most backends need: authentication, logging, rate limiting, health checks, pagination, testing, and CI. You start on domain logic, not infrastructure.

## What you get

| Area             | What ships out of the box                                                     |
| ---------------- | ----------------------------------------------------------------------------- |
| Structure        | A consistent, domain-first layout with `src/core/` for shared infrastructure. |
| Auth             | JWT authentication and basic user management (`register`, `login`, `/me`).    |
| Rate limiting    | slowapi on the sensitive endpoints.                                           |
| CORS and headers | Environment-driven CORS and security headers.                                 |
| Logging          | structlog: console in dev, JSON in prod, with a per-request `X-Request-ID`.   |
| Health           | `/healthz` (liveness) and `/readyz` (real DB probe).                          |
| Pagination       | A reusable cursor-pagination `Page[T]` envelope.                              |
| Data             | PostgreSQL and Alembic migrations, uv, and Docker.                            |
| Quality          | pytest, Ruff, pre-commit, and a GitHub Actions CI pipeline.                   |

## Where to go next

Pick the path that matches what you are doing.

### Just looking around

* Read [Technology Stack](developer-manual/technology_stack.md) to understand which tools the template adopts.
* Read [Project Structure](architecture/project_structure.md) to see how the code is organised.

### Starting a new project from the template

* Start with [Quickstart](developer-manual/quickstart.md) to spin up the stack.
* Then read [Project Structure](architecture/project_structure.md) and [Conventions](architecture/conventions.md) so your new code follows the same rules.

### Running it on your own machine

* Read [Local Development](developer-manual/local_development.md), [Configuration](developer-manual/configuration.md), and [Database & Migrations](developer-manual/database_migrations.md).

### Working on the code and quality

* [Testing](architecture/testing.md) explains the test suite and policy.
* [Contributing](contributing/contributing.md) explains the conventions for proposing changes.

### Helping or contributing back

* Start at [Contributing](contributing/contributing.md).

> New here? Read [Conventions](architecture/conventions.md) next. It covers formatting, imports, and the Pydantic and SQLAlchemy style.
