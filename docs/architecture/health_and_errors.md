# Health Checks & Error Handling

Every process needs liveness/readiness probes for orchestration, and consistent error responses for consumers. Both are wired in this template at **startup in `src/main.py`** plus a tiny `src/health/` package.

## 🟢 Health endpoints

`src/health/router.py` exposes two public (unauthenticated, unrate-limited) probes:

| Endpoint       | Kind          | Behaviour                                                                                                         |
| -------------- | ------------- | ----------------------------------------------------------------------------------------------------------------- |
| `GET /healthz` | **liveness**  | always `200` with `{"status":"ok"}` as long as the process is alive                                               |
| `GET /readyz`  | **readiness** | runs `SELECT 1` against PostgreSQL → `200 {"status":"ready"}` or `503 {"status":"unavailable"}` if the DB is down |

```bash
curl http://localhost:8080/healthz   # {"status":"ok"}
curl http://localhost:8080/readyz    # {"status":"ready"}
```

> 🩺 Use `/readyz` as the load-balancer/orchestrator health check — it catches "DB is down" before traffic is routed. `/healthz` is the lightweight "am I up" probe.

## 🏗️ How the app starts and is wired

`src/main.py` is **declarative top-down glue**. Reading it top-to-bottom shows the whole runtime:

1. `configure_logging(...)` — structlog setup from settings.
2. Build `app = FastAPI(title=...)`.
3. Attach slowapi: `app.state.limiter = limiter` + the `RateLimitExceeded` → **429** handler.
4. Register middleware (outermost last): **CORS → security headers → request-ID**.
5. Include routers: health, package, auth.
6. Register the central `AuthError` handler.

## 🐛 Domain error handling (one central map)

Bigger domains raise **typed exceptions**, and `main.py` holds a tiny map from exception → HTTP status:

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

Why this pattern? **The endpoint raises intent (`UserAlreadyExists`), and one reviewer-friendly place decides the mapping.** Adding a 5xx? You see it in one table, not scattered across handlers.

## 🧪 Rate-limit response

slowapi is registered globally, so any endpoint guarded by `@limiter.limit(...)` that exceeds its quota gets:

```json
{
  "detail": "429: Too Many Requests..."
}
```

with HTTP status **429** (see [Core Cross-cutting](../developer-manual/core_crosscutting.md)).

## 📦 Error envelope

Responses intentionally reuse the FastAPI `{"detail": ...}` envelope for simplicity and to keep validation errors (422) identical across the app — see [Conventions](conventions.md). Auth errors include a `WWW-Authenticate: Bearer` header on `401` so clients know how to authenticate.

## ✅ Adding a new domain guard

1. In the new package define `class MyError(Exception)` and subclasses in `src/<pkg>/exceptions.py`.
2. Raise them from `src/<pkg>/service.py`.
3. Register a handler (or extend the map approach) in `main.py` mapping them to a status.

> 🔀 Compare: the `package/` example raises `HTTPException` directly because it has no custom errors. For a real domain, prefer explicit exceptions + a central map.
