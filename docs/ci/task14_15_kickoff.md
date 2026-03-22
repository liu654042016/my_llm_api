CI Kickoff Plan for Task 14-15
- Objective: Validate final verification workflow by running tests, lint, and type checks via CI.
- Prereqs: Ensure a git remote exists and the repository is accessible.
- Steps:
 1) Create and switch to feature branch:
   - git checkout -b feat/ci-task14-15
 2) Push & PR:
   - git push -u origin feat/ci-task14-15
   - Open PR: feat/ci-task14-15 -> main
 3) CI Verification:
   - Monitor GitHub Actions job for test, lint, and type-check checks.
   - If all pass: status DONE on all checks.
   - If any fail: patch the relevant tests or typing, push, and re-run CI.
 4) Local verification (optional):
   - bootstrap_env + make test && make lint && make typecheck
- Notes: This is a planning document to be executed in CI-enabled environments.
