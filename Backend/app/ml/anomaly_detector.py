"""Statistical anomaly detection for expenses.

An expense is flagged when its amount deviates strongly from the user's
historical spending in the same category (z-score based, with a minimum
sample size). No AI model is required for the detection itself; the AI
layer can later explain the anomaly in natural language.
"""
from dataclasses import dataclass, field
from statistics import fmean, pstdev
from typing import Optional


@dataclass
class AnomalyResult:
    is_anomaly: bool
    amount: float
    mean: float
    std: float
    z_score: float
    threshold: float
    sample_size: int
    reason: str = ""


@dataclass
class AnomalyDetectionConfig:
    min_samples: int = 3
    z_threshold: float = 2.0
    absolute_min_amount: float = 1000.0


def _compute_statistics(amounts: list[float]) -> tuple[float, float]:
    if len(amounts) < 2:
        return fmean(amounts), 0.0
    return fmean(amounts), pstdev(amounts)


def detect_category_anomaly(
    historical_amounts: list[float],
    new_amount: float,
    config: AnomalyDetectionConfig | None = None,
) -> Optional[AnomalyResult]:
    config = config or AnomalyDetectionConfig()
    sample_size = len(historical_amounts)

    if sample_size < config.min_samples:
        return None

    mean, std = _compute_statistics(historical_amounts)
    if std == 0:
        z_score = 0.0
    else:
        z_score = (new_amount - mean) / std

    is_anomaly = z_score >= config.z_threshold and new_amount >= config.absolute_min_amount
    if not is_anomaly:
        return None

    return AnomalyResult(
        is_anomaly=True,
        amount=new_amount,
        mean=round(mean, 2),
        std=round(std, 2),
        z_score=round(z_score, 2),
        threshold=config.z_threshold,
        sample_size=sample_size,
        reason=(
            f"Expense of {new_amount:,.2f} is {z_score:.1f} standard deviations "
            f"above your average of {mean:,.2f} in this category."
        ),
    )


def detect_global_anomaly(
    historical_amounts: list[float],
    new_amount: float,
    config: AnomalyDetectionConfig | None = None,
) -> Optional[AnomalyResult]:
    config = config or AnomalyDetectionConfig()
    config.min_samples = max(config.min_samples, 5)
    return detect_category_anomaly(historical_amounts, new_amount, config)
