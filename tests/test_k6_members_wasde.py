"""Stage E.8 K6-wasdepre-01 and K6-wasdepost-01 (MemberCoder-B): reports/stage_e8_member_specs.md
sections 6 and 7, S0.3-S0.12, K6-L-11, K6-L-12 and ruling R-1b-1.

Synthetic bars only, built with tests/test_k6_members_limitcont.py's kit. The rule is pinned by
feeding the member its bars in order with a fixed account (direct calls), and its fills and exits
through the real Stage E engine with a WASDE release at 11:00 CT (12:00 ET) in the calendar. The
event dates are the real EC-WASDE table (strategy/members/k6/_wasde.py).
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

import pytest

from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k6 import _calendar, _wasde, wasdepost, wasdepre
from strategy.stage_e.interface import LegSpec, StageEMember, TradingInterval
from tests.test_k6_members_limitcont import (
    Day,
    feed,
    fills,
    hm,
    intents,
    release_at,
    run,
    trade,
)

WASDE = date(2025, 6, 12)  # a research-window WASDE date (Thursday), a full grain session
PRIOR = date(2025, 6, 11)  # its d-1: the engine's D9.7 needs d-1's settlement proxy
NOT_WASDE = date(2025, 6, 13)
CANCELLED = date(2025, 10, 9)  # the October 2025 WASDE was not published (R-1b-1)
MOVED_FROM, MOVED_TO = date(2025, 11, 10), date(2025, 11, 14)  # the November 2025 release
PRE_ROOTS = ("ZC", "ZS")
O830, E1029, X1114 = hm(8, 30), hm(10, 29), hm(11, 14)
S1059, E1114, X1313 = hm(10, 59), hm(11, 14), hm(13, 13)


def pre(root: str) -> wasdepre.WasdePre:
    return wasdepre.make_zc() if root == "ZC" else wasdepre.make_zs()


def post() -> wasdepost.WasdePost:
    return wasdepost.make_zc()


def pre_day(day: date, start_open: int = 0, entry_close: int = 5, **kw: Any) -> Day:
    """The 08:30 bar opens at ``start_open`` ticks (closes at 0), the 10:29 bar closes at
    ``entry_close``; every other bar at 0."""
    closes = {E1029: entry_close, **kw.pop("closes", {})}
    opens = {O830: start_open, **kw.pop("opens", {})}
    return Day(day, closes=closes, opens=opens, **kw)


def post_day(day: date, signal_close: int = 0, entry_close: int = 5, **kw: Any) -> Day:
    closes = {S1059: signal_close, E1114: entry_close, **kw.pop("closes", {})}
    return Day(day, closes=closes, **kw)


# ------------------------------------------------------------------ declarations ----
@pytest.mark.parametrize("root", PRE_ROOTS)
def test_wasdepre_declaration(root: str) -> None:
    member = pre(root)
    assert isinstance(member, StageEMember)
    assert member.name == f"K6-wasdepre-01 {root}" and member.legs == (LegSpec(root, True),)
    assert member.trading_windows == {root: (TradingInterval(time(8, 30), time(8, 31)),
                                             TradingInterval(time(10, 29), time(11, 16)))}
    assert load_frozen_tables().vehicles[root].q_c == member._q == 1


def test_wasdepost_declaration() -> None:
    member = post()
    assert isinstance(member, StageEMember)
    assert member.name == "K6-wasdepost-01 ZC" and member.legs == (LegSpec("ZC", True),)
    assert member.trading_windows == {"ZC": (TradingInterval(time(10, 59), time(13, 15)),)}
    assert load_frozen_tables().vehicles["ZC"].q_c == member._q == 1


def test_exposures() -> None:
    with pytest.raises(ValueError, match="does not trade"):
        wasdepre.WasdePre("ZW")
    with pytest.raises(ValueError, match="does not trade"):
        wasdepost.WasdePost("ZS")


def test_the_event_dates_used_here() -> None:
    w = _wasde.WASDE_DATES
    assert WASDE in w and MOVED_TO in w
    assert NOT_WASDE not in w and CANCELLED not in w and MOVED_FROM not in w
    for d in (WASDE, NOT_WASDE, CANCELLED, MOVED_FROM, MOVED_TO):
        assert d in _calendar.GRAIN_FULL_SESSIONS, d


# ----------------------------------------------------------------- wasdepre rule ----
@pytest.mark.parametrize("root", PRE_ROOTS)
def test_wasdepre_trades_a_wasde_date_and_not_another(root: str) -> None:
    assert feed(pre(root), [pre_day(WASDE)]) == [(WASDE, "10:29", "buy")]
    for d in (NOT_WASDE, CANCELLED, MOVED_FROM):
        assert feed(pre(root), [pre_day(d)]) == [], d
    assert feed(pre(root), [pre_day(MOVED_TO)]) == [(MOVED_TO, "10:29", "buy")]


def test_wasdepre_a_dropped_wasde_does_not_trade(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_wasde, "DROPPED_WASDE", {WASDE: "synthetic"})
    assert feed(pre("ZC"), [pre_day(WASDE)]) == []
    assert feed(pre("ZC"), [pre_day(MOVED_TO)]) == [(MOVED_TO, "10:29", "buy")]


def test_wasdepre_needs_a_full_grain_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wasdepre, "GRAIN_FULL_SESSIONS", frozenset({MOVED_TO}))
    assert feed(pre("ZC"), [pre_day(WASDE)]) == []
    assert feed(pre("ZC"), [pre_day(MOVED_TO)]) == [(MOVED_TO, "10:29", "buy")]


@pytest.mark.parametrize("root", PRE_ROOTS)
def test_wasdepre_signal_is_the_1029_close_minus_the_0830_open(root: str) -> None:
    # the 08:30 bar opens at -3 and closes at +10; the 10:29 bar opens at -20 and closes at +5:
    # Dr = 5 - (-3) = +8 (buy); the 08:30 close or the 10:29 open would give a sell
    day = pre_day(WASDE, start_open=-3, entry_close=5, closes={O830: 10},
                  opens={E1029: -20})
    assert feed(pre(root), [day]) == [(WASDE, "10:29", "buy")]
    assert feed(pre(root), [pre_day(WASDE, start_open=2, entry_close=-4)]) == [
        (WASDE, "10:29", "sell")]
    assert feed(pre(root), [pre_day(WASDE, start_open=1, entry_close=2)]) == [
        (WASDE, "10:29", "buy")]
    assert feed(pre(root), [pre_day(WASDE, start_open=-1, entry_close=-2)]) == [
        (WASDE, "10:29", "sell")]


def test_wasdepre_zero_drift_does_not_trade() -> None:
    assert feed(pre("ZC"), [pre_day(WASDE, start_open=4, entry_close=4)]) == []


@pytest.mark.parametrize("missing", [O830, E1029])
def test_wasdepre_a_missing_signal_or_entry_bar_gives_no_trade(missing: int) -> None:
    assert feed(pre("ZS"), [pre_day(WASDE, skip=frozenset({missing}))]) == []


@pytest.mark.parametrize("other", [O830, E1029])
def test_wasdepre_instrument_guard(other: int) -> None:
    assert feed(pre("ZC"), [pre_day(WASDE, ids={other: 778})]) == []
    assert feed(pre("ZC"), [pre_day(WASDE, instrument_id=778)]) == [(WASDE, "10:29", "buy")]


def test_wasdepre_state_resets_each_trade_date() -> None:
    first, second = date(2025, 7, 11), date(2025, 8, 12)  # two WASDE dates
    days = [pre_day(first), pre_day(second, skip=frozenset({O830}))]
    assert feed(pre("ZC"), days) == [(first, "10:29", "buy")]


@pytest.mark.parametrize("root", PRE_ROOTS)
def test_wasdepre_exit_on_the_1114_bar_or_the_first_later_bar(root: str) -> None:
    held = feed(pre(root), [pre_day(NOT_WASDE)], position=1)
    assert held[0] == (NOT_WASDE, "11:14", "sell")
    late = feed(pre(root), [pre_day(NOT_WASDE, skip=frozenset({X1114}))], position=-1)
    assert late[0] == (NOT_WASDE, "11:15", "buy")
    assert feed(pre(root), [pre_day(NOT_WASDE)], position=1, pending=-1) == []
    assert feed(pre(root), [pre_day(WASDE)], pending=1) == []  # an entry already pending


@pytest.mark.parametrize("root", PRE_ROOTS)
def test_wasdepre_engine_fills_and_no_intent_in_the_release_minutes(root: str) -> None:
    res = run(pre(root), [Day(PRIOR), pre_day(WASDE)], releases=release_at(root, WASDE, 11, 0))
    assert fills(res) == trade(WASDE, "10:30", "11:15")
    assert intents(res) == [(WASDE, "10:29", True, None), (WASDE, "11:14", True, None)]
    res = run(pre(root), [Day(PRIOR), pre_day(WASDE, entry_close=-5, skip=frozenset({X1114}))],
              releases=release_at(root, WASDE, 11, 0))
    assert fills(res) == trade(WASDE, "10:30", "11:16", "sell")
    assert not [i for i in intents(res) if i[1] in ("11:00", "11:01")]


# ----------------------------------------------------------------- wasdepost rule ----
def test_wasdepost_trades_a_wasde_date_and_not_another() -> None:
    assert feed(post(), [post_day(WASDE)]) == [(WASDE, "11:14", "buy")]
    for d in (NOT_WASDE, CANCELLED, MOVED_FROM):
        assert feed(post(), [post_day(d)]) == [], d
    assert feed(post(), [post_day(MOVED_TO)]) == [(MOVED_TO, "11:14", "buy")]


def test_wasdepost_a_dropped_wasde_does_not_trade(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_wasde, "DROPPED_WASDE", {WASDE: "synthetic"})
    assert feed(post(), [post_day(WASDE)]) == []
    assert feed(post(), [post_day(MOVED_TO)]) == [(MOVED_TO, "11:14", "buy")]


def test_wasdepost_needs_a_full_grain_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wasdepost, "GRAIN_FULL_SESSIONS", frozenset({MOVED_TO}))
    assert feed(post(), [post_day(WASDE)]) == []
    assert feed(post(), [post_day(MOVED_TO)]) == [(MOVED_TO, "11:14", "buy")]


def test_wasdepost_signal_is_the_1114_close_minus_the_1059_close() -> None:
    # the 10:59 bar opens at +20 and closes at 0; the 11:14 bar opens at -30 and closes at +5:
    # R = 5 - 0 = +5 (buy); the 10:59 open or the 11:14 open would give a sell
    day = post_day(WASDE, signal_close=0, entry_close=5, opens={S1059: 20, E1114: -30})
    assert feed(post(), [day]) == [(WASDE, "11:14", "buy")]
    assert feed(post(), [post_day(WASDE, signal_close=3, entry_close=1)]) == [
        (WASDE, "11:14", "sell")]
    assert feed(post(), [post_day(WASDE, signal_close=-1, entry_close=0)]) == [
        (WASDE, "11:14", "buy")]


def test_wasdepost_zero_response_does_not_trade() -> None:
    assert feed(post(), [post_day(WASDE, signal_close=7, entry_close=7)]) == []


@pytest.mark.parametrize("missing", [S1059, E1114])
def test_wasdepost_a_missing_signal_or_entry_bar_gives_no_trade(missing: int) -> None:
    assert feed(post(), [post_day(WASDE, skip=frozenset({missing}))]) == []


@pytest.mark.parametrize("other", [S1059, E1114])
def test_wasdepost_instrument_guard(other: int) -> None:
    assert feed(post(), [post_day(WASDE, ids={other: 778})]) == []
    assert feed(post(), [post_day(WASDE, instrument_id=778)]) == [(WASDE, "11:14", "buy")]


def test_wasdepost_state_resets_each_trade_date() -> None:
    first, second = date(2025, 7, 11), date(2025, 8, 12)
    days = [post_day(first), post_day(second, skip=frozenset({S1059}))]
    assert feed(post(), days) == [(first, "11:14", "buy")]


def test_wasdepost_exit_on_the_first_bar_at_or_after_1313() -> None:
    held = feed(post(), [post_day(NOT_WASDE)], position=1)
    assert held[0] == (NOT_WASDE, "13:13", "sell")
    late = feed(post(), [post_day(NOT_WASDE, skip=frozenset({X1313}))], position=-1)
    assert late[0] == (NOT_WASDE, "13:14", "buy")
    assert feed(post(), [post_day(NOT_WASDE)], position=-1, pending=1) == []
    assert feed(post(), [post_day(WASDE)], pending=1) == []


def test_wasdepost_engine_fills_and_no_intent_in_the_release_minutes() -> None:
    res = run(post(), [Day(PRIOR), post_day(WASDE)], releases=release_at("ZC", WASDE, 11, 0))
    assert fills(res) == trade(WASDE, "11:15", "13:14")
    assert intents(res) == [(WASDE, "11:14", True, None), (WASDE, "13:13", True, None)]
    assert not [i for i in intents(res) if i[1] in ("11:00", "11:01")]
    res = run(post(), [Day(PRIOR), post_day(WASDE, entry_close=-5, skip=frozenset({X1313}))],
              releases=release_at("ZC", WASDE, 11, 0))
    assert fills(res) == trade(WASDE, "11:15", "13:15", "sell")
