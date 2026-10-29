"""Tests for dstats_lib (Stage E.33c Part D). Run from the repo root:

    PYTHONPYCACHEPREFIX=<scratch> nice -n 10 uv run python -m pytest -q reports/stage_e33c_briefs/work/stats
"""
from __future__ import annotations

import math
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
for _p in (str(REPO), str(HERE), str(REPO / "reports" / "stage_e32_briefs" / "protocol")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dstats_lib as L  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402
from screening.stage_e_verdict import moments, t_stat  # noqa: E402


def _weekdays(first: date, n: int) -> list:
    out, d = [], first
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


# ---------------------------------------------------------------- calendar groupings
@pytest.mark.parametrize("d, key", [("2020-12-30", "2020-12"), ("2021-01-04", "2020-12"), ("2021-02-26", "2020-12"),
                                    ("2021-03-01", "2021-03"), ("2021-05-31", "2021-03"), ("2021-06-01", "2021-06"),
                                    ("2021-11-30", "2021-09"), ("2024-02-29", "2023-12")])
def test_quarter_key_names_dec_feb_by_december(d, key):
    assert L.quarter_key(d) == key


def test_fold_slices_are_p61_blocks():
    s = L.fold_slices(796)
    assert [len(b) for b in s] == [133, 133, 133, 133, 132, 132]
    assert s[0][0] == 0 and s[-1][-1] == 795
    with pytest.raises(ValueError):
        L.fold_slices(795)


def test_tercile_slices_sizes_and_date_tiebreak():
    dates = _weekdays(date(2021, 1, 4), 796)
    sigma = [1.0] * 796
    s = L.tercile_slices(dates, sigma)
    assert [len(v) for v in s] == [265, 265, 266]
    assert s[0] == list(range(265))  # all ties: date order


# ---------------------------------------------------------------- gates
def _series(n_dates=796, per_date=1, net=0.6, noise=None):
    x = [per_date * net + (noise[j] if noise else 0.0) for j in range(n_dates)]
    return x, [per_date] * n_dates


def test_g1_boundaries_integer_comparisons():
    dates = _weekdays(date(2021, 1, 4), 796)
    sigma = [1.0 + 0.001 * j for j in range(796)]
    nt = [2] * 398 + [0] * 398       # 796 trades, 398 dates with a trade: passes
    x = [0.1 if k else 0.0 for k in nt]
    r = L.evaluate(x, nt, dates, sigma, 838, 0.164882, moments, t_stat, deflated_sharpe_ratio)
    assert r["gates"]["G1"]
    nt2 = [2] * 397 + [1] + [0] * 398  # 795 trades: fails
    r2 = L.evaluate(x, nt2, dates, sigma, 838, 0.164882, moments, t_stat, deflated_sharpe_ratio)
    assert not r2["gates"]["G1"]
    nt3 = [3] * 397 + [0] * 399        # 1191 trades, 397 dates: fails the 50% share
    r3 = L.evaluate(x, nt3, dates, sigma, 838, 0.164882, moments, t_stat, deflated_sharpe_ratio)
    assert not r3["gates"]["G1"]


def test_g2_mean_net_per_trade_threshold():
    dates = _weekdays(date(2021, 1, 4), 796)
    sigma = [1.0] * 796
    nt = [1] * 796
    x = [0.5] * 795 + [0.5]
    assert L.evaluate(x, nt, dates, sigma, 838, 0.1649, moments, t_stat, deflated_sharpe_ratio)["gates"]["G2"]
    x2 = [0.4999] * 796
    assert not L.evaluate(x2, nt, dates, sigma, 838, 0.1649, moments, t_stat,
                          deflated_sharpe_ratio)["gates"]["G2"]


def test_constant_series_fails_g3_g4_and_has_sharpe_zero():
    dates = _weekdays(date(2021, 1, 4), 796)
    r = L.evaluate([0.0] * 796, [0] * 796, dates, [1.0] * 796, 838, 0.1649, moments, t_stat,
                   deflated_sharpe_ratio)
    assert r["constant"] and r["sharpe"] == 0.0 and r["dsr"] is None and r["se"] is None
    assert not any(r["gates"].values())
    assert r["mean_net_per_trade"] is None


def test_se_g4_undefined_radicand():
    assert L.se_sharpe_g4(0.5, 10.0, 3.0, 796) is None   # 1 - 5 + 0.125 < 0
    se = L.se_sharpe_g4(0.2, 0.0, 3.0, 796)
    assert se == pytest.approx(math.sqrt((1 + 0.5 * 0.04) / 795))


def test_strong_steady_series_passes_every_gate():
    dates = _weekdays(date(2020, 12, 30), 796)
    sigma = [2.0 + (j % 7) * 0.1 for j in range(796)]
    noise = [((j * 7919) % 13 - 6) * 0.25 for j in range(796)]   # deterministic, mean ~0
    x, nt = _series(net=0.9, per_date=2, noise=noise)
    r = L.evaluate(x, nt, dates, sigma, 838, 0.164882, moments, t_stat, deflated_sharpe_ratio)
    assert r["sharpe"] > 0.5
    assert all(r["gates"].values()), r["gates"]


def test_g5b_dominant_month_fails_and_share_reported():
    dates = _weekdays(date(2021, 1, 4), 796)
    x = [0.0] * 796
    for j in range(20):
        x[j] = 5.0          # January 2021 holds the whole total
    x[400] = -1.0
    g = L.g5_parts(x, dates, [1.0] * 796, moments, t_stat)
    assert g["max_month"] == "2021-01" and not g["b"]
    assert g["max_month_share"] == pytest.approx(100.0 / 99.0)


def test_largest_month_share_undefined_when_total_not_positive():
    dates = _weekdays(date(2021, 1, 4), 60)
    lm = L.largest_month([1.0] * 20 + [-2.0] * 40, dates)
    assert lm["share"] is None and lm["total"] < 0


def test_funnel_alone_and_in_order():
    rows = [{"G1": True, "G2": True, "G3": False, "G4": False, "G5": True},
            {"G1": False, "G2": True, "G3": True, "G4": True, "G5": True},
            {"G1": True, "G2": False, "G3": False, "G4": False, "G5": False}]
    f = L.funnel(rows)
    assert f["alone"] == {"G1": 2, "G2": 2, "G3": 1, "G4": 1, "G5": 2}
    assert f["in_order"] == {"G1": 2, "G1..G2": 1, "G1..G3": 0, "G1..G4": 0, "G1..G5": 0}


def test_rank_key_tiebreaks():
    a = L.rank_key("E33-S2F30G2200", 0.04778, 55)
    b = L.rank_key("E33-S1F15G3200", 0.04778, 60)   # same rounded SR, more trades -> after
    c = L.rank_key("E33-S1F15L001A", 0.04778, 55)   # same trades, LOGIT -> before
    assert sorted([a, b, c]) == [c, a, b]


# ---------------------------------------------------------------- reports
def test_firm_net_is_a_fee_shift():
    assert L.firm_net(0.5, L.FEES["Tradeify"]) == pytest.approx(0.108)   # P8 G2: 0.392 shift leaves 0.108
    assert L.firm_net(1.0, L.FEES["Topstep"]) == 1.0
    assert L.firm_net(None, 0.6) is None


BH_1995 = [0.0001, 0.0004, 0.0019, 0.0095, 0.0201, 0.0278, 0.0298, 0.0344, 0.0459, 0.3240, 0.4262, 0.5719,
           0.6528, 0.7590, 1.000]


def test_bh_and_holm_reproduce_benjamini_hochberg_1995():
    assert L.bh_count(BH_1995, 0.05) == 4      # BH (1995) section 4.2: four hypotheses rejected
    assert L.holm_count(BH_1995, 0.05) == 3    # implied by the published Bonferroni/Hochberg count (reading K11)


def test_one_sided_p():
    assert L.one_sided_p(None) == 1.0
    assert L.one_sided_p(0.0) == pytest.approx(0.5)
    assert L.one_sided_p(1.6448536269514722) == pytest.approx(0.05)


def test_expected_max_normal_matches_program_function():
    for n in (20, 300, 838):
        # the program's _norm_ppf is a rational approximation (relative error about 1e-9)
        assert L.expected_max_normal(n, 0.0, 1.0) == pytest.approx(expected_max_sharpe(n, 1.0), rel=1e-8)
    assert L.expected_max_normal(838, 0.0, math.sqrt(1 / 795)) == pytest.approx(0.1137, abs=5e-5)  # P7.2 SR0


def test_p7_thresholds_and_power_lines_reproduce_protocol():
    import p7_final as p7
    t_disc, t_test = 796, 870
    sr0 = expected_max_sharpe(838, 1 / (t_disc - 1))
    g3 = p7.required_sharpe(838, t_disc, 1 / (t_disc - 1), 0.0, 3.0)
    b_test = max(3.0 / math.sqrt(t_test), p7.required_sharpe(838, t_test, 1 / (t_test - 1), 0.0, 3.0))
    g4 = p7.g4_threshold(b_test, t_disc)
    assert round(sr0, 4) == 0.1137 and round(g3, 4) == 0.1724 and round(g4, 4) == 0.2007
    assert round(b_test, 6) == 0.164882
    assert round(L.s80_at_bar(b_test, t_test), 4) == 0.1936          # P7.2: 80% test power at 0.1936
    sel = max(g3, g4)
    # P7.2 per-trade line: 0.71 (5 min, 4/date), 0.50 (8), 1.22 (15, 4), 0.87 (8), 1.73 (30, 4), 3.46 (60, 2)
    for h, n, want in ((5, 4, 0.71), (5, 8, 0.50), (15, 4, 1.22), (15, 8, 0.87), (30, 4, 1.73), (60, 2, 3.46)):
        assert round(L.mde_random_walk(sel, h, n), 2) == want


def test_s80_exact_is_close_to_bar_convention():
    a, b = L.s80_at_bar(0.2007, 796), L.s80_exact(0.2007, 796)
    assert b > a > 0.2007 and abs(a - b) < 1e-3
    # exact: P(SR_hat >= bar | s) = 0.8 with se at s
    assert L.Z.cdf((b - 0.2007) / L.se_normal(b, 796)) == pytest.approx(0.8, abs=1e-9)


def test_mde_measured():
    assert L.mde_measured(0.2, 5.0, 2.0) == pytest.approx(0.5)
    assert L.mde_measured(0.2, 5.0, 0.0) is None
    assert L.mde_measured(0.2, 0.0, 1.0) is None


def test_quantiles_match_numpy_linear():
    import numpy as np
    xs = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
    q = L.quantiles(xs, (0.1, 0.5, 0.9))
    assert q["q0.1"] == pytest.approx(float(np.quantile(xs, 0.1)))
    assert q["q0.5"] == pytest.approx(float(np.quantile(xs, 0.5)))
    assert q["q0.9"] == pytest.approx(float(np.quantile(xs, 0.9)))


def test_all_ids_are_300_unique_in_p5_order():
    ids = L.all_ids()
    assert len(ids) == 300 and len(set(ids)) == 300
    assert ids[0] == "E33-S5F15L001A" and ids[-1] == "E33-S4T30G3200"
    assert all(L.parse_id(c)["h"] in (5, 15, 30, 60) for c in ids)
