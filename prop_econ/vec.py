"""Vectorized Stage E.19 funnel (sim_spec sections 2 to 4) over ShockSet rows.

The same rules as the scalar reference prop_econ/funnel.py, written as numpy steps over many paths
per day, chunked over paths to bound memory. Results equal the scalar reference path for path
(tests pin them to 1e-9 dollars): every arithmetic expression below mirrors its scalar twin
operation for operation. Finished paths are dropped from the working arrays as they end.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from prop_econ.funnel import (
    ATTEMPT_BREACH,
    ATTEMPT_PASS,
    ATTEMPT_TIMEOUT,
    DLL_TIE_USD,
    XFA_BREACH,
    XFA_CALLUP,
    XFA_HORIZON,
    XFA_PAYOUT_LIMIT,
    FunnelError,
    PhaseSpec,
    Policy,
    callup_after,
    check_row,
    combine_phase,
    payout_cap,
    payout_rules,
    xfa_phase,
)
from prop_econ.rules import PayoutRules, SizeRules
from prop_econ.types import MICROS_PER_FULL, ProductSpec, ShockSet

DEFAULT_CHUNK = 5000


@dataclass(frozen=True)
class AttemptPool:
    """Combine attempt outcomes, one per ShockSet row."""

    passed: np.ndarray  # bool
    length: np.ndarray  # int32, trading days including the pass / breach day
    reason: np.ndarray  # int8, ATTEMPT_* codes

    @property
    def n(self) -> int:
        return int(self.passed.shape[0])


@dataclass(frozen=True)
class XfaPool:
    """XFA life outcomes, one per ShockSet row (payout arrays padded to max_payouts)."""

    payout_days: np.ndarray  # int32 (n, max_payouts), start-of-day index, -1 padded
    payout_gross: np.ndarray  # float64 (n, max_payouts), 0 padded
    n_payouts: np.ndarray  # int32, all payouts (may exceed max_payouts: see overflow)
    total_gross: np.ndarray  # float64, all payouts
    first_payout_day: np.ndarray  # int32, -1 when none
    end_day: np.ndarray  # int32, elapsed trading days
    end_reason: np.ndarray  # int8, XFA_* codes
    end_balance: np.ndarray  # float64
    overflow: np.ndarray  # bool

    @property
    def n(self) -> int:
        return int(self.n_payouts.shape[0])

    @property
    def max_payouts(self) -> int:
        return int(self.payout_days.shape[1])


@dataclass(frozen=True)
class _Products:
    sigma_full: np.ndarray
    rt_full: np.ndarray
    has_micro: np.ndarray
    sigma_micro: np.ndarray  # nan where no micro
    rt_micro: np.ndarray


def _products(specs: tuple[ProductSpec, ...]) -> _Products:
    def col(name: str) -> np.ndarray:
        return np.array([np.nan if getattr(s, name) is None else getattr(s, name) for s in specs],
                        dtype=np.float64)

    return _Products(col("sigma_full_usd"), col("rt_full_usd"),
                     np.array([s.has_micro for s in specs], dtype=bool),
                     col("sigma_micro_usd"), col("rt_micro_usd"))


def day_step_vec(balance: np.ndarray, floor: np.ndarray, p: np.ndarray, z: np.ndarray,
                 w: np.ndarray, policy: Policy, cap_minis: np.ndarray | int,
                 dll_usd: float | None, prods: _Products) -> tuple[np.ndarray, np.ndarray]:
    """funnel.day_step over arrays: (pnl, breach)."""
    d_open = balance - floor
    s = policy.f * d_open
    sigma_full = prods.sigma_full[p]
    full = ~prods.has_micro[p] | (s >= sigma_full)
    sigma = np.where(full, sigma_full, prods.sigma_micro[p])
    rt = np.where(full, prods.rt_full[p], prods.rt_micro[p])
    n = s / sigma
    if policy.mode == "integer":
        n = np.floor(np.round(n, 9))
    n = np.maximum(n, 1.0)
    n = np.minimum(n, (cap_minis * np.where(full, 1, MICROS_PER_FULL)).astype(np.float64))
    mu = sigma * policy.drift + (policy.k * rt if policy.cost_in_drift else 0.0)
    close = n * (sigma * z + mu) - n * policy.k * rt
    worst = n * sigma * w - n * policy.k * rt
    if dll_usd is None:
        dll_hit = np.zeros(balance.shape, dtype=bool)
    else:
        dll_hit = (worst <= -dll_usd) & (dll_usd < d_open - DLL_TIE_USD)
    breach = ~dll_hit & (worst <= -d_open)
    pnl = np.where(dll_hit, -(dll_usd or 0.0), np.where(breach, -d_open, close))
    return pnl, breach


def tier_cap_vec(balance: np.ndarray, phase: PhaseSpec) -> np.ndarray:
    """funnel.tier_cap over arrays."""
    cap = np.full(balance.shape, phase.tiers[-1][1], dtype=np.int64)
    for below, minis in reversed(phase.tiers[:-1]):
        inside = balance <= below if phase.boundary == "lower" else balance < below
        cap = np.where(inside, minis, cap)
    return cap


def cents_floor_vec(x: np.ndarray) -> np.ndarray:
    return np.floor(np.round(x * 100.0, 6)) / 100.0


def _chunk_columns(shocks: ShockSet, r0: int, r1: int, days: int) -> tuple[np.ndarray, ...]:
    """Day-major (days, rows) copies of one chunk so each day's column is contiguous."""
    return tuple(np.ascontiguousarray(a[r0:r1, :days].T) for a in (shocks.z, shocks.w, shocks.prod))


def _check_shocks(shocks: ShockSet, days: int) -> None:
    if shocks.n_paths:
        check_row(shocks, 0, days)


# --------------------------------------------------------------------------- Combine ----
def _target_met_vec(balance: np.ndarray, best: np.ndarray, rules: SizeRules) -> np.ndarray:
    c, inclusive = rules.combine, rules.glob.combine_consistency_inclusive
    if c.consistency_type == "best_day_max_frac_of_target":
        if inclusive:
            return balance >= np.maximum(c.profit_target_usd, best / c.consistency_frac)
        return (balance >= c.profit_target_usd) & (balance > best / c.consistency_frac)
    if c.consistency_type == "best_day_max_frac_of_profit":
        limit = c.consistency_frac * balance
        within = best <= limit if inclusive else best < limit
        return (balance >= c.profit_target_usd) & within
    return balance >= c.profit_target_usd


def simulate_attempts(shocks: ShockSet, rules: SizeRules, policy: Policy,
                      chunk: int = DEFAULT_CHUNK) -> AttemptPool:
    """funnel.run_attempt for every row of ``shocks``."""
    phase = combine_phase(rules, policy)
    max_days = policy.attempt_max_days
    _check_shocks(shocks, max_days)
    n_all = shocks.n_paths
    passed = np.zeros(n_all, dtype=bool)
    length = np.full(n_all, max_days, dtype=np.int32)
    reason = np.full(n_all, ATTEMPT_TIMEOUT, dtype=np.int8)
    prods = _products(shocks.products)
    c = rules.combine
    for r0 in range(0, n_all, chunk):
        r1 = min(r0 + chunk, n_all)
        z_t, w_t, p_t = _chunk_columns(shocks, r0, r1, max_days)
        ids = np.arange(r1 - r0)
        balance = np.zeros(ids.size)
        floor = np.full(ids.size, -c.mll_usd)
        best = np.full(ids.size, -np.inf)
        for d in range(max_days):
            if ids.size == 0:
                break
            pnl, breach = day_step_vec(balance, floor, p_t[d, ids], z_t[d, ids], w_t[d, ids],
                                       policy, c.max_minis, phase.dll_usd, prods)
            balance = balance + pnl
            best = np.maximum(best, pnl)
            floor = np.maximum(floor, np.minimum(balance - c.mll_usd, c.mll_floor_max_rel_usd))
            ok = ~breach & _target_met_vec(balance, best, rules) if d + 1 >= c.min_trading_days \
                else np.zeros(ids.size, dtype=bool)
            done = breach | ok
            if done.any():
                gid = r0 + ids[done]
                length[gid] = d + 1
                passed[gid] = ok[done]
                reason[gid] = np.where(ok[done], ATTEMPT_PASS, ATTEMPT_BREACH)
                keep = ~done
                ids, balance, floor, best = ids[keep], balance[keep], floor[keep], best[keep]
    return AttemptPool(passed=passed, length=length, reason=reason)


# ------------------------------------------------------------------------------- XFA ----
class _XfaState:
    """Working arrays of the live paths of one chunk (local, mutable)."""

    FIELDS = ("ids", "balance", "floor", "close", "fixed", "npay", "win_n", "win_net",
              "win_days", "win_best")

    def __init__(self, n: int, start: float, mll: float) -> None:
        self.ids = np.arange(n)
        self.balance = np.full(n, start)
        self.floor = np.full(n, start - mll)
        self.close = np.full(n, start)
        self.fixed = np.zeros(n, dtype=bool)
        self.npay = np.zeros(n, dtype=np.int64)
        self.win_n = np.zeros(n, dtype=np.int64)
        self.win_net = np.zeros(n)
        self.win_days = np.zeros(n, dtype=np.int64)
        self.win_best = np.full(n, -np.inf)

    def reset_window(self, mask: np.ndarray) -> None:
        self.win_n = np.where(mask, 0, self.win_n)
        self.win_net = np.where(mask, 0.0, self.win_net)
        self.win_days = np.where(mask, 0, self.win_days)
        self.win_best = np.where(mask, -np.inf, self.win_best)

    def keep(self, mask: np.ndarray) -> None:
        for name in self.FIELDS:
            setattr(self, name, getattr(self, name)[mask])


@dataclass(frozen=True)
class _XfaOut:
    pay_days: np.ndarray
    pay_gross: np.ndarray
    npay: np.ndarray
    total: np.ndarray
    first: np.ndarray
    end_day: np.ndarray
    reason: np.ndarray
    end_balance: np.ndarray
    overflow: np.ndarray


def _eligible_vec(st: _XfaState, pr: PayoutRules, inclusive: bool) -> np.ndarray:
    if pr.path == "standard":
        ok = st.win_n >= pr.winning_days
        if pr.net_positive_since_last:
            ok &= np.where(st.npay > 0, st.win_net > 0, st.balance > 0)
        return ok
    limit = pr.best_day_max_frac * st.win_net
    within = st.win_best <= limit if inclusive else st.win_best < limit
    return (st.win_days >= pr.traded_days) & (st.win_net > 0) & within


def _finish(st: _XfaState, mask: np.ndarray, out: _XfaOut, r0: int, end_day: int,
            reason: np.ndarray | int) -> None:
    gid = r0 + st.ids[mask]
    out.npay[gid] = st.npay[mask]
    out.end_day[gid] = end_day
    out.reason[gid] = reason
    out.end_balance[gid] = st.balance[mask]
    st.keep(~mask)


def _request_payouts(st: _XfaState, d: int, out: _XfaOut, r0: int, rules: SizeRules,
                     policy: Policy, pr: PayoutRules, cap: float) -> np.ndarray:
    """Start-of-day payout requests; returns the mask of paths whose window skips today."""
    x, g = rules.xfa, rules.glob
    eligible = _eligible_vec(st, pr, g.xfa_consistency_inclusive)
    if not eligible.any():
        return np.zeros(st.ids.size, dtype=bool)
    amount = cents_floor_vec(np.minimum(np.minimum(cap, pr.frac_of_balance * st.balance),
                                        st.balance - policy.keep_d * x.mll_usd))
    req = eligible & (amount >= g.payout_min_request_usd)
    if not req.any():
        return req
    ri = np.flatnonzero(req)
    gid = r0 + st.ids[ri]
    slot = st.npay[ri]
    fits = slot < policy.max_payouts
    out.pay_days[gid[fits], slot[fits]] = d
    out.pay_gross[gid[fits], slot[fits]] = amount[ri][fits]
    out.overflow[gid[~fits]] = True
    out.total[gid] = out.total[gid] + amount[ri]
    out.first[gid[slot == 0]] = d
    st.npay = st.npay + req
    st.balance = np.where(req, st.balance - amount, st.balance)
    if x.mll_after_first_payout_usd is not None:
        first_now = req & (st.npay == 1)
        st.floor = np.where(first_now, x.mll_after_first_payout_usd, st.floor)
        st.fixed = st.fixed | first_now
    st.reset_window(req)
    return req if not g.payout_day_counts_toward_next_window else np.zeros(req.size, dtype=bool)


def _stop_after_payout(st: _XfaState, skip: np.ndarray, d: int, out: _XfaOut, r0: int,
                       rules: SizeRules, stop_after: int | None) -> np.ndarray:
    if stop_after is None:
        return skip
    done = st.npay >= stop_after
    if not done.any():
        return skip
    callup = rules.glob.callup
    is_callup = (callup.type == "after_n_payouts") & (st.npay[done] >= (callup.n or 0))
    _finish(st, done, out, r0, d, np.where(is_callup, XFA_CALLUP, XFA_PAYOUT_LIMIT))
    return skip[~done]


def _trade_day(st: _XfaState, skip: np.ndarray, d: int, cols: tuple[np.ndarray, ...],
               out: _XfaOut, r0: int, rules: SizeRules, policy: Policy, phase: PhaseSpec,
               pr: PayoutRules, prods: _Products) -> None:
    z_t, w_t, p_t = cols
    x = rules.xfa
    d_open = st.balance - st.floor
    if (d_open <= 0).any():
        bad = int(r0 + st.ids[np.argmax(d_open <= 0)])
        raise FunnelError(f"row {bad} day {d}: D_open <= 0 after a payout")
    cap_minis = tier_cap_vec(st.close, phase)
    pnl, breach = day_step_vec(st.balance, st.floor, p_t[d, st.ids], z_t[d, st.ids],
                               w_t[d, st.ids], policy, cap_minis, phase.dll_usd, prods)
    st.balance = st.balance + pnl
    if breach.any():
        _finish(st, breach, out, r0, d + 1, XFA_BREACH)
        pnl, skip = pnl[~breach], skip[~breach]
    add = ~skip
    if pr.path == "standard":
        st.win_n = st.win_n + (add & (pnl >= pr.winning_day_usd))
    st.win_net = np.where(add, st.win_net + pnl, st.win_net)
    st.win_days = st.win_days + add
    st.win_best = np.where(add, np.maximum(st.win_best, pnl), st.win_best)
    trailed = np.maximum(st.floor, np.minimum(st.balance - x.mll_usd, x.mll_floor_lock_usd))
    st.floor = np.where(st.fixed, st.floor, trailed)
    st.close = st.balance


def simulate_xfas(shocks: ShockSet, rules: SizeRules, policy: Policy,
                  chunk: int = DEFAULT_CHUNK) -> XfaPool:
    """funnel.run_xfa for every row of ``shocks``."""
    phase = xfa_phase(rules, policy)
    max_days, max_pay = policy.xfa_max_days, policy.max_payouts
    _check_shocks(shocks, max_days)
    pr, cap = payout_rules(rules, policy), payout_cap(rules, policy)
    stop_after = callup_after(rules)
    n_all = shocks.n_paths
    out = _XfaOut(
        pay_days=np.full((n_all, max_pay), -1, dtype=np.int32),
        pay_gross=np.zeros((n_all, max_pay)),
        npay=np.zeros(n_all, dtype=np.int32),
        total=np.zeros(n_all),
        first=np.full(n_all, -1, dtype=np.int32),
        end_day=np.zeros(n_all, dtype=np.int32),
        reason=np.zeros(n_all, dtype=np.int8),
        end_balance=np.zeros(n_all),
        overflow=np.zeros(n_all, dtype=bool),
    )
    prods = _products(shocks.products)
    for r0 in range(0, n_all, chunk):
        r1 = min(r0 + chunk, n_all)
        cols = _chunk_columns(shocks, r0, r1, max_days)
        st = _XfaState(r1 - r0, rules.xfa.start_balance_usd, rules.xfa.mll_usd)
        for d in range(max_days):
            if st.ids.size == 0:
                break
            skip = _request_payouts(st, d, out, r0, rules, policy, pr, cap)
            skip = _stop_after_payout(st, skip, d, out, r0, rules, stop_after)
            if st.ids.size == 0:
                break
            _trade_day(st, skip, d, cols, out, r0, rules, policy, phase, pr, prods)
        if st.ids.size:
            _finish(st, np.ones(st.ids.size, dtype=bool), out, r0, max_days, XFA_HORIZON)
    return XfaPool(payout_days=out.pay_days, payout_gross=out.pay_gross, n_payouts=out.npay,
                   total_gross=out.total, first_payout_day=out.first, end_day=out.end_day,
                   end_reason=out.reason, end_balance=out.end_balance, overflow=out.overflow)
