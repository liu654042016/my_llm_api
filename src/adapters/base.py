from abc import ABC, abstractmethod
from typing import Any, List, Optional

import httpx


class AdapterError(Exception):
    def __init__(self, message: str, provider: Optional[str] = None) -> None:
        super().__init__(message)
        self.provider = provider


class BaseAdapter(ABC):
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        models: Optional[List[str]] = None,
    ) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.models = models or []
        self._client: Optional[httpx.AsyncClient] = None

    def supports_model(self, model: str) -> bool:
        return model in self.models

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def chat_completions(
        self,
        messages: List[dict],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        pass
