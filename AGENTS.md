# Agent Guidelines for my-llm-api-proxy

## Project Overview

A minimal Python reverse proxy that unifies multiple LLM API providers (OpenAI, Gemini, Qwen) under a single OpenAI-compatible interface with sequential fallback support.

## Development Environment

### Python Version
- Minimum: Python 3.9+
- Target: Python 3.11
- Note: Uses `from __future__ import annotations` for compatibility

### Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"  # Install with dev dependencies

# Run tests
pytest -v                           # All tests
pytest tests/path/test_file.py      # Single test file
pytest tests/path/test_file.py::test_name  # Single test

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Code Style

### Formatting & Linting
- Line length: 100 characters
- Use `ruff check` for linting (enforces pycodestyle, pyflakes, isort, and more)
- Format imports with ruff or isort (stdlib → third-party → local)

### Type Annotations
- Use `from __future__ import annotations` for forward references
- Use `Optional[X]` instead of `X | None` for Python 3.9 compatibility
- Use `List[X]`, `Dict[X, Y]` instead of `list[X]`, `dict[X, Y]` for Python 3.9
- Private attributes: `_name` (single underscore)
- Protected attributes: `__name` (double underscore)

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | lowercase | `config.py` |
| Classes | PascalCase | `BaseAdapter` |
| Functions | snake_case | `load_config` |
| Variables | snake_case | `api_key` |
| Constants | UPPER_SNAKE | `ADAPTER_CLASSES` |
| Private | _prefix | `_client` |

### Imports Order
```python
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

import httpx
import yaml

from src.adapters.base import BaseAdapter, AdapterError
from src.core.config import Config
```

## Project Structure

```
src/
├── adapters/          # Provider adapters
│   ├── base.py      # BaseAdapter ABC, AdapterError
│   ├── openai.py    # OpenAI-compatible adapter
│   ├── gemini.py    # Google Gemini adapter
│   └── qwen.py     # Alibaba Qwen adapter
├── core/            # Core functionality
│   ├── config.py    # YAML config loader
│   ├── router.py    # Request routing + fallback
│   ├── health.py    # Health checker
│   └── logging.py   # Request logger (singleton)
├── api/             # FastAPI routes
│   ├── main.py      # App entry point
│   └── routes.py    # API endpoints
└── schemas/          # Pydantic models
    └── requests.py  # Request validation

tests/
├── adapters/        # Adapter unit tests
├── integration/     # Integration tests
└── test_*.py       # Core component tests
```

## Key Patterns

### Adding a New Adapter
1. Create `src/adapters/<name>.py` inheriting from `BaseAdapter`
2. Implement `chat_completions()` method
3. Add to `ADAPTER_CLASSES` dict in `router.py`
4. Add model names to `config.yaml.example`

```python
from src.adapters.base import BaseAdapter, AdapterError

class NewAdapter(BaseAdapter):
    def __init__(self, name, api_key, base_url, models=None):
        super().__init__(name, api_key, base_url, models)

    async def chat_completions(self, messages, model, stream=False, **kwargs):
        # Implementation
        pass
```

### Error Handling
- Use custom exception classes: `AdapterError`, `RouterError`
- Catch `httpx.HTTPStatusError` and `httpx.RequestError`
- Always raise `AdapterError` with `provider` context

```python
try:
    response = await client.post(url, json=data)
    response.raise_for_status()
    return response
except httpx.HTTPStatusError as e:
    raise AdapterError(
        f"API error: {e.response.status_code}",
        provider=self.name
    )
```

### Async/Await
- Use `async def` for all public adapter methods
- Always `await` async client calls
- Close clients in `close()` method

```python
async def _get_client(self) -> httpx.AsyncClient:
    if self._client is None:
        self._client = httpx.AsyncClient(timeout=60.0)
    return self._client

async def close(self) -> None:
    if self._client is not None:
        await self._client.aclose()
        self._client = None
```

## Testing Guidelines

- Use pytest with `pytest-asyncio` for async tests
- Mock external HTTP calls in unit tests
- Use `MagicMock` and `AsyncMock` from unittest.mock
- Always call `await router.close()` in tests to cleanup

```python
@pytest.mark.asyncio
async def test_example():
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Test implementation
    await router.close()
```

## Configuration

- YAML-based config with environment variable substitution: `${VAR_NAME}`
- See `config.yaml.example` for structure
- Use `load_config()` function to load configuration

## CI/CD

GitHub Actions runs on every push to main and PRs:
- Python 3.11
- pytest, ruff, mypy
- See `.github/workflows/ci.yml`
