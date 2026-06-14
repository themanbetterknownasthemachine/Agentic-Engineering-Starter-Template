# Security rules

- IMPORTANT: never read, print, or commit `.env`, `*.p8`, or any credentials.
- No secrets in `.mcp.json`, settings, skills, or code. Reference env vars instead.
- Never run DROP, DELETE, or TRUNCATE against Snowflake without explicit approval.
- Do not push or merge unless explicitly requested.
- Mark generated files clearly so they are never mistaken for source.

Note: these are context. The hard blocks are enforced in
`.claude/settings.json` (permissions.deny) and `.claude/hooks/protect-files.sh`.
