import os
import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class AdapterConfig(BaseModel):
    """Configuration for a single LLM provider adapter."""
    name: str
    api_key: str
    base_url: str
    models: list[str] = Field(default_factory=list)


class Config(BaseModel):
    """Application configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    adapters: list[AdapterConfig] = Field(default_factory=list)
    log_level: str = "INFO"
    log_requests: bool = True


def _substitute_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} with environment variable values."""
    pattern = re.compile(r'\$\{([^}]+)\}')
    
    def replace(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    
    return pattern.sub(replace, value)


def _process_dict_env_vars(data: dict) -> dict:
    """Recursively substitute env vars in dictionary values."""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = _substitute_env_vars(value)
        elif isinstance(value, dict):
            result[key] = _process_dict_env_vars(value)
        elif isinstance(value, list):
            result[key] = [
                _substitute_env_vars(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            result[key] = value
    return result


def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration from YAML file with env var substitution."""
    path = Path(config_path)
    if not path.exists():
        # Return default config if file doesn't exist
        return Config()
    
    with open(path) as f:
        raw_data = yaml.safe_load(f)
    
    if raw_data is None:
        return Config()
    
    # Substitute environment variables
    data = _process_dict_env_vars(raw_data)
    
    return Config(**data)
