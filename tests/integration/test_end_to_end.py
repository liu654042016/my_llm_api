import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.router import Router
from src.core.config import Config, AdapterConfig
from src.adapters.base import AdapterError


@pytest.fixture
def config():
    return Config(
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o"],
            ),
            AdapterConfig(
                name="gemini",
                api_key="test-key",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-flash"],
            ),
        ]
    )


@pytest.mark.asyncio
async def test_successful_request(config):
    
    router = Router(config)
    
    # Mock the adapter's chat_completions method
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    mock_response.aiter_bytes = AsyncMock(return_value=iter(b'{"choices": []}'))
    
    async def mock_chat(*args, **kwargs):
        return mock_response
    
    router._adapters["openai"].chat_completions = mock_chat
    
    response = await router.route(
        messages=[{"role": "user", "content": "Hi"}],
        model="gpt-4o",
    )
    
    assert response.status_code == 200
    await router.close()


@pytest.mark.asyncio
async def test_fallback_on_failure(config):
    
    router = Router(config)
    
    # First adapter fails
    async def fail_first(*args, **kwargs):
        raise AdapterError("Service unavailable", provider="openai")
    
    # Second adapter succeeds
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Hello from Gemini!"}]
            }
        }]
    }
    mock_response.aiter_bytes = AsyncMock(return_value=iter(b'{}'))
    
    async def succeed_second(*args, **kwargs):
        return mock_response
    
    router._adapters["openai"].chat_completions = fail_first
    router._adapters["gemini"].chat_completions = succeed_second
    
    response = await router.route(
        messages=[{"role": "user", "content": "Hi"}],
        model="gemini-1.5-flash",
    )
    
    assert response.status_code == 200
    
    # Check logs show fallback
    logs = router._logger.get_logs()
    assert len(logs) == 2  # One failed, one succeeded
    assert logs[0].status == "error"
    assert logs[1].status == "success"
    assert logs[1].fallback_used is True
    
    await router.close()


@pytest.mark.asyncio
async def test_no_adapter_found(config):
    
    router = Router(config)
    
    with pytest.raises(Exception) as exc_info:
        await router.route(
            messages=[{"role": "user", "content": "Hi"}],
            model="unknown-model",
        )
    
    assert "No adapter found" in str(exc_info.value)
    await router.close()
