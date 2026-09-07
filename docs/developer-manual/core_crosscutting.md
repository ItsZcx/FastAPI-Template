# Core Cross-cutting Features

Everything that is not domain logic lives in `src/core/`. This is the plumbing every endpoint uses: configuration, the database engine, logging, middleware, rate limiting, and global exceptions. This page explains each component and how they plug together.

For the request lifecycle, see [Health Checks & Error Handling](../architecture/health_and_errors.md).

## What lives where

| File                                  | Responsibility                                                                                            |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `src/core/config.py`                  | `EnvFileLoader` and the global `SrcSetting`. See [Configuration](configuration.md).                       |
| `src/core/database.py`                | Engine, sessions, `Base`, `get_db`, `db_dependency`. See [Database & Migrations](database_migrations.md). |
| `src/core/logging.py`                 | structlog setup with console or JSON output.                                                              |
| `src/core/middleware.py`              | Request-ID and security-headers middleware, plus the CORS helper.                                         |
| `src/core/rate_limit.py`              | The shared slowapi `Limiter` and per-route limits.                                                        |
| `src/core/exceptions.py`, `schema.py` | Placeholders for global app exceptions and general pydantic models.                                       |

## Logging

`src/core/logging.py::configure_logging(level, format)` runs once at import in `src/main.py`. It:

1. Builds a `structlog.stdlib.ProcessorFormatter`.
2. Attaches it to the stdlib root logger, then routes `uvicorn`, `uvicorn.error`, and `uvicorn.access` through the same formatter.
3. Configures structlog to use stdlib as its backend and to merge context variables.

`LOG_FORMAT` picks the renderer:

* `console` uses `structlog.dev.ConsoleRenderer()`, which is colourful and human-friendly.
* `json` uses `structlog.processors.JSONRenderer()`, one JSON object per line, ready for Datadog, Loki, or CloudWatch.

To log from your code:

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

* The Request-ID middleware binds `request_id` into structlog context variables per request.
* `merge_contextvars` in the processor chain injects it into every log line from app code.
* The same value appears on responses as the `X-Request-ID` header.

One limit: uvicorn's own `uvicorn.access` line cannot pick up per-request context. It is emitted outside the middleware context over an ASGI streaming response. Request IDs therefore appear only on app-level logs and the response header, which is enough to trace a request across services. For IDs in access logs too, replace uvicorn's access logger with a custom formatter.

## Middleware

Three layers are registered in `src/main.py`. In Starlette, the last `add_middleware()` call becomes the outermost layer:

`CORSMiddleware` wraps `SecurityHeadersMiddleware` wraps `RequestIDMiddleware` wraps the app.

### RequestIDMiddleware

It is pure ASGI, written as `__call__`, not `BaseHTTPMiddleware`. It:

* Reads an inbound `X-Request-ID` header, or generates a `uuid4` hex value.
* Binds it into structlog context with `clear_contextvars` and `bind_contextvars`.
* Adds `X-Request-ID` to the response.

Pure ASGI matters. Route handlers run in the same task, so they see the context variables. `BaseHTTPMiddleware` runs the inner app in a separate task and loses them.

### SecurityHeadersMiddleware

It applies a conservative set of headers to every response with `setdefault`, so it never overrides values the app sets:

* `X-Content-Type-Options: nosniff`
* `X-Frame-Options: DENY`
* `Referrer-Policy: no-referrer`
* `Strict-Transport-Security: max-age=31536000; includeSubDomains`, only when `ENVIRONMENT=production`

A strict Content-Security-Policy is not baked in. It matters for browser-rendered content and can break a separate frontend when set wrong. For a JSON API, the headers above suffice. Extend `SecurityHeadersMiddleware` if you need CSP.

### CORS

`get_cors_origins()` parses `CORS_ORIGINS`, a comma-separated list, and `src/main.py` registers Starlette's `CORSMiddleware`.

* `allow_credentials` is enabled only when origins are non-empty and do not contain `*`. Browsers reject `*` with credentials.
* An empty `CORS_ORIGINS` disables CORS. No cross-origin headers are added, which is right for server-only APIs.

## Rate limiting

One shared slowapi `Limiter` is created in `src/core/rate_limit.py` and attached to the app as `app.state.limiter`. Two constants are exported and reused by the auth router:

```python
LOGIN_RATE_LIMIT = "5/minute"
REGISTER_RATE_LIMIT = "3/minute"
```

Usage:

```python
@router.post("/login", ...)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(request: Request, db: db_dependency, login_request: LoginRequest):
    ...
```

* The `limiter.limit()` decorator must wrap an endpoint that accepts `request: Request`.
* slowapi needs `app.state.limiter = limiter` and a `RateLimitExceeded` handler. Both are wired in `src/main.py` and return 429 when a limit is breached.
* The default backend is in-memory and per-process. For multiple workers, replace `get_remote_address` with a Redis-backed key function. Otherwise you under-limit.

## Testing hooks

* Tests reset the shared limiter before each test with `limiter.reset()` in fixtures, so rate-limited endpoints behave deterministically.
* The dependency override swaps `get_db` for an isolated test session. See [Testing](../architecture/testing.md).
