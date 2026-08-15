"""Prompt templates for the AI providers.

Prompts are kept here so providers stay free of prompt content and the
templates can evolve independently.
"""
import json

CATEGORIZE_SYSTEM = (
    "You are a personal finance assistant. Given a transaction description "
    "and optional merchant, choose the single best expense category from the "
    "provided list and reply with ONLY valid JSON: "
    '{"category": "...", "confidence": 0.0-1.0, "reason": "..."}.'
)

INSIGHTS_SYSTEM = (
    "You are a personal finance analyst. Based ONLY on the provided "
    "aggregated financial data, produce 3-5 concise, actionable insights. "
    "Reply with ONLY valid JSON: "
    '{"insights": [{"title": "...", "content": "...", "severity": "INFO|WARNING|IMPORTANT", "type": "SPENDING|BUDGET|ANOMALY|SAVING|RECURRING"}]}.'
)

SUMMARY_SYSTEM = (
    "You are a personal finance analyst. Write a short, friendly monthly "
    "financial summary (2-4 sentences) based ONLY on the provided aggregated "
    "data. Reply with ONLY valid JSON: {\"summary\": \"...\"}."
)

RECOMMENDATION_SYSTEM = (
    "You are a personal finance advisor. Based ONLY on the provided "
    "historical spending data, review the suggested budget for each category "
    "and reply with ONLY valid JSON: "
    '{"recommendations": [{"category": "...", "recommended_budget": 0, "reason": "..."}]}.'
)

ANOMALY_EXPLAIN_SYSTEM = (
    "You are a personal finance analyst. Explain the following detected "
    "spending anomaly in one or two clear, non-alarming sentences. Reply with "
    'ONLY valid JSON: {"explanation": "..."}.'
)


def categorize_prompt(description: str, merchant: str | None, categories: list[str]) -> str:
    return json.dumps(
        {
            "description": description,
            "merchant": merchant,
            "available_categories": categories,
        }
    )


def insights_prompt(aggregated_data: dict) -> str:
    return json.dumps(aggregated_data, default=str)


def summary_prompt(aggregated_data: dict) -> str:
    return json.dumps(aggregated_data, default=str)


def recommendation_prompt(aggregated_data: dict) -> str:
    return json.dumps(aggregated_data, default=str)


def anomaly_prompt(anomaly_data: dict) -> str:
    return json.dumps(anomaly_data, default=str)
