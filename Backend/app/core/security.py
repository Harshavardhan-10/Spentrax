"""Security primitives: bcrypt password hashing and JWT tokens.

Passwords are hashed with bcrypt and never stored or logged in plain text.
JWT tokens contain sub (user id), email and an expiration time.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import AppError, ErrorCode

settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AppError(
            "Session expired. Please log in again.",
            ErrorCode.AUTH_TOKEN_EXPIRED,
            status_code=401,
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError(
            "Invalid authentication token.",
            ErrorCode.AUTH_TOKEN_INVALID,
            status_code=401,
        ) from exc
    return payload
