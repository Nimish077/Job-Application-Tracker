"""Pydantic schemas for user registration, login and responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES

MIN_PASSWORD_LENGTH = 8


class UserBase(BaseModel):
    """Fields shared by every user representation."""

    email: EmailStr = Field(
        ...,
        max_length=320,
        description="Unique email address used to sign in.",
        examples=["user@example.com"],
    )

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        """Lowercase and strip so `A@B.com` and `a@b.com` are one account."""
        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserCreate(UserBase):
    """Registration payload."""

    password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=BCRYPT_MAX_BYTES,
        description="Plaintext password; stored only as a bcrypt hash.",
        examples=["Sup3rSecret!"],
        repr=False,
    )


class UserLogin(BaseModel):
    """Login payload."""

    email: EmailStr = Field(..., description="Registered email address.")
    password: str = Field(..., description="Account password.", repr=False)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserResponse(BaseModel):
    """Public representation of a user. Never exposes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    """Bearer token returned by `/auth/register` and `/auth/login`."""

    access_token: str = Field(..., description="Signed JWT access token.")
    token_type: str = Field(default="bearer", description="Authorization scheme.")
    expires_in: int = Field(
        ...,
        description="Access token lifetime in seconds.",
        examples=[1800],
    )
