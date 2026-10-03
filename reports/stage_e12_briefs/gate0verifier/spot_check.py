"""Step 5: recompute 20 gross targets from the step 2 parquet opens (training-window stores only).
Rows: h60 and h120 both ok, entry and both exits outside [r - 5 min, r + 30 min) of EVERY release
in reports/stage_e2b_release_calendar.json (a stricter condition than the vehicle's own list, so
no fill-guard deferral and no event-window cost applies). Seed = int(list sha256[:8], 16)."""
from __future__ import annotations

import json
import os
import pickle
from pathlib import Path

os.nice(10)
import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e12_briefs/gate0verifier"
STAGES = Path(os.path.expanduser("~/.cache/propexp_e12_phase1/stages"))
SEED = int("53e7ef57", 16)
NS_MIN = 60_000_000_000
# constants.UNIVERSE (read 2026-10-03): vehicle -> price-path root
PATH = {"MNQ": "NQ", "M2K": "RTY", "MYM": "YM", "ZT": "ZT", "ZF": "ZF", "ZN": "ZN", "TN": "TN",
        "ZB": "ZB", "UB": "UB", "6E": "6E", "6A": "6A", "6B": "6B", "6C": "6C", "6J": "6J", "6S": "6S",
        "6N": "6N", "MCL": "CL", "NG": "NG", "MGC": "GC", "MHG": "HG", "ZC": "ZC", "ZW": "ZW",
        "ZS": "ZS", "ZM": "ZM", "ZL": "ZL", "HE": "HE", "LE": "LE", "MBT": "MBT"}

import sys
sys.path.insert(0, str(REPO))
from rules.products import product  # static contract table (ticks per vendor unit)

with open(STAGES / "phase1_panel.pkl", "rb") as fh:
    frame = pickle.load(fh)["out"]["panel"].frame
rel = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())["releases"]
rel_ns = np.sort(np.array([pd.Timestamp(r["instant_utc"]).value for r in rel], dtype=np.int64))


def in_window(ts: np.ndarray) -> np.ndarray:
    """ts in [r - 5 min, r + 30 min) for some release r (any product)."""
    idx = np.searchsorted(rel_ns, ts + 5 * NS_MIN, side="right") - 1
    ok = idx >= 0
    r = rel_ns[np.clip(idx, 0, None)]
    return ok & (ts >= r - 5 * NS_MIN) & (ts < r + 30 * NS_MIN)


t = frame["decision_ts_ns"].to_numpy(np.int64)
e = frame["entry_ts_ns"].to_numpy(np.int64)
x60 = frame["exit_ts_ns_h60"].to_numpy(np.int64)
x120 = frame["exit_ts_ns_h120"].to_numpy(np.int64)
cand = (frame["ok_h60"].to_numpy(bool) & frame["ok_h120"].to_numpy(bool)
        & ~frame["release_window"].to_numpy(bool)
        & ~in_window(t) & ~in_window(t + 60 * NS_MIN) & ~in_window(t + 120 * NS_MIN))
cidx = np.flatnonzero(cand)
print("candidates", cidx.size, "of", len(frame))
# with no release nearby there must be no deferral
assert (e[cidx] == t[cidx]).all(), "a candidate entry was deferred"
assert (x60[cidx] == t[cidx] + 60 * NS_MIN).all() and (x120[cidx] == t[cidx] + 120 * NS_MIN).all()
rng = np.random.default_rng(SEED)
pick = np.sort(rng.choice(cidx, 20, replace=False))
rows = frame.iloc[pick]
recs = []
for i, (_, r) in zip(pick, rows.iterrows()):
    v = str(r["root"])
    path = PATH[v]
    files = sorted((REPO / "data/processed_step2" / path).glob("*_2019-05-06_2024-02-29_step2.parquet"))
    assert len(files) == 1, (path, files)
    need = [int(r["decision_ts_ns"]), int(r["decision_ts_ns"]) + 60 * NS_MIN,
            int(r["decision_ts_ns"]) + 120 * NS_MIN]
    pf = pq.ParquetFile(files[0])
    ts_type = pf.schema_arrow.field("ts_event").type
    import pyarrow as pa
    vals = pa.array(need, type=pa.int64())
    if pa.types.is_timestamp(ts_type):
        vals = vals.cast(ts_type)
    tbl = pq.read_table(files[0], columns=["ts_event", "open", "trade_date"],
                        filters=pc.field("ts_event").isin(vals))
    df = tbl.to_pandas()
    ts_col = df["ts_event"]
    ts_i = (ts_col.astype("int64") if not pd.api.types.is_datetime64_any_dtype(ts_col)
            else pd.to_datetime(ts_col, utc=True).astype("int64")).to_numpy()
    opens = dict(zip(ts_i.tolist(), df["open"].to_numpy(np.float64).tolist()))
    tds = dict(zip(ts_i.tolist(), df["trade_date"].astype(str).tolist()))
    pu = 1.0 / (product(path).vendor_price_factor * float(product(v).tick_size))
    o_e, o_60, o_120 = opens.get(need[0]), opens.get(need[1]), opens.get(need[2])
    rec = {"row": int(i), "root": v, "path": path, "trade_date": str(pd.Timestamp(r["trade_date"]).date()),
           "decision_utc": str(pd.Timestamp(int(r["decision_ts_ns"]), tz="UTC")),
           "per_unit": pu, "open_entry": o_e, "open_h60": o_60, "open_h120": o_120,
           "bar_trade_dates": sorted(set(tds.values())),
           "panel_entry_price": float(r["entry_price"]),
           "my_y_h60": None if (o_e is None or o_60 is None) else (o_60 - o_e) * pu,
           "panel_y_h60": float(r["y_gross_h60"]),
           "my_y_h120": None if (o_e is None or o_120 is None) else (o_120 - o_e) * pu,
           "panel_y_h120": float(r["y_gross_h120"])}
    rec["entry_match"] = o_e is not None and abs(o_e - rec["panel_entry_price"]) <= 1e-9 * max(1, abs(o_e))
    rec["h60_match"] = rec["my_y_h60"] is not None and abs(rec["my_y_h60"] - rec["panel_y_h60"]) <= 1e-6
    rec["h120_match"] = rec["my_y_h120"] is not None and abs(rec["my_y_h120"] - rec["panel_y_h120"]) <= 1e-6
    recs.append(rec)
out = pd.DataFrame(recs)
out.to_csv(OUT / "my_spot_check.csv", index=False)
summary = {"seed": SEED, "n_candidates": int(cidx.size), "n_checked": len(out),
           "entry_matches": int(out["entry_match"].sum()), "h60_matches": int(out["h60_match"].sum()),
           "h120_matches": int(out["h120_match"].sum()), "roots": sorted(out["root"].unique().tolist()),
           "per_unit_by_root": {k: float(v) for k, v in out.groupby("root")["per_unit"].first().items()},
           "max_abs_diff_h60": float((out["my_y_h60"] - out["panel_y_h60"]).abs().max()),
           "max_abs_diff_h120": float((out["my_y_h120"] - out["panel_y_h120"]).abs().max())}
(OUT / "my_spot_check.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary))
