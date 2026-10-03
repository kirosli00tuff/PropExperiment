"""V2.3 member signals of the core ports CP1, CP2 and CP3: one pooled feature per port variable.

Source: strategy/members/k<n>/cp1.py, cp2.py, cp3.py (D6 lines 364-366: each port is one rule
ported to every product; inventory reports/stage_e11_briefs/member_inventory.md "Core ports").
Lead ruling (Stage E.11): the 21 port families K1-cp1-01 .. K7-cp3-01 enter as four pooled
signals, each computed for every vehicle of constants.UNIVERSE by the same frozen definition on
the vehicle's price path with the vehicle's frozen D6 O and C, applicable on every product's rows
once the value is known at t (missing for data reasons stays NaN, V2.3):
- CP1 ``cp1_ret``: close(O+29) - open(first bar of trade date d), vehicle ticks ("sign and
  size", reading SC-3: the member's sign enters as the signed move). First bar: the 17:00 CT bar of
  CT date d-1 with trade date d (K1-K5, K7); grains: the first bar of trade date d opening at or
  after 19:00 CT d-1 (the 08:30 bar when there is no evening bar); livestock: the 08:30 bar of d.
  Both bars present with one instrument_id, else missing. Known at O+30 (= t1).
- CP2 ``cp2_range``: OR_high - OR_low of the present bars of CT date d opening in [O, O+15),
  vehicle ticks; ``cp2_brk``: the latest close (bars of d opening in [O+15, C) closed by t)
  beyond the range: close - OR_high above it, close - OR_low below it, 0 inside (vehicle ticks).
- CP3 ``cp3_clv``: CLV = (C - L) / (H - L) of the most recent port-complete day before d
  (Family H, signals._daily), H > L; d-1's instrument_id must equal the O bar of d's; known at the
  O bar's close.
"""

from __future__ import annotations

from functools import partial

import numpy as np
import pandas as pd

from ml_route_v2.clock import session_group
from ml_route_v2.constants import CLUSTERS, UNIVERSE
from ml_route_v2.signals._core import (
    NS_MIN,
    SignalContext,
    SignalSpec,
    bars_of,
    ct_ns,
    empty,
    minute_of,
    path_of,
    per_unit,
    result,
    rows_of,
)
from ml_route_v2.signals._daily import _segment_reduce, daily_of, session_minutes


def _member_literals() -> tuple[int, int, int, int, int]:
    """The ports' clock literals, read from the member modules (identical in k1..k7)."""
    from rules.sessions import LIVESTOCK_OPEN_CT
    from strategy.members.k1 import cp1, cp2
    from strategy.members.k6 import cp1 as k6cp1

    return (cp1.SIGNAL_AFTER_O_MIN, cp2.RANGE_MINUTES, minute_of(cp1.GLOBEX_OPEN_CT),
            minute_of(k6cp1.GRAIN_EVENING_OPEN_CT), minute_of(LIVESTOCK_OPEN_CT))


(SIGNAL_AFTER_O_MIN, RANGE_MINUTES, GLOBEX_OPEN_MIN, GRAIN_EVENING_MIN,
 LIVESTOCK_OPEN_MIN) = _member_literals()


def cluster_vehicles(cluster: str) -> tuple[str, ...]:
    return tuple(v for v, (k, _p) in UNIVERSE.items() if k == cluster)


def _first_bar(bars, vehicle: str, days: np.ndarray, o_min: int) -> np.ndarray:  # noqa: ANN001
    group = session_group(vehicle)
    if group == "livestock":
        idx = bars.at(ct_ns(days, LIVESTOCK_OPEN_MIN))
        return np.where(bars.on_day(idx, days), idx, -1)
    if group == "grains":
        start = ct_ns(days, GRAIN_EVENING_MIN, day_offset=-1)
        idx = np.searchsorted(bars.ts, start, side="left").astype(np.int64)
        idx = np.where(idx < len(bars.ts), idx, -1)
        idx = np.where(bars.on_day(idx, days), idx, -1)
        day_open = ct_ns(days, o_min)
        late = (idx >= 0) & (bars.ts[np.clip(idx, 0, None)] >= day_open)
        exact_open = bars.at(day_open)
        return np.where(late, np.where(exact_open == idx, idx, -1), idx)
    idx = bars.at(ct_ns(days, GLOBEX_OPEN_MIN, day_offset=-1))
    return np.where(bars.on_day(idx, days), idx, -1)


def _cp1(vehicles: tuple[str, ...], ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    for v in vehicles:
        rows = view.where_root((v,))
        if not len(rows):
            continue
        b = bars_of(ctx, path_of(v))
        o_min, _c = session_minutes(v)
        days = view.day[rows]
        first = _first_bar(b, v, days, o_min)
        sig = b.at(ct_ns(days, o_min + SIGNAL_AFTER_O_MIN))
        sig = np.where(b.on_day(sig, days), sig, -1)
        ok = (first >= 0) & (sig >= 0)
        ok[ok] = b.iid[first[ok]] == b.iid[sig[ok]]
        nominal = ct_ns(days, o_min + SIGNAL_AFTER_O_MIN) + NS_MIN
        known = nominal <= view.t[rows]
        val = np.full(len(rows), np.nan)
        val[ok] = (b.close[sig[ok]] - b.open[first[ok]]) * per_unit(v)
        value[rows[known]] = val[known]
        avail[rows[known]] = nominal[known]
        app[rows[known]] = True
    return result(view, value, app, avail)


def _opening_range(ctx: SignalContext, v: str, rows: np.ndarray
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(OR_high, OR_low, availability) per row; NaN when no range bar."""
    view = rows_of(ctx)
    b = bars_of(ctx, path_of(v))
    o_min, _c = session_minutes(v)
    days = view.day[rows]
    lo_ns = ct_ns(days, o_min)
    hi_ns = ct_ns(days, o_min + RANGE_MINUTES)
    dpos = b.day_pos(days)
    lo = np.searchsorted(b.ts, lo_ns, side="left")
    hi = np.searchsorted(b.ts, hi_ns, side="left")
    lo = np.where(dpos >= 0, np.maximum(lo, b.first[np.clip(dpos, 0, None)]), 0)
    hi = np.where(dpos >= 0, np.minimum(hi, b.last[np.clip(dpos, 0, None)] + 1), 0)
    return (_segment_reduce(b.high, lo, hi, "max"), _segment_reduce(b.low, lo, hi, "min"),
            hi_ns)


def _cp2_range(vehicles: tuple[str, ...], ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    for v in vehicles:
        rows = view.where_root((v,))
        if not len(rows):
            continue
        orh, orl, known_at = _opening_range(ctx, v, rows)
        known = known_at <= view.t[rows]
        value[rows[known]] = ((orh - orl) * per_unit(v))[known]
        avail[rows[known]] = known_at[known]
        app[rows[known]] = True
    return result(view, value, app, avail)


def _cp2_brk(vehicles: tuple[str, ...], ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    for v in vehicles:
        rows = view.where_root((v,))
        if not len(rows):
            continue
        b = bars_of(ctx, path_of(v))
        o_min, c_min = session_minutes(v)
        days, t = view.day[rows], view.t[rows]
        orh, orl, known_at = _opening_range(ctx, v, rows)
        start = known_at  # bars opening at or after O+15
        end = np.minimum(t, ct_ns(days, c_min))  # closed by t, opening before C
        j = np.searchsorted(b.ts, end - NS_MIN, side="right") - 1
        ok = (j >= 0) & b.on_day(j, days)
        ok[ok] &= b.ts[j[ok]] >= start[ok]
        known = known_at <= t
        c = np.where(ok, b.close[np.clip(j, 0, None)], np.nan)
        dist = np.where(c > orh, c - orh, np.where(c < orl, c - orl, 0.0))
        dist = np.where(ok & np.isfinite(orh), dist * per_unit(v), np.nan)
        av = np.where(ok, b.ts[np.clip(j, 0, None)] + NS_MIN, -1)
        has_bar_after = known & ok
        sel = rows[known]
        value[sel] = dist[known]
        avail[sel] = np.where(has_bar_after[known], av[known], -1)
        app[sel] = True
    return result(view, value, app, avail)


def _cp3(vehicles: tuple[str, ...], ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    for v in vehicles:
        rows = view.where_root((v,))
        if not len(rows):
            continue
        b = bars_of(ctx, path_of(v))
        dl = daily_of(ctx, v)
        o_min, _c = session_minutes(v)
        days, t = view.day[rows], view.t[rows]
        comp = np.flatnonzero(dl.port_complete & (dl.hi > dl.lo))
        k = np.searchsorted(dl.days[comp], days, side="left") - 1  # strictly earlier date
        has = k >= 0
        prev = np.where(has, comp[np.clip(k, 0, None)], -1)
        o_ns = ct_ns(days, o_min)
        o_idx = b.at(o_ns)
        o_idx = np.where(b.on_day(o_idx, days), o_idx, -1)
        ok = has & (o_idx >= 0)
        c1 = np.where(ok, dl.c1_idx[np.clip(prev, 0, None)], -1)
        ok &= c1 >= 0
        ok[ok] = b.iid[c1[ok]] == b.iid[o_idx[ok]]
        clv = np.full(len(rows), np.nan)
        p = prev[ok]
        clv[ok] = (dl.c1_close[p] - dl.lo[p]) / (dl.hi[p] - dl.lo[p])
        nominal = o_ns + NS_MIN
        known = nominal <= t
        value[rows[known]] = clv[known]
        avail[rows[known]] = nominal[known]
        app[rows[known]] = True
    return result(view, value, app, avail)


VEHICLES = tuple(UNIVERSE)
ALL_PATHS = tuple(sorted({path_of(v) for v in VEHICLES}))
_SRC = "strategy/members/k1..k7/cp%d.py (one rule, D6 lines 364-366)"
# Lead ruling (Stage E.11, after the Task 2 return): one pooled feature per port variable.
SPECS = (
    SignalSpec("cp1_ret", "CP1", None, "member", _SRC % 1, ALL_PATHS, True,
               partial(_cp1, VEHICLES), own_path_only=True),
    SignalSpec("cp2_range", "CP2", None, "member", _SRC % 2, ALL_PATHS, True,
               partial(_cp2_range, VEHICLES), own_path_only=True),
    SignalSpec("cp2_brk", "CP2", None, "member", _SRC % 2, ALL_PATHS, True,
               partial(_cp2_brk, VEHICLES), own_path_only=True),
    SignalSpec("cp3_clv", "CP3", None, "member", _SRC % 3, ALL_PATHS, True,
               partial(_cp3, VEHICLES), own_path_only=True),
)
PORT_SIGNALS = {"CP1": ("cp1_ret",), "CP2": ("cp2_range", "cp2_brk"), "CP3": ("cp3_clv",)}
# the 21 inventory families the pooled signals carry (K1-cp1-01 .. K7-cp3-01)
FAMILIES = {f"{k}-cp{i}-01": PORT_SIGNALS[f"CP{i}"] for k in CLUSTERS for i in (1, 2, 3)}
# known by t1 = O + 30 on every product's rows: the app_ flag is constant 1 (panel reading PN-1)
ALWAYS_APPLICABLE = frozenset(s.name for s in SPECS)

__all__ = ["ALWAYS_APPLICABLE", "FAMILIES", "PORT_SIGNALS", "SPECS", "VEHICLES",
           "cluster_vehicles"]
