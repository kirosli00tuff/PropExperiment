"""Tests for synth33 (P4.2 synthetic proof generator). Non-production seeds only (9001+, 70001+).

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_synth33.py
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(PIPE), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth33 as g  # noqa: E402

N_SMALL = 60


@pytest.fixture(scope="module")
def small():
    return g.generate(9011, "planted", N_SMALL)


def test_production_seed_kinds():
    assert g.kind_of_seed(1) == "null" and g.kind_of_seed(20) == "null"
    assert g.kind_of_seed(101) == "planted" and g.kind_of_seed(120) == "planted"
    with pytest.raises(ValueError):
        g.kind_of_seed(9001)
    assert g.beta_of("null") == 0.0 and g.beta_of("planted") == g.PLANT_BETA


def test_beta_is_the_calibrated_value():
    cal = json.loads((PIPE.parent / "ProofCoder_calibration.json").read_text())
    assert g.PLANT_BETA == cal["beta"]
    assert abs(cal["check_mean"] - 0.35) < 3 * cal["check_se"]


def test_deterministic_per_seed():
    a = g.generate(9012, "null", 25)
    b = g.generate(9012, "null", 25)
    c = g.generate(9013, "null", 25)
    assert np.array_equal(a.feats, b.feats) and np.array_equal(a.path.bid, b.path.bid)
    for lb in g.LABELS:
        for k in g.LABEL_COLUMNS:
            assert np.array_equal(a.labels[lb][k], b.labels[lb][k], equal_nan=True), (lb, k)
    assert not np.array_equal(a.feats, c.feats)


def test_reduced_calendar_is_a_prefix():
    a = g.generate(9014, "planted", 25)
    b = g.generate(9014, "planted", 40)
    assert np.array_equal(a.path.bid, b.path.bid[:45])
    assert np.array_equal(a.feats, b.feats[:25])


def test_schema_and_engine_load(tmp_path):
    import search33 as s
    g.write_seed(9015, tmp_path, "planted", 30)
    for lb in g.LABELS:
        t = s.load_tables(tmp_path, lb, expected_n=None)
        assert t.X.shape == (30 * (278 - s.LABEL_H[lb]), 59)
        assert "mid_move" in t.lab
    assert tuple(g.FEATURE_COLUMNS) == tuple(s.FEATURE_COLUMNS)
    assert tuple(c for c in g.LABEL_COLUMNS if c != "mid_move") == tuple(s.LABEL_COLUMNS)
    assert (tmp_path / "synth" / "DONE").exists() and (tmp_path / "synth" / "oracle.json").exists()
    assert g.write_seed(9015, tmp_path, "planted", 30)["seed"] == 9015    # resume: skipped


def test_calendar_rules(small):
    cal = small.cal
    for lb, (kind, h) in g.LABELS.items():
        lab = small.labels[lb]
        for d in range(cal.n_oof):
            if cal.excluded[g.N_BURN + d]:
                assert not lab["entry_ok"][d].any() and not lab["row_ok"][d].any()
                assert np.all(np.isnan(lab["mid_move"][d]))
                continue
            t = lab["t_ns"][d]
            hit = np.zeros(len(t), bool)
            for r in cal.releases[g.N_BURN + d]:
                hit |= (t <= r + 30 * g.MIN_NS) & (t + g.L_NS + h * g.MIN_NS >= r - 2 * g.MIN_NS)
            assert np.array_equal(lab["entry_ok"][d], ~hit)
            if cal.releases[g.N_BURN + d]:
                assert hit.any()
            assert lab["t_ns"][d][-1] + g.L_NS + h * g.MIN_NS <= cal.t0_ns[g.N_BURN + d] + 278 * g.MIN_NS + g.L_NS


def test_fh_label_invariants(small):
    lab = small.labels["F15"]
    ok = lab["row_ok"]
    y, nl, ns = lab["y"][ok], lab["n_long"][ok], lab["n_short"][ok]
    assert np.all((y == 1) == (nl > 0)) and np.all((y == -1) == (ns > 0))
    assert not np.any((nl > 0) & (ns > 0))
    assert np.array_equal(lab["long_net"][ok], nl) and np.array_equal(lab["short_net"][ok], ns)
    assert np.all(lab["long_exit_ns"][ok] == lab["t_ns"][ok] + 15 * g.MIN_NS + g.L_NS)
    assert np.all(lab["long_entry_ns"][ok] == lab["t_ns"][ok] + g.L_NS)
    gross = nl + g.FEE
    assert np.allclose(gross, np.round(gross))       # integer ticks net of f
    assert np.allclose(ns + g.FEE, np.round(ns + g.FEE))
    # short side against independent arithmetic (ProofReview N9): bid(B_i) - ask(B_{i+15}) - f
    path, cal = small.path, small.cal
    for d in range(0, cal.n_oof, 7):
        dd = g.N_BURN + d
        r = lab["row_ok"][d]
        i = np.flatnonzero(r)
        ref = (path.bid[dd, g.PRE + i, 1] - path.ask[dd, g.PRE + i + 15, 1]).astype(float) - g.FEE
        assert np.array_equal(lab["n_short"][d][r], ref) and np.array_equal(lab["short_net"][d][r], ref)
        assert np.all(lab["short_exit_ns"][d][r] == lab["t_ns"][d][r] + 15 * g.MIN_NS + g.L_NS)


def test_tb_label_against_a_row_loop(small):
    lab, path, cal = small.labels["T30"], small.path, small.cal
    h = 30
    for d in (0, 7, 33):
        dd = g.N_BURN + d
        if cal.excluded[dd]:
            continue
        mid2 = path.bid[dd, :, 1] + path.ask[dd, :, 1]
        b = path.sigma_zm[dd] * math.sqrt(h)
        for i in range(0, 278 - h, 17):
            jb = g.PRE + i
            k_hit, y = h, 0
            for k in range(1, h + 1):
                diff = mid2[jb + k] - mid2[jb]
                if diff >= 2 * b:
                    k_hit, y = k, 1
                    break
                if diff <= -2 * b:
                    k_hit, y = k, -1
                    break
            jx = jb + k_hit
            n_long = float(path.bid[dd, jx, 2] - path.ask[dd, jb, 1]) - g.FEE
            n_short = float(path.bid[dd, jb, 1] - path.ask[dd, jx, 2]) - g.FEE
            assert lab["y"][d, i] == (y if lab["row_ok"][d, i] else 0)
            assert lab["long_net"][d, i] == n_long or not lab["entry_ok"][d, i]
            assert lab["short_net"][d, i] == n_short or not lab["entry_ok"][d, i]
            assert lab["n_short"][d, i] == n_short or not lab["row_ok"][d, i]
            assert lab["long_exit_ns"][d, i] == lab["t_ns"][d, i] + k_hit * g.MIN_NS + 2 * g.L_NS \
                or not lab["entry_ok"][d, i]


def test_weights_match_lab33(small):
    import lab33
    for lb in g.LABELS:
        lab = small.labels[lb]
        for d in range(0, small.cal.n_oof, 9):
            r = lab["row_ok"][d]
            if not r.any():
                continue
            ref = lab33.uniqueness_weights(lab["t_ns"][d][r], lab["span_end_ns"][d][r])
            assert np.allclose(lab["w"][d][r], ref, rtol=1e-12, atol=0)


def test_no_look_ahead_in_features(small):
    """Changing the path after minute i0 leaves every feature at minutes <= i0 unchanged."""
    i0 = 120
    p2 = copy.deepcopy(small.path)
    cut = g.PRE + i0 + 1
    p2.bid[:, cut:, :] += 7
    p2.ask[:, cut:, :] += 7
    p2.bid[:, cut - 1, 1:] += 3            # B and C points of minute i0 itself (t + L, t + 2L): ProofReview N8
    p2.ask[:, cut - 1, 1:] += 3
    p2.z[:, cut:] += 1.0
    p2.spread_a[:, cut:] = 3.0 - p2.spread_a[:, cut:]
    f1 = g.make_features(9011, small.cal, small.path)
    f2 = g.make_features(9011, small.cal, p2)
    assert np.array_equal(f1[:, :i0 + 1], f2[:, :i0 + 1])
    assert not np.array_equal(f1[:, i0 + 1:], f2[:, i0 + 1:])


def test_null_has_no_drift_and_plant_is_f3_4():
    null = g.generate(9016, "null", 200, with_features=False, labels=("F15",))
    lab = null.labels["F15"]
    ok = lab["row_ok"]
    z = null.path.z[g.N_BURN:][:, g.PRE:g.PRE + lab["t_ns"].shape[1]][ok]
    mv = lab["mid_move"][ok]
    assert abs(np.corrcoef(z, mv)[0, 1]) < 0.02
    planted = g.generate(9016, "planted", 200, with_features=False, labels=("F15",))
    lab_p = planted.labels["F15"]
    mv_p = lab_p["mid_move"][lab_p["row_ok"]]
    assert np.corrcoef(z, mv_p)[0, 1] > 0.1
    assert g.PLANT_FEATURE == "F3_4" and g.FEATURE_COLUMNS.index("F3_4") == 37


def test_oracle_probabilities_closed_form_vs_monte_carlo():
    rng = np.random.default_rng(1)
    q = g.SPREAD2_SHARE
    for m, v in ((0.0, 150.0), (4.0, 140.0), (-2.0, 9.0)):
        n = 1_000_000
        a = rng.uniform(0, 1000, n)
        e = a + rng.normal(m, math.sqrt(v), n)
        se, sx = rng.random(n) < q, rng.random(n) < q
        bid_e = np.where(se, np.floor(a + 0.5) - 1, np.floor(a))
        ask_e = bid_e + np.where(se, 2, 1)
        bid_x = np.where(sx, np.floor(e + 0.5) - 1, np.floor(e))
        ask_x = bid_x + np.where(sx, 2, 1)
        pu, pd = g.fh_class_probs(np.array([m]), np.array([v]))
        assert abs((bid_x - ask_e - g.FEE > 0).mean() - pu[0]) < 0.002
        assert abs((bid_e - ask_x - g.FEE > 0).mean() - pd[0]) < 0.002


def test_drift_moments_by_simulation():
    beta, h = 0.4, 15
    m, vz = g.drift_moments(beta, h)
    rng = np.random.default_rng(4)
    n, phi = 200_000, g.PLANT_PHI
    z = np.empty((n, h + 1))
    z[:, 0] = 1.5
    for k in range(1, h + 1):
        z[:, k] = phi * z[:, k - 1] + math.sqrt(1 - phi * phi) * rng.standard_normal(n)
    c = np.ones(h + 1)
    c[0], c[h] = 59 / 60, 1 / 60
    drift = beta * (z * c).sum(axis=1)
    assert drift.mean() == pytest.approx(m * 1.5, rel=0.01)
    assert drift.var() == pytest.approx(vz, rel=0.02)


def test_oracle_simulation_matches_search33(small):
    import search33 as s
    lab, path, cal = small.labels["F15"], small.path, small.cal
    n = lab["t_ns"].shape[1]
    gm, vz = g.drift_moments(small.beta, 15)
    zi = path.z[g.N_BURN:][:, g.PRE:g.PRE + n]
    pu, pd = g.fh_class_probs(gm * zi, (path.sigma[g.N_BURN:] ** 2 * 15)[:, None] + vz)
    ok = lab["row_ok"]
    mu_l, mu_s = g.class_means(lab["y"][ok], lab["w"][ok], lab["n_long"][ok], lab["n_short"][ok])
    ev_l = pd * mu_l[0] + (1 - pu - pd) * mu_l[1] + pu * mu_l[2]
    ev_s = pd * mu_s[0] + (1 - pu - pd) * mu_s[1] + pu * mu_s[2]
    for d in range(cal.n_oof):
        outcome = {side: {f: lab[f"{side}_{f}"][d] for f in ("made", "net", "entry_ns", "exit_ns", "flags")}
                   for side in ("long", "short")}
        res = s.simulate_date(lab["t_ns"][d], lab["entry_ok"][d], ev_l[d], ev_s[d], outcome)
        trades = res[0]
        tot, k = g.simulate_day(lab["t_ns"][d], lab["entry_ok"][d], ev_l[d], ev_s[d], lab["long_net"][d],
                                lab["short_net"][d], lab["long_exit_ns"][d], lab["short_exit_ns"][d])
        assert k == len(trades) and tot == pytest.approx(sum(t[2] for t in trades), abs=1e-9)


def test_sigma_zm_scale():
    sz = [np.nanmean(g.make_path(s, 0.0, 816).sigma_zm[g.N_BURN:]) for s in range(70001, 70006)]
    assert 2.9 < np.mean(sz) < 3.3
