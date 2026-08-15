"""Recurring expense schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RecurringExpenseResponse(BaseModel):
    id: int
    expense_id: Optional[int]
    name: str
    amount: float
    frequency: str
    next_due_date: Optional[date]
    confidence_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecurringExpenseUpdate(BaseModel):
    is_active: Optional[bool] = None
