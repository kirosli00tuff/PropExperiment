"""Bar validation on synthetic data with planted defects."""

from __future__ import annotations

import numpy as np
import pandas as pd

from data.validate import expected_minutes, gap_runs, in_windows, ordering_counts, validate_bars

M = 60 * 1_000_000_000
T0 = 1_784_120_400 * 1_000_000_000  # 2026-07-15 13:00 UTC = 08:00 CDT (Wed)


def _raw(ts: list[int], volume: int = 10, price_fixed: int = 7_600_000_000_000) -> pd.DataFrame:
    n = len(ts)
    return pd.DataFrame({
        "ts_event": np.array(ts, dtype=np.int64), "instrument_id": [1] * n,
        "open_fixed": [price_fixed] * n, "high_fixed": [price_fixed] * n,
        "low_fixed": [price_fixed] * n, "close_fixed": [price_fixed] * n,
        "volume": [volume] * n,
    })


NO_WINDOWS = (np.array([], dtype=np.int64), np.array([], dtype=np.int64))


def test_duplicates_and_non_monotonic_steps_are_counted() -> None:
    assert ordering_counts(np.array([1, 2, 2, 3, 1])) == (2, 2)
    report, _ = validate_bars(_raw([T0, T0 + M, T0 + M]), T0, T0 + 3 * M, *NO_WINDOWS)
    assert report.duplicate_timestamps == 1 and report.hard_failures


def test_negative_volume_and_off_tick_are_hard_failures() -> None:
    report, _ = validate_bars(_raw([T0], volume=-1, price_fixed=7_600_100_000_000),
                              T0, T0 + M, *NO_WINDOWS)
    assert report.negative_volume == 1 and report.off_tick_prices == 4


def test_gaps_are_flagged_not_filled() -> None:
    present = [T0, T0 + M, T0 + 4 * M, T0 + 5 * M]  # minutes 2 and 3 missing
    raw = _raw(present)
    report, before = validate_bars(raw, T0, T0 + 6 * M, *NO_WINDOWS)
    assert len(raw) == 4, "validation must not add rows"
    assert [(r.start_ns, r.minutes) for r in report.gap_runs] == [(T0 + 2 * M, 2)]
    assert before.tolist() == [0, 0, 2, 0]
    assert report.present_expected_minutes == 4 and report.expected_minutes == 6


def test_closed_minutes_are_not_expected_and_bars_inside_are_flagged() -> None:
    starts = np.array([T0 + 2 * M]); ends = np.array([T0 + 4 * M])  # noqa: E702
    grid = expected_minutes(T0, T0 + 6 * M, starts, ends)
    assert grid.tolist() == [T0, T0 + M, T0 + 4 * M, T0 + 5 * M]
    report, _ = validate_bars(_raw([T0, T0 + 2 * M]), T0, T0 + 6 * M, starts, ends)
    assert report.bars_in_scheduled_closure == [T0 + 2 * M]
    runs, _ = gap_runs(grid, np.array([T0, T0 + M, T0 + 4 * M, T0 + 5 * M]))
    assert runs == []


def test_window_membership_is_half_open() -> None:
    starts, ends = np.array([10]), np.array([20])
    assert in_windows(np.array([9, 10, 19, 20]), starts, ends).tolist() == [
        False, True, True, False,
    ]


# ---- flag columns on the continuous series (data/bars.py) ----
def _ns(iso: str) -> int:
    return int(pd.Timestamp(iso).value)


def test_flatten_and_roll_flags_on_bars() -> None:
    from data.adapter import RollBoundary
    from data.bars import add_flags

    stamps = [
        _ns("2026-07-15T20:07:00Z"),  # 15:07 CDT: before cutoff
        _ns("2026-07-15T20:08:00Z"),  # 15:08 CDT: no new positions
        _ns("2026-07-15T20:09:00Z"),  # 15:09 CDT: last bar before flatten
        _ns("2026-07-15T20:10:00Z"),  # 15:10 CDT: flatten window
        _ns("2026-07-15T22:00:00Z"),  # 17:00 CDT: reopen, next trade date
        _ns("2025-11-27T17:44:00Z"),  # Thanksgiving 11:44 CST: past 11:43 cutoff, pre-flatten
        _ns("2025-11-27T17:45:00Z"),  # 11:45 CST: flatten (CME halt 12:00)
    ]
    raw = _raw(stamps)
    roll = RollBoundary("MES.v.0", "2026-07-16", _ns("2026-07-16T00:00:00Z"), "1", "2",
                        "MESU6", "MESZ6")
    gap_before = np.array([0, 0, 0, 0, 3, 0, 0])
    out = add_flags(raw, [roll], *NO_WINDOWS, gap_before, {"2025-11-27"})
    assert len(out) == len(raw), "flags never add or drop bars"
    assert out["in_flatten_window"].tolist() == [False, False, False, True, False, False, True]
    assert out["in_no_new_positions_window"].tolist() == [
        False, True, True, True, False, True, True,
    ]
    assert out["early_halt_ct"].tolist()[-1] == "12:00"
    assert str(out["trade_date"].iloc[4]) == "2026-07-16"
    assert out["is_roll_session"].tolist()[3:5] == [False, True]
    assert out["gap_before_minutes"].tolist()[4] == 3
    assert out["vendor_degraded_day"].tolist() == [False] * 5 + [True, True]
    assert out["raw_symbol"].iloc[0] == "MESU6"
    assert out["close"].iloc[0] == 7600.0
