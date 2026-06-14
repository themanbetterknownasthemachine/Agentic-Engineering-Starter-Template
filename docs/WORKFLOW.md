# Beispiel-Durchlauf: vom leeren Repo zur produktiven View

Dieser Durchlauf zeigt an einem konkreten Beispiel, wie ein Projekt mit diesem Template abläuft, von der leeren Vorlage bis zur produktiven Snowflake-View. Das Beispiel ist illustrativ (ein Forecast); ersetze es durch dein eigenes Vorhaben. Die einmalige Einrichtung und die anzupassenden Dateien stehen in der [README](../README.md).

Das Grundprinzip dahinter: erst spezifizieren (Spec), dann ein maschinell prüfbares Erfolgssignal bauen (Verifier), dann delegieren. Du behältst Spec, finale Bewertung und Verständnis; den Code in der Schleife übernimmt der Agent.

## Beispiel-Vorhaben

Tägliche Prognose des Wareneingangsvolumens (Paletten pro Tag) je Standort, damit die Kapazität am Wareneingang (Personal, Tore, Stellplätze) vorausschauend geplant werden kann. Konsum in Power BI.

## 1. Repo anlegen

Auf GitHub "Use this template", neues Repo (z.B. `wareneingang-forecast`), dann klonen und in VS Code öffnen:

```bash
git clone https://github.com/<org>/wareneingang-forecast.git
cd wareneingang-forecast
code .
```

Du startest mit der fertigen Struktur: CLAUDE.md, `.claude/` mit Rules, Skills, Subagents und Hooks sowie `.mcp.json` sind schon da.

## 2. Kontext anpassen

Die vier Dateien aus der Checkliste in der README anpassen: in `CLAUDE.md` Name, Beschreibung, Stack, Schemas und Quality-Bar (z.B. die MAPE-Schwelle); `.env` aus `.env.example`; in `.mcp.json` den Snowflake-MCP-Befehl eintragen.

Warum: Das ist der dauerhafte Kontext, den Claude bei jeder Session mitbekommt, damit es eure Konventionen nicht jedes Mal neu errät.

## 3. Claude Code starten

Im Projekt-Root `claude` starten, mit `/memory` prüfen, welche Dateien geladen sind, optional `/init`, damit Claude die CLAUDE.md aus dem echten Code verfeinert.

## 4. Spec bauen mit /spec

`/spec` startet die Spec-Skill. Claude interviewt dich. Eine Session sieht etwa so aus:

> **Du:** `/spec`
>
> **Claude:** Was soll am Ende konkret besser sein?
> **Du:** Die Schichtplanung am Wareneingang läuft heute nach Bauchgefühl. Ich will eine Tagesprognose, damit wir Personal und Tore vorausschauend planen.
>
> **Claude:** Welche Zielgrösse, welche Granularität, welcher Horizont?
> **Du:** Paletten pro Tag je Standort, 14 Tage voraus.
>
> **Claude:** Welche Daten und Constraints gelten?
> **Du:** Historie in Snowflake, Features über DIM_DATE (AT=1), Rolle ROLE_ML_TESTING, Konsum in Power BI via DirectQuery.
>
> **Claude:** Akzeptanzkriterium?
> **Du:** MAPE unter 12 Prozent, keine negativen Werte, Bias nahe null.

Ergebnis: eine kurze Spec nach `docs/specs/active/wareneingang_forecast.md`:

```text
# Spec: Wareneingangs-Forecast
Ziel: Tagesgenaue Prognose Wareneingangsvolumen je Standort, Konsum via Power BI.
Zielgrösse: Paletten/Tag   Horizont: 14 Tage
Features: DIM_DATE (AT=1), Wochentag, Vorjahreswert -364 Tage, Feiertags-Flags
Akzeptanz: MAPE < 12 %, keine negativen Werte, Bias nahe null
Output-View: BUT_LANDING.ML_INFERENCE.V_FORECAST_WARENEINGANG
Offene Entscheidungen: Standorte einzeln vs. aggregiert; Aktionen als Feature?
```

Warum: Du besitzt das Ziel und die Top-Level-Entscheidungen. Ohne Spec ist alles Weitere nur schnelleres Raten.

## 5. Kriterien festlegen mit /criteria

`/criteria` schreibt eine prüfbare Checkliste, die zur Definition of Done in der CLAUDE.md wird: MAPE-Schwelle eingehalten, keine negativen Werte, Bias nahe null, Plausibilität (3 SD), Holdout sauber getrennt.

Warum: Erfolg muss messbar sein, bevor der Agent loslegt, sonst kann er sich nicht selbst korrigieren.

## 6. Verifier bauen

Erst das Mess-Skript, dann implementieren lassen. `eval/eval_wareneingang.py`:

```python
import pandas as pd, numpy as np, sys

df = pd.read_parquet("holdout.parquet")           # Spalten: y_true, y_pred
mape = np.mean(np.abs((df.y_true - df.y_pred) / df.y_true)) * 100
neg  = (df.y_pred < 0).sum()
bias = np.mean(df.y_pred - df.y_true)

print(f"MAPE={mape:.2f}% | Bias={bias:+.1f} | Negative={neg}")
sys.exit(0 if (mape < 12 and neg == 0) else 1)    # Exit-Code = Reward
```

Warum: Das ist der Schritt, den die meisten überspringen. Mit diesem Signal kannst du grosse Blöcke sicher delegieren.

## 7. Bauen lassen, in der Schleife

Jetzt delegierst du den eigentlichen Code:

> **Du:** Lies die Spec und die Kriterien. Baue die Pipeline: Daten aus Snowflake ziehen, Features über DIM_DATE, ein erstes Modell (saisonale Baseline plus LightGBM), schreib die Prognose in die View. Iteriere, bis `eval/eval_wareneingang.py` grün ist. Nenne vorher deine Annahmen.

Claude zieht über den MCP die Historie, baut die Features, trainiert, läuft das Eval, sieht den MAPE, korrigiert (z.B. Feiertage als Feature ergänzen), läuft erneut, bis grün. Du schaust zu, statt jeden Block selbst zu schreiben.

Warum: Genau das ist der Hebel, implementieren gegen ein prüfbares Erfolgssignal.

## 8. Review und Deploy

Den `code-reviewer`-Subagent über den Diff laufen lassen, die Annahmen fachlich prüfen (Plausibilität, kein Feature-Leakage), die Tests ausführen, die Spec nach `docs/specs/completed/` verschieben, die View deployen. Power BI konsumiert sie.

Warum: Tests fangen das Mechanische, dein Urteil fängt das Architektonische. Ein grüner MAPE-Wert ist nicht automatisch deploy-reif.

## Kurzfassung

Repo aus dem Template anlegen, Kontext anpassen, `/spec`, `/criteria`, Verifier bauen, in der Schleife bauen lassen, dann Review und Deploy. Der Mensch besitzt Spec, Verifikation und Verständnis; der Agent füllt die Implementierung gegen ein prüfbares Erfolgssignal.
