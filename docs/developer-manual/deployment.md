# Deployment

This page explains how the repository is built, tested, and prepared for deployment. The repo ships a **CI + Docker** setup that keeps you one step away from any host that can run containers.

> ℹ️ This project is a **template**. It has no staging/production infrastructure baked in; instead it provides the repeatable pieces (Docker, a CI workflow, migrations) plus the deploy guidance below.

## 📦 Deliverables

| Asset                      | Purpose                                                           |
| -------------------------- | ----------------------------------------------------------------- |
| `Dockerfile`               | Builds the API image (uv, runtime deps only).                 |
| `compose.yaml`             | Runs `fastapi` (port `8080`) + `postgres` (port `5432`).          |
| `.github/workflows/ci.yml` | Lint + format + tests on every push/PR.                           |
| `alembic/`                 | Database schema migrations, applied on the host before/at deploy. |

## 🐳 The production image (Dockerfile)

```dockerfile
FROM python:3.10-alpine3.20
ENV PYTHONUNBUFFERED=1 UV_NO_CACHE=1
RUN pip install --no-cache-dir uv==0.12.10
RUN uv sync --no-dev --frozen   # runtime deps only, from the committed lock
CMD ["uv", "run", "--frozen", "fastapi", "run", "src/main.py", "--reload", "--port", "8080"]
```

Key points:

* Installs **runtime** dependencies only (`--no-dev`) — Ruff, pytest & pre-commit never ship to production.
* `--frozen` installs exactly from the committed `uv.lock`, so the image is reproducible.
* **No `.env` is baked into the image.** Configuration is injected at runtime via environment variables (`compose.yaml` does this for local, your platform for prod). Inside a container the database is `fastapi-postgres`, **not** `localhost`.
* The `--reload` flag in the `CMD` is development-oriented; for production you will typically drop `--reload` (and may add `--workers` behind a load balancer).

> ⚠️ The image prepares port `8080`. Route external traffic there (or remap via Compose as `compose.yaml` does).

## 🧱 CI/CD pipeline (GitHub Actions)

`.github/workflows/ci.yml` triggers on **push and pull_request**:

| Stage                | Command                         | Purpose                     |
| -------------------- | ------------------------------- | --------------------------- |
| Provision PostgreSQL | `postgres:16.2-alpine` service  | gives tests a real database |
| Install uv & deps    | `uv sync --frozen`              | uv `0.12.10`                |
| Ruff lint            | `uv run ruff check .`           | code style/correctness      |
| Ruff format          | `uv run ruff format --check .`  | formatting                  |
| Tests                | `uv run pytest -q`              | runs the full suite         |

Required environment (provided as workflow `env`): `DB_URL`, `TEST_DB_URL`, `AUTH_SECRET_KEY`.

> 🔁 The pipeline is deliberately **test-first** — nothing advances unless the checks pass. It does **not** build/push Docker by default; add a `build` job (below) when you have a registry.

### Adding image build + push to a registry

A minimal extension that builds and pushes after tests pass:

```yaml
  build:
    needs: test            # only build once tests are green
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

## 🚢 Deploying the API

There is no single "correct" host for a template; pick one and apply the same steps:

1. **Provision PostgreSQL** accessible to the app (or run it with Compose as in development).
2. **Set real environment variables** — never rely on a committed `.env`. Inject `DB_URL`, `AUTH_SECRET_KEY`, `ENVIRONMENT=production`, and tune `LOG_FORMAT=json`, `CORS_ORIGINS`, `LOG_LEVEL` via your platform (env vars **override** the `.env` file thanks to `pydantic-settings`).
3. **Run Alembic migrations** once, pointing at the real database:
   ```bash
   uv run alembic upgrade head
   ```
4. **Start the image** and expose port `8080`.
5. **Configure load balancing / TLS** in front; set `ENVIRONMENT=production` so `Strict-Transport-Security` is added.

> 🩺 Use the readiness probe `/readyz` as your orchestrator health check — it fails (503) when the database is unreachable. `/healthz` is the lighter liveness check.

## 🔍 Tuning for production scale

* **Workers**: run multiple uvicorn workers for concurrency (`--workers N`) behind a load balancer.
* **Rate limiting**: the default slowapi backend is **in-memory and per-process**. With multiple workers, switch to a Redis-backed key function so limits are shared.
* **Logs**: keep `LOG_FORMAT=json` so structured logs land cleanly in your aggregator.
* **Secrets**: rotate `AUTH_SECRET_KEY` via your secret store at deploy time.

## 📌 Deployment checklist

- [ ] Database reachable + migrations applied
- [ ] `ENVIRONMENT=production`
- [ ] Strong `AUTH_SECRET_KEY` injected (not committed)
- [ ] `LOG_FORMAT=json`, correct `LOG_LEVEL`
- [ ] `CORS_ORIGINS` set to your real frontend origins (else disabled)
- [ ] Readiness probe wired to `/readyz`
- [ ] Multi-worker rate limiting resolved (Redis) if >1 worker
