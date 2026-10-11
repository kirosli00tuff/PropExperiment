"""Scalar reference of the Stage E.19 funnel (reports/stage_e19_briefs/sim_spec.md sections 2 to
4).

One Combine attempt (``run_attempt``) or one XFA life (``run_xfa``) from one ShockSet row, written
as plain loops. This module is the specification the vectorized code (prop_econ/vec.py) is pinned
to; both share the phase set-up helpers below so that every rule is read in one place.

Time convention: day ``d`` (0-based) is the account's (d+1)-th trading day. "Elapsed" counts
(attempt ``length``, XFA ``end_day``) are the number of trading days the account traded, so an
account that ends on day d by a breach or a pass has elapsed d+1; a payout requested at the START
of day d is at elapsed d (``payout_days`` hold these d), and an XFA called up right after that
payout ends at elapsed d.

Readings the spec leaves open are marked "QUESTION" and listed in
reports/stage_e19_briefs/funnel_questions.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from prop_econ.rules import PayoutRules, SizeRules
from prop_econ.types import MICROS_PER_FULL, ProductSpec, ShockSet

TRADING_DAYS_PER_YEAR = 252
SIZE_MODES = ("continuous", "integer")
EDGE_MODES = ("zero", "sharpe")
PAYOUT_PATHS = ("standard", "consistency")
DEFAULT_MAX_DAYS = 756
DEFAULT_MAX_PAYOUTS = 64
# The DLL test "DLL < D_open" meets exact ties by construction (after one DLL stop from the trailing
# peak, D_open = MLL - DLL, which equals the DLL when MLL = 2 x DLL); float noise must not decide
# them. A tie (within this many dollars) reads as DLL >= D_open: the MLL governs, as in exact
# arithmetic, and a DLL stop always leaves D > 0.
DLL_TIE_USD = 1e-6
# "discretionary" has no automatic trigger and runs like "none" (lead, 2026-10-10 17:30)
CALLUP_TYPES = ("none", "discretionary", "after_n_payouts")

# end reasons (int codes shared with prop_econ/vec.py)
ATTEMPT_BREACH, ATTEMPT_PASS, ATTEMPT_TIMEOUT = 0, 1, 2
XFA_BREACH, XFA_CALLUP, XFA_PAYOUT_LIMIT, XFA_HORIZON = 0, 1, 2, 3


class UnsupportedRule(NotImplementedError):
    """A rule value the spec does not model; the lead decides how to model it."""


class FunnelError(RuntimeError):
    """A state the spec rules out (for example D_open <= 0 after a payout)."""


@dataclass(frozen=True)
class Policy:
    """The bot's choices and the run settings (not rules)."""

    f: float  # sizing fraction: risk target s* = f x D_open
    mode: str = "continuous"  # contracts: "continuous" or "integer" (floor)
    edge: str = "zero"  # "zero" (gross drift 0) or "sharpe" (net Sharpe ``sharpe`` after costs)
    sharpe: float = 0.0
    k: int = 1  # round trips a day (QUESTION: the spec names k only for the zero edge)
    dll_chosen: bool = False  # DLL chosen at Combine checkout: both phases, doubled caps, discounts
    payout_path: str = "standard"
    keep_d: float = 0.0  # payout policy: request leaves keep_d x MLL (0 = "max", 0.5 = keep-D)
    attempt_max_days: int = DEFAULT_MAX_DAYS
    xfa_max_days: int = DEFAULT_MAX_DAYS
    max_payouts: int = DEFAULT_MAX_PAYOUTS  # padded payout record length (n_payouts counts all)

    def __post_init__(self) -> None:
        problems = []
        if not (math.isfinite(self.f) and self.f > 0):
            problems.append(f"f must be > 0, got {self.f}")
        if self.mode not in SIZE_MODES:
            problems.append(f"mode {self.mode!r} not in {SIZE_MODES}")
        if self.edge not in EDGE_MODES:
            problems.append(f"edge {self.edge!r} not in {EDGE_MODES}")
        if not math.isfinite(self.sharpe) or (self.edge == "zero" and self.sharpe != 0.0):
            problems.append(f"sharpe {self.sharpe} invalid for edge {self.edge!r}")
        if not (isinstance(self.k, int) and self.k >= 1):
            problems.append(f"k must be an int >= 1, got {self.k!r}")
        if self.payout_path not in PAYOUT_PATHS:
            problems.append(f"payout_path {self.payout_path!r} not in {PAYOUT_PATHS}")
        if not (math.isfinite(self.keep_d) and self.keep_d >= 0):
            problems.append(f"keep_d must be >= 0, got {self.keep_d}")
        for name in ("attempt_max_days", "xfa_max_days", "max_payouts"):
            if getattr(self, name) < 1:
                problems.append(f"{name} must be >= 1")
        if problems:
            raise ValueError("; ".join(problems))

    @property
    def drift(self) -> float:
        """Net drift per unit sigma per day: S / sqrt(252) (0 at the zero edge)."""
        return self.sharpe / math.sqrt(TRADING_DAYS_PER_YEAR) if self.edge == "sharpe" else 0.0

    @property
    def cost_in_drift(self) -> bool:
        """At a Sharpe edge the gross drift also covers k round trips (sim_spec 2.4)."""
        return self.edge == "sharpe"


@dataclass(frozen=True)
class PhaseSpec:
    """The daily-step parameters of one phase (Combine or XFA)."""

    mll_usd: float
    floor_cap_usd: float  # Combine mll_floor_max_rel_usd / XFA mll_floor_lock_usd
    dll_usd: float | None  # active daily loss limit, None when off
    tiers: tuple[tuple[float | None, int], ...]  # (below_usd, max_minis); Combine: one tier
    boundary: str  # "lower" | "upper"


def combine_dll(rules: SizeRules, policy: Policy) -> float | None:
    """Lead 17:30: the DLL chosen at checkout applies in the Combine at combine.dll_option_usd;
    combine.dll_usd is a mandatory Combine DLL (null in the FINAL file). Both active: the
    smaller (QUESTION: no rule file has both)."""
    c = rules.combine
    active = [] if c.dll_usd is None else [c.dll_usd]
    if policy.dll_chosen:
        if c.dll_option_usd is None:
            raise UnsupportedRule("dll_chosen but the size has no combine.dll_option_usd")
        active.append(c.dll_option_usd)
    return min(active) if active else None


def combine_phase(rules: SizeRules, policy: Policy) -> PhaseSpec:
    c = rules.combine
    if c.mll_trail != "eod":
        raise UnsupportedRule(f"combine mll_trail {c.mll_trail!r}: only EOD trailing is modelled")
    if rules.glob.combine_time_limit_days is not None:
        raise UnsupportedRule("combine_time_limit_days is set: the spec has no Combine time limit")
    return PhaseSpec(mll_usd=c.mll_usd, floor_cap_usd=c.mll_floor_max_rel_usd,
                     dll_usd=combine_dll(rules, policy), tiers=((None, c.max_minis),),
                     boundary="lower")


def xfa_phase(rules: SizeRules, policy: Policy) -> PhaseSpec:
    x = rules.xfa
    if x.mll_trail != "eod":
        raise UnsupportedRule(f"xfa mll_trail {x.mll_trail!r}: the spec models EOD trailing only")
    callup = rules.glob.callup
    if callup.type not in CALLUP_TYPES:
        raise UnsupportedRule(f"callup type {callup.type!r} is not modelled by the spec")
    if callup.type == "after_n_payouts" and (callup.n is None or callup.n < 1):
        raise UnsupportedRule("callup after_n_payouts needs n >= 1")
    if policy.dll_chosen and x.dll_option_usd is None:
        raise UnsupportedRule("dll_chosen but the size has no XFA DLL option")
    return PhaseSpec(mll_usd=x.mll_usd, floor_cap_usd=x.mll_floor_lock_usd,
                     dll_usd=x.dll_option_usd if policy.dll_chosen else None,
                     tiers=x.scaling, boundary=x.scaling_boundary)


def payout_rules(rules: SizeRules, policy: Policy) -> PayoutRules:
    return rules.xfa.payout(policy.payout_path)


def payout_cap(rules: SizeRules, policy: Policy) -> float:
    pr = payout_rules(rules, policy)
    if policy.dll_chosen and rules.glob.dll_doubles_payout_caps:
        if pr.cap_usd_dll is None:
            raise UnsupportedRule(f"{pr.path}: dll_doubles_payout_caps but cap_usd_dll is null")
        return pr.cap_usd_dll
    return pr.cap_usd


def callup_after(rules: SizeRules) -> int | None:
    """The payout count after which the XFA ends (call-up or payout_count_limit), None if never."""
    limits = [rules.xfa.payout_count_limit]
    if rules.glob.callup.type == "after_n_payouts":
        limits.append(rules.glob.callup.n)
    limits = [n for n in limits if n is not None]
    return min(limits) if limits else None


def tier_cap(balance: float, tiers: tuple[tuple[float | None, int], ...], boundary: str) -> int:
    """Max minis for a balance; a balance exactly on ``below`` takes the lower tier when the
    boundary is 'lower', the upper tier when it is 'upper'."""
    for below, minis in tiers:
        if below is None or balance < below or (boundary == "lower" and balance == below):
            return minis
    raise AssertionError("the last tier has below_usd null")


def cents_floor(x: float) -> float:
    """Floor to the cent after stripping float noise (the same numpy calls as vec.py)."""
    return float(np.floor(np.round(np.float64(x) * 100.0, 6)) / 100.0)


def integer_contracts(x: float) -> float:
    return float(np.floor(np.round(np.float64(x), 9)))


@dataclass(frozen=True)
class DayResult:
    pnl: float
    breach: bool
    dll_stop: bool
    contracts: float
    full_size: bool


def day_step(balance: float, floor: float, spec: ProductSpec, z: float, w: float, policy: Policy,
             cap_minis: int, dll_usd: float | None) -> DayResult:
    """sim_spec section 2, steps 1 to 8 (the caller applies the balance, floor and counters)."""
    d_open = balance - floor
    s = policy.f * d_open
    full = (not spec.has_micro) or s >= spec.sigma_full_usd
    sigma = spec.sigma_full_usd if full else spec.sigma_micro_usd
    rt = spec.rt_full_usd if full else spec.rt_micro_usd
    n = s / sigma
    if policy.mode == "integer":
        n = integer_contracts(n)
    n = max(n, 1.0)
    n = min(n, float(cap_minis * (1 if full else MICROS_PER_FULL)))
    mu = sigma * policy.drift + (policy.k * rt if policy.cost_in_drift else 0.0)
    close = n * (sigma * z + mu) - n * policy.k * rt
    worst = n * sigma * w - n * policy.k * rt
    if dll_usd is not None and worst <= -dll_usd and dll_usd < d_open - DLL_TIE_USD:
        return DayResult(-dll_usd, False, True, n, full)
    if worst <= -d_open:
        return DayResult(-d_open, True, False, n, full)
    return DayResult(close, False, False, n, full)


@dataclass(frozen=True)
class DayLog:
    """One traded day of the scalar reference (returned only when ``trace=True``)."""

    day: int
    balance_open: float  # after a same-morning payout
    floor_open: float
    cap_minis: int
    contracts: float
    full_size: bool
    pnl: float
    breach: bool
    dll_stop: bool
    balance_close: float
    floor_close: float


def _log(day: int, b_open: float, f_open: float, cap: int, res: DayResult, b_close: float,
         f_close: float) -> DayLog:
    return DayLog(day, b_open, f_open, cap, res.contracts, res.full_size, res.pnl, res.breach,
                  res.dll_stop, b_close, f_close)


def check_row(shocks: ShockSet, row: int, days: int) -> None:
    if not 0 <= row < shocks.n_paths:
        raise IndexError(f"row {row} outside 0..{shocks.n_paths - 1}")
    if shocks.n_days < days:
        raise ValueError(f"ShockSet has {shocks.n_days} days, the phase needs {days}")


# --------------------------------------------------------------------------- Combine ----
@dataclass(frozen=True)
class AttemptOutcome:
    passed: bool
    length: int  # trading days, the pass / breach day included
    reason: int  # ATTEMPT_BREACH / ATTEMPT_PASS / ATTEMPT_TIMEOUT
    days: tuple[DayLog, ...] = ()  # filled when trace=True


def combine_target_met(balance: float, best_day: float, rules: SizeRules) -> bool:
    """Pass test at EOD; global.combine_consistency_inclusive picks <= (True) or < (False)."""
    c, inclusive = rules.combine, rules.glob.combine_consistency_inclusive
    if c.consistency_type == "best_day_max_frac_of_target":
        if inclusive:
            return balance >= max(c.profit_target_usd, best_day / c.consistency_frac)
        return balance >= c.profit_target_usd and balance > best_day / c.consistency_frac
    if c.consistency_type == "best_day_max_frac_of_profit":
        limit = c.consistency_frac * balance
        within = best_day <= limit if inclusive else best_day < limit
        return balance >= c.profit_target_usd and within
    return balance >= c.profit_target_usd


def run_attempt(shocks: ShockSet, row: int, rules: SizeRules, policy: Policy,
                trace: bool = False) -> AttemptOutcome:
    """One Combine attempt (sim_spec section 3) from ShockSet row ``row``, days 0, 1, ..."""
    phase = combine_phase(rules, policy)
    max_days = policy.attempt_max_days
    check_row(shocks, row, max_days)
    c = rules.combine
    balance, floor, best = 0.0, -c.mll_usd, -math.inf
    logs: list[DayLog] = []
    for d in range(max_days):
        spec = shocks.products[int(shocks.prod[row, d])]
        res = day_step(balance, floor, spec, float(shocks.z[row, d]), float(shocks.w[row, d]),
                       policy, c.max_minis, phase.dll_usd)
        b_open, f_open = balance, floor
        balance = balance + res.pnl
        if not res.breach:
            best = max(best, res.pnl)
            floor = max(floor, min(balance - c.mll_usd, c.mll_floor_max_rel_usd))
        if trace:
            logs.append(_log(d, b_open, f_open, c.max_minis, res, balance, floor))
        if res.breach:
            return AttemptOutcome(False, d + 1, ATTEMPT_BREACH, tuple(logs))
        if d + 1 >= c.min_trading_days and combine_target_met(balance, best, rules):
            return AttemptOutcome(True, d + 1, ATTEMPT_PASS, tuple(logs))
    return AttemptOutcome(False, max_days, ATTEMPT_TIMEOUT, tuple(logs))


# ------------------------------------------------------------------------------- XFA ----
@dataclass
class _Window:
    """Payout-window aggregates since the last payout (local bookkeeping of run_xfa)."""

    n_win: int = 0
    net: float = 0.0
    n_days: int = 0
    best: float = -math.inf

    def add(self, pnl: float, pr: PayoutRules) -> None:
        if pr.path == "standard" and pnl >= pr.winning_day_usd:
            self.n_win += 1
        self.net = self.net + pnl
        self.n_days += 1
        self.best = max(self.best, pnl)


def payout_eligible(win: _Window, n_payouts: int, balance: float, pr: PayoutRules,
                    inclusive: bool) -> bool:
    """sim_spec section 4: the window since the last payout qualifies for a request.
    ``inclusive`` (global.xfa_consistency_inclusive): best day <= (True) or < (False) frac x net."""
    if pr.path == "standard":
        if win.n_win < pr.winning_days:
            return False
        if not pr.net_positive_since_last:
            return True
        return win.net > 0 if n_payouts > 0 else balance > 0
    # QUESTION: the consistency path requires window net > 0 whatever net_positive_since_last says
    limit = pr.best_day_max_frac * win.net
    within = win.best <= limit if inclusive else win.best < limit
    return win.n_days >= pr.traded_days and win.net > 0 and within


@dataclass(frozen=True)
class XfaOutcome:
    payout_days: tuple[int, ...]  # start-of-day indices of the first max_payouts requests
    payout_gross: tuple[float, ...]
    n_payouts: int
    total_gross: float
    first_payout_day: int  # -1 when none
    end_day: int  # elapsed trading days at the end
    end_reason: int  # XFA_BREACH / XFA_CALLUP / XFA_PAYOUT_LIMIT / XFA_HORIZON
    end_balance: float
    overflow: bool  # more than max_payouts payouts (only the first max_payouts are listed)
    days: tuple[DayLog, ...] = ()  # filled when trace=True


@dataclass
class _XfaLog:
    days: list[int] = field(default_factory=list)
    gross: list[float] = field(default_factory=list)
    n: int = 0
    total: float = 0.0

    def record(self, day: int, amount: float, cap: int) -> None:
        if self.n < cap:
            self.days.append(day)
            self.gross.append(amount)
        self.n += 1
        self.total = self.total + amount

    def outcome(self, end_day: int, reason: int, balance: float, cap: int,
                logs: list[DayLog]) -> XfaOutcome:
        return XfaOutcome(tuple(self.days), tuple(self.gross), self.n, self.total,
                          self.days[0] if self.days else -1, end_day, reason, balance, self.n > cap,
                          tuple(logs))


def payout_amount(balance: float, cap: float, pr: PayoutRules, keep_d: float, mll: float) -> float:
    return cents_floor(min(cap, pr.frac_of_balance * balance, balance - keep_d * mll))


def run_xfa(shocks: ShockSet, row: int, rules: SizeRules, policy: Policy,
            trace: bool = False) -> XfaOutcome:
    """One XFA life (sim_spec section 4) from ShockSet row ``row``, days 0, 1, ..."""
    phase = xfa_phase(rules, policy)
    max_days, max_pay = policy.xfa_max_days, policy.max_payouts
    check_row(shocks, row, max_days)
    x, g, pr = rules.xfa, rules.glob, payout_rules(rules, policy)
    cap, stop_after = payout_cap(rules, policy), callup_after(rules)
    balance = x.start_balance_usd
    floor = balance - x.mll_usd
    close_balance = balance  # balance at the prior session's close (start balance on day 1)
    floor_fixed = False
    win, log = _Window(), _XfaLog()
    logs: list[DayLog] = []
    for d in range(max_days):
        skip_today = False
        if payout_eligible(win, log.n, balance, pr, g.xfa_consistency_inclusive):
            amount = payout_amount(balance, cap, pr, policy.keep_d, x.mll_usd)
            if amount >= g.payout_min_request_usd:
                balance = balance - amount
                log.record(d, amount, max_pay)
                if log.n == 1 and x.mll_after_first_payout_usd is not None:
                    floor, floor_fixed = x.mll_after_first_payout_usd, True
                win = _Window()
                skip_today = not g.payout_day_counts_toward_next_window
                if stop_after is not None and log.n >= stop_after:
                    is_callup = g.callup.type == "after_n_payouts" and log.n >= g.callup.n
                    reason = XFA_CALLUP if is_callup else XFA_PAYOUT_LIMIT
                    return log.outcome(d, reason, balance, max_pay, logs)
        if balance - floor <= 0:
            raise FunnelError(f"row {row} day {d}: D_open {balance - floor} <= 0 after a payout")
        # QUESTION: the tier uses the prior close, i.e. the balance before a same-morning payout
        cap_minis = tier_cap(close_balance, phase.tiers, phase.boundary)
        spec = shocks.products[int(shocks.prod[row, d])]
        res = day_step(balance, floor, spec, float(shocks.z[row, d]), float(shocks.w[row, d]),
                       policy, cap_minis, phase.dll_usd)
        b_open, f_open = balance, floor
        balance = balance + res.pnl
        if not res.breach:
            if not skip_today:
                win.add(res.pnl, pr)
            if not floor_fixed:
                floor = max(floor, min(balance - x.mll_usd, x.mll_floor_lock_usd))
        if trace:
            logs.append(_log(d, b_open, f_open, cap_minis, res, balance, floor))
        if res.breach:
            return log.outcome(d + 1, XFA_BREACH, balance, max_pay, logs)
        close_balance = balance
    return log.outcome(max_days, XFA_HORIZON, balance, max_pay, logs)
