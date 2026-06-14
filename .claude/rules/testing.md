---
paths:
  - "tests/**/*"
  - "**/test_*.py"
  - "**/*_test.py"
---

# Testing rules

- Add or update tests with every behavior change.
- Never delete or skip a failing test just to make the suite pass.
- Unit tests live in `tests/unit/`, integration tests in `tests/integration/`.
- A change is done only when relevant tests, lint, and type checks pass.
