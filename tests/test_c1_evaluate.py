"""Test C1, part 2 (c1_replication.evaluate) end to end on a synthetic world. No market data:
six SYNTHETIC hist calendars, a SYNTHETIC release file, frozen synthetic bars (ml_route_v2.
synthetic) served by a test double with load_hist_leg's interface, SYNTHETIC store files that are
only hashed, a SYNTHETIC M1 (a frozen-format ridge payload with chosen coefficients) and a temp
trial registry. E.12's real covered-signal list (a committed report, no data) gives the panel's
signals.

Covers: a planted edge passes and noise fails through the frozen panel and statistic; the run-once
marker is written before any bar is read and a second run is refused; every precondition refusal
writes nothing and reads no bar (registry, freeze, model, payload, stores, C11 before the
marker, C12 share, the clock); the C10 and C11 stops after the marker close the attempt with
verdict STOPPED; a C12-excluded date has no NG row; the pass-bar boundaries.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from c1_replication import evaluate as ev
from c1_replication.constants import E12_GATE0_LIST, STORE_ROOTS
from c1_replication.guards import C1Refused
from data.hist_store import hist_parquet_path
from screening import trial_registry
from tests._c1_fixtures import (
    Inputs,
    calendar_payload,
    ridge_model,
    sha,
    synthetic_leg,
    vol_ticks_table,
    write_inputs,
    write_model,
)

FIRST, LAST_BARS = date(2010, 6, 7), date(2011, 9, 30)
HARNESS = "a" * 64
SIGNALS = tuple(json.loads(E12_GATE0_LIST.read_text())["covered_signals"])
COLS = ev.expected_feature_cols(SIGNALS)
RET60 = {"h60": {"z_g02_ret60": 1.0}, "hF": {"z_g02_ret60": 1.0}}
Q = {"h60": 0.5, "hF": 0.5}
EDGE = ({"kind": "sign", "edge_cost_multiple": 8.0, "feature_minutes": 60, "horizon_minutes": 60,
         "vehicles": ("NG",)},)
LIVE = ("cp1_ret", "g02_ret60", "g17_nq", "g17_zn", "g17_6e", "g17_gc", "g17_zc", "k4_ngpre_mto",
        "k4_ovr_pct")
_LEGS: dict = {}


@pytest.fixture(scope="module", autouse=True)
def _free_legs():
    yield
    _LEGS.clear()


@dataclass(frozen=True)
class Env:
    base: Path
    inputs: Inputs
    registry: Path
    freeze: Path
    freeze_sha: str
    store_hashes: Path
    hist_root: Path
    model: Path
    model_sha: str
    model_dir: Path


def c10_ref(extra: dict | None = None) -> dict:
    app = {s: (7 if s in LIVE else 0) for s in SIGNALS}
    app.update(extra or {})
    return {h: {"ng_ok_rows": 100, "applicable": dict(app)} for h in ("h60", "hF")}


def make_env(base: Path, *, weights=RET60, q=Q, ref=None, calendars=None, releases=None,
             register=True, cols=COLS) -> Env:
    vol_ticks_table()
    inputs = write_inputs(base / "cal", calendars=calendars, releases=releases)
    freeze = base / "prereg_C1.md"
    freeze.write_text("SYNTHETIC C1 freeze for tests\n")
    registry = base / "trial_registrations.jsonl"
    trial_registry.init_registry(registry)
    if register:
        trial_registry.register("C1", ["C1-T1", "C1-T2"], freeze, sha(freeze), HARNESS,
                                path=registry)
    hist_root = base / "hist"
    stores = {}
    for r in STORE_ROOTS:
        p = hist_parquet_path(r, "ext2010", hist_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"SYNTHETIC store {r}".encode())
        stores[r] = sha(p)
    store_hashes = base / "store_hashes.json"
    store_hashes.write_text(json.dumps({"schema": ev.STORE_HASHES_SCHEMA, "plan": "ext2010",
                                        "stores": stores}))
    fitted = {h: ridge_model(COLS, weights[h]) for h in ("h60", "hF")}
    model, model_sha, model_dir = write_model(base, cols, SIGNALS, fitted, q, ref or c10_ref())
    return Env(base, inputs, registry, freeze, sha(freeze), store_hashes, hist_root, model,
               model_sha, model_dir)


def run_inputs(env: Env, **kw) -> ev.RunInputs:
    return ev.RunInputs(HARNESS, env.freeze_sha, env.model, env.model_sha, env.model_dir,
                        env.store_hashes, env.inputs.hashes, env.base / "result.json",
                        freeze_path=env.freeze, marker_path=env.base / "RUN_ONCE.json",
                        registry_path=env.registry, hist_root=env.hist_root, **kw)


def loader(seed: int, plants=(), reads: list | None = None):
    def load(root, *, expected_sha256, calendar):
        assert calendar.group == {"NG": "energy", "NQ": "equity", "ZN": "rates", "6E": "fx",
                                  "GC": "metals", "ZC": "grains"}[root]
        if reads is not None:
            reads.append(root)
        key = (seed, json.dumps(plants, sort_keys=True), root)
        if key not in _LEGS:
            _LEGS[key] = synthetic_leg(root, FIRST, LAST_BARS, seed=seed, plants=plants)
        return _LEGS[key]

    return load


def _run(env: Env, *, seed=3, plants=(), reads=None, **kw):
    return ev.run(run_inputs(env, **kw), preflight=lambda s: s,
                  leg_loader=loader(seed, plants, reads), log=lambda _m: None)


# ------------------------------------------------------------------ end to end ----
def test_planted_edge_passes_and_writes_the_verdict_first(tmp_path):
    env = make_env(tmp_path)
    out = _run(env, plants=EDGE)
    assert out["verdict"] == ev.PASS
    t1 = out["tests"]["C1-T1"]
    assert t1["decision"] == ev.PASS and t1["n_trades"] >= 30
    assert t1["mean_gross_ticks"] >= 1.5 * t1["cost_ticks"] and t1["p_one_sided"] <= 0.025
    keys = list(json.loads((tmp_path / "result.json").read_text()))
    assert keys[:4] == ["schema", "test", "test_ids", "verdict"]
    assert keys.index("tests") < keys.index("descriptive")
    d = out["descriptive"]["C1-T1"]["c15"]
    assert d["long"]["n"] + d["short"]["n"] == t1["n_trades"]
    assert sum(d["trades_per_year"].values()) == t1["n_trades"]
    assert 0 < d["share_of_rows_at_or_above_q"] <= 1
    assert out["inputs"]["c12"]["share"] == 0.0 and len(out["trades_sha256"]) == 64
    assert (tmp_path / "RUN_ONCE.json").is_file()


def test_noise_fails(tmp_path):
    env = make_env(tmp_path)
    out = _run(env, seed=5)
    assert out["verdict"] == ev.FAIL
    assert all(out["tests"][t]["decision"] == ev.FAIL for t in ("C1-T1", "C1-T2"))


def test_a_second_run_is_refused_and_writes_nothing(tmp_path):
    env = make_env(tmp_path)
    _run(env)
    before = (tmp_path / "result.json").read_bytes()
    with pytest.raises(C1Refused, match="runs once"):
        _run(env)
    (tmp_path / "result.json").unlink()
    with pytest.raises(C1Refused, match="runs once"):  # the marker alone refuses
        _run(env)
    assert not (tmp_path / "result.json").exists() and before


def test_marker_is_written_before_any_bar_is_read(tmp_path):
    env = make_env(tmp_path)
    seen = []

    def load(root, *, expected_sha256, calendar):
        seen.append((root, (tmp_path / "RUN_ONCE.json").is_file()))
        return loader(3)(root, expected_sha256=expected_sha256, calendar=calendar)

    ev.run(run_inputs(env), preflight=lambda s: s, leg_loader=load, log=lambda _m: None)
    assert [r for r, _ in seen] == list(STORE_ROOTS) and all(m for _, m in seen)


# ------------------------------------------------------------------ refusals ----
def _refused(env: Env, match: str, **kw) -> None:
    reads: list = []
    with pytest.raises(C1Refused, match=match):
        _run(env, reads=reads, **kw)
    assert not reads
    assert not (env.base / "RUN_ONCE.json").exists() and not (env.base / "result.json").exists()


def test_registry_refusals(tmp_path):
    _refused(make_env(tmp_path / "a", register=False), "not registered")
    env = make_env(tmp_path / "b")
    other = env.base / "other_freeze.md"
    other.write_text("another freeze\n")
    reg2 = env.base / "reg2.jsonl"
    trial_registry.init_registry(reg2)
    trial_registry.register("C1", ["C1-T1", "C1-T2"], other, sha(other), HARNESS, path=reg2)
    _refused(dataclasses.replace(env, registry=reg2), "freeze sha256")


def test_freeze_model_payload_and_store_refusals(tmp_path):
    env = make_env(tmp_path)
    _refused(dataclasses.replace(env, freeze_sha="0" * 64), "freeze")
    _refused(dataclasses.replace(env, model_sha="0" * 64), "model JSON")
    payload = env.model_dir / "c1_m1_h60.ridge"
    keep = payload.read_bytes()
    payload.write_bytes(keep + b"x")
    _refused(env, "M1 h60 payload")
    payload.write_bytes(keep)
    store = hist_parquet_path("ZC", "ext2010", env.hist_root)
    store.write_bytes(b"changed")
    _refused(env, "store")


def test_v2_freeze_and_harness_refusals(tmp_path):
    env = make_env(tmp_path)
    _refused(env, "v2 freeze", v2_freeze=(ev.V2_FREEZE_MANIFEST, "0" * 64))

    def boom(_sha):
        raise C1Refused("harness preflight refused")

    reads: list = []
    with pytest.raises(C1Refused, match="harness"):
        ev.run(run_inputs(env), preflight=boom, leg_loader=loader(3, (), reads),
               log=lambda _m: None)
    assert not reads and not (env.base / "RUN_ONCE.json").exists()


def test_feature_cols_other_than_the_signals_give_are_refused_before_the_marker(tmp_path):
    env = make_env(tmp_path, cols=(*COLS[1:], COLS[0]))
    _refused(env, "C11")


def test_c12_share_above_two_percent_is_refused(tmp_path):
    days = [d for d in (date(2012, 1, 2) + __import__("datetime").timedelta(days=i)
                        for i in range(120)) if d.weekday() < 5][:60]
    cal = calendar_payload("energy",
                           unsourced=[(d.isoformat(), "SYNTHETIC unsourced") for d in days])
    env = make_env(tmp_path, calendars={"energy": cal})
    _refused(env, "C12 STOP")


def test_a_day_session_other_than_d6_is_refused(tmp_path):
    cal = calendar_payload("energy")
    cal["sessions"][0]["day_session_ct"] = {"*": ["09:00", "13:30"]}
    env = make_env(tmp_path, calendars={"energy": cal})
    _refused(env, "D6")


# ------------------------------------------------------------------ guards after the marker ----
def test_c10_stop_closes_the_attempt(tmp_path):
    env = make_env(tmp_path, ref=c10_ref({"k1_vwap_dist": 12}))
    out = _run(env)
    assert out["verdict"] == ev.STOPPED and out["stop_reason"].startswith("C10")
    assert "k1_vwap_dist" in out["stop_reason"]
    assert out["guards"]["C10"]["h60"]["applicable"]["k1_vwap_dist"] == 0
    assert out["guards"]["C10"]["h60"]["applicable"]["g17_nq"] > 0
    assert "tests" not in out
    with pytest.raises(C1Refused, match="runs once"):
        _run(env)


def test_c11_stop_after_the_marker(tmp_path, monkeypatch):
    import c1_replication.world as world

    real = world.replication_panel

    def shuffled(w, signals):
        p = real(w, signals)
        return dataclasses.replace(p, feature_cols=tuple(reversed(p.feature_cols)))

    monkeypatch.setattr(world, "replication_panel", shuffled)
    out = _run(make_env(tmp_path))
    assert out["verdict"] == ev.STOPPED and out["stop_reason"].startswith("C11")


def test_any_error_after_the_marker_is_a_stopped_verdict(tmp_path):
    env = make_env(tmp_path)

    def broken(root, *, expected_sha256, calendar):
        raise RuntimeError("store refused (synthetic)")

    out = ev.run(run_inputs(env), preflight=lambda s: s, leg_loader=broken, log=lambda _m: None)
    assert out["verdict"] == ev.STOPPED and "store refused" in out["stop_reason"]
    assert (env.base / "result.json").is_file()


def test_c12_excluded_dates_have_no_ng_row(tmp_path, monkeypatch):
    excluded = date(2011, 6, 15)
    cal = calendar_payload("energy", unsourced=[(excluded.isoformat(), "SYNTHETIC")])
    env = make_env(tmp_path, calendars={"energy": cal})
    import c1_replication.world as world

    seen = {}
    real = world.replication_panel

    def spy(w, signals):
        p = real(w, signals)
        seen["days"] = set(p.frame["trade_date"].dt.date)
        seen["excluded"] = set(w.excluded)
        return p

    monkeypatch.setattr(world, "replication_panel", spy)
    out = _run(env)
    assert out["verdict"] in (ev.PASS, ev.FAIL)
    assert excluded in seen["excluded"] and date(2011, 6, 16) in seen["excluded"]  # prior gap
    assert not ({excluded, date(2011, 6, 16)} & seen["days"]) and seen["days"]
    assert out["inputs"]["c12"]["excluded"] == 2


def test_cli_refuses_with_exit_2_and_writes_nothing(tmp_path, monkeypatch, capsys):
    env = make_env(tmp_path, register=False)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    marker = ev.MARKER_PATH
    existed = marker.exists()
    args = ["--harness-sha256", HARNESS, "--freeze", str(env.freeze), "--freeze-sha256",
            env.freeze_sha, "--model", str(env.model), "--model-sha256", env.model_sha,
            "--model-dir", str(env.model_dir), "--store-hashes", str(env.store_hashes),
            "--calendar-hashes", str(env.inputs.hashes), "--out", str(tmp_path / "cli.json")]
    # the real registry holds no C1 registration under this synthetic freeze
    assert ev.main(args, preflight=lambda s: s) == ev.RC_REFUSED
    assert "REFUSED, nothing written" in capsys.readouterr().err
    assert not (tmp_path / "cli.json").exists() and marker.exists() == existed


# ------------------------------------------------------------------ the pass bar ----
@pytest.mark.parametrize(("mean", "cost", "p", "n", "ok"), [
    (3.0, 2.0, 0.025, 30, True),  # every bound inclusive
    (2.9999999, 2.0, 0.01, 100, False),  # below 1.5 c
    (5.0, 2.0, 0.0250001, 100, False),  # p above 0.025
    (5.0, 2.0, 0.01, 29, False),  # fewer than 30 trades
    (float("nan"), 2.0, 0.01, 100, False),
    (5.0, 2.0, float("nan"), 100, False),
])
def test_pass_bar_boundaries(mean, cost, p, n, ok):
    assert ev.passes(mean, cost, p, n) is ok


def test_replication_passes_iff_one_test_passes():
    blocks = {"C1-T1": {"decision": ev.FAIL}, "C1-T2": {"decision": ev.PASS}}
    assert ev.verdict_of(blocks)["verdict"] == ev.PASS
    blocks["C1-T2"]["decision"] = ev.FAIL
    assert ev.verdict_of(blocks)["verdict"] == ev.FAIL


def test_expected_feature_cols_equal_the_frozen_panel_rule(tmp_path):
    from c1_replication.context import hist_tables
    from c1_replication.evaluate import load_calendars
    from c1_replication.exclusions import c12_exclusions
    from c1_replication.world import build_world, replication_panel

    vol_ticks_table()
    inp = write_inputs(tmp_path)
    cal = load_calendars(inp.hashes, FIRST, date(2019, 4, 30))
    c12 = c12_exclusions(cal["calendars"], ())
    with hist_tables(cal["tables"]):
        w = build_world(lambda r: loader(3)(r, expected_sha256="", calendar=cal["calendars"][
            {"NG": "energy", "NQ": "equity", "ZN": "rates", "6E": "fx", "GC": "metals",
             "ZC": "grains"}[r]]), cal["releases"].calendar, c12.excluded_dates())
        panel = replication_panel(w, SIGNALS)
    assert tuple(panel.feature_cols) == COLS
    assert set(panel.frame["root"]) == {"NG"}
