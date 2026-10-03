"""Stage E.11 Task 4: account parameters and the payout simulator (docs/STAGE_E_ML_V2_DESIGN.md
V2.0, V2.9 "Payout simulation"). Hand-computed sequences pinned to the cent, agreement with
rules.xfa_rules, and the vectorized simulator pinned path for path to run_path."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta

import numpy as np
import pytest

from ml_route_v2.account import ACCOUNT_50K, ACCOUNT_150K, payout_cap_usd, trail_floor
from ml_route_v2.constants import PAYOUT_KEEP_D_FRAC
from ml_route_v2.payout_sim import (
    DayRecord,
    TradeRecord,
    bootstrap_indices,
    run_path,
    simulate_paths,
    simulate_payouts,
    simulate_payouts_pair,
)
from rules import xfa_rules as xr

D0 = date(2020, 1, 2)
MIN = 60_000_000_000


def tr(pnl: float, worst: float | None = None, *, root: str = "ZN", sigma: float = 0.1,
       loss: float = 0.1, cost: float = 0.0, entry: int = 0, exit_: int = 0,
       day: date = D0) -> TradeRecord:
    """A trade of one contract by construction on ZN (a mini: product cap 1; tiny risk numbers so
    the sizing never binds below the cap)."""
    from ml_route_v2.portfolio import vehicle_facts

    f = vehicle_facts(root)
    w = min(pnl, 0.0) if worst is None else worst
    return TradeRecord(root, "h60", day, 1, pnl, w, sigma, loss, cost, f.tick_value_usd,
                       f.lot_equiv, "", entry, exit_)


def days_of(pnls) -> list[DayRecord]:
    """One DayRecord per entry: a number is one trade with that P&L, None a no-trade date."""
    out = []
    for i, p in enumerate(pnls):
        d = D0 + timedelta(days=i)
        out.append(DayRecord(d, () if p is None else (tr(p, day=d),)))
    return out


# ---- account parameters --------------------------------------------------------------------
def test_account_50k_is_xfa_50k_in_dollars() -> None:
    x = xr.XFA_50K
    a = ACCOUNT_50K
    assert a.mll_usd * 100 == x.mll_cents and a.mll_lock_usd * 100 == x.mll_lock_cents
    assert a.post_payout_floor_usd * 100 == x.post_payout_mll_floor_cents
    assert a.standard_cap_usd * 100 == x.standard.per_request_cap_cents
    assert a.consistency_cap_usd * 100 == x.consistency.per_request_cap_cents
    assert a.min_payout_usd * 100 == x.min_payout_cents
    assert a.balance_ceiling_frac * xr.BPS == x.payout_balance_ceiling_bps
    assert (a.standard_min_days, a.standard_winning_day_usd * 100) == (
        x.standard.min_days, x.standard.winning_day_min_net_cents)
    assert (a.consistency_min_days, a.consistency_largest_frac * xr.BPS) == (
        x.consistency.min_days, x.consistency.largest_day_max_bps)
    assert a.base_lots == x.base_max_minis
    assert a.scaling_tiers == ((1500.0, True, 3.0), (2000.0, False, 5.0))
    assert (a.dll_usd, a.dll_cap_multiplier, a.split) == (1000.0, 2.0, 0.9)


def test_account_150k_figures_and_dll_doubling() -> None:
    a = ACCOUNT_150K
    assert (a.mll_usd, a.dll_usd, a.standard_cap_usd, a.consistency_cap_usd) == (
        4500.0, 3000.0, 5000.0, 6000.0)
    assert a.scaling_tiers == ACCOUNT_50K.scaling_tiers and a.base_lots == 2.0
    assert payout_cap_usd(a, "standard", True) == 10_000.0
    assert payout_cap_usd(a, "consistency", True) == 12_000.0
    assert payout_cap_usd(ACCOUNT_50K, "standard", True) == 4_000.0
    assert payout_cap_usd(ACCOUNT_50K, "consistency", False) == 3_000.0
    with pytest.raises(ValueError, match="unknown_path_type"):
        payout_cap_usd(a, "fast", False)


@pytest.mark.parametrize("prev,eod", [(-200_000, 50_000), (-200_000, 250_000), (-50_000, 10_000),
                                      (0, -30_000), (-150_000, 175_000)])
def test_trailing_floor_matches_xfa_rules(prev: int, eod: int) -> None:
    assert trail_floor(ACCOUNT_50K, prev / 100, eod / 100) * 100 == xr.trail_mll_floor(
        prev, eod, xr.Phase.XFA)


# ---- hand-computed sequences ---------------------------------------------------------------
STANDARD = [200, 150, 100, 300, 160, 175, 200, 149.90, 150, 150, 150, 150, 150, 50]


def test_keep_d_policy_constant() -> None:
    assert PAYOUT_KEEP_D_FRAC == 0.5


def test_standard_sequence_old_policy_hand_computed_to_the_cent() -> None:
    res = run_path(days_of(STANDARD), ACCOUNT_50K, path_type="standard", dll=False, ks=False,
                   keep_d_frac=0.0)
    # Old policy: min(cap, 50% of the balance).
    # d1..d6: winners d1 200, d2 150, d4 300, d5 160, d6 175 (d3 100 is not) -> 5 after d6.
    # d7: request at the start: min($2,000, 50% x $1,085.00) = $542.50 -> net $488.25; balance
    # $542.50, floor reset to $0; d7 +200 -> $742.50 (d7 does not count: the request day).
    # d8 +149.90 (not a winner); d9..d13 +150 x 5 -> 5 winners after d13 (after d12 only 4,
    # which would have been 5 had d7 counted). d14: request min($2,000, 50% x $1,642.40) =
    # $821.20 -> net $739.08; balance $821.20; d14 +50 -> $871.20.
    assert [(p.day_index, p.amount_usd) for p in res.payouts] == [(6, 542.50), (13, 821.20)]
    assert [p.net_usd for p in res.payouts] == pytest.approx([488.25, 739.08], abs=1e-9)
    assert res.balance == pytest.approx([200, 350, 450, 750, 910, 1085, 742.5, 892.4, 1042.4,
                                         1192.4, 1342.4, 1492.4, 1642.4, 871.2], abs=1e-9)
    # floor: max(prev, min(balance - 2000, 0)): -1800, -1650, -1550, -1250, -1090, -915, then $0
    assert res.floor == pytest.approx([-1800, -1650, -1550, -1250, -1090, -915] + [0] * 8,
                                      abs=1e-9)
    assert res.status == "active" and res.first_breach_day is None


def test_standard_sequence_keep_d_policy_hand_computed_to_the_cent() -> None:
    res = run_path(days_of(STANDARD), ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    # Policy: min(cap, 50% x balance, balance - 0.5 x $2,000). Eligible after d6 (5 winners):
    # d7 request min($2,000, $542.50, $1,085 - $1,000 = $85) = $85 < $125 -> none; d7 +200 ->
    # $1,285. d8: min($2,000, $642.50, $285) = $285.00 -> net $256.50; balance $1,000, floor $0;
    # d8 +149.90 -> $1,149.90 (the request day). d9..d13 +150 x 5: 5 winners -> d14:
    # min($2,000, 50% x $1,899.90 = $949.95, $899.90) = $899.90 -> net $809.91; balance $1,000;
    # d14 +50 -> $1,050. D after each payout = $1,000 = 0.5 x MLL (KS2 not tripped).
    assert [(p.day_index, p.amount_usd) for p in res.payouts] == [(7, 285.00), (13, 899.90)]
    assert [p.net_usd for p in res.payouts] == pytest.approx([256.50, 809.91], abs=1e-9)
    assert res.balance == pytest.approx([200, 350, 450, 750, 910, 1085, 1285, 1149.9, 1299.9,
                                         1449.9, 1599.9, 1749.9, 1899.9, 1050], abs=1e-9)
    # floor: ..., -915, then d7 min(1,285 - 2,000, 0) = -715, then $0 from the d8 payout on
    assert res.floor == pytest.approx([-1800, -1650, -1550, -1250, -1090, -915, -715] + [0] * 7,
                                      abs=1e-9)


CONSISTENCY = [300, 250, 200, 100, 500, None, 100, 100, 300, 250, -50]


def test_consistency_sequence_old_policy_hand_computed_to_the_cent() -> None:
    res = run_path(days_of(CONSISTENCY), ACCOUNT_50K, path_type="consistency", dll=False,
                   ks=False, keep_d_frac=0.0)
    # Old policy. d1..d3: 3 traded dates, net $750, largest $300 = 40.00% (inclusive) -> d4 request:
    # min($3,000, 50% x $750) = $375.00 -> net $337.50; balance $375; d4 +100 -> $475 (excluded).
    # d5 +500, d6 no trade (not a traded date), d7 +100, d8 +100: largest 500 / 700 = 71% no;
    # d9 +300: 500 / 1000 = 50% no; d10 +250: 500 / 1250 = 40% yes -> d11 request:
    # min($3,000, 50% x $1,725) = $862.50 -> net $776.25; balance $862.50; d11 -50 -> $812.50.
    assert [(p.day_index, p.amount_usd) for p in res.payouts] == [(3, 375.00), (10, 862.50)]
    assert [p.net_usd for p in res.payouts] == pytest.approx([337.50, 776.25], abs=1e-9)
    assert res.balance == pytest.approx([300, 550, 750, 475, 975, 975, 1075, 1175, 1475, 1725,
                                         812.5], abs=1e-9)
    assert res.floor == pytest.approx([-1700, -1450, -1250] + [0] * 8, abs=1e-9)


def test_consistency_sequence_keep_d_policy_hand_computed_to_the_cent() -> None:
    res = run_path(days_of(CONSISTENCY), ACCOUNT_50K, path_type="consistency", dll=False,
                   ks=False)
    # Eligible after d3 ($750, largest 40%): d4 min($3,000, $375, $750 - $1,000) < $125 -> none;
    # d4 +100 -> $850 (window 4 traded, 300 / 850 = 35%); d5 min(.., $425, -$150) -> none;
    # d5 +500 -> $1,350 (500 / 1,350 = 37%); d6 min($3,000, $675, $350) = $350.00 -> net
    # $315.00; balance $1,000, floor $0; d6 no trade. d7 +100, d8 +100, d9 +300 (300 / 500 =
    # 60% no), d10 +250 (300 / 750 = 40% yes) -> d11 min($3,000, $875, $750) = $750.00 -> net
    # $675.00; balance $1,000; d11 -50 -> $950.
    assert [(p.day_index, p.amount_usd) for p in res.payouts] == [(5, 350.00), (10, 750.00)]
    assert [p.net_usd for p in res.payouts] == pytest.approx([315.00, 675.00], abs=1e-9)
    assert res.balance == pytest.approx([300, 550, 750, 850, 1350, 1000, 1100, 1200, 1500, 1750,
                                         950], abs=1e-9)
    assert res.floor == pytest.approx([-1700, -1450, -1250, -1150, -650] + [0] * 6, abs=1e-9)


# ---- agreement with rules.xfa_rules --------------------------------------------------------
def _xfa_replay(pnls_cents, path: xr.PayoutPath, keep_cents: int):
    state = xr.new_xfa_account()
    rules = xr.XFA_50K.standard if path is xr.PayoutPath.STANDARD else xr.XFA_50K.consistency
    payouts, bal, flo = [], [], []
    for i, p in enumerate(pnls_cents):
        if path is xr.PayoutPath.STANDARD:
            elig = xr.standard_path_eligibility(state.payout_window, state.payouts_processed)
        else:
            elig = xr.consistency_path_eligibility(state.payout_window)
        amount = min(rules.per_request_cap_cents,
                     xr.XFA_50K.payout_balance_ceiling_bps * state.balance_cents // xr.BPS,
                     state.balance_cents - keep_cents)
        if elig is None and amount >= xr.XFA_50K.min_payout_cents:
            out = xr.process_payout(state, path, amount)
            assert out.refusal is None
            state = out.state
            payouts.append((i, amount))
        if p is not None:
            state = xr.record_realized_pnl(state, p)
        state = xr.close_trading_day(state, D0 + timedelta(days=i), 0 if p is None else 1)
        if state.status is not xr.Status.ACTIVE:
            return payouts, bal, flo, i
        bal.append(state.balance_cents)
        flo.append(state.mll_floor_cents)
    return payouts, bal, flo, None


@pytest.mark.parametrize("keep", [0.0, PAYOUT_KEEP_D_FRAC])
@pytest.mark.parametrize("path_type", ["standard", "consistency"])
@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 6])
def test_eligibility_and_payouts_agree_with_xfa_rules(path_type: str, seed: int,
                                                      keep: float) -> None:
    rng = np.random.default_rng(seed)
    cents = []
    for _ in range(120):
        u = rng.random()
        cents.append(None if u < 0.1 else 15_000 if u < 0.2 else int(rng.integers(-25_000,
                                                                                    40_000)))
    path = xr.PayoutPath.STANDARD if path_type == "standard" else xr.PayoutPath.CONSISTENCY
    x_pay, x_bal, x_flo, x_breach = _xfa_replay(cents, path,
                                                round(keep * xr.XFA_50K.mll_cents))
    res = run_path(days_of([None if c is None else c / 100 for c in cents]), ACCOUNT_50K,
                   path_type=path_type, dll=False, ks=False, keep_d_frac=keep)
    assert [(p.day_index, round(p.amount_usd * 100)) for p in res.payouts] == x_pay
    n = len(x_bal)
    assert np.allclose(np.array(res.balance[:n]) * 100, x_bal, atol=1e-6)
    assert np.allclose(np.array(res.floor[:n]) * 100, x_flo, atol=1e-6)
    assert res.first_breach_day == x_breach
    assert len(x_pay) >= 1  # the sequences reach at least one payout


# ---- DLL, ruin, kill switches ---------------------------------------------------------------
def test_dll_truncates_the_day_at_minus_dll() -> None:
    day = [DayRecord(D0, (tr(-300.0, -1200.0),))]
    on = run_path(day, ACCOUNT_50K, path_type="standard", dll=True, ks=False)
    assert on.day_pnl == (-1000.0,) and on.stopped == (True,)
    assert on.balance == (-1000.0,) and on.floor == (-2000.0,)
    off = run_path(day, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    assert off.day_pnl == (-300.0,) and off.stopped == (False,) and off.status == "active"


def test_ruin_when_the_intraday_worst_touches_the_floor() -> None:
    days = [DayRecord(D0, (tr(-100.0, -2000.0),)), DayRecord(D0 + timedelta(1), (tr(50.0),))]
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    assert res.status == "breached" and res.first_breach_day == 0 and res.n_breaches == 1
    assert res.balance == (-2000.0, -2000.0) and res.contracts[1] == ()
    # with the DLL: day 1 stops at -$1,000 (D 2,000 -> 1,000); day 2's worst -$1,000 reaches
    # the MLL (D_open 1,000 <= DLL 1,000): breach
    d2 = [DayRecord(D0, (tr(-100.0, -2000.0),)), DayRecord(D0 + timedelta(1),
                                                          (tr(50.0, -1000.0),))]
    res = run_path(d2, ACCOUNT_50K, path_type="standard", dll=True, ks=False)
    assert res.day_pnl[0] == -1000.0 and res.first_breach_day == 1 and res.status == "breached"


def test_restart_after_a_breach_counts_resets() -> None:
    days = [DayRecord(D0 + timedelta(i), (tr(-100.0, -2500.0),) if i in (0, 3) else (tr(10.0),))
            for i in range(6)]
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False, restart=True,
                   reset_delay_dates=1)
    # breach d1; d2 waits; account 2 starts d3; d3 +10; breach d4; d5 waits; account 3 on d6
    assert res.n_breaches == 2 and res.first_breach_day == 0
    assert res.contracts[1] == () and res.contracts[2] == (1,) and res.contracts[4] == ()
    assert res.balance[5] == 10.0 and res.status == "active"


def test_ks1_stops_the_day_and_the_path_never_breaches_with_ks() -> None:
    days = [DayRecord(D0, (tr(-200.0, -700.0),)), DayRecord(D0 + timedelta(1),
                                                           (tr(-100.0, -5000.0),))]
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=True)
    # KS1 at 0.30 x 2000 = 600; then D 1400 -> 0.30 x 1400 = 420
    assert res.day_pnl == pytest.approx((-600.0, -420.0)) and res.stopped == (True, True)
    assert res.status == "active" and res.first_breach_day is None


def test_ks3_skips_the_date_after_five_losing_dates() -> None:
    res = run_path(days_of([-10, -10, -10, -10, -10, 50, 50]), ACCOUNT_50K,
                   path_type="standard", dll=False, ks=True)
    assert [c for c in res.contracts] == [(1,)] * 5 + [(0,), (1,)]
    assert res.day_pnl[5] == 0.0 and res.day_pnl[6] == 50.0


def test_ks2_half_size_below_half_the_mll() -> None:
    mnq = TradeRecord("MNQ", "h60", D0, 1, 10.0, 0.0, 10.0, 1.0, 0.0, 0.5, 0.1)
    days = days_of([-550, -430, -120]) + [DayRecord(D0 + timedelta(3), (mnq,))]
    on = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=True)
    off = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    # D_open after the losses: 2000 - 1100 = 900. b = 0.1 x 900 / sqrt(3) = 51.96; one sigma
    # = 10 x 0.5 = $5 -> 10 (the product cap); KS2: 25.98 / 5 -> 5
    assert on.contracts[3] == (5,) and off.contracts[3] == (10,)


def test_ks2b_halts_after_an_early_payout_under_the_old_policy_only() -> None:
    days = days_of([150] * 5 + [10, 10])
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=True, keep_d_frac=0.0)
    # $750 -> request min($2,000, $375) on d6 -> balance $375, floor $0: D = 375 < 0.25 x 2000
    assert [(p.day_index, p.amount_usd) for p in res.payouts] == [(5, 375.0)]
    assert res.status == "halted" and res.halt_day == 5 and res.contracts[5:] == ((), ())
    free = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False,
                    keep_d_frac=0.0)
    assert free.status == "active" and free.contracts[5] == (1,)
    # the keep-D policy: min($2,000, $375, $750 - $1,000) < $125 -> no request, no halt
    kept = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=True)
    assert kept.payouts == () and kept.status == "active" and kept.halt_day is None
    assert kept.contracts[5:] == ((1,), (1,)) and kept.balance[-1] == 770.0


def test_resizing_from_the_paths_own_d_after_a_payout() -> None:
    def mnq(day: date) -> TradeRecord:
        return TradeRecord("MNQ", "h60", day, 3, 200.0, 0.0, 70.0, 100.0, 3.0, 0.5, 0.1)

    days = [DayRecord(D0, (mnq(D0),))] + days_of([None, 600, 600, 600, 600])[1:]
    days.append(DayRecord(D0 + timedelta(5), (mnq(D0 + timedelta(5)),)))
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    # d1 at D 2000: 3 contracts x $200 = $600; d2..d5 +600: 5 winners, balance $3,000.
    # d6: request min($2,000, $1,500) = $1,500 -> balance $1,500, floor $0: D 1500 -> 2
    # contracts (86.60 / 35 = 2.47) x $200 -> $1,900
    assert res.contracts[0] == (3,) and res.contracts[5] == (2,)
    assert res.payouts[0].day_index == 5 and res.payouts[0].amount_usd == 1500.0
    assert res.balance[5] == 1900.0


def test_concurrency_from_entry_and_exit_times() -> None:
    def leg(root: str, entry: int, exit_: int, known: bool = True) -> TradeRecord:
        from ml_route_v2.portfolio import vehicle_facts

        f = vehicle_facts(root)
        return TradeRecord(root, "h60", D0, 1, 10.0, 0.0, 0.1, 0.1, 0.0, f.tick_value_usd,
                           f.lot_equiv, "", entry * MIN if known else 0,
                           exit_ * MIN if known else 0)

    def sizes(trades) -> tuple[int, ...]:
        return run_path([DayRecord(D0, tuple(trades))], ACCOUNT_50K, path_type="standard",
                        dll=False, ks=False).contracts[0]

    # 19 tenths: MNQ 10 micros (1 lot cap), MGC the 9 left while MNQ is open
    assert sizes([leg("MNQ", 540, 600), leg("MGC", 570, 630)]) == (10, 9)
    assert sizes([leg("MNQ", 540, 600), leg("MGC", 600, 660)]) == (10, 10)  # MNQ closed
    assert sizes([leg("MNQ", 0, 0, False), leg("MGC", 0, 0, False)]) == (10, 9)  # unknown


# ---- the vectorized simulator ------------------------------------------------------------------
def _base_days(n_days: int, seed: int, with_q_c: bool = False) -> list[DayRecord]:
    """Random dates of up to 4 trades. ``with_q_c``: engine sizes 1..4 and the vehicle's q_c on
    about two trades in three, drawn from a second stream so the base draws stay the same."""
    from ml_route_v2.portfolio import vehicle_facts

    rng = np.random.default_rng(seed)
    extra = np.random.default_rng(seed + 1000)
    roots = ("MNQ", "MGC", "ZN", "MCL", "6E")
    out = []
    for i in range(n_days):
        trades = []
        for k in range(int(rng.integers(0, 5))):
            root = roots[int(rng.integers(0, len(roots)))]
            f = vehicle_facts(root)
            pnl = float(np.round(rng.normal(8.0, 90.0) / max(f.tick_value_usd, 1.0) * 2, 2))
            worst = min(pnl, pnl - float(np.round(abs(rng.normal(0, 150.0)), 2)))
            entry = 540 + 30 * k + int(rng.integers(0, 3)) * 30
            known = rng.random() < 0.8
            n_eng, q_c = 1, None
            if with_q_c:
                n_eng = int(extra.integers(1, 5))
                q_c = f.q_c if extra.random() < 0.67 else None
            trades.append(TradeRecord(
                root, "h60", D0 + timedelta(i), n_eng, pnl, worst, float(rng.uniform(5, 60)),
                float(rng.uniform(20, 150)), 2.0, f.tick_value_usd, f.lot_equiv, "",
                entry * MIN if known else 0, (entry + 60) * MIN if known else 0, q_c))
        out.append(DayRecord(D0 + timedelta(i), tuple(trades)))
    return out


@pytest.mark.parametrize("path_type,dll,ks,delay,keep,ks2,q_c", [
    ("standard", False, True, 0, 0.5, None, False),
    ("consistency", True, False, 0, 0.5, None, False),
    ("standard", True, False, 2, 0.5, None, False),
    ("consistency", False, True, 1, 0.5, None, False),
    ("standard", False, False, 0, 0.5, None, False),
    ("standard", False, True, 0, 0.0, None, False),
    ("consistency", True, False, 1, 0.0, None, False),
    ("standard", False, False, 0, 0.5, True, True),  # the verdict reading (D-01), with q_c
    ("consistency", True, False, 1, 0.5, True, True),
    ("standard", False, True, 0, 0.5, None, True),
    ("standard", True, True, 2, 0.0, False, True)])
def test_vectorized_paths_equal_run_path(path_type: str, dll: bool, ks: bool, delay: int,
                                         keep: float, ks2, q_c: bool) -> None:
    base = _base_days(40, 11, with_q_c=q_c)
    idx = bootstrap_indices(len(base), 48, 90, 5, 7)
    arr = simulate_paths(base, ACCOUNT_50K, idx, path_type=path_type, dll=dll, ks=ks,
                         restart=True, reset_delay_dates=delay, keep_d_frac=keep,
                         ks2_sizing=ks2)
    events = {"pay": 0, "breach": 0, "halt": 0, "ruin": 0}
    for p in range(idx.shape[0]):
        res = run_path([base[i] for i in idx[p]], ACCOUNT_50K, path_type=path_type, dll=dll,
                       ks=ks, restart=True, reset_delay_dates=delay, keep_d_frac=keep,
                       ks2_sizing=ks2)
        first = res.first_account_payouts
        assert arr.net_payouts_first[p] == pytest.approx(sum(x.net_usd for x in first),
                                                         abs=1e-9)
        assert arr.n_payouts_first[p] == len(first)
        assert arr.first_payout_day[p] == (first[0].day_index if first else -1)
        assert arr.first_breach_day[p] == (-1 if res.first_breach_day is None
                                           else res.first_breach_day)
        assert arr.halt_day[p] == (-1 if res.halt_day is None else res.halt_day)
        assert arr.n_breaches[p] == res.n_breaches
        assert arr.net_payouts_all[p] == pytest.approx(sum(x.net_usd for x in res.payouts),
                                                       abs=1e-9)
        assert arr.first_ruin_day[p] == (-1 if res.first_ruin_day is None
                                         else res.first_ruin_day)
        events["pay"] += bool(first)
        events["breach"] += res.n_breaches > 0
        events["halt"] += res.halt_day is not None
        events["ruin"] += res.first_ruin_day is not None
    assert events["pay"] > 0  # the comparison covers payouts, and breaches or halts
    assert events["halt"] > 0 if ks else events["breach"] > 0
    assert events["ruin"] >= events["breach"]


def test_bootstrap_is_seeded_and_in_range() -> None:
    a = bootstrap_indices(30, 20, 50, 10, 3)
    assert (a == bootstrap_indices(30, 20, 50, 10, 3)).all()
    assert not (a == bootstrap_indices(30, 20, 50, 10, 4)).all()
    assert a.min() >= 0 and a.max() < 30
    steps = (a[:, 1:] - a[:, :-1]) % 30
    assert 0.80 < (steps == 1).mean() < 0.97  # blocks continue with probability about 0.9


def test_simulate_payouts_is_deterministic_by_seed() -> None:
    base = _base_days(40, 5)
    kw = dict(path_type="standard", dll=False, n_paths=200, horizon=63, block_mean=5)
    a = simulate_payouts(base, ACCOUNT_50K, seed=9, **kw)
    assert asdict(a) == asdict(simulate_payouts(base, ACCOUNT_50K, seed=9, **kw))
    assert asdict(a) != asdict(simulate_payouts(base, ACCOUNT_50K, seed=10, **kw))


def test_ks_pair_is_one_draw_and_equals_two_calls() -> None:
    base = _base_days(40, 5)
    kw = dict(path_type="standard", dll=False, n_paths=200, horizon=63, block_mean=5, seed=4)
    pair = simulate_payouts_pair(base, ACCOUNT_50K, **kw)
    assert set(pair) == {True, False}
    for ks in (True, False):
        assert asdict(pair[ks]) == asdict(simulate_payouts(base, ACCOUNT_50K, ks=ks, **kw))
    # the KS1 stop always comes first (finding 2): no breach with the switches on; ruin (D-01)
    # also counts D falling to 0.25 x MLL at a close, which the switches do not prevent
    assert pair[True].breach_only_prob == 0.0
    assert pair[False].breach_only_prob > 0.0
    for ks in (True, False):
        assert pair[ks].ruin_prob >= pair[ks].breach_only_prob
        assert pair[ks].ks2_sizing  # the verdict reading (False) keeps KS2's sizing on


def test_payouts_never_trip_ks2_under_the_keep_d_policy() -> None:
    base = _base_days(40, 11)
    idx = bootstrap_indices(len(base), 30, 120, 5, 3)
    seen = 0
    for p in range(idx.shape[0]):
        res = run_path([base[i] for i in idx[p]], ACCOUNT_50K, path_type="standard", dll=False,
                       ks=False)
        for pay in res.payouts:
            before = res.balance[pay.day_index - 1] if pay.day_index else 0.0
            assert before - pay.amount_usd >= 0.5 * ACCOUNT_50K.mll_usd - 1e-9
            seen += 1
    assert seen > 0


def test_five_copied_accounts_are_one_draw() -> None:
    base = _base_days(40, 5)
    kw = dict(path_type="consistency", dll=True, n_paths=200, horizon=63, block_mean=5, seed=2)
    one = simulate_payouts(base, ACCOUNT_50K, n_accounts=1, ks=False, **kw)
    five = simulate_payouts(base, ACCOUNT_50K, n_accounts=5, ks=False, **kw)
    for name in ("monthly_net_mean", "monthly_net_median", "monthly_net_p10", "monthly_net_p90"):
        assert getattr(five, name) == pytest.approx(5 * getattr(one, name), abs=1e-9)
    assert five.ruin_prob == one.ruin_prob and five.halt_prob == one.halt_prob
    assert five.expected_resets == one.expected_resets
    assert one.monthly_net_mean > 0 and five.n_accounts == 5


def test_summary_monthly_scale_and_150k_runs() -> None:
    base = days_of(STANDARD)
    s = simulate_payouts(base, ACCOUNT_50K, path_type="standard", dll=False, n_paths=50,
                         horizon=42, block_mean=5, n_accounts=1, ks=False, seed=1)
    assert s.horizon == 42 and s.n_paths == 50 and s.ruin_prob == 0.0
    big = simulate_payouts(base, ACCOUNT_150K, path_type="standard", dll=True, n_paths=50,
                           horizon=42, block_mean=5, n_accounts=1, ks=False, seed=1)
    assert big.account == "150K" and big.ruin_prob == 0.0


# ---- design review D-01: ruin = a breach or D <= 0.25 x MLL at a close ---------------------------
def test_a_drift_to_the_ks2b_level_is_ruin_without_a_breach() -> None:
    # ZN, one contract: D 2,000 -> 1,400 -> 900 -> 450 at the third close (<= 0.25 x 2,000)
    res = run_path(days_of([-600, -500, -450, 10]), ACCOUNT_50K, path_type="standard",
                   dll=False, ks=False)
    assert res.first_ruin_day == 2
    assert res.first_breach_day is None and res.status == "active"
    # exactly at the level counts (D 500 at the close): <=
    at = run_path(days_of([-1000, -500]), ACCOUNT_50K, path_type="standard", dll=False,
                  ks=False)
    assert at.first_ruin_day == 1 and at.first_breach_day is None


def test_a_breach_is_both_ruin_and_breach() -> None:
    days = [DayRecord(D0, (tr(-100.0, -2000.0),)), DayRecord(D0 + timedelta(1), (tr(50.0),))]
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    assert res.first_breach_day == 0 and res.first_ruin_day == 0


def test_summary_ruin_and_breach_only_hand_computed() -> None:
    # every date loses $100 (ZN, 1 contract): D at the close falls 100 a date; D 500 after 15
    # dates (index 14) -> ruin; the floor (-2,000) is reached after 20 dates (index 19)
    base = days_of([-100.0] * 30)
    kw = dict(path_type="standard", dll=False, n_paths=40, block_mean=5, n_accounts=1,
              ks=False, seed=3)
    short = simulate_payouts(base, ACCOUNT_50K, horizon=17, **kw)
    assert (short.ruin_prob, short.breach_only_prob) == (1.0, 0.0)  # ruined, never breached
    long = simulate_payouts(base, ACCOUNT_50K, horizon=25, **kw)
    assert (long.ruin_prob, long.breach_only_prob) == (1.0, 1.0)  # the breach counts as both
    assert short.ks2_sizing and not short.ks  # the verdict reading


def test_the_verdict_reading_keeps_ks2_sizing_and_drops_the_stops() -> None:
    mnq = TradeRecord("MNQ", "h60", D0, 1, 10.0, 0.0, 10.0, 1.0, 0.0, 0.5, 0.1)
    days = days_of([-550, -430, -120]) + [DayRecord(D0 + timedelta(3), (mnq,))]
    verdict = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False,
                       ks2_sizing=True)
    assert verdict.contracts[3] == (5,)  # D 900 < 0.5 x MLL: KS2 halves the size (10 -> 5)
    # KS1 off: the day's intraday worst is not cut at 0.30 x D_open
    stop = [DayRecord(D0, (tr(-200.0, -700.0),))]
    assert run_path(stop, ACCOUNT_50K, path_type="standard", dll=False, ks=False,
                    ks2_sizing=True).day_pnl == (-200.0,)
    assert run_path(stop, ACCOUNT_50K, path_type="standard", dll=False,
                    ks=True).day_pnl == (-600.0,)


# ---- design review D-03 and D-08a in the re-sizing ---------------------------------------------
def mnq_leg(k: int, *, pnl: float = 0.0, contracts: int = 1, q_c: int | None = None,
            day: date = D0) -> TradeRecord:
    """MNQ, sigma 70 ticks x $0.50 = $35, loss 100 + cost 3; entries 30 minutes apart, each
    closed before the next (no capacity or concurrency effect)."""
    return TradeRecord("MNQ", "h60", day, contracts, pnl, min(pnl, 0.0), 70.0, 100.0, 3.0, 0.5,
                       0.1, "K1", (540 + 30 * k) * MIN, (560 + 30 * k) * MIN, q_c)


def test_resizing_spends_the_daily_budget_hand_computed() -> None:
    day1 = DayRecord(D0, tuple(mnq_leg(k) for k in range(6)))
    day2 = DayRecord(D0 + timedelta(1), (mnq_leg(0, day=D0 + timedelta(1)),))
    res = run_path([day1, day2], ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    # budget 200^2 = 40,000: 3 (uses 105^2 = 11,025) -> 28,975; 3 -> 17,950;
    # floor(133.98 / 35) = 3 -> 3 -> 6,925; floor(83.22 / 35) = 2 -> 2 (4,900) -> 2,025;
    # floor(45 / 35) = 1 -> 1 (1,225) -> 800; floor(28.28 / 35) = 0 -> refused.
    assert res.contracts[0] == (3, 3, 3, 2, 1, 0)
    assert res.contracts[1] == (3,)  # the next date starts with a new budget


def test_resizing_reprices_the_contracts_beyond_q_c() -> None:
    # Engine record: 3 contracts at q_c 1, net $10.00 a contract, which already holds the
    # engine's surcharge 2 x 2 / 3 ticks x $0.50 = $0.6667 a contract. Re-sized by the budget to
    # 3, 3, 3, 2, 1: at 2, + 0.50 x (4/3 - 1) = +$0.1667 a contract; at 1, + 0.50 x 4/3 = +$0.6667
    legs = tuple(mnq_leg(k, pnl=10.0, contracts=3, q_c=1) for k in range(6))
    res = run_path([DayRecord(D0, legs)], ACCOUNT_50K, path_type="standard", dll=False,
                   ks=False)
    assert res.contracts[0] == (3, 3, 3, 2, 1, 0)
    assert res.day_pnl[0] == pytest.approx(90.0 + 2 * (10.0 + 0.5 / 3) + (10.0 + 2.0 / 3),
                                           abs=1e-9)  # 121.00
    plain = tuple(mnq_leg(k, pnl=10.0, contracts=3) for k in range(6))  # no q_c: no re-pricing
    flat = run_path([DayRecord(D0, plain)], ACCOUNT_50K, path_type="standard", dll=False,
                    ks=False)
    assert flat.day_pnl[0] == pytest.approx(120.0, abs=1e-9)
    assert legs[0].resize_adjustment_usd(3) == 0.0
    with pytest.raises(ValueError, match="bad_q_c"):
        TradeRecord("MNQ", "h60", D0, 0, 1.0, 0.0, 70.0, 100.0, 3.0, 0.5, 0.1, q_c=1)


# ---- code review C-09: the tier at the prior session's close ----------------------------------
def _micro(root: str, day: date, pnl: float = 0.0) -> TradeRecord:
    """One micro leg (1 tenth a contract, product cap 10) with tiny risk numbers, so only the
    product cap and the tier's capacity bind; times unknown (every earlier leg counts as open)."""
    from ml_route_v2.portfolio import vehicle_facts

    f = vehicle_facts(root)
    return TradeRecord(root, "h60", day, 1, pnl, min(pnl, 0.0), 0.1, 0.1, 0.1,
                       f.tick_value_usd, f.lot_equiv)


def test_the_tier_is_read_at_the_prior_close_before_the_payout_debit() -> None:
    """V2.8: capacity comes from the tier at the prior session's closing balance. Days 0-4 win
    $600 each (balance $3,000: tier 5 lots); day 5 requests $1,500 (balance $1,500: tier 3 lots)
    and holds five micro legs. At the prior close's tier, 5.0 - 0.1 lots = 49 tenths: 10, 10, 10,
    10, 9 contracts (after the debit it would be 29: 10, 10, 9, 0, 0). MYM's 9 contracts earn
    $10 each: balance $1,590. Days 6-10 win $150 each ($2,340); day 11 requests
    min($2,000, 50% x 2,340, 2,340 - 1,000) = $1,170. The vectorized path agrees."""
    roots = ("MNQ", "MGC", "MCL", "M2K", "MYM")
    d5 = D0 + timedelta(5)
    days = days_of([600] * 5 + [None] + [150] * 5 + [None])
    days[5] = DayRecord(d5, tuple(_micro(r, d5, 10.0 if r == "MYM" else 0.0) for r in roots))
    res = run_path(days, ACCOUNT_50K, path_type="standard", dll=False, ks=False)
    assert [p.day_index for p in res.payouts] == [5, 11]
    assert res.contracts[5] == (10, 10, 10, 10, 9)
    assert res.balance[5] == pytest.approx(1590.0, abs=1e-9)
    assert res.payouts[1].amount_usd == pytest.approx(1170.0, abs=1e-9)
    arr = simulate_paths(days, ACCOUNT_50K, np.arange(len(days))[None, :],
                         path_type="standard", dll=False, ks=False)
    assert arr.n_payouts_first.tolist() == [2]
    assert arr.net_payouts_first[0] == pytest.approx((1500.0 + 1170.0) * ACCOUNT_50K.split,
                                                     abs=1e-9)
