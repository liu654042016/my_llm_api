.PHONY: test lint typecheck

test:
	@if ! command -v pytest >/dev/null 2>&1; then \
	  echo "pytest not found. Installing dev dependencies..."; \
	  if command -v python3 >/dev/null 2>&1; then \
	    python3 -m pip install --upgrade pip; \
	    if [ -f requirements-dev.txt ]; then python3 -m pip install -r requirements-dev.txt; fi; \
	  else \
	    echo "Python3 not found. Please install Python 3.x to continue."; \
	    exit 1; \
	  fi; \
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
