"""V2.3 member signals of K1's own members: K1-vwap-01 and K1-vxnband-01 (MNQ rows, NQ bars).

Sources: strategy/members/k1/vwap.py (docstring rule, K1-L-06) and strategy/members/k1/vxnband.py
(K1-L-01..K1-L-05); dates: EQUITY_FULL_SESSIONS (k1/_event_common.FULL_SESSIONS).
- ``k1_vwap_dist``: close of the latest bar closed by t minus the session VWAP, where VWAP =
  sum((H + L + C) x vol) / (3 sum(vol)) over the present bars of CT date d opening from 08:30
  through that bar, vehicle ticks (reading SC-3: the member's sign s_t = sign(3 C sum(vol) -
  sum((H + L + C) vol)) enters as the signed distance). sum(vol) = 0: missing.
- ``k1_vxn_regime``: V = VXN close of the EQUITY_TRADE_DATES entry before d (vxnband.vxn_for),
  read at the close of d's 08:30 bar (08:31 CT). No VXN row (the prior equity trade date was an
  NYSE holiday): the member does not trade d, so not applicable (reading SC-8), for both K1-vxnband
  signals.
- ``k1_vxn_band``: x = 1600 (close - C_prev) / (C_prev V) at the latest bar of CT date d opening
  in [08:30, 14:29) closed by t; C_prev = the 14:59 close of the most recent port-complete date
  before d whose instrument_id equals d's 08:30 bar's (else missing). The member sells at x > 1,
  buys at x < -1; the regime filter V < 20 or V >= 30 is the member's trade rule, not the variable.
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
    empty,
    in_days,
    minute_of,
    per_unit,
    result,
    rows_of,
    window_sums,
)
from ml_route_v2.signals._daily import daily_of, session_minutes

VEHICLE = "MNQ"
PATH = "NQ"
SESSION_OPEN_MIN = session_minutes(VEHICLE)[0]  # D6 O of MNQ (08:30), the frozen table


def _scan_end() -> int:
    from strategy.members.k1.vxnband import SCAN_END_CT

    return minute_of(SCAN_END_CT)


SCAN_END_MIN = _scan_end()  # entry-intent bars open in [08:30, 14:29)


def _full_sessions() -> np.ndarray:
    from strategy.members.k1._calendar import EQUITY_FULL_SESSIONS

    return day_set(EQUITY_FULL_SESSIONS)


def _rows(ctx: SignalContext, need_bars: bool = True) -> tuple:  # noqa: ANN202
    """(view, rows of MNQ on full sessions, NQ bars or None)."""
    view = rows_of(ctx)
    rows = view.where_root((VEHICLE,))
    rows = rows[in_days(view.day[rows], _full_sessions())]
    return view, rows, (bars_of(ctx, PATH) if len(rows) and need_bars else None)


def _vwap(ctx: SignalContext) -> pd.DataFrame:
    view, rows, b = _rows(ctx)
    value, app, avail = empty(view)
    if len(rows):
        days, t = view.day[rows], view.t[rows]
        start = ct_ns(days, SESSION_OPEN_MIN)
        lo = np.searchsorted(b.ts, start, side="left")
        hi = np.searchsorted(b.ts, t - NS_MIN, side="right")  # bars closed by t
        last = hi - 1
        ok = (hi > lo) & b.on_day(np.where(hi > lo, last, -1), days)
        lo_ok, hi_ok = np.where(ok, lo, 0), np.where(ok, hi, 0)
        vol = window_sums(b.volume, lo_ok, hi_ok)

        def typical(idx: np.ndarray) -> np.ndarray:
            return (b.high[idx] + b.low[idx] + b.close[idx]) * b.volume[idx]

        ok &= vol > 0
        vwap = np.where(ok, window_sums(typical, lo_ok, hi_ok) / (3.0 * np.where(ok, vol, 1)),
                        np.nan)
        known = start + NS_MIN <= t
        val = np.where(ok, (b.close[np.clip(last, 0, None)] - vwap) * per_unit(VEHICLE), np.nan)
        sel = rows[known]
        value[sel] = val[known]
        avail[sel] = np.where(ok[known], b.ts[np.clip(last[known], 0, None)] + NS_MIN, -1)
        app[sel] = True
    return result(view, value, app, avail)


def _vxn(days: np.ndarray) -> np.ndarray:
    from strategy.members.k1.vxnband import vxn_for

    out = np.full(len(days), np.nan)
    for d in np.unique(days):
        v = vxn_for(as_date(int(d)))
        if v is not None:
            out[days == d] = float(v)
    return out


def _regime(ctx: SignalContext) -> pd.DataFrame:
    view, rows, _b = _rows(ctx, need_bars=False)
    value, app, avail = empty(view)
    if len(rows):
        days, t = view.day[rows], view.t[rows]
        known_at = ct_ns(days, SESSION_OPEN_MIN) + NS_MIN
        known = (known_at <= t) & np.isfinite(_vxn(days))
        sel = rows[known]
        value[sel] = _vxn(days)[known]
        avail[sel] = known_at[known]
        app[sel] = True
    return result(view, value, app, avail)


def _band(ctx: SignalContext) -> pd.DataFrame:
    view, rows, b = _rows(ctx)
    value, app, avail = empty(view)
    if len(rows):
        dl = daily_of(ctx, VEHICLE)
        days, t = view.day[rows], view.t[rows]
        o_ns = ct_ns(days, SESSION_OPEN_MIN)
        o_idx = b.at(o_ns)
        o_idx = np.where(b.on_day(o_idx, days), o_idx, -1)
        comp = np.flatnonzero(dl.port_complete)
        k = np.searchsorted(dl.days[comp], days, side="left") - 1
        prev = np.where(k >= 0, comp[np.clip(k, 0, None)], -1)
        c1 = np.where(prev >= 0, dl.c1_idx[np.clip(prev, 0, None)], -1)
        ok = (o_idx >= 0) & (c1 >= 0)
        ok[ok] = b.iid[c1[ok]] == b.iid[o_idx[ok]]
        end = np.minimum(t, ct_ns(days, SCAN_END_MIN))
        j = np.searchsorted(b.ts, end - NS_MIN, side="right") - 1
        ok &= (j >= 0) & b.on_day(j, days)
        ok[ok] &= b.ts[j[ok]] >= o_ns[ok]
        v = _vxn(days)
        c_prev = np.where(ok, b.close[np.clip(c1, 0, None)], np.nan)
        x = 1600.0 * (b.close[np.clip(j, 0, None)] - c_prev) / (c_prev * v)
        known = (o_ns + NS_MIN <= t) & np.isfinite(v)
        sel = rows[known]
        value[sel] = np.where(ok, x, np.nan)[known]
        avail[sel] = np.where(ok, b.ts[np.clip(j, 0, None)] + NS_MIN, -1)[known]
        app[sel] = True
    return result(view, value, app, avail)


SPECS = (
    SignalSpec("k1_vwap_dist", "K1-vwap-01", "K1", "member",
               "strategy/members/k1/vwap.py:1-34 (K1-L-06)", (PATH,), True, _vwap),
    SignalSpec("k1_vxn_regime", "K1-vxnband-01", "K1", "member",
               "strategy/members/k1/vxnband.py:79 (vxn_for), K1-L-01", (), True, _regime),
    SignalSpec("k1_vxn_band", "K1-vxnband-01", "K1", "member",
               "strategy/members/k1/vxnband.py:90 (breach_side), K1-L-04", (PATH,), True, _band),
)

__all__ = ["SPECS"]
