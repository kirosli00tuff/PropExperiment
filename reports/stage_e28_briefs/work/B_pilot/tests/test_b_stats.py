"""Kaplan-Meier, the day-block bootstrap, VPO and the cell statistics (spec section 4)."""

import measure_stats as ms
import numpy as np
import pytest


def test_kaplan_meier_by_hand():
    # durations 1, 2, 2, 3, 5 with events 1, 1, 0, 1, 0:
    # t=1: 5 at risk, 1 event -> S = 0.8; t=2: 4 at risk, 1 event -> 0.6; t=3: 2 at risk -> 0.3
    times, surv = ms.kaplan_meier(np.array([1, 2, 2, 3, 5.0]), np.array([1, 1, 0, 1, 0]))
    assert times.tolist() == [1, 2, 3]
    assert surv.tolist() == pytest.approx([0.8, 0.6, 0.3])
    assert ms.km_cdf(times, surv, 0.5) == 0.0
    assert ms.km_cdf(times, surv, 2.5) == pytest.approx(0.4)
    assert ms.km_median(times, surv) == 3


def test_km_censoring_at_60s_including_cancel_latency_fills():
    ttf = np.array([0.5, 12.0, 60.03, np.inf, np.inf])
    filled = np.array([True, True, True, False, False])
    durations, events = ms.km_inputs(ttf, filled)
    assert durations.tolist() == [0.5, 12.0, 60.0, 60.0, 60.0]
    assert events.tolist() == [True, True, False, False, False]
    times, surv = ms.kaplan_meier(durations, events)
    # no censoring before 60 s: KM equals the empirical share filled by t
    assert ms.km_cdf(times, surv, 10) == pytest.approx(1 / 5)
    assert ms.km_cdf(times, surv, 60) == pytest.approx(2 / 5)
    assert ms.km_median(times, surv) is None


def test_bootstrap_weights_seed_28_reproducible_and_by_day():
    w1, w2 = ms.bootstrap_weights(7), ms.bootstrap_weights(7)
    assert w1.shape == (2000, 7) and np.array_equal(w1, w2)
    assert np.all(w1.sum(axis=1) == 7)
    expected = np.random.default_rng(28).integers(0, 7, size=(2000, 7))
    assert np.array_equal(w1[0], np.bincount(expected[0], minlength=7))


def test_day_block_resampling_keeps_days_whole():
    # day 0: 0 of 10 filled; day 1: 10 of 10 filled -> any replicate is 0, 0.5 or 1
    num, den = np.array([0.0, 10.0]), np.array([10.0, 10.0])
    w = ms.bootstrap_weights(2)
    stat = ms.ratio_stat(num, den, w)
    boot = ms._ratio(w @ num, w @ den)
    assert set(np.round(boot, 9).tolist()) <= {0.0, 0.5, 1.0}
    assert stat["value"] == 0.5 and stat["ci95"] == [0.0, 1.0] and stat["boot_valid"] == 2000


def test_classify_labels():
    assert ms.classify(0.1, 0.3) == ms.POSITIVE
    assert ms.classify(-0.3, -0.1) == ms.NEGATIVE
    assert ms.classify(-0.1, 0.3) == ms.NOT_DIST
    assert ms.classify(None, None) is None


def _one_day_table():
    # 4 T|MAIN placements on day 0: buys fill (markouts 60 s: 1.0 and 2.0), sells do not
    tab = {"day": np.zeros(4, dtype=np.int64), "type": np.array(["T"] * 4, dtype=object),
           "session": np.array(["MAIN"] * 4, dtype=object), "side": np.array([1, 1, -1, -1]),
           "j_ns": np.zeros(4, dtype=np.int64),
           "touch_ns": np.array([1, 2, -1, 5], dtype=np.int64) * 10**9,
           "spec:fill_ns": np.array([2 * 10**9, 30 * 10**9, -1, -1], dtype=np.int64)}
    tab["touch_ns"][2] = -1
    # RS-04 trigger and aggressor of each fill; RS-06 stale flag (1, 0, -1 unknown)
    tab["spec:trigger"] = np.array(["queue", "through", None, None], dtype=object)
    tab["spec:trigger_side"] = np.array(["A", "A", None, None], dtype=object)
    tab["stale"] = np.array([0, 1, 0, -1], dtype=np.int64)
    for h, vals in ((1, [0.5, -0.5]), (10, [1.0, 0.0]), (60, [1.0, 2.0])):
        tab[f"spec:m{h}"] = np.array([*vals, np.nan, np.nan])
        tab[f"spec:drop{h}"] = np.array([None] * 4, dtype=object)
        # RS-05 no-drop variant: equal to the headline except at 60 s, where the second fill's
        # mid comes from the last valid state (-1.0 instead of 2.0)
        nd = [1.0, -1.0] if h == 60 else vals
        tab[f"spec:n{h}"] = np.array([*nd, np.nan, np.nan])
        tab[f"spec:ndrop{h}"] = np.array([None] * 4, dtype=object)
    return tab


def test_cell_stats_vpo_and_net_by_hand():
    tab = _one_day_table()
    mask = (tab["type"] == "T") & (tab["session"] == "MAIN")
    w = ms.bootstrap_weights(1)
    out = ms.cell_stats(tab, mask, "spec", 1, w, fee_side=0.5)
    assert out["placements"] == 4 and out["fills"] == 2
    assert out["fill_rate"]["value"] == 0.5
    assert out["touch_rate"]["value"] == 0.75
    assert out["km"]["p_fill_by_1s"]["value"] == 0.0
    assert out["km"]["p_fill_by_10s"]["value"] == 0.25
    assert out["km"]["p_fill_by_60s"]["value"] == 0.5
    assert out["km"]["median_ttf_s"] == 30.0
    m60 = out["markouts"]["60"]
    assert m60["mean"]["value"] == 1.5 and m60["median"] == 1.5
    assert m60["share_positive"]["value"] == 1.0
    assert m60["mean_net"]["value"] == 1.0
    assert m60["mean_net"]["label"] == ms.POSITIVE  # one day: degenerate interval [1, 1]
    # VPO_60 = fill rate x (mean - fee) = 0.5 x (1.5 - 0.5) = 0.5
    assert out["vpo"]["60"]["value"] == pytest.approx(0.5)
    assert out["vpo"]["60"]["ci95"] == [pytest.approx(0.5), pytest.approx(0.5)]
    # VPO_10 = 0.5 x (0.5 - 0.5) = 0
    assert out["vpo"]["10"]["value"] == pytest.approx(0.0)
    assert out["markouts"]["1"]["share_positive"]["value"] == 0.5
    # RS-04: fills by trigger/aggressor; RS-06: stale share over the 3 placements with a known
    # flag (1 of 3); RS-05: no-drop mean 60 s = (1 - 1) / 2 = 0, net = -0.5, VPO = 0.5 x -0.5
    assert out["fills_by_trigger"] == {"queue/A": 1, "through/A": 1}
    assert out["stale_share"]["value"] == pytest.approx(1 / 3)
    n60 = out["markouts_nodrop"]["60"]
    assert n60["mean"]["value"] == 0.0 and n60["mean_net"]["value"] == -0.5
    assert out["vpo_nodrop"]["60"]["value"] == pytest.approx(-0.25)
    # no second fee given: no alt keys
    assert "mean_net_alt" not in m60 and "vpo_alt" not in out


def test_second_fee_reports_net_markouts_and_vpo_beside_the_primary():
    # spec section 0 (QM): primary 0.1368 tick per side, conservative reading 0.296
    tab = _one_day_table()
    mask = (tab["type"] == "T") & (tab["session"] == "MAIN")
    w = ms.bootstrap_weights(1)
    out = ms.cell_stats(tab, mask, "spec", 1, w, fee_side=0.1368, fee_side_alt=(0.296,))
    m60, n60 = out["markouts"]["60"], out["markouts_nodrop"]["60"]
    assert ms.fee_key(0.296) == "0.296"
    assert m60["mean_net"]["value"] == pytest.approx(1.5 - 0.1368)
    assert m60["mean_net_alt"]["0.296"]["value"] == pytest.approx(1.5 - 0.296)
    assert m60["mean_net_alt"]["0.296"]["ci95"] == [pytest.approx(1.204), pytest.approx(1.204)]
    assert n60["mean_net_alt"]["0.296"]["value"] == pytest.approx(-0.296)
    assert n60["mean_net_alt"]["0.296"]["label"] == ms.NEGATIVE
    # VPO_60 at 0.296 = 0.5 x (1.5 - 0.296); no-drop = 0.5 x (0 - 0.296)
    assert out["vpo_alt"]["0.296"]["60"]["value"] == pytest.approx(0.5 * 1.204)
    assert out["vpo_nodrop_alt"]["0.296"]["60"]["value"] == pytest.approx(-0.148)
    assert out["vpo"]["60"]["value"] == pytest.approx(0.5 * (1.5 - 0.1368))
    res = ms.all_cells(tab, ["spec"], 1, 0.1368, fee_side_alt=(0.296,))
    md = ms.render_cells_markdown(res)
    assert "| mean NET markout 60 s at fee 0.296 tick/side |" in md
    assert "| VPO 60 s at fee 0.296 tick/side |" in md


def test_all_cells_has_every_cell_and_side():
    tab = _one_day_table()
    res = ms.all_cells(tab, ["spec"], 1, 0.5)
    assert set(res["spec"]) == {"T|MAIN", "T|OVERNIGHT", "I|MAIN", "I|OVERNIGHT"}
    assert set(res["spec"]["T|MAIN"]) == {"pooled", "buy", "sell"}
    assert res["spec"]["T|MAIN"]["buy"]["fill_rate"]["value"] == 1.0
    assert res["spec"]["T|MAIN"]["sell"]["fill_rate"]["value"] == 0.0
    assert res["spec"]["I|MAIN"]["pooled"]["placements"] == 0
    assert res["spec"]["I|MAIN"]["pooled"]["fill_rate"]["value"] is None
    md = ms.render_cells_markdown(res)
    assert "### Cell T|MAIN (rule spec)" in md and "| fill rate |" in md


def test_vpo_is_zero_without_fills_and_undefined_without_placements():
    vals = ms._vpo_values(np.array([0.0, 2.0, 0.0, 2.0]), np.array([10.0, 10.0, 0.0, 10.0]),
                          np.array([0.0, 3.0, 0.0, 0.0]), np.array([0.0, 2.0, 0.0, 0.0]), 0.5)
    # no fill -> 0; 2 of 10 filled, mean 1.5 -> 0.2 x 1.0; no placements -> NaN;
    # fills whose markouts were all dropped -> NaN
    assert vals[0] == 0.0 and vals[1] == pytest.approx(0.2)
    assert np.isnan(vals[2]) and np.isnan(vals[3])
