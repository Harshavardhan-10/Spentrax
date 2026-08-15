"""Rule-based expense categorization fallback.

Keyword patterns map a description/merchant to the best category. Confidence
is derived from the number and weight of matching keywords. Used directly
when no external AI provider is configured, and as a fallback when the
provider fails.
"""
import re
from typing import Optional

KEYWORD_RULES: list[tuple[str, str, float]] = [
    # (regex pattern, category, weight)
    (r"\b(swiggy|zomato|ubereats|foodpanda|dominos|pizza|burger|mcdonald|kfc|restaurant|dinner|lunch|breakfast|cafe|coffee|starbucks|grocer|supermarket|bazar|mart|kirana|meat|vegetable|fruit)\b", "Food", 0.9),
    (r"\b(uber|ola|rapido|taxi|cab|fuel|petrol|diesel|gas|metro|train|bus|parking|toll|ride|auto)\b", "Transportation", 0.9),
    (r"\b(amazon|flipkart|myntra|ajio|clothing|shoe|electronics|gadget|mall|sale|watch|mobile|phone|laptop)\b", "Shopping", 0.8),
    (r"\b(netflix|prime|hotstar|spotify|youtube premium|playstation|steam|xbox|movie|cinema|game|concert|theatre|bookmy show|bookmyshow)\b", "Entertainment", 0.9),
    (r"\b(electricity|water bill|internet|broadband|wifi|jio|airtel|vodafone|phone bill|mobile recharge|gas bill|bill)\b", "Bills", 0.85),
    (r"\b(hospital|doctor|clinic|pharmacy|medic|chemist|dentist|health|insurance|lab)\b", "Healthcare", 0.9),
    (r"\b(udemy|coursera|course|tuition|school|college|book|ebook|exam|training|workshop)\b", "Education", 0.85),
    (r"\b(flight|airline|hotel|airbnb|booking|make my trip|makemytrip|goibibo|oyo|resort|trip|vacation)\b", "Travel", 0.9),
    (r"\b(rent)\b", "Rent", 0.95),
    (r"\b(apartment|society maintenance|maintenance)\b", "Utilities", 0.8),
]


def _keyword_score(text: str) -> tuple[str, float]:
    best_category = "Other"
    best_score = 0.0
    for pattern, category, weight in KEYWORD_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            score = weight
            if score > best_score:
                best_score = score
                best_category = category
    return best_category, best_score


def fallback_categorize(
    description: str, merchant: Optional[str], categories: list[str]
) -> dict:
    text = f"{description or ''} {merchant or ''}"
    category, score = _keyword_score(text)

    if category == "Other" or not score:
        return {
            "category": "Other",
            "confidence": 0.5,
            "reason": "No strong keyword match found. Please choose a category.",
        }
    if category not in categories:
        category = "Other"

    confidence = round(min(0.95, 0.6 + score * 0.35), 2)
    return {
        "category": category,
        "confidence": confidence,
        "reason": f"Transaction text matches typical {category.lower()} keywords.",
    }
