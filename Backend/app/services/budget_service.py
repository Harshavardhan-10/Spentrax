"""Budget business logic with utilization calculation.

Budget states: <70% healthy, 70-90% warning, >90% critical, >100% exceeded.
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.services.category_service import get_category_for_user
from app.utils.date_utils import month_bounds


def _check_duplicate(
    db: Session, user: User, category_id: int, month: int, year: int, exclude_id: Optional[int] = None
) -> None:
    statement = select(Budget.id).where(
        Budget.user_id == user.id,
        Budget.category_id == category_id,
        Budget.month == month,
        Budget.year == year,
    )
    if exclude_id is not None:
        statement = statement.where(Budget.id != exclude_id)
    if db.scalar(statement) is not None:
        raise AppError(
            "A budget for this category already exists for the selected month.",
            ErrorCode.BUDGET_ALREADY_EXISTS,
            status_code=409,
        )


def create_budget(db: Session, user: User, payload: BudgetCreate) -> Budget:
    get_category_for_user(db, payload.category_id, user)
    _check_duplicate(db, user, payload.category_id, payload.month, payload.year)

    budget = Budget(
        user_id=user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        month=payload.month,
        year=payload.year,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_budget(db: Session, user: User, budget_id: int) -> Budget:
    budget = db.scalar(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id)
    )
    if budget is None:
        raise AppError("Budget not found.", ErrorCode.BUDGET_NOT_FOUND, status_code=404)
    return budget


def update_budget(db: Session, user: User, budget_id: int, payload: BudgetUpdate) -> Budget:
    budget = get_budget(db, user, budget_id)
    data = payload.model_dump(exclude_unset=True)

    if "category_id" in data and data["category_id"] is not None:
        get_category_for_user(db, data["category_id"], user)
    if "month" in data or "year" in data:
        category_id = data.get("category_id", budget.category_id)
        month = data.get("month", budget.month)
        year = data.get("year", budget.year)
        _check_duplicate(db, user, category_id, month, year, exclude_id=budget.id)

    for field, value in data.items():
        setattr(budget, field, value)

    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, user: User, budget_id: int) -> None:
    budget = get_budget(db, user, budget_id)
    db.delete(budget)
    db.commit()


def spent_for_budget(db: Session, user: User, budget: Budget) -> float:
    start, end = month_bounds(budget.year, budget.month)
    return (
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.user_id == user.id,
                Expense.category_id == budget.category_id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            )
        )
        or 0.0
    )


def budget_usage(db: Session, user: User, budget: Budget) -> dict:
    spent = round(float(spent_for_budget(db, user, budget)), 2)
    used_percentage = round(spent / budget.amount * 100, 2) if budget.amount > 0 else 0.0
    remaining = round(budget.amount - spent, 2)

    if used_percentage > 100:
        status = "EXCEEDED"
    elif used_percentage > 90:
        status = "CRITICAL"
    elif used_percentage >= 70:
        status = "WARNING"
    else:
        status = "HEALTHY"

    return {
        "spent": spent,
        "remaining": remaining,
        "used_percentage": used_percentage,
        "status": status,
    }


def list_budgets(db: Session, user: User, month: Optional[int], year: Optional[int]) -> list[Budget]:
    statement = select(Budget).where(Budget.user_id == user.id)
    if month is not None:
        statement = statement.where(Budget.month == month)
    if year is not None:
        statement = statement.where(Budget.year == year)
    return list(db.scalars(statement.order_by(Budget.year.desc(), Budget.month.desc())))
