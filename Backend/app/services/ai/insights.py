"""Rule-based financial insights and monthly summary fallback.

These functions generate deterministic insights from aggregated data when no
external AI provider is available (or as fallback when the provider fails).
"""
from statistics import fmean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.recurring import RecurringExpense
from app.models.user import User
from app.utils.date_utils import month_bounds, previous_month

SEVERITY = {"INFO": "INFO", "WARNING": "WARNING", "IMPORTANT": "IMPORTANT"}


def _month_category_totals(db: Session, user: User, year: int, month: int) -> dict[str, float]:
    start, end = month_bounds(year, month)
    rows = db.execute(
        select(Category.name, func.coalesce(func.sum(Expense.amount), 0.0))
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user.id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        )
        .group_by(Category.name)
    ).all()
    return {name: round(float(total), 2) for name, total in rows}


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


def prepare_aggregated_data(
    db: Session, user: User, year: int, month: int
) -> dict[str, Any]:
    """Prepare structured financial data for the AI layer.

    Only aggregated, user-scoped data leaves this function — never raw rows.
    """
    prev_year, prev_month = previous_month(year, month)

    categories = _month_category_totals(db, user, year, month)
    monthly_expenses = round(sum(categories.values()), 2)
    previous_month_expenses = _month_total(db, user, prev_year, prev_month)

    averages: dict[str, float] = {}
    for name in set(categories) or set(_month_category_totals(db, user, prev_year, prev_month)):
        totals = []
        cy, cm = year, month
        for _ in range(3):
            totals.append(_month_category_totals(db, user, cy, cm).get(name, 0.0))
            cy, cm = previous_month(cy, cm)
        if totals:
            averages[name] = round(fmean(totals), 2)

    budgets_snapshot: dict[str, dict[str, float]] = {}
    budgets = list(
        db.scalars(
            select(Budget).where(Budget.user_id == user.id, Budget.month == month, Budget.year == year)
        )
    )
    for budget in budgets:
        category_name = budget.category.name
        spent = _month_category_totals(db, user, year, month).get(category_name, 0.0)
        budgets_snapshot[category_name] = {
            "budget_amount": budget.amount,
            "spent": spent,
            "used_percentage": round(spent / budget.amount * 100, 2) if budget.amount else 0.0,
        }

    recurring = list(
        db.scalars(
            select(RecurringExpense).where(
                RecurringExpense.user_id == user.id, RecurringExpense.is_active.is_(True)
            )
        )
    )

    return {
        "month": month,
        "year": year,
        "monthly_expenses": monthly_expenses,
        "previous_month_expenses": round(previous_month_expenses, 2),
        "categories": categories,
        "category_averages": averages,
        "budgets": budgets_snapshot,
        "recurring_expenses": [
            {
                "name": r.name,
                "amount": r.amount,
                "frequency": r.frequency,
                "confidence": r.confidence_score,
            }
            for r in recurring
        ],
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fallback_insights(aggregated: dict) -> list[dict]:
    insights: list[dict] = []
    total = _safe_float(aggregated.get("monthly_expenses"))
    previous = _safe_float(aggregated.get("previous_month_expenses"))
    categories: dict = aggregated.get("categories") or {}

    if total <= 0:
        return insights

    if previous > 0:
        change = (total - previous) / previous * 100
        if change > 15:
            insights.append({
                "title": "Spending increased",
                "content": (
                    f"Your spending is {change:.1f}% higher than last month. "
                    "Review your largest categories for savings opportunities."
                ),
                "severity": "WARNING",
                "type": "SPENDING",
            })
        elif change < -10:
            insights.append({
                "title": "Spending decreased",
                "content": f"Great job — spending dropped {abs(change):.1f}% compared to last month.",
                "severity": "INFO",
                "type": "SPENDING",
            })

    if categories:
        top_category = max(categories, key=lambda k: _safe_float(categories[k]))
        top_amount = _safe_float(categories[top_category])
        share = (top_amount / total * 100) if total else 0
        if share >= 30:
            insights.append({
                "title": f"High concentration in {top_category}",
                "content": (
                    f"{top_category} accounts for {share:.0f}% of this month's "
                    f"spending (₹{top_amount:,.2f}). Consider setting a budget for it."
                ),
                "severity": "WARNING" if share >= 40 else "INFO",
                "type": "BUDGET",
            })

    budget_snapshot = aggregated.get("budgets") or {}
    for category, info in budget_snapshot.items():
        if not isinstance(info, dict):
            continue
        used = _safe_float(info.get("used_percentage"))
        if used > 90:
            insights.append({
                "title": f"{category} budget nearly exhausted",
                "content": f"You have used {used:.0f}% of your {category} budget this month.",
                "severity": "IMPORTANT",
                "type": "BUDGET",
            })

    if total > 0 and categories:
        insights.append({
            "title": "Average daily spend",
            "content": (
                f"You spend about ₹{total / 30:,.0f} per day on average. "
                "Small daily expenses add up quickly."
            ),
            "severity": "INFO",
            "type": "SPENDING",
        })

    return insights[:5]


def fallback_monthly_summary(aggregated: dict) -> str:
    total = _safe_float(aggregated.get("monthly_expenses"))
    previous = _safe_float(aggregated.get("previous_month_expenses"))
    categories: dict = aggregated.get("categories") or {}

    if total <= 0:
        return "No spending was recorded this month."

    parts = [f"You spent ₹{total:,.2f} this month."]
    if previous > 0:
        change = (total - previous) / previous * 100
        parts.append(
            f"That is {change:.1f}% {'higher' if change > 0 else 'lower'} than last month."
        )
    if categories:
        top = max(categories, key=lambda k: _safe_float(categories[k]))
        parts.append(f"{top} was your largest category at ₹{_safe_float(categories[top]):,.2f}.")
    return " ".join(parts)
