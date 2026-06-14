#!/usr/bin/env bash
# PreToolUse-Hook: blockt gefaehrliche Operationen, egal was das Modell entscheidet.
# Eingerichtet in .claude/settings.json unter hooks.PreToolUse. Exit-Code 2 = blockieren.
reason="$(python3 "$(dirname "$0")/_check.py")"
if [ -n "$reason" ]; then
  echo "Blockiert durch protect-files.sh: ${reason} ist ohne explizite Freigabe gesperrt." >&2
  exit 2
fi
exit 0
