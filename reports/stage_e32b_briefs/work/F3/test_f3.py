"""Unit tests for Stage E.32b F3 (synthetic bars and a synthetic file tree only; no market data is opened).

Run: uv run pytest -q reports/stage_e32b_briefs/work/F3/test_f3.py
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from f3_core import (HORIZONS, MAIN_PT, NS_MIN, aggregate, day_record, main_session_from_calendar,  # noqa: E402
                     overnight_changes, pt_minutes, scheduled_minutes, summarize, trade_dates, transfer_oc1)
from f3_guard import BarGuard, GuardError, REL_BASE  # noqa: E402

TICK = 1.0
DAY = date(2023, 6, 14)  # regular Wednesday


def make_day(group: str, day: date, price, inst=None, drop=None, last_pt: int | None = None):
    """Bars at every scheduled minute of ``day``; price(i, is_main, k_main) gives the close; hi/lo = close +- 1."""
    grid = scheduled_minutes(group, day)
    ptm = pt_minutes(grid)
    if last_pt is not None:  # early close: no bar after last_pt (PT minutes) on the trade date
        cut = pd.Timestamp(f"{day} {last_pt // 60:02d}:{last_pt % 60:02d}", tz="America/Vancouver").value
        keep = grid <= cut
        grid, ptm = grid[keep], ptm[keep]
    is_main = (ptm >= MAIN_PT[0]) & (ptm < MAIN_PT[1])
    kmain = np.cumsum(is_main) - 1
    close = np.array([price(i, m, k) for i, (m, k) in enumerate(zip(is_main, kmain))], dtype="float64")
    ins = np.array([inst(i, m, k) if inst else 1 for i, (m, k) in enumerate(zip(is_main, kmain))], dtype="int64")
    sel = np.ones(grid.size, bool) if drop is None else ~drop(is_main, kmain)
    return grid[sel], close[sel], close[sel] + 1, close[sel] - 1, ins[sel], is_main[sel], kmain[sel]


def rec_of(group, day, bars):
    ts, c, hi, lo, ins = bars[:5]
    return day_record(group, day, ts, c, hi, lo, ins, TICK)


def wiggle(i, m, k):
    return 1000.0 + ((k * 7) % 11 if m else 500 + i % 5)  # main pattern varies; overnight far away


# ---- D_h with overlapping starts ------------------------------------------------------------------------------
def test_dh_overlapping_starts_match_brute_force():
    bars = make_day("equity", DAY, wiggle)
    rec = rec_of("equity", DAY, bars)
    c_main = bars[1][bars[5]]
    assert c_main.size == 390
    for h in HORIZONS:
        brute = c_main[h:] - c_main[:-h]
        assert rec["D"][h].size == 390 - h  # every main minute t with t+h in the main session
        np.testing.assert_array_equal(rec["D"][h], brute)


def test_dh_carry_forward_over_missing_bars():
    def drop(is_main, k):
        return is_main & (k >= 100) & (k < 110)
    bars = make_day("equity", DAY, wiggle, drop=drop)
    rec = rec_of("equity", DAY, bars)
    full = make_day("equity", DAY, wiggle)
    c = full[1][full[5]].copy()
    c[100:110] = c[99]  # untraded minutes carry the last close
    np.testing.assert_array_equal(rec["D"][1], c[1:] - c[:-1])
    np.testing.assert_array_equal(rec["D"][15], c[15:] - c[:-15])


# ---- roll exclusion -------------------------------------------------------------------------------------------
def test_roll_pairs_excluded():
    def inst(i, m, k):
        return 2 if (m and k >= 200) or (not m and i > 600) else 1

    def price(i, m, k):
        return wiggle(i, m, k) + (5000 if (m and k >= 200) else 0)  # big jump at the roll
    bars = make_day("equity", DAY, price, inst=inst)
    rec = rec_of("equity", DAY, bars)
    for h in HORIZONS:
        assert rec["D"][h].size == max(200 - h, 0) + max(190 - h, 0)
        assert np.all(np.abs(rec["D"][h]) < 100)
    assert rec["oc"] is None  # first and last main closes are on different instruments


# ---- session cut ----------------------------------------------------------------------------------------------
def test_session_cut_equity_and_grains():
    assert main_session_from_calendar("equity", DAY) == (390, ["06:30", "13:00"])
    assert main_session_from_calendar("grains", DAY) == (290, ["06:30", "11:20"])
    g = rec_of("grains", DAY, make_day("grains", DAY, wiggle))
    assert g["n_main"] == 290 and g["D"][1].size == 289 and g["D"][240].size == 50


def test_session_cut_ignores_outside_minutes_and_early_close():
    rec = rec_of("equity", DAY, make_day("equity", DAY, wiggle))
    assert np.all(np.abs(rec["D"][1]) <= 10)  # overnight prices (offset 500) never enter D_h
    early = rec_of("equity", DAY, make_day("equity", DAY, wiggle, last_pt=10 * 60))
    assert early["n_main"] == 211 and early["D"][1].size == 210 and early["D"][240].size == 0


# ---- 17:00 CT trade-date rule ---------------------------------------------------------------------------------
def test_trade_date_rule_1700_ct():
    def ns(s):
        return pd.Timestamp(s, tz="America/Chicago").tz_convert("UTC").value
    cases = {"2023-06-14 16:59": "2023-06-14", "2023-06-14 17:00": "2023-06-15",
             "2023-06-16 17:00": "2023-06-19", "2023-06-18 17:00": "2023-06-19",
             "2023-01-11 16:59": "2023-01-11", "2023-01-11 17:00": "2023-01-12"}
    got = trade_dates(np.array([ns(k) for k in cases], dtype="int64"))
    assert [str(d) for d in got] == list(cases.values())


# ---- OC and overnight -----------------------------------------------------------------------------------------
def test_oc_is_last_minus_first_main_close():
    bars = make_day("equity", DAY, wiggle)
    rec = rec_of("equity", DAY, bars)
    c_main = bars[1][bars[5]]
    assert rec["oc"] == c_main[-1] - c_main[0]
    assert rec["first"] == (c_main[0], 1) and rec["last"] == (c_main[-1], 1)


def test_overnight_cc_on_and_instrument_check():
    d1, d2, d3 = date(2023, 6, 13), date(2023, 6, 14), date(2023, 6, 15)
    r1 = rec_of("equity", d1, make_day("equity", d1, lambda i, m, k: 100.0 + k % 3))
    r2 = rec_of("equity", d2, make_day("equity", d2, lambda i, m, k: 120.0 + k % 4))
    r3 = rec_of("equity", d3, make_day("equity", d3, lambda i, m, k: 90.0, inst=lambda i, m, k: 2))
    ov = overnight_changes([(d1, r1), (d2, r2), (d3, r3)], excluded=set())
    np.testing.assert_array_equal(ov["cc"], [r2["last"][0] - r1["last"][0]])  # d2->d3 dropped: roll
    np.testing.assert_array_equal(ov["on"], [r2["first"][0] - r1["last"][0]])
    ov2 = overnight_changes([(d1, r1), (d3, r2)], excluded={d2})
    assert ov2["pairs_span_excluded"] == 1 and ov2["cc"].size == 1


# ---- R_d ------------------------------------------------------------------------------------------------------
def test_rd_uses_last_bar_instrument_over_full_trade_date():
    def inst(i, m, k):
        return 1 if i < 50 else 2

    def price(i, m, k):
        return 5000.0 if i < 50 else (200.0 if i == 60 else (100.0 + k % 5 if m else 150.0))
    bars = make_day("equity", DAY, price, inst=inst)
    rec = rec_of("equity", DAY, bars)
    # instrument 2 only: high 200+1 (overnight bar i=60), low 100-1 (main) -> 102 ticks; inst 1's 5000 ignored
    assert rec["rng"] == 102.0
    assert rec["main_rng"] == (104.0 + 1) - (100.0 - 1)


def test_aggregate_rd_p99_and_tick_units():
    days = [date(2023, 6, d) for d in (12, 13, 14, 15)]
    dated = [(d, rec_of("equity", d, make_day("equity", d, lambda i, m, k, s=s: 100.0 + s * (k % 2))))
             for s, d in enumerate(days, 1)]
    agg = aggregate(dated, set(), tick=TICK, price_to_exchange=0.5)
    rng = np.array([r["rng"] for _, r in dated])
    assert agg["R_d"]["median"] == np.median(rng) and agg["R_d"]["p99"] == np.percentile(rng, 99)
    assert agg["n_dates"] == 4 and agg["h"]["1"]["n"] == 4 * 389
    assert agg["median_close"] == np.median([r["last"][0] for _, r in dated]) * 0.5


# ---- summaries and OC-1 ---------------------------------------------------------------------------------------
def test_summarize_definitions():
    x = np.array([-3.0, 1.0, 0.0, 2.0, -1.0])
    s = summarize(x)
    assert s["sigma"] == pytest.approx(np.std(x, ddof=1)) and s["m"] == pytest.approx(1.4)
    assert s["median_abs"] == 1.0 and s["p99_abs"] == pytest.approx(np.percentile(np.abs(x), 99))
    assert s["n"] == 5 and summarize(np.array([]))["sigma"] is None


def test_transfer_oc1_scales_ticks_not_counts():
    h = {"sigma": 4.0, "m": 3.0, "median_abs": 2.0, "p99_abs": 10.0, "n": 77}
    src = {"n_dates": 250, "h": {"1": dict(h)}, "OC": {"sigma": 8.0, "m": 6.0, "n": 250},
           "overnight": {"cc": {"sigma": 2.0, "m": 1.0, "n": 249}, "on": {"sigma": None, "m": None, "n": 0}},
           "R_d": {"median": 100.0, "p99": 300.0, "n": 250}, "main_range_median": 80.0, "median_close": 75.5}
    t = transfer_oc1(src, 0.4)
    assert t["h"]["1"] == {"sigma": 1.6, "m": 1.2000000000000002, "median_abs": 0.8, "p99_abs": 4.0, "n": 77}
    assert t["OC"]["sigma"] == 3.2 and t["R_d"]["median"] == 40.0 and t["R_d"]["n"] == 250
    assert t["overnight"]["on"]["sigma"] is None and t["main_range_median"] == 32.0
    assert t["median_close"] == 75.5 and t["n_dates"] == 250


# ---- guard ----------------------------------------------------------------------------------------------------
@pytest.fixture()
def tree(tmp_path_factory):
    repo = tmp_path_factory.mktemp("bars")
    base = repo / REL_BASE
    for d, n in [("CL_v_0", "range=2022-11-01_2022-12-01.dbn.zst"), ("CL_v_0", "range=2023-10-01_2023-11-01.dbn.zst"),
                 ("CL_v_0", "range=2022-10-01_2022-11-01.dbn.zst"), ("CL_v_0", "range=2023-11-01_2023-12-01.dbn.zst"),
                 ("CL_v_0", "range=2024-03-01_2024-04-01.dbn.zst"), ("MES_v_0", "range=2022-11-01_2022-12-01.dbn.zst"),
                 ("CL_v_0", "range=2022-11-01_2022-12-01.dbn.zst.bak")]:
        (base / d).mkdir(parents=True, exist_ok=True)
        (base / d / n).write_bytes(b"x")
    side = repo / "data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0"
    side.mkdir(parents=True)
    (side / "range=2022-11-01_2022-12-01.dbn.zst").write_bytes(b"y")
    return repo, base


def guard_of(repo):
    return BarGuard(repo, repo / "opens.log")


def test_guard_allows_window_file_and_logs(tree):
    repo, base = tree
    g = guard_of(repo)
    seen = []
    out = g.open(base / "CL_v_0/range=2022-11-01_2022-12-01.dbn.zst", lambda p: seen.append(p) or "ok")
    assert out == "ok" and seen == [os.path.realpath(base / "CL_v_0/range=2022-11-01_2022-12-01.dbn.zst")]
    assert g.check(base / "CL_v_0/range=2023-10-01_2023-11-01.dbn.zst")
    assert "| OPEN |" in (repo / "opens.log").read_text()


@pytest.mark.parametrize("rel", [
    "CL_v_0/range=2022-10-01_2022-11-01.dbn.zst",  # before the window
    "CL_v_0/range=2023-11-01_2023-12-01.dbn.zst",  # pilot window
    "CL_v_0/range=2024-03-01_2024-04-01.dbn.zst",  # holdout era
    "MES_v_0/range=2022-11-01_2022-12-01.dbn.zst",  # not one of the 47 codes
    "CL_v_0/range=2022-11-01_2022-12-01.dbn.zst.bak",  # wrong name
    "CL_v_0/range=2022-12-01_2023-01-01.dbn.zst",  # allowed name but absent
    "CL_v_0/../MES_v_0/range=2022-11-01_2022-12-01.dbn.zst",  # traversal
    "../mbp-1/CL_v_0/range=2022-11-01_2022-12-01.dbn.zst",  # other schema
])
def test_guard_refuses_and_never_reads(tree, rel):
    repo, base = tree
    g = guard_of(repo)
    with pytest.raises(GuardError):
        g.open(str(base) + "/" + rel, lambda p: pytest.fail("reader called on a refused path"))
    assert g.opened == [] and "| REFUSED |" in (repo / "opens.log").read_text()


@pytest.mark.parametrize("token", ["mbo", "tbbo", "holdout", "sealed", "enc", "MBP"])
def test_guard_refuses_forbidden_tokens_in_given_path(tree, token):
    repo, base = tree
    link_dir = repo / f"x_{token}_dir"
    link_dir.mkdir()
    link = link_dir / "range=2022-11-01_2022-12-01.dbn.zst"
    link.symlink_to(base / "CL_v_0/range=2022-11-01_2022-12-01.dbn.zst")  # resolves to an allowed file
    with pytest.raises(GuardError, match="forbidden token"):
        guard_of(repo).check(link)


def test_guard_refuses_symlink_resolving_outside(tree):
    repo, base = tree
    (base / "NG_v_0").mkdir()
    bad = base / "NG_v_0/range=2022-11-01_2022-12-01.dbn.zst"
    bad.symlink_to(repo / "data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2022-11-01_2022-12-01.dbn.zst")
    with pytest.raises(GuardError, match="forbidden token 'mbp'"):
        guard_of(repo).check(bad)
    other = repo / "elsewhere.dbn.zst"
    other.write_bytes(b"z")
    (base / "GC_v_0").mkdir()
    (base / "GC_v_0/range=2022-11-01_2022-12-01.dbn.zst").symlink_to(other)
    with pytest.raises(GuardError, match="outside"):
        guard_of(repo).check(base / "GC_v_0/range=2022-11-01_2022-12-01.dbn.zst")


def test_guard_on_real_tree_refuses_out_of_window_without_opening(tmp_path_factory):
    log = tmp_path_factory.mktemp("logs") / "opens.log"
    g = BarGuard(REPO, log)
    for rel in ["CL_v_0/range=2024-03-01_2024-04-01.dbn.zst", "CL_v_0/range=2023-11-01_2023-12-01.dbn.zst",
                "ZS_v_0/range=2019-01-01_2019-02-01.dbn.zst"]:
        with pytest.raises(GuardError):
            g.check(REPO / REL_BASE / rel)
    assert g.opened == []
