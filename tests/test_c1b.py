"""Test C1b (c1_replication.c1b): C1's evaluation under C1b's ids with guard C10's one clause.
Synthetic world only (tests/test_c1_evaluate.py's environment: SYNTHETIC calendars, releases,
bars, M1 and a temp trial registry).

Covers: the exempt list is exactly g17_mbt and g17_cl; the amended c10_check exempts those two and
keeps C1's rule on every other covered signal; the frozen C1 check stops where C1b's does not
(the E.17 contradiction); the profile swaps and restores evaluate's attributes (also on an
exception) and refuses nesting; end to end, a reference with g17_mbt live in E.12 no longer
stops, a dead non-exempt signal still stops and closes the attempt, the result carries C1b's ids
and exempt list, C1's registration does not admit C1b; the CLI's C1b freeze and marker paths.
"""

from __future__ import annotations

import json

import pytest

from c1_replication import c1b
from c1_replication import evaluate as ev
from c1_replication.guards import C1Refused
from screening import trial_registry
from tests import test_c1_evaluate
from tests.test_c1_evaluate import EDGE, HARNESS, SIGNALS, c10_ref, loader, make_env, run_inputs

EXEMPT = ("g17_cl", "g17_mbt")
C1_ATTRS = {name: getattr(ev, name) for name in c1b.SWAPS}


@pytest.fixture(scope="module", autouse=True)
def _free_legs():
    yield
    test_c1_evaluate._LEGS.clear()


def _ref(n: int = 5, **override: int) -> dict:
    app = {s: n for s in SIGNALS}
    app.update(override)
    return {h: {"ng_ok_rows": 100, "applicable": dict(app)} for h in ("h60", "hF")}


def _env_c1b(base, **kw):
    env = make_env(base, register=False, **kw)
    trial_registry.register(c1b.TEST, list(c1b.TEST_IDS), env.freeze, env.freeze_sha, HARNESS,
                            path=env.registry)
    return env


def _run_c1b(env, *, seed=3, plants=()):
    return c1b.run(run_inputs(env), preflight=lambda s: s, leg_loader=loader(seed, plants),
                   log=lambda _m: None)


# ------------------------------------------------------------------ the exempt list ----
def test_exempt_list_is_exactly_mbt_and_cl_and_both_are_covered_signals():
    assert tuple(sorted(c1b.C10_EXEMPT)) == EXEMPT
    assert set(EXEMPT) <= set(SIGNALS)
    assert c1b.TEST_IDS == ("C1b-T1", "C1b-T2")
    assert dict(c1b.HORIZON_OF) == {"C1b-T1": "h60", "C1b-T2": "hF"}


def test_amended_c10_exempts_mbt_where_c1s_rule_stops():
    ref = _ref(g17_mbt=87, g17_cl=0)
    counts = _ref(g17_mbt=0, g17_cl=0)
    assert c1b.c10_check(counts, ref) == []
    assert ev.c10_check(counts, ref) == ["g17_mbt (h60)", "g17_mbt (hF)"]  # C1, as in E.17


@pytest.mark.parametrize("signal", [s for s in SIGNALS if s not in EXEMPT])
def test_amended_c10_keeps_c1s_rule_on_every_other_signal(signal):
    ref, counts = _ref(), _ref(**{signal: 0})
    want = [f"{signal} (h60)", f"{signal} (hF)"]
    assert c1b.c10_check(counts, ref) == want == ev.c10_check(counts, ref)
    assert c1b.c10_check(_ref(**{signal: 0}), _ref(**{signal: 0})) == []  # dead in E.12: no stop


@pytest.mark.parametrize("signal", EXEMPT)
def test_exempt_signals_never_stop(signal):
    assert c1b.c10_check(_ref(**{signal: 0}), _ref()) == []
    assert ev.c10_check(_ref(**{signal: 0}), _ref()) == [f"{signal} (h60)", f"{signal} (hF)"]


def test_amended_c10_leaves_the_reference_unchanged():
    ref = _ref(g17_mbt=87)
    before = json.dumps(ref, sort_keys=True)
    c1b.c10_check(_ref(g17_mbt=0), ref)
    assert json.dumps(ref, sort_keys=True) == before


# ------------------------------------------------------------------ the profile ----
def test_profile_swaps_and_restores_evaluates_attributes():
    with c1b.c1b_profile():
        assert ev.TEST == "C1b" and ev.TEST_IDS == c1b.TEST_IDS
        assert ev.HORIZON_OF is c1b.HORIZON_OF and ev.c10_check is c1b.c10_check
        with pytest.raises(C1Refused, match="already active"), c1b.c1b_profile():
            pass
    assert {name: getattr(ev, name) for name in c1b.SWAPS} == C1_ATTRS
    with pytest.raises(RuntimeError, match="boom"), c1b.c1b_profile():
        raise RuntimeError("boom")
    assert {name: getattr(ev, name) for name in c1b.SWAPS} == C1_ATTRS
    assert ev.TEST == "C1" and ev.TEST_IDS == ("C1-T1", "C1-T2")


# ------------------------------------------------------------------ end to end ----
def test_mbt_live_in_e12_no_longer_stops_and_the_result_is_c1bs(tmp_path):
    env = _env_c1b(tmp_path, ref=c10_ref({"g17_mbt": 87}))
    out = _run_c1b(env, plants=EDGE)
    assert out["verdict"] == ev.PASS and out["test"] == "C1b"
    assert out["test_ids"] == ["C1b-T1", "C1b-T2"] and sorted(out["tests"]) == ["C1b-T1", "C1b-T2"]
    assert out["guards"]["C10"]["h60"]["applicable"]["g17_mbt"] == 0
    assert sorted(out["inputs"]["c1b"]["c10_exempt"]) == list(EXEMPT)
    assert out["inputs"]["registry"]["entry_id"].endswith("-C1b")
    marker = json.loads((tmp_path / "RUN_ONCE.json").read_text())
    assert marker["test"] == "C1b" and "c1b" in marker["inputs"]
    assert {name: getattr(ev, name) for name in c1b.SWAPS} == C1_ATTRS
    with pytest.raises(C1Refused, match="runs once"):
        _run_c1b(env)


def test_the_same_reference_stops_c1s_frozen_run(tmp_path):
    env = make_env(tmp_path, ref=c10_ref({"g17_mbt": 87}))  # registered as C1
    out = ev.run(run_inputs(env), preflight=lambda s: s, leg_loader=loader(3),
                 log=lambda _m: None)
    assert out["verdict"] == ev.STOPPED and "g17_mbt" in out["stop_reason"]


def test_a_dead_non_exempt_signal_still_stops_and_closes_the_attempt(tmp_path):
    env = _env_c1b(tmp_path, ref=c10_ref({"g17_mbt": 87, "k1_vwap_dist": 12}))
    out = _run_c1b(env)
    assert out["verdict"] == ev.STOPPED and out["stop_reason"].startswith("C10")
    assert "k1_vwap_dist" in out["stop_reason"] and "g17_mbt" not in out["stop_reason"]
    assert "tests" not in out
    with pytest.raises(C1Refused, match="runs once"):
        _run_c1b(env)


def test_c1s_registration_does_not_admit_c1b(tmp_path):
    env = make_env(tmp_path)  # C1-T1 and C1-T2 registered, not C1b's ids
    with pytest.raises(C1Refused, match="not registered"):
        _run_c1b(env)
    assert not (tmp_path / "RUN_ONCE.json").exists() and not (tmp_path / "result.json").exists()


def test_cli_uses_c1bs_freeze_and_marker(tmp_path, monkeypatch):
    seen = {}

    def fake_run(inp, *, preflight=None):
        seen["inp"] = inp
        return {"verdict": ev.FAIL}

    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    monkeypatch.setattr(c1b, "run", fake_run)
    args = ["--harness-sha256", HARNESS, "--freeze-sha256", "b" * 64, "--model", "m.json",
            "--model-sha256", "c" * 64, "--model-dir", str(tmp_path), "--store-hashes", "s.json",
            "--calendar-hashes", "k.json", "--out", str(tmp_path / "out.json")]
    assert c1b.main(args) == 0
    assert seen["inp"].freeze_path == c1b.FREEZE_PATH
    assert seen["inp"].marker_path == c1b.MARKER_PATH != ev.MARKER_PATH


def test_cli_refuses_with_exit_2_and_writes_nothing(tmp_path, monkeypatch, capsys):
    env = make_env(tmp_path, register=False)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    existed = c1b.MARKER_PATH.exists()
    args = ["--harness-sha256", HARNESS, "--freeze", str(env.freeze), "--freeze-sha256",
            env.freeze_sha, "--model", str(env.model), "--model-sha256", env.model_sha,
            "--model-dir", str(env.model_dir), "--store-hashes", str(env.store_hashes),
            "--calendar-hashes", str(env.inputs.hashes), "--out", str(tmp_path / "cli.json")]
    # the real registry holds no C1b registration under this synthetic freeze
    assert c1b.main(args, preflight=lambda s: s) == ev.RC_REFUSED
    assert "REFUSED, nothing written" in capsys.readouterr().err
    assert not (tmp_path / "cli.json").exists() and c1b.MARKER_PATH.exists() == existed
    assert {name: getattr(ev, name) for name in c1b.SWAPS} == C1_ATTRS
