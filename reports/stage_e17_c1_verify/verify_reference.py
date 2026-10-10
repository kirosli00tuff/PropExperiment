"""Check 1 (VerdictVerifier-FableXHigh, Stage E.17): recompute E.12's C10 reference counts.

Reads E.12's persisted state copy (~/.cache/propexp_e14_c1/e12_state_copy, read-only) through
the frozen loader (ml_route_v2.phase1.build.load_build, as c1_replication.q_m1.run does), counts
per horizon the NG ok rows on which each covered signal applies, and compares every count with
reports/stage_e14_c1_model.json "c10_reference". Prints counts, dates and booleans only; never a
price or a feature value. Writes reports/stage_e17_c1_verify/reference_recount.json.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

os.nice(10)

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

OUT = REPO / "reports" / "stage_e17_c1_verify" / "reference_recount.json"
STATE = Path.home() / ".cache" / "propexp_e14_c1" / "e12_state_copy"
MANIFEST = REPO / "reports" / "stage_e14_c1_e12_state_manifest.json"
MANIFEST_SHA256 = "8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9"
MODEL = REPO / "reports" / "stage_e14_c1_model.json"
HORIZONS = ("h60", "hF")
VEHICLE = "NG"
DATE_COLUMNS = ("day", "trade_date", "date", "row_date", "decision_date")


def own_counts(frame: pd.DataFrame, signals: list[str]) -> dict[str, dict]:
    """My count: NG rows with ok_<h>; per signal, how many of them have app_<signal> > 0."""
    is_ng = frame["root"].astype(str).to_numpy() == VEHICLE
    out: dict[str, dict] = {}
    for h in HORIZONS:
        sel = is_ng & frame[f"ok_{h}"].to_numpy(bool)
        sub = frame.loc[sel, [f"app_{s}" for s in signals]]
        app = {s: int((sub[f"app_{s}"] > 0).sum()) for s in signals}
        out[h] = {"ng_ok_rows": int(sel.sum()), "applicable": app}
    return out


def mbt_span(frame: pd.DataFrame, date_col: str | None) -> dict:
    """Where E.12's g17_mbt applied on NG rows: counts and first/last trade date (no values)."""
    is_ng = frame["root"].astype(str).to_numpy() == VEHICLE
    app = frame["app_g17_mbt"].to_numpy(np.float64) > 0
    rec: dict = {"ng_rows_total": int(is_ng.sum()), "ng_rows_app_g17_mbt": int((is_ng & app).sum()),
                 "non_ng_rows_app_g17_mbt": int((~is_ng & app).sum())}
    for h in HORIZONS:
        ok = frame[f"ok_{h}"].to_numpy(bool)
        rec[f"ng_ok_{h}_rows_app_g17_mbt"] = int((is_ng & ok & app).sum())
    if date_col is not None:
        days = pd.to_datetime(frame.loc[is_ng & app, date_col].astype(str)).dt.date
        rec["date_column"] = date_col
        rec["first_date"] = min(days).isoformat() if len(days) else None
        rec["last_date"] = max(days).isoformat() if len(days) else None
        rec["distinct_dates"] = int(days.nunique())
        all_days = pd.to_datetime(frame.loc[is_ng, date_col].astype(str)).dt.date
        rec["ng_panel_first_date"] = min(all_days).isoformat()
        rec["ng_panel_last_date"] = max(all_days).isoformat()
    return rec


def main() -> int:
    from c1_replication.guards import verify_state
    from c1_replication.q_m1 import c10_reference as frozen_c10_reference
    from ml_route_v2.phase1.build import load_build

    model = json.loads(MODEL.read_bytes())
    reference = model["c10_reference"]
    state_rec = verify_state(STATE, MANIFEST, MANIFEST_SHA256)
    build = load_build(STATE)
    frame = build.panel.frame
    signals = list(build.panel.signal_names)
    date_col = next((c for c in DATE_COLUMNS if c in frame.columns), None)
    non_signal_cols = [c for c in frame.columns
                       if not c.startswith(("app_", "val_", "x_", "f_", "avail_"))]
    mine = own_counts(frame, signals)
    frozen = frozen_c10_reference(build.panel)
    diffs = {h: {s: {"mine": mine[h]["applicable"][s], "model_json": reference[h]["applicable"].get(s)}
                 for s in signals if mine[h]["applicable"][s] != reference[h]["applicable"].get(s)}
             for h in HORIZONS}
    rows_diff = {h: (mine[h]["ng_ok_rows"], reference[h]["ng_ok_rows"]) for h in HORIZONS
                 if mine[h]["ng_ok_rows"] != reference[h]["ng_ok_rows"]}
    g17 = {h: {s: mine[h]["applicable"][s] for s in signals if s.startswith("g17_")} for h in HORIZONS}
    zero_ref = {h: sorted(s for s, n in mine[h]["applicable"].items() if n == 0) for h in HORIZONS}
    rec = {
        "schema": "stage_e17_c1_verify/reference/1",
        "state_dir": str(STATE), "state_manifest_sha256": MANIFEST_SHA256,
        "state_verified": state_rec,
        "model_json": str(MODEL.relative_to(REPO)),
        "panel": {"rows": int(len(frame)), "signals": len(signals),
                  "feature_cols": len(build.panel.feature_cols),
                  "roots": int(frame["root"].astype(str).nunique()),
                  "non_signal_columns": non_signal_cols, "date_column": date_col},
        "mine": mine,
        "frozen_function_equals_model_json": frozen == reference,
        "mine_equals_model_json": not any(diffs.values()) and not rows_diff,
        "differences": diffs, "ng_ok_rows_differences": rows_diff,
        "g17_counts_mine": g17,
        "g17_mbt_reference_model_json": {h: reference[h]["applicable"]["g17_mbt"] for h in HORIZONS},
        "zero_count_signals_in_reference": zero_ref,
        "n_live_in_e12_by_count": {h: sum(1 for n in mine[h]["applicable"].values() if n > 0)
                                   for h in HORIZONS},
        "mbt_span": mbt_span(frame, date_col),
    }
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print(f"state verified: files {state_rec.get('n_files', state_rec)}")
    print(f"panel rows {rec['panel']['rows']}, signals {len(signals)}, roots {rec['panel']['roots']}, "
          f"date column {date_col}; non-signal columns {non_signal_cols}")
    for h in HORIZONS:
        print(f"{h}: NG ok rows mine {mine[h]['ng_ok_rows']} vs model_json {reference[h]['ng_ok_rows']}; "
              f"g17 mine {g17[h]}; zero-count signals {len(zero_ref[h])}; "
              f"live by count {rec['n_live_in_e12_by_count'][h]}")
    print(f"mine == model_json: {rec['mine_equals_model_json']}; frozen function == model_json: "
          f"{rec['frozen_function_equals_model_json']}; differences {diffs} {rows_diff}")
    print("g17_mbt span on NG rows:", json.dumps(rec["mbt_span"]))
    print(f"written {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
