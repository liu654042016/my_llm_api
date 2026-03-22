#!/usr/bin/env bash
set -euo pipefail

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest not found. Please install Python and pytest to run tests locally." >&2
  exit 1
fi

pytest -v
