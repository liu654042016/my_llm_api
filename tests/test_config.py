import os
import tempfile
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
    assert config.models is not None and "model-a" in config.models


def test_env_var_substitution():
    os.environ["TEST_API_KEY"] = "secret-123"
    os.environ["TEST_BASE_URL"] = "https://custom.test.com"
    
    yaml_content = """
adapters:
  - name: test
    api_key: ${TEST_API_KEY}
    base_url: ${TEST_BASE_URL}
    models:
      - model-a
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    config = load_config(temp_path)
    assert len(config.adapters) == 1
    assert config.adapters[0].api_key == "secret-123"
    assert config.adapters[0].base_url == "https://custom.test.com"
    
    os.unlink(temp_path)
    del os.environ["TEST_API_KEY"]
    del os.environ["TEST_BASE_URL"]


def test_config_loads_yaml():
    config = load_config("config.yaml.example")
    assert config.port == 8000
    assert len(config.adapters) >= 1
