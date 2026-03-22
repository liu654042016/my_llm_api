import pytest
from src.core.logging import RequestLog, RequestLogger


def test_request_log_captures_data():
    log = RequestLog(
        model="gpt-4o",
        provider="openai",
        tokens_used=100,
        tokens_completed=50,
        duration_ms=500,
        fallback_used=False,
        fallback_to=None,
        status="success",
        error_message=None,
    )
    assert log.model == "gpt-4o"
    assert log.tokens_used == 100


def test_request_logger_singleton():
    logger1 = RequestLogger()
    logger2 = RequestLogger()
    # Should be the same instance
    assert logger1 is logger2


def test_request_logger_records():
    logger = RequestLogger()
    logger.clear()
    logger.log(
        model="gpt-4o",
        provider="openai",
        tokens_used=100,
        tokens_completed=50,
        duration_ms=500,
    )
    
    logs = logger.get_logs()
    assert len(logs) == 1
    assert logs[0].model == "gpt-4o"
