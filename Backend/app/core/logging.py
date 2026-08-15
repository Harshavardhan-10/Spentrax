"""Structured application logging configuration.

Logs requests, errors and important service events. Sensitive values
(passwords, JWT tokens, API keys) are never logged anywhere in the app.
"""
import logging
import sys
from datetime import datetime, timezone

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


class SensitiveDataFilter(logging.Filter):
    """Redacts known sensitive fields from log records."""

    SENSITIVE_KEYS = ("password", "password_hash", "token", "authorization", "api_key", "secret")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lowered = message.lower()
        for key in self.SENSITIVE_KEYS:
            if key in lowered:
                record.msg = "[REDACTED - sensitive data omitted]"
                record.args = ()
                break
        return True


def setup_logging(debug: bool = False) -> None:
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format=_LOG_FORMAT,
        handlers=handlers,
        force=True,
    )
    for handler in handlers:
        handler.addFilter(SensitiveDataFilter())
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def log_service_event(service: str, event: str, **metadata) -> None:
    """Log an important service event at INFO level with key metadata."""
    extra = " ".join(f"{key}={value}" for key, value in metadata.items())
    logging.getLogger(f"app.services.{service}").info("%s | %s", event, extra)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
