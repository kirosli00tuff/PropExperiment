"""The Step 6 sentinel dry check (reports/stage_e20_plan.md sections 10.1, 13; review PR-1, PR-15;
recheck PR-16 and PR-18). Synthetic data only: sentinel bars are the frozen synthetic generator's
1-minute random walks (ml_route_v2.synthetic._root_bars) laid on each date's session intervals of
the 2010-2019 calendars inside backward.backward_context, so every leg is in its 2010-2019 listing
(each root from its B1 first date) and calendar state. No store is opened.

1. Features (``feature_check``): on three sample windows (2010-07-01..2012-09-28, the rates 17:30
   and grains 09:30 eras and their ends (a window must hold a port-complete day of every vehicle:
   the frozen ports._cp3 raises IndexError on a frame without one); 2014-12-15..2016-02-26,
   LE's 08:00 era; 2017-07-10..2018-09-28, every
   root listed), with every swap applied: the frozen clock plus t4, ruling 2's exclusion,
   compute_signals on the 34 KEPT signals and the two rod features. A feature passes when it
   computes, is applicable on rows of the vehicles it serves, has finite values there, and (for a
   table-driven feature) is applicable only on its table's event dates and on some of them in each
   window whose table has events. The calendar-only swap (members' tables left frozen) is run as a
   control: it shows which features the member swaps carry.
2. Legs (``leg_check``): on the third window, removing each of the 17 roots' frames makes the
   composed builder raise, and compute_signals on the full world's rows raises
   SignalInputMissing for the removed root.
3. Row losses (``row_loss_check``): per root over its whole B1 window, the dates whose every row
   lacks a port or G5 input (ports and G5 computed with sigma_X,d set to 1, so only an absent bar
   makes a value missing), against plan 10.1's declared table; the same with the true sigma_X,d
   and G9 (the warm-up extension); and ruling 2's excluded rows per t_index (PR-18).
4. Fallback reach (``fallback_table``, PR-16): from the calendars and the frozen release minutes
   alone, every (vehicle, release type, decision time, horizon, entry or exit) whose nominal fill
   minute lies in ruling 4's window [m, m + 30) on the backward trade dates, with each vehicle's
   share of entries and exits affected.
``python -m pattern_search.dry_check`` writes reports/stage_e20_dry_check_step6.md and .json.
"""

from __future__ import annotations

import argparse
import sys
import time as _time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from pattern_search import backward as B
from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

SEED = 20261012
WINDOWS = (("W1", date(2010, 7, 1), date(2012, 9, 28)),
           ("W2", date(2014, 12, 15), date(2016, 2, 26)),
           ("W3", date(2017, 7, 10), date(2018, 9, 28)))
PORTS_G5 = ("cp1_ret", "cp2_range", "cp2_brk", "cp3_clv", "g05_gap")
DECLARED_LOSS = {  # plan 10.1: (backward dates, dates losing every row)
    "NQ": (2280, 6), "6E": (2280, 6), **{r: (2279, 313) for r in ("ZT", "ZF", "ZN", "ZB", "UB")},
    **{r: (2225, 477) for r in ("ZC", "ZS", "ZL")}, "LE": (1103, 63),
    **{r: (None, 0) for r in ("RTY", "TN", "CL", "NG", "GC", "HE")}}
DECLARED_RULING2 = {"LE": {1: 296}}
REPORT_MD_REL = "reports/stage_e20_dry_check_step6.md"
REPORT_JSON_REL = "reports/stage_e20_dry_check_step6.json"
TABLE_FEATURES = {  # feature -> backward table field it reads (S4-S10)
    "k1_vwap_dist": "equity_full", "k2_auction_mto": "auctions", "k2_auction_msince": "auctions",
    "k2_monthend_msince": "month_end_dates", "k4_eiafade_move": "wpsr",
    "k4_ngpre_mto": "ngs", "k4_ngpre_msince": "ngs"}


@dataclass(frozen=True)
class SentinelWorld:
    vehicles: tuple[str, ...]
    bars: Mapping[str, pd.DataFrame]
    blackout: Mapping[str, frozenset[date]]
    releases: Any
    costs: Mapping[str, Any]
    calendar: tuple[date, ...] = ()
    first: Mapping[str, date] = field(default_factory=dict)


def _vehicle_of(path: str) -> str:
    return next(v for v, p in K.VEHICLE_PATHS.items() if p == path)


def sentinel_bars(paths: Sequence[str], first: date, last: date, *, seed: int = SEED,
                  floor: bool = True) -> dict[str, pd.DataFrame]:
    """Inside the context: synthetic bars of each path from max(first, its B1 first date)
    (``floor`` False: from ``first``)."""
    from ml_route_v2.synthetic import _root_bars, default_vol_ticks

    out = {}
    for p in paths:
        lo = max(first, B.B1_FIRST[p]) if floor else first
        if lo > last:
            continue
        out[p] = _root_bars(p, lo, last, seed=seed, vol_ticks=default_vol_ticks(p), plants=(),
                            vehicles=(), compact=True)
    return out


def sentinel_world(first: date, last: date, releases: Any, *, seed: int = SEED,
                   drop: Sequence[str] = ()) -> SentinelWorld:
    """Inside the context: the world of the vehicles listed by ``last``, without ``drop``."""
    from ml_route_v2.targets import frozen_costs

    paths = [p for p in K.PATH_ROOTS if B.B1_FIRST[p] <= last and p not in drop]
    bars = sentinel_bars(paths, first, last, seed=seed)
    vs = tuple(_vehicle_of(p) for p in bars)
    return SentinelWorld(vs, bars, {p: frozenset() for p in bars}, releases,
                         frozen_costs(vs), first={p: max(first, B.B1_FIRST[p]) for p in bars})


def b1_rows(world: Any, exclusions: Mapping[str, frozenset[date]] | None = None,
            vehicles: Sequence[str] | None = None) -> pd.DataFrame:
    """Inside the context: the frozen clock (hist calendars) plus t4, with each vehicle's own
    roll blackout and the B1 exclusions (rulings 5 and 6) removed."""
    from ml_route_v2.clock import decision_rows, trade_dates_of
    from ml_route_v2.constants import UNIVERSE
    from ml_route_v2.pipeline import own_blackout
    from pattern_search.rows import with_t4

    vs = tuple(vehicles if vehicles is not None else world.vehicles)
    excl = own_blackout(world.blackout, vs)
    for v in vs:
        excl[v] = frozenset(excl.get(v, frozenset()) | (exclusions or {}).get(v, frozenset()))
    rows = decision_rows(vs, {v: trade_dates_of(world.bars[UNIVERSE[v][1]]) for v in vs},
                         exclude=excl)
    return with_t4(rows)


def _ctx(world: Any, rows: pd.DataFrame, *, unit_sigma: bool = False) -> Any:
    from ml_route_v2.signals import SignalContext
    from ml_route_v2.targets import sigma_d

    sig = pd.Series(1.0, index=rows.index) if unit_sigma else sigma_d(rows, world.bars)
    return SignalContext(rows, world.bars, world.releases, sig, blackout=world.blackout)


def apply_ruling2(world: Any, rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(kept rows, excluded rows) under ruling 2 (backward.late_always_applicable_mask)."""
    mask = B.late_always_applicable_mask(_ctx(world, rows))
    return rows.loc[~mask].reset_index(drop=True), rows.loc[mask].reset_index(drop=True)


def ruling2_counts(excluded: pd.DataFrame) -> dict[str, dict[int, int]]:
    out: dict[str, dict[int, int]] = {}
    for (root, k), n in excluded.groupby(["path_root", "t_index"]).size().items():
        out.setdefault(str(root), {})[int(k)] = int(n)
    return out


# ------------------------------------------------------------------ 1. features ----
def _event_days(tables: Any, name: str, vehicle: str) -> set[date] | None:
    fld = TABLE_FEATURES.get(name)
    if fld is None:
        return None
    if fld == "auctions":
        from strategy.members.k2._event_common import AUCTION_TENOR

        tenor = AUCTION_TENOR.get(vehicle)
        return {date.fromisoformat(d) for d, t, _ in tables.auctions if t == tenor}
    if fld == "month_end_dates":
        return set(tables.month_end_dates)
    rows = getattr(tables, fld)
    return {date.fromisoformat(r[0] if isinstance(r, (tuple, list)) else r) for r in rows}


def _served(name: str, rows: pd.DataFrame, sig: pd.DataFrame) -> list[str]:
    """Vehicles on whose rows the feature is ever applicable or whose spec names them."""
    app = sig[f"app_{name}"].to_numpy() > 0
    return sorted(set(rows.loc[app, "root"]))


def feature_records(world: Any, rows: pd.DataFrame, tables: Any, window: str
                    ) -> tuple[dict[str, dict[str, Any]], pd.DataFrame]:
    """Inside the full context: compute every KEPT signal and both rod features on ``rows``."""
    from ml_route_v2.signals import compute_signals
    from pattern_search.features import rod_frame

    ctx = _ctx(world, rows)
    sig = compute_signals(ctx, K.KEPT_SIGNALS)
    rod = rod_frame(ctx)
    frame = pd.concat([sig, rod], axis=1)
    days = pd.to_datetime(rows["trade_date"]).dt.date.to_numpy()
    out = {}
    for name in K.FEATURE_NAMES:
        app = frame[f"app_{name}"].to_numpy() > 0
        val = frame[f"raw_{name}"].to_numpy(np.float64)
        rec: dict[str, Any] = {"window": window, "rows": int(len(rows)), "app_rows": int(app.sum()),
                               "finite_app_rows": int((app & np.isfinite(val)).sum()),
                               "vehicles_applicable": _served(name, rows, frame)}
        if name in TABLE_FEATURES:
            outside, hit_days, table_days_in_window = 0, set(), 0
            for v in pd.unique(rows["root"]):
                ev = _event_days(tables, name, v) or set()
                sel = (rows["root"] == v).to_numpy()
                in_tab = np.array([d in ev for d in days[sel]], dtype=bool)
                outside += int((app[sel] & ~in_tab).sum())
                hit_days |= set(days[sel][app[sel] & in_tab])
                if rec["vehicles_applicable"] and v in rec["vehicles_applicable"]:
                    table_days_in_window += len({d for d in days[sel] if d in ev})
            rec.update({"app_rows_off_table_dates": outside,
                        "event_dates_applicable": len(hit_days),
                        "event_dates_of_served_vehicles": table_days_in_window})
        out[name] = rec
    return out, frame


def _verdict(rec: Mapping[str, Any], expect: bool) -> tuple[bool, str]:
    if not expect:
        return True, "no served vehicle listed in this window"
    if rec["app_rows"] == 0:
        return False, "never applicable"
    if rec["finite_app_rows"] == 0:
        return False, "applicable but never finite"
    if rec.get("app_rows_off_table_dates", 0):
        return False, "applicable off its table's event dates"
    if "event_dates_applicable" in rec and rec["event_dates_applicable"] == 0:
        return False, "no event date applicable"
    return True, ""


SERVES = {  # vehicles a feature serves (spec scope), for "is it expected in this window"
    "k1_vwap_dist": ("MNQ",), "k2_auction_mto": ("ZT", "ZF", "ZN", "ZB", "UB", "TN"),
    "k2_auction_msince": ("ZT", "ZF", "ZN", "ZB", "UB", "TN"),
    "k2_monthend_msince": ("TN", "UB", "ZB", "ZN", "ZF", "ZT"), "k4_eiafade_move": ("MCL",),
    "k4_ngpre_mto": ("NG",), "k4_ngpre_msince": ("NG",), "k4_ovr_ret": ("MCL", "NG"),
    "k4_ovr_pct": ("MCL", "NG"), "k5_ovr_ret": ("MGC",), "k5_ovr_pct": ("MGC",)}


def feature_check(tables: Any, releases: Any, *,
                  windows: Sequence[tuple[str, date, date]] = WINDOWS,
                  seed: int = SEED) -> dict[str, Any]:
    """Item 1 (module docstring), with the calendar-only control."""
    out: dict[str, Any] = {"windows": {}, "features": {n: {} for n in K.FEATURE_NAMES},
                           "control_calendar_only": {}, "ruling2": {}}
    excl = B.b1_exclusions(tables.calendars)
    for wname, first, last in windows:
        t0 = _time.perf_counter()
        with B.backward_context(tables):
            w = sentinel_world(first, last, releases, seed=seed)
            rows, dropped = apply_ruling2(w, b1_rows(w, excl))
            recs, _frame = feature_records(w, rows, tables, wname)
        with B.backward_context(tables, patches=B.CALENDAR_PATCHES):
            from ml_route_v2.signals import compute_signals

            ctl = compute_signals(_ctx(w, rows), list(SERVES))
        for name, rec in recs.items():
            served = SERVES.get(name)
            expect = served is None or any(v in w.vehicles for v in served)
            ok, why = _verdict(rec, expect)
            out["features"][name][wname] = {**rec, "passes": ok, "why": why}
        out["control_calendar_only"][wname] = {
            n: int(((ctl[f"app_{n}"].to_numpy() > 0)
                    & np.isfinite(ctl[f"raw_{n}"].to_numpy())).sum()) for n in SERVES}
        out["ruling2"][wname] = ruling2_counts(dropped)
        out["windows"][wname] = {"first": first, "last": last, "vehicles": list(w.vehicles),
                                 "rows": int(len(rows)), "rows_ruling2": int(len(dropped)),
                                 "wall_s": round(_time.perf_counter() - t0, 1)}
    out["failures"] = sorted({n for n, per in out["features"].items()
                              for r in per.values() if not r["passes"]})
    return out


# ------------------------------------------------------------------ 2. legs ----
def leg_check(tables: Any, releases: Any, *, window: tuple[str, date, date] = WINDOWS[2],
              seed: int = SEED) -> dict[str, Any]:
    """Item 2 (module docstring): every removal stops the build."""
    from ml_route_v2.signals import SignalInputMissing, compute_signals
    from ml_route_v2.targets import TargetInputMissing

    _wname, first, last = window
    out: dict[str, Any] = {}
    with B.backward_context(tables):
        full = sentinel_world(first, last, releases, seed=seed)
        rows, _ = apply_ruling2(full, b1_rows(full))
        for p in full.bars:
            bars = {r: f for r, f in full.bars.items() if r != p}
            cut = SentinelWorld(full.vehicles, bars, {r: frozenset() for r in bars}, releases,
                                full.costs)
            rec: dict[str, Any] = {}
            try:
                b1_rows(cut)
                rec["builder"] = "did not raise"
            except (KeyError, SignalInputMissing) as exc:
                rec["builder"] = f"{type(exc).__name__}: {exc}"[:160]
            try:  # sigma_X,d set to 1 so the failure comes from a feature reading the leg
                compute_signals(_ctx(cut, rows, unit_sigma=True), K.KEPT_SIGNALS)
                rec["signals"] = "did not raise"
            except SignalInputMissing as exc:
                rec["signals"] = f"SignalInputMissing: {exc}"[:160]
            try:
                _ctx(cut, rows)
                rec["sigma_d"] = "did not raise"
            except TargetInputMissing as exc:
                rec["sigma_d"] = f"TargetInputMissing: {exc}"[:120]
            rec["stops"] = rec["builder"] != "did not raise" and rec["signals"] != "did not raise"
            rec["names_the_leg"] = p in rec["signals"]
            out[p] = rec
    return out


# ------------------------------------------------------------------ 3. row losses ----
def _all_rows_lost(rows: pd.DataFrame, frame: pd.DataFrame, names: Sequence[str],
                   extra_missing: np.ndarray | None = None) -> set[date]:
    miss = np.zeros(len(rows), dtype=bool)
    for n in names:
        app = frame[f"app_{n}"].to_numpy() > 0
        miss |= app & ~np.isfinite(frame[f"raw_{n}"].to_numpy(np.float64))
    if extra_missing is not None:
        miss |= extra_missing
    days = pd.to_datetime(rows["trade_date"]).dt.date
    lost = pd.Series(miss).groupby(days.to_numpy()).all()
    return {d for d, v in lost.items() if v}


def _boundary_loss(world: Any, p: str, first: date, last: date, releases: Any, seed: int
                   ) -> dict[str, Any]:
    """Inside the context: whether the window's first kept date loses every row when the bars
    start at the window's first date (B1's state: no d-1 bars for G5's prior C or cp3)."""
    from ml_route_v2.signals import compute_signals
    from pattern_search.rows import with_t4  # noqa: F401  (b1_rows uses it)

    end = min(last, first + pd.Timedelta(days=21).to_pytimedelta())
    bars = sentinel_bars((p,), first, end, seed=seed)
    w = SentinelWorld(world.vehicles, bars, {p: frozenset()}, releases, world.costs)
    rows = b1_rows(w)
    if not len(rows):
        return {"first_kept_date": None, "lost": False}
    d0 = min(pd.to_datetime(rows["trade_date"]).dt.date)
    try:
        rows, _ = apply_ruling2(w, rows)
        frame = compute_signals(_ctx(w, rows, unit_sigma=True), PORTS_G5)
    except IndexError as exc:  # frozen ports._cp3 on a frame with no port-complete day
        return {"first_kept_date": d0, "lost": None,
                "note": f"frozen ports._cp3 raises IndexError ({exc}) on a frame whose first "
                        "three weeks hold no port-complete day; the date's own inputs are absent"}
    return {"first_kept_date": d0, "lost": d0 in _all_rows_lost(rows, frame, PORTS_G5)}


def row_loss_check(tables: Any, releases: Any, *, roots: Sequence[str] = K.PATH_ROOTS,
                   seed: int = SEED) -> dict[str, Any]:
    """Item 3 (module docstring), one root at a time over its whole B1 window."""
    from data.group_session import previous_trade_date, trade_dates_between
    from ml_route.inputs import _group_calendar
    from ml_route_v2.signals import compute_signals
    from ml_route_v2.targets import frozen_costs

    out: dict[str, Any] = {}
    for p in roots:
        v = _vehicle_of(p)
        t0 = _time.perf_counter()
        with B.backward_context(tables):
            from data.calendars import GROUP_OF_PRODUCT

            cal = _group_calendar(GROUP_OF_PRODUCT[v])
            first, last = B.B1_FIRST[p], B.B1_LAST
            n_trade = len(trade_dates_between(cal, first, last))
            # bars from the trade date before the window, so the first date's d-1 inputs exist
            # as the calendar-only table assumes; the B1 boundary is counted separately below
            prev = previous_trade_date(cal, first)
            bars = sentinel_bars((p,), prev, last, seed=seed, floor=False)
            w = SentinelWorld((v,), bars, {p: frozenset()}, releases, frozen_costs((v,)))
            rows_all = b1_rows(w)
            rows_all = rows_all.loc[pd.to_datetime(rows_all["trade_date"]).dt.date
                                    >= first].reset_index(drop=True)
            boundary = _boundary_loss(w, p, first, last, releases, seed)
            kept_dates = set(pd.to_datetime(rows_all["trade_date"]).dt.date)
            rows, dropped = apply_ruling2(w, rows_all)
            unit = compute_signals(_ctx(w, rows, unit_sigma=True), PORTS_G5)
            true = compute_signals(_ctx(w, rows), (*PORTS_G5, "g09_vol_state"))
            sig_nan = ~np.isfinite(_ctx(w, rows).sigma_d.to_numpy(np.float64))
        lost = _all_rows_lost(rows, unit, PORTS_G5)
        lost_wu = _all_rows_lost(rows, true, (*PORTS_G5, "g09_vol_state"), sig_nan)
        declared_dates, declared_lost = DECLARED_LOSS[p]
        out[p] = {"vehicle": v, "window": [first, last], "trade_dates": n_trade,
                  "kept_dates": len(kept_dates), "dates_all_rows_lost": len(lost),
                  "boundary": boundary,
                  "share": len(lost) / n_trade if n_trade else None,
                  "declared": {"trade_dates": declared_dates, "dates_all_rows_lost": declared_lost},
                  "reproduced": len(lost) == declared_lost and (declared_dates is None
                                                               or declared_dates == n_trade),
                  "dates_all_rows_lost_with_sigma_g9_warmup": len(lost_wu),
                  "first_lost": sorted(lost)[:3], "last_lost": sorted(lost)[-3:],
                  "ruling2_excluded": ruling2_counts(dropped).get(p, {}),
                  "wall_s": round(_time.perf_counter() - t0, 1)}
    return out


# ------------------------------------------------------------------ 4. fallback reach ----
def _type_minutes(hist_types: frozenset[str]) -> dict[str, tuple[set[int], set[str]]]:
    """Release type -> (its frozen CT minutes, roots it concerns), for types with no 2010-2019
    rows (base_rules.costs.build_release_rules' rule, per type)."""
    import json

    doc = json.loads(B.read_source("e2b_frozen"))
    out: dict[str, tuple[set[int], set[str]]] = {}
    for r in doc["releases"]:
        if not ("2019-05-01" <= str(r["date"]) <= "2024-02-29") or not r.get("instant_utc"):
            continue
        kind = str(r["release"])
        if kind in hist_types:
            continue
        ct = B._ct(r["instant_utc"])
        mins, roots = out.setdefault(kind, (set(), set()))
        mins.add(ct.hour * 60 + ct.minute)
        roots.update(r.get("products") or ())
    return out


def fallback_table(tables: Any, rules: Any) -> dict[str, Any]:
    """Item 4 (PR-16): nominal fills in ruling 4's windows on the backward kept dates."""
    from base_rules import constants as BK
    from data.calendars import GROUP_OF_PRODUCT
    from data.group_session import trade_dates_between
    from ml_route.inputs import _group_calendar
    from ml_route_v2.clock import decision_rows, minutes_after_midnight_ct
    from pattern_search.rows import with_t4

    types = _type_minutes(frozenset(rules.hist_types))
    detail, summary = [], {}
    with B.backward_context(tables):
        for v, p in K.VEHICLE_PATHS.items():
            cal = _group_calendar(GROUP_OF_PRODUCT[v])
            days = trade_dates_between(cal, B.B1_FIRST[p], B.B1_LAST)
            rows = with_t4(decision_rows((v,), {v: days}))
            t = minutes_after_midnight_ct(rows["decision_ts_ns"].to_numpy(np.int64))
            f = minutes_after_midnight_ct(rows["flatten_ts_ns"].to_numpy(np.int64))
            k = rows["t_index"].to_numpy()
            roots = {v, p, BK.VEHICLE_OF.get(p, p)}
            mine = {kind: m for kind, (m, rs) in types.items() if roots & rs}
            fills = {"entry": {kk: t[k == kk] for kk in (1, 2, 3, 4)}}
            exits = {}
            for kk in (1, 2, 3, 4):
                sel = k == kk
                exits[(kk, "h60")] = np.where(t[sel] + 60 <= f[sel], t[sel] + 60, -1)
                exits[(kk, "h120")] = np.where(t[sel] + 120 <= f[sel], t[sel] + 120, -1)
                exits[(kk, "hF")] = f[sel]
            any_e = {kk: np.zeros(int((k == kk).sum()), dtype=bool) for kk in (1, 2, 3, 4)}
            any_x = {key: np.zeros(len(val), dtype=bool) for key, val in exits.items()}
            for kind, mins in sorted(mine.items()):
                for kk, tt in fills["entry"].items():
                    hit = np.zeros(len(tt), dtype=bool)
                    for m in mins:
                        hit |= (tt >= m) & (tt < m + BK.EVENT_MINUTES)
                    any_e[kk] |= hit
                    if hit.any():
                        detail.append({"vehicle": v, "type": kind, "minutes_ct": sorted(mins),
                                       "t_index": kk, "horizon": "all", "side": "entry",
                                       "fills": int(len(tt)), "affected": int(hit.sum())})
                for (kk, h), xx in exits.items():
                    hit = np.zeros(len(xx), dtype=bool)
                    for m in mins:
                        hit |= (xx >= m) & (xx < m + BK.EVENT_MINUTES)
                    any_x[(kk, h)] |= hit
                    if hit.any():
                        detail.append({"vehicle": v, "type": kind, "minutes_ct": sorted(mins),
                                       "t_index": kk, "horizon": h, "side": "exit",
                                       "fills": int((xx >= 0).sum()), "affected": int(hit.sum())})
            n_e = sum(len(a) for a in any_e.values())
            n_x = sum(int((exits[key] >= 0).sum()) for key in exits)
            summary[v] = {"types": sorted(mine), "kept_dates": int(len(set(rows["trade_date"]))),
                          "entries": n_e,
                          "entries_affected": int(sum(a.sum() for a in any_e.values())),
                          "exits": n_x, "exits_affected": int(sum(a.sum() for a in any_x.values()))}
            summary[v]["entry_share"] = summary[v]["entries_affected"] / n_e if n_e else None
            summary[v]["exit_share"] = summary[v]["exits_affected"] / n_x if n_x else None
    return {"note": "nominal fill minutes (entry at t; exit at t + h when within F, or F); the "
                    "D9.5a deferral and ruling 3's session-end exits are not applied here",
            "summary": summary, "detail": detail,
            "types_without_hist_rows": {k: sorted(m) for k, (m, _r) in sorted(types.items())}}


# ------------------------------------------------------------------ the report ----
def run_dry_check(*, windows: Sequence[tuple[str, date, date]] = WINDOWS,
                  roots: Sequence[str] = K.PATH_ROOTS, seed: int = SEED) -> dict[str, Any]:
    tables = B.backward_tables()
    rules = B.backward_release_rules()
    releases = rules.calendar
    t0 = _time.perf_counter()
    doc = {"schema": "stage_e20_dry_check_step6/1", "seed": seed,
           "tables": dict(tables.record), "reopenings": B.reopening_record(tables),
           "exclusions": {v: sorted(d.isoformat() for d in s)
                          for v, s in B.b1_exclusions(tables.calendars).items() if s},
           "fallback_ct_minutes": rules.record.get("fallback_ct_minutes")}
    doc["features"] = feature_check(tables, releases, windows=windows, seed=seed)
    doc["legs"] = leg_check(tables, releases, window=windows[-1], seed=seed)
    doc["row_losses"] = row_loss_check(tables, releases, roots=roots, seed=seed)
    doc["fallback"] = fallback_table(tables, rules)
    doc["wall_s"] = round(_time.perf_counter() - t0, 1)
    doc["passes"] = {
        "features": not doc["features"]["failures"],
        "legs": all(r["stops"] for r in doc["legs"].values()),
        "row_losses": all(r["reproduced"] for r in doc["row_losses"].values()),
        "ruling2_only_le_t1": all(set(c) <= {"LE"} for c in doc["features"]["ruling2"].values())
        and all((not r["ruling2_excluded"]) or (p == "LE" and set(r["ruling2_excluded"]) == {1})
                for p, r in doc["row_losses"].items())}
    return doc


def _pct(x: Any) -> str:
    return "n/a" if x is None else f"{100 * float(x):.1f}%"


def report_md(doc: Mapping[str, Any]) -> str:
    L = ["# Stage E.20 Step 6 sentinel dry check (synthetic sentinel frames, no store)", "",
         f"Written {doc.get('written_local')} (PDT) by pattern_search.dry_check (seed "
         f"{doc['seed']}, wall {doc['wall_s']} s). Plan sections 10.1 and 13; review PR-1, PR-15; "
         "recheck PR-16, PR-18.", "", "## Verdicts", ""]
    for k, v in doc["passes"].items():
        L.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    L += ["", f"Features failing: {doc['features']['failures'] or 'none'}", "",
          "Derived tables equal the frozen ones on the overlap: "
          f"{doc['tables'].get('overlap')}", "",
          "## 1. Every KEPT feature and both rod features under the swaps", "",
          "| Feature | " + " | ".join(f"{w} app rows / finite / event dates" for w in
                                     doc["features"]["windows"]) + " | Passes |",
          "|---|" + "---|" * len(doc["features"]["windows"]) + "---|"]
    for name, per in doc["features"]["features"].items():
        cells = []
        for w in doc["features"]["windows"]:
            r = per.get(w, {})
            ev = r.get("event_dates_applicable")
            cells.append(f"{r.get('app_rows')} / {r.get('finite_app_rows')}"
                         + (f" / {ev}" if ev is not None else ""))
        ok = all(r["passes"] for r in per.values())
        why = "; ".join(f"{w}: {r['why']}" for w, r in per.items() if r["why"])
        L.append(f"| {name} | " + " | ".join(cells) + f" | {'yes' if ok else 'NO'} {why} |")
    L += ["", "Calendar-only control (member tables left frozen): finite applicable rows per "
          "window", "", "| Feature | " + " | ".join(doc["features"]["control_calendar_only"])
          + " |", "|---|" + "---|" * len(doc["features"]["control_calendar_only"])]
    for n in SERVES:
        L.append(f"| {n} | " + " | ".join(str(c[n]) for c in
                                          doc["features"]["control_calendar_only"].values()) + " |")
    L += ["", "Windows: " + "; ".join(f"{w}: {r['first']}..{r['last']}, {len(r['vehicles'])} "
                                      f"vehicles, {r['rows']} rows ({r['rows_ruling2']} excluded "
                                      f"by ruling 2), {r['wall_s']} s"
                                      for w, r in doc["features"]["windows"].items()), "",
          "## 2. Removing one leg's frames stops the build", "",
          "| Root | Builder | compute_signals | Stops |", "|---|---|---|---|"]
    for p, r in doc["legs"].items():
        L.append(f"| {p} | {r['builder'][:60]} | {r['signals'][:70]} | {r['stops']} |")
    L += ["", "## 3. Declared row losses (plan 10.1) and ruling 2's exclusions (PR-18)", "",
          "| Root | Trade dates | Kept dates | Dates losing every row | Share | Declared | "
          "Reproduced | With sigma/G9 warm-up | Ruling 2 excluded (t_index: rows) | "
          "B1 first date lost (no d-1 bars) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for p, r in doc["row_losses"].items():
        d = r["declared"]
        L.append(f"| {p} | {r['trade_dates']} | {r['kept_dates']} | {r['dates_all_rows_lost']} | "
                 f"{_pct(r['share'])} | {d['dates_all_rows_lost']} ({d['trade_dates']}) | "
                 f"{r['reproduced']} | {r['dates_all_rows_lost_with_sigma_g9_warmup']} | "
                 f"{r['ruling2_excluded'] or '-'} | {r['boundary'].get('first_kept_date')}: "
                 f"{r['boundary'].get('lost')} |")
    L += ["", "Counts use sentinel bars from the trade date before each window, as the "
          "calendar-only table assumes d-1 bars; in B1 the bars start at the window's first date, "
          "whose rows are then lost too (last column). None marks the frozen ports._cp3 "
          "IndexError on a frame without any port-complete day (grains 2010, whose first dates "
          "lack their own 08:30 bar anyway).", "",
          "The warm-up column adds sigma_X,d's 20 complete dates and G9's 120 sigma values; "
          "for every root it includes the window-start warm-up, for the grains also the restart "
          "after 2012-05-21 (plan 10.1: about 615).", "",
          "## 4. Ruling 4's reach (PR-16): nominal fills in the fallback windows", "",
          doc["fallback"]["note"], "",
          "| Vehicle | Types without 2010-2019 rows | Kept dates | Entries affected | Share | "
          "Exits affected | Share |", "|---|---|---|---|---|---|---|"]
    for v, r in doc["fallback"]["summary"].items():
        L.append(f"| {v} | {', '.join(r['types']) or '-'} | {r['kept_dates']} | "
                 f"{r['entries_affected']} / {r['entries']} | {_pct(r['entry_share'])} | "
                 f"{r['exits_affected']} / {r['exits']} | {_pct(r['exit_share'])} |")
    L += ["", "| Vehicle | Type | CT minutes | t_index | Horizon | Side | Affected / fills |",
          "|---|---|---|---|---|---|---|"]
    for r in doc["fallback"]["detail"]:
        mins = ", ".join(f"{m // 60:02d}:{m % 60:02d}" for m in r["minutes_ct"])
        L.append(f"| {r['vehicle']} | {r['type']} | {mins} | t{r['t_index']} | {r['horizon']} | "
                 f"{r['side']} | {r['affected']} / {r['fills']} |")
    L += ["", "## Exclusions (rulings 5 and 6) and reopenings (ruling 7)", "",
          f"{doc['exclusions']}", "", f"{doc['reopenings']}", ""]
    return "\n".join(L) + "\n"


def write_report(doc: dict[str, Any], md_path: Path, json_path: Path) -> None:
    from pattern_search.results import write_atomic, write_json

    doc["written_local"] = datetime.now(ZoneInfo("America/Vancouver")).isoformat(
        timespec="seconds")
    write_json(json_path, doc)
    write_atomic(md_path, report_md(doc).encode())


def main(argv: Sequence[str] | None = None) -> int:
    from pattern_search import preflight as pf

    guard.install_audit_hook()
    parser = argparse.ArgumentParser(prog="python -m pattern_search.dry_check")
    parser.parse_args(argv)
    from compute.platform import lower_priority

    lower_priority()
    doc = run_dry_check()
    write_report(doc, pf.repo_path(REPORT_MD_REL), pf.repo_path(REPORT_JSON_REL))
    print(f"dry check: {doc['passes']} -> {REPORT_MD_REL}")
    return K.RC_OK if all(doc["passes"].values()) else K.RC_ERROR


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["DECLARED_LOSS", "WINDOWS", "SentinelWorld", "apply_ruling2", "b1_rows",
           "fallback_table", "feature_check", "leg_check", "main", "report_md", "row_loss_check",
           "run_dry_check", "sentinel_bars", "sentinel_world", "write_report"]
