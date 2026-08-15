"""Analytics endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    CategorySpend,
    ComparisonResponse,
    MonthlyAnalytics,
    TrendPoint,
)
from app.services.analytics_service import (
    category_analytics,
    monthly_analytics,
    monthly_comparison,
    monthly_trends,
)
from app.utils.date_utils import current_month
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/monthly", response_model=Envelope[MonthlyAnalytics])
def get_monthly_analytics(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Totals, averages, extremes, top category and MoM change for a month."""
    cy, cm = current_month()
    return ok(monthly_analytics(db, current_user, year or cy, month or cm))


@router.get("/categories", response_model=Envelope[list[CategorySpend]])
def get_category_analytics(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Category totals and percentage share for a month."""
    cy, cm = current_month()
    return ok(category_analytics(db, current_user, year or cy, month or cm))


@router.get("/trends", response_model=Envelope[list[TrendPoint]])
def get_trends(
    months: int = Query(6, ge=2, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Monthly totals with month-over-month changes over the last N months."""
    return ok(monthly_trends(db, current_user, months))


@router.get("/comparison", response_model=Envelope[ComparisonResponse])
def get_comparison(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare the selected month with the previous month, per category."""
    cy, cm = current_month()
    return ok(monthly_comparison(db, current_user, year or cy, month or cm))
