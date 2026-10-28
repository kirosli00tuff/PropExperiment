"""Tests for select33 (P8, mechanical selection). Synthetic series only; the real 796 OOF dates (cal33) give
the calendar of quarters, months and terciles.

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_select33.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(PIPE), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import select33 as sel  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio  # noqa: E402
from screening.stage_e_verdict import moments, t_stat  # noqa: E402

N838 = 838


# ---------------------------------------------------------------- fixtures and builders
@pytest.fixture(scope="module")
def dates():
    import cal33
    return [d.isoformat() for d in cal33.oof_dates()]


@pytest.fixture(scope="module")
def sigma(dates):
    rng = np.random.default_rng(11)
    return list(3.0 + rng.random(len(dates)))


@pytest.fixture(scope="module")
def base(dates):
    """A fixed standardised series (mean 0, population SD 1) with mild skew; its moments are known."""
    rng = np.random.default_rng(7)
    b = rng.standard_normal(len(dates)) + 0.15 * (rng.standard_normal(len(dates)) ** 2 - 1)
    b = (b - b.mean()) / b.std()
    return b


def series(base, sr: float, scale: float = 10.0) -> list:
    """x = scale (sr + base): Sharpe sr (up to rounding), the base's skewness and kurtosis."""
    return list(scale * (sr + base))


def trades(n_dates: int, per_date: int = 2) -> list:
    return [per_date] * n_dates


def bisect(f, lo: float, hi: float, n: int = 200) -> float:
    """Smallest x in [lo, hi] with f(x) True (f monotone)."""
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if f(mid) else (mid, hi)
    return hi


# ---------------------------------------------------------------- thresholds at N
def test_b_test_838_is_the_pinned_value():
    b = sel.b_test_at(N838)
    assert round(b, 6) == 0.164882
    assert round(b, 4) == 0.1649


def test_b_test_other_n_recomputed_by_p7_final():
    import p7_final as p7
    b900 = sel.b_test_at(900)
    direct = max(3.0 / math.sqrt(870), p7.required_sharpe(900, 870, 1 / 869, 0.0, 3.0))
    assert b900 == direct
    assert b900 > sel.b_test_at(N838)
    # N small enough that the t > 3.0 bar binds
    assert sel.b_test_at(2) == pytest.approx(3.0 / math.sqrt(870))


def test_g4_threshold_at_838_matches_protocol(dates, sigma):
    """A normal-moment series needs SR_d >= 0.2007 at G4 (P7.2)."""
    import p7_final as p7
    g4 = p7.g4_threshold(sel.b_test_at(N838), 796)
    assert round(g4, 4) == 0.2007


# ---------------------------------------------------------------- gate boundaries
def _eval(x, nt, dates, sigma, n=N838):
    return sel.evaluate("E33-S5F15L001A", x, nt, dates, sigma, n, sel.b_test_at(n))


def test_g1_boundaries(dates, sigma, base):
    x = series(base, 0.3)
    t = len(dates)
    nt = [1] * t                                   # exactly 796 trades on every date: passes
    assert _eval(x, nt, dates, sigma)["gates"]["G1"]
    nt2 = [1] * (t - 1) + [0]                      # 795 trades: fails
    assert not _eval(x, nt2, dates, sigma)["gates"]["G1"]
    half = t // 2                                  # 398 dates with a trade, 796 trades: passes
    nt3 = [2] * half + [0] * (t - half)
    r = _eval(x, nt3, dates, sigma)
    assert r["dates_with_trade"] == 398 and r["gates"]["G1"]
    nt4 = [0] * (t - half + 1) + [3] * (half - 2) + [4]   # 397 dates with a trade, many trades: fails
    nt4 = nt4[:t]
    assert sum(1 for k in nt4 if k) == 397 and sum(nt4) >= t
    assert not _eval(x, nt4, dates, sigma)["gates"]["G1"]


def test_g2_boundaries(dates, sigma):
    t = len(dates)
    nt = [2] * t
    x_pass = [1.0] * t                                  # 0.5 per trade exactly (representable): passes
    assert _eval(x_pass, nt, dates, sigma)["mean_net_per_trade"] == 0.5
    assert _eval(x_pass, nt, dates, sigma)["gates"]["G2"]
    x_fail = [1.0] * (t - 1) + [1.0 - 1e-6]
    assert not _eval(x_fail, nt, dates, sigma)["gates"]["G2"]
    assert not _eval([0.0] * t, [0] * t, dates, sigma)["gates"]["G2"]   # no trades: undefined -> fails


def test_g3_boundary(dates, sigma, base):
    mom = moments(list(base))
    v = 1 / (len(dates) - 1)
    sr_star = bisect(lambda s: deflated_sharpe_ratio(s, len(dates), N838, v, mom["skew"], mom["kurtosis"])[
        "deflated_sharpe_ratio"] > 0.95, 0.0, 1.0)
    above = _eval(series(base, sr_star + 1e-6), trades(len(dates)), dates, sigma)
    below = _eval(series(base, sr_star - 1e-6), trades(len(dates)), dates, sigma)
    assert above["gates"]["G3"] and above["dsr"] > 0.95
    assert not below["gates"]["G3"] and below["dsr"] <= 0.95
    assert above["moments"]["skew"] == pytest.approx(mom["skew"], abs=1e-9)
    # N enters G3: the same series fails at a much larger N
    big = sel.evaluate("E33-S5F15L001A", series(base, sr_star + 1e-6), trades(len(dates)), dates, sigma, 5000,
                       sel.b_test_at(5000))
    assert big["dsr"] < above["dsr"] and not big["gates"]["G3"]


def test_g4_boundary(dates, sigma, base):
    mom = moments(list(base))
    b = sel.b_test_at(N838)
    t = len(dates)

    def passes(s):
        se = math.sqrt((1 - mom["skew"] * s + (mom["kurtosis"] - 1) / 4 * s * s) / (t - 1))
        return s - se >= b
    sr_star = bisect(passes, 0.0, 1.0)
    assert _eval(series(base, sr_star + 1e-6), trades(t), dates, sigma)["gates"]["G4"]
    assert not _eval(series(base, sr_star - 1e-6), trades(t), dates, sigma)["gates"]["G4"]


def test_se_undefined_fails_g4():
    assert sel.se_sharpe(2.0, 3.0, 1.0, 796) is None        # 1 - 6 + 0 < 0
    assert sel.se_sharpe(0.2, 0.0, 3.0, 796) == pytest.approx(math.sqrt((1 + 0.02) / 795))


def _quarter_series(dates, positive_quarters: int) -> list:
    keys = sorted({sel.quarter_key(d) for d in dates})
    assert len(keys) == 13
    good = set(keys[:positive_quarters])
    return [1.0 if sel.quarter_key(d) in good else -0.5 for d in dates]


def test_g5a_quarters(dates, sigma):
    r9 = sel.g5_stability(_quarter_series(dates, 9), dates, sigma)[1]
    r8 = sel.g5_stability(_quarter_series(dates, 8), dates, sigma)[1]
    assert r9["n_quarters"] == 13 and r9["quarters_positive"] == 9 and r9["a"]
    assert r8["quarters_positive"] == 8 and not r8["a"]
    # the first quarter (Dec 2020 - Feb 2021) carries no burn-in date
    assert dates[0] == "2020-12-30" and sel.quarter_key(dates[0]) == "2020-12"


def test_g5b_month_share(dates, sigma):
    months = sorted({d[:7] for d in dates})
    assert len(months) == 39
    # all net in 4 months, equal: each month exactly 25% of the total -> passes; a 5th of 3 months -> fails
    four = set(months[1:5])
    x = [0.0] * len(dates)
    for m in four:
        idx = [j for j, d in enumerate(dates) if d[:7] == m]
        for j in idx:
            x[j] = 1.0 / len(idx)
    r = sel.g5_stability(x, dates, sigma)[1]
    assert math.isclose(r["max_month_share"], 0.25, rel_tol=1e-12) and r["b"] is (r["max_month_sum"] <= 0.25 *
                                                                               r["total"])
    x3 = [v * (1.0 if dates[j][:7] != months[1] else 1.01) for j, v in enumerate(x)]
    assert not sel.g5_stability(x3, dates, sigma)[1]["b"]
    neg = sel.g5_stability([-1.0] * len(dates), dates, sigma)[1]
    assert not neg["b"]


def test_g5b_exact_quarter_share_passes(dates, sigma):
    """Integer nets make the 25% comparison exact: 4 months of 10 each, total 40 -> max share exactly 0.25."""
    months = sorted({d[:7] for d in dates})
    x = [0.0] * len(dates)
    for m in months[1:5]:
        j = next(j for j, d in enumerate(dates) if d[:7] == m)
        x[j] = 10.0
    r = sel.g5_stability(x, dates, sigma)[1]
    assert r["total"] == 40.0 and r["max_month_sum"] == 10.0 and r["b"]
    x[next(j for j, d in enumerate(dates) if d[:7] == months[6])] = -1e-9
    assert not sel.g5_stability(x, dates, sigma)[1]["b"]


def test_g5c_leave_one_month_out(dates, sigma, base):
    x = series(base, 0.3)
    _, det = sel.g5_stability(x, dates, sigma)
    months = sorted({d[:7] for d in dates})
    direct = min(t_stat(moments([v for v, d in zip(x, dates) if d[:7] != m])) for m in months)
    assert det["min_lomo_t"] == pytest.approx(direct, rel=1e-12)
    assert det["c"]
    # a series whose whole edge sits in one month: leaving it out leaves t < 2.5
    y = [0.0 if d[:7] != months[10] else 50.0 for d in dates]
    y = [v + 0.01 * b for v, b in zip(y, base)]
    assert not sel.g5_stability(y, dates, sigma)[1]["c"]


def test_g5c_boundary(dates, sigma, base):
    """min leave-one-month-out t just above / below 2.5."""
    def lomo_min(s):
        return sel.g5_stability(series(base, s), dates, sigma)[1]["min_lomo_t"]
    s_star = bisect(lambda s: lomo_min(s) >= 2.5, 0.0, 0.5, n=60)
    assert sel.g5_stability(series(base, s_star), dates, sigma)[1]["c"]
    assert not sel.g5_stability(series(base, s_star - 1e-6), dates, sigma)[1]["c"]


def test_g5d_terciles_and_ties(dates, sigma):
    t = len(dates)
    sl = sel.tercile_slices(dates, sigma)
    assert [len(s) for s in sl] == [265, 265, 266]
    # ties broken by date: equal sigma -> date order
    flat = sel.tercile_slices(dates, [1.0] * t)
    assert flat[0] == list(range(265)) and flat[2] == list(range(530, 796))
    x = [1.0] * t
    for j in sl[1]:
        x[j] = -0.1
    det = sel.g5_stability(x, dates, sigma)[1]
    assert det["tercile_means"][1] < 0 and not det["d"]
    assert sel.g5_stability([1.0] * t, dates, sigma)[1]["d"]


def test_g5_strict_calendar(dates, sigma):
    with pytest.raises(AssertionError):
        sel.g5_stability([1.0] * 100, dates[:100], sigma[:100])
    ok, _ = sel.g5_stability([1.0] * 100, dates[:100], sigma[:100], strict=False)
    assert ok is False      # fewer than 9 quarters exist in 100 dates


# ---------------------------------------------------------------- failed and constant series, funnel
def test_failed_and_constant(dates, sigma, base):
    t = len(dates)
    cfg = {"E33-S5F15L001A": None,                                          # failed (P5)
           "E33-S5F15L001E": ([0.0] * t, [0] * t),                          # constant: no trade
           "E33-S5F15L010A": (series(base, 0.30), trades(t))}
    res = sel.select(cfg, dates, sigma, N838)
    by = {r["config"]: r for r in res["configs"]}
    assert by["E33-S5F15L001A"]["failed"] and not any(by["E33-S5F15L001A"]["gates"].values())
    c = by["E33-S5F15L001E"]
    assert c["constant"] and c["dsr"] is None and not any(c["gates"].values())
    assert res["funnel"]["failed_configs"] == 1
    assert res["tier_a"] == ["E33-S5F15L010A"]
    assert res["ranking_all"][-1] == "E33-S5F15L001A"     # no series: last
    assert res["best_config"] == "E33-S5F15L010A"
    neg = sel.select({"E33-S5F15L001E": ([0.0] * t, [0] * t), "E33-S5F15L010A": (series(base, -0.1), trades(t))},
                     dates, sigma, N838)
    assert neg["best_config"] == "E33-S5F15L010A" and neg["best_sharpe"] < 0   # a no-trade series is never best
    # Tier B: nothing non-constant remains -> fill with the constant one (a defined series), never the failed
    assert res["tier_b"] == ["E33-S5F15L001E"]
    assert res["tier_b_detail"]["continue"]["filled"] == ["E33-S5F15L001E"]
    assert res["tier_b_detail"]["continue"]["fill_correlations"]["E33-S5F15L001E"]["E33-S5F15L010A"] is None


def test_funnel_counts(dates, sigma, base):
    t = len(dates)
    rng = np.random.default_rng(3)
    cfg = {
        "E33-S5F15L001A": (series(base, 0.30), trades(t)),                 # passes everything
        "E33-S5F15L001E": (series(base, 0.30), [1] * (t - 1) + [0]),      # fails G1 only
        "E33-S5F15L010A": (series(base, 0.05), trades(t)),                 # fails G3, G4 (and G5)
        "E33-S5F15L010E": None,                                            # failed
        "E33-S5F15L100A": (list(0.1 * (0.30 + rng.standard_normal(t))), trades(t, 1)),  # G2 fails (tiny nets)
    }
    res = sel.select(cfg, dates, sigma, N838)
    by = {r["config"]: r["gates"] for r in res["configs"]}
    assert all(by["E33-S5F15L001A"].values())
    assert not by["E33-S5F15L001E"]["G1"] and all(v for k, v in by["E33-S5F15L001E"].items() if k != "G1")
    alone = res["funnel"]["alone"]
    assert alone["G1"] == sum(1 for g in by.values() if g["G1"])
    for gname in sel.GATES:
        assert alone[gname] == sum(1 for g in by.values() if g[gname])
    order = res["funnel"]["in_order"]
    assert list(order) == ["G1", "G1..G2", "G1..G3", "G1..G4", "G1..G5"]
    assert order["G1..G5"] == sum(1 for g in by.values() if all(g.values()))
    assert all(a >= b for a, b in zip(list(order.values()), list(order.values())[1:]))


# ---------------------------------------------------------------- ranking
def _r(cid, sharpe, count):
    return {"config": cid, **sel.parse_id(cid), "defined": True, "sharpe": sharpe, "trade_count": count}


def test_ranking_tie_breaks():
    rs = [
        _r("E33-S5F15L001A", 0.250049, 900),   # rounds to 0.2500
        _r("E33-S1F15L001A", 0.249951, 900),   # rounds to 0.2500: same SR, same trades -> lower set index first
        _r("E33-S1F15G2050", 0.25, 800),       # 0.2500, fewer trades -> first
        _r("E33-S1F15L001E", 0.25, 900),       # same as S1F15L001A except grid -> after it
        _r("E33-S1T15L001A", 0.25, 900),       # TB15 after FH15 at equal h
        _r("E33-S1F05L001A", 0.25, 900),       # shorter horizon before
        _r("E33-S1F15G3200", 0.25, 900),       # LGBM after every LOGIT at equal SR and trades
        _r("E33-S2F60L100E", 0.2501, 2000),    # higher rounded SR: first of all
    ]
    order = [r["config"] for r in sorted(rs, key=sel.rank_key)]
    assert order == ["E33-S2F60L100E", "E33-S1F15G2050", "E33-S1F05L001A", "E33-S1F15L001A", "E33-S1F15L001E",
                     "E33-S1T15L001A", "E33-S5F15L001A", "E33-S1F15G3200"]


def test_ranking_uses_python_round():
    a, b = _r("E33-S1F15L001A", 0.21235, 900), _r("E33-S1F15L001E", 0.21244, 900)
    assert round(0.21235, 4) == round(0.21244, 4) == 0.2124   # same key value: falls to the grid tie-break
    assert sorted([b, a], key=sel.rank_key)[0]["config"] == "E33-S1F15L001A"


def test_parse_id_matches_search33():
    import search33 as s
    for cid in s.all_config_ids():
        p, c = sel.parse_id(cid), s.parse_config_id(cid)
        assert (p["set"], p["label"], p["grid"], p["family"], p["h"]) == (c.set_name, c.label, c.grid, c.family,
                                                                          c.h)
    with pytest.raises(ValueError):
        sel.parse_id("E33-S6F15L001A")


# ---------------------------------------------------------------- walks
def _correlated(base, rng, rho: float, sr: float) -> list:
    noise = rng.standard_normal(len(base))
    noise = (noise - noise.mean()) / noise.std()
    z = rho * base + math.sqrt(1 - rho * rho) * noise
    z = (z - z.mean()) / z.std()
    return list(10.0 * (sr + z))


def test_tier_a_walk_correlation_and_cap(dates, sigma, base):
    t = len(dates)
    rng = np.random.default_rng(5)
    others = [rng.standard_normal(t) for _ in range(4)]
    others = [(o - o.mean()) / o.std() for o in others]
    cfg = {
        "E33-S5F15L001A": (series(base, 0.34), trades(t)),                       # rank 1, taken
        "E33-S5F15L001E": (_correlated(base, rng, 0.95, 0.33), trades(t)),      # rho > 0.7: skipped
        "E33-S5F15L010A": (list(10.0 * (0.32 + others[0])), trades(t)),         # taken
        "E33-S5F15L010E": (list(10.0 * (0.31 + others[1])), trades(t)),         # taken (third)
        "E33-S5F15L100A": (list(10.0 * (0.30 + others[2])), trades(t)),         # passes but Tier A is full
    }
    res = sel.select(cfg, dates, sigma, N838)
    assert res["ranking_pass"][:2] == ["E33-S5F15L001A", "E33-S5F15L001E"]
    assert res["tier_a"] == ["E33-S5F15L001A", "E33-S5F15L010A", "E33-S5F15L010E"]
    skipped = [e for e in res["tier_a_log"] if e["config"] == "E33-S5F15L001E"][0]
    assert not skipped["taken"] and skipped["rho_with_taken"]["E33-S5F15L001A"] > 0.7
    # the walk stopped at the third member; L100A was never examined
    assert "E33-S5F15L100A" not in [e["config"] for e in res["tier_a_log"]]
    # Tier B (continue): from after L010E in the all-config order -> L100A, then nothing else -> fill L001E
    tb = res["tier_b_detail"]["continue"]
    assert tb["walked"] == ["E33-S5F15L100A"] and tb["filled"] == ["E33-S5F15L001E"]
    assert tb["fill_correlations"]["E33-S5F15L001E"]["E33-S5F15L001A"] > 0.7


def test_tier_b_readings_differ_on_a_high_ranked_gate_failure(dates, sigma, base):
    """A configuration ranked above the Tier A member but failing G1 is Tier B under 'restart' only."""
    t = len(dates)
    rng = np.random.default_rng(9)
    o = [rng.standard_normal(t) for _ in range(3)]
    o = [(v - v.mean()) / v.std() for v in o]
    cfg = {
        "E33-S5F15L001A": (list(10.0 * (0.40 + o[0])), [1] * (t - 1) + [0]),   # best SR, fails G1
        "E33-S5F15L001E": (series(base, 0.30), trades(t)),                     # Tier A
        "E33-S5F15L010A": (list(10.0 * (0.10 + o[1])), trades(t)),            # fails G3
        "E33-S5F15L010E": (list(10.0 * (0.05 + o[2])), trades(t)),            # fails G3
    }
    res = sel.select(cfg, dates, sigma, N838)
    assert res["tier_a"] == ["E33-S5F15L001E"]
    assert res["tier_b_detail"]["continue"]["tier_b"] == ["E33-S5F15L010A", "E33-S5F15L010E"]
    assert res["tier_b_detail"]["restart"]["tier_b"] == ["E33-S5F15L001A", "E33-S5F15L010A"]
    assert res["tier_b_reading"] == "continue" and res["tier_b"] == ["E33-S5F15L010A", "E33-S5F15L010E"]
    res_r = sel.select(cfg, dates, sigma, N838, tier_b_reading="restart")
    assert res_r["tier_b"] == ["E33-S5F15L001A", "E33-S5F15L010A"]


def test_empty_tier_a(dates, sigma, base):
    t = len(dates)
    cfg = {"E33-S5F15L001A": (series(base, 0.05), trades(t)), "E33-S5F15L001E": None}
    res = sel.select(cfg, dates, sigma, N838)
    assert res["tier_a"] == [] and res["ranking_pass"] == []
    assert res["best_config"] == "E33-S5F15L001A"


# ---------------------------------------------------------------- reports (never gates)
def test_reference_thresholds_p72():
    ref = sel.reference_thresholds(300, N838)
    assert round(ref["bonferroni_holm_step1_m"], 3) == 3.588
    assert round(ref["by_rank1"], 3) == 4.042 and round(ref["by_c_m"], 3) == 6.283
    assert round(ref["bonferroni_at_N"], 3) == 3.847
    assert [round(ref["test_holm_K9"][k], 3) for k in (1, 2, 3)] == [2.539, 2.773, 2.902]


def test_bh_holm():
    from statistics import NormalDist
    z = NormalDist()
    ts = {"E33-S5F15L001A": z.inv_cdf(1 - 0.001), "E33-S5F15L001E": z.inv_cdf(1 - 0.02),
          "E33-S5F15L010A": z.inv_cdf(1 - 0.03), "E33-S5F15L010E": None}
    res = sel.bh_holm([{"config": k, "t": v} for k, v in ts.items()])
    # m = 4: BH thresholds 0.0125, 0.025, 0.0375, 0.05 -> ranks 1..3 rejected; Holm: 0.001 <= 0.0125, 0.02 > 0.0167
    assert res["bh_rejected"] == ["E33-S5F15L001A", "E33-S5F15L001E", "E33-S5F15L010A"]
    assert res["holm_rejected"] == ["E33-S5F15L001A"]
    assert res["p_values"]["E33-S5F15L010E"] == 1.0


def test_pbo_report(dates, sigma, base):
    t = len(dates)
    rng = np.random.default_rng(2)
    cfg = {f"E33-S5F15{g}": (list(rng.standard_normal(t)), trades(t)) for g in sel.GRID_ORDER[:4]}
    cfg["E33-S5F15G2050"] = None
    res = sel.select(cfg, dates, sigma, N838)
    assert res["reports"]["pbo"]["n_strategies"] == 4 and 0.0 <= res["reports"]["pbo"]["pbo"] <= 1.0


# ---------------------------------------------------------------- loading a search tree
def test_load_root_and_cli(tmp_path, dates, sigma, base):
    t = len(dates)
    root = tmp_path
    fdir = root / "features" / "abcdef012345" / "_day"
    fdir.mkdir(parents=True)
    for d, s in zip(dates, sigma):
        (fdir / f"{d}.json").write_text(json.dumps({"sigma_zm": s}))
    good = series(base, 0.3)
    for cid, x in (("E33-S5F15L001A", good), ("E33-S5F15L001E", None)):
        b = root / "search" / cid
        b.mkdir(parents=True)
        if x is None:
            (b / "stats.json").write_text(json.dumps({"failed": True}))
        else:
            pd.DataFrame({"date": dates, "X_D": x, "n_trades": [2] * t}).to_parquet(b / "daily.parquet")
            (b / "stats.json").write_text(json.dumps({"failed": False, "trade_count": 2 * t,
                                                      "moments": moments(x)}))
        (b / "DONE").write_text("{}")
    ds, sg, cfg = sel.load_root(root, ["E33-S5F15L001A", "E33-S5F15L001E"])
    assert ds == dates and sg == pytest.approx(sigma) and cfg["E33-S5F15L001E"] is None
    out = tmp_path / "sel.json"
    assert sel.main(["--root", str(root), "--ids", "E33-S5F15L001A", "E33-S5F15L001E", "--n", "838",
                     "--out", str(out)]) == 0
    res = json.loads(out.read_text())
    assert res["tier_a"] == ["E33-S5F15L001A"] and res["n_trials"] == 838
    with pytest.raises(RuntimeError):
        sel.load_root(root, ["E33-S5F15L010A"])                 # no DONE marker
    (root / "search" / "E33-S5F15L001A" / "stats.json").write_text(
        json.dumps({"failed": False, "trade_count": 2 * t + 1, "moments": moments(good)}))
    with pytest.raises(ValueError):
        sel.load_root(root, ["E33-S5F15L001A"])                 # stats disagree with daily.parquet
