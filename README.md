# BIDA Claude Code Projekt-Template

Ein push-fertiges Skelett, um ein neues Projekt so aufzusetzen, dass du Claude Code (Agentic
Engineering) optimal nutzen kannst. Es folgt einer sauberen, konventionellen Softwarestruktur
und ergänzt sie um den `.claude`-Ordner mit Kontext, Regeln, Skills, Subagents und Leitplanken.

## Pro Projekt anpassen (Checkliste)

Beim Start eines neuen Projekts nur diese Dateien anfassen, der Rest des Skeletts bleibt unverändert:

- [ ] **CLAUDE.md**: `<PROJECT_NAME>` und Beschreibung ersetzen, Stack, Schemas, Rollen und Quality-Bar anpassen
- [ ] **.env**: aus `.env.example` kopieren und Werte eintragen (wird nie committet)
- [ ] **.mcp.json**: Platzhalter `REPLACE_WITH_YOUR_SNOWFLAKE_MCP_COMMAND` durch den echten Snowflake-MCP-Befehl ersetzen
- [ ] **README.md / docs/architecture.md**: optional an das konkrete Projekt anpassen

Unverändert bleiben: `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`, `.claude/settings.json`, `scripts/` und `.gitignore`.

## Einmalige Einrichtung (nur einmal pro Template-Repo)

Das macht eine Person einmalig, danach nie wieder:

1. Dieses Template einmal nach GitHub pushen.
2. Im Repo unter Settings die Option "Template repository" aktivieren.

Danach steht das Repo allen im Team als Vorlage zur Verfügung. Beim Anlegen oder Klonen eines
konkreten Projekts ist dieser Schritt nicht mehr nötig.

## Neues Projekt starten

Das machst du (oder ein Teammitglied) bei jedem neuen Projekt:

1. Auf GitHub oben rechts "Use this template" klicken, ein neues Repo anlegen und klonen.
   (Ohne GitHub: den Template-Ordner kopieren und umbenennen.)
2. Die vier Dateien aus der Checkliste oben anpassen: `CLAUDE.md` (Pfadspezifisches nach
   `.claude/rules/`), `.env` (aus `.env.example`), `.mcp.json` und optional `README.md` /
   `docs/architecture.md`.
3. `claude` im Projekt-Root starten. Mit `/memory` prüfen, welche Dateien geladen sind, und
   optional `/init` laufen lassen, um die `CLAUDE.md` aus dem echten Code zu verfeinern.
4. `/spec` laufen lassen, kleine abgegrenzte Spec nach `docs/specs/active/`.
5. `/criteria` laufen lassen, Definition of Done in `CLAUDE.md` übernehmen.
6. Verifier bauen (`eval/eval_forecast.py` oder dbt-Tests), bevor implementiert wird.
7. MCP und Wissensbasis anbinden; Permissions und Hooks sind bereits aktiv.

Einen vollständigen Beispiel-Durchlauf von der Spec bis zur produktiven View, inklusive einer
`/spec`-Session, einer Beispiel-Spec und einem Eval-Skript, findest du in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md).

## Struktur und was jeder Baustein tut

- **CLAUDE.md** - dauerhafter, immer gültiger Projektkontext. Wird bei jeder Session als
  Kontext geladen und überlebt `/compact`. Kurz halten (unter 200 Zeilen).
- **.claude/rules/** - modulare Regeln. Dateien mit `paths`-Frontmatter laden nur, wenn Claude
  an passenden Dateien arbeitet (spart Kontext); Dateien ohne `paths` laden immer. Hier:
  `sql.md` (dbt/SQL), `python.md` (Forecasting), `testing.md`, `security.md`.
- **.claude/skills/** - wiederholbare Abläufe, je mit `/name` aufrufbar oder vom Modell bei
  Bedarf genutzt. Hier: `spec` (Interview zum Spec bauen), `criteria` (Evaluationskriterien),
  `review` (zweites Modell als Kritiker).
- **.claude/agents/** - spezialisierte Subagents mit eingegrenzter Fähigkeit. `code-reviewer`
  und `security-reviewer` sind read-only (`tools: Read, Grep, Glob`), können also prüfen, aber
  nichts ändern. Subagents nutzen, um Fähigkeit einzugrenzen, nicht nur um zu parallelisieren.
- **.claude/settings.json** - Berechtigungen (allow/deny) und Hook-Konfiguration. Geteilt,
  wird committet.
- **.claude/hooks/** - Skripte für Lifecycle-Events. `protect-files.sh` ist ein PreToolUse-Hook,
  der `.env`, `*.p8` und `DROP/DELETE/TRUNCATE` hart blockt (Exit-Code 2). `validate-changes.sh`
  ist ein PostToolUse-Hook, der nach Edits Ruff bzw. sqlfluff laufen lässt.
- **.mcp.json** - geteilte MCP-Server (Snowflake, GitHub). Nur env-Referenzen, keine Secrets.
- **docs/** - `architecture.md`, `adr/` (Architecture Decision Records), `specs/active` und
  `specs/completed`, `runbooks/`.
- **eval/eval_forecast.py** - der maschinelle Verifier (MAPE/Bias/Plausibilität, Exit-Code als
  Reward-Signal).
- **scripts/** - `setup`, `lint`, `test`, `verify` als ausführbare Einstiegspunkte.

## Wichtig: Kontext gegen Durchsetzung

CLAUDE.md und Rules sind **Kontext**, keine erzwungene Konfiguration. Sie beeinflussen das
Verhalten, erzwingen es aber nicht. Was niemals passieren darf, gehört in eine **Deny-Permission**
in `settings.json` oder in einen **PreToolUse-Hook**. Genau das macht `protect-files.sh`.

## Secrets

Nie Secrets in `.mcp.json`, Settings, Skills oder Code. Immer env-Referenzen (`${VAR}`) und die
Werte in `.env` oder der Umgebung. `.gitignore` schützt `.env`, `*.p8` und `settings.local.json`.

## Hinweis zu persönlichen Einstellungen

- Für persönliche, nicht committete Anweisungen den Import aus dem Home-Verzeichnis nutzen
  (`@~/.claude/<datei>.md`). Das funktioniert auch über mehrere git worktrees; `CLAUDE.local.md`
  tut das nicht und gilt in einer Doku-Quelle als veraltet.
