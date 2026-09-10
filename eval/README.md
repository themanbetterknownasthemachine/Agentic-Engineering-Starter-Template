# eval/ - der Verifier-Baukasten

Hier lebt das maschinelle Erfolgssignal des Projekts. Der Verifier wird **vor**
der Implementierung gebaut (siehe `docs/WORKFLOW.md`): erst festlegen, woran
Erfolg gemessen wird, dann implementieren lassen, bis das Signal gruen ist.

## Der Verifier-Kontrakt

Jedes `eval/eval_<thema>.py` haelt sich an diese Regeln:

1. **Exit-Code 0 = PASS, != 0 = FAIL.** Der Exit-Code ist das Reward-Signal
   fuer den Agenten-Loop; nichts anderes zaehlt.
2. **Laeuft ohne Interaktion.** Keine Prompts, keine manuellen Schritte;
   sinnvolle Defaults fuer alle Argumente.
3. **Deterministisch.** Gleicher Input, gleiches Ergebnis (Seeds fixieren).
4. **Klare Ausgabe.** Bei FAIL steht in der Ausgabe, *welche* Pruefung
   *warum* fehlgeschlagen ist (Metrik, Wert, Schwelle).
5. **Wird vor der Implementierung gebaut** und danach nicht stillschweigend
   aufgeweicht, um rot auf gruen zu drehen. Technisch abgesichert: jede Aenderung
   an `eval/eval_*.py` loest in Claude Code eine Rueckfrage aus
   (`.claude/settings.json`, `permissions.ask`), auch im Auto-Accept-Modus.

## Verwendung pro Projekt

- Passendes Beispiel aus `eval/examples/` nach `eval/eval_<thema>.py` kopieren
  und die Schwellen an die Quality-Bar der Spec anpassen.
- `scripts/verify.sh` fuehrt automatisch alle `eval/eval_*.py` aus
  (die Beispiele unter `eval/examples/` bewusst nicht).
- **DWH-Projekte:** `dbtf test` ist bereits der Verifier - dort ist kein
  eigenes Python-Eval noetig; Tests gehoeren in die `schema.yml` der Modelle.

## Beispiele

| Bereich       | Datei                        | Prueft                                     |
|---------------|------------------------------|--------------------------------------------|
| Forecast      | `eval_forecast.py`           | MAPE/Bias/negative Werte                   |
| ML allgemein  | `eval_baseline_beat.py`      | Modell schlaegt Baseline + Quality-Bar     |
| Abstimmung    | `eval_abstimmung.py`         | Ziel = Quelle je Schluessel + Sollwerte    |

- `examples/eval_forecast.py` - Forecast-Verifier (MAPE/Bias/negative Werte).
  Zeilen mit `y_true == 0` werden fuer die MAPE ausgeschlossen; bei vielen
  Nullern besser auf WAPE/sMAPE wechseln.
- `examples/eval_baseline_beat.py` - generischer ML-Verifier: PASS nur, wenn das
  Modell die Baseline schlaegt UND die Quality-Bar erfuellt (WAPE, robust gegen
  `y_true == 0`). Liest Baseline- und Modell-Vorhersagen aus einer results-JSON.
- `examples/eval_abstimmung.py` - fachlicher Abgleich fuer Marts und Kennzahlen:
  keine doppelten Schluessel, Vollstaendigkeit, Ziel = Quelle je Schluessel und
  Kennzahl, plus mindestens ein vom Fachbereich bestaetigter Sollwert. Faengt
  "Tests gruen, Zahl falsch" (Join-Explosion, falscher Filter, falsche Periode).
  Die Sollwerte stehen im Verifier selbst und sind damit durch Regel 5 geschuetzt.
  Fuer DWH-Projekte dasselbe Muster als dbt-Singular-Test unter `tests/`.
