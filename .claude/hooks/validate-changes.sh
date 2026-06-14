#!/usr/bin/env bash
# PostToolUse-Hook (Edit|Write): leichte Validierung nach Datei-Aenderungen. Nicht-blockierend.
file="$(python3 "$(dirname "$0")/_file.py")"
case "$file" in
  *.py)  command -v ruff >/dev/null 2>&1 && ruff check "$file" || true ;;
  *.sql) command -v sqlfluff >/dev/null 2>&1 && sqlfluff lint "$file" || true ;;
esac
exit 0
