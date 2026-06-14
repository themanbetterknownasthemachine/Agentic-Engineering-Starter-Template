import sys, json, re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

ti = data.get("tool_input", {})
hay = " ".join(str(v) for v in ti.values())

patterns = [
    (r"\.env(\b|$|/)", ".env-Dateien"),
    (r"\.p8\b", "Schluesseldateien (*.p8)"),
    (r"\bDROP\b", "DROP gegen Snowflake"),
    (r"\bDELETE\b", "DELETE gegen Snowflake"),
    (r"\bTRUNCATE\b", "TRUNCATE gegen Snowflake"),
]
for pat, label in patterns:
    if re.search(pat, hay, re.IGNORECASE):
        print(label)
        sys.exit(0)
