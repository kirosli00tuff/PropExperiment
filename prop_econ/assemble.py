"""Stage E.19 fees, cycles and campaigns (reports/stage_e19_briefs/sim_spec.md section 5).

Pure functions on the attempt and XFA pools (prop_econ/vec.py). A cycle draws attempts in sequence
until a pass or the attempt cap, then one XFA, then Back2Funded XFAs when that policy is on; index
draws come from a seeded numpy Generator(PCG64) and are separated from the deterministic assembly,
so the scalar reference ``assemble_cycle`` and the vectorized ``assemble_cycles`` are compared on
the same draws.

Clock: trading days. Time t is the start of the cycle's (t+1)-th trading day, i.e. t days elapsed.
An attempt of length L started at t occupies days t..t+L-1 and ends at t+L; a reset after a fail,
the activation after a pass and the XFA start all happen at t+L (the next trading day). XFA payouts
happen at XFA start + payout day; an XFA ends at XFA start + end_day.

Readings the spec leaves open are marked "QUESTION" (see
reports/stage_e19_briefs/funnel_questions.md).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from prop_econ.funnel import TRADING_DAYS_PER_YEAR, XFA_BREACH
from prop_econ.rules import SizeRules
from prop_econ.vec import AttemptPool, XfaPool

CALENDAR_DAYS_PER_YEAR = 365
KIND_START, KIND_REBILL, KIND_RESET, KIND_ACTIVATION, KIND_B2F = 0, 1, 2, 3, 4
PURCHASE_KINDS = (KIND_START, KIND_REBILL, KIND_RESET)  # every P or R payment
DEFAULT_ATTEMPT_CAP = 60
DEFAULT_PURCHASE_CAP = 400
DEFAULT_TARGETS = (5000.0, 10000.0)
ASSEMBLY_BATCH = 50_000  # cycles assembled per vectorized call (bounds the index matrices)
MAX_ROUND_CYCLES = 32  # campaign: most cycles added to one slot per round


def billing_period_days(calendar_days: int) -> int:
    """Calendar billing period in trading days: 30 x 252/365 = 20.7 -> 21 (rounded half up)."""
    return int(math.floor(calendar_days * TRADING_DAYS_PER_YEAR / CALENDAR_DAYS_PER_YEAR + 0.5))


@dataclass(frozen=True)
class FeeTerms:
    """Fee and cycle settings for one size, pricing path and DLL choice."""

    monthly_usd: float  # P (after the DLL discount when chosen)
    reset_usd: float  # R
    activation_usd: float
    b2f_usd: float  # Back2Funded price (after the DLL discount when chosen)
    period_days: int  # rebill period in trading days
    rebill_adds_credit: bool
    reset_pushes_rebill: bool
    split: float  # trader's share of a gross payout
    attempt_cap: int
    b2f_on: bool
    b2f_max: int  # always drawn, so B2F on / off share their index draws
    b2f_before_first_only: bool

    def __post_init__(self) -> None:
        if self.period_days < 1 or self.attempt_cap < 1 or self.b2f_max < 0:
            raise ValueError("period_days and attempt_cap must be >= 1, b2f_max >= 0")


def fee_terms(rules: SizeRules, *, pricing_path: str, dll_chosen: bool, b2f_on: bool,
              attempt_cap: int = DEFAULT_ATTEMPT_CAP) -> FeeTerms:
    price = rules.pricing(pricing_path)
    b2f = rules.xfa.back2funded
    monthly_discount = (price.dll_discount_monthly_usd or 0.0) if dll_chosen else 0.0
    b2f_discount = (b2f.dll_discount_usd or 0.0) if dll_chosen else 0.0
    return FeeTerms(
        monthly_usd=price.monthly_price_usd - monthly_discount,
        reset_usd=price.reset_price_usd,  # QUESTION: the DLL discount is applied to P only
        activation_usd=price.activation_fee_usd,
        b2f_usd=b2f.price_usd - b2f_discount,
        period_days=billing_period_days(rules.glob.billing_period_calendar_days),
        rebill_adds_credit=rules.glob.rebill_adds_reset_credit,
        reset_pushes_rebill=rules.glob.reset_pushes_rebill,
        split=rules.glob.profit_split_trader,
        attempt_cap=attempt_cap,
        b2f_on=b2f_on,
        b2f_max=b2f.max_per_xfa,
        b2f_before_first_only=b2f.before_first_payout_only,
    )


def draw_indices(rng: np.random.Generator, n: int, attempts: AttemptPool, xfas: XfaPool,
                 terms: FeeTerms) -> tuple[np.ndarray, np.ndarray]:
    """Pool rows for n cycles: (n, attempt_cap) attempts and (n, 1 + b2f_max) XFAs."""
    att = rng.integers(0, attempts.n, size=(n, terms.attempt_cap), dtype=np.int64)
    xfa = rng.integers(0, xfas.n, size=(n, 1 + terms.b2f_max), dtype=np.int64)
    return att, xfa


def _b2f_again(xfas: XfaPool, x: np.ndarray | int, terms: FeeTerms) -> np.ndarray | bool:
    """Back2Funded applies to an XFA that breached (before its first payout, per the rules)."""
    breached = xfas.end_reason[x] == XFA_BREACH
    no_payout = xfas.n_payouts[x] == 0
    return breached & (no_payout | (not terms.b2f_before_first_only))


# ------------------------------------------------------------------- scalar reference ----
@dataclass(frozen=True)
class Cycle:
    fees: tuple[tuple[int, float, int], ...]  # (time, usd, kind) in time order
    cash: tuple[tuple[int, float], ...]  # (time, user cash after the split) in time order
    end: int  # elapsed trading days when the cycle ends
    n_attempts: int
    passed: bool
    credit_resets: int
    xfas: tuple[tuple[int, int, int], ...]  # (start, end, pool row) per XFA, Back2Funded included
    overflow_xfas: int

    @property
    def purchases(self) -> int:
        return sum(1 for _, _, kind in self.fees if kind in PURCHASE_KINDS)

    @property
    def fees_total(self) -> float:
        return sum(usd for _, usd, _ in self.fees)

    @property
    def cash_total(self) -> float:
        return sum(usd for _, usd in self.cash)

    @property
    def net(self) -> float:
        return self.cash_total - self.fees_total


def _subscription(att_row: Sequence[int], attempts: AttemptPool, terms: FeeTerms
                  ) -> tuple[list[tuple[int, float, int]], int, int, bool, int]:
    """Combine phase of one cycle: (fees, end time, attempts used, passed, credit resets)."""
    fees = [(0, terms.monthly_usd, KIND_START)]
    credits = credit_resets = 0
    next_rebill, t = terms.period_days, 0

    def rebill_until(bound: int, inclusive: bool) -> None:
        nonlocal next_rebill, credits
        while next_rebill < bound or (inclusive and next_rebill == bound):
            fees.append((next_rebill, terms.monthly_usd, KIND_REBILL))
            credits += int(terms.rebill_adds_credit)
            next_rebill += terms.period_days

    for i in range(terms.attempt_cap):
        a = int(att_row[i])
        if i > 0:
            rebill_until(t, inclusive=True)  # QUESTION: a rebill due on the reset day comes first
            if credits > 0:
                credits -= 1
                credit_resets += 1
            else:
                fees.append((t, terms.reset_usd, KIND_RESET))
            if terms.reset_pushes_rebill:
                next_rebill = t + terms.period_days
        end = t + int(attempts.length[a])
        rebill_until(end, inclusive=False)
        t = end
        if attempts.passed[a]:
            return fees, t, i + 1, True, credit_resets
    return fees, t, terms.attempt_cap, False, credit_resets


def assemble_cycle(att_row: Sequence[int], xfa_row: Sequence[int], attempts: AttemptPool,
                   xfas: XfaPool, terms: FeeTerms) -> Cycle:
    """One cycle from given pool rows (sim_spec section 5), written as a plain loop."""
    fees, t, n_att, passed, credit_resets = _subscription(att_row, attempts, terms)
    cash: list[tuple[int, float]] = []
    chain: list[tuple[int, int, int]] = []
    overflow = 0
    end = t
    if passed:
        fees.append((t, terms.activation_usd, KIND_ACTIVATION))
        start = t
        for j in range(1 + terms.b2f_max):
            x = int(xfa_row[j])
            n_rec = min(int(xfas.n_payouts[x]), xfas.max_payouts)
            for q in range(n_rec):
                cash.append((start + int(xfas.payout_days[x, q]),
                             terms.split * float(xfas.payout_gross[x, q])))
            end = start + int(xfas.end_day[x])
            if xfas.overflow[x]:  # QUESTION: unrecorded payouts credited at the XFA's end
                rest = float(xfas.total_gross[x]) - float(np.sum(xfas.payout_gross[x, :n_rec]))
                cash.append((end, terms.split * rest))
                overflow += 1
            chain.append((start, end, x))
            if not (terms.b2f_on and j < terms.b2f_max and _b2f_again(xfas, x, terms)):
                break
            fees.append((end, terms.b2f_usd, KIND_B2F))  # QUESTION: reactivated the next day
            start = end
    return Cycle(tuple(fees), tuple(cash), end, n_att, passed, credit_resets, tuple(chain),
                 overflow)


# --------------------------------------------------------------------------- vectorized ----
@dataclass(frozen=True)
class CycleBatch:
    """Cycles assembled from index rows; flat event arrays sorted by (cycle, time, kind)."""

    end: np.ndarray  # int64 (C,)
    n_attempts: np.ndarray  # int64
    passed: np.ndarray  # bool
    credit_resets: np.ndarray  # int64
    purchases: np.ndarray  # int64
    fees_total: np.ndarray  # float64
    cash_total: np.ndarray  # float64
    overflow_xfas: np.ndarray  # int64
    xfa_start: np.ndarray  # int64 (C, 1 + b2f_max), -1 when unused
    xfa_end: np.ndarray  # int64 (C, 1 + b2f_max), -1 when unused
    xfa_row: np.ndarray  # int64 (C, 1 + b2f_max), -1 when unused
    fee_cycle: np.ndarray
    fee_time: np.ndarray
    fee_usd: np.ndarray
    fee_kind: np.ndarray
    cash_cycle: np.ndarray
    cash_time: np.ndarray
    cash_usd: np.ndarray

    @property
    def n(self) -> int:
        return int(self.end.shape[0])

    @property
    def net(self) -> np.ndarray:
        return self.cash_total - self.fees_total

    @property
    def n_xfas(self) -> np.ndarray:
        return (self.xfa_row >= 0).sum(axis=1)


class _Events:
    """Growing lists of event arrays (local to one assembly call)."""

    def __init__(self) -> None:
        self.parts: list[tuple[np.ndarray, ...]] = []

    def add(self, *cols: np.ndarray) -> None:
        if cols[0].size:
            self.parts.append(cols)

    def stack(self, n_cols: int) -> list[np.ndarray]:
        if not self.parts:
            return [np.zeros(0, dtype=np.int64) for _ in range(n_cols)]
        return [np.concatenate([p[i] for p in self.parts]) for i in range(n_cols)]


def _emit_rebills(fees: _Events, ci: np.ndarray, bound: np.ndarray, inclusive: bool,
                  next_rebill: np.ndarray, credits: np.ndarray, terms: FeeTerms) -> None:
    """Rebills due at times < bound (<= bound when inclusive) for cycles ci."""
    nr, per = next_rebill[ci], terms.period_days
    gap = bound - nr
    count = gap // per + 1 if inclusive else (gap + per - 1) // per
    count = np.maximum(count, 0)
    total = int(count.sum())
    if total:
        first = np.cumsum(count) - count
        k = np.arange(total) - np.repeat(first, count)
        times = np.repeat(nr, count) + per * k
        fees.add(np.repeat(ci, count), times, np.full(total, terms.monthly_usd),
                 np.full(total, KIND_REBILL))
    if terms.rebill_adds_credit:
        credits[ci] += count
    next_rebill[ci] = nr + count * per


def _subscriptions_vec(att_idx: np.ndarray, attempts: AttemptPool, terms: FeeTerms,
                       fees: _Events) -> tuple[np.ndarray, ...]:
    n = att_idx.shape[0]
    t = np.zeros(n, dtype=np.int64)
    next_rebill = np.full(n, terms.period_days, dtype=np.int64)
    credits = np.zeros(n, dtype=np.int64)
    credit_resets = np.zeros(n, dtype=np.int64)
    n_att = np.zeros(n, dtype=np.int64)
    passed = np.zeros(n, dtype=bool)
    active = np.ones(n, dtype=bool)
    fees.add(np.arange(n), np.zeros(n, dtype=np.int64), np.full(n, terms.monthly_usd),
             np.full(n, KIND_START))
    for i in range(terms.attempt_cap):
        ci = np.flatnonzero(active)
        if ci.size == 0:
            break
        a = att_idx[ci, i]
        if i > 0:
            ti = t[ci]
            _emit_rebills(fees, ci, ti, True, next_rebill, credits, terms)
            has = credits[ci] > 0
            credits[ci] -= has
            credit_resets[ci] += has
            cash_reset = ci[~has]
            fees.add(cash_reset, t[cash_reset], np.full(cash_reset.size, terms.reset_usd),
                     np.full(cash_reset.size, KIND_RESET))
            if terms.reset_pushes_rebill:
                next_rebill[ci] = ti + terms.period_days
        end = t[ci] + attempts.length[a].astype(np.int64)
        _emit_rebills(fees, ci, end, False, next_rebill, credits, terms)
        n_att[ci] += 1
        t[ci] = end
        won = attempts.passed[a]
        passed[ci[won]] = True
        active[ci[won]] = False
    return t, n_att, passed, credit_resets


def _xfa_chains_vec(t: np.ndarray, passed: np.ndarray, xfa_idx: np.ndarray, xfas: XfaPool,
                    terms: FeeTerms, fees: _Events, cash: _Events) -> tuple[np.ndarray, ...]:
    n, width = xfa_idx.shape
    end = t.copy()
    overflow = np.zeros(n, dtype=np.int64)
    xs, xe, xr = (np.full((n, width), -1, dtype=np.int64) for _ in range(3))
    chain = np.flatnonzero(passed)
    fees.add(chain, t[chain], np.full(chain.size, terms.activation_usd),
             np.full(chain.size, KIND_ACTIVATION))
    start = t[chain]
    for j in range(width):
        if chain.size == 0:
            break
        x = xfa_idx[chain, j]
        days = xfas.payout_days[x]
        rows, cols = np.nonzero(days >= 0)
        cash.add(chain[rows], start[rows] + days[rows, cols],
                 terms.split * xfas.payout_gross[x[rows], cols])
        stop = start + xfas.end_day[x].astype(np.int64)
        ovf = xfas.overflow[x]
        if ovf.any():
            rest = xfas.total_gross[x[ovf]] - np.sum(xfas.payout_gross[x[ovf]], axis=1)
            cash.add(chain[ovf], stop[ovf], terms.split * rest)
            overflow[chain[ovf]] += 1
        xs[chain, j], xe[chain, j], xr[chain, j] = start, stop, x
        end[chain] = stop
        if not terms.b2f_on or j == width - 1:
            break
        again = _b2f_again(xfas, x, terms)
        chain, start = chain[again], stop[again]
        fees.add(chain, start, np.full(chain.size, terms.b2f_usd), np.full(chain.size, KIND_B2F))
    return end, overflow, xs, xe, xr


def assemble_cycles(att_idx: np.ndarray, xfa_idx: np.ndarray, attempts: AttemptPool,
                    xfas: XfaPool, terms: FeeTerms) -> CycleBatch:
    """assemble_cycle for every row of the index matrices, vectorized over cycles."""
    n = att_idx.shape[0]
    if att_idx.shape != (n, terms.attempt_cap) or xfa_idx.shape != (n, 1 + terms.b2f_max):
        raise ValueError(f"index shapes {att_idx.shape} {xfa_idx.shape} do not match the terms")
    fees, cash = _Events(), _Events()
    t, n_att, passed, credit_resets = _subscriptions_vec(att_idx, attempts, terms, fees)
    end, overflow, xs, xe, xr = _xfa_chains_vec(t, passed, xfa_idx, xfas, terms, fees, cash)
    f_cyc, f_time, f_usd, f_kind = fees.stack(4)
    order = np.lexsort((f_kind, f_time, f_cyc))
    f_cyc, f_time, f_usd, f_kind = f_cyc[order], f_time[order], f_usd[order], f_kind[order]
    c_cyc, c_time, c_usd = cash.stack(3)
    order = np.lexsort((c_time, c_cyc))
    c_cyc, c_time, c_usd = c_cyc[order], c_time[order], c_usd[order].astype(np.float64)
    is_purchase = np.isin(f_kind, PURCHASE_KINDS)
    return CycleBatch(
        end=end, n_attempts=n_att, passed=passed, credit_resets=credit_resets,
        purchases=np.bincount(f_cyc[is_purchase], minlength=n).astype(np.int64),
        fees_total=np.bincount(f_cyc, weights=f_usd, minlength=n),
        cash_total=np.bincount(c_cyc, weights=c_usd, minlength=n),
        overflow_xfas=overflow, xfa_start=xs, xfa_end=xe, xfa_row=xr,
        fee_cycle=f_cyc, fee_time=f_time, fee_usd=f_usd.astype(np.float64), fee_kind=f_kind,
        cash_cycle=c_cyc, cash_time=c_time, cash_usd=c_usd,
    )


def draw_cycles(rng: np.random.Generator, n: int, attempts: AttemptPool, xfas: XfaPool,
                terms: FeeTerms) -> tuple[CycleBatch, np.ndarray, np.ndarray]:
    """n fresh cycles (i.i.d. draws from the pools): (batch, attempt index rows, XFA index rows)."""
    att, xfa = draw_indices(rng, n, attempts, xfas, terms)
    return assemble_cycles(att, xfa, attempts, xfas, terms), att, xfa


# ----------------------------------------------------------------------------- campaign ----
@dataclass(frozen=True)
class CampaignTrace:
    """Every cycle a campaign drew (tests and audits), one row per cycle."""

    rep: np.ndarray
    slot: np.ndarray
    order: np.ndarray  # position of the cycle in its slot's sequence
    start: np.ndarray  # campaign time the cycle started
    end: np.ndarray
    att_idx: np.ndarray  # (n, attempt_cap)
    xfa_idx: np.ndarray  # (n, 1 + b2f_max)
    xfa_start: np.ndarray  # (n, 1 + b2f_max), campaign time, -1 unused
    xfa_end: np.ndarray


@dataclass(frozen=True)
class CampaignResult:
    """Per target (rows) and replication (columns): reached, and purchases / fees / days by then."""

    targets: tuple[float, ...]
    slots: int
    purchase_cap: int
    reached: np.ndarray  # bool
    purchases: np.ndarray  # int64, Combine purchases made when the target is first reached (-1)
    fees: np.ndarray  # float64, purchases + activations + Back2Funded paid by then (nan)
    days: np.ndarray  # int64, elapsed trading days (-1)
    cycles_drawn: int
    overflow_xfas: int  # drawn XFAs whose unrecorded payouts were credited at their end
    trace: CampaignTrace | None = None


@dataclass
class _Store:
    """Campaign events of the open replications (local, mutable)."""

    rep: np.ndarray
    time: np.ndarray
    is_cash: np.ndarray
    purchase: np.ndarray
    fee: np.ndarray
    cash: np.ndarray

    @classmethod
    def empty(cls) -> _Store:
        z = np.zeros(0)
        return cls(z.astype(np.int64), z.astype(np.int64), z.astype(np.int8), z.astype(np.int64),
                   z, z)

    def append(self, other: _Store) -> None:
        for name in ("rep", "time", "is_cash", "purchase", "fee", "cash"):
            setattr(self, name, np.concatenate([getattr(self, name), getattr(other, name)]))

    def keep(self, mask: np.ndarray) -> None:
        for name in ("rep", "time", "is_cash", "purchase", "fee", "cash"):
            setattr(self, name, getattr(self, name)[mask])


def _batch_events(batch: CycleBatch, rep_of: np.ndarray, start_of: np.ndarray) -> _Store:
    nf, nc = batch.fee_cycle.size, batch.cash_cycle.size
    return _Store(
        rep=np.concatenate([rep_of[batch.fee_cycle], rep_of[batch.cash_cycle]]),
        time=np.concatenate([start_of[batch.fee_cycle] + batch.fee_time,
                             start_of[batch.cash_cycle] + batch.cash_time]),
        is_cash=np.concatenate([np.zeros(nf, dtype=np.int8), np.ones(nc, dtype=np.int8)]),
        purchase=np.concatenate([np.isin(batch.fee_kind, PURCHASE_KINDS).astype(np.int64),
                                 np.zeros(nc, dtype=np.int64)]),
        fee=np.concatenate([batch.fee_usd, np.zeros(nc)]),
        cash=np.concatenate([np.zeros(nf), batch.cash_usd]),
    )


def _first_crossings(cash: np.ndarray, purchase: np.ndarray, targets: Sequence[float],
                     cap: int) -> tuple[list[int], int]:
    """Indices of the first event where cumulative cash >= each target, and where purchases > cap
    (len(cash) when never)."""
    cum_cash = np.cumsum(cash)
    hit = [int(np.searchsorted(cum_cash, tgt, side="left")) for tgt in targets]
    over = int(np.searchsorted(np.cumsum(purchase), cap, side="right"))
    return hit, over


def _evaluate_open(store: _Store, open_reps: np.ndarray, horizon: np.ndarray,
                   targets: Sequence[float], cap: int, out: dict[str, np.ndarray],
                   offset: int) -> np.ndarray:
    """Settle the open replications whose outcome is fixed by the events before their horizon
    (every slot's cycles reach it); returns the mask of settled reps within ``open_reps``."""
    sel = store.time < horizon[store.rep]
    rep, time = store.rep[sel], store.time[sel]
    order = np.lexsort((store.is_cash[sel], time, rep))
    rep, time = rep[order], time[order]
    purchase, fee, cash = store.purchase[sel][order], store.fee[sel][order], store.cash[sel][order]
    lo = np.searchsorted(rep, open_reps, side="left")
    hi = np.searchsorted(rep, open_reps, side="right")
    settled = np.zeros(open_reps.size, dtype=bool)
    for i, (r, a, b) in enumerate(zip(open_reps, lo, hi, strict=True)):
        hit, over = _first_crossings(cash[a:b], purchase[a:b], targets, cap)
        n = b - a
        if hit[-1] == n and over == n:
            continue
        settled[i] = True
        cum_p, cum_f = np.cumsum(purchase[a:b]), np.cumsum(fee[a:b])
        for ti, h in enumerate(hit):
            if h < n and h < over:
                out["reached"][ti, offset + r] = True
                out["purchases"][ti, offset + r] = cum_p[h]
                out["fees"][ti, offset + r] = cum_f[h]
                out["days"][ti, offset + r] = time[a + h]
    return settled


def _draw_round(rng: np.random.Generator, n: int, attempts: AttemptPool, xfas: XfaPool,
                terms: FeeTerms) -> list[tuple[CycleBatch, np.ndarray, np.ndarray]]:
    parts = []
    for b0 in range(0, n, ASSEMBLY_BATCH):
        parts.append(draw_cycles(rng, min(ASSEMBLY_BATCH, n - b0), attempts, xfas, terms))
    return parts


def _campaign_chunk(rng: np.random.Generator, n_reps: int, offset: int, attempts: AttemptPool,
                    xfas: XfaPool, terms: FeeTerms, slots: int, targets: Sequence[float],
                    cap: int, first_round: int, out: dict[str, np.ndarray],
                    trace_rows: list[dict[str, np.ndarray]] | None) -> tuple[int, int]:
    slot_time = np.zeros((n_reps, slots), dtype=np.int64)
    slot_count = 0
    open_reps = np.arange(n_reps)
    store = _Store.empty()
    k, drawn, overflow = first_round, 0, 0
    while open_reps.size:
        u = open_reps.size
        parts = _draw_round(rng, u * slots * k, attempts, xfas, terms)
        dur = np.concatenate([p[0].end for p in parts]).reshape(u, slots, k)
        base = slot_time[open_reps]
        starts = (base[:, :, None] + np.cumsum(dur, axis=2) - dur).reshape(-1)
        slot_time[open_reps] = base + dur.sum(axis=2)
        rep_of = np.repeat(open_reps, slots * k)
        b0 = 0
        for batch, att, xfa in parts:
            sl = slice(b0, b0 + batch.n)
            store.append(_batch_events(batch, rep_of[sl], starts[sl]))
            overflow += int(batch.overflow_xfas.sum())
            if trace_rows is not None:
                st = starts[sl]
                trace_rows.append({
                    "rep": offset + rep_of[sl],
                    "slot": np.tile(np.repeat(np.arange(slots), k), u)[sl],
                    "order": slot_count + np.tile(np.arange(k), u * slots)[sl],
                    "start": st, "end": st + batch.end, "att_idx": att, "xfa_idx": xfa,
                    "xfa_start": np.where(batch.xfa_start >= 0, batch.xfa_start + st[:, None], -1),
                    "xfa_end": np.where(batch.xfa_end >= 0, batch.xfa_end + st[:, None], -1),
                })
            b0 += batch.n
        drawn += u * slots * k
        slot_count += k
        settled = _evaluate_open(store, open_reps, slot_time.min(axis=1), targets, cap, out,
                                 offset)
        open_reps = open_reps[~settled]
        store.keep(np.isin(store.rep, open_reps))
        k = min(2 * k, MAX_ROUND_CYCLES)
    return drawn, overflow


def run_campaign(attempts: AttemptPool, xfas: XfaPool, terms: FeeTerms, *, slots: int,
                 max_active_xfas: int, n_reps: int, seed: int,
                 targets: Sequence[float] = DEFAULT_TARGETS,
                 purchase_cap: int = DEFAULT_PURCHASE_CAP, rep_chunk: int = 1000,
                 first_round: int = 4, trace: bool = False) -> CampaignResult:
    """sim_spec section 5 campaign: ``slots`` independent slots run cycles back to back (so at most
    ``slots`` <= max_active_xfas XFAs are live); per replication, the Combine purchases, fees and
    elapsed days when cumulative user cash first reaches each target. QUESTION: "not reached" when
    more than ``purchase_cap`` purchases are made by then (purchases on the target's day count)."""
    if not 1 <= slots <= max_active_xfas:
        raise ValueError(f"slots must be in 1..{max_active_xfas}, got {slots}")
    tg = tuple(float(t) for t in targets)
    if not tg or any(t <= 0 for t in tg) or list(tg) != sorted(tg):
        raise ValueError(f"targets must be positive and ascending, got {targets}")
    if n_reps < 1 or purchase_cap < 1 or rep_chunk < 1 or first_round < 1:
        raise ValueError("n_reps, purchase_cap, rep_chunk and first_round must be >= 1")
    rng = np.random.Generator(np.random.PCG64(seed))
    shape = (len(tg), n_reps)
    out = {"reached": np.zeros(shape, dtype=bool), "purchases": np.full(shape, -1, dtype=np.int64),
           "fees": np.full(shape, np.nan), "days": np.full(shape, -1, dtype=np.int64)}
    rows: list[dict[str, np.ndarray]] | None = [] if trace else None
    drawn = overflow = 0
    for c0 in range(0, n_reps, rep_chunk):
        d, o = _campaign_chunk(rng, min(rep_chunk, n_reps - c0), c0, attempts, xfas, terms, slots,
                               tg, purchase_cap, first_round, out, rows)
        drawn, overflow = drawn + d, overflow + o
    tr = None
    if rows is not None:
        tr = CampaignTrace(**{name: np.concatenate([r[name] for r in rows])
                              for name in CampaignTrace.__dataclass_fields__})
    return CampaignResult(targets=tg, slots=slots, purchase_cap=purchase_cap, cycles_drawn=drawn,
                          overflow_xfas=overflow, trace=tr, **out)


def campaign_scalar(slot_cycles: Sequence[Sequence[Cycle]], targets: Sequence[float],
                    purchase_cap: int) -> list[tuple[bool, int, float, int]]:
    """Reference for one replication: lay each slot's cycles back to back, merge every event in
    time order (fees before cash on the same day) and read off each target."""
    events = []
    for cycles in slot_cycles:
        t0 = 0
        for cyc in cycles:
            events += [(t0 + t, 0, int(kind in PURCHASE_KINDS), usd, 0.0)
                       for t, usd, kind in cyc.fees]
            events += [(t0 + t, 1, 0, 0.0, usd) for t, usd in cyc.cash]
            t0 += cyc.end
    events.sort(key=lambda e: (e[0], e[1]))
    result = []
    for target in targets:
        cash = purchases = 0
        fees = 0.0
        found = (False, -1, float("nan"), -1)
        for time, _, is_purchase, fee, usd in events:
            purchases += is_purchase
            fees += fee
            cash += usd
            if purchases > purchase_cap:
                break
            if cash >= target:
                found = (True, purchases, fees, time)
                break
        result.append(found)
    return result


def campaign_quantiles(result: CampaignResult, probs: Sequence[float] = (0.5, 0.8)
                       ) -> dict[float, dict[str, float]]:
    """P50 / P80 per target: the smallest K reached with that probability (inf when the share of
    replications reaching the target is below it)."""
    summary: dict[float, dict[str, float]] = {}
    for ti, target in enumerate(result.targets):
        reached = result.reached[ti]
        row = {"share_reached": float(reached.mean())}
        for name in ("purchases", "fees", "days"):
            values = np.where(reached, getattr(result, name)[ti].astype(np.float64), np.inf)
            for p in probs:
                row[f"{name}_p{round(p * 100)}"] = float(np.quantile(values, p,
                                                                     method="inverted_cdf"))
        summary[target] = row
    return summary
