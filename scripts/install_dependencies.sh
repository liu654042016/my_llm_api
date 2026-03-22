#!/usr/bin/env bash
set -euo pipefail

echo "Attempting to install dependencies via uv sync..."

if command -v uv >/dev/null 2>&1; then
  uv sync
  echo "Dependency installation attempted via uv sync."
else
  echo "uv tool not found in environment. Please install dependencies manually in a virtual environment:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install fastapi>=0.115.0 httpx>=0.27.0 pydantic>=2.9.0 pyyaml>=6.0.0 uvicorn>=0.30.0 pytest>=8.0.0 pytest-asyncio>=0.24.0 pytest-httpserver>=1.0.0 ruff>=0.6.0 mypy>=1.11.0"
fi
