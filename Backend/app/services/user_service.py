"""User profile business logic."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserUpdate


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.email is not None:
        new_email = payload.email.lower()
        conflict = db.scalar(select(User).where(User.email == new_email, User.id != user.id))
        if conflict is not None:
            raise AppError(
                "An account with this email already exists.",
                ErrorCode.AUTH_EMAIL_TAKEN,
                status_code=409,
            )
        user.email = new_email
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise AppError(
            "Current password is incorrect.",
            ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=400,
        )
    if payload.new_password == payload.current_password:
        raise AppError(
            "New password must be different from the current password.",
            ErrorCode.VALIDATION_ERROR,
            status_code=400,
        )
    user.password_hash = hash_password(payload.new_password)
    db.commit()
