"""Consistent API response helpers and the success envelope.

Success responses are always:

    {"success": true, "data": ..., "message": ...?}

Error responses (produced by global handlers in main.py) are always:

    {"success": false, "message": "...", "error_code": "..."}
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None


def ok(data: Any, message: Optional[str] = None) -> dict:
    response: dict[str, Any] = {"success": True, "data": data}
    if message is not None:
        response["message"] = message
    return response


def error_response(message: str, error_code: str) -> dict:
    return {"success": False, "message": message, "error_code": error_code}
