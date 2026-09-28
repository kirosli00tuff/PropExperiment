"""Stage E.7 K1 ports of MemberCoder-A, part 3: K1-cp3-01 on MNQ, M2K and MYM
(reports/stage_e7_member_specs.md section 3; readings E.3-L-09, E.3-L-10, E.3-L-11, K4-L-05,
K7-L-01).

Synthetic bars only, built with tests/test_k1_members_ports.py's kit and run through the real
Stage E engine, plus direct calls of ``clv_side`` and of the member where the equity calendar
never produces the case. No bar file is read.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from data.group_session import load_group_calendar
from strategy.members.k1 import cp3
from tests.test_k1_members_ports import (
    FRI,
    FRI_JUL,
    FRI_MD,
    GOOD_FRIDAY,
    HOLIDAY_MD,
    MON,
    MON_GF,
    MON_JUL,
    Q_C,
    ROOTS,
    THU_GF,
    THU_JUL,
    THU_MD,
    TUE,
    TUE_MD,
    WED,
    WED_JUL,
    WED_MD,
    Day,
    Ticks,
    account_of,
    bar_at,
    feed,
    fill_qty,
    fills,
    forced_limit_rules,
    halt_label,
    hm,
    intents,
    make,
    price,
    release_at,
    run,
    trade,
    view_of,
)

TUE_JUL = date(2025, 7, 8)
WIDE = (0, 30, -30, 0)  # would move a daily bar's range to B-30..B+30 if it were read


def daily(high: int, low: int, close: int, **kw: Ticks) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (14:59 close) = B+close, plus two
    extreme bars just OUTSIDE [08:30, 15:00), at 08:29 and 15:00, that must not enter it."""
    return {hm(8, 29): (0, 50, -50, 0), hm(15, 0): (0, 50, -50, 0),
            hm(10, 0): (0, high, 0, 0), hm(11, 0): (0, 0, low, 0),
            hm(14, 59): (0, max(0, close), min(0, close), close), **kw}


BUY_08 = daily(10, 0, 8)  # CLV = 8/10 = 0.8 exactly
SELL_02 = daily(10, 0, 2)  # CLV = 2/10 = 0.2 exactly


def m(root: str = "MNQ") -> cp3.Cp3CloseLocation:
    return make(cp3, root)


def test_cp3_literals_are_the_clv_cuts_and_the_clock() -> None:
    cuts = (cp3.CLV_BUY_AT_OR_ABOVE, cp3.CLV_SELL_AT_OR_BELOW)
    assert (Decimal("0.8"), Decimal("0.2")) == cuts
    assert (cp3.CLOSE_BEFORE_C_MIN, cp3.EXIT_BEFORE_C_MIN) == (1, 2)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459(root: str) -> None:
    res = run(m(root), [Day(MON, BUY_08), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, "08:30", True, None), (TUE, "14:58", True, None)]
    assert fill_qty(res) == [Q_C[root], Q_C[root]]  # q_c (S0.3); the exit closes it all


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_prior_clv_at_02_sells(root: str) -> None:
    res = run(m(root), [Day(MON, SELL_02), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "sell")
    assert fill_qty(res) == [Q_C[root], Q_C[root]]


def test_cp3_the_cuts_are_exact_where_a_float_clv_misses_them() -> None:
    # M2K (tick 0.10): L 2000.0, H 2001.0, C 2000.8 gives a float CLV of 0.79999..., and C 2000.2
    # one of 0.20000...; in integer ticks they are 8/10 and 2/10, on the cuts (S0.10, K4-L-05)
    lo, hi = price("M2K", 0), price("M2K", 10)
    assert (price("M2K", 8) - lo) / (hi - lo) < 0.8
    assert (price("M2K", 2) - lo) / (hi - lo) > 0.2
    assert fills(run(m("M2K"), [Day(MON, BUY_08), Day(TUE)])) == trade(TUE, "08:31", "14:59")
    assert fills(run(m("M2K"), [Day(MON, SELL_02), Day(TUE)])) == trade(TUE, "08:31", "14:59",
                                                                        "sell")


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(root: str, close: int) -> None:
    assert intents(run(m(root), [Day(MON, daily(10, 0, close)), Day(TUE)])) == []


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize(("close", "side"), [(10, "buy"), (9, "buy"), (1, "sell"), (0, "sell")])
def test_cp3_clv_beyond_the_cuts_trades(root: str, close: int, side: str) -> None:
    res = run(m(root), [Day(MON, daily(10, 0, close)), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", side)


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None), (-1, 0, None),
    # one part in 100 and in 1000 inside each cut: no trade (the cuts are 0.8 and 0.2 exactly)
    (100, 80, "buy"), (100, 79, None), (1000, 799, None), (100, 20, "sell"), (100, 21, None),
    (1000, 201, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


@pytest.mark.parametrize(("close", "side"), [(6, "buy"), (-6, "sell")])
def test_cp3_the_daily_low_is_the_min_low(close: int, side: str) -> None:
    # H = B+10, L = B-10 (the 11:00 bar): CLV = 16/20 = 0.8 buys, 4/20 = 0.2 sells
    res = run(m("MYM"), [Day(MON, daily(10, -10, close)), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", side)


def test_cp3_day_accumulators_reset_each_trade_date() -> None:
    # MON's B-30..B+30 range (CLV 0.5) must not carry into TUE's daily bar (CLV 0.8)
    res = run(m("M2K"), [Day(MON, daily(30, -30, 0)), Day(TUE, BUY_08), Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_zero_range_is_no_trade(root: str) -> None:
    flat = {hm(8, 29): (0, 50, -50, 0)}  # the only non-flat bar is outside [08:30, 15:00)
    assert intents(run(m(root), [Day(MON, flat), Day(TUE)])) == []


def test_cp3_warm_up_no_complete_earlier_bar_is_no_trade() -> None:
    assert intents(run(m("MNQ"), [Day(MON, BUY_08)])) == []
    mon = Day(MON, BUY_08, skip=frozenset({hm(14, 59)}))  # incomplete: no d-1 for TUE
    assert intents(run(m("MNQ"), [mon, Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(m("MYM"), [Day(MON, BUY_08), Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy") + trade(WED, "08:31", "14:59",
                                                                     "sell")


def test_cp3_d_minus_1_is_the_most_recent_complete_day() -> None:
    # TUE lacks its 14:59 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade".
    # TUE's range B..B+30 is wide, so a day that kept MON's 14:59 close (B+8) would give TUE a
    # CLV of 8/30 and WED no trade
    tue = Day(TUE, daily(30, 0, 2), skip=frozenset({hm(14, 59)}))
    res = run(m("M2K"), [Day(MON, BUY_08), tue, Day(WED)])
    # TUE's exit, decided on 14:58, fills at the next present bar (15:00)
    assert fills(res) == trade(TUE, "08:31", "15:00", "buy") + trade(WED, "08:31", "14:59",
                                                                     "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(9, 0): 778})  # one bar in [08:30, 15:00) differs
    res = run(m("MNQ"), [mon, Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "sell")  # TUE: no complete d-1 yet


def test_cp3_other_ids_outside_the_daily_window_do_not_make_it_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(8, 29): 778, hm(15, 0): 778})
    res = run(m("MYM"), [mon, Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy")


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar(root: str) -> None:
    tue = Day(TUE, BUY_08, instrument_id=778)
    res = run(m(root), [Day(MON, BUY_08), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")  # TUE refused by the guard
    # only the 08:30 bar is compared: the evening's and the 08:29 bar's ids do not matter (a
    # later bar cannot differ while a position is held: the engine refuses a contract splice)
    tue_late = Day(TUE, ids={hm(8, 29): 778}, evening_id=778)
    res_late = run(m(root), [Day(MON, BUY_08), tue_late])
    assert fills(res_late) == trade(TUE, "08:31", "14:59", "buy")


def test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete() -> None:
    tue = Day(TUE, SELL_02, skip=frozenset({hm(8, 30)}))
    res = run(m("M2K"), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")  # WED's d-1 is MON


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_early_halt_day_is_not_traded_and_is_incomplete(root: str) -> None:
    # Memorial Day 2025-05-26 (early halt 12:00, F 11:30): bars kept to 15:12 so it would be
    # complete but for its halt; the engine would accept an 08:30 entry, so the member's own
    # test is what blocks it. Tuesday 05-27's d-1 is Friday 05-23 (buy), not the holiday (sell)
    label = halt_label(HOLIDAY_MD)
    days = [Day(FRI_MD, BUY_08), Day(HOLIDAY_MD, SELL_02, halt=label),
            Day(TUE_MD, evening_halt=label)]
    res = run(m(root), days)
    assert [i for i in intents(res) if i[0] == HOLIDAY_MD] == []
    assert fills(res) == trade(TUE_MD, "08:31", "14:59", "buy")


def test_cp3_a_halt_day_with_a_buy_prior_is_still_not_traded() -> None:
    # the halt excludes day d itself (E.3-L-09, E.3-L-11): Friday's buy is not traded on 05-26
    label = halt_label(HOLIDAY_MD)
    res = run(m("MNQ"), [Day(FRI_MD, BUY_08), Day(HOLIDAY_MD, halt=label, end=hm(12, 0))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_the_tuesday_after_memorial_day_reads_friday(root: str) -> None:
    # the holiday as the bars are: they end at the 12:00 halt (no 14:59 bar) and carry "12:00";
    # Friday 05-23 sells, the holiday's bars would buy if the holiday were read as d-1
    label = halt_label(HOLIDAY_MD)
    holiday = Day(HOLIDAY_MD, {hm(9, 0): (0, 10, 0, 0), hm(11, 59): (0, 8, 0, 8)}, halt=label,
                  end=hm(12, 0))
    res = run(m(root), [Day(FRI_MD, SELL_02), holiday, Day(TUE_MD, evening_halt=label)])
    assert fills(res) == trade(TUE_MD, "08:31", "14:59", "sell")


def test_cp3_the_tuesday_after_memorial_day_is_not_a_halt_day() -> None:
    # Tuesday 05-27's first bars (Monday 05-26 from 17:00 CT) carry the holiday's "12:00" label;
    # they are bars of CT date d-1, so Tuesday is traded and is a complete d-1 for Wednesday
    label = halt_label(HOLIDAY_MD)
    days = [Day(THU_MD, SELL_02), Day(FRI_MD, BUY_08), Day(HOLIDAY_MD, halt=label, end=hm(12, 0)),
            Day(TUE_MD, SELL_02, evening_halt=label), Day(WED_MD)]
    res = run(m("MYM"), days)
    assert fills(res) == (trade(FRI_MD, "08:31", "14:59", "sell")
                          + trade(TUE_MD, "08:31", "14:59", "buy")
                          + trade(WED_MD, "08:31", "14:59", "sell"))


def test_cp3_two_early_halt_dates_in_a_row_are_both_skipped() -> None:
    # 07-03 (halt 12:15) and 07-04 (halt 12:00), bars kept to 15:12 with opposite CLVs:
    # Monday 07-07 reads Wednesday 07-02 (sell); Tuesday 07-08 reads Monday (buy), so the halt
    # flag does not carry past the halt days
    assert load_group_calendar("equity").early_halt_ct(TUE_JUL) is None
    days = [Day(WED_JUL, SELL_02), Day(THU_JUL, BUY_08, halt=halt_label(THU_JUL)),
            Day(FRI_JUL, BUY_08, halt=halt_label(FRI_JUL)), Day(MON_JUL, BUY_08), Day(TUE_JUL)]
    res = run(m("M2K"), days)
    assert fills(res) == trade(MON_JUL, "08:31", "14:59", "sell") + trade(
        TUE_JUL, "08:31", "14:59", "buy")


def test_cp3_after_good_friday_monday_reads_thursday() -> None:
    # 2025-04-18 is closed (no trade date, no bars): Monday 04-21's d-1 is Thursday 04-17
    assert not load_group_calendar("equity").is_trade_date(GOOD_FRIDAY)
    res = run(m("MNQ"), [Day(THU_GF, BUY_08), Day(MON_GF)])
    assert fills(res) == trade(MON_GF, "08:31", "14:59", "buy")


def test_cp3_monday_uses_fridays_bar_and_no_sunday_evening_bar() -> None:
    # Monday opens Sunday 17:00: WIDE Sunday bars must not enter Monday's daily bar (Monday's
    # CLV 0.2 would become 32/60 and Tuesday would not trade)
    mon = Day(MON, SELL_02, evening={hm(17, 0): WIDE, hm(17, 1): WIDE})
    res = run(m("MYM"), [Day(FRI, BUY_08), mon, Day(TUE)])
    assert fills(res) == trade(MON, "08:31", "14:59", "buy") + trade(TUE, "08:31", "14:59",
                                                                     "sell")


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_missing_1458_bar_sends_the_exit_on_1459(root: str) -> None:
    res = run(m(root), [Day(MON, BUY_08), Day(TUE, skip=frozenset({hm(14, 58)}))])
    assert fills(res) == trade(TUE, "08:31", "15:00")
    assert intents(res)[-1] == (TUE, "14:59", True, None)


def test_cp3_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    res = run(m("MNQ"), [Day(MON, BUY_08), Day(TUE)], releases=release_at("MNQ", TUE, 8, 31))
    assert fills(res) == trade(TUE, "08:33", "14:59")


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(m("M2K"), [Day(MON, BUY_08), Day(TUE, flatten_from=hm(14, 0))])
    assert fills(res) == trade(TUE, "08:31", "14:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:30"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [Day(MON, BUY_08), Day(TUE)]
    member = m(root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 30))]))
    assert fills(res) == trade(TUE, "08:31", "09:31", exit_reason="price_limit_exit")
    assert [i[:2] for i in intents(res)] == [(TUE, "08:30")]


def test_cp3_daily_bar_and_entry_bar_are_bars_of_ct_date_d() -> None:
    # direct calls with bars the equity calendar never produces: bars of CT date d-1 at 08:30,
    # 11:00 and 14:59 carrying trade date d are not part of d's daily bar and not its entry bar
    prev = TUE - timedelta(days=1)
    member = m("MYM")
    mon = [bar_at("MYM", MON, x, BUY_08.get(x, (0, 0, 0, 0))) for x in
           (hm(8, 30), hm(10, 0), hm(11, 0), hm(14, 59))]
    assert feed(member, mon) == []  # MON: complete, CLV 0.8
    wrong = [bar_at("MYM", prev, x, (0, 50, -50, 0), trade_day=TUE) for x in (hm(8, 30),)]
    assert feed(member, wrong) == []  # not TUE's 08:30 bar: no entry, entry unused
    (intent,) = feed(member, [bar_at("MYM", TUE, hm(8, 30))])
    assert (intent.side, intent.quantity) == ("buy", 3)
    # a WIDE bar of CT date d-1 carrying TUE's trade date does not enter TUE's daily bar: TUE
    # closes at its 14:59 bar on B+2 in a B..B+10 range, a sell for WED
    member2 = m("MYM")
    tue = [bar_at("MYM", TUE, x, SELL_02.get(x, (0, 0, 0, 0))) for x in
           (hm(8, 30), hm(10, 0), hm(11, 0), hm(14, 59))]
    feed(member2, [*tue[:2], bar_at("MYM", prev, hm(12, 0), WIDE, trade_day=TUE), *tue[2:]])
    (intent,) = feed(member2, [bar_at("MYM", WED, hm(8, 30))])
    assert intent.side == "sell"


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending(root: str) -> None:
    def primed() -> cp3.Cp3CloseLocation:
        member = m(root)  # MON's complete daily bar, CLV 0.8, by direct calls
        bars = [bar_at(root, MON, x, p) for x, p in
                sorted({hm(8, 30): (0, 0, 0, 0), **BUY_08}.items())]
        assert feed(member, bars) == []
        return member

    entry = bar_at(root, TUE, hm(8, 30))
    view = view_of(root, entry.ts_event_ns, entry)
    member = primed()
    (intent,) = member.on_minute(view, account_of(root))
    assert (intent.side, intent.quantity) == ("buy", Q_C[root])
    assert member.on_minute(view, account_of(root)) == ()  # S0.6: once per trade date
    assert primed().on_minute(view, account_of(root, 0, Q_C[root])) == ()  # never while pending
