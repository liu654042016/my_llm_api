import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class AdapterConfig:
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: Optional[List[str]] = None


@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 8000
    adapters: List[AdapterConfig] = field(default_factory=list)
    log_level: str = "INFO"
    log_requests: bool = True


def _substitute_env_vars(value: str) -> str:
    pattern = re.compile(r'\$\{([^}]+)\}')
    
    def replace(match: re.Match) -> str:
        var_name = match.group(1)
        env_val = os.environ.get(var_name)
        return env_val if env_val is not None else match.group(0)
    
    return pattern.sub(replace, value)


def _process_dict_env_vars(data):
    if isinstance(data, dict):
        return {k: _process_dict_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_process_dict_env_vars(v) for v in data]
    elif isinstance(data, str):
        return _substitute_env_vars(data)
    return data


def load_config(config_path: str = "config.yaml") -> Config:
    path = Path(config_path)
    if not path.exists():
        return Config()
    
    with open(path) as f:
        raw_data = yaml.safe_load(f)
    
    if raw_data is None:
        return Config()
    
    if not isinstance(raw_data, dict):
        return Config()
    
    data = _process_dict_env_vars(raw_data)
    
    if not isinstance(data, dict):
        return Config()
    
    known_keys = {'host', 'port', 'adapters', 'log_level', 'log_requests'}
    filtered_data: dict = {k: v for k, v in data.items() if k in known_keys}
    
    if 'adapters' in filtered_data and isinstance(filtered_data['adapters'], list):
        adapters = []
        for a in filtered_data['adapters']:
            if isinstance(a, dict):
                adapters.append(AdapterConfig(**a))
        filtered_data['adapters'] = adapters
    
    return Config(**filtered_data)  # type: ignore
