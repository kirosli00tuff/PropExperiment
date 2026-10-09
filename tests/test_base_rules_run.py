"""base_rules.run: the freeze-manifest check, the registration check and the run-once marker
(written before any bar; a second run refused), on temporary files only (no real ledger)."""

from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from base_rules import constants as K
from base_rules import guards as G
from base_rules import results as R
from base_rules.common import RunOutput
from base_rules.run import main
from screening.trial_registry import init_registry, register


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture()
def setup(tmp_path):  # noqa: ANN001, ANN201
    inputs = {}
    for name in G.INPUT_NAMES:
        p = tmp_path / "inputs" / f"{name}.json"
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps({"name": name}))
        inputs[name] = str(p)
    paths = tmp_path / "input_paths.json"
    paths.write_text(json.dumps(inputs))
    freeze = G.manifest_body([*G.code_files(), *(Path(p) for p in inputs.values())])
    fpath = tmp_path / "freeze.json"
    fpath.write_text(json.dumps(freeze))
    registry = tmp_path / "trial_registrations.jsonl"
    init_registry(registry, time_local="2026-10-09T00:00:00-07:00")
    out = tmp_path / "runs"
    return {"freeze": fpath, "sha": _sha(fpath), "registry": registry, "out": out,
            "freeze_obj": freeze, "tmp": tmp_path, "inputs": inputs, "paths": paths}


def _register(s) -> None:  # noqa: ANN001
    register("E16", [f"E16-{t}" for t in K.TESTS], s["freeze"], s["sha"], "a" * 64,
             path=s["registry"], time_local="2026-10-09T00:00:00-07:00")


def _args(s, test: str, *extra: str) -> list[str]:  # noqa: ANN001
    return ["run", "--test", test, "--freeze", str(s["freeze"]), "--freeze-sha256", s["sha"],
            "--out-dir", str(s["out"]), "--registry", str(s["registry"]),
            "--input-paths", str(s["paths"]), *extra]


def _component_results(s) -> None:  # noqa: ANN001
    days = [date(2016, 1, 4) + timedelta(days=k) for k in range(300)]
    for i, name in enumerate(K.H5_COMPONENTS):
        series = {c: [(d, 0.1 * ((k * (i + 3)) % 7 - 3)) for k, d in enumerate(days)]
                  for c in K.COST_CASES}
        out = RunOutput(name, series, {c: dict(v) for c, v in series.items()}, set(days),
                         __import__("collections").Counter(), {}, [])
        R.write(out, s["out"], {"status": "complete", "freeze_sha256": s["sha"]})


def test_an_unregistered_test_is_refused_and_nothing_is_written(setup) -> None:
    assert main(_args(setup, "H5")) == K.RC_REFUSED
    assert not G.marker_path(setup["out"], "H5").exists()


def test_a_wrong_freeze_sha256_or_changed_code_is_refused(setup) -> None:
    _register(setup)
    bad = dict(setup, sha="0" * 64)
    assert main(_args(bad, "H5")) == K.RC_REFUSED
    drift = dict(setup["freeze_obj"], files=[e for e in setup["freeze_obj"]["files"]
                                             if e["path"] != "base_rules/run.py"])
    setup["freeze"].write_text(json.dumps(drift))
    assert main(_args(dict(setup, sha=_sha(setup["freeze"])), "H5")) == K.RC_REFUSED
    assert not G.marker_path(setup["out"], "H5").exists()


def test_a_changed_input_is_refused(setup) -> None:
    _register(setup)
    Path(setup["inputs"]["settlement"]).write_text("{}")
    assert main(_args(setup, "H5")) == K.RC_REFUSED


def test_h1_without_a_run_manifest_and_h5_without_components_are_refused(setup) -> None:
    _register(setup)
    assert main(_args(setup, "H1")) == K.RC_REFUSED
    assert main(_args(setup, "H5")) == K.RC_REFUSED
    assert not setup["out"].exists() or not any(setup["out"].glob("*RUN_ONCE*"))


def test_the_marker_is_written_once_and_a_second_run_is_refused(setup) -> None:
    _register(setup)
    _component_results(setup)
    assert main(_args(setup, "H5")) == K.RC_OK
    marker = json.loads(G.marker_path(setup["out"], "H5").read_text())
    assert marker["test"] == "H5" and set(marker["components"]) == set(K.H5_COMPONENTS)
    assert marker["registry"]["sha256"] == _sha(setup["registry"])
    rec = json.loads(R.result_path(setup["out"], "H5").read_text())
    assert rec["status"] == "complete" and rec["stats"]["base"]["n"] == 300 - K.H5_WARMUP
    assert main(_args(setup, "H5")) == K.RC_REFUSED
    with pytest.raises(G.Refused):
        G.write_marker(setup["out"], "H5", {})


def test_the_registration_must_hold_the_freeze_label(setup) -> None:
    register("E99", ["E99-H1"], setup["freeze"], setup["sha"], "a" * 64, path=setup["registry"],
             time_local="2026-10-09T00:00:00-07:00")
    freeze = G.check_freeze(setup["freeze"], setup["sha"], input_paths=setup["inputs"])
    with pytest.raises(G.Refused):
        G.check_registered("H1", freeze, setup["registry"], setup["sha"])
    with pytest.raises(G.Refused):  # an input outside the freeze's files
        G.check_freeze(setup["freeze"], setup["sha"])


def test_an_e16_registration_under_another_freeze_sha256_is_refused(setup) -> None:
    other = setup["tmp"] / "other_freeze.json"
    other.write_text("{}")
    register("E16", [f"E16-{t}" for t in K.TESTS], other, _sha(other), "a" * 64,
             path=setup["registry"], time_local="2026-10-09T00:00:00-07:00")
    freeze = G.check_freeze(setup["freeze"], setup["sha"], input_paths=setup["inputs"])
    with pytest.raises(G.Refused, match="freeze sha256"):
        G.check_registered("H1", freeze, setup["registry"], setup["sha"])
    _component_results(setup)
    assert main(_args(setup, "H5")) == K.RC_REFUSED
    assert not G.marker_path(setup["out"], "H5").exists()


def test_a_registry_other_than_the_ledger_needs_the_test_mode(setup) -> None:
    with pytest.raises(G.Refused, match="ledger"):
        G.check_registry_path(setup["registry"], test_mode=False)
    got = G.check_registry_path(setup["registry"], test_mode=True)
    assert got["sha256"] == _sha(setup["registry"])
    _register(setup)
    _component_results(setup)
    args = [a for a in _args(setup, "H5")]
    k = args.index("--input-paths")
    assert main(args[:k] + args[k + 2:]) == K.RC_REFUSED  # no test mode: the tmp registry fails


def test_a_lead_format_manifest_lists_every_code_file() -> None:
    body = G.manifest_body(G.code_files())
    assert {e["path"] for e in body["files"]} >= {"base_rules/run.py", "base_rules/sim.py"}


def test_the_verdict_applies_holm_across_the_registered_tests(setup) -> None:
    _register(setup)
    _component_results(setup)
    assert main(_args(setup, "H5")) == K.RC_OK
    args = ["verdict", "--freeze", str(setup["freeze"]), "--freeze-sha256", setup["sha"],
            "--out-dir", str(setup["out"]), "--registry", str(setup["registry"]),
            "--input-paths", str(setup["paths"])]
    assert main(args) == K.RC_OK
    v = json.loads((setup["out"] / "verdict.json").read_text())
    assert set(v["tests"]) == set(K.TESTS) and v["n_trials_at_verdict"] == 471 + 5
    assert "dsr" in v and v["registry"]["sha256"] == _sha(setup["registry"])
    assert v["registered_tests"] == list(K.TESTS)
    with pytest.raises(SystemExit):  # F-03: no --tests option
        main([*args, "--tests", "H1"])


def test_an_input_problem_found_building_the_context_refuses_before_the_marker(setup) -> None:
    _register(setup)
    manifest = setup["tmp"] / "run_manifest.json"
    manifest.write_text(json.dumps({"schema": K.RUN_MANIFEST_SCHEMA, "stores": {
        p: {"ext2010": None, "step2": {"path": f"/nowhere/{p}/x.parquet", "sha256": "a" * 64}}
        for p in K.PRODUCTS}}))
    args = _args(setup, "H2", "--manifest", str(manifest), "--manifest-sha256", _sha(manifest))
    assert main(args) == K.RC_REFUSED  # the dummy settlement table refuses (an input problem)
    assert not G.marker_path(setup["out"], "H2").exists()
