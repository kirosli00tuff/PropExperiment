"""data33 loaders: ordering (LT4), cutoff truncation (LT1 input), guard use (LT6), and the
E.33 ZS/ZL split equal to the raw records field by field (counts and equality only)."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pytest

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import data33 as d  # noqa: E402
import guard33 as g  # noqa: E402
import measure31 as m31  # noqa: E402

NS = g.NS
DAY = date(2022, 3, 14)  # Monday after the DST start


def _utc(y: int, mo: int, dd: int, h: int) -> int:
    return int(datetime(y, mo, dd, h, tzinfo=UTC).timestamp()) * NS


# ------------------------------------------------------------------ synthetic ----
def test_window_is_dst_aware() -> None:
    assert d.window("2022-03-14") == (_utc(2022, 3, 13, 21), _utc(2022, 3, 14, 21))
    assert d.window("2022-01-14") == (_utc(2022, 1, 13, 22), _utc(2022, 1, 14, 22))
    lo, hi = d.window("2022-11-07")  # 2022-11-06 is the DST end (Sunday)
    assert (lo, hi) == (_utc(2022, 11, 6, 22), _utc(2022, 11, 7, 22))


def test_truncate_keeps_ts_recv_at_or_before_cutoff() -> None:
    arr = np.zeros(5, dtype=d.MBO_COMPACT)
    arr["ts_recv"] = [10, 20, 20, 30, 40]
    assert len(d.truncate(arr, None)) == 5
    assert d.truncate(arr, 20)["ts_recv"].tolist() == [10, 20, 20]
    assert len(d.truncate(arr, 9)) == 0
    assert len(d.truncate(arr, 40)) == 5


def test_order_uses_ts_recv_and_is_stable() -> None:
    """LT4: a decrease in stored order gives a stable ts_recv sort; ts_event plays no part, and a
    record with ts_recv < ts_event keeps its ts_recv position."""
    arr = np.zeros(4, dtype=d.MBO_COMPACT)
    arr["ts_recv"] = [10, 30, 20, 30]
    arr["ts_event"] = [5, 1, 99, 2]  # record 2 has ts_recv < ts_event
    arr["order_id"] = [1, 2, 3, 4]
    d.ORDER_LOG.clear()
    out = d._in_ts_recv_order(arr, "TEST", DAY)
    assert out["order_id"].tolist() == [1, 3, 2, 4]
    assert {f"TEST {DAY}": 1} == d.ORDER_LOG
    d.ORDER_LOG.clear()
    same = d._in_ts_recv_order(out, "TEST", DAY)
    assert same is out and d.ORDER_LOG == {}


# ------------------------------------------------------------------ guard ----
def test_loaders_refuse_sealed_and_post_cutoff_dates() -> None:
    with pytest.raises(g.GuardRefused, match="soy test window"):
        d.load_zm("2019-03-05")
    with pytest.raises(g.GuardRefused, match="soy test window"):
        d.load_mbp1("ZS", "2020-11-30")
    with pytest.raises(g.GuardRefused, match="on or after 2024-03-01"):
        d.load_mbp1("ZL", "2024-03-01")
    with pytest.raises(ValueError, match="ZS or ZL"):
        d.load_mbp1("ZC", DAY)


# ------------------------------------------------------------------ real data (counts only) ----
def _check_loaded(arr: np.ndarray, day: date) -> None:
    lo, hi = d.window(day)
    assert len(arr) > 0
    assert d.ts_recv_decreases(arr["ts_recv"]) == 0
    assert int(arr["ts_recv"][0]) >= lo and int(arr["ts_recv"][-1]) < hi


def test_load_zm_order_window_and_cutoff() -> None:
    arr = d.load_zm(DAY)
    assert arr.dtype == m31.MBO_COMPACT
    _check_loaded(arr, DAY)
    cut = d.window(DAY)[0] + 15 * 3600 * NS
    part = d.load_zm(DAY, cutoff_ns=cut)
    assert len(part) == int(np.count_nonzero(arr["ts_recv"] <= cut))
    assert np.array_equal(part, arr[: len(part)])
    assert len(d.load_zm(DAY, cutoff_ns=d.window(DAY)[0] - 1)) == 0
    assert d.ORDER_LOG == {}


@pytest.mark.parametrize("root", ["ZS", "ZL"])
def test_load_mbp1_order_window_and_cutoff(root: str) -> None:
    arr = d.load_mbp1(root, DAY)
    assert arr.dtype == d.MBP1_SPLIT
    _check_loaded(arr, DAY)
    cut = d.window(DAY)[0] + 17 * 3600 * NS
    part = d.load_mbp1(root, DAY, cutoff_ns=cut)
    assert len(part) == int(np.count_nonzero(arr["ts_recv"] <= cut))


@pytest.mark.parametrize("root", ["ZS", "ZL"])
def test_split_equals_raw_records_field_by_field(root: str) -> None:
    """Every stored field equals the raw record (action/side as ASCII codes); counts only."""
    series = d.ROOT_SERIES[root]
    lo, hi = d.window(DAY)
    sf = next(f for f in d.source_files()[series] if f.month == "2022-03")
    parts = []
    for raw in d._decode(sf):
        ts = raw["ts_recv"].astype(np.int64)
        sel = (ts >= lo) & (ts < hi)
        if sel.any():
            parts.append(raw[sel])
    raw = np.concatenate(parts)
    split = d.load_mbp1(root, DAY)
    assert len(split) == len(raw)
    for name in d.MBP1_SPLIT.names:
        src = raw[name]
        if src.dtype.kind == "S":
            src = src.view(np.uint8)
        assert np.array_equal(split[name], src.astype(split[name].dtype)), name


def test_definitions_sorted_truncated_and_read_only() -> None:
    allrec = d.definitions()
    out = d.definitions(outright_only=True)
    assert len(allrec) == 1_810_372 and len(out) == 70_131
    assert len(np.unique(out["instrument_id"])) == 148
    assert set(out["instrument_class"].tolist()) == {b"F"}
    assert d.ts_recv_decreases(allrec["ts_recv"]) == 0
    assert set(d.DEF_FIELDS) <= set(allrec.dtype.names)
    cut = int(allrec["ts_recv"][len(allrec) // 2])
    part = d.definitions(cutoff_ns=cut)
    assert len(part) == int(np.count_nonzero(allrec["ts_recv"] <= cut))
    with pytest.raises(ValueError):
        allrec["high_limit_price"][0] = 0
