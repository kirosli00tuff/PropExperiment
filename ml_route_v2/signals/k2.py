"""V2.3 member signals of K2's event members (rates rows).

Sources: strategy/members/k2/aucpre.py, aucpost.py, fomcpost.py, monthend.py (fixed clock) and
predrift.py; literal tables strategy/members/k2/_releases.py and _month_end.py.
- Fixed clock (signals._events.fixed_clock: minutes to, minutes since; a side the decision clock
  can never reach is left out, reading SC-9):
  - ``k2_auction_*`` (K2-aucpre-01 and K2-aucpost-01 share the event, reading SC-4): the
    tenor-matched Treasury auction instant T_a (k2/_event_common.auction_schedule's T_a, CT) on
    each vehicle's own tenor (AUCTION_TENOR);
  - ``k2_fomc_*`` (K2-fomcpost-01): the FOMC statement at 13:00 CT on FOMC_STATEMENT_DATES;
  - ``k2_monthend_*`` (K2-monthend-01): trade dates N-1 and N (monthend.EVENT_DATES); the member
    has no release instant, so the anchor is its own entry bar, 07:20 CT (reading SC-5).
- ``k2_predrift_move`` (K2-predrift-01, ZN and ZB): close(08:49) - open(08:30) in vehicle ticks on
  ISM_SERVICES_DATES, both bars with one instrument_id; known at 08:50 CT.
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
    day_set,
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
    per_vehicle,
    vehicle_rows,
)


def _literals() -> tuple[tuple[str, ...], int, int, tuple[str, ...]]:
    from strategy.members.k2._event_common import RATES_EXPOSURES
    from strategy.members.k2.predrift import EXPOSURES
    from strategy.members.k5.fomc import SIGNAL_START_CT  # the 12:59 bar before the statement

    o_rates = session_minutes("ZN")[0]  # monthend.py: the entry bar at O = 07:20
    return RATES_EXPOSURES, minute_of(SIGNAL_START_CT) + 1, o_rates, EXPOSURES


# fomcpost.py: statements released at 13:00 CT (k5/fomc.py reads the 12:59 bar before it)
RATES, FOMC_MIN, MONTHEND_ANCHOR_MIN, PREDRIFT = _literals()


def _auction(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k2._event_common import AUCTION_TENOR
    from strategy.members.k2._releases import TREASURY_AUCTIONS

    view, _ = vehicle_rows(ctx, RATES)
    frames = []
    for v in RATES:
        rows = view.where_root((v,))
        recs = [(epoch_day(d), minute_of(t)) for d, tenor, t in TREASURY_AUCTIONS
                if tenor == AUCTION_TENOR[v]]
        days = np.array([r[0] for r in recs], dtype=np.int64)
        mins = np.array([r[1] for r in recs], dtype=np.int64)
        frames.append(fixed_clock(view, rows, days, ct_ns(days, mins)))
    return _merge(frames)


def _merge(frames: list[tuple[pd.DataFrame, pd.DataFrame]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Combine per-vehicle pairs whose applicable rows are disjoint."""
    return combine([f[0] for f in frames]), combine([f[1] for f in frames])


def _fomc(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k2._releases import FOMC_STATEMENT_DATES

    view, rows = vehicle_rows(ctx, RATES)
    days = day_set(FOMC_STATEMENT_DATES)
    return fixed_clock(view, rows, days, ct_ns(days, FOMC_MIN))


def _monthend(ctx: SignalContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    from strategy.members.k2.monthend import EVENT_DATES

    view, rows = vehicle_rows(ctx, RATES)
    days = day_set(EVENT_DATES)
    return fixed_clock(view, rows, days, ct_ns(days, MONTHEND_ANCHOR_MIN))


_PAIRS = {"auction": _auction, "fomc": _fomc, "monthend": _monthend}


def _pair_side(key: str, side: int, ctx: SignalContext) -> pd.DataFrame:
    return cached_pair(ctx, "k2_" + key, _PAIRS[key])[side]


def _predrift(ctx: SignalContext) -> pd.DataFrame:
    from strategy.members.k2._releases import ISM_SERVICES_DATES
    from strategy.members.k2.predrift import (
        ENTRY_DECISION_OFFSET_MIN,
        RELEASE_CT,
        SIGNAL_START_OFFSET_MIN,
    )

    view, _ = vehicle_rows(ctx, PREDRIFT)
    ev = day_set(ISM_SERVICES_DATES)
    t_rel = minute_of(RELEASE_CT)
    start_ns = ct_ns(ev, t_rel + SIGNAL_START_OFFSET_MIN)
    end_ns = ct_ns(ev, t_rel + ENTRY_DECISION_OFFSET_MIN)

    def one(v: str, rows: np.ndarray) -> pd.DataFrame:
        b = bars_of(ctx, path_of(v))
        i0, i1 = b.at(start_ns), b.at(end_ns)
        ok = same_iid(b, i0, i1)
        val = np.full(len(ev), np.nan)
        val[ok] = (b.close[i1[ok]] - b.open[i0[ok]]) * per_unit(v)
        return event_rows(view, rows, ev, val, end_ns + NS_MIN)

    return per_vehicle(ctx, PREDRIFT, one)


def _pair_specs(key: str, family: str, source: str, stem: str,
                sides: tuple[str, ...] = ("mto", "msince")) -> tuple[SignalSpec, ...]:
    """The fixed-clock signals of one event; a side the clock never reaches is left out."""
    return tuple(SignalSpec(f"k2_{stem}_{side}", family, "K2", "member", source, (), True,
                            partial(_pair_side, key, 0 if side == "mto" else 1))
                 for side in sides)


SPECS = (
    *_pair_specs("auction", "K2-aucpre-01", "strategy/members/k2/_event_common.py:78 "
                 "(auction_schedule T_a); aucpre.py, aucpost.py", "auction"),
    # 13:00 CT is after the last rates decision time (12:50): minutes since never applies
    *_pair_specs("fomc", "K2-fomcpost-01", "strategy/members/k2/fomcpost.py:33-38", "fomc",
                 ("mto",)),
    # the 07:20 anchor is before the first rates decision time (07:50): minutes to never applies
    *_pair_specs("monthend", "K2-monthend-01", "strategy/members/k2/monthend.py:45-50",
                 "monthend", ("msince",)),
    SignalSpec("k2_predrift_move", "K2-predrift-01", "K2", "member",
               "strategy/members/k2/predrift.py:45-52", ("ZN", "ZB"), True, _predrift,
               own_path_only=True),
)

# Families that share another family's signals (reading SC-4).
SHARED = {"K2-aucpost-01": ("k2_auction_mto", "k2_auction_msince")}

__all__ = ["SHARED", "SPECS"]
