# Handbuch: Agentic Engineering Starter Template

Dieses Handbuch erklärt das komplette Template — Sinn, Aufbau und jede Datei. Es ist zum
**Durchlesen** gedacht (danach verstehst du, warum das Template so aussieht) und zum
**Nachschlagen** (Teil C ist eine Datei-für-Datei-Referenz).

Es ist bewusst **erklärend**, nicht befehlsgenau: konkrete Befehle, Platzhalterlisten und
Setup-Schritte stehen in ihren Quelldateien ([README](../README.md), [CLAUDE.md](../CLAUDE.md),
[WORKFLOW.md](WORKFLOW.md)) und werden hier verlinkt statt kopiert — so bleibt nur eine Stelle
pflegebedürftig.

**Lesereihenfolge, wenn du neu bist:** Teil A (Konzept) → Teil B (Lebenszyklus) → bei Bedarf in
Teil C nachschlagen.

---

## Inhalt

- [Teil A — Das Konzept](#teil-a--das-konzept)
- [Teil B — Der Lebenszyklus eines Projekts](#teil-b--der-lebenszyklus-eines-projekts)
- [Teil C — Vollständige Referenz: jeder Ordner, jede Datei](#teil-c--vollständige-referenz-jeder-ordner-jede-datei)
- [Teil D — Die drei Domänen im Vergleich](#teil-d--die-drei-domänen-im-vergleich)
- [Teil E — Das Sicherheitsmodell (zwei Schichten)](#teil-e--das-sicherheitsmodell-zwei-schichten)
- [Teil F — Nachschlagen: Wo finde ich was?](#teil-f--nachschlagen-wo-finde-ich-was)

---

## Teil A — Das Konzept

### Wozu das Template überhaupt?

Es ist ein **push-fertiges Projekt-Skelett**, das eine saubere, konventionelle Softwarestruktur
mit einem `.claude/`-Ordner kombiniert. Der `.claude/`-Ordner gibt Claude Code (dem Agenten)
von Anfang an Kontext, Regeln, wiederholbare Abläufe und harte Leitplanken. Das Ziel: Claude
**nicht blind drauflos coden lassen**, sondern die Zusammenarbeit sauber aufstellen.

Das Template ist die gemeinsame Grundlage für **jedes** BIDA-Projekt. Das ML-Methodenwissen
(wie man forecastet, klassifiziert, regressiert) lebt bewusst **nicht** hier, sondern im
separaten [BIDA-ML-Starter](https://github.com/themanbetterknownasthemachine/BIDA-ML-Starter)
und wird bei ML-Projektstart hineinkopiert (siehe [Teil D](#teil-d--die-drei-domänen-im-vergleich)).

### Die Grundidee in einem Satz

> Erst sagst **du**, was gebaut werden soll (Spec) und woran man Erfolg misst (Verifier) —
> dann baut **Claude** den Code in einer Schleife, bis das Erfolgssignal grün ist.

### Die Arbeitsteilung

Das ist das Herzstück. Alles im Template dient dieser Aufteilung:

| Der **Mensch** besitzt … | Der **Agent** besitzt … |
|---|---|
| **Die Spec** — was soll besser werden? | **Die Implementierung in der Schleife** — Code schreiben, testen, Fehler lesen, korrigieren, wiederholen |
| **Die finale Bewertung** — ist es wirklich deploy-reif? | |
| **Das Verständnis** — was passiert da fachlich? | |

Der Mensch delegiert die mühsame innere Schleife, behält aber Ziel, Urteil und Verständnis.
Ein grüner Metrik-Wert ist **nicht** automatisch deploy-reif — die fachliche Freigabe bleibt
beim Menschen.

### Der innere und der äußere Loop

- **Innerer Loop (Agent):** Code → Verifier ausführen → Exit-Code lesen → korrigieren →
  erneut. Der **Exit-Code des Verifiers ist das Reward-Signal**. Das ist der Teil, den du
  delegierst.
- **Äußerer Loop (Mensch):** Spec formulieren → Kriterien festlegen → Verifier bauen →
  delegieren → reviewen → freigeben → Loop schliessen (`/handover`). Das ist der Teil, den
  du behältst.

### Das zentrale mentale Modell: Kontext vs. Durchsetzung

Das musst du verinnerlicht haben, sonst missversteht man das halbe Template:

- **Kontext** (`CLAUDE.md`, `.claude/rules/`) *beeinflusst* Claudes Verhalten. Es ist ein
  starker Hinweis, aber **keine Garantie**. Ein Modell kann Kontext auch mal übergehen.
- **Durchsetzung** (`.claude/settings.json` `permissions.deny`, `.claude/hooks/`) *erzwingt*
  Verhalten technisch. Was **niemals** passieren darf (Secrets lesen, `DROP` ausführen),
  gehört hierhin — nicht in eine Regel-Datei.

Faustregel: *Konventionen und Wissen* → Kontext. *„Das darf auf keinen Fall"* → Durchsetzung.
Details in [Teil E](#teil-e--das-sicherheitsmodell-zwei-schichten).

### Kontext-Ökonomie: warum es Rules-Dateien gibt

Claudes Kontextfenster ist begrenzt und wertvoll. Deshalb ist Wissen gestaffelt:

- **`CLAUDE.md`** — immer geladen, überlebt `/compact`. Deshalb kurz halten (< 200 Zeilen).
- **`.claude/rules/*.md` mit `paths:`-Frontmatter** — laden **nur**, wenn Claude an passenden
  Dateien arbeitet. Die dbt-Regeln kosten keinen Kontext, solange du an Python arbeitest.
- **`.claude/rules/*.md` ohne `paths:`** — laden immer (z. B. `security.md`).
- **`.claude/skills/*/SKILL.md`** — laden erst, wenn der Skill aufgerufen wird (`/name`).

So sieht Claude genau das, was für die aktuelle Aufgabe relevant ist — nicht mehr.

### Drei Regeln für mehrstufige Arbeit

Sobald ein Vorhaben aus mehreren Schritten besteht (Laden, Transformieren, Prüfen, Ausliefern),
gelten drei Regeln. Sie sorgen dafür, dass das Ergebnis deterministische, nachvollziehbare
Software bleibt: Der Agent baut die Pipeline, er ist nicht selbst die Pipeline.

- **Code vor Agent** ([`CLAUDE.md`](../CLAUDE.md), nicht verhandelbare Regeln): Deterministische
  Schritte (Filtern, Dedupe, Joins, Normalisierung) gehören in Code, nie in einen Agent- oder
  LLM-Aufruf. Ein Modell nur dort, wo echtes Urteil nötig ist. Grund: Code liefert bei gleichem
  Input dieselbe Zahl, ein Modell nicht zwingend.
- **Node-Kontrakt** ([`/spec`](../.claude/skills/spec/SKILL.md), Schritt 4): Jeder Schritt hat
  genau eine Aufgabe, benannte Inputs, eine strukturierte Ausgabe und einen definierten
  Fehlerzustand. Dieselbe Idee wie die [Data Contracts](contracts/README.md), angewendet auf
  Prozessschritte statt auf Tabellen.
- **Fehlerpolitik je Task** ([`airflow.md`](../.claude/rules/airflow.md)): Jeder Task deklariert,
  was bei einem Fehler passiert: RETRY, FALLBACK, SKIP, REPAIR, ESCALATE oder STOP. Ein pauschales
  `retries=3` ist ein Default, keine Entscheidung. Der teure Fall ist ein Task, der technisch
  durchläuft, aber unplausible Zahlen liefert: Ein Retry liefert sie erneut aus, ESCALATE hält
  sie an. Das Beispiel-DAG [`example_dbt_daily.py`](../dags/example_dbt_daily.py) zeigt STOP,
  RETRY und ESCALATE.

---

## Teil B — Der Lebenszyklus eines Projekts

Chronologisch, von der leeren Vorlage bis zum geschlossenen Loop. Die befehlsgenaue Version
steht in der [README](../README.md) und dem durchgespielten Beispiel in [WORKFLOW.md](WORKFLOW.md);
hier geht es um den roten Faden und das *Warum*.

### Phase 0 — Einmalige Template-Einrichtung (einmal pro Template-Repo)

Eine Person pusht das Template nach GitHub und aktiviert unter Settings „Template repository".
Danach steht es dem ganzen Team als Vorlage zur Verfügung. Nie wieder nötig.

### Phase 1 — Neues Projekt anlegen

Auf GitHub „Use this template" → neues Repo → klonen. (Ohne GitHub: Ordner kopieren.) Du
startest mit der fertigen Struktur: `CLAUDE.md`, `.claude/`, `.mcp.json` sind schon da.

### Phase 2 — Domäne wählen

`bash scripts/init-domain.sh <ml|de|dwh>` entfernt die Ordner, die deine Domäne nicht braucht
(siehe [Teil D](#teil-d--die-drei-domänen-im-vergleich) und `docs/domain-setup/`). Für ML gibt
es zusätzlich `scripts/new-ml-project.sh`, das Phase 2–4 automatisiert und die Methoden-Skills
aus dem BIDA-ML-Starter zieht.

### Phase 3 — Kontext füllen (Projekt „bewohnbar" machen)

Nur wenige Dateien anfassen — der Rest des Skeletts bleibt unverändert. Der Setup-Wizard
`bash scripts/init-project.sh` fragt die Kernwerte ab, ersetzt die `<PLACEHOLDER>`, generiert
eine schlanke Projekt-README (statt des Template-Handbuchs) und entfernt das
Template-Einführungsmaterial unter `docs/rollout/`.
Danach `.env` aus `.env.example` anlegen und in `.mcp.json` den Snowflake-MCP-Befehl eintragen.

**Setup-Gate:** Solange die Markerdatei `.template` existiert, gilt das Repo als
unkonfiguriertes Template. `scripts/init-project.sh` entfernt sie; ab dann erzwingt
`scripts/check-template.sh`, dass keine `<PLACEHOLDER>` mehr offen sind. Das läuft auch in CI.

### Phase 4 — Der äußere Loop (die eigentliche Arbeit)

Diese Reihenfolge ist der Kern der Methode:

1. **`/spec`** — Claude interviewt dich und schreibt eine kleine, abgegrenzte Spec nach
   `docs/specs/active/`. *Du besitzt das Ziel.*
2. **`/criteria`** — legt die maschinell prüfbare Definition of Done fest, die in `CLAUDE.md`
   übernommen wird. *Erfolg muss messbar sein, bevor der Agent loslegt.*
3. **Verifier bauen** — **vor** der Implementierung. Beispiel aus `eval/examples/` nach
   `eval/eval_<thema>.py` kopieren und Schwellen setzen (Kontrakt: [eval/README.md](../eval/README.md)).
   Für DWH-Arbeit ist `dbtf test` der Verifier. *Das ist der Schritt, den die meisten
   überspringen — und genau der Hebel, der sicheres Delegieren erst möglich macht.*
4. **Delegieren (innerer Loop)** — „Lies Spec + Kriterien, baue es, iteriere bis
   `eval/eval_<thema>.py` grün ist." Claude schreibt, testet, korrigiert selbstständig.
5. **`/review`** — ein zweites Modell als Kritiker prüft gegen die Definition of Done
   (kein Rubber-Stamp). Zusätzlich die read-only Subagents `code-reviewer` /
   `security-reviewer` über den Diff laufen lassen.
6. **Freigabe & Deploy** — dein fachliches Urteil. Tests fangen das Mechanische, dein Urteil
   das Architektonische.
7. **`/handover`** — schließt den äußeren Loop: verschiebt die Spec nach
   `docs/specs/completed/` und schreibt eine kurze Übergabe-Zusammenfassung.

---

## Teil C — Vollständige Referenz: jeder Ordner, jede Datei

Hier kannst du gezielt nachschlagen. Gegliedert nach Funktionsbereich, nicht alphabetisch.

### C.1 — Projektkontext (Wurzelebene)

| Datei | Funktion |
|---|---|
| [`CLAUDE.md`](../CLAUDE.md) | **Dauerhafter Projektkontext**, bei jeder Session geladen, überlebt `/compact`. Enthält Betriebsprinzip, Technology, Architecture, Commands, die *nicht verhandelbaren Regeln* und die *Definition of Done*. Kurz halten (< 200 Zeilen). Enthält im ungefüllten Zustand `<PLACEHOLDER>`. |
| [`README.md`](../README.md) | Einstieg: Grundidee, Setup-Checkliste, „Neues Projekt starten", knappe Strukturübersicht. **Beim Projekt-Setup ersetzt der Wizard sie durch eine schlanke Projekt-README** (Titel, Beschreibung, Stack, Setup/Entwicklung, Links). |
| [`LICENSE`](../LICENSE) | Lizenz des Templates. |
| `.template` | **Marker-Datei.** Vorhanden = unkonfiguriertes Template (Platzhalter erlaubt). Wird von `init-project.sh` entfernt; danach erzwingt `check-template.sh` gefüllte Platzhalter. |

### C.2 — Der `.claude/`-Ordner (das Herzstück)

Hier lebt alles, was Claude Code steuert.

#### `.claude/rules/` — modulare Konventionen (Kontext)

Regeln laden path-gebunden (siehe [Kontext-Ökonomie](#kontext-ökonomie-warum-es-rules-dateien-gibt)).
Frontmatter `paths:` steuert, wann eine Regel geladen wird.

| Datei | Lädt bei … | Inhalt |
|---|---|---|
| [`security.md`](../.claude/rules/security.md) | **immer** (kein `paths:`) | Secret-Handhabung, kein destruktives SQL ohne Freigabe, kein Push/Merge ungefragt. Erklärt zusätzlich das **zweischichtige Enforcement** (siehe Teil E). |
| [`python.md`](../.claude/rules/python.md) | Python-Dateien | Python 3.12, uv, Ruff, mypy, Vektorisierung, keine I/O beim Import, Config über Env-Vars. |
| [`dbt-snowflake.md`](../.claude/rules/dbt-snowflake.md) | `models/**`, `macros/**`, `seeds/**`, `snapshots/**`, `dbt_project.yml`, `packages.yml` | dbt-Namenskonventionen, kein `SELECT *`, Tests auf Keys, `dbtf`-Wrapper, Key-Pair-Auth, DIM_DATE/`AT=1`, `COPY INTO`. |
| [`oracle.md`](../.claude/rules/oracle.md) | `oracle/**` | Oracle-SQL/PL-SQL-Dialekt. Snowflake-Konventionen gelten hier **nicht**. Format-Masken, Bind-Variablen, ANSI-Joins. |
| [`airflow.md`](../.claude/rules/airflow.md) | `dags/**` | Idempotenz, Backfill-Sicherheit, keine Top-Level-Berechnung, explizite Retries/`catchup`, keine Secrets im DAG. Fehlerpolitik je Task (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP). |
| [`forecasting.md`](../.claude/rules/forecasting.md) | `src/forecast/**`, `eval/**` | Kein Feature-Leakage, Halbtage-Fragilität, deterministische Verifier (Seeds fixieren), keine negativen Mengen, robuste Metriken. |
| [`testing.md`](../.claude/rules/testing.md) | Test-Dateien | Tests mit jeder Verhaltensänderung, keine roten Tests löschen, Struktur `tests/unit` vs. `tests/integration`. |

#### `.claude/skills/` — wiederholbare Abläufe

Jeder Skill ist per `/name` aufrufbar oder wird vom Modell bei Bedarf genutzt. Aufbau: ein
Ordner pro Skill mit `SKILL.md` (Frontmatter `name` + `description`).

| Skill | Aufruf | Funktion |
|---|---|---|
| [`spec`](../.claude/skills/spec/SKILL.md) | `/spec` | Interviewt dich und schreibt eine kleine Spec nach `docs/specs/active/<thema>.md`. Bei mehrstufiger Arbeit mit Node-Kontrakt je Schritt. |
| [`criteria`](../.claude/skills/criteria/SKILL.md) | `/criteria` | Legt maschinell prüfbare Evaluationskriterien fest → Definition of Done in `CLAUDE.md`. |
| [`review`](../.claude/skills/review/SKILL.md) | `/review` | Zweites Modell als Kritiker gegen die Definition of Done. Kein Rubber-Stamp. |
| [`handover`](../.claude/skills/handover/SKILL.md) | `/handover` | Schließt den äußeren Loop: Spec nach `completed/` verschieben, Übergabe schreiben. |

Bei ML-Projekten kommen Methoden-Skills (`forecasting`, `classification`, `regression`) aus dem
BIDA-ML-Starter dazu — Skill + Notebook immer als Paar (siehe [Teil D](#teil-d--die-drei-domänen-im-vergleich)).

#### `.claude/agents/` — spezialisierte Subagents

Subagents mit **eingegrenzter Fähigkeit**. Beide sind read-only (`tools: Read, Grep, Glob`) —
sie können prüfen, aber nichts ändern. Der Zweck von Subagents ist Fähigkeits-Eingrenzung,
nicht nur Parallelisierung.

| Agent | Funktion |
|---|---|
| [`code-reviewer`](../.claude/agents/code-reviewer.md) | Prüft Diffs/Dateien auf Korrektheit, Konventionen, Forecasting-Risiken (Leakage, unplausible Koeffizienten), Definition of Done. Meldet priorisiert (blocking vs. nice-to-have) mit Datei + Zeile. |
| [`security-reviewer`](../.claude/agents/security-reviewer.md) | Prüft auf Secret-Leaks, unsichere Snowflake-Operationen, ungewolltes Push/Merge/Deploy, versehentlich committete Artefakte. |

#### `.claude/hooks/` — harte Leitplanken (Durchsetzung)

Skripte für Lifecycle-Events, konfiguriert in `settings.json`.

| Datei | Typ | Funktion |
|---|---|---|
| [`protect-files.sh`](../.claude/hooks/protect-files.sh) | **PreToolUse** (Exit 2 = blockieren) | Fail-closed-Wrapper: findet Python, ruft `_check.py`. Ohne Python, bei nicht lesbarem Payload oder abgestürzter Prüfung → blockiert. |
| [`_check.py`](../.claude/hooks/_check.py) | Logik | Inspiziert das Tool-Payload: blockt Zugriff auf Credential-Dateien (`.env`, `*.p8`, `*.pem`, `*.key`; `.env.example` erlaubt) und destruktives SQL (`DROP`/`DELETE`/`TRUNCATE`). Bei Bash **nur**, wenn das Kommando tatsächlich SQL ausführt (snowsql, `snow sql`, `dbt(f) run-operation`, sqlplus …). Bei MCP-Tools, wenn Tool-Name oder Input eines der Wörter enthält (`drop_object`, `DELETE FROM`), nicht aber als Wortanfang (`dropdown`, `deleted`). Abgesichert durch `tests/unit/test_hooks.py`. |
| [`validate-changes.sh`](../.claude/hooks/validate-changes.sh) | **PostToolUse** (nicht-blockierend) | Nach `Edit`/`Write`: läuft Ruff (`.py`) bzw. sqlfluff (`.sql`) über die geänderte Datei und gibt Befunde als `additionalContext` an Claude zurück, damit der Agent sie sofort behebt. Findet Ruff auch in der Projekt-`.venv`. |
| `_file.py` | Helfer | Extrahiert den geänderten Dateipfad aus dem Payload für `validate-changes.sh`. |

#### `.claude/settings.json` und Beispiel

| Datei | Funktion |
|---|---|
| [`settings.json`](../.claude/settings.json) | **Geteilt, wird committet.** `permissions.allow` (erlaubte Bash-Befehle + Read/Edit/Write/Grep/Glob), `permissions.ask` (Rückfrage vor Änderungen an `eval/eval_*.py`), `permissions.deny` (Credential-Pfade, `git push`), und die Hook-Verdrahtung (PreToolUse/PostToolUse). |
| `.claude/settings.local.json.example` | Vorlage für **persönliche, nicht committete** lokale Settings. |

Wichtiges Detail zur Deny-Liste: Sie enthält **bewusst keine** `Bash(*DROP *)`-Regeln —
Permission-Globs können keinen Substring in der Mitte eines Bash-Kommandos matchen und würden
falsche Sicherheit geben. Zuverlässiges DDL-Blocking liegt im Hook (Schicht 1, siehe Teil E).

### C.3 — `.mcp.json` (Datenanbindung)

[`.mcp.json`](../.mcp.json) definiert die geteilten MCP-Server: **snowflake** (Platzhalter
`REPLACE_WITH_YOUR_SNOWFLAKE_MCP_COMMAND`, wird pro Projekt gesetzt) und **github**. Nur
Env-Referenzen (`${VAR}`), **niemals Secrets**.

### C.4 — `docs/` (Dokumentation & Prozess-Artefakte)

| Pfad | Funktion |
|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | Durchgespielter Beispiel-Durchlauf vom leeren Repo zur produktiven View (illustrativer Forecast). |
| `HANDBUCH.md` | **Dieses Dokument.** |
| [`datenarchitektur.md`](datenarchitektur.md) | **Firmweite** Referenz: das Pistor-Schichtenmodell (Data Vault 2.0: Landing → Vault → Consumption → Tabular → Report) + Namenskonventionen. In jedem DWH-Projekt gleich; das knappe Pendant für Claude steht in [`dbt-snowflake.md`](../.claude/rules/dbt-snowflake.md). |
| [`architecture.md`](architecture.md) | **Projektspezifische** Architektur: was *dieses* Projekt im firmweiten Modell tut. Enthält TODO/`<PLACEHOLDER>`, pro Projekt füllen. |
| `adr/` | **Architecture Decision Records.** [`0001`](adr/0001-record-architecture-decisions.md) etabliert das Muster: jede grössere Entscheidung als nummerierte Datei (Kontext, Entscheidung, Konsequenzen). |
| `specs/active/` | Laufende Specs (aus `/spec`). |
| `specs/completed/` | Abgeschlossene Specs (via `/handover` verschoben). |
| `domain-setup/` | Anleitungen pro Domäne: [`ml.md`](domain-setup/ml.md), [`de.md`](domain-setup/de.md), [`dwh.md`](domain-setup/dwh.md). Was behalten, was `init-domain.sh` entfernt, was danach anzupassen ist. |
| `runbooks/` | Betriebsanleitungen: [`development.md`](runbooks/development.md), [`deployment.md`](runbooks/deployment.md) (beide aktuell TODO-Stubs, pro Projekt füllen). |
| `contracts/` | **Data Contracts.** [`README.md`](contracts/README.md) erklärt die zwei Ebenen (fachlich als Markdown + technisch via dbt `contract: {enforced: true}`), `_template.md` als Vorlage, `mart_example__orders_daily.md` als Beispiel. |

### C.5 — `eval/` (der Verifier-Baukasten)

Das maschinelle Erfolgssignal. **Exit-Code 0 = PASS, ≠ 0 = FAIL** — nichts anderes zählt.

| Pfad | Funktion |
|---|---|
| [`README.md`](../eval/README.md) | Der **Verifier-Kontrakt**: Exit-Code als Reward, ohne Interaktion lauffähig, deterministisch, klare Fehlerausgabe, vor der Implementierung gebaut und danach nicht aufgeweicht. |
| `examples/eval_forecast.py` | Forecast-Verifier (MAPE/Bias/negative Werte). Kopiervorlage. |
| `examples/eval_abstimmung.py` | Abstimmungs-Verifier für Marts und Kennzahlen: keine doppelten Schlüssel, Vollständigkeit, Ziel = Quelle je Schlüssel, mindestens ein vom Fachbereich bestätigter Sollwert. Fängt „Tests grün, Zahl falsch". |
| `examples/eval_baseline_beat.py` | Generischer ML-Verifier: PASS nur, wenn Modell die Baseline schlägt **und** die Quality-Bar erfüllt. |

Nutzung: passendes Beispiel nach `eval/eval_<thema>.py` kopieren, Schwellen setzen.
`scripts/verify.sh` führt automatisch alle `eval/eval_*.py` aus (die `examples/` bewusst nicht).
Änderungen an `eval/eval_*.py` lösen in Claude Code immer eine Rückfrage aus
(`permissions.ask`), damit ein Verifier nicht still aufgeweicht wird.
**Für DWH-Projekte ist `dbtf test` der Verifier** — kein eigenes Python-Eval nötig.

### C.6 — Der dbt-Stack (DWH / Snowflake)

| Pfad | Funktion |
|---|---|
| `models/staging/`, `models/marts/` | dbt-Modelle. Beispiele `stg_example__orders`, `mart_example__orders_daily`. Konventionen: [`.claude/rules/dbt-snowflake.md`](../.claude/rules/dbt-snowflake.md). |
| `macros/`, `seeds/`, `snapshots/` | dbt-Makros, Seed-CSVs, Snapshots (Grundgerüst mit `.gitkeep`). |
| `dbt_project.yml`, `packages.yml` | dbt-Projektkonfiguration und Paket-Abhängigkeiten. |
| `profiles.yml.example` | Profil-Vorlage (Key-Pair, `snowflake_jwt`, Werte aus Env-Vars). Nach `~/.dbt/profiles.yml` kopieren. |
| `.sqlfluff` | SQL-Linter-Konfiguration (von `validate-changes.sh` genutzt). |
| `tests/dbt/` | dbt-spezifische Tests. |

### C.7 — Domänen-Ordner (behalten oder per `init-domain.sh` entfernen)

Jeder hat ein README mit Konventionen; die zugehörige Rule lädt path-gebunden.

| Ordner | Domäne | Funktion |
|---|---|---|
| [`src/`](../src/README.md) | alle | Produktiver Python-Code (`src/forecast/`, `src/ingest/` …). „Notebooks explorieren, `src/` produziert." Enthält Beispiel-`config.py` und `data_loader.py`. |
| [`dags/`](../dags/README.md) | DE / ML | Airflow-DAGs (ein DAG pro Datei, Dateiname = DAG-Id). Beispiel `example_dbt_daily.py` mit deklarierter Fehlerpolitik je Task. |
| [`oracle/`](../oracle/README.md) | DE | Oracle-SQL/PL-SQL für Quellsysteme. Empfohlen: `views/`, `packages/`, `scripts/`. |
| [`notebooks/`](../notebooks/README.md) | ML | Exploration. Nummern-Prefix, kein Produktionscode, Outputs via nbstripout gestrippt. |

### C.8 — `scripts/` (ausführbare Einstiegspunkte)

| Skript | Funktion |
|---|---|
| `setup.sh` | `uv sync`, dann Hinweis auf `.env`. Erster Schritt. |
| `init-project.sh` | **Setup-Wizard:** fragt Kernwerte ab, ersetzt `<PLACEHOLDER>` in `CLAUDE.md` + Docs, generiert eine schlanke Projekt-README, entfernt Template-Einführungsmaterial (`docs/rollout/`) und den `.template`-Marker. |
| `init-domain.sh <ml\|de\|dwh>` | Entfernt die für die gewählte Domäne nicht benötigten Ordner. |
| `new-ml-project.sh` | **ML-Vollautomatik:** Domäne einrichten, Platzhalter füllen, Methoden-Skill+Notebook aus dem BIDA-ML-Starter kopieren, `uv sync --group ml`, Checks laufen lassen. |
| `check-template.sh` | Prüft, ob noch offene `<PLACEHOLDER>` existieren (Exit 1, wenn ja). Läuft auch in CI. |
| `lint.sh` | Ruff (check + format) und mypy über `src` + `eval`. Sammelt Fehler, steigt nicht beim ersten aus. |
| `test.sh` | `dbtf test` (falls dbt-Projekt) + `pytest`. Fehlendes `dbtf` lokal = Warnung, kein FAIL. |
| `verify.sh` | **Der komplette Verifier:** check-template + lint + test + alle `eval/eval_*.py`. Gesammelter Exit-Code = Reward-Signal des Loops. |

### C.9 — Konfiguration & Infrastruktur (Wurzelebene)

| Pfad | Funktion |
|---|---|
| [`pyproject.toml`](../pyproject.toml) | Python-Projekt: Basis-Dependencies (pandas, numpy, scikit-learn, statsmodels), Gruppe `dev` (Ruff, mypy, pytest) und optionale Gruppe `ml` (der grosse ML-Stack, `uv sync --group ml`). Ruff/mypy-Konfig. |
| `uv.lock`, `.python-version` | Gepinnte Abhängigkeiten (committet) und Python-Version. |
| [`.env.example`](../.env.example) | Vorlage für Secrets (Snowflake-Account/User/Key-Pfad, GitHub-Token). Nach `.env` kopieren — `.env` wird **nie** committet. |
| `.mcp.json` | Siehe [C.3](#c3--mcpjson-datenanbindung). |
| `.gitignore` | Schützt `.env`, `*.p8`, `settings.local.json` u. a. vor versehentlichem Commit. |
| `.pre-commit-config.yaml` | Pre-commit-Hooks, u. a. nbstripout (strippt Notebook-Outputs). Einrichten: `uv tool install pre-commit && pre-commit install`. |
| `.github/workflows/ci.yml` | **CI = derselbe Verifier wie lokal, automatisiert.** Job `python`: uv sync, check-template, Ruff, mypy, pytest, alle `eval_*.py`. Job `dbt`: läuft nur mit gesetzten Snowflake-Secrets (Secret-Guard), baut dbt inkl. Tests. |
| `.devcontainer/` | Dev-Container (Python 3.12 + Node, VS-Code-Extensions für Ruff/mypy/dbt). `post-create.sh` als Setup-Hook. |
| `.gitattributes`, `.sqlfluff` | Git-Attribute und SQL-Linter-Konfig. |

---

## Teil D — Die drei Domänen im Vergleich

Das Template deckt drei Projekttypen ab. `bash scripts/init-domain.sh <ml|de|dwh>` schneidet
es auf die gewählte Domäne zu.

| | **ml** (ML / Data Science) | **de** (Data Engineering) | **dwh** (Data Warehouse) |
|---|---|---|---|
| **Kern** | Training/Inferenz in `src/`, Notebooks | Airflow-Orchestrierung, ggf. dbt + Oracle | dbt-Modelle auf Snowflake |
| **Verifier** | `eval/eval_<thema>.py` (Pflicht) | Python-Eval oder `dbtf test` | **`dbtf test`** (kein Python-Eval nötig) |
| **`init-domain.sh` entfernt** | dbt-Stack, `oracle/` | `notebooks/` | `oracle/`, `dags/`, `notebooks/` |
| **Detail-Anleitung** | [`domain-setup/ml.md`](domain-setup/ml.md) | [`domain-setup/de.md`](domain-setup/de.md) | [`domain-setup/dwh.md`](domain-setup/dwh.md) |

**ML-Sonderfall — der BIDA-ML-Starter:** Das Methodenwissen (Forecasting, Klassifikation,
Regression) lebt bewusst nicht im Template (Anti-Drift), sondern im
[BIDA-ML-Starter](https://github.com/themanbetterknownasthemachine/BIDA-ML-Starter). Bei
ML-Start werden **Methoden-Skill + Anleitungs-Notebook als Paar** ins Projekt kopiert —
automatisch via `scripts/new-ml-project.sh`, manuell nach der Tabelle in
[`domain-setup/ml.md`](domain-setup/ml.md).

> **Offener Punkt (Stand Template):** `uv sync --group ml` wurde noch nie gegen den Ziel-Index
> ausgeführt; und falls die IT conda vorgibt, braucht es eine Hybrid-Lösung. Details und
> To-dos stehen in [`domain-setup/ml.md`](domain-setup/ml.md).

---

## Teil E — Das Sicherheitsmodell (zwei Schichten)

Der wichtigste Grundsatz (siehe [Kontext vs. Durchsetzung](#das-zentrale-mentale-modell-kontext-vs-durchsetzung)):
Regeln in Text sind Kontext, kein Zwang. Was niemals passieren darf, wird in **zwei Schichten**
technisch erzwungen — beschrieben in [`.claude/rules/security.md`](../.claude/rules/security.md):

**Schicht 1 (primär): der PreToolUse-Hook.**
[`protect-files.sh`](../.claude/hooks/protect-files.sh) → [`_check.py`](../.claude/hooks/_check.py)
inspiziert jedes Tool-Payload und blockt mit Exit 2:
- Reads/Edits/Writes, deren **Pfad** eine Credential-Datei ist (`.env`, `*.p8`, `*.pem`,
  `*.key`) — `.env.example` ist erlaubt, damit Doku über `.env` schreiben darf;
- destruktives SQL (`DROP`/`DELETE`/`TRUNCATE`) in Bash, aber **nur**, wenn das Kommando
  tatsächlich SQL ausführt (snowsql, `snow sql`, `dbt(f) run-operation`, sqlplus, sqlcmd, psql,
  sqlite3), nicht bei jedem Vorkommen des Wortes;
- MCP-Tools, deren Name oder Input eines dieser Wörter enthält (`drop_object`, `DELETE FROM`),
  nicht aber als Wortanfang (`dropdown`, `deleted`).

Der Hook ist **fail-closed**: kein Python-Interpreter, nicht lesbares Payload oder abgestürzte
Prüfung → blockieren. Abgesichert durch `tests/unit/test_hooks.py`.

**Zusätzlich: Verifier-Schutz über `permissions.ask`.** Jede Änderung an `eval/eval_*.py` löst
eine Rückfrage aus, auch im Auto-Accept-Modus. Damit ist Regel 5 des Verifier-Kontrakts
(„nicht aufweichen, um rot auf grün zu drehen") technisch abgesichert. Änderungen per Bash
(`sed -i` usw.) deckt die Regel nicht ab; dort bleibt es Kontext.

**Schicht 2 (Backstop): `permissions.deny` in [`settings.json`](../.claude/settings.json).**
Grobe Zusatzabsicherung für Muster, die zuverlässig matchen (Credential-Pfade, `git push`).
Bewusst **ohne** `Bash(*DROP *)`-Regeln, weil Permission-Globs keinen Substring in der Mitte
eines Bash-Kommandos matchen können — zuverlässiges DDL-Blocking liegt in Schicht 1.

**Secrets generell:** nie in `.mcp.json`, Settings, Skills oder Code. Immer Env-Referenzen
(`${VAR}`), Werte in `.env`. `.gitignore` schützt `.env`, `*.p8` und `settings.local.json`.

---

## Teil F — Nachschlagen: Wo finde ich was?

| Ich will … | … dann schau in |
|---|---|
| das Gesamtkonzept verstehen | [Teil A](#teil-a--das-konzept) |
| ein Projekt komplett aufsetzen (Schritte) | [README](../README.md) + [Teil B](#teil-b--der-lebenszyklus-eines-projekts) |
| ein konkretes Beispiel durchspielen | [WORKFLOW.md](WORKFLOW.md) |
| wissen, was eine bestimmte Datei tut | [Teil C](#teil-c--vollständige-referenz-jeder-ordner-jede-datei) |
| die richtige Domäne wählen | [Teil D](#teil-d--die-drei-domänen-im-vergleich) + `docs/domain-setup/` |
| verstehen, was Claude blockiert und warum | [Teil E](#teil-e--das-sicherheitsmodell-zwei-schichten) + [`security.md`](../.claude/rules/security.md) |
| einen Verifier schreiben | [`eval/README.md`](../eval/README.md) |
| Konventionen für dbt / Python / Oracle / Airflow | die passende Datei in [`.claude/rules/`](../.claude/rules/) |
| einen wiederholbaren Ablauf starten | `/spec`, `/criteria`, `/review`, `/handover` (siehe [C.2](#c2--der-claude-ordner-das-herzstück)) |
| eine Architekturentscheidung festhalten | `docs/adr/` (Muster: [`0001`](adr/0001-record-architecture-decisions.md)) |
| eine Datenprodukt-Zusage dokumentieren | [`docs/contracts/`](contracts/README.md) |

---

*Dieses Handbuch beschreibt Struktur und Absicht des Templates. Wenn sich das Template ändert,
gilt jeweils die verlinkte Quelldatei als Wahrheit — dieses Dokument erklärt das Zusammenspiel,
nicht die letzte Detailzeile.*
