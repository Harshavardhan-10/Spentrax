"""Authentication business logic: registration, login, session creation."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.core.security import create_access_token, hash_password, verify_password
from app.core.logging import log_service_event
from app.models.user import User
from app.schemas.auth import AuthResponse, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = payload.email.lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise AppError(
            "An account with this email already exists.",
            ErrorCode.AUTH_EMAIL_TAKEN,
            status_code=409,
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_service_event("auth", "user_registered", user_id=user.id)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise AppError(
            "Invalid email or password.",
            ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=401,
        )
    if not user.is_active:
        raise AppError(
            "This account has been deactivated.",
            ErrorCode.AUTH_INACTIVE_ACCOUNT,
            status_code=403,
        )
    return user


def build_auth_response(user: User) -> AuthResponse:
    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user=user)
