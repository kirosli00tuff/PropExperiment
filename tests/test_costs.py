"""Cost model: pure lookups against a hand-built table, plus sanity on the real calibration."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sim import costs
from sim.costs import SlippageTable, SlippageTableError


def _stat(mean: float) -> dict:
    return {"mean": mean, "p50": mean, "p90": mean, "p99": mean, "insufficient_depth": 0}


TABLE = SlippageTable(
    sizes_micros=(1, 5, 10),
    bucket_minutes=15,
    buckets={
        "08:30": {"1": _stat(0.6), "5": _stat(0.7), "10": _stat(0.9)},
        "11:00": {"1": _stat(0.5), "5": _stat(0.5), "10": _stat(0.6)},
    },
    windows={},
)


def test_commission_figure_and_reconfirmation_flag() -> None:
    assert costs.MES_ROUND_TURN_COMMISSION_USD == 1.22
    assert costs.COMMISSION_NEEDS_RECONFIRMATION is True


def test_bucket_uses_central_time_across_dst() -> None:
    # 13:40 UTC = 08:40 CDT (July); 14:40 UTC = 08:40 CST (January).
    assert costs.bucket_key(datetime(2026, 7, 15, 13, 40, tzinfo=UTC), 15) == "08:30"
    assert costs.bucket_key(datetime(2026, 1, 14, 14, 40, tzinfo=UTC), 15) == "08:30"


def test_open_costs_more_than_midday() -> None:
    open_ = costs.expected_slippage_ticks(TABLE, datetime(2026, 7, 15, 13, 31, tzinfo=UTC), 1)
    mid = costs.expected_slippage_ticks(TABLE, datetime(2026, 7, 15, 16, 5, tzinfo=UTC), 1)
    assert (open_, mid) == (0.6, 0.5)


def test_size_rounds_up_never_down() -> None:
    # 6 micros uses the 10-micro row (0.9), not the cheaper 5-micro row.
    ts = datetime(2026, 7, 15, 13, 31, tzinfo=UTC)
    assert costs.expected_slippage_ticks(TABLE, ts, 6) == 0.9
    with pytest.raises(SlippageTableError):
        costs.expected_slippage_ticks(TABLE, ts, 11)


def test_round_turn_cost_hand_computed() -> None:
    # 5 micros, entry 08:31 CT (0.7 t), exit 11:05 CT (0.5 t):
    # 5 x (1.22 + 1.2 ticks x 1.25) = 5 x (1.22 + 1.50) = 13.60
    cost = costs.round_turn_cost_usd(
        TABLE,
        datetime(2026, 7, 15, 13, 31, tzinfo=UTC),
        datetime(2026, 7, 15, 16, 5, tzinfo=UTC),
        5,
    )
    assert cost == pytest.approx(13.60)


def test_missing_bucket_is_an_error_not_a_guess() -> None:
    with pytest.raises(SlippageTableError):
        costs.expected_slippage_ticks(TABLE, datetime(2026, 7, 15, 3, 0, tzinfo=UTC), 1)


def test_naive_timestamp_refused() -> None:
    with pytest.raises(ValueError):
        costs.bucket_key(datetime(2026, 7, 15, 13, 31), 15)


def test_real_calibration_has_three_distinct_windows() -> None:
    table = costs.load_slippage_table()
    for window in ("open_0830_0900", "midday_1100_1300", "close_1430_1510"):
        assert table.windows[window]["samples_s"] > 0
    # A market order can never cost less than half a tick against the mid.
    for bucket in table.buckets.values():
        assert bucket["1"]["mean"] >= 0.5
