"""B4 record-level synthetic streams through BOTH feature builders (P4.2 first bullet).

30 target dates = the 30 OOF dates up to 2024-01-10 (they include the early close 2023-11-24 in their histories and
the scheduled late opens 2023-12-26 and 2024-01-02). Every date a builder asks for (targets, 21 history dates, the
previous date of a late open) gets synthetic ZM MBO and ZS / ZL MBP-1 records generated on demand (synth_streams, the
data facts' rates) inside that date's real session intervals (data.group_session), with the date's real front
instrument ids, so both builders run unchanged with the real calendar, fronts, releases and definitions. Only the
market-data loaders data33.load_zm / data33.load_mbp1 are replaced (in this process and its forked workers).

Outputs under DERIVED/b4/synthfeat/<seed>/: streams/{zm,zs,zl}/<D>.npy, A/ (build_features33 pass 1 and pass 2),
B/ (build_featB day raws and features), the comparison (compare_b3 rules) and independent oracle checks of C.1-C.4,
C.15, F4.1 and F4.6 from this script's own replay of the synthetic ZM stream. Synthetic data only.

Usage: uv run python .../tests_b4/run_synth_features.py [--seed 7] [--procs 3] [--stage gen,a,b,cmp]
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
IMPLB = PIPE.parent / "implB"
for _p in (str(HERE), str(PIPE), str(IMPLB), str(PIPE / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cal33  # noqa: E402
import data33  # noqa: E402
import guard33 as g  # noqa: E402
import synth_streams as ss  # noqa: E402
from data.group_session import session_intervals  # noqa: E402

OUT = g.DERIVED / "b4" / "synthfeat"
LAST_TARGET = date(2024, 1, 10)
N_TARGETS = 30
FAIR0 = {"ZM": 4000, "ZS": 5600, "ZL": 6000}
RATES = {"ZM": (14.0, 3.0), "ZS": (9.0, 2.5), "ZL": (6.0, 1.5)}
SIGMA = {"ZS": 2.0, "ZL": 4.0}
SEED = 7
_ROOT: Path | None = None


def targets() -> list[date]:
    oof = [d for d in cal33.oof_dates() if d <= LAST_TARGET]
    return oof[-N_TARGETS:]


def _fair(root: str, d: date) -> int:
    """Opening fair of D: a deterministic random walk over the universe's trade dates (daily SD 50 ticks)."""
    td = list(cal33.trade_dates())
    rng = np.random.default_rng(SEED * 1000 + {"ZM": 1, "ZS": 2, "ZL": 3}[root])
    walk = FAIR0[root] + np.concatenate([[0], np.cumsum(rng.normal(0, 30, len(td) - 1))]).round().astype(int)
    return int(walk[td.index(d)])


def _stream_path(kind: str, d: date) -> Path:
    assert _ROOT is not None
    return _ROOT / "streams" / kind / f"{d.isoformat()}.npy"


def generate(d: date) -> None:
    if all(_stream_path(k, d).exists() for k in ("zm", "zs", "zl")):
        return
    fr = cal33.fronts(d)
    iv = [(int(a), int(b)) for a, b in session_intervals(_grains(), d)]
    prm = ss.ZMParams(iid=int(fr["ZM"]), iid_back=int(fr["ZM"]) + 1, rate_day=RATES["ZM"][0],
                      rate_night=RATES["ZM"][1])
    k = d.toordinal()
    zm, _ = ss.make_zm_day(d, SEED * 100_000 + k, prm, ss.Episodes(), fair0=_fair("ZM", d), intervals=iv)
    out = {"zm": zm}
    for j, root in enumerate(("ZS", "ZL")):
        arr, _ = ss.make_mbp1_day(d, root, SEED * 100_000 + k + 7 * (j + 1), int(fr[root]), _fair(root, d),
                                  RATES[root][0], RATES[root][1], SIGMA[root], data33.MBP1_SPLIT, intervals=iv)
        out[root.lower()] = arr
    for kind, arr in out.items():
        p = _stream_path(kind, d)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(f".{p.stem}.{os.getpid()}.tmp.npy")
        np.save(tmp, arr)
        tmp.replace(p)


_GRAINS = None


def _grains():  # noqa: ANN202
    global _GRAINS
    if _GRAINS is None:
        import calB  # noqa: PLC0415
        _GRAINS = calB.grains()
    return _GRAINS


def fake_load_zm(d, cutoff_ns: int | None = None) -> np.ndarray:  # noqa: ANN001
    day = data33.as_date(d)
    generate(day)
    return data33.truncate(np.load(_stream_path("zm", day)), cutoff_ns)


def fake_load_mbp1(root: str, d, cutoff_ns: int | None = None) -> np.ndarray:  # noqa: ANN001
    day = data33.as_date(d)
    generate(day)
    return data33.truncate(np.load(_stream_path(root.lower(), day)), cutoff_ns)


def patch(root: Path) -> None:
    global _ROOT
    _ROOT = root
    data33.load_zm = fake_load_zm
    data33.load_mbp1 = fake_load_mbp1


def needed_dates(tg: list[date]) -> list[date]:
    s = set(tg)
    for d in tg:
        s |= set(cal33.previous_trade_dates(d, 21))
    return sorted(s)


def _pool(procs: int):  # noqa: ANN202
    return mp.get_context("fork").Pool(processes=procs, initializer=os.nice, initargs=(10,))


def stage_gen(root: Path, procs: int) -> None:
    need = needed_dates(targets())
    with _pool(procs) as pool:
        pool.map(generate, need)


def _a_pass1(d: date) -> dict:
    import build_features33 as bf  # noqa: PLC0415
    return bf.pass1(d, _ROOT / "A")


def stage_a(root: Path, procs: int) -> None:
    import build_features33 as bf  # noqa: PLC0415
    tg = targets()
    need = needed_dates(tg)
    (root / "A").mkdir(parents=True, exist_ok=True)
    with _pool(procs) as pool:
        pool.map(_a_pass1, need)
    for d in tg:
        bf.pass2(d, root / "A")


def _b_raw(d: date) -> str:
    import build_featB as bb  # noqa: PLC0415
    p = _ROOT / "B" / "dayraw" / f"{d.isoformat()}.npz"
    if not p.exists():
        bb.raw_job(d.isoformat(), str(p), None)
    return d.isoformat()


def stage_b(root: Path, procs: int) -> None:
    import build_featB as bb  # noqa: PLC0415
    import calB  # noqa: PLC0415
    tg = targets()
    need = sorted(set(needed_dates(tg)))
    (root / "B" / "dayraw").mkdir(parents=True, exist_ok=True)
    (root / "B" / "features").mkdir(parents=True, exist_ok=True)
    with _pool(procs) as pool:
        pool.map(_b_raw, need)
    for d in tg:
        raw = bb.load_raw(root / "B" / "dayraw" / f"{d}.npz")
        hist = []
        for h in calB.previous_dates(d, bb.N_HIST_RAW):
            hp = root / "B" / "dayraw" / f"{h}.npz"
            if not hp.exists():
                _b_raw(h)
            hist.append(bb.load_raw(hp))
        bb.write_features(d, raw, hist, root / "B" / "features")


# ---------------------------------------------------------------- independent oracle checks --
def oracle(root: Path, d: date) -> dict:
    """C.1, C.2, C.3, C.4, C.15 and F4.1, F4.6 recomputed here from the synthetic ZM stream with mbo_book31 (P0.3
    book; F_LAST updates), sigma_ZM from A's _day (sigma itself is compared A vs B separately)."""
    import mbo_book31 as mb  # noqa: PLC0415
    fr = int(cal33.fronts(d)["ZM"])
    rec = np.load(_stream_path("zm", d))
    rec = rec[rec["instrument_id"] == fr]
    grid = cal33.ct_ns(d, "08:35:00") + np.arange(273, dtype=np.int64) * 60 * 10**9
    tick = cal33.tick("ZM")
    book = mb.Book()
    upd_t, bid, ask, qb, qa, ok = [], [], [], [], [], []
    for ts, act, side, px, sz, oid, fl in zip(rec["ts_recv"].tolist(), rec["action"].tolist(), rec["side"].tolist(),
                                              rec["price"].tolist(), rec["size"].tolist(), rec["order_id"].tolist(),
                                              rec["flags"].tolist(), strict=True):
        if act == ss.R_:
            book.clear(bool(fl & ss.F_SNAP))
        elif book.started:
            if fl & ss.F_BAD:
                book.mark_bad()
            if book.in_snapshot and not fl & ss.F_SNAP:
                book.end_snapshot()
            if act in (ss.A_, ss.M_) and side in (ss.SB, ss.SA):
                bs = mb.BID if side == ss.SB else mb.ASK
                (book.add if act == ss.A_ else book.modify)(oid, bs, px, sz)
            elif act == ss.C_:
                book.cancel(oid, sz)
            if fl & ss.F_SNAP and fl & ss.F_LAST:
                book.end_snapshot()
        if fl & ss.F_LAST:
            b, a = book.best(mb.BID), book.best(mb.ASK)
            upd_t.append(ts)
            bid.append(-1 if b is None else b // tick)
            ask.append(-1 if a is None else a // tick)
            qb.append(0 if b is None else book.level_total(mb.BID, b))
            qa.append(0 if a is None else book.level_total(mb.ASK, a))
            ok.append(book.started and not book.bad and b is not None and a is not None and b < a)
    upd_t, bid, ask, qb, qa, ok = map(np.asarray, (upd_t, bid, ask, qb, qa, ok))

    def asof(u: np.ndarray) -> np.ndarray:
        return np.searchsorted(upd_t, u, side="right") - 1

    k = asof(grid)
    sig = json.loads((root / "A" / "_day" / f"{d}.json").read_text())["sigma_zm"]
    exp = {"C_1": np.arange(273) / 278.0, "C_2": (np.arange(273) / 278.0) ** 2,
           "C_3": np.where(ok[k], np.minimum(ask[k] - bid[k], 5), 0.0),
           "C_4": np.where(ok[k], np.log1p(qb[k] + qa[k]), 0.0),
           "C_15": np.full(273, 1.0 if d.month in (6, 7, 8) else 0.0)}
    m = (bid + ask) / 2.0
    k1 = asof(grid - 60 * 10**9)
    f41 = np.where(ok[k] & ok[k1] & (sig is not None), (m[k] - m[k1]) / (sig or 1.0), 0.0)
    exp["F4_1"] = np.clip(f41, -5, 5)  # checked for i >= 1 (i = 0 samples the 07:45 junction of the open axis)
    t0830 = cal33.ct_ns(d, "08:30:00")
    rp = np.zeros(273)
    for j in range(273):
        lo = asof(np.array([t0830]))[0]
        sel = np.arange(max(lo, 0), k[j] + 1)
        sel = sel[ok[sel] & ((upd_t[sel] > t0830) | (sel == lo))]
        if not ok[k[j]] or len(sel) == 0:
            rp[j] = 0.0
            continue
        hi_, lo_ = m[sel].max(), m[sel].min()
        rp[j] = 0.5 if hi_ == lo_ else (m[k[j]] - lo_) / (hi_ - lo_)
    exp["F4_6"] = rp
    res = {}
    import compare_b3 as cb  # noqa: PLC0415
    for impl, folder in (("A", root / "A"), ("B", root / "B" / "features")):
        df = pd.read_parquet(folder / f"{d}.parquet")
        res[impl] = {c: int((~cb.eq_feature(df[c].to_numpy()[1:], v[1:])).sum()) if c == "F4_1"
                     else int((~cb.eq_feature(df[c].to_numpy(), v)).sum()) for c, v in exp.items()}
    return res


def stage_cmp(root: Path) -> dict:
    import compare_b3 as cb  # noqa: PLC0415
    tg = [d.isoformat() for d in targets()]
    feat = cb.compare_features(root / "A", root / "B" / "features", tg)
    sig = cb.compare_sigma(root / "A", root / "B" / "features", None, tg)
    cells = pd.DataFrame(feat["cells"], columns=["family", "label", "date", "i", "column", "a", "b"])
    cells.to_parquet(root / "feature_mismatches.parquet", index=False)
    t = feat["total"]
    by_col = {c: n for c, n in t.disagree.items() if n}
    by_date = {d: v for d, v in feat["per_date"].items() if v[1]}
    sig_bad = [r["date"] for r in sig if cb._sig_eq(r["A_feat_zm"], r["B_feat_zm"]) != "agree"]
    orc = {d: oracle(root, date.fromisoformat(d)) for d in tg}
    orc_bad = {d: v for d, v in orc.items() if any(n for x in v.values() for n in x.values())}
    summary = {"targets": tg, "rows": t.rows, "rows_with_mismatch": t.rows_with_mismatch,
               "cells_by_column": by_col, "dates_with_mismatch": by_date, "nan_cells": feat["nan_cells"],
               "missing": feat["missing"], "sigma_zm_disagree_dates": sig_bad,
               "oracle_columns": ["C_1", "C_2", "C_3", "C_4", "C_15", "F4_1", "F4_6"],
               "oracle_mismatch_dates": orc_bad}
    (root / "features_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--stage", default="gen,a,b,cmp")
    args = ap.parse_args(argv)
    os.nice(10)
    root = OUT / str(args.seed)
    root.mkdir(parents=True, exist_ok=True)
    patch(root)
    # pin the code: import both builders now (forked workers inherit these modules) and record their sha256s
    import hashlib  # noqa: PLC0415
    import build_featB  # noqa: F401,PLC0415
    import build_features33  # noqa: F401,PLC0415
    files = [PIPE / f for f in ("feat33.py", "build_features33.py", "data33.py", "cal33.py")] + \
        [IMPLB / f for f in ("featB.py", "dayB.py", "replayB.py", "calB.py", "build_featB.py")]
    shas = {f.name: hashlib.sha256(f.read_bytes()).hexdigest()[:12] for f in files}
    (root / "code_used.json").write_text(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                                                    "sha256_12": shas}, indent=1))
    print(json.dumps(shas), flush=True)
    procs = max(1, min(args.procs, 3))
    for st in args.stage.split(","):
        t0 = time.time()
        if st == "gen":
            stage_gen(root, procs)
        elif st == "a":
            stage_a(root, procs)
        elif st == "b":
            stage_b(root, procs)
        elif st == "cmp":
            s = stage_cmp(root)
            print(json.dumps({k: s[k] for k in ("rows", "rows_with_mismatch", "cells_by_column",
                                                 "sigma_zm_disagree_dates", "oracle_mismatch_dates")}), flush=True)
        print(f"stage {st} {time.time() - t0:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
