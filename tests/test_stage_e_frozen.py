"""Stage E frozen inputs (screening/stage_e_frozen.py): the E.2a tables are read only when their
sha256 equals the recorded value; costs, ticks, q_c and eps come from them (known answers)."""

from __future__ import annotations

import shutil
from datetime import UTC, date, datetime, time
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from data.config import REPO_ROOT
from screening.stage_e_frozen import (
    E2A_TABLES,
    FrozenInputError,
    build_tables,
    leg_inputs,
    load_frozen_tables,
    slippage_cents,
)

CT = ZoneInfo("America/Chicago")


def _at(hh: int, mm: int) -> datetime:
    return datetime.combine(date(2025, 6, 4), time(hh, mm), tzinfo=CT).astimezone(UTC)


def test_the_recorded_hashes_are_the_e2a_return_values() -> None:
    assert E2A_TABLES["costs"][1].startswith("f4360bb7") and E2A_TABLES["costs"][1].endswith(
        "96df14")
    assert E2A_TABLES["sizes"][1].startswith("280d7e9d")
    assert E2A_TABLES["vehicles"][1].startswith("1f1cafee")
    assert E2A_TABLES["epsilon"][1].startswith("4e2c7731")
    assert dict(load_frozen_tables().hashes) == {k: v[1] for k, v in E2A_TABLES.items()}


def test_a_one_byte_change_to_any_frozen_table_is_refused(tmp_path: Path) -> None:
    for rel, _sha in E2A_TABLES.values():
        for orel, _ in E2A_TABLES.values():
            (tmp_path / orel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / orel, tmp_path / orel)
        data = bytearray((tmp_path / rel).read_bytes())
        data[-2] = data[-2] ^ 1
        (tmp_path / rel).write_bytes(bytes(data))
        with pytest.raises(FrozenInputError, match="not the recorded"):
            build_tables(tmp_path)


def test_a_missing_frozen_table_is_refused(tmp_path: Path) -> None:
    with pytest.raises(FrozenInputError, match="is missing"):
        build_tables(tmp_path)


def test_vehicles_q_c_and_operative_eps_match_the_e2a_return() -> None:
    expect = {"MNQ": (1, 170), "M2K": (3, 50), "MYM": (3, 56), "ZN": (1, 3), "ZB": (1, 2),
              "MCL": (4, 21), "NG": (1, 8), "MGC": (1, 71), "MHG": (2, 27), "6E": (1, 12),
              "ZC": (1, 4), "LE": (1, 8), "MBT": (1, 90), "ZT": (1, 5)}
    for root, (q, eps) in expect.items():
        leg = leg_inputs(root, traded=True)
        assert (leg.vehicle.q_c, leg.eps_ticks) == (q, eps), root
    assert len(load_frozen_tables().vehicles) == 28


def test_a_non_vehicle_can_only_be_a_signal_leg() -> None:
    for root in ("MES", "NQ", "CL", "SI", "M6E"):
        with pytest.raises(FrozenInputError, match="signal leg"):
            leg_inputs(root, traded=True)
        assert leg_inputs(root, traded=False).costs is None
    assert leg_inputs("MES", traded=False).research_parquet_sha256.startswith("aea959a5")


def test_tick_values_are_exact_cents_including_the_fractional_ones() -> None:
    assert leg_inputs("ZN", traded=True).tick_value_cents == Fraction(3125, 2)
    assert leg_inputs("ZT", traded=True).tick_value_cents == Fraction(3125, 4)
    assert leg_inputs("MNQ", traded=True).tick_value_cents == 50
    assert leg_inputs("ZC", traded=True).tick_value_cents == 1250
    assert leg_inputs("ZC", traded=True).product.vendor_tick == 100 * leg_inputs(
        "ZC", traded=True).product.tick_size  # vendor cents


def test_commission_is_half_the_round_turn_per_side() -> None:
    assert leg_inputs("MCL", traded=True).costs.commission_side_cents == 86  # $1.72 RT (F3.6)
    assert leg_inputs("ZC", traded=True).costs.commission_side_cents == 264
    assert leg_inputs("MNQ", traded=True).costs.commission_side_cents == 61


def test_event_window_cost_is_the_largest_half_spread_plus_the_own_bucket_depth_T12_4() -> None:
    costs = leg_inputs("MCL", traded=True).costs
    bucket = costs.bucket_at(_at(9, 45))
    assert costs.max_half_spread_ticks == max(b.half_spread_ticks for b in costs.buckets)
    event = costs.side_slippage_ticks(_at(9, 45), "buy", True)
    assert event == costs.max_half_spread_ticks + bucket.depth_ticks["buy"]
    table_field = max(b.half_spread_ticks + b.depth_ticks["buy"] for b in costs.buckets)
    assert costs.side_slippage_ticks(_at(9, 45), "buy", False) == bucket.side_ticks["buy"]
    # MCL's table field is max(s_b + depth); the literal reading differs where depth varies
    assert event <= table_field + 1e-12


def test_a_fill_time_with_no_calibrated_bucket_raises_never_a_guess() -> None:
    costs = leg_inputs("ZC", traded=True).costs
    with pytest.raises(FrozenInputError, match="no calibrated bucket"):
        costs.side_slippage_ticks(_at(8, 0), "buy", False)  # the grain pause


def test_slippage_is_ceiled_to_the_cent_as_the_mes_engine() -> None:
    assert slippage_cents(1, 0.5010625313606667, Fraction(3125, 2)) == 783
    assert slippage_cents(4, 1.3132355052574765, 100) == 526
    assert slippage_cents(1, 0.5, Fraction(3125, 2)) == 782  # 781.25 -> 782
