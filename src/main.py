from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.auth.exceptions import AuthError
from src.auth.exceptions import InactiveUser
from src.auth.exceptions import InvalidCredentials
from src.auth.exceptions import InvalidToken
from src.auth.exceptions import UserAlreadyExists
from src.auth.exceptions import UserNotFound
from src.auth.router import router as auth_router
from src.core.config import src_setting
from src.core.logging import configure_logging
from src.core.middleware import RequestIDMiddleware
from src.core.middleware import SecurityHeadersMiddleware
from src.core.middleware import get_cors_origins
from src.core.rate_limit import limiter
from src.health.router import router as health_router
from src.package.router import router as package_router

configure_logging(src_setting.LOG_LEVEL, src_setting.LOG_FORMAT)

app = FastAPI(title="FastAPI-Template")

# slowapi needs the limiter on app.state to enforce @limiter.limit decorators
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, error: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": str(error)})


# Middleware: last added is the outermost layer
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=bool(cors_origins) and "*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(package_router)
app.include_router(auth_router)

# Map auth package errors to HTTP responses
STATUS_BY_AUTH_ERROR = {
    UserAlreadyExists: 409,
    InvalidCredentials: 401,
    InvalidToken: 401,
    InactiveUser: 403,
    UserNotFound: 404,
}


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, error: AuthError):
    status_code = STATUS_BY_AUTH_ERROR[type(error)]
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    return JSONResponse(status_code=status_code, content={"detail": str(error)}, headers=headers)


@app.get("/")
def read_root():
    return {"msg": "Server is running"}
