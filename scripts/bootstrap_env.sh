#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Please install Python 3.x to continue." >&2
  exit 1
fi

echo "Installing dev dependencies..."
python3 -m pip install --upgrade pip
if [ -f requirements-dev.txt ]; then
  python3 -m pip install -r requirements-dev.txt
fi

echo "Bootstrap complete. You can now run: make test, make lint, make typecheck"
