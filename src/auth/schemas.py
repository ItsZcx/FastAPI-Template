# Pydantic models
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def normalize_email(value: str) -> str:
    """Normalise an email so lookups and uniqueness are case-insensitive."""
    return value.strip().lower()


class UserBase(BaseModel):
    """Shared fields for a user (used to build request and response models)."""

    email: str = Field(
        description="Login identity. Unique per user. Stored and matched in lowercase.",
        pattern=EMAIL_REGEX,
        examples=["user@example.com"],
    )
    username: str = Field(
        description="Public display name shown on the account. Unique per user. Case-sensitive.",
        min_length=1,
        max_length=32,
        examples=["johndoe"],
    )

    _normalize_email = field_validator("email")(normalize_email)


class UserCreate(UserBase):
    """Payload to create a new user (`POST /auth/register`)."""

    password: str = Field(
        description="Plain-text password. Hashed with PBKDF2-HMAC-SHA256 before storing; never returned.",
        min_length=8,
        max_length=128,
        examples=["supersecret123"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "supersecret123",
            }
        }
    )


class UserUpdate(BaseModel):
    """Optional fields to update on the current user (`PATCH /auth/me`).

    Only the fields you want to change need to be sent. Email is the login
    identity and cannot be changed here.
    """

    username: str | None = Field(
        default=None,
        description="New public display name. Must be unique.",
        min_length=1,
        max_length=32,
        examples=["newusername"],
    )
    password: str | None = Field(
        default=None,
        description="New plain-text password.",
        min_length=8,
        max_length=128,
        examples=["anewsecurepassword"],
    )

    model_config = ConfigDict(json_schema_extra={"example": {"username": "newusername", "password": "supersecret456"}})


class UserRead(BaseModel):
    """A user as returned by the API (never contains the password hash)."""

    id: int = Field(description="Database id of the user.", examples=[1])
    email: str = Field(
        description="Login identity (email address).", pattern=EMAIL_REGEX, examples=["user@example.com"]
    )
    username: str = Field(description="Public display name.", examples=["johndoe"])
    is_active: bool = Field(description="Whether the account is active.", examples=[True])
    created_at: datetime = Field(description="When the user was created (UTC ISO-8601).")

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Credentials to sign in (`POST /auth/login`). Returns a bearer token."""

    email: str = Field(
        description="Email of the account to sign in to. Case-insensitive.",
        pattern=EMAIL_REGEX,
        examples=["user@example.com"],
    )
    password: str = Field(
        description="Password for that account.",
        min_length=1,
        max_length=128,
        examples=["supersecret123"],
    )

    _normalize_email = field_validator("email")(normalize_email)

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "user@example.com", "password": "supersecret123"}}
    )


class TokenResponse(BaseModel):
    """Bearer token returned on a successful login."""

    access_token: str = Field(
        description="Signed JWT. Send it as `Authorization: Bearer <access_token>`.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(default="bearer", description="Token scheme (always `bearer`).", examples=["bearer"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )
