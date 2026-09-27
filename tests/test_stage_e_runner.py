"""The generalized Stage E runner end to end on synthetic data (screening/stage_e_runner.py): the
preflight comes first and its refusal stops the entry, the frozen member and legs, the record
(harness sha, freeze sha, table hashes, series in ticks per contract), the coverage exclusion, the
D9 floor labels, the D5 screen, the power check's named not-run, tiers, write-once records, CLI."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from types import MappingProxyType

import pytest

import screening.stage_e_runner as runner
from data.stage_e_bars import ParquetHashMismatch, research_parquet_path
from screening import harness_freeze, stage_e_freeze
from screening.harness_freeze import HarnessFreezeError
from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import ReleaseCalendar
from strategy.stage_e.interface import LegSpec
from tests._stage_e_synthetic import install_member_package, product_frame, write_parquet

HARNESS = "a" * 64
DAYS = tuple(date(2025, 6, 2) + timedelta(days=i) for i in range(12)
             if (date(2025, 6, 2) + timedelta(days=i)).weekday() < 5)
LEGS = (LegSpec("ZN", True),)
LABEL = "K1-test-01 ZN"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A synthetic repository: one frozen member on ZN, a research store, a release calendar."""
    def build(entry=(9, 10), exit_=(9, 40), early=False, skip=None):
        module = install_member_package(tmp_path, monkeypatch, entry=entry, exit_=exit_,
                                        early=early)
        write_cluster_freeze("K1", [MemberDecl(LABEL, 7, module, "make_member", LEGS)],
                             root=tmp_path)
        research = tmp_path / "research"
        path = research_parquet_path("ZN", research)
        write_parquet(product_frame("ZN", DAYS, 5, start=(9, 0), end=(10, 0), skip=skip), path,
                      {"rolls": []})
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        real_load, real_verify = runner.load_cluster_freeze, runner.verify_cluster_code
        monkeypatch.setattr(runner, "load_cluster_freeze",
                            lambda c: stage_e_freeze.load_cluster_freeze(c, root=tmp_path))
        monkeypatch.setattr(runner, "verify_cluster_code",
                            lambda f: stage_e_freeze.verify_cluster_code(f, root=tmp_path))
        monkeypatch.setattr(runner, "_legs_inputs", lambda legs: {
            leg.root: replace(leg_inputs(leg.root, traded=leg.traded),
                              research_parquet_sha256=sha) for leg in legs})
        monkeypatch.setattr(runner, "load_release_calendar", lambda: ReleaseCalendar(
            MappingProxyType({}), (), date(2019, 5, 1), date(2026, 6, 19), "c" * 64, "test"))
        monkeypatch.setattr(harness_freeze, "preflight", lambda expected: expected)
        del real_load, real_verify
        return {"research_root": research, "step2_root": tmp_path / "no_step2",
                "out_dir": tmp_path / "out"}
    return build


def _screen(paths: dict, **kw):
    return runner.screen_member("K1", LABEL, None, None, "research", harness_sha256=HARNESS,
                                **paths, **kw)


def test_the_entry_refuses_when_preflight_raises_before_reading_anything(world, monkeypatch
                                                                         ) -> None:
    paths = world()
    calls = []

    def refuse(expected: str) -> str:
        raise HarnessFreezeError("Stage E harness preflight refused: planted")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr(runner, "load_cluster_freeze", lambda c: calls.append(c))
    with pytest.raises(HarnessFreezeError, match="planted"):
        _screen(paths)
    assert calls == [] and not paths["out_dir"].exists()


def test_a_member_is_screened_and_its_record_carries_every_frozen_hash(world) -> None:
    paths = world()
    rec = _screen(paths)
    assert rec["status"] == "run" and rec["labels"] == []
    assert rec["harness_sha256"] == HARNESS and len(rec["cluster_freeze_sha256"]) == 64
    assert set(rec["frozen_tables"]) == {"costs", "sizes", "vehicles", "epsilon"}
    assert rec["ordinal"] == 7 and rec["primary_vehicle"] == "ZN"
    series = rec["series"]
    assert series["dates"] == list(DAYS) and series["n_trips"] == len(DAYS)
    assert rec["screen"].n_days == len(DAYS)
    assert rec["power"]["status"] == "not_run" and "StartRuleMissing" in rec["power"]["reason"]
    written = json.loads((paths["out_dir"] / "K1_K1-test-01_ZN_research.json").read_text())
    assert written["harness_sha256"] == HARNESS and written["series"]["values"] == series["values"]
    with pytest.raises(runner.RunnerRefusal, match="written once"):
        _screen(paths)


def test_the_series_is_net_ticks_per_contract_of_the_vehicle(world) -> None:
    paths = world()
    rec = _screen(paths)
    assert rec["engine"]["accounts_started"] == 1
    # ZN: tick value $15.625, one contract per trip: ticks = net USD / 15.625, day by day
    usd = rec["daily_net_usd"]
    assert len(usd) == len(DAYS) and any(usd)
    assert rec["series"]["values"] == pytest.approx([x / 15.625 for x in usd], abs=1e-12)


def test_coverage_below_095_excludes_the_member_before_screening_without_running_it(
        world, monkeypatch) -> None:
    paths = world(skip={9 * 60 + m for m in range(0, 60, 10)})  # 6 of 60 minutes missing
    monkeypatch.setattr(runner, "_run_member", lambda *a, **k: pytest.fail("ran the engine"))
    rec = _screen(paths)
    assert rec["status"] == "excluded_before_screening"
    assert rec["labels"] == ["coverage_below_0.95"] and rec["screen"] is None
    assert rec["coverage"]["ZN"]["ratio"] == pytest.approx(0.9)


def test_the_d9_floor_labels_a_member_it_does_not_drop(world) -> None:
    paths = world(entry=(9, 10), exit_=(9, 15), early=True)  # 1-minute exit tries, 5-min holds
    rec = _screen(paths)
    assert rec["status"] == "run"
    assert set(rec["labels"]) == {"hold_below_2min", "mean_holding_below_10min"}
    assert rec["trade_rate"]["min_hold_refusals"] == len(DAYS)
    assert rec["trade_rate"]["mean_hold_minutes"] == pytest.approx(5.0)
    assert rec["screen"] is not None


def test_legs_other_than_the_frozen_ones_are_refused(world) -> None:
    paths = world()
    with pytest.raises(runner.RunnerRefusal, match="differ from the frozen"):
        runner.screen_member("K1", LABEL, None, (LegSpec("ZB", True),), "research",
                             harness_sha256=HARNESS, **paths)


def test_an_unknown_window_name_is_refused(world) -> None:
    paths = world()
    with pytest.raises(runner.RunnerRefusal, match="window"):
        runner.screen_member("K1", LABEL, None, None, "holdout", harness_sha256=HARNESS, **paths)


def test_the_confirmation_window_needs_a_frozen_start_rule(world) -> None:
    paths = world()
    with pytest.raises(runner.StartRuleMissing, match="S_X"):
        runner.screen_member("K1", LABEL, None, None, "confirmation", harness_sha256=HARNESS,
                             **paths)


def test_the_release_calendar_is_required_and_refused_by_name_when_absent(world,
                                                                          monkeypatch) -> None:
    from screening import stage_e_rules

    paths = world()
    monkeypatch.setattr(runner, "load_release_calendar",
                        lambda: stage_e_rules.load_release_calendar(paths["out_dir"]))
    with pytest.raises(stage_e_rules.ReleaseCalendarMissing, match="event-window"):
        _screen(paths)


def test_screen_cluster_assigns_tiers_from_the_stats_module(world) -> None:
    paths = world()
    out = runner.screen_cluster("K1", "research", harness_sha256=HARNESS, **paths)
    tiers = out["tiers"]
    (m,) = tiers.members
    assert m.member_id == LABEL and m.tier in ("A", "B")
    assert (paths["out_dir"] / "K1_research_cluster.json").is_file()


def test_the_cli_requires_the_harness_hash_and_explicit_roots(capsys) -> None:
    with pytest.raises(SystemExit):
        runner.main(["--cluster", "K1", "--member", LABEL, "--window", "research",
                     "--research-root", "r", "--step2-root", "s", "--out-dir", "o"])
    with pytest.raises(SystemExit):
        runner.main(["--harness-sha256", HARNESS, "--cluster", "K1", "--member", LABEL,
                     "--window", "research", "--step2-root", "s", "--out-dir", "o"])


def test_the_cli_calls_the_preflight_with_its_hash(monkeypatch, tmp_path) -> None:
    seen = []

    def refuse(expected: str) -> str:
        seen.append(expected)
        raise HarnessFreezeError("refused")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    with pytest.raises(HarnessFreezeError):
        runner.main(["--harness-sha256", HARNESS, "--cluster", "K1", "--member", LABEL,
                     "--window", "research", "--research-root", str(tmp_path),
                     "--step2-root", str(tmp_path), "--out-dir", str(tmp_path / "o")])
    assert seen == [HARNESS]


def test_two_traded_legs_use_the_combined_dollar_series_of_the_primary_vehicle() -> None:
    from screening.stage_e_runner import TripRecord, _series

    legs = (LegSpec("ZN", True), LegSpec("ZB", True))
    inputs = {leg.root: leg_inputs(leg.root, traded=True) for leg in legs}
    trips = [TripRecord("ZN", 0, 1, DAYS[0], 3125, 1, "strategy", False),
             TripRecord("ZB", 2, 3, DAYS[0], 6250, 1, "strategy", False)]
    series = _series("m", legs, inputs, trips, DAYS)
    assert series.vehicle == "ZN"
    assert series.values[0] == pytest.approx(93.75 / 15.625) and series.values[1] == 0.0


def test_traded_legs_on_two_calendars_are_refused() -> None:
    with pytest.raises(runner.RunnerRefusal, match="span calendars"):
        runner._legs_inputs((LegSpec("ZN", True), LegSpec("ZC", True)))


# ------------------------------- S_X from the shared loader (lead ruling OC-K) ----
CONF_DAYS = tuple(date(2023, 6, 5) + timedelta(days=i) for i in range(12)
                  if (date(2023, 6, 5) + timedelta(days=i)).weekday() < 5)


def _step2_store(tmp_path: Path) -> Path:
    from data.step2_store import step2_parquet_path

    base = tmp_path / "step2"
    write_parquet(product_frame("ZN", CONF_DAYS, 5, start=(9, 0), end=(10, 0)),
                  step2_parquet_path("ZN", base), {"rolls": []})
    return base


def _step2_sha(base: Path) -> str:
    from data.step2_store import step2_parquet_path

    return hashlib.sha256(step2_parquet_path("ZN", base).read_bytes()).hexdigest()


def _start_files(tmp_path: Path, monkeypatch, step2_sha256: str = "a" * 64,
                 **sets: dict) -> dict[str, str]:
    """Per-set start-rule files under tmp_path/reports (entries that follow from their own
    medians, pinned to ``step2_sha256``); the runner's loader pointed there."""
    from screening import stage_e_start_dates as sd
    from tests.test_stage_e_start_dates import consistent_entry

    shas = {}
    for set_id, products in sets.items():
        doc = {"schema": sd.SCHEMA, "set": set_id, "inputs": [], "harness_sha256": HARNESS,
               "created_pdt": "2026-09-26T15:00:00-07:00",
               "products": {r: consistent_entry(s, root=r, step2_sha256=step2_sha256)
                            for r, s in products.items()}}
        path = tmp_path / "reports" / f"stage_e_start_rule_{set_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc), encoding="utf-8")
        shas[set_id] = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(runner, "_start_dates", lambda roots, allow_empty=False:
                        sd.start_dates_for(roots, root=tmp_path, allow_empty=allow_empty))
    return shas


def test_the_runner_reads_s_x_through_the_shared_loader(monkeypatch) -> None:
    from screening import stage_e_start_dates as sd

    seen = []
    monkeypatch.setattr(sd, "start_dates_for", lambda roots, allow_empty=False: seen.append(
        (roots, allow_empty)) or ({}, {}))
    assert runner._start_dates(["ZN", "MES"]) == ({}, {}) and seen == [(("ZN", "MES"), False)]
    assert not hasattr(runner, "START_RULE_PATH") and not hasattr(runner, "load_start_rule")


def test_the_confirmation_window_starts_at_each_legs_shared_s_x_and_records_its_file(
        world, tmp_path, monkeypatch) -> None:
    paths = world() | {"step2_root": _step2_store(tmp_path)}
    store_sha = _step2_sha(paths["step2_root"])
    shas = _start_files(tmp_path, monkeypatch, store_sha, K2={"ZN": "2023-06-07"},
                        ML={"ZN": "2023-06-07"})
    rec = runner.screen_member("K1", LABEL, None, None, "confirmation", harness_sha256=HARNESS,
                               **paths)
    assert rec["status"] == "run" and rec["screen"] is None and rec["power"] is None
    assert rec["window_dates"]["first"] == date(2023, 6, 7)
    assert rec["window_dates"]["n"] == len([d for d in CONF_DAYS if d >= date(2023, 6, 7)])
    assert rec["s_x"] == {"ZN": "2023-06-07"}
    assert rec["bars"]["ZN"]["sha256"] == store_sha  # the store the start rule read
    assert rec["start_rule"]["ZN"] == {"s_x": "2023-06-07", "step2_sha256": store_sha, "files": [
        {"path": "reports/stage_e_start_rule_K2.json", "sha256": shas["K2"]},
        {"path": "reports/stage_e_start_rule_ML.json", "sha256": shas["ML"]}]}


def test_two_start_rule_files_that_disagree_refuse_the_confirmation_run(world, tmp_path,
                                                                        monkeypatch) -> None:
    paths = world() | {"step2_root": _step2_store(tmp_path)}
    _start_files(tmp_path, monkeypatch, _step2_sha(paths["step2_root"]),
                 K2={"ZN": "2023-06-07"}, ML={"ZN": "2023-06-08"})
    with pytest.raises(runner.StartRuleConflict, match="ZN"):
        runner.screen_member("K1", LABEL, None, None, "confirmation", harness_sha256=HARNESS,
                             **paths)


def test_the_power_check_supply_counts_step2_days_from_the_shared_s_x(world, tmp_path,
                                                                      monkeypatch) -> None:
    from screening import stage_e_stats as st

    paths = world() | {"step2_root": _step2_store(tmp_path)}
    _start_files(tmp_path, monkeypatch, _step2_sha(paths["step2_root"]), K2={"ZN": "2023-06-07"})
    seen = []
    monkeypatch.setattr(st, "power_check", lambda s, c, o, supply: seen.append(supply) or "ok")
    rec = _screen(paths)
    assert seen == [len([d for d in CONF_DAYS if d >= date(2023, 6, 7)])]
    assert rec["power"]["status"] == "run" and rec["power"]["check"] == "ok"
    assert rec["power"]["start_rule"]["ZN"]["s_x"] == "2023-06-07"


def test_an_empty_window_supplies_0_days_and_the_member_is_inconclusive_by_design(
        world, tmp_path, monkeypatch) -> None:
    paths = world()  # no step 2 store: with an empty window it is never read
    _start_files(tmp_path, monkeypatch, K2={"ZN": None})
    rec = _screen(paths)
    power = rec["power"]
    assert power["status"] == "run" and power["supply_days"] == 0
    assert power["check"].label == "inconclusive by design"
    assert power["check"].inconclusive_by_design is True
    assert power["empty_window"] == ["ZN"] and power["start_rule"]["ZN"]["s_x"] is None
    assert "full-size price-path fallback" in power["note"] and "user's decision" in power["note"]


def test_a_doctored_step2_store_is_refused_for_confirmation_and_the_supply_count(
        world, tmp_path, monkeypatch) -> None:
    """Review F-3 (b): the store read must be the one the start rule was computed from."""
    from data.step2_store import step2_parquet_path

    paths = world() | {"step2_root": _step2_store(tmp_path)}
    _start_files(tmp_path, monkeypatch, _step2_sha(paths["step2_root"]), K2={"ZN": "2023-06-07"})
    store = step2_parquet_path("ZN", paths["step2_root"])
    frame = product_frame("ZN", CONF_DAYS, 5, start=(9, 0), end=(10, 0))
    write_parquet(frame.assign(volume=frame["volume"] + 1), store, {"rolls": []})
    with pytest.raises(ParquetHashMismatch, match="not the recorded"):
        runner.screen_member("K1", LABEL, None, None, "confirmation", harness_sha256=HARNESS,
                             **paths)
    rec = _screen(paths)  # research: the supply count is refused by name, recorded
    assert rec["power"]["status"] == "not_run"
    assert rec["power"]["reason"].startswith("ParquetHashMismatch")


def test_a_confirmation_run_on_an_empty_window_is_refused_by_name(world, tmp_path,
                                                                  monkeypatch) -> None:
    paths = world() | {"step2_root": _step2_store(tmp_path)}
    _start_files(tmp_path, monkeypatch, K2={"ZN": None})
    with pytest.raises(runner.StartWindowEmpty, match="ZN.*empty"):
        runner.screen_member("K1", LABEL, None, None, "confirmation", harness_sha256=HARNESS,
                             **paths)


# ------------------------------------ lead ruling on Q10: mean <= 0 is Tier B ----
def test_a_member_that_never_trades_fails_the_screen_and_is_tier_b(world, tmp_path,
                                                                   monkeypatch) -> None:
    paths = world(entry=(20, 0)) | {"step2_root": _step2_store(tmp_path)}  # never enters
    _start_files(tmp_path, monkeypatch, _step2_sha(paths["step2_root"]), K2={"ZN": "2023-06-07"})
    out = runner.screen_cluster("K1", "research", harness_sha256=HARNESS, **paths)
    (m,) = out["tiers"].members
    assert m.tier == "B" and m.screen.passes is False and m.screen.t_daily is None
    assert m.screen.mean_ticks == 0.0 and m.screen.sd_pop_ticks == 0.0
    assert out["not_tiered"] == {} and out["power_check_undefined"] == [LABEL]
    rec = json.loads((paths["out_dir"] / "K1_K1-test-01_ZN_research.json").read_text())
    assert rec["power"]["status"] == "power check undefined" and rec["power"]["supply_days"] == 8
    assert rec["screen"]["passes"] is False and rec["screen"]["t_daily"] is None


def test_mean_at_or_below_zero_fails_even_where_the_stats_module_cannot_compute_t(
        monkeypatch) -> None:
    from screening import stage_e_stats as st

    def no_s_x(legs, root):  # noqa: ANN001, ANN202
        raise runner.StartRuleMissing("no frozen S_X for ['ZN']")

    monkeypatch.setattr(runner, "confirmation_supply_days", no_s_x)
    one_day = st.DailySeries("m", "ZN", (DAYS[0],), (-3.0,), 1)  # n < 2: ScreenUndefined
    got = runner._research_statistics("K1", 1, LEGS, one_day, Path("unused"))
    assert isinstance(got["screen"], st.ScreenResult)
    assert got["screen"].passes is False and got["screen"].t_daily is None
    assert got["power"]["status"] == "not_run"
    flat_positive = st.DailySeries("m", "ZN", DAYS[:2], (2.0, 2.0), 2)  # sd 0, mean > 0
    assert runner._research_statistics("K1", 1, LEGS, flat_positive, Path("unused"))[
        "screen"]["status"] == "screen_undefined"
    non_finite = st.DailySeries("m", "ZN", DAYS[:2], (float("-inf"), 0.0), 1)
    assert runner._research_statistics("K1", 1, LEGS, non_finite, Path("unused"))[
        "screen"]["status"] == "screen_undefined"


def test_oct_a_frozen_input_error_during_a_run_is_a_named_member_refusal(world,
                                                                       monkeypatch) -> None:
    """Lead ruling OC-T (C-2): a CostLookupError raised by the engine refuses the member by name;
    screen_cluster continues and lists the refusal first in its summary."""
    from screening.stage_e_frozen import CostLookupError

    paths = world()

    def boom(*args: object, **kwargs: object) -> None:
        raise CostLookupError("ZN: no calibrated bucket at CT 16:00")

    monkeypatch.setattr(runner, "_run_member", boom)
    out = runner.screen_cluster("K1", "research", harness_sha256=HARNESS, **paths)
    assert list(out)[:3] == ["cluster", "window", "refused_members"]
    assert out["refused_members"] == {LABEL: "CostLookupError: ZN: no calibrated bucket at CT "
                                             "16:00"}
    rec = json.loads((paths["out_dir"] / "K1_K1-test-01_ZN_research.json").read_text())
    assert rec["status"] == "refused_case" and rec["screen"] is None
    assert out["tiers"] is None  # nothing to tier; the run still completes


def test_oct_the_record_counts_closure_bars_per_leg(world) -> None:
    rec = _screen(world())
    assert rec["bars"]["ZN"]["closure_bars"] == 0
    assert rec["engine"]["closure_bars_seen"] == {"ZN": 0}
    assert rec["engine"]["closure_gap_fills"] == 0
