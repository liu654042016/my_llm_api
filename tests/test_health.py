import pytest
from src.core.health import HealthChecker
from src.core.config import Config, AdapterConfig


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
        ]
    )


def test_health_checker_init(config):
    checker = HealthChecker(config)
    assert len(checker.adapters) == 1
    assert checker.adapters[0].name == "openai"
