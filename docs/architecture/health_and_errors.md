# Health Checks and Error Handling

Every process needs liveness and readiness probes for orchestration, and consistent error responses for consumers. The template wires both at startup in `src/main.py`, plus a small `src/health/` package.

## Health endpoints

`src/health/router.py` exposes two public probes. They are unauthenticated and not rate-limited.

| Endpoint       | Kind      | Behaviour                                                                                                                                        |
| -------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GET /healthz` | liveness  | returns `200` with `{"status":"ok"}` as long as the process is alive                                                                             |
| `GET /readyz`  | readiness | runs `SELECT 1` against PostgreSQL. Returns `200` with `{"status":"ready"}`, or `503` with `{"status":"unavailable"}` when the database is down. |

```bash
curl http://localhost:8080/healthz   # {"status":"ok"}
curl http://localhost:8080/readyz    # {"status":"ready"}
```

Use `/readyz` as the load-balancer or orchestrator health check. It catches a down database before traffic routes there. `/healthz` is the lightweight "am I up" probe.

## How the app starts and is wired

`src/main.py` is declarative, top-down glue. Reading it top to bottom shows the runtime.

1. `configure_logging(...)` sets up structlog from settings.
2. Build `app = FastAPI(title=...)`.
3. Attach slowapi: `app.state.limiter = limiter` and the `RateLimitExceeded` handler, which returns 429.
4. Register middleware. The last one added is outermost: CORS, then security headers, then request-ID.
5. Include the routers: health, package, auth.
6. Register the central `AuthError` handler.

## Domain error handling

Bigger domains raise typed exceptions, and `main.py` holds a small map from exception to HTTP status:

```python
STATUS_BY_AUTH_ERROR = {
    UserAlreadyExists: 409,
    InvalidCredentials: 401,     # + WWW-Authenticate: Bearer
    InvalidToken: 401,           # + WWW-Authenticate: Bearer
    InactiveUser: 403,
    UserNotFound: 404,
}

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, error: AuthError):
    status_code = STATUS_BY_AUTH_ERROR[type(error)]
    # ...
```

The endpoint raises intent, such as `UserAlreadyExists`, and one reviewer-friendly place decides the mapping. Adding a 500 means editing one table, not hunting through handlers.

## Rate-limit response

slowapi is registered globally. Any endpoint guarded by `@limiter.limit()` that exceeds its quota returns:

```json
{
  "detail": "429: Too Many Requests..."
}
```

with HTTP status 429. See [Core Cross-cutting Features](../developer-manual/core_crosscutting.md).

## Error envelope

Responses reuse the FastAPI `{"detail": ...}` envelope for simplicity and to keep validation errors, 422, identical across the app. See [Conventions](conventions.md). Auth errors add a `WWW-Authenticate: Bearer` header on 401 so clients know how to authenticate.

## Add a domain guard

1. In the new package, define `class MyError(Exception)` and subclasses in `src/<pkg>/exceptions.py`.
2. Raise them from `src/<pkg>/service.py`.
3. Register a handler, or extend the map approach, in `main.py` to map them to status codes.

The `package/` example raises `HTTPException` directly because it has no custom errors. For a real domain, prefer explicit exceptions and a central map.
