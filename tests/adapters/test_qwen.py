import pytest
from src.adapters.qwen import QwenAdapter


def test_supports_qwen_models():
    adapter = QwenAdapter(
        name="qwen",
        api_key="test-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        models=["qwen-turbo", "qwen-plus"],
    )
    assert adapter.supports_model("qwen-turbo")
    assert adapter.supports_model("qwen-plus")
    assert not adapter.supports_model("gpt-4o")
