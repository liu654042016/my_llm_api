import pytest
from src.adapters.openai import OpenAIAdapter
from src.adapters.base import AdapterError


def test_supports_openai_models():
    adapter = OpenAIAdapter(
        name="openai",
        api_key="sk-test",
        base_url="https://api.openai.com/v1",
        models=["gpt-4o", "gpt-3.5-turbo"],
    )
    assert adapter.supports_model("gpt-4o")
    assert adapter.supports_model("gpt-3.5-turbo")
    assert not adapter.supports_model("gemini-1.5-flash")
