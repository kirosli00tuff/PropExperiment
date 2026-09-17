"""Tests for funnel/null_generator.py (Stage B, Task 2): the zero-edge daily
P&L generator.

Long-run tolerance used below: for n independent-ish segment draws, the
sample mean's standard error is sd/sqrt(n); we accept |mean(pnl_ticks)| up to
4 such standard errors (a four-sigma bound, chance of a false failure on a
truly-zero-mean process is on the order of 1e-4), computed from the draw's
own sample sd so nothing is pasted from a prior run.
"""

from __future__ import annotations

import math
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from data.research_bars import RESEARCH_SERIES_PATH
from funnel.null_generator import (
    RTH_OPEN_MINUTE_CT,
    NullDayGenerator,
    SegmentTable,
    build_segment_table,
    calibration_summary,
    fair_signs,
    load_null_generator,
    stationary_bootstrap_indices,
)

CT = ZoneInfo("America/Chicago")


# ============================================================== synthetic bars ====
def _ts_ns(trade_date: str, minute_ct: int) -> int:
    """UTC nanosecond bar-open timestamp for a CT minute-of-day on ``trade_date``.

    January dates are CST (UTC-6): 08:30 CT == 14:30 UTC, verified directly
    against ``zoneinfo`` (no network) before writing this helper.
    """
    year, month, day = (int(part) for part in trade_date.split("-"))
    local = datetime(year, month, day, minute_ct // 60, minute_ct % 60, tzinfo=CT)
    return int(local.timestamp()) * 1_000_000_000


def _ramp_row(minute_ct: int, index: int, base: float) -> dict:
    """One bar on the 0.25 grid: open = base + index, close = open + 1 tick,
    high = open + 2 ticks, low = open - 1 tick."""
    open_price = base + index * 1.0
    return {
        "minute_ct": minute_ct,
        "open": open_price,
        "close": open_price + 0.25,
        "high": open_price + 0.5,
        "low": open_price - 0.25,
    }


def make_day(
    trade_date: str,
    n_rth: int,
    *,
    rth_start_minute: int = RTH_OPEN_MINUTE_CT,
    pre_open: int = 0,
    flatten: int = 0,
    base: float = 5000.0,
) -> pd.DataFrame:
    """One synthetic trade date: optional pre-08:30 bars, ``n_rth`` RTH bars on
    a linear ramp, then optional flatten-window bars. Pre-open bars are before
    ``RTH_OPEN_MINUTE_CT`` and flatten bars carry ``in_flatten_window=True`` --
    both must be invisible to ``build_segment_table``.
    """
    rows: list[dict] = []
    for k in range(pre_open):
        minute = rth_start_minute - pre_open + k
        row = _ramp_row(minute, k, base - 1000.0)
        row["in_flatten_window"] = False
        rows.append(row)
    for i in range(n_rth):
        minute = rth_start_minute + i
        row = _ramp_row(minute, i, base)
        row["in_flatten_window"] = False
        rows.append(row)
    for k in range(flatten):
        minute = rth_start_minute + n_rth + k
        row = _ramp_row(minute, n_rth + k, base + 1000.0)
        row["in_flatten_window"] = True
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame["ts_event"] = [_ts_ns(trade_date, m) for m in frame["minute_ct"]]
    frame["trade_date"] = trade_date
    return frame.drop(columns=["minute_ct"])


def _table(move: np.ndarray, low: np.ndarray, high: np.ndarray) -> SegmentTable:
    """Build a ``SegmentTable`` directly from arrays, bypassing bar parsing and
    the holdout/embargo refusal (those are ``build_segment_table``'s job, and
    the real dates it refuses on are covered by the tests that call it)."""
    move = np.asarray(move, dtype=np.int64)
    low = np.asarray(low, dtype=np.int64)
    high = np.asarray(high, dtype=np.int64)
    n_days, segs = move.shape
    zeros = np.zeros((n_days, segs), dtype=np.int64)
    return SegmentTable(
        trade_dates=tuple(f"day-{i:06d}" for i in range(n_days)),
        segments_per_day=segs,
        move_ticks=move,
        low_ticks=low,
        high_ticks=high,
        entry_minute_ct=zeros,
        exit_minute_ct=zeros,
    )


# ============================================================== build_segment_table ====
def test_build_segment_table_two_segments_hand_computed() -> None:
    """8 RTH bars split 4+4 (np.array_split(range(8), 2)); 2 pre-open bars must
    be ignored. Bar i (i=0..7, minute 510+i): open=5000+i, close=open+0.25,
    high=open+0.5, low=open-0.25 (ticks: multiply by 4).
    """
    bars = make_day("2026-01-06", n_rth=8, pre_open=2)
    table = build_segment_table(bars, 2)

    assert table.trade_dates == ("2026-01-06",)
    assert table.skipped_trade_dates == ()

    # segment 0 = bars 0..3 (minutes 510..513):
    #   entry = open_0 = 5000.00 (tick 20000)
    #   exit  = close_3 = (5000+3)+0.25 = 5003.25 (tick 20013); move = 20013-20000 = 13
    #   low   = low_0 = 5000-0.25 = 4999.75 (tick 19999); low_ticks = 19999-20000 = -1
    #   high  = high_3 = (5000+3)+0.5 = 5003.5 (tick 20014); high_ticks = 20014-20000 = 14
    # segment 1 = bars 4..7 (minutes 514..517):
    #   entry = open_4 = 5004.00 (tick 20016)
    #   exit  = close_7 = (5000+7)+0.25 = 5007.25 (tick 20029); move = 20029-20016 = 13
    #   low   = low_4 = 5004-0.25 = 5003.75 (tick 20015); low_ticks = 20015-20016 = -1
    #   high  = high_7 = (5000+7)+0.5 = 5007.5 (tick 20030); high_ticks = 20030-20016 = 14
    assert table.move_ticks.tolist() == [[13, 13]]
    assert table.low_ticks.tolist() == [[-1, -1]]
    assert table.high_ticks.tolist() == [[14, 14]]
    # entry minute = first bar's own minute; exit minute = last bar's minute + 1
    assert table.entry_minute_ct.tolist() == [[510, 514]]
    assert table.exit_minute_ct.tolist() == [[514, 518]]


def test_build_segment_table_three_segments_hand_computed() -> None:
    """8 RTH bars split 3+3+2 (np.array_split(range(8), 3))."""
    bars = make_day("2026-01-06", n_rth=8)
    table = build_segment_table(bars, 3)

    # segment 0 = bars 0..2 (minutes 510..512):
    #   entry=open_0=5000.00(tick20000); exit=close_2=5002.25(tick20009); move=9
    #   low=low_0=4999.75(tick19999) -> -1; high=high_2=5002.5(tick20010) -> 10
    # segment 1 = bars 3..5 (minutes 513..515):
    #   entry=open_3=5003.00(tick20012); exit=close_5=5005.25(tick20021); move=9
    #   low=low_3=5002.75(tick20011) -> -1; high=high_5=5005.5(tick20022) -> 10
    # segment 2 = bars 6..7 (minutes 516..517):
    #   entry=open_6=5006.00(tick20024); exit=close_7=5007.25(tick20029); move=5
    #   low=low_6=5005.75(tick20023) -> -1; high=high_7=5007.5(tick20030) -> 6
    assert table.move_ticks.tolist() == [[9, 9, 5]]
    assert table.low_ticks.tolist() == [[-1, -1, -1]]
    assert table.high_ticks.tolist() == [[10, 10, 6]]
    assert table.entry_minute_ct.tolist() == [[510, 513, 516]]
    assert table.exit_minute_ct.tolist() == [[513, 516, 518]]


def test_day_with_wrong_first_bar_is_skipped() -> None:
    good = make_day("2026-01-06", n_rth=8)
    bad = make_day("2026-01-07", n_rth=8, rth_start_minute=RTH_OPEN_MINUTE_CT + 1)
    table = build_segment_table(pd.concat([good, bad], ignore_index=True), 2)
    assert table.trade_dates == ("2026-01-06",)
    assert table.skipped_trade_dates == ("2026-01-07",)


def test_day_with_fewer_bars_than_segments_is_skipped() -> None:
    good = make_day("2026-01-06", n_rth=8)
    bad = make_day("2026-01-07", n_rth=1)  # T=2 needs >= 2 RTH bars
    table = build_segment_table(pd.concat([good, bad], ignore_index=True), 2)
    assert table.trade_dates == ("2026-01-06",)
    assert table.skipped_trade_dates == ("2026-01-07",)


def test_flatten_window_bars_are_excluded_from_segments() -> None:
    with_extra = make_day("2026-01-06", n_rth=8, pre_open=2, flatten=3)
    without_extra = make_day("2026-01-07", n_rth=8)
    t1 = build_segment_table(with_extra, 2)
    t2 = build_segment_table(without_extra, 2)
    assert np.array_equal(t1.move_ticks, t2.move_ticks)
    assert np.array_equal(t1.low_ticks, t2.low_ticks)
    assert np.array_equal(t1.high_ticks, t2.high_ticks)
    assert np.array_equal(t1.entry_minute_ct, t2.entry_minute_ct)
    assert np.array_equal(t1.exit_minute_ct, t2.exit_minute_ct)


def test_segment_table_arrays_are_read_only() -> None:
    table = build_segment_table(make_day("2026-01-06", n_rth=8), 2)
    with pytest.raises(ValueError):
        table.move_ticks[0, 0] = 999
    with pytest.raises(ValueError):
        table.low_ticks[0, 0] = 999
    with pytest.raises(ValueError):
        table.high_ticks[0, 0] = 999


# ============================================================== refusals ====
def test_holdout_date_is_refused_with_message() -> None:
    with pytest.raises(ValueError, match="holdout"):
        build_segment_table(make_day("2026-06-22", n_rth=1), 1)


def test_embargo_date_is_refused_with_message() -> None:
    with pytest.raises(ValueError, match="embargo"):
        build_segment_table(make_day("2026-06-16", n_rth=1), 1)


def test_unsorted_ts_event_raises() -> None:
    trade_date = "2026-01-06"
    bars = pd.DataFrame({
        "ts_event": [
            _ts_ns(trade_date, RTH_OPEN_MINUTE_CT + 1),
            _ts_ns(trade_date, RTH_OPEN_MINUTE_CT),
        ],
        "open": [5000.0, 5000.0],
        "high": [5000.5, 5000.5],
        "low": [4999.75, 4999.75],
        "close": [5000.25, 5000.25],
        "trade_date": [trade_date, trade_date],
        "in_flatten_window": [False, False],
    })
    with pytest.raises(ValueError):
        build_segment_table(bars, 1)


def test_off_grid_price_raises() -> None:
    trade_date = "2026-01-06"
    bars = pd.DataFrame({
        "ts_event": [_ts_ns(trade_date, RTH_OPEN_MINUTE_CT)],
        "open": [5000.00],
        "high": [5000.10],  # not a multiple of 0.25
        "low": [4999.75],
        "close": [5000.25],
        "trade_date": [trade_date],
        "in_flatten_window": [False],
    })
    with pytest.raises(ValueError):
        build_segment_table(bars, 1)


def test_missing_column_raises() -> None:
    trade_date = "2026-01-06"
    bars = pd.DataFrame({
        "ts_event": [_ts_ns(trade_date, RTH_OPEN_MINUTE_CT)],
        "open": [5000.0],
        "high": [5000.5],
        "low": [4999.75],
        # "close" is missing
        "trade_date": [trade_date],
        "in_flatten_window": [False],
    })
    with pytest.raises(ValueError):
        build_segment_table(bars, 1)


def test_segments_per_day_zero_raises() -> None:
    with pytest.raises(ValueError):
        build_segment_table(make_day("2026-01-06", n_rth=1), 0)


# ============================================================== fair_signs / zero-edge ====
def test_fair_signs_only_returns_plus_or_minus_one() -> None:
    signs = fair_signs(np.random.default_rng(7), (5000,))
    assert set(np.unique(signs).tolist()) <= {-1, 1}


def test_side_is_identical_across_differently_biased_tables_same_seed() -> None:
    """The side comes from ``fair_signs(rng, shape)`` alone: it reads no data,
    so two tables with opposite drift must draw bit-identical side arrays
    given the same seed and the same (n_days, T) shape."""
    n_days, segs = 40, 4
    table_pos = _table(
        np.full((n_days, segs), 40), np.full((n_days, segs), -5), np.full((n_days, segs), 45)
    )
    table_neg = _table(
        np.full((n_days, segs), -7), np.full((n_days, segs), -30), np.full((n_days, segs), 3)
    )
    draws_pos = NullDayGenerator(table_pos).draw(np.random.default_rng(2024), 1000)
    draws_neg = NullDayGenerator(table_neg).draw(np.random.default_rng(2024), 1000)
    assert np.array_equal(draws_pos.side, draws_neg.side)
    assert set(np.unique(draws_pos.side).tolist()) <= {-1, 1}


def test_long_run_pnl_mean_is_zero_while_source_drift_is_positive() -> None:
    """See module docstring for the tolerance. 100,000 days * T=4 = 400,000
    segments."""
    pattern = np.array([10, 30, 50, 70], dtype=np.int64)  # mean (10+30+50+70)/4 = 40
    n_source_days, segs = 310, 4
    move = np.tile(pattern, (n_source_days, 1))
    low = np.full((n_source_days, segs), -20, dtype=np.int64)
    high = np.full((n_source_days, segs), 90, dtype=np.int64)
    table = _table(move, low, high)

    n_draw_days = 100_000
    draws = NullDayGenerator(table).draw(np.random.default_rng(42), n_draw_days)
    assert draws.pnl_ticks.size == n_draw_days * segs  # 400,000 >= 400,000 required

    unflipped = table.move_ticks[draws.day_index]
    assert unflipped.mean() > 30  # every row is [10,30,50,70]; mean is exactly 40

    pnl = draws.pnl_ticks.astype(np.float64)
    se_bound = 4 * pnl.std(ddof=1) / math.sqrt(pnl.size)  # 4 standard errors
    assert abs(pnl.mean()) <= se_bound


def test_pnl_is_exactly_mirror_symmetric_about_zero() -> None:
    move_ticks = 37
    table = _table([[move_ticks]], [[-5]], [[40]])
    n_draw = 200_000
    draws = NullDayGenerator(table).draw(np.random.default_rng(11), n_draw)
    pnl = draws.pnl_ticks.reshape(-1)

    plus = int((pnl == move_ticks).sum())
    minus = int((pnl == -move_ticks).sum())
    assert plus + minus == n_draw  # only +-move_ticks are possible outcomes here

    se = math.sqrt(0.5 * 0.5 / n_draw)  # binomial standard error at p=0.5
    assert abs(plus / n_draw - 0.5) <= 4 * se
    assert abs(minus / n_draw - 0.5) <= 4 * se


def test_adverse_ticks_matches_side_and_never_beats_pnl() -> None:
    n_days, segs = 9, 3
    day_idx = np.arange(n_days)[:, None]
    seg_idx = np.arange(segs)[None, :]
    move = np.broadcast_to((day_idx + seg_idx) % 7 - 3, (n_days, segs)).astype(np.int64)
    low = np.tile((-(10 + day_idx % 3)), (1, segs)).astype(np.int64)
    high = np.tile((10 + seg_idx % 3), (n_days, 1)).astype(np.int64)
    # by construction: -12 <= low <= -10 < move (in -3..3) < high <= 12, so
    # adverse_ticks (derived from low/high only) must always sit below pnl.
    table = _table(move, low, high)

    draws = NullDayGenerator(table).draw(np.random.default_rng(5), 500)
    low_used = table.low_ticks[draws.day_index]
    high_used = table.high_ticks[draws.day_index]
    expected = np.where(draws.side > 0, low_used, -high_used)
    assert np.array_equal(draws.adverse_ticks, expected)
    assert np.all(draws.adverse_ticks <= np.minimum(0, draws.pnl_ticks))


# ============================================================== stationary_bootstrap_indices ====
def test_bootstrap_indices_stay_within_source_range() -> None:
    idx = stationary_bootstrap_indices(np.random.default_rng(3), n_source=37, n_draw=5000,
                                        mean_block=3.0)
    assert idx.shape == (5000,)
    assert idx.min() >= 0
    assert idx.max() < 37


def test_bootstrap_mean_block_one_is_valid() -> None:
    idx = stationary_bootstrap_indices(np.random.default_rng(4), n_source=50, n_draw=10_000,
                                        mean_block=1.0)
    assert idx.shape == (10_000,)
    assert idx.min() >= 0
    assert idx.max() < 50


def test_bootstrap_renewal_fraction_matches_one_over_mean_block() -> None:
    """A renewal can coincidentally continue the previous block (idx == prior+1)
    with probability 1/n_source; n_source=2000 keeps that correction (~0.0001)
    far inside the statistical tolerance below."""
    n_source, n_draw, mean_block = 2000, 200_000, 5.0
    idx = stationary_bootstrap_indices(np.random.default_rng(9), n_source, n_draw, mean_block)
    continues = idx[1:] == (idx[:-1] + 1) % n_source
    breaks_frac = 1.0 - continues.mean()
    se = math.sqrt(0.2 * 0.8 / n_draw)  # bernoulli SE at p=1/mean_block=0.2
    assert abs(breaks_frac - 0.2) <= 6 * se


def test_bootstrap_invalid_args_raise() -> None:
    rng = np.random.default_rng(1)
    with pytest.raises(ValueError):
        stationary_bootstrap_indices(rng, n_source=0, n_draw=10, mean_block=2.0)
    with pytest.raises(ValueError):
        stationary_bootstrap_indices(rng, n_source=10, n_draw=-1, mean_block=2.0)
    with pytest.raises(ValueError):
        stationary_bootstrap_indices(rng, n_source=10, n_draw=10, mean_block=0.5)


# ============================================================== calibration_summary ====
def test_calibration_summary_hand_computed() -> None:
    move = np.array([[10, 20], [5, 15], [-10, -10], [25, 25]], dtype=np.int64)
    low = np.full((4, 2), -5, dtype=np.int64)
    high = np.full((4, 2), 30, dtype=np.int64)
    table = _table(move, low, high)
    summary = calibration_summary(table)

    assert summary["research_days"] == 4
    assert summary["first_trade_date"] == table.trade_dates[0]
    assert summary["last_trade_date"] == table.trade_dates[-1]
    assert summary["skipped_trade_dates"] == []
    assert summary["segments_per_day"] == 2

    # session sums (move_ticks.sum(axis=1)): 30, 20, -20, 50
    # mean = (30 + 20 - 20 + 50) / 4 = 80 / 4 = 20
    assert summary["rth_session_move_mean_ticks_long_drift"] == pytest.approx(20.0)

    # sd, ddof=1: deviations from 20 are 10, 0, -40, 30; squares 100,0,1600,900
    # sum 2600; variance = 2600 / (4-1) = 866.6666...7
    expected_sd_ticks = math.sqrt(2600 / 3)
    assert summary["rth_session_move_sd_ticks"] == pytest.approx(round(expected_sd_ticks, 3))
    assert summary["rth_session_move_sd_usd_per_micro"] == pytest.approx(
        round(expected_sd_ticks * 1.25, 2)
    )

    # segment_move_sd_ticks over the 8 raw values 10,20,5,15,-10,-10,25,25:
    # mean = 80/8 = 10; deviations 0,10,-5,5,-20,-20,15,15; squares sum 1400
    # variance = 1400/7 = 200
    assert summary["segment_move_sd_ticks"] == pytest.approx(round(math.sqrt(200), 3))

    # abs values sorted: 5,10,10,10,15,20,25,25 -> median = (10+15)/2 = 12.5
    assert summary["segment_abs_move_median_ticks"] == pytest.approx(12.5)
    assert summary["segment_low_median_ticks"] == pytest.approx(-5.0)
    assert summary["segment_high_median_ticks"] == pytest.approx(30.0)


# ============================================================== real-data integration ====
@pytest.mark.skipif(not RESEARCH_SERIES_PATH.is_file(), reason="research parquet not present")
def test_load_null_generator_matches_lead_measurement() -> None:
    generator = load_null_generator(1)
    summary = calibration_summary(generator.table)

    assert summary["research_days"] == 310
    assert summary["first_trade_date"] == "2025-04-01"
    assert summary["last_trade_date"] == "2026-06-12"
    # Good Friday 2026: flatten 08:00 CT is before the 08:30 RTH open.
    assert summary["skipped_trade_dates"] == ["2026-04-03"]
    assert summary["rth_session_move_sd_usd_per_micro"] == pytest.approx(283.62, abs=0.02)
    assert all(d <= "2026-06-12" for d in generator.table.trade_dates)
