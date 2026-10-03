"""V2.3 generic features G1-G17 (G18, G19 identifiers are built in panel.py).

docs/STAGE_E_ML_V2_DESIGN.md V2.3 "Generic features"; v1 ml_route/features.py and rows.py
readings kept where the feature is v1's (F1-F17). Every value reads the row's own price path
(prices in vehicle ticks) from bars closed by t, or calendars known in advance:
- "the bar at t" is the bar closing at t (opening t - 1 min) with the row's trade date; absent:
  missing (V2.3, "an absent bar at t"). G1-G3: close(t) - close(t - k) (the bar closing at t - k
  must exist on the same trade date); G4: close(t) - open(first bar of the trade date). G1-G5,
  G7, G8 are divided by sigma_X,d (reading SG-1: v1's F1-F7 convention; G7, G8 say so).
- G5: open of the O_X bar of d minus the close of the C_X - 1 bar of the group calendar's previous
  trade date (v1 F7); reading SG-4: when that date is an early-halt date (no C_X close exists),
  G5 is not applicable. G6: sqrt of the sum of squared one-minute close changes of the bars closing
  in (t - 60, t] on the trade date, over its mean at the same decision time on the product's 20
  previous row dates (v1 F10's same-clock window). G7: high - low of the trade date's bars closed
  by t. G8: close(C-1) - open(O) of the most recent complete date before d (signals._daily).
  G9: sigma_X,d over its median over the 120 dates ending at d (v1 F17). G10: log of the volume of
  the bars closing in (t - 30, t] over the median of the same window on the 20 previous row dates.
- G11 decision-time index, G12 day of week, G15 release day, G16 month end: flags, not normalized.
  G13/G14: minutes to the next release at or after t / since the last before t (v1 F13/F14) from
  the vehicle's D8 list; not applicable outside the calendar's coverage.
- G16: the last two trade dates of the month of the vehicle's group calendar.
- G17: the 60-minute log return (x 1e4) of each other cluster's lead price path and of MES, from
  the lead's latest bar closed by t and its latest bar at least 60 minutes before that, both of the
  row's trade date (v1 F16 kept as-of). Reading SG-2: a lead with no such bar (not listed, not
  trading) is "not applicable" (0 plus flag); the row's own cluster lead is not applicable.
"""

from __future__ import annotations

from datetime import date
from functools import lru_cache, partial

import numpy as np
import pandas as pd

from ml_route_v2.constants import (
    CLUSTER_LEADS,
    G6_RV_MINUTES,
    G10_VOLUME_MINUTES,
    G16_MONTH_END_DATES,
    G17_LOG_RETURN_SCALE,
    G17_RETURN_MINUTES,
    G_BASE_DATES,
    G_RETURN_MINUTES,
    SIGNAL_ONLY_ROOTS,
    UNIVERSE,
)
from ml_route_v2.signals._core import (
    NS_MIN,
    RowsView,
    SignalContext,
    SignalSpec,
    as_date,
    bars_of,
    empty,
    epoch_day,
    path_of,
    per_unit,
    release_coverage,
    release_times,
    result,
    rows_of,
    weekday,
    window_sums,
)
from ml_route_v2.signals._daily import _segment_reduce, daily_of, in_session

RETURN_MINUTES = dict(zip(("g01_ret30", "g02_ret60", "g03_ret120"), G_RETURN_MINUTES,
                          strict=True))
RV_MINUTES = G6_RV_MINUTES
VOL_MINUTES = G10_VOLUME_MINUTES
BASE_DATES = G_BASE_DATES
LEAD_MINUTES = G17_RETURN_MINUTES
LEAD_SCALE = G17_LOG_RETURN_SCALE
ALL_PATHS = tuple(sorted({p for _k, p in UNIVERSE.values()}))
_SRC = "docs/STAGE_E_ML_V2_DESIGN.md V2.3 "


def _own(ctx: SignalContext) -> dict[str, np.ndarray]:
    """Per row: the bar closing at t on the trade date (``it``), the trade date's first bar
    (``first``) and the vehicle's ticks per vendor unit (``pu``)."""
    if "own" in ctx.cache:
        return ctx.cache["own"]
    view = rows_of(ctx)
    it = np.full(view.n, -1, dtype=np.int64)
    first = np.full(view.n, -1, dtype=np.int64)
    pu = np.full(view.n, np.nan)
    for v, rows in view.by_root().items():
        b = bars_of(ctx, path_of(v))
        days = view.day[rows]
        i = b.at(view.t[rows] - NS_MIN)
        it[rows] = np.where(b.on_day(i, days), i, -1)
        dp = b.day_pos(days)
        first[rows] = np.where(dp >= 0, b.first[np.clip(dp, 0, None)], -1)
        pu[rows] = per_unit(v)
    ctx.cache["own"] = {"it": it, "first": first, "pu": pu}
    return ctx.cache["own"]


def _by_vehicle(ctx: SignalContext):  # noqa: ANN202 - generator of (vehicle, rows, bars)
    view = rows_of(ctx)
    for v, rows in view.by_root().items():
        yield v, rows, bars_of(ctx, path_of(v))


def _ret(minutes: int, ctx: SignalContext) -> pd.DataFrame:
    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    for v, rows, b in _by_vehicle(ctx):
        it = own["it"][rows]
        start = view.t[rows] - NS_MIN - minutes * NS_MIN
        ik = b.at(start)
        ok = (it >= 0) & b.on_day(ik, view.day[rows])
        val = np.full(len(rows), np.nan)
        val[ok] = (b.close[it[ok]] - b.close[ik[ok]]) * own["pu"][rows][ok]
        value[rows] = val / view.sigma[rows]
        avail[rows] = view.t[rows]
        app[rows] = in_session(v, view.day[rows], start)  # reading SG-3
    return result(view, value, app, avail)


def _ret_day(ctx: SignalContext) -> pd.DataFrame:
    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for _v, rows, b in _by_vehicle(ctx):
        it, first = own["it"][rows], own["first"][rows]
        ok = (it >= 0) & (first >= 0)
        val = np.full(len(rows), np.nan)
        val[ok] = (b.close[it[ok]] - b.open[first[ok]]) * own["pu"][rows][ok]
        value[rows] = val / view.sigma[rows]
        avail[rows] = view.t[rows]
    return result(view, value, app, avail)


@lru_cache(maxsize=200_000)
def _previous_trade_day(vehicle: str, day: int) -> int:
    from data.calendars import GROUP_OF_PRODUCT
    from data.group_session import previous_trade_date
    from ml_route.inputs import _group_calendar

    prev = previous_trade_date(_group_calendar(GROUP_OF_PRODUCT[vehicle]), as_date(day))
    return -1 if prev is None else epoch_day(prev)


def _gap(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    for v, rows, b in _by_vehicle(ctx):
        dl = daily_of(ctx, v)
        days = view.day[rows]
        pos = dl.pos(days)
        prev_days = np.array([_previous_trade_day(v, int(d)) for d in days], dtype=np.int64)
        ppos = dl.pos(prev_days)
        o = np.where(pos >= 0, dl.o_idx[np.clip(pos, 0, None)], -1)
        c1 = np.where(ppos >= 0, dl.c1_idx[np.clip(ppos, 0, None)], -1)
        ok = (o >= 0) & (c1 >= 0)
        val = np.full(len(rows), np.nan)
        val[ok] = (b.open[o[ok]] - b.close[c1[ok]]) * per_unit(v)
        value[rows] = val / view.sigma[rows]
        avail[rows] = np.where(ok, b.ts[np.clip(o, 0, None)] + NS_MIN, -1)
        # reading SG-4: after an early-halt date there is no C_X close to gap from
        app[rows] = ~((ppos >= 0) & dl.halt[np.clip(ppos, 0, None)])
    return result(view, value, app, avail)


def _base_ratio(view: RowsView, rows: np.ndarray, cur: np.ndarray, how: str) -> np.ndarray:
    """cur over its mean or median on the 20 previous row dates at the same decision time."""
    out = np.full(len(rows), np.nan)
    for k in np.unique(view.t_index[rows]):
        sel = np.flatnonzero(view.t_index[rows] == k)
        order = sel[np.argsort(view.day[rows][sel], kind="mergesort")]
        s = pd.Series(cur[order])
        roll = s.rolling(BASE_DATES, min_periods=BASE_DATES)
        base = (roll.mean() if how == "mean" else roll.median()).shift(1).to_numpy()
        out[order] = base
    return out


def _rv(ctx: SignalContext) -> pd.DataFrame:
    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for _v, rows, b in _by_vehicle(ctx):
        it, first, t = own["it"][rows], own["first"][rows], view.t[rows]
        lo = np.maximum(np.searchsorted(b.ts, t - RV_MINUTES * NS_MIN, side="left"), first)
        ok = (it >= 0) & (first >= 0) & (it - lo >= 1)

        def sq_change(idx: np.ndarray, b=b) -> np.ndarray:  # noqa: ANN001 - one root's bars
            return (b.close[idx] - b.close[idx - 1]) ** 2  # idx > lo >= the date's first bar

        rv = np.full(len(rows), np.nan)
        rv[ok] = np.sqrt(window_sums(sq_change, lo[ok] + 1, it[ok] + 1))
        base = _base_ratio(view, rows, rv, "mean")
        good = ok & np.isfinite(base) & (base > 0)
        val = np.full(len(rows), np.nan)
        val[good] = rv[good] / base[good]
        value[rows] = val
        avail[rows] = t
    return result(view, value, app, avail)


def _range(ctx: SignalContext) -> pd.DataFrame:
    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for _v, rows, b in _by_vehicle(ctx):
        it, first = own["it"][rows], own["first"][rows]
        ok = (it >= 0) & (first >= 0)
        lo = np.where(ok, first, 0)
        hi = np.where(ok, it + 1, 0)
        rng = _segment_reduce(b.high, lo, hi, "max") - _segment_reduce(b.low, lo, hi, "min")
        value[rows] = np.where(ok, rng * own["pu"][rows], np.nan) / view.sigma[rows]
        avail[rows] = view.t[rows]
    return result(view, value, app, avail)


def _prev_ret(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for v, rows, b in _by_vehicle(ctx):
        dl = daily_of(ctx, v)
        comp = np.flatnonzero(dl.complete)
        k = np.searchsorted(dl.days[comp], view.day[rows], side="left") - 1
        ok = k >= 0
        p = comp[np.clip(k, 0, None)]
        value[rows] = np.where(ok, dl.ret[p], np.nan) / view.sigma[rows]
        avail[rows] = np.where(ok, b.ts[np.clip(dl.c1_idx[p], 0, None)] + NS_MIN, -1)
    return result(view, value, app, avail)


def _vol_state(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for v, rows, _b in _by_vehicle(ctx):
        dl = daily_of(ctx, v)
        pos = dl.pos(view.day[rows])
        ok = pos >= 0
        p = np.clip(pos, 0, None)
        value[rows] = np.where(ok, dl.g9[p], np.nan)
        avail[rows] = np.where(ok, dl.sigma_avail[p], -1)
    return result(view, value, app, avail)


def _logvol(ctx: SignalContext) -> pd.DataFrame:
    view, own = rows_of(ctx), _own(ctx)
    value, app, avail = empty(view)
    app[:] = True
    for _v, rows, b in _by_vehicle(ctx):
        first, t = own["first"][rows], view.t[rows]
        lo = np.maximum(np.searchsorted(b.ts, t - VOL_MINUTES * NS_MIN, side="left"), first)
        hi = np.searchsorted(b.ts, t - NS_MIN, side="right")
        ok = (first >= 0) & (hi > lo)
        cur = np.full(len(rows), np.nan)
        cur[ok] = window_sums(b.volume, lo[ok], hi[ok])
        base = _base_ratio(view, rows, cur, "median")
        good = np.isfinite(cur) & (cur > 0) & np.isfinite(base) & (base > 0)
        val = np.full(len(rows), np.nan)
        val[good] = np.log(cur[good] / base[good])
        value[rows] = val
        avail[rows] = t
    return result(view, value, app, avail)


def _t_index(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    return result(view, view.t_index.astype(np.float64), np.ones(view.n, bool), view.t)


def _dow(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    return result(view, weekday(view.day).astype(np.float64), np.ones(view.n, bool), view.t)


def _covered(ctx: SignalContext, view: RowsView) -> np.ndarray:
    cov = release_coverage(ctx.releases)
    if cov is None:
        return np.ones(view.n, dtype=bool)
    return (view.day >= cov[0]) & (view.day <= cov[1])


def _ct_day(ns: np.ndarray) -> np.ndarray:
    idx = pd.to_datetime(ns, utc=True).tz_convert("America/Chicago").tz_localize(None)
    return idx.normalize().to_numpy().astype("datetime64[D]").astype(np.int64)


def _release(kind: str, ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    cov = _covered(ctx, view)
    for v, rows in view.by_root().items():
        rel = release_times(ctx.releases, v)
        t = view.t[rows]
        nxt = np.searchsorted(rel, t, side="left")
        padded = np.append(rel, -1)  # index len(rel) -> a sentinel, masked by ``ok``
        if kind == "to":
            ok = nxt < len(rel)
            val = (padded[nxt] - t) / NS_MIN
        elif kind == "since":
            ok = nxt > 0
            val = (t - padded[nxt - 1]) / NS_MIN
        else:
            rel_days = np.unique(_ct_day(rel)) if len(rel) else np.zeros(0, np.int64)
            ok = np.ones(len(rows), dtype=bool)
            val = np.isin(_ct_day(t), rel_days).astype(np.float64)
        ok = ok & cov[rows]
        value[rows[ok]] = val[ok]
        app[rows[ok]] = True
        avail[rows[ok]] = t[ok]
    return result(view, value, app, avail)


@lru_cache(maxsize=4096)
def _month_end_days(vehicle: str, year: int, month: int) -> tuple[int, ...]:
    from data.calendars import GROUP_OF_PRODUCT
    from data.group_session import trade_dates_between
    from ml_route.inputs import _group_calendar

    first = date(year, month, 1)
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    last = date.fromordinal(nxt.toordinal() - 1)
    days = trade_dates_between(_group_calendar(GROUP_OF_PRODUCT[vehicle]), first, last)
    return tuple(epoch_day(d) for d in days[-G16_MONTH_END_DATES:])


def _month_end(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value = np.zeros(view.n)
    for v, rows in view.by_root().items():
        for d in np.unique(view.day[rows]):
            day = as_date(int(d))
            if int(d) in _month_end_days(v, day.year, day.month):
                value[rows[view.day[rows] == d]] = 1.0
    return result(view, value, np.ones(view.n, dtype=bool), view.t)


def _lead(lead: str, ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    b = bars_of(ctx, lead)
    own_cluster = next((k for k, p in CLUSTER_LEADS.items() if p == lead), None)
    j = b.last_closed(view.t)
    ok = (j >= 0) & b.on_day(j, view.day)
    jj = np.clip(j, 0, None)
    j60 = np.searchsorted(b.ts, b.ts[jj] - LEAD_MINUTES * NS_MIN, side="right") - 1
    ok &= (j60 >= 0) & b.on_day(j60, view.day)
    j60 = np.clip(j60, 0, None)
    ok &= (b.close[jj] > 0) & (b.close[j60] > 0)
    if own_cluster is not None:
        ok &= view.cluster != own_cluster
    value[ok] = LEAD_SCALE * np.log(b.close[jj[ok]] / b.close[j60[ok]])
    avail[ok] = b.ts[jj[ok]] + NS_MIN
    app[ok] = True
    return result(view, value, app, avail)


def _specs() -> tuple[SignalSpec, ...]:
    g = []
    for name, minutes in RETURN_MINUTES.items():
        gid = f"G{int(name[1:3])}"
        g.append(SignalSpec(name, gid, None, "generic", _SRC + gid, ALL_PATHS, True,
                            partial(_ret, minutes), own_path_only=True))
    g += [
        SignalSpec("g04_ret_day", "G4", None, "generic", _SRC + "G4", ALL_PATHS, True, _ret_day,
                   own_path_only=True),
        SignalSpec("g05_gap", "G5", None, "generic", _SRC + "G5", ALL_PATHS, True, _gap,
                   own_path_only=True),
        SignalSpec("g06_rv60", "G6", None, "generic", _SRC + "G6", ALL_PATHS, True, _rv,
                   own_path_only=True),
        SignalSpec("g07_range", "G7", None, "generic", _SRC + "G7", ALL_PATHS, True, _range,
                   own_path_only=True),
        SignalSpec("g08_prev_ret", "G8", None, "generic", _SRC + "G8", ALL_PATHS, True,
                   _prev_ret, own_path_only=True),
        SignalSpec("g09_vol_state", "G9", None, "generic", _SRC + "G9", ALL_PATHS, True,
                   _vol_state, own_path_only=True),
        SignalSpec("g10_logvol30", "G10", None, "generic", _SRC + "G10", ALL_PATHS, True,
                   _logvol, own_path_only=True),
        SignalSpec("g11_t_index", "G11", None, "flag", _SRC + "G11", (), False, _t_index),
        SignalSpec("g12_dow", "G12", None, "flag", _SRC + "G12", (), False, _dow),
        SignalSpec("g13_min_to_rel", "G13", None, "generic", _SRC + "G13", (), True,
                   partial(_release, "to")),
        SignalSpec("g14_min_since_rel", "G14", None, "generic", _SRC + "G14", (), True,
                   partial(_release, "since")),
        SignalSpec("g15_rel_day", "G15", None, "flag", _SRC + "G15", (), False,
                   partial(_release, "day")),
        SignalSpec("g16_month_end", "G16", None, "flag", _SRC + "G16", (), False, _month_end),
    ]
    for lead in (*CLUSTER_LEADS.values(), *SIGNAL_ONLY_ROOTS):
        g.append(SignalSpec(f"g17_{lead.lower()}", "G17", None, "generic", _SRC + "G17",
                            (lead,), True, partial(_lead, lead)))
    return tuple(g)


SPECS = _specs()
# Signals applicable on every row by construction (their app_ flag is constant 1).
ALWAYS_APPLICABLE = frozenset({
    "g04_ret_day", "g06_rv60", "g07_range",
    "g08_prev_ret", "g09_vol_state", "g10_logvol30", "g11_t_index", "g12_dow", "g16_month_end"})

__all__ = ["ALL_PATHS", "ALWAYS_APPLICABLE", "SPECS"]
