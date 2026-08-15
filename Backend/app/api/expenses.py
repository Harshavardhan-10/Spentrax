"""Expense endpoints: full CRUD with filters, search, sorting and pagination."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.services.expense_service import (
    create_expense,
    delete_expense,
    get_expense,
    list_expenses,
    update_expense,
)
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _serialize(expense) -> dict:
    return {
        "id": expense.id,
        "user_id": expense.user_id,
        "category_id": expense.category_id,
        "category_name": expense.category.name,
        "amount": expense.amount,
        "description": expense.description,
        "merchant": expense.merchant,
        "payment_method": expense.payment_method,
        "expense_date": expense.expense_date.isoformat(),
        "notes": expense.notes,
        "is_recurring": expense.is_recurring,
        "created_at": expense.created_at.isoformat(),
        "updated_at": expense.updated_at.isoformat(),
    }


@router.post("", response_model=Envelope[ExpenseResponse], status_code=status.HTTP_201_CREATED)
def add_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an expense. Runs recurring and anomaly checks automatically."""
    return ok(_serialize(create_expense(db, current_user, payload)))


@router.get("", response_model=Envelope[ExpenseListResponse])
def get_expenses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[int] = Query(None, description="Filter by category id"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    payment_method: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None, description="Search description/merchant"),
    sort_by: str = Query("date", pattern="^(date|amount|description|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = list_expenses(
        db,
        current_user,
        page=page,
        limit=limit,
        category_id=category,
        start_date=start_date,
        end_date=end_date,
        payment_method=payment_method,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ok(
        {
            "items": [_serialize(e) for e in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }
    )


@router.get("/{expense_id}", response_model=Envelope[ExpenseResponse])
def get_single_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_serialize(get_expense(db, current_user, expense_id)))


@router.put("/{expense_id}", response_model=Envelope[ExpenseResponse])
def edit_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_serialize(update_expense(db, current_user, expense_id, payload)))


@router.delete("/{expense_id}")
def remove_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_expense(db, current_user, expense_id)
    return ok(None, "Expense deleted successfully.")
