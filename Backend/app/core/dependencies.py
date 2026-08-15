"""FastAPI dependencies: database session and the authenticated user.

The authenticated user is always derived from the JWT token. user_id values
supplied by the client are never trusted for protected operations.
"""
from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError, ErrorCode
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(
            "Authentication required.",
            ErrorCode.AUTH_NOT_AUTHENTICATED,
            status_code=401,
        )

    payload = decode_access_token(credentials.credentials)
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError) as exc:
        raise AppError(
            "Invalid authentication token.",
            ErrorCode.AUTH_TOKEN_INVALID,
            status_code=401,
        ) from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(
            "User account is no longer active.",
            ErrorCode.AUTH_INACTIVE_ACCOUNT,
            status_code=401,
        )
    return user
