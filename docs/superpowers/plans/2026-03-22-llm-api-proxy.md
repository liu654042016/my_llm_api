# LLM API Proxy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Python reverse proxy that unifies multiple LLM API providers (OpenAI, Gemini, Qwen) under a single OpenAI-compatible interface, with sequential fallback and request logging.

**Architecture:** Plugin-style adapter architecture where each provider is a separate adapter class extending a common base. The router finds adapters by model name and calls them sequentially for fallback. Configuration uses YAML files with environment variable overrides.

**Tech Stack:** FastAPI, httpx, pydantic, PyYAML, pytest

---

## Chunk 1: Project Scaffolding

### Task 1: Create pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write initial pyproject.toml**

```toml
[project]
name = "llm-api-proxy"
version = "0.1.0"
description = "Minimal LLM API proxy with OpenAI-compatible interface"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "httpx>=0.27.0",
    "pydantic>=2.9.0",
    "pyyaml>=6.0.0",
    "uvicorn>=0.30.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-httpserver>=1.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
```

- [ ] **Step 2: Install dependencies**

Run: `cd /Users/liu/Desktop/project/my_llm_api_server && uv sync`
Expected: Dependencies installed in `.venv/`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add project config with dependencies"
```

---

### Task 2: Create directory structure

**Files:**
- Create: `src/__init__.py`
- Create: `src/adapters/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/api/__init__.py`
- Create: `src/schemas/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/adapters/__init__.py`

- [ ] **Step 1: Create all directories and __init__.py files**

```bash
mkdir -p src/adapters src/core src/api src/schemas tests/adapters
touch src/__init__.py src/adapters/__init__.py src/core/__init__.py src/api/__init__.py src/schemas/__init__.py tests/__init__.py tests/adapters/__init__.py
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: add project directory structure"
```

---

### Task 3: Create config.yaml.example

**Files:**
- Create: `config.yaml.example`

- [ ] **Step 1: Write config.yaml.example**

```yaml
# LLM API Proxy Configuration
# Copy to config.yaml and fill in your API keys

# Server settings
host: "0.0.0.0"
port: 8000

# Adapters configuration
adapters:
  - name: "openai"
    api_key: "${OPENAI_API_KEY}"        # Set via environment variable
    base_url: "https://api.openai.com/v1"
    models:
      - "gpt-4o"
      - "gpt-4o-mini"
      - "gpt-4-turbo"
      - "gpt-3.5-turbo"

  - name: "gemini"
    api_key: "${GEMINI_API_KEY}"
    base_url: "https://generativelanguage.googleapis.com/v1beta"
    models:
      - "gemini-1.5-flash"
      - "gemini-1.5-pro"
      - "gemini-pro"

  - name: "qwen"
    api_key: "${QWEN_API_KEY}"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    models:
      - "qwen-turbo"
      - "qwen-plus"
      - "qwen-max"

# Fallback order (sequential, first available)
# Models map to adapters in order listed above
model_fallback:
  # For models not listed, try adapters in order
  default:
    - "openai"
    - "gemini"
    - "qwen"

# Logging
log_level: "INFO"
log_requests: true
```

- [ ] **Step 2: Commit**

```bash
git add config.yaml.example && git commit -m "feat: add config.yaml.example"
```

---

## Chunk 2: Core - Config Loader

### Task 4: Config Loader

**Files:**
- Create: `src/core/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_config.py
import os
import pytest
from src.core.config import Config, AdapterConfig, load_config


def test_adapter_config_from_dict():
    config = AdapterConfig(
        name="test",
        api_key="sk-test",
        base_url="https://api.test.com/v1",
        models=["model-a", "model-b"],
    )
    assert config.name == "test"
    assert config.api_key == "sk-test"
    assert "model-a" in config.models


def test_env_var_substitution():
    os.environ["TEST_API_KEY"] = "secret-123"
    os.environ["TEST_BASE_URL"] = "https://custom.test.com"
    
    config = AdapterConfig(
        name="test",
        api_key="${TEST_API_KEY}",
        base_url="${TEST_BASE_URL}",
        models=["model-a"],
    )
    
    assert config.api_key == "secret-123"
    assert config.base_url == "https://custom.test.com"


def test_config_loads_yaml():
    config = load_config("config.yaml.example")
    assert config.port == 8000
    assert len(config.adapters) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL - ModuleNotFoundError or test failure

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/config.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/config.py tests/test_config.py && git commit -m "feat: add config loader with YAML and env var support"
```

---

## Chunk 3: Core - Request Logging

### Task 5: Request Logger

**Files:**
- Create: `src/core/logging.py`
- Test: `tests/test_logging.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_logging.py
import pytest
from src.core.logging import RequestLog, RequestLogger


def test_request_log_captures_data():
    log = RequestLog(
        model="gpt-4o",
        provider="openai",
        tokens_used=100,
        tokens_completed=50,
        duration_ms=500,
        fallback_used=False,
        fallback_to=None,
        status="success",
        error_message=None,
    )
    assert log.model == "gpt-4o"
    assert log.tokens_used == 100


def test_request_logger_singleton():
    logger1 = RequestLogger()
    logger2 = RequestLogger()
    # Should be the same instance
    assert logger1 is logger2


def test_request_logger_records():
    logger = RequestLogger()
    logger.log(
        model="gpt-4o",
        provider="openai",
        tokens_used=100,
        tokens_completed=50,
        duration_ms=500,
    )
    
    logs = logger.get_logs()
    assert len(logs) == 1
    assert logs[0].model == "gpt-4o"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_logging.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/logging.py
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RequestLog:
    """Record of a single API request."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    model: str
    provider: str
    tokens_used: int = 0
    tokens_completed: int = 0
    duration_ms: int = 0
    fallback_used: bool = False
    fallback_to: Optional[str] = None
    status: str = "success"  # "success", "error", "fallback"
    error_message: Optional[str] = None


class RequestLogger:
    """Singleton logger for API requests."""
    
    _instance: Optional["RequestLogger"] = None
    _logs: list[RequestLog] = []
    
    def __new__(cls) -> "RequestLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logs = []
        return cls._instance
    
    def log(
        self,
        model: str,
        provider: str,
        tokens_used: int = 0,
        tokens_completed: int = 0,
        duration_ms: int = 0,
        fallback_used: bool = False,
        fallback_to: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """Log a request."""
        log_entry = RequestLog(
            model=model,
            provider=provider,
            tokens_used=tokens_used,
            tokens_completed=tokens_completed,
            duration_ms=duration_ms,
            fallback_used=fallback_used,
            fallback_to=fallback_to,
            status=status,
            error_message=error_message,
        )
        self._logs.append(log_entry)
        
        logger.info(
            f"[{provider}] {model} | "
            f"tokens: {tokens_used}/{tokens_completed} | "
            f"duration: {duration_ms}ms | "
            f"status: {status}"
            + (f" | fallback to {fallback_to}" if fallback_used else "")
        )
    
    def get_logs(self) -> list[RequestLog]:
        """Get all logged requests."""
        return self._logs.copy()
    
    def clear(self) -> None:
        """Clear all logs."""
        self._logs.clear()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_logging.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/logging.py tests/test_logging.py && git commit -m "feat: add request logger"
```

---

## Chunk 4: Adapters - Base Adapter

### Task 6: Base Adapter

**Files:**
- Create: `src/adapters/base.py`
- Test: `tests/adapters/test_base.py`

- [ ] **Step 1: Write failing test**

```python
# tests/adapters/test_base.py
import pytest
from src.adapters.base import BaseAdapter, AdapterError


def test_adapter_error_has_context():
    error = AdapterError("Connection failed", provider="openai")
    assert "Connection failed" in str(error)
    assert error.provider == "openai"


def test_base_adapter_interface():
    adapter = BaseAdapter(
        name="test",
        api_key="sk-test",
        base_url="https://api.test.com/v1",
        models=["model-a"],
    )
    assert adapter.name == "test"
    assert adapter.supports_model("model-a")
    assert not adapter.supports_model("model-b")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/adapters/test_base.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/adapters/base.py
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional

import httpx


class AdapterError(Exception):
    """Error raised by an adapter."""
    
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message)
        self.provider = provider


class BaseAdapter(ABC):
    """Base class for all LLM provider adapters."""
    
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        models: list[str],
    ):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.models = models
        self._client: Optional[httpx.AsyncClient] = None
    
    def supports_model(self, model: str) -> bool:
        """Check if this adapter supports the given model."""
        return model in self.models
    
    @abstractmethod
    async def chat_completions(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Call the chat completions API.
        
        Returns the raw httpx.Response so router can handle streaming.
        Raises AdapterError on failure.
        """
        pass
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/adapters/test_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/base.py tests/adapters/test_base.py && git commit -m "feat: add base adapter interface"
```

---

## Chunk 5: Adapters - OpenAI Compatible

### Task 7: OpenAI Adapter

**Files:**
- Create: `src/adapters/openai.py`
- Test: `tests/adapters/test_openai.py`

- [ ] **Step 1: Write failing test**

```python
# tests/adapters/test_openai.py
import pytest
from unittest.mock import AsyncMock, patch
from src.adapters.openai import OpenAIAdapter
from src.adapters.base import AdapterError


@pytest.fixture
def adapter():
    return OpenAIAdapter(
        name="openai",
        api_key="sk-test",
        base_url="https://api.openai.com/v1",
        models=["gpt-4o", "gpt-3.5-turbo"],
    )


def test_supports_openai_models(adapter):
    assert adapter.supports_model("gpt-4o")
    assert adapter.supports_model("gpt-3.5-turbo")
    assert not adapter.supports_model("gemini-1.5-flash")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/adapters/test_openai.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/adapters/openai.py
from typing import Any

import httpx

from src.adapters.base import BaseAdapter, AdapterError


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI-compatible API providers."""
    
    async def chat_completions(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Call OpenAI-compatible chat completions API."""
        client = await self._get_client()
        
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
                f"OpenAI API error: {e.response.status_code} - {e.response.text}",
                provider=self.name,
            )
        except httpx.RequestError as e:
            raise AdapterError(
                f"Request failed: {e}",
                provider=self.name,
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/adapters/test_openai.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/openai.py tests/adapters/test_openai.py && git commit -m "feat: add OpenAI adapter"
```

---

## Chunk 6: Adapters - Gemini

### Task 8: Gemini Adapter

**Files:**
- Create: `src/adapters/gemini.py`
- Test: `tests/adapters/test_gemini.py`

- [ ] **Step 1: Write failing test**

```python
# tests/adapters/test_gemini.py
import pytest
from src.adapters.gemini import GeminiAdapter


def test_supports_gemini_models():
    adapter = GeminiAdapter(
        name="gemini",
        api_key="test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        models=["gemini-1.5-flash", "gemini-pro"],
    )
    assert adapter.supports_model("gemini-1.5-flash")
    assert adapter.supports_model("gemini-pro")
    assert not adapter.supports_model("gpt-4o")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/adapters/test_gemini.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/adapters/gemini.py
from typing import Any

import httpx

from src.adapters.base import BaseAdapter, AdapterError


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini API."""
    
    async def chat_completions(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Call Gemini API with OpenAI-compatible interface."""
        client = await self._get_client()
        
        # Convert OpenAI format to Gemini format
        contents = self._convert_messages(messages)
        
        request_body = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.9),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            },
        }
        
        # Remove api key from URL for Gemini
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
    
    def _convert_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI message format to Gemini format."""
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            # Gemini only supports "user" and "model"
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/adapters/test_gemini.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/gemini.py tests/adapters/test_gemini.py && git commit -m "feat: add Gemini adapter"
```

---

## Chunk 7: Adapters - Qwen

### Task 9: Qwen Adapter

**Files:**
- Create: `src/adapters/qwen.py`
- Test: `tests/adapters/test_qwen.py`

- [ ] **Step 1: Write failing test**

```python
# tests/adapters/test_qwen.py
import pytest
from src.adapters.qwen import QwenAdapter


def test_supports_qwen_models():
    adapter = QwenAdapter(
        name="qwen",
        api_key="test-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        models=["qwen-turbo", "qwen-plus"],
    )
    assert adapter.supports_model("qwen-turbo")
    assert adapter.supports_model("qwen-plus")
    assert not adapter.supports_model("gpt-4o")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/adapters/test_qwen.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/adapters/qwen.py
from typing import Any

import httpx

from src.adapters.base import BaseAdapter, AdapterError


class QwenAdapter(BaseAdapter):
    """Adapter for Alibaba Qwen (DashScope) API."""
    
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/adapters/test_qwen.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/qwen.py tests/adapters/test_qwen.py && git commit -m "feat: add Qwen adapter"
```

---

## Chunk 8: Core - Router with Fallback

### Task 10: Router with Sequential Fallback

**Files:**
- Create: `src/core/router.py`
- Test: `tests/test_router.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_router.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.router import Router, RouterError
from src.core.config import Config, AdapterConfig
from src.adapters.base import AdapterError


@pytest.fixture
def config():
    return Config(
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o"],
            ),
            AdapterConfig(
                name="gemini",
                api_key="test-key",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-flash"],
            ),
        ]
    )


def test_find_adapters_for_model(config):
    router = Router(config)
    
    # gpt-4o should use openai adapter
    adapters = router.find_adapters("gpt-4o")
    assert len(adapters) >= 1
    assert adapters[0].name == "openai"


def test_find_adapters_unknown_model(config):
    router = Router(config)
    
    # Unknown model should return empty
    adapters = router.find_adapters("unknown-model")
    assert len(adapters) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_router.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/router.py
import time
from typing import Any

import httpx

from src.adapters.base import BaseAdapter, AdapterError
from src.adapters.openai import OpenAIAdapter
from src.adapters.gemini import GeminiAdapter
from src.adapters.qwen import QwenAdapter
from src.core.config import Config
from src.core.logging import RequestLogger


ADAPTER_CLASSES = {
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "qwen": QwenAdapter,
}


class RouterError(Exception):
    """Error raised when routing fails."""
    pass


class Router:
    """Routes requests to appropriate adapters with fallback support."""
    
    def __init__(self, config: Config):
        self.config = config
        self._adapters: dict[str, BaseAdapter] = {}
        self._logger = RequestLogger()
        self._init_adapters()
    
    def _init_adapters(self) -> None:
        """Initialize all configured adapters."""
        for adapter_config in self.config.adapters:
            adapter_class = ADAPTER_CLASSES.get(adapter_config.name)
            if adapter_class is None:
                continue
            
            adapter = adapter_class(
                name=adapter_config.name,
                api_key=adapter_config.api_key,
                base_url=adapter_config.base_url,
                models=adapter_config.models,
            )
            self._adapters[adapter_config.name] = adapter
    
    def find_adapters(self, model: str) -> list[BaseAdapter]:
        """Find all adapters that support the given model, in fallback order."""
        result = []
        
        for adapter_config in self.config.adapters:
            adapter = self._adapters.get(adapter_config.name)
            if adapter and adapter.supports_model(model):
                result.append(adapter)
        
        return result
    
    async def route(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Route request to appropriate adapter with sequential fallback.
        
        Tries adapters in order until one succeeds.
        """
        adapters = self.find_adapters(model)
        
        if not adapters:
            raise RouterError(f"No adapter found for model: {model}")
        
        last_error: AdapterError | None = None
        
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
                
                # Extract usage if available
                tokens_used = 0
                tokens_completed = 0
                try:
                    data = response.json()
                    usage = data.get("usage", {})
                    tokens_used = usage.get("prompt_tokens", 0)
                    tokens_completed = usage.get("completion_tokens", 0)
                except Exception:
                    pass
                
                # Log successful request
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
        """Close all adapter connections."""
        for adapter in self._adapters.values():
            await adapter.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_router.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/router.py tests/test_router.py && git commit -m "feat: add router with sequential fallback"
```

---

## Chunk 9: Core - Health Check

### Task 11: Health Check

**Files:**
- Create: `src/core/health.py`
- Test: `tests/test_health.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_health.py
import pytest
from src.core.health import HealthChecker
from src.core.config import Config, AdapterConfig


@pytest.fixture
def config():
    return Config(
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o"],
            ),
        ]
    )


def test_health_checker_init(config):
    checker = HealthChecker(config)
    assert len(checker.adapters) == 1
    assert checker.adapters[0].name == "openai"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/health.py
from typing import Any

import httpx

from src.core.config import Config, AdapterConfig
from src.adapters.base import BaseAdapter


class HealthStatus:
    """Health status for an adapter."""
    
    def __init__(
        self,
        adapter_name: str,
        healthy: bool,
        latency_ms: int = 0,
        error: str | None = None,
    ):
        self.adapter_name = adapter_name
        self.healthy = healthy
        self.latency_ms = latency_ms
        self.error = error


class HealthChecker:
    """Manually trigger health checks on adapters."""
    
    def __init__(self, config: Config):
        self.config = config
        self.adapters: list[BaseAdapter] = []
        self._init_adapters()
    
    def _init_adapters(self) -> None:
        """Initialize adapters from config."""
        from src.adapters.openai import OpenAIAdapter
        from src.adapters.gemini import GeminiAdapter
        from src.adapters.qwen import QwenAdapter
        
        ADAPTER_CLASSES = {
            "openai": OpenAIAdapter,
            "gemini": GeminiAdapter,
            "qwen": QwenAdapter,
        }
        
        for adapter_config in self.config.adapters:
            adapter_class = ADAPTER_CLASSES.get(adapter_config.name)
            if adapter_class is None:
                continue
            
            adapter = adapter_class(
                name=adapter_config.name,
                api_key=adapter_config.api_key,
                base_url=adapter_config.base_url,
                models=adapter_config.models,
            )
            self.adapters.append(adapter)
    
    async def check_adapter(self, adapter: BaseAdapter) -> HealthStatus:
        """Check health of a single adapter with a simple API call."""
        import time
        
        start_time = time.time()
        
        try:
            client = await adapter._get_client()
            
            # Use models list endpoint if available, otherwise do a minimal completion
            test_messages = [{"role": "user", "content": "Hi"}]
            
            response = await adapter.chat_completions(
                messages=test_messages,
                model=adapter.models[0] if adapter.models else "",
                stream=False,
                max_tokens=1,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return HealthStatus(
                adapter_name=adapter.name,
                healthy=response.status_code == 200,
                latency_ms=latency_ms,
                error=None,
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return HealthStatus(
                adapter_name=adapter.name,
                healthy=False,
                latency_ms=latency_ms,
                error=str(e),
            )
    
    async def check_all(self) -> list[HealthStatus]:
        """Check health of all configured adapters."""
        import asyncio
        
        tasks = [self.check_adapter(adapter) for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        statuses = []
        for result in results:
            if isinstance(result, Exception):
                statuses.append(HealthStatus(
                    adapter_name="unknown",
                    healthy=False,
                    error=str(result),
                ))
            else:
                statuses.append(result)
        
        return statuses
    
    async def close(self) -> None:
        """Close all adapter connections."""
        for adapter in self.adapters:
            await adapter.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/health.py tests/test_health.py && git commit -m "feat: add manual health checker"
```

---

## Chunk 10: API Routes

### Task 12: FastAPI Routes

**Files:**
- Create: `src/schemas/requests.py`
- Create: `src/api/routes.py`
- Create: `src/api/main.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/schemas/requests.py
from typing import Any, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = Field(..., description="Model name")
    messages: list[Message] = Field(..., description="Chat messages")
    stream: bool = Field(default=False, description="Stream responses")
    temperature: Optional[float] = Field(default=0.9, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2, le=2)
    presence_penalty: Optional[float] = Field(default=None, ge=-2, le=2)
    stop: Optional[list[str]] = Field(default=None)
```

```python
# src/api/routes.py
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from src.core.router import Router, RouterError
from src.core.health import HealthChecker
from src.core.logging import RequestLogger
from src.schemas.requests import ChatCompletionRequest


router = APIRouter()


# Global router instance (initialized in main.py)
_router: Router | None = None
_health_checker: HealthChecker | None = None


def set_router(router: Router) -> None:
    global _router
    _router = router


def set_health_checker(health_checker: HealthChecker) -> None:
    global _health_checker
    _health_checker = health_checker


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Response:
    """OpenAI-compatible chat completions endpoint."""
    if _router is None:
        raise HTTPException(status_code=500, detail="Router not initialized")
    
    messages = [msg.model_dump() for msg in request.messages]
    
    try:
        response = await _router.route(
            messages=messages,
            model=request.model,
            stream=request.stream,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop,
        )
        
        # Return streaming or non-streaming response
        if request.stream:
            return StreamingResponse(
                response.aiter_bytes(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
        else:
            return Response(
                content=response.content,
                media_type="application/json",
            )
    except RouterError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/health")
async def health() -> dict[str, Any]:
    """Manual health check endpoint."""
    if _health_checker is None:
        return {"status": "ok", "adapters": []}
    
    statuses = await _health_checker.check_all()
    
    return {
        "status": "ok" if all(s.healthy for s in statuses) else "degraded",
        "adapters": [
            {
                "name": s.adapter_name,
                "healthy": s.healthy,
                "latency_ms": s.latency_ms,
                "error": s.error,
            }
            for s in statuses
        ],
    }


@router.get("/logs")
async def get_logs() -> dict[str, Any]:
    """Get request logs."""
    logger = RequestLogger()
    logs = logger.get_logs()
    
    return {
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "model": log.model,
                "provider": log.provider,
                "tokens_used": log.tokens_used,
                "tokens_completed": log.tokens_completed,
                "duration_ms": log.duration_ms,
                "fallback_used": log.fallback_used,
                "status": log.status,
                "error": log.error_message,
            }
            for log in logs
        ]
    }


@router.post("/logs/clear")
async def clear_logs() -> dict[str, str]:
    """Clear request logs."""
    logger = RequestLogger()
    logger.clear()
    return {"status": "ok"}
```

```python
# src/api/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import load_config
from src.core.router import Router
from src.core.health import HealthChecker
from src.api.routes import router, set_router, set_health_checker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    # Load config
    config = load_config("config.yaml")
    
    # Initialize router and health checker
    router = Router(config)
    health_checker = HealthChecker(config)
    
    set_router(router)
    set_health_checker(health_checker)
    
    logger.info(f"Initialized with {len(config.adapters)} adapters")
    
    yield
    
    # Cleanup
    await router.close()
    await health_checker.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="LLM API Proxy",
    description="Minimal LLM API proxy with OpenAI-compatible interface",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/schemas/requests.py src/api/routes.py src/api/main.py tests/test_api.py && git commit -m "feat: add FastAPI routes"
```

---

## Chunk 11: Integration Tests

### Task 13: Integration Tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_end_to_end.py`

- [ ] **Step 1: Write conftest.py**

```python
# tests/conftest.py
import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    from src.core.config import Config, AdapterConfig
    
    return Config(
        host="0.0.0.0",
        port=8000,
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o", "gpt-3.5-turbo"],
            ),
            AdapterConfig(
                name="gemini",
                api_key="test-key",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-flash"],
            ),
        ],
        log_level="INFO",
        log_requests=True,
    )
```

```python
# tests/integration/__init__.py
```

- [ ] **Step 2: Write end-to-end test**

```python
# tests/integration/test_end_to_end.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.router import Router
from src.core.config import Config, AdapterConfig
from src.adapters.base import AdapterError


@pytest.fixture
def config():
    return Config(
        adapters=[
            AdapterConfig(
                name="openai",
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o"],
            ),
            AdapterConfig(
                name="gemini",
                api_key="test-key",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-flash"],
            ),
        ]
    )


@pytest.mark.asyncio
async def test_successful_request(config):
    """Test successful request through router."""
    router = Router(config)
    
    # Mock the adapter's chat_completions method
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    mock_response.aiter_bytes = AsyncMock(return_value=iter(b'{"choices": []}'))
    
    async def mock_chat(*args, **kwargs):
        return mock_response
    
    router._adapters["openai"].chat_completions = mock_chat
    
    response = await router.route(
        messages=[{"role": "user", "content": "Hi"}],
        model="gpt-4o",
    )
    
    assert response.status_code == 200
    await router.close()


@pytest.mark.asyncio
async def test_fallback_on_failure(config):
    """Test fallback to second adapter when first fails."""
    router = Router(config)
    
    # First adapter fails
    async def fail_first(*args, **kwargs):
        raise AdapterError("Service unavailable", provider="openai")
    
    # Second adapter succeeds
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Hello from Gemini!"}]
            }
        }]
    }
    mock_response.aiter_bytes = AsyncMock(return_value=iter(b'{}'))
    
    async def succeed_second(*args, **kwargs):
        return mock_response
    
    router._adapters["openai"].chat_completions = fail_first
    router._adapters["gemini"].chat_completions = succeed_second
    
    response = await router.route(
        messages=[{"role": "user", "content": "Hi"}],
        model="gemini-1.5-flash",
    )
    
    assert response.status_code == 200
    
    # Check logs show fallback
    logs = router._logger.get_logs()
    assert len(logs) == 2  # One failed, one succeeded
    assert logs[0].status == "error"
    assert logs[1].status == "success"
    assert logs[1].fallback_used is True
    
    await router.close()


@pytest.mark.asyncio
async def test_no_adapter_found(config):
    """Test error when no adapter supports the model."""
    router = Router(config)
    
    with pytest.raises(Exception) as exc_info:
        await router.route(
            messages=[{"role": "user", "content": "Hi"}],
            model="unknown-model",
        )
    
    assert "No adapter found" in str(exc_info.value)
    await router.close()
```

- [ ] **Step 2: Run integration tests**

Run: `pytest tests/integration/ -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py tests/integration/ && git commit -m "test: add integration tests"
```

---

## Chunk 12: Final Verification

### Task 14: Run All Tests

- [ ] **Step 1: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

- [ ] **Step 2: Run linting**

Run: `ruff check src/ tests/`
Expected: No errors

- [ ] **Step 3: Run type checking**

Run: `mypy src/`
Expected: No errors

---

### Task 15: Add README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

```markdown
# LLM API Proxy

A minimal Python reverse proxy that unifies multiple LLM API providers under a single OpenAI-compatible interface.

## Features

- OpenAI-compatible API (`/v1/chat/completions`)
- Sequential fallback: automatically tries next provider if one fails
- Manual health check endpoint
- Request logging with metrics

## Supported Providers

- OpenAI (GPT-4o, GPT-3.5-turbo)
- Google Gemini (gemini-1.5-flash, gemini-1.5-pro)
- Alibaba Qwen (qwen-turbo, qwen-plus)

## Quick Start

1. Copy config and fill in API keys:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your API keys
   ```

2. Run the server:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

3. Test with curl:
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-4o",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | OpenAI-compatible chat completions |
| `/health` | GET | Manual health check for all adapters |
| `/logs` | GET | View request logs |
| `/logs/clear` | POST | Clear request logs |

## Configuration

See `config.yaml.example` for all options. Environment variables can override config values using `${VAR_NAME}` syntax.

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md && git commit -m "docs: add README"
```

---

**Plan complete and saved to `docs/superpowers/plans/`. Ready to execute?**
