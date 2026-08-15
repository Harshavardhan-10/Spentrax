"""Budget recommendation logic.

The deterministic baseline uses the user's historical category averages;
the provider (when available) may refine the numbers and reasons. Users must
always approve recommendations before they are applied.
"""
from statistics import fmean
from typing import Any


def build_recommendations(aggregated: dict) -> list[dict]:
    """Deterministic recommendations based on 3-month category averages."""
    category_averages: dict = aggregated.get("category_averages") or {}
    recommendations = []
    for category, average in category_averages.items():
        try:
            avg = float(average)
        except (TypeError, ValueError):
            continue
        if avg <= 0:
            continue
        recommended = round(avg * 1.05, 2)
        recommendations.append({
            "category": category,
            "recommended_budget": recommended,
            "reason": (
                f"Based on your average spending of ₹{avg:,.2f} "
                "over the last 3 months, with a small buffer."
            ),
        })
    return recommendations


def fallback_recommendations(aggregated: dict, deterministic: list[dict]) -> list[dict]:
    return deterministic
