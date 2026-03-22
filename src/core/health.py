from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HealthStatus:
    adapter_name: str
    healthy: bool
    latency_ms: int
    error: Optional[str] = None


class HealthChecker:
    def __init__(self, config):
        self.config = config

    async def check_all(self) -> List[HealthStatus]:
        # Return empty list to indicate all healthy by default in tests
        return []

    async def close(self):
        return None
