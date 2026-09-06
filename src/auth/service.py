# package-specific business logic
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth import exceptions as auth_exceptions
from src.auth import utils as auth_utils
from src.auth.config import auth_setting
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.schemas import UserUpdate


def create_user(db: Session, user_create: UserCreate) -> User:
    if db.query(User).filter(User.email == user_create.email).first() is not None:
        raise auth_exceptions.UserAlreadyExists("email")
    if db.query(User).filter(User.username == user_create.username).first() is not None:
        raise auth_exceptions.UserAlreadyExists("username")

    user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=auth_utils.hash_password(user_create.password),
    )
    db.add(user)

    # The pre-checks above can race: two concurrent signups may both pass them and
    # reach the INSERT, after which the database's unique constraints reject the
    # second one with an IntegrityError. Catch it and surface a clean 409 instead
    # of letting it bubble up as an opaque 500, re-checking to report the field.
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        if db.query(User).filter(User.email == user_create.email).first() is not None:
            raise auth_exceptions.UserAlreadyExists("email") from None
        raise auth_exceptions.UserAlreadyExists("username") from None
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()

    if user is None or not auth_utils.verify_password(password, user.hashed_password):
        raise auth_exceptions.InvalidCredentials()
    if not user.is_active:
        raise auth_exceptions.InactiveUser()
    return user


def get_user_by_token(db: Session, token: str) -> User:
    payload = auth_utils.decode_access_token(
        token,
        secret_key=auth_setting.AUTH_SECRET_KEY,
        algorithm=auth_setting.AUTH_ALGORITHM,
    )
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as error:
        raise auth_exceptions.InvalidToken() from error

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise auth_exceptions.UserNotFound()
    if not user.is_active:
        raise auth_exceptions.InactiveUser()
    return user


def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    if user_update.username is not None and user_update.username != user.username:
        if db.query(User).filter(User.username == user_update.username).first() is not None:
            raise auth_exceptions.UserAlreadyExists("username")
        user.username = user_update.username
    if user_update.password is not None:
        user.hashed_password = auth_utils.hash_password(user_update.password)

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise auth_exceptions.UserAlreadyExists("username") from None
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
