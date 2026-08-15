"""CSV import and export business logic."""
import csv
import io
from datetime import date

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError, ErrorCode
from app.core.logging import log_service_event
from app.models.category import Category
from app.models.expense import Expense, PaymentMethod
from app.models.user import User
from app.schemas.csv import ImportRowError, ImportSummary
from app.utils.csv_utils import read_csv_bytes
from app.utils.date_utils import parse_date

REQUIRED_COLUMNS = ["date", "description", "category", "amount"]

EXPORT_COLUMNS = ["Date", "Description", "Merchant", "Category", "Amount", "Payment Method"]

settings = get_settings()


def _resolve_category(db: Session, user: User, name: str) -> Category:
    """Find a default or user category by name, creating a custom one if missing."""
    category = db.scalar(
        select(Category).where(
            Category.name.ilike(name),
            (Category.user_id.is_(None)) | (Category.user_id == user.id),
        )
    )
    if category is None:
        category = Category(name=name.strip()[:100], is_default=False, user_id=user.id)
        db.add(category)
        db.flush()
    return category


def _is_duplicate(db: Session, user: User, amount: float, expense_date: date, description: str) -> bool:
    return (
        db.scalar(
            select(Expense.id).where(
                Expense.user_id == user.id,
                Expense.amount == amount,
                Expense.expense_date == expense_date,
                Expense.description.ilike(description),
            ).limit(1)
        )
        is not None
    )


def import_csv(db: Session, user: User, file: UploadFile) -> ImportSummary:
    raw = file.file.read()
    max_bytes = settings.MAX_CSV_SIZE_MB * 1024 * 1024
    if len(raw) > max_bytes:
        raise AppError(
            f"CSV file exceeds the {settings.MAX_CSV_SIZE_MB} MB size limit.",
            ErrorCode.CSV_TOO_LARGE,
            status_code=413,
        )

    try:
        rows = read_csv_bytes(raw)
    except ValueError as exc:
        raise AppError(
            f"Could not parse CSV file: {exc}",
            ErrorCode.CSV_INVALID_FILE,
            status_code=400,
        ) from exc

    if not rows:
        raise AppError(
            "CSV file contains no data rows.",
            ErrorCode.CSV_INVALID_FILE,
            status_code=400,
        )

    headers = set(rows[0].keys())
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise AppError(
            f"CSV is missing required columns: {', '.join(missing)}.",
            ErrorCode.CSV_MISSING_COLUMNS,
            status_code=400,
        )

    imported = 0
    duplicates = 0
    errors: list[ImportRowError] = []

    for index, row in enumerate(rows, start=2):
        row_number = index
        try:
            amount = float(row.get("amount", "").replace(",", "").replace("₹", "").strip())
            if amount <= 0:
                raise ValueError("amount must be greater than zero")
            expense_date = parse_date(row.get("date", ""))
            description = row.get("description", "").strip()
            if not description:
                raise ValueError("description is required")

            if _is_duplicate(db, user, amount, expense_date, description):
                duplicates += 1
                continue

            category = _resolve_category(db, user, row.get("category", "").strip() or "Other")

            payment_value = row.get("payment_method", "").upper().replace(" ", "_")
            if payment_value and payment_value not in PaymentMethod.__members__:
                payment_value = PaymentMethod.OTHER.value

            db.add(
                Expense(
                    user_id=user.id,
                    category_id=category.id,
                    amount=amount,
                    description=description,
                    merchant=row.get("merchant", "").strip() or None,
                    payment_method=payment_value or PaymentMethod.OTHER.value,
                    expense_date=expense_date,
                    notes=row.get("notes", "").strip() or None,
                )
            )
            db.flush()
            imported += 1
        except (ValueError, TypeError) as exc:
            errors.append(ImportRowError(row=row_number, error=str(exc)))

    db.commit()
    log_service_event(
        "csv",
        "import_completed",
        user_id=user.id,
        imported=imported,
        failed=len(errors),
        duplicates=duplicates,
    )
    return ImportSummary(
        total_rows=len(rows),
        imported=imported,
        failed=len(errors),
        duplicates=duplicates,
        errors=errors,
    )


def export_csv(db: Session, user: User) -> str:
    expenses = list(
        db.scalars(
            select(Expense).where(Expense.user_id == user.id).order_by(Expense.expense_date.desc())
        )
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(EXPORT_COLUMNS)
    for expense in expenses:
        writer.writerow(
            [
                expense.expense_date.isoformat(),
                expense.description,
                expense.merchant or "",
                expense.category.name,
                f"{expense.amount:.2f}",
                expense.payment_method,
            ]
        )
    return buffer.getvalue()
