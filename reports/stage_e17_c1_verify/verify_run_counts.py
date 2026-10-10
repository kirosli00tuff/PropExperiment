"""Check 2 (VerdictVerifier-FableXHigh, Stage E.17): rebuild C1's world and panel in memory with
the frozen code and recount C10 applicability independently of the run.

Does NOT call c1_replication.evaluate.run or .evaluate (the evaluation runs once; the marker
exists). It calls the same frozen building blocks the run used (load_calendars, c12_exclusions,
hist_tables, build_world, replication_panel) with the pinned inputs, then counts with its own code:
- the MBT and CL frames the run gave the world (ruling C7): bars, trade dates, all after the window,
  every bar timestamp after every NG decision time in the panel;
- per horizon, NG ok rows and per-signal applicable counts, compared with the result's guards.C10;
- the C10 rule by my own logic (reference > 0 and run == 0) against the result's stop_reason;
- panel counts and world leg records against the result.
Prints counts, dates and booleans only; never a price or a feature value. Checks free memory first
(the run peaked at 2.06 GB RSS). Writes reports/stage_e17_c1_verify/run_recount.json.
"""

from __future__ import annotations

import gc
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

OUT = REPO / "reports" / "stage_e17_c1_verify" / "run_recount.json"
RESULT = REPO / "reports" / "stage_e14_c1_result.json"
MODEL = REPO / "reports" / "stage_e14_c1_model.json"
STORE_HASHES = REPO / "reports" / "stage_e17_c1_store_hashes.json"
CALENDAR_HASHES = REPO / "reports" / "stage_e17_c1_calendar_hashes.json"
HORIZONS = ("h60", "hF")
VEHICLE = "NG"
MIN_AVAILABLE_KB = 3_500_000  # 3.5 GB; the run peaked at 2.06 GB RSS
DATE_COLUMNS = ("day", "trade_date", "date", "row_date", "decision_date")
TS_COLUMNS = ("t", "t_ns", "ts", "ts_ns", "decision_ts_ns", "ts_event")


def mem_available_kb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    raise RuntimeError("MemAvailable not found")


def own_counts(frame: pd.DataFrame, signals: list[str]) -> dict[str, dict]:
    is_ng = frame["root"].astype(str).to_numpy() == VEHICLE
    out: dict[str, dict] = {}
    for h in HORIZONS:
        sel = is_ng & frame[f"ok_{h}"].to_numpy(bool)
        sub = frame.loc[sel, [f"app_{s}" for s in signals]]
        out[h] = {"ng_ok_rows": int(sel.sum()),
                  "applicable": {s: int((sub[f"app_{s}"] > 0).sum()) for s in signals}}
    return out


def own_c10_rule(reference: dict, counts: dict) -> list[str]:
    """The freeze's rule as I read it: a signal with a non-zero E.12 count that applies on no row."""
    dead = []
    for h in HORIZONS:
        for s, n_ref in reference[h]["applicable"].items():
            if n_ref > 0 and counts[h]["applicable"].get(s, 0) == 0:
                dead.append(f"{s} ({h})")
    return dead


def frame_record(name: str, bars: pd.DataFrame, first: date, last: date,
                 max_decision_ts_ns: int | None) -> dict:
    days = pd.to_datetime(bars["trade_date"].astype(str)).dt.date
    ts_col = next((c for c in TS_COLUMNS if c in bars.columns), None)
    rec = {"root": name, "bars": int(len(bars)), "columns": list(bars.columns),
           "trade_dates": sorted({d.isoformat() for d in days}),
           "bars_with_trade_date_in_window": int(((days >= first) & (days <= last)).sum()),
           "bars_with_trade_date_after_window": int((days > last).sum()),
           "timestamp_column": ts_col}
    if ts_col is not None and max_decision_ts_ns is not None:
        ts = bars[ts_col].to_numpy(np.int64)
        rec["bars_at_or_before_last_ng_decision_time"] = int((ts <= max_decision_ts_ns).sum())
        rec["min_bar_ts_utc"] = pd.Timestamp(int(ts.min()), tz="UTC").isoformat()
    return rec


def main() -> int:
    avail = mem_available_kb()
    print(f"MemAvailable {avail // 1024} MB")
    if avail < MIN_AVAILABLE_KB:
        print(f"refusing: less than {MIN_AVAILABLE_KB // 1024} MB available")
        return 2
    from c1_replication.constants import (
        E12_GATE0_LIST,
        E12_GATE0_LIST_SHA256,
        EMPTY_ROOTS,
        WINDOW_FIRST,
        WINDOW_LAST,
    )
    from c1_replication.context import hist_tables
    from c1_replication.evaluate import c10_check as frozen_c10_check
    from c1_replication.evaluate import default_leg_loader, load_calendars, load_store_hashes
    from c1_replication.exclusions import c12_exclusions
    from c1_replication.guards import pinned_file
    from c1_replication.world import build_world, replication_panel
    from data.group_session import group_of

    result = json.loads(RESULT.read_bytes())
    model = json.loads(MODEL.read_bytes())
    reference = model["c10_reference"]
    run_c10 = result["guards"]["C10"]
    signals = tuple(json.loads(pinned_file(E12_GATE0_LIST, E12_GATE0_LIST_SHA256, "E.12 Gate 0 list"))
                    ["covered_signals"])
    stores = load_store_hashes(STORE_HASHES)
    cal = load_calendars(CALENDAR_HASHES, WINDOW_FIRST, WINDOW_LAST)
    c12 = c12_exclusions(cal["calendars"], tuple(cal["releases"].unsourced),
                         first=WINDOW_FIRST, last=WINDOW_LAST)
    loader = default_leg_loader(None)
    with hist_tables(cal["tables"]):
        world = build_world(
            lambda r: loader(r, expected_sha256=stores[r], calendar=cal["calendars"][group_of(r)]),
            cal["releases"].calendar, c12.excluded_dates(), first=WINDOW_FIRST, last=WINDOW_LAST)
        world_roots = {r: dict(v) for r, v in world.roots.items()}
        empty_frames = {r: world.bars[r] for r in EMPTY_ROOTS}
        world_rec = {"roots": sorted(world.bars.keys()), "calendar_dates": len(world.calendar),
                     "excluded_dates": sorted(d.isoformat() for d in world.excluded),
                     "legs_of_NG": list(world.legs[VEHICLE]),
                     "blackout_dates_per_root": {r: len(v) for r, v in world.blackout.items()}}
        panel = replication_panel(world, signals)
        del world
        gc.collect()
    frame = panel.frame
    print(f"panel rows {len(frame)}; roots {sorted(frame['root'].astype(str).unique())}")
    ts_col = next((c for c in TS_COLUMNS if c in frame.columns), None)
    date_col = next((c for c in DATE_COLUMNS if c in frame.columns), None)
    is_ng = frame["root"].astype(str).to_numpy() == VEHICLE
    max_t = int(frame.loc[is_ng, ts_col].to_numpy(np.int64).max()) if ts_col else None
    frames_rec = {r: frame_record(r, f, WINDOW_FIRST, WINDOW_LAST, max_t) for r, f in empty_frames.items()}
    mine = own_counts(frame, list(signals))
    app_all_ng = {s: int((frame.loc[is_ng, f"app_{s}"] > 0).sum()) for s in ("g17_mbt", "g17_cl")}
    diffs = {h: {s: {"mine": mine[h]["applicable"][s], "result": run_c10[h]["applicable"].get(s)}
                 for s in signals if mine[h]["applicable"][s] != run_c10[h]["applicable"].get(s)}
             for h in HORIZONS}
    rows_diff = {h: (mine[h]["ng_ok_rows"], run_c10[h]["ng_ok_rows"]) for h in HORIZONS
                 if mine[h]["ng_ok_rows"] != run_c10[h]["ng_ok_rows"]}
    zero_run = {h: sorted(s for s, n in mine[h]["applicable"].items() if n == 0) for h in HORIZONS}
    zero_ref = {h: sorted(s for s, n in reference[h]["applicable"].items() if n == 0) for h in HORIZONS}
    only_zero_now = {h: sorted(set(zero_run[h]) - set(zero_ref[h])) for h in HORIZONS}
    zero_in_ref_live_now = {h: sorted(set(zero_ref[h]) - set(zero_run[h])) for h in HORIZONS}
    dead_mine = own_c10_rule(reference, mine)
    dead_frozen = frozen_c10_check(mine, reference)
    panel_counts_mine = {k: int(v) for k, v in dict(panel.counts).items()}
    rec = {
        "schema": "stage_e17_c1_verify/run/1",
        "window": [WINDOW_FIRST.isoformat(), WINDOW_LAST.isoformat()],
        "c12": c12.record(),
        "world": world_rec,
        "world_roots_equal_result": world_roots == result["world"]["roots"],
        "world_roots_differences": {r: {k: (world_roots[r].get(k), result["world"]["roots"][r].get(k))
                                        for k in set(world_roots[r]) | set(result["world"]["roots"][r])
                                        if world_roots[r].get(k) != result["world"]["roots"][r].get(k)}
                                    for r in world_roots if world_roots[r] != result["world"]["roots"].get(r)},
        "c7_frames": frames_rec,
        "panel": {"rows": int(len(frame)), "ng_rows": int(is_ng.sum()), "signals": len(signals),
                  "feature_cols": len(panel.feature_cols),
                  "feature_cols_equal_model": tuple(panel.feature_cols) == tuple(model["feature_cols"]),
                  "timestamp_column": ts_col, "date_column": date_col},
        "panel_counts_mine": panel_counts_mine,
        "panel_counts_equal_result": panel_counts_mine == result["panel_counts"],
        "mine": mine,
        "mine_equals_result_guards_C10": not any(diffs.values()) and not rows_diff,
        "differences": diffs, "ng_ok_rows_differences": rows_diff,
        "app_on_all_ng_rows": app_all_ng,
        "zero_count_signals_run": zero_run,
        "zero_count_signals_reference": zero_ref,
        "zero_now_but_live_in_reference": only_zero_now,
        "zero_in_reference_but_live_now": zero_in_ref_live_now,
        "dead_by_my_rule": dead_mine,
        "dead_by_frozen_c10_check_on_my_counts": dead_frozen,
        "result_stop_reason": result["stop_reason"],
        "result_verdict": result["verdict"],
    }
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n")
    for r, f in frames_rec.items():
        print(f"C7 frame {r}: bars {f['bars']}, trade dates {f['trade_dates']}, in window "
              f"{f['bars_with_trade_date_in_window']}, at/before last NG decision time "
              f"{f.get('bars_at_or_before_last_ng_decision_time')}")
    for h in HORIZONS:
        g17 = {s: mine[h]["applicable"][s] for s in signals if s.startswith("g17_")}
        print(f"{h}: NG ok rows mine {mine[h]['ng_ok_rows']} vs result {run_c10[h]['ng_ok_rows']}; g17 {g17}")
    print(f"mine == result guards.C10: {rec['mine_equals_result_guards_C10']}; diffs {diffs} {rows_diff}")
    print(f"app_g17_mbt/cl > 0 on any NG row: {app_all_ng}")
    print(f"zero now but live in reference: {only_zero_now}; zero in reference but live now: {zero_in_ref_live_now}")
    print(f"dead by my rule: {dead_mine}; by frozen c10_check: {dead_frozen}")
    print(f"panel_counts equal result: {rec['panel_counts_equal_result']}; world roots equal: "
          f"{rec['world_roots_equal_result']}; feature_cols equal model: {rec['panel']['feature_cols_equal_model']}")
    print(f"written {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
