from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from src.auth.exceptions import AuthError
from src.auth.exceptions import InactiveUser
from src.auth.exceptions import InvalidCredentials
from src.auth.exceptions import InvalidToken
from src.auth.exceptions import UserAlreadyExists
from src.auth.exceptions import UserNotFound
from src.auth.router import router as auth_router
from src.package.router import router as package_router

app = FastAPI(title="FastAPI-Template")
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
