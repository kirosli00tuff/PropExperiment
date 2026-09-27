"""The member template (strategy/stage_e/_template.py) runs under the generalized engine: its
clock and size come from the frozen tables, it trades one entry per trade date on a breakout of
the first 15 minutes by 4 ticks, and exits 75 minutes after the entry decision. Synthetic MNQ."""

from __future__ import annotations

from datetime import date, time

import pandas as pd

from screening.stage_e_engine import Fill, run_engine
from strategy.stage_e._template import TemplateBreakout, make_member
from strategy.stage_e.interface import LegSpec, StageEMember, TradingInterval
from tests._stage_e_synthetic import minute_ct, product_frame
from tests.test_stage_e_rules import _rules

MON, TUE = date(2025, 6, 2), date(2025, 6, 3)
BASE = 80000


def _frame(breakout: bool = True) -> pd.DataFrame:
    paths = {(TUE, 8 * 60 + 30 + k): (BASE, BASE + 2, BASE - 2, BASE) for k in range(15)}
    if breakout:
        paths[(TUE, 8 * 60 + 50)] = (BASE, BASE + 10, BASE, BASE + 10)  # close >= hi + 4 ticks
    else:
        paths[(TUE, 8 * 60 + 50)] = (BASE, BASE + 3, BASE, BASE + 3)  # hi + 3: no breakout
    prior = product_frame("MNQ", [MON], 1, start=(14, 0), end=(15, 10), base_ticks=BASE,
                          vol_ticks=0.0)
    day = product_frame("MNQ", [TUE], 2, start=(8, 30), end=(15, 10), base_ticks=BASE,
                        vol_ticks=0.0, path_ticks=paths)
    return pd.concat([prior, day], ignore_index=True)


def test_the_template_reads_its_clock_and_size_from_the_frozen_tables() -> None:
    member = make_member()
    assert isinstance(member, StageEMember)
    assert member.legs == (LegSpec("MNQ", True),)
    assert member.trading_windows == {"MNQ": (TradingInterval(time(8, 30), time(15, 0)),)}


def test_the_template_trades_one_breakout_and_exits_after_75_minutes() -> None:
    res = run_engine({"MNQ": _frame()}, TemplateBreakout("MNQ"), (LegSpec("MNQ", True),),
                     _rules(["MNQ"], dates=(MON, TUE)))
    fills = res.events(Fill)
    assert [f.side for f in fills] == ["buy", "sell"] and fills[0].qty == 1
    assert minute_ct(fills[0].fill_ts_ns) == (8, 51)
    assert minute_ct(fills[1].fill_ts_ns) == (10, 6)  # decision 08:51 + 75 min, next open
    assert fills[1].reason == "strategy"


def test_without_a_breakout_the_template_does_not_trade() -> None:
    res = run_engine({"MNQ": _frame(breakout=False)}, TemplateBreakout("MNQ"),
                     (LegSpec("MNQ", True),), _rules(["MNQ"], dates=(MON, TUE)))
    assert not res.events(Fill)
