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
