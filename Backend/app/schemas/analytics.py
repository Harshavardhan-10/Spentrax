"""Analytics schemas."""
from typing import Optional

from pydantic import BaseModel


class CategorySpend(BaseModel):
    category_id: int
    category_name: str
    amount: float
    percentage: float


class TopExpense(BaseModel):
    id: int
    description: str
    merchant: Optional[str]
    amount: float
    expense_date: str
    category_name: str


class MonthlyAnalytics(BaseModel):
    month: int
    year: int
    total_expenses: float
    avg_daily_spending: float
    avg_monthly_spending: float
    highest_expense: Optional[TopExpense]
    lowest_expense: Optional[TopExpense]
    top_category: Optional[dict]
    category_breakdown: list[CategorySpend]
    month_over_month_change: Optional[float]
    month_over_month_delta: Optional[float]


class TrendPoint(BaseModel):
    month: int
    year: int
    label: str
    total: float
    change_percentage: Optional[float]


class ComparisonResponse(BaseModel):
    month: int
    year: int
    current_total: float
    previous_total: float
    difference: float
    change_percentage: Optional[float]
    categories: list[dict]
