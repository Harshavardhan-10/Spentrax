"""AI endpoints: categorization, insights, summary, recommendations.

Routes delegate to the service layer, which delegates to AIService, which
talks to a provider (or falls back to deterministic logic).
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.ai_insight import AIInsight
from app.models.user import User
from app.schemas.ai import (
    BudgetRecommendation,
    CategorizeRequest,
    CategorizeResponse,
    InsightItem,
    MonthlySummaryResponse,
)
from app.services.ai.ai_service import get_ai_service, save_insight
from app.services.ai.insights import prepare_aggregated_data
from app.services.category_service import list_categories
from app.utils.date_utils import current_month
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/categorize", response_model=Envelope[CategorizeResponse])
def categorize_expense(
    payload: CategorizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Suggest a category for a transaction. The user always has the final say."""
    categories = [c.name for c in list_categories(db, current_user)]
    result = get_ai_service().suggest_category(payload.description, payload.merchant, categories)
    return ok(
        CategorizeResponse(
            category=result["category"],
            confidence=result.get("confidence", 0.5),
            reason=result.get("reason", ""),
        )
    )


@router.get("/insights", response_model=Envelope[list[InsightItem]])
def get_insights(
    refresh: bool = Query(False, description="Regenerate and persist fresh insights"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the user's insights. With refresh=true, new insights are generated."""
    if refresh:
        year, month = current_month()
        aggregated = prepare_aggregated_data(db, current_user, year, month)
        generated = get_ai_service().generate_insights(aggregated)
        stale = db.scalars(
            select(AIInsight).where(
                AIInsight.user_id == current_user.id,
                AIInsight.insight_type.in_(["SPENDING", "BUDGET", "SAVING", "RECURRING"]),
            )
        )
        for insight in stale:
            db.delete(insight)
        db.commit()
        for item in generated:
            save_insight(
                db,
                current_user,
                insight_type=item.get("type", "SPENDING"),
                title=item.get("title", "Insight"),
                content=item.get("content", ""),
                severity=item.get("severity", "INFO"),
            )

    insights = list(
        db.scalars(
            select(AIInsight)
            .where(AIInsight.user_id == current_user.id)
            .order_by(AIInsight.created_at.desc())
            .limit(50)
        )
    )
    return ok(
        [
            InsightItem(
                id=i.id,
                insight_type=i.insight_type,
                title=i.title,
                content=i.content,
                severity=i.severity,
                metadata=i.insight_metadata,
                created_at=i.created_at,
            )
            for i in insights
        ]
    )


@router.get("/summary", response_model=Envelope[MonthlySummaryResponse])
def get_monthly_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate (and persist) a monthly financial summary."""
    cy, cm = current_month()
    year, month = year or cy, month or cm

    aggregated = prepare_aggregated_data(db, current_user, year, month)
    summary_text = get_ai_service().generate_monthly_summary(aggregated)

    for insight in db.scalars(
        select(AIInsight).where(
            AIInsight.user_id == current_user.id,
            AIInsight.insight_type == "MONTHLY_SUMMARY",
        )
    ):
        meta = insight.insight_metadata or {}
        if meta.get("month") == month and meta.get("year") == year:
            db.delete(insight)
    db.commit()

    insight = save_insight(
        db,
        current_user,
        insight_type="MONTHLY_SUMMARY",
        title=f"Monthly summary — {month:02d}/{year}",
        content=summary_text,
        severity="INFO",
        metadata={"month": month, "year": year},
    )
    return ok(
        MonthlySummaryResponse(
            summary=summary_text,
            month=month,
            year=year,
            insight=InsightItem(
                id=insight.id,
                insight_type=insight.insight_type,
                title=insight.title,
                content=insight.content,
                severity=insight.severity,
                metadata=insight.insight_metadata,
                created_at=insight.created_at,
            ),
        )
    )


@router.get("/recommendations", response_model=Envelope[list[BudgetRecommendation]])
def get_budget_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Suggested budgets based on 3-month averages. Not applied automatically."""
    year, month = current_month()
    aggregated = prepare_aggregated_data(db, current_user, year, month)
    recommendations = get_ai_service().generate_budget_recommendations(aggregated)
    category_ids = {c.name: c.id for c in list_categories(db, current_user)}
    return ok(
        [
            BudgetRecommendation(
                category=r.get("category", ""),
                category_id=category_ids.get(r.get("category", "")),
                recommended_budget=r.get("recommended_budget", 0),
                reason=r.get("reason", ""),
            )
            for r in recommendations
            if r.get("category") and r.get("recommended_budget")
        ]
    )


@router.get("/anomalies", response_model=Envelope[list[InsightItem]])
def get_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return stored spending anomaly insights."""
    anomalies = list(
        db.scalars(
            select(AIInsight)
            .where(AIInsight.user_id == current_user.id, AIInsight.insight_type == "ANOMALY")
            .order_by(AIInsight.created_at.desc())
            .limit(20)
        )
    )
    return ok(
        [
            InsightItem(
                id=i.id,
                insight_type=i.insight_type,
                title=i.title,
                content=i.content,
                severity=i.severity,
                metadata=i.insight_metadata,
                created_at=i.created_at,
            )
            for i in anomalies
        ]
    )
