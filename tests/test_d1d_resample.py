"""Known-answer tests for the Stage D.1d resampler (declaration section 1, rules R1-R7).

Everything here is pinned against the declaration
(``reports/stage_d1d_timeframe_declaration.md`` section 1), never against the
implementation's own output:

1. The session-minute grid and ``slot_of``: 17:00 CT is minute 0, the RTH open is 930, and
   the stubs R3 drops (08:00-08:30 ETH and 14:30-15:00 RTH at tf 60) really are dropped.
   15:00-15:07 CT belongs to no coarse bar at any timeframe.
2. Early closes: a 12:15 CT halt ends RTH at 11:58 CT, a Good Friday 08:15 CT halt leaves
   no RTH segment at all, and an evening bar ignores the halt its row carries.
3. ``coarse_bars`` over a synthetic frame that spans two whole trade dates, 17:00 CT
   through 15:07 CT: OHLCV aggregation to the tick, the declared slot counts, a slot that
   keeps its coarse bar with one minute missing, and a slot dropped for two instrument ids.
4. ``CoarseBarBuilder`` (what every D.1d strategy runs) reproduces the vectorised bars
   exactly, in order, including both of those cases, and flags ``completed_late`` on the
   one slot whose last minute is missing and on no other.
5. ``missing_minute_share`` arithmetic.

The synthetic frame is built programmatically: one bar per session minute, price
6000.00 + seq * 0.25 with a deterministic high/low wobble, so every expected number below
is arithmetic a reader can redo by hand.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules.xfa_rules import no_new_positions_time_ct
from sim.engine import BAR_COLUMNS, iter_bars
from strategy.research.g_timeframe.resample import (
    DEFAULT_LIMIT,
    ETH_NOMINAL_END,
    MIDNIGHT_SESSION_MINUTE,
    RTH_NOMINAL_END,
    RTH_START,
    TIMEFRAMES,
    CoarseBar,
    CoarseBarBuilder,
    Slot,
    coarse_bars,
    limit_minute,
    missing_minute_share,
    segment_end,
    session_minute,
    slot_count,
    slot_of,
)

CT = ZoneInfo("America/Chicago")
TICK = 0.25
BASE_PRICE = 6000.00
DEFAULT_INSTRUMENT = 4242
SPLICE_INSTRUMENT = 4243

# The session grid, as minutes from the 17:00 CT reopen.
SM_1700 = 0
SM_MIDNIGHT = 420
SM_0800 = 900
SM_0829 = 929
SM_0830 = 930
SM_1459 = 1319
SM_1500 = 1320
SM_1507 = 1327
SESSION_MINUTES = 1328  # sm 0 (17:00 CT) .. sm 1327 (15:07 CT), inclusive

# A whole trade date's worth of 1-minute bars, twice.
TRADE_DATES = (date(2025, 9, 2), date(2025, 9, 3))
# sm 359 is 22:59 CT: the LAST minute of a slot at 5, 15, 30 and 60 (359 % 60 == 59), so
# dropping it makes exactly one slot per timeframe complete late with n_minutes = tf - 1.
MISSING_MINUTE = (TRADE_DATES[1], 359)
# sm 1203 is 13:03 CT: one bar with a second instrument id, which drops its slot at every
# timeframe (rule R4) without dropping any other.
SPLICE_MINUTE = (TRADE_DATES[0], 1203)

# Declared slot counts on a normal day (declaration R3).
DECLARED_SLOTS = {"ETH": {5: 186, 15: 62, 30: 31, 60: 15},
                  "RTH": {5: 78, 15: 26, 30: 13, 60: 6}}

COARSE_FIELDS = ("trade_date", "segment", "slot", "start", "end", "open", "high", "low",
                 "close", "volume", "n_minutes", "instrument_id")


# ------------------------------------------------------------------- synthetic frame ----
def ts_event_ns(trade_date: date, sm: int) -> int:
    """UTC ns of the bar that opens ``sm`` minutes after the 17:00 CT reopen of ``trade_date``."""
    reopen = datetime.combine(trade_date - timedelta(days=1), time(17, 0), tzinfo=CT)
    return int((reopen + timedelta(minutes=sm)).astimezone(UTC).timestamp()) * 10**9


def synthetic_row(trade_date: date, sm: int, seq: int, instrument_id: int,
                  early_halt_ct: str) -> dict:
    """One 1-minute bar: open = 6000.00 + seq ticks, with a deterministic high/low wobble."""
    o = BASE_PRICE + seq * TICK
    return {
        "ts_event": ts_event_ns(trade_date, sm),
        "open": o,
        "high": o + TICK * (2 + sm % 4),
        "low": o - TICK * (1 + sm % 3),
        "close": o + TICK,
        "volume": 1 + sm % 5,
        "instrument_id": instrument_id,
        "raw_symbol": "MESZ5",
        "trade_date": trade_date.isoformat(),
        "in_flatten_window": False,
        "in_no_new_positions_window": False,
        "early_halt_ct": early_halt_ct,
        "in_scheduled_closure": False,
        "is_roll_session": False,
        "gap_before_minutes": 0,
        "vendor_degraded_day": False,
    }


def build_frame(minutes: Sequence[tuple[date, int]],
                splices: Iterable[tuple[date, int]] = (),
                early_halt_ct: str = "") -> pd.DataFrame:
    spliced = frozenset(splices)
    rows = [synthetic_row(day, sm, seq,
                          SPLICE_INSTRUMENT if (day, sm) in spliced else DEFAULT_INSTRUMENT,
                          early_halt_ct)
            for seq, (day, sm) in enumerate(minutes)]
    return pd.DataFrame(rows, columns=list(BAR_COLUMNS))


FULL_MINUTES = tuple((day, sm) for day in TRADE_DATES for sm in range(SESSION_MINUTES)
                     if (day, sm) != MISSING_MINUTE)
FULL_FRAME = build_frame(FULL_MINUTES, splices=(SPLICE_MINUTE,))
FULL_BARS = tuple(iter_bars(FULL_FRAME))


# --------------------------------------------------------------- reference resampler ----
@dataclass(frozen=True)
class RefSlot:
    segment: str
    index: int
    start: int
    end: int


def reference_slot(sm: int, tf: int, limit: int = DEFAULT_LIMIT) -> RefSlot | None:
    """R2/R3 written out longhand, independently of ``resample``: the expected answer."""
    if sm < min(ETH_NOMINAL_END, limit):
        segment, seg_start, seg_end = "ETH", 0, min(ETH_NOMINAL_END, limit)
    elif RTH_START <= sm < min(RTH_NOMINAL_END, limit):
        segment, seg_start, seg_end = "RTH", RTH_START, min(RTH_NOMINAL_END, limit)
    else:
        return None
    index = (sm - seg_start) // tf
    start = seg_start + index * tf
    if start + tf > seg_end:
        return None
    return RefSlot(segment, index, start, start + tf)


def reference_coarse(minutes: Sequence[tuple[date, int]], frame: pd.DataFrame,
                     tf: int) -> list[tuple]:
    """R4 written out longhand: group the rows by (trade date, slot) and aggregate."""
    groups: dict[tuple[date, str, int], list[dict]] = {}
    for (day, sm), (_, row) in zip(minutes, frame.iterrows(), strict=True):
        slot = reference_slot(sm, tf)
        if slot is None:
            continue
        groups.setdefault((day, slot.segment, slot.index), []).append(
            {"slot": slot, "row": row})
    out = []
    for (day, segment, index), members in groups.items():
        rows = [m["row"] for m in members]
        ids = {int(r["instrument_id"]) for r in rows}
        if len(ids) != 1:
            continue  # rule R4: two instrument ids drop the slot
        slot = members[0]["slot"]
        out.append((day, segment, index, slot.start, slot.end,
                    float(rows[0]["open"]), max(float(r["high"]) for r in rows),
                    min(float(r["low"]) for r in rows), float(rows[-1]["close"]),
                    sum(int(r["volume"]) for r in rows), len(rows), ids.pop()))
    return sorted(out, key=lambda t: (t[0], t[3]))


def coarse_tuples(coarse: pd.DataFrame) -> list[tuple]:
    return [(r.trade_date, str(r.segment), int(r.slot), int(r.start), int(r.end),
             float(r.open), float(r.high), float(r.low), float(r.close),
             int(r.volume), int(r.n_minutes), int(r.instrument_id))
            for r in coarse.itertuples()]


def bar_tuple(bar: CoarseBar) -> tuple:
    return (bar.trade_date, bar.segment, bar.slot, bar.start, bar.end, bar.open, bar.high,
            bar.low, bar.close, int(bar.volume), bar.n_minutes, bar.instrument_id)


def drain(builder: CoarseBarBuilder, bars: Iterable) -> list[CoarseBar]:
    return [coarse for bar in bars for coarse in builder.push(bar)]


# ====================================================== 1. session_minute / slot_of ====
def test_session_minute_is_zero_at_the_1700_ct_reopen_and_930_at_the_rth_open() -> None:
    # Arrange / Act / Assert: the grid the whole module counts on.
    assert session_minute(17 * 60) == SM_1700
    assert session_minute(8 * 60 + 30) == SM_0830 == RTH_START
    assert session_minute(0) == SM_MIDNIGHT == MIDNIGHT_SESSION_MINUTE  # 00:00 CT
    assert session_minute(14 * 60 + 59) == SM_1459
    assert session_minute(15 * 60) == SM_1500 == RTH_NOMINAL_END
    assert session_minute(15 * 60 + 8) == DEFAULT_LIMIT == 1328  # no new positions


def test_rth_slot_zero_starts_at_the_0830_ct_open_for_every_timeframe() -> None:
    for tf in TIMEFRAMES:
        assert slot_of(SM_0830, tf, DEFAULT_LIMIT) == Slot("RTH", 0, RTH_START, RTH_START + tf)
        assert slot_of(SM_1700, tf, DEFAULT_LIMIT) == Slot("ETH", 0, 0, tf)
        # 08:29 CT is the last ETH minute; it never leaks into RTH slot 0. At tf 60 it is
        # in the dropped 08:00-08:30 stub, so it is in no slot at all.
        eth_last = slot_of(SM_0829, tf, DEFAULT_LIMIT)
        assert eth_last is None if tf == 60 else eth_last.segment == "ETH"


def test_1459_ct_closes_the_last_rth_slot_below_60_minutes_but_is_in_no_60_minute_slot() -> None:
    # R3: the 14:30-15:00 stub is dropped at tf 60, never truncated.
    for tf in (5, 15, 30):
        slot = slot_of(SM_1459, tf, DEFAULT_LIMIT)
        assert slot == Slot("RTH", DECLARED_SLOTS["RTH"][tf] - 1, SM_1500 - tf, SM_1500)
    assert slot_of(SM_1459, 60, DEFAULT_LIMIT) is None
    # The dropped 60-min stub is exactly 14:30-15:00 CT, sm 1290..1319.
    for sm in range(1290, SM_1500):
        assert slot_of(sm, 60, DEFAULT_LIMIT) is None
    assert slot_of(1289, 60, DEFAULT_LIMIT) == Slot("RTH", 5, 1230, 1290)  # 14:29 CT


def test_the_0800_to_0829_ct_eth_stub_is_in_no_slot_at_60_minutes() -> None:
    # R3: 60-min ETH has 15 slots, ending at 08:00 CT.
    for sm in range(SM_0800, SM_0830):
        assert slot_of(sm, 60, DEFAULT_LIMIT) is None
    assert slot_of(SM_0800 - 1, 60, DEFAULT_LIMIT) == Slot("ETH", 14, 840, SM_0800)


def test_1500_to_1507_ct_belongs_to_no_slot_at_any_timeframe() -> None:
    # R2: from the RTH segment end to the next 17:00 open, nothing is a coarse bar.
    for tf in TIMEFRAMES:
        for sm in range(SM_1500, SM_1507 + 1):
            assert slot_of(sm, tf, DEFAULT_LIMIT) is None


def test_no_60_minute_slot_crosses_midnight_ct() -> None:
    for sm in range(SESSION_MINUTES):
        slot = slot_of(sm, 60, DEFAULT_LIMIT)
        if slot is not None:
            assert not slot.start < SM_MIDNIGHT < slot.end
    assert slot_of(SM_MIDNIGHT - 1, 60, DEFAULT_LIMIT).end == SM_MIDNIGHT
    assert slot_of(SM_MIDNIGHT, 60, DEFAULT_LIMIT).start == SM_MIDNIGHT


def test_slot_counts_on_a_normal_day_match_the_declaration() -> None:
    for segment, per_tf in DECLARED_SLOTS.items():
        for tf, expected in per_tf.items():
            assert slot_count(segment, tf, DEFAULT_LIMIT) == expected


# ================================================================== 2. early closes ====
HALT_1215 = time(12, 15)          # a CME 12:15 CT early close
HALT_GOOD_FRIDAY = time(8, 15)    # Good Friday's 08:15 CT close
SM_1158 = 1138                    # 11:58 CT
SM_0758 = 898                     # 07:58 CT
DAY_BAR_MINUTE = RTH_START        # any bar on the trade date's own calendar day


def test_early_close_at_1215_ct_ends_rth_at_1158_and_drops_the_1155_slot() -> None:
    # Arrange: the flatten is 15 min before the halt, no new positions 2 min earlier still.
    assert no_new_positions_time_ct(HALT_1215) == time(11, 58)
    limit = limit_minute(DAY_BAR_MINUTE, HALT_1215)

    # Act / Assert
    assert limit == SM_1158 == session_minute(11 * 60 + 58)
    assert segment_end("RTH", limit) == SM_1158
    assert slot_count("RTH", 5, limit) == 41  # (1138 - 930) // 5
    assert slot_of(session_minute(11 * 60 + 50), 5, limit) == Slot("RTH", 40, 1130, 1135)
    # 11:55-12:00 would cross 11:58: dropped, never truncated.
    assert slot_of(session_minute(11 * 60 + 55), 5, limit) is None
    assert slot_of(session_minute(11 * 60 + 57), 5, limit) is None
    assert slot_count("ETH", 5, limit) == DECLARED_SLOTS["ETH"][5]  # ETH is untouched


def test_good_friday_early_close_leaves_no_rth_segment_and_ends_eth_at_0758() -> None:
    # Arrange
    assert no_new_positions_time_ct(HALT_GOOD_FRIDAY) == time(7, 58)
    limit = limit_minute(DAY_BAR_MINUTE, HALT_GOOD_FRIDAY)

    # Act / Assert: R2, "a segment with a non-positive length does not exist".
    assert limit == SM_0758 == session_minute(7 * 60 + 58)
    for tf in TIMEFRAMES:
        assert slot_count("RTH", tf, limit) == 0
        assert slot_of(SM_0830, tf, limit) is None
    assert segment_end("ETH", limit) == SM_0758
    assert slot_count("ETH", 5, limit) == 179  # 898 // 5; the last slot is 07:50-07:55
    assert slot_of(session_minute(7 * 60 + 50), 5, limit) == Slot("ETH", 178, 890, 895)
    assert slot_of(session_minute(7 * 60 + 55), 5, limit) is None  # would cross 07:58


def test_an_evening_bar_ignores_the_early_halt_its_row_carries() -> None:
    # An evening bar carries the PREVIOUS calendar day's halt, which is already over.
    for halt in (HALT_1215, HALT_GOOD_FRIDAY):
        assert limit_minute(SM_1700, halt) == DEFAULT_LIMIT
        assert limit_minute(MIDNIGHT_SESSION_MINUTE - 1, halt) == DEFAULT_LIMIT
        assert limit_minute(MIDNIGHT_SESSION_MINUTE, halt) < DEFAULT_LIMIT
    assert limit_minute(DAY_BAR_MINUTE, None) == DEFAULT_LIMIT


def test_early_close_frame_stops_the_rth_segment_at_the_no_new_positions_time() -> None:
    # Arrange: one whole trade date whose every row carries the 12:15 CT halt.
    day = TRADE_DATES[0]
    minutes = [(day, sm) for sm in range(SESSION_MINUTES)]
    frame = build_frame(minutes, early_halt_ct="12:15")

    # Act
    coarse = coarse_bars(frame, 5)

    # Assert
    rth = coarse[coarse["segment"] == "RTH"]
    assert len(rth) == 41
    assert int(rth["end"].max()) == 1135 < SM_1158
    assert len(coarse[coarse["segment"] == "ETH"]) == DECLARED_SLOTS["ETH"][5]


# ================================================================== 3. coarse_bars ====
def test_coarse_bars_aggregate_the_first_eth_slot_to_the_tick() -> None:
    # Arrange: trade date 1, sm 0..4 -> seq 0..4, so open = 6000.00 + sm ticks.
    #   high = open + (2 + sm%4) ticks -> max at sm 3: 6000.75 + 1.25 = 6002.00
    #   low  = open - (1 + sm%3) ticks -> min at sm 0..2: 5999.75
    #   volume = 1 + sm%5 -> 1+2+3+4+5 = 15
    coarse = coarse_bars(FULL_FRAME, 5)

    # Act
    row = coarse.iloc[0]

    # Assert
    assert (row["trade_date"], row["segment"], row["slot"]) == (TRADE_DATES[0], "ETH", 0)
    assert (row["start"], row["end"]) == (0, 5)
    assert (row["open"], row["high"], row["low"], row["close"]) == (
        6000.00, 6002.00, 5999.75, 6001.25)
    assert (row["volume"], row["n_minutes"]) == (15, 5)
    assert row["instrument_id"] == DEFAULT_INSTRUMENT


def test_coarse_bars_aggregate_the_first_rth_slot_to_the_tick() -> None:
    # Arrange: trade date 1, sm 930..934 -> seq == sm, so open = 6000 + 930*0.25 = 6232.50.
    #   high max at sm 934: 6000 + (934+2+2)*0.25 = 6234.50
    #   low  min at sm 930..932: 6000 + 929*0.25 = 6232.25
    coarse = coarse_bars(FULL_FRAME, 5)

    # Act
    rth = coarse[(coarse["trade_date"] == TRADE_DATES[0]) & (coarse["segment"] == "RTH")]
    row = rth.iloc[0]

    # Assert
    assert (row["slot"], row["start"], row["end"]) == (0, 930, 935)
    assert (row["open"], row["high"], row["low"], row["close"]) == (
        6232.50, 6234.50, 6232.25, 6233.75)
    assert (row["volume"], row["n_minutes"]) == (15, 5)


def test_coarse_bars_match_an_independent_longhand_resampler_for_every_timeframe() -> None:
    for tf in TIMEFRAMES:
        # Act
        got = coarse_tuples(coarse_bars(FULL_FRAME, tf))
        # Assert
        assert got == reference_coarse(FULL_MINUTES, FULL_FRAME, tf)


def test_coarse_bar_counts_per_trade_date_and_segment_match_the_declared_slots() -> None:
    for tf in TIMEFRAMES:
        coarse = coarse_bars(FULL_FRAME, tf)
        counts = coarse.groupby(["trade_date", "segment"]).size().to_dict()
        expected = {
            # Trade date 1 loses exactly one RTH slot: the one holding the spliced minute.
            (TRADE_DATES[0], "ETH"): DECLARED_SLOTS["ETH"][tf],
            (TRADE_DATES[0], "RTH"): DECLARED_SLOTS["RTH"][tf] - 1,
            # Trade date 2's missing minute does NOT drop its slot (rule R4).
            (TRADE_DATES[1], "ETH"): DECLARED_SLOTS["ETH"][tf],
            (TRADE_DATES[1], "RTH"): DECLARED_SLOTS["RTH"][tf],
        }
        assert counts == expected


def test_a_slot_with_a_missing_minute_is_kept_with_one_fewer_minute() -> None:
    day, missing_sm = MISSING_MINUTE
    for tf in TIMEFRAMES:
        # Act
        coarse = coarse_bars(FULL_FRAME, tf)
        hit = coarse[(coarse["trade_date"] == day) & (coarse["start"] <= missing_sm)
                     & (coarse["end"] > missing_sm)]
        # Assert
        assert len(hit) == 1
        assert int(hit.iloc[0]["n_minutes"]) == tf - 1
        assert int(hit.iloc[0]["end"]) == missing_sm + 1  # the missing minute closed it
        # Every other bar of that trade date is complete.
        others = coarse[(coarse["trade_date"] == day) & (coarse.index != hit.index[0])]
        assert (others["n_minutes"] == tf).all()


def test_a_slot_whose_bars_carry_two_instrument_ids_is_dropped() -> None:
    day, spliced_sm = SPLICE_MINUTE
    for tf in TIMEFRAMES:
        # Act
        coarse = coarse_bars(FULL_FRAME, tf)
        covering = coarse[(coarse["trade_date"] == day) & (coarse["start"] <= spliced_sm)
                          & (coarse["end"] > spliced_sm)]
        # Assert
        assert len(covering) == 0
        assert set(coarse["instrument_id"]) == {DEFAULT_INSTRUMENT}
        # Its neighbours survive: only that one slot goes.
        start = RTH_START + ((spliced_sm - RTH_START) // tf) * tf
        neighbours = coarse[(coarse["trade_date"] == day)
                            & coarse["start"].isin([start - tf, start + tf])]
        assert len(neighbours) == 2


def test_no_coarse_bar_covers_1500_to_1507_ct() -> None:
    expected_minutes = {5: 1319, 15: 1319, 30: 1319, 60: 1259}
    for tf in TIMEFRAMES:
        # Act
        coarse = coarse_bars(FULL_FRAME, tf)
        # Assert
        assert int(coarse["end"].max()) <= RTH_NOMINAL_END
        assert not ((coarse["start"] >= SM_1500) | (coarse["end"] > SM_1500)).any()
        # Trade date 2 has 1327 bars; 8 of them (15:00-15:07) are in no coarse bar, and at
        # tf 60 the two dropped stubs account for 60 more.
        day2 = coarse[coarse["trade_date"] == TRADE_DATES[1]]
        assert int(day2["n_minutes"].sum()) == expected_minutes[tf]


def test_coarse_bars_refuses_an_undeclared_timeframe_and_an_unsorted_frame() -> None:
    with pytest.raises(ValueError, match="not one of"):
        coarse_bars(FULL_FRAME, 10)
    with pytest.raises(ValueError, match="ts_event order"):
        coarse_bars(FULL_FRAME.iloc[::-1], 5)


# ============================================================ 4. CoarseBarBuilder ====
def test_builder_reproduces_the_vectorised_bars_exactly_for_every_timeframe() -> None:
    for tf in TIMEFRAMES:
        # Arrange
        builder = CoarseBarBuilder(tf)
        # Act
        incremental = [bar_tuple(b) for b in drain(builder, FULL_BARS)]
        # Assert: same bars, same order, including the late and dropped slots.
        assert incremental == coarse_tuples(coarse_bars(FULL_FRAME, tf))


def test_builder_marks_completed_late_only_on_the_slot_whose_last_minute_is_missing() -> None:
    day, missing_sm = MISSING_MINUTE
    for tf in TIMEFRAMES:
        # Arrange / Act
        produced = drain(CoarseBarBuilder(tf), FULL_BARS)
        late = [b for b in produced if b.completed_late]
        # Assert
        assert len(late) == 1
        assert (late[0].trade_date, late[0].end) == (day, missing_sm + 1)
        assert late[0].n_minutes == tf - 1
        assert all(b.n_minutes == tf for b in produced if not b.completed_late)


def test_builder_completes_a_normal_slot_on_the_bar_that_opens_its_last_minute() -> None:
    # Arrange: the first ETH slot of trade date 1, 17:00-17:05 CT.
    builder = CoarseBarBuilder(5)
    # Act
    early = [builder.push(bar) for bar in FULL_BARS[:4]]
    on_the_last_minute = builder.push(FULL_BARS[4])
    # Assert: nothing before sm 4 = slot end - 1, then exactly one bar, on time.
    assert early == [(), (), (), ()]
    assert len(on_the_last_minute) == 1
    bar = on_the_last_minute[0]
    assert (bar.start, bar.end, bar.n_minutes, bar.completed_late) == (0, 5, 5, False)
    assert (bar.open, bar.close, bar.body) == (6000.00, 6001.25, 1.25)
    assert bar.range == 6002.00 - 5999.75


def test_builder_never_emits_the_slot_that_carries_two_instrument_ids() -> None:
    day, spliced_sm = SPLICE_MINUTE
    for tf in TIMEFRAMES:
        produced = drain(CoarseBarBuilder(tf), FULL_BARS)
        assert not [b for b in produced
                    if b.trade_date == day and b.start <= spliced_sm < b.end]
        assert {b.instrument_id for b in produced} == {DEFAULT_INSTRUMENT}


def test_a_slot_missing_its_last_rth_minute_completes_on_the_first_1500_ct_bar() -> None:
    # Arrange: one trade date with 14:59 CT (sm 1319) absent, so RTH slot 77 (14:55-15:00)
    # cannot complete on time. R6: it completes on the NEXT bar the strategy receives,
    # which here is the 15:00 CT bar, itself in no slot.
    day = TRADE_DATES[0]
    minutes = [(day, sm) for sm in range(SESSION_MINUTES) if sm != SM_1459]
    frame = build_frame(minutes)

    # Act
    builder = CoarseBarBuilder(5)
    pushed = {sm: builder.push(bar)
              for (_, sm), bar in zip(minutes, iter_bars(frame), strict=True)}

    # Assert
    assert pushed[SM_1459 - 1] == ()  # 14:58 CT closes nothing: its slot runs to 15:00
    assert len(pushed[SM_1500]) == 1
    late = pushed[SM_1500][0]
    assert (late.segment, late.slot, late.start, late.end) == ("RTH", 77, 1315, SM_1500)
    assert (late.n_minutes, late.completed_late) == (4, True)
    assert all(pushed[sm] == () for sm in range(SM_1500 + 1, SM_1507 + 1))
    # And the whole stream still reproduces the vectorised bars exactly.
    emitted = [bar_tuple(b) for out in pushed.values() for b in out]
    assert emitted == coarse_tuples(coarse_bars(frame, 5))


def test_builder_refuses_an_undeclared_timeframe() -> None:
    with pytest.raises(ValueError, match="not one of"):
        CoarseBarBuilder(10)


# ======================================================== 5. missing_minute_share ====
def test_missing_minute_share_counts_slots_with_a_gap_per_segment() -> None:
    # Arrange: ETH slots 0 and 1 (sm 0..9) with sm 3 missing, plus two complete RTH slots.
    day = TRADE_DATES[0]
    minutes = [(day, sm) for sm in [0, 1, 2, 4, 5, 6, 7, 8, 9] + list(range(930, 940))]
    frame = build_frame(minutes)

    # Act
    coarse = coarse_bars(frame, 5)
    share = missing_minute_share(coarse, 5)

    # Assert: 1 of 2 ETH slots has a gap, 0 of 2 RTH slots do.
    assert sorted(coarse["n_minutes"]) == [4, 5, 5, 5]
    assert share == {"ETH": 0.5, "RTH": 0.0}


def test_missing_minute_share_is_nan_for_a_segment_with_no_coarse_bars() -> None:
    # Arrange: ETH only, both slots complete.
    day = TRADE_DATES[0]
    frame = build_frame([(day, sm) for sm in range(10)])

    # Act
    share = missing_minute_share(coarse_bars(frame, 5), 5)

    # Assert
    assert share["ETH"] == 0.0
    assert math.isnan(share["RTH"])


# =================================================== 6. suspected bug in resample.py ====
SUSPECTED_TRUNCATED_FEED = (
    "SUSPECTED BUG (not fixed here, by instruction). resample.py's module docstring says "
    "coarse_bars and CoarseBarBuilder produce identical bars, but CoarseBarBuilder has no "
    "flush: an accumulator still open when the feed stops is never returned, while "
    "coarse_bars emits that slot as a short coarse bar. The two therefore agree only when "
    "the feed runs past each segment's end. On the current research parquet no trade "
    "date's last bar leaves the builder mid-slot, so nothing computed so far is wrong; a "
    "frame sliced mid-session, a truncated vendor day or a live session cut short would "
    "diverge silently. Either add a flush()/finalize() to the builder, or state the "
    "precondition in the docstring and have coarse_bars drop a slot whose last minute is "
    "past the frame's end."
)


@pytest.mark.xfail(strict=True, reason=SUSPECTED_TRUNCATED_FEED)
def test_builder_and_coarse_bars_agree_when_the_feed_stops_inside_a_slot() -> None:
    # Arrange: the frame stops at 14:57 CT (sm 1317), three minutes into RTH slot 77.
    day = TRADE_DATES[0]
    minutes = [(day, sm) for sm in range(SM_1500 - 2)]
    frame = build_frame(minutes)

    # Act
    vectorised = coarse_tuples(coarse_bars(frame, 5))
    incremental = [bar_tuple(b) for b in drain(CoarseBarBuilder(5), iter_bars(frame))]

    # Assert: coarse_bars keeps slot 77 with 3 minutes; the builder never returns it.
    assert vectorised[-1][:5] == (day, "RTH", 77, 1315, SM_1500)
    assert vectorised[-1][10] == 3
    assert incremental == vectorised
