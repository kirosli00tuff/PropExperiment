"""V2.3 member signals of K6's members (grain and livestock rows).

Sources: strategy/members/k6/crushgap.py, limitcont.py, wasdepre.py; tables
strategy/members/k6/_calendar.py (GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES, LIVESTOCK_*),
k6/_wasde.py (WASDE_DATES) and k6/_limits.py (LIMIT_PERIODS, DROPPED_LIMIT_DATES).
- ``k6_crushgap_gap`` (ZS, reads ZM and ZL): G(d) = GPM(08:30 opens of d) - GPM(13:14 closes of
  the previous GRAIN_TRADE_DATES entry), GPM = 0.022 P_ZM + 11 P_ZL - P_ZS in USD/bu (vendor price
  / vendor_price_factor; crushgap.GPM_WEIGHTS); each leg's two bars present with one
  instrument_id; d in GRAIN_FULL_SESSIONS; known at 08:31 CT.
- ``k6_limitcont_dir`` (HE, LE): +1 after a limit-up settlement of d-1 (S(d-1) - S(d-2) = +L(d-1)
  ticks exactly, S(d-2) - S(d-3) not +-L(d-2)), -1 after limit-down, else not applicable; S = the
  D9.7 proxy (limitcont.settlement_window: volume-weighted close of the bars opening in the
  window, else the last close before its end), every bar it uses carrying the instrument_id of d's
  08:30 bar; L = limitcont.limit_ticks; dates d-1, d-2 in DROPPED_LIMIT_DATES: not applicable;
  known at 08:31 CT of d. A direction, not normalized.
- ``k6_wasdepre_drift`` (ZC, ZS): close(10:29) - open(08:30) on WASDE dates in
  GRAIN_FULL_SESSIONS, vehicle ticks; both bars one instrument_id; known at 10:30 CT.
K6-wasdepost-01 is excluded (signals.__init__.EXCLUDED): its move is known at 11:15 CT, after the
last grain decision time (11:00 CT).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    SignalContext,
    SignalSpec,
    as_date,
    bars_of,
    ct_ns,
    day_set,
    in_days,
    minute_of,
    path_of,
    per_unit,
    rows_of,
    same_iid,
)
from ml_route_v2.signals._daily import session_minutes
from ml_route_v2.signals._events import event_rows, nothing, per_vehicle, vehicle_rows


def _literals() -> tuple[int, int, int, int]:
    from strategy.members.k6.crushgap import CLOSE_BEFORE_C_MIN
    from strategy.members.k6.wasdepre import DRIFT_START_BAR, ENTRY_BAR

    o, c = session_minutes("ZS")  # D6 O 08:30 and C 13:15 (frozen table)
    return o, c - CLOSE_BEFORE_C_MIN, minute_of(DRIFT_START_BAR), minute_of(ENTRY_BAR)


# the 08:30 bar of d (crushgap opens, limitcont's c); the 13:14 bars of d - 1; wasdepre's bars
DAY_OPEN_MIN, GRAIN_CLOSE_BAR_MIN, WASDE_DRIFT_START_MIN, WASDE_DRIFT_END_MIN = _literals()
TICK_TOLERANCE = 1e-6  # exact tick compares of float settlements (limitcont.moved_exactly)


def _prev_in(table: np.ndarray, days: np.ndarray, k: int = 1) -> np.ndarray:
    """The k-th entry of a sorted day table strictly before each day, -1 when none."""
    pos = np.searchsorted(table, days, side="left") - k
    return np.where(pos >= 0, table[np.clip(pos, 0, None)], -1)


def _crushgap(ctx: SignalContext) -> pd.DataFrame:
    from rules.products import product
    from strategy.members.k6._calendar import GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES
    from strategy.members.k6.crushgap import GPM_WEIGHTS

    view, rows = vehicle_rows(ctx, ("ZS",))
    if not len(rows):
        return nothing(view)
    days = np.unique(view.day[rows])
    days = days[in_days(days, day_set(GRAIN_FULL_SESSIONS))]
    prev = _prev_in(day_set(GRAIN_TRADE_DATES), days)
    gpm_open = np.zeros(len(days))
    gpm_close = np.zeros(len(days))
    ok = prev >= 0
    open_ns = ct_ns(days, DAY_OPEN_MIN)
    close_ns = ct_ns(np.where(ok, prev, days), GRAIN_CLOSE_BAR_MIN)
    for leg, weight in GPM_WEIGHTS.items():
        b = bars_of(ctx, leg)
        factor = float(product(leg).vendor_price_factor)
        i_o, i_c = b.at(open_ns), b.at(close_ns)
        ok &= same_iid(b, i_o, i_c) & b.on_day(i_o, days) & b.on_day(i_c, np.where(ok, prev, -9))
        gpm_open += float(weight) * np.where(i_o >= 0, b.open[np.clip(i_o, 0, None)], 0) / factor
        gpm_close += float(weight) * np.where(i_c >= 0, b.close[np.clip(i_c, 0, None)], 0) / factor
    val = np.where(ok, gpm_open - gpm_close, np.nan)
    return event_rows(view, rows, days, val, open_ns + NS_MIN)


def _proxies(ctx: SignalContext, root: str, xdays: np.ndarray
             ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(S, min iid, max iid) of the D9.7 proxy of each trade date (NaN when undefined)."""
    from strategy.members.k6.limitcont import settlement_window

    b = bars_of(ctx, root)
    lo_ns = np.empty(len(xdays), dtype=np.int64)
    end_ns = np.empty(len(xdays), dtype=np.int64)
    for i, x in enumerate(xdays):
        start, end = settlement_window(as_date(int(x)))
        lo_ns[i] = ct_ns(np.array([x]), start.hour * 60 + start.minute)[0]
        end_ns[i] = ct_ns(np.array([x]), end.hour * 60 + end.minute)[0] + \
            (end.second * 1_000_000_000)
    key = ("proxy_cum", root)
    if key not in ctx.cache:
        pos = b.volume > 0
        ctx.cache[key] = (np.concatenate([[0.0], np.cumsum(np.where(pos, b.close * b.volume, 0))]),
                          np.concatenate([[0.0], np.cumsum(np.where(pos, b.volume, 0))]))
    cvw, cv = ctx.cache[key]
    dp = b.day_pos(xdays)
    first = np.where(dp >= 0, b.first[np.clip(dp, 0, None)], 0)
    last = np.where(dp >= 0, b.last[np.clip(dp, 0, None)], -1)
    lo = np.maximum(np.searchsorted(b.ts, lo_ns, side="left"), first)
    hi = np.minimum(np.searchsorted(b.ts, end_ns, side="left"), last + 1)
    has = (dp >= 0) & (hi > lo)
    vol = np.where(has, cv[np.where(has, hi, 0)] - cv[np.where(has, lo, 0)], 0.0)
    s = np.full(len(xdays), np.nan)
    imin = np.full(len(xdays), -1, dtype=np.int64)
    imax = np.full(len(xdays), -2, dtype=np.int64)
    w = has & (vol > 0)
    s[w] = (cvw[hi[w]] - cvw[lo[w]]) / vol[w]
    for i in np.flatnonzero(w):
        sel = b.volume[lo[i]:hi[i]] > 0
        ids = b.iid[lo[i]:hi[i]][sel]
        imin[i], imax[i] = ids.min(), ids.max()
    fb = (dp >= 0) & ~w & (hi - 1 >= first) & (hi - 1 <= last)
    j = hi - 1
    s[fb] = b.close[j[fb]]
    imin[fb] = b.iid[j[fb]]
    imax[fb] = b.iid[j[fb]]
    return s, imin, imax


def _limitcont_one(ctx: SignalContext, root: str, view, rows: np.ndarray  # noqa: ANN001
                   ) -> pd.DataFrame:
    from rules.products import product
    from strategy.members.k6._calendar import LIVESTOCK_FULL_SESSIONS, LIVESTOCK_TRADE_DATES
    from strategy.members.k6._limits import DROPPED_LIMIT_DATES
    from strategy.members.k6.limitcont import limit_ticks

    days = np.unique(view.day[rows])
    days = days[in_days(days, day_set(LIVESTOCK_FULL_SESSIONS))]
    table = day_set(LIVESTOCK_TRADE_DATES)
    d1, d2, d3 = (_prev_in(table, days, k) for k in (1, 2, 3))
    b = bars_of(ctx, root)
    o_ns = ct_ns(days, DAY_OPEN_MIN)
    o_idx = b.at(o_ns)
    o_idx = np.where(b.on_day(o_idx, days), o_idx, -1)
    xs = np.unique(np.concatenate([d1, d2, d3]))
    xs = xs[xs >= 0]
    s, imin, imax = _proxies(ctx, root, xs)
    tick = float(product(root).vendor_tick)
    dropped = day_set(DROPPED_LIMIT_DATES.get(root, {}))
    lim = {int(x): limit_ticks(root, as_date(int(x))) for x in xs}
    val = np.full(len(days), np.nan)
    on = np.zeros(len(days), dtype=bool)
    for i in range(len(days)):
        if min(d1[i], d2[i], d3[i]) < 0 or d1[i] in dropped or d2[i] in dropped:
            continue
        l1, l2 = lim.get(int(d1[i])), lim.get(int(d2[i]))
        if l1 is None or l2 is None:
            continue
        if o_idx[i] < 0:
            on[i] = True  # an event cannot be told without d's 08:30 bar: missing
            continue
        c = b.iid[o_idx[i]]
        p = np.searchsorted(xs, [d1[i], d2[i], d3[i]])
        if not (np.all(np.isfinite(s[p])) and np.all(imin[p] == c) and np.all(imax[p] == c)):
            on[i] = True  # S undefined or another contract: missing
            continue
        m1 = (s[p[0]] - s[p[1]]) / tick
        m2 = (s[p[1]] - s[p[2]]) / tick
        prior_limit = abs(abs(m2) - l2) < TICK_TOLERANCE
        if prior_limit:
            continue
        if abs(m1 - l1) < TICK_TOLERANCE:
            val[i], on[i] = 1.0, True
        elif abs(m1 + l1) < TICK_TOLERANCE:
            val[i], on[i] = -1.0, True
    keep = on
    return event_rows(view, rows, days[keep], val[keep], (o_ns + NS_MIN)[keep])


def _limitcont(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    return per_vehicle(ctx, ("HE", "LE"), lambda r, rows: _limitcont_one(ctx, r, view, rows))


def _wasdepre(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k6._calendar import GRAIN_FULL_SESSIONS
    from strategy.members.k6._wasde import WASDE_DATES

    ev = day_set(WASDE_DATES)
    ev = ev[in_days(ev, day_set(GRAIN_FULL_SESSIONS))]
    view = rows_of(ctx)
    start_ns = ct_ns(ev, WASDE_DRIFT_START_MIN)
    end_ns = ct_ns(ev, WASDE_DRIFT_END_MIN)

    def one(v: str, rows: np.ndarray) -> pd.DataFrame:
        b = bars_of(ctx, path_of(v))
        i0, i1 = b.at(start_ns), b.at(end_ns)
        ok = same_iid(b, i0, i1)
        val = np.full(len(ev), np.nan)
        val[ok] = (b.close[i1[ok]] - b.open[i0[ok]]) * per_unit(v)
        return event_rows(view, rows, ev, val, end_ns + NS_MIN)

    return per_vehicle(ctx, ("ZC", "ZS"), one)


SPECS = (
    SignalSpec("k6_crushgap_gap", "K6-crushgap-01", "K6", "member",
               "strategy/members/k6/crushgap.py:65-92, 155-175 (_side)", ("ZS", "ZM", "ZL"),
               True, _crushgap),
    SignalSpec("k6_limitcont_dir", "K6-limitcont-01", "K6", "member",
               "strategy/members/k6/limitcont.py:1-30, 73-145", ("HE", "LE"), False, _limitcont,
               own_path_only=True),
    SignalSpec("k6_wasdepre_drift", "K6-wasdepre-01", "K6", "member",
               "strategy/members/k6/wasdepre.py:45-50", ("ZC", "ZS"), True, _wasdepre,
               own_path_only=True),
)

__all__ = ["SPECS"]
