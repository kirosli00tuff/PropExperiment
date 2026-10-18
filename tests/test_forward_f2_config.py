"""E22-F2 config and tables (F2BookCoder, E.24): frozen blocks copied from config_f1.json."""

import json
from pathlib import Path

import numpy as np

from forward import core

ROOT = Path(__file__).resolve().parents[1]
F1 = json.loads((ROOT / "forward/config_f1.json").read_text())
F2 = json.loads((ROOT / "forward/config_f2.json").read_text())
T2 = json.loads((ROOT / "forward/tables_f2.json").read_text())
ETFS = ["QQQ", "IWM", "GLD", "USO", "UNG", "FXE", "SHY", "IEF", "TLT", "CORN", "SOYB"]
MICROS = ["MNQ", "M2K", "MGC", "MCL", "MNG", "M6E", "2YY", "10Y", "30Y", "MZC", "MZS"]


def test_identity_and_constants():
    assert F2["schema"] == "stage_e24_f2_config/1"
    assert F2["test_id"] == "E22-F2"
    assert F2["source"]["path"] == "forward/config_f1.json"
    assert F2["capital_usd"]["value"] == 25000.0
    assert F2["leverage_cap_usd"]["value"] == 50000.0
    assert (
        F2["leverage_cap_usd"]["value"]
        == F2["reg_t_multiplier"]["value"] * F2["capital_usd"]["value"]
    )
    assert F2["costs"]["sec_fee_rate"]["value"] == 0.0000206
    assert F2["costs"]["finra_taf_per_share"]["value"] == 0.0
    assert F2["costs"]["cat_fee_per_share"]["value"] == 0.000003
    assert F2["financing"]["borrow_fee_b"]["value"] == 0.01
    assert F2["financing"]["margin_spread_s"]["value"] == 0.025
    assert F2["cash_symbol"]["value"] == "BIL"
    assert F2["instruments_order"] == ETFS
    for s, m in zip(ETFS, MICROS, strict=True):
        spec = F2["instruments"][s]
        assert spec["multiplier"] == 1.0 and spec["yield_quoted"] is False
        assert spec["e22_f1_micro"] == m


def test_rule_blocks_are_config_f1_verbatim():
    for key in F2["source"]["copied_verbatim"]:
        assert F2[key] == F1[key], key
    assert set(F2["source"]["copied_verbatim"]) >= {
        "ewmac",
        "forecast_cap",
        "average_abs_forecast",
        "vol",
        "vol_target",
        "fdm",
        "warmup_diffs",
        "simple_rounding",
    }


def test_idm_block_is_f1_submatrix_and_recomputes():
    order = F1["idm"]["instruments"]
    idx = [order.index(m) for m in MICROS]
    sub = [[F1["idm"]["correlation"][i][j] for j in idx] for i in idx]
    assert F2["idm"]["correlation"] == sub
    assert F2["idm"]["instruments"] == ETFS and F2["idm"]["e22_f1_instruments"] == MICROS
    idm = core.idm_for_live(
        np.asarray(F2["idm"]["correlation"]), np.ones(11, bool), F2["idm"]["dm_max"]["value"]
    )
    assert idm == 2.3293791420997985 == F2["idm"]["value"]


def test_tables_pinned_to_config():
    assert set(T2["half_spread_usd"]) == set(ETFS)
    for s in ETFS:
        assert T2["half_spread_usd"][s] == F2["instruments"][s]["half_spread_usd"]
    assert {s for s in ETFS if T2["half_spread_usd"][s] == 0.03} == {"FXE", "CORN", "SOYB"}
    assert {s for s in ETFS if T2["half_spread_usd"][s] == 0.01} == set(ETFS) - {
        "FXE",
        "CORN",
        "SOYB",
    }


def test_no_pending_values_remain():
    text = (ROOT / "forward/config_f2.json").read_text() + (
        ROOT / "forward/tables_f2.json"
    ).read_text()
    assert "PENDING" not in text
