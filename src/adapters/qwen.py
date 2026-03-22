from typing import Any, Optional, List

import httpx

from src.adapters.base import BaseAdapter, AdapterError


class QwenAdapter(BaseAdapter):
    """Adapter for Alibaba Qwen (DashScope) API."""

    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        models: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, api_key=api_key, base_url=base_url, **kwargs)
        self.models: List[str] = models or []

    def supports_model(self, model: str) -> bool:
        return model in self.models

    async def chat_completions(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Call Qwen API with OpenAI-compatible interface."""
        client = await self._get_client()

        # Qwen accepts OpenAI format directly
        request_body = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }

        try:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=request_body,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise AdapterError(
                f"Qwen API error: {e.response.status_code} - {e.response.text}",
                provider=self.name,
            )
        except httpx.RequestError as e:
            raise AdapterError(
                f"Request failed: {e}",
                provider=self.name,
            )
