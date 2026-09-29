"""Reusable FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Declaring the scheme here makes FastAPI's interactive docs render an
# "Authorize" button that stores the bearer token for every protected call.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

CREDENTIALS_EXCEPTION_HEADERS = {"WWW-Authenticate": "Bearer"}


def _credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers=CREDENTIALS_EXCEPTION_HEADERS,
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from the ``Authorization: Bearer`` header.

    Decodes and verifies the JWT, then confirms the referenced user still
    exists in the database so that a deleted account cannot keep using an
    unexpired token.

    Raises:
        HTTPException: 401 if the header is missing/invalid, the token is
            expired or tampered with, or the user no longer exists.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise _credentials_exception("Could not validate credentials.") from None

    subject = payload.get("sub")
    if subject is None:
        raise _credentials_exception("Could not validate credentials.")

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _credentials_exception("Could not validate credentials.") from None

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _credentials_exception("User no longer exists.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
