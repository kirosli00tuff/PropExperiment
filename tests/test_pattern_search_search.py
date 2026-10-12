"""The search and the SCREEN (reports/stage_e20_plan.md sections 8 and 9) on synthetic panels:
the empty-admissible refusal, each screen item's rule, the DSR at N = 528, and the trade-level
reported items reproducing the frozen record (pipeline._nested_schedule, config_daily)."""

from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from pattern_search import constants as K
from pattern_search import search as S
from tests._pattern_search_synth import configs_named, panel_small, world_small

SMALL_CONFIGS = ("ridge_l0.1_k1.5_h60", "ridge_l1_k1.5_hF", "ridge_l1_k3_h60")


@pytest.fixture(scope="module")
def small_run(tmp_path_factory):  # noqa: ANN201
    panel = panel_small()
    filt = S.admissibility(panel)
    cfgs = configs_named(*SMALL_CONFIGS)
    state = tmp_path_factory.mktemp("search_state")
    nested = S.run_nested(panel, filt, world_small().calendar, state, cfgs)
    final = S.run_final(panel, filt, world_small().calendar, state, cfgs)
    return panel, filt, cfgs, nested, final, state


# ------------------------------------------------------------------ admissibility ----
def test_an_empty_admissible_set_is_refused_not_turned_into_no_filter() -> None:
    panel = panel_small()
    frame = panel.frame.copy()
    for h in ("h60", "h120", "hF"):
        for side in ("long", "short"):
            frame[f"cost_{side}_{h}"] = frame[f"cost_{side}_{h}"] * 1e4
    with pytest.raises(S.EmptyAdmissible, match="no model"):
        S.admissibility(dataclasses.replace(panel, frame=frame))
    with pytest.raises(S.EmptyAdmissible):
        S.run_nested(panel, {"admissible": (), "risk": None}, world_small().calendar, "/nowhere",
                     configs_named(SMALL_CONFIGS[0]))


def test_the_filter_is_the_frozen_one_pass_c_sigma_filter() -> None:
    from ml_route_v2.cost_filter import c_sigma_table

    panel = panel_small()
    filt = S.admissibility(panel)
    table = c_sigma_table(panel)
    want = {(r, h) for r, h, a in table[["root", "horizon", "admissible"]].itertuples(index=False)
            if a}
    assert set(filt["admissible"]) == want and want


# ------------------------------------------------------------------ the screen ----
def _stub(mean: float, sd: float, *, n: int = 1200, configs: int = 3, seed: int = 0):  # noqa: ANN202
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, n)
    base = (base - base.mean()) / base.std(ddof=1) * sd + mean
    idx = pd.Index(pd.bdate_range("2019-05-06", periods=n).date, name="trade_date")
    path_daily = pd.DataFrame({j: base for j in range(5)}, index=idx)
    config_daily = pd.DataFrame({f"c{i}": base - i * 5.0 + rng.normal(0, 0.01, n)
                                 for i in range(configs)}, index=idx)
    nested = SimpleNamespace(path_daily=path_daily, config_daily=config_daily,
                             selected=["c0"] * 15,
                             config_sharpes=pd.Series({c: 0.1 for c in config_daily}))
    final = SimpleNamespace(config=SimpleNamespace(config_id="c0"))
    return nested, final


def test_the_screen_passes_when_every_item_holds() -> None:
    nested, final = _stub(2.0, 20.0)  # t = 2/(20/sqrt 1200) = 3.46; Sharpe = 0.1 x sqrt 252
    sc = S.screen(nested, final)
    assert sc["verdict"] == K.PASS
    assert sc["items"]["1_median_path_t"]["value"] == pytest.approx(2 / (20 / np.sqrt(1200)))
    assert sc["items"]["3_sharpe_annual"]["value"] == pytest.approx(0.1 * np.sqrt(252))
    assert sc["items"]["2_pbo"]["value"] < 0.5


def test_a_median_path_t_below_2_fails_item_1() -> None:
    nested, final = _stub(1.0, 20.0)  # t = 1.73
    sc = S.screen(nested, final)
    assert sc["verdict"] == K.FAIL and not sc["items"]["1_median_path_t"]["passes"]


def test_a_sharpe_above_4_fails_item_3_and_raises_the_leakage_alarm() -> None:
    nested, final = _stub(10.0, 20.0)  # Sharpe 0.5 x sqrt 252 = 7.9
    sc = S.screen(nested, final)
    assert sc["verdict"] == K.FAIL and sc["leakage_alarm"]
    assert not sc["items"]["3_sharpe_annual"]["passes"]
    assert sc["items"]["1_median_path_t"]["passes"]


def test_a_sharpe_below_0_5_fails_item_3() -> None:
    nested2, final = _stub(0.5, 20.0, n=40000)  # t = 3.5, Sharpe 0.025 x 15.9 = 0.40
    sc = S.screen(nested2, final)
    assert not sc["items"]["3_sharpe_annual"]["passes"] and sc["verdict"] == K.FAIL


def test_pbo_counts_as_failed_when_it_raises_is_degenerate_or_nan(monkeypatch) -> None:
    nested, final = _stub(2.0, 20.0)
    bad = nested.config_daily.copy()
    bad.iloc[0, 0] = np.nan
    assert S.pbo_record(bad)["passes"] is False
    import ml_route_v2.cpcv as cpcv

    monkeypatch.setattr(cpcv, "pbo_cscv", lambda perf: {"pbo": 0.1, "degenerate": True})
    assert S.screen(nested, final)["verdict"] == K.FAIL
    monkeypatch.setattr(cpcv, "pbo_cscv", lambda perf: {"pbo": float("nan"), "degenerate": False})
    assert S.screen(nested, final)["verdict"] == K.FAIL
    monkeypatch.setattr(cpcv, "pbo_cscv", lambda perf: {"pbo": 0.6, "degenerate": False})
    assert S.screen(nested, final)["verdict"] == K.FAIL


def test_no_final_configuration_fails_the_screen() -> None:
    nested, _final = _stub(2.0, 20.0)
    sc = S.screen(nested, SimpleNamespace(config=None))
    assert sc["verdict"] == K.FAIL and not sc["items"]["final_selection"]["passes"]


def test_the_dsr_uses_n_528_passed_explicitly() -> None:
    from ml_route_v2.cpcv import dsr_at_n, sharpe_variance

    nested, _ = _stub(2.0, 20.0)
    nested.config_sharpes = pd.Series({"a": 0.05, "b": 0.1, "c": 0.12})
    rec = S.dsr_record(nested)
    want = dsr_at_n(nested.path_daily.mean(axis=1).to_numpy(), 528,
                    sharpe_variance([0.05, 0.1, 0.12]))
    assert rec["n_trials"] == 528 == K.N_TOTAL_AT_SCREEN == K.N_TRIALS_BEFORE + 45
    assert rec["status"] == "computed"
    assert rec["deflated_sharpe_ratio"] == pytest.approx(want["deflated_sharpe_ratio"])


# ------------------------------------------------------------------ a small real run ----
def test_the_nested_run_registers_the_configs_and_screens(small_run) -> None:
    from ml_route_v2.configs import ConfigLedger

    panel, filt, cfgs, nested, final, state = small_run
    led = ConfigLedger(state / S.LEDGER_FILE)
    assert led.n_registered("config") == len(cfgs)
    assert len(nested.splits) == 15 and len(nested.paths) == 5
    sc = S.screen(nested, final)
    assert sc["verdict"] in (K.PASS, K.FAIL) and sc["n_dates"] == len(world_small().calendar)
    table = S.config_table(nested, final)
    assert list(table["config_id"]) == list(SMALL_CONFIGS)
    assert table["registry_id"].tolist() == [
        {v: k for k, v in K.config_ids().items()}[c] for c in SMALL_CONFIGS]


def test_the_oos_record_reproduces_the_frozen_schedule_and_config_daily(small_run) -> None:
    from ml_route_v2.pipeline import _nested_schedule, split_risk_fn
    from pattern_search.oos import Refits, final_record, nested_record

    panel, filt, cfgs, nested, final, _state = small_run
    refits = Refits(panel, nested, filt["admissible"], split_risk_fn(panel))
    rec = nested_record(refits, {c.config_id: c for c in cfgs})
    frozen = _nested_schedule(panel, nested, cfgs, filt["admissible"],
                              risk_fn=split_risk_fn(panel))
    for m in ("1.0", "1.5"):
        assert rec["cost_sensitivity"][m]["median_path_t"] == pytest.approx(
            frozen["cost_sensitivity"][float(m)]["median_path_t"])
    np.testing.assert_allclose(rec["path_daily_1_5x"].to_numpy(),
                               frozen["path_daily_by_multiple"][1.5].to_numpy(), atol=1e-9)
    assert rec["trades_total"] == int(rec["trips"]["all_paths_total"].sum())
    fin = final_record(refits, final.config)
    if final.config is not None:
        assert fin["config_id"] == final.config.config_id
        assert fin["pnl_total_15_splits_usd"] == pytest.approx(
            5.0 * nested.config_daily[final.config.config_id].sum(), abs=1e-6)
        if fin["pnl_total_15_splits_usd"]:
            assert fin["t4_share"] == pytest.approx(
                fin["pnl_t4_15_splits_usd"] / fin["pnl_total_15_splits_usd"])


def test_the_round_trip_table_flags_products_below_30_under_each_reading() -> None:
    from pattern_search.oos import round_trip_table

    per = pd.DataFrame({0: [40, 10], 1: [35, 50], 2: [29, 60], 3: [31, 5], 4: [33, 2]},
                       index=pd.Index(["MNQ", "ZC"], name="root"))
    t = round_trip_table(per)
    assert t.loc["MNQ", "all_paths_total"] == 168 and t.loc["MNQ", "path_min"] == 29
    assert bool(t.loc["MNQ", "below_30_path_min"]) and not bool(t.loc["MNQ",
                                                                      "below_30_path_median"])
    assert bool(t.loc["ZC", "below_30_path_median"]) and not bool(t.loc["ZC",
                                                                       "below_30_all_paths_total"])
