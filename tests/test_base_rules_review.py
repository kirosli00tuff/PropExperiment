"""The freeze review's fixes (reports/stage_e16_review.md, the lead's rulings): F-07 (the engine's
limit-lock test on every fill, the no-new-positions count, the 2010-2019 high == low diagnostic),
F-08 (the engine's closure-gap fill equals the simulator's R-B1 close point), F-13 and F-14 (the
descriptive tables). Synthetic data only."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime
from decimal import Decimal

import numpy as np
import pandas as pd

from base_rules import constants as K
from base_rules.context import empty_release_rules
from base_rules.costs import ReleaseRules, vehicle_cost
from base_rules.intraday import DESCRIPTIVE, _pool, product_units, run_intraday
from base_rules.limits import LockRule
from base_rules.sim import simulate
from base_rules.store import ProductBars
from rules import price_limits as pl
from screening.stage_e_engine import Fill, run_engine
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.stage_e.interface import LegSpec, leg_market_intent
from tests._base_rules_fixtures import (
    calendars,
    context,
    intraday_world,
    make_bars,
    ns,
    trade_dates,
)
from tests._stage_e_synthetic import CT, NS, product_frame

PREV, DAY = date(2023, 6, 12), date(2023, 6, 13)
ZC_TICK = 0.25  # vendor units (cents)


# ------------------------------------------------------------------ F-07 ----
def _zc_locked_world(lock: bool) -> tuple[ProductBars, Decimal]:
    s_ticks = 1800  # 450.00 cents
    s = Decimal(repr(s_ticks * ZC_TICK))
    band = pl.limit_band("ZC", DAY, datetime(2023, 6, 13, 17, 45, tzinfo=UTC), s)
    up, _down = pl.limit_prices(band, s)
    up_ticks = int(up / Decimal("0.25"))
    rows = [(PREV, 13 * 60 + 14, s_ticks, s_ticks, "Z"),
            (DAY, 12 * 60 + 45, up_ticks, up_ticks, "Z"), (DAY, 13 * 60 + 15, up_ticks,
                                                            up_ticks, "Z")]
    lo = up_ticks if lock else up_ticks - 4
    extra = {(PREV, 13 * 60 + 14): {"volume": 10},
             (DAY, 12 * 60 + 45): {"high": up_ticks, "low": lo}}
    return make_bars("ZC", rows, extra=extra), s


def test_a_fill_at_a_limit_locked_bar_is_excluded() -> None:
    cals = calendars(("grains",))
    for lock in (True, False):
        bars, s = _zc_locked_world(lock)
        rule = LockRule(bars, cals["grains"].frozen)
        assert rule.prior_settlement(DAY) == s
        res = simulate(bars, vehicle_cost("ZC"), empty_release_rules(), [(1, 1), (2, 0)],
                       locks=rule)
        assert (not res.ok and res.reason == "limit locked") if lock else res.ok
    bars, _ = _zc_locked_world(True)
    rule = LockRule(bars, cals["grains"].frozen)
    assert not rule(1, -1)  # a sell is locked only at limit down
    old = make_bars("ZC", [(date(2016, 3, 7), 765, 10, 10, "Z")])
    assert not LockRule(old, cals["grains"].frozen)(0, 1)  # no limit table before 2019-05


def _nq_world():  # noqa: ANN202
    cals = calendars(("equity", "rates"))
    days = trade_dates(cals["equity"], date(2016, 1, 4), date(2017, 12, 29))
    bars = intraday_world("NQ", days, h1_edge=8.0, h4_edge=0.0, noise=4.0, seed=9)
    flags = np.zeros(len(bars.ts), dtype=bool)
    flags[np.flatnonzero(bars.ts == ns(days[100], 14 * 60 + 30))] = True  # an H1 entry bar
    flat = bars.td == days[100].toordinal()  # that date's bars have high == low
    bars = ProductBars(**{**bars.__dict__, "no_new": flags,
                          "high_t": np.where(flat, bars.open_t, bars.open_t + 1),
                          "low_t": bars.open_t})
    return context(cals, {"NQ": bars}, starts={p: date(2016, 1, 1) for p in K.PRODUCTS}), bars


def test_no_new_positions_entries_are_counted_and_the_descriptive_tables_exist() -> None:
    ctx, bars = _nq_world()
    c: Counter = Counter()
    units = product_units("H1", ctx, "NQ", bars, c, set())
    assert c["no new positions (Topstep)"] == 1
    assert c["diag: 2010-2019 fill bars with high == low"] == 2  # entry and exit on days[100]
    out = run_intraday("H1", ctx, ("NQ",))
    desc = out.notes["descriptive"]
    assert set(desc) == set(DESCRIPTIVE["H1"])
    base_n = len(out.units[K.BASE])
    assert desc["topstep_without_no_new_positions (F-07)"]["stats"][K.BASE]["n"] == base_n - 1
    assert desc["without_S_after_1508 (F-14)"]["stats"][K.BASE]["n"] == base_n  # S = 15:00
    from base_rules.scaling import TRADED

    for u in units:
        u.status, u.sigma = TRADED, 1.0
    units[0].info["after_1508"] = True
    kept = _pool(units, DESCRIPTIVE["H1"]["without_S_after_1508 (F-14)"])
    assert len(kept[K.BASE]) == len(units) - 1
    assert set(run_intraday("H4", ctx, ("NQ",)).notes["descriptive"]) == set(DESCRIPTIVE["H4"])


# ------------------------------------------------------------------ F-08 ----
class _Script:
    name = "script"
    trading_windows: dict = {}

    def __init__(self, orders: dict) -> None:
        self.orders = orders

    def on_minute(self, view, account):  # noqa: ANN001, ANN201
        local = datetime.fromtimestamp(view.ts_event_ns / NS, tz=UTC).astimezone(CT)
        side = self.orders.get((local.hour, local.minute))
        return [leg_market_intent(view, next(iter(view.bars)), side, 1)] if side else []


def test_the_engine_closure_gap_fill_equals_the_r_b1_close_point() -> None:
    """A grains day whose session closes at 13:15 (2010-2015; R-B1 also governs equity 15:15):
    the 13:15 bar is a closure print, entry 12:45, exit ordered at 13:15. Equity cannot be run
    here: the engine's Topstep flatten (15:08) closes an equity position before 15:15."""
    frame = product_frame("ZC", [DAY], 4, start=(12, 30), end=(13, 16), base_ticks=1800,
                          vol_ticks=2.0)
    head = product_frame("ZC", [PREV], 99, start=(13, 0), end=(13, 16), base_ticks=1800,
                         vol_ticks=0.0)
    frame = pd.concat([head, frame], ignore_index=True)
    closure = frame["ts_event"].to_numpy() == ns(DAY, 13 * 60 + 15)
    frame.loc[closure, "in_scheduled_closure"] = True
    releases = ReleaseCalendar({}, (), date(2019, 5, 1), date(2026, 6, 19), "0" * 64, "none")
    rules = StageERules({"ZC": leg_inputs("ZC", traded=True)}, frozenset({DAY}), frozenset(),
                        releases)
    assert rules.skip_closure_bars
    res = run_engine({"ZC": frame}, _Script({(12, 44): "buy", (13, 14): "sell"}),
                     (LegSpec("ZC", True),), rules)
    fills = [f for f in res.events(Fill) if f.reason == "strategy"]
    assert len(fills) == 2 and fills[1].closure_gap
    ts = frame["ts_event"].to_numpy(dtype=np.int64)
    days = [date.fromisoformat(d) for d in frame["trade_date"]]
    bars = ProductBars("ZC", ts, np.rint(frame["open"].to_numpy() / ZC_TICK).astype(np.int64),
                       np.rint(frame["close"].to_numpy() / ZC_TICK).astype(np.int64),
                       np.zeros(len(ts), dtype=np.int32), ("C",),
                       ~frame["in_scheduled_closure"].to_numpy(dtype=bool),
                       np.array([d.toordinal() for d in days], dtype=np.int64), (), frozenset(),
                       ())
    i_in = bars.bar(DAY, 12 * 60 + 45)
    i_last = bars.bar(DAY, 13 * 60 + 14)
    assert bars.bar(DAY, 13 * 60 + 15) is None  # the closure print is never usable
    sim = simulate(bars, vehicle_cost("ZC"), ReleaseRules(releases, {}, frozenset(), {}),
                   [((i_in, False), 1), ((i_last, True), 0)])
    assert [f.fill_ns for f in sim.fills] == [f.fill_ts_ns for f in fills]
    assert [f.price_ticks * ZC_TICK for f in sim.fills] == [f.price for f in fills]
    assert [f.costs["base"] for f in sim.fills] == [f.commission_cents + f.slippage_cents
                                                    for f in fills]
    assert [f.event for f in sim.fills] == [f.event_window for f in fills]
    assert sim.gross_cents == fills[1].gross_realized_cents
