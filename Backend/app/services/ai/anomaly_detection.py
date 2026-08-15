"""Fallback natural-language explanation for detected spending anomalies."""
from typing import Any


def fallback_explain_anomaly(anomaly_data: dict) -> str:
    amount = anomaly_data.get("amount")
    mean = anomaly_data.get("mean")
    category = anomaly_data.get("category") or "this category"
    z_score = anomaly_data.get("z_score")

    parts = [
        f"An unusual expense of ₹{amount:,.2f} was detected"
        if isinstance(amount, (int, float))
        else "An unusually large expense was detected"
    ]
    if isinstance(mean, (int, float)):
        parts.append(f"compared to your typical average of ₹{mean:,.2f} in {category}")
    if isinstance(z_score, (int, float)):
        parts.append(f"({z_score:.1f} standard deviations above your normal range)")
    parts.append("Review the transaction to confirm it is correct.")
    return " ".join(parts)
