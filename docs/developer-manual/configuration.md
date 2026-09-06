# Configuration

All application configuration is loaded from a `.env` file (or real environment variables) with `pydantic-settings`. There are two settings classes:

* `src.core.config.SrcSetting` → shared/global settings (`src_setting`).
* `src.auth.config.AuthSetting` → authentication-only settings (`auth_setting`).

Both inherit from `EnvFileLoader`, whose only job is to read `.env` and ignore unknown keys (`extra="ignore"`).

> 💡 **Why `extra="ignore"`?** It lets every settings class read the *same* `.env` while only picking the fields it declares. Your `.env` can then safely contain variables for the app, Alembic, and tests together.

## 🌍 Loading priority

`pydantic-settings` merges sources in this order (later wins):

1. `.env` file values
2. real OS environment variables

So a real environment variable overrides what is in `.env`. This is exactly how CI supplies secrets without a `.env`.

## 📋 Environment variables reference

### Connection (required unless overridden in CI/tests)

| Variable          | Type | Required   | Description                                                                                                   |
| ----------------- | ---- | ---------- | ------------------------------------------------------------------------------------------------------------- |
| `DB_URL`          | str  | ✅          | SQLAlchemy connection string for the running API. In Docker use `fastapi-postgres`; on host use `localhost`.  |
| `AUTH_SECRET_KEY` | str  | ✅          | Key signing the JWT tokens. **Generate a strong one** (`openssl rand -hex 32`).                               |
| `ALEMBIC_DB_URL`  | str  | ✅ (manual) | Read directly by `alembic/env.py` (not by the app). Always uses `localhost` because Alembic runs on the host. |

### Application behaviour

| Variable       | Type | Default       | Description                                                                                         |
| -------------- | ---- | ------------- | --------------------------------------------------------------------------------------------------- |
| `ENVIRONMENT`  | str  | `development` | `development` or `production`. Enables the `Strict-Transport-Security` header only in `production`. |
| `LOG_LEVEL`    | str  | `INFO`        | Python log level.                                                                                   |
| `LOG_FORMAT`   | str  | `console`     | `console` for human-readable logs, `json` for log aggregators.                                      |
| `CORS_ORIGINS` | str  | `""`          | Comma-separated allowed CORS origins. Empty disables CORS.                                          |

### Authentication tuning (`AuthSetting`)

| Variable                    | Type | Default | Description                |
| --------------------------- | ---- | ------- | -------------------------- |
| `AUTH_SECRET_KEY`           | str  | —       | JWT signing secret.        |
| `AUTH_ALGORITHM`            | str  | `HS256` | JWT signing algorithm.     |
| `AUTH_TOKEN_EXPIRE_MINUTES` | int  | `60`    | Token lifetime in minutes. |

### Test-only

| Variable      | Type | Default                                                   | Description                                  |
| ------------- | ---- | --------------------------------------------------------- | -------------------------------------------- |
| `TEST_DB_URL` | str  | `postgresql://postgres:1234@localhost:5432/postgres_test` | The `postgres_test` database used by pytest. |

## 🧪 Rate limits & pagination

These are currently **constants in code**, not env vars:

* Login / register limits live in `src.core.rate_limit` (`LOGIN_RATE_LIMIT`, `REGISTER_RATE_LIMIT`).
* Pagination default page size lives at the endpoint (`limit=20`).

> 💡 Tip: promote these to `SrcSetting` fields if you want to tune them per environment without editing code.

## 📄 Example `.env`

```bash
# --- Connection ---
DB_URL=postgresql://postgres:1234@fastapi-postgres:5432/postgres
ALEMBIC_DB_URL=postgresql://postgres:1234@localhost:5432/postgres
AUTH_SECRET_KEY=replace-with-openssl-rand-hex-32

# --- Behaviour ---
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_FORMAT=console
CORS_ORIGINS=http://localhost:3000

# --- Test ---
TEST_DB_URL=postgresql://postgres:1234@localhost:5432/postgres_test
```

## ⚠️ Troubleshooting

* **App crashes at import with a validation error** — most likely a required variable (`DB_URL`, `AUTH_SECRET_KEY`) is missing from `.env`. Look for `pydantic_settings` / `ValidationError` in the traceback.
* **CORS headers absent** — `CORS_ORIGINS` is empty or does not include the request `Origin`.
* **Migrations can't connect** — `ALEMBIC_DB_URL` points at the container hostname (`fastapi-postgres`) instead of `localhost`.
