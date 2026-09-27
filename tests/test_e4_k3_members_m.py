"""Stage E.4 Part 3, K3-mehedge-01 on 6J (MemberCoder-A): the event set, the clock in both regimes
and the member through the real engine on synthetic bars (reports/stage_e4c_member_specs.md
section 6 and section 11; K3-L-06, K3-L-07; catalog reports/stage_e0_catalog_K3.md lines
555-647). The signal table's pin is tests/test_e4_k3_members_m_signal.py.

Expected event dates and T_L are recomputed here from independent sources: EC-CAL FX
(data.group_session), the release check's England-and-Wales holidays and zoneinfo for the 16:00
London fix, never from the member's own tables. The synthetic kit is
tests/test_e4_k3_members_a.py's.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from functools import cache
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from data.group_session import load_group_calendar
from rules.sessions import flatten_time_ct
from screening.stage_e_freeze import (
    MemberDecl,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from strategy.members.k3 import mehedge
from strategy.members.k3._calendar import MONTH_ENDS
from strategy.members.k3._mehedge_signal import MEHEDGE_R_EQ_6J
from strategy.stage_e.interface import LegSpec, StageEMember, TradingInterval
from tests.test_e4_k3_members_a import (
    Day,
    Fill,
    account_of,
    bar_at,
    blackout_rules,
    fills,
    forced_limit_rules,
    hm,
    intents,
    release_at,
    run,
    trade,
    view_of,
)

REPO = Path(__file__).resolve().parents[1]
CT = ZoneInfo("America/Chicago")
LONDON = ZoneInfo("Europe/London")
R_EQ = {month: (me, r) for month, me, r in MEHEDGE_R_EQ_6J}

# month-ends used below, with the sign of their R_eq (checked against the table in a test)
SELL_CDT = date(2025, 9, 30)  # R_eq > 0; T_L 10:00 CT (BST / CDT)
SELL_MISMATCH_OCT = date(2025, 10, 31)  # R_eq > 0; London on GMT since 10-26, US on CDT: 11:00
SELL_MISMATCH_MAR = date(2024, 3, 28)  # R_eq > 0; US on CDT since 03-10, London on GMT: 11:00
SELL_CST = date(2026, 1, 30)  # R_eq > 0; T_L 10:00 CT (GMT / CST)
BUY_CST = date(2025, 2, 28)  # R_eq < 0; T_L 10:00 CT
BUY_CDT = date(2026, 3, 31)  # R_eq < 0; London on BST since 03-29: T_L 10:00 CT
HALTED_ME = date(2025, 11, 28)  # EC-CAL FX early halt 13:45 (R_eq < 0)
EW_ME = date(2020, 8, 31)  # England-and-Wales summer bank holiday, a full FX session
EW_AND_HALT_ME = date(2021, 5, 31)  # E&W spring bank holiday and an EC-CAL FX early halt


@cache
def release_check() -> dict:
    return json.loads((REPO / "reports" / "stage_e4c_release_check.json").read_text("utf-8"))


def london_fix_ct(day: date) -> str:
    """T_L: 16:00 Europe/London on ``day`` in CT (C9's rule), by zoneinfo."""
    fix = datetime.combine(day, time(16, 0), tzinfo=LONDON).astimezone(UTC).astimezone(CT)
    assert fix.date() == day
    return f"{fix:%H:%M}"


def times(day: date) -> tuple[str, str, str, str]:
    """(entry decision bar, entry fill, exit bar, exit fill) = T_L - 61, -60, -4, -3."""
    hh, mm = (int(x) for x in london_fix_ct(day).split(":"))
    t_l = hh * 60 + mm
    return tuple(f"{m // 60:02d}:{m % 60:02d}" for m in (t_l - 61, t_l - 60, t_l - 4, t_l - 3))


def side_of(day: date) -> str:
    return "sell" if R_EQ[f"{day:%Y-%m}"][1] > 0 else "buy"


def hedge_run(day: date, **kw: object) -> tuple[list, list]:
    res = run(mehedge.make_6j(), [Day(day, **kw)])
    return fills(res), intents(res)


# ----------------------------------------------------------------- declarations ----
def test_mehedge_passes_the_freeze_static_check() -> None:
    rel = "strategy/members/k3/mehedge.py"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K3") == []


def test_only_6j_is_traded_and_declared() -> None:
    member = mehedge.make_6j()
    assert isinstance(member, StageEMember)
    assert member.name == "K3-mehedge-01 6J"  # S0.2
    assert member.root == "6J" and member.legs == (LegSpec("6J", True),)  # the index is no leg
    assert mehedge.make_6j() is not member
    for other in ("make_6e", "make_e7", "make_m6e", "make_6a", "make_6s"):  # 6E not traded
        assert not hasattr(mehedge, other)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    assert mehedge.make_6j().trading_windows == {"6J": (
        TradingInterval(time(8, 59), time(9, 58)), TradingInterval(time(9, 59), time(10, 58)))}


def test_the_declaration_freezes_under_tmp_path_with_ordinal_27(tmp_path: Path) -> None:
    """Specs S0.2 and section 11: with 6E not declared, the ordinals close up and mehedge 6J is
    27. The member and the modules it imports are copied under tmp_path (never the repository's
    write-once freeze)."""
    src, dst = REPO / "strategy" / "members" / "k3", tmp_path / "strategy" / "members" / "k3"
    dst.mkdir(parents=True)
    (dst.parent / "__init__.py").write_bytes(b"")
    (dst / "__init__.py").write_bytes(b"")
    for name in ("mehedge.py", "_mehedge_signal.py", "_port_common.py", "_calendar.py",
                 "_clocks.py"):
        shutil.copyfile(src / name, dst / name)
    decl = MemberDecl("K3-mehedge-01 6J", 27, "strategy.members.k3.mehedge", "make_6j",
                      (LegSpec("6J", True),))
    write_cluster_freeze("K3", [decl], tmp_path)
    freeze = load_cluster_freeze("K3", tmp_path)
    verify_cluster_code(freeze)
    assert [(m.label, m.ordinal) for m in freeze.members] == [("K3-mehedge-01 6J", 27)]


# --------------------------------------------------------------------- the rule ----
@pytest.mark.parametrize(("r_eq", "side"), [
    (0.0421, "sell"), (1e-12, "sell"), (-0.0092, "buy"), (-1e-12, "buy"), (0.0, None),
    (-0.0, None), (None, None)])
def test_hedge_side(r_eq: float | None, side: str | None) -> None:
    assert mehedge.hedge_side(r_eq) == side


def test_the_signal_rows_name_the_same_month_ends_as_month_ends() -> None:
    assert [(m, me) for m, me, _ in MEHEDGE_R_EQ_6J] == [(m, me) for m, me in MONTH_ENDS]


def test_the_event_set_is_recomputed_from_ec_cal_and_ec_ew() -> None:
    """ME(m) traded iff EC-CAL FX marks no early halt on it, the engine's F is the regular 15:08
    (K3-L-11) and it is no E&W bank holiday; every R_eq is non-zero, so the sides follow the
    table's signs."""
    cal = load_group_calendar("fx")
    ew = {date.fromisoformat(h["date"]) for h in release_check()["ec_ew"]}
    expected = {}
    for _month, me_text, r_eq in MEHEDGE_R_EQ_6J:
        me = date.fromisoformat(me_text)
        regular_f = flatten_time_ct("6J", me) == time(15, 8)
        if cal.early_halt_ct(me) is None and regular_f and me not in ew:
            expected[me] = "sell" if r_eq > 0 else "buy"
    assert dict(mehedge.event_sides()) == expected
    dropped = sorted(date.fromisoformat(me) for _, me, _ in MEHEDGE_R_EQ_6J
                     if date.fromisoformat(me) not in expected)
    assert HALTED_ME in dropped and EW_ME in dropped and EW_AND_HALT_ME in dropped
    assert len(expected) + len(dropped) == 85


def test_the_clock_is_the_16_00_london_fix_in_ct_on_every_traded_month_end() -> None:
    for day in mehedge.event_sides():
        entry, _, exit_, _ = times(day)
        assert mehedge.fix_minutes(day) == (time.fromisoformat(entry), time.fromisoformat(exit_))
    assert london_fix_ct(SELL_MISMATCH_OCT) == london_fix_ct(SELL_MISMATCH_MAR) == "11:00"
    assert london_fix_ct(SELL_CDT) == london_fix_ct(SELL_CST) == london_fix_ct(BUY_CDT) == "10:00"


def test_the_named_month_ends_have_the_signs_this_file_uses() -> None:
    for day in (SELL_CDT, SELL_MISMATCH_OCT, SELL_MISMATCH_MAR, SELL_CST):
        assert side_of(day) == "sell" and mehedge.event_sides()[day] == "sell"
    for day in (BUY_CST, BUY_CDT):
        assert side_of(day) == "buy" and mehedge.event_sides()[day] == "buy"
    assert R_EQ["2025-11"][1] < 0 and R_EQ["2020-08"][1] > 0 and R_EQ["2021-05"][1] > 0


# ----------------------------------------------------------- through the engine ----
@pytest.mark.parametrize("day", [SELL_CDT, SELL_MISMATCH_OCT, SELL_MISMATCH_MAR, SELL_CST,
                                 BUY_CST, BUY_CDT], ids=str)
def test_entry_at_t_l_minus_61_and_exit_at_t_l_minus_4_in_both_regimes(day: date) -> None:
    entry, entry_fill, exit_, exit_fill = times(day)
    got_fills, got_intents = hedge_run(day)
    assert got_fills == trade(day, entry_fill, exit_fill, side_of(day))
    assert got_intents == [(day, entry, True, None), (day, exit_, True, None)]


def test_the_literal_times_standard_and_mismatch() -> None:
    assert times(SELL_CDT) == ("08:59", "09:00", "09:56", "09:57")
    assert times(SELL_MISMATCH_OCT) == ("09:59", "10:00", "10:56", "10:57")
    res = run(mehedge.make_6j(), [Day(SELL_MISMATCH_OCT)])
    assert fills(res) == trade(SELL_MISMATCH_OCT, "10:00", "10:57", "sell")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1


def test_a_day_that_is_not_a_month_end_is_not_traded() -> None:
    for day in (date(2025, 9, 29), date(2025, 10, 1), date(2025, 10, 30)):
        assert hedge_run(day) == ([], [])


def test_a_halted_month_end_is_not_traded() -> None:
    # 2025-11-28: EC-CAL FX early halt 13:45 (Topstep F 11:45); the engine would accept a 08:59
    # entry, so the member's FX_FULL_SESSIONS test is what drops the month (K3-L-04, K3-L-06)
    assert hedge_run(HALTED_ME, halt="13:45") == ([], [])
    assert hedge_run(HALTED_ME) == ([], [])  # the table, not the bar's label, decides


@pytest.mark.parametrize("day", [EW_ME, EW_AND_HALT_ME], ids=str)
def test_an_england_and_wales_bank_holiday_month_end_is_not_traded(day: date) -> None:
    assert hedge_run(day) == ([], [])
    # the month before, a normal month-end with the same clock, trades
    assert hedge_run(date(2020, 7, 31))[0] == trade(date(2020, 7, 31), "09:00", "09:57",
                                                    side_of(date(2020, 7, 31)))


@pytest.mark.parametrize("value", [None, 0.0, -0.0])
def test_a_missing_close_or_a_zero_r_eq_is_no_trade(monkeypatch: pytest.MonkeyPatch,
                                                    value: float | None) -> None:
    rows = tuple((m, me, value if m == "2025-09" else r) for m, me, r in MEHEDGE_R_EQ_6J)
    monkeypatch.setattr(mehedge, "MEHEDGE_R_EQ_6J", rows)
    assert SELL_CDT not in mehedge.event_sides()
    assert hedge_run(SELL_CDT) == ([], [])
    assert hedge_run(SELL_MISMATCH_OCT)[0] == trade(SELL_MISMATCH_OCT, "10:00", "10:57", "sell")


def test_a_signal_row_for_another_date_is_no_trade(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = tuple((m, "2025-09-29" if m == "2025-09" else me, r) for m, me, r in MEHEDGE_R_EQ_6J)
    monkeypatch.setattr(mehedge, "MEHEDGE_R_EQ_6J", rows)
    assert hedge_run(SELL_CDT) == ([], [])


def test_the_missing_t_l_minus_61_bar_is_no_trade() -> None:
    # no entry on the 09:00 bar or later: the entry names the 08:59 bar only (E.3-L-04)
    assert hedge_run(SELL_CDT, skip=frozenset({hm(8, 59)})) == ([], [])
    assert hedge_run(SELL_MISMATCH_OCT, skip=frozenset({hm(9, 59)})) == ([], [])


def test_the_missing_t_l_minus_4_bar_moves_the_exit_to_the_next_present_bar() -> None:
    got_fills, got_intents = hedge_run(SELL_CDT, skip=frozenset({hm(9, 56)}))
    assert got_fills == trade(SELL_CDT, "09:00", "09:58", "sell")
    assert got_intents[-1] == (SELL_CDT, "09:57", True, None)


def test_a_refused_exit_is_resent() -> None:
    # no bars 09:00..09:55: the entry fills at the 09:56 open and the 09:56 exit is refused
    # (engine_min_hold, D9.3b); it is sent again on 09:57 and fills at 09:58
    got_fills, got_intents = hedge_run(SELL_CDT, skip=frozenset(range(hm(9, 0), hm(9, 56))))
    assert got_intents == [(SELL_CDT, "08:59", True, None),
                           (SELL_CDT, "09:56", False, "engine_min_hold"),
                           (SELL_CDT, "09:57", True, None)]
    assert got_fills == trade(SELL_CDT, "09:56", "09:58", "sell")


def test_the_exit_is_sent_whatever_the_exit_bars_instrument_id() -> None:
    # K3-L-03: the exit must close the position. The engine itself refuses a position that
    # spans a contract change (EngineInvariantError), so this is a direct call: the member, short
    # one lot after its 08:59 entry, sends the exit on a 09:56 bar of another instrument_id
    member = mehedge.make_6j()
    entry = bar_at("6J", SELL_CDT, hm(8, 59))
    (intent,) = member.on_minute(view_of("6J", entry.ts_event_ns, entry), account_of("6J"))
    assert (intent.side, intent.quantity) == ("sell", 1)
    exit_bar = bar_at("6J", SELL_CDT, hm(9, 56), instrument_id=778)
    (out,) = member.on_minute(view_of("6J", exit_bar.ts_event_ns, exit_bar), account_of("6J", -1))
    assert (out.side, out.quantity) == ("buy", 1)


def test_the_d95a_guard_moves_a_fill_and_a_release_beside_it_does_not() -> None:
    # a 09:00 CT US release (C line 626) at the entry fill: the fill waits to 09:02
    res = run(mehedge.make_6j(), [Day(SELL_CDT)], releases=release_at("6J", SELL_CDT, 9, 0))
    assert fills(res) == trade(SELL_CDT, "09:02", "09:57", "sell")
    for hh, mm in ((8, 58), (9, 1)):  # guards [08:58, 09:00) and [09:01, 09:03)
        beside = run(mehedge.make_6j(), [Day(SELL_CDT)],
                     releases=release_at("6J", SELL_CDT, hh, mm))
        assert fills(beside) == trade(SELL_CDT, "09:00", "09:57", "sell")


def test_a_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    got_fills, got_intents = hedge_run(SELL_CDT, flatten_from=hm(9, 30))
    assert got_fills == trade(SELL_CDT, "09:00", "09:31", "sell", exit_reason="forced_flatten")
    assert [i[1] for i in got_intents] == ["08:59"]


def test_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [Day(BUY_CST)]
    member = mehedge.make_6j()
    res = run(member, days, rules=forced_limit_rules(member, days, [(BUY_CST, hm(9, 30))]))
    assert fills(res) == trade(BUY_CST, "09:00", "09:31", "buy", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:59"]


def test_a_roll_blackout_month_end_refuses_the_entry_and_nothing_is_resent() -> None:
    days: Sequence[Day] = [Day(SELL_CDT)]
    member = mehedge.make_6j()
    res = run(member, days, rules=blackout_rules(member, days, [SELL_CDT]))
    assert intents(res) == [(SELL_CDT, "08:59", False, "engine_roll_blackout")]
    assert fills(res) == []


def test_consecutive_month_ends_each_trade_once() -> None:
    res = run(mehedge.make_6j(), [Day(SELL_CDT), Day(date(2025, 10, 1)), Day(SELL_MISMATCH_OCT)])
    assert fills(res) == (trade(SELL_CDT, "09:00", "09:57", "sell")
                          + trade(SELL_MISMATCH_OCT, "10:00", "10:57", "sell"))
