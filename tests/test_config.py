import os
import pytest
from src.core.config import Config, AdapterConfig, load_config


def test_adapter_config_from_dict():
    config = AdapterConfig(
        name="test",
        api_key="sk-test",
        base_url="https://api.test.com/v1",
        models=["model-a", "model-b"],
    )
    assert config.name == "test"
    assert config.api_key == "sk-test"
    assert "model-a" in config.models


def test_env_var_substitution():
    os.environ["TEST_API_KEY"] = "secret-123"
    os.environ["TEST_BASE_URL"] = "https://custom.test.com"
    
    config = AdapterConfig(
        name="test",
        api_key="${TEST_API_KEY}",
        base_url="${TEST_BASE_URL}",
        models=["model-a"],
    )
    
    assert config.api_key == "secret-123"
    assert config.base_url == "https://custom.test.com"


def test_config_loads_yaml():
    config = load_config("config.yaml.example")
    assert config.port == 8000
    assert len(config.adapters) >= 1
