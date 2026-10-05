"""Test C1, part 1 (c1_replication.q_m1) on a synthetic E.12-like state. No market data, no real
E.12 state: tests/_c1_state.py builds the state with the frozen code (the 45 OOF splits are fitted
once there and only reloaded by q_m1).

Covers: the reproduction reloads and never refits (a spy on the frozen ridge fit), q = the
smallest |r_hat| of NG's Gate 0 trades, M1 determinism (same payload sha256 twice, equal to a
direct frozen fit), the mismatch stop (exact counts, absolute 1e-9 on mean and t_B, nothing
written), the state-manifest refusals before anything is loaded, a missing split, the ledger
checks, the output and model-dir refusals, and the CLI's exit codes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from c1_replication import q_m1
from c1_replication.constants import RC_REFUSED, RC_STOP
from c1_replication.guards import C1Refused, C1Stop
from ml_route_v2 import models
from ml_route_v2.configs import ConfigLedger, ridge_spec
from ml_route_v2.constants import GATE0_RIDGE_LAMBDA
from ml_route_v2.cpcv import horizon_data
from ml_route_v2.gate0 import family_b_id, gate0_b_trades
from tests._c1_state import make_state, rewrite_report, sha, write_manifest


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return make_state(tmp_path_factory.mktemp("c1_state"))


def _run(st, tmp: Path, *, report=None, ledger=None, name="m", **kw):
    return q_m1.run(st.state, st.manifest, tmp / f"{name}.json", tmp / f"{name}_models",
                    ledger=ledger or st.ledger, report=report or (st.report, st.report_sha),
                    listed=(st.listed, st.listed_sha), log=lambda _m: None, **kw)


def _fit_spy(monkeypatch):
    calls = {"n": 0}
    real = models._fit_ridge

    def spy(*a, **k):
        calls["n"] += 1
        return real(*a, **k)

    monkeypatch.setattr(models, "_fit_ridge", spy)
    return calls


def test_reproduces_without_refitting_and_fits_m1_twice_per_horizon(built, tmp_path,
                                                                       monkeypatch):
    calls = _fit_spy(monkeypatch)
    doc = _run(built, tmp_path)
    # Gate 0's 45 splits were only reloaded; the 4 fits are M1's (2 horizons x 2 fits)
    assert calls["n"] == 4
    for h in ("h60", "hF"):
        rec = doc["reproduction"]["rows"][h]
        assert rec["match"] and rec["abs_diff"]["mean_gross_ticks"] == 0.0
        assert rec["reproduced"]["n_trades"] == rec["e12"]["n_trades"]
    assert doc["ml_ledger"]["unchanged"] and doc["ml_ledger"]["copy_unchanged"]
    assert doc["state"]["before"] == doc["state"]["after"]
    assert (tmp_path / "m.json").is_file()


def test_q_is_the_smallest_abs_prediction_among_ngs_trades(built, tmp_path):
    doc = _run(built, tmp_path)
    trades = gate0_b_trades(built.panel, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                            state_dir=built.state / "gate0", admissible=built.admissible,
                            calendar=list(built.calendar))
    for h in ("h60", "hF"):
        sub = trades.loc[trades["test_id"] == family_b_id("NG", h)]
        want = float(np.min(np.abs(sub["r_hat"].to_numpy())))
        assert doc["q"][h]["q"] == want and doc["q"][h]["q_repr"] == repr(want)
        assert doc["q"][h]["n_trades"] == len(sub)
        # the threshold rule picks exactly Gate 0's trade set on the training rows (ruling C3)
        assert doc["q"][h]["n_oof_rows_at_or_above_q"] == len(sub)


def test_m1_is_deterministic_and_equals_the_frozen_fit(built, tmp_path):
    a = _run(built, tmp_path, name="a")
    b = _run(built, tmp_path, name="b")
    for h in ("h60", "hF"):
        assert a["m1"][h]["payload_sha256"] == b["m1"][h]["payload_sha256"]
        data = horizon_data(built.panel, h, built.admissible)
        direct = models.fit_model(ridge_spec(GATE0_RIDGE_LAMBDA), data.X, data.y)
        assert direct.sha256 == a["m1"][h]["payload_sha256"]
        stored = Path(a["m1"][h]["payload_file"]).read_bytes()
        assert models._sha256(stored) == direct.sha256
        assert a["m1"][h]["n_train_rows"] == data.y.shape[0]
    assert a["feature_cols"] == list(built.panel.feature_cols)
    assert a["feature_cols_sha256"] == q_m1.feature_cols_sha256(built.panel.feature_cols)


def test_a_state_from_the_frozen_synthetic_pipeline(tmp_path, monkeypatch):
    from ml_route_v2.signals import REGISTRY
    from tests._c1_state import make_pipeline_state

    st = make_pipeline_state(tmp_path / "p")
    calls = _fit_spy(monkeypatch)
    doc = _run(st, tmp_path)
    assert calls["n"] == 4  # M1 only: the 45 splits were written once by make_pipeline_state
    assert doc["feature_cols_follow_from_signals"] is True
    assert doc["signals"] == list(REGISTRY)
    for h in ("h60", "hF"):
        assert doc["reproduction"]["rows"][h]["match"]
        ref = doc["c10_reference"][h]["applicable"]
        assert ref["g02_ret60"] == doc["c10_reference"][h]["ng_ok_rows"] > 0
        assert ref["k4_apipre_ret"] == 0 and ref["g17_cl"] == 0  # MCL member; own cluster lead
        assert doc["q"][h]["n_oof_rows_at_or_above_q"] == doc["q"][h]["n_trades"]


def test_c10_reference_counts_ng_rows_where_each_signal_applies(built, tmp_path):
    doc = _run(built, tmp_path)
    for h in ("h60", "hF"):
        ref = doc["c10_reference"][h]
        assert ref["applicable"]["s2"] == 0  # synthetic: s2 never applies on NG rows
        assert ref["applicable"]["s0"] == ref["ng_ok_rows"] > 0


@pytest.mark.parametrize("edit", [
    {"h60": {"n_trades": -1}},
    {"hF": {"n_dates": 1}},
    {"h60": {"mean_gross_ticks": "shift:2e-9"}},
    {"hF": {"t_B": "shift:-2e-9"}},
])
def test_any_mismatch_stops_and_writes_nothing(built, tmp_path, edit):
    base = json.loads(built.report.read_text())
    rows = {r["horizon"]: r for r in base["tests"]}
    applied = {}
    for h, kv in edit.items():
        applied[h] = {}
        for k, v in kv.items():
            if isinstance(v, str) and v.startswith("shift:"):
                applied[h][k] = rows[h][k] + float(v.split(":")[1])
            elif k == "n_trades":
                applied[h][k] = rows[h][k] + 1
            else:
                applied[h][k] = rows[h][k] + v
    report = rewrite_report(built, applied)
    with pytest.raises(C1Stop, match="C1 STOP: q reproduction mismatch"):
        _run(built, tmp_path, report=report)
    assert not (tmp_path / "m.json").exists()
    assert not (tmp_path / "m_models").exists() or not any((tmp_path / "m_models").iterdir())


def test_float_tolerance_is_absolute_1e9_inclusive(built, tmp_path):
    rows = {r["horizon"]: r for r in json.loads(built.report.read_text())["tests"]}
    report = rewrite_report(built, {"h60": {"mean_gross_ticks": rows["h60"]["mean_gross_ticks"]
                                            + 5e-10}})
    doc = _run(built, tmp_path, report=report)
    assert 0 < doc["reproduction"]["rows"]["h60"]["abs_diff"]["mean_gross_ticks"] <= 1e-9


def test_state_refusals_happen_before_anything_is_loaded(built, tmp_path, monkeypatch):
    import ml_route_v2.phase1.build as build_mod

    loaded = {"n": 0}
    real = build_mod.load_build
    monkeypatch.setattr(build_mod, "load_build",
                        lambda *a, **k: loaded.__setitem__("n", loaded["n"] + 1) or real(*a, **k))
    doc = json.loads(built.manifest.read_text())
    victim = "gate0/gate0B_h60_s03.npy"
    bad = dict(doc)
    bad["files"] = {**doc["files"], victim: {**doc["files"][victim], "sha256": "0" * 64}}
    path = tmp_path / "bad_manifest.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(C1Refused, match="sha256 differs"):
        q_m1.run(built.state, path, tmp_path / "x.json", tmp_path / "xm", ledger=built.ledger,
                 report=(built.report, built.report_sha), listed=(built.listed, built.listed_sha))
    missing = dict(doc)
    missing["files"] = {k: v for k, v in doc["files"].items() if k != victim}
    path.write_text(json.dumps(missing))
    with pytest.raises(C1Refused, match="does not list"):
        q_m1.run(built.state, path, tmp_path / "x.json", tmp_path / "xm", ledger=built.ledger,
                 report=(built.report, built.report_sha), listed=(built.listed, built.listed_sha))
    with pytest.raises(C1Refused, match="sha256"):
        _run(built, tmp_path, manifest_sha256="f" * 64)
    assert loaded["n"] == 0 and not (tmp_path / "x.json").exists()


def test_an_unlisted_file_in_the_state_dir_is_refused(tmp_path):
    st = make_state(tmp_path / "s", seed=8)
    (st.state / "gate0" / "stray.tmp.npy").write_bytes(b"x")
    with pytest.raises(C1Refused, match="not in the manifest"):
        _run(st, tmp_path)


def test_a_missing_split_file_is_refused_before_any_fit(tmp_path, monkeypatch):
    st = make_state(tmp_path / "s", seed=9)
    (st.state / "gate0" / "gate0B_hF_s07.npy").unlink()
    write_manifest(st.state, st.manifest)  # a manifest of what is there: 44 split files
    calls = _fit_spy(monkeypatch)
    with pytest.raises(C1Refused, match="does not list"):
        _run(st, tmp_path)
    assert calls["n"] == 0


def test_split_check_names_the_missing_file(built, tmp_path):
    from ml_route_v2.phase1.build import load_build

    b = load_build(built.state)
    gate = tmp_path / "gate0"
    gate.mkdir()
    with pytest.raises(C1Stop, match="OOF split files missing"):
        q_m1.split_files(b, built.admissible, gate)


def test_no_fit_guard_stops_a_refit(built, tmp_path):
    from c1_replication.guards import no_fits
    from ml_route_v2 import gate0

    original = gate0.fit_model
    with pytest.raises(C1Stop, match="tried to fit"), no_fits():
        gate0.fit_model(ridge_spec(0.1), np.ones((3, 1)), np.ones(3))
    assert gate0.fit_model is original


def test_ledger_without_the_registrations_stops(built, tmp_path):
    empty = tmp_path / "empty_ledger.jsonl"
    empty.write_text("")
    before = sha(empty)
    with pytest.raises(C1Stop, match="ledger"):
        _run(built, tmp_path, ledger=empty)
    assert sha(empty) == before  # the real file is never written
    assert not (tmp_path / "m.json").exists()


def test_out_and_model_dir_refusals(built, tmp_path):
    from data.config import REPO_ROOT

    (tmp_path / "m.json").write_text("{}")
    with pytest.raises(C1Refused, match="written once"):
        _run(built, tmp_path)
    with pytest.raises(C1Refused, match="inside the repository"):
        q_m1.run(built.state, built.manifest, tmp_path / "y.json", REPO_ROOT / "reports" / "x",
                 ledger=built.ledger)


def test_model_file_with_other_bytes_is_never_replaced(built, tmp_path):
    md = tmp_path / "m_models"
    md.mkdir()
    (md / q_m1.payload_name("h60")).write_bytes(b"other")
    with pytest.raises(C1Refused, match="never replaced"):
        _run(built, tmp_path)


def test_cli_exit_codes(built, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(q_m1, "E12_GATE0_REPORT", built.report)
    monkeypatch.setattr(q_m1, "E12_GATE0_REPORT_SHA256", built.report_sha)
    monkeypatch.setattr(q_m1, "E12_GATE0_LIST", built.listed)
    monkeypatch.setattr(q_m1, "E12_GATE0_LIST_SHA256", built.listed_sha)
    monkeypatch.setattr(q_m1, "ML_LEDGER", built.ledger)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    args = ["--state", str(built.state), "--state-manifest", str(built.manifest),
            "--model-dir", str(tmp_path / "md")]
    assert q_m1.main([*args, "--out", str(tmp_path / "ok.json")]) == 0
    assert q_m1.main([*args, "--out", str(tmp_path / "ok.json")]) == RC_REFUSED
    report, report_sha = rewrite_report(built, {"h60": {"n_trades": 0}})
    monkeypatch.setattr(q_m1, "E12_GATE0_REPORT", report)
    monkeypatch.setattr(q_m1, "E12_GATE0_REPORT_SHA256", report_sha)
    assert q_m1.main([*args, "--out", str(tmp_path / "stop.json")]) == RC_STOP
    assert "C1 STOP: q reproduction mismatch" in capsys.readouterr().err
    assert not (tmp_path / "stop.json").exists()
