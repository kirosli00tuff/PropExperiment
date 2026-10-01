"""Stage E.8 K6 ports of MemberCoder-A, part 3: K6-cp3-01 on ZC, ZW, ZS, ZM, ZL, HE and LE
(reports/stage_e8_member_specs.md section 3; readings E.3-L-09, E.3-L-10, E.3-L-11, K4-L-05,
K7-L-01, K6-L-18). The engine-level D9.7 case (a grain root entered, then the price beyond the
stop level: the engine's forced exit, and nothing more from the member that day) is
test_cp3_d97_real_stop_level_engine_exit_then_nothing_more.

Synthetic bars only, built with tests/test_k6_members_ports.py's kit and run through the real
Stage E engine, plus direct calls where the calendars never produce the case. No bar file is read.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from decimal import Decimal
from typing import Any

import pytest

from strategy.members.k6 import cp3
from strategy.members.k6.cp3 import DailyBar, clv_side
from tests.test_k6_members_ports import (
    CLOSE_BAR,
    EXIT,
    EXIT_FILL,
    FRI,
    FRI_MD,
    GRAIN_ROOTS,
    HALT_TG,
    HALT_XMAS,
    LATE_XMAS,
    LIVESTOCK_ROOTS,
    MON,
    MON_TG,
    ROOTS,
    TUE,
    TUE_MD,
    TUE_XMAS,
    WED,
    WED_TG,
    Day,
    Ticks,
    account_of,
    bar_at,
    feed,
    fill_qty,
    fills,
    grp,
    halt_label,
    hm,
    intents,
    is_grain,
    make,
    price,
    run,
    stop_offsets,
    trade,
    view_of,
)


def m(root: str = "ZC") -> cp3.Cp3CloseLocation:
    return make(cp3, root)


def prior(day: date, root: str, close: int, high: int = 10, low: int = 0, **kw: Any) -> Day:
    """A complete day: H = B+high (the 09:00 bar), L = B+low (the 10:00 bar), C_d = B+close
    (the C-1 bar: grains 13:14, livestock 12:59); every other bar at B."""
    paths: dict[int, Ticks] = {hm(9, 0): (0, high, 0, 0), hm(10, 0): (0, 0, low, 0),
                               CLOSE_BAR[grp(root)]: (0, max(close, 0), min(close, 0), close)}
    paths.update(kw.pop("paths", {}))
    return Day(day, paths=paths, **kw)


def cp3_trade(root: str, day: date = TUE, side: str = "buy") -> list[tuple]:
    return trade(day, "08:31", EXIT_FILL[grp(root)], side)


def test_cp3_literals_are_the_clv_cuts_and_the_clock() -> None:
    cuts = (Decimal("0.8"), Decimal("0.2"))
    assert cuts == (cp3.CLV_BUY_AT_OR_ABOVE, cp3.CLV_SELL_AT_OR_BELOW)
    assert (cp3.CLOSE_BEFORE_C_MIN, cp3.EXIT_BEFORE_C_MIN) == (1, 2)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2(root: str) -> None:
    res = run(m(root), [prior(MON, root, 8), Day(TUE)])
    assert fills(res) == cp3_trade(root)  # fills 08:31, exit 13:14 (grains) / 12:59
    g = grp(root)
    assert intents(res) == [(TUE, "08:30", True, None), (TUE, EXIT[g], True, None)]
    assert fill_qty(res) == [1, 1]


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_prior_clv_at_02_sells(root: str) -> None:
    res = run(m(root), [prior(MON, root, 2), Day(TUE)])
    assert fills(res) == cp3_trade(root, side="sell")


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(root: str, close: int) -> None:
    assert intents(run(m(root), [prior(MON, root, close), Day(TUE)])) == []


@pytest.mark.parametrize("root", ("ZS", "HE"))
@pytest.mark.parametrize(("close", "side"), [(9, "buy"), (1, "sell"), (0, "sell")])
def test_cp3_clv_beyond_the_cuts_trades(root: str, close: int, side: str) -> None:
    assert fills(run(m(root), [prior(MON, root, close), Day(TUE)])) == cp3_trade(root, side=side)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_a_limit_close_clv_1_buys(root: str) -> None:
    # d-1 closes at its high (CLV 1, e.g. a close locked at the limit): buy
    res = run(m(root), [prior(MON, root, 10, paths={hm(9, 0): (0, 0, 0, 0)}), Day(TUE)])
    assert fills(res) == cp3_trade(root)


@pytest.mark.parametrize(("root", "span", "num", "side"),
                         [("ZM", 5, 4, "buy"), ("ZM", 5, 1, "sell"), ("ZL", 10, 8, "buy"),
                          ("ZL", 10, 2, "sell"), ("HE", 5, 4, "buy"), ("LE", 10, 2, "sell")])
def test_cp3_the_cuts_are_exact_where_a_float_clv_misses_them(root: str, span: int, num: int,
                                                              side: str) -> None:
    lo, hi, c = price(root, 0), price(root, span), price(root, num)
    float_clv = (c - lo) / (hi - lo)
    cut = 0.8 if side == "buy" else 0.2
    assert float_clv != cut and ((float_clv < cut) if side == "buy" else (float_clv > cut))
    res = run(m(root), [prior(MON, root, num, high=span), Day(TUE)])
    assert fills(res) == cp3_trade(root, side=side)


@pytest.mark.parametrize(("span", "num", "side"),
                         [(10, 8, "buy"), (10, 7, None), (10, 2, "sell"), (10, 3, None),
                          (5, 4, "buy"), (5, 1, "sell"), (15, 12, "buy"), (15, 11, None),
                          (15, 3, "sell"), (15, 4, None), (1, 1, "buy"), (1, 0, "sell"),
                          (0, 0, None), (100, 80, "buy"), (100, 79, None), (100, 20, "sell"),
                          (100, 21, None), (1000, 799, None), (1000, 201, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    assert clv_side(DailyBar(TUE, 100 + span, 100, 100 + num, 1)) == side


@pytest.mark.parametrize(("close", "side"), [(-2, "buy"), (-8, "sell")])
def test_cp3_the_daily_low_is_the_min_low(close: int, side: str) -> None:
    # H = B, L = B-10 (the 10:00 bar): C = B-2 is CLV 0.8, C = B-8 is 0.2
    res = run(m("ZW"), [prior(MON, "ZW", close, high=0, low=-10), Day(TUE)])
    assert fills(res) == cp3_trade("ZW", side=side)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_zero_range_is_no_trade(root: str) -> None:
    assert intents(run(m(root), [Day(MON), Day(TUE)])) == []


@pytest.mark.parametrize("root", ("ZC", "LE"))
def test_cp3_warm_up_no_complete_earlier_bar_is_no_trade(root: str) -> None:
    res = run(m(root), [prior(TUE, root, 8), Day(WED)])
    assert fills(res) == cp3_trade(root, WED)
    assert intents(run(m(root), [prior(TUE, root, 8)])) == []  # TUE: no earlier bar


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # TUE's own bar (CLV 0.8) never decides TUE; MON (CLV 0.5) decides: no trade on TUE
    res = run(m("ZS"), [prior(MON, "ZS", 5), prior(TUE, "ZS", 8), Day(WED)])
    assert fills(res) == cp3_trade("ZS", WED)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_d_minus_1_is_the_most_recent_complete_day(root: str) -> None:
    # MON would be CLV 0.2 (a sell on TUE) if complete; incomplete, TUE reads FRI (a buy)
    c_bar = CLOSE_BAR[grp(root)]
    for incomplete in (prior(MON, root, 2, skip=frozenset({hm(8, 30)})),  # no 08:30 bar
                       prior(MON, root, 2, skip=frozenset({c_bar})),  # no C-1 bar
                       prior(MON, root, 2, ids={hm(8, 30): 778})):  # two ids in [O, C)
        res = run(m(root), [prior(FRI, root, 8), incomplete, Day(TUE)])
        assert [f for f in fills(res) if f[0] == TUE] == cp3_trade(root, TUE)
    complete = prior(MON, root, 2)
    res = run(m(root), [prior(FRI, root, 8), complete, Day(TUE)])
    assert [f for f in fills(res) if f[0] == TUE] == cp3_trade(root, TUE, "sell")


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp3_grain_ids_outside_the_daily_window_do_not_make_it_incomplete(root: str) -> None:
    # MON's evening (CT date Sunday), overnight and 13:15 bars carry other ids; the daily bar
    # [08:30, 13:15) has one id, so MON is complete
    mon = prior(MON, root, 8, evening_id=555, ids={hm(7, 40): 556, hm(13, 15): 557})
    res = run(m(root), [mon, Day(TUE)])
    assert fills(res) == cp3_trade(root)


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp3_grain_evening_and_overnight_bars_are_not_in_the_daily_bar(root: str) -> None:
    # bars of trade date MON outside [08:30, 13:15) far above / below: CLV still 0.8
    wide = (0, 40, -40, 0)
    mon = prior(MON, root, 8, evening={hm(19, 0): wide}, paths={hm(7, 40): wide,
                                                                 hm(13, 15): wide})
    assert fills(run(m(root), [mon, Day(TUE)])) == cp3_trade(root)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar(root: str) -> None:
    other = 778
    res = run(m(root), [prior(MON, root, 8), Day(TUE, instrument_id=other)])
    assert intents(res) == []
    res = run(m(root), [prior(MON, root, 8, instrument_id=other), Day(TUE, instrument_id=other)])
    assert fills(res) == cp3_trade(root)


@pytest.mark.parametrize("root", ("ZM", "HE"))
def test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete(root: str) -> None:
    res = run(m(root), [prior(MON, root, 8), Day(TUE, skip=frozenset({hm(8, 30)}))])
    assert intents(res) == []  # TUE: no 08:30 bar, no entry (the 08:31 bar is not one)
    # TUE (CLV 0.5 if complete) lacks its 08:30 bar: incomplete, so WED reads MON (CLV 0.8)
    res = run(m(root), [prior(MON, root, 8), prior(TUE, root, 5, skip=frozenset({hm(8, 30)})),
                        Day(WED)])
    assert fills(res) == cp3_trade(root, WED)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_early_halt_day_is_not_traded_and_is_incomplete(root: str) -> None:
    # 2025-12-24 halts (grains 12:05, livestock 12:15); its bars carry the label. d = 12-24 is
    # not traded (12-23 is CLV 0.8); d = 12-26 (a grain late open) reads 12-23, not 12-24
    g = grp(root)
    label = halt_label(g, HALT_XMAS)
    end = hm(12, 5) if is_grain(root) else hm(12, 15)
    halt = Day(HALT_XMAS, paths={hm(9, 0): (0, 10, 0, 0), hm(10, 0): (0, 0, 0, 0),
                                 hm(11, 0): (0, 2, 0, 2)}, halt=label, end=end)
    late = Day(LATE_XMAS, no_evening=True)
    res = run(m(root), [prior(TUE_XMAS, root, 8), halt, late])
    assert fills(res) == cp3_trade(root, LATE_XMAS)
    assert (HALT_XMAS, "08:30", True, None) not in intents(res)


@pytest.mark.parametrize("root", ("ZL", "LE"))
def test_cp3_a_halt_day_with_all_bars_to_c_is_still_incomplete(root: str) -> None:
    # bars to C on a halt-labelled day (C-1 bar present): the label alone makes it incomplete
    g = grp(root)
    halt = prior(HALT_XMAS, root, 2, halt=halt_label(g, HALT_XMAS))
    res = run(m(root), [prior(TUE_XMAS, root, 8), halt, Day(LATE_XMAS, no_evening=True)])
    assert [f for f in fills(res) if f[0] == HALT_XMAS] == []
    assert fills(res)[-2:] == cp3_trade(root, LATE_XMAS)  # 12-26 reads 12-23 (buy)


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp3_grain_thanksgiving_friday_is_a_late_open_and_an_early_halt(root: str) -> None:
    # 2025-11-28: no evening session, halts 12:05: not traded, incomplete; Monday 12-01 reads
    # Wednesday 11-26
    halt = Day(HALT_TG, no_evening=True, halt="12:05", end=hm(12, 5),
               paths={hm(9, 0): (0, 10, 0, 0), hm(11, 0): (0, 2, 0, 2)})
    res = run(m(root), [prior(WED_TG, root, 8), halt, Day(MON_TG)])
    assert fills(res) == cp3_trade(root, MON_TG)


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp3_the_tuesday_after_memorial_day_reads_friday(root: str) -> None:
    res = run(m(root), [prior(FRI_MD, root, 2), Day(TUE_MD)])
    assert fills(res) == cp3_trade(root, TUE_MD, "sell")


@pytest.mark.parametrize("root", ("ZW", "LE"))
def test_cp3_monday_reads_friday(root: str) -> None:
    res = run(m(root), [prior(FRI, root, 8), Day(MON)])
    assert fills(res) == cp3_trade(root, MON)


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_missing_c_minus_2_bar_sends_the_exit_on_the_next_bar(root: str) -> None:
    exit_on = hm(13, 13) if is_grain(root) else hm(12, 58)
    res = run(m(root), [prior(MON, root, 8), Day(TUE, skip=frozenset({exit_on}))])
    later = "13:15" if is_grain(root) else "13:00"
    assert fills(res) == trade(TUE, "08:31", later)
    assert intents(res)[-1] == (TUE, EXIT_FILL[grp(root)], True, None)


@pytest.mark.parametrize("root", ("ZS", "HE"))
def test_cp3_no_exit_before_c_minus_2(root: str) -> None:
    res = run(m(root), [prior(MON, root, 8), Day(TUE)])
    assert [i[1] for i in intents(res)] == ["08:30", EXIT[grp(root)]]


@pytest.mark.parametrize("root", ("ZM", "LE"))
def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine(root: str) -> None:
    res = run(m(root), [prior(MON, root, 8), Day(TUE, flatten_from=hm(12, 0))])
    assert fills(res) == trade(TUE, "08:31", "12:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:30"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_d97_real_stop_level_engine_exit_then_nothing_more(root: str) -> None:
    # engine-level case (2): MON's settlement proxy is its C-1 close B+8 (the VWAP of the bars
    # overlapping the window: grains [13:14, 13:15), the 13:14 bar; livestock
    # [12:59:30, 13:00), the 12:59 bar). TUE: long from 08:31; the 10:30 close reaches
    # the upper stop level, so the engine closes at the 10:31 open (price_limit_exit). The
    # member sends no C-2 exit and no new entry, though later bars would qualify an exit
    up, _ = stop_offsets(root, TUE, 8)
    tue = Day(TUE, paths={hm(10, 30): (0, up, 0, up)})
    res = run(m(root), [prior(MON, root, 8), tue])
    assert fills(res) == trade(TUE, "08:31", "10:31", exit_reason="price_limit_exit")
    assert intents(res) == [(TUE, "08:30", True, None)]
    # one tick inside the stop: no forced exit
    inside = Day(TUE, paths={hm(10, 30): (0, up - 1, 0, up - 1)})
    assert fills(run(m(root), [prior(MON, root, 8), inside])) == cp3_trade(root)
    # the next trade date trades again: TUE is complete (H = the stop bar's high, C_d = B,
    # CLV 0), a sell on WED
    res = run(m(root), [prior(MON, root, 8), tue, Day(WED)])
    assert fills(res)[2:] == cp3_trade(root, WED, "sell")


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_daily_bar_and_entry_bar_are_bars_of_ct_date_d(root: str) -> None:
    # direct calls: bars of CT date d-1 carrying trade date d (the calendars never produce them
    # at these clocks) are neither daily-bar bars nor the entry bar
    c_bar = CLOSE_BAR[grp(root)]
    member = m(root)
    mon = [bar_at(root, MON, hm(8, 30)), bar_at(root, MON, hm(9, 0), (0, 10, 0, 0)),
           bar_at(root, MON, c_bar, (0, 8, 0, 8))]
    stray = [bar_at(root, MON, hm(8, 30), trade_day=TUE),
             bar_at(root, MON, c_bar, (0, 0, -30, -30), trade_day=TUE)]
    assert feed(member, mon + stray) == []
    (intent,) = feed(member, [bar_at(root, TUE, hm(8, 30))])
    assert intent.side == "buy"
    assert TUE - timedelta(days=1) == MON


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending(root: str) -> None:
    c_bar = CLOSE_BAR[grp(root)]

    def primed() -> cp3.Cp3CloseLocation:
        member = m(root)
        assert feed(member, [bar_at(root, MON, hm(8, 30)),
                             bar_at(root, MON, hm(9, 0), (0, 10, 0, 0)),
                             bar_at(root, MON, c_bar, (0, 8, 0, 8))]) == []
        return member

    entry = bar_at(root, TUE, hm(8, 30))
    view = view_of(root, entry.ts_event_ns, entry)
    member = primed()
    (intent,) = member.on_minute(view, account_of(root))
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert member.on_minute(view, account_of(root)) == ()  # once per trade date
    assert primed().on_minute(view, account_of(root, 0, 1)) == ()  # never while pending


@pytest.mark.parametrize("root", LIVESTOCK_ROOTS)
def test_cp3_an_entry_bar_carrying_early_halt_is_not_traded(root: str) -> None:
    # direct calls: the 08:30 bar of d with an early_halt_ct label: no entry (E.3-L-11)
    member = m(root)
    feed(member, [bar_at(root, MON, hm(8, 30)), bar_at(root, MON, hm(9, 0), (0, 10, 0, 0)),
                  bar_at(root, MON, hm(12, 59), (0, 8, 0, 8))])
    assert feed(member, [bar_at(root, TUE, hm(8, 30), halt=time(12, 15))]) == []
    member = m(root)
    feed(member, [bar_at(root, MON, hm(8, 30)), bar_at(root, MON, hm(9, 0), (0, 10, 0, 0)),
                  bar_at(root, MON, hm(12, 59), (0, 8, 0, 8))])
    assert len(feed(member, [bar_at(root, TUE, hm(8, 30))])) == 1


def test_cp3_kit_c_minus_1_bars() -> None:
    assert CLOSE_BAR["grains"] == hm(13, 14) and CLOSE_BAR["livestock"] == hm(12, 59)


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp3_day_accumulators_reset_each_trade_date(root: str) -> None:
    # MON spans B-40..B+40 (CLV 0.5, no trade on TUE); TUE spans B..B+10 with C_d B+8 (CLV
    # 0.8): WED buys. Carrying MON's high or low into TUE would make TUE's CLV 0.6
    mon = prior(MON, root, 0, high=40, low=-40)
    res = run(m(root), [mon, prior(TUE, root, 8), Day(WED)])
    assert fills(res) == cp3_trade(root, WED)


@pytest.mark.parametrize("root", ("ZS", "LE"))
def test_cp3_the_halt_flag_resets_on_the_next_trade_date(root: str) -> None:
    # 12-23 CLV 0.5; 12-24 an early halt (incomplete); 12-26 complete, CLV 0.8: Monday 12-29
    # reads 12-26 and buys. A halt flag carried from 12-24 would make 12-26 incomplete
    g = grp(root)
    mon = date(2025, 12, 29)
    end = hm(12, 5) if is_grain(root) else hm(12, 15)
    halt = Day(HALT_XMAS, halt=halt_label(g, HALT_XMAS), end=end)
    res = run(m(root), [prior(TUE_XMAS, root, 5), halt,
                        prior(LATE_XMAS, root, 8, no_evening=True), Day(mon)])
    assert fills(res) == cp3_trade(root, mon)
