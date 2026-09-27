"""Stage E.4 Part 2, K5 members of MemberCoder-A, part 2: K5-ovr-01
(reports/stage_e4b_member_specs.md section 7; readings K4-L-05, K4-L-08, K4-L-09, K4-L-10,
K5-L-05, K5-L-06; E.1 F-7: K4-ovr-01's rule text with K5's clock).

Synthetic bars only, built with tests/test_e4_k5_members_a.py's kit and run through the real Stage E
engine; direct calls where the engine cannot reach a case (prices <= 0 for C10). The reference
set is a "ladder": 20 sparse reference days (only the signal bars) whose r values are the tick
offsets -10n..10n-1 over the base B, n the number of decision times (MGC 5: -50..49, so
P10 = -40.1/B and P90 = 39.1/B; MHG 4: -40..39, so P10 = -32.1/B and P90 = 31.1/B; numpy linear).
The decision times are written out as literals per root (spec section 7), not derived.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, time
from types import MappingProxyType
from typing import Any

import numpy as np
import pytest

from screening.stage_e_engine import Fill
from strategy.interface import Bar
from strategy.members.k5 import ovr
from strategy.members.k5._calendar import METALS_FULL_SESSIONS
from strategy.members.k5._port_common import EXPOSURES
from tests.test_e4_k5_members_a import (
    Q_C,
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
    make,
    release_at,
    run,
    trade,
    view_of,
)

# spec section 7: the decision times t, the value floor, and the ladder's cut boundaries (in
# ticks over B: "buy"/"sell" just beyond the cuts, "in_low"/"in_high" just inside)
OVR = MappingProxyType({
    "MGC": {"times": ("08:20", "09:20", "10:20", "11:20", "12:20"), "floor": 80,
            "buy": -41, "sell": 40, "in_low": -40, "in_high": 39},
    "MHG": {"times": ("08:10", "09:10", "10:10", "11:10"), "floor": 64,
            "buy": -33, "sell": 32, "in_low": -32, "in_high": 31}})
FULL = tuple(date.fromisoformat(s) for s in METALS_FULL_SESSIONS)


def minute(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def clock(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def t_min(root: str) -> tuple[int, ...]:
    return tuple(minute(s) for s in OVR[root]["times"])


def open_min(root: str) -> tuple[int, ...]:
    return tuple(t - 60 for t in t_min(root))  # the bars at t-60


def close_min(root: str) -> tuple[int, ...]:
    return tuple(t - 1 for t in t_min(root))  # the bars at t-1 (decision bars)


def n_times(root: str) -> int:
    return len(OVR[root]["times"])


def ladder_values(root: str) -> tuple[tuple[int, ...], ...]:
    n = n_times(root)
    return tuple(tuple(n * k + j - 10 * n for j in range(n)) for k in range(20))


def hold(root: str, j: int) -> tuple[str, str, str, str]:
    """(entry intent bar, entry fill, exit intent bar, exit fill) of decision time j."""
    t = t_min(root)[j]
    return clock(t - 1), clock(t), clock(t + 58), clock(t + 59)


def sessions_from(start: date, n: int) -> tuple[date, ...]:
    i = FULL.index(start)
    return FULL[i:i + n]


S = sessions_from(date(2025, 7, 7), 26)  # 2025-07-07 .. 2025-08-11, no early halt among them
D = S[20]  # the first date past the warm-up when the run starts on S[0]


def closes(root: str, values: Sequence[int]) -> dict[int, Ticks]:
    """The decision bars closing at B + values[j] (their t-60 bars open at B)."""
    return {m: (0, max(0, x), min(0, x), x)
            for m, x in zip(close_min(root), values, strict=True)}


def ref_day(root: str, day: date, values: Sequence[int],
            paths: Mapping[int, Ticks] | None = None, **kw: Any) -> Day:
    """A sparse reference day: only the signal bars; r(t_j) = values[j] / B."""
    signal_bars = frozenset(open_min(root) + close_min(root))
    return Day(day, paths={**closes(root, values), **(paths or {})}, only=signal_bars, **kw)


def trade_day(root: str, day: date, signal: Mapping[int, int],
              paths: Mapping[int, Ticks] | None = None, **kw: Any) -> Day:
    """A full day; r(t_j) = signal.get(j, 0) / B (0 lies between the ladder's cuts)."""
    base = closes(root, [signal.get(j, 0) for j in range(n_times(root))])
    return Day(day, paths={**base, **(paths or {})}, **kw)


def ladder(root: str, dates: Sequence[date] = S[:20], omit: frozenset[int] = frozenset(),
           **per_k: Mapping[str, Any]) -> list[Day]:
    """The 20 ladder reference days on ``dates``; ``omit`` leaves days out of the frame
    entirely; ``per_k["k<n>"]`` passes extra Day arguments to day n."""
    rows = ladder_values(root)
    return [ref_day(root, d, rows[k], **dict(per_k.get(f"k{k}", {})))
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


# ------------------------------------------------------------ the clock and the floor ----
def test_decision_times_are_o_plus_60k_while_t_at_most_c() -> None:
    as_str = lambda ts: tuple(f"{t:%H:%M}" for t in ts)  # noqa: E731
    assert as_str(ovr.decision_times(time(7, 20), time(12, 30))) == OVR["MGC"]["times"]
    assert as_str(ovr.decision_times(time(7, 10), time(12, 0))) == OVR["MHG"]["times"]
    # t = C is included (t <= C), t = O is not (k starts at 1); K4's energy clock (O 08:00,
    # C 13:30) gives K4-ovr-01's literal five times, the F-7 check of the one rule text
    assert as_str(ovr.decision_times(time(8, 0), time(13, 0)))[-1] == "13:00"
    assert as_str(ovr.decision_times(time(8, 0), time(13, 30))) == ("09:00", "10:00", "11:00",
                                                                    "12:00", "13:00")
    for root in EXPOSURES:
        member = make(ovr, root)
        assert as_str(member._times) == OVR[root]["times"]


def test_the_value_floor_is_80_percent_of_the_possible_values_k5_l06() -> None:
    assert ovr.VALUE_FLOOR_PERCENT == 80 and ovr.REFERENCE_DATES == 20
    assert (ovr.min_values(5), ovr.min_values(4)) == (80, 64)  # 80 of 100, 64 of 80
    for root in EXPOSURES:
        assert make(ovr, root)._min_values == OVR[root]["floor"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_the_ladder_cuts(root: str) -> None:
    b = base_ticks(root)
    values = [x / b for row in ladder_values(root) for x in row]
    assert len(values) == 20 * n_times(root)
    p10, p90 = np.percentile(values, [10, 90], method="linear")
    spec = OVR[root]
    assert spec["buy"] < p10 * b < spec["in_low"] and spec["in_high"] < p90 * b < spec["sell"]


def test_reference_dates_are_the_20_metals_full_sessions_strictly_before_d() -> None:
    refs = ovr.reference_dates(date(2025, 7, 21))
    assert len(refs) == 20 and refs[0] == date(2025, 6, 20) and refs[-1] == date(2025, 7, 18)
    assert date(2025, 7, 4) not in refs  # the July 4 early halt is not a full session
    assert date(2025, 6, 19) not in ovr.reference_dates(date(2025, 7, 17))  # Juneteenth halt
    # an early-halt d has the same reference dates as the next full session
    assert ovr.reference_dates(date(2025, 9, 1)) == ovr.reference_dates(date(2025, 9, 2))
    assert ovr.reference_dates(D) == S[:20]
    assert ovr.reference_dates(FULL[0]) == ()
    assert ovr.reference_dates(FULL[5]) == FULL[:5]


@pytest.mark.parametrize(("to", "tc", "expected"), [
    (100, 99, -0.01), (20000, 20041, 41 / 20000), (9000, 9000, 0.0),
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
    tie = [0.0] * 64
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
    res = run(make(ovr, root), [*ladder(root), trade_day(root, D, {0: OVR[root]["buy"]})])
    entry, entry_fill, exit_, exit_fill = hold(root, 0)  # MGC 08:19/08:20, 09:18/09:19
    assert fills(res) == trade(D, entry_fill, exit_fill, "buy")
    assert intents(res) == [(D, entry, True, None), (D, exit_, True, None)]
    assert [f.qty for f in res.events(Fill)] == [Q_C[root], Q_C[root]]  # q_c 1 / 2


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_cut_boundaries_on_the_ladder(root: str) -> None:
    spec = OVR[root]
    signal = {0: spec["in_low"], 1: spec["in_high"], 2: spec["buy"], 3: spec["sell"]}
    res = run(make(ovr, root), [*ladder(root), trade_day(root, D, signal)])
    assert fills(res) == (trade(D, hold(root, 2)[1], hold(root, 2)[3], "buy")
                          + trade(D, hold(root, 3)[1], hold(root, 3)[3], "sell"))


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_every_decision_time_back_to_back_never_overlaps(root: str) -> None:
    spec, n = OVR[root], n_times(root)
    signal = {j: spec["buy"] if j % 2 == 0 else spec["sell"] for j in range(n)}
    res = run(make(ovr, root), [*ladder(root), trade_day(root, D, signal)])
    expected = []
    for j in range(n):
        expected += trade(D, hold(root, j)[1], hold(root, j)[3], "buy" if j % 2 == 0 else "sell")
    assert fills(res) == expected
    assert [i[1] for i in intents(res)] == [x for j in range(n)
                                            for x in (hold(root, j)[0], hold(root, j)[2])]
    # MGC: five t 08:20..12:20, the last exit fill 13:19; MHG: four t 08:10..11:10, 12:09
    assert fills(res)[-1][1] == {"MGC": "13:19", "MHG": "12:09"}[root]


def test_ovr_r_uses_the_t_minus_60_open_and_the_t_minus_1_close() -> None:
    # r(08:20) = (close 08:19 - open 07:20) / open 07:20 = -41/B: buy. Decoys: the 07:20 CLOSE
    # and the 08:19 OPEN are B-100 (either as the base would give a positive r), the 07:19 bar
    # (t-61) closes at B+300
    decoys = {hm(7, 20): (0, 0, -100, -100), hm(8, 19): (-100, 0, -100, -41),
              hm(7, 19): (0, 300, 0, 300)}
    res = run(ovr.make_mgc(), [*ladder("MGC"), trade_day("MGC", D, {}, paths=decoys)])
    assert fills(res) == trade(D, "08:20", "09:19", "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_warm_up_needs_all_20_reference_dates_in_the_run_k4_l09(root: str) -> None:
    # S[19] would sell (its r values sit above the in-run values' P90) but one of its reference
    # dates, 2025-07-03, precedes the run's first trade date: no trade. S[20] trades.
    rows = ladder_values(root)
    days = [*ladder(root, S[:19]), trade_day(root, S[19], dict(enumerate(rows[19]))),
            trade_day(root, D, {0: OVR[root]["buy"]})]
    res = run(make(ovr, root), days)
    assert [i for i in intents(res) if i[0] == S[19]] == []
    assert fills(res) == trade(D, hold(root, 0)[1], hold(root, 0)[3], "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_fewer_than_20_table_dates_before_d_is_no_trade_k4_l13(root: str) -> None:
    # the run starts on the table's first date (2019-05-01, K4-L-13): FULL[19] has only 19 table
    # dates before it, all in the run, and an r above their P90, yet no trade; FULL[20] has its
    # full 20 and trades
    s = FULL[:21]
    assert s[0] == date(2019, 5, 1) and len(ovr.reference_dates(s[19])) == 19
    rows = ladder_values(root)
    days = [*ladder(root, s[:19]), trade_day(root, s[19], dict(enumerate(rows[19]))),
            trade_day(root, s[20], {0: OVR[root]["buy"]})]
    res = run(make(ovr, root), days)
    assert [i for i in intents(res) if i[0] == s[19]] == []
    assert fills(res) == trade(s[20], hold(root, 0)[1], hold(root, 0)[3], "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_early_halt_dates_are_not_reference_dates(root: str) -> None:
    # run from 2025-06-20; the 07-04 early halt carries extreme values. 07-18 (s[19]) would
    # sell if 07-04 filled a slot (its 20 dates would all be in the run); it does not, so one
    # of 07-18's dates (06-18) precedes the run: no trade. 07-21 (s[20]) trades on the ladder.
    s = sessions_from(date(2025, 6, 20), 21)
    assert s[19] == date(2025, 7, 18) and s[20] == date(2025, 7, 21)
    halt = ref_day(root, date(2025, 7, 4), [-500] * n_times(root),
                   halt=halt_label(date(2025, 7, 4)))
    rows = ladder_values(root)
    days = sorted([*ladder(root, s[:19]), halt,
                   trade_day(root, s[19], dict(enumerate(rows[19]))),
                   trade_day(root, s[20], {0: OVR[root]["buy"]})], key=lambda d: d.trade_date)
    res = run(make(ovr, root), days)
    assert [i for i in intents(res) if i[0] in (date(2025, 7, 4), s[19])] == []
    assert fills(res) == trade(s[20], hold(root, 0)[1], hold(root, 0)[3], "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_an_early_halt_trade_date_is_not_traded(root: str) -> None:
    # 2025-09-01 (Labor Day, F 11:30): the first entries (t-1 before F) would be accepted by
    # the engine, so the member's own test is what blocks them. 09-02 has the same 20
    # reference dates and trades.
    halt_day, next_day = date(2025, 9, 1), date(2025, 9, 2)
    label = halt_label(halt_day)
    spec = OVR[root]
    days = [*ladder(root, ovr.reference_dates(halt_day)),
            trade_day(root, halt_day, {0: spec["buy"], 1: spec["sell"]}, halt=label),
            trade_day(root, next_day, {0: spec["buy"]}, evening_halt=label)]
    res = run(make(ovr, root), days)
    assert [i for i in intents(res) if i[0] == halt_day] == []
    assert fills(res) == trade(next_day, hold(root, 0)[1], hold(root, 0)[3], "buy")


def test_ovr_only_the_20_most_recent_dates_are_referenced() -> None:
    # five older dates with r = -500/B each: were they referenced, P10 would fall far below
    # -41/B and 08:20 would not buy. (Ladder days past the warm-up trade too; only s[25] is
    # asserted.)
    s = sessions_from(date(2025, 6, 30), 26)
    old = [ref_day("MGC", d, [-500] * 5) for d in s[:5]]
    res = run(ovr.make_mgc(), [*old, *ladder("MGC", s[5:25]), trade_day("MGC", s[25], {0: -41})])
    assert [f for f in fills(res) if f[0] == s[25]] == trade(s[25], "08:20", "09:19", "buy")


# ----------------------------------------------- engine: the value floor and the slots ----
@pytest.mark.parametrize(("root", "omit", "trades"), [
    ("MGC", frozenset({5, 6, 7, 8}), True),  # 16 dates x 5: exactly 80 of 100
    ("MGC", frozenset({5, 6, 7, 8, 9}), False),  # 75 values
    ("MHG", frozenset({5, 6, 7, 8}), True),  # 16 dates x 4: exactly 64 of 80
    ("MHG", frozenset({5, 6, 7, 8, 9}), False)])  # 60 values
def test_ovr_absent_dates_keep_their_slot_and_the_floor_is_80_percent(
        root: str, omit: frozenset[int], trades: bool) -> None:
    # were the slots refilled from earlier dates, those dates would precede the run (warm-up)
    res = run(make(ovr, root), [*ladder(root, omit=omit), trade_day(root, D, {0: -60})])
    expected = trade(D, hold(root, 0)[1], hold(root, 0)[3], "buy") if trades else []
    assert fills(res) == expected


@pytest.mark.parametrize(("root", "omit", "trades"), [
    ("MGC", frozenset({5, 6, 7}), True),  # 85 - 1 = 84 values
    ("MGC", frozenset({5, 6, 7, 8}), False),  # 80 - 1 = 79
    ("MHG", frozenset({5, 6, 7}), True),  # 68 - 1 = 67
    ("MHG", frozenset({5, 6, 7, 8}), False)])  # 64 - 1 = 63
def test_ovr_a_full_session_date_with_missing_bars_occupies_its_slot(
        root: str, omit: frozenset[int], trades: bool) -> None:
    first_open = open_min(root)[0]  # k0 loses its first r (the t-60 bar is missing)
    days = ladder(root, omit=omit, k0={"skip": frozenset({first_open})})
    res = run(make(ovr, root), [*days, trade_day(root, D, {0: -60})])
    expected = trade(D, hold(root, 0)[1], hold(root, 0)[3], "buy") if trades else []
    assert fills(res) == expected


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_a_roll_blackout_reference_date_counts(root: str) -> None:
    # the floor is met only with S[3]'s values; S[3] is a roll-blackout date (bars delivered,
    # opens refused by name). The member does not exclude it (K5-L-05, K4-L-08).
    member = make(ovr, root)
    days = [*ladder(root, omit=frozenset({5, 6, 7, 8})), trade_day(root, D, {0: -60})]
    res = run(member, days, rules=blackout_rules(member, days, [S[3]]))
    assert fills(res) == trade(D, hold(root, 0)[1], hold(root, 0)[3], "buy")


def test_ovr_a_reference_value_with_two_instrument_ids_is_not_counted() -> None:
    # exactly the floor less k10's r(09:20), whose 08:20 bar carries another instrument_id: 79
    days = ladder("MGC", omit=frozenset({5, 6, 7, 8}), k10={"ids": {hm(8, 20): 778}})
    assert fills(run(ovr.make_mgc(), [*days, trade_day("MGC", D, {0: -60})])) == []
    mhg = ladder("MHG", omit=frozenset({5, 6, 7, 8}), k10={"ids": {hm(8, 10): 778}})  # 63
    assert fills(run(ovr.make_mhg(), [*mhg, trade_day("MHG", D, {0: -60})])) == []


def test_ovr_reference_values_of_an_earlier_contract_count() -> None:
    # K4-L-14: each reference value needs ITS two bars on one instrument_id; reference days on
    # the previous contract (776) still count against today's 777
    days = ladder("MGC", omit=frozenset({5, 6, 7, 8}), **{f"k{k}": {"instrument_id": 776}
                                                          for k in range(10)})
    res = run(ovr.make_mgc(), [*days, trade_day("MGC", D, {0: -60})])
    assert fills(res) == trade(D, "08:20", "09:19", "buy")


# ------------------------------------------------------- engine: the day's own bars ----
def test_ovr_signal_bars_on_two_instrument_ids_block_that_t_only() -> None:
    # 07:20 (t-60 of 08:20) on 778: no trade at 08:20; 09:20 trades; an unread bar (07:50) on
    # another id does not matter
    day = trade_day("MGC", D, {0: -41, 1: 40}, ids={hm(7, 20): 778})
    assert fills(run(ovr.make_mgc(), [*ladder("MGC"), day])) == trade(D, "09:20", "10:19",
                                                                      "sell")
    unread = trade_day("MGC", D, {0: -41}, ids={hm(7, 50): 778})
    assert fills(run(ovr.make_mgc(), [*ladder("MGC"), unread])) == trade(D, "08:20", "09:19")


@pytest.mark.parametrize("missing", [hm(8, 9), hm(7, 10)])
def test_ovr_a_missing_signal_bar_is_no_trade_at_that_t(missing: int) -> None:
    # MHG: the 08:09 decision bar or the 07:10 (t-60) bar of t = 08:10 is missing
    day = trade_day("MHG", D, {0: -33, 1: 32}, skip=frozenset({missing}))
    assert fills(run(ovr.make_mhg(), [*ladder("MHG"), day])) == trade(D, "09:10", "10:09",
                                                                      "sell")


def test_ovr_a_missing_exit_bar_moves_the_exit_and_skips_the_overlapping_entry() -> None:
    # no 09:18 bar: the exit goes on 09:19 (fills 09:20), so the member still holds at the
    # 09:20 decision bar and 09:20 is not traded; 10:20 is
    day = trade_day("MGC", D, {0: -41, 1: 40, 2: -41}, skip=frozenset({hm(9, 18)}))
    res = run(ovr.make_mgc(), [*ladder("MGC"), day])
    assert fills(res) == trade(D, "08:20", "09:20", "buy") + trade(D, "10:20", "11:19", "buy")
    assert [i[1] for i in intents(res)] == ["08:19", "09:19", "10:19", "11:18"]


def test_ovr_d95a_release_at_t_defers_the_entry_fill() -> None:
    res = run(ovr.make_mgc(), [*ladder("MGC"), trade_day("MGC", D, {0: -41})],
              releases=release_at("MGC", D, 8, 20))
    assert fills(res) == trade(D, "08:22", "09:19", "buy")


def test_ovr_d95a_release_next_to_t_leaves_the_fill_alone() -> None:
    res = run(ovr.make_mgc(), [*ladder("MGC"), trade_day("MGC", D, {0: -41})],
              releases=release_at("MGC", D, 8, 18))  # guard [08:18, 08:20)
    assert fills(res) == trade(D, "08:20", "09:19", "buy")


def test_ovr_d95a_deferred_exit_keeps_the_next_t_out() -> None:
    # a release at 09:19: the exit fills at 09:21; the member still holds (exit pending) at the
    # 09:19 decision bar of t = 09:20, so 09:20 is not traded (positions never overlap)
    res = run(ovr.make_mgc(), [*ladder("MGC"), trade_day("MGC", D, {0: -41, 1: 40})],
              releases=release_at("MGC", D, 9, 19))
    assert fills(res) == trade(D, "08:20", "09:21", "buy")
    assert [i[1] for i in intents(res)] == ["08:19", "09:18"]


def test_ovr_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    day = trade_day("MGC", D, {4: -41}, flatten_from=hm(12, 50))
    res = run(ovr.make_mgc(), [*ladder("MGC"), day])
    assert fills(res) == trade(D, "12:20", "12:51", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["12:19"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_d97_engine_exit_later_decision_times_still_trade(root: str) -> None:
    member = make(ovr, root)
    spec = OVR[root]
    days = [*ladder(root), trade_day(root, D, {0: spec["buy"], 1: spec["sell"]})]
    t0 = t_min(root)[0]
    res = run(member, days, rules=forced_limit_rules(member, days, [(D, t0 + 20)]))
    assert fills(res) == ([at(D, clock(t0), "buy"),
                           at(D, clock(t0 + 21), "sell", "price_limit_exit")]
                          + trade(D, hold(root, 1)[1], hold(root, 1)[3], "sell"))
    # no exit at t+58 of the first trade, no re-entry at that t; the next t proceeds
    assert [i[1] for i in intents(res)] == [hold(root, 0)[0], hold(root, 1)[0], hold(root, 1)[2]]


def test_ovr_d97_engine_exit_on_the_exit_bar_is_not_duplicated() -> None:
    member = ovr.make_mgc()
    days = [*ladder("MGC"), trade_day("MGC", D, {0: -41})]
    res = run(member, days, rules=forced_limit_rules(member, days, [(D, hm(9, 18))]))
    assert fills(res) == trade(D, "08:20", "09:19", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:19"]


def test_ovr_state_carries_across_days_and_trades_again_the_next_day() -> None:
    # D and S[21]: S[21]'s reference dates are S[1..20], D's own values included
    days = [*ladder("MHG"), trade_day("MHG", D, {0: -33}), trade_day("MHG", S[21], {1: 60})]
    res = run(ovr.make_mhg(), days)
    assert fills(res) == trade(D, "08:10", "09:09") + trade(S[21], "09:10", "10:09", "sell")


# ------------------------------------------------------------ direct calls: C10 ----
@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_c10_open_of_t_minus_60_at_or_below_zero_is_no_trade_at_t(root: str) -> None:
    b = base_ticks(root)
    spec = OVR[root]
    first_open = open_min(root)[0]
    signal = {0: spec["buy"], 1: spec["sell"]}
    zero = trade_day(root, D, signal, paths={first_open: (-b, 0, -b, 0)})  # open 0
    below = trade_day(root, D, signal, paths={first_open: (-b - 5, 0, -b - 5, 0)})
    control = trade_day(root, D, signal)
    first, second = hold(root, 0)[0], hold(root, 1)[0]
    assert drive(make(ovr, root), [*ladder(root), control]) == [(D, first, "buy"),
                                                                (D, second, "sell")]
    assert drive(make(ovr, root), [*ladder(root), zero]) == [(D, second, "sell")]
    assert drive(make(ovr, root), [*ladder(root), below]) == [(D, second, "sell")]


@pytest.mark.parametrize("root", EXPOSURES)
def test_ovr_c10_a_reference_value_with_open_at_or_below_zero_is_not_counted(root: str) -> None:
    b = base_ticks(root)
    first_open = open_min(root)[0]
    control = ladder(root, omit=frozenset({5, 6, 7, 8}))  # exactly the floor
    zero = ladder(root, omit=frozenset({5, 6, 7, 8}),
                  k0={"paths": {first_open: (-b, 0, -b, 0)}})
    first = hold(root, 0)[0]
    assert drive(make(ovr, root), [*control, trade_day(root, D, {0: -60})]) == [(D, first, "buy")]
    assert drive(make(ovr, root), [*zero, trade_day(root, D, {0: -60})]) == []
