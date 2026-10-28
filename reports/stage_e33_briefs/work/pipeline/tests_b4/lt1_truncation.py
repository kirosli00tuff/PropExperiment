"""B4 LT1 truncation test (protocol P4.1 LT1) for Coder-A's production feature builder.

Draw (stated): OOF = cal33.oof_dates() (the 796 dates, sorted); grid = every (date, i) with i = 0..272
(796 x 273 = 217,308 decision times, excluded dates included because features are computed on every date);
idx = numpy.random.default_rng(20261027).choice(217308, 200, replace=False); date = OOF[idx // 273],
i = idx % 273, t = 08:35:00 CT + i minutes on that date; the 200 times are processed in (date, i) order.

For each time t: build_features33.build_cutoff(t, prior) re-streams D from ZM MBO, ZS and ZL MBP-1 and the
definitions truncated at ts_recv <= t (prior "recompute" also re-streams the 21 history dates, whose records all
precede D's window), writing <features>/_lt1/<t>/<D>.parquet; the row with t_ns == t must equal the production
row (date, i) of <features>/<D>.parquet in every one of the 59 columns within G7
(|a - b| <= max(1e-9 max(|a|, |b|), 1e-12)), and the rebuilt table must hold no row with t_ns > t.

Usage: uv run python .../tests_b4/lt1_truncation.py --features DIR [--n 200] [--limit K] [--prior recompute]
       [--draw-only] --out JSON
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(HERE), str(PIPE), str(PIPE / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cal33  # noqa: E402
import guard33 as g  # noqa: E402
import compare_b3 as cb  # noqa: E402

LT1_SEED = 20261027
N_MIN = 273
DRAW_PATH = PIPE.parent / "LT1_draw.json"


def draw_times(n: int = 200) -> list[dict]:
    oof = [d.isoformat() for d in cal33.oof_dates()]
    if len(oof) != 796:
        raise SystemExit("expected 796 OOF dates")
    idx = np.random.default_rng(LT1_SEED).choice(len(oof) * N_MIN, n, replace=False)
    out = []
    for x in idx.tolist():
        d, i = oof[x // N_MIN], x % N_MIN
        out.append({"date": d, "i": i, "t_ns": cal33.ct_ns(d, "08:35:00") + i * 60 * 10**9,
                    "excluded": bool(cal33.excluded(d)[0])})
    return sorted(out, key=lambda r: (r["date"], r["i"]))


def check_one(fdir: Path, x: dict, prior: str) -> dict:
    import build_features33 as bf  # noqa: PLC0415

    t0 = time.time()
    d, i, t = x["date"], int(x["i"]), int(x["t_ns"])
    bf.build_cutoff(t, prior, fdir.parent)
    rebuilt = pd.read_parquet(g.check_path(fdir / "_lt1" / str(t) / f"{d}.parquet"))
    prod = pd.read_parquet(g.check_path(fdir / f"{d}.parquet"))
    res = {"date": d, "i": i, "seconds": 0.0, "rows_after_t": int((rebuilt["t_ns"] > t).sum()), "bad_cols": []}
    ra, rb = prod[prod["i"] == i], rebuilt[rebuilt["i"] == i]
    if len(ra) != 1 or len(rb) != 1 or int(rb["t_ns"].iloc[0]) != t:
        res["bad_cols"].append("__row__")
    else:
        a = ra[list(cb.FEATURE_COLS)].to_numpy(dtype=np.float64)[0]
        b = rb[list(cb.FEATURE_COLS)].to_numpy(dtype=np.float64)[0]
        ok = cb.eq_feature(a, b)
        res["bad_cols"] = [c for c, o in zip(cb.FEATURE_COLS, ok, strict=True) if not o]
    res["seconds"] = round(time.time() - t0, 1)
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default=None, help="A's production DERIVED/features/<sha> dir")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--limit", type=int, default=None, help="process only the first K draws (timing)")
    ap.add_argument("--prior", choices=("recompute", "production"), default="recompute")
    ap.add_argument("--draw-only", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    os.nice(10)
    draw = draw_times(args.n)
    DRAW_PATH.write_text(json.dumps({"seed": LT1_SEED, "n": args.n, "rule": __doc__.split("\n\n")[1],
                                     "times": draw}, indent=1))
    print(f"draw {len(draw)} times on {len({x['date'] for x in draw})} dates "
          f"({sum(x['excluded'] for x in draw)} on excluded dates) -> {DRAW_PATH}", flush=True)
    if args.draw_only:
        return 0
    fdir = Path(args.features)
    out_path = Path(args.out)
    done: dict = json.loads(out_path.read_text()) if out_path.exists() else {"results": []}
    seen = {(r["date"], r["i"]) for r in done["results"]}
    todo = [x for x in draw if (x["date"], x["i"]) not in seen]
    if args.limit is not None:
        todo = todo[: max(0, args.limit - len(seen))]
    missing = [x for x in todo if not (fdir / f"{x['date']}.parquet").exists()]
    if missing:
        print(f"production rows missing for {len(missing)} draws (dates without a production table); "
              f"first {missing[0]['date']}", flush=True)
        todo = [x for x in todo if x not in missing]
    for x in todo:
        r = check_one(fdir, x, args.prior)
        done["results"].append(r)
        out_path.write_text(json.dumps(done, indent=1))  # resumable
        print(f"{r['date']} i={r['i']} s={r['seconds']} bad_cols={len(r['bad_cols'])} "
              f"rows_after_t={r['rows_after_t']}", flush=True)
    res = done["results"]
    print(f"LT1 checked {len(res)}; with mismatch {sum(1 for r in res if r['bad_cols'])}; rows after t "
          f"{sum(r['rows_after_t'] for r in res)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
