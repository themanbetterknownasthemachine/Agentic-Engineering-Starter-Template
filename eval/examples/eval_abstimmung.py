"""Abstimmungs-Verifier: Zielzahlen muessen zur Quelle passen (Kontrakt: eval/README.md).

Faengt den Fall "Tests gruen, Zahl falsch": ein Mart kann Schema-Tests und Metriken
bestehen und trotzdem falsche Summen liefern (Join-Explosion, fehlender Filter,
falsche Periodenzuordnung). Dieser Verifier stimmt deshalb fachlich ab:

  (a) keine doppelten Schluessel im Ziel (Hinweis auf Join-Explosion),
  (b) Vollstaendigkeit: jeder Schluessel der Quelle ist im Ziel und umgekehrt,
  (c) Abgleich je Schluessel und Kennzahl: Ziel = Quelle (innerhalb TOLERANZ_ABS),
  (d) Sollwerte: vom Fachbereich bestaetigte Zahlen werden getroffen.

(d) ist Pflicht: Quelle und Ziel koennen denselben Fehler teilen (z. B. derselbe falsche
Filter in beiden Queries). Erst ein bestaetigter Sollwert verankert die Wahrheit.

Quelle und Ziel sind bereits aggregiert (je Schluessel eine Zeile) und werden vorher
deterministisch exportiert, z. B. per Query gegen Quellsystem und Mart. Der Verifier
selbst greift auf keine Datenbank zu. NULL gilt als fehlender Wert, nicht als 0.

Erwartetes JSON-Format (Spalten gemaess SCHLUESSEL und KENNZAHLEN):
    {
      "quelle": [{"monat": "2026-07", "standort": "ROT", "menge": 1200}, ...],
      "ziel":   [{"monat": "2026-07", "standort": "ROT", "menge": 1200}, ...]
    }

Exit-Code 0 = PASS (Reward-Signal fuer den Agenten), 1 = FAIL, 2 = SETUP-FEHLER.

Aufruf:
    python eval/eval_abstimmung.py
    python eval/eval_abstimmung.py --daten abstimmung_juli_2026.json
"""

import argparse
import json
import math
import sys
from typing import Any, NoReturn

# --- Konfiguration -----------------------------------------------------------
# <PLATZHALTER: aus /criteria-Ergebnis setzen>
DATEN_PATH = "abstimmung.json"
SCHLUESSEL = ("monat", "standort")
KENNZAHLEN = ("menge",)
# Erlaubte absolute Abweichung je Schluessel und Kennzahl. 0 = exakt (Mengen, Anzahlen).
# Nur fuer Rundungseffekte bei Betraegen setzen, nie um eine Abweichung zu verdecken.
TOLERANZ_ABS = 0.0
# Vom Fachbereich bestaetigte Zahlen (Known Answers), mindestens eine. Stehen bewusst
# hier und nicht in der Datendatei: Aenderungen an eval/eval_*.py loesen eine
# Rueckfrage aus (.claude/settings.json, permissions.ask).
# Format: {"monat": "2026-07", "standort": "ROT", "menge": 1200, "beleg": "Wer, wann, wo"}
SOLLWERTE: list[dict[str, Any]] = []
# -----------------------------------------------------------------------------

MAX_BEISPIELE = 10  # so viele Abweichungen je Pruefung ausgeben, Rest zusammenfassen

Key = tuple[str, ...]


def fail_setup(message: str) -> NoReturn:
    """Setup-Fehler klar benennen und mit Exit 2 abbrechen (FAIL, aber kein Abgleich-FAIL)."""
    print(f"SETUP-FEHLER: {message}", file=sys.stderr)
    sys.exit(2)


def zahl(x: float | None) -> str:
    """Schweizer Zahlenformat fuer die Ausgabe, NULL sichtbar als NULL."""
    return "NULL" if x is None else f"{x:,.2f}".replace(",", "'")


def fmt_key(key: Key) -> str:
    return "/".join(key)


def beispiele(eintraege: list[str]) -> str:
    rest = len(eintraege) - MAX_BEISPIELE
    text = "; ".join(eintraege[:MAX_BEISPIELE])
    return f"{text}; ... und {rest} weitere" if rest > 0 else text


def schluessel_von(zeile: dict[str, Any], wo: str) -> Key:
    fehlend = [s for s in SCHLUESSEL if s not in zeile]
    if fehlend:
        fail_setup(f"{wo}: Schluesselspalte(n) {fehlend} fehlen in Zeile {zeile}.")
    return tuple(str(zeile[s]) for s in SCHLUESSEL)


def wert(zeile: dict[str, Any], kennzahl: str, wo: str) -> float | None:
    if kennzahl not in zeile:
        fail_setup(f"{wo}: Kennzahl '{kennzahl}' fehlt in Zeile {zeile}.")
    v = zeile[kennzahl]
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, int | float | str):
        fail_setup(f"{wo}: Kennzahl '{kennzahl}' ist keine Zahl: {v!r}.")
    try:
        return float(v)
    except ValueError:
        fail_setup(f"{wo}: Kennzahl '{kennzahl}' ist keine Zahl: {v!r}.")


def lade_zeilen(daten: dict[str, Any], seite: str, pfad: str) -> list[dict[str, Any]]:
    zeilen = daten.get(seite)
    if not isinstance(zeilen, list) or not all(isinstance(z, dict) for z in zeilen):
        fail_setup(f"'{pfad}': '{seite}' muss eine Liste von Objekten sein.")
    if not zeilen:
        fail_setup(f"'{pfad}': '{seite}' enthaelt keine Zeilen.")
    return zeilen


def indexiere(
    zeilen: list[dict[str, Any]], seite: str
) -> tuple[dict[Key, dict[str, Any]], list[Key]]:
    """Zeilen nach Schluessel ablegen; doppelte Schluessel separat zurueckgeben."""
    index: dict[Key, dict[str, Any]] = {}
    doppelt: list[Key] = []
    for zeile in zeilen:
        key = schluessel_von(zeile, seite)
        if key in index:
            doppelt.append(key)
        index[key] = zeile
    return index, doppelt


def gleich(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=TOLERANZ_ABS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daten", default=DATEN_PATH, help="JSON mit 'quelle' und 'ziel'")
    args = ap.parse_args()

    if not SOLLWERTE:
        fail_setup(
            "Keine SOLLWERTE hinterlegt. Mindestens eine vom Fachbereich bestaetigte Zahl "
            "eintragen: Quelle und Ziel koennen denselben Fehler teilen."
        )

    try:
        with open(args.daten, encoding="utf-8") as f:
            daten = json.load(f)
    except FileNotFoundError:
        fail_setup(f"Datendatei '{args.daten}' nicht gefunden.")
    except json.JSONDecodeError as exc:
        fail_setup(f"'{args.daten}' ist kein gueltiges JSON: {exc}.")
    if not isinstance(daten, dict):
        fail_setup(f"'{args.daten}' muss ein Objekt mit 'quelle' und 'ziel' sein.")

    zeilen_quelle = lade_zeilen(daten, "quelle", args.daten)
    zeilen_ziel = lade_zeilen(daten, "ziel", args.daten)
    quelle, doppelt_quelle = indexiere(zeilen_quelle, "quelle")
    ziel, doppelt_ziel = indexiere(zeilen_ziel, "ziel")
    if doppelt_quelle:
        fail_setup(
            f"Quelle hat doppelte Schluessel, der Export ist nicht aggregiert: "
            f"{beispiele([fmt_key(k) for k in doppelt_quelle])}."
        )

    fehler: list[str] = []

    # (a) doppelte Schluessel im Ziel
    if doppelt_ziel:
        fehler.append(
            f"Doppelte Schluessel im Ziel ({len(doppelt_ziel)}), Hinweis auf Join-Explosion: "
            f"{beispiele([fmt_key(k) for k in doppelt_ziel])}"
        )

    # (b) Vollstaendigkeit
    nur_quelle = sorted(quelle.keys() - ziel.keys())
    nur_ziel = sorted(ziel.keys() - quelle.keys())
    if nur_quelle:
        fehler.append(
            f"Im Ziel fehlen {len(nur_quelle)} Schluessel der Quelle: "
            f"{beispiele([fmt_key(k) for k in nur_quelle])}"
        )
    if nur_ziel:
        fehler.append(
            f"Im Ziel stehen {len(nur_ziel)} Schluessel ohne Quelle: "
            f"{beispiele([fmt_key(k) for k in nur_ziel])}"
        )

    # (c) Abgleich je Schluessel und Kennzahl
    gemeinsam = sorted(quelle.keys() & ziel.keys())
    for kennzahl in KENNZAHLEN:
        # ueber die Rohzeilen, damit doppelte Zeilen im Ziel auch in der Summe sichtbar sind
        summe_q = sum(wert(z, kennzahl, "quelle") or 0.0 for z in zeilen_quelle)
        summe_z = sum(wert(z, kennzahl, "ziel") or 0.0 for z in zeilen_ziel)
        print(
            f"{kennzahl:<12} Summe Quelle {zahl(summe_q):>16} | Summe Ziel {zahl(summe_z):>16} "
            f"| {len(gemeinsam)} Schluessel abgeglichen"
        )
        abweichungen: list[str] = []
        for key in gemeinsam:
            q = wert(quelle[key], kennzahl, "quelle")
            z = wert(ziel[key], kennzahl, "ziel")
            if q is None and z is None:
                continue
            if q is None or z is None or not gleich(z, q):
                diff = "" if q is None or z is None else f", Differenz {zahl(z - q)}"
                abweichungen.append(f"{fmt_key(key)}: Quelle {zahl(q)}, Ziel {zahl(z)}{diff}")
        if abweichungen:
            fehler.append(
                f"{kennzahl}: {len(abweichungen)} Abweichung(en) ueber Toleranz "
                f"{zahl(TOLERANZ_ABS)}: {beispiele(abweichungen)}"
            )

    # (d) Sollwerte vom Fachbereich
    for soll in SOLLWERTE:
        key = schluessel_von(soll, "SOLLWERTE")
        beleg = soll.get("beleg", "ohne Beleg")
        if key not in ziel:
            fehler.append(f"Sollwert {fmt_key(key)} ({beleg}): Schluessel fehlt im Ziel")
            continue
        for kennzahl in KENNZAHLEN:
            if kennzahl not in soll:
                continue
            s = wert(soll, kennzahl, "SOLLWERTE")
            z = wert(ziel[key], kennzahl, "ziel")
            if s is None or z is None or not gleich(z, s):
                fehler.append(
                    f"Sollwert {fmt_key(key)} {kennzahl} ({beleg}): "
                    f"erwartet {zahl(s)}, Ziel {zahl(z)}"
                )
    print(f"Sollwerte    {len(SOLLWERTE)} geprueft")

    for meldung in fehler:
        print(f"FAIL: {meldung}", file=sys.stderr)
    print("RESULT       =", "FAIL" if fehler else "PASS")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
