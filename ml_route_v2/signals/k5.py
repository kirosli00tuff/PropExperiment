"""V2.3 member signals of K5's members (MGC rows on GC bars, MHG rows on HG bars).

Sources: strategy/members/k5/ovr.py, pmfix.py, preauc.py (fixed clock); tables
strategy/members/k5/_releases.py (GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS) and k5/_calendar.py.
- ``k5_ovr_ret`` and ``k5_ovr_pct`` (MGC, MHG): as K4-ovr-01 (signals.k4.ovr_frames) at the
  member's clocks t = O + 60k while t <= C (ovr.decision_times: MGC 08:20..12:20, MHG
  08:10..11:10), reference ovr.reference_dates(d), floor ovr.min_values (80% of the possible).
- ``k5_pmfix_move`` (MGC): close(T_P + 1) - close(T_P - 1) on GOLD_PM_AUCTIONS dates, vehicle
  ticks; both bars one instrument_id; known at T_P + 2.
- ``k5_preauc_msince`` (MGC): minutes since the AM auction instant T (preauc.schedule entry +
  31 min); T precedes every metals decision time, so there is no minutes-to signal.
K5-fomc-01 is excluded (signals.__init__.EXCLUDED): its move is known at 13:05 CT, after the last
metals decision time (12:50 CT).
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
    nothing,
    vehicle_rows,
)
from ml_route_v2.signals.k4 import ovr_frames

MGC, MHG = "MGC", "MHG"


def _ovr_side(side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k5_ovr", lambda c: ovr_frames(c, (MGC, MHG), "k5"))[side]


def _pmfix(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k5 import pmfix

    plans = pmfix.schedule(pmfix.make_mgc().pm_auctions)
    keys = sorted(plans)
    days = np.array([epoch_day(d) for d in keys], dtype=np.int64)
    m0 = np.array([plans[d][0] for d in keys], dtype=np.int64)
    m1 = np.array([plans[d][1] for d in keys], dtype=np.int64)
    view, rows = vehicle_rows(ctx, (MGC,))
    if not len(rows):
        return nothing(view)
    b = bars_of(ctx, path_of(MGC))
    end_ns = ct_ns(days, m1)
    i0, i1 = b.at(ct_ns(days, m0)), b.at(end_ns)
    ok = same_iid(b, i0, i1)
    val = np.full(len(days), np.nan)
    val[ok] = (b.close[i1[ok]] - b.close[i0[ok]]) * per_unit(MGC)
    return event_rows(view, rows, days, val, end_ns + NS_MIN)


def _preauc(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k5 import preauc

    plans = preauc.schedule(preauc.make_mgc().am_auctions)
    days = np.array([epoch_day(d) for d in plans], dtype=np.int64)
    t_auc = np.array([e - preauc.ENTRY_DECISION_OFFSET_MIN for e, _x in plans.values()],
                     dtype=np.int64)
    view, rows = vehicle_rows(ctx, (MGC,))
    return fixed_clock(view, rows, days, ct_ns(days, t_auc))


def _preauc_side(side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k5_preauc", _preauc)[side]


SPECS = (
    SignalSpec("k5_ovr_ret", "K5-ovr-01", "K5", "member", "strategy/members/k5/ovr.py:64-110",
               ("GC", "HG"), True, partial(_ovr_side, 0), own_path_only=True),
    SignalSpec("k5_ovr_pct", "K5-ovr-01", "K5", "member",
               "strategy/members/k5/ovr.py:64-120 (reference_dates, min_values)", ("GC", "HG"),
               True, partial(_ovr_side, 1), own_path_only=True),
    SignalSpec("k5_pmfix_move", "K5-pmfix-01", "K5", "member",
               "strategy/members/k5/pmfix.py:38-54 (schedule)", ("GC",), True, _pmfix),
    # the AM auction (04:30 or 05:30 CT) precedes every metals decision time: minutes since only
    SignalSpec("k5_preauc_msince", "K5-preauc-01", "K5", "member",
               "strategy/members/k5/preauc.py:42-58 (schedule)", (), True,
               partial(_preauc_side, 1)),
)

__all__ = ["SPECS"]
