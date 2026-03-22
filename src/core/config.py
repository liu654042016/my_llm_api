from dataclasses import dataclass
from typing import List


@dataclass
class AdapterConfig:
    name: str


@dataclass
class Config:
    adapters: List[AdapterConfig]


def load_config(path: str) -> Config:
    # Minimal placeholder config loader for tests
    return Config(adapters=[])
