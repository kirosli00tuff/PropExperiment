"""B4 record-level synthetic run (P4.2 first bullet): generate 30 synthetic trade dates of ZM MBO and ZS / ZL MBP-1
records at the data facts' rates, store them under DERIVED/b4/synth/<seed>/ (synthetic only), and run BOTH label
implementations on them (Coder-A lab33, Coder-B labB) with the same day contexts; compare with the B3 harness's
rules. Output: DERIVED/b4/synth/<seed>/labels_{A,B}/<LABEL>/<D>.parquet, mismatches parquet, and a JSON summary
(counts per date and label). Synthetic data: no INTERFACE rule 1 limits apply, but only counts are printed.

Usage: uv run python reports/stage_e33_briefs/work/pipeline/tests_b4/run_synth_b4.py [--seed 4242] [--procs 3]
       [--stage gen,labels]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(HERE), str(PIPE), str(PIPE / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_streams as ss  # noqa: E402
import synth_labels as sl  # noqa: E402
import compare_b3 as cb  # noqa: E402
import data33  # noqa: E402
import guard33 as g  # noqa: E402

OUT = g.DERIVED / "b4" / "synth"
N_DATES = 30
ZS_PRM = {"fair0": 5600, "rate_day": 9.0, "rate_night": 2.5, "sigma_1m": 2.0, "iid": 910_001}
ZL_PRM = {"fair0": 6000, "rate_day": 6.0, "rate_night": 1.5, "sigma_1m": 4.0, "iid": 920_001}
LIMIT_HALF = 300  # ticks (+-30 USD around the open, ZM-like)


def ctx_spec(k: int, fair0: int) -> dict:
    """The day context of synthetic date k (same for A and B): limits in ticks, releases, exclusion."""
    lim: tuple[int, int] | None = (fair0 + LIMIT_HALF, fair0 - LIMIT_HALF)
    if k == 5:
        lim = (fair0 + 80, fair0 - 520)  # high-side proximity band starts about 4 ticks above the open
    if k == 6:
        lim = (fair0 + 520, fair0 - 80)  # low-side proximity band
    if k in (15, 19, 23):
        lim = None  # rule 5 skip case (and the D2 locked-book episodes on 15 and 23)
    return {"limits": lim, "releases": k in (2, 9, 13), "excluded": k == 27, "sigma": 3.15}


def _gen(task: tuple) -> dict:
    os.nice(10) if os.getpriority(os.PRIO_PROCESS, 0) < 10 else None
    k, day_s, seed, fair0, folder = task
    day = pd.Timestamp(day_s).date()
    prm = ss.ZMParams()
    if k >= 15:
        prm.iid, prm.iid_back = 900_003, 900_004
    ep = ss.DEFAULT_EPISODES.get(k, ss.Episodes())
    if k in (15, 23):  # D2: locked book exactly at a decision minute
        ep = ss.Episodes(crossed=((9, 14, 59.6), 1.0) if k == 15 else ((11, 29, 59.8), 2.0))
    t0 = time.time()
    zm, fair_end = ss.make_zm_day(day, seed + k, prm, ep, fair0=fair0)
    zs, _ = ss.make_mbp1_day(day, "ZS", seed + 1000 + k, ZS_PRM["iid"], ZS_PRM["fair0"], ZS_PRM["rate_day"],
                             ZS_PRM["rate_night"], ZS_PRM["sigma_1m"], data33.MBP1_SPLIT)
    zl, _ = ss.make_mbp1_day(day, "ZL", seed + 2000 + k, ZL_PRM["iid"], ZL_PRM["fair0"], ZL_PRM["rate_day"],
                             ZL_PRM["rate_night"], ZL_PRM["sigma_1m"], data33.MBP1_SPLIT)
    f = Path(folder)
    for name, arr in (("zm", zm), ("zs", zs), ("zl", zl)):
        (f / name).mkdir(parents=True, exist_ok=True)
        np.save(f / name / f"{day_s}.npy", arr)
    return {"k": k, "date": day_s, "iid": prm.iid, "fair0": fair0, "fair_end": fair_end, "n_zm": len(zm),
            "n_zs": len(zs), "n_zl": len(zl), "seconds": round(time.time() - t0, 1)}


def generate(seed: int, procs: int) -> list[dict]:
    """ZM fair carries from date to date, so dates are generated in order of their opening fair: the opening fair
    of date k is drawn up front (a random walk of daily closes) to allow parallel generation."""
    folder = OUT / str(seed)
    folder.mkdir(parents=True, exist_ok=True)
    dates = ss.synth_dates(N_DATES)
    rng = np.random.default_rng(seed)
    opens = (4000 + np.concatenate([[0], np.cumsum(rng.normal(0, 50, N_DATES - 1))])).round().astype(int)
    tasks = [(k, d.isoformat(), seed, int(opens[k]), str(folder)) for k, d in enumerate(dates)]
    with ProcessPoolExecutor(max_workers=procs) as pool:
        meta = sorted(pool.map(_gen, tasks), key=lambda r: r["k"])
    for m in meta:
        m["ctx"] = ctx_spec(m["k"], m["fair0"])
    (folder / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def _labels(task: tuple) -> dict:
    k, m, folder = task
    day = pd.Timestamp(m["date"]).date()
    zm = np.load(Path(folder) / "zm" / f"{m['date']}.npy")
    c = m["ctx"]
    rel = (ss.ct_ns(day, 11, 0),) if c["releases"] else ()
    lim = tuple(c["limits"]) if c["limits"] is not None else None
    ctx = sl.SynthCtx(day=day, iid=m["iid"], releases_ns=rel, limits_ticks=lim, excluded=c["excluded"],
                      sigma_ticks=c["sigma"])
    out = {}
    for impl, fn in (("A", sl.run_a), ("B", sl.run_b)):
        t0 = time.time()
        tabs = fn(zm, ctx)
        for lab, df in tabs.items():
            p = Path(folder) / f"labels_{impl}" / lab
            p.mkdir(parents=True, exist_ok=True)
            df.to_parquet(p / f"{m['date']}.parquet", index=False)
        out[impl] = round(time.time() - t0, 1)
    return {"date": m["date"], "seconds": out}


def labels(seed: int, procs: int) -> dict:
    folder = OUT / str(seed)
    meta = json.loads((folder / "meta.json").read_text())
    with ProcessPoolExecutor(max_workers=procs) as pool:
        list(pool.map(_labels, [(m["k"], m, str(folder)) for m in meta]))
    dates = [m["date"] for m in meta]
    res = cb.compare_labels(folder / "labels_A", folder / "labels_B", dates, list(sl.LABELS))
    cells = pd.DataFrame(res["cells"], columns=["family", "label", "date", "i", "column", "a", "b"])
    cells.to_parquet(folder / "label_mismatches.parquet", index=False)
    per_date = {f"{lab} {d}": list(v) for (lab, d), v in res["per_date"].items() if v[1] or v[2]}
    per_col: dict[str, dict[str, int]] = {}
    for lab, t in res["per_label"].items():
        per_col[lab] = {c: n for c, n in t.disagree.items() if n}
    summary = {"seed": seed, "dates": len(dates),
               "rows": {lab: t.rows for lab, t in res["per_label"].items()},
               "rows_with_mismatch": {lab: t.rows_with_mismatch for lab, t in res["per_label"].items()},
               "disagreeing_cells_by_column": per_col, "dates_with_mismatch": per_date,
               "missing": res["missing"],
               "row_ok_counts_A": {}, "entry_ok_counts_A": {}}
    for lab in sl.LABELS:
        ra = sum(int(pd.read_parquet(folder / "labels_A" / lab / f"{d}.parquet")["row_ok"].sum()) for d in dates)
        ea = sum(int(pd.read_parquet(folder / "labels_A" / lab / f"{d}.parquet")["entry_ok"].sum()) for d in dates)
        summary["row_ok_counts_A"][lab], summary["entry_ok_counts_A"][lab] = ra, ea
    (folder / "labels_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--stage", default="gen,labels")
    args = ap.parse_args(argv)
    os.nice(10)
    stages = set(args.stage.split(","))
    if "gen" in stages:
        meta = generate(args.seed, min(args.procs, 3))
        print(f"generated {len(meta)} dates; ZM records median {int(np.median([m['n_zm'] for m in meta]))}",
              flush=True)
    if "labels" in stages:
        s = labels(args.seed, min(args.procs, 3))
        print(json.dumps({k: s[k] for k in ("rows", "rows_with_mismatch", "disagreeing_cells_by_column",
                                             "dates_with_mismatch")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
