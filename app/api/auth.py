"""Authentication endpoints: user registration and login."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import DbSession
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


def _issue_token(user: User) -> Token:
    return Token(
        access_token=create_access_token(subject=user.id),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={409: {"description": "Email address is already registered."}},
)
def register(payload: UserCreate, db: DbSession) -> Token:
    """Create an account and return a ready-to-use access token.

    The password is bcrypt-hashed before it touches the database and is never
    echoed back in the response.
    """
    existing_user = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _issue_token(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and obtain an access token",
    responses={401: {"description": "Incorrect email or password."}},
)
def login(payload: UserLogin, db: DbSession) -> Token:
    """Verify credentials and return a signed JWT access token.

    Failures deliberately return one generic message so the endpoint cannot be
    used to enumerate which email addresses are registered.
    """
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email))

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _issue_token(user)
