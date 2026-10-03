"""Payout simulation of ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md V2.9 "Payout simulation", V2.8).

Inputs are per-trade-date records of the portfolio's trips (simulate.run_portfolio): per trade,
P&L and worst intraday excursion per contract in dollars and the V2.8 risk quantities.

``run_path`` is the specification (deterministic; the tests pin it to the cent). Per date:
1. a breached account waits ``reset_delay_dates`` and restarts when ``restart`` (expected resets);
   a halted one (KS2b) stops for good;
2. payout request at the start of the date when the window of closed dates since the last payout
   is eligible (Standard: ``standard_min_days`` dates of >= $150 net, and a positive window net
   after a first payout; Consistency: ``consistency_min_days`` traded dates, positive net, largest
   traded date <= 40% of it): the largest allowed amount under the policy (lead ruling
   2026-10-03), min(cap x DLL multiplier when the DLL was added, 50% of the balance, balance -
   keep_d_frac x MLL), floored to the cent, requested only if >= the $125 minimum.
   keep_d_frac = PAYOUT_KEEP_D_FRAC (0.5) keeps D = balance - $0 floor >= 0.5 x MLL after a
   payout, so a payout never trips KS2 or KS2b by itself; keep_d_frac = 0.0 is the old policy
   (the largest amount the Payout Policy allows). The balance is
   debited, the floor is reset to the post-payout floor ($0 balance), the window restarts and the
   request date's own close does not count (rules.xfa_rules.process_payout / debit_payout);
3. D_open = balance - floor; kill switches (``ks``): KS3 skip, KS2b halt (killswitch.py);
4. each trade is re-sized with sizing.contracts from the path's own D (D_now = D_open + the net
   of the date's trades closed before its entry; capacity = the tier at the prior close less the
   margin and the lot-equivalents of the date's trades still open at its entry; the tier is read
   from the balance at the prior session's close, before that date's payout debit (V2.8; code
   review C-09; a restarted account's prior close is its starting balance); KS2's multiplier
   when ``ks`` or ``ks2_sizing``); with unknown entry/exit times every earlier trade of the date
   counts as open (conservative). The date starts with the variance budget (0.10 x D_open)^2 and
   each taken trade consumes (n x sigma x tick value)^2 (design review D-03, sizing.py). A trade
   re-sized from the engine's n to n' is re-priced for the beyond-q_c surcharge (design review
   D-08a): per contract, + tick value x (excess(n) - excess(n')) with excess(n) = 2 x (n - q_c)^+
   / n ticks (sizing.excess_cost_ticks; the record's P&L already holds the engine's own surcharge
   at n; a record without q_c is not re-priced);
5. the date's intraday worst = the sum of the taken trades' worst excursions x contracts
   (conservative: they are assumed to coincide). A stop level s = KS1's (0.30 x D_open, or the
   DLL if nearer) and/or the DLL: when the worst reaches -min(s, D_open), the date ends at -s if
   s < D_open (stopped, flat), else the real-time MLL is breached (the touch counts);
6. end of date: balance += P&L, floor = max(floor, min(balance - MLL, lock)), the window gains the
   date unless it was a request date, KS3's counter moves.

Ruin (design review D-01): a path is ruined at the first date whose close leaves D = balance -
floor at or below KS2B_HALT_BELOW x MLL (the KS2b level); a breach (D = 0 after the liquidation at
the floor) is ruin too. ``first_ruin_day`` / ``ruin_prob`` is that event, ``first_breach_day`` /
``breach_only_prob`` the plain MLL breach. Under D-proportional sizing a breach is rare by
construction; the KS2b level is what ends the income.

Property of step 5 the lead should know: with ``ks=True`` the KS1 stop (0.30 x D_open) always comes
before the MLL (1.0 x D_open), so a path can never breach under this approximation (the stop is
assumed to fill at its level). The verdict reads ruin with KS1, KS3 and KS4 off and KS2's
half-size multiplier on (it is sizing, not a stop): ``ks=False, ks2_sizing=True``, the ``False``
entry of ``simulate_payouts_pair`` (design review D-01; KS2b does not halt there, its level is the
ruin event). ``simulate_payouts_pair`` gives both figures from one bootstrap draw.

``simulate_payouts`` runs the same rules vectorized over paths of a stationary block bootstrap of
trade dates (mean block PAYOUT_BLOCK_MEAN, seeded); a test pins it to ``run_path`` path for path.
Five copied accounts are one draw (F11): payouts x n_accounts, the same ruin.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from math import inf, isfinite

import numpy as np

from ml_route_v2.account import AccountSpec, payout_cap_usd, tier_max_tenths, trail_floor
from ml_route_v2.constants import (
    BEYOND_QC_EXTRA_TICKS_PER_SIDE,
    DAILY_SIGMA_FRACTION,
    KS1_DAILY_LOSS_FRACTION,
    KS2_HALF_SIZE_BELOW,
    KS2_SIZE_MULTIPLIER,
    KS2B_HALT_BELOW,
    KS3_LOSING_DATES,
    N_COPIED_ACCOUNTS,
    PAYOUT_BLOCK_MEAN,
    PAYOUT_HORIZON_DATES,
    PAYOUT_KEEP_D_FRAC,
    PAYOUT_PATHS,
    PAYOUT_RESET_DELAY_DATES,
    RISK_ROUND_UP_RATIO,
    RISK_SPLIT_M,
    SEED,
    TRADE_DATES_PER_MONTH,
    TRADE_LOSS_FRACTION,
)
from ml_route_v2.killswitch import KillSwitches
from ml_route_v2.portfolio import MARGIN_TENTHS, vehicle_facts
from ml_route_v2.sizing import (
    FLOOR_GUARD,
    budget_use,
    contracts,
    daily_variance_budget,
    excess_cost_ticks,
)
from rules.products import TENTHS_PER_LOT
from rules.xfa_rules import BPS

ACTIVE, BREACHED, WAITING, HALTED = 0, 1, 2, 3
STATUS_NAMES = {ACTIVE: "active", BREACHED: "breached", WAITING: "breached", HALTED: "halted"}


# ------------------------------------------------------------------------------- records ----
@dataclass(frozen=True)
class TradeRecord:
    """One trip of the portfolio run (interfaces section 7, plus cluster and the entry/exit
    fill times, which re-sizing needs for concurrency; 0 means unknown)."""

    root: str
    horizon: str
    trade_date: date
    contracts: int
    pnl_usd_per_contract: float
    worst_usd_per_contract: float
    sigma_ticks: float
    loss_ticks: float
    cost_ticks: float
    tick_value_usd: float
    lot_equiv: float
    cluster: str = ""
    entry_ts_ns: int = 0
    exit_ts_ns: int = 0
    q_c: int | None = None  # D2's size of the vehicle (D-08a re-pricing); None: not re-priced

    def __post_init__(self) -> None:
        nums = (self.pnl_usd_per_contract, self.worst_usd_per_contract, self.sigma_ticks,
                self.loss_ticks, self.cost_ticks, self.tick_value_usd, self.lot_equiv)
        if not all(isfinite(x) for x in nums):
            raise ValueError(f"trade_record_not_finite: {self}")
        if self.sigma_ticks <= 0 or self.tick_value_usd <= 0 or self.lot_equiv <= 0:
            raise ValueError(f"trade_record_bad_risk: {self}")
        if self.loss_ticks < 0 or self.cost_ticks < 0 or self.loss_ticks + self.cost_ticks <= 0:
            raise ValueError(f"trade_record_bad_loss: {self}")
        if self.worst_usd_per_contract > self.pnl_usd_per_contract:
            raise ValueError(f"trade_record_worst_above_pnl: {self}")
        if self.q_c is not None and (self.q_c < 0 or self.contracts < 1):
            raise ValueError(f"trade_record_bad_q_c: {self}")

    @property
    def times_known(self) -> bool:
        return self.entry_ts_ns > 0 and self.exit_ts_ns > 0

    @property
    def lot_tenths(self) -> int:
        return round(self.lot_equiv * TENTHS_PER_LOT)

    def resize_adjustment_usd(self, n: int) -> float:
        """Per-contract $ added to the P&L and the worst excursion when re-sized from the
        engine's ``contracts`` to n: tick value x (excess(contracts) - excess(n)) (D-08a)."""
        return self.tick_value_usd * (excess_cost_ticks(self.contracts, self.q_c)
                                      - excess_cost_ticks(n, self.q_c))


@dataclass(frozen=True)
class DayRecord:
    trade_date: date
    trades: tuple[TradeRecord, ...] = ()


@dataclass(frozen=True)
class Payout:
    day_index: int
    trade_date: date
    account_index: int
    amount_usd: float
    net_usd: float  # after the split


@dataclass(frozen=True)
class PathResult:
    status: str  # final: active | breached | halted
    first_breach_day: int | None
    halt_day: int | None
    n_breaches: int
    payouts: tuple[Payout, ...]
    balance: tuple[float, ...]  # end of each date
    floor: tuple[float, ...]
    day_pnl: tuple[float, ...]
    contracts: tuple[tuple[int, ...], ...]  # per date, per trade (0 = not taken)
    stopped: tuple[bool, ...]  # the date ended at a stop (KS1 or DLL)
    first_ruin_day: int | None = None  # D-01: first close with D <= 0.25 x MLL, or a breach

    @property
    def first_account_payouts(self) -> tuple[Payout, ...]:
        return tuple(p for p in self.payouts if p.account_index == 0)


# ------------------------------------------------------------------------- shared pieces ----
def _cents_floor(x: float) -> float:
    """Floor to the cent after stripping float noise (np.round, used by both implementations)."""
    return float(np.floor(np.round(x * 100.0, 6)) / 100.0)


@dataclass
class _Window:
    """Payout-window aggregates since the last payout (mutable local bookkeeping of run_path)."""

    n_win: int = 0
    net: float = 0.0
    n_traded: int = 0
    traded_sum: float = 0.0
    traded_max: float = -inf

    def add(self, pnl: float, traded: bool, account: AccountSpec) -> None:
        self.n_win += pnl >= account.standard_winning_day_usd
        self.net += pnl
        if traded:
            self.n_traded += 1
            self.traded_sum += pnl
            self.traded_max = max(self.traded_max, pnl)


def _largest_bps(account: AccountSpec) -> int:
    return round(account.consistency_largest_frac * BPS)


def _eligible(w: _Window, payouts_processed: int, account: AccountSpec, path_type: str) -> bool:
    if path_type == "standard":
        if w.n_win < account.standard_min_days:
            return False
        return not (payouts_processed > 0 and w.net <= 0)
    if w.n_traded < account.consistency_min_days or w.traded_sum <= 0:
        return False
    return w.traded_max * BPS <= _largest_bps(account) * w.traded_sum


def _check_args(account: AccountSpec, path_type: str, reset_delay_dates: int,
                keep_d_frac: float) -> None:
    payout_cap_usd(account, path_type, False)  # raises on an unknown path type
    if reset_delay_dates < 0:
        raise ValueError(f"payout_bad_reset_delay: {reset_delay_dates}")
    if not (isfinite(keep_d_frac) and keep_d_frac >= 0.0):
        raise ValueError(f"payout_bad_keep_d_frac: {keep_d_frac}")


def payout_amount(account: AccountSpec, cap_usd: float, balance_usd: float,
                  keep_d_frac: float) -> float:
    """The policy's request: min(cap, ceiling x balance, balance - keep_d_frac x MLL), floored to
    the cent (may be below the minimum; the caller then requests nothing)."""
    return _cents_floor(min(cap_usd, account.balance_ceiling_frac * balance_usd,
                            balance_usd - keep_d_frac * account.mll_usd))


# ------------------------------------------------------------------------------ run_path ----
@dataclass
class _Acct:
    balance: float
    floor: float
    window: _Window = field(default_factory=_Window)
    payouts_processed: int = 0
    exclude_next: bool = False


def _new_acct(account: AccountSpec) -> _Acct:
    start = account.starting_balance_usd
    return _Acct(start, start - account.mll_usd)


def _new_ks(account: AccountSpec, dll: bool) -> KillSwitches:
    return KillSwitches(account.mll_usd, account.dll_usd if dll else None)


def run_path(days: Sequence[DayRecord], account: AccountSpec, *, path_type: str, dll: bool,
             ks: bool = True, restart: bool = False,
             reset_delay_dates: int = PAYOUT_RESET_DELAY_DATES,
             keep_d_frac: float = PAYOUT_KEEP_D_FRAC,
             ks2_sizing: bool | None = None) -> PathResult:
    """One account path over ``days`` (deterministic). See the module docstring for the rules.
    ``ks2_sizing``: KS2's half-size multiplier on or off; None follows ``ks``."""
    _check_args(account, path_type, reset_delay_dates, keep_d_frac)
    cap = payout_cap_usd(account, path_type, dll)
    use_ks2 = ks if ks2_sizing is None else bool(ks2_sizing)
    ruin_level = KS2B_HALT_BELOW * account.mll_usd
    acct, switches = _new_acct(account), _new_ks(account, dll)
    status, wait, account_index = ACTIVE, 0, 0
    first_breach = halt_day = None
    n_breaches = 0
    payouts: list[Payout] = []
    bal, flo, pnl_out, n_out, stop_out, ruined = [], [], [], [], [], []

    def record(pnl: float, sizes: tuple[int, ...], stopped: bool) -> None:
        bal.append(acct.balance)
        flo.append(acct.floor)
        pnl_out.append(pnl)
        n_out.append(sizes)
        stop_out.append(stopped)
        if not ruined and acct.balance - acct.floor <= ruin_level:
            ruined.append(len(bal) - 1)  # D-01: D at this close (0 after a breach)

    for i, day in enumerate(days):
        if status == WAITING:
            if wait > 0:
                wait -= 1
                record(0.0, (), False)
                continue
            acct, switches = _new_acct(account), _new_ks(account, dll)
            status, account_index = ACTIVE, account_index + 1
        if status != ACTIVE:
            record(0.0, (), False)
            continue
        # V2.8: the tier at the prior session's close, before this date's payout debit (C-09)
        tier = tier_max_tenths(account, acct.balance)
        # 2. payout request at the start of the date
        if _eligible(acct.window, acct.payouts_processed, account, path_type):
            amount = payout_amount(account, cap, acct.balance, keep_d_frac)
            if amount >= account.min_payout_usd:
                acct.balance -= amount
                acct.floor = account.post_payout_floor_usd
                acct.window = _Window()
                acct.payouts_processed += 1
                acct.exclude_next = True
                payouts.append(Payout(i, day.trade_date, account_index, amount,
                                      amount * account.split))
        # 3. D_open and the kill switches
        d_open = acct.balance - acct.floor
        if ks:
            switches = switches.start_day(d_open)
            if switches.halted:
                status, halt_day = HALTED, i
                record(0.0, (), False)
                continue
        # 4. re-size the date's trades (the daily risk budget, D-03)
        budget = daily_variance_budget(d_open)
        taken: list[tuple[TradeRecord, int, float]] = []
        sizes: list[int] = []
        pnl_sum = worst_sum = 0.0
        for tr in day.trades:
            realized = 0.0
            open_tenths = 0
            for prev, n_prev, net_prev in taken:
                if tr.times_known and prev.times_known and prev.exit_ts_ns <= tr.entry_ts_ns:
                    realized += net_prev
                else:
                    open_tenths += n_prev * prev.lot_tenths
            d_now = d_open + realized
            mult = 1.0
            if ks:
                switches, allowed = switches.on_entry(d_now)
                if not allowed:
                    sizes.append(0)
                    continue
            if use_ks2:
                mult = switches.size_multiplier(d_now)
            capacity = max(tier - MARGIN_TENTHS - open_tenths, 0) // tr.lot_tenths
            n = contracts(d_open=d_open, d_now=d_now, sigma_ticks=tr.sigma_ticks,
                          loss_ticks=tr.loss_ticks, cost_ticks=tr.cost_ticks,
                          tick_value_usd=tr.tick_value_usd,
                          product_cap=vehicle_facts(tr.root).product_cap,
                          capacity_contracts=capacity, multiplier=mult, budget_var=budget)
            sizes.append(n)
            if n < 1:
                continue
            budget = budget - budget_use(n, tr.sigma_ticks, tr.tick_value_usd)
            adj = tr.resize_adjustment_usd(n)
            net = n * (tr.pnl_usd_per_contract + adj)
            taken.append((tr, n, net))
            pnl_sum += net
            worst_sum += n * (tr.worst_usd_per_contract + adj)
        # 5. stops and the real-time MLL on the date's intraday worst
        stop = inf
        if ks:
            stop = switches.ks1_threshold()
        if dll:
            stop = min(stop, account.dll_usd)
        day_pnl, stopped, breach = pnl_sum, False, False
        if worst_sum <= -min(stop, d_open):
            if stop < d_open:
                day_pnl, stopped = -stop, True
            else:
                breach = True
        if not breach and acct.balance + day_pnl <= acct.floor:
            breach = True  # end-of-day check (cannot trigger after step 5; kept as the rule)
        if breach:
            loss = acct.floor - acct.balance
            acct.balance = acct.floor  # liquidated at the floor
            n_breaches += 1
            first_breach = i if first_breach is None else first_breach
            status, wait = (WAITING, reset_delay_dates) if restart else (BREACHED, 0)
            record(loss, tuple(sizes), False)
            continue
        # 6. end of date
        acct.balance += day_pnl
        acct.floor = trail_floor(account, acct.floor, acct.balance)
        if not acct.exclude_next:
            acct.window.add(day_pnl, bool(taken), account)
        acct.exclude_next = False
        if ks:
            switches = switches.end_day(day_pnl)
            if switches.halted:
                status, halt_day = HALTED, i
        record(day_pnl, tuple(sizes), stopped)
    return PathResult(STATUS_NAMES[status], first_breach, halt_day, n_breaches, tuple(payouts),
                      tuple(bal), tuple(flo), tuple(pnl_out), tuple(n_out), tuple(stop_out),
                      ruined[0] if ruined else None)


# --------------------------------------------------------------------- vectorized paths ----
@dataclass(frozen=True)
class _Packed:
    """The base dates' trades as [n_days, K] arrays (K = most trades on one date)."""

    valid: np.ndarray
    pnl: np.ndarray
    worst: np.ndarray
    sigma: np.ndarray
    loss: np.ndarray
    cost: np.ndarray
    tv: np.ndarray
    tenths: np.ndarray
    pcap: np.ndarray
    qc: np.ndarray  # D2's q_c as float; inf when unknown (no D-08a re-pricing)
    xeng: np.ndarray  # excess_cost_ticks at the engine's n (the record's own surcharge)
    closed_before: np.ndarray  # [n_days, K, K]: trade j closed before trade k's entry
    open_before: np.ndarray  # [n_days, K, K]: trade j (j < k) still open at k's entry


def _pack(days: Sequence[DayRecord]) -> _Packed:
    n, k = len(days), max(1, max((len(d.trades) for d in days), default=1))
    f = {name: np.zeros((n, k)) for name in ("pnl", "worst", "sigma", "loss", "cost", "tv")}
    f["sigma"][:] = f["tv"][:] = f["loss"][:] = 1.0  # padding, never taken (valid False)
    valid = np.zeros((n, k), dtype=bool)
    tenths = np.ones((n, k), dtype=np.int64)
    pcap = np.zeros((n, k), dtype=np.int64)
    qc = np.full((n, k), np.inf)
    xeng = np.zeros((n, k))
    closed = np.zeros((n, k, k), dtype=bool)
    open_ = np.zeros((n, k, k), dtype=bool)
    for d, day in enumerate(days):
        for j, tr in enumerate(day.trades):
            valid[d, j] = True
            f["pnl"][d, j], f["worst"][d, j] = tr.pnl_usd_per_contract, tr.worst_usd_per_contract
            f["sigma"][d, j], f["loss"][d, j] = tr.sigma_ticks, tr.loss_ticks
            f["cost"][d, j], f["tv"][d, j] = tr.cost_ticks, tr.tick_value_usd
            tenths[d, j], pcap[d, j] = tr.lot_tenths, vehicle_facts(tr.root).product_cap
            if tr.q_c is not None:
                qc[d, j] = float(tr.q_c)
            xeng[d, j] = excess_cost_ticks(tr.contracts, tr.q_c)
            for i, prev in enumerate(day.trades[:j]):
                c = tr.times_known and prev.times_known and prev.exit_ts_ns <= tr.entry_ts_ns
                closed[d, j, i], open_[d, j, i] = c, not c
    return _Packed(valid, f["pnl"], f["worst"], f["sigma"], f["loss"], f["cost"], f["tv"],
                   tenths, pcap, qc, xeng, closed, open_)


def _contracts_vec(d_open, d_now, sigma, loss, cost, tv, pcap, capacity, mult, rem):  # noqa: ANN001,ANN202
    """sizing.contracts (with ``budget_var`` = rem) over arrays, the same operations in the same
    order."""
    budget = (DAILY_SIGMA_FRACTION * d_open / np.sqrt(RISK_SPLIT_M)) * mult
    one_sigma = sigma * tv
    n_risk = np.floor(budget / one_sigma + FLOOR_GUARD)
    n_risk = np.where((n_risk == 0) & (one_sigma <= RISK_ROUND_UP_RATIO * budget), 1.0, n_risk)
    n_loss = np.floor(TRADE_LOSS_FRACTION * d_now / ((loss + cost) * tv) + FLOOR_GUARD)
    n = np.minimum(np.minimum(n_risk, n_loss), np.minimum(pcap, capacity))
    dead = (d_open <= 0) | (d_now <= 0) | (mult == 0) | (pcap < 1) | (capacity < 1)
    n = np.where(dead, 0.0, np.maximum(n, 0.0))
    n_budget = np.floor(np.sqrt(np.maximum(rem, 0.0)) / (sigma * tv) + FLOOR_GUARD)
    return np.minimum(n, n_budget)


def _excess_vec(n: np.ndarray, qc: np.ndarray) -> np.ndarray:
    """sizing.excess_cost_ticks over arrays (0 where n < 1 or q_c is unknown)."""
    safe = np.where(n >= 1, n, 1.0)
    x = 2.0 * BEYOND_QC_EXTRA_TICKS_PER_SIDE * np.maximum(n - qc, 0.0) / safe
    return np.where(n >= 1, x, 0.0)


def _tier_vec(account: AccountSpec, balance: np.ndarray) -> np.ndarray:
    lots = np.full(balance.shape, account.base_lots)
    for threshold, inclusive, tier_lots in account.scaling_tiers:
        hit = (balance > threshold) | ((balance == threshold) if inclusive else False)
        lots = np.where(hit, tier_lots, lots)
    return np.round(lots * TENTHS_PER_LOT).astype(np.int64)


@dataclass(frozen=True)
class PathArrays:
    """Per-path outcomes of the vectorized simulation (first account unless stated)."""

    net_payouts_first: np.ndarray  # sum of payouts after the split, first account
    n_payouts_first: np.ndarray
    first_payout_day: np.ndarray  # 0-based date index of the first request, -1 if none
    first_breach_day: np.ndarray  # -1 if none
    halt_day: np.ndarray  # -1 if none (a halt is terminal: at most one per path)
    n_breaches: np.ndarray  # with restarts
    net_payouts_all: np.ndarray  # every account of the path
    first_ruin_day: np.ndarray  # D-01: first close with D <= 0.25 x MLL or a breach; -1 if none


def bootstrap_indices(n_days: int, n_paths: int, horizon: int, block_mean: int,
                      seed: int) -> np.ndarray:
    """Stationary block bootstrap (Politis-Romano) of date indices: a new block starts with
    probability 1/block_mean, else the next date (circular)."""
    if n_days < 1 or n_paths < 1 or horizon < 1 or block_mean < 1:
        raise ValueError(f"bootstrap_bad_args: {(n_days, n_paths, horizon, block_mean)}")
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n_days, size=(n_paths, horizon))
    new = rng.random((n_paths, horizon)) < 1.0 / block_mean
    idx = np.empty((n_paths, horizon), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, horizon):
        idx[:, t] = np.where(new[:, t], starts[:, t], (idx[:, t - 1] + 1) % n_days)
    return idx


def simulate_paths(days: Sequence[DayRecord], account: AccountSpec, idx: np.ndarray, *,
                   path_type: str, dll: bool, ks: bool = True, restart: bool = True,
                   reset_delay_dates: int = PAYOUT_RESET_DELAY_DATES,
                   keep_d_frac: float = PAYOUT_KEEP_D_FRAC,
                   ks2_sizing: bool | None = None) -> PathArrays:
    """``run_path`` over every row of ``idx`` (paths of date indices into ``days``), vectorized."""
    _check_args(account, path_type, reset_delay_dates, keep_d_frac)
    use_ks2 = ks if ks2_sizing is None else bool(ks2_sizing)
    ruin_level = KS2B_HALT_BELOW * account.mll_usd
    pk = _pack(days)
    p, horizon = idx.shape
    k_max = pk.valid.shape[1]
    cap = payout_cap_usd(account, path_type, dll)
    mll, lbps = account.mll_usd, _largest_bps(account)
    start = account.starting_balance_usd
    bal, flo = np.full(p, start), np.full(p, start - mll)
    status, wait = np.full(p, ACTIVE), np.zeros(p, dtype=np.int64)
    acct_ix = np.zeros(p, dtype=np.int64)
    w_win, w_tr, w_pay = (np.zeros(p, dtype=np.int64) for _ in range(3))
    w_net, w_sum, w_max = np.zeros(p), np.zeros(p), np.full(p, -inf)
    excl, streak = np.zeros(p, dtype=bool), np.zeros(p, dtype=np.int64)
    halted_ks = np.zeros(p, dtype=bool)
    out_first, n_first = np.zeros(p), np.zeros(p, dtype=np.int64)
    out_all = np.zeros(p)
    first_pay, first_breach, halt_day, first_ruin = (np.full(p, -1) for _ in range(4))
    n_breach = np.zeros(p, dtype=np.int64)

    def reset_window(mask: np.ndarray) -> None:
        w_win[mask], w_net[mask], w_tr[mask], w_sum[mask], w_max[mask] = 0, 0.0, 0, 0.0, -inf

    for t in range(horizon):
        d = idx[:, t]
        # 1. restarts
        waiting = status == WAITING
        tick_down = waiting & (wait > 0)
        wait[tick_down] -= 1
        fresh = waiting & ~tick_down
        bal[fresh], flo[fresh] = start, start - mll
        reset_window(fresh)
        w_pay[fresh], excl[fresh], streak[fresh], halted_ks[fresh] = 0, False, 0, False
        status[fresh], acct_ix[fresh] = ACTIVE, acct_ix[fresh] + 1
        act = status == ACTIVE
        tier = _tier_vec(account, bal)  # the prior close, before the payout debit (C-09)
        # 2. payouts
        if path_type == "standard":
            elig = (w_win >= account.standard_min_days) & ~((w_pay > 0) & (w_net <= 0))
        else:
            elig = ((w_tr >= account.consistency_min_days) & (w_sum > 0)
                    & (w_max * BPS <= lbps * w_sum))
        wanted = np.minimum(np.minimum(cap, account.balance_ceiling_frac * bal),
                            bal - keep_d_frac * mll)
        amount = np.floor(np.round(wanted * 100.0, 6)) / 100.0
        pay = act & elig & (amount >= account.min_payout_usd)
        bal[pay] -= amount[pay]
        flo[pay] = account.post_payout_floor_usd
        reset_window(pay)
        w_pay[pay] += 1
        excl[pay] = True
        net_amt = amount * account.split
        first_acct = pay & (acct_ix == 0)
        out_first[first_acct] += net_amt[first_acct]
        n_first[first_acct] += 1
        out_all[pay] += net_amt[pay]
        first_pay[first_acct & (first_pay < 0)] = t
        # 3. D_open and kill switches
        d_open = bal - flo
        skip = np.zeros(p, dtype=bool)
        if ks:
            skip = act & (streak >= KS3_LOSING_DATES)
            streak[skip] = 0
            halted_ks |= act & (d_open < KS2B_HALT_BELOW * mll)
            stop_now = act & halted_ks
            status[stop_now] = HALTED
            halt_day[stop_now & (halt_day < 0)] = t
            act = act & ~stop_now
        # 4. trades
        rem = daily_variance_budget(d_open)  # D-03
        net_t = np.zeros((p, k_max))
        ten_t = np.zeros((p, k_max), dtype=np.int64)
        pnl_sum, worst_sum = np.zeros(p), np.zeros(p)
        taken_any = np.zeros(p, dtype=bool)
        for k in range(k_max):
            live = act & pk.valid[d, k]
            realized = np.zeros(p)
            open_ten = np.zeros(p, dtype=np.int64)
            for j in range(k):
                realized = realized + np.where(pk.closed_before[d, k, j], net_t[:, j], 0.0)
                open_ten = open_ten + np.where(pk.open_before[d, k, j], ten_t[:, j], 0)
            d_now = d_open + realized
            mult = np.ones(p)
            if ks:
                halted_ks |= live & (d_now < KS2B_HALT_BELOW * mll)
                live = live & ~halted_ks & ~skip
            if use_ks2:
                mult = np.where(d_now < KS2_HALF_SIZE_BELOW * mll, KS2_SIZE_MULTIPLIER, 1.0)
            capacity = np.maximum(tier - MARGIN_TENTHS - open_ten, 0) // pk.tenths[d, k]
            n = _contracts_vec(d_open, d_now, pk.sigma[d, k], pk.loss[d, k], pk.cost[d, k],
                               pk.tv[d, k], pk.pcap[d, k], capacity, mult, rem)
            n = np.where(live, n, 0.0)
            took = n >= 1
            rem = rem - np.where(took, (n * (pk.sigma[d, k] * pk.tv[d, k])) ** 2, 0.0)
            adj = pk.tv[d, k] * (pk.xeng[d, k] - _excess_vec(n, pk.qc[d, k]))
            net_t[:, k] = np.where(took, n * (pk.pnl[d, k] + adj), 0.0)
            ten_t[:, k] = np.where(took, n.astype(np.int64) * pk.tenths[d, k], 0)
            pnl_sum = pnl_sum + net_t[:, k]
            worst_sum = worst_sum + np.where(took, n * (pk.worst[d, k] + adj), 0.0)
            taken_any |= took
        # 5. stops and the real-time MLL
        stop = np.full(p, inf)
        if ks:
            ks1 = KS1_DAILY_LOSS_FRACTION * d_open
            stop = np.minimum(ks1, account.dll_usd) if dll else ks1
        if dll:
            stop = np.minimum(stop, account.dll_usd)
        hit = act & (worst_sum <= -np.minimum(stop, d_open))
        stopped = hit & (stop < d_open)
        breach = hit & ~stopped
        day_pnl = np.where(stopped, -stop, pnl_sum)
        breach |= act & ~breach & (bal + day_pnl <= flo)
        bal[breach] = flo[breach]
        n_breach[breach] += 1
        first_breach[breach & (acct_ix == 0) & (first_breach < 0)] = t
        if restart:
            status[breach], wait[breach] = WAITING, reset_delay_dates
        else:
            status[breach] = BREACHED
        # 6. end of date
        ok = act & ~breach
        bal[ok] += day_pnl[ok]
        flo[ok] = np.maximum(flo[ok], np.minimum(bal[ok] - mll, account.mll_lock_usd))
        add = ok & ~excl
        w_win[add] += day_pnl[add] >= account.standard_winning_day_usd
        w_net[add] += day_pnl[add]
        tr = add & taken_any
        w_tr[tr] += 1
        w_sum[tr] += day_pnl[tr]
        w_max[tr] = np.maximum(w_max[tr], day_pnl[tr])
        excl[ok] = False
        if ks:
            streak[ok] = np.where(day_pnl[ok] < 0, streak[ok] + 1, 0)
            late = ok & halted_ks
            status[late] = HALTED
            halt_day[late & (halt_day < 0)] = t
        # D-01: D at this close (0 after a breach); every path records a close each date
        first_ruin[(bal - flo <= ruin_level) & (first_ruin < 0)] = t
    return PathArrays(out_first, n_first, first_pay, first_breach, halt_day, n_breach, out_all,
                      first_ruin)


# ------------------------------------------------------------------------------ summary ----
@dataclass(frozen=True)
class PayoutSummary:
    account: str
    path_type: str
    dll: bool
    ks: bool
    ks2_sizing: bool  # KS2's half-size multiplier on (the verdict reading has it on, D-01)
    n_paths: int
    horizon: int
    n_accounts: int
    monthly_net_mean: float  # after the split, x n_accounts (one draw, F11)
    monthly_net_median: float
    monthly_net_p10: float
    monthly_net_p90: float
    ruin_prob: float  # D-01: first account ruined (breach, or D <= 0.25 x MLL at a close)
    breach_only_prob: float  # first account's MLL breached within the horizon
    halt_prob: float  # the path halted by KS2b within the horizon
    p_any_payout: float
    first_payout_days_mean: float  # dates to the first request (1-based), NaN if none
    first_payout_days_median: float
    expected_resets: float  # breaches per path over the horizon, with restarts
    mean_payouts_first: float  # requests per path, first account


def summarize(arr: PathArrays, account: AccountSpec, *, path_type: str, dll: bool, ks: bool,
              horizon: int, n_accounts: int, ks2_sizing: bool | None = None) -> PayoutSummary:
    months = horizon / TRADE_DATES_PER_MONTH
    monthly = n_accounts * arr.net_payouts_first / months
    paid = arr.first_payout_day >= 0
    days_to = arr.first_payout_day[paid] + 1.0
    return PayoutSummary(
        account.name, path_type, dll, ks, ks if ks2_sizing is None else bool(ks2_sizing),
        len(monthly), horizon, n_accounts,
        float(np.mean(monthly)), float(np.median(monthly)), float(np.quantile(monthly, 0.10)),
        float(np.quantile(monthly, 0.90)), float(np.mean(arr.first_ruin_day >= 0)),
        float(np.mean(arr.first_breach_day >= 0)),
        float(np.mean(arr.halt_day >= 0)), float(np.mean(paid)),
        float(np.mean(days_to)) if paid.any() else float("nan"),
        float(np.median(days_to)) if paid.any() else float("nan"),
        float(np.mean(arr.n_breaches)), float(np.mean(arr.n_payouts_first)))


def simulate_payouts(days: Sequence[DayRecord], account: AccountSpec, *, path_type: str,
                     dll: bool, n_paths: int = PAYOUT_PATHS, horizon: int = PAYOUT_HORIZON_DATES,
                     block_mean: int = PAYOUT_BLOCK_MEAN, seed: int = SEED,
                     n_accounts: int = N_COPIED_ACCOUNTS, ks: bool = True,
                     reset_delay_dates: int = PAYOUT_RESET_DELAY_DATES,
                     keep_d_frac: float = PAYOUT_KEEP_D_FRAC,
                     ks2_sizing: bool = True) -> PayoutSummary:
    """V2.9's payout simulation: bootstrap paths, run_path's rules, one summary. ``ks=False``
    with the default ``ks2_sizing=True`` is the verdict's reading (design review D-01)."""
    return simulate_payouts_pair(
        days, account, path_type=path_type, dll=dll, n_paths=n_paths, horizon=horizon,
        block_mean=block_mean, seed=seed, n_accounts=n_accounts, ks_values=(ks,),
        reset_delay_dates=reset_delay_dates, keep_d_frac=keep_d_frac,
        ks2_sizing=ks2_sizing)[ks]


def simulate_payouts_pair(days: Sequence[DayRecord], account: AccountSpec, *, path_type: str,
                          dll: bool, n_paths: int = PAYOUT_PATHS,
                          horizon: int = PAYOUT_HORIZON_DATES,
                          block_mean: int = PAYOUT_BLOCK_MEAN, seed: int = SEED,
                          n_accounts: int = N_COPIED_ACCOUNTS,
                          ks_values: Sequence[bool] = (True, False),
                          reset_delay_dates: int = PAYOUT_RESET_DELAY_DATES,
                          keep_d_frac: float = PAYOUT_KEEP_D_FRAC,
                          ks2_sizing: bool = True) -> dict[bool, PayoutSummary]:
    """The summaries with and without kill switches on ONE bootstrap draw (common paths), keyed
    by ``ks``. The verdict's ruin is the ``False`` entry: KS1, KS3 and KS4 off, KS2's sizing on
    (``ks2_sizing``, default True; design review D-01, lead ruling 2026-10-03)."""
    if not days:
        raise ValueError("payout_no_days")
    if n_accounts < 1:
        raise ValueError(f"payout_bad_n_accounts: {n_accounts}")
    idx = bootstrap_indices(len(days), n_paths, horizon, block_mean, seed)
    out = {}
    for ks in ks_values:
        ks2 = bool(ks) or bool(ks2_sizing)
        arr = simulate_paths(days, account, idx, path_type=path_type, dll=dll, ks=ks,
                             restart=True, reset_delay_dates=reset_delay_dates,
                             keep_d_frac=keep_d_frac, ks2_sizing=ks2)
        out[bool(ks)] = summarize(arr, account, path_type=path_type, dll=dll, ks=bool(ks),
                                  horizon=horizon, n_accounts=n_accounts, ks2_sizing=ks2)
    return out


__all__ = [
    "DayRecord", "PathArrays", "PathResult", "Payout", "PayoutSummary", "TradeRecord",
    "bootstrap_indices", "payout_amount", "run_path", "simulate_paths", "simulate_payouts",
    "simulate_payouts_pair", "summarize",
]
