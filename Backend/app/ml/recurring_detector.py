"""Deterministic recurring expense detection.

Detection is purely statistical: transactions are grouped by normalized
merchant/description, amounts must be similar, and the gaps between dates
must match a known frequency. No LLM is involved in detection; the AI layer
only explains detected patterns afterwards.
"""
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from statistics import fmean

from app.models.expense import Expense
from app.utils.date_utils import days_between

FREQUENCY_DAYS = {
    "WEEKLY": 7,
    "MONTHLY": 30,
    "QUARTERLY": 91,
    "YEARLY": 365,
}

INTERVAL_TOLERANCE = 0.25
AMOUNT_TOLERANCE_RATIO = 0.10
AMOUNT_TOLERANCE_ABSOLUTE = 50.0
MIN_OCCURRENCES = 3
CONFIDENCE_FLOOR = 0.80


@dataclass
class RecurringCandidate:
    name: str
    amount: float
    frequency: str
    confidence: float
    next_due_date: date
    occurrences: int
    expense_ids: list[int]


def _normalize_name(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9 ]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _amounts_similar(amounts: list[float]) -> bool:
    if len(amounts) < 2:
        return True
    mean = fmean(amounts)
    tolerance = max(AMOUNT_TOLERANCE_ABSOLUTE, mean * AMOUNT_TOLERANCE_RATIO)
    return (max(amounts) - min(amounts)) <= tolerance


def _best_frequency(gaps_days: list[int]) -> tuple[str, float]:
    best_frequency = "MONTHLY"
    best_consistency = 0.0
    for frequency, expected in FREQUENCY_DAYS.items():
        tolerance = expected * INTERVAL_TOLERANCE
        matched = sum(
            1 for gap in gaps_days if abs(gap - expected) <= tolerance
        )
        consistency = matched / len(gaps_days) if gaps_days else 0.0
        if consistency > best_consistency:
            best_consistency = consistency
            best_frequency = frequency
    return best_frequency, best_consistency


def detect_recurring_candidates(expenses: list[Expense]) -> list[RecurringCandidate]:
    """Analyze a user's expenses and return recurring candidates."""
    groups: dict[str, list[Expense]] = defaultdict(list)
    for expense in expenses:
        key = _normalize_name(expense.merchant or expense.description)
        if key:
            groups[key].append(expense)

    candidates: list[RecurringCandidate] = []
    for name, group in groups.items():
        group = sorted(group, key=lambda e: e.expense_date)
        if len(group) < MIN_OCCURRENCES:
            continue

        amounts = [e.amount for e in group]
        if not _amounts_similar(amounts):
            continue

        gaps = [
            days_between(group[i].expense_date, group[i + 1].expense_date)
            for i in range(len(group) - 1)
        ]
        frequency, consistency = _best_frequency(gaps)

        occurrences = len(group)
        confidence = round(
            min(
                0.99,
                CONFIDENCE_FLOOR + 0.05 * (occurrences - MIN_OCCURRENCES)
                + 0.10 * consistency,
            ),
            2,
        )

        next_due = date.fromordinal(
            group[-1].expense_date.toordinal()
            + FREQUENCY_DAYS[frequency]
        )

        candidates.append(
            RecurringCandidate(
                name=_display_name(group[0]),
                amount=round(fmean(amounts), 2),
                frequency=frequency,
                confidence=confidence,
                next_due_date=next_due,
                occurrences=occurrences,
                expense_ids=[e.id for e in group],
            )
        )

    return sorted(candidates, key=lambda c: c.confidence, reverse=True)


def _display_name(expense: Expense) -> str:
    return expense.merchant or expense.description
