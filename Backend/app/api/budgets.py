"""Budget endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate, BudgetUsageResponse
from app.services.budget_service import (
    budget_usage,
    create_budget,
    delete_budget,
    get_budget,
    list_budgets,
    update_budget,
)
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def _serialize(budget, usage: Optional[dict] = None) -> dict:
    base = {
        "id": budget.id,
        "category_id": budget.category_id,
        "category_name": budget.category.name,
        "amount": budget.amount,
        "month": budget.month,
        "year": budget.year,
        "created_at": budget.created_at.isoformat(),
        "updated_at": budget.updated_at.isoformat(),
    }
    if usage is not None:
        base.update(usage)
    return base


@router.post("", response_model=Envelope[BudgetResponse], status_code=status.HTTP_201_CREATED)
def add_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a budget for a category in a specific month/year."""
    return ok(_serialize(create_budget(db, current_user, payload)))


@router.get("", response_model=Envelope[list[BudgetUsageResponse]])
def get_budgets(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List budgets with spent, remaining, usage percentage and status."""
    budgets = list_budgets(db, current_user, month, year)
    return ok([_serialize(b, budget_usage(db, current_user, b)) for b in budgets])


@router.put("/{budget_id}", response_model=Envelope[BudgetResponse])
def edit_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_serialize(update_budget(db, current_user, budget_id, payload)))


@router.delete("/{budget_id}")
def remove_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_budget(db, current_user, budget_id)
    return ok(None, "Budget deleted successfully.")
