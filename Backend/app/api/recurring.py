"""Recurring expense endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.recurring import RecurringExpenseResponse, RecurringExpenseUpdate
from app.services.recurring_service import (
    delete_recurring,
    list_recurring,
    run_detection,
    update_recurring,
)
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/recurring", tags=["Recurring Expenses"])


@router.get("", response_model=Envelope[list[RecurringExpenseResponse]])
def get_recurring_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List detected recurring expenses for the current user."""
    return ok(list_recurring(db, current_user))


@router.post("/detect", response_model=Envelope[list[RecurringExpenseResponse]])
def detect_recurring(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run statistical recurring expense detection and upsert findings."""
    return ok(run_detection(db, current_user))


@router.patch("/{recurring_id}", response_model=Envelope[RecurringExpenseResponse])
def edit_recurring(
    recurring_id: int,
    payload: RecurringExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enable/disable a recurring expense."""
    return ok(update_recurring(db, current_user, recurring_id, payload.is_active))


@router.delete("/{recurring_id}")
def remove_recurring(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_recurring(db, current_user, recurring_id)
    return ok(None, "Recurring expense deleted successfully.")
