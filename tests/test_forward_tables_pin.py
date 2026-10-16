"""Pin forward/tables_f1.json to forward/config_f1.json (review finding S7)."""

import json
from pathlib import Path

from forward.runner import load_tables

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "forward" / "config_f1.json"
TABLES_PATH = ROOT / "forward" / "tables_f1.json"


def _config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def test_tables_instrument_keys_match_config_order() -> None:
    cfg = _config()
    multipliers, costs = load_tables(TABLES_PATH)
    assert list(multipliers) == list(cfg["instruments_order"])
    assert list(costs) == list(cfg["instruments_order"])


def test_tables_multipliers_equal_config() -> None:
    cfg = _config()
    multipliers, _ = load_tables(TABLES_PATH)
    for code in cfg["instruments_order"]:
        assert multipliers[code] == cfg["instruments"][code]["multiplier"], code


def test_tables_cost_per_side_equal_config() -> None:
    cfg = _config()
    _, costs = load_tables(TABLES_PATH)
    for code in cfg["instruments_order"]:
        assert costs[code] == cfg["instruments"][code]["cost_per_side_usd"], code
