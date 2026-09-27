"""Cross-product alignment (D11.5), cross-product windows (D4) and the member-level coverage check
(D9): the shared UTC minute grid, no forward fill, a missing leg bar blocks new exposure, the
union of the legs' roll blackouts, rule UR-1, and coverage known answers. Synthetic data only."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

import pandas as pd
import pytest

from data.stage_e_bars import RESEARCH, STEP2, LegFrame
from screening.stage_e_align import (
    UNSEEN_ROLL_DATES,
    leg_coverage,
    member_coverage,
    member_window,
)
from screening.stage_e_engine import Fill, IntentRecord, iter_minutes, run_engine
from screening.stage_e_rules import product_bar_iterator
from strategy.stage_e.interface import LegSpec, TradingInterval
from tests._stage_e_synthetic import product_frame
from tests.test_stage_e_rules import MON, TUE, Script, _rules

WED = date(2025, 6, 4)


def _leg(root: str, frame: pd.DataFrame, store: str = RESEARCH, blackout=()) -> LegFrame:
    days = tuple(sorted({date.fromisoformat(d) for d in frame["trade_date"]}))
    return LegFrame(root, store, f"{root}.parquet", "0" * 64, frame, days, (), frozenset(blackout))


def test_the_grid_is_the_union_of_minutes_and_nothing_is_forward_filled() -> None:
    a = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 5))
    b = product_frame("ZB", [MON], 2, start=(9, 2), end=(9, 7))
    feeds = {"ZN": product_bar_iterator("ZN"), "ZB": product_bar_iterator("ZB")}
    grid = list(iter_minutes({"ZN": a, "ZB": b}, feeds))
    assert len(grid) == 7
    assert [sorted(bars) for _, bars in grid] == [["ZN"], ["ZN"], ["ZB", "ZN"], ["ZB", "ZN"],
                                                  ["ZB", "ZN"], ["ZB"], ["ZB"]]


def test_a_member_sees_none_for_a_missing_leg_bar_and_never_a_later_bar() -> None:
    a = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 10), skip={9 * 60 + 4})
    b = product_frame("ZB", [MON], 2, start=(9, 0), end=(9, 10))

    @dataclass
    class Recorder:
        name: str = "rec"
        trading_windows: dict = field(default_factory=dict)
        rows: list = field(default_factory=list)

        def on_minute(self, view, account):
            for bar in view.bars.values():
                assert bar is None or bar.ts_event_ns == view.ts_event_ns
            self.rows.append({r: b is not None for r, b in view.bars.items()})
            return ()

    member = Recorder()
    run_engine({"ZN": a, "ZB": b}, member, (LegSpec("ZN", True), LegSpec("ZB", False)),
               _rules(["ZN", "ZB"], traded=["ZN"]))
    assert len(member.rows) == 10
    assert member.rows[4] == {"ZN": False, "ZB": True}
    assert all(all(r.values()) for i, r in enumerate(member.rows) if i != 4)


def test_no_new_exposure_when_a_read_leg_has_no_bar_but_an_exit_is_allowed() -> None:
    """D11.5: a member whose leg has no bar at a decision time does not trade (opening); closing
    an open position stays allowed (reading RR-1)."""
    zn = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30))
    zb = product_frame("ZB", [MON], 2, start=(9, 0), end=(9, 30),
                       skip={9 * 60 + 5, 9 * 60 + 20})
    member = Script({(MON, 9, 5): [("ZN", "buy", 1)], (MON, 9, 6): [("ZN", "buy", 1)],
                     (MON, 9, 20): [("ZN", "flat", 0)]})
    res = run_engine({"ZN": zn, "ZB": zb}, member, (LegSpec("ZN", True), LegSpec("ZB", False)),
                     _rules(["ZN", "ZB"], traded=["ZN"]))
    refusals = [e.refusal.reason for e in res.events(IntentRecord) if e.refusal]
    assert refusals == ["engine_leg_missing_bar"]
    fills = res.events(Fill)
    assert [f.side for f in fills] == ["buy", "sell"] and fills[1].reason == "strategy"


def test_the_window_is_the_common_dates_less_every_legs_blackout() -> None:
    a = _leg("ZN", product_frame("ZN", [MON, TUE, WED], 1, start=(9, 0), end=(9, 2)),
             blackout=[MON])
    b = _leg("MES", product_frame("MES", [TUE, WED], 2, start=(9, 0), end=(9, 2),
                                  base_ticks=24000), blackout=[WED])
    w = member_window({"ZN": a, "MES": b}, RESEARCH)
    assert w.dates == (TUE,)
    assert w.excluded["not_every_leg_trades"] == (MON,)
    assert w.excluded["roll_blackout_any_leg"] == (WED,)
    assert w.blackout_union == {MON, WED}


def test_rule_ur1_removes_2026_06_18_and_19_from_research_windows_only() -> None:
    days = [date(2026, 6, 17), *UNSEEN_ROLL_DATES]
    frame = product_frame("ZN", days, 1, start=(9, 0), end=(9, 2))
    w = member_window({"ZN": _leg("ZN", frame)}, RESEARCH)
    assert w.dates == (date(2026, 6, 17),)
    assert w.excluded["unseen_roll_UR-1"] == UNSEEN_ROLL_DATES
    old = product_frame("ZN", [date(2020, 6, 17), date(2020, 6, 18)], 1, start=(9, 0),
                        end=(9, 2))
    assert len(member_window({"ZN": _leg("ZN", old, STEP2)}, STEP2).dates) == 2


def test_legs_from_two_stores_are_refused() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 2))
    with pytest.raises(ValueError, match="stores"):
        member_window({"ZN": _leg("ZN", frame), "ZB": _leg("ZB", frame, STEP2)}, RESEARCH)


def test_coverage_known_answers_and_the_095_threshold() -> None:
    iv = (TradingInterval(time(9, 0), time(9, 30)),)
    full = _leg("ZN", product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30)))
    assert (leg_coverage(full, [MON], iv).present, leg_coverage(full, [MON], iv).expected) == (
        30, 30)
    two_missing = _leg("ZN", product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30),
                                           skip={9 * 60 + 3, 9 * 60 + 7}))
    cov = leg_coverage(two_missing, [MON], iv)
    assert (cov.present, cov.expected, cov.passes) == (28, 30, False)  # 0.933 < 0.95
    one_missing = _leg("ZN", product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30),
                                           skip={9 * 60 + 3}))
    assert leg_coverage(one_missing, [MON], iv).passes  # 29/30 = 0.967


def test_coverage_counts_only_minutes_the_group_calendar_has_open() -> None:
    """Rates close at 16:00 CT: [15:50, 17:30) on the trade date's own day expects 10 minutes
    (17:00 onwards is the next trade date's evening)."""
    frame = product_frame("ZN", [MON], 1, start=(15, 50), end=(16, 0))
    cov = leg_coverage(_leg("ZN", frame), [MON], (TradingInterval(time(15, 50), time(17, 30)),))
    assert (cov.present, cov.expected) == (10, 10)


def test_every_read_leg_needs_a_declared_trading_window() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 2))
    with pytest.raises(ValueError, match="no trading window"):
        member_coverage({"ZN": _leg("ZN", frame), "ZB": _leg("ZB", frame)}, [MON],
                        {"ZN": (TradingInterval(time(9, 0), time(9, 2)),)})


def test_the_cross_product_grid_follows_each_legs_own_trade_date() -> None:
    """An equity signal leg and a grain traded leg: grains open at 19:00 CT, equity at 17:00; a
    minute where only the signal leg trades opens no position on the grain leg."""
    zc = product_frame("ZC", [TUE], 1, start=(9, 0), end=(9, 10), base_ticks=1800)
    mes = product_frame("MES", [TUE], 2, start=(8, 55), end=(9, 10), base_ticks=24000)
    member = Script({(TUE, 8, 56): [("ZC", "buy", 1)]})
    res = run_engine({"ZC": zc, "MES": mes}, member, (LegSpec("ZC", True), LegSpec("MES", False)),
                     _rules(["ZC", "MES"], traded=["ZC"]))
    assert [e.refusal.reason for e in res.events(IntentRecord)] == ["engine_leg_missing_bar"]
