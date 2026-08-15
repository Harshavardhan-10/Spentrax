"""Expense business logic: CRUD, filtering, pagination and post-save checks.

Post-save checks run automatically after every expense is created:
  1. Recurring expense detection (statistical, in ml/recurring_detector).
  2. Anomaly detection (statistical, in ml/anomaly_detector) -> AI insight.

All queries are scoped to the authenticated user; ownership is always derived
from the JWT, never from client-supplied ids.
"""
import math
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.ml.anomaly_detector import detect_category_anomaly
from app.ml.recurring_detector import detect_recurring_candidates
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.ai.ai_service import save_insight
from app.services.category_service import get_category_for_user
from app.utils.date_utils import month_bounds

RECURRING_MIN_CONFIDENCE = 0.80
MAX_HISTORY_DAYS = 730


def _category_check(db: Session, user: User, category_id: int):
    get_category_for_user(db, category_id, user)


def create_expense(db: Session, user: User, payload: ExpenseCreate) -> Expense:
    _category_check(db, user, payload.category_id)

    expense = Expense(
        user_id=user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description.strip(),
        merchant=payload.merchant.strip() if payload.merchant else None,
        payment_method=payload.payment_method.value,
        expense_date=payload.expense_date,
        notes=payload.notes,
        is_recurring=payload.is_recurring,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    _post_create_checks(db, user, expense)
    return expense


def _post_create_checks(db: Session, user: User, expense: Expense) -> None:
    run_recurring_detection(db, user)

    historical = list(
        db.scalars(
            select(Expense.amount)
            .where(
                Expense.user_id == user.id,
                Expense.category_id == expense.category_id,
                Expense.expense_date < expense.expense_date,
            )
            .order_by(Expense.expense_date)
        )
    )
    anomaly = detect_category_anomaly(historical, expense.amount)
    if anomaly is not None:
        category = expense.category.name
        explanation = (
            f"An expense of ₹{expense.amount:,.2f} in {category} is "
            f"{anomaly.z_score:.1f} standard deviations above your typical "
            f"average of ₹{anomaly.mean:,.2f} in this category. Verify this "
            "transaction is correct."
        )
        save_insight(
            db,
            user,
            insight_type="ANOMALY",
            title=f"Unusual spending in {category}",
            content=explanation,
            severity="WARNING",
            metadata={
                "amount": expense.amount,
                "category": category,
                "z_score": anomaly.z_score,
                "mean": anomaly.mean,
                "expense_id": expense.id,
            },
        )


def get_expense(db: Session, user: User, expense_id: int) -> Expense:
    expense = db.scalar(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    if expense is None:
        raise AppError("Expense not found.", ErrorCode.EXPENSE_NOT_FOUND, status_code=404)
    return expense


def list_expenses(
    db: Session,
    user: User,
    *,
    page: int = 1,
    limit: int = 20,
    category_id: Optional[int] = None,
    start_date=None,
    end_date=None,
    payment_method: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = "date",
    sort_order: str = "asc",
) -> dict:
    page = max(1, page)
    limit = min(max(1, limit), 100)

    filters = [Expense.user_id == user.id]
    if category_id is not None:
        filters.append(Expense.category_id == category_id)
    if start_date is not None:
        filters.append(Expense.expense_date >= start_date)
    if end_date is not None:
        filters.append(Expense.expense_date <= end_date)
    if payment_method is not None:
        filters.append(Expense.payment_method == payment_method)
    if min_amount is not None:
        filters.append(Expense.amount >= min_amount)
    if max_amount is not None:
        filters.append(Expense.amount <= max_amount)
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            Expense.description.ilike(pattern) | Expense.merchant.ilike(pattern)
        )

    total = db.scalar(select(func.count(Expense.id)).where(*filters)) or 0

    sort_column = {
        "date": Expense.expense_date,
        "amount": Expense.amount,
        "description": Expense.description,
        "created_at": Expense.created_at,
    }.get(sort_by, Expense.expense_date)
    order = sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc()

    items = list(
        db.scalars(
            select(Expense)
            .where(*filters)
            .order_by(order, Expense.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if total else 0,
    }


def update_expense(
    db: Session, user: User, expense_id: int, payload: ExpenseUpdate
) -> Expense:
    expense = get_expense(db, user, expense_id)
    data = payload.model_dump(exclude_unset=True)

    if "category_id" in data and data["category_id"] is not None:
        _category_check(db, user, data["category_id"])
    if "payment_method" in data and data["payment_method"] is not None:
        data["payment_method"] = data["payment_method"].value
    if "merchant" in data and data["merchant"] is not None:
        data["merchant"] = data["merchant"].strip() or None
    if "description" in data and data["description"] is not None:
        data["description"] = data["description"].strip()

    for field, value in data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, user: User, expense_id: int) -> None:
    expense = get_expense(db, user, expense_id)
    db.delete(expense)
    db.commit()


def run_recurring_detection(db: Session, user: User) -> list:
    """Detect recurring expenses from the user's transaction history.

    Returns the list of RecurringExpense records created or updated.
    """
    from app.models.recurring import RecurringExpense

    expenses = list(
        db.scalars(
            select(Expense)
            .where(Expense.user_id == user.id)
            .order_by(Expense.expense_date)
        )
    )
    candidates = detect_recurring_candidates(expenses)

    updated: list[RecurringExpense] = []
    for candidate in candidates:
        if candidate.confidence < RECURRING_MIN_CONFIDENCE:
            continue

        existing = db.scalar(
            select(RecurringExpense).where(
                RecurringExpense.user_id == user.id,
                RecurringExpense.name == candidate.name,
                RecurringExpense.frequency == candidate.frequency,
            )
        )
        if existing is not None:
            existing.amount = candidate.amount
            existing.next_due_date = candidate.next_due_date
            existing.confidence_score = candidate.confidence
            updated.append(existing)
        else:
            record = RecurringExpense(
                user_id=user.id,
                expense_id=candidate.expense_ids[-1],
                name=candidate.name,
                amount=candidate.amount,
                frequency=candidate.frequency,
                next_due_date=candidate.next_due_date,
                confidence_score=candidate.confidence,
                is_active=True,
            )
            db.add(record)
            updated.append(record)

    if updated:
        db.commit()
        for record in updated:
            db.refresh(record)
    return updated
