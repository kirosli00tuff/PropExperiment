"""ml_route_v2.decide: the cost gate (V2.7; the gross reading is the default, V23 item 1, and the
literal F7 "net" reading stays selectable) and the section 6 candidates."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.constants as v2c
from ml_route_v2.configs import CONFIGS_BY_ID
from ml_route_v2.decide import CANDIDATE_COLUMNS, DecisionError, candidates, cost_gate


def test_cost_gate_boundaries_hand_computed_k_1_5_net_reading():
    # c = 1 tick, k = 1.5, net: long iff r - 1 > 1.5, i.e. r > 2.5; short iff r < -2.5.
    r = np.array([2.5, 2.5001, 3.0, -2.5, -2.6, 0.0, -10.0])
    side, ratio = cost_gate(r, np.ones(7), np.ones(7), 1.5, reading="net")
    assert side.dtype == np.int8
    assert side.tolist() == [0, 1, 1, 0, -1, 0, -1]
    np.testing.assert_allclose(ratio[[1, 2, 4, 6]], [1.5001, 2.0, 1.6, 9.0])
    assert np.isnan(ratio[[0, 3, 5]]).all()


def test_cost_gate_boundaries_hand_computed_k_1_5_gross_default():
    # c = 1 tick, k = 1.5, gross (the default, V23 item 1): long iff r > 1.5; short iff r < -1.5.
    r = np.array([1.5, 1.5001, 3.0, -1.5, -1.6, 0.0, -10.0])
    side, ratio = cost_gate(r, np.ones(7), np.ones(7), 1.5)
    assert side.dtype == np.int8
    assert side.tolist() == [0, 1, 1, 0, -1, 0, -1]
    np.testing.assert_allclose(ratio[[1, 2, 4, 6]], [0.5001, 2.0, 0.6, 9.0])
    assert np.isnan(ratio[[0, 3, 5]]).all()


def test_cost_gate_uses_each_sides_own_cost_net_reading():
    # c_long = 1, c_short = 2, k = 2, net: long iff r > 3; short iff -r - 2 > 4, i.e. r < -6.
    r = np.array([3.0, 3.01, -5.0, -6.0, -6.5])
    side, ratio = cost_gate(r, np.full(5, 1.0), np.full(5, 2.0), 2.0, reading="net")
    assert side.tolist() == [0, 1, 0, 0, -1]
    np.testing.assert_allclose(ratio[[1, 4]], [(3.01 - 1) / 1, (6.5 - 2) / 2])


def test_cost_gate_uses_each_sides_own_cost_gross_default():
    # c_long = 1, c_short = 2, k = 2, gross: long iff r > 2; short iff -r > 4, i.e. r < -4.
    r = np.array([2.0, 2.01, -4.0, -4.01, -3.0])
    side, ratio = cost_gate(r, np.full(5, 1.0), np.full(5, 2.0), 2.0)
    assert side.tolist() == [0, 1, 0, -1, 0]
    np.testing.assert_allclose(ratio[[1, 3]], [(2.01 - 1) / 1, (4.01 - 2) / 2])


def test_cost_gate_k_3_needs_gross_above_four_costs_net_reading():
    side, _ = cost_gate(np.array([2.0, 2.02, -2.02]), np.full(3, 0.5), np.full(3, 0.5), 3.0,
                        reading="net")
    assert side.tolist() == [0, 1, -1]


def test_cost_gate_k_3_needs_gross_above_three_costs_gross_default():
    side, _ = cost_gate(np.array([1.5, 1.52, -1.52, 2.0]), np.full(4, 0.5), np.full(4, 0.5), 3.0)
    assert side.tolist() == [0, 1, -1, 1]


def test_cost_gate_rejects_bad_inputs():
    with pytest.raises(DecisionError, match="not positive"):
        cost_gate(np.array([1.0]), np.array([0.0]), np.array([1.0]), 1.5)
    with pytest.raises(DecisionError, match="non-finite"):
        cost_gate(np.array([np.nan]), np.array([1.0]), np.array([1.0]), 1.5)
    with pytest.raises(DecisionError, match="expected"):
        cost_gate(np.array([1.0, 2.0]), np.array([1.0]), np.array([1.0]), 1.5)


def _rows():
    return pd.DataFrame({
        "root": ["ZB", "AA", "CC", "DD"],
        "cluster": ["K2", "K1", "K3", "K4"],
        "trade_date": pd.to_datetime(["2020-01-06"] * 4),
        "decision_ts_ns": np.array([200, 100, 100, 100], dtype=np.int64),
        "flatten_ts_ns": np.array([900, 900, 900, 900], dtype=np.int64),
        "cost_long_h60": [1.0, 1.0, 1.0, 1.0],
        "cost_short_h60": [2.0, 2.0, 2.0, 2.0],
        "exit_ts_ns_h60": [260.0, 160.0, np.nan, 160.0],
        "release_window": [False, True, False, False],  # V23 item 11, from targets.py
    })


def test_candidates_section6_columns_order_and_values():
    cfg = CONFIGS_BY_ID["ridge_l0.1_k1.5_h60"]
    out = candidates(_rows(), np.array([5.0, 3.0, -8.0, 0.1]), cfg)
    assert tuple(out.columns) == CANDIDATE_COLUMNS
    # DD does not trade; at ts 100 CC (edge (8-2)/2 = 3) ranks before AA ((3-1)/1 = 2); ZB at 200.
    assert out["root"].tolist() == ["CC", "AA", "ZB"]
    assert out["side"].tolist() == [-1, 1, 1] and out["side"].dtype == np.int8
    assert out["cost_ticks"].tolist() == [2.0, 1.0, 1.0]
    np.testing.assert_allclose(out["edge_over_cost"], [3.0, 2.0, 4.0])
    assert out["exit_ts_ns"].tolist() == [900, 160, 260]  # CC's missing exit -> flatten
    assert (out["horizon"] == "h60").all()
    assert out["release_window"].tolist() == [False, True, False]  # each row's own flag
    assert out["release_window"].dtype == bool


def test_candidates_need_a_boolean_release_window_column():
    cfg = CONFIGS_BY_ID["ridge_l0.1_k1.5_h60"]
    with pytest.raises(DecisionError, match="release_window"):
        candidates(_rows().drop(columns="release_window"), np.zeros(4), cfg)
    with pytest.raises(DecisionError, match="not bool"):
        candidates(_rows().assign(release_window=[0.0, 1.0, np.nan, 0.0]), np.zeros(4), cfg)


def test_candidates_ties_go_to_root_alphabetical_and_empty_is_typed():
    rows = _rows().assign(decision_ts_ns=np.int64(100))
    cfg = CONFIGS_BY_ID["ridge_l0.1_k1.5_h60"]
    out = candidates(rows, np.array([3.0, 3.0, 3.0, 3.0]), cfg)
    assert out["root"].tolist() == ["AA", "CC", "DD", "ZB"]
    empty = candidates(rows, np.zeros(4), cfg)
    assert len(empty) == 0 and tuple(empty.columns) == CANDIDATE_COLUMNS


# ---- design review D-05: the cost-gate reading switch -------------------------------------------
def test_the_default_reading_is_the_decided_gross_one() -> None:
    assert v2c.COST_GATE_READING == "gross"  # V23 item 1
    r = np.array([4.0, -4.0])
    default = cost_gate(r, np.full(2, 2.0), np.full(2, 2.0), 1.5)
    gross = cost_gate(r, np.full(2, 2.0), np.full(2, 2.0), 1.5, reading="gross")
    net = cost_gate(r, np.full(2, 2.0), np.full(2, 2.0), 1.5, reading="net")
    assert default[0].tolist() == gross[0].tolist() == [1, -1]  # 4 > 1.5 x 2 = 3
    assert net[0].tolist() == [0, 0]  # 4 - 2 = 2 is not > 3


@pytest.mark.parametrize("k", [1.5, 2.0, 3.0])
def test_net_reading_boundaries(k: float) -> None:
    # c = 2 (exact in binary): long iff r - 2 > 2k, i.e. r > 2 (1 + k); short iff r < -2 (1 + k)
    edge = 2.0 * (1.0 + k)
    r = np.array([edge, edge + 1e-9, -edge, -edge - 1e-9, 2.0 * k + 0.5])
    side, ratio = cost_gate(r, np.full(5, 2.0), np.full(5, 2.0), k, reading="net")
    assert side.tolist() == [0, 1, 0, -1, 0]  # a gross just over k c is not enough here
    np.testing.assert_allclose(ratio[[1, 3]], [(edge + 1e-9 - 2.0) / 2.0] * 2)


@pytest.mark.parametrize("k", [1.5, 2.0, 3.0])
def test_gross_reading_boundaries(k: float) -> None:
    # c = 2: long iff r > 2k; short iff -r > 2k (no cost subtracted before the comparison)
    edge = 2.0 * k
    r = np.array([edge, edge + 1e-9, -edge, -edge - 1e-9, 2.0 * (1.0 + k) - 0.5])
    side, ratio = cost_gate(r, np.full(5, 2.0), np.full(5, 2.0), k, reading="gross")
    assert side.tolist() == [0, 1, 0, -1, 1]
    # the ranking quantity stays the predicted net edge over cost, (|r| - c) / c
    np.testing.assert_allclose(ratio[[1, 3, 4]], [(edge + 1e-9 - 2.0) / 2.0,
                                                  (edge + 1e-9 - 2.0) / 2.0,
                                                  (2.0 * (1.0 + k) - 0.5 - 2.0) / 2.0])


def test_the_constant_flips_the_default_in_one_line(monkeypatch: pytest.MonkeyPatch) -> None:
    r = np.array([3.5, -3.5])  # c = 2, k = 1.5: gross 3.5 > 3 passes; net 1.5 > 3 does not
    assert cost_gate(r, np.full(2, 2.0), np.full(2, 2.0), 1.5)[0].tolist() == [1, -1]
    rows = _rows()
    cfg = CONFIGS_BY_ID["ridge_l0.1_k1.5_h60"]
    r_hat = np.full(len(rows), 2.0)  # c_long 1: gross 2 > 1.5 passes; net 2 - 1 > 1.5 does not
    assert len(candidates(rows, r_hat, cfg)) == 4  # the default reads "gross"
    monkeypatch.setattr(v2c, "COST_GATE_READING", "net")
    assert cost_gate(r, np.full(2, 2.0), np.full(2, 2.0), 1.5)[0].tolist() == [0, 0]
    assert len(candidates(rows, r_hat, cfg)) == 0  # the flipped default reads "net"
    assert len(candidates(rows, r_hat, cfg, reading="gross")) == 4


def test_an_unknown_reading_raises() -> None:
    with pytest.raises(DecisionError, match="reading"):
        cost_gate(np.array([1.0]), np.array([1.0]), np.array([1.0]), 1.5, reading="mid")


def test_a_minus_one_exit_is_missing_and_takes_the_flatten() -> None:
    """Code review C-06: targets.py encodes a missing exit as -1 (int64); it is treated like NaN
    (the flatten), and real int64 nanosecond exits pass through without float rounding."""
    t0 = 1_577_977_200 * 1_000_000_000 + 123  # a nanosecond count float64 cannot hold exactly
    rows = _rows().assign(decision_ts_ns=np.int64(t0),
                          flatten_ts_ns=np.int64(t0 + 7_000_000_000_001),
                          exit_ts_ns_h60=np.array([t0 + 60_000_000_001, -1, 0, t0 + 1],
                                                  dtype=np.int64))
    cfg = CONFIGS_BY_ID["ridge_l0.1_k1.5_h60"]
    out = candidates(rows, np.array([5.0, 5.0, 5.0, 5.0]), cfg)
    by_root = dict(zip(out["root"], out["exit_ts_ns"], strict=True))
    assert by_root == {"ZB": t0 + 60_000_000_001, "AA": t0 + 7_000_000_000_001,
                       "CC": t0 + 7_000_000_000_001, "DD": t0 + 1}
    assert out["exit_ts_ns"].dtype == np.int64
