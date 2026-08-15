"""Expense schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.expense import PaymentMethod


class ExpenseBase(BaseModel):
    amount: float = Field(gt=0, le=100_000_000)
    description: str = Field(min_length=1, max_length=255)
    merchant: Optional[str] = Field(default=None, max_length=255)
    category_id: int
    payment_method: PaymentMethod = PaymentMethod.OTHER
    expense_date: date
    notes: Optional[str] = Field(default=None, max_length=2000)
    is_recurring: bool = False


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0, le=100_000_000)
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    merchant: Optional[str] = Field(default=None, max_length=255)
    category_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    expense_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    is_recurring: Optional[bool] = None


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    category_name: str
    amount: float
    description: str
    merchant: Optional[str]
    payment_method: str
    expense_date: date
    notes: Optional[str]
    is_recurring: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    limit: int
    pages: int
