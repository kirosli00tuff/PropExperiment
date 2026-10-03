"""Stage E.11 Task 5: ML route v2 end to end on a small synthetic world (ml_route_v2/pipeline.py,
docs/STAGE_E_ML_V2_DESIGN.md V2.2b, V2.9, V2.11).

Four products, about 320 training dates (plus warm-up history), a reduced configuration list.
Checks: determinism (two runs: identical model sha256s, CPCV records, engine daily P&L and payout
figures), resumability (a run stopped after Gate 0 and restarted recomputes no finished stage),
the trial count (ledger N = N_program + configurations + Gate 0 tests), Gate 0's stop (V2.2b) and
the synthetic world's own contract (planted edge size, determinism). Plus the regression test of
bug G0-1 (gate0_family_a with admissible= on a built panel; fixed).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from ml_route_v2 import engine_stage, pipeline
from ml_route_v2.configs import CONFIGS, ConfigLedger
from ml_route_v2.constants import N_PROGRAM_AT_FREEZE, UNIVERSE
from ml_route_v2.cost_filter import c_sigma_table
from ml_route_v2.gate0 import gate0_family_a
from ml_route_v2.pipeline import (
    STAGES,
    admissible_ok_panel,
    assert_bars_on_session_grid,
    build_world_panel,
    run_pipeline,
    stage_table,
)
from ml_route_v2.synthetic import engine_frame, nominal_cost_ticks, synthetic_universe
from tests.ml_v2_fixtures import world

SEED = 20261003
VEHICLES = ("MNQ", "MGC", "MCL", "6E")
FIRST, LAST = date(2021, 1, 4), date(2022, 3, 31)
EDGE_C = 10.0
CONFIG_IDS = ("ridge_l0.1_k1.5_h60", "ridge_l0.1_k2_h60", "ridge_l1_k1.5_h60")
PAYOUT_PATHS = 200


def e2e_world():
    return world(VEHICLES, FIRST, LAST, seed=SEED + 10,
                 plant={"kind": "sign", "edge_cost_multiple": EDGE_C})


def e2e_configs():
    return tuple(c for c in CONFIGS if c.config_id in CONFIG_IDS)


def _run(state_dir, **kw):
    """Inline engine paths (the pipeline's default is one process per path, design fix 9)."""
    return run_pipeline(e2e_world(), state_dir=state_dir, configs=e2e_configs(), paths=(0,),
                        payout_paths=PAYOUT_PATHS, isolate_paths=False, **kw)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Run A end to end; run B stopped after Gate 0, then restarted with the finished stages'
    builders replaced by functions that fail, so a recomputation would raise."""
    a = _run(tmp_path_factory.mktemp("run_a"))
    dir_b = tmp_path_factory.mktemp("run_b")
    b_stop = _run(dir_b, stop_after="gate0")
    mp = pytest.MonkeyPatch()

    def boom(*_a, **_k):
        raise AssertionError("a finished stage was recomputed")

    for name in ("build_world_panel", "_filter", "_gate0"):
        mp.setattr(pipeline, name, boom)
    try:
        b = _run(dir_b)
    finally:
        mp.undo()
    return a, b_stop, b


def test_run_completes_with_timing_records(runs) -> None:
    a, _stop, _b = runs
    assert a.stopped_at is None
    table = stage_table(a)
    assert tuple(table["name"]) == STAGES
    assert (table["status"] == "computed").all()
    assert (table["wall_s"] >= 0).all() and (table["disk_mb"] > 0).all()
    assert table["peak_rss_mb"].notna().all()
    assert a.results["gate0"]["verdict"].passed
    assert a.results["stats"]["median_path_t"] >= 3.0
    assert a.results["simulate"][0]["n_trips"] > 100


def test_determinism_two_runs_identical_models_and_daily_pnl(runs) -> None:
    a, _stop, b = runs
    assert a.results["final"]["sha256"] == b.results["final"]["sha256"]
    assert a.results["final"]["config"] == b.results["final"]["config"]
    assert a.results["cpcv"].selected_sha256 == b.results["cpcv"].selected_sha256
    pd.testing.assert_frame_equal(a.results["cpcv"].path_daily, b.results["cpcv"].path_daily)
    pd.testing.assert_series_equal(a.results["simulate"][0]["daily"],
                                   b.results["simulate"][0]["daily"])
    pd.testing.assert_frame_equal(a.results["payouts"], b.results["payouts"])


def test_resume_after_gate0_recomputes_no_finished_stage(runs) -> None:
    _a, stop, b = runs
    assert stop.stopped_at == "after:gate0"
    assert [s.name for s in stop.stages] == ["panel", "filter", "gate0"]
    status = {s.name: s.status for s in b.stages}
    assert status == {**dict.fromkeys(("panel", "filter", "gate0"), "loaded"),
                      **dict.fromkeys(STAGES[3:], "computed")}


def test_engine_stages_checkpoint_per_path_and_free_the_panel(runs) -> None:
    a, stop, _b = runs
    assert (a.state_dir / pipeline.ENGINE_DIR / "path_0.pkl").exists()
    assert (a.state_dir / pipeline.PAYOUT_DIR / "path_0.pkl").exists()
    assert "panel" not in a.results  # freed before the engine (V2.11 memory, FIX 3)
    assert "panel" in stop.results


def test_restart_inside_the_engine_stages_reuses_the_path_checkpoints(
        runs, monkeypatch: pytest.MonkeyPatch) -> None:
    """A run killed after its paths finished but before the stage file was written: the restart
    loads every path's checkpoint and recomputes no engine run and no payout draw."""
    a, _stop, b = runs
    for name in ("simulate", "payouts"):
        (b.state_dir / "stages" / f"{name}.pkl").unlink()

    def boom(*_a, **_k):
        raise AssertionError("a checkpointed path was recomputed")

    monkeypatch.setattr(engine_stage, "run_engine_path", boom)
    monkeypatch.setattr(engine_stage, "_payout_rows", boom)
    c = _run(b.state_dir)
    assert c.status("simulate") == "computed" and c.status("payouts") == "computed"
    pd.testing.assert_series_equal(c.results["simulate"][0]["daily"],
                                   a.results["simulate"][0]["daily"])
    pd.testing.assert_frame_equal(c.results["payouts"], a.results["payouts"])


def test_ledger_n_is_program_plus_configs_plus_gate0_tests(runs) -> None:
    a, _stop, _b = runs
    g0 = a.results["gate0"]
    n_gate0 = g0["n_a"] + g0["n_b"]
    assert n_gate0 == g0["verdict"].n_tests
    ledger = ConfigLedger(a.state_dir / pipeline.LEDGER_FILE)
    assert ledger.n_registered("config") == len(e2e_configs())
    assert ledger.n_registered("gate0_A") + ledger.n_registered("gate0_B") == n_gate0
    expected = N_PROGRAM_AT_FREEZE + len(e2e_configs()) + n_gate0
    assert ledger.n_total() == expected == a.results["stats"]["n_total"]


def test_schedule_is_the_nested_oos_record(runs) -> None:
    a, _stop, _b = runs
    nested, sched = a.results["cpcv"], a.results["schedule"]
    block = {d: b for b, days in enumerate(nested.blocks) for d in days}
    path0 = sched["paths"][0]
    assert len(path0)
    for day in pd.to_datetime(path0["trade_date"]).dt.date.unique()[:50]:
        assert nested.selected[nested.paths[0][block[day]]] is not None


def test_gate0_failure_stops_the_pipeline_and_force_continues(tmp_path) -> None:
    noise = world(("MNQ", "MGC", "MCL"), date(2021, 1, 4), date(2022, 2, 28), seed=SEED + 1,
                  sigma_cost_multiple=20.0)
    rep = run_pipeline(noise, state_dir=tmp_path, configs=e2e_configs()[:1], timing=False)
    assert rep.stopped_at == "gate0"
    assert [s.name for s in rep.stages] == ["panel", "filter", "gate0"]
    forced = run_pipeline(noise, state_dir=tmp_path, configs=e2e_configs()[:1], timing=False,
                          force_after_gate0_fail=True, stop_after="cpcv")
    assert forced.stopped_at == "after:cpcv"
    assert forced.status("gate0") == "loaded" and forced.status("cpcv") == "computed"


# ------------------------------------------------------------------ the synthetic world ----
def test_world_is_deterministic_and_on_the_session_grid() -> None:
    a = synthetic_universe(("MGC",), date(2021, 3, 1), date(2021, 3, 12), seed=3,
                           warmup_dates=3)
    b = synthetic_universe(("MGC",), date(2021, 3, 1), date(2021, 3, 12), seed=3,
                           warmup_dates=3)
    assert sorted(a.bars) == sorted(b.bars)
    for r in a.bars:
        pd.testing.assert_frame_equal(a.bars[r], b.bars[r])
    pd.testing.assert_frame_equal(a.frames["MGC"], b.frames["MGC"])
    assert_bars_on_session_grid(a.bars)
    assert {"NQ", "ZN", "6E", "CL", "GC", "ZC", "MBT", "MES", "HG"} <= set(a.bars)
    assert a.calendar[0] >= date(2021, 3, 1) and a.bars_first < date(2021, 3, 1)


def test_engine_frame_cut_to_dates_matches_the_eager_frame() -> None:
    w = synthetic_universe(("MGC",), date(2021, 3, 1), date(2021, 3, 12), seed=3,
                           warmup_dates=3)
    keep = {d.isoformat() for d in w.calendar}
    eager = w.frames["MGC"]
    eager = eager.loc[eager["trade_date"].isin(keep)].reset_index(drop=True)
    lazy = engine_frame("MGC", w.bars[UNIVERSE["MGC"][1]], keep)
    pd.testing.assert_frame_equal(eager, lazy)


def test_planted_sign_edge_has_its_stated_size() -> None:
    w = e2e_world()
    panel = build_world_panel(w)
    f = panel.frame.loc[panel.frame["ok_h60"]]
    for v in VEHICLES:
        s = f.loc[f["root"] == v]
        g = np.sign(s["z_g02_ret60"].to_numpy()) * s["y_gross_h60"].to_numpy()
        edge = EDGE_C * nominal_cost_ticks(v)
        se = g.std(ddof=1) / np.sqrt(len(g))
        assert abs(g.mean() - edge) < 4 * se + 0.15 * edge, (v, g.mean(), edge, se)
    table = c_sigma_table(panel)
    assert table["admissible"].all()


def test_gate0_family_a_accepts_admissible_pairs_on_a_built_panel(tmp_path) -> None:
    panel = build_world_panel(e2e_world())
    adm = (("MNQ", "h60"), ("MGC", "h60"))
    got = gate0_family_a(panel, ledger=ConfigLedger(tmp_path / "a.jsonl"), admissible=adm)
    via_ok = gate0_family_a(admissible_ok_panel(panel, adm),
                            ledger=ConfigLedger(tmp_path / "b.jsonl"))
    assert [t.test_id for t in got] == [t.test_id for t in via_ok]
    assert [t.n_obs for t in got] == [t.n_obs for t in via_ok]
    # NaN-aware: a signal never applicable on the admissible rows has t = NaN in both
    np.testing.assert_array_equal([t.t for t in got], [t.t for t in via_ok])


# ---- design review D-08b, D-21, D-01 in the pipeline report --------------------------------------
def test_cost_sensitivity_reprices_the_nested_record(runs) -> None:
    """The schedule stage re-scores the nested OOS predictions with each split's own risk table
    (D-04): at 1.0 x slippage it reproduces the CPCV record (checked inside the stage), and at
    1.5 x the same trades earn less (D-08b)."""
    a, _stop, _b = runs
    sched, stats = a.results["schedule"], a.results["stats"]
    assert sched["cost_check_max_abs_diff"] <= pipeline.COST_CHECK_TOL_USD
    pd.testing.assert_frame_equal(sched["path_daily_by_multiple"][1.0],
                                  a.results["cpcv"].path_daily, check_exact=False, atol=1e-6)
    one, more = sched["cost_sensitivity"][1.0], sched["cost_sensitivity"][1.5]
    assert one["median_path_t"] == pytest.approx(stats["median_path_t"], abs=1e-9)
    assert one["sharpe_annual"] == pytest.approx(stats["sharpe_annual"], abs=1e-9)
    assert more["daily_mean"] < one["daily_mean"]
    assert more["median_path_t"] < one["median_path_t"]
    assert more["sharpe_daily"] < one["sharpe_daily"]


def test_final_configuration_reports_its_own_cpcv_oos_figures(runs) -> None:
    a, _stop, _b = runs
    final, nested = a.results["final"], a.results["cpcv"]
    col = nested.config_daily[final["config"].config_id].to_numpy()
    sd = col.std(ddof=1)
    assert final["own_oos_t"] == pytest.approx(col.mean() / (sd / np.sqrt(col.size)), abs=1e-9)
    assert final["own_oos_sharpe_daily"] == pytest.approx(col.mean() / sd, abs=1e-12)
    assert final["own_oos_sharpe_annual"] == pytest.approx(col.mean() / sd * np.sqrt(252),
                                                           abs=1e-9)
    assert final["nested_median_path_t"] == a.results["stats"]["median_path_t"]


def test_payout_rows_carry_the_d01_ruin_beside_the_plain_breach(runs) -> None:
    a, _stop, _b = runs
    pay = a.results["payouts"]
    verdict = pay[pay["verdict_reading"]]
    assert len(verdict) == 8 and len(pay) == 16  # 2 accounts x 2 path types x DLL off/on
    assert (~verdict["ks"]).all() and verdict["ks2_sizing"].all()  # KS1/3/4 off, KS2 on
    assert (pay["ruin_prob"] >= pay["breach_only_prob"]).all()


def test_schedule_rows_carry_their_own_splits_risk_table(runs) -> None:
    """Code review C-04 (completing D-04): every row of a path's schedule carries sigma_ticks and
    loss_ticks of the table on its own outer split's training rows (pipeline.split_risk_fn), not
    the all-blocks table of stage 2, and the engine's trade records carry the same values."""
    from ml_route_v2.cpcv import horizon_data, split_masks

    a, stop, _b = runs
    nested, sched, filt = a.results["cpcv"], a.results["schedule"], a.results["filter"]
    panel = stop.results["panel"]  # the same world, stopped after Gate 0
    path0 = sched["paths"][0]
    assert {"sigma_ticks", "loss_ticks"} <= set(path0.columns) and len(path0)
    block = {d: b for b, days in enumerate(nested.blocks) for d in days}
    split_of = [nested.paths[0][block[d]] for d in pd.to_datetime(path0["trade_date"]).dt.date]
    by_index = {s.index: s for s in nested.splits}
    risk_fn = pipeline.split_risk_fn(panel)
    differs = 0
    for s, part in path0.groupby(np.asarray(split_of)):
        h = str(part["horizon"].iloc[0])
        data = horizon_data(panel, h, a.results["filter"]["admissible"] or None)
        train, _test = split_masks(by_index[s], data.days, data.t_ns, data.x_ns)
        table = risk_fn(data.rows.iloc[np.flatnonzero(train)])
        keys = part[["root", "horizon"]]
        own = keys.merge(table, on=["root", "horizon"], how="left", validate="many_to_one")
        whole = keys.merge(filt["risk"], on=["root", "horizon"], how="left")
        for col in ("sigma_ticks", "loss_ticks"):
            np.testing.assert_array_equal(part[col].to_numpy(), own[col].to_numpy())
        differs += int((whole["sigma_ticks"].to_numpy() != part["sigma_ticks"].to_numpy()).sum())
    assert differs > 0  # the split tables are not the all-blocks table
    trades = [t for d in a.results["simulate"][0]["days"] for t in d.trades]
    allowed = set(zip(path0["root"], path0["horizon"], path0["sigma_ticks"],
                      path0["loss_ticks"], strict=True))
    assert trades and all((t.root, t.horizon, t.sigma_ticks, t.loss_ticks) in allowed
                          for t in trades)
