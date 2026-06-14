#!/usr/bin/env bash
set -euo pipefail
dbtf test || true
uv run pytest
