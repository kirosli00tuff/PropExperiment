"""Known-answer tests for Stage D.1d's Family G stylized facts (declaration sections 3-5).

Everything here is pinned against ``reports/stage_d1d_timeframe_declaration.md`` sections
3-5, never against the implementation's own output, and nothing reads the research
parquet: ``run_timeframe`` and ``resolve_eda_dates`` are never called. Only the pure
functions are exercised, on hand-built inputs:

1. ``build_days`` on a synthetic 1-minute frame (three trade dates, 17:00 CT through
   15:07 CT, the third with a 12:15 CT early close, plus one sparse hand-priced date):
   nominal slot arrays, present/absent flags, slot end minutes, the RTH end, ``p_end``,
   the ETH extremes and the RTH VWAP.
2. ``_forward``: the next slot's close minus this one in ticks, only when the next slot
   exists and is present in the same segment.
3. ``_trailing_baseline`` and ``_relative_events`` (through ``g1_body``): the 20-day
   same-slot baseline, the relative size, the frozen Q80 and the three event gates.
4. ``g2_events``: the running extreme of EARLIER present slots; the first present slot
   never fires.
5. ``g3_events``: one opening-range break per day, valued to the RTH end, with the slot
   that ends at the RTH end excluded.
6. ``g5_events``: the first close beyond the overnight range, at most one each way.
7. ``g0_autocorrelation``: Pearson r of consecutive return pairs, formed only where three
   consecutive slots are present.
8. ``select``: Benjamini-Hochberg across every record, the five selection conditions in
   their declared order, the 2.11-tick cost bar, the |t| x |estimate| ranking and the
   cap of 8.

The synthetic bars are built programmatically; every expected number below is either a
literal a reader can redo by hand or a longhand reference written out independently of
the module under test.
"""

from __future__ import annotations

import math
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from rules.xfa_rules import no_new_positions_time_ct
from sim.engine import BAR_COLUMNS
from strategy.research.g_timeframe._stylized_facts import (
    BASELINE_DAYS,
    BH_Q,
    COST_BAR_TICKS,
    FORMALIZATION_CAP,
    INELIGIBLE,
    M_STATS,
    MIN_BASELINE_OBS,
    MIN_EVENTS,
    MIN_SUBBLOCKS_AGREE,
    TOP_QUANTILE,
    DayData,
    _forward,
    _relative_events,
    _trailing_baseline,
    build_days,
    g0_autocorrelation,
    g1_body,
    g2_events,
    g3_events,
    g5_events,
    select,
)
from strategy.research.g_timeframe.resample import (
    ETH_NOMINAL_END,
    RTH_NOMINAL_END,
    RTH_START,
    TICK,
    TIMEFRAMES,
    annotate_session,
    coarse_bars,
)

CT = ZoneInfo("America/Chicago")
BASE_PRICE = 6000.00
INSTRUMENT = 4242

# The session grid, as minutes from the 17:00 CT reopen (resample.session_minute).
SESSION_MINUTES = 1328  # sm 0 (17:00 CT) .. sm 1327 (15:07 CT), inclusive
SM_0830 = 930           # == RTH_START
SM_1459 = 1319          # the last 1-minute bar before a normal RTH end
SM_1500 = 1320          # == RTH_NOMINAL_END
SM_1158 = 1138          # 11:58 CT: no new positions before a 12:15 CT early close
HALT_1215 = "12:15"
HALT_LAST_MINUTE = 1154  # 12:14 CT: the last bar an early-close day prints
RTH_SPIKE_MINUTE = 1000  # 09:40 CT: a deliberate RTH-only high and low
SPIKE_HIGH = 7000.00
SPIKE_LOW = 5000.00

TRADE_DATES = (date(2025, 9, 2), date(2025, 9, 3), date(2025, 9, 4))
HALT_DATE = TRADE_DATES[2]

# Declared slot counts on a normal day (declaration R3), restated as nominal array lengths.
DECLARED_SLOTS = {"ETH": {5: 186, 15: 62, 30: 31, 60: 15},
                  "RTH": {5: 78, 15: 26, 30: 13, 60: 6}}


# ------------------------------------------------------------------- synthetic frame ----
def ts_event_ns(trade_date: date, sm: int) -> int:
    """UTC ns of the bar opening ``sm`` minutes after the 17:00 CT reopen of ``trade_date``."""
    reopen = datetime.combine(trade_date - timedelta(days=1), time(17, 0), tzinfo=CT)
    return int((reopen + timedelta(minutes=sm)).astimezone(UTC).timestamp()) * 10**9


def bar_row(trade_date: date, sm: int, open_: float, high: float, low: float, close: float,
            volume: int, early_halt_ct: str = "") -> dict:
    return {
        "ts_event": ts_event_ns(trade_date, sm),
        "open": open_, "high": high, "low": low, "close": close, "volume": volume,
        "instrument_id": INSTRUMENT, "raw_symbol": "MESZ5",
        "trade_date": trade_date.isoformat(),
        "in_flatten_window": False, "in_no_new_positions_window": False,
        "early_halt_ct": early_halt_ct, "in_scheduled_closure": False,
        "is_roll_session": False, "gap_before_minutes": 0, "vendor_degraded_day": False,
    }


def walking_row(trade_date: date, sm: int, seq: int, early_halt_ct: str) -> dict:
    """One 1-minute bar: open = 6000.00 + seq ticks, with a deterministic high/low wobble.

    The bar opening at 09:40 CT carries an extreme high and low, so that a day's own
    high/low sit inside RTH and can never be confused with its ETH high/low.
    """
    o = BASE_PRICE + seq * TICK
    high = SPIKE_HIGH if sm == RTH_SPIKE_MINUTE else o + TICK * (2 + sm % 4)
    low = SPIKE_LOW if sm == RTH_SPIKE_MINUTE else o - TICK * (1 + sm % 3)
    return bar_row(trade_date, sm, o, high, low, o + TICK, 1 + sm % 5, early_halt_ct)


def _build_walking_frame() -> tuple[pd.DataFrame, dict[tuple[date, int], dict]]:
    rows, by_key, seq = [], {}, 0
    for trade_date in TRADE_DATES:
        halt = HALT_1215 if trade_date == HALT_DATE else ""
        last = HALT_LAST_MINUTE if trade_date == HALT_DATE else SESSION_MINUTES - 1
        for sm in range(last + 1):
            row = walking_row(trade_date, sm, seq, halt)
            rows.append(row)
            by_key[(trade_date, sm)] = row
            seq += 1
    return pd.DataFrame(rows, columns=list(BAR_COLUMNS)), by_key


WALKING_FRAME, ROWS = _build_walking_frame()

# A sparse, hand-priced trade date: every typical price (H+L+C)/3 is a whole number, so
# the VWAP below is arithmetic a reader can redo without a computer.
HAND_DATE = date(2025, 9, 9)
HAND_ROWS = (
    # (sm, open, high, low, close, volume)
    (0, 5985.00, 5990.00, 5980.00, 5985.00, 10),    # ETH slot 0, 17:00 CT
    (1, 5985.00, 5988.00, 5982.00, 5986.00, 10),    # ETH slot 0, 17:01 CT
    (930, 6000.00, 6002.00, 6000.00, 6001.00, 1),   # RTH slot 0 at tf 5: typical 6001.00
    (931, 6001.00, 6002.00, 6000.00, 6001.00, 2),
    (932, 6001.00, 6002.00, 6000.00, 6001.00, 3),
    (933, 6001.00, 6002.00, 6000.00, 6001.00, 4),
    (934, 6001.00, 6002.00, 6000.00, 6001.00, 5),
    (935, 6011.00, 6012.00, 6010.00, 6011.00, 5),   # RTH slot 1 at tf 5: typical 6011.00
    (936, 6011.00, 6012.00, 6010.00, 6011.00, 5),
    (937, 6011.00, 6012.00, 6010.00, 6011.00, 5),
    (938, 6011.00, 6012.00, 6010.00, 6011.00, 5),
    (939, 6011.00, 6012.00, 6010.00, 6011.00, 5),
)
HAND_FRAME = pd.DataFrame([bar_row(HAND_DATE, *spec) for spec in HAND_ROWS],
                          columns=list(BAR_COLUMNS))


def days_for(frame: pd.DataFrame, tf: int, dates: tuple[date, ...]) -> list[DayData]:
    """``run_timeframe``'s own preparation, minus the parts that load real data."""
    bars = annotate_session(frame)
    bars["trade_date_obj"] = pd.to_datetime(bars["trade_date"].astype(str)).dt.date
    return build_days(bars, coarse_bars(frame, tf), tf, list(dates))


DAYS_BY_TF = {tf: days_for(WALKING_FRAME, tf, TRADE_DATES) for tf in TIMEFRAMES}
HAND_DAY = days_for(HAND_FRAME, 5, (HAND_DATE,))[0]


# --------------------------------------------------------------- longhand references ----
def reference_eth_extremes(trade_date: date) -> tuple[float, float]:
    """Declaration G5: the max high and min low of the ETH 1-minute bars, longhand."""
    rows = [r for (d, sm), r in ROWS.items() if d == trade_date and sm < ETH_NOMINAL_END]
    return max(r["high"] for r in rows), min(r["low"] for r in rows)


def reference_vwap(trade_date: date, rth_end: int, ends: np.ndarray) -> list[float]:
    """Declaration G4, longhand: cumulative typical x volume / volume over RTH bars."""
    rth = [(sm, r) for (d, sm), r in sorted(ROWS.items())
           if d == trade_date and RTH_START <= sm < rth_end]
    out = []
    for end in ends:
        total_tv = total_v = 0.0
        for sm, r in rth:
            if sm < end:
                total_tv += (r["high"] + r["low"] + r["close"]) / 3.0 * r["volume"]
                total_v += r["volume"]
        out.append(total_tv / total_v if total_v else math.nan)
    return out


# ------------------------------------------------------------------ hand-built DayData ----
HAND_TF = 30  # 31 ETH slots, 13 RTH slots: the smallest nominal arrays that stay realistic
HAND_DATES = tuple(date(2026, 1, 1) + timedelta(days=i) for i in range(30))


def slot_bar(open_: float, close: float, high: float | None = None, low: float | None = None,
             volume: float = 100.0) -> tuple[float, float, float, float, float]:
    return (open_,
            max(open_, close) if high is None else high,
            min(open_, close) if low is None else low,
            close, volume)


def hand_segment(segment: str, bars: dict[int, tuple], tf: int) -> dict[str, np.ndarray]:
    nominal = ETH_NOMINAL_END if segment == "ETH" else RTH_NOMINAL_END - RTH_START
    n = nominal // tf
    start = 0 if segment == "ETH" else RTH_START
    arrays = {k: np.full(n, np.nan) for k in ("open", "high", "low", "close", "volume")}
    arrays["present"] = np.zeros(n, dtype=bool)
    arrays["end"] = start + (np.arange(n) + 1) * tf
    for j, values in bars.items():
        for key, value in zip(("open", "high", "low", "close", "volume"), values, strict=True):
            arrays[key][j] = value
        arrays["present"][j] = True
    return arrays


def hand_day(obs_date: date, *, rth: dict[int, tuple] | None = None,
             eth: dict[int, tuple] | None = None, rth_end: int | None = RTH_NOMINAL_END,
             p_end: float | None = None, eth_high: float | None = None,
             eth_low: float | None = None, vwap: list[float] | None = None,
             tf: int = HAND_TF) -> DayData:
    seg = {"ETH": hand_segment("ETH", eth or {}, tf), "RTH": hand_segment("RTH", rth or {}, tf)}
    n_rth = len(seg["RTH"]["close"])
    return DayData(obs_date=obs_date, seg=seg, rth_end=rth_end, p_end=p_end,
                   eth_high=eth_high, eth_low=eth_low,
                   vwap=np.full(n_rth, np.nan) if vwap is None else np.asarray(vwap, float))


# ============================================================== 1. build_days ====
def test_build_days_slot_arrays_have_the_declared_nominal_length_at_every_timeframe() -> None:
    # Arrange: the declaration's R3 counts, restated as nominal array lengths.
    assert {tf: ETH_NOMINAL_END // tf for tf in TIMEFRAMES} == DECLARED_SLOTS["ETH"]
    assert {tf: (RTH_NOMINAL_END - RTH_START) // tf for tf in TIMEFRAMES} == DECLARED_SLOTS["RTH"]

    # Act / Assert: every array of every segment of every day has the nominal length,
    # early close or not.
    for tf in TIMEFRAMES:
        for day in DAYS_BY_TF[tf]:
            for segment, per_tf in DECLARED_SLOTS.items():
                for key in ("open", "high", "low", "close", "volume", "present", "end"):
                    assert len(day.seg[segment][key]) == per_tf[tf]
            assert len(day.vwap) == DECLARED_SLOTS["RTH"][tf]


def test_build_days_slot_end_minutes_are_whole_timeframes_from_the_segment_start() -> None:
    for tf in TIMEFRAMES:
        day = DAYS_BY_TF[tf][0]
        # Act / Assert
        assert list(day.seg["ETH"]["end"]) == [tf * (j + 1)
                                               for j in range(DECLARED_SLOTS["ETH"][tf])]
        assert list(day.seg["RTH"]["end"]) == [RTH_START + tf * (j + 1)
                                               for j in range(DECLARED_SLOTS["RTH"][tf])]
        assert day.seg["ETH"]["end"][-1] <= ETH_NOMINAL_END
        assert day.seg["RTH"]["end"][-1] <= RTH_NOMINAL_END
    # R3's dropped stubs: at 60 minutes ETH ends at 08:00 CT and RTH at 14:30 CT.
    assert DAYS_BY_TF[60][0].seg["ETH"]["end"][-1] == 900
    assert DAYS_BY_TF[60][0].seg["RTH"]["end"][-1] == 1290
    # Below 60 minutes both segments tile exactly.
    for tf in (5, 15, 30):
        assert DAYS_BY_TF[tf][0].seg["ETH"]["end"][-1] == ETH_NOMINAL_END
        assert DAYS_BY_TF[tf][0].seg["RTH"]["end"][-1] == RTH_NOMINAL_END


def test_build_days_marks_every_slot_present_on_a_full_normal_trade_date() -> None:
    for tf in TIMEFRAMES:
        for day in DAYS_BY_TF[tf][:2]:  # the two normal dates
            # Act / Assert
            assert day.seg["ETH"]["present"].all()
            assert day.seg["RTH"]["present"].all()
            assert np.isfinite(day.seg["RTH"]["close"]).all()
            assert np.isfinite(day.seg["ETH"]["open"]).all()


def test_build_days_marks_the_rth_slots_past_an_early_close_absent() -> None:
    for tf in TIMEFRAMES:
        # Arrange: the 12:15 CT halt stops new positions at 11:58 CT, session minute 1138.
        day = DAYS_BY_TF[tf][2]
        expected_present = (SM_1158 - RTH_START) // tf  # 41 / 13 / 6 / 3

        # Act
        present = day.seg["RTH"]["present"]

        # Assert: the surviving slots are 0..n-1, and the last one ends at or before 11:58
        # (R3: a slot that would cross the end is dropped, never truncated).
        assert int(present.sum()) == expected_present
        assert list(np.flatnonzero(present)) == list(range(expected_present))
        assert day.seg["RTH"]["end"][expected_present - 1] <= SM_1158
        assert day.seg["RTH"]["end"][expected_present] > SM_1158
        assert np.isnan(day.seg["RTH"]["close"][expected_present])
        assert day.seg["ETH"]["present"].all()  # an afternoon halt leaves ETH untouched


def test_build_days_rth_end_is_1320_on_a_normal_day_and_1138_before_a_1215_ct_halt() -> None:
    # Arrange: the flatten is 15 minutes before the halt, no new positions 2 earlier still.
    assert no_new_positions_time_ct(time(12, 15)) == time(11, 58)

    for tf in TIMEFRAMES:
        # Act
        normal_a, normal_b, halt = DAYS_BY_TF[tf]

        # Assert
        assert normal_a.rth_end == normal_b.rth_end == RTH_NOMINAL_END == SM_1500
        assert halt.rth_end == SM_1158 == 1138


def test_build_days_p_end_is_the_close_of_the_last_1_minute_bar_before_the_rth_end() -> None:
    for tf in TIMEFRAMES:
        # Act
        normal, _, halt = DAYS_BY_TF[tf]

        # Assert: 14:59 CT on a normal day (open 6000.00 + 1319 ticks, close one tick up).
        assert normal.p_end == ROWS[(TRADE_DATES[0], SM_1459)]["close"] == 6330.00
        # 11:57 CT before the early close, NOT the day's last printed bar at 12:14 CT.
        assert halt.p_end == ROWS[(HALT_DATE, SM_1158 - 1)]["close"]
        assert halt.p_end != ROWS[(HALT_DATE, HALT_LAST_MINUTE)]["close"]


def test_build_days_eth_high_and_low_come_from_the_eth_1_minute_bars_only() -> None:
    for tf in TIMEFRAMES:
        for day, trade_date in zip(DAYS_BY_TF[tf], TRADE_DATES, strict=True):
            # Act
            high, low = reference_eth_extremes(trade_date)

            # Assert
            assert (day.eth_high, day.eth_low) == (high, low)
            # The day's own extremes are the 09:40 CT RTH spike and are not these.
            assert day.eth_high < SPIKE_HIGH
            assert day.eth_low > SPIKE_LOW
    # Trade date 1, longhand: the ETH high is 6233.00 (session minutes 927 and 929) and the
    # ETH low is 5999.75 (session minutes 0, 1 and 2).
    assert (DAYS_BY_TF[5][0].eth_high, DAYS_BY_TF[5][0].eth_low) == (6233.00, 5999.75)


def test_build_days_vwap_at_each_slot_end_matches_a_longhand_cumulative_mean() -> None:
    tf = 30
    for day, trade_date in zip(DAYS_BY_TF[tf], TRADE_DATES, strict=True):
        # Act
        expected = reference_vwap(trade_date, day.rth_end, day.seg["RTH"]["end"])

        # Assert
        assert list(day.vwap) == pytest.approx(expected, rel=1e-12, nan_ok=True)


def test_build_days_vwap_equals_a_hand_computed_typical_price_volume_mean() -> None:
    # Arrange: RTH slot 0 (08:30-08:35 CT) holds five bars of typical price 6001.00 on
    # volumes 1+2+3+4+5 = 15; slot 1 (08:35-08:40) five of typical 6011.00 on 25.
    day = HAND_DAY

    # Act / Assert
    assert day.vwap[0] == 6001.00                       # 90,015 / 15
    assert day.vwap[1] == 6007.25                       # (90,015 + 150,275) / 40
    # Every later slot end is past the last RTH bar, so the cumulative mean stops moving.
    assert set(day.vwap[2:]) == {6007.25}


def test_build_days_on_a_sparse_date_marks_only_the_slots_that_have_bars() -> None:
    # Arrange / Act: two ETH bars in slot 0, ten RTH bars in slots 0 and 1, at tf 5.
    day = HAND_DAY

    # Assert
    assert list(np.flatnonzero(day.seg["ETH"]["present"])) == [0]
    assert list(np.flatnonzero(day.seg["RTH"]["present"])) == [0, 1]
    assert (day.eth_high, day.eth_low) == (5990.00, 5980.00)  # ETH bars only
    assert day.p_end == 6011.00                               # close of the 08:39 CT bar
    assert day.rth_end == RTH_NOMINAL_END


# ================================================================= 2. _forward ====
def test_forward_is_the_next_slots_close_minus_this_one_in_ticks() -> None:
    # Arrange: slots 0, 1 and 3 present; slot 2 absent.
    close = np.array([6000.00, 6002.50, np.nan, 6001.00])
    present = np.array([True, True, False, True])

    # Act / Assert
    assert _forward(close, present, 0) == (6002.50 - 6000.00) / TICK == 10.0
    assert _forward(close, present, 1) is None   # slot 2 is absent
    assert _forward(close, present, 3) is None   # the last slot has no next slot


def test_forward_is_none_at_the_last_slot_of_a_segment() -> None:
    # Arrange: no ETH -> RTH forward window exists, because each segment has its own array.
    close = np.array([6000.00, 6001.00])
    present = np.array([True, True])

    # Act / Assert
    assert _forward(close, present, 0) == 4.0
    assert _forward(close, present, 1) is None


# ============================ 3. _trailing_baseline and _relative_events (G1) ====
def test_trailing_baseline_averages_the_previous_20_days_that_have_that_slot() -> None:
    # Arrange: slot 0 present on all 21 days; slot 1 on only 9 of the first 20; slot 2 on
    # exactly 10; slot 3 never.
    assert (BASELINE_DAYS, MIN_BASELINE_OBS) == (20, 10)
    measure = np.full((21, 4), np.nan)
    measure[:, 0] = [1.0] * 20 + [99.0]
    measure[:9, 1] = 2.0
    measure[:10, 2] = 4.0

    # Act
    baseline = _trailing_baseline(measure, 20)

    # Assert
    assert baseline[0] == 1.0             # rows 0..19 only: the 21st day is not its own baseline
    assert math.isnan(baseline[1])        # 9 observations < the 10 required
    assert baseline[2] == 4.0             # exactly 10 observations is enough
    assert math.isnan(baseline[3])        # never present


def test_trailing_baseline_window_slides_with_the_day_index() -> None:
    # Arrange: the same column, read one day later, drops day 0 and takes in day 20.
    measure = np.full((21, 1), np.nan)
    measure[:, 0] = [1.0] * 20 + [99.0]

    # Act / Assert: (19 x 1.0 + 99.0) / 20 = 5.9
    assert _trailing_baseline(measure, 21)[0] == pytest.approx(5.9)


def g1_days_with_one_large_day() -> list[DayData]:
    """21 days: slot 0's |body| is 1.00, then 5.00 on the last; slot 2's body is always 0."""
    days = []
    for i, obs_date in enumerate(HAND_DATES[:BASELINE_DAYS + 1]):
        big = i == BASELINE_DAYS
        rth = {
            0: slot_bar(6000.00, 6005.00 if big else 6001.00),
            1: slot_bar(6005.00 if big else 6001.00, 6004.50 if big else 6000.50),
            2: slot_bar(6004.50 if big else 6000.50, 6004.50 if big else 6000.50),
        }
        days.append(hand_day(obs_date, rth=rth))
    return days


def test_relative_events_divide_the_body_by_its_trailing_same_slot_baseline() -> None:
    # Arrange
    days = g1_days_with_one_large_day()
    measure = np.abs(np.array([g1_body("RTH")(d) for d in days]))

    # Act
    baseline = _trailing_baseline(measure, BASELINE_DAYS)

    # Assert: slot 0's baseline is 1.00, slot 1's 0.50, slot 2's is 0 (every body is 0) and
    # slot 3 is never present.
    assert (baseline[0], baseline[1], baseline[2]) == (1.00, 0.50, 0.00)
    assert math.isnan(baseline[3])
    # The relative sizes on the last day: 5.00 / 1.00 and 0.50 / 0.50; slot 2's baseline of
    # 0 leaves its relative size undefined.
    assert measure[BASELINE_DAYS, 0] / baseline[0] == 5.0
    assert measure[BASELINE_DAYS, 1] / baseline[1] == 1.0


def test_relative_events_freeze_q80_as_numpys_80th_percentile_of_the_pooled_sizes() -> None:
    # Arrange
    days = g1_days_with_one_large_day()

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: only the 21st day contributes relative sizes (5.0 and 1.0); their 80th
    # percentile is numpy's linear interpolation, 1.0 + 0.8 x 4.0.
    assert TOP_QUANTILE == 0.80
    assert q80 == float(np.percentile(np.array([5.0, 1.0]), 80)) == pytest.approx(4.2)


def test_relative_events_drop_the_first_20_days_as_warm_up() -> None:
    # Arrange
    days = g1_days_with_one_large_day()

    # Act
    obs, _ = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: one observation day, the 21st; days 1-20 contribute neither events nor a day.
    assert [o.obs_date for o in obs] == [HAND_DATES[BASELINE_DAYS]]


def test_relative_events_value_an_event_as_sign_of_body_times_the_forward_move() -> None:
    # Arrange: on the 21st day slot 0 runs 6000.00 -> 6005.00 and slot 1 closes 6004.50.
    days = g1_days_with_one_large_day()

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: slot 0 alone clears Q80 = 4.2; its forward move is (6004.50 - 6005.00) / 0.25
    # = -2 ticks, signed by the body's +1.
    assert list(obs[0].data["x"]) == [-2.0]


def test_relative_events_treat_a_relative_size_exactly_at_q80_as_an_event() -> None:
    # Arrange: slot 1's body is 0 on every one of the first 20 days, so its baseline is 0
    # and its relative size is undefined. Slot 0 is then the only pooled observation on the
    # 21st day, which makes Q80 exactly its own relative size.
    days = []
    for i, obs_date in enumerate(HAND_DATES[:BASELINE_DAYS + 1]):
        big = i == BASELINE_DAYS
        rth = {0: slot_bar(6000.00, 6005.00 if big else 6001.00),
               1: slot_bar(6005.00 if big else 6001.00, 6004.50 if big else 6001.00)}
        days.append(hand_day(obs_date, rth=rth))

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: the gate is ">= Q80", so an observation sitting exactly on it is an event,
    # valued at (6004.50 - 6005.00) / 0.25 = -2 ticks.
    assert q80 == 5.0
    assert list(obs[0].data["x"]) == [-2.0]


def test_relative_events_sign_a_down_body_event_against_its_forward_move() -> None:
    # Arrange: the same 21 days, but the 21st day's large body is DOWN, 6005.00 -> 6000.00,
    # and the next slot closes one point higher at 6001.00.
    days = []
    for i, obs_date in enumerate(HAND_DATES[:BASELINE_DAYS + 1]):
        big = i == BASELINE_DAYS
        rth = {0: slot_bar(6005.00 if big else 6000.00, 6000.00 if big else 6001.00),
               1: slot_bar(6000.00 if big else 6001.00, 6001.00)}
        days.append(hand_day(obs_date, rth=rth))

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: the forward move is +4 ticks, but the body's sign is -1, so the event's
    # contribution to the continuation statistic is -4 ticks.
    assert q80 == 5.0
    assert list(obs[0].data["x"]) == [-4.0]


def test_relative_events_need_a_present_next_slot_even_when_the_size_clears_q80() -> None:
    # Arrange: slots 0 and 1 present for 20 days; on the 21st only slot 0 is present.
    days = []
    for i, obs_date in enumerate(HAND_DATES[:BASELINE_DAYS + 1]):
        if i == BASELINE_DAYS:
            rth = {0: slot_bar(6000.00, 6005.00)}
        else:
            rth = {0: slot_bar(6000.00, 6001.00), 1: slot_bar(6001.00, 6001.50)}
        days.append(hand_day(obs_date, rth=rth))

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert: the relative size is the only pooled value, so it IS Q80 and clears the
    # inclusive >= gate, but slot 1 is absent, so there is no forward move and no event.
    assert q80 == 5.0
    assert list(obs[0].data["x"]) == []


def test_relative_events_exclude_a_zero_body_even_when_it_clears_q80() -> None:
    # Arrange: eight slots, each with |body| 1.00 for 20 days, so every baseline is 1.00.
    # On the 21st day only slot 5 has a body; the other seven are flat, so the pooled
    # relative sizes are seven zeros and one 5.0, whose 80th percentile is exactly 0.
    days = []
    for i, obs_date in enumerate(HAND_DATES[:BASELINE_DAYS + 1]):
        if i == BASELINE_DAYS:
            rth = {j: slot_bar(6000.00 + j * 0.25, 6000.00 + j * 0.25) for j in range(5)}
            rth[5] = slot_bar(6000.00, 6005.00)
            rth[6] = slot_bar(6005.75, 6005.75)
            rth[7] = slot_bar(6006.00, 6006.00)
        else:
            rth = {j: slot_bar(6000.00 + j, 6001.00 + j) for j in range(8)}
        days.append(hand_day(obs_date, rth=rth))

    # Act
    obs, q80 = _relative_events(days, "RTH", g1_body("RTH"))

    # Assert
    assert q80 == float(np.percentile(np.array([0.0] * 7 + [5.0]), 80)) == 0.0
    # Slots 0-4, 6 and 7 pass the >= Q80 gate and are excluded only by body != 0.
    # Slot 5's forward move is (6005.75 - 6005.00) / 0.25 = +3 ticks.
    assert list(obs[0].data["x"]) == [3.0]


# ================================================================ 4. g2_events ====
def test_g2_fires_only_when_a_close_passes_the_extreme_of_earlier_present_slots() -> None:
    # Arrange: slot 0 sets high 6001.00 / low 5999.00; slot 1 stays inside; slot 2 closes
    # above the running high; slot 3 below the running low; slot 4 breaks up with no next
    # slot to measure against.
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6001.00, low=5999.00),
        1: slot_bar(6000.00, 6000.25, high=6000.50, low=5999.75),
        2: slot_bar(6000.25, 6002.00, high=6002.50, low=6000.00),
        3: slot_bar(6002.00, 5998.00, high=6002.25, low=5997.50),
        4: slot_bar(5998.00, 6003.00, high=6003.00, low=5998.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth)

    # Act
    obs = g2_events([day], "RTH")

    # Assert: up at slot 2, d = +1 x (5998.00 - 6002.00) / 0.25 = -16 ticks; down at slot
    # 3, d = -1 x (6003.00 - 5998.00) / 0.25 = -20 ticks. Slot 1 never fires (inside), and
    # slot 4 has no present next slot.
    assert list(obs[0].data["x"]) == [-16.0, -20.0]


def test_g2_never_fires_on_the_first_present_slot_of_a_segment() -> None:
    # Arrange: slots 0-2 absent, so the first present slot is 3 - however extreme it is.
    rth = {
        3: slot_bar(6000.00, 6009.00, high=6010.00, low=5990.00),
        4: slot_bar(6009.00, 6010.50, high=6011.00, low=6008.00),
        5: slot_bar(6010.50, 6012.00, high=6012.50, low=6010.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth)

    # Act
    obs = g2_events([day], "RTH")

    # Assert: only slot 4 fires, at (6012.00 - 6010.50) / 0.25 = +6 ticks. Slot 5 breaks up
    # too, but slot 6 is absent.
    assert list(obs[0].data["x"]) == [6.0]


def test_g2_treats_a_close_exactly_at_the_running_extreme_as_no_break() -> None:
    # Arrange: slot 1 closes exactly at the running high and slot 2 exactly at the running
    # low; only slot 3 passes one of them.
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6001.00, low=5999.00),
        1: slot_bar(6000.00, 6001.00, high=6001.00, low=5999.00),
        2: slot_bar(6001.00, 5999.00, high=6001.00, low=5999.00),
        3: slot_bar(5999.00, 6001.50, high=6002.00, low=5998.00),
        4: slot_bar(6001.50, 6000.00, high=6001.50, low=6000.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth)

    # Act
    obs = g2_events([day], "RTH")

    # Assert: the test is strict on both sides, so only slot 3 fires, at
    # (6000.00 - 6001.50) / 0.25 = -6 ticks.
    assert list(obs[0].data["x"]) == [-6.0]


def test_g2_gives_no_events_on_a_day_with_a_single_present_slot() -> None:
    # Arrange / Act
    day = hand_day(HAND_DATES[0], rth={0: slot_bar(6000.00, 6010.00)})
    obs = g2_events([day], "RTH")

    # Assert
    assert list(obs[0].data["x"]) == []
    assert obs[0].obs_date == HAND_DATES[0]


def test_g2_runs_on_the_eth_segment_with_the_same_rule() -> None:
    # Arrange
    eth = {
        0: slot_bar(6000.00, 6000.00, high=6001.00, low=5999.00),
        1: slot_bar(6000.00, 6001.50, high=6001.50, low=6000.00),
        2: slot_bar(6001.50, 6000.00, high=6001.75, low=5999.50),
    }
    day = hand_day(HAND_DATES[0], eth=eth)

    # Act
    obs = g2_events([day], "ETH")

    # Assert: slot 1 closes above slot 0's high; the forward move is
    # (6000.00 - 6001.50) / 0.25 = -6 ticks.
    assert list(obs[0].data["x"]) == [-6.0]


# ================================================================ 5. g3_events ====
def test_g3_takes_the_first_break_of_slot_zeros_range_and_values_it_to_the_rth_end() -> None:
    # Arrange: slot 0's range is 5990.00 .. 6010.00; slot 1 stays inside; slot 2 breaks up;
    # slot 3 would break down but the day is already decided.
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6010.00, low=5990.00),
        1: slot_bar(6000.00, 6005.00, high=6006.00, low=5999.00),
        2: slot_bar(6005.00, 6011.00, high=6011.50, low=6004.00),
        3: slot_bar(6011.00, 5980.00, high=6011.00, low=5979.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, p_end=6020.00)

    # Act
    obs = g3_events([day])

    # Assert: one event, valued to the RTH end, (6020.00 - 6011.00) / 0.25 = +36 ticks -
    # not to slot 3's close, which would give a different number.
    assert list(obs[0].data["x"]) == [36.0]


def test_g3_signs_a_downside_break_against_the_move_to_the_rth_end() -> None:
    # Arrange
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6010.00, low=5990.00),
        1: slot_bar(6000.00, 5985.00, high=6000.00, low=5984.00),
        2: slot_bar(5985.00, 5975.00, high=5985.00, low=5974.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, p_end=5975.00)

    # Act
    obs = g3_events([day])

    # Assert: d = -1 x (5975.00 - 5985.00) / 0.25 = +40 ticks.
    assert list(obs[0].data["x"]) == [40.0]


def test_g3_excludes_a_break_on_the_slot_that_ends_at_the_rth_end() -> None:
    # Arrange: at tf 30 the last RTH slot is index 12 and ends at session minute 1320,
    # exactly the RTH end, so there is no window left to measure.
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6010.00, low=5990.00),
        12: slot_bar(6000.00, 6011.00, high=6011.50, low=5999.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, p_end=6020.00)
    assert day.seg["RTH"]["end"][12] == day.rth_end == RTH_NOMINAL_END

    # Act
    obs = g3_events([day])

    # Assert
    assert list(obs[0].data["x"]) == []


def test_g3_gives_no_event_on_a_day_that_never_leaves_slot_zeros_range() -> None:
    # Arrange
    rth = {
        0: slot_bar(6000.00, 6000.00, high=6010.00, low=5990.00),
        1: slot_bar(6000.00, 6010.00, high=6010.00, low=5999.00),
        2: slot_bar(6010.00, 5990.00, high=6010.00, low=5990.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, p_end=6005.00)

    # Act
    obs = g3_events([day])

    # Assert: touching the range is not passing it; the test is strict.
    assert list(obs[0].data["x"]) == []


def test_g3_needs_slot_zero_present_and_a_defined_rth_end() -> None:
    # Arrange: the same breakout, but slot 0 is absent; then the same day with no p_end.
    rth = {
        1: slot_bar(6000.00, 6011.00, high=6011.50, low=5999.00),
        2: slot_bar(6011.00, 6015.00, high=6015.00, low=6010.00),
    }
    no_or = hand_day(HAND_DATES[0], rth=rth, p_end=6020.00)
    with_or = {0: slot_bar(6000.00, 6000.00, high=6010.00, low=5990.00), **rth}
    no_p_end = hand_day(HAND_DATES[1], rth=with_or, p_end=None)
    no_rth_end = hand_day(HAND_DATES[2], rth=with_or, p_end=6020.00, rth_end=None)

    # Act
    obs = g3_events([no_or, no_p_end, no_rth_end])

    # Assert
    assert [list(o.data["x"]) for o in obs] == [[], [], []]


# ================================================================ 6. g5_events ====
def test_g5_fires_once_above_the_overnight_high_and_once_below_its_low() -> None:
    # Arrange: the ETH range is 5990.00 .. 6010.00.
    rth = {
        0: slot_bar(6000.00, 6000.00),
        1: slot_bar(6000.00, 6011.00),
        2: slot_bar(6011.00, 6012.00),
        3: slot_bar(6012.00, 5985.00),
        4: slot_bar(5985.00, 5980.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, eth_high=6010.00, eth_low=5990.00)

    # Act
    obs = g5_events([day])

    # Assert: up at slot 1, +1 x (6012.00 - 6011.00) / 0.25 = +4 ticks; down at slot 3,
    # -1 x (5980.00 - 5985.00) / 0.25 = +20 ticks. Slot 2 is above the ETH high too, but
    # only the FIRST break each way counts.
    assert list(obs[0].data["x"]) == [4.0, 20.0]


def test_g5_needs_a_present_next_slot_for_each_break() -> None:
    # Arrange: the downside break is the last present slot of the day.
    rth = {
        0: slot_bar(6000.00, 6000.00),
        1: slot_bar(6000.00, 6011.00),
        2: slot_bar(6011.00, 5985.00),
    }
    day = hand_day(HAND_DATES[0], rth=rth, eth_high=6010.00, eth_low=5990.00)

    # Act
    obs = g5_events([day])

    # Assert: only the upside event survives, at (5985.00 - 6011.00) / 0.25 = -104 ticks.
    assert list(obs[0].data["x"]) == [-104.0]


def test_g5_gives_no_events_without_eth_bars_or_without_a_break() -> None:
    # Arrange
    rth = {j: slot_bar(6000.00 + j, 6001.00 + j) for j in range(4)}
    no_eth = hand_day(HAND_DATES[0], rth=rth, eth_high=None, eth_low=None)
    # The RTH closes run 6001.00 .. 6004.00 and touch both overnight bounds exactly; the
    # declaration's test is strict, so touching is not breaking.
    inside = hand_day(HAND_DATES[1], rth=rth, eth_high=6004.00, eth_low=6001.00)

    # Act
    obs = g5_events([no_eth, inside])

    # Assert
    assert [list(o.data["x"]) for o in obs] == [[], []]


# ======================================================= 7. g0_autocorrelation ====
def reference_lag1(days: list[DayData], segment: str) -> tuple[int, float]:
    """Longhand: pair consecutive log returns wherever three consecutive slots are present."""
    first, second = [], []
    for day in days:
        seg = day.seg[segment]
        n = len(seg["close"])
        for j in range(n - 2):
            if seg["present"][j] and seg["present"][j + 1] and seg["present"][j + 2]:
                first.append(math.log(seg["close"][j + 1] / seg["close"][j]))
                second.append(math.log(seg["close"][j + 2] / seg["close"][j + 1]))
    return len(first), float(np.corrcoef(first, second)[0, 1])


def test_g0_is_the_pearson_r_of_consecutive_coarse_bar_return_pairs() -> None:
    # Arrange: one day with six consecutive present slots, and one whose slot 2 is absent.
    closes_a = [6000.00, 6002.00, 6001.00, 6004.00, 6003.00, 6006.00]
    day_a = hand_day(HAND_DATES[0],
                     rth={j: slot_bar(c, c) for j, c in enumerate(closes_a)})
    day_b = hand_day(HAND_DATES[1], rth={
        0: slot_bar(6000.00, 6000.00), 1: slot_bar(6000.00, 6010.00),
        3: slot_bar(6005.00, 6005.00), 4: slot_bar(6005.00, 6007.00),
    })
    expected_pairs, expected_r = reference_lag1([day_a, day_b], "RTH")

    # Act
    got = g0_autocorrelation([day_a, day_b], "RTH")

    # Assert: the gap day contributes nothing, because no three of its slots are
    # consecutive and present.
    assert expected_pairs == 4
    assert got["segment"] == "RTH"
    assert got["n_pairs"] == expected_pairs
    assert got["lag1_autocorrelation"] == pytest.approx(expected_r)


def test_g0_returns_nan_when_there_are_fewer_than_two_return_pairs() -> None:
    # Arrange: three present slots give exactly one pair.
    day = hand_day(HAND_DATES[0], rth={j: slot_bar(6000.00 + j, 6000.00 + j)
                                       for j in range(3)})

    # Act
    got = g0_autocorrelation([day], "RTH")

    # Assert
    assert got["n_pairs"] == 1
    assert math.isnan(got["lag1_autocorrelation"])


# ==================================================================== 8. select ====
def record(stat_id: str, *, p: float, estimate: float | None, t: float = 1.0, agree: int = 4,
           n_events: int = 100, q80: float | None = 3.0) -> dict:
    """A ``compute_result`` record plus the fields ``run_timeframe`` adds to it."""
    fact, segment, tf = stat_id.split(".")
    return {
        "id": stat_id, "family": "G", "description": stat_id, "directional": True,
        "n": n_events, "estimate": estimate, "ci95_low": None, "ci95_high": None,
        "p_boot": p, "sub_block_estimates": [estimate] * 4, "sub_block_sign_agree": agree,
        "implied_edge_ticks": estimate,
        "tf": int(tf), "segment": segment, "fact": fact, "n_events": n_events, "q80": q80,
        "t_boot": t, "eligible": stat_id not in INELIGIBLE,
    }


def test_select_applies_the_five_conditions_in_their_declared_order() -> None:
    # Arrange: one record failing each condition, and one that qualifies.
    records = [
        record("G1.RTH.5", p=0.0, estimate=10.0),                    # 1: ineligible
        record("G2.RTH.15", p=0.9, estimate=10.0),                   # 2: not BH-significant
        record("G2.ETH.15", p=0.0001, estimate=10.0, agree=2),       # 3: sign agreement
        record("G3.RTH.15", p=0.0001, estimate=2.10),                # 4: under the cost bar
        record("G4.RTH.15", p=0.0001, estimate=10.0, n_events=29),   # 5: too few events
        record("G5.RTH.15", p=0.0001, estimate=-2.11, t=2.0),        # qualifies
    ]

    # Act
    out = select(records)

    # Assert: the declared constants, then the reason each record carries.
    assert (COST_BAR_TICKS, MIN_EVENTS, MIN_SUBBLOCKS_AGREE) == (2.11, 30, 3)
    reasons = {r["id"]: r["selection"] for r in records}
    assert reasons["G1.RTH.5"] == "ineligible by declaration (the re-tests' own mechanism and grid)"
    assert reasons["G2.RTH.15"] == f"not BH-significant at FDR 10% across M={M_STATS} (p=0.9)"
    assert reasons["G2.ETH.15"] == "sign agrees in only 2/4 sub-blocks"
    assert reasons["G3.RTH.15"] == "|edge| 2.10 ticks < 2.11 cost bar"
    assert reasons["G4.RTH.15"] == "only 29 events < 30"
    assert reasons["G5.RTH.15"] == "qualifies"
    # The 2.11-tick bar is inclusive and applies to |estimate|, so -2.11 clears it.
    assert out["qualifiers"] == ["G5.RTH.15"]
    assert out["formalized"] == ["G5.RTH.15"]
    assert out["cap"] == FORMALIZATION_CAP == 8


def test_select_reports_the_first_failed_condition_when_several_fail() -> None:
    # Arrange: every record below fails everything from its own condition onwards.
    records = [
        record("G3.RTH.5", p=0.9, estimate=0.0, agree=0, n_events=0),
        record("G1.RTH.60", p=0.9, estimate=0.0, agree=0, n_events=0),
        record("G2.RTH.60", p=0.0001, estimate=0.0, agree=0, n_events=0),
        record("G3.RTH.60", p=0.0001, estimate=0.0, agree=4, n_events=0),
    ]

    # Act
    select(records)

    # Assert
    reasons = [r["selection"] for r in records]
    assert reasons[0].startswith("ineligible by declaration")
    assert reasons[1].startswith("not BH-significant")
    assert reasons[2] == "sign agrees in only 0/4 sub-blocks"
    assert reasons[3] == "|edge| 0.00 ticks < 2.11 cost bar"


def test_select_rejects_every_ineligible_id_however_significant_it_is() -> None:
    # Arrange: the three ids the declaration reserves for the re-tests' own grid, each the
    # most significant, largest-edge record in the set.
    assert sorted(INELIGIBLE) == ["G1.ETH.5", "G1.RTH.5", "G3.RTH.5"]
    records = [record(stat_id, p=0.0, estimate=25.0, t=9.0) for stat_id in sorted(INELIGIBLE)]
    records.append(record("G5.RTH.30", p=0.0001, estimate=3.0, t=2.0))

    # Act
    out = select(records)

    # Assert: all four are BH-significant; only the eligible one can qualify.
    assert out["n_bh_significant"] == 4
    assert out["qualifiers"] == ["G5.RTH.30"]
    assert out["formalized"] == ["G5.RTH.30"]
    assert all(r["selection"].startswith("ineligible") for r in records[:3])


def eligible_and_ineligible_pool() -> list[dict]:
    """Three ineligible records with tiny p, one eligible at p = 0.035, six dead records."""
    pool = [record("G1.RTH.5", p=0.001, estimate=9.0),
            record("G1.ETH.5", p=0.002, estimate=9.0),
            record("G3.RTH.5", p=0.003, estimate=9.0),
            record("G4.RTH.30", p=0.035, estimate=5.0, t=2.0)]
    pool += [record(f"G2.RTH.{tf}", p=0.9, estimate=5.0) for tf in (5, 15, 30, 60)]
    pool += [record(f"G2.ETH.{tf}", p=0.9, estimate=5.0) for tf in (5, 15)]
    return pool


def test_select_runs_benjamini_hochberg_across_all_records_including_ineligible_ones() -> None:
    # Arrange: 10 records, q = 0.10, so rank k's threshold is k/10 x 0.10. The eligible
    # record sits at rank 4 (p = 0.035 <= 0.040) only because the three ineligible records
    # occupy ranks 1-3 of the same pool.
    assert BH_Q == 0.10
    records = eligible_and_ineligible_pool()

    # Act
    out = select(records)

    # Assert
    assert out["n_bh_significant"] == 4
    assert {r["id"] for r in records if r["bh_reject"]} == {
        "G1.RTH.5", "G1.ETH.5", "G3.RTH.5", "G4.RTH.30"}
    assert out["qualifiers"] == ["G4.RTH.30"]


def test_select_would_not_reject_that_record_if_the_ineligible_ones_were_dropped() -> None:
    # Arrange: the same pool with the three ineligible records removed. At m = 7 the
    # smallest p is 0.035, above rank 1's threshold of 0.10 / 7 = 0.0143.
    records = [r for r in eligible_and_ineligible_pool() if r["eligible"]]

    # Act
    out = select(records)

    # Assert: the counterfactual that pins "across all records" as load-bearing.
    assert len(records) == 7
    assert out["n_bh_significant"] == 0
    assert out["qualifiers"] == []


def test_select_ranks_qualifiers_by_absolute_t_times_absolute_estimate_and_caps_at_eight() -> None:
    # Arrange: ten qualifying records, with |t| rising and |estimate| falling and signs
    # alternating, so that ranking by |t| alone, by |estimate| alone, or by the signed
    # product would each give a different order from the declared |t| x |estimate|.
    sizes = ((1.0, 30.00), (2.0, 14.50), (3.0, 9.00), (4.0, 6.50), (5.0, 5.00),
             (6.0, 4.00), (7.0, 3.00), (8.0, 2.50), (9.0, 2.20), (10.0, 2.11))
    products = [t * estimate for t, estimate in sizes]
    assert products == [30.0, 29.0, 27.0, 26.0, 25.0, 24.0, 21.0, 20.0,
                        pytest.approx(19.8), pytest.approx(21.1)]
    records = [record(f"G{2 + k % 4}.RTH.{(5, 15, 30, 60)[k % 4]}", p=0.0001,
                      estimate=estimate * (-1) ** k, t=t)
               for k, (t, estimate) in enumerate(sizes)]
    for k, r in enumerate(records):
        r["id"] = f"S{k}"  # distinct ids, so the ranking is unambiguous
    assert all(r["eligible"] for r in records)

    # Act
    out = select(records)

    # Assert: S9 (the smallest estimate, exactly at the cost bar, but the largest |t|)
    # ranks seventh, ahead of S6, S7 and S8, and S8 is the one qualifier the cap drops.
    assert out["n_bh_significant"] == 10
    assert out["qualifiers"] == ["S0", "S1", "S2", "S3", "S4", "S5", "S9", "S6", "S7", "S8"]
    assert out["formalized"] == ["S0", "S1", "S2", "S3", "S4", "S5", "S9", "S6"]
    assert len(out["formalized"]) == FORMALIZATION_CAP == 8


def test_select_formalizes_nothing_when_no_record_qualifies() -> None:
    # Arrange
    records = [record(f"G2.RTH.{tf}", p=0.9, estimate=0.5) for tf in (5, 15, 30, 60)]

    # Act
    out = select(records)

    # Assert
    assert out == {"n_bh_significant": 0, "qualifiers": [], "formalized": [],
                   "cap": FORMALIZATION_CAP}
