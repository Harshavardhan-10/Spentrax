from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.analytics import router as analytics_router
from app.api.budgets import router as budgets_router
from app.api.categories import router as categories_router
from app.api.csv import router as csv_router
from app.api.dashboard import router as dashboard_router
from app.api.expenses import router as expenses_router
from app.api.recurring import router as recurring_router
from app.api.users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
    "categories_router",
    "expenses_router",
    "budgets_router",
    "recurring_router",
    "analytics_router",
    "dashboard_router",
    "csv_router",
    "ai_router",
]
