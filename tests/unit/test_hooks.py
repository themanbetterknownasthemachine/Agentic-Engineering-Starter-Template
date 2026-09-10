"""Tests fuer die Hooks unter .claude/hooks/ (Durchsetzung, siehe .claude/rules/security.md).

Hooks versagen still: blockt der Schutz-Hook nicht mehr oder erreicht Lint-Feedback
Claude nicht, merkt es niemand. Deshalb sind sie hier abgesichert. Die Shell-Tests
laufen nur, wenn bash verfuegbar ist (CI: immer; Windows: in Git Bash).
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"
BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="bash nicht verfuegbar")
# dieselbe Suche wie find_tool in validate-changes.sh
HAS_RUFF = shutil.which("ruff") is not None or any(
    (ROOT / ".venv" / p).exists() for p in ("bin/ruff", "Scripts/ruff.exe")
)
needs_ruff = pytest.mark.skipif(not HAS_RUFF, reason="ruff weder im PATH noch in .venv")

_spec = importlib.util.spec_from_file_location("hook_check", HOOKS / "_check.py")
assert _spec is not None and _spec.loader is not None
_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_check)
check = _check.check


@pytest.mark.parametrize(
    ("tool", "tool_input"),
    [
        ("Read", {"file_path": ".env"}),
        ("Edit", {"file_path": "C:/projekt/.env.local"}),
        ("Read", {"file_path": "keys/snowflake.p8"}),
        ("Bash", {"command": "cat .env"}),
        ("Bash", {"command": "snowsql -q 'DROP TABLE mart'"}),
        ("Bash", {"command": "dbtf run-operation truncate_stage"}),
        ("mcp__snowflake__run_snowflake_query", {"statement": "DELETE FROM mart WHERE 1=1"}),
        ("mcp__snowflake__run_snowflake_query", {"statement": "call truncate_stage()"}),
        ("mcp__snowflake__drop_object", {"object_type": "table", "name": "MART"}),
        ("mcp__github__delete_file", {"path": "README.md"}),
    ],
)
def test_blockt(tool: str, tool_input: dict) -> None:
    assert check(tool, tool_input) is not None


@pytest.mark.parametrize(
    ("tool", "tool_input"),
    [
        ("Read", {"file_path": ".env.example"}),
        ("Write", {"file_path": "docs/setup.md", "content": "cp .env.example .env"}),
        ("Bash", {"command": "grep -rn DROP models/"}),
        ("Bash", {"command": "uv run pytest"}),
        ("mcp__github__create_issue", {"title": "Dropdown im Filter", "body": "Zeilen deleted"}),
        ("mcp__snowflake__run_snowflake_query", {"statement": "select x from dropdown_werte"}),
    ],
)
def test_laesst_durch(tool: str, tool_input: dict) -> None:
    assert check(tool, tool_input) is None


def run_check(stdin: str) -> str:
    result = subprocess.run(
        [sys.executable, str(HOOKS / "_check.py")],
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.mark.parametrize(
    "payload",
    ["kein json", "[1, 2]", json.dumps({"tool_name": "Bash", "tool_input": ["ls"]})],
)
def test_unlesbares_payload_wird_geblockt(payload: str) -> None:
    assert run_check(payload) != ""


def test_harmloses_payload_liefert_keinen_grund() -> None:
    assert run_check(json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})) == ""


def run_hook(script: str, payload: str) -> subprocess.CompletedProcess[str]:
    assert BASH is not None
    env = {**os.environ, "CLAUDE_PROJECT_DIR": ROOT.as_posix()}
    return subprocess.run(
        [BASH, (HOOKS / script).as_posix()],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
    )


@needs_bash
def test_protect_files_blockt_mit_exit_2() -> None:
    result = run_hook(
        "protect-files.sh", json.dumps({"tool_name": "Read", "tool_input": {"file_path": ".env"}})
    )
    assert result.returncode == 2
    assert "Credential" in result.stderr


@needs_bash
def test_protect_files_blockt_unlesbares_payload() -> None:
    assert run_hook("protect-files.sh", "kein json").returncode == 2


@needs_bash
def test_protect_files_laesst_harmloses_durch() -> None:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
    assert run_hook("protect-files.sh", payload).returncode == 0


@needs_bash
@needs_ruff
def test_validate_changes_meldet_lint_befund_an_claude(tmp_path: Path) -> None:
    datei = tmp_path / "kaputt.py"
    datei.write_text("import os\n", encoding="utf-8")  # F401: ungenutzter Import
    result = run_hook(
        "validate-changes.sh", json.dumps({"tool_input": {"file_path": datei.as_posix()}})
    )
    assert result.returncode == 0
    ausgabe = json.loads(result.stdout)["hookSpecificOutput"]
    assert ausgabe["hookEventName"] == "PostToolUse"
    assert "F401" in ausgabe["additionalContext"]


@needs_bash
@needs_ruff
def test_validate_changes_schweigt_bei_sauberer_datei(tmp_path: Path) -> None:
    datei = tmp_path / "sauber.py"
    datei.write_text('print("ok")\n', encoding="utf-8")
    result = run_hook(
        "validate-changes.sh", json.dumps({"tool_input": {"file_path": datei.as_posix()}})
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
