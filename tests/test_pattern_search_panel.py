"""The composed search panel (reports/stage_e20_plan.md sections 5 and 6): the feature list equals
the plan's 36 exactly, the frozen checks plan 6 names are re-applied (a shifted root makes the
composed builder raise; the window guard; the empty-panel refusal), and check_panel's refusals."""

from __future__ import annotations

import dataclasses
from datetime import date

import numpy as np
import pytest

from pattern_search import constants as K
from pattern_search.panel import (
    PanelCheckError,
    build_search_panel,
    check_panel,
    expected_feature_cols,
)
from tests._pattern_search_synth import SEED, panel_small, world_small

PLAN_DROPPED = (  # plan 5.1, the 33 dropped signals
    "k1_vxn_regime", "k1_vxn_band", "k2_predrift_move", "k3_ldnmom_trend", "k3_ldnrev_move",
    "k3_ecbfix_mto", "k3_ecbfix_msince", "k4_apipre_ret", "k4_eiamom_r3", "k5_pmfix_move",
    "k5_preauc_msince", "k6_limitcont_dir", "k6_wasdepre_drift", "k9_anncday", "g13_min_to_rel",
    "g14_min_since_rel", "g15_rel_day", "k2_fomc_mto", "g17_mbt", "g17_mes", "k7_montrend_ret",
    "k7_rev2h_ret", "k7_expiry_mto", "k7_expiry_msince", "k8_wkndbtc_move", "k8_flight_ret",
    "k8_flight_tail", "k6_crushgap_gap", "k8_oilcad_ret", "k8_oilcad_z", "k3_mehedge_req",
    "k3_tkypost_msince", "k3_tkypre_msince")


def test_the_feature_list_is_the_plans_34_kept_plus_the_two_rod_features() -> None:
    from ml_route_v2.signals import REGISTRY

    assert len(K.KEPT_SIGNALS) == K.N_KEPT == 34 and len(set(K.KEPT_SIGNALS)) == 34
    assert len(PLAN_DROPPED) == 33 and not set(PLAN_DROPPED) & set(K.KEPT_SIGNALS)
    assert set(K.KEPT_SIGNALS) | set(PLAN_DROPPED) == set(REGISTRY)
    assert list(K.KEPT_SIGNALS) == [n for n in REGISTRY if n in K.KEPT_SIGNALS]
    assert (*K.KEPT_SIGNALS, "rod_ret", "rod_absratio") == K.FEATURE_NAMES
    assert K.ACCEPTED_PART_A == ()
    assert "k2_fomc_mto" not in K.KEPT_SIGNALS


def test_every_kept_signal_is_covered_by_the_17_roots_without_mes() -> None:
    from ml_route_v2.phase1.world import signal_coverage

    cov = signal_coverage(K.VEHICLES, unavailable=dict(K.UNAVAILABLE_ROOTS))
    assert set(K.KEPT_SIGNALS) <= set(cov.covered)
    for n in ("g17_mbt", "g17_mes", "k7_montrend_ret", "k8_wkndbtc_move", "k6_crushgap_gap",
              "k8_flight_ret"):
        assert n in cov.uncovered


def test_the_composed_panel_has_exactly_the_plans_features_and_passes_its_checks() -> None:
    panel = panel_small()
    assert tuple(panel.signal_names) == K.FEATURE_NAMES
    assert tuple(panel.feature_cols) == expected_feature_cols()
    rec = check_panel(panel)
    assert rec["n_features"] == 36 and set(rec["rows_by_t_index"]) == {1, 2, 3, 4}
    assert rec["ok_rows_t4"]["h120"] == 0 and rec["ok_rows_t4"]["h60"] > 0
    assert len({c for c in panel.feature_cols if c.startswith("z_")}) == 36


def test_the_panel_keeps_only_training_calendar_dates_and_counts_the_cut() -> None:
    panel, w = panel_small(), world_small()
    days = set(panel.frame["trade_date"].dt.date)
    assert days <= set(w.calendar)
    assert panel.counts["rows_warmup_dropped"] > 0 and panel.counts["rows_training"] == len(
        panel.frame)


def test_a_shifted_root_makes_the_composed_builder_raise() -> None:
    from ml_route_v2.pipeline import BarGridError
    from pattern_search.world import synthetic_world

    w = synthetic_world(date(2021, 5, 3), date(2021, 5, 14), seed=SEED, warmup_dates=5,
                        plant={"kind": "shift", "roots": ("ZN",), "minutes": -1})
    with pytest.raises(BarGridError, match="ZN"):
        build_search_panel(w)


def test_the_window_guard_refuses_a_world_reaching_march_2024() -> None:
    from pattern_search.guard import GuardRefusal
    from pattern_search.world import synthetic_world

    w = synthetic_world(date(2024, 2, 26), date(2024, 3, 4), seed=SEED, warmup_dates=3,
                        vehicles=("MNQ",))
    with pytest.raises(GuardRefusal, match="2024-03-01"):
        build_search_panel(w, check_grid=False)


def test_a_planted_march_2024_row_fails_assert_window() -> None:
    from ml_route_v2.panel import WindowError, assert_window

    panel = panel_small()
    frame = panel.frame.copy()
    frame.iloc[0, frame.columns.get_loc("trade_date")] = np.datetime64("2024-03-01")
    with pytest.raises(WindowError):
        assert_window(dataclasses.replace(panel, frame=frame), "train")


def test_an_empty_training_panel_is_refused() -> None:
    from ml_route_v2.pipeline import PipelineError

    w = dataclasses.replace(world_small(), calendar=(date(2030, 1, 2),))
    with pytest.raises(PipelineError, match="empty"):
        build_search_panel(w)


def test_check_panel_refuses_each_planted_defect() -> None:
    panel = panel_small()
    with pytest.raises(PanelCheckError, match="36"):
        check_panel(dataclasses.replace(panel, signal_names=panel.signal_names[:-1]))
    with pytest.raises(PanelCheckError, match="feature_cols"):
        check_panel(dataclasses.replace(panel, feature_cols=panel.feature_cols[:-1]))
    frame = panel.frame.copy()
    t4 = np.flatnonzero(frame["t_index"].to_numpy() == K.T4_INDEX)[0]
    frame.iloc[t4, frame.columns.get_loc("ok_h120")] = True
    with pytest.raises(PanelCheckError, match="h120"):
        check_panel(dataclasses.replace(panel, frame=frame))
    frame = panel.frame.copy()
    frame.iloc[3, frame.columns.get_loc("z_rod_ret")] = np.nan
    with pytest.raises(PanelCheckError, match="non-finite"):
        check_panel(dataclasses.replace(panel, frame=frame))
    late = np.asarray(panel.avail_max_ts_ns).copy()
    late[0] = int(panel.frame["decision_ts_ns"].iloc[0]) + 1
    with pytest.raises(PanelCheckError, match="available after"):
        check_panel(dataclasses.replace(panel, avail_max_ts_ns=late))


def test_horizon_data_accepts_the_composed_panel_for_every_horizon() -> None:
    from ml_route_v2.constants import HORIZONS
    from ml_route_v2.cpcv import horizon_data

    panel = panel_small()
    for h in HORIZONS:
        data = horizon_data(panel, h)
        assert data.X.shape[1] == len(panel.feature_cols) == 94
        t4 = data.rows["t_index"].to_numpy() == K.T4_INDEX
        assert (t4.any()) == (h != "h120")
