"""Shared API dependencies (README §11).

Provides the DB session, the authenticated user, and an optional-user variant
for endpoints (like /compare) that work for both signed-in sellers and
anonymous visitors (§9 actors).
"""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.repositories import UsersRepository

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _user_from_token(token: str, db: Session) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise _CREDENTIALS_EXC
    user = UsersRepository(db).get_by_id(user_id)
    if user is None:
        raise _CREDENTIALS_EXC
    return user


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid bearer token; 401 otherwise."""
    if credentials is None:
        raise _CREDENTIALS_EXC
    return _user_from_token(credentials.credentials, db)


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return the user if a token is present and valid; None if absent.

    A present-but-invalid token still 401s — we never silently downgrade a
    failed authentication to anonymous.
    """
    if credentials is None:
        return None
    return _user_from_token(credentials.credentials, db)
