"""base_rules.sim: a hand-computed multi-day trade to the cent (a roll across a splice and an
overnight mark) and a single-day trade that matches the frozen engine fill for fill."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from datetime import UTC, date, datetime
from fractions import Fraction

import numpy as np

from base_rules.context import empty_release_rules
from base_rules.costs import ReleaseRules, vehicle_cost
from base_rules.sim import simulate
from base_rules.store import ProductBars
from data.config import REPO_ROOT
from screening.stage_e_engine import Fill, run_engine
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.stage_e.interface import LegSpec, leg_market_intent
from tests._base_rules_fixtures import make_bars
from tests._stage_e_synthetic import CT, NS, product_frame

D1, D2, D3, D4 = date(2016, 3, 7), date(2016, 3, 8), date(2016, 3, 9), date(2016, 3, 10)
ZN_TV = Fraction(3125, 2)  # $15.625 a tick, in cents


def _table_cost(root: str, ts_ns: int, side: str) -> int:
    """By hand from reports/stage_e2a_costs.json: commission per side + ceil(side_ticks x tv)."""
    raw = json.loads((REPO_ROOT / "reports" / "stage_e2a_costs.json").read_text())
    entry = raw["products"][root]
    local = datetime.fromtimestamp(ts_ns / NS, tz=UTC).astimezone(CT)
    minute = local.hour * 60 + local.minute
    (bucket,) = [b for b in entry["buckets"] if b["start_min"] <= minute < b["end_min"]]
    tv = Fraction(str(entry["tick_value_usd"])) * 100
    comm = int(Fraction(str(entry["commission_rt_usd"])) * 100) // 2
    return comm + math.ceil(round(float(bucket["side_ticks"][side]) * float(tv), 6))


def test_multi_day_long_with_overnight_marks_and_a_roll_is_exact_to_the_cent() -> None:
    splice = int(datetime(2016, 3, 9, tzinfo=UTC).timestamp()) * NS  # 18:00 CT on D2
    bars = make_bars("ZN", [
        (D1, 14 * 60, 10000, 10001, "ZNH6"), (D2, 14 * 60, 10010, 10011, "ZNH6"),
        (D2, 15 * 60 + 30, 10012, 10012, "ZNH6"), (D3, 7 * 60 + 30, 9900, 9901, "ZNM6"),
        (D3, 14 * 60, 9905, 9906, "ZNM6"), (D4, 14 * 60, 9920, 9921, "ZNM6")],
        splices=[(splice, D3)])
    i = {(d, m): k for k, (d, m) in enumerate([(D1, 840), (D2, 840), (D2, 930), (D3, 450),
                                                (D3, 840), (D4, 840)])}
    vc = vehicle_cost("ZN")
    res = simulate(bars, vc, empty_release_rules(), [(i[(D1, 840)], 1), (i[(D4, 840)], 0)],
                   [i[(D1, 840)], i[(D2, 840)], i[(D3, 840)], i[(D4, 840)]])
    assert res.ok
    assert [(f.kind, f.trade, f.price_ticks) for f in res.fills] == [
        ("entry", 1, 10000), ("roll_out", -1, 10012), ("roll_in", 1, 9900), ("exit", -1, 9920)]
    # gross by hand: (10010-10000) + (10012-10010) [old contract] + (9905-9900) + (9920-9905)
    assert res.gross_cents == 32 * ZN_TV == 50000
    c = [_table_cost("ZN", int(bars.ts[k]), s) for k, s in
         ((i[(D1, 840)], "buy"), (i[(D2, 930)], "sell"), (i[(D3, 450)], "buy"),
          (i[(D4, 840)], "sell"))]
    assert res.costs["base"] == sum(c)
    assert res.costs["stress"] == sum(c) + 4 * ZN_TV  # one extra tick per side, every fill
    assert res.daily["base"] == {D1: -c[0], D2: 12 * ZN_TV - c[1], D3: 5 * ZN_TV - c[2],
                                 D4: 15 * ZN_TV - c[3]}
    assert sum(res.daily["base"].values()) == res.net("base") == 50000 - sum(c)
    assert (res.entry_date, res.exit_date) == (D1, D4)


def test_a_short_flip_to_long_pays_two_sides_at_the_flip() -> None:
    bars = make_bars("ZN", [(D1, 840, 100, 100, "A"), (D2, 840, 90, 90, "A"),
                            (D3, 840, 95, 95, "A")])
    res = simulate(bars, vehicle_cost("ZN"), empty_release_rules(), [(0, -1), (1, 1), (2, 0)])
    assert [(f.kind, f.trade) for f in res.fills] == [("entry", -1), ("flip", 2), ("exit", -1)]
    assert res.gross_cents == (10 + 5) * ZN_TV
    flip_cost = _table_cost("ZN", int(bars.ts[1]), "buy")
    assert res.fills[1].costs["base"] == 2 * flip_cost


def test_a_contract_change_not_explained_by_a_recorded_splice_excludes_the_unit() -> None:
    splice = int(datetime(2016, 3, 9, tzinfo=UTC).timestamp()) * NS
    vc, rel = vehicle_cost("ZN"), empty_release_rules()
    rolled = make_bars("ZN", [(D1, 840, 100, 100, "A"), (D4, 840, 90, 90, "B")],
                       splices=[(splice, D3)])
    res = simulate(rolled, vc, rel, [(0, 1), (1, 0)])
    assert res.ok and [f.kind for f in res.fills] == ["entry", "roll_out", "roll_in", "exit"]
    unrecorded = make_bars("ZN", [(D1, 840, 100, 100, "A"), (D4, 840, 90, 90, "B")])
    res = simulate(unrecorded, vc, rel, [(0, 1), (1, 0)])
    assert not res.ok and res.reason == "contract change"
    same = make_bars("ZN", [(D1, 840, 100, 100, "A"), (D4, 840, 90, 90, "A")],
                     splices=[(splice, D3)])
    res = simulate(same, vc, rel, [(0, 1), (1, 0)])
    assert not res.ok and res.reason == "contract change"


# ------------------------------------------------------------- frozen engine match ----
class _Script:
    name = "script"
    trading_windows: dict = {}

    def __init__(self, orders: dict) -> None:
        self.orders = orders

    def on_minute(self, view, account):  # noqa: ANN001, ANN201
        local = datetime.fromtimestamp(view.ts_event_ns / NS, tz=UTC).astimezone(CT)
        side = self.orders.get((local.hour, local.minute))
        return [leg_market_intent(view, view_root(view), side, 1)] if side else []


def view_root(view) -> str:  # noqa: ANN001
    return next(iter(view.bars))


def _bars_of(root: str, frame, tick: float) -> ProductBars:
    ts = frame["ts_event"].to_numpy(dtype=np.int64)
    days = [date.fromisoformat(d) for d in frame["trade_date"]]
    return ProductBars(root, ts, np.rint(frame["open"].to_numpy() / tick).astype(np.int64),
                       np.rint(frame["close"].to_numpy() / tick).astype(np.int64),
                       np.zeros(len(ts), dtype=np.int32), ("C",), np.ones(len(ts), dtype=bool),
                       np.array([d.toordinal() for d in days], dtype=np.int64), (),
                       frozenset(), ())


def _engine_vs_sim(root: str, legs: dict, frame, entry: tuple[int, int], exit_: tuple[int, int],
                   tick: float, day: date, releases: ReleaseCalendar | None = None) -> list:
    releases = releases or ReleaseCalendar({}, (), date(2019, 5, 1), date(2026, 6, 19), "0" * 64,
                                           "none")
    rules = StageERules(legs, frozenset({day}), frozenset(), releases)

    def before(hm: tuple[int, int]) -> tuple[int, int]:  # the decision bar: one minute earlier
        m = hm[0] * 60 + hm[1] - 1
        return m // 60, m % 60

    member = _Script({before(entry): "buy", before(exit_): "sell"})
    res = run_engine({root: frame}, member, (LegSpec(root, True),), rules)
    fills = [f for f in res.events(Fill) if f.reason == "strategy"]
    assert len(fills) == 2
    bars = _bars_of(root, frame, tick)
    idx = {int(t): k for k, t in enumerate(bars.ts)}
    i_in, i_out = idx[fills[0].fill_ts_ns], idx[fills[1].fill_ts_ns]
    local = [datetime.fromtimestamp(f.fill_ts_ns / NS, tz=UTC).astimezone(CT) for f in fills]
    assert [(t.hour, t.minute) for t in local] == [entry, exit_]
    rel = ReleaseRules(releases, {}, frozenset(), {})
    sim = simulate(bars, vehicle_cost(root), rel, [(i_in, 1), (i_out, 0)])
    assert [f.event for f in sim.fills] == [f.event_window for f in fills]
    assert [f.ts_ns for f in sim.fills] == [f.fill_ts_ns for f in fills]
    assert [f.price_ticks * tick for f in sim.fills] == [f.price for f in fills]
    assert [f.costs["base"] for f in sim.fills] == [f.commission_cents + f.slippage_cents
                                                    for f in fills]
    assert sim.gross_cents == fills[1].gross_realized_cents
    assert sim.net("base") == sum(f.gross_realized_cents - f.commission_cents - f.slippage_cents
                                  for f in fills)
    return fills


def test_zn_h1_window_trade_matches_the_frozen_engine_fill_for_fill() -> None:
    day = date(2023, 6, 13)
    frame = product_frame("ZN", [day], 5, start=(13, 0), end=(14, 30), vol_ticks=3.0)
    _engine_vs_sim("ZN", {"ZN": leg_inputs("ZN", traded=True)}, frame, (13, 30), (14, 0),
                   0.015625, day)


def test_an_event_window_fill_pays_the_engine_event_cost() -> None:
    from screening.stage_e_rules import release_calendar_from_dict

    day = date(2023, 6, 13)
    release = datetime(2023, 6, 13, 13, 15, tzinfo=CT).astimezone(UTC)
    releases = release_calendar_from_dict(
        {"schema": "stage_e_release_calendar/1",
         "coverage": {"first": "2023-06-01", "last": "2023-06-30"},
         "releases": [{"id": "r", "instant_utc": release.isoformat(), "products": ["ZN"]}]},
        "0" * 64, "test")
    frame = product_frame("ZN", [day], 6, start=(13, 0), end=(14, 30), vol_ticks=3.0)
    fills = _engine_vs_sim("ZN", {"ZN": leg_inputs("ZN", traded=True)}, frame, (13, 30),
                           (14, 0), 0.015625, day, releases)
    assert [f.event_window for f in fills] == [True, False]


def test_nq_path_on_the_mnq_vehicle_matches_the_frozen_engine_fill_for_fill() -> None:
    import pandas as pd

    day, prior = date(2023, 6, 13), date(2023, 6, 12)
    frame = product_frame("NQ", [day], 7, start=(14, 0), end=(15, 5), base_ticks=60000,
                          vol_ticks=4.0)
    head = product_frame("NQ", [prior], 99, start=(14, 0), end=(15, 5), base_ticks=60000,
                         vol_ticks=0.0)
    frame = pd.concat([head, frame], ignore_index=True)
    mnq = leg_inputs("MNQ", traded=True)
    hybrid = replace(mnq, root="NQ", product=leg_inputs("NQ", traded=False).product,
                     costs=replace(mnq.costs, root="NQ"))
    assert hybrid.tick_value_cents == vehicle_cost("NQ").tick_value_cents == 50
    _engine_vs_sim("NQ", {"NQ": hybrid}, frame, (14, 30), (15, 0), 0.25, day)
