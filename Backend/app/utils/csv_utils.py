"""CSV parsing helpers."""
import csv
import io
from typing import Any


def normalize_headers(headers: list[str]) -> list[str]:
    """Lowercase, strip and normalize CSV headers."""
    return [h.lower().strip().replace(" ", "_").replace("-", "_") for h in headers]


def read_csv_bytes(raw: bytes) -> list[dict[str, Any]]:
    """Decode CSV bytes (handles BOM) into a list of row dicts."""
    text = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError("Could not decode CSV file with a supported encoding.")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("CSV file is empty or has no header row.")

    normalized = normalize_headers(reader.fieldnames)
    rows = []
    for raw_row in reader:
        row: dict[str, Any] = {}
        for header, value in zip(normalized, [raw_row.get(f, "") for f in reader.fieldnames]):
            row[header] = (value or "").strip()
        if any(row.values()):
            rows.append(row)
    return rows
