"""V2.3 member signals of K8's cross-product members.

Sources: strategy/members/k8/flight.py, oilcad.py, wkndbtc.py; tables k8/_calendar.py
(FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES, previous_dates).
- ``k8_flight_ret`` (MGC rows, MES bars): r_k = (c1 - c6) / c6 of the MES closes at t_k - 1 and
  t_k - 6 for the latest block t_k in {08:35, ..., 14:55} known by t; both bars of the trade date
  with one instrument_id, c6 > 0; d in FLIGHT_DATES. ``k8_flight_tail``: r_k / |Q(d)|, Q(d) = the
  m-th smallest defined r_k over flight.reference_dates(d), m = ceil(n / 200), n >= 1,200 else
  missing (reading SC-7: the member's trigger r_k <= Q(d) enters as the ratio; -1 is the trigger).
- ``k8_oilcad_ret`` (6C rows, CL bars as MCL's price path): r_t = (c1 - c6) / c6 at the latest
  t in {08:05, ..., 13:25} known by t; ``k8_oilcad_z``: r_t / s(d), s(d) = the sample sd of every
  defined r over the 20 OILCAD_DATES before d (n >= 1,000, s > 0, else missing); d in OILCAD_DATES.
- ``k8_wkndbtc_move`` (MNQ rows, MBT bars): close(MBT 17:59 Sunday d - 1) - close(MBT 14:59
  Friday d - 3) in MBT ticks on wkndbtc.is_trade_monday dates; both bars one instrument_id; known
  at 18:00 CT Sunday.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    BarArrays,
    SignalContext,
    SignalSpec,
    as_date,
    bars_of,
    ct_ns,
    day_set,
    epoch_day,
    in_days,
    minute_of,
    own_per_unit,
    same_iid,
)
from ml_route_v2.signals._events import (
    cached_pair,
    event_rows,
    nothing,
    slot_rows,
    vehicle_rows,
)

FIVE_MIN_BLOCK_BEFORE = (1, 6)  # c1 at t - 1, c6 at t - 6 (flight.py, oilcad.py)


def _block_returns(b: BarArrays, days: np.ndarray, slots: tuple[int, ...]
                   ) -> tuple[np.ndarray, np.ndarray]:
    """(r, availability) of shape (len(days), len(slots)): (c1 - c6) / c6."""
    r = np.full((len(days), len(slots)), np.nan)
    av = np.zeros((len(days), len(slots)), dtype=np.int64)
    end_before, start_before = FIVE_MIN_BLOCK_BEFORE
    for s, tau in enumerate(slots):
        e_ns = ct_ns(days, tau - end_before)
        i1, i6 = b.at(e_ns), b.at(ct_ns(days, tau - start_before))
        ok = same_iid(b, i1, i6) & b.on_day(i1, days) & b.on_day(i6, days)
        ok[ok] &= b.close[i6[ok]] > 0
        r[ok, s] = (b.close[i1[ok]] - b.close[i6[ok]]) / b.close[i6[ok]]
        av[:, s] = e_ns + NS_MIN
    return r, av


def _reference_stat(r_all: np.ndarray, all_days: np.ndarray, udays: np.ndarray,
                    refs: Callable[[int], tuple[int, ...]], stat: Callable[[np.ndarray], float]
                    ) -> np.ndarray:
    out = np.full(len(udays), np.nan)
    for i, d in enumerate(udays):
        ref = np.array(refs(int(d)), dtype=np.int64)
        pos = np.searchsorted(all_days, ref)
        ok = (pos < len(all_days))
        ok[ok] = all_days[pos[ok]] == ref[ok]
        vals = r_all[pos[ok]].ravel()
        out[i] = stat(vals[np.isfinite(vals)])
    return out


def _cross(ctx: SignalContext, member: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k8 import flight, oilcad
    from strategy.members.k8._calendar import FLIGHT_DATES, OILCAD_DATES, previous_dates

    if member == "flight":
        vehicle, signal_root, dates = "MGC", "MES", FLIGHT_DATES
        slots = tuple(minute_of(x) for x in flight.decision_times())
        n_ref, min_n = flight.REFERENCE_DATES, flight.MIN_VALUES

        def stat(v: np.ndarray) -> float:
            if len(v) < min_n:
                return np.nan
            m = (len(v) + flight.TAIL_DIVISOR - 1) // flight.TAIL_DIVISOR
            q = np.partition(v, m - 1)[m - 1]
            return abs(q) if q != 0 else np.nan
    else:
        vehicle, signal_root, dates = "6C", "CL", OILCAD_DATES
        slots = tuple(minute_of(x) for x in oilcad.DECISION_TIMES_CT)
        n_ref, min_n = oilcad.REFERENCE_DATES, oilcad.MIN_VALUES

        def stat(v: np.ndarray) -> float:
            if len(v) < min_n:
                return np.nan
            s = float(np.std(v, ddof=1))
            return s if s > 0 else np.nan
    sorted_dates = tuple(sorted(dates))

    def refs(d: int) -> tuple[int, ...]:
        return tuple(epoch_day(x) for x in previous_dates(sorted_dates, as_date(d), n_ref))

    view, rows = vehicle_rows(ctx, (vehicle,))
    if not len(rows):
        return nothing(view), nothing(view)
    b = bars_of(ctx, signal_root)
    udays = np.unique(view.day[rows])
    ref_days = [np.array(refs(int(d)), np.int64) for d in udays]
    all_days = np.unique(np.concatenate([udays, *ref_days])) if len(udays) else udays
    r_all, av_all = _block_returns(b, all_days, slots)
    scale = _reference_stat(r_all, all_days, udays, refs, stat)
    pos = np.searchsorted(all_days, view.day[rows])
    r_rows, av_rows = r_all[pos], av_all[pos]
    ratio = r_rows / scale[np.searchsorted(udays, view.day[rows])][:, None]
    on = in_days(view.day[rows], day_set(dates))
    return (slot_rows(view, rows, av_rows, r_rows, on),
            slot_rows(view, rows, av_rows, ratio, on))


def _cross_side(member: str, side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k8_" + member, partial(_cross, member=member))[side]


def _wkndbtc(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k8 import wkndbtc

    view, rows = vehicle_rows(ctx, ("MNQ",))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, "MBT")
    days = np.unique(view.day[rows])
    days = days[[wkndbtc.is_trade_monday(as_date(int(d))) for d in days]] if len(days) else days
    s_ns = ct_ns(days, minute_of(wkndbtc.SUNDAY_BAR_CT), day_offset=wkndbtc.SUNDAY_OFFSET_DAYS)
    f_ns = ct_ns(days, minute_of(wkndbtc.FRIDAY_BAR_CT), day_offset=wkndbtc.FRIDAY_OFFSET_DAYS)
    i_s, i_f = b.at(s_ns), b.at(f_ns)
    ok = same_iid(b, i_s, i_f) & b.on_day(i_s, days)
    ok &= b.on_day(i_f, days + wkndbtc.FRIDAY_OFFSET_DAYS)
    val = np.full(len(days), np.nan)
    val[ok] = (b.close[i_s[ok]] - b.close[i_f[ok]]) * own_per_unit("MBT")
    return event_rows(view, rows, days, val, s_ns + NS_MIN)


SPECS = (
    SignalSpec("k8_flight_ret", "K8-flight-01", "K8", "member",
               "strategy/members/k8/flight.py:68-140 (block_return)", ("MES",), True,
               partial(_cross_side, "flight", 0)),
    SignalSpec("k8_flight_tail", "K8-flight-01", "K8", "member",
               "strategy/members/k8/flight.py:68-140 (threshold, reference_dates)", ("MES",),
               True, partial(_cross_side, "flight", 1)),
    SignalSpec("k8_oilcad_ret", "K8-oilcad-01", "K8", "member",
               "strategy/members/k8/oilcad.py:54-120 (block_return)", ("CL",), True,
               partial(_cross_side, "oilcad", 0)),
    SignalSpec("k8_oilcad_z", "K8-oilcad-01", "K8", "member",
               "strategy/members/k8/oilcad.py:54-120 (scale, passes_threshold)", ("CL",), True,
               partial(_cross_side, "oilcad", 1)),
    SignalSpec("k8_wkndbtc_move", "K8-wkndbtc-01", "K8", "member",
               "strategy/members/k8/wkndbtc.py:50-95 (is_trade_monday)", ("MBT",), True,
               _wkndbtc),
)

__all__ = ["SPECS"]
