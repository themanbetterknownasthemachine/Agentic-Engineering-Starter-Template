"""Minimales, idempotentes Beispiel-DAG (passend zu .claude/rules/airflow.md).

Zeigt die Pflichten aus den Regeln:
- keine Top-Level-Berechnungen (nur Imports, Funktionen und die DAG-Definition)
- backfill-safe: die Logik nutzt die logische Datenintervall-Grenze, nie now()
- idempotent: derselbe logische Tag erzeugt dasselbe Ergebnis
- catchup bewusst gesetzt, Alerting explizit
- Fehlerpolitik je Task deklariert (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP),
  kein pauschales retries fuer alle Tasks
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pendulum
from airflow.decorators import dag, task


def notify_failure(context: dict[str, Any]) -> None:
    """Alerting-Platzhalter: hier Teams/Mail anbinden. Fehler muessen sichtbar sein."""
    ti = context["task_instance"]
    print(f"ALERT: {ti.dag_id}.{ti.task_id} fehlgeschlagen fuer {context['ds']}.")


DEFAULT_ARGS = {
    # Kein pauschaler Retry: jeder Task deklariert seine Fehlerpolitik selbst.
    "retries": 0,
    "on_failure_callback": notify_failure,
}


@dag(
    dag_id="example_dbt_daily",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Zurich"),
    catchup=False,  # bewusst gesetzt; fuer Backfill auf True stellen
    default_args=DEFAULT_ARGS,
    tags=["example", "dbt"],
)
def example_dbt_daily():
    # Fehlerpolitik STOP: reiner Rechenschritt. Ein Fehler ist ein Bug, Wiederholen
    # hilft nicht; nachgelagerte Tasks laufen nicht.
    @task(retries=0)
    def resolve_run_date(data_interval_end: pendulum.DateTime | None = None) -> str:
        # data_interval_end kommt aus dem Kontext -> backfill-safe, kein now().
        assert data_interval_end is not None
        return data_interval_end.to_date_string()

    # Fehlerpolitik RETRY: transiente Fehler (Netzwerk, Snowflake-Timeout).
    # Gefahrlos wiederholbar, weil der Schritt idempotent ist.
    @task(retries=2, retry_delay=timedelta(minutes=5), retry_exponential_backoff=True)
    def build_marts(run_date: str) -> str:
        # Platzhalter fuer den eigentlichen, idempotenten Schritt (z. B. dbtf build).
        # Idempotenz: Ziel per MERGE / --full-refresh je Partition, kein blindes INSERT.
        print(f"Baue Marts idempotent fuer {run_date} (Platzhalter).")
        return run_date

    # Fehlerpolitik ESCALATE: Plausibilitaet verletzt -> Mensch alarmieren
    # (on_failure_callback), nie automatisch wiederholen. Ein Retry wuerde
    # unplausible Zahlen nur erneut ausliefern.
    @task(retries=0)
    def check_plausibility(run_date: str) -> None:
        # Platzhalter: Pruefungen gegen Quelle oder Vorperiode eintragen
        # (Muster: eval/examples/eval_abstimmung.py).
        abweichungen: list[str] = []
        if abweichungen:
            raise ValueError(f"Plausibilitaet verletzt fuer {run_date}: {abweichungen}")

    check_plausibility(build_marts(resolve_run_date()))


example_dbt_daily()
