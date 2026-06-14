"""Verifier fuer Ruestmengen-Forecasts.

Exit-Code 0 = bestanden (Reward-Signal fuer den Agenten), 1 = durchgefallen.
Erwartet eine Parquet-Datei mit den Spalten y_true und y_pred.

Beispiel:
    python eval/eval_forecast.py --holdout holdout_april_2026.parquet
"""
import argparse
import sys

import numpy as np
import pandas as pd

THRESHOLD_MAPE = 8.0    # Prozent
MAX_ABS_BIAS_PCT = 3.0  # erlaubter mittlerer Bias in Prozent des Mittelwerts


def mape(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", default="holdout.parquet",
                    help="Parquet mit Spalten y_true, y_pred")
    args = ap.parse_args()

    df = pd.read_parquet(args.holdout)
    m = mape(df["y_true"], df["y_pred"])
    bias = float(np.mean(df["y_pred"] - df["y_true"]))
    bias_pct = bias / float(np.mean(df["y_true"])) * 100
    n_negative = int((df["y_pred"] < 0).sum())

    print(f"MAPE      = {m:6.2f} %   (Schwelle < {THRESHOLD_MAPE} %)")
    print(f"Bias      = {bias:+10.0f}   ({bias_pct:+.1f} % vom Mittelwert)")
    print(f"Negative  = {n_negative:6d}     (erlaubt: 0)")

    ok = (
        m < THRESHOLD_MAPE
        and abs(bias_pct) <= MAX_ABS_BIAS_PCT
        and n_negative == 0
    )
    print("RESULT    =", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
