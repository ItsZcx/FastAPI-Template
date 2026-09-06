# specific router dependencies
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from src.auth import exceptions as auth_exceptions
from src.auth import service as auth_service
from src.auth.models import User
from src.database import db_dependency

# auto_error=False so missing/invalid credentials raise our InvalidToken
# exception and are handled by the global handler in src.main (HTTP 401)
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: db_dependency,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise auth_exceptions.InvalidToken()

    return auth_service.get_user_by_token(db, credentials.credentials)


current_user_dependency = Annotated[User, Depends(get_current_user)]
