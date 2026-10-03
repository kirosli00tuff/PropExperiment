"""Stage E.11: the runtime probe's CLI and pieces (ml_route_v2/probe.py;
docs/STAGE_E_ML_V2_DESIGN.md V2.11). Argument parsing, the AiTrader-window wait, the
extrapolation arithmetic and one tiny run of the engine-and-payouts step on a small synthetic
world (the size A and B runs themselves are the probe's job, not a test's). Synthetic data only.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from ml_route_v2 import probe
from ml_route_v2.constants import UNIVERSE
from ml_route_v2.engine_stage import prepare_engine
from ml_route_v2.pipeline import ENGINE_DIR, _filter, build_world_panel
from tests.ml_v2_fixtures import world


def test_products_are_28_or_the_8_standin() -> None:
    assert probe.products_of(28) == tuple(UNIVERSE)
    assert probe.products_of(8) == probe.PHASE1_STANDIN
    with pytest.raises(SystemExit):
        probe.products_of(5)


def test_parse_args_reads_the_cli(tmp_path: Path) -> None:
    args = probe.parse_args(["--products", "8", "--state-dir", str(tmp_path), "--full",
                             "--payout-paths", "100", "--no-isolate-paths"])
    assert (args.products, args.state_dir, args.full, args.force_full) == (8, tmp_path, True,
                                                                          False)
    assert args.payout_paths == 100 and args.isolate_paths is False
    default = probe.parse_args(["--products", "28", "--state-dir", str(tmp_path)])
    assert default.isolate_paths is None and default.payout_paths is None


@pytest.mark.parametrize("argv", [
    ["--products", "5", "--state-dir", "x"],
    ["--products", "8"],
    ["--products", "8", "--state-dir", "x", "--payout-paths", "0"],
])
def test_parse_args_rejects_bad_input(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        probe.parse_args(argv)


def test_wait_outside_collector_window(monkeypatch: pytest.MonkeyPatch) -> None:
    times = iter([datetime(2026, 10, 2, 15, 45, tzinfo=probe.PT),
                  datetime(2026, 10, 2, 16, 0, 5, tzinfo=probe.PT)])

    class _Clock:
        @staticmethod
        def now(_tz):  # noqa: ANN001, ANN205 - test double of datetime.now
            return next(times)

    monkeypatch.setattr(probe, "datetime", _Clock)
    slept: list[float] = []
    waited = probe.wait_outside_collector_window(slept.append)
    assert slept == [15 * 60 + 5] and waited == slept[0]


def test_extrapolate_adds_the_pieces() -> None:
    log = {"stages": {s: {"wall_s": 1.0} for s in ("world", "panel", "filter", "gate0")},
           "one_split": {"wall_s": 10.0},
           "pieces": {"final_refit_lgbm_d3_all_rows": {"wall_s": 2.0},
                      "pbo_dsr": {"wall_s": 0.5}},
           "engine_payouts": {"simulate_one_path": {"wall_s": 100.0},
                              "payouts_one_path": {"wall_s": 20.0}}}
    est = probe.extrapolate(log)
    assert est["cpcv_s"] == probe.N_OUTER_SPLITS * 10.0
    assert est["schedule_s"] == probe.N_OUTER_SPLITS * 2.0
    assert est["simulate_s"] == probe.N_PATHS * 100.0 and est["payouts_s"] == probe.N_PATHS * 20.0
    assert est["total_s"] == pytest.approx(4.0 + 150.0 + 2.0 + 0.5 + 30.0 + 500.0 + 100.0)


def test_one_tiny_engine_and_payouts_run(tmp_path: Path,
                                        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe, "wait_outside_collector_window", lambda: 0.0)  # never block
    w = world(("MGC", "6E"), date(2021, 3, 1), date(2021, 6, 30), seed=20261005,
              plant={"kind": "sign", "edge_cost_multiple": 10.0})
    panel = build_world_panel(w)
    filt = _filter(panel)
    sched = probe.standin_schedule(panel, filt["admissible"])
    engine = prepare_engine(w, {0: sched}, (0,), tmp_path / ENGINE_DIR)
    out = probe.time_engine_and_payouts(engine, sched, filt["risk"], 20, tmp_path, False)
    sim, pay = out["simulate_one_path"], out["payouts_one_path"]
    assert sim["n_trips"] > 0 and sim["n_schedule"] == len(sched) and sim["wall_s"] >= 0
    assert sim["peak_rss_mb"] > 0 and pay["n_paths"] == 20 and pay["n_calls"] == 8
    assert (tmp_path / probe.PROBE_ENGINE_DIR / "path_0.pkl").exists()
    assert (tmp_path / probe.PROBE_PAYOUT_DIR / "path_0.pkl").exists()
