import time
from typing import Any, Dict, List, Optional, Union

import httpx

from src.adapters.base import AdapterError, BaseAdapter
from src.adapters.gemini import GeminiAdapter
from src.adapters.openai import OpenAIAdapter
from src.adapters.qwen import QwenAdapter
from src.core.config import Config, AdapterConfig
from src.core.logging import RequestLogger


ADAPTER_CLASSES = {
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "qwen": QwenAdapter,
}


class RouterError(Exception):
    pass


class Router:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._adapters: Dict[str, BaseAdapter] = {}
        self._logger = RequestLogger()
        self._init_adapters()

    def _init_adapters(self) -> None:
        for adapter_config in self.config.adapters:
            adapter_class = ADAPTER_CLASSES.get(adapter_config.name)
            if adapter_class is None:
                continue

            adapter = adapter_class(
                name=adapter_config.name,
                api_key=adapter_config.api_key or "",
                base_url=adapter_config.base_url or "",
                models=adapter_config.models or [],
            )
            self._adapters[adapter_config.name] = adapter

    def find_adapters(self, model: str) -> List[BaseAdapter]:
        result = []
        for adapter_config in self.config.adapters:
            adapter = self._adapters.get(adapter_config.name)
            if adapter and adapter.supports_model(model):
                result.append(adapter)
        return result

    async def route(
        self,
        messages: List[dict],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        adapters = self.find_adapters(model)

        if not adapters:
            raise RouterError(f"No adapter found for model: {model}")

        last_error: Optional[AdapterError] = None

        for i, adapter in enumerate(adapters):
            start_time = time.time()

            try:
                response = await adapter.chat_completions(
                    messages=messages,
                    model=model,
                    stream=stream,
                    **kwargs,
                )

                duration_ms = int((time.time() - start_time) * 1000)

                tokens_used = 0
                tokens_completed = 0
                try:
                    data = response.json()
                    usage = data.get("usage", {})
                    tokens_used = usage.get("prompt_tokens", 0)
                    tokens_completed = usage.get("completion_tokens", 0)
                except Exception:
                    pass

                self._logger.log(
                    model=model,
                    provider=adapter.name,
                    tokens_used=tokens_used,
                    tokens_completed=tokens_completed,
                    duration_ms=duration_ms,
                    fallback_used=i > 0,
                    fallback_to=None if i == 0 else adapters[i - 1].name,
                    status="success",
                )

                return response

            except AdapterError as e:
                last_error = e
                duration_ms = int((time.time() - start_time) * 1000)

                self._logger.log(
                    model=model,
                    provider=adapter.name,
                    duration_ms=duration_ms,
                    fallback_used=True,
                    fallback_to=adapters[i + 1].name if i + 1 < len(adapters) else None,
                    status="error",
                    error_message=str(e),
                )

                continue

        raise RouterError(
            f"All adapters failed for model {model}: {last_error}"
        )

    async def close(self) -> None:
        for adapter in self._adapters.values():
            await adapter.close()
