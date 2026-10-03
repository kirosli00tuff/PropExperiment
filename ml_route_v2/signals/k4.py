"""V2.3 member signals of K4's members (MCL rows on CL bars, NG rows on NG bars).

Sources: strategy/members/k4/apipre.py, eiafade.py, eiamom.py, ngpre.py (fixed clock), ovr.py;
tables strategy/members/k4/_releases.py (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL,
API_DROPPED_WEEKS) and k4/_calendar.py (ENERGY_FULL_SESSIONS), read through the members' own
functions (event_wednesdays, release_minutes, event_dates, schedule, reference_dates).
- ``k4_apipre_ret`` (MCL): close(15:39) - close(15:24) on W - 1 for the members' Wednesdays W,
  vehicle ticks; the two bars and W's 07:29 bar share one instrument_id; known at 07:30 of W.
- ``k4_eiafade_move`` (MCL): M = (close(T_W + 14) - close(T_W - 1)) / close(T_W - 1) on the
  release_minutes rows; both bars one instrument_id; known at T_W + 15.
- ``k4_eiamom_r3`` (MCL): close(09:59) - close(09:29) on eiamom.event_dates; the two bars share one
  instrument_id (the member's guard also names the 14:29 entry bar; reading SC-6); known at 10:00.
- ``k4_ngpre_*`` (NG): the NGS release instant T (ngpre.schedule entry + 91 min).
- ``k4_ovr_ret`` and ``k4_ovr_pct`` (MCL, NG): r(tau) = (close(tau - 1) - open(tau - 60)) /
  open(tau - 60) at the latest member clock tau in {09:00, ..., 13:00} known by t, both bars with
  one instrument_id and open > 0; pct = the position of r(tau) among the reference values r at the
  five clocks on ovr.reference_dates(d) (fraction below plus half the ties); fewer than MIN_VALUES
  reference values: missing (reading SC-7: the member's P10/P90 cut enters as the position).
"""

from __future__ import annotations

import importlib
from datetime import time
from functools import partial

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    SignalContext,
    SignalSpec,
    as_date,
    bars_of,
    ct_ns,
    epoch_day,
    minute_of,
    path_of,
    per_unit,
    same_iid,
)
from ml_route_v2.signals._daily import session_minutes
from ml_route_v2.signals._events import (
    cached_pair,
    combine,
    event_rows,
    fixed_clock,
    nothing,
    slot_rows,
    vehicle_rows,
)

MCL, NG = "MCL", "NG"


def _days_sorted(dates) -> np.ndarray:  # noqa: ANN001 - iterable of date
    return np.array(sorted(epoch_day(d) for d in dates), dtype=np.int64)


def _apipre(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k4 import apipre

    m = apipre.make_mcl()
    w = _days_sorted(apipre.event_wednesdays(m.wpsr, m.full_sessions, m.monday_holidays,
                                             m.api_dropped))
    view, rows = vehicle_rows(ctx, (MCL,))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, path_of(MCL))
    i0 = b.at(ct_ns(w, minute_of(apipre.SIGNAL_START_CT), day_offset=-1))
    i1 = b.at(ct_ns(w, minute_of(apipre.SIGNAL_END_CT), day_offset=-1))
    entry_ns = ct_ns(w, minute_of(apipre.ENTRY_DECISION_CT))
    ok = same_iid(b, i0, i1, b.at(entry_ns))
    val = np.full(len(w), np.nan)
    val[ok] = (b.close[i1[ok]] - b.close[i0[ok]]) * per_unit(MCL)
    return event_rows(view, rows, w, val, entry_ns + NS_MIN)


def _eiafade(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k4 import eiafade

    rel = eiafade.release_minutes(eiafade.make_mcl().wpsr)
    days = np.array([epoch_day(d) for d in sorted(rel)], dtype=np.int64)
    t_w = np.array([rel[d] for d in sorted(rel)], dtype=np.int64)
    view, rows = vehicle_rows(ctx, (MCL,))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, path_of(MCL))
    i0 = b.at(ct_ns(days, t_w + eiafade.BASE_OFFSET_MIN))
    end_ns = ct_ns(days, t_w + eiafade.ENTRY_DECISION_OFFSET_MIN)
    i1 = b.at(end_ns)
    ok = same_iid(b, i0, i1)
    ok[ok] &= b.close[i0[ok]] > 0
    val = np.full(len(days), np.nan)
    val[ok] = (b.close[i1[ok]] - b.close[i0[ok]]) / b.close[i0[ok]]
    return event_rows(view, rows, days, val, end_ns + NS_MIN)


def _eiamom(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k4 import eiamom

    m = eiamom.make_mcl()
    days = _days_sorted(eiamom.event_dates(m.wpsr, m.nyse_not_full))
    view, rows = vehicle_rows(ctx, (MCL,))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, path_of(MCL))
    i0 = b.at(ct_ns(days, minute_of(eiamom.SIGNAL_START_CT)))
    end_ns = ct_ns(days, minute_of(eiamom.SIGNAL_END_CT))
    i1 = b.at(end_ns)
    ok = same_iid(b, i0, i1)
    val = np.full(len(days), np.nan)
    val[ok] = (b.close[i1[ok]] - b.close[i0[ok]]) * per_unit(MCL)
    return event_rows(view, rows, days, val, end_ns + NS_MIN)


def _ngpre(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k4 import ngpre

    plans = ngpre.schedule(ngpre.make_ng().ngs)
    days = np.array([epoch_day(d) for d in plans], dtype=np.int64)
    t_rel = np.array([e - ngpre.ENTRY_DECISION_OFFSET_MIN for e, _x in plans.values()],
                     dtype=np.int64)
    view, rows = vehicle_rows(ctx, (NG,))
    return fixed_clock(view, rows, days, ct_ns(days, t_rel))


def ovr_values(ctx: SignalContext, vehicle: str, slots: tuple[int, ...], days: np.ndarray,
               signal_minutes: int, bar_before: int) -> tuple[np.ndarray, np.ndarray]:
    """(r, availability) arrays of shape (len(days), len(slots)): r = (close(tau - 1) -
    open(tau - 60)) / open(tau - 60), both bars present with one instrument_id and open > 0."""
    b = bars_of(ctx, path_of(vehicle))
    r = np.full((len(days), len(slots)), np.nan)
    av = np.zeros((len(days), len(slots)), dtype=np.int64)
    for s, tau in enumerate(slots):
        i0 = b.at(ct_ns(days, tau - signal_minutes))
        end_ns = ct_ns(days, tau - bar_before)
        i1 = b.at(end_ns)
        ok = same_iid(b, i0, i1) & b.on_day(i0, days)
        ok[ok] &= b.open[i0[ok]] > 0
        r[ok, s] = (b.close[i1[ok]] - b.open[i0[ok]]) / b.open[i0[ok]]
        av[:, s] = end_ns + NS_MIN
    return r, av


def position_of(r: np.ndarray, ref: np.ndarray, min_values: int) -> np.ndarray:
    """Per row: (count(ref < r) + count(ref == r) / 2) / n over the finite reference values; NaN
    when fewer than ``min_values`` of them."""
    finite = np.isfinite(ref)
    n = finite.sum(axis=1)
    below = (finite & (ref < r[:, None])).sum(axis=1)
    ties = (finite & (ref == r[:, None])).sum(axis=1)
    out = np.where(n >= min_values, (below + 0.5 * ties) / np.maximum(n, 1), np.nan)
    return np.where(np.isfinite(r), out, np.nan)


def ovr_frames(ctx: SignalContext, vehicles: tuple[str, ...], module: str
               ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(ret, pct) frames of K4-ovr-01 or K5-ovr-01 (``module`` "k4" or "k5")."""
    mod = importlib.import_module(f"strategy.members.{module}.ovr")
    view, _ = vehicle_rows(ctx, vehicles)
    rets, pcts = [], []
    for v in vehicles:
        rows = view.where_root((v,))
        if not len(rows):
            continue
        if module == "k4":
            slots = tuple(minute_of(x) for x in mod.DECISION_TIMES_CT)
            min_values = mod.MIN_VALUES
        else:
            o, c = session_minutes(v)
            times = mod.decision_times(time(o // 60, o % 60), time(c // 60, c % 60))
            slots = tuple(minute_of(x) for x in times)
            min_values = mod.min_values(len(slots))
        udays = np.unique(view.day[rows])
        refs = [tuple(epoch_day(d) for d in mod.reference_dates(as_date(int(d))))
                for d in udays]
        all_days = np.unique(np.concatenate([udays, *[np.array(x, np.int64) for x in refs]])
                             ) if len(udays) else udays
        r_all, av_all = ovr_values(ctx, v, slots, all_days, mod.SIGNAL_MINUTES,
                                   mod.DECISION_BAR_BEFORE_T_MIN)
        pos_row = np.searchsorted(all_days, view.day[rows])
        r_rows, av_rows = r_all[pos_row], av_all[pos_row]
        n_ref = mod.REFERENCE_DATES
        ref_idx = np.full((len(udays), n_ref), -1, dtype=np.int64)
        for i, x in enumerate(refs):
            if x:
                ref_idx[i, n_ref - len(x):] = np.searchsorted(all_days, np.array(x, np.int64))
        ref_vals = np.where(ref_idx[:, :, None] >= 0, r_all[np.clip(ref_idx, 0, None)], np.nan)
        ref_vals = ref_vals.reshape(len(udays), -1)
        ref_rows = ref_vals[np.searchsorted(udays, view.day[rows])]
        pct_rows = np.column_stack([position_of(r_rows[:, s], ref_rows, min_values)
                                    for s in range(len(slots))])
        on = np.ones(len(rows), dtype=bool)
        rets.append(slot_rows(view, rows, av_rows, r_rows, on))
        pcts.append(slot_rows(view, rows, av_rows, pct_rows, on))
    if not rets:
        return nothing(view), nothing(view)
    return combine(rets), combine(pcts)


def _ovr_side(side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k4_ovr", lambda c: ovr_frames(c, (MCL, NG), "k4"))[side]


def _ngpre_side(side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k4_ngpre", _ngpre)[side]


SPECS = (
    SignalSpec("k4_apipre_ret", "K4-apipre-01", "K4", "member",
               "strategy/members/k4/apipre.py:51-74 (event_wednesdays)", ("CL",), True, _apipre),
    SignalSpec("k4_eiafade_move", "K4-eiafade-01", "K4", "member",
               "strategy/members/k4/eiafade.py:48-63 (release_minutes)", ("CL",), True,
               _eiafade),
    SignalSpec("k4_eiamom_r3", "K4-eiamom-01", "K4", "member",
               "strategy/members/k4/eiamom.py:47-64 (event_dates)", ("CL",), True, _eiamom),
    SignalSpec("k4_ngpre_mto", "K4-ngpre-01", "K4", "member",
               "strategy/members/k4/ngpre.py:42-57 (schedule)", (), True, partial(_ngpre_side, 0)),
    SignalSpec("k4_ngpre_msince", "K4-ngpre-01", "K4", "member",
               "strategy/members/k4/ngpre.py:42-57 (schedule)", (), True, partial(_ngpre_side, 1)),
    SignalSpec("k4_ovr_ret", "K4-ovr-01", "K4", "member",
               "strategy/members/k4/ovr.py:60-90", ("CL", "NG"), True, partial(_ovr_side, 0),
               own_path_only=True),
    SignalSpec("k4_ovr_pct", "K4-ovr-01", "K4", "member",
               "strategy/members/k4/ovr.py:60-110 (reference_dates, percentile_side)",
               ("CL", "NG"), True, partial(_ovr_side, 1), own_path_only=True),
)

__all__ = ["SPECS", "ovr_frames", "position_of"]
