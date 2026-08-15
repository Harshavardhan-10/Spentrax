"""Recurring expense business logic (list, detect, toggle, delete)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.models.recurring import RecurringExpense
from app.models.user import User
from app.services.expense_service import run_recurring_detection as _run_detection


def list_recurring(db: Session, user: User) -> list[RecurringExpense]:
    return list(
        db.scalars(
            select(RecurringExpense)
            .where(RecurringExpense.user_id == user.id)
            .order_by(RecurringExpense.confidence_score.desc())
        )
    )


def get_recurring(db: Session, user: User, recurring_id: int) -> RecurringExpense:
    record = db.scalar(
        select(RecurringExpense).where(
            RecurringExpense.id == recurring_id,
            RecurringExpense.user_id == user.id,
        )
    )
    if record is None:
        raise AppError(
            "Recurring expense not found.", ErrorCode.RECURRING_NOT_FOUND, status_code=404
        )
    return record


def run_detection(db: Session, user: User) -> list[RecurringExpense]:
    return _run_detection(db, user)


def update_recurring(
    db: Session, user: User, recurring_id: int, is_active: bool
) -> RecurringExpense:
    record = get_recurring(db, user, recurring_id)
    record.is_active = is_active
    db.commit()
    db.refresh(record)
    return record


def delete_recurring(db: Session, user: User, recurring_id: int) -> None:
    record = get_recurring(db, user, recurring_id)
    db.delete(record)
    db.commit()
