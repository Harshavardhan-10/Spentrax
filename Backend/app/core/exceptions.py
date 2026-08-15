"""Centralized application exceptions and error codes.

Every error raised inside the application is converted into a consistent
response shape by the global exception handlers registered in main.py:

    {"success": false, "message": "...", "error_code": "..."}
"""
from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTH_INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "TOKEN_INVALID"
    AUTH_NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    AUTH_EMAIL_TAKEN = "EMAIL_ALREADY_REGISTERED"
    AUTH_INACTIVE_ACCOUNT = "ACCOUNT_INACTIVE"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    CATEGORY_ALREADY_EXISTS = "CATEGORY_ALREADY_EXISTS"
    CATEGORY_ACCESS_DENIED = "CATEGORY_ACCESS_DENIED"
    EXPENSE_NOT_FOUND = "EXPENSE_NOT_FOUND"
    BUDGET_NOT_FOUND = "BUDGET_NOT_FOUND"
    BUDGET_ALREADY_EXISTS = "BUDGET_ALREADY_EXISTS"
    RECURRING_NOT_FOUND = "RECURRING_NOT_FOUND"
    CSV_INVALID_FILE = "CSV_INVALID_FILE"
    CSV_TOO_LARGE = "CSV_TOO_LARGE"
    CSV_MISSING_COLUMNS = "CSV_MISSING_COLUMNS"
    AI_UNAVAILABLE = "AI_UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """Base application error carrying an HTTP status, message and code."""

    def __init__(self, message: str, error_code: ErrorCode, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


def not_found_error(entity: str) -> AppError:
    return AppError(
        f"{entity} not found",
        ErrorCode.NOT_FOUND,
        status_code=404,
    )
