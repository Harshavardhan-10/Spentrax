"""Date helpers used across services and the ML layer."""
from datetime import date, datetime, timedelta

from pydantic import BaseModel


def month_bounds(year: int, month: int) -> tuple[date, date]:
    """Return (first_day, last_day) of the given month."""
    first = date(year, month, 1)
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    return first, last


def previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def current_month() -> tuple[int, int]:
    today = date.today()
    return today.year, today.month


def parse_date(value: str) -> date:
    """Parse a date string supporting ISO and common day-first formats."""
    value = value.strip()
    formats = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y")
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {value!r}")


def days_between(a: date, b: date) -> int:
    return abs((b - a).days)


def next_occurrence(from_date: date, gap_days: int) -> date:
    return from_date + timedelta(days=gap_days)


def to_iso(d: date) -> str:
    return d.isoformat()


class DateRange(BaseModel):
    start: date
    end: date
