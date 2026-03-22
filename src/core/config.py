from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AdapterConfig:
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: Optional[list[str]] = None


@dataclass
class Config:
    adapters: List[AdapterConfig]


def load_config(path: str) -> Config:
    # Minimal placeholder config loader for tests
    return Config(adapters=[])
