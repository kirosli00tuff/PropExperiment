"""Data layer (lead_spec_B.md S0, S2): the 12 owned E.21 price paths, one root at a time, through
base_rules' loader and multiday.daily's marks and per-contract path (reused by import, never
edited), reduced to one small frame per root and cached to reports/stage_e22_microbook/cache/.

Per mark date d of a root (E.21's MK = base_rules.common.settle_point):
- price: the held contract's own mark, in the contract's price units (sizing price, S2);
- dp: the back-adjusted (chained) move of one contract from the previous mark to this mark, rolled
  at each store splice exactly as E.21's per-contract path (multiday.daily._interval), in price
  units; NaN on the first mark and on a failed interval (counted);
- n_rolls and the roll legs' D8 costs (frozen vehicles), the mark's D8 fill cost per side.

Two quirks handled (memory, E.21): consecutive recorded splices with no usable bar between them
(ZC/ZL/ZS weekend pairs) are treated as ONE splice (the later one is kept); the 2019-04-30 ->
2019-05-06 store boundary interval is chained like a splice (multiday.daily.with_boundary_splice
adds a splice there when the contract changes; same contract: the chain runs through). Window trade
dates without a mark (e.g. equity-calendar US holidays) are dropped (no new mark), counted.
"""

from __future__ import annotations

import gc
import hashlib
import json
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from base_rules import constants as BK
from base_rules.common import RunContext
from base_rules.context import context_from_freeze
from base_rules.costs import VehicleCost
from base_rules.store import EXT2010, STEP2_ERA, ProductBars, load_manifest, preflight
from multiday.daily import Interval, Mark, _interval, fill_cost, marks_of, with_boundary_splice
from multiday.run import e21_starts
from rules.products import product

REPO = BK.repo_path(".")
FREEZE_E21 = Path("reports/stage_e21_freeze.json")
CONTEXT_ROLES = ("settlement", "windows", "release_frozen", "release_hist", "ecauc_hist",
                 "ecauc_announcements", "livestock_hist", "hist_calendar_equity",
                 "hist_calendar_rates", "hist_calendar_fx", "hist_calendar_energy",
                 "hist_calendar_metals", "hist_calendar_grains", "run_manifest")
ALLOWED_ROOTS = ("NQ", "RTY", "GC", "CL", "NG", "6E", "ZT", "ZN", "ZB", "ZC", "ZS", "ZL", "TN",
                 "UB")
FROZEN_VEHICLE_ROOTS = ("NQ", "RTY", "GC", "CL")  # MNQ, M2K, MGC, MCL (base_rules VEHICLE_OF)
STUDY_FIRST = pd.Timestamp("2010-07-01")
STUDY_LAST = pd.Timestamp("2024-02-29")
CACHE_SCHEMA = "stage_e22_microbook_cache/2"


class DataRefused(RuntimeError):
    """A boundary of lead_spec_B S0 would be crossed."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def e21_inputs(freeze_path: Path = FREEZE_E21) -> dict[str, dict[str, str]]:
    """E.21's own input files (the freeze's paths and sha256s), each re-hashed now: the study
    reads exactly the calendars, settlement table, windows, release rows and run manifest E.21
    read."""
    body = json.loads(BK.repo_path(freeze_path).read_text(encoding="utf-8"))
    listed = {str(BK.repo_path(e["path"]).resolve()): e["sha256"] for e in body["files"]}
    out = {}
    for role in CONTEXT_ROLES:
        p = BK.repo_path(body["inputs"][role])
        sha = listed.get(str(p.resolve()))
        if sha is None or _sha256(p) != sha:
            raise DataRefused(f"E.21 input {role} ({p}) is not the frozen file")
        out[role] = {"path": str(p), "sha256": sha}
    return out


def build_context(freeze_path: Path = FREEZE_E21) -> tuple[RunContext, Any]:
    """E.21's run context (context_from_freeze on E.21's inputs, window starts by e21_starts)."""
    inputs = e21_inputs(freeze_path)
    manifest = load_manifest(Path(inputs["run_manifest"]["path"]),
                             inputs["run_manifest"]["sha256"])
    ctx = context_from_freeze({"inputs": inputs}, manifest)
    ctx.starts = e21_starts(dict(ctx.starts))
    return ctx, manifest


def check_root(root: str, manifest: Any) -> None:
    if root not in ALLOWED_ROOTS:
        raise DataRefused(f"{root} is not a Part B root (lead_spec_B S0)")
    refs = manifest.stores.get(root) or {}
    for era in (EXT2010, STEP2_ERA):
        ref = refs.get(era)
        if ref is None:
            raise DataRefused(f"{root}: no {era} store in the E.17 run manifest")
        path = str(ref.path)
        if "sealed" in path or "data/processed/" in path:
            raise DataRefused(f"{root}: {path} is out of bounds (S0)")


# ------------------------------------------------------------------ splices ----
def merge_adjacent_splices(bars: ProductBars) -> tuple[ProductBars, int]:
    """Consecutive splices with no usable bar between them are one splice: the group keeps only
    its last splice; when the last usable bar before the group and the first usable bar after it
    carry the SAME contract (a roll away and back with no bar between), the group is dropped
    (no roll happened). Returns the bars and the number of splices removed."""
    sp = list(bars.splices)
    groups: list[list] = []
    for s in sp:
        if groups:
            i = bars.first_at_or_after(groups[-1][-1].ts_ns)
            if i is None or int(bars.ts[i]) >= s.ts_ns:
                groups[-1].append(s)
                continue
        groups.append([s])
    keep, removed = [], 0
    for g in groups:
        if len(g) == 1:
            keep.append(g[0])
            continue
        i_out, i_in = bars.last_before(g[0].ts_ns), bars.first_at_or_after(g[-1].ts_ns)
        same = (i_out is not None and i_in is not None
                and bars.contract(i_out) == bars.contract(i_in))
        if not same:
            keep.append(g[-1])
        removed += len(g) - (0 if same else 1)
    return (replace(bars, splices=tuple(keep)) if removed else bars), removed


# ------------------------------------------------------------------ one root ----
def _interval_of(bars: ProductBars, vc: VehicleCost, ctx: RunContext, a: Mark, b: Mark,
                 counters: Counter) -> Interval:
    iv = _interval(bars, vc, ctx.releases, a, b, vc.tick_value_cents, None, counters)
    if iv.fail == "store boundary":
        # the boundary interval chained like a splice (with_boundary_splice added it when the
        # contract changes): the era check is the only thing bypassed (a's day is not used else)
        iv = _interval(bars, vc, ctx.releases, replace(a, day=b.day), b, vc.tick_value_cents,
                       None, counters)
        counters["store boundary interval chained"] += 1
    return iv


def _roll_costs(iv: Interval) -> tuple[float, float]:
    """(long, short) cents per contract held, base case: a long rolls by selling the old
    contract (roll_out) and buying the new one (roll_in); a short the other way round."""
    long_c = short_c = 0.0
    for leg in iv.rolls:
        sell, buy = float(leg.fill.cost["sell"][BK.BASE]), float(leg.fill.cost["buy"][BK.BASE])
        long_c += sell if leg.kind == "roll_out" else buy
        short_c += buy if leg.kind == "roll_out" else sell
    return long_c, short_c


def extract_root(ctx: RunContext, bars: ProductBars, root: str) -> tuple[pd.DataFrame, dict]:
    """The per-mark frame of ``root`` (module docstring) and its counters."""
    counters: Counter = Counter()
    vc = ctx.vc(root)
    tick = float(product(root).tick_size)
    tv = vc.tick_value_cents
    merged, n_merged = merge_adjacent_splices(bars)
    counters["splices removed by merging (no bar between)"] += n_merged
    chain, boundary_ts = with_boundary_splice(merged)
    counters["store boundary splice added"] += int(boundary_ts is not None)
    marks = marks_of(ctx, bars, root)
    window = [d for d in ctx.window_dates(root) if ctx.listed(root, d)]
    counters["listed window dates without a mark (dropped)"] += len(window) - len(marks)
    frozen = root in FROZEN_VEHICLE_ROOTS
    comm_side = float(vc.costs.commission_side_cents) if frozen else float("nan")
    rows = []
    for k, m in enumerate(marks):
        row = {"date": pd.Timestamp(m.day), "contract": m.contract, "price": m.price * tick,
               "dp": np.nan, "fail": "", "n_rolls": 0, "roll_long_c": 0.0, "roll_short_c": 0.0,
               "cost_buy_c": np.nan, "cost_sell_c": np.nan, "comm_side_c": comm_side,
               "event": False}
        if k > 0:
            iv = _interval_of(chain, vc, ctx, marks[k - 1], m, counters)
            if iv.fail:
                row["fail"] = iv.fail
                counters[f"interval failed: {iv.fail}"] += 1
            else:
                cents = sum((Fraction(c) for _, c in iv.increments), Fraction(0))
                ticks = cents / Fraction(tv)
                if ticks.denominator != 1:
                    raise RuntimeError(f"{root} {m.day}: non-integer tick move {ticks}")
                row["dp"] = int(ticks) * tick
                row["n_rolls"] = len(iv.rolls) // 2
                if frozen and iv.rolls:
                    lc, sc = _roll_costs(iv)
                    row["roll_long_c"], row["roll_short_c"] = lc, sc
                counters["rolls"] += len(iv.rolls) // 2
        if frozen:
            fc = fill_cost(bars, vc, ctx.releases, m.point[0], m.point[1], None)
            row["cost_buy_c"] = float(fc.cost["buy"][BK.BASE])
            row["cost_sell_c"] = float(fc.cost["sell"][BK.BASE])
            row["event"] = bool(fc.event)
            counters["mark fills in an uncalibrated bucket"] += int(any(fc.uncal.values()))
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame = frame[(frame["date"] >= STUDY_FIRST) & (frame["date"] <= STUDY_LAST)]
    if frame["date"].duplicated().any():
        raise RuntimeError(f"{root}: duplicate mark dates")
    counters["marks"] = len(frame)
    counters["dp defined"] = int(frame["dp"].notna().sum())
    meta = {"root": root, "tick_size": tick, "frozen_vehicle": frozen,
            "vehicle": vc.vehicle, "first": str(frame["date"].min().date()),
            "last": str(frame["date"].max().date()), "counters": dict(sorted(counters.items()))}
    return frame.reset_index(drop=True), meta


def cache_paths(cache_dir: Path, root: str) -> tuple[Path, Path]:
    return cache_dir / f"{root}.parquet", cache_dir / f"{root}.json"


def load_root_cached(root: str, cache_dir: Path, ctx_manifest: tuple | None = None
                     ) -> tuple[pd.DataFrame, dict]:
    """The cached frame of ``root``; built (bars read once, then freed) when absent."""
    pq_path, js_path = cache_paths(cache_dir, root)
    if pq_path.is_file() and js_path.is_file():
        meta = json.loads(js_path.read_text(encoding="utf-8"))
        if meta.get("schema") == CACHE_SCHEMA:
            return pd.read_parquet(pq_path), meta
    if ctx_manifest is None:
        ctx_manifest = build_context()
    ctx, manifest = ctx_manifest
    check_root(root, manifest)
    cals = ctx.cal(root)
    pre = preflight(root, manifest.stores[root], {EXT2010: cals.hist, STEP2_ERA: cals.frozen})
    bars = ctx.load_bars(root)
    frame, meta = extract_root(ctx, bars, root)
    del bars
    gc.collect()
    meta.update({"schema": CACHE_SCHEMA, "stores": pre})
    cache_dir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(pq_path, index=False)
    js_path.write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    return frame, meta


__all__ = ["ALLOWED_ROOTS", "DataRefused", "build_context", "cache_paths", "check_root",
           "e21_inputs", "extract_root", "load_root_cached", "merge_adjacent_splices"]
