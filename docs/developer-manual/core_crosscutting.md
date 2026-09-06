# Core Cross-cutting Features

Everything that is **not** domain logic lives in `src/core/`. It is the "plumbing" every endpoint benefits from: configuration, the database engine, logging, middleware, rate limiting, and global exceptions. This page explains each component and how they plug together.

> For how they fit into the request lifecycle, see [Health Checks & Error Handling](../architecture/health_and_errors.md) and the middleware ordering note below.

## 📦 What lives where

| File                                  | Responsibility                                                                                            |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `src/core/config.py`                  | `EnvFileLoader` + global `SrcSetting` (see [Configuration](configuration.md))                             |
| `src/core/database.py`                | engine, sessions, `Base`, `get_db`, `db_dependency` (see [Database & Migrations](database_migrations.md)) |
| `src/core/logging.py`                 | structlog setup — console vs JSON output                                                                  |
| `src/core/middleware.py`              | request-ID + security-headers middleware and the CORS helper                                              |
| `src/core/rate_limit.py`              | shared slowapi `Limiter` + per-route limits                                                               |
| `src/core/exceptions.py`, `schema.py` | placeholders for global app exceptions / general pydantic models                                          |

## 🪵 Logging (structlog)

`src/core/logging.py::configure_logging(level, format)` is called once at import in `src/main.py`. It:

1. Builds a `structlog.stdlib.ProcessorFormatter`.
2. Attaches it to the **stdlib root logger**, then re-routes `uvicorn`, `uvicorn.error` and `uvicorn.access` through the same formatter.
3. Configures structlog to use stdlib as its backend and to merge context variables.

The `LOG_FORMAT` setting picks the renderer:

* `console` → `structlog.dev.ConsoleRenderer()` (colourful, human-friendly).
* `json` → `structlog.processors.JSONRenderer()` (one JSON object per line — ready for Datadog, Loki, CloudWatch, …).

**Logging from your code:**

```python
from src.core.logging import get_logger

logger = get_logger(__name__)

def handle(user_id: int) -> None:
    logger.info("processing user", user_id=user_id)
```

Example JSON output:

```json
{"event": "processing user", "request_id": "9bca88ea...", "level": "info", "logger": "...", "user_id": 7, "timestamp": "2026-..."}
```

### request_id correlation

* The [Request-ID middleware](#request-id-middleware) binds `request_id` into structlog **context variables** per request.
* `merge_contextvars` in the processor chain injects it into every log line **from code**.
* The same value is echoed on responses as the `X-Request-ID` header.

> ⚠️ **Known limitation**: uvicorn's *own* `uvicorn.access` line can't pick up per-request context (it is emitted outside the middleware context over an ASGI streaming response). Request IDs are therefore present on **app-level logs and the response header**, which is enough to trace a request across services. If you need IDs in access logs too, replace uvicorn's access logger with a custom formatter.

## 🛡️ Middleware (`src/core/middleware.py`)

Three layers are registered in `src/main.py`. In Starlette, **the last `add_middleware(...)` call becomes the outermost layer**:

`CORSMiddleware` → `SecurityHeadersMiddleware` → `RequestIDMiddleware` → app

### RequestIDMiddleware (pure ASGI)

* Reads an inbound `X-Request-ID` header **or** generates a `uuid4` hex value.
* Binds it into structlog context (`clear_contextvars` + `bind_contextvars`).
* Adds `X-Request-ID` to the **response**.

> 💡 Written as **pure ASGI** (`__call__`), not `BaseHTTPMiddleware`. Context variables set here are visible to route handlers because they run in the same task — `BaseHTTPMiddleware` would run the inner app in a separate task and lose them.

### SecurityHeadersMiddleware (conservative subset)

Applied to every response via `setdefault` (never overrides app-set values):

* `X-Content-Type-Options: nosniff`
* `X-Frame-Options: DENY`
* `Referrer-Policy: no-referrer`
* Only when `ENVIRONMENT=production` → `Strict-Transport-Security: max-age=31536000; includeSubDomains`

> 💡 A strict Content-Security-Policy is deliberately **not** baked in: it shines for browser-rendered content and can break a separate frontend if set wrong. For a JSON API the "must-have" headers above suffice. Extend `SecurityHeadersMiddleware` if your adopters need CSP.

### CORS

`get_cors_origins()` parses `CORS_ORIGINS` (comma-separated) and `src/main.py` registers Starlette's `CORSMiddleware`:

* `allow_credentials` is enabled **only** when origins are non-empty and do not contain `*` (browsers reject `*` + credentials).
* Empty `CORS_ORIGINS` ⇒ CORS effectively disabled (no cross-origin headers) — the right default for server-only APIs.

## 🚦 Rate limiting (`src/core/rate_limit.py`)

A single shared slowapi `Limiter` is created here and attached to the app (`app.state.limiter`). Two rate constants are exported and reused by the auth router:

```python
LOGIN_RATE_LIMIT = "5/minute"
REGISTER_RATE_LIMIT = "3/minute"
```

Usage pattern:

```python
@router.post("/login", ...)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(request: Request, db: db_dependency, login_request: LoginRequest):
    ...
```

Notes:

* The `limiter.limit(...)` decorator **must** wrap an endpoint that accepts `request: Request`.
* slowapi requires `app.state.limiter = limiter` and a `RateLimitExceeded` exception handler — both are wired in `src/main.py`, returning **429** when breached.
* The **default backend is in-memory** and therefore **per-process**. For multi-worker / multi-process production, replace `get_remote_address` with a Redis-backed key function (slowapi works with Redis) or you will silently under-limit.

## 🧪 Testing hooks

* Tests reset the shared limiter before each test (`limiter.reset()` in fixtures) so rate-limited endpoints can be exercised deterministically.
* The dependency override mechanism swaps `get_db` for an isolated test session — see [Testing](../architecture/testing.md).
