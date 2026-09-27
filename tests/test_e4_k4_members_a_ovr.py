"""Stage E.4 K4 members of MemberCoder-A, part 2: K4-ovr-01 (reports/stage_e4_member_specs.md
section 8; readings K4-L-05, K4-L-08, K4-L-09, K4-L-10).

Synthetic bars only, built with tests/test_e4_k4_members_a.py's kit and run through the real Stage E
engine; direct calls where the engine cannot reach a case (prices <= 0 for C10). The reference
set is a "ladder": 20 sparse reference days (only the ten signal bars) whose r values are the tick
offsets -50..49 over the base B, so P10 = -40.1/B and P90 = 39.1/B (numpy linear).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, time
from typing import Any

import numpy as np
import pytest

from screening.stage_e_engine import Fill
from strategy.interface import Bar
from strategy.members.k4 import ovr
from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
from strategy.members.k4._port_common import EXPOSURES
from tests.test_e4_k4_members_a import (
    Day,
    Ticks,
    account_of,
    base_ticks,
    blackout_rules,
    ct,
    fills,
    forced_limit_rules,
    frame,
    halt_label,
    hm,
    intents,
    release_at,
    run,
    trade,
    view_of,
)

OPEN_MIN = tuple(hm(h, 0) for h in (8, 9, 10, 11, 12))  # the bars at t-60
CLOSE_MIN = tuple(hm(h, 59) for h in (8, 9, 10, 11, 12))  # the bars at t-1 (decision bars)
SIGNAL_BARS = frozenset(OPEN_MIN + CLOSE_MIN)
FULL = tuple(date.fromisoformat(s) for s in ENERGY_FULL_SESSIONS)
LADDER = tuple(tuple(5 * k + j - 50 for j in range(5)) for k in range(20))  # -50..49


def sessions_from(start: date, n: int) -> tuple[date, ...]:
    i = FULL.index(start)
    return FULL[i:i + n]


S = sessions_from(date(2025, 7, 7), 26)  # 2025-07-07 .. 2025-08-11, no early halt among them
D = S[20]  # the first date past the warm-up when the run starts on S[0]


def closes(values: Sequence[int]) -> dict[int, Ticks]:
    """The five decision bars closing at B + values[j] (their t-60 bars open at B)."""
    return {m: (0, max(0, x), min(0, x), x) for m, x in zip(CLOSE_MIN, values, strict=True)}


def ref_day(day: date, values: Sequence[int], paths: Mapping[int, Ticks] | None = None,
            **kw: Any) -> Day:
    """A sparse reference day: only the ten signal bars; r(t_j) = values[j] / B."""
    return Day(day, paths={**closes(values), **(paths or {})}, only=SIGNAL_BARS, **kw)


def trade_day(day: date, signal: Mapping[int, int], paths: Mapping[int, Ticks] | None = None,
              **kw: Any) -> Day:
    """A full day; r(t_j) = signal.get(j, 0) / B (0 lies between the ladder's cuts)."""
    base = closes([signal.get(j, 0) for j in range(5)])
    return Day(day, paths={**base, **(paths or {})}, **kw)


def ladder(dates: Sequence[date] = S[:20], omit: frozenset[int] = frozenset(),
           **per_k: Mapping[str, Any]) -> list[Day]:
    """The 20 ladder reference days on ``dates``; ``omit`` leaves days out of the frame
    entirely; ``per_k["k<n>"]`` passes extra Day arguments to day n."""
    return [ref_day(d, LADDER[k], **dict(per_k.get(f"k{k}", {})))
            for k, d in enumerate(dates) if k not in omit]


def at(day: date, hhmm: str, side: str, reason: str = "strategy") -> tuple[date, str, str, str]:
    return (day, hhmm, side, reason)


def drive(member: Any, days: Sequence[Day]) -> list[tuple[date, str, str]]:
    """Every bar of ``days`` fed to the member directly with a flat account (so every decision
    time decides on its own); (CT date, emitting bar hh:mm, side) of each intent."""
    out = []
    for row in frame(member.root, days).itertuples():
        halt = time.fromisoformat(row.early_halt_ct) if row.early_halt_ct else None
        bar = Bar(int(row.ts_event), row.open, row.high, row.low, row.close, 10,
                  int(row.instrument_id), row.raw_symbol, date.fromisoformat(row.trade_date),
                  False, False, halt, False, False, 0, False)
        for intent in member.on_minute(view_of(member.root, bar.ts_event_ns, bar),
                                       account_of(member.root)):
            opened = ct(bar.ts_event_ns)
            out.append((opened.date(), f"{opened:%H:%M}", intent.side))
    return out


# ----------------------------------------------------------------- the pure pieces ----
def test_decision_times_and_the_ladder_cuts() -> None:
    assert ovr.DECISION_TIMES_CT == (time(9, 0), time(10, 0), time(11, 0), time(12, 0),
                                     time(13, 0))
    for root in EXPOSURES:
        b = base_ticks(root)
        values = [x / b for row in LADDER for x in row]
        p10, p90 = np.percentile(values, [10, 90], method="linear")
        assert p10 == pytest.approx(-40.1 / b) and p90 == pytest.approx(39.1 / b)


def test_reference_dates_are_the_20_full_sessions_strictly_before_d() -> None:
    refs = ovr.reference_dates(date(2025, 7, 21))
    assert len(refs) == 20 and refs[0] == date(2025, 6, 20) and refs[-1] == date(2025, 7, 18)
    assert date(2025, 7, 4) not in refs  # the July 4 early halt is not a full session
    assert date(2025, 6, 19) not in ovr.reference_dates(date(2025, 7, 17))
    # an early-halt d has the same reference dates as the next full session
    assert ovr.reference_dates(date(2025, 9, 1)) == ovr.reference_dates(date(2025, 9, 2))
    assert ovr.reference_dates(D) == S[:20]
    assert ovr.reference_dates(FULL[0]) == ()
    assert ovr.reference_dates(FULL[5]) == FULL[:5]


@pytest.mark.parametrize(("to", "tc", "expected"), [
    (100, 99, -0.01), (7000, 7041, 41 / 7000), (3000, 3000, 0.0),
    (0, 5, None), (-3, 5, None)])  # C10: open of t-60 <= 0
def test_hourly_return_from_integer_ticks(to: int, tc: int, expected: float | None) -> None:
    got = ovr.hourly_return(to, tc)
    assert got == expected and (got is None or isinstance(got, float))


def test_percentile_side_non_strict_cuts_and_the_tie() -> None:
    # v0..v10 = -5, v11..v88 = 0, v89..v99 = 5: P10 = -5 and P90 = 5 exactly
    values = [-5.0] * 11 + [0.0] * 78 + [5.0] * 11
    assert ovr.percentile_side(-5.0, values) == "buy"  # r = P10
    assert ovr.percentile_side(-4.999, values) is None
    assert ovr.percentile_side(5.0, values) == "sell"  # r = P90
    assert ovr.percentile_side(4.999, values) is None
    tie = [0.0] * 80
    assert ovr.percentile_side(0.0, tie) is None  # P10 = P90 = r (K4-L-10)
    assert ovr.percentile_side(-1e-9, tie) == "buy"
    assert ovr.percentile_side(1e-9, tie) == "sell"


def test_percentile_side_uses_numpy_linear() -> None:
    values = [float(i) for i in range(100)]  # linear P10 = 9.9, P90 = 89.1
    assert ovr.percentile_side(9.5, values) == "buy"  # method="lower" (P10 = 9) would not
    assert ovr.percentile_side(9.95, values) is None  # "higher"/"nearest" (P10 = 10) would buy
    assert ovr.percentile_side(89.5, values) == "sell"  # "higher" (P90 = 90) would not
    assert ovr.percentile_side(89.05, values) is None  # "lower"/"nearest" (P90 = 89) would sell


# ------------------------------------------------------------------ engine: entries ----
@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_buys_at_or_below_p10_fills_at_t_and_exits_at_t_plus_59(root: str) -> None:
    member = vars(ovr)[f"make_{root.lower()}"]()
    res = run(member, [*ladder(), trade_day(D, {0: -41})])
    assert fills(res) == trade(D, "09:00", "09:59", "buy")
    assert intents(res) == [(D, "08:59", True, None), (D, "09:58", True, None)]
    q_c = {"MCL": 4, "NG": 1}[root]
    assert [f.qty for f in res.events(Fill)] == [q_c, q_c]


def test_ovr_cut_boundaries_on_the_ladder() -> None:
    # P10 = -40.1/B, P90 = 39.1/B: -40 and +39 stay inside, -41 buys, +40 sells
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {0: -40, 1: 39, 2: -41, 3: 40})])
    assert fills(res) == trade(D, "11:00", "11:59", "buy") + trade(D, "12:00", "12:59", "sell")


def test_ovr_the_five_decision_times_back_to_back_never_overlap() -> None:
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {0: -41, 1: 40, 2: -41, 3: 40, 4: -41})])
    assert fills(res) == (trade(D, "09:00", "09:59", "buy") + trade(D, "10:00", "10:59", "sell")
                          + trade(D, "11:00", "11:59", "buy") + trade(D, "12:00", "12:59", "sell")
                          + trade(D, "13:00", "13:59", "buy"))
    assert [i[1] for i in intents(res)] == ["08:59", "09:58", "09:59", "10:58", "10:59",
                                            "11:58", "11:59", "12:58", "12:59", "13:58"]


def test_ovr_r_uses_the_t_minus_60_open_and_the_t_minus_1_close() -> None:
    # r(09:00) = (close 08:59 - open 08:00) / open 08:00 = -41/B: buy. Decoys: the 08:00 CLOSE
    # and the 08:59 OPEN are B-100 (either as the base would give a positive r), the 07:59 bar
    # (t-61) closes at B+300
    decoys = {hm(8, 0): (0, 0, -100, -100), hm(8, 59): (-100, 0, -100, -41),
              hm(7, 59): (0, 300, 0, 300)}
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {}, paths=decoys)])
    assert fills(res) == trade(D, "09:00", "09:59", "buy")


def test_ovr_warm_up_needs_all_20_reference_dates_in_the_run_k4_l09() -> None:
    # S[19] would sell (r = 45/B above its 95 in-run values' P90) but one of its reference
    # dates, 2025-07-03, precedes the run's first trade date: no trade. S[20] trades.
    days = [*ladder(S[:19]), trade_day(S[19], dict(enumerate(LADDER[19]))),
            trade_day(D, {0: -41})]
    res = run(ovr.make_mcl(), days)
    assert [i for i in intents(res) if i[0] == S[19]] == []
    assert fills(res) == trade(D, "09:00", "09:59", "buy")


def test_ovr_fewer_than_20_table_dates_before_d_is_no_trade_k4_l13() -> None:
    # the run starts on the table's first date (2019-05-01, K4-L-13): FULL[19] has only 19 table
    # dates before it, all in the run, with 95 values and an r above their P90, yet no trade;
    # FULL[20] has its full 20 and trades
    s = FULL[:21]
    assert s[0] == date(2019, 5, 1) and len(ovr.reference_dates(s[19])) == 19
    days = [*ladder(s[:19]), trade_day(s[19], dict(enumerate(LADDER[19]))),
            trade_day(s[20], {0: -41})]
    res = run(ovr.make_mcl(), days)
    assert [i for i in intents(res) if i[0] == s[19]] == []
    assert fills(res) == trade(s[20], "09:00", "09:59", "buy")


def test_ovr_early_halt_dates_are_not_reference_dates() -> None:
    # run from 2025-06-20; the 07-04 early halt carries extreme values. 07-18 (S'[19]) would
    # sell if 07-04 filled a slot (its 20 dates would all be in the run); it does not, so one
    # of 07-18's dates (06-18) precedes the run: no trade. 07-21 (S'[20]) trades on the ladder.
    s = sessions_from(date(2025, 6, 20), 21)
    assert s[19] == date(2025, 7, 18) and s[20] == date(2025, 7, 21)
    halt = ref_day(date(2025, 7, 4), [-500] * 5, halt=halt_label(date(2025, 7, 4)))
    days = sorted([*ladder(s[:19]), halt, trade_day(s[19], dict(enumerate(LADDER[19]))),
                   trade_day(s[20], {0: -41})], key=lambda d: d.trade_date)
    res = run(ovr.make_mcl(), days)
    assert [i for i in intents(res) if i[0] in (date(2025, 7, 4), s[19])] == []
    assert fills(res) == trade(s[20], "09:00", "09:59", "buy")


def test_ovr_an_early_halt_trade_date_is_not_traded() -> None:
    # 2025-09-01 (Labor Day, F 11:30): entries at 08:59 and 09:59 would be before F, so the
    # member's own test is what blocks them. 09-02 has the same 20 reference dates and trades.
    halt_day, next_day = date(2025, 9, 1), date(2025, 9, 2)
    label = halt_label(halt_day)
    days = [*ladder(ovr.reference_dates(halt_day)),
            trade_day(halt_day, {0: -41, 1: 40}, halt=label),
            trade_day(next_day, {0: -41}, evening_halt=label)]
    res = run(ovr.make_mcl(), days)
    assert [i for i in intents(res) if i[0] == halt_day] == []
    assert fills(res) == trade(next_day, "09:00", "09:59", "buy")


def test_ovr_only_the_20_most_recent_dates_are_referenced() -> None:
    # five older dates with r = -500/B each: were they referenced, P10 would fall far below
    # -41/B and 09:00 would not buy. (Ladder days past the warm-up trade too; only s[25] is
    # asserted.)
    s = sessions_from(date(2025, 6, 30), 26)
    old = [ref_day(d, [-500] * 5) for d in s[:5]]
    res = run(ovr.make_mcl(), [*old, *ladder(s[5:25]), trade_day(s[25], {0: -41})])
    assert [f for f in fills(res) if f[0] == s[25]] == trade(s[25], "09:00", "09:59", "buy")


# ----------------------------------------------------- engine: counts and slots (L-08) ----
@pytest.mark.parametrize(("omit", "trades"), [
    (frozenset({5, 6, 7, 8}), True),  # 16 dates present: exactly 80 values
    (frozenset({5, 6, 7, 8, 9}), False)])  # 75 values
def test_ovr_absent_dates_keep_their_slot_and_80_values_are_needed(omit: frozenset[int],
                                                                   trades: bool) -> None:
    # were the slots refilled from earlier dates, those dates would precede the run (warm-up)
    res = run(ovr.make_mcl(), [*ladder(omit=omit), trade_day(D, {0: -60})])
    assert fills(res) == (trade(D, "09:00", "09:59", "buy") if trades else [])


@pytest.mark.parametrize(("omit", "trades"), [(frozenset({5, 6, 7}), True),  # 84 values
                                              (frozenset({5, 6, 7, 8}), False)])  # 79 values
def test_ovr_a_date_with_missing_bars_contributes_fewer_values(omit: frozenset[int],
                                                               trades: bool) -> None:
    days = ladder(omit=omit, k0={"skip": frozenset({hm(8, 0)})})  # k0 loses r(09:00)
    res = run(ovr.make_mcl(), [*days, trade_day(D, {0: -60})])
    assert fills(res) == (trade(D, "09:00", "09:59", "buy") if trades else [])


def test_ovr_a_roll_blackout_reference_date_counts() -> None:
    # 80 values only with S[3]'s five; S[3] is a roll-blackout date (bars delivered, opens
    # refused by name). The member does not exclude it (K4-L-08).
    member = ovr.make_mcl()
    days = [*ladder(omit=frozenset({5, 6, 7, 8})), trade_day(D, {0: -60})]
    res = run(member, days, rules=blackout_rules(member, days, [S[3]]))
    assert fills(res) == trade(D, "09:00", "09:59", "buy")


def test_ovr_a_reference_value_with_two_instrument_ids_is_not_counted() -> None:
    # 80 values less k10's r(10:00), whose 09:00 bar carries another instrument_id: 79
    days = ladder(omit=frozenset({5, 6, 7, 8}), k10={"ids": {hm(9, 0): 778}})
    assert fills(run(ovr.make_mcl(), [*days, trade_day(D, {0: -60})])) == []


def test_ovr_reference_values_of_an_earlier_contract_count() -> None:
    # section 8: each reference value needs ITS two bars on one instrument_id; reference days
    # on the previous contract (776) still count against today's 777
    days = ladder(omit=frozenset({5, 6, 7, 8}), **{f"k{k}": {"instrument_id": 776}
                                                   for k in range(10)})
    res = run(ovr.make_mcl(), [*days, trade_day(D, {0: -60})])
    assert fills(res) == trade(D, "09:00", "09:59", "buy")


# ------------------------------------------------------- engine: the day's own bars ----
def test_ovr_signal_bars_on_two_instrument_ids_block_that_t_only() -> None:
    # 08:00 (t-60 of 09:00) on 778: no trade at 09:00; 10:00 trades; an unread bar (08:30) on
    # another id does not matter
    day = trade_day(D, {0: -41, 1: 40}, ids={hm(8, 0): 778})
    assert fills(run(ovr.make_mcl(), [*ladder(), day])) == trade(D, "10:00", "10:59", "sell")
    unread = trade_day(D, {0: -41}, ids={hm(8, 30): 778})
    assert fills(run(ovr.make_mcl(), [*ladder(), unread])) == trade(D, "09:00", "09:59")


@pytest.mark.parametrize("missing", [hm(8, 59), hm(8, 0)])
def test_ovr_a_missing_signal_bar_is_no_trade_at_that_t(missing: int) -> None:
    day = trade_day(D, {0: -41, 1: 40}, skip=frozenset({missing}))
    assert fills(run(ovr.make_mcl(), [*ladder(), day])) == trade(D, "10:00", "10:59", "sell")


def test_ovr_a_missing_exit_bar_moves_the_exit_and_skips_the_overlapping_entry() -> None:
    # no 09:58 bar: the exit goes on 09:59 (fills 10:00), so the member still holds at the
    # 10:00 decision bar and 10:00 is not traded; 11:00 is
    day = trade_day(D, {0: -41, 1: 40, 2: -41}, skip=frozenset({hm(9, 58)}))
    res = run(ovr.make_mcl(), [*ladder(), day])
    assert fills(res) == trade(D, "09:00", "10:00", "buy") + trade(D, "11:00", "11:59", "buy")
    assert [i[1] for i in intents(res)] == ["08:59", "09:59", "10:59", "11:58"]


def test_ovr_d95a_release_at_t_defers_the_entry_fill() -> None:
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {0: -41})],
              releases=release_at("MCL", D, 9, 0))
    assert fills(res) == trade(D, "09:02", "09:59", "buy")


def test_ovr_d95a_release_next_to_t_leaves_the_fill_alone() -> None:
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {0: -41})],
              releases=release_at("MCL", D, 8, 58))  # guard [08:58, 09:00)
    assert fills(res) == trade(D, "09:00", "09:59", "buy")


def test_ovr_d95a_deferred_exit_keeps_the_next_t_out() -> None:
    # a release at 09:59: the exit fills at 10:01; the member still holds (exit pending) at the
    # 10:00 decision bar, so 10:00 is not traded (positions never overlap)
    res = run(ovr.make_mcl(), [*ladder(), trade_day(D, {0: -41, 1: 40})],
              releases=release_at("MCL", D, 9, 59))
    assert fills(res) == trade(D, "09:00", "10:01", "buy")
    assert [i[1] for i in intents(res)] == ["08:59", "09:58"]


def test_ovr_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    day = trade_day(D, {4: -41}, flatten_from=hm(13, 30))
    res = run(ovr.make_mcl(), [*ladder(), day])
    assert fills(res) == trade(D, "13:00", "13:31", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["12:59"]


def test_ovr_d97_engine_exit_later_decision_times_still_trade() -> None:
    member = ovr.make_mcl()
    days = [*ladder(), trade_day(D, {0: -41, 1: 40})]
    res = run(member, days, rules=forced_limit_rules(member, days, [(D, hm(9, 20))]))
    assert fills(res) == ([at(D, "09:00", "buy"), at(D, "09:21", "sell", "price_limit_exit")]
                          + trade(D, "10:00", "10:59", "sell"))
    assert [i[1] for i in intents(res)] == ["08:59", "09:59", "10:58"]  # no 09:58 exit


def test_ovr_d97_engine_exit_on_the_exit_bar_is_not_duplicated() -> None:
    member = ovr.make_mcl()
    days = [*ladder(), trade_day(D, {0: -41})]
    res = run(member, days, rules=forced_limit_rules(member, days, [(D, hm(9, 58))]))
    assert fills(res) == trade(D, "09:00", "09:59", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:59"]


def test_ovr_state_carries_across_days_and_trades_again_the_next_day() -> None:
    # D and S[21]: S[21]'s reference dates are S[1..20], D's own values included
    days = [*ladder(), trade_day(D, {0: -41}), trade_day(S[21], {1: 60})]
    res = run(ovr.make_mcl(), days)
    assert fills(res) == trade(D, "09:00", "09:59") + trade(S[21], "10:00", "10:59", "sell")


# ------------------------------------------------------------ direct calls: C10 ----
def test_ovr_c10_open_of_t_minus_60_at_or_below_zero_is_no_trade_at_t() -> None:
    for root in EXPOSURES:
        b = base_ticks(root)
        make = vars(ovr)[f"make_{root.lower()}"]
        zero = trade_day(D, {0: -41, 1: 40}, paths={hm(8, 0): (-b, 0, -b, 0)})  # open 0
        below = trade_day(D, {0: -41, 1: 40}, paths={hm(8, 0): (-b - 5, 0, -b - 5, 0)})
        control = trade_day(D, {0: -41, 1: 40})
        assert drive(make(), [*ladder(), control]) == [(D, "08:59", "buy"), (D, "09:59", "sell")]
        assert drive(make(), [*ladder(), zero]) == [(D, "09:59", "sell")]
        assert drive(make(), [*ladder(), below]) == [(D, "09:59", "sell")]


def test_ovr_c10_a_reference_value_with_open_at_or_below_zero_is_not_counted() -> None:
    b = base_ticks("MCL")
    control = ladder(omit=frozenset({5, 6, 7, 8}))  # exactly 80 values
    zero = ladder(omit=frozenset({5, 6, 7, 8}), k0={"paths": {hm(8, 0): (-b, 0, -b, 0)}})
    assert drive(ovr.make_mcl(), [*control, trade_day(D, {0: -60})]) == [(D, "08:59", "buy")]
    assert drive(ovr.make_mcl(), [*zero, trade_day(D, {0: -60})]) == []
