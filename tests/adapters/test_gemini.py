import pytest
from src.adapters.gemini import GeminiAdapter


def test_supports_gemini_models():
    adapter = GeminiAdapter(
        name="gemini",
        api_key="test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        models=["gemini-1.5-flash", "gemini-pro"],
    )
    assert adapter.supports_model("gemini-1.5-flash")
    assert adapter.supports_model("gemini-pro")
    assert not adapter.supports_model("gpt-4o")
