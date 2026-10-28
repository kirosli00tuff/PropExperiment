"""E.33 feature builder, Coder-A (brief_FeatureCoder deliverable 1; INTERFACE.md 4.1).

Resumable per-date builder of the P4 features (feat33). Pass 1 per trade date streams the date's
records (data33, through guard33) and writes DERIVED/features/<code_sha12>/_p1/<D>.npz; pass 2
per date reads the pass-1 tables of D and the 21 trade dates before it and writes
_day/<D>.json (sigma_zm, sigma_zs, sigma_zl in ticks, null when undefined; the fronts) for every
date it covers and <D>.parquet (date, i, t_ns, the 59 features) for OOF dates. A DONE marker per
date and pass; nice 10; at most --procs processes (default 3).

Usage (repo root):
  uv run python reports/stage_e33_briefs/work/pipeline/build_features33.py --dates b3
  ... --dates 2022-02-15,2022-07-27      ... --dates all       ... --dates oof
  ... --cutoff-ns <ns> [--prior production|recompute]   (LT1: every input stream truncated at
      ts_recv <= cutoff; output under _lt1/<cutoff>/, rows with t_ns <= cutoff only)

Rule (INTERFACE 2.1): this builder computes features only; it prints counts and timings, never a
statistic of labels or returns.
"""

# ruff: noqa: I001 - guard33 sets sys.path before the E.31 and repo imports
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import guard33 as g  # noqa: E402
import cal33  # noqa: E402
import data33  # noqa: E402
import feat33 as F  # noqa: E402
from data.group_session import session_intervals  # noqa: E402

# READING FA-28: the code_sha12 files (feature code and the E.31 book it runs on)
FEATURE_CODE = (HERE / "feat33.py", HERE / "build_features33.py", F._PILOT / "mbo_book31.py")
DEPENDENCIES = (HERE / "data33.py", HERE / "cal33.py", HERE / "guard33.py")
OUT_ROOT = g.DERIVED / "features"
B3_SEED, B3_N = 20261028, 20  # reports/stage_e33_STATE.md, B3 dates rule (14:45)
MAX_PROCS = 4  # INTERFACE 2.4


# ------------------------------------------------------------------ identity ----
def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_sha12() -> str:
    """First 12 hex of the sha256 of the concatenated feature code files (INTERFACE 4.1)."""
    h = hashlib.sha256()
    for p in FEATURE_CODE:
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def out_dir(root: Path = OUT_ROOT) -> Path:
    return root / code_sha12()


def write_manifest(folder: Path) -> None:
    man = {"code_sha12": code_sha12(),
           "feature_code": {str(p.relative_to(g.REPO)): file_sha(p) for p in FEATURE_CODE},
           "dependencies": {str(p.relative_to(g.REPO)): file_sha(p) for p in DEPENDENCIES},
           "protocol_sha256": file_sha(g.REPO / "reports" / "stage_e32_discovery_protocol.md"),
           "columns": ["date", "i", "t_ns", *F.FEATURES]}
    _atomic_text(folder / "manifest.json", json.dumps(man, indent=1))


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


# ------------------------------------------------------------------ dates ----
def b3_dates() -> list[date]:
    """STATE B3 dates rule: OOF sorted; idx = default_rng(20261028).choice(796, 20,
    replace=False); dates = sorted(OOF[idx])."""
    oof = sorted(cal33.oof_dates())
    idx = np.random.default_rng(B3_SEED).choice(len(oof), B3_N, replace=False)
    return sorted(oof[int(k)] for k in idx)


def parse_dates(spec: str) -> list[date]:
    if spec == "b3":
        return b3_dates()
    if spec == "all":
        return list(cal33.trade_dates())
    if spec == "oof":
        return list(cal33.oof_dates())
    return sorted(data33.as_date(x.strip()) for x in spec.split(",") if x.strip())


def history(day: date) -> list[date | None]:
    """The N_HIST = 21 trade dates before D, oldest first, None-padded at the start of data."""
    prev = cal33.previous_trade_dates(day, F.N_HIST)
    return [None] * (F.N_HIST - len(prev)) + list(prev)


def day_info(day: date) -> F.DayInfo:
    fr = cal33.fronts(day)
    prev = cal33.previous_trade_dates(day, 1)
    seg = int(cal33.segment_id(day))
    return F.DayInfo(day=day, fronts=(int(fr["ZM"]), int(fr["ZS"]), int(fr["ZL"])),
                     seg=seg, releases=tuple(cal33.releases(day)),
                     expiry_dates=cal33.expiry_trade_dates(day),
                     monday_or_after_closure=bool(cal33.monday_or_after_closure(day)),
                     jja=bool(cal33.jja(day)),
                     prev_same_seg=bool(prev) and int(cal33.segment_id(prev[0])) == seg)


def day_axis(day: date) -> tuple[F.Axis, date | None]:
    """Ruling FD1/FD2 (READING FA-30): D's actual open intervals from the grains calendar
    (data.group_session.session_intervals: early halts, scheduled late opens); when D has no
    overnight session, the previous trade date's day session (its last open interval) comes
    first. Returns the axis and the previous date whose records it needs (or None)."""
    cal = cal33._calendar()
    ivs = session_intervals(cal, day)
    if not ivs:
        raise RuntimeError(f"{day}: no open interval")
    if len(ivs) >= 2:
        return F.build_axis(day, ivs), None
    prev = cal33.previous_trade_dates(day, 1)
    if not prev:
        raise RuntimeError(f"{day}: no overnight session and no previous trade date")
    return F.build_axis(day, ivs, session_intervals(cal, prev[0])[-1]), prev[0]


# ------------------------------------------------------------------ pass 1 ----
def p1_path(folder: Path, day: date) -> Path:
    return folder / "_p1" / f"{day.isoformat()}.npz"


def pass1(day: date, folder: Path, cutoff_ns: int | None = None) -> dict:
    """Stream D once and store its pass-1 tables (resumable: skipped when DONE)."""
    path = p1_path(folder, day)
    done = path.with_suffix(".DONE")
    if done.is_file():
        return json.loads(done.read_text(encoding="utf-8"))
    t0 = time.time()
    fr = cal33.fronts(day)
    ticks = {r: int(cal33.tick(r)) for r in ("ZM", "ZS", "ZL")}
    ax, prev = day_axis(day)
    days = [day] if prev is None else [prev, day]  # the previous day's records first (FD2)
    zm = np.concatenate([data33.load_zm(d, cutoff_ns) for d in days])
    zs = np.concatenate([data33.load_mbp1("ZS", d, cutoff_ns) for d in days])
    zl = np.concatenate([data33.load_mbp1("ZL", d, cutoff_ns) for d in days])
    t_load = time.time() - t0
    p1 = F.stream_day(day, zm, zs, zl, fr, ticks, ax)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.npz")
    np.savez(tmp, **p1)
    tmp.replace(path)
    info = {"date": day.isoformat(), "axis_marks": int(len(ax.marks)), "prev_date":
            None if prev is None else prev.isoformat(),
            "records": {"ZM": int(len(zm)), "ZS": int(len(zs)),
                                                 "ZL": int(len(zl))},
            "load_s": round(t_load, 3), "stream_s": round(time.time() - t0 - t_load, 3),
            "maxrss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
            "cutoff_ns": cutoff_ns}
    _atomic_text(done, json.dumps(info))
    return info


def load_p1(folder: Path, day: date) -> dict:
    path = p1_path(folder, day)
    if not path.with_suffix(".DONE").is_file():
        raise FileNotFoundError(f"pass 1 of {day} not done: {path}")
    with np.load(g.check_path(path)) as z:
        return {k: z[k] for k in z.files}


# ------------------------------------------------------------------ pass 2 ----
def _ref_json(ref: F.Refs) -> dict:
    ols = None if ref.ols is None else dict(zip(("a", "b_S", "b_L", "sd_e_ticks", "n", "dates"),
                                                ref.ols, strict=True))
    return {"obar": ref.obar, "dbar_sum": ref.dbar_sum, "sbar5": ref.sbar5,
            "rbar15": ref.rbar15, "lam_med": ref.lam_med, "f13_ols": ols, "gC": ref.gc,
            "GAP": ref.gap, "counts": ref.counts}


def pass2(day: date, folder: Path, p1_folders: dict[date, Path] | None = None,
          cutoff_ns: int | None = None) -> dict:
    """Features of D from the pass-1 tables of D and the 21 trade dates before D."""
    done = folder / f"{day.isoformat()}.DONE"
    if done.is_file():
        return json.loads(done.read_text(encoding="utf-8"))
    t0 = time.time()
    src = p1_folders or {}
    cur = (load_p1(src.get(day, folder), day), day_info(day))
    hist = [None if h is None else (load_p1(src.get(h, folder), h), day_info(h))
            for h in history(day)]
    ref = F.build_refs(cur, hist)
    fr = cal33.fronts(day)
    dayj = {"date": day.isoformat(), "fronts": {k: int(v) for k, v in fr.items()},
            "sigma_zm": ref.sigma["zm"], "sigma_zs": ref.sigma["zs"], "sigma_zl": ref.sigma["zl"],
            "segment": int(cal33.segment_id(day)), "n_history": sum(h is not None for h in hist),
            "refs": _ref_json(ref), "cutoff_ns": cutoff_ns}
    _atomic_text(folder / "_day" / f"{day.isoformat()}.json", json.dumps(dayj, indent=1))
    info = {"date": day.isoformat(), "rows": 0, "invalid": {}}
    if day in set(cal33.oof_dates()):
        vals, oks = F.features_day(cur[0], cur[1], ref)
        t_ns = cur[0]["wall_ns"][:F.N_GRID].astype(np.int64)  # t = 08:35 + i min on D (wall)
        keep = np.ones(F.N_GRID, bool) if cutoff_ns is None else t_ns <= cutoff_ns
        _write_parquet(folder / f"{day.isoformat()}.parquet", day, vals[keep], t_ns[keep],
                       np.arange(F.N_GRID)[keep])
        info["rows"] = int(keep.sum())
        info["invalid"] = {f: int((~oks[keep, k]).sum()) for k, f in enumerate(F.FEATURES)
                           if (~oks[keep, k]).any()}
    info["pass2_s"] = round(time.time() - t0, 3)
    _atomic_text(done, json.dumps(info))
    return info


def _write_parquet(path: Path, day: date, vals: np.ndarray, t_ns: np.ndarray,
                   ii: np.ndarray) -> None:
    import pandas as pd

    df = pd.DataFrame(vals.astype(np.float64), columns=F.FEATURES)
    df.insert(0, "t_ns", t_ns.astype(np.int64))
    df.insert(0, "i", ii.astype(np.int16))
    df.insert(0, "date", day.isoformat())
    tmp = path.with_name(f".{path.name}.tmp")
    df.to_parquet(tmp, index=False)
    tmp.replace(path)


# ------------------------------------------------------------------ orchestration ----
def set_nice(target: int = 10) -> None:
    """INTERFACE 2.4: real-data runs at niceness 10 (os.nice adds; workers inherit it)."""
    cur = os.nice(0)
    if cur < target:
        os.nice(target - cur)


def _run_pool(fn, items: list, procs: int) -> list:  # noqa: ANN001
    if procs <= 1 or len(items) <= 1:
        return [fn(*it) for it in items]
    with ProcessPoolExecutor(max_workers=procs) as ex:
        return list(ex.map(fn, *zip(*items, strict=True)))


def needed_pass1(targets: list[date]) -> list[date]:
    need = set(targets)
    for d in targets:
        need.update(h for h in history(d) if h is not None)
    return sorted(need)


def build(targets: list[date], procs: int, root: Path = OUT_ROOT) -> dict:
    folder = out_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    write_manifest(folder)
    t0 = time.time()
    p1_dates = needed_pass1(targets)
    p1_info = _run_pool(pass1, [(d, folder) for d in p1_dates], procs)
    t1 = time.time()
    p2_info = _run_pool(pass2, [(d, folder) for d in targets], procs)
    return {"folder": str(folder), "pass1_dates": len(p1_dates), "pass2_dates": len(targets),
            "pass1_wall_s": round(t1 - t0, 1), "pass2_wall_s": round(time.time() - t1, 1),
            "pass1": p1_info, "pass2": p2_info}


def build_cutoff(cutoff_ns: int, prior: str, root: Path = OUT_ROOT) -> dict:
    """LT1 (P4.1): every input stream truncated at ts_recv <= cutoff_ns. The trade date D holding
    the cutoff is re-streamed from truncated records; the 21 dates before D are re-streamed too
    (prior="recompute"; their records all have ts_recv < D's window start <= cutoff, so the
    truncation leaves them whole) or read from the production pass 1 (prior="production").
    cal33's C.7 and fronts read definitions with ts_recv <= 08:30:00 CT on D and the manifests'
    symbology; a cutoff before 08:30:00 on D is refused, so that definitions read lie inside the
    truncated stream."""
    day = next((d for d in cal33.trade_dates()
                if cal33.day_bounds(d)[0] <= cutoff_ns < cal33.day_bounds(d)[1]), None)
    if day is None:
        raise ValueError(f"cutoff {cutoff_ns} is not inside a trade date")
    if cutoff_ns < cal33.ct_ns(day, "08:30:00"):  # READING FA-26
        raise ValueError("cutoff before 08:30:00 CT: C.7's definitions would exceed it")
    prod = out_dir(root)
    folder = prod / "_lt1" / str(cutoff_ns)
    folder.mkdir(parents=True, exist_ok=True)
    pass1(day, folder, cutoff_ns)
    src = {day: folder}
    for h in history(day):
        if h is None:
            continue
        if prior == "recompute":
            pass1(h, folder, cutoff_ns)
            src[h] = folder
        else:
            src[h] = prod
    return pass2(day, folder, src, cutoff_ns)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dates", default="b3", help="b3 | all | oof | comma list of YYYY-MM-DD")
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--cutoff-ns", type=int, default=None)
    ap.add_argument("--prior", choices=("production", "recompute"), default="recompute")
    ap.add_argument("--root", default=str(OUT_ROOT))
    ap.add_argument("--summary", default=None, help="write the run summary JSON here")
    args = ap.parse_args(argv)
    set_nice(10)
    if not 1 <= args.procs <= MAX_PROCS:
        raise SystemExit(f"--procs must be 1..{MAX_PROCS}")
    root = Path(args.root)
    g.check_path(root)
    if args.cutoff_ns is not None:
        res = build_cutoff(args.cutoff_ns, args.prior, root)
        print(json.dumps({"cutoff_ns": args.cutoff_ns, "rows": res.get("rows")}))
        return 0
    targets = parse_dates(args.dates)
    res = build(targets, args.procs, root)
    if args.summary:
        _atomic_text(Path(args.summary), json.dumps(res, indent=1))
    inv_tot: dict[str, int] = {}
    for it in res["pass2"]:
        for k, v in it.get("invalid", {}).items():
            inv_tot[k] = inv_tot.get(k, 0) + v
    print(json.dumps({"folder": res["folder"], "pass1_dates": res["pass1_dates"],
                      "pass2_dates": res["pass2_dates"], "pass1_wall_s": res["pass1_wall_s"],
                      "pass2_wall_s": res["pass2_wall_s"],
                      "rows": sum(it["rows"] for it in res["pass2"]), "invalid": inv_tot}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
