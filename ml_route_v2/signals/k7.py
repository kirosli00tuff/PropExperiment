"""V2.3 member signals of K7's members (MBT rows on MBT bars).

Sources: strategy/members/k7/expiry.py (fixed clock), montrend.py, rev2h.py; dates
k7/_event_common.ENTRY_DATES (CRYPTO_FULL_SESSIONS not VENDOR_DEGRADED) and k7/_calendar.MBTX.
- ``k7_expiry_*``: the MBTX expiry instant T_exp (expiry.event_schedule's exit bar + 2 min).
- ``k7_montrend_ret`` (Monday trade dates, montrend.is_trade_day): close(t - 1) - open(t - 60) at
  the latest member clock (montrend.day_schedule: Sunday 18:00 .. Monday 13:00, hourly) known by t,
  vehicle ticks; both bars of the trade date with one instrument_id (reading SC-3: the member's
  sign s_t enters as the signed move).
- ``k7_rev2h_ret`` (ENTRY_DATES): the latest of r1 = close(10:29) - open(08:30) (known 10:30) and
  r2 = close(12:29) - open(10:30) (known 12:30) known by t (rev2h.day_schedule, anchor O = 08:30).
"""

from __future__ import annotations

from functools import partial

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    SignalContext,
    SignalSpec,
    as_date,
    bars_of,
    epoch_day,
    per_unit,
    same_iid,
)
from ml_route_v2.signals._daily import session_minutes
from ml_route_v2.signals._events import (
    cached_pair,
    fixed_clock,
    nothing,
    slot_rows,
    vehicle_rows,
)

MBT = "MBT"
def _exit_bar_before_t() -> int:
    from strategy.members.k7._event_common import FILL_DELAY_MIN
    from strategy.members.k7.expiry import EXIT_FILL_BEFORE_T_MIN

    return EXIT_FILL_BEFORE_T_MIN + FILL_DELAY_MIN


EXIT_BAR_BEFORE_T_MIN = _exit_bar_before_t()  # expiry.py: the exit bar is T_exp - 2


def _expiry(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k7.expiry import event_schedule

    plans = event_schedule()
    days = np.array([epoch_day(d) for d in plans], dtype=np.int64)
    inst = np.array([x + EXIT_BAR_BEFORE_T_MIN * NS_MIN for _e, x in plans.values()],
                    dtype=np.int64)
    view, rows = vehicle_rows(ctx, (MBT,))
    return fixed_clock(view, rows, days, inst)


def _expiry_side(side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k7_expiry", _expiry)[side]


def _schedule_rows(ctx: SignalContext, member: str) -> pd.DataFrame:
    from strategy.members.k7 import montrend, rev2h
    from strategy.members.k7._event_common import is_entry_date

    view, rows = vehicle_rows(ctx, (MBT,))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, MBT)
    days = view.day[rows]
    udays = np.unique(days)
    o_min, _c = session_minutes(MBT)
    sched, on_days = [], []
    for d in udays:
        day = as_date(int(d))
        if member == "montrend":
            ok = montrend.is_trade_day(day)
            dec = montrend.day_schedule(day).decisions if ok else ()
        else:
            ok = is_entry_date(day)
            dec = rev2h.day_schedule(day, o_min).decisions if ok else ()
        on_days.append(ok)
        sched.append(dec)
    n_slots = max((len(s) for s in sched), default=0)
    start = np.zeros((len(udays), max(n_slots, 1)), dtype=np.int64)
    end = np.zeros_like(start)
    for i, dec in enumerate(sched):
        for s, x in enumerate(dec):
            start[i, s], end[i, s] = x.start_ns, x.end_ns
    pos = np.searchsorted(udays, days)
    st, en = start[pos], end[pos]
    i0 = b.at(st.ravel()).reshape(st.shape)
    i1 = b.at(en.ravel()).reshape(en.shape)
    dd = np.repeat(days[:, None], st.shape[1], axis=1)
    ok = same_iid(b, i0.ravel(), i1.ravel()).reshape(st.shape)
    ok &= b.on_day(i0.ravel(), dd.ravel()).reshape(st.shape) & (st > 0)
    val = np.where(ok, (b.close[np.clip(i1, 0, None)] - b.open[np.clip(i0, 0, None)])
                   * per_unit(MBT), np.nan)
    slot_avail = np.where(st > 0, en + NS_MIN, 0)
    return slot_rows(view, rows, slot_avail, val, np.array(on_days, dtype=bool)[pos])


SPECS = (
    SignalSpec("k7_expiry_mto", "K7-expiry-01", "K7", "member",
               "strategy/members/k7/expiry.py:52-71 (event_schedule)", (), True,
               partial(_expiry_side, 0)),
    SignalSpec("k7_expiry_msince", "K7-expiry-01", "K7", "member",
               "strategy/members/k7/expiry.py:52-71 (event_schedule)", (), True,
               partial(_expiry_side, 1)),
    SignalSpec("k7_montrend_ret", "K7-montrend-01", "K7", "member",
               "strategy/members/k7/montrend.py:57-90 (day_schedule, is_trade_day)", (MBT,), True,
               partial(_schedule_rows, member="montrend")),
    SignalSpec("k7_rev2h_ret", "K7-rev2h-01", "K7", "member",
               "strategy/members/k7/rev2h.py:54-75 (day_schedule)", (MBT,), True,
               partial(_schedule_rows, member="rev2h")),
)

__all__ = ["SPECS"]
