.PHONY: test lint typecheck

test:
	@if ! command -v pytest >/dev/null 2>&1; then \
	  echo "pytest not found. Please install Python and pytest to run tests locally."; \
	  exit 1; \
	fi
	pytest -v

lint:
	if ! command -v ruff >/dev/null 2>&1; then \
  echo "ruff not found. Please install Python tooling to lint locally."; \
  exit 1; \
fi
	ruff check src/ tests/

typecheck:
	if ! command -v mypy >/dev/null 2>&1; then \
  echo "mypy not found. Please install Python typing tools to type-check locally."; \
  exit 1; \
fi
	mypy src/
