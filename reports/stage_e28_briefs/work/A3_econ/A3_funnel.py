"""A3 economic model (ranking spec section 3) on E.19's simulator (prop_econ, imported read-only).

Per-trade layer (spec): T = 20 round trips a day, size 1, independent trades, gross P&L per trade normal with mean
mu and SD sigma_T = sigma_1m ticks; cost c ticks per round trip. Daily P&L in USD is then exactly normal with mean
m = T (mu - c) v and SD s = sqrt(T) sigma_T v. The intraday path is E.19's normal source: a Brownian bridge from 0
to the day's close, whose minimum (the worst intraday P&L) is drawn given the close (prop_econ.returns.bridge_min
semantics, drift-free once the endpoint is fixed); its maximum is drawn the same way for intraday-trailing rules.

Common random numbers: one set of standard draws (z ~ N(0,1), e1, e2 ~ Exp(1)) per phase (evaluation attempts,
funded accounts), fixed seeds, shared by every pair and every mu; a pair and a mu only shift and scale them:
close = m + s z, worst = bridge minimum of (0 -> close). Size 1 is forced through E.19's day step with sizing
fraction f = 1e-12 (n = max(f D / sigma, 1) = 1).

What runs on prop_econ unchanged: Topstep's evaluation (vec.simulate_attempts) and XFA (vec.simulate_xfas), the
evaluation attempts of Lucid, Tradeify and MFFU (simulate_attempts on a SizeRules carrying their rules), the day
step (vec.day_step_vec), cycle assembly (assemble.assemble_cycles) and E.19's API wallet convention. What prop_econ
cannot represent is added here, as thin extensions that reuse the day step: an intraday trailing drawdown
(Bulenox Option 1) and the funded-stage payout rules of the four other firms (simulate_funded). The extension
reproduces prop_econ.vec.simulate_xfas path for path on Topstep's rules (tests).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from prop_econ.assemble import PURCHASE_KINDS, FeeTerms, assemble_cycles
from prop_econ.funnel import (
    ATTEMPT_BREACH,
    ATTEMPT_PASS,
    ATTEMPT_TIMEOUT,
    XFA_BREACH,
    XFA_HORIZON,
    XFA_PAYOUT_LIMIT,
    FunnelError,
    PhaseSpec,
    Policy,
)
from prop_econ.grid import derive_seed
from prop_econ.rules import SizeRules
from prop_econ.types import ProductSpec, ShockSet
from prop_econ.vec import (
    AttemptPool,
    XfaPool,
    _products,
    cents_floor_vec,
    day_step_vec,
    simulate_attempts,
    simulate_xfas,
    tier_cap_vec,
)

T_RT = 20  # round trips per trading day (spec)
N_PATHS = 20_000  # attempt and funded paths per pool (spec: 20,000 paths)
N_CYCLES = 20_000
N_REPS = 20_000  # campaign replications for mu10K
HORIZON = 756  # E.19 attempt and XFA horizon (trading days)
MAX_PAYOUTS = 192  # E.19 padded payout record
ATTEMPT_CAP = 60  # E.19 attempts per cycle
CAMPAIGN_DAYS = 250
CAMPAIGN_TARGET = 10_000.0
CAMPAIGN_ROUND = 2  # cycles drawn per open replication per round
CAMPAIGN_CHUNK = 500  # replications per assembly block (seeded per block and round: fixed, so CRN holds)
CYCLE_CHUNK = 1000  # cycles per assembly block (long subscriptions emit thousands of rebills per cycle)
B2F_WIDTH = 3  # XFA index columns drawn per cycle (Topstep 1 + 2 Back2Funded; others use column 0)
F_TINY = 1e-12  # sizing fraction that forces exactly 1 contract in E.19's day step
BASE_SEED = 20261021
CHUNK = 5000


# ------------------------------------------------------------------- common random numbers ----
@dataclass(frozen=True)
class Draws:
    """Standard draws of one phase, (N_PATHS, HORIZON), float32 storage (float64 arithmetic)."""

    z: np.ndarray
    e1: np.ndarray  # -ln U for the bridge minimum
    e2: np.ndarray | None  # -ln U' for the bridge maximum (intraday trailing only)


def phase_seed(phase: str, what: str) -> int:
    return derive_seed(BASE_SEED, "e28a3", phase, what)


def make_draws(phase: str, n: int = N_PATHS, days: int = HORIZON, with_max: bool = False) -> Draws:
    def gen(what: str, kind: str) -> np.ndarray:
        g = np.random.Generator(np.random.PCG64(phase_seed(phase, what)))
        if kind == "normal":
            return g.standard_normal((n, days), dtype=np.float32)
        return g.standard_exponential((n, days), dtype=np.float32)

    return Draws(gen("z", "normal"), gen("e1", "exp"), make_e2(phase, n, days) if with_max else None)


def make_e2(phase: str, n: int = N_PATHS, days: int = HORIZON) -> np.ndarray:
    """The bridge-maximum draws of a phase alone (same stream as make_draws(..., with_max=True).e2)."""
    g = np.random.Generator(np.random.PCG64(phase_seed(phase, "e2")))
    return g.standard_exponential((n, days), dtype=np.float32)


def _root(x: np.ndarray, e: np.ndarray) -> np.ndarray:
    """sqrt(x^2 + 2 E) in float64, in place on one temporary."""
    t = x * x
    t += e
    t += e
    return np.sqrt(t, out=t)


def bridge_min_e(x: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Minimum of a unit Brownian bridge 0 -> x given E = -ln U: (x - sqrt(x^2 - 2 ln U)) / 2, the formula of
    prop_econ.returns.bridge_min with u = exp(-E), capped at min(x, 0) as there."""
    w = _root(x, e)
    np.subtract(x, w, out=w)
    w *= 0.5
    np.minimum(w, x, out=w)
    return np.minimum(w, 0.0, out=w)


def bridge_max_e(x: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Maximum of the same bridge (the mirror formula), floored at max(x, 0)."""
    h = _root(x, e)
    h += x
    h *= 0.5
    np.maximum(h, x, out=h)
    return np.maximum(h, 0.0, out=h)


@dataclass(frozen=True)
class DayLaw:
    """The per-trade layer of one pair at one mu: daily mean m and SD s in USD."""

    m: float
    s: float

    @classmethod
    def from_trades(cls, mu: float, c: float, sigma_t: float, v: float, t: int = T_RT) -> DayLaw:
        return cls(m=t * (mu - c) * v, s=math.sqrt(t) * sigma_t * v)


def shock_set(dr: Draws, law: DayLaw, rows: slice | None = None) -> tuple[ShockSet, np.ndarray | None]:
    """(ShockSet in standardized units with the drift inside z, standardized bridge maximum or None)."""
    sl = slice(None) if rows is None else rows
    x = dr.z[sl].astype(np.float64)
    x += law.m / law.s
    w = bridge_min_e(x, dr.e1[sl])
    h = None if dr.e2 is None else bridge_max_e(x, dr.e2[sl])
    spec = ProductSpec("pair", law.s, 0.0, None, None, None)
    return ShockSet(x, w, np.zeros(x.shape, dtype=np.int16), (spec,)), h


def size1_policy(attempt_max_days: int = HORIZON) -> Policy:
    return Policy(f=F_TINY, mode="continuous", edge="zero", sharpe=0.0, k=1, dll_chosen=False,
                  payout_path="standard", keep_d=0.0, attempt_max_days=attempt_max_days,
                  xfa_max_days=HORIZON, max_payouts=MAX_PAYOUTS)


# --------------------------------------------------------------- evaluation (extension) ----
def simulate_attempts_intraday(shocks: ShockSet, h: np.ndarray, rules: SizeRules, policy: Policy,
                               dll_usd: float | None, chunk: int = CHUNK) -> AttemptPool:
    """prop_econ.vec.simulate_attempts with the drawdown trailing the intraday high (equity incl. open P&L).

    Conservative ordering inside a day: the day's high is taken to come before its low, so the floor in force
    during the day is F_eff = max(F, min(B + H - MLL, lock)); the day then runs E.19's day step against F_eff
    (breach when the worst intraday P&L reaches B - F_eff). After the day the floor is F_eff (the high bounds the
    close), so the trailing uses intraday highs, not closes.
    """
    c = rules.combine
    max_days = policy.attempt_max_days
    n_all = shocks.n_paths
    passed = np.zeros(n_all, dtype=bool)
    length = np.full(n_all, max_days, dtype=np.int32)
    reason = np.full(n_all, ATTEMPT_TIMEOUT, dtype=np.int8)
    if c.consistency_type != "none":
        raise NotImplementedError("intraday attempts: no firm mapped here has an evaluation consistency rule")
    prods = _products(shocks.products)
    for r0 in range(0, n_all, chunk):
        r1 = min(r0 + chunk, n_all)
        z_t = np.ascontiguousarray(shocks.z[r0:r1, :max_days].T)
        w_t = np.ascontiguousarray(shocks.w[r0:r1, :max_days].T)
        h_t = np.ascontiguousarray(h[r0:r1, :max_days].T)
        p_t = np.ascontiguousarray(shocks.prod[r0:r1, :max_days].T)
        ids = np.arange(r1 - r0)
        balance = np.zeros(ids.size)
        floor = np.full(ids.size, -c.mll_usd)
        best = np.full(ids.size, -np.inf)
        for d in range(max_days):
            if ids.size == 0:
                break
            s = prods.sigma_full[p_t[d, ids]]  # size 1: the day's P&L sd in USD
            f_eff = np.maximum(floor, np.minimum(balance + s * h_t[d, ids] - c.mll_usd,
                                                 c.mll_floor_max_rel_usd))
            pnl, breach = day_step_vec(balance, f_eff, p_t[d, ids], z_t[d, ids], w_t[d, ids], policy,
                                       c.max_minis, dll_usd, prods)
            balance = balance + pnl
            best = np.maximum(best, pnl)
            floor = np.maximum(f_eff, np.minimum(balance - c.mll_usd, c.mll_floor_max_rel_usd))
            ok = (~breach & (balance >= c.profit_target_usd) if d + 1 >= c.min_trading_days
                  else np.zeros(ids.size, dtype=bool))
            done = breach | ok
            if done.any():
                gid = r0 + ids[done]
                length[gid] = d + 1
                passed[gid] = ok[done]
                reason[gid] = np.where(ok[done], ATTEMPT_PASS, ATTEMPT_BREACH)
                keep = ~done
                ids, balance, floor, best = ids[keep], balance[keep], floor[keep], best[keep]
    return AttemptPool(passed=passed, length=length, reason=reason)


# ------------------------------------------------------------------ funded (extension) ----
@dataclass(frozen=True)
class FundedRules:
    """Funded-stage rules in E.19's units (balance relative to the start; floor = start - MLL at day 0)."""

    mll_usd: float
    trail: str  # "eod" or "intraday"
    lock_usd: float  # the floor never trails above this (relative balance)
    floor_after_first_payout: float | None  # floor set (and fixed) at the first payout, None = no rule
    dll_usd: float | None
    tiers: tuple[tuple[float | None, int], ...]
    boundary: str
    # payout eligibility, all on the window since the last payout unless noted
    win_threshold: float | None  # a winning day has pnl >= (or > when strict) this
    win_strict: bool
    win_days: int  # winning days required
    traded_days: int  # traded days required
    net_positive_since_last: bool  # E.19 standard path: window net > 0 after the first payout, else bal > 0
    net_min_first: float | None  # window net >= this for the first payout
    net_min_later: float | None  # window net >= this for later payouts
    min_balance: float | None  # balance >= this to request
    consistency_frac: float | None  # best day <= frac x profit (strict when not inclusive)
    consistency_scope: str  # "window" or "cumulative" (since the funded start, never reset)
    consistency_inclusive: bool
    request_weekday: int | None  # requests only at the start of days with d % 5 == this
    dead_days_after_payout: int  # traded days after the request day that do not count toward the next window
    # payout amount
    frac_of_balance: float
    caps: tuple[float, ...]  # cap for payout 1, 2, ...; the last value repeats
    buffer_usd: float  # amount <= balance - buffer
    min_request_usd: float
    payout_count_limit: int | None
    payout_day_counts: bool
    start_balance: float = 0.0


def funded_from_topstep(rules: SizeRules, path: str = "standard", dll: bool = False) -> FundedRules:
    """E.19's XFA rules in FundedRules form (the equality tests use this)."""
    x, g = rules.xfa, rules.glob
    pr = x.payout(path)
    cap = pr.cap_usd_dll if (dll and g.dll_doubles_payout_caps) else pr.cap_usd
    std = path == "standard"
    return FundedRules(
        mll_usd=x.mll_usd, trail="eod", lock_usd=x.mll_floor_lock_usd,
        floor_after_first_payout=x.mll_after_first_payout_usd,
        dll_usd=x.dll_option_usd if dll else None, tiers=x.scaling, boundary=x.scaling_boundary,
        win_threshold=pr.winning_day_usd if std else None, win_strict=False,
        win_days=pr.winning_days if std else 0, traded_days=0 if std else pr.traded_days,
        net_positive_since_last=bool(std and pr.net_positive_since_last), net_min_first=None,
        net_min_later=None, min_balance=None,
        consistency_frac=None if std else pr.best_day_max_frac, consistency_scope="window",
        consistency_inclusive=g.xfa_consistency_inclusive, request_weekday=None,
        dead_days_after_payout=0, frac_of_balance=pr.frac_of_balance, caps=(cap,), buffer_usd=0.0,
        min_request_usd=g.payout_min_request_usd,
        payout_count_limit=x.payout_count_limit if g.callup.type != "after_n_payouts"
        else min(n for n in (x.payout_count_limit, g.callup.n) if n is not None),
        payout_day_counts=g.payout_day_counts_toward_next_window,
        start_balance=x.start_balance_usd)


class _State:
    FIELDS = ("ids", "balance", "floor", "close", "fixed", "npay", "win_n", "win_net", "win_days",
              "win_best", "cum_net", "cum_best", "dead")

    def __init__(self, n: int, fr: FundedRules) -> None:
        self.ids = np.arange(n)
        self.balance = np.full(n, fr.start_balance)
        self.floor = np.full(n, fr.start_balance - fr.mll_usd)
        self.close = np.full(n, fr.start_balance)
        self.fixed = np.zeros(n, dtype=bool)
        self.npay = np.zeros(n, dtype=np.int64)
        self.win_n = np.zeros(n, dtype=np.int64)
        self.win_net = np.zeros(n)
        self.win_days = np.zeros(n, dtype=np.int64)
        self.win_best = np.full(n, -np.inf)
        self.cum_net = np.zeros(n)
        self.cum_best = np.full(n, -np.inf)
        self.dead = np.zeros(n, dtype=np.int64)

    def reset_window(self, mask: np.ndarray) -> None:
        self.win_n = np.where(mask, 0, self.win_n)
        self.win_net = np.where(mask, 0.0, self.win_net)
        self.win_days = np.where(mask, 0, self.win_days)
        self.win_best = np.where(mask, -np.inf, self.win_best)

    def keep(self, mask: np.ndarray) -> None:
        for name in self.FIELDS:
            setattr(self, name, getattr(self, name)[mask])


def _eligible(st: _State, fr: FundedRules, d: int) -> np.ndarray:
    ok = np.ones(st.ids.size, dtype=bool)
    if fr.win_days:
        ok &= st.win_n >= fr.win_days
    if fr.net_positive_since_last:
        ok &= np.where(st.npay > 0, st.win_net > 0, st.balance > 0)
    if fr.traded_days:
        ok &= st.win_days >= fr.traded_days
    if fr.net_min_first is not None:
        ok &= np.where(st.npay == 0, st.win_net >= fr.net_min_first, True)
    if fr.net_min_later is not None:
        ok &= np.where(st.npay > 0, st.win_net >= fr.net_min_later, True)
    if fr.min_balance is not None:
        ok &= st.balance >= fr.min_balance
    if fr.consistency_frac is not None:
        base, best = ((st.win_net, st.win_best) if fr.consistency_scope == "window"
                      else (st.cum_net, st.cum_best))
        limit = fr.consistency_frac * base
        within = best <= limit if fr.consistency_inclusive else best < limit
        ok &= (base > 0) & within
    if fr.request_weekday is not None and d % 5 != fr.request_weekday:
        ok &= False
    return ok


@dataclass
class _Out:
    pay_days: np.ndarray
    pay_gross: np.ndarray
    npay: np.ndarray
    total: np.ndarray
    first: np.ndarray
    end_day: np.ndarray
    reason: np.ndarray
    end_balance: np.ndarray
    overflow: np.ndarray


def _finish(st: _State, mask: np.ndarray, out: _Out, r0: int, end_day: int, reason: int) -> None:
    gid = r0 + st.ids[mask]
    out.npay[gid] = st.npay[mask]
    out.end_day[gid] = end_day
    out.reason[gid] = reason
    out.end_balance[gid] = st.balance[mask]
    st.keep(~mask)


def _request(st: _State, d: int, out: _Out, r0: int, fr: FundedRules, max_pay: int) -> np.ndarray:
    """Start-of-day payout requests (E.19 timing); returns the mask of paths whose window skips today."""
    eligible = _eligible(st, fr, d)
    if not eligible.any():
        return np.zeros(st.ids.size, dtype=bool)
    caps = np.asarray(fr.caps, dtype=np.float64)
    cap = caps[np.minimum(st.npay, caps.size - 1)]
    amount = cents_floor_vec(np.minimum(np.minimum(cap, fr.frac_of_balance * st.balance),
                                        st.balance - fr.buffer_usd))
    req = eligible & (amount >= fr.min_request_usd)
    if not req.any():
        return req
    ri = np.flatnonzero(req)
    gid = r0 + st.ids[ri]
    slot = st.npay[ri]
    fits = slot < max_pay
    out.pay_days[gid[fits], slot[fits]] = d
    out.pay_gross[gid[fits], slot[fits]] = amount[ri][fits]
    out.overflow[gid[~fits]] = True
    out.total[gid] = out.total[gid] + amount[ri]
    out.first[gid[slot == 0]] = d
    st.npay = st.npay + req
    st.balance = np.where(req, st.balance - amount, st.balance)
    if fr.floor_after_first_payout is not None:
        first_now = req & (st.npay == 1)
        st.floor = np.where(first_now, fr.floor_after_first_payout, st.floor)
        st.fixed = st.fixed | first_now
    st.reset_window(req)
    st.dead = np.where(req, fr.dead_days_after_payout, st.dead)
    return req if not fr.payout_day_counts else np.zeros(req.size, dtype=bool)


def _trade(st: _State, skip: np.ndarray, d: int, cols: tuple[np.ndarray, ...], out: _Out, r0: int,
           fr: FundedRules, phase: PhaseSpec, policy: Policy, prods: object) -> None:
    z_t, w_t, p_t, h_t = cols
    if (st.balance - st.floor <= 0).any():
        bad = int(r0 + st.ids[np.argmax(st.balance - st.floor <= 0)])
        raise FunnelError(f"row {bad} day {d}: D_open <= 0 after a payout")
    cap_minis = tier_cap_vec(st.close, phase)
    if fr.trail == "intraday":
        s = prods.sigma_full[p_t[d, st.ids]]  # size 1: the day's P&L sd in USD
        hi = st.balance + s * h_t[d, st.ids] - fr.mll_usd
        f_eff = np.where(st.fixed, st.floor, np.maximum(st.floor, np.minimum(hi, fr.lock_usd)))
    else:
        f_eff = st.floor
    pnl, breach = day_step_vec(st.balance, f_eff, p_t[d, st.ids], z_t[d, st.ids], w_t[d, st.ids],
                               policy, cap_minis, fr.dll_usd, prods)
    st.balance = st.balance + pnl
    st.floor = f_eff
    if breach.any():
        _finish(st, breach, out, r0, d + 1, XFA_BREACH)
        pnl, skip = pnl[~breach], skip[~breach]
    add = ~skip & (st.dead == 0)
    st.dead = np.where(~skip & (st.dead > 0), st.dead - 1, st.dead)
    if fr.win_threshold is not None:
        win = pnl > fr.win_threshold if fr.win_strict else pnl >= fr.win_threshold
        st.win_n = st.win_n + (add & win)
    st.win_net = np.where(add, st.win_net + pnl, st.win_net)
    st.win_days = st.win_days + add
    st.win_best = np.where(add, np.maximum(st.win_best, pnl), st.win_best)
    st.cum_net = st.cum_net + pnl
    st.cum_best = np.maximum(st.cum_best, pnl)
    trailed = np.maximum(st.floor, np.minimum(st.balance - fr.mll_usd, fr.lock_usd))
    st.floor = np.where(st.fixed, st.floor, trailed)
    st.close = st.balance


def simulate_funded(shocks: ShockSet, h: np.ndarray | None, fr: FundedRules, policy: Policy,
                    chunk: int = CHUNK) -> XfaPool:
    """prop_econ.vec.simulate_xfas generalized to FundedRules (same timing, day step and records)."""
    max_days, max_pay = policy.xfa_max_days, policy.max_payouts
    if fr.trail == "intraday" and h is None:
        raise ValueError("intraday trailing needs the bridge maximum")
    phase = PhaseSpec(mll_usd=fr.mll_usd, floor_cap_usd=fr.lock_usd, dll_usd=fr.dll_usd,
                      tiers=fr.tiers, boundary=fr.boundary)
    n_all = shocks.n_paths
    out = _Out(pay_days=np.full((n_all, max_pay), -1, dtype=np.int32),
               pay_gross=np.zeros((n_all, max_pay)), npay=np.zeros(n_all, dtype=np.int32),
               total=np.zeros(n_all), first=np.full(n_all, -1, dtype=np.int32),
               end_day=np.zeros(n_all, dtype=np.int32), reason=np.zeros(n_all, dtype=np.int8),
               end_balance=np.zeros(n_all), overflow=np.zeros(n_all, dtype=bool))
    prods = _products(shocks.products)
    for r0 in range(0, n_all, chunk):
        r1 = min(r0 + chunk, n_all)
        cols = tuple(np.ascontiguousarray(a[r0:r1, :max_days].T) for a in (shocks.z, shocks.w))
        cols = cols + (np.ascontiguousarray(shocks.prod[r0:r1, :max_days].T),
                       None if h is None else np.ascontiguousarray(h[r0:r1, :max_days].T))
        st = _State(r1 - r0, fr)
        for d in range(max_days):
            if st.ids.size == 0:
                break
            skip = _request(st, d, out, r0, fr, max_pay)
            if fr.payout_count_limit is not None:
                done = st.npay >= fr.payout_count_limit
                if done.any():
                    _finish(st, done, out, r0, d, XFA_PAYOUT_LIMIT)
                    skip = skip[~done]
            if st.ids.size == 0:
                break
            _trade(st, skip, d, cols, out, r0, fr, phase, policy, prods)
        if st.ids.size:
            _finish(st, np.ones(st.ids.size, dtype=bool), out, r0, max_days, XFA_HORIZON)
    return XfaPool(payout_days=out.pay_days, payout_gross=out.pay_gross, n_payouts=out.npay,
                   total_gross=out.total, first_payout_day=out.first, end_day=out.end_day,
                   end_reason=out.reason, end_balance=out.end_balance, overflow=out.overflow)


# ---------------------------------------------------------------------- firm model ----
@dataclass(frozen=True)
class FirmModel:
    firm: str
    plan: str
    eval_rules: SizeRules  # combine block carries the evaluation rules
    eval_trail: str  # "eod" (prop_econ) or "intraday" (extension)
    eval_dll_usd: float | None  # the evaluation DLL as applied by the day step
    attempt_max_days: int
    xfa_rules: SizeRules | None  # Topstep: prop_econ simulate_xfas on these rules
    funded: FundedRules | None  # other firms: the extension
    terms: FeeTerms
    api_monthly_usd: float
    api_period_days: int
    mll_usd: float
    dll_usd: float | None

    @property
    def needs_max(self) -> bool:
        return self.eval_trail == "intraday" or (self.funded is not None and self.funded.trail == "intraday")


def with_terms(model: FirmModel, **kw: float) -> FirmModel:
    return replace(model, terms=replace(model.terms, **kw))


# -------------------------------------------------------------------------- pools ----
@dataclass(frozen=True)
class Pools:
    attempts: AttemptPool
    xfas: XfaPool


def _concat_attempts(parts: list[AttemptPool]) -> AttemptPool:
    return AttemptPool(*(np.concatenate([getattr(p, f) for p in parts]) for f in ("passed", "length", "reason")))


def _concat_xfas(parts: list[XfaPool]) -> XfaPool:
    names = ("payout_days", "payout_gross", "n_payouts", "total_gross", "first_payout_day", "end_day",
             "end_reason", "end_balance", "overflow")
    return XfaPool(*(np.concatenate([getattr(p, f) for p in parts]) for f in names))


def simulate_pools(model: FirmModel, law: DayLaw, d_att: Draws, d_xfa: Draws, chunk: int = CHUNK) -> Pools:
    """Attempt and funded pools for one pair at one mu. Rows are independent paths, so the shock sets are built
    and simulated CHUNK rows at a time (the simulators chunk the same way inside); results equal one call."""
    pol = size1_policy(model.attempt_max_days)
    a_parts, x_parts = [], []
    for r0 in range(0, d_att.z.shape[0], chunk):
        sh, h = shock_set(d_att, law, slice(r0, r0 + chunk))
        if model.eval_trail == "intraday":
            a_parts.append(simulate_attempts_intraday(sh, h, model.eval_rules, pol, model.eval_dll_usd))
        else:
            a_parts.append(simulate_attempts(sh, model.eval_rules, pol))
    for r0 in range(0, d_xfa.z.shape[0], chunk):
        sh, h = shock_set(d_xfa, law, slice(r0, r0 + chunk))
        if model.xfa_rules is not None:
            x_parts.append(simulate_xfas(sh, model.xfa_rules, pol))
        else:
            x_parts.append(simulate_funded(sh, h, model.funded, pol))
    return Pools(_concat_attempts(a_parts), _concat_xfas(x_parts))


# ------------------------------------------------------------------------- cycles ----
def cycle_indices(n: int = N_CYCLES, n_att: int = N_PATHS, n_xfa: int = N_PATHS
                  ) -> tuple[np.ndarray, np.ndarray]:
    g = np.random.Generator(np.random.PCG64(derive_seed(BASE_SEED, "e28a3", "cycle")))
    att = g.integers(0, n_att, size=(n, ATTEMPT_CAP), dtype=np.int64)
    xfa = g.integers(0, n_xfa, size=(n, B2F_WIDTH), dtype=np.int64)
    return att, xfa


def api_cycle(end: np.ndarray, model: FirmModel) -> np.ndarray:
    """E.19 wallet (L-12): one API subscription per started billing period of the cycle."""
    if model.api_monthly_usd == 0:
        return np.zeros(end.shape)
    return model.api_monthly_usd * (-(-np.asarray(end, dtype=np.int64) // model.api_period_days))


@dataclass(frozen=True)
class CycleStats:
    ev: float  # mean net cash per cycle incl. API
    se: float
    ev_ex_api: float
    eval_fees_per_attempt: float  # (start + rebills + resets) / attempts, ratio of means
    eval_fees_api_per_attempt: float  # plus API over the evaluation stage
    all_fees_per_attempt: float  # plus activation (and Back2Funded, off here)
    p_pass_attempt: float
    mean_attempts: float
    p_no_payout: float
    mean_cycle_days: float
    mean_cash: float
    mean_fees: float


def cycle_stats(model: FirmModel, pools: Pools, att_idx: np.ndarray, xfa_idx: np.ndarray,
                chunk: int = CYCLE_CHUNK) -> CycleStats:
    t = model.terms
    cols = {k: [] for k in ("net", "net_ex", "eval_fees", "api_eval", "fees_api", "att", "got", "end", "cash")}
    for c0 in range(0, att_idx.shape[0], chunk):
        a, x = att_idx[c0:c0 + chunk], xfa_idx[c0:c0 + chunk, : 1 + t.b2f_max]
        batch = assemble_cycles(a, x, pools.attempts, pools.xfas, t)
        api = api_cycle(batch.end, model)
        is_eval = np.isin(batch.fee_kind, PURCHASE_KINDS)
        combine_days = np.where(batch.passed, batch.xfa_start[:, 0], batch.end)
        got = np.zeros(batch.n, dtype=bool)
        got[batch.cash_cycle[batch.cash_usd > 0]] = True
        cols["net"].append(batch.net - api)
        cols["net_ex"].append(batch.net)
        cols["eval_fees"].append(np.bincount(batch.fee_cycle[is_eval], weights=batch.fee_usd[is_eval],
                                             minlength=batch.n))
        cols["api_eval"].append(api_cycle(combine_days, model))
        cols["fees_api"].append(batch.fees_total + api)
        cols["att"].append(batch.n_attempts)
        cols["got"].append(got)
        cols["end"].append(batch.end)
        cols["cash"].append(batch.cash_total)
    v = {k: np.concatenate(arr) for k, arr in cols.items()}
    att = float(v["att"].mean())
    net = v["net"]
    return CycleStats(
        ev=float(net.mean()), se=float(net.std(ddof=1) / math.sqrt(net.size)),
        ev_ex_api=float(v["net_ex"].mean()), eval_fees_per_attempt=float(v["eval_fees"].mean()) / att,
        eval_fees_api_per_attempt=float((v["eval_fees"] + v["api_eval"]).mean()) / att,
        all_fees_per_attempt=float(v["fees_api"].mean()) / att,
        p_pass_attempt=float(pools.attempts.passed.mean()), mean_attempts=att,
        p_no_payout=float((~v["got"]).mean()), mean_cycle_days=float(v["end"].mean()),
        mean_cash=float(v["cash"].mean()), mean_fees=float(v["fees_api"].mean()))


# ------------------------------------------------------------------------ campaign ----
def campaign_indices(block: int, rnd: int, n: int, n_att: int, n_xfa: int) -> tuple[np.ndarray, np.ndarray]:
    """Index draws of one replication block and round (seeded by both, so every mu sees the same cycles)."""
    g = np.random.Generator(np.random.PCG64(derive_seed(BASE_SEED, "e28a3", "campaign", block, rnd)))
    att = g.integers(0, n_att, size=(n, CAMPAIGN_ROUND, ATTEMPT_CAP), dtype=np.int64)
    xfa = g.integers(0, n_xfa, size=(n, CAMPAIGN_ROUND, B2F_WIDTH), dtype=np.int64)
    return att, xfa


def _segment_running(rep: np.ndarray, amt: np.ndarray, carry: np.ndarray) -> np.ndarray:
    """Running sum of amt within each run of equal rep (rep sorted), plus carry[rep]."""
    cs = np.cumsum(amt)
    seg0 = np.flatnonzero(np.r_[True, rep[1:] != rep[:-1]])
    base = np.repeat(cs[seg0] - amt[seg0], np.diff(np.r_[seg0, rep.size]))
    return carry[rep] + cs - base


def _campaign_block(model: FirmModel, pools: Pools, block: int, n: int, days: int, target: float
                    ) -> np.ndarray:
    t = model.terms
    reached = np.zeros(n, dtype=bool)
    clock = np.zeros(n, dtype=np.int64)  # start time of the next cycle per replication
    carry = np.zeros(n)  # cash - fees of the processed events
    pend = (np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int8),
            np.zeros(0))
    open_reps = np.arange(n)
    rnd = 0
    while open_reps.size:
        att, xfa = campaign_indices(block, rnd, n, pools.attempts.n, pools.xfas.n)
        u = open_reps.size
        a = att[open_reps].reshape(u * CAMPAIGN_ROUND, ATTEMPT_CAP)
        x = xfa[open_reps].reshape(u * CAMPAIGN_ROUND, B2F_WIDTH)[:, : 1 + t.b2f_max]
        batch = assemble_cycles(a, x, pools.attempts, pools.xfas, t)
        dur = batch.end.reshape(u, CAMPAIGN_ROUND)
        starts = (clock[open_reps][:, None] + np.cumsum(dur, axis=1) - dur).reshape(-1)
        clock[open_reps] = clock[open_reps] + dur.sum(axis=1)
        rep = np.repeat(open_reps, CAMPAIGN_ROUND)
        f_t = starts[batch.fee_cycle] + batch.fee_time
        c_t = starts[batch.cash_cycle] + batch.cash_time
        fk, ck = f_t <= days, c_t <= days  # nothing after the horizon can matter
        ev_rep = np.concatenate([pend[0], rep[batch.fee_cycle[fk]], rep[batch.cash_cycle[ck]]])
        ev_t = np.concatenate([pend[1], f_t[fk], c_t[ck]])
        ev_cash = np.concatenate([pend[2], np.zeros(int(fk.sum()), dtype=np.int8),
                                  np.ones(int(ck.sum()), dtype=np.int8)])
        ev_amt = np.concatenate([pend[3], -batch.fee_usd[fk], batch.cash_usd[ck]])
        del batch
        live = ~reached[ev_rep]
        now = live & (ev_t < clock[ev_rep])  # events at the clock wait for the next round's fees
        later = live & ~now
        pend = (ev_rep[later], ev_t[later], ev_cash[later], ev_amt[later])
        ev_rep, ev_t, ev_cash, ev_amt = ev_rep[now], ev_t[now], ev_cash[now], ev_amt[now]
        order = np.lexsort((ev_cash, ev_t, ev_rep))
        ev_rep, ev_t, ev_cash, ev_amt = ev_rep[order], ev_t[order], ev_cash[order], ev_amt[order]
        if ev_rep.size:
            run = _segment_running(ev_rep, ev_amt, carry)
            api = model.api_monthly_usd * (ev_t // model.api_period_days + 1)
            reached[np.unique(ev_rep[(ev_cash == 1) & (run - api >= target)])] = True
            last = np.r_[np.flatnonzero(ev_rep[1:] != ev_rep[:-1]), ev_rep.size - 1]
            carry[ev_rep[last]] = run[last]
        open_reps = open_reps[(~reached[open_reps]) & (clock[open_reps] <= days)]
        keep = np.isin(pend[0], open_reps)  # a deferred event has t = clock <= days: its rep stays open
        pend = tuple(arr[keep] for arr in pend)
        rnd += 1
    return reached


def campaign_p_reach(model: FirmModel, pools: Pools, n_reps: int = N_REPS,
                     days: int = CAMPAIGN_DAYS, target: float = CAMPAIGN_TARGET) -> float:
    """P(net cash = withdrawals - fees - API reaches `target` within `days` trading days), one account at a time.

    Cycles run back to back (the next cycle starts when the previous one ends: evaluations failed up to the
    attempt cap, or the funded account breached, ended by its payout limit or reached the horizon). Events at
    elapsed day t <= days count; fees come before cash on the same day, across cycles too (events at the current
    clock wait for the next round, as in E.19's _evaluate_open); the API is paid per started billing period of
    operation (E.19's api_periods_at). Replications run in fixed blocks of CAMPAIGN_CHUNK, each block and round
    seeded on its own, so a replication sees the same cycles at every mu (common random numbers).
    """
    hits = 0
    for b, r0 in enumerate(range(0, n_reps, CAMPAIGN_CHUNK)):
        hits += int(_campaign_block(model, pools, b, min(CAMPAIGN_CHUNK, n_reps - r0), days, target).sum())
    return hits / n_reps
