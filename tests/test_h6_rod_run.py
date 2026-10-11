"""h6_rod.run end to end on synthetic bars: the lead's settings, the freeze manifest, the
registration (a temporary registry in the test mode, never ledger/trial_registrations.jsonl) and
the run-once marker. No store and no GEX file of the repository is opened: the store, the GEX CSV
and every output are temporary files, and the loader is injected."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from h6_rod import clock, run
from h6_rod import constants as K
from h6_rod import preflight as pf
from tests._h6_rod_synth import make_run_setup

HARNESS = K.HARNESS_SHA256


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _real_registry_sha() -> str:
    from screening.trial_registry import REGISTRY_PATH

    return _sha(REGISTRY_PATH)


@pytest.fixture
def setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    return make_run_setup(tmp_path, monkeypatch.setattr)


# ------------------------------------------------------------------ the lead's settings ----
def test_every_entry_point_refuses_while_t3_registered_is_none(monkeypatch) -> None:
    monkeypatch.setattr(K, "T3_REGISTERED", None)
    with pytest.raises(pf.Refused, match="T3_REGISTERED"):
        pf.lead_settings()
    with pytest.raises(ValueError):
        K.registered_tests()


def test_entry_points_refuse_while_the_engine_lead_in_is_undecided(monkeypatch) -> None:
    monkeypatch.setattr(K, "T3_REGISTERED", False)
    monkeypatch.setattr(K, "ENGINE_LEAD_IN_DATES", None)
    with pytest.raises(pf.Refused, match="ENGINE_LEAD_IN_DATES"):
        pf.lead_settings()


def test_ruled_names_accepted_hyphenated_label_refused_s1(monkeypatch) -> None:
    # lead ruling S1 (prereg section 8): label E20H6, ids E20H6-T1..T3; no hyphen in a label
    assert K.REGISTRY_LABEL == "E20H6"
    assert dict(K.TEST_IDS) == {"T1": "E20H6-T1", "T2": "E20H6-T2", "T3": "E20H6-T3"}
    pf.registry_names_valid()
    monkeypatch.setattr(K, "REGISTRY_LABEL", "E20-H6")
    monkeypatch.setattr(K, "TEST_IDS", {"T1": "E20-H6-T1", "T2": "E20-H6-T2", "T3": "E20-H6-T3"})
    with pytest.raises(pf.Refused, match="trial_registry refuses"):
        pf.registry_names_valid()


def test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha() -> None:
    from data.config import REPO_ROOT

    assert K.T3_REGISTERED is True and K.ENGINE_LEAD_IN_DATES == 1
    assert K.GEX_CSV_SHA256 == "51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62"
    proc = subprocess.run([sys.executable, "-m", "h6_rod", "check", "--freeze-sha256", "0" * 64,
                           "--harness-sha256", HARNESS], cwd=REPO_ROOT, capture_output=True,
                          text=True, timeout=120, check=False)
    assert proc.returncode == K.RC_REFUSED and "REFUSED" in proc.stderr
    assert "T3_REGISTERED" not in proc.stderr
    assert "freeze manifest" in proc.stderr  # review H6R-10: refused at the freeze check


# ------------------------------------------------------------------ check ----
def test_check_passes_and_reads_no_bar(setup) -> None:
    rec = run.check(setup["freeze_sha"], HARNESS, setup["paths"], setup["hooks"])
    assert rec["tests"] == ["T1", "T2", "T3"] and rec["engine_lead_in_dates"] == 1


def test_check_refuses_another_freeze_sha_a_changed_file_and_a_foreign_harness(setup) -> None:
    with pytest.raises(pf.Refused, match="freeze manifest"):
        run.check("1" * 64, HARNESS, setup["paths"], setup["hooks"])
    with pytest.raises(pf.Refused, match="harness"):
        run.check(setup["freeze_sha"], "2" * 64, setup["paths"], setup["hooks"])
    setup["paths"].gex.write_text("date,price,dix,gex\n", encoding="utf-8")
    with pytest.raises(pf.Refused, match="changed"):
        run.check(setup["freeze_sha"], HARNESS, setup["paths"], setup["hooks"])


def test_a_manifest_missing_an_h6_file_is_refused(setup) -> None:
    body = json.loads(setup["paths"].freeze.read_text())
    body["files"] = [f for f in body["files"] if not f["path"].endswith("h6_rod/stats.py")]
    setup["paths"].freeze.write_text(json.dumps(body))
    with pytest.raises(pf.Refused, match="stats.py"):
        run.check(_sha(setup["paths"].freeze), HARNESS, setup["paths"], setup["hooks"])


# ------------------------------------------------------------------ register / evaluate ----
def test_evaluate_before_register_refuses_and_writes_no_marker(setup) -> None:
    before = _real_registry_sha()
    with pytest.raises(pf.Refused, match="not registered"):
        run.evaluate(setup["freeze_sha"], HARNESS, setup["paths"], setup["hooks"],
                     test_mode=True, log=lambda s: None)
    assert not setup["paths"].marker.exists() and _real_registry_sha() == before


def test_the_test_registry_needs_the_test_mode(setup) -> None:
    with pytest.raises(pf.Refused, match="test mode"):
        run.register(setup["freeze_sha"], HARNESS, setup["paths"], setup["hooks"])


def test_register_once_evaluate_once_then_refuse(setup) -> None:
    from screening.trial_registry import read_registry

    before = _real_registry_sha()
    p, h, fsha = setup["paths"], setup["hooks"], setup["freeze_sha"]
    entry = run.register(fsha, HARNESS, p, h, test_mode=True)
    assert entry["test_ids"] == ["E20H6-T1", "E20H6-T2", "E20H6-T3"]
    assert (entry["n_before"], entry["n_after"]) == (471, 474) and entry["freeze_sha256"] == fsha
    with pytest.raises(pf.Refused, match="already registered"):
        run.register(fsha, HARNESS, p, h, test_mode=True)
    doc = run.evaluate(fsha, HARNESS, p, h, test_mode=True, log=lambda s: None)
    assert p.marker.exists() and p.result_json.exists() and p.result_md.exists()
    saved = json.loads(p.result_json.read_text())
    assert saved["registration"]["entry_id"] == entry["entry_id"]
    assert set(saved["verdicts"]) == {"T1", "T2", "T3"}
    assert all(v == K.FAIL for v in saved["verdicts"].values())  # fewer trades than the floor
    t1 = doc["tests"]["T1"]
    assert t1["n_trades"] == 10 and t1["lead_in_dates"] == ["2020-05-29"]
    assert t1["entry_outcomes"]["counts"] == {"traded": 10}
    n_window = len(clock.trade_dates(K.VERDICT_FIRST, K.VERDICT_LAST))
    assert doc["tests"]["T2"]["schedule_exclusions"] == {
        K.REASON_T2_WARMUP: 10, K.REASON_MISSING_SIGNAL_BAR: n_window - 10}
    assert t1["window_trade_dates"] == n_window
    t3 = doc["tests"]["T3"]
    # prior-day GEX < 0 on 05-29, 06-02 and 06-04 (T3 on 06-01, 06-03, 06-05); 06-01's row is
    # positive (06-02 excluded); no row for 06-03, 06-05, 06-08, 06-09, 06-10, 06-11
    assert [r["trade_date"] for r in t3["trades"]] == ["2020-06-01", "2020-06-03", "2020-06-05"]
    assert t3["schedule_exclusions"][K.REASON_GEX_NOT_NEGATIVE] == 1
    assert t3["schedule_exclusions"][K.REASON_GEX_MISSING] == 6
    assert saved["holm"]["m"] == 3
    assert saved["v2_modules_loaded_after_the_freeze_check"] == []
    assert doc["overlap"]["T1"]["n_trades"] == 0
    with pytest.raises(pf.Refused, match="run-once marker"):
        run.evaluate(fsha, HARNESS, p, h, test_mode=True, log=lambda s: None)
    assert len(read_registry(p.registry)) == 2 and _real_registry_sha() == before


def test_a_loader_refusal_after_the_marker_stops_every_test_and_is_written(setup) -> None:
    from dataclasses import replace

    from data.stage_e_bars import StageEBarRefusal

    def refuse(_p: object) -> None:
        raise StageEBarRefusal("planted refusal")

    p, fsha = setup["paths"], setup["freeze_sha"]
    hooks = replace(setup["hooks"], load_leg=refuse)
    run.register(fsha, HARNESS, p, hooks, test_mode=True)
    doc = run.evaluate(fsha, HARNESS, p, hooks, test_mode=True, log=lambda s: None)
    assert p.marker.exists()
    assert doc["verdicts"] == {"T1": K.STOPPED, "T2": K.STOPPED, "T3": K.STOPPED}
    assert "planted refusal" in json.loads(p.result_json.read_text())["tests"]["T1"]["reason"]


def test_any_exception_after_the_marker_stops_every_test_and_the_result_is_written(setup) -> None:
    from dataclasses import replace

    from tests._h6_rod_synth import no_releases

    calls = {"n": 0}

    def releases_then_fail() -> object:  # first call in check (before the marker), then fails
        calls["n"] += 1
        if calls["n"] > 1:
            raise RuntimeError("planted failure after the marker")
        return no_releases()

    p, fsha = setup["paths"], setup["freeze_sha"]
    run.register(fsha, HARNESS, p, setup["hooks"], test_mode=True)
    calls["n"] = 0
    hooks = replace(setup["hooks"], releases=releases_then_fail)
    doc = run.evaluate(fsha, HARNESS, p, hooks, test_mode=True, log=lambda s: None)
    assert calls["n"] == 2 and p.marker.exists() and p.result_json.exists()
    saved = json.loads(p.result_json.read_text())
    assert saved["verdicts"] == {"T1": K.STOPPED, "T2": K.STOPPED, "T3": K.STOPPED}
    for block in ("tests", "overlap"):
        for rec in saved[block].values():
            assert rec["status"] == K.STOPPED and "planted failure" in rec["reason"]
            assert "Traceback" in rec["traceback"] and "RuntimeError" in rec["traceback"]
    assert saved["post_marker_exception"]["type"] == "RuntimeError"
    assert run.evaluation_exit_code(doc) == K.RC_ERROR
    assert run.evaluation_exit_code({"verdicts": {}}) == K.RC_OK


def test_a_store_validation_problem_refuses_before_the_marker(setup) -> None:
    from dataclasses import replace

    def bad(_p: object) -> None:
        raise ValueError("planted duplicate timestamps")

    p, fsha = setup["paths"], setup["freeze_sha"]
    hooks = replace(setup["hooks"], validate_store=bad)
    run.register(fsha, HARNESS, p, hooks, test_mode=True)
    with pytest.raises(pf.Refused, match="planted"):
        run.evaluate(fsha, HARNESS, p, hooks, test_mode=True, log=lambda s: None)
    assert not p.marker.exists()


def test_a_stopped_test_enters_holm_with_p_one() -> None:
    records = {"T1": {"status": K.STOPPED},
               "T2": {"p_one_sided": 0.001, "mean_gross_ticks": 9.0, "mean_cost_ticks": 4.0,
                      "n_trades": 200, "annualized_net_sharpe": 0.9}}
    out = run.verdicts(records, ("T1", "T2"))
    assert out["verdicts"] == {"T1": K.STOPPED, "T2": K.PASS}
    assert out["holm"]["m"] == 2 and out["holm"]["rejected"] == {"T1": False, "T2": True}


def test_the_default_store_functions_refuse_through_the_guard_before_opening(tmp_path) -> None:
    from h6_rod.guard import GuardRefusal

    elsewhere = tmp_path / "allowed.parquet"  # the NQ step 2 path is not this file
    paths = run.RunPaths(elsewhere, elsewhere, tmp_path / "g.csv", tmp_path / "f.json",
                         tmp_path / "m.json", tmp_path / "r.json", tmp_path / "r.md",
                         tmp_path / "reg.jsonl")
    with pytest.raises(GuardRefusal):
        run.validate_store(paths)
    with pytest.raises(GuardRefusal):
        run.load_leg(paths)


_HOOKED_RUN = """
import sys
sys.path.insert(0, {repo!r})
from h6_rod import guard
guard.install_audit_hook()
from h6_rod import run
from tests._h6_rod_synth import make_run_setup
s = make_run_setup({tmp!r}, setattr)
run.register(s["freeze_sha"], {harness!r}, s["paths"], s["hooks"], test_mode=True)
doc = run.evaluate(s["freeze_sha"], {harness!r}, s["paths"], s["hooks"], test_mode=True,
                   log=lambda m: None)
print("HOOKED_RUN_OK", guard.hook_installed(), doc["tests"]["T1"]["n_trades"])
"""


def test_the_whole_synthetic_run_works_under_the_audit_hook(tmp_path) -> None:
    from data.config import REPO_ROOT

    script = _HOOKED_RUN.format(repo=str(REPO_ROOT), tmp=str(tmp_path), harness=HARNESS)
    proc = subprocess.run([sys.executable, "-c", script], cwd=REPO_ROOT, capture_output=True,
                          text=True, timeout=300, check=False)
    assert proc.returncode == 0, proc.stderr[-3000:]
    assert "HOOKED_RUN_OK True 10" in proc.stdout
    assert (tmp_path / "RUN_ONCE.json").exists() and (tmp_path / "result.json").exists()
