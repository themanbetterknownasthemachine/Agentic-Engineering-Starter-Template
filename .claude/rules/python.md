---
paths:
  - "**/*.py"
---

# Python / forecasting rules

- Python 3.12, dependencies via uv. Format/lint with Ruff, type-check with mypy.
- Forecasting: no feature leakage. Never use features unknown at prediction time.
- Half-days (IS_HALBTAG) are statistically fragile (very few training rows):
  always sanity-check sign and magnitude of coefficients, never trust them blindly.
- Before deploying a forecast, the holdout must pass `python eval/eval_forecast.py`.
- Prefer pandas/numpy vectorization; keep functions small and testable.
