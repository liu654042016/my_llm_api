from typing import Any

import httpx


class AdapterError(Exception):
    def __init__(self, message: str, provider: str | None = None) -> None:
        super().__init__(message)
        self.provider = provider


class BaseAdapter:
    def __init__(self, name: str, api_key: str, base_url: str, **kwargs: Any) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client
