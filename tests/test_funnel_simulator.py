"""Tests for funnel/simulator.py (Stage B, Task 3): the Combine -> XFA -> payouts
Monte Carlo loop.

Every stub generator below is deliberately trivial (T=1 segment per day, fixed
entry/exit minutes) so the funnel arithmetic can be traced and predicted by hand
before the code runs, per the no-peeking rule: expected values here come from
probability theory or plain arithmetic on the stub's own constants, never from
observing what the simulator returns.
"""

from __future__ import annotations

import math
import os
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np
import pytest

from funnel.null_generator import DayDraws
from funnel.simulator import (
    CostBook,
    FunnelConfig,
    RunResult,
    run_many,
    run_one,
    stability_ladder,
    summarize,
)
from rules.xfa_rules import PayoutPath


# ============================================================== shared stubs ====
class _ZeroCostBook(CostBook):
    """A CostBook whose side_cents is always 0. Never calls super().__init__: no
    real SlippageTable is needed since side_cents is fully overridden."""

    def __init__(self) -> None:
        pass

    def side_cents(self, minute_ct: int, micros: int) -> int:
        return 0


def _day_draws(pnl: np.ndarray, adverse: np.ndarray) -> DayDraws:
    """Build a T=1 DayDraws from (n_days, 1) pnl/adverse arrays; entry/exit minute
    fixed at 600/660 CT, day_index and side are unused by the funnel arithmetic
    here but must be present and shaped correctly."""
    n_days = pnl.shape[0]
    entry = np.full((n_days, 1), 600, dtype=np.int64)
    exitm = np.full((n_days, 1), 660, dtype=np.int64)
    side = np.ones((n_days, 1), dtype=np.int64)
    return DayDraws(
        day_index=np.arange(n_days), side=side, pnl_ticks=pnl, adverse_ticks=adverse,
        entry_minute_ct=entry, exit_minute_ct=exitm,
    )


class _CoinFlipDayGenerator:
    """T=1 day generator for the known-answer test: pnl_ticks per micro is +20 or
    -20 on a fair coin drawn from ``rng``; adverse_ticks = min(0, pnl_ticks) (the
    day's path is monotone: it only ever moves toward its own close, never past
    it and back). Reads no data, no state beyond the rng passed in."""

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        signs = rng.integers(0, 2, size=(n_days, 1)).astype(np.float64) * 2 - 1
        pnl = signs * 20.0
        adverse = np.minimum(0.0, pnl)
        return _day_draws(pnl, adverse)


class _ZeroPnlDayGenerator:
    """Deterministic T=1 generator: every day nets exactly 0 ticks, 0 adverse
    excursion, regardless of rng or day count."""

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        zeros = np.zeros((n_days, 1))
        return _day_draws(zeros, zeros)


class _CountingZeroPnlDayGenerator:
    """Same as ``_ZeroPnlDayGenerator`` but counts its own draw() calls, to prove
    how many times the funnel actually asks the generator for a new stream."""

    def __init__(self) -> None:
        self.calls = 0

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        self.calls += 1
        zeros = np.zeros((n_days, 1))
        return _day_draws(zeros, zeros)


class _Plus300DayGenerator:
    """Deterministic T=1 generator: every day nets +$300 at size 1 micro.
    240 ticks * 125 cents/tick (MES_TICK_VALUE_CENTS) * 1 micro = 30,000 cents."""

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        pnl = np.full((n_days, 1), 240.0)
        zeros = np.zeros((n_days, 1))
        return _day_draws(pnl, zeros)


# ====================================================== 1. known-answer combine ====
# run_many() always loads the REAL slippage table (funnel.simulator._init_worker
# calls load_slippage_table() unconditionally -- it takes no book argument), so it
# cannot host a zero-cost known-answer test. We drive run_one() directly instead,
# spread across worker processes for speed, mirroring run_many's own chunking.
_KA_CFG = FunnelConfig(
    path=PayoutPath.STANDARD, micros_per_trade=2, horizon_days=4_000, max_xfa_accounts=20,
)
_KA_GENERATOR = _CoinFlipDayGenerator()
_KA_BOOK = _ZeroCostBook()
_KA_SEED = 20_260_917


def _known_answer_chunk(indices: Sequence[int]) -> tuple[int, int]:
    """(combine_passes, combine_breaches) summed over one chunk of run indices."""
    passes = breaches = 0
    for i in indices:
        result = run_one(i, _KA_SEED, _KA_CFG, _KA_GENERATOR, _KA_BOOK)
        passes += result.combine_passes
        breaches += result.combine_breaches
    return passes, breaches


def test_combine_pass_probability_matches_random_walk_known_answer() -> None:
    """Exact random-walk known answer for the Combine.

    With micros_per_trade=2, a day's net P&L is always +/- 2 * 20 ticks * 125
    cents = +/- 5,000 cents = +/- $50: a step of the SAME fixed size every day,
    fair-coin signed. Costs are zero (``_ZeroCostBook``). So the Combine's
    balance, in units of one $50 step, is exactly a symmetric simple random walk:

    - The trailing MLL is $2,000 = 40 steps, locking (capping) at the $50,000
      start (0 net profit = 0 steps) once the running max of profit reaches
      +$2,000 = +40 steps. That is the classic "trailing stop" problem: for a
      symmetric random walk, P(running max reaches +N before a pullback of N
      from that max) = (N / (N + 1)) ** N. With N = 40:
        ln(40/41)       = -0.024693
        40 * ln(40/41)  = -0.98772
        exp(-0.98772)   =  0.37242   <- P(the walk ever reaches +40 first)
    - The raised target is $3,000 = 60 steps; the best-day rule never raises it
      here (a $50 day is nowhere near 50% of $3,000, so effective target stays
      $3,000 throughout). Once the max reaches +40, the floor locks at exactly
      0 steps (breakeven) and never moves again, so passing now needs a plain
      gambler's-ruin race from +40 to +60 before falling back to 0 -- fixed
      absorbing barriers at 0 and 60, starting at 40:
        P(hit 60 before 0 | start 40) = 40 / 60 = 2/3
    - P(pass) = 0.37242 * 2/3 = 0.24828.

    Why the intraday real-time MLL check (adverse_ticks = min(0, pnl_ticks),
    evaluated mid-trade before the exit P&L is booked) doesn't change this
    answer: with a zero-cost book and T=1, the day's only real-time check sees
    equity = balance_after_entry_cost(=balance, cost 0) + worst_unrealized. When
    pnl_ticks >= 0, worst_unrealized = 0, so this equity equals the PRE-trade
    balance, which is <= the post-trade (close) balance -- a real-time breach
    here would already have been a breach at the previous close, so it adds no
    new information. When pnl_ticks < 0, worst_unrealized = pnl_ticks itself (the
    day is monotone down to its close, by construction), so equity at the
    real-time check exactly equals balance_after_entry_cost + full trade P&L,
    which is exactly what close_trading_day will see too (exit cost is also 0).
    Either way, checking mid-trade gives the identical breach verdict as
    checking only at the close: the path is monotone within the day, so there
    is no intraday excursion the close doesn't already reflect.
    """
    target_resolved = 4_000
    workers = min(16, os.cpu_count() or 1)
    chunk_size = 25
    batch_runs = 2_000
    max_total_runs = 20_000

    total_passes = total_breaches = 0
    start = 0
    while total_passes + total_breaches < target_resolved and start < max_total_runs:
        indices = list(range(start, start + batch_runs))
        chunks = [indices[k : k + chunk_size] for k in range(0, len(indices), chunk_size)]
        with ProcessPoolExecutor(workers) as pool:
            for passes, breaches in pool.map(_known_answer_chunk, chunks):
                total_passes += passes
                total_breaches += breaches
        start += batch_runs

    n = total_passes + total_breaches
    assert n >= target_resolved, (
        f"only {n} resolved Combine attempts after {start} runs (need >= {target_resolved})"
    )

    ln_ratio = math.log(40 / 41)
    p_reach_40_before_drawdown = math.exp(40 * ln_ratio)
    p_pass_expected = p_reach_40_before_drawdown * (2 / 3)
    assert p_pass_expected == pytest.approx(0.24828, abs=1e-5)

    p_hat = total_passes / n
    se = math.sqrt(p_pass_expected * (1 - p_pass_expected) / n)
    assert abs(p_hat - p_pass_expected) <= 4 * se, (
        f"p_hat={p_hat:.5f} expected={p_pass_expected:.5f} se={se:.5f} n={n} "
        f"passes={total_passes} breaches={total_breaches}"
    )


# ===================================================== 2. fee accounting ====
def test_fee_accounting_hand_computed_on_zero_pnl_stub() -> None:
    """42 trading days, +$0/day, zero costs. API fee bills on day%21==0 -> days 0
    and 21 (2 * $14.50 = 2,900 cents). One Combine attempt starts day 0 (fee
    $49.00) and, since 0 P&L never breaches or passes, is rebilled at
    combine_bill_day = 0 + 21 = 21 (fee $49.00 again; day 42 would be the next
    bill but the horizon is range(42) = days 0..41, so day 42 never happens).
    Total fees = 2,900 (api) + 2 * 4,900 (combine) = 12,700 cents. No pass ->
    no XFA -> no payouts: monthly_payout_cents is all zero, net_cents = -12,700.
    """
    cfg = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=42, max_xfa_accounts=5,
    )
    result = run_one(0, 1, cfg, _ZeroPnlDayGenerator(), _ZeroCostBook())

    assert result.combine_attempts == 1
    assert result.combine_passes == 0
    assert result.combine_breaches == 0
    assert result.fee_cents == 12_700
    assert result.net_cents == -12_700
    assert result.monthly_payout_cents == (0, 0)


# ===================================================== 3. correlated vs independent ====
def test_correlated_draws_market_once_independent_draws_per_account() -> None:
    """correlated=True: every account (the Combine, any XFA) trades the SAME
    stream, drawn once as ``market`` in run_one -> exactly 1 draw() call, no
    matter how many accounts are created. correlated=False: every new account
    calls stream_for_new_account(), which draws fresh -> 1 (market) + 1 per
    account creation (each Combine attempt and each XFA activation calls it
    exactly once). Using a 0-P&L stub over a short horizon, the Combine never
    resolves (no pass, no breach), so exactly 1 account (that Combine) is ever
    created: independent calls = 1 + 1 = 2 > 1 = correlated calls."""
    cfg_correlated = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=5,
        max_xfa_accounts=5, correlated=True,
    )
    gen_correlated = _CountingZeroPnlDayGenerator()
    run_one(0, 1, cfg_correlated, gen_correlated, _ZeroCostBook())
    assert gen_correlated.calls == 1

    cfg_independent = replace(cfg_correlated, correlated=False)
    gen_independent = _CountingZeroPnlDayGenerator()
    result = run_one(0, 1, cfg_independent, gen_independent, _ZeroCostBook())

    expected_calls = 1 + result.combine_attempts + result.xfa_activated
    assert result.combine_attempts == 1
    assert result.xfa_activated == 0
    assert expected_calls == 2
    assert gen_independent.calls == expected_calls
    assert gen_independent.calls > gen_correlated.calls


# ===================================================== 4. payout path ====
def test_standard_payout_path_hand_traced() -> None:
    """+$300/day, zero costs, Standard path.

    Combine: target $3,000 at $300/day -> cumulative profit = (day_index + 1) *
    $300 reaches $3,000 exactly when day_index + 1 = 10, i.e. at the close of
    day index 9 (the 10th trading day) -> first_pass_day = 9. Best-day rule:
    effective target = max($300,000, ceil($300 * 10,000 / 5,000)) =
    max($300,000, $600) = $300,000 unchanged -- never binds.

    The XFA activates and starts trading the day AFTER the pass: day 10. The
    Standard path needs 5 winning days (net >= $150); every $300 day qualifies,
    so the window is satisfied at the close of the XFA's 5th trading day
    (days 10, 11, 12, 13, 14) -> the payout is requested and granted at the
    close of day 14 -> first_payout_day = 14. Balance at that point =
    5 * $300 = $1,500; amount = min($2,000 per-request cap, 50% of $1,500) =
    $750 = 75,000 cents, which lands in monthly bucket 0 (day 14 // 21 == 0).

    Fees: combine monthly (day 0, $49.00) + api monthly (day 0, $14.50, and no
    second bill: day 21 is outside horizon_days=15) + XFA activation (day 9,
    $149.00) = 4,900 + 1,450 + 14,900 = 21,250 cents. The combine's own
    combine_bill_day (21) is also never reached. max_xfa_accounts=1 so that,
    once the XFA activates, no SECOND Combine attempt starts on day 10 (the
    run_one loop starts a new Combine whenever one is None AND fewer than
    max_xfa_accounts XFAs are live -- with the default of 5 a second attempt
    would start immediately and add its own monthly fee, which is not part of
    this hand trace).
    """
    cfg = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=15, max_xfa_accounts=1,
    )
    result = run_one(0, 1, cfg, _Plus300DayGenerator(), _ZeroCostBook())

    assert result.first_pass_day == 9
    assert result.first_payout_day == 14
    assert result.payout_count == 1
    assert result.payout_cents == 75_000
    assert result.monthly_payout_cents == (75_000,)
    assert result.xfa_activated == 1
    assert result.combine_passes == 1
    assert result.combine_breaches == 0
    assert result.fee_cents == 21_250


# ===================================================== 5. determinism / chunking ====
def test_run_many_agrees_across_workers_and_chunk_sizes() -> None:
    """run_many's own docstring promises: results identical for any workers/chunk,
    because each run's RNG depends only on (base_seed, run_index)."""
    cfg = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=10, max_xfa_accounts=2,
    )
    gen = _ZeroPnlDayGenerator()

    serial = run_many(cfg, gen, n_runs=6, base_seed=4242, workers=1, chunk=2)
    parallel = run_many(cfg, gen, n_runs=6, base_seed=4242, workers=2, chunk=3)

    assert serial == parallel
    assert len(serial) == 6
    assert all(isinstance(r, RunResult) for r in serial)


# ===================================================== 6. summarize() ====
def test_summarize_hand_computed_on_three_run_results() -> None:
    """Three hand-built RunResults, horizon_days=21 (1 month, so months=1.0 and
    monthly_net_usd == net_cents / 100 exactly, no division to track by hand).

    R1: attempts=1 passes=1, net_cents=5,000-1,000=4,000 -> $40.00/mo,
        first_payout_day=5 (has payout), breach_days=().
    R2: attempts=2 passes=0 breaches=2, net_cents=0-2,000=-2,000 -> -$20.00/mo,
        first_payout_day=-1 (no payout), breach_days=((3, 1, 1),) (1 live, 1
        breached: a < 2, excluded from the "2+ live" blowup stats).
    R3: attempts=1 passes=1, net_cents=8,000-1,500=6,500 -> $65.00/mo,
        first_payout_day=4 (has payout), breach_days=((6, 2, 2),) (2 live, 2
        breached: a >= 2, included; b == a, "all live breached").

    Hand arithmetic:
      pass_rate_per_attempt = (1+0+1) / (1+2+1) = 2/4 = 0.5
      pass_rate_per_resolved_attempt = 2 / (2 + (0+2+0)) = 2/4 = 0.5
      p_run_passes_at_least_once = mean([True, False, True]) = 2/3
      p_within_horizon (has payout) = mean([True, False, True]) = 2/3
      net_of_fees.mean = (40 - 20 + 65) / 3 = 85/3 = 28.3333...
      multi_open (a>=2 rows) = [(2, 2)] from R3 only
      days_with_2plus_live_and_a_breach = len(multi_open) = 1
      share_multi_account_given_2plus_live = mean([2 >= 2]) = 1.0
      share_all_live_breached_given_2plus_live = mean([2 == 2]) = 1.0
      p_run_has_same_day_multi_breach = mean([False, False, True]) = 1/3
      breached_count_histogram_given_2plus_live (max_xfa_accounts=5):
        {"1": 0, "2": 1, "3": 0, "4": 0, "5": 0}
    """
    cfg = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=21, max_xfa_accounts=5,
    )
    r1 = RunResult(
        combine_attempts=1, combine_passes=1, combine_breaches=0,
        first_pass_day=3, first_payout_day=5, payout_count=1, payout_cents=5_000,
        fee_cents=1_000, monthly_payout_cents=(5_000,), xfa_activated=1, xfa_breaches=0,
        breach_days=(), xfa_account_days=10, max_concurrent_xfa=1,
    )
    r2 = RunResult(
        combine_attempts=2, combine_passes=0, combine_breaches=2,
        first_pass_day=-1, first_payout_day=-1, payout_count=0, payout_cents=0,
        fee_cents=2_000, monthly_payout_cents=(0,), xfa_activated=0, xfa_breaches=0,
        breach_days=((3, 1, 1),), xfa_account_days=0, max_concurrent_xfa=0,
    )
    r3 = RunResult(
        combine_attempts=1, combine_passes=1, combine_breaches=0,
        first_pass_day=2, first_payout_day=4, payout_count=1, payout_cents=8_000,
        fee_cents=1_500, monthly_payout_cents=(8_000,), xfa_activated=1, xfa_breaches=1,
        breach_days=((6, 2, 2),), xfa_account_days=15, max_concurrent_xfa=2,
    )
    summary = summarize([r1, r2, r3], cfg)

    assert summary["combine"]["pass_rate_per_attempt"] == pytest.approx(0.5)
    assert summary["combine"]["pass_rate_per_resolved_attempt"] == pytest.approx(0.5)
    assert summary["combine"]["p_run_passes_at_least_once"] == pytest.approx(2 / 3)
    assert summary["combine"]["mean_attempts_per_run"] == pytest.approx(4 / 3)
    assert summary["first_payout"]["p_within_horizon"] == pytest.approx(2 / 3)
    assert summary["monthly_income_usd"]["net_of_fees"]["mean"] == pytest.approx(85 / 3)
    assert summary["blowups"]["days_with_2plus_live_and_a_breach"] == 1
    assert summary["blowups"]["share_multi_account_given_2plus_live"] == pytest.approx(1.0)
    assert summary["blowups"]["share_all_live_breached_given_2plus_live"] == pytest.approx(1.0)
    assert summary["blowups"]["p_run_has_same_day_multi_breach"] == pytest.approx(1 / 3)
    assert summary["blowups"]["breached_count_histogram_given_2plus_live"] == {
        "1": 0, "2": 1, "3": 0, "4": 0, "5": 0,
    }


# ===================================================== 7. stability_ladder() ====
def _flat_run_result(combine_passes: int) -> RunResult:
    """Every field constant except combine_passes (0 or 1), so every headline
    metric except pass_rate_per_attempt has zero variance (SE=0, delta=0) at
    every N, and only pass_rate_per_attempt drives the stability verdict."""
    return RunResult(
        combine_attempts=1, combine_passes=combine_passes, combine_breaches=0,
        first_pass_day=-1, first_payout_day=-1, payout_count=0, payout_cents=0,
        fee_cents=0, monthly_payout_cents=(0,), xfa_activated=0, xfa_breaches=0,
        breach_days=(), xfa_account_days=0, max_concurrent_xfa=0,
    )


def test_stability_ladder_small_n_unstable_larger_n_stable() -> None:
    """20,000 RunResults with combine_passes alternating 0, 1, 0, 1, ... (attempts
    always 1). For any EVEN N, sum(passes) = N/2 exactly, so
    pass_rate_per_attempt = 0.5 for every even N in the ladder -- delta_to_next
    is exactly 0 always. What differs is the Monte Carlo SE:

    residual_i = passes_i - 0.5 * attempts_i = +/-0.5 (half the values +0.5,
    half -0.5, for any even N), so sample variance (ddof=1) = N * 0.25 / (N-1)
    and SE(N) = sqrt(variance/N) = 0.5 / sqrt(N-1) exactly.

    Stability needs 1.96 * SE(N) <= tol = 0.01 (STABILITY_RATE_TOL), i.e.
    SE(N) <= 0.0051020..., i.e. 0.5/sqrt(N-1) <= 0.0051020, i.e.
    N - 1 >= (0.5/0.0051020)^2 = 9,603.8, i.e. N >= 9,605.

    So N=20 (SE = 0.5/sqrt(19) = 0.1147, 1.96*SE = 0.2248 >> 0.01) must be
    UNSTABLE, and N=15,000 (SE = 0.5/sqrt(14,999) = 0.004083,
    1.96*SE = 0.008003 <= 0.01) must be STABLE, with delta_to_next = 0 <= tol
    at every rung. Every other headline metric is constant (SE=0, delta=0)
    by construction, so it never blocks stability.
    """
    results = [_flat_run_result(i % 2) for i in range(20_000)]
    cfg = FunnelConfig(
        path=PayoutPath.STANDARD, micros_per_trade=1, horizon_days=21, max_xfa_accounts=5,
    )
    ladder = stability_ladder(results, cfg, ladder=(20, 15_000, 20_000))

    rows_by_n = {row["n"]: row for row in ladder["ladder"]}
    assert rows_by_n[20]["stable"] is False
    assert rows_by_n[20]["checks_vs_next"]["pass_rate_per_attempt"]["ok"] is False
    assert rows_by_n[15_000]["stable"] is True
    assert rows_by_n[15_000]["checks_vs_next"]["pass_rate_per_attempt"]["ok"] is True
    assert ladder["stable_n"] == 15_000


# ===================================================== 8. FunnelConfig validation ====
def test_funnel_config_refuses_non_positive_micros_per_trade() -> None:
    with pytest.raises(ValueError):
        FunnelConfig(path=PayoutPath.STANDARD, micros_per_trade=0)
