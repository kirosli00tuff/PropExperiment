"""Stage E.11 Task 4: portfolio caps, accept_trades, fixed_d_daily_pnl and the V2.9 selection
metric (docs/STAGE_E_ML_V2_DESIGN.md V2.8 "Caps", V2.9 "Selection metric"). Synthetic frames."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.account import ACCOUNT_50K, ACCOUNT_150K, tier_max_tenths
from ml_route_v2.constants import UNIVERSE
from ml_route_v2.portfolio import (
    PortfolioInputError,
    accept_trades,
    admission_record,
    admit,
    fixed_d_daily_pnl,
    refusal_counts,
    release_window_binds,
    release_window_mask,
    vehicle_facts,
)
from ml_route_v2.selection_metric import daily_sharpe, score_split
from rules import xfa_rules as xr
from rules.products import member_cap_contracts, product

MIN = 60_000_000_000
T0 = 1_577_977_200 * 1_000_000_000  # 2020-01-02 09:00 CT (15:00 UTC)


def cand(root: str, t: int, exit_: int, *, side: int = 1, edge: float = 1.0, cost: float = 3.0,
         horizon: str = "h60", day: str = "2020-01-02", rw: bool = False) -> dict:
    return {"root": root, "cluster": UNIVERSE[root][0], "trade_date": pd.Timestamp(day),
            "decision_ts_ns": T0 + t * MIN, "horizon": horizon, "exit_ts_ns": T0 + exit_ * MIN,
            "side": side, "r_hat_ticks": 10.0 * side, "cost_ticks": cost,
            "edge_over_cost": edge, "release_window": rw}


def risk(roots, sigma: float = 1.0, loss: float = 1.0, horizons=("h60", "h120", "hF")):
    return pd.DataFrame([{"root": r, "horizon": h, "sigma_ticks": sigma, "loss_ticks": loss,
                          "c_ticks": 3.0} for r in roots for h in horizons])


def accepted_pairs(frame: pd.DataFrame) -> list[tuple[str, int, int]]:
    return [(r.root, (r.decision_ts_ns - T0) // MIN, int(r.contracts))
            for r in frame.itertuples(index=False)]


# ---- vehicle facts and tiers ---------------------------------------------------------------
def test_vehicle_facts_come_from_rules_products() -> None:
    for root in UNIVERSE:
        f = vehicle_facts(root)
        p = product(root)
        assert f.tick_value_usd == float(p.tick_value_usd)
        assert f.lot_tenths == p.lot_weight_tenths
        assert f.product_cap == member_cap_contracts(root)
    assert (vehicle_facts("MNQ").lot_equiv, vehicle_facts("ZN").lot_equiv,
            vehicle_facts("MBT").lot_equiv) == (0.1, 1.0, 1.0)
    assert (vehicle_facts("MHG").product_cap, vehicle_facts("MCL").product_cap,
            vehicle_facts("MGC").product_cap) == (2, 10, 10)


@pytest.mark.parametrize("cents", [-50_000, 0, 149_999, 150_000, 150_001, 200_000, 200_001,
                                   900_000])
def test_tiers_agree_with_xfa_rules(cents: int) -> None:
    assert tier_max_tenths(ACCOUNT_50K, cents / 100) == xr.max_position_micros(xr.Phase.XFA, cents)


@pytest.mark.parametrize("balance,tenths", [
    (0.0, 30), (1_499.99, 30), (1_500.0, 40), (2_000.0, 40), (2_000.01, 50), (3_000.0, 50),
    (3_000.01, 100), (4_500.0, 100), (4_500.01, 150)])
def test_150k_tiers_are_topsteps_published_schedule(balance: float, tenths: int) -> None:
    """E.12 (V23 item 12; reports/stage_e12_topstep_150k.md): 3 / 4 / 5 / 10 / 15 lots, $1,500
    opening the 4-lot tier and a balance exactly on $2,000, $3,000 or $4,500 in the lower tier
    (lead ruling). Replaces the E.11 stand-in that pinned the 150K tiers to the 50K ones."""
    assert tier_max_tenths(ACCOUNT_150K, balance) == tenths


# ---- accept_trades ---------------------------------------------------------------------------
def test_ranking_at_one_decision_time_then_capacity() -> None:
    # base tier 2 lots - 0.1 = 19 tenths. MNQ (edge 3) takes 10 micros (its 1-lot cap), MGC
    # (edge 2) the 9 that remain, 6E (edge 1, a 1-lot mini) none.
    c = pd.DataFrame([cand("6E", 0, 60, edge=1.0), cand("MGC", 0, 60, edge=2.0),
                      cand("MNQ", 0, 60, edge=3.0)])
    out = accept_trades(c, risk(["6E", "MGC", "MNQ"]), ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 10), ("MGC", 0, 9)]
    assert list(out["tick_value_usd"]) == [0.5, 1.0] and list(out["lot_equiv"]) == [0.1, 0.1]


def test_equal_edges_break_by_root() -> None:
    c = pd.DataFrame([cand("MNQ", 0, 60, edge=2.0), cand("M2K", 0, 60, edge=2.0)])
    out = accept_trades(c, risk(["MNQ", "M2K"]), ACCOUNT_50K, d_fixed=2000.0)
    assert [r for r, _, _ in accepted_pairs(out)] == ["M2K"]  # same cluster K1: one only


def test_one_position_per_product_open_on_decision_to_exit() -> None:
    c = pd.DataFrame([cand("MNQ", 0, 60), cand("MNQ", 30, 90), cand("MNQ", 60, 120)])
    out = accept_trades(c, risk(["MNQ"], sigma=200.0), ACCOUNT_50K, d_fixed=2000.0)
    # sigma $100 -> 1 contract; the t=30 candidate meets the open position; t=60 is its exit
    assert accepted_pairs(out) == [("MNQ", 0, 1), ("MNQ", 60, 1)]


def test_at_most_one_position_per_cluster() -> None:
    c = pd.DataFrame([cand("MNQ", 0, 60, edge=1.0), cand("M2K", 0, 60, edge=5.0),
                      cand("MYM", 30, 90, edge=9.0), cand("MYM", 60, 120)])
    out = accept_trades(c, risk(["MNQ", "M2K", "MYM"], sigma=200.0), ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("M2K", 0, 1), ("MYM", 60, 1)]


def risk_per_root(spec: dict[str, tuple[float, float]]) -> pd.DataFrame:
    """(sigma_ticks, loss_ticks) per root, every horizon."""
    return pd.concat([risk([r], sigma=s, loss=loss) for r, (s, loss) in spec.items()],
                     ignore_index=True)


def test_at_most_three_open_positions() -> None:
    # one sigma $60 each (MNQ, MBT 120 x $0.50; MCL, MGC 60 x $1.00) -> 1 contract (115.47 / 60);
    # the daily budget never binds: 4 x 60^2 = 14,400 <= 200^2 (with sigma $200 the band trades
    # MCL and MGC would not fit what MNQ leaves of the budget, D-03)
    c = pd.DataFrame([cand("MNQ", 0, 60, edge=4.0), cand("MCL", 0, 60, edge=3.0),
                      cand("MGC", 0, 60, edge=2.0), cand("MBT", 0, 60, edge=1.0),
                      cand("MBT", 60, 120)])
    rk = risk_per_root({"MNQ": (120.0, 1.0), "MCL": (60.0, 1.0), "MGC": (60.0, 1.0),
                        "MBT": (120.0, 1.0)})
    out = accept_trades(c, rk, ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 1), ("MCL", 0, 1), ("MGC", 0, 1), ("MBT", 60, 1)]


def test_d911_cap_binds_on_mhg() -> None:
    out = accept_trades(pd.DataFrame([cand("MHG", 0, 60)]), risk(["MHG"]), ACCOUNT_50K,
                        d_fixed=2000.0)
    assert accepted_pairs(out) == [("MHG", 0, 2)]


def test_sizing_at_fixed_d() -> None:
    # MNQ sigma 70 x $0.50 = $35 -> 3; loss 500 / ((100 + 3) x 0.5) = 9 -> 3 contracts
    out = accept_trades(pd.DataFrame([cand("MNQ", 0, 60)]), risk(["MNQ"], 70.0, 100.0),
                        ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 3)]


def test_inputs_are_not_mutated() -> None:
    c = pd.DataFrame([cand("MNQ", 0, 60), cand("MGC", 0, 60)])
    r = risk(["MNQ", "MGC"])
    before_c, before_r = c.copy(), r.copy()
    accept_trades(c, r, ACCOUNT_50K, d_fixed=2000.0)
    pd.testing.assert_frame_equal(c, before_c)
    pd.testing.assert_frame_equal(r, before_r)


@pytest.mark.parametrize("bad,match", [
    (dict(d_fixed=None), "accept_trades_needs_d_fixed"),
    (dict(risk_roots=["MGC"]), "risk_missing_pairs"),
    (dict(side=0), "candidate_bad_side"),
    (dict(exit_=0), "candidate_exit_not_after_decision"),
])
def test_contract_violations_raise_by_name(bad: dict, match: str) -> None:
    c = pd.DataFrame([cand("MNQ", 0, bad.get("exit_", 60), side=bad.get("side", 1))])
    with pytest.raises(PortfolioInputError, match=match):
        accept_trades(c, risk(bad.get("risk_roots", ["MNQ"])), ACCOUNT_50K,
                      d_fixed=bad.get("d_fixed", 2000.0))


# ---- fixed_d_daily_pnl -----------------------------------------------------------------------
def targets_frame() -> pd.DataFrame:
    rows = [("MNQ", 0, "2020-01-02", 12.0, 3.5, 3.6), ("MGC", 30, "2020-01-02", -20.0, 2.0, 2.1),
            ("MNQ", 0 + 1440, "2020-01-03", -4.0, 3.5, 3.6)]
    return pd.DataFrame([{"root": r, "decision_ts_ns": T0 + t * MIN,
                          "trade_date": pd.Timestamp(d), "y_gross_h60": y, "cost_long_h60": cl,
                          "cost_short_h60": cs} for r, t, d, y, cl, cs in rows])


def test_fixed_d_daily_pnl_hand_computed() -> None:
    acc = pd.DataFrame([
        {"root": "MNQ", "decision_ts_ns": T0, "trade_date": pd.Timestamp("2020-01-02"),
         "horizon": "h60", "side": 1, "contracts": 3},
        {"root": "MGC", "decision_ts_ns": T0 + 30 * MIN, "trade_date": pd.Timestamp("2020-01-02"),
         "horizon": "h60", "side": -1, "contracts": 2},
        {"root": "MNQ", "decision_ts_ns": T0 + 1440 * MIN,
         "trade_date": pd.Timestamp("2020-01-03"), "horizon": "h60", "side": 1, "contracts": 1}])
    got = fixed_d_daily_pnl(acc, targets_frame())
    # Contracts beyond q_c (1 for MNQ and MGC) pay 2 x (n - q_c) / n ticks a contract (D-08a).
    # 01-02: MNQ 3 x (12 - 3.5 - 2 x 2 / 3) x 0.5 = 3 x 7.1667 x 0.5 = 10.75;
    #        MGC 2 x (20 - 2.1 - 2 x 1 / 2) x 1.0 = 2 x 16.9 = 33.80 -> 44.55
    # 01-03: MNQ 1 contract (= q_c, no surcharge): 1 x (-4 - 3.5) x 0.5 = -3.75
    assert got.to_dict() == {pd.Timestamp("2020-01-02"): pytest.approx(44.55, abs=1e-9),
                             pd.Timestamp("2020-01-03"): pytest.approx(-3.75, abs=1e-9)}


def test_fixed_d_daily_pnl_refuses_a_missing_target() -> None:
    t = targets_frame().assign(y_gross_h60=np.nan)
    acc = pd.DataFrame([{"root": "MNQ", "decision_ts_ns": T0,
                         "trade_date": pd.Timestamp("2020-01-02"), "horizon": "h60", "side": 1,
                         "contracts": 1}])
    with pytest.raises(PortfolioInputError, match="target_missing"):
        fixed_d_daily_pnl(acc, t)


# ---- the selection metric (score_split) --------------------------------------------------------
def score_rows() -> pd.DataFrame:
    data = [("MNQ", "2020-01-02", 0, 12.0, 3.5, 3.6), ("MNQ", "2020-01-03", 1440, 5.0, 3.5, 3.6),
            ("MGC", "2020-01-06", 4 * 1440, -20.0, 2.0, 2.1)]
    return pd.DataFrame([{"root": r, "path_root": r, "cluster": UNIVERSE[r][0],
                          "trade_date": pd.Timestamp(d), "decision_ts_ns": T0 + t * MIN,
                          "flatten_ts_ns": T0 + (t + 368) * MIN,
                          "exit_ts_ns_h60": T0 + (t + 60) * MIN, "y_gross_h60": y,
                          "cost_long_h60": cl, "cost_short_h60": cs, "ok_h60": True,
                          "release_window": False}
                         for r, d, t, y, cl, cs in data])


R_HAT = np.array([20.0, 1.0, -15.0])
RISK = pd.DataFrame([{"root": "MNQ", "horizon": "h60", "sigma_ticks": 70.0, "loss_ticks": 100.0},
                     {"root": "MGC", "horizon": "h60", "sigma_ticks": 50.0, "loss_ticks": 100.0}])
# hand: MNQ long 3 (sigma $35 -> 3; loss 500 / 51.75 -> 9); MGC short 2 (115.47 / 50 -> 2;
# loss 500 / 102.1 -> 4). Beyond q_c = 1: + 2 x 2 / 3 ticks (MNQ), + 2 x 1 / 2 ticks (MGC).
# Daily: 3 x (12 - 3.5 - 1.3333) x 0.5 = 10.75; 0 (01-03, no trade); 2 x (20 - 2.1 - 1) x 1.0
# = 33.80.
EXPECTED_DAILY = [10.75, 0.0, 33.8]


def stub_candidates(rows: pd.DataFrame, r_hat: np.ndarray, config) -> pd.DataFrame:
    take = np.abs(r_hat) > 10.0
    side = np.sign(r_hat).astype(np.int8)
    cost = np.where(side > 0, rows["cost_long_h60"], rows["cost_short_h60"])
    return pd.DataFrame({
        "root": rows["root"], "cluster": rows["cluster"], "trade_date": rows["trade_date"],
        "decision_ts_ns": rows["decision_ts_ns"], "horizon": "h60",
        "exit_ts_ns": rows["exit_ts_ns_h60"], "side": side, "r_hat_ticks": r_hat,
        "cost_ticks": cost, "edge_over_cost": (np.abs(r_hat) - cost) / cost,
        "release_window": rows["release_window"].to_numpy(dtype=bool)})[take]


def test_score_split_hand_computed_with_a_stub_decision_layer() -> None:
    score = score_split(score_rows(), R_HAT, None, risk=RISK, candidates_fn=stub_candidates)
    assert score.n_trades == 2
    assert list(score.daily.index) == [pd.Timestamp(d) for d in
                                       ("2020-01-02", "2020-01-03", "2020-01-06")]
    assert score.daily.to_numpy() == pytest.approx(EXPECTED_DAILY, abs=1e-9)
    v = np.array(EXPECTED_DAILY)
    # mean 44.55 / 3, sd with ddof 1
    assert score.sharpe == pytest.approx(v.mean() / v.std(ddof=1), abs=1e-12)
    assert score.sharpe == pytest.approx(0.859924, abs=1e-6)  # 14.85 / 17.26898


def test_score_split_with_the_real_cost_gate() -> None:
    decide = pytest.importorskip("ml_route_v2.decide")
    configs = pytest.importorskip("ml_route_v2.configs")
    cfg = configs.Config("ridge_l0.1_k1.5_h60", configs.ridge_spec(0.1), 1.5, "h60")
    got = decide.candidates(score_rows(), R_HAT, cfg)
    # gross (V23 item 1): 20 > 1.5 x 3.5 and 15 > 1.5 x 2.1 trade, 1 does not
    assert list(got["root"]) == ["MNQ", "MGC"]
    score = score_split(score_rows(), R_HAT, cfg, risk=RISK)
    assert score.n_trades == 2 and score.daily.to_numpy() == pytest.approx(EXPECTED_DAILY)


def test_score_split_drops_unscorable_candidates_and_zero_sd() -> None:
    rows = score_rows().assign(y_gross_h60=[12.0, 5.0, np.nan])
    score = score_split(rows, R_HAT, None, risk=RISK, candidates_fn=stub_candidates)
    assert score.n_trades == 1 and score.daily.to_numpy() == pytest.approx([10.75, 0.0, 0.0])
    none = score_split(score_rows(), np.zeros(3), None, risk=RISK, candidates_fn=stub_candidates)
    assert none.n_trades == 0 and none.sharpe == 0.0 and (none.daily == 0).all()
    assert daily_sharpe(pd.Series([5.0])) == 0.0


# ---- design review D-03: the daily risk budget -------------------------------------------------
def test_daily_risk_budget_over_one_day_hand_computed() -> None:
    """Seven candidates in sequence on one trade date (each exits before the next decision, so
    no cap binds), then one on the next date; D fixed at $2,000: each date starts with
    sigma_target^2 = 200^2 = 40,000."""
    c = pd.DataFrame([cand("MNQ", 0, 30), cand("MGC", 30, 60), cand("MCL", 60, 90),
                      cand("6E", 90, 120), cand("MYM", 120, 150), cand("MNQ", 150, 180),
                      cand("MGC", 180, 210), cand("MGC", 1440, 1470, day="2020-01-03")])
    rk = risk_per_root({"MNQ": (70.0, 100.0), "MGC": (50.0, 100.0), "MCL": (60.0, 100.0),
                        "6E": (16.0, 10.0), "MYM": (160.0, 100.0)})
    # MNQ 0  : sigma $35 -> n_risk 3; budget floor(200 / 35) = 5 -> 3; uses 105^2 = 11,025 -> 28,975
    # MGC 30 : $50 -> 2; floor(170.22 / 50) = 3 -> 2; uses 100^2 = 10,000 -> 18,975
    # MCL 60 : $60 -> 1 (115.47 / 60 = 1.92); floor(137.75 / 60) = 2 -> 1; uses 3,600 -> 15,375
    # 6E 90  : 16 x $6.25 = $100 -> 1 (loss 500 / (13 x 6.25) = 6); floor(124.00 / 100) = 1;
    #          uses 10,000 -> 5,375
    # MYM 120: $80 -> 1; floor(73.31 / 80) = 0 -> refused (the budget is spent for this size)
    # MNQ 150: sigma 70 ticks again ($35) -> 3; floor(73.31 / 35) = 2 -> 2; uses 70^2 = 4,900
    #          -> 475
    # MGC 180: $50 -> floor(21.79 / 50) = 0 -> refused
    # MGC on 01-03: a new trade date, a new budget -> 2
    out = accept_trades(c, rk, ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 3), ("MGC", 30, 2), ("MCL", 60, 1), ("6E", 90, 1),
                                   ("MNQ", 150, 2), ("MGC", 1440, 2)]


def test_a_spent_budget_refuses_an_entry_by_name() -> None:
    kw = dict(root="MNQ", cluster="K1", sigma_ticks=70.0, loss_ticks=100.0, cost_ticks=3.0,
              d_open=2000.0, d_now=2000.0, book=(), tier_tenths=19, release_window=False)
    assert admit(**kw).contracts == 3  # no budget given: sizing alone
    assert admit(**kw, budget_var=40_000.0).contracts == 3
    assert admit(**kw, budget_var=35.0 ** 2).contracts == 1  # exactly one contract's use fits
    spent = admit(**kw, budget_var=0.0)
    assert (spent.contracts, spent.reason) == (0, "risk_budget_spent")
    # a size-zero candidate keeps its own reason even with no budget left
    tiny = admit(**{**kw, "d_now": 1.0}, budget_var=0.0)
    assert (tiny.contracts, tiny.reason) == (0, "size_zero")


# ---- design review D-08a and D-08b: cost beyond q_c, slippage multiple ---------------------------
def one_trade(contracts: int, side: int = 1) -> pd.DataFrame:
    return pd.DataFrame([{"root": "MNQ", "decision_ts_ns": T0,
                          "trade_date": pd.Timestamp("2020-01-02"), "horizon": "h60",
                          "side": side, "contracts": contracts}])


def test_vehicle_facts_carry_the_frozen_q_c_and_commission() -> None:
    f = vehicle_facts("MNQ")
    assert (f.q_c, f.commission_rt_ticks) == (1, 2.44)  # 122 cents / 50 cents a tick
    assert (vehicle_facts("MCL").q_c, vehicle_facts("MHG").q_c) == (4, 2)


@pytest.mark.parametrize("n,expected", [
    (1, 1 * (12 - 3.5) * 0.5),  # n = q_c: unchanged, 4.25
    (2, 2 * (12 - 3.5 - 2 * 1 / 2) * 0.5),  # one beyond: + 1 tick a contract, 7.50
    (4, 4 * (12 - 3.5 - 2 * 3 / 4) * 0.5),  # three beyond: + 1.5 ticks a contract, 14.00
])
def test_fixed_d_charges_one_tick_a_side_beyond_q_c(n: int, expected: float) -> None:
    got = fixed_d_daily_pnl(one_trade(n), targets_frame())
    assert got[pd.Timestamp("2020-01-02")] == pytest.approx(expected, abs=1e-12)


def test_slippage_multiple_one_is_the_current_figure_and_higher_lowers_pnl() -> None:
    acc = one_trade(3)
    base = fixed_d_daily_pnl(acc, targets_frame())
    pd.testing.assert_series_equal(fixed_d_daily_pnl(acc, targets_frame(), slippage_multiple=1.0),
                                   base)
    one = fixed_d_daily_pnl(one_trade(1), targets_frame(), slippage_multiple=1.5)
    # MNQ commission 2.44 ticks; slippage 3.5 - 2.44 = 1.06 -> x 1.5 = 1.59; cost 4.03:
    # 1 x (12 - 4.03) x 0.5 = 3.985
    assert one[pd.Timestamp("2020-01-02")] == pytest.approx(3.985, abs=1e-12)
    # at 3 contracts the beyond-q_c surcharge (4/3 tick) is slippage too and scales with it
    got3 = fixed_d_daily_pnl(acc, targets_frame(), slippage_multiple=1.5)
    assert got3.iloc[0] == pytest.approx(3 * (12 - (2.44 + 1.5 * (3.5 + 4 / 3 - 2.44))) * 0.5,
                                         abs=1e-12)
    values = [fixed_d_daily_pnl(acc, targets_frame(), slippage_multiple=m).iloc[0]
              for m in (1.0, 1.25, 1.5, 2.0, 3.0)]
    assert all(a > b for a, b in zip(values, values[1:], strict=False))
    with pytest.raises(PortfolioInputError, match="bad_slippage_multiple"):
        fixed_d_daily_pnl(acc, targets_frame(), slippage_multiple=float("nan"))


def test_score_split_slippage_multiple_lowers_the_score_monotonically() -> None:
    scores = [score_split(score_rows(), R_HAT, None, risk=RISK, candidates_fn=stub_candidates,
                          slippage_multiple=m) for m in (1.0, 1.5, 2.0)]
    assert scores[0].daily.to_numpy() == pytest.approx(EXPECTED_DAILY, abs=1e-9)
    totals = [float(sc.daily.sum()) for sc in scores]
    assert totals[0] > totals[1] > totals[2]
    assert all(sc.n_trades == 2 for sc in scores)  # the same trades, re-priced


# ---- code review C-02: a pair with no usable risk is skipped and counted --------------------
def test_a_pair_with_nan_risk_is_skipped_as_risk_unknown_and_counted() -> None:
    """MGC's sigma is NaN in the split's table (fewer than two training rows): its candidate is
    not sized (reason risk_unknown), MNQ trades as before, and the selection metric counts the
    skip. A pair absent from the table still raises (risk_missing_pairs)."""
    from ml_route_v2.portfolio import join_risk, risk_unknown

    c = pd.DataFrame([cand("MNQ", 0, 60, edge=3.0), cand("MGC", 0, 60, edge=2.0)])
    table = risk(["MNQ", "MGC"])
    table.loc[table["root"] == "MGC", "sigma_ticks"] = np.nan
    joined = join_risk(c, table)
    assert risk_unknown(joined).tolist() == [False, True]
    out = accept_trades(c, table, ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 10)]
    adm = admit(root="MGC", cluster="K5", sigma_ticks=float("nan"), loss_ticks=1.0,
                cost_ticks=3.0, d_open=2000.0, d_now=2000.0, book=(), tier_tenths=20,
                release_window=False)
    assert (adm.contracts, adm.reason) == (0, "risk_unknown")
    zero = admit(root="MGC", cluster="K5", sigma_ticks=0.0, loss_ticks=1.0, cost_ticks=3.0,
                 d_open=2000.0, d_now=2000.0, book=(), tier_tenths=20, release_window=False)
    assert zero.reason == "risk_unknown"  # sd 0: not sizeable either
    rows = score_rows()
    nan_mgc = RISK.assign(loss_ticks=[100.0, np.nan])
    score = score_split(rows, R_HAT, None, risk=nan_mgc, candidates_fn=stub_candidates)
    assert score.n_trades == 1 and score.n_risk_unknown == 1
    assert score.daily.to_numpy() == pytest.approx([10.75, 0.0, 0.0])
    assert score_split(rows, R_HAT, None, risk=RISK,
                       candidates_fn=stub_candidates).n_risk_unknown == 0
    with pytest.raises(PortfolioInputError, match="risk_missing_pairs"):
        accept_trades(c, risk(["MNQ"]), ACCOUNT_50K, d_fixed=2000.0)


# ---- code review C-04: row-level sigma and loss win over the table ---------------------------
def test_join_risk_prefers_the_candidates_own_sigma_and_loss() -> None:
    """Candidates carrying sigma_ticks and loss_ticks (the nested schedule attaches each split's
    own table) keep them; the table is not merged. One of the two columns alone is refused."""
    from ml_route_v2.portfolio import join_risk

    c = pd.DataFrame([cand("MNQ", 0, 60)])
    table = risk(["MNQ"], sigma=70.0, loss=100.0)
    own = c.assign(sigma_ticks=35.0, loss_ticks=100.0)
    assert join_risk(c, table)["sigma_ticks"].tolist() == [70.0]
    assert join_risk(own, table)["sigma_ticks"].tolist() == [35.0]
    assert join_risk(own, risk(["MGC"]))["sigma_ticks"].tolist() == [35.0]  # table not read
    # D 2000: budget 115.47 / (sigma x $0.50): 70 -> 3 contracts, 35 -> 6
    assert accepted_pairs(accept_trades(c, table, ACCOUNT_50K, d_fixed=2000.0)) == [
        ("MNQ", 0, 3)]
    assert accepted_pairs(accept_trades(own, table, ACCOUNT_50K, d_fixed=2000.0)) == [
        ("MNQ", 0, 6)]
    with pytest.raises(PortfolioInputError, match="candidate_partial_risk_columns"):
        join_risk(c.assign(sigma_ticks=35.0), table)


# ---- V23 item 11 (E.12 lead rule P-5): the release-window rule ---------------------------------
R_REL = T0 + 100 * MIN  # a scheduled release concerning MGC
R_OTHER = T0 + 150 * MIN  # a release concerning 6E only


def test_release_window_mask_is_half_open_around_each_release() -> None:
    rel = np.array([R_REL, R_REL + 300 * MIN])
    fills = np.array([R_REL - 5 * MIN - 1, R_REL - 5 * MIN, R_REL, R_REL + 29 * MIN,
                      R_REL + 30 * MIN - 1, R_REL + 30 * MIN, R_REL + 295 * MIN, -1, 0])
    assert release_window_mask(fills, rel).tolist() == [False, True, True, True, True, False,
                                                       True, False, False]
    assert release_window_mask(fills, rel[::-1]).tolist() == release_window_mask(fills,
                                                                                 rel).tolist()
    assert not release_window_mask(fills, np.array([], dtype=np.int64)).any()


def test_release_window_binds_above_half_the_tier_only() -> None:
    # 50K tiers 2 / 3 / 5 lots: half = 10 / 15 / 25 tenths
    assert [bool(release_window_binds(x, 20)) for x in (9, 10, 11)] == [False, False, True]
    assert [bool(release_window_binds(x, 30)) for x in (15, 16)] == [False, True]
    assert [bool(release_window_binds(x, 50)) for x in (25, 26)] == [False, True]
    got = release_window_binds(np.array([10, 11, 15, 16]), np.array([20, 20, 30, 30]))
    assert got.tolist() == [False, True, False, True]


def test_admit_refuses_a_window_entry_only_above_half_the_tier() -> None:
    """MNQ 5 contracts open (0.5 lot) at the base tier (2 lots: half = 1.0). An MGC entry in its
    release window of 5 micros (0.5 lot) reaches exactly half and is admitted; 6 micros exceed
    half and are refused by name. Outside the window the same 6 micros are admitted."""
    from ml_route_v2.portfolio import OpenPosition

    book = (OpenPosition("MNQ", "K1", 5, T0 + 300 * MIN),)
    kw = dict(root="MGC", cluster="K5", sigma_ticks=1.0, loss_ticks=1.0, cost_ticks=3.0,
              d_open=2000.0, d_now=2000.0, book=book, tier_tenths=20)
    assert admit(**kw, release_window=True, extra_cap=5).contracts == 5
    refused = admit(**kw, release_window=True, extra_cap=6)
    assert (refused.contracts, refused.reason) == (0, "release_window")
    assert admit(**kw, release_window=False, extra_cap=6).contracts == 6
    # at the 3-lot tier half is 1.5 lots: the same 6 micros fit
    assert admit(**{**kw, "tier_tenths": 30}, release_window=True, extra_cap=6).contracts == 6


def _window_cands(book: bool) -> pd.DataFrame:
    """MGC entries around its release R_REL, each exiting a minute later, with flags from MGC's
    own release list; MNQ (1 lot, half the base tier) open over the window when ``book``."""
    rel_mgc = np.array([R_REL])
    rows = [cand("MGC", t, t + 1) for t in (94, 95, 129, 130, 150)]
    if book:
        rows.insert(0, cand("MNQ", 0, 200, edge=5.0))
    c = pd.DataFrame(rows)
    fills = c["decision_ts_ns"].to_numpy(dtype=np.int64)
    flags = np.where(c["root"] == "MGC", release_window_mask(fills, rel_mgc), False)
    return c.assign(release_window=flags.astype(bool))


def test_accept_trades_refuses_window_entries_above_half_and_counts_them() -> None:
    """With MNQ's 1.0 lot open (= half the 2-lot base tier), MGC entries at r - 5 min and
    r + 29 min are refused ("release_window"); r - 6 min and r + 30 min (the half-open end) are
    admitted; at 6E's release time (not MGC's) the entry is admitted: another product's release
    does not bind. The record counts the two refusals."""
    c = _window_cands(book=True)
    assert c["release_window"].tolist() == [False, False, True, True, False, False]
    other = release_window_mask(np.array([T0 + 150 * MIN]), np.array([R_OTHER]))
    assert other.tolist() == [True]  # the same entry would sit in 6E's window
    rec = admission_record(c, risk(["MNQ", "MGC"]), ACCOUNT_50K, d_fixed=2000.0)
    assert list(zip(rec["root"], (rec["decision_ts_ns"] - T0) // MIN, rec["contracts"],
                    rec["reason"], strict=True)) == [
        ("MNQ", 0, 10, ""), ("MGC", 94, 9, ""), ("MGC", 95, 0, "release_window"),
        ("MGC", 129, 0, "release_window"), ("MGC", 130, 9, ""), ("MGC", 150, 9, "")]
    assert refusal_counts(rec) == {"release_window": 2}
    out = accept_trades(c, risk(["MNQ", "MGC"]), ACCOUNT_50K, d_fixed=2000.0)
    assert accepted_pairs(out) == [("MNQ", 0, 10), ("MGC", 94, 9), ("MGC", 130, 9),
                                   ("MGC", 150, 9)]
    assert "reason" not in out.columns


def test_accept_trades_admits_a_window_entry_at_exactly_half_the_tier() -> None:
    """Without the MNQ book, MGC at r + 29 min takes 10 micros (1.0 lot): exactly half the base
    tier, not above it, so it is admitted; the window binds only above half."""
    c = _window_cands(book=False)
    rec = admission_record(c, risk(["MGC"]), ACCOUNT_50K, d_fixed=2000.0)
    assert rec["contracts"].tolist() == [10, 10, 10, 10, 10]
    assert refusal_counts(rec) == {}


def test_candidates_need_a_boolean_release_window_flag() -> None:
    c = pd.DataFrame([cand("MNQ", 0, 60)])
    with pytest.raises(PortfolioInputError, match="release_window"):
        accept_trades(c.drop(columns="release_window"), risk(["MNQ"]), ACCOUNT_50K,
                      d_fixed=2000.0)
    with pytest.raises(PortfolioInputError, match="candidate_bad_release_window"):
        accept_trades(c.assign(release_window=1.0), risk(["MNQ"]), ACCOUNT_50K, d_fixed=2000.0)


def test_score_split_applies_the_release_window_rule() -> None:
    """The selection metric reads each row's flag through the decision layer. One date: MNQ at
    09:00 sized to its 1-lot product cap (sigma 1, loss 1), then MGC at 09:10 with 9 micros (the
    capacity left under the 1.9-lot portfolio cap): 1.9 lots exceed half the base tier, so a
    flagged MGC row is refused and only MNQ trades; unflagged, both trade."""
    base = score_rows().iloc[[0, 2]].reset_index(drop=True)
    rows = base.assign(trade_date=pd.Timestamp("2020-01-02"),
                       decision_ts_ns=[T0, T0 + 10 * MIN],
                       flatten_ts_ns=[T0 + 368 * MIN, T0 + 378 * MIN],
                       exit_ts_ns_h60=[T0 + 60 * MIN, T0 + 70 * MIN])
    tight = RISK.assign(sigma_ticks=1.0, loss_ticks=1.0)
    r_hat = np.array([20.0, -15.0])
    plain = score_split(rows, r_hat, None, risk=tight, candidates_fn=stub_candidates)
    flagged = score_split(rows.assign(release_window=[False, True]), r_hat, None, risk=tight,
                          candidates_fn=stub_candidates)
    assert plain.n_trades == 2 and flagged.n_trades == 1
    assert flagged.daily.to_numpy() == pytest.approx([10 * (12.0 - 3.5 - excess(10)) * 0.5])


def excess(n: int) -> float:
    """The beyond-q_c surcharge per contract for MNQ (D-08a): 2 x (n - q_c)^+ / n ticks."""
    q_c = vehicle_facts("MNQ").q_c
    return 2.0 * max(n - q_c, 0) / n
