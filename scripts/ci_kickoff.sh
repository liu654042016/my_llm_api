#!/usr/bin/env bash
set -euo pipefail

echo "Starting CI kickoff for Task 14-15..."
echo "1) Create and switch to feature branch: git checkout -b feat/ci-task14-15"
echo "2) Push to remote and open PR against main to trigger GitHub Actions at .github/workflows/ci.yml"
echo "   git push -u origin feat/ci-task14-15"
echo "3) Open PR: feat/ci-task14-15 -> main"
echo ""
echo "Environment notes:" 
echo "- If a remote is not configured, add origin with your repo URL and push."
echo "- The CI job will run pytest -v, ruff, and mypy."
