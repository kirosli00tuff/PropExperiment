"""V2.3 member signals of K3's fix members (FX rows).

Sources: strategy/members/k3/ldnmom.py, ldnrev.py, mehedge.py, ecbfix.py, tkypost.py, tkypre.py;
their schedule() functions are called with the members' own frozen tables (k3/_clocks.py T_L,
T_E, T_T; k3/_calendar.py), so the event dates and bar instants are the members' exactly.
- ``k3_ldnmom_trend`` (6E, 6J): S = close(T_L - 13) - open(T_L - 15), vehicle ticks; both bars
  with one instrument_id; known at T_L - 12.
- ``k3_ldnrev_move`` (6E, 6J, 6S, month ends): M = close(T_L - 1) - close(T_L - 11); the read bars
  share one instrument_id (reading SC-6: the member's guard also names the T_L + 4 entry bar, which
  is not closed by every t; the feature guards only the bars it reads); known at T_L.
- ``k3_mehedge_req`` (6J, ME(m) dates that are FX full sessions and not E&W bank holidays, with a
  signal row for the same ME): the Nikkei month log return R_eq from k3/_mehedge_signal.py; known
  from Nikkei closes strictly before ME's calendar date, availability set to 01:00 CT of ME - 1
  (an upper bound of the Tokyo close, 15:00 JST).
- Fixed clock: ``k3_ecbfix_mto`` / ``_msince`` (6E): T_E on its event dates;
  ``k3_tkypost_msince`` (6J): T_T on d - 1 for Tokyo business days; ``k3_tkypre_msince`` (6J): T_T
  on d - 1 for gotobi dates (T_T precedes every decision time of d: no minutes-to signal).
"""

from __future__ import annotations

from functools import partial

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    SignalContext,
    SignalSpec,
    bars_of,
    ct_ns,
    epoch_day,
    path_of,
    per_unit,
    same_iid,
)
from ml_route_v2.signals._events import (
    cached_pair,
    event_rows,
    fixed_clock,
    per_vehicle,
    vehicle_rows,
)

MEHEDGE_AVAIL_MIN = 60  # 01:00 CT of ME - 1


def _plans(member: str) -> dict:
    from strategy.members.k3 import ldnmom, ldnrev

    if member == "ldnmom":
        m = ldnmom.make_6e()
        return ldnmom.schedule(m.t_l, m.full_sessions, m.ew_holidays)
    m = ldnrev.make_6e()
    return ldnrev.schedule(m.month_ends, m.t_l, m.full_sessions, m.ew_holidays)


def _two_read(member: str, vehicles: tuple[str, ...], ctx: SignalContext) -> pd.DataFrame:
    """field(read 2) - field(read 1) of the member's two signal bars, per event date."""
    view, _ = vehicle_rows(ctx, vehicles)
    plans = _plans(member)
    days = np.array([epoch_day(d) for d in sorted(plans)], dtype=np.int64)
    reads = [plans[d].reads for d in sorted(plans)]
    if any(len(r) != 2 for r in reads):
        raise ValueError(f"K3 {member}: expected two signal bars per date")
    ns0 = np.array([r[0][0] for r in reads], dtype=np.int64)
    ns1 = np.array([r[1][0] for r in reads], dtype=np.int64)
    f0, f1 = reads[0][0][1], reads[0][1][1]

    def one(v: str, rows: np.ndarray) -> pd.DataFrame:
        b = bars_of(ctx, path_of(v))
        i0, i1 = b.at(ns0), b.at(ns1)
        ok = same_iid(b, i0, i1)
        a0 = b.open if f0 == "open" else b.close
        a1 = b.open if f1 == "open" else b.close
        val = np.full(len(days), np.nan)
        val[ok] = (a1[i1[ok]] - a0[i0[ok]]) * per_unit(v)
        return event_rows(view, rows, days, val, ns1 + NS_MIN)

    return per_vehicle(ctx, vehicles, one)


def _mehedge(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k3._calendar import EW_BANK_HOLIDAYS, FX_FULL_SESSIONS, MONTH_ENDS
    from strategy.members.k3._mehedge_signal import MEHEDGE_R_EQ_6J

    view, rows = vehicle_rows(ctx, ("6J",))
    full, bank = frozenset(FX_FULL_SESSIONS), frozenset(EW_BANK_HOLIDAYS)
    signal = {month: (me, r_eq) for month, me, r_eq in MEHEDGE_R_EQ_6J}
    recs = []
    for month, me in MONTH_ENDS:
        if me not in full or me in bank or month not in signal or signal[month][0] != me:
            continue
        r_eq = signal[month][1]
        recs.append((epoch_day(me), np.nan if r_eq is None else float(r_eq)))
    recs.sort()
    days = np.array([r[0] for r in recs], dtype=np.int64)
    val = np.array([r[1] for r in recs], dtype=np.float64)
    return event_rows(view, rows, days, val, ct_ns(days, MEHEDGE_AVAIL_MIN, day_offset=-1))


def _ecbfix(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k3 import ecbfix

    m = ecbfix.make_6e()
    plans = ecbfix.schedule(m.t_e, m.full_sessions, m.tgt_closing_days)
    view, rows = vehicle_rows(ctx, ("6E",))
    days = np.array([epoch_day(d) for d in plans], dtype=np.int64)
    inst = np.array([p.leg2_entry_ns for p in plans.values()], dtype=np.int64)  # T_E
    return fixed_clock(view, rows, days, inst)


def _tky(member: str, ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k3 import tkypost, tkypre

    if member == "tkypost":
        m = tkypost.make_6j()
        plans = tkypost.schedule(m.business_days, m.t_t, m.full_sessions)
        inst = [p.entry_ns for p in plans.values()]  # T_T on d - 1
    else:
        m = tkypre.make_6j()
        plans = tkypre.schedule(m.event_days, m.t_t, m.full_sessions)
        inst = [p.exit_ns + NS_MIN for p in plans.values()]  # exit bar T_T - 1 on d - 1
    view, rows = vehicle_rows(ctx, ("6J",))
    days = np.array([epoch_day(d) for d in plans], dtype=np.int64)
    return fixed_clock(view, rows, days, np.array(inst, dtype=np.int64))


_PAIRS = {"ecbfix": _ecbfix, "tkypost": partial(_tky, "tkypost"),
          "tkypre": partial(_tky, "tkypre")}


def _pair_side(key: str, side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k3_" + key, _PAIRS[key])[side]


def _pair_specs(key: str, family: str, source: str,
                sides: tuple[str, ...] = ("mto", "msince")) -> tuple[SignalSpec, ...]:
    """The fixed-clock signals of one event; a side the clock never reaches is left out."""
    return tuple(SignalSpec(f"k3_{key}_{side}", family, "K3", "member", source, (), True,
                            partial(_pair_side, key, 0 if side == "mto" else 1))
                 for side in sides)


SPECS = (
    SignalSpec("k3_ldnmom_trend", "K3-ldnmom-01", "K3", "member",
               "strategy/members/k3/ldnmom.py:48-77 (schedule, momentum_side)", ("6E", "6J"),
               True, partial(_two_read, "ldnmom", ("6E", "6J")), own_path_only=True),
    SignalSpec("k3_ldnrev_move", "K3-ldnrev-01", "K3", "member",
               "strategy/members/k3/ldnrev.py:47-82 (schedule, contrarian_side)",
               ("6E", "6J", "6S"), True, partial(_two_read, "ldnrev", ("6E", "6J", "6S")),
               own_path_only=True),
    SignalSpec("k3_mehedge_req", "K3-mehedge-01", "K3", "member",
               "strategy/members/k3/mehedge.py:75-91 (event_sides); k3/_mehedge_signal.py", (),
               True, _mehedge),
    *_pair_specs("ecbfix", "K3-ecbfix-01", "strategy/members/k3/ecbfix.py:72-91 (schedule)"),
    # T_T falls on the evening of d - 1, before every decision time of d: minutes since only
    *_pair_specs("tkypost", "K3-tkypost-01", "strategy/members/k3/tkypost.py:51-67",
                 ("msince",)),
    *_pair_specs("tkypre", "K3-tkypre-01", "strategy/members/k3/tkypre.py:53-70", ("msince",)),
)

__all__ = ["SPECS"]
