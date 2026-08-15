"""Analytics engine: monthly, category, trends and comparison analytics.

All aggregation is done in SQL over the authenticated user's expenses only.
"""
from calendar import monthrange
from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.utils.date_utils import month_bounds, previous_month


def _month_total(db: Session, user: User, year: int, month: int) -> float:
    start, end = month_bounds(year, month)
    return (
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.user_id == user.id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            )
        )
        or 0.0
    )


def _category_breakdown(db: Session, user: User, year: int, month: int) -> list[dict]:
    start, end = month_bounds(year, month)
    rows = db.execute(
        select(
            Category.id,
            Category.name,
            func.coalesce(func.sum(Expense.amount), 0.0),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user.id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        )
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    total = sum(row[2] for row in rows) or 0.0
    return [
        {
            "category_id": row[0],
            "category_name": row[1],
            "amount": round(float(row[2]), 2),
            "percentage": round((float(row[2]) / total * 100), 2) if total else 0.0,
        }
        for row in rows
    ]


def _extreme_expense(
    db: Session, user: User, year: int, month: int, order: str
) -> Optional[dict]:
    start, end = month_bounds(year, month)
    statement = (
        select(Expense, Category.name)
        .join(Category, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user.id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        )
        .order_by(Expense.amount.asc() if order == "asc" else Expense.amount.desc())
        .limit(1)
    )
    row = db.execute(statement).first()
    if row is None:
        return None
    expense, category_name = row
    return {
        "id": expense.id,
        "description": expense.description,
        "merchant": expense.merchant,
        "amount": expense.amount,
        "expense_date": expense.expense_date.isoformat(),
        "category_name": category_name,
    }


def monthly_analytics(db: Session, user: User, year: int, month: int) -> dict:
    total = _month_total(db, user, year, month)
    days = monthrange(year, month)[1]

    prev_year, prev_month = previous_month(year, month)
    previous_total = _month_total(db, user, prev_year, prev_month)

    breakdown = _category_breakdown(db, user, year, month)
    top_category = breakdown[0] if breakdown else None

    change = None
    delta = None
    if previous_total > 0:
        delta = round(total - previous_total, 2)
        change = round(delta / previous_total * 100, 2)
    elif total > 0:
        change = None

    return {
        "month": month,
        "year": year,
        "total_expenses": round(total, 2),
        "avg_daily_spending": round(total / days, 2) if days else 0.0,
        "avg_monthly_spending": round(_average_monthly(db, user, year, month), 2),
        "highest_expense": _extreme_expense(db, user, year, month, "desc"),
        "lowest_expense": _extreme_expense(db, user, year, month, "asc"),
        "top_category": top_category,
        "category_breakdown": breakdown,
        "month_over_month_change": change,
        "month_over_month_delta": delta,
    }


def _average_monthly(db: Session, user: User, year: int, month: int) -> float:
    """Average monthly spend over the last 3 completed months."""
    totals = []
    cy, cm = previous_month(year, month)
    for _ in range(3):
        totals.append(_month_total(db, user, cy, cm))
        cy, cm = previous_month(cy, cm)
    return sum(totals) / len(totals) if totals else 0.0


def monthly_trends(db: Session, user: User, months: int = 6) -> list[dict]:
    year, month = _today_month()
    points = []
    previous_total = None
    for _ in range(months):
        total = _month_total(db, user, year, month)
        change = None
        if previous_total is not None and previous_total > 0:
            change = round((total - previous_total) / previous_total * 100, 2)
        points.append(
            {
                "month": month,
                "year": year,
                "label": f"{month:02d}/{year}",
                "total": round(total, 2),
                "change_percentage": change,
            }
        )
        previous_total = total
        year, month = previous_month(year, month)
    points.reverse()
    return points


def category_analytics(db: Session, user: User, year: int, month: int) -> list[dict]:
    return _category_breakdown(db, user, year, month)


def monthly_comparison(db: Session, user: User, year: int, month: int) -> dict:
    prev_year, prev_month = previous_month(year, month)
    current = _month_total(db, user, year, month)
    previous = _month_total(db, user, prev_year, prev_month)

    current_by_category = {
        row["category_name"]: row["amount"] for row in _category_breakdown(db, user, year, month)
    }
    previous_by_category = {
        row["category_name"]: row["amount"]
        for row in _category_breakdown(db, user, prev_year, prev_month)
    }
    categories = []
    for name in sorted(set(current_by_category) | set(previous_by_category)):
        current_amount = current_by_category.get(name, 0.0)
        previous_amount = previous_by_category.get(name, 0.0)
        change = None
        if previous_amount > 0:
            change = round((current_amount - previous_amount) / previous_amount * 100, 2)
        categories.append(
            {
                "category": name,
                "current": round(current_amount, 2),
                "previous": round(previous_amount, 2),
                "change_percentage": change,
            }
        )

    return {
        "month": month,
        "year": year,
        "current_total": round(current, 2),
        "previous_total": round(previous, 2),
        "difference": round(current - previous, 2),
        "change_percentage": (
            round((current - previous) / previous * 100, 2) if previous > 0 else None
        ),
        "categories": categories,
    }


def _today_month() -> tuple[int, int]:
    today = date.today()
    return today.year, today.month
