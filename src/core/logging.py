import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RequestLog:
    """Record of a single API request."""
    model: str
    provider: str
    tokens_used: int = 0
    tokens_completed: int = 0
    duration_ms: int = 0
    fallback_used: bool = False
    fallback_to: Optional[str] = None
    status: str = "success"  # e.g., 'success', 'error', 'fallback'
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RequestLogger:
    """Singleton logger for API requests."""

    _instance: Optional["RequestLogger"] = None
    _logs: list[RequestLog] = []

    def __new__(cls) -> "RequestLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logs = []
        return cls._instance

    def log(
        self,
        model: str,
        provider: str,
        tokens_used: int = 0,
        tokens_completed: int = 0,
        duration_ms: int = 0,
        fallback_used: bool = False,
        fallback_to: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """Log a request."""
        log_entry = RequestLog(
            model=model,
            provider=provider,
            tokens_used=tokens_used,
            tokens_completed=tokens_completed,
            duration_ms=duration_ms,
            fallback_used=fallback_used,
            fallback_to=fallback_to,
            status=status,
            error_message=error_message,
        )
        self._logs.append(log_entry)

        logger.info(
            f"[{provider}] {model} | "
            f"tokens: {tokens_used}/{tokens_completed} | "
            f"duration: {duration_ms}ms | "
            f"status: {status}"
            + (f" | fallback to {fallback_to}" if fallback_used else "")
        )

    def get_logs(self) -> list[RequestLog]:
        """Get all logged requests."""
        return self._logs.copy()

    def clear(self) -> None:
        """Clear all logs."""
        self._logs.clear()
