"""AI endpoint schemas."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CategorizeRequest(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    merchant: Optional[str] = Field(default=None, max_length=255)


class CategorizeResponse(BaseModel):
    category: str
    confidence: float
    reason: str


class BudgetRecommendation(BaseModel):
    category: str
    category_id: Optional[int] = None
    recommended_budget: float
    reason: str


class InsightItem(BaseModel):
    id: int
    insight_type: str
    title: str
    content: str
    severity: str
    metadata: Optional[dict[str, Any]]
    created_at: datetime


class MonthlySummaryResponse(BaseModel):
    summary: str
    month: int
    year: int
    insight: InsightItem
