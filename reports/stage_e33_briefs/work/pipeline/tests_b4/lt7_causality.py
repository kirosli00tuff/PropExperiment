"""B4 LT7 simulator causality (protocol P4.1 LT7), PREPARED; runs once the seed-1 null proof fold models exist.

At each of the 200 LT1 decision times (D, i, t) (draw: lt1_truncation.draw_times, seed 20261027) and each of the
20 seed-1 null proof configurations (S5 x {F15, T30} x the 10 P7.1 grid points) with i in G_h(D):
- the fold model is the one whose OOF block holds D (search33.make_folds on the 796 OOF dates), loaded with
  search33.load_fold_model from <proofs-dir>/seed1/search/<cid>/fold<k>.model.json;
- production decision: entry_ok of the production label table at (D, i) and search33.decide on the EVs from
  search33.predict_proba of the PRODUCTION feature row; recomputed decision: entry_ok from lab33 on the ZM records
  truncated at ts_recv <= t and decide on the feature row rebuilt from all streams truncated at t (LT1's
  build_features33 --cutoff-ns output under <features>/_lt1/<t>/). They must be equal (side or no trade);
- entry fill (for the decided side, and separately for both sides): production = lab33.entry_fill on the date's
  records (ts_recv < 13:20:00 CT); recomputed = lab33.entry_fill_from_records truncated at the production fill
  time (t + L, or the fallback update); made, fill time, price and flags must be equal, and the production fill time
  must equal the label table's <side>_entry_ns.

INTERFACE rule 1: no label value is read (only entry_ok and <side>_entry_ns of the label tables); fill prices enter
only the equality test; output is counts and mismatch locations.

Usage: uv run python .../tests_b4/lt7_causality.py --features DIR --labels DIR [--proofs-dir DIR] [--seed 1]
       [--draw JSON] --out JSON
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
for _p in (str(HERE), str(PIPE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cal33  # noqa: E402
import data33  # noqa: E402
import guard33 as g  # noqa: E402
import lab33  # noqa: E402
import search33 as s  # noqa: E402

PROOFS_DIR = g.DERIVED / "proofs"
GRID = ("L001A", "L001E", "L010A", "L010E", "L100A", "L100E", "G2050", "G2200", "G3050", "G3200")
CONFIGS = tuple(f"E33-S5{lab}{gp}" for lab in ("F15", "T30") for gp in GRID)
H = {"F15": 15, "T30": 30}


def fold_of(dates: list[str]) -> dict[str, int]:
    out = {}
    for f in s.make_folds(dates):
        for d in f.eval_dates:
            out[d] = f.k
    return out


def _model_path(pdir: Path, seed: int, cid: str, k: int) -> Path:
    return pdir / f"seed{seed}" / "search" / cid / f"fold{k}.model.json"


def models_ready(pdir: Path, seed: int, configs: tuple[str, ...] = CONFIGS) -> tuple[int, int]:
    have = sum(_model_path(pdir, seed, c, k).exists() for c in configs for k in range(1, 7))
    return have, len(configs) * 6


def _day_inputs(d: str) -> lab33.DayInputs:
    excl, _ = cal33.excluded(d)
    return lab33.DayInputs(date=d, t0_ns=cal33.ct_ns(d, "08:35:00"), close_ns=cal33.ct_ns(d, "13:13:00"),
                           session_end_ns=cal33.ct_ns(d, "13:20:00"),
                           releases=tuple(int(r) for r in cal33.releases(d)), limits=cal33.limits(d),
                           tick=cal33.tick("ZM"), excluded=bool(excl), sigma_zm=None)


def _entry_ok_from(hist: lab33.BookHistory, day: lab33.DayInputs, label: str, t: int) -> bool:
    """entry_ok at t from lab33's entry rules (P3.6 first paragraph, R-B3-D2 included in lab33) on a book replayed
    from records truncated at t; the entry rules use only the book as of t and the calendar."""
    if day.excluded:
        return False
    _kind, h = lab33.LABELS[label]
    return not any(lab33.entry_rule_fails(hist, day, h, t).values())


REASONS = ("usable", "usable_on_excluded_date", "not_in_grid", "no_production_features", "no_lt1_rebuild",
           "no_label_table")
_CTX: dict = {}


def _new_cnt(configs: tuple[str, ...]) -> dict:
    return {"draws": 0, "checks": 0, "decision_equal": 0, "decision_mismatch": [], "decided_trades": 0,
            "fill_checks": 0, "fill_equal": 0, "fill_mismatch": [], "fill_vs_table_checks": 0,
            "fill_vs_table_mismatch": [], "both_side_fill_checks": 0, "both_side_fill_equal": 0,
            "both_side_fill_mismatch": [], "entry_ok_equal": 0, "entry_ok_checks": 0, "entry_ok_mismatch": [],
            "skipped_not_in_grid": 0, "missing_inputs": [],
            "per_config": {c: {r: 0 for r in REASONS} for c in configs}}


def _merge(a: dict, b: dict) -> None:
    for k, v in b.items():
        if k == "per_config":
            for c, rs in v.items():
                for r, n in rs.items():
                    a[k][c][r] += n
        elif isinstance(v, list):
            a[k].extend(v)
        elif isinstance(v, int):
            a[k] += v


def _date_job(job: tuple[str, list[dict]]) -> dict:
    """LT7 on one date's draws (forked worker; _CTX set before the fork). Counts only."""
    os.nice(10) if os.getpriority(os.PRIO_PROCESS, 0) < 10 else None
    d, items = job
    pdir, seed, configs, labels = _CTX["pdir"], _CTX["seed"], _CTX["configs"], _CTX["labels"]
    fdir, ldir, fold = _CTX["fdir"], _CTX["ldir"], _CTX["fold"]
    cnt = _new_cnt(configs)
    pc = cnt["per_config"]
    pf = fdir / f"{d}.parquet"
    if not pf.exists():
        cnt["missing_inputs"].extend(f"{d} {x['i']}: no production feature table" for x in items)
        for x in items:
            for cid in configs:
                pc[cid]["no_production_features"] += 1
        return cnt
    front = int(cal33.fronts(d)["ZM"])
    stop = cal33.ct_ns(d, "13:20:00")
    rec = data33.load_zm(d, cutoff_ns=stop - 1)
    tick = cal33.tick("ZM")
    day = _day_inputs(d)
    hist_full = lab33.replay(rec, front, tick, end_ns=stop - 1)
    prod_feat = pd.read_parquet(g.check_path(pf)).set_index("i")
    lab_tabs = {}
    for label in labels:
        lp = ldir / label / f"{d}.parquet"
        if lp.exists():
            lab_tabs[label] = pd.read_parquet(g.check_path(lp), columns=[
                "i", "entry_ok", "long_entry_ns", "short_entry_ns"]).set_index("i")
    models: dict[tuple[str, int], dict] = {}
    for x in items:
        i, t = int(x["i"]), int(x["t_ns"])
        lt1 = fdir / "_lt1" / str(t) / f"{d}.parquet"
        if not lt1.exists():
            cnt["missing_inputs"].append(f"{d} {i}: no LT1 rebuild")
            for cid in configs:
                pc[cid]["no_lt1_rebuild"] += 1
            continue
        cnt["draws"] += 1
        tr_feat = pd.read_parquet(g.check_path(lt1)).set_index("i")
        hist_t = lab33.replay(rec, front, tick, end_ns=t)
        trunc_cache: dict[int, lab33.BookHistory] = {}
        per_label = {}
        for label in labels:
            kind, h = lab33.LABELS[label]
            if i > 277 - h:
                continue
            if label not in lab_tabs or i not in lab_tabs[label].index:
                cnt["missing_inputs"].append(f"{d} i={i} {label}: no production label row")
                continue
            ok_prod = bool(lab_tabs[label].loc[i, "entry_ok"])
            ok_tr = _entry_ok_from(hist_t, day, label, t)
            cnt["entry_ok_checks"] += 1
            cnt["entry_ok_equal"] += int(ok_prod == ok_tr)
            if ok_prod != ok_tr:
                cnt["entry_ok_mismatch"].append(f"{d} i={i} {label}")
            fills = {}
            for side in (lab33.LONG, lab33.SHORT):
                ef = lab33.entry_fill(hist_full, kind, h, t, side)
                cut = ef.fill_ns if ef.made else lab33.planned_exit_ns(kind, h, t) - 1
                if cut not in trunc_cache:
                    trunc_cache[cut] = lab33.replay(rec, front, tick, end_ns=cut)
                rf = lab33.entry_fill(trunc_cache[cut], kind, h, t, side)
                same = (ef.made, ef.fill_ns, ef.price, ef.flags) == (rf.made, rf.fill_ns, rf.price, rf.flags)
                sname = "long" if side == lab33.LONG else "short"
                cnt["both_side_fill_checks"] += 1
                cnt["both_side_fill_equal"] += int(same)
                if not same:
                    cnt["both_side_fill_mismatch"].append(f"{d} i={i} {label} {sname}")
                if ok_prod:
                    cnt["fill_vs_table_checks"] += 1
                    if int(lab_tabs[label].loc[i, f"{sname}_entry_ns"]) != (ef.fill_ns if ef.made else -1):
                        cnt["fill_vs_table_mismatch"].append(f"{d} i={i} {label} {sname}")
                fills[side] = same
            per_label[label] = (ok_prod, ok_tr, fills)
        for cid in configs:
            label = cid[6:9]
            if i > 277 - lab33.LABELS[label][1]:
                cnt["skipped_not_in_grid"] += 1
                pc[cid]["not_in_grid"] += 1
                continue
            if label not in per_label:
                pc[cid]["no_label_table"] += 1
                continue
            pc[cid]["usable_on_excluded_date" if day.excluded else "usable"] += 1
            ok_prod, ok_tr, fills = per_label[label]
            k = fold[d]
            if (cid, k) not in models:
                models[(cid, k)] = s.load_fold_model(_model_path(pdir, seed, cid, k))
            m = models[(cid, k)]
            cols = list(m["columns"])
            ev = []
            for frame in (prod_feat, tr_feat):
                p = s.predict_proba(m, frame.loc[[i], cols].to_numpy(dtype=np.float64))
                el, es = s.expected_values(p, np.array(m["mu_long"]), np.array(m["mu_short"]))
                ev.append((float(el[0]), float(es[0])))
            dec_prod = s.decide(*ev[0]) if ok_prod else 0
            dec_tr = s.decide(*ev[1]) if ok_tr else 0
            cnt["checks"] += 1
            cnt["decision_equal"] += int(dec_prod == dec_tr)
            if dec_prod != dec_tr:
                cnt["decision_mismatch"].append(f"{cid} {d} i={i}")
            if dec_prod != 0:
                cnt["decided_trades"] += 1
                cnt["fill_checks"] += 1
                same = fills[lab33.LONG if dec_prod > 0 else lab33.SHORT]
                cnt["fill_equal"] += int(same)
                if not same:
                    cnt["fill_mismatch"].append(f"{cid} {d} i={i}")
    return cnt


def run(args: argparse.Namespace) -> dict:
    """Per-configuration accounting (E.33b): every (draw, configuration) pair is counted once under REASONS:
    usable (a decision check), usable_on_excluded_date (a check on a P1.4-excluded date: no trade on both sides),
    not_in_grid (i > 277 - h), no_production_features, no_lt1_rebuild, no_label_table (no label row at (D, i))."""
    pdir = Path(args.proofs_dir)
    configs = tuple(args.configs.split(",")) if args.configs else CONFIGS
    have, need = models_ready(pdir, args.seed, configs)
    if have < need:
        return {"status": "pending", "models_found": have, "models_needed": need}
    draw = json.loads(Path(args.draw).read_text())["times"]
    oof = [x.isoformat() for x in cal33.oof_dates()]
    by_date: dict[str, list] = {}
    for x in draw:
        by_date.setdefault(x["date"], []).append(x)
    _CTX.update(pdir=pdir, seed=args.seed, configs=configs, labels=sorted({c[6:9] for c in configs}),
                fdir=Path(args.features), ldir=Path(args.labels), fold=fold_of(oof))
    cnt = _new_cnt(configs)
    jobs = sorted(by_date.items())
    procs = max(1, min(int(getattr(args, "procs", 1)), 3))
    if procs == 1:
        for j in jobs:
            _merge(cnt, _date_job(j))
    else:
        import multiprocessing as mp  # noqa: PLC0415
        with mp.get_context("fork").Pool(processes=procs) as pool:
            for part in pool.imap_unordered(_date_job, jobs):
                _merge(cnt, part)
    for k in ("decision_mismatch", "fill_mismatch", "fill_vs_table_mismatch", "both_side_fill_mismatch",
              "entry_ok_mismatch", "missing_inputs"):
        cnt[k] = sorted(cnt[k])
    cnt["draws_total"] = len(draw)
    cnt["status"] = "ran"
    return cnt


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True, help="A's production features <sha> dir (with _lt1/)")
    ap.add_argument("--labels", required=True, help="A's production labels <sha> dir")
    ap.add_argument("--proofs-dir", default=str(PROOFS_DIR))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--draw", default=str(PIPE.parent / "LT1_draw.json"))
    ap.add_argument("--configs", default=None, help="comma list (dry runs); default the 20 LT7 configurations")
    ap.add_argument("--procs", type=int, default=1, help="dates in parallel (at most 3)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    os.nice(10)
    t0 = time.time()
    res = run(args)
    res["seconds"] = round(time.time() - t0, 1)
    Path(args.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res.items() if k != "per_config"}),
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
