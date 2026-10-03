"""ml_route_v2.configs: the 45-configuration grid, the V2.9 tie-break and the ledger."""

from __future__ import annotations

import json

import pytest

from ml_route_v2.configs import (
    CONFIGS,
    CONFIGS_BY_ID,
    ConfigLedger,
    LedgerError,
    register_configs,
    tie_break_key,
)
from ml_route_v2.constants import COST_GATE_KS, HORIZONS, N_CONFIGURATIONS, N_PROGRAM_AT_DRAFT


def test_grid_has_45_unique_configs_in_documented_order():
    assert len(CONFIGS) == N_CONFIGURATIONS == 45
    assert len({c.config_id for c in CONFIGS}) == 45
    assert CONFIGS[0].config_id == "ridge_l0.01_k1.5_h60"
    assert CONFIGS[1].config_id == "ridge_l0.01_k1.5_h120"
    assert CONFIGS[3].config_id == "ridge_l0.01_k2_h60"
    assert CONFIGS[9].config_id == "ridge_l0.1_k1.5_h60"
    assert CONFIGS[27].config_id == "lgbm_d2_k1.5_h60"
    assert CONFIGS[44].config_id == "lgbm_d3_k3_hF"
    assert {c.horizon for c in CONFIGS} == set(HORIZONS)
    assert {c.k for c in CONFIGS} == set(COST_GATE_KS)
    assert CONFIGS_BY_ID["lgbm_d2_k2_h120"].model.param == 2.0


def test_tie_break_prefers_ridge_then_larger_lambda_then_smaller_depth():
    key = lambda cid: tie_break_key(CONFIGS_BY_ID[cid])  # noqa: E731
    assert key("ridge_l0.01_k1.5_hF") < key("lgbm_d2_k3_h60")
    assert key("ridge_l1_k1.5_h60") < key("ridge_l0.1_k3_h60") < key("ridge_l0.01_k3_h60")
    assert key("lgbm_d2_k1.5_h60") < key("lgbm_d3_k3_h60")


def test_tie_break_then_larger_k_then_shorter_horizon():
    key = lambda cid: tie_break_key(CONFIGS_BY_ID[cid])  # noqa: E731
    assert key("ridge_l1_k3_hF") < key("ridge_l1_k2_h60") < key("ridge_l1_k1.5_h60")
    assert key("ridge_l1_k3_h60") < key("ridge_l1_k3_h120") < key("ridge_l1_k3_hF")
    ordered = sorted(CONFIGS, key=tie_break_key)
    assert ordered[0].config_id == "ridge_l1_k3_h60"
    assert ordered[-1].config_id == "lgbm_d3_k1.5_hF"
    assert len({tie_break_key(c) for c in CONFIGS}) == 45


def test_ledger_registers_once_and_counts(tmp_path):
    ledger = ConfigLedger(tmp_path / "ledger.jsonl")
    register_configs(ledger, CONFIGS)
    register_configs(ledger, CONFIGS)  # resumability: same spec is a no-op
    ledger.register("gate0A_s0_h60", "gate0_A", {"signal": "s0", "horizon": "h60"})
    ledger.register("gate0B_AA_h60", "gate0_B", {"root": "AA", "horizon": "h60"})
    assert ledger.n_registered() == 47
    assert ledger.n_registered("config") == 45
    assert ledger.n_registered("gate0_A") == 1
    assert ledger.n_total() == N_PROGRAM_AT_DRAFT + 47
    assert ledger.n_total(10) == 57
    lines = (tmp_path / "ledger.jsonl").read_text().splitlines()
    assert len(lines) == 47
    rec = json.loads(lines[0])
    assert set(rec) == {"entry_id", "kind", "spec", "time"}
    assert rec["entry_id"] == "ridge_l0.01_k1.5_h60" and rec["kind"] == "config"


def test_ledger_reloads_and_rejects_a_changed_spec(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ConfigLedger(path).register("x", "config", {"a": 1, "b": (1, 2)})
    again = ConfigLedger(path)
    assert again.n_registered() == 1
    again.register("x", "config", {"b": [1, 2], "a": 1})  # same canonical spec
    with pytest.raises(LedgerError, match="another spec"):
        again.register("x", "config", {"a": 2})
    with pytest.raises(LedgerError, match="another spec"):
        again.register("x", "gate0_A", {"a": 1, "b": [1, 2]})
    assert len(path.read_text().splitlines()) == 1


def test_ledger_rejects_bad_kind_bad_line_and_reports_missing(tmp_path):
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    with pytest.raises(LedgerError, match="kind"):
        ledger.register("x", "other", {})
    with pytest.raises(LedgerError, match="computation before registration"):
        ledger.require(["never"])
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n")
    with pytest.raises(LedgerError, match="unreadable"):
        ConfigLedger(bad)
