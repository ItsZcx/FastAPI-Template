# Deployment

This page explains how to build, test, and prepare the repository for deployment. It ships a CI and Docker setup that works on any host that can run containers.

This project is a template. It has no staging or production infrastructure. It provides the repeatable pieces: a Dockerfile, a CI workflow, migrations, and the guidance below.

## Deliverables

| Asset                      | Purpose                                                      |
| -------------------------- | ------------------------------------------------------------ |
| `Dockerfile`               | Builds the API image with uv and runtime dependencies only.  |
| `compose.yaml`             | Runs `fastapi` on port `8080` and `postgres` on port `5432`. |
| `.github/workflows/ci.yml` | Runs lint, format, and tests on every push and pull request. |
| `alembic/`                 | Database migrations, applied on the host at deploy time.     |

## The production image

```dockerfile
FROM python:3.10-alpine3.20
ENV PYTHONUNBUFFERED=1 UV_NO_CACHE=1
RUN pip install --no-cache-dir uv==0.12.10
RUN uv sync --no-dev --frozen   # runtime deps only, from the committed lock
CMD ["uv", "run", "--frozen", "fastapi", "run", "src/main.py", "--reload", "--port", "8080"]
```

* `--no-dev` installs only runtime dependencies. Ruff, pytest, and pre-commit never ship to production.
* `--frozen` installs exactly what `uv.lock` pins, so the image is reproducible.
* No `.env` is baked into the image. Configuration arrives at runtime as environment variables. `compose.yaml` provides them locally; your platform provides them in production. Inside a container the database is `fastapi-postgres`, not `localhost`.
* `--reload` in the `CMD` is for development. For production, drop `--reload`, and add `--workers` behind a load balancer if you need concurrency.

The image exposes port `8080`. Route external traffic there, or remap it in `compose.yaml`.

## CI pipeline

`.github/workflows/ci.yml` triggers on push and pull request.

| Stage                | Command                        | Purpose                     |
| -------------------- | ------------------------------ | --------------------------- |
| Provision PostgreSQL | `postgres:16.2-alpine` service | gives tests a real database |
| Install uv and deps  | `uv sync --frozen`             | uv `0.12.10`                |
| Ruff lint            | `uv run ruff check .`          | code style                  |
| Ruff format          | `uv run ruff format --check .` | formatting                  |
| Tests                | `uv run pytest -q`             | runs the full suite         |

The workflow sets `DB_URL`, `TEST_DB_URL`, and `AUTH_SECRET_KEY` as `env` values.

The pipeline is test-first. Nothing advances unless the checks pass. It does not build or push Docker images. Add a build job when you have a registry.

### Build and push an image

This extension builds and pushes after tests pass:

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

## Deploy the API

Pick a host and apply the same steps.

1. Provision PostgreSQL reachable from the app. Run it with Compose as in development if you like.
2. Set real environment variables. Do not rely on a committed `.env`. Set `DB_URL`, `AUTH_SECRET_KEY`, and `ENVIRONMENT=production`. Tune `LOG_FORMAT=json`, `CORS_ORIGINS`, and `LOG_LEVEL` on your platform. Environment variables override the `.env` file through `pydantic-settings`.
3. Run the migrations against the real database:
   ```bash
   uv run alembic upgrade head
   ```
4. Start the image and expose port `8080`.
5. Put load balancing and TLS in front. Set `ENVIRONMENT=production` so `Strict-Transport-Security` is added.

Use `/readyz` as the orchestrator health check. It returns 503 when the database is unreachable. `/healthz` is the lighter liveness check.

## Tuning for production scale

* **Workers.** Run several uvicorn workers with `--workers N` behind a load balancer for concurrency.
* **Rate limiting.** The default slowapi backend is in-memory and per-process. With multiple workers, switch to a Redis-backed key function so limits are shared.
* **Logs.** Keep `LOG_FORMAT=json` so structured logs land cleanly in your aggregator.
* **Secrets.** Rotate `AUTH_SECRET_KEY` through your secret store at deploy time.

## Deployment checklist

- [ ] Database reachable and migrations applied
- [ ] `ENVIRONMENT=production`
- [ ] Strong `AUTH_SECRET_KEY` injected, not committed
- [ ] `LOG_FORMAT=json` and correct `LOG_LEVEL`
- [ ] `CORS_ORIGINS` set to your real frontend origins, or empty
- [ ] Readiness probe wired to `/readyz`
- [ ] Multi-worker rate limiting resolved with Redis if more than one worker
