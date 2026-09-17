"""Fill model: MES market-order costs, priced against a hand-built table plus sanity on
the real calibration.

Mirrors the hand-built ``SlippageTable`` pattern in ``tests/test_costs.py``.
"""

from __future__ import annotations

import json
import math
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from sim import costs
from sim.costs import SlippageTable, SlippageTableError, load_slippage_table
from sim.fill_model import (
    COMMISSION_PER_SIDE_CENTS_PER_MICRO,
    FillCost,
    side_cost,
    side_cost_at_ct_minute,
    slippage_cents,
)


def _stat(mean: float) -> dict:
    return {"mean": mean, "p50": mean, "p90": mean, "p99": mean, "insufficient_depth": 0}


TABLE = SlippageTable(
    sizes_micros=(1, 5, 10),
    bucket_minutes=15,
    buckets={
        "08:30": {"1": _stat(0.547), "5": _stat(0.52), "10": _stat(0.6)},
        "11:00": {"1": _stat(0.5), "5": _stat(0.5), "10": _stat(0.5)},
    },
    windows={},
)

# 2026-07-15 13:31 UTC = 08:31 CDT (UTC-5 in July); falls in the "08:30" bucket.
_TS_0830 = datetime(2026, 7, 15, 13, 31, tzinfo=UTC)
# 2026-07-15 16:05 UTC = 11:05 CDT; falls in the "11:00" bucket.
_TS_1100 = datetime(2026, 7, 15, 16, 5, tzinfo=UTC)


def test_commission_per_side_matches_half_the_round_turn() -> None:
    # $1.22 round turn -> 122 cents; half a round turn is one side's commission.
    assert COMMISSION_PER_SIDE_CENTS_PER_MICRO == 61
    assert round(1.22 * 100) == 2 * 61


def test_side_cost_qty1_08_30_bucket() -> None:
    result = side_cost(TABLE, _TS_0830, 1)
    # slippage = ceil(1 * 0.547 * 125) = ceil(68.375) = 69
    # commission = 1 * 61 = 61
    # total = 69 + 61 = 130
    assert result.slippage_cents == 69
    assert result.commission_cents == 61
    assert result.total_cents == 130


def test_side_cost_qty6_rounds_up_to_10_micro_row() -> None:
    # 6 micros must use the size-10 row (mean 0.6), never the cheaper size-5 row (mean 0.52).
    result = side_cost(TABLE, _TS_0830, 6)
    # slippage = ceil(6 * 0.6 * 125) = ceil(450.0) = 450 (float mult gives 449.99999999999994,
    # which ceil already rounds up to 450 regardless of noise direction)
    # commission = 6 * 61 = 366
    # total = 450 + 366 = 816
    assert result.slippage_cents == 450
    assert result.commission_cents == 366
    assert result.total_cents == 816


def test_side_cost_qty5_exact_integer_not_bumped_by_noise() -> None:
    result = side_cost(TABLE, _TS_0830, 5)
    # 5 * 0.52 * 125 = 325.0 exactly -> ceil(325.0) = 325 (NOT 326: the round(.., 6) guard
    # in slippage_cents would also collapse any float noise back to 325.0 first)
    # commission = 5 * 61 = 305
    # total = 325 + 305 = 630
    assert result.slippage_cents == 325
    assert result.commission_cents == 305
    assert result.total_cents == 630


def test_side_cost_qty1_11_00_bucket_half_tick() -> None:
    result = side_cost(TABLE, _TS_1100, 1)
    # slippage = ceil(1 * 0.5 * 125) = ceil(62.5) = 63
    # commission = 61
    # total = 63 + 61 = 124
    assert result.slippage_cents == 63
    assert result.commission_cents == 61
    assert result.total_cents == 124


def test_slippage_cents_direct_cases() -> None:
    # ceil(1 * 0.6 * 125) = ceil(75.0) = 75
    assert slippage_cents(1, 0.6) == 75
    # ceil(1 * 0.5 * 125) = ceil(62.5) = 63
    assert slippage_cents(1, 0.5) == 63
    # float noise from 0.1 + 0.2: the sum is 0.30000000000000004, not exactly 0.3.
    # raw = 1 * 0.30000000000000004 * 125 = 37.50000000000001; round(.., 6) -> 37.5 -> ceil 38
    assert slippage_cents(1, 0.1 + 0.2) == 38
    # 5 * 0.52 * 125 = 325.0 exactly -> ceil = 325 (NOT 326)
    assert slippage_cents(5, 0.52) == 325


def test_slippage_cents_guards_float_noise_crossing_an_integer() -> None:
    # exact math: 3 * 0.2 * 125 = 75.0
    # but IEEE-754 float multiplication actually produces 75.00000000000001 (noise strictly
    # above the integer); math.ceil of that raw value would wrongly return 76.
    # round(.., 6) collapses it back to 75.0 first, so ceil gives the correct 75.
    assert slippage_cents(3, 0.2) == 75


def test_side_cost_dst_summer_and_winter_give_equal_cost() -> None:
    # 2026-07-15 13:31 UTC = 08:31 CDT (UTC-5); 2026-01-14 14:31 UTC = 08:31 CST (UTC-6).
    # Both land in the "08:30" CT bucket, so both must price identically.
    summer = side_cost(TABLE, datetime(2026, 7, 15, 13, 31, tzinfo=UTC), 1)
    winter = side_cost(TABLE, datetime(2026, 1, 14, 14, 31, tzinfo=UTC), 1)
    assert summer == winter


def test_side_cost_at_ct_minute_matches_side_cost_by_utc_timestamp() -> None:
    # minute 511 = 8*60 + 31 = 08:31, and 2026-07-15 13:31 UTC is 08:31 CDT.
    by_minute = side_cost_at_ct_minute(TABLE, 8 * 60 + 31, 1)
    by_ts = side_cost(TABLE, _TS_0830, 1)
    assert by_minute == by_ts


def test_side_cost_refuses_non_positive_or_non_integer_qty() -> None:
    for bad_qty in (0, -1, True, 1.5):
        with pytest.raises(ValueError):
            side_cost(TABLE, _TS_0830, bad_qty)


def test_side_cost_refuses_naive_datetime() -> None:
    naive = datetime(2026, 7, 15, 13, 31)  # no tzinfo
    with pytest.raises(ValueError):
        side_cost(TABLE, naive, 1)


def test_side_cost_at_ct_minute_refuses_out_of_range_minute() -> None:
    with pytest.raises(ValueError):
        side_cost_at_ct_minute(TABLE, -1, 1)
    with pytest.raises(ValueError):
        side_cost_at_ct_minute(TABLE, 1440, 1)


def test_side_cost_refuses_bucket_missing_from_table() -> None:
    # The hand-built TABLE only defines "08:30" and "11:00"; any other bucket, such as the
    # real daily-halt window (16:00-17:00 CT), has no entry at all.
    # 2026-07-15 21:05 UTC = 16:05 CDT (UTC-5) -> bucket key "16:00", not in TABLE.buckets.
    ts = datetime(2026, 7, 15, 21, 5, tzinfo=UTC)
    with pytest.raises(SlippageTableError):
        side_cost(TABLE, ts, 1)


def test_side_cost_refuses_bucket_inside_real_daily_halt() -> None:
    # Same CT wall-clock instant, but against the real calibration, whose 16:00 CT bucket
    # is dropped because it sits inside the daily maintenance halt (no book samples).
    table = load_slippage_table()
    ts = datetime(2026, 7, 15, 21, 5, tzinfo=UTC)  # 16:05 CDT
    with pytest.raises(SlippageTableError):
        side_cost(table, ts, 1)


def test_side_cost_refuses_qty_above_largest_calibrated_size() -> None:
    # TABLE.sizes_micros tops out at 10; 11 exceeds every calibrated row.
    with pytest.raises(SlippageTableError):
        side_cost(TABLE, _TS_0830, 11)


def test_fillcost_is_frozen() -> None:
    result = side_cost(TABLE, _TS_0830, 1)
    with pytest.raises(FrozenInstanceError):
        result.commission_cents = 999  # type: ignore[misc]


def test_fillcost_total_is_commission_plus_slippage() -> None:
    result = side_cost(TABLE, _TS_0830, 1)
    assert isinstance(result, FillCost)
    assert result.total_cents == result.commission_cents + result.slippage_cents


def test_side_cost_at_ct_minute_matches_real_calibration_json() -> None:
    raw = json.loads(costs.CALIBRATION_PATH.read_text())
    mean_1 = raw["buckets_ct"]["08:30"]["1"]["mean"]
    mean_10 = raw["buckets_ct"]["08:30"]["10"]["mean"]
    table = load_slippage_table()
    for qty, mean in ((1, mean_1), (10, mean_10)):
        # commission = 61 cents/micro * qty; slippage = ceil(qty * mean * 125), rounded to
        # 6 decimals first to strip float noise, exactly as sim.fill_model.slippage_cents does.
        expected_total = 61 * qty + math.ceil(round(qty * mean * 125, 6))
        result = side_cost_at_ct_minute(table, 8 * 60 + 30, qty)  # 510 = 08:30
        assert result.total_cents == expected_total


def test_fill_model_docstring_keeps_the_caveats() -> None:
    import sim.fill_model as fill_model_module

    doc = fill_model_module.__doc__ or ""
    for phrase in ("TWO days", "latency", "adverse selection", "queue position", "LOWER BOUND"):
        assert phrase in doc
