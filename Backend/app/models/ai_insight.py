"""AI insight model. Persisted insights shown on dashboard and insights page."""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class InsightType(str, Enum):
    SPENDING = "SPENDING"
    BUDGET = "BUDGET"
    ANOMALY = "ANOMALY"
    RECURRING = "RECURRING"
    SAVING = "SAVING"
    MONTHLY_SUMMARY = "MONTHLY_SUMMARY"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    IMPORTANT = "IMPORTANT"


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    insight_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default=Severity.INFO.value)
    insight_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped["User"] = relationship(back_populates="ai_insights")
