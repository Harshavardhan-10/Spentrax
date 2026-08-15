"""Dashboard aggregation service."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_insight import AIInsight
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.recurring import RecurringExpense
from app.models.user import User
from app.services.analytics_service import _category_breakdown, monthly_trends
from app.utils.date_utils import current_month, month_bounds


def get_dashboard(db: Session, user: User) -> dict:
    year, month = current_month()
    start, end = month_bounds(year, month)

    total_expenses = (
        db.scalar(select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.user_id == user.id))
        or 0.0
    )

    monthly_expenses = (
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.user_id == user.id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            )
        )
        or 0.0
    )

    budgets = list(
        db.scalars(
            select(Budget).where(Budget.user_id == user.id, Budget.month == month, Budget.year == year)
        )
    )
    budget_total = sum(b.amount for b in budgets) or 0.0
    spent_budgeted = sum(
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.user_id == user.id,
                Expense.category_id == b.category_id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            )
        )
        or 0.0
        for b in budgets
    )
    budget_used_percentage = round(spent_budgeted / budget_total * 100, 2) if budget_total > 0 else 0.0
    remaining_budget = round(budget_total - spent_budgeted, 2)

    breakdown = _category_breakdown(db, user, year, month)
    top_category = breakdown[0] if breakdown else None

    recent_expenses = list(
        db.scalars(
            select(Expense)
            .where(Expense.user_id == user.id)
            .order_by(Expense.expense_date.desc(), Expense.id.desc())
            .limit(5)
        )
    )

    insights = list(
        db.scalars(
            select(AIInsight)
            .where(AIInsight.user_id == user.id)
            .order_by(AIInsight.created_at.desc())
            .limit(5)
        )
    )

    recurring = list(
        db.scalars(
            select(RecurringExpense)
            .where(RecurringExpense.user_id == user.id, RecurringExpense.is_active.is_(True))
            .order_by(RecurringExpense.confidence_score.desc())
            .limit(5)
        )
    )

    return {
        "total_expenses": round(float(total_expenses), 2),
        "monthly_expenses": round(float(monthly_expenses), 2),
        "budget": round(budget_total, 2),
        "budget_used_percentage": budget_used_percentage,
        "remaining_budget": remaining_budget,
        "top_category": top_category,
        "recent_expenses": [
            {
                "id": e.id,
                "description": e.description,
                "merchant": e.merchant,
                "amount": e.amount,
                "expense_date": e.expense_date.isoformat(),
                "category_name": e.category.name,
            }
            for e in recent_expenses
        ],
        "category_breakdown": breakdown,
        "monthly_trend": monthly_trends(db, user, 6),
        "ai_insights": [
            {
                "id": i.id,
                "insight_type": i.insight_type,
                "title": i.title,
                "content": i.content,
                "severity": i.severity,
                "created_at": i.created_at.isoformat(),
            }
            for i in insights
        ],
        "recurring_expenses": [
            {
                "id": r.id,
                "name": r.name,
                "amount": r.amount,
                "frequency": r.frequency,
                "next_due_date": r.next_due_date.isoformat() if r.next_due_date else None,
                "confidence_score": r.confidence_score,
            }
            for r in recurring
        ],
        "month": month,
        "year": year,
    }
