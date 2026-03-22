import pytest


@pytest.fixture
def sample_config():
    # Sample configuration for testing.
    from src.core.config import Config, AdapterConfig
    
    return Config(
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o", "gpt-3.5-turbo"],
            ),
            AdapterConfig(
                name="gemini",
                api_key="test-key",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-flash"],
            ),
        ],
    )
