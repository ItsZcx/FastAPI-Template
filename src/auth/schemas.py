# Pydantic models
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class UserBase(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    username: str = Field(min_length=1, max_length=32)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "username": "johndoe"},
        }
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    # Email is the login identity, so it cannot be changed here
    username: str | None = Field(default=None, min_length=1, max_length=32)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
