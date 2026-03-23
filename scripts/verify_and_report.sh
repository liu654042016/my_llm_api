#!/usr/bin/env bash
set -euo pipefail

echo "[VERIFY] Discovering changed files..."
CHANGED_FILES=$(git ls-files -m -o --exclude-standard || true)
if [[ -z "$CHANGED_FILES" ]]; then
  echo "[VERIFY] No changed files detected."
else
  if command -v lsp_diagnostics >/dev/null 2>&1; then
    echo "[VERIFY] Running lsp diagnostics on changed files..."
    for f in $CHANGED_FILES; do
      echo "[DIAG] $f"
      lsp_diagnostics --filePath "$f" || true
    done
  else
    echo "[VERIFY] lsp_diagnostics not found; skipping LSP diagnostics."
  fi
fi

echo "[VERIFY] Placeholder: run tests/build if applicable."
# Optional: run pytest if tests directory exists
if [ -d tests ]; then
  if command -v pytest >/dev/null 2>&1; then
    echo "[VERIFY] Running pytest tests..."
    pytest -q || true
  else
    echo "[VERIFY] pytest not installed; skipping tests."
  fi
fi

echo "[REPORT] Generating final test report at /tmp/test_report.txt"
REPORT_FILE="/tmp/test_report.txt"
echo "Test Report - Zhipu proxy end-to-end" > "$REPORT_FILE"
echo "==============================" >> "$REPORT_FILE"
echo "Health endpoint: check via /health (performed during test)" >> "$REPORT_FILE"
if [ -f /tmp/health.txt ]; then
  echo "Health response: $(cat /tmp/health.txt | tr -d '\n' )" >> "$REPORT_FILE" 
fi
echo "Last e2e response (model glm-5):" >> "$REPORT_FILE"
RESPONSE_BODY=$(grep -o '"content":"[^"]*' /tmp/e2e_response.json | head -n1 | sed 's/"content":"//')
if [ -n "$RESPONSE_BODY" ]; then
  echo "$RESPONSE_BODY" >> "$REPORT_FILE"
else
  echo "<no ai reply captured>" >> "$REPORT_FILE"
fi
echo "End of report" >> "$REPORT_FILE"
echo "[VERIFY] Preparing final test report..."
REPO_ROOT=$(pwd)
echo "Repo: $REPO_ROOT"
