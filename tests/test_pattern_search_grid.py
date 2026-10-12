"""The 45 configurations (reports/stage_e20_plan.md section 7; F6, F9): the count, the frozen order,
the registry ids E20S-nn = CONFIGS[nn - 1], and the fixed LightGBM settings."""

from __future__ import annotations

from pattern_search import constants as K


def _plan_order() -> list[str]:
    """Plan 7's order rebuilt independently: models outermost (ridge 0.01, 0.1, 1.0, LightGBM
    depth 2, 3), then k 1.5, 2, 3, then horizon h60, h120, hF."""
    models = ["ridge_l0.01", "ridge_l0.1", "ridge_l1", "lgbm_d2", "lgbm_d3"]
    return [f"{m}_k{k}_{h}" for m in models for k in ("1.5", "2", "3")
            for h in ("h60", "h120", "hF")]


def test_the_grid_has_45_configurations_in_the_plans_order() -> None:
    from ml_route_v2.configs import CONFIGS

    assert len(CONFIGS) == K.N_CONFIGS == 45
    assert [c.config_id for c in CONFIGS] == _plan_order()


def test_registry_ids_map_e20s_nn_to_configs_nn_minus_1() -> None:
    ids = K.config_ids()
    assert list(ids) == [f"E20S-{n:02d}" for n in range(1, 46)]
    assert ids["E20S-01"] == "ridge_l0.01_k1.5_h60"
    assert ids["E20S-02"] == "ridge_l0.01_k1.5_h120"
    assert ids["E20S-03"] == "ridge_l0.01_k1.5_hF"
    assert ids["E20S-45"] == "lgbm_d3_k3_hF"
    assert list(ids.values()) == _plan_order()


def test_the_registry_accepts_the_label_and_ids() -> None:
    from pattern_search.preflight import registry_names_valid
    from screening.trial_registry import _ID, _TEST

    assert _TEST.fullmatch(K.REGISTRY_LABEL) and "-" not in K.REGISTRY_LABEL
    assert all(_ID.fullmatch(i) for i in K.CONFIG_IDS) and len(set(K.CONFIG_IDS)) == 45
    registry_names_valid()


def test_the_fixed_lightgbm_settings_are_the_plans() -> None:
    from ml_route_v2.constants import COST_GATE_READING, LGBM_FIXED, SEED

    assert LGBM_FIXED["min_data_in_leaf"] == 2000 and LGBM_FIXED["lambda_l2"] == 100
    assert LGBM_FIXED["learning_rate"] == 0.02 and LGBM_FIXED["num_threads"] == 8
    assert LGBM_FIXED["feature_fraction"] == 0.7 and LGBM_FIXED["bagging_fraction"] == 0.7
    assert LGBM_FIXED["deterministic"] is True
    assert LGBM_FIXED["num_boost_round"] == 300
    assert SEED == 20261003 and COST_GATE_READING == "gross"


def test_the_search_uses_the_frozen_grid_and_nothing_else() -> None:
    from ml_route_v2.configs import CONFIGS
    from pattern_search.search import frozen_configs

    assert frozen_configs() == tuple(CONFIGS)
