"""E.31 stats layer: the engine's per-day tables -> spec statistics, the kill rule and the report.

Usage (repo root):
  uv run python reports/stage_e31_briefs/work/pilot/stats31.py --runs DIR --out-json PATH \
      --out-md PATH --expect-dates FILE [--boot 2000 --seed 31]

Completeness gate (lead, 12:43 PDT): FILE lists the purchased trade dates, one ISO date per line.
Unless every one of them has a done folder and no other done folder exists, the program prints
REFUSED and exits 2 before reading any table, so a partial run never yields a verdict.
Reads every date folder DIR/<YYYY-MM-DD>/ that holds a done marker (TABLES31.md: placements, loop,
implied and days parquet files); folders without one are listed. Never touches DBN
files. Spec: reports/stage_e31_pilot_spec.md sections 4 to 8 (binding); interface: TABLES31.md.

- Cells: model (a, b, c) x session (DAY, OVERNIGHT) x symbol (ZM.v.0, ZM.v.1), buy and sell
  pooled and each side: placements, fills (inside the order's life, which includes the 50 ms
  cancel latency after j + 60 s; those are also counted on their own, as E.28), fill rate,
  touch rate, stale share, KM time to fill censored at 60 s; among fills c_half, and per
  h = 1, 10, 60 s the markout, E_h = markout_h + c_half, N_h(firm) = E_h - fee per fill for the
  five firms, the share of positive E_h and VPO_h = fill rate x mean N_h, with the no-drop
  variant beside. A fill whose E_h is NaN (markout dropped) is left out of that horizon's means.
- Splits (spec 5, decide nothing): ZS, ZL and joint move buckets at L = 1 and 10 s, USDA buckets
  (fill-time conditions: statistics among fills only) and queue-imbalance buckets (an entry-time
  quantity: also placements and fill rate), per model x symbol x session, sides pooled, headline
  (dropping) markouts. Sessions are the cells themselves.
- Loop (spec 6), implied liquidity (spec 8) and the exclusion counts of days.parquet.
- Intervals: 95% two-sided percentile intervals of a day-block bootstrap over the done trade
  dates (2,000 replicates, seed 31), ONE draw matrix shared by every rate and mean and by the
  loop mean; a replicate whose denominator is 0 is left out (``boot_valid``). Medians: point only.
- Kill rule (spec 7, v2 sha256 31d33e68...) on ZM.v.0, DAY, model (c), sides pooled: K1 the lower
  bound of mean N_10(Topstep) (pooled over fills with a valid 10 s markout of the variant, a ratio
  of sums in each replicate) is not above 0 under EITHER the dropping or the no-drop variant; K2
  fewer than 400 model (c) fills, counted before any markout drop; K3 mean loop round trips per
  DAY trade date (model c) < 20. FAIL if any holds, else PASS. Beside K1, for information only:
  both bounds at 0.528 per fill; a PASS whose K1 would hold there reads "PASS, fragile (fee
  reading)". Nothing else decides.
- Model (a) is also reported for trade dates from 2023-11-01 alone (spec 3.1), with intervals
  that resample only those dates. It decides nothing.
"""
# ruff: noqa: E402 - the folder is put on sys.path before the sibling imports

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow.parquet as pq

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import stats31_core as core
import stats31_report as report
from stats31_core import FEE_PER_FILL_TICKS, HORIZONS_S, per_day, ratio_stat

MODELS = ("a", "b", "c")
SESSIONS = ("DAY", "OVERNIGHT")
SYMBOLS = ("ZM.v.0", "ZM.v.1")
SIDE_LABELS = (("pooled", 0), ("buy", 1), ("sell", -1))
TRIGGERS = ("queue", "through")
PRIMARY = {"model": "c", "session": "DAY", "symbol": "ZM.v.0"}
K1_HORIZON_S = 10
K2_MIN_FILLS = 400
K3_MIN_ROUND_TRIPS = 20.0
FULL_RT_TOPSTEP_TICKS = 2 * FEE_PER_FILL_TICKS["Topstep"]  # 0.528, information only
MODEL_A_FIRST_DATE = "2023-11-01"  # spec 3.1: model (a) also reported from this trade date
VARIANTS = (("drop", "mo_"), ("nodrop", "mo_nd_"))
DONE_MARKERS = ("DONE", "done", "_DONE", ".done", "DONE.json", "done.json")
DATE_DIR = re.compile(r"\d{4}-\d{2}-\d{2}")
PT = ZoneInfo("America/Vancouver")
LOOP_BINS = ((0, 1, "0"), (1, 5, "1-4"), (5, 10, "5-9"), (10, 20, "10-19"), (20, 30, "20-29"),
             (30, 50, "30-49"), (50, 100, "50-99"), (100, math.inf, "100+"))
LOOP_QUANTILES = (10, 25, 50, 75, 90)

PLACEMENT_COLS = {
    "trade_date": "date", "session": "str", "symbol": "str", "model": "str", "side": "int",
    "j_ns": "int", "stale": "bool", "filled": "bool", "t_fill_ns": "int", "trigger": "str",
    "wait_s": "float", "c_half": "float", "touched": "bool",
    **{f"{prefix}{h}": "float" for _, prefix in VARIANTS for h in HORIZONS_S},
    **{f"{c}_d{lag}": "float" for c in ("zs", "zl") for lag in (1, 10)},
    "usda_min": "float", "imb": "float"}
LOOP_COLS = {"trade_date": "date", "symbol": "str", "model": "str", "round_trips": "int",
             "entries_filled": "int", "orders_placed": "int", "mean_rt_s": "float"}
IMPLIED_COUNTS = ("n_ab", "vol_ab", "n_none", "vol_none", "n_short", "vol_short", "n_n", "vol_n")
IMPLIED_COLS = {"trade_date": "date", "symbol": "str", "session": "str",
                **{c: "int" for c in IMPLIED_COUNTS}}
DAYS_SUMS = ("n_records", "inversions", "bad_flag_records", "crossed_moments", "placements_day",
             "placements_on")
DAYS_COLS = {"trade_date": "date", "symbol": "str", "instrument_id": "int", "raw_symbol": "str",
             "included": "bool", "reason": "str", "max_gap_day_s": "float",
             **{c: "int" for c in DAYS_SUMS}}
TABLES = (("placements", "placements.parquet", PLACEMENT_COLS), ("loop", "loop.parquet", LOOP_COLS),
          ("implied", "implied.parquet", IMPLIED_COLS), ("days", "days.parquet", DAYS_COLS))
_DTYPES = {"float": float, "int": np.int64, "bool": bool, "str": object, "date": object}


# ------------------------------------------------------------------ loading ----
def _convert(col: Any, kind: str, where: str) -> np.ndarray:
    if kind == "float":
        return np.asarray(col.to_numpy(zero_copy_only=False), dtype=float)
    if kind == "str":  # a null string is read as "" (TABLES31: "" means none)
        return np.array(["" if x is None else str(x) for x in col.to_pylist()], dtype=object)
    if col.null_count:
        raise ValueError(f"{where}: {col.null_count} nulls in a {kind} column")
    if kind == "date":
        return np.array([x.isoformat() if hasattr(x, "isoformat") else str(x)
                         for x in col.to_pylist()], dtype=object)
    return np.asarray(col.to_numpy(zero_copy_only=False), dtype=_DTYPES[kind])


def read_table(path: Path, schema: dict[str, str]) -> dict[str, np.ndarray]:
    table = pq.read_table(path)
    missing = [c for c in schema if c not in table.column_names]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return {name: _convert(table.column(name), kind, f"{path}:{name}")
            for name, kind in schema.items()}


def _empty(schema: dict[str, str]) -> dict[str, np.ndarray]:
    out = {name: np.array([], dtype=_DTYPES[kind]) for name, kind in schema.items()}
    out["day"] = np.array([], dtype=np.int64)
    return out


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def is_done(folder: Path) -> bool:
    return any((folder / name).exists() for name in DONE_MARKERS)


def read_expected_dates(path: Path) -> list[str]:
    """The purchased trade dates: one ISO date (YYYY-MM-DD) per line; blank lines are ignored."""
    lines = [s.strip() for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]
    bad = [s for s in lines if not DATE_DIR.fullmatch(s)]
    for s in lines:
        if s not in bad:
            try:
                date.fromisoformat(s)
            except ValueError:
                bad.append(s)
    if bad:
        raise ValueError(f"{path}: not ISO dates: {bad[:5]}")
    dup = sorted(s for s, n in Counter(lines).items() if n > 1)
    if dup:
        raise ValueError(f"{path}: duplicate dates {dup[:5]}")
    if not lines:
        raise ValueError(f"{path}: no dates")
    return sorted(lines)


def completeness(runs_dir: Path, expected: list[str]) -> dict[str, list[str]]:
    """Expected dates without a done folder, and done folders that are not expected. The verdict
    runs only when both are empty, so a partial or mismatched run is never read."""
    done = ({p.name for p in runs_dir.iterdir()
             if p.is_dir() and DATE_DIR.fullmatch(p.name) and is_done(p)}
            if runs_dir.is_dir() else set())
    return {"missing": sorted(set(expected) - done), "unexpected": sorted(done - set(expected))}


def load_runs(runs_dir: Path) -> dict[str, Any]:
    """All done date folders, concatenated per table, with a ``day`` index (sorted dates)."""
    if not runs_dir.is_dir():
        raise FileNotFoundError(f"{runs_dir}: not a directory")
    folders = sorted(p for p in runs_dir.iterdir() if p.is_dir() and DATE_DIR.fullmatch(p.name))
    done = [p for p in folders if is_done(p)]
    parts: dict[str, list[dict[str, np.ndarray]]] = {key: [] for key, _, _ in TABLES}
    digests: list[str] = []
    for i, folder in enumerate(done):
        for key, fname, schema in TABLES:
            path = folder / fname
            if not path.is_file():
                raise FileNotFoundError(f"{path}: missing in a folder with a done marker")
            tab = read_table(path, schema)
            stray = sorted(set(tab["trade_date"].tolist()) - {folder.name})
            if stray:
                raise ValueError(f"{path}: trade_date {stray[:3]} differs from the folder date")
            tab["day"] = np.full(len(tab["trade_date"]), i, dtype=np.int64)
            parts[key].append(tab)
            digests.append(f"{folder.name}/{fname} {_sha256(path)}")
    tables = {key: ({c: np.concatenate([p[c] for p in parts[key]]) for c in parts[key][0]}
                    if parts[key] else _empty(schema)) for key, _, schema in TABLES}
    return {"runs_dir": str(runs_dir), "dates": [p.name for p in done],
            "skipped_no_marker": [p.name for p in folders if not is_done(p)],
            "inputs_sha256": hashlib.sha256("\n".join(digests).encode()).hexdigest(),
            "input_files": len(digests), **tables}


def _check_values(tab: dict[str, np.ndarray], col: str, allowed: tuple[Any, ...],
                  where: str) -> None:
    bad = sorted(set(np.unique(tab[col]).tolist()) - set(allowed), key=str)
    if bad:
        raise ValueError(f"{where}.{col}: values {bad[:5]} outside {allowed}")


def _check_unique(tab: dict[str, np.ndarray], cols: tuple[str, ...], where: str) -> None:
    keys = Counter(zip(*(tab[c].tolist() for c in cols), strict=True))
    dup = [k for k, n in keys.items() if n > 1]
    if dup:
        raise ValueError(f"{where}: {len(dup)} duplicate rows by {cols}, e.g. {dup[0]}")


def validate(runs: dict[str, Any]) -> None:
    """Fail fast on values outside TABLES31's domains."""
    p = runs["placements"]
    _check_values(p, "model", MODELS, "placements")
    _check_values(p, "session", SESSIONS, "placements")
    _check_values(p, "symbol", SYMBOLS, "placements")
    _check_values(p, "side", (1, -1), "placements")
    if not np.all(np.isfinite(p["wait_s"])):
        raise ValueError("placements.wait_s: non-finite values")
    _check_values({"t": p["trigger"][p["filled"]]}, "t", TRIGGERS, "placements(filled).trigger")
    _check_values({"t": p["trigger"][~p["filled"]]}, "t", ("",), "placements(unfilled).trigger")
    _check_values(runs["loop"], "model", MODELS, "loop")
    _check_unique(runs["loop"], ("day", "symbol", "model"), "loop")
    _check_values(runs["implied"], "session", SESSIONS, "implied")
    _check_unique(runs["implied"], ("day", "symbol", "session"), "implied")
    _check_unique(runs["days"], ("day", "symbol"), "days")


# ------------------------------------------------------------------ cell statistics ----
def _median(values: np.ndarray) -> float | None:
    return float(np.median(values)) if len(values) else None


def edge_arrays(p: dict[str, np.ndarray]) -> dict[str, dict[int, np.ndarray]]:
    """E_h = markout_h + c_half (spec 5) for the headline and the no-drop markouts."""
    return {variant: {h: p[f"{prefix}{h}"] + p["c_half"] for h in HORIZONS_S}
            for variant, prefix in VARIANTS}


def horizon_block(p: dict[str, np.ndarray], edge: np.ndarray, mo: np.ndarray,
                  filled: np.ndarray, n_d: np.ndarray, f_d: np.ndarray, n_days: int,
                  w: np.ndarray, *, with_vpo: bool = True) -> dict[str, Any]:
    """Among fills with a finite E_h: markout, c_half, E_h, share E_h > 0, N_h and VPO_h."""
    day = p["day"]
    ok = filled & np.isfinite(edge)
    cnt_d = per_day(day, ok, n_days)
    e_d = per_day(day, ok, n_days, edge)
    boot_e = core.ratio(w @ e_d, w @ cnt_d)
    mean_e = ratio_stat(e_d, cnt_d, w, label=True)
    med_e = _median(edge[ok])
    dropped = filled & ~ok
    out: dict[str, Any] = {
        "n": int(cnt_d.sum()), "dropped": int(np.count_nonzero(dropped)),
        "dropped_share": ratio_stat(per_day(day, dropped, n_days), f_d, w),
        "markout_mean": ratio_stat(per_day(day, ok, n_days, mo), cnt_d, w, label=True),
        "markout_median": _median(mo[ok]),
        "c_half_mean": ratio_stat(per_day(day, ok, n_days, p["c_half"]), cnt_d, w, label=True),
        "edge_mean": mean_e, "edge_median": med_e,
        "edge_share_positive": ratio_stat(
            per_day(day, ok & (np.where(ok, edge, 0.0) > 0), n_days), cnt_d, w),
        "net": {}}
    for firm, fee in FEE_PER_FILL_TICKS.items():
        point = None if mean_e["value"] is None else mean_e["value"] - fee
        net: dict[str, Any] = {"fee_per_fill": fee,
                               "mean": core.interval(point, boot_e - fee, label=True),
                               "median": None if med_e is None else med_e - fee}
        if with_vpo:
            vpo_pt = core.vpo_values(np.array([f_d.sum()]), np.array([n_d.sum()]),
                                     np.array([e_d.sum()]), np.array([cnt_d.sum()]), fee)[0]
            net["vpo"] = core.interval(
                float(vpo_pt), core.vpo_values(w @ f_d, w @ n_d, w @ e_d, w @ cnt_d, fee),
                label=True)
        out["net"][firm] = net
    return out


def cell_stats(p: dict[str, np.ndarray], mask: np.ndarray,
               edges: dict[str, dict[int, np.ndarray]], n_days: int,
               w: np.ndarray) -> dict[str, Any]:
    day, wait = p["day"], p["wait_s"]
    filled = mask & p["filled"]
    n_d, f_d = per_day(day, mask, n_days), per_day(day, filled, n_days)
    triggers = Counter(p["trigger"][filled].tolist())
    ok_c = filled & np.isfinite(p["c_half"])
    return {
        "placements": int(n_d.sum()), "fills": int(f_d.sum()),
        "fills_in_cancel_latency": int(np.count_nonzero(filled & (wait > core.KM_CENSOR_S))),
        "fills_by_trigger": {t: int(triggers.get(t, 0)) for t in TRIGGERS},
        "fill_rate": ratio_stat(f_d, n_d, w),
        "touch_rate": ratio_stat(per_day(day, mask & p["touched"], n_days), n_d, w),
        "stale_share": ratio_stat(per_day(day, mask & p["stale"], n_days), n_d, w),
        "km": core.km_stats(wait[mask], p["filled"][mask], day[mask], n_days, w),
        "c_half": {"n": int(np.count_nonzero(ok_c)), "median": _median(p["c_half"][ok_c]),
                   "mean": ratio_stat(per_day(day, ok_c, n_days, p["c_half"]),
                                      per_day(day, ok_c, n_days), w, label=True)},
        "horizons": {variant: {str(h): horizon_block(p, edges[variant][h], p[f"{prefix}{h}"],
                                                     filled, n_d, f_d, n_days, w)
                               for h in HORIZONS_S}
                     for variant, prefix in VARIANTS}}


def _base_mask(p: dict[str, np.ndarray], model: str, symbol: str, session: str) -> np.ndarray:
    return (p["model"] == model) & (p["symbol"] == symbol) & (p["session"] == session)


def compute_cells(p: dict[str, np.ndarray], edges: dict[str, dict[int, np.ndarray]],
                  n_days: int, w: np.ndarray,
                  models: tuple[str, ...] = MODELS) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for model in models:
        out[model] = {}
        for symbol in SYMBOLS:
            out[model][symbol] = {}
            for session in SESSIONS:
                base = _base_mask(p, model, symbol, session)
                out[model][symbol][session] = {
                    label: cell_stats(p, base if side == 0 else base & (p["side"] == side),
                                      edges, n_days, w)
                    for label, side in SIDE_LABELS}
    return out


# ------------------------------------------------------------------ splits (spec 5) ----
def split_labels(p: dict[str, np.ndarray]) -> dict[str, tuple[np.ndarray, tuple[str, ...], bool]]:
    """Family -> (bucket label per row, bucket order, placement-level?)."""
    side = p["side"]
    moves = {f"{name} L={lag} s": core.move_bucket(side, p[f"{col}_d{lag}"])
             for lag in (1, 10) for name, col in (("ZS", "zs"), ("ZL", "zl"))}
    out: dict[str, tuple[np.ndarray, tuple[str, ...], bool]] = {
        k: (v, core.MOVE_BUCKETS, False) for k, v in moves.items()}
    for lag in (1, 10):
        out[f"ZS+ZL L={lag} s"] = (core.joint_bucket(moves[f"ZS L={lag} s"],
                                                     moves[f"ZL L={lag} s"]),
                                   core.JOINT_BUCKETS, False)
    out["USDA release"] = (core.usda_bucket(p["usda_min"]), core.USDA_BUCKETS, False)
    out["queue imbalance"] = (core.imb_bucket(p["imb"]), core.IMB_BUCKETS, True)
    return out


def split_block(p: dict[str, np.ndarray], mask: np.ndarray,
                edges: dict[str, dict[int, np.ndarray]], n_days: int, w: np.ndarray,
                placement_level: bool) -> dict[str, Any]:
    """A fill-time condition is known only for fills, so its bucket has no placements or fill
    rate; the entry-time imbalance has both (and VPO)."""
    day = p["day"]
    filled = mask & p["filled"]
    n_d, f_d = per_day(day, mask, n_days), per_day(day, filled, n_days)
    out: dict[str, Any] = {"fills": int(f_d.sum())}
    if placement_level:
        out["placements"] = int(n_d.sum())
        out["fill_rate"] = ratio_stat(f_d, n_d, w)
    out["horizons"] = {str(h): horizon_block(p, edges["drop"][h], p[f"mo_{h}"], filled, n_d,
                                             f_d, n_days, w, with_vpo=placement_level)
                       for h in HORIZONS_S}
    return out


def compute_splits(p: dict[str, np.ndarray], edges: dict[str, dict[int, np.ndarray]],
                   n_days: int, w: np.ndarray) -> dict[str, Any]:
    labels = split_labels(p)
    out: dict[str, Any] = {}
    for model in MODELS:
        out[model] = {}
        for symbol in SYMBOLS:
            out[model][symbol] = {}
            for session in SESSIONS:
                base = _base_mask(p, model, symbol, session)
                out[model][symbol][session] = {
                    family: {b: split_block(p, base & (lab == b), edges, n_days, w, level)
                             for b in order}
                    for family, (lab, order, level) in labels.items()}
    return out


# ------------------------------------------------------------------ loop, implied, days ----
def _loop_block(lp: dict[str, np.ndarray], mask: np.ndarray, dates: list[str], n_days: int,
                w: np.ndarray) -> dict[str, Any]:
    rt = lp["round_trips"][mask].astype(float)
    rts, mean_s = lp["round_trips"][mask], lp["mean_rt_s"][mask]
    timed = (rts > 0) & np.isfinite(mean_s)
    return {
        "dates": int(np.count_nonzero(mask)), "round_trips_total": int(rt.sum()),
        "mean": ratio_stat(per_day(lp["day"], mask, n_days, lp["round_trips"]),
                           per_day(lp["day"], mask, n_days), w),
        "median": _median(rt), "min": float(rt.min()) if len(rt) else None,
        "max": float(rt.max()) if len(rt) else None,
        "quantiles": {f"p{q}": float(np.percentile(rt, q)) if len(rt) else None
                      for q in LOOP_QUANTILES},
        "histogram": {label: int(np.count_nonzero((rt >= lo) & (rt < hi)))
                      for lo, hi, label in LOOP_BINS},
        "entries_filled_total": int(lp["entries_filled"][mask].sum()),
        "orders_placed_total": int(lp["orders_placed"][mask].sum()),
        "mean_rt_s": (float(np.average(mean_s[timed], weights=rts[timed]))
                      if timed.any() else None),
        "per_date": {dates[d]: int(r) for d, r in zip(lp["day"][mask].tolist(),
                                                      lp["round_trips"][mask].tolist(),
                                                      strict=True)}}


def loop_stats(lp: dict[str, np.ndarray], dates: list[str], n_days: int, w: np.ndarray,
               models: tuple[str, ...] = MODELS) -> dict[str, Any]:
    """Round trips per DAY trade date (spec 6) per symbol and model; ZM.v.0 always present."""
    symbols = sorted(set(lp["symbol"].tolist()) | {PRIMARY["symbol"]})
    return {symbol: {model: _loop_block(lp, (lp["symbol"] == symbol) & (lp["model"] == model),
                                        dates, n_days, w)
                     for model in models}
            for symbol in symbols}


def implied_stats(imp: dict[str, np.ndarray], n_days: int, w: np.ndarray) -> dict[str, Any]:
    """Spec 8: among A/B trades, the shares of prints and volume at a price with (i) no displayed
    resting quantity on the passive side, (ii) less than the trade's size; side N beside."""
    out: dict[str, Any] = {}
    for symbol in sorted(set(imp["symbol"].tolist())):
        out[symbol] = {}
        for session in SESSIONS:
            m = (imp["symbol"] == symbol) & (imp["session"] == session)
            d = {c: per_day(imp["day"], m, n_days, imp[c]) for c in IMPLIED_COUNTS}
            out[symbol][session] = {
                "dates": int(np.count_nonzero(m)),
                "totals": {c: int(d[c].sum()) for c in IMPLIED_COUNTS},
                "share_prints_no_resting": ratio_stat(d["n_none"], d["n_ab"], w),
                "share_volume_no_resting": ratio_stat(d["vol_none"], d["vol_ab"], w),
                "share_prints_short": ratio_stat(d["n_short"], d["n_ab"], w),
                "share_volume_short": ratio_stat(d["vol_short"], d["vol_ab"], w),
                "share_prints_side_n_of_all": ratio_stat(d["n_n"], d["n_ab"] + d["n_n"], w)}
    return out


def exclusion_stats(days: dict[str, np.ndarray]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for symbol in sorted(set(days["symbol"].tolist())):
        m = days["symbol"] == symbol
        inc = days["included"][m]
        gaps = days["max_gap_day_s"][m]
        reasons = Counter(days["reason"][m][~inc].tolist())
        out[symbol] = {
            "dates": int(np.count_nonzero(m)), "included": int(inc.sum()),
            "excluded": int(np.count_nonzero(~inc)),
            "excluded_by_reason": dict(sorted(reasons.items())),
            **{c: int(days[c][m].sum()) for c in DAYS_SUMS},
            "max_gap_day_s_max": (float(np.max(gaps[np.isfinite(gaps)]))
                                  if np.isfinite(gaps).any() else None),
            "dates_gap_over_60s": int(np.count_nonzero(np.where(np.isfinite(gaps), gaps, 0) > 60)),
            "instruments": sorted(set(days["raw_symbol"][m].tolist()))}
    return out


def consistency_checks(runs: dict[str, Any]) -> dict[str, Any]:
    """Counts that should be 0 if the engine and the stats layer agree (reported, not fatal)."""
    p, lp, days = runs["placements"], runs["loop"], runs["days"]
    inc = dict(zip(zip(days["day"].tolist(), days["symbol"].tolist(), strict=True),
                   days["included"].tolist(), strict=True))
    p_keys = list(zip(p["day"].tolist(), p["symbol"].tolist(), strict=True))
    lp_keys = list(zip(lp["day"].tolist(), lp["symbol"].tolist(), strict=True))
    lp_have = set(zip(lp["day"].tolist(), lp["model"].tolist(), strict=True))
    front_inc = [d for (d, s), ok in inc.items() if ok and s == PRIMARY["symbol"]]
    filled = p["filled"]
    counts: dict[tuple[str, str, int], dict[str, int]] = {}
    for model, symbol, session, side in zip(p["model"].tolist(), p["symbol"].tolist(),
                                            p["session"].tolist(), p["side"].tolist(),
                                            strict=True):
        cell = counts.setdefault((symbol, session, side), {})
        cell[model] = cell.get(model, 0) + 1
    unequal = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in counts.items()
               if len(set(v.values())) > 1 or len(v) != len(MODELS)}
    return {
        "placement_rows_on_dates_not_included": sum(inc.get(k) is False for k in p_keys),
        "placement_rows_on_dates_missing_from_days": sum(k not in inc for k in p_keys),
        "loop_rows_on_dates_not_included": sum(inc.get(k) is False for k in lp_keys),
        "included_front_dates_without_loop_row": {
            m: sum((d, m) not in lp_have for d in front_inc) for m in MODELS},
        "placement_counts_unequal_across_models": unequal,
        "model_c_fills_not_through": int(np.count_nonzero(
            filled & (p["model"] == "c") & (p["trigger"] != "through"))),
        "fills_with_t_fill_before_j": int(np.count_nonzero(filled & (p["t_fill_ns"] < p["j_ns"]))),
        "fills_with_nan_c_half": int(np.count_nonzero(filled & ~np.isfinite(p["c_half"])))}


# ------------------------------------------------------------------ kill rule (spec 7) ----
def _not_above_zero(bound: float | None) -> bool:
    return bound is None or not bound > 0


def evaluate_kill(k1_drop: float | None, k1_nodrop: float | None, fills: int,
                  loop_mean: float | None, full_drop: float | None,
                  full_nodrop: float | None) -> dict[str, Any]:
    """Spec 7 (v2). K1 holds if the lower bound of mean N_10(Topstep) is not above 0 under EITHER
    the dropping or the no-drop variant (a missing bound counts as not above 0); K2 if fills < 400;
    K3 unless the loop mean exists and is at least 20. FAIL if any holds, else PASS. A PASS whose
    K1 would hold at 0.528 per fill (either variant) reads "PASS, fragile (fee reading)"; the
    0.528 bounds never turn a PASS into a FAIL."""
    k1d, k1n = _not_above_zero(k1_drop), _not_above_zero(k1_nodrop)
    k2 = fills < K2_MIN_FILLS
    k3 = loop_mean is None or loop_mean < K3_MIN_ROUND_TRIPS
    verdict = "FAIL" if (k1d or k1n or k2 or k3) else "PASS"
    fragile = verdict == "PASS" and (_not_above_zero(full_drop) or _not_above_zero(full_nodrop))
    return {
        "K1": {"statistic": "lower 95% bound of mean N_10(Topstep) = E_10 - 0.264 over fills "
                            "with a valid 10 s markout, dropping and no-drop variants",
               "lower_drop": k1_drop, "lower_nodrop": k1_nodrop, "holds_drop": k1d,
               "holds_nodrop": k1n, "rule": "holds if either bound is not above 0",
               "holds": k1d or k1n},
        "K2": {"statistic": "model (c) fills of the population, before any markout drop",
               "value": fills, "rule": f"holds if < {K2_MIN_FILLS}", "holds": k2},
        "K3": {"statistic": "mean loop round trips per DAY trade date, model (c)",
               "value": loop_mean, "rule": f"holds if < {K3_MIN_ROUND_TRIPS:g}", "holds": k3},
        "verdict": verdict, "fragile": fragile,
        "verdict_line": "PASS, fragile (fee reading)" if fragile else verdict,
        "fragile_test": {"full_fee_lower_drop": full_drop, "full_fee_lower_nodrop": full_nodrop,
                         "rule": "a PASS is fragile if K1 would hold at 0.528 per fill"}}


def _net_mean(p: dict[str, np.ndarray], filled: np.ndarray, edge: np.ndarray, fee: float,
              n_days: int, w: np.ndarray) -> dict[str, Any]:
    """Pooled mean of edge - fee over fills with a finite edge: a ratio of sums per replicate."""
    ok = filled & np.isfinite(edge)
    cnt_d, e_d = per_day(p["day"], ok, n_days), per_day(p["day"], ok, n_days, edge)
    point = float(core.ratio(np.array([e_d.sum()]), np.array([cnt_d.sum()]))[0])
    out = core.interval(point - fee, core.ratio(w @ e_d, w @ cnt_d) - fee, label=True)
    return {**out, "n": int(cnt_d.sum()), "dropped": int(np.count_nonzero(filled & ~ok)),
            "fee_per_fill": fee}


def kill_rule(p: dict[str, np.ndarray], edges: dict[str, dict[int, np.ndarray]],
              loop_res: dict[str, Any], n_days: int, w: np.ndarray) -> dict[str, Any]:
    filled = _base_mask(p, **PRIMARY) & p["filled"]
    fee = FEE_PER_FILL_TICKS["Topstep"]
    net = {(variant, f): _net_mean(p, filled, edges[variant][K1_HORIZON_S], f, n_days, w)
           for variant in ("drop", "nodrop") for f in (fee, FULL_RT_TOPSTEP_TICKS)}
    loop_mean = loop_res[PRIMARY["symbol"]][PRIMARY["model"]]["mean"]
    out = evaluate_kill(net[("drop", fee)]["ci95"][0], net[("nodrop", fee)]["ci95"][0],
                        int(np.count_nonzero(filled)), loop_mean["value"],
                        net[("drop", FULL_RT_TOPSTEP_TICKS)]["ci95"][0],
                        net[("nodrop", FULL_RT_TOPSTEP_TICKS)]["ci95"][0])
    out["K1"]["interval_drop"] = net[("drop", fee)]
    out["K1"]["interval_nodrop"] = net[("nodrop", fee)]
    out["K3"]["interval"] = loop_mean
    out["K3"]["dates"] = loop_res[PRIMARY["symbol"]][PRIMARY["model"]]["dates"]
    out["primary"] = dict(PRIMARY, sides="buy and sell pooled")
    out["information_only"] = {
        "K1_bound_0.528_drop": net[("drop", FULL_RT_TOPSTEP_TICKS)],
        "K1_bound_0.528_nodrop": net[("nodrop", FULL_RT_TOPSTEP_TICKS)]}
    return out


def subset_runs(runs: dict[str, Any], first_date: str) -> dict[str, Any]:
    """A new runs dict holding only the trade dates on or after ``first_date`` (day re-indexed)."""
    keep = [i for i, d in enumerate(runs["dates"]) if d >= first_date]
    remap = np.full(len(runs["dates"]), -1, dtype=np.int64)
    remap[keep] = np.arange(len(keep))
    out = {k: v for k, v in runs.items() if k not in {key for key, _, _ in TABLES}}
    out["dates"] = [runs["dates"][i] for i in keep]
    for key, _, _ in TABLES:
        rows = remap[runs[key]["day"]] >= 0
        out[key] = {c: (remap[v[rows]] if c == "day" else v[rows]) for c, v in runs[key].items()}
    return out


def model_a_block(runs: dict[str, Any], boot: int, seed: int) -> dict[str, Any]:
    """Spec 3.1: model (a) also reported for trade dates from 2023-11-01 alone (decides nothing).
    Its intervals resample only those dates (a draw matrix of their own, same seed)."""
    sub = subset_runs(runs, MODEL_A_FIRST_DATE)
    dates = sub["dates"]
    base = {"first_date": MODEL_A_FIRST_DATE, "dates": len(dates),
            "date_range": [dates[0], dates[-1]] if dates else None,
            "bootstrap": {"replicates": boot, "seed": seed,
                          "pool": f"trade dates on or after {MODEL_A_FIRST_DATE} only"}}
    if not dates:
        return {**base, "note": f"no done trade date on or after {MODEL_A_FIRST_DATE}"}
    w = core.bootstrap_weights(len(dates), boot, seed).astype(float)
    p = sub["placements"]
    return {**base, "cells": compute_cells(p, edge_arrays(p), len(dates), w, models=("a",)),
            "loop": loop_stats(sub["loop"], dates, len(dates), w, models=("a",))}


# ------------------------------------------------------------------ driver ----
def compute_all(runs: dict[str, Any], boot: int = core.BOOT_REPLICATES,
                seed: int = core.BOOT_SEED) -> dict[str, Any]:
    validate(runs)
    dates = runs["dates"]
    n_days = len(dates)
    w = core.bootstrap_weights(n_days, boot, seed).astype(float)
    p = runs["placements"]
    edges = edge_arrays(p)
    loop_res = loop_stats(runs["loop"], dates, n_days, w)
    code = {f.name: _sha256(f) for f in (_HERE / "stats31.py", _HERE / "stats31_core.py",
                                         _HERE / "stats31_report.py")}
    meta = {
        "spec": "reports/stage_e31_pilot_spec.md sections 4-8; TABLES31.md",
        "generated_pt": datetime.now(PT).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "runs_dir": runs["runs_dir"], "dates_done": n_days,
        "first_date": dates[0] if dates else None, "last_date": dates[-1] if dates else None,
        "folders_skipped_no_marker": runs["skipped_no_marker"],
        "expected_dates": runs.get("expected_dates"),
        "rows": {k: int(len(runs[k]["day"])) for k, _, _ in TABLES},
        "bootstrap": {"replicates": boot, "seed": seed, "unit": "trade date",
                      "pool": "all done trade dates; one draw matrix for every statistic"},
        "fees_rt_usd": core.FEES_RT_USD, "fees_per_fill_ticks": FEE_PER_FILL_TICKS,
        "inputs_sha256": runs["inputs_sha256"], "input_files": runs["input_files"],
        "code_sha256": code}
    return {"meta": meta, "kill_rule": kill_rule(p, edges, loop_res, n_days, w),
            "cells": compute_cells(p, edges, n_days, w),
            "model_a_from_2023_11_01": model_a_block(runs, boot, seed),
            "splits": compute_splits(p, edges, n_days, w), "loop": loop_res,
            "implied": implied_stats(runs["implied"], n_days, w),
            "days": exclusion_stats(runs["days"]), "checks": consistency_checks(runs)}


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _fmt_num(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--expect-dates", required=True, type=Path,
                    help="the purchased trade dates, one ISO date per line")
    ap.add_argument("--boot", type=int, default=core.BOOT_REPLICATES)
    ap.add_argument("--seed", type=int, default=core.BOOT_SEED)
    args = ap.parse_args(argv)
    with contextlib.suppress(OSError):
        os.nice(10)
    try:
        expected = read_expected_dates(args.expect_dates)
    except (OSError, ValueError) as exc:
        print(f"REFUSED: --expect-dates unreadable: {exc}", file=sys.stderr)
        return 2
    gaps = completeness(args.runs, expected)
    if gaps["missing"] or gaps["unexpected"]:
        print(f"REFUSED: {len(gaps['missing'])} of {len(expected)} expected dates have no done "
              f"marker (e.g. {gaps['missing'][:5]}); {len(gaps['unexpected'])} done folders "
              f"are not expected (e.g. {gaps['unexpected'][:5]}). No statistics or verdict "
              "were computed.", file=sys.stderr)
        return 2
    runs = load_runs(args.runs)
    runs["expected_dates"] = {"file": str(args.expect_dates), "count": len(expected),
                              "sha256": _sha256(args.expect_dates)}
    results = to_jsonable(compute_all(runs, args.boot, args.seed))
    _write(args.out_json, json.dumps(results, indent=1, allow_nan=False))
    _write(args.out_md, report.render(results))
    kr = results["kill_rule"]
    k1 = kr["K1"]
    res = {True: "holds", False: "clear"}
    print(f"dates {len(runs['dates'])}, skipped (no marker) {len(runs['skipped_no_marker'])}")
    for variant in ("drop", "nodrop"):
        print(f"K1 ({variant}) N_10(Topstep) mean {_fmt_num(k1[f'interval_{variant}']['value'])}"
              f" lower bound {_fmt_num(k1[f'lower_{variant}'])} -> {res[k1[f'holds_{variant}']]}")
    print(f"K2 fills {kr['K2']['value']} (need >= {K2_MIN_FILLS}) -> {res[kr['K2']['holds']]}")
    print(f"K3 loop mean {_fmt_num(kr['K3']['value'])} over {kr['K3']['dates']} dates "
          f"(need >= {K3_MIN_ROUND_TRIPS:g}) -> {res[kr['K3']['holds']]}")
    info = kr["information_only"]
    print(f"info: K1 bounds at 0.528: drop {_fmt_num(info['K1_bound_0.528_drop']['ci95'][0])}, "
          f"no-drop {_fmt_num(info['K1_bound_0.528_nodrop']['ci95'][0])}")
    print(f"VERDICT {kr['verdict_line']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
