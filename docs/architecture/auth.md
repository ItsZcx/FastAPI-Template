# Authentication

The `src/auth/` package provides a **complete, minimal user-management system** over **JWT bearer tokens**. It is the reference implementation for the package pattern described in [Project Structure](project_structure.md).

## 📦 Package layout

```
src/auth/
├── config.py        # AuthSetting: AUTH_SECRET_KEY, AUTH_ALGORITHM, AUTH_TOKEN_EXPIRE_MINUTES
├── models.py        # User table
├── schemas.py       # UserCreate, UserRead, UserUpdate, LoginRequest, TokenResponse
├── exceptions.py    # AuthError hierarchy
├── utils.py         # password hashing + JWT encode/decode (pure functions)
├── service.py       # business logic over the User model
├── dependencies.py  # get_current_user + bearer scheme
└── router.py        # /auth/* endpoints, rate-limited
```

> 💡 The stateful part (models, service) and the stateless helpers (JWT, hashing) are separated exactly as the package convention prescribes: **business logic in `service.py`, pure helpers in `utils.py`**.

## 🎫 API surface

All routes are under the prefix `/auth` (tag `Auth`) and except `/register` + `/login`, all require the `Authorization: Bearer <token>` header.

| Method | Path             | Auth | Description                                            |
| ------ | ---------------- | ---- | ------------------------------------------------------ |
| POST   | `/auth/register` | no   | create user (email, username, password) — rate-limited |
| POST   | `/auth/login`    | no   | exchange credentials for a JWT — rate-limited          |
| GET    | `/auth/me`       | yes  | return the authenticated user                          |
| PATCH  | `/auth/me`       | yes  | update username / password                             |
| DELETE | `/auth/me`       | yes  | delete the account                                     |

## 🧑💻 The `User` model

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

* **Login identity is `email`** — it cannot be changed after creation (that is why `UserUpdate` has no email field).
* Only `hashed_password` is stored — never the plaintext.
* The database enforces uniqueness on both `email` and `username`.

## 🔒 Passwords — PBKDF2 (stdlib, no extra dependency)

`src/auth/utils.py` hashes with **PBKDF2-HMAC-SHA256**, the OWASP-recommended iteration count **600,000**, and a per-user random salt.

* **`hash_password(password)`** → stores `"<salt>$<hex digest>"`.
* **`verify_password(password, stored)`** → recomputes and compares with a **constant-time** comparison (`hmac.compare_digest`).

> ✅ No `bcrypt`/`passlib` dependency is needed. If you later prefer argon2 or bcrypt, only `utils.hash_password` / `verify_password` change — callers and storage stay the same (they see only the `"salt$digest"` string).

## 🪙 JWT tokens

`utils.create_access_token(...)` builds an HS256-signed JWT:

* `sub` = the user id (as a string, per the JWT spec)
* `iat` / `exp` set from `AUTH_TOKEN_EXPIRE_MINUTES` (default **60** minutes)
* signed with `AUTH_SECRET_KEY` + `AUTH_ALGORITHM` (default `HS256`)

`utils.decode_access_token(...)` verifies signature, `exp`, and returns the payload — raising `InvalidToken` on any failure (expired, wrong key, malformed, etc.).

`TokenResponse` is `{ "access_token": "...", "token_type": "bearer" }`.

## 🧠 Login → use the token (flow)

```mermaid
sequenceDiagram
    participant C as Client
    participant R as /auth/login
    participant DB as Database

    C->>R: POST /auth/login {email, password}
    R->>DB: find user by email
    R->>R: verify_password(pw, stored_hash)
    alt correct
        R-->>C: 200 {access_token, token_type:"bearer"}
        Note over C: Client stores token (e.g. memory / localStorage)
        C->>R: GET /auth/me  "Authorization: Bearer <token>"
        R->>R: decode JWT → user id claim
        R->>DB: load user; check is_active
        R-->>C: 200 user JSON
    else wrong credentials
        R-->>C: 401
    end
```

## 🛂 Protecting an endpoint

`src/auth/dependencies.py` exposes the reusable guard:

```python
current_user_dependency = Annotated[User, Depends(get_current_user)]
```

Use it on any router:

```python
from src.auth.dependencies import current_user_dependency

@router.get("/me")
def get_me(current_user: current_user_dependency):
    return current_user
        # ^ the resolved User is injected
```

Internals of `get_current_user`:

1. Reads the `Bearer` token with `HTTPBearer(auto_error=False)` (so a *missing* header is handled by us, not Starlette's default 403).
2. Calls `service.get_user_by_token(...)`, which decodes the JWT and loads the user.
3. Rejects inactive users via `is_active`.

> 🔀 This is the same dependency you import into **your** routers; the `todo` example only demonstrates unauthenticated CRUD, so copy the auth route pattern into the package you extend.

## 🌐 From other code / swagger

* Swagger UI (<http://localhost:8080/docs>) shows an **Authorize** button for the bearer scheme — paste the token there to fire authenticated requests from the UI.
* The `login` endpoint takes a **JSON body** (`{email, password}`), not an OAuth2 form. This keeps the client simple; see [Conventions](../architecture/conventions.md).

### Example round-trip

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"supersecret123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl http://localhost:8080/auth/me -H "Authorization: Bearer $TOKEN"
```

## ✅ Validation & business rules

* `email` matches an email regex on both `register` and `login`.
* `username`: 1–32 characters.
* `password`: 8–128 characters (register/update).
* Duplicate `email` / `username` → **409 Conflict** with a helpful detail.
* Unknown user, wrong password → **401**.
* Deactivated-or-now-deleted user id from a still-valid token → **404/403** depending (mapped in the error-table below).

## 🚦 Rate limiting

Both public endpoints are protected by slowapi so `register` and `login` can't be hammered (see [Core Cross-cutting](../developer-manual/core_crosscutting.md)):

* `/auth/login` → `5/minute`
* `/auth/register` → `3/minute`

## 🄱 Error mapping (auth exceptions → HTTP)

Auth raises domain exceptions (e.g. `InvalidCredentials`, `InvalidToken`, `UserAlreadyExists`, `InactiveUser`, `UserNotFound`). `src/main.py` maps them centrally in one table (details in [Health & Errors](health_and_errors.md)).

> 🔐 **Key security notes for adopters**: rotate `AUTH_SECRET_KEY` in production; keep tokens short-lived; add refresh tokens only if your UI needs long-lived sessions. Password never leaves your DB except via the `/me` endpoints which hide `hashed_password` through `response_model=UserRead`.
