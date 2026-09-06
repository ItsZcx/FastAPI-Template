# Router with the endpoints
from fastapi import APIRouter
from starlette import status

from src.auth import utils as auth_utils
from src.auth.config import auth_setting
from src.auth.dependencies import current_user_dependency
from src.auth.schemas import LoginRequest
from src.auth.schemas import TokenResponse
from src.auth.schemas import UserCreate
from src.auth.schemas import UserRead
from src.auth.schemas import UserUpdate
from src.auth.service import authenticate_user
from src.auth.service import create_user
from src.auth.service import delete_user
from src.auth.service import update_user
from src.database import db_dependency

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(db: db_dependency, user_create: UserCreate):
    return create_user(db, user_create)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(db: db_dependency, login_request: LoginRequest):
    user = authenticate_user(db, login_request.email, login_request.password)
    access_token = auth_utils.create_access_token(
        subject=user.id,
        secret_key=auth_setting.AUTH_SECRET_KEY,
        algorithm=auth_setting.AUTH_ALGORITHM,
        expires_minutes=auth_setting.AUTH_TOKEN_EXPIRE_MINUTES,
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserRead)
def get_me(current_user: current_user_dependency):
    return current_user


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=UserRead)
def update_me(db: db_dependency, user_update: UserUpdate, current_user: current_user_dependency):
    return update_user(db, current_user, user_update)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: db_dependency, current_user: current_user_dependency):
    delete_user(db, current_user)
