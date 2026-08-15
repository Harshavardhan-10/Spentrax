"""AI provider abstraction and the central AIService.

Routes never call an AI SDK directly. They go through:

    API Route -> Service -> AIService -> Provider

The provider is selected from configuration (AI_PROVIDER). If a remote
provider is configured but unavailable or fails, every capability falls back
to deterministic rule-based logic so the application keeps working.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx

from app.core.config import get_settings
from app.core.exceptions import AppError, ErrorCode
from app.core.logging import log_service_event
from app.models.ai_insight import AIInsight
from app.models.user import User
from app.services.ai import prompts

logger = logging.getLogger("app.services.ai")

settings = get_settings()


class AIProvider(ABC):
    """Interface every AI provider must implement."""

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def generate_json(self, system: str, user: str) -> dict: ...


class OpenAICompatProvider(AIProvider):
    """Speaks the OpenAI chat-completions protocol over HTTP.

    Works with OpenAI and any compatible endpoint (Azure, local LLMs, etc.).
    """

    def __init__(self) -> None:
        self._api_key = settings.AI_API_KEY
        self._model = settings.AI_MODEL or "gpt-4o-mini"
        self._base_url = settings.AI_BASE_URL.rstrip("/")
        self._timeout = settings.AI_TIMEOUT_SECONDS

    def is_available(self) -> bool:
        return bool(self._api_key)

    def generate_json(self, system: str, user: str) -> dict:
        if not self.is_available():
            raise AppError(
                "AI provider is not configured.",
                ErrorCode.AI_UNAVAILABLE,
                status_code=503,
            )

        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800,
                    "response_format": {"type": "json_object"},
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            log_service_event("ai", "provider_response", model=self._model)
            return json.loads(content)
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.warning("AI provider request failed: %s", exc)
            raise AppError(
                "The AI provider could not complete the request.",
                ErrorCode.AI_UNAVAILABLE,
                status_code=503,
            ) from exc


class RuleBasedProvider(AIProvider):
    """Deterministic fallback that never requires network access."""

    def is_available(self) -> bool:
        return True

    def generate_json(self, system: str, user: str) -> dict:
        return {}


class AIService:
    """Facade exposing AI capabilities with automatic fallback."""

    def __init__(self, provider: Optional[AIProvider] = None) -> None:
        self.provider = provider or self._build_provider()

    def _build_provider(self) -> AIProvider:
        if settings.AI_PROVIDER.lower() == "openai":
            provider = OpenAICompatProvider()
            if provider.is_available():
                return provider
            logger.info("AI_PROVIDER=openai but no API key set; using rule-based fallback.")
        return RuleBasedProvider()

    # ---- categorization -------------------------------------------------
    def suggest_category(self, description: str, merchant: Optional[str], categories: list[str]) -> dict:
        from app.services.ai.categorization import fallback_categorize

        if self.provider.is_available():
            try:
                result = self.provider.generate_json(
                    prompts.CATEGORIZE_SYSTEM,
                    prompts.categorize_prompt(description, merchant, categories),
                )
                if self._valid_category_result(result, categories):
                    return result
            except AppError:
                pass
        return fallback_categorize(description, merchant, categories)

    # ---- insights -------------------------------------------------------
    def generate_insights(self, aggregated: dict) -> list[dict]:
        from app.services.ai.insights import fallback_insights

        if self.provider.is_available():
            try:
                result = self.provider.generate_json(
                    prompts.INSIGHTS_SYSTEM, prompts.insights_prompt(aggregated)
                )
                insights = result.get("insights")
                if isinstance(insights, list) and insights:
                    return [i for i in insights if isinstance(i, dict)]
            except AppError:
                pass
        return fallback_insights(aggregated)

    # ---- monthly summary ------------------------------------------------
    def generate_monthly_summary(self, aggregated: dict) -> str:
        from app.services.ai.insights import fallback_monthly_summary

        if self.provider.is_available():
            try:
                result = self.provider.generate_json(
                    prompts.SUMMARY_SYSTEM, prompts.summary_prompt(aggregated)
                )
                summary = result.get("summary")
                if isinstance(summary, str) and summary.strip():
                    return summary.strip()
            except AppError:
                pass
        return fallback_monthly_summary(aggregated)

    # ---- budget recommendations -----------------------------------------
    def generate_budget_recommendations(self, aggregated: dict) -> list[dict]:
        from app.services.ai.recommendations import (
            build_recommendations,
            fallback_recommendations,
        )

        deterministic = build_recommendations(aggregated)
        if self.provider.is_available():
            try:
                result = self.provider.generate_json(
                    prompts.RECOMMENDATION_SYSTEM,
                    prompts.recommendation_prompt(aggregated),
                )
                recommendations = result.get("recommendations")
                if isinstance(recommendations, list) and recommendations:
                    return recommendations
            except AppError:
                pass
        return fallback_recommendations(aggregated, deterministic)

    # ---- anomaly explanation --------------------------------------------
    def explain_anomaly(self, anomaly_data: dict) -> str:
        from app.services.ai.anomaly_detection import fallback_explain_anomaly

        if self.provider.is_available():
            try:
                result = self.provider.generate_json(
                    prompts.ANOMALY_EXPLAIN_SYSTEM, prompts.anomaly_prompt(anomaly_data)
                )
                explanation = result.get("explanation")
                if isinstance(explanation, str) and explanation.strip():
                    return explanation.strip()
            except AppError:
                pass
        return fallback_explain_anomaly(anomaly_data)

    @staticmethod
    def _valid_category_result(result: dict, categories: list[str]) -> bool:
        category = result.get("category")
        confidence = result.get("confidence")
        return isinstance(category, str) and category in categories and isinstance(confidence, (int, float))


def get_ai_service() -> AIService:
    return AIService()


def save_insight(
    db,
    user: User,
    insight_type: str,
    title: str,
    content: str,
    severity: str = "INFO",
    metadata: dict | None = None,
) -> AIInsight:
    """Persist an AI insight for a user (used by all insight producers)."""
    insight = AIInsight(
        user_id=user.id,
        insight_type=insight_type,
        title=title,
        content=content,
        severity=severity,
        insight_metadata=metadata,
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def insight_to_dict(insight: AIInsight) -> dict[str, Any]:
    return {
        "id": insight.id,
        "insight_type": insight.insight_type,
        "title": insight.title,
        "content": insight.content,
        "severity": insight.severity,
        "metadata": insight.insight_metadata,
        "created_at": insight.created_at.isoformat(),
    }
