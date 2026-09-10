#!/usr/bin/env bash
# PostToolUse-Hook (Edit|Write): Lint-Befunde nach Datei-Aenderungen an Claude zurueckgeben.
# Die Datei ist bereits geschrieben, blockiert wird nichts. Claude sieht die Befunde nur
# als JSON-Feld additionalContext auf stdout (Exit 0); reiner Text auf stdout oder
# stderr landet nur im Debug-Log.
# Linter-Konvention (Ruff, sqlfluff): Exit 1 = Befunde, Exit >= 2 = Werkzeugfehler.
# Werkzeugfehler (z. B. fehlendes dbt-Profil fuer den sqlfluff-Templater) sind kein
# Befund an der Datei und werden nicht zurueckgemeldet.

py_bin=""
for c in python3 python py; do
  if "$c" -c "" >/dev/null 2>&1; then
    py_bin="$c"
    break
  fi
done
[ -z "$py_bin" ] && exit 0

file="$("$py_bin" "$(dirname "$0")/_file.py")"
[ -z "$file" ] && exit 0

# Werkzeug im PATH oder in der Projekt-.venv (uv legt Ruff dort ab, nicht im PATH).
find_tool() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "$1"
    return
  fi
  root="${CLAUDE_PROJECT_DIR:-.}"
  for p in "$root/.venv/bin/$1" "$root/.venv/Scripts/$1.exe"; do
    if [ -x "$p" ]; then
      echo "$p"
      return
    fi
  done
}

case "$file" in
  *.py)  tool="$(find_tool ruff)";     args=(check --output-format concise) ;;
  *.sql) tool="$(find_tool sqlfluff)"; args=(lint) ;;
  *)     exit 0 ;;
esac
[ -z "$tool" ] && exit 0

out="$("$tool" "${args[@]}" "$file" 2>&1)"
rc=$?
if [ "$rc" -eq 1 ]; then
  printf 'Lint-Befunde in %s (bitte beheben):\n%s\n' "$file" "$out" | "$py_bin" -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": sys.stdin.read(),
}}))
'
fi
exit 0
