"""Import all models so SQLAlchemy registers them with the metadata."""
from app.models.ai_insight import AIInsight, InsightType, Severity
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense, PaymentMethod
from app.models.recurring import Frequency, RecurringExpense
from app.models.user import User

__all__ = [
    "User",
    "Category",
    "Expense",
    "PaymentMethod",
    "Budget",
    "RecurringExpense",
    "Frequency",
    "AIInsight",
    "InsightType",
    "Severity",
]
