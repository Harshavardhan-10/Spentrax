"""CSV import/export schemas."""
from typing import Optional

from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    error: str


class ImportSummary(BaseModel):
    total_rows: int
    imported: int
    failed: int
    duplicates: int
    errors: list[ImportRowError]
