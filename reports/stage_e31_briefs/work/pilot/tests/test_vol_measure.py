"""Synthetic-only tests for vol_measure.py (no DBN file, no network)."""
import datetime as dt
import importlib.util
from pathlib import Path

import numpy as np
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "vol_measure", Path(__file__).resolve().parents[1] / "vol_measure.py")
vm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(vm)

D = dt.date
NS = vm.NS_PER_DAY


def ns(day: dt.date) -> int:
    return (day - D(1970, 1, 1)).days * NS


def mappings(sym_to_id: dict) -> dict:
    return {s: [{"start_date": D(2020, 1, 1), "end_date": D(2030, 1, 1), "symbol": str(i)}]
            for s, i in sym_to_id.items()}


def run(rows, sym_to_id, end=D(2026, 10, 22)):
    ts = np.array([ns(d) for d, _, _ in rows], dtype=np.int64)
    iid = np.array([sym_to_id[s] for _, s, _ in rows], dtype=np.int64)
    vol = np.array([v for _, _, v in rows], dtype=np.int64)
    meta = {"start_ns": ns(D(2023, 1, 1)), "end_ns": ns(end)}
    return vm.measure(ts, iid, vol, mappings(sym_to_id), meta)


# ---- delivery year
@pytest.mark.parametrize("digits,year,expected", [
    ("6", 2026, 2026), ("7", 2026, 2027), ("5", 2026, 2025),   # prior year kept (t-1)
    ("4", 2026, 2034),                                        # below t-1 -> +10
    ("0", 2029, 2030), ("1", 2029, 2031), ("9", 2029, 2029),  # decade wrap
    ("8", 2029, 2028), ("0", 2030, 2030), ("9", 2030, 2039),
    ("27", 2026, 2027), ("30", 2029, 2030),                   # two digits = 20dd
])
def test_decode_delivery_year(digits, year, expected):
    assert vm.decode_delivery_year(digits, year) == expected


def test_decode_rejects_bad_digits():
    with pytest.raises(ValueError):
        vm.decode_delivery_year("123", 2026)


def test_delivery_key_and_regex():
    assert vm.delivery_key("QMZ5", 2026) == (2025, 12)
    assert vm.delivery_key("ZMF0", 2029) == (2030, 1)
    assert vm.delivery_key("QMZ5-QMF6", 2026) is None
    assert not vm.matches_outright("QMA5")
    assert vm.matches_outright("ZMN27")


# ---- hyphen filter
def test_hyphen_filter_drops_spreads_and_counts_them():
    ids = {"QMZ6": 1, "QMZ6-QMF7": 2, "ZMZ6": 3, "ZM:BF Z7-F8-H8": 4}
    rows = [(D(2026, 1, 5), "QMZ6", 100), (D(2026, 1, 5), "QMZ6-QMF7", 999),
            (D(2026, 1, 5), "ZMZ6", 50), (D(2026, 1, 5), "ZM:BF Z7-F8-H8", 7)]
    res = run(rows, ids)
    assert res["hyphen_dropped"]["QM"] == {"symbols": 1, "bars": 1, "volume": 999}
    assert res["hyphen_dropped"]["ZM"]["volume"] == 7
    q = res["roots"]["QM"]["quarters_primary"][0]
    assert q["total_volume"] == 100
    assert res["instruments"]["QM"]["with_bars"] == 2


# ---- weekend drop
def test_weekend_bars_excluded_and_reported():
    ids = {"QMZ6": 1, "ZMZ6": 2}
    rows = [(D(2026, 1, 3), "QMZ6", 40),   # Saturday
            (D(2026, 1, 4), "ZMZ6", 5),    # Sunday
            (D(2026, 1, 5), "QMZ6", 10)]   # Monday
    res = run(rows, ids)
    assert res["weekend_bars"]["QM"] == {"bars": 1, "volume": 40}
    assert res["weekend_bars"]["ZM"] == {"bars": 1, "volume": 5}
    assert res["universe_days"]["primary"] == 1


# ---- zero-fill on the union universe
def test_zero_fill_on_union_universe():
    ids = {"QMZ6": 1, "ZMZ6": 2}
    days = [D(2026, 2, 2), D(2026, 2, 3), D(2026, 2, 4)]
    rows = [(days[0], "QMZ6", 10), (days[1], "QMZ6", 20), (days[2], "QMZ6", 30),
            (days[0], "ZMZ6", 100)]  # ZM trades only on day 0
    res = run(rows, ids)
    zm = res["roots"]["ZM"]
    assert zm["quarters_primary"][0]["days"] == 3
    assert zm["quarters_primary"][0]["median"] == 0.0     # [100, 0, 0]
    assert zm["quarters_own"][0]["median"] == 100.0
    assert res["roots"]["QM"]["quarters_primary"][0]["median"] == 20.0


# ---- front month
def test_front_month_is_earliest_delivery_and_top_share():
    ids = {"QMF7": 1, "QMZ6": 2, "QMG7": 3, "QMN30": 4}
    d = D(2026, 11, 2)
    rows = [(d, "QMF7", 500), (d, "QMZ6", 100), (d, "QMG7", 50), (d, "QMN30", 1)]
    res = run(rows, ids, end=D(2026, 12, 1))
    q = res["roots"]["QM"]["quarters_primary"][0]
    assert q["front_share"] == pytest.approx(100 / 651)
    assert q["top_share"] == pytest.approx(500 / 651)


def test_front_month_decade_wrap_beats_later_digit():
    # on a 2029 date: QMZ9 = Dec 2029 is earlier than QMF0 = Jan 2030
    daily = vm.daily_by_root([
        {"date": D(2029, 11, 5), "symbol": "QMF0", "volume": 9, "root": "QM"},
        {"date": D(2029, 11, 5), "symbol": "QMZ9", "volume": 3, "root": "QM"}])
    assert daily["QM"][D(2029, 11, 5)]["front_symbol"] == "QMZ9"


# ---- window
@pytest.mark.parametrize("end,expected", [
    (D(2026, 10, 22), (D(2025, 10, 1), D(2026, 9, 30))),
    (D(2026, 10, 21), (D(2025, 10, 1), D(2026, 9, 30))),
    (D(2026, 10, 1), (D(2025, 10, 1), D(2026, 9, 30))),   # exclusive end on the 1st
    (D(2026, 1, 15), (D(2025, 1, 1), D(2025, 12, 31))),   # year wrap
    (D(2026, 3, 1), (D(2025, 3, 1), D(2026, 2, 28))),
])
def test_window_last_12_full_months(end, expected):
    assert vm.window_from_end(ns(end)) == expected


def test_window_end_mid_day_counts_month_as_partial():
    end = ns(D(2026, 10, 1)) + 3600 * 10**9  # 2026-10-01T01:00Z
    assert vm.window_from_end(end) == (D(2025, 10, 1), D(2026, 9, 30))


# ---- quarter stats
def test_quarter_stats_median_p10_and_partial():
    ids = {"QMZ6": 1, "ZMZ6": 2}
    q1 = [D(2026, 1, 5) + dt.timedelta(days=i) for i in range(5)]  # Mon..Fri
    vols = [10, 20, 30, 40, 50]
    rows = [(d, "QMZ6", v) for d, v in zip(q1, vols)] + [(D(2026, 4, 6), "QMZ6", 7)]
    res = run(rows, ids)
    tab = res["roots"]["QM"]["quarters_primary"]
    assert [r["quarter"] for r in tab] == ["2026Q1", "2026Q2"]
    assert tab[0]["median"] == 30.0
    assert tab[0]["p10"] == pytest.approx(np.percentile(vols, 10))  # 14.0
    assert tab[0]["p10"] == pytest.approx(14.0)
    assert tab[0]["front_share"] == 1.0
    assert not tab[0]["partial"] and tab[1]["partial"] and tab[1]["days"] == 1


def test_window_medians_and_verdicts():
    ids = {"QMZ6": 1, "ZMZ6": 2}
    d0 = D(2026, 3, 2)
    rows = [(d0, "QMZ6", 999), (d0, "ZMZ6", 5000), (D(2025, 6, 2), "QMZ6", 10**6)]
    res = run(rows, ids)
    assert res["roots"]["QM"]["window_primary"]["median"] == 999.0
    assert res["roots"]["QM"]["verdict_primary"] == "FAIL"
    assert res["roots"]["ZM"]["verdict_primary"] == "PASS"   # 5000 is not below 5000


# ---- mapping stop
def test_missing_mapping_stops():
    ts = np.array([ns(D(2026, 1, 5))], dtype=np.int64)
    with pytest.raises(vm.MeasureError):
        vm.measure(ts, np.array([42]), np.array([1]), {}, {"start_ns": 0, "end_ns": ns(D(2026, 2, 1))})


def test_reused_instrument_id_resolved_by_interval():
    inv = vm.invert_mappings({
        "QMZ5-QMX0": [{"start_date": D(2024, 11, 6), "end_date": D(2025, 12, 3), "symbol": "7"}],
        "QMZ6": [{"start_date": D(2025, 12, 3), "end_date": D(2026, 10, 22), "symbol": "7"}]})
    assert vm.symbol_for(7, D(2025, 1, 2), inv) == "QMZ5-QMX0"
    assert vm.symbol_for(7, D(2026, 1, 2), inv) == "QMZ6"
    with pytest.raises(vm.MeasureError):
        vm.symbol_for(7, D(2023, 1, 2), inv)
