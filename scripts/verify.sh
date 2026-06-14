#!/usr/bin/env bash
# Fuehrt alle Pruefungen aus: lint, tests, forecast-eval. Exit != 0 wenn etwas fehlschlaegt.
set -euo pipefail
bash scripts/lint.sh
bash scripts/test.sh
# Forecast-Eval nur, wenn ein Holdout existiert:
if ls holdout*.parquet >/dev/null 2>&1; then
  python eval/eval_forecast.py --holdout "$(ls holdout*.parquet | head -n1)"
fi
echo "Alle Pruefungen durch."
