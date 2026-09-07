# Configuration

The app loads configuration from a `.env` file or real environment variables, using `pydantic-settings`. Two settings classes read it:

* `src.core.config.SrcSetting` for shared settings, exposed as `src_setting`.
* `src.auth.config.AuthSetting` for authentication settings, exposed as `auth_setting`.

Both inherit from `EnvFileLoader`, which reads `.env` and ignores unknown keys because it sets `extra="ignore"`.

The project's `.env` drives host-side tooling: running the app locally, Alembic, and pytest. Inside Docker, `compose.yaml` injects the runtime values as environment variables using the `fastapi-postgres` hostname. The container does not read a `.env`.

`extra="ignore"` lets each settings class read the same `.env` and pick only the fields it declares. One `.env` can then hold variables for the app, Alembic, and tests together.

## Loading priority

`pydantic-settings` merges these sources in order. A later source wins.

1. Values in the `.env` file.
2. Real OS environment variables.

A real environment variable overrides the `.env` value. This is how CI supplies secrets without a `.env` file.

## Environment variables reference

### Connection

These are required unless CI or the tests override them.

| Variable          | Type | Required     | Description                                                                                                                                                      |
| ----------------- | ---- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DB_URL`          | str  | yes          | SQLAlchemy connection string for the running API. Use `localhost` when the app runs on the host. In Docker, `compose.yaml` sets the `fastapi-postgres` hostname. |
| `AUTH_SECRET_KEY` | str  | yes          | Key that signs the JWT tokens. Generate one with `openssl rand -hex 32`.                                                                                         |
| `ALEMBIC_DB_URL`  | str  | yes (manual) | Read by `alembic/env.py`, not by the app. Always uses `localhost` because Alembic runs on the host.                                                              |

### Application behaviour

| Variable       | Type | Default       | Description                                                                                      |
| -------------- | ---- | ------------- | ------------------------------------------------------------------------------------------------ |
| `ENVIRONMENT`  | str  | `development` | `development` or `production`. Adds the `Strict-Transport-Security` header only in `production`. |
| `LOG_LEVEL`    | str  | `INFO`        | Python log level.                                                                                |
| `LOG_FORMAT`   | str  | `console`     | `console` for human-readable logs, `json` for log aggregators.                                   |
| `CORS_ORIGINS` | str  | `""`          | Comma-separated allowed CORS origins. Empty disables CORS.                                       |

### Authentication tuning (`AuthSetting`)

| Variable                    | Type | Default | Description                |
| --------------------------- | ---- | ------- | -------------------------- |
| `AUTH_SECRET_KEY`           | str  | none    | JWT signing secret.        |
| `AUTH_ALGORITHM`            | str  | `HS256` | JWT signing algorithm.     |
| `AUTH_TOKEN_EXPIRE_MINUTES` | int  | `60`    | Token lifetime in minutes. |

### Test-only

| Variable      | Type | Default                                                   | Description                                  |
| ------------- | ---- | --------------------------------------------------------- | -------------------------------------------- |
| `TEST_DB_URL` | str  | `postgresql://postgres:1234@localhost:5432/postgres_test` | The `postgres_test` database used by pytest. |

## Rate limits and pagination

These are constants in code, not environment variables:

* Login and register limits live in `src.core.rate_limit.py` as `LOGIN_RATE_LIMIT` and `REGISTER_RATE_LIMIT`.
* The pagination default page size is the `limit` default (`20`) on the endpoint.

To tune them per environment without editing code, move them into `SrcSetting` fields.

## Example `.env`

This drives host-side execution: the local app, Alembic, and pytest. Inside Docker, `compose.yaml` configures the app instead.

```bash
# Connection (host side; Docker sets its own DB_URL)
DB_URL=postgresql://postgres:1234@localhost:5432/postgres
ALEMBIC_DB_URL=postgresql://postgres:1234@localhost:5432/postgres
AUTH_SECRET_KEY=replace-with-openssl-rand-hex-32

# Behaviour
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_FORMAT=console
CORS_ORIGINS=http://localhost:3000

# Test
TEST_DB_URL=postgresql://postgres:1234@localhost:5432/postgres_test
```

## Troubleshooting

**The app crashes at import with a validation error.** A required variable is missing from `.env`. Usually that is `DB_URL` or `AUTH_SECRET_KEY`. Check the traceback for `pydantic_settings` or `ValidationError`.

**CORS headers are absent.** `CORS_ORIGINS` is empty, or it does not include the request `Origin`.

**Migrations cannot connect.** `ALEMBIC_DB_URL` points at the container hostname `fastapi-postgres` instead of `localhost`.
