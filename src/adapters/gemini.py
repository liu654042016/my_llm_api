from __future__ import annotations

from typing import Any, List, Optional

import httpx

from src.adapters.base import BaseAdapter, AdapterError


class GeminiAdapter(BaseAdapter):
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        models: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, api_key=api_key, base_url=base_url, models=models)

    async def chat_completions(
        self,
        messages: list,
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        client = await self._get_client()

        contents = self._convert_messages(messages)

        request_body = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.9),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            },
        }

        url = f"{self.base_url}/models/{model}:generateContent"

        try:
            response = await client.post(
                url,
                json=request_body,
                params={"key": self.api_key},
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise AdapterError(
                f"Gemini API error: {e.response.status_code} - {e.response.text}",
                provider=self.name,
            )
        except httpx.RequestError as e:
            raise AdapterError(
                f"Request failed: {e}",
                provider=self.name,
            )

    def _convert_messages(self, messages: list) -> list:
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "assistant":
                role = "model"
            elif role == "system":
                role = "user"

            content = msg.get("content", "")
            contents.append({
                "role": role,
                "parts": [{"text": content}],
            })
        return contents
