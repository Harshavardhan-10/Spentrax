"""Budget schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category_id: int
    amount: float = Field(gt=0, le=100_000_000)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2200)


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = Field(default=None, gt=0, le=100_000_000)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    year: Optional[int] = Field(default=None, ge=2000, le=2200)


class BudgetResponse(BaseModel):
    id: int
    category_id: int
    category_name: str
    amount: float
    month: int
    year: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetUsageResponse(BudgetResponse):
    spent: float
    remaining: float
    used_percentage: float
    status: str
