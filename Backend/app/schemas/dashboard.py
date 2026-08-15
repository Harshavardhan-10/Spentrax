"""Dashboard schemas."""
from typing import Any, Optional

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_expenses: float
    monthly_expenses: float
    budget: float
    budget_used_percentage: float
    remaining_budget: float
    top_category: Optional[dict]
    recent_expenses: list[dict]
    category_breakdown: list[dict]
    monthly_trend: list[dict]
    ai_insights: list[dict]
    recurring_expenses: list[dict]
    month: int
    year: int
