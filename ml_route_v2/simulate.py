"""The v2 portfolio on the frozen Stage E engine (docs/STAGE_E_ML_V2_DESIGN.md V2.8, "The
simulator").

``PortfolioRules`` subclasses screening.stage_e_rules.StageERules. It overrides three parent
methods (screening/stage_e_rules.py; each parent method's sha256 is pinned in the tests) and adds
one field. Two changes sit inside ``StageERules._opening_refusal``, made by handing the parent
method a read-only view of the run whose ``traded`` is the ordered product alone:
- lines 524-526 (``others = [r for r in run.traded if r != root and run.exposure(r)]`` ->
  ``engine_second_leg_position``): ``others`` is always empty, so several products may hold
  positions (the catalog's one-position rule, K8 rule 5, is dropped);
- lines 527-529 (``after = {r: run.exposure(r) for r in run.traded}`` -> ``check_member_size``):
  ``after`` holds only the ordered product, so D9.5's 1-lot-equivalent member cap and D9.11's 50K
  caps apply per product.
The third change, the per-product roll blackout (V2.2, lead ruling 2026-10-03, design fix 8): the
frozen rules hold one blackout set, the union of the traded legs' roll dates (D4), so on any
product's roll date the engine would refuse entries in every product. v2 excludes only each
product's own roll dates. With the field ``product_blackout`` (vehicle root -> its own roll
blackout dates, pipeline.own_blackout: its root's and its price path's), ``_opening_refusal`` runs
the parent method on a copy of the rules (dataclasses.replace) whose ``blackout`` is the ordered
product's own set: an entry in P is refused (``engine_roll_blackout``, the parent's own line and
message) only on P's roll-blackout dates, which keeps the guard against a position spanning P's
contract change. Without ``product_blackout`` (None) the parent's union applies unchanged; with
one traded product and identical sets the two are the same rule.
No parent line is skipped: every other line of ``_opening_refusal`` (window date, roll blackout,
skipped-for-day, passive checks, the entry cap, D9.7) runs on the real run's state through the
view, and everything outside it is inherited unchanged: run_engine, the fills at a later bar's
open, the D9.5a fill guard, the D9.12 CPI window, the price-limit rules, the forced
flatten, the minimum hold, ``gate`` (the XFA scaling plan over ALL products' lot-equivalents) and
the real-time and end-of-day trailing MLL with restart on breach.

Cost beyond D2's size (design review D-08a): ``fill_cost`` and ``close_cost`` call the parent's and
add, for a market fill (and every close at a bar's close) of qty contracts, (qty - q_c)^+ x
BEYOND_QC_EXTRA_TICKS_PER_SIDE ticks x tick value, rounded up to the cent like the parent's
slippage (stage_e_frozen.slippage_cents); q_c is the leg's frozen D2 size
(LegInputs.vehicle.q_c). The override only adds cost: at qty <= q_c the parent's FillCost is
returned unchanged. A passive fill (none in v2: the member issues market intents only) keeps the
parent's cost, since a resting limit order does not reach past the top level.

The combined MLL audit (lead ruling 2026-10-03). The engine's real-time MLL
(stage_e_engine._Run.check_mll) marks each leg's adverse extreme against the floor with that leg's
unrealized P&L alone; with several open positions the combined unrealized loss is not checked
intraday. The engine is not changed. ``combined_mll_audit`` reads its run afterwards: at every
grid minute where two or more legs are open (positions replayed from the Fill ledger with the
engine's own FIFO, in the engine's order: a minute's open fills before its MLL check, an MLL
liquidation after it), the combined worst equity = the realized balance + every open leg's
adverse-extreme unrealized for that bar (low for a long, high for a short; a leg with no tradable
bar that minute is marked at its last tradable close), against the floor in force (the account's
AccountStart floor, then each DayClose's trailed floor). A minute at or below the floor at which
the engine had not breached is a combined breach (PortfolioRun.combined_mll_breaches).
RULE: any combined breach counts as an MLL breach in every verdict.

LABEL (code review C-11): ``run_portfolio``'s record (PortfolioRun.daily, its trips and days) and
its combined-MLL audit are the KILL SWITCHES OFF record. The member sizes with multiplier 1.0 and
implements none of KS1-KS4 (its only skip of that kind is "no bar -> skip", ks5_no_bar); the kill
switches enter only in payout_sim's re-sizing. Reports label these figures "kill switches off"
(engine_stage.ENGINE_KILL_SWITCHES), never as the live system's path.

``PortfolioMember`` implements the member interface (strategy/stage_e/interface.py) from a
precomputed schedule (the candidates frame of interfaces section 6) and the risk table (a
schedule row's own sigma_ticks and loss_ticks when it carries them: the table of the split that
produced it, code review C-04; portfolio.join_risk): at each decision time it sizes with
portfolio.admit (sizing.contracts with D = equity - floor from the account view, and the V2.8
portfolio caps; a row whose sigma or loss is unknown is skipped as risk_unknown, C-02), issues
market intents, and exits at the schedule's exit time; an hF trade, or an exit that falls in
the flatten window, is left to the engine's forced flatten. The release window (V23 item 11;
E.12 lead rule P-5): each schedule row carries targets.py's release_window flag (its entry fill
in [r - 5 min, r + 30 min) of a release of its vehicle's list); portfolio.admit refuses such an
entry when the open lot-equivalents including it would exceed half the tier at the prior
session's close, recorded in ``decisions`` with reason "release_window"; the trade records carry
the flag so payout_sim's re-sizing applies the same rule. The daily risk budget (design review
D-03): each trade date starts with (0.10 x D_open)^2 and every issued entry consumes
(n x sigma(p,h) x tick value)^2 (sizing.daily_variance_budget / budget_use); the budget is
consumed when the intent is issued (an intent the engine then refuses keeps its budget spent:
conservative).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time
from fractions import Fraction
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from ml_route_v2.account import ACCOUNT_50K, AccountSpec
from ml_route_v2.constants import BEYOND_QC_EXTRA_TICKS_PER_SIDE, UNIVERSE
from ml_route_v2.payout_sim import DayRecord, TradeRecord
from ml_route_v2.portfolio import (
    OpenPosition,
    admit,
    join_risk,
    live_tier_tenths,
    rank_candidates,
    vehicle_facts,
)
from ml_route_v2.sizing import budget_use, daily_variance_budget
from rules import sessions
from rules.constraints import CPI_MICRO_MAX_50K, check_cpi_opening
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Status
from screening.stage_e_engine import (
    AccountStart,
    DayClose,
    EngineResult,
    Fill,
    Position,
    apply_fill,
    run_engine,
)
from screening.stage_e_frozen import leg_inputs, slippage_cents
from screening.stage_e_rules import StageERules, load_release_calendar
from screening.stage_e_runner import TripRecord, extract_trips, trip_gross_cents
from sim.fill_model import FillCost
from strategy.interface import NS_PER_S
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
MEMBER_NAME = "ml_v2_portfolio"


# ------------------------------------------------------------------------- the rules ----
class _PerProductRun:
    """A read-only view of the engine's run in which only ``root`` is traded. Everything else
    (positions, pending orders, entries, skipped products, the D9.7 settlement store) is the real
    run's."""

    def __init__(self, run: Any, root: str, settlements: dict) -> None:
        self.__dict__["_run"] = run
        self.__dict__["traded"] = (root,)
        self.__dict__["_stage_e_settlements"] = settlements  # StageERules._settlements reads it

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__dict__["_run"], name)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"_PerProductRun is read-only ({name})")


@dataclass(frozen=True)
class PortfolioRules(StageERules):
    """StageERules with the member caps per product, no one-position-at-a-time refusal, the roll
    blackout per product (``product_blackout``) and the beyond-q_c cost (module docstring)."""

    product_blackout: Mapping[str, frozenset[date]] | None = None  # None: the parent's union

    def __post_init__(self) -> None:
        if self.product_blackout is None:
            return
        missing = sorted(set(self.legs) - set(self.product_blackout))
        if missing:
            raise ValueError(f"portfolio_rules_blackout_missing: no own roll-blackout set for "
                             f"{missing}")

    def _opening_refusal(self, run: Any, norm: Any, bar: Any, decision: datetime) -> Any:
        view = _PerProductRun(run, norm.root, self._settlements(run))
        rules: StageERules = self
        if self.product_blackout is not None:
            rules = replace(self, blackout=frozenset(self.product_blackout[norm.root]),
                            product_blackout=None)
        return StageERules._opening_refusal(rules, view, norm, bar, decision)

    def _beyond_q_c(self, root: str, qty: int, cost: FillCost) -> FillCost:
        leg = self.legs[root]
        excess = qty - leg.vehicle.q_c if leg.vehicle is not None else 0
        if excess <= 0:
            return cost
        extra = slippage_cents(excess, BEYOND_QC_EXTRA_TICKS_PER_SIDE, leg.tick_value_cents)
        return FillCost(cost.qty_micros, cost.commission_cents, cost.slippage_cents + extra,
                        cost.slippage_ticks_per_micro
                        + excess * BEYOND_QC_EXTRA_TICKS_PER_SIDE / qty, cost.statistic)

    def fill_cost(self, run: Any, order: Any, bar: Any, qty: int, side: str, reason: str
                  ) -> tuple[FillCost, bool]:
        cost, event = super().fill_cost(run, order, bar, qty, side, reason)
        if order.is_passive:
            return cost, event
        return self._beyond_q_c(order.root, qty, cost), event

    def close_cost(self, run: Any, root: str, bar: Any, qty: int, side: str
                   ) -> tuple[FillCost, bool]:
        cost, event = super().close_cost(run, root, bar, qty, side)
        return self._beyond_q_c(root, qty, cost), event


# ------------------------------------------------------------------------- the member ----
@dataclass(frozen=True)
class _Plan:
    row_id: int
    root: str
    cluster: str
    horizon: str
    side: int
    decision_ts_ns: int
    exit_ts_ns: int
    sigma_ticks: float
    loss_ticks: float
    cost_ticks: float
    release_window: bool  # V23 item 11: the schedule row's release-window flag (targets.py)


@dataclass(frozen=True)
class MemberDecision:
    decision_ts_ns: int
    row_id: int
    root: str
    contracts: int
    reason: str  # "" when an intent was issued


def _ct_time(ns: int) -> time:
    return datetime.fromtimestamp(ns / NS_PER_S, tz=UTC).astimezone(CT).time()


def _usd(cents: int | float | Fraction) -> float:
    return float(cents) / 100.0


class PortfolioMember:
    """The schedule-driven member of the v2 portfolio. Its bookkeeping is the one mutable state
    the engine's member contract requires; it never mutates its inputs."""

    def __init__(self, schedule: pd.DataFrame, risk: pd.DataFrame, account: AccountSpec, *,
                 cpi: Sequence[datetime] = ()) -> None:
        ranked = rank_candidates(join_risk(schedule, risk))
        if ranked.duplicated(["root", "decision_ts_ns"]).any():
            raise ValueError("schedule_duplicate_rows: one row per (root, decision_ts_ns)")
        plans = [_Plan(i, r.root, r.cluster, r.horizon, int(r.side), int(r.decision_ts_ns),
                       int(r.exit_ts_ns), float(r.sigma_ticks), float(r.loss_ticks),
                       float(r.cost_ticks), bool(r.release_window))
                 for i, r in enumerate(ranked.itertuples(index=False))]
        by_ts: dict[int, list[_Plan]] = defaultdict(list)
        for p in plans:
            by_ts[p.decision_ts_ns].append(p)
        self.name = MEMBER_NAME
        self.plans = tuple(plans)
        self.plan_by_key = {(p.root, p.decision_ts_ns): p for p in plans}
        self.trading_windows = self._windows(plans)
        self._by_ts = {t: tuple(v) for t, v in by_ts.items()}
        self._cluster = {p.root: p.cluster for p in plans}
        self._account = account
        self._cpi = tuple(cpi)
        self._held: dict[str, _Plan] = {}
        self._issued_ns: dict[str, int] = {}
        self._last_close: dict[str, float] = {}
        self._day: date | None = None
        self._prior_close_usd = 0.0
        self._d_open = account.mll_usd
        self._budget = daily_variance_budget(account.mll_usd)  # D-03, reset per trade date
        self.decisions: list[MemberDecision] = []
        self.intents: list[tuple[int, LegIntent]] = []  # (minute ts_event_ns, intent)

    @staticmethod
    def _windows(plans: Sequence[_Plan]) -> Mapping[str, tuple[TradingInterval, ...]]:
        out = {}
        for root in sorted({p.root for p in plans}):
            mine = [p for p in plans if p.root == root]
            start = min(_ct_time(p.decision_ts_ns) for p in mine)
            end = max(_ct_time(p.exit_ts_ns) for p in mine)
            out[root] = (TradingInterval(start, max(end, start)),)
        return out

    # -- account quantities -------------------------------------------------------------------
    def _unrealized_usd(self, account: MemberAccountView) -> float:
        total = 0.0
        for root, q in account.positions.items():
            avg = account.avg_entry_price.get(root)
            if not q or avg is None or root not in self._last_close:
                continue
            p = product(root)
            total += q * (self._last_close[root] - avg) / float(p.vendor_tick) * float(
                p.tick_value_usd)
        return total

    def _d_now(self, account: MemberAccountView) -> float:
        return (_usd(account.balance_cents) + self._unrealized_usd(account)
                - _usd(account.mll_floor_cents))

    def _roll_day(self, account: MemberAccountView) -> None:
        if account.trade_date == self._day:
            return
        self._day = account.trade_date
        self._prior_close_usd = _usd(account.balance_cents)  # flat at a session's first minute
        self._d_open = self._d_now(account)
        self._budget = daily_variance_budget(self._d_open)

    def _forget_closed(self, account: MemberAccountView, minute_ns: int) -> None:
        for root in list(self._held):
            flat = account.position(root) == 0 and account.pending.get(root, 0) == 0
            if flat and self._issued_ns[root] < minute_ns:
                del self._held[root]
                del self._issued_ns[root]

    def _book(self, account: MemberAccountView, exiting: set[str]) -> tuple[OpenPosition, ...]:
        book = []
        for root, q in account.positions.items():
            exposure = q + account.pending.get(root, 0)
            if exposure and root not in exiting:
                cluster = self._cluster.get(root) or UNIVERSE[root][0]
                held = self._held.get(root)
                book.append(OpenPosition(root, cluster, abs(exposure),
                                         held.exit_ts_ns if held else 0))
        return tuple(book)

    def _cpi_cap(self, root: str, fill_ns: int) -> int | None:
        if not self._cpi:
            return None
        at = datetime.fromtimestamp(fill_ns / NS_PER_S, tz=UTC)
        if check_cpi_opening(root, at, 1, self._cpi) is not None:
            return 0
        if check_cpi_opening(root, at, CPI_MICRO_MAX_50K + 1, self._cpi) is not None:
            return CPI_MICRO_MAX_50K
        return None

    @staticmethod
    def _engine_flattens(view: MinuteView, root: str) -> bool:
        bar = view.bars.get(root)
        if bar is None:
            return True  # no bar: an order would be refused; retry at the next minute
        state = sessions.session_state(root, view.decision_ts_utc)
        return bool(bar.in_flatten_window or state.must_be_flat)

    # -- the member call ----------------------------------------------------------------------
    def _exits(self, view: MinuteView, account: MemberAccountView) -> list[LegIntent]:
        out = []
        for root, plan in self._held.items():
            pos = account.position(root)
            if (pos == 0 or account.pending.get(root, 0) != 0
                    or view.decision_ts_ns < plan.exit_ts_ns or plan.horizon == "hF"
                    or self._engine_flattens(view, root)):
                continue
            intent = leg_market_intent(view, root, "sell" if pos > 0 else "buy", abs(pos))
            if isinstance(intent, LegIntent):
                out.append(intent)
        return out

    def _entries(self, view: MinuteView, account: MemberAccountView, plans: Sequence[_Plan],
                 exiting: set[str]) -> list[LegIntent]:
        ts = view.decision_ts_ns
        if account.status is not Status.ACTIVE:
            self.decisions.extend(MemberDecision(ts, p.row_id, p.root, 0, "account_not_active")
                                  for p in plans)
            return []
        book = self._book(account, exiting)
        d_now = self._d_now(account)
        tier = live_tier_tenths(self._account, self._prior_close_usd)
        out = []
        for p in plans:
            if view.bars.get(p.root) is None:
                self.decisions.append(MemberDecision(ts, p.row_id, p.root, 0, "ks5_no_bar"))
                continue
            adm = admit(root=p.root, cluster=p.cluster, sigma_ticks=p.sigma_ticks,
                        loss_ticks=p.loss_ticks, cost_ticks=p.cost_ticks, d_open=self._d_open,
                        d_now=d_now, book=book, tier_tenths=tier,
                        release_window=p.release_window,  # V23 item 11
                        extra_cap=self._cpi_cap(p.root, ts), budget_var=self._budget)
            if adm.contracts < 1:
                self.decisions.append(MemberDecision(ts, p.row_id, p.root, 0, adm.reason))
                continue
            intent = leg_market_intent(view, p.root, "buy" if p.side > 0 else "sell",
                                       adm.contracts)
            if not isinstance(intent, LegIntent):
                self.decisions.append(MemberDecision(ts, p.row_id, p.root, 0, intent.reason))
                continue
            out.append(intent)
            self._budget -= budget_use(adm.contracts, p.sigma_ticks,
                                       vehicle_facts(p.root).tick_value_usd)
            book = (*book, OpenPosition(p.root, p.cluster, adm.contracts, p.exit_ts_ns))
            self._held[p.root] = p
            self._issued_ns[p.root] = view.ts_event_ns
            self.decisions.append(MemberDecision(ts, p.row_id, p.root, adm.contracts, ""))
        return out

    def on_minute(self, view: MinuteView, account: MemberAccountView) -> Sequence[LegIntent]:
        for root, bar in view.bars.items():
            if bar is not None:
                self._last_close[root] = bar.close
        self._roll_day(account)
        self._forget_closed(account, view.ts_event_ns)
        out = self._exits(view, account)
        plans = self._by_ts.get(view.decision_ts_ns)
        if plans:
            out += self._entries(view, account, plans, {i.root for i in out})
        self.intents.extend((view.ts_event_ns, i) for i in out)
        return out


# --------------------------------------------------------------------------- the run ----
@dataclass(frozen=True)
class PortfolioRun:
    """The engine run of a schedule: the KILL SWITCHES OFF record and its combined-MLL audit
    (module docstring, C-11)."""

    engine_result: EngineResult
    trips: tuple[TripRecord, ...]
    days: tuple[DayRecord, ...]
    daily: pd.Series  # net $ per trade date (every closed date, zeros on no-trade dates)
    decisions: tuple[MemberDecision, ...]
    intents: tuple[tuple[int, LegIntent], ...]
    combined_mll_breaches: tuple[CombinedMllBreach, ...] = ()

    @property
    def breached_combined(self) -> bool:
        """Any combined breach: an MLL breach in every verdict (lead ruling 2026-10-03)."""
        return bool(self.combined_mll_breaches)


# ----------------------------------------------------------------- combined MLL audit ----
@dataclass(frozen=True)
class CombinedMllBreach:
    trade_date: date
    ts_ns: int  # the grid minute (its bars' open, UTC ns) at which the engine marks the MLL
    combined_worst_usd: float  # realized balance + every open leg's adverse-extreme unrealized
    floor_usd: float  # the MLL floor in force
    legs: tuple[tuple[str, int, float], ...]  # (root, signed contracts, adverse unrealized $)
    account_index: int = 0


TIE_CENTS = 1e-6  # float tolerance: a combined worst within this of the floor counts as a touch
NO_TIME = np.iinfo(np.int64).max // 4


def _floors(result: EngineResult) -> tuple[dict[int, Any], dict[int, list]]:
    starts = {e.account_index: e.floor_cents for e in result.events(AccountStart)}
    closes: dict[int, list] = defaultdict(list)
    for e in result.events(DayClose):
        closes[e.account_index].append((e.trade_date, e.floor_after_cents))
    return starts, closes


def _floor_in_force(starts: Mapping, closes: Mapping, account: int, day: date) -> float:
    """Cents: the account's start floor, then the floor trailed at each earlier date's close."""
    floor = starts[account]
    for d, after in closes.get(account, ()):
        if d < day:
            floor = after
    return float(floor)


def _engine_breach_ns(fills: Sequence[Fill], starts: Mapping, closes: Mapping) -> dict[int, int]:
    """Per account, the first minute the engine breached intraday: an MLL liquidation, or a fill
    that left the realized balance at or below the floor (xfa_rules.record_realized_pnl)."""
    out: dict[int, int] = {}
    for f in fills:
        floor = _floor_in_force(starts, closes, f.account_index, f.trade_date)
        if f.reason == "mll_liquidation" or float(f.balance_after_cents) <= floor:
            out.setdefault(f.account_index, f.fill_ts_ns)
    return out


@dataclass(frozen=True)
class _Leg:
    ts: np.ndarray
    low: np.ndarray  # vendor ticks
    high: np.ndarray
    close: np.ndarray
    last_tradable: np.ndarray  # index of the latest non-closure bar at or before each bar (-1)


def _leg_arrays(frame: pd.DataFrame, rules: StageERules, root: str) -> _Leg:
    tick_fixed = rules.legs[root].product.vendor_tick_fixed

    def ticks(col: str) -> np.ndarray:
        fixed = np.rint(frame[col].to_numpy(dtype=float) * PRICE_SCALE).astype(np.int64)
        return fixed // tick_fixed

    tradable = ~frame["in_scheduled_closure"].to_numpy(dtype=bool)
    idx = np.where(tradable, np.arange(len(frame)), -1)
    return _Leg(frame["ts_event"].to_numpy(dtype=np.int64), ticks("low"), ticks("high"),
                ticks("close"), np.maximum.accumulate(idx) if len(idx) else idx)


def _adverse_ticks(leg: _Leg, minutes: np.ndarray, long: bool) -> np.ndarray:
    """The leg's adverse-extreme price (ticks) at each minute, or its last tradable close."""
    i = np.searchsorted(leg.ts, minutes)
    ic = np.minimum(i, len(leg.ts) - 1)
    here = (i < len(leg.ts)) & (leg.ts[ic] == minutes) & (leg.last_tradable[ic] == ic)
    extreme = leg.low[ic] if long else leg.high[ic]
    j = leg.last_tradable[np.maximum(np.searchsorted(leg.ts, minutes, "right") - 1, 0)]
    return np.where(here, extreme, leg.close[np.maximum(j, 0)])


def _apply_keys(fills: Sequence[Fill], grid: np.ndarray) -> np.ndarray:
    """2 x the grid minute whose MLL check already includes each fill, + 1 for an MLL liquidation
    (booked after the check), monotone in ledger order (a session-end or closure-gap close is
    booked at the minute that processes it)."""
    ts = np.asarray([f.fill_ts_ns for f in fills], dtype=np.int64)
    pos = np.searchsorted(grid, ts, "left")
    minute = np.where(pos < len(grid), grid[np.minimum(pos, len(grid) - 1)], NO_TIME)
    liq = np.asarray([f.reason == "mll_liquidation" for f in fills], dtype=np.int64)
    return np.maximum.accumulate(2 * minute + liq)


def combined_mll_audit(result: EngineResult, frames: Mapping[str, pd.DataFrame],
                       rules: StageERules) -> tuple[CombinedMllBreach, ...]:
    """The minutes at which the combined worst equity of two or more open legs was at or below
    the floor while the engine had not breached (module docstring). Reads; changes nothing. It
    audits the kill-switches-off run (C-11), so its breaches are labelled "kill switches off"."""
    fills = list(result.events(Fill))
    if not fills:
        return ()
    roots = sorted({f.root for f in fills})
    grid = np.unique(np.concatenate([frames[r]["ts_event"].to_numpy(dtype=np.int64)
                                     for r in roots]))
    legs = {r: _leg_arrays(frames[r], rules, r) for r in roots}
    starts, closes = _floors(result)
    breach_ns = _engine_breach_ns(fills, starts, closes)
    keys = _apply_keys(fills, grid)
    pos = {r: Position() for r in roots}
    out: list[CombinedMllBreach] = []
    for i, f in enumerate(fills):
        signed = f.qty if f.side == "buy" else -f.qty
        pos[f.root], _ = apply_fill(pos[f.root], signed, rules.price_ticks(f.root, f.price),
                                    rules.tick_value(f.root))
        open_ = {r: p for r, p in pos.items() if p.qty}
        if len(open_) < 2:
            continue
        upper = keys[i + 1] if i + 1 < len(fills) else 2 * NO_TIME
        minutes = grid[(2 * grid >= keys[i]) & (2 * grid < upper)]
        minutes = minutes[minutes < breach_ns.get(f.account_index, NO_TIME)]
        if not len(minutes):
            continue
        floor = _floor_in_force(starts, closes, f.account_index, f.trade_date)
        worst = {r: (p.qty * _adverse_ticks(legs[r], minutes, p.qty > 0) - p.basis_ticks)
                 * float(rules.tick_value(r)) for r, p in open_.items()}
        combined = float(f.balance_after_cents) + sum(worst.values())
        for k in np.flatnonzero(combined <= floor + TIE_CENTS):
            out.append(CombinedMllBreach(
                f.trade_date, int(minutes[k]), float(combined[k]) / 100.0, floor / 100.0,
                tuple((r, open_[r].qty, float(worst[r][k]) / 100.0) for r in sorted(open_)),
                f.account_index))
    return tuple(out)


def _trip_openings(result: EngineResult) -> list[Fill]:
    """The first fill of every flat-to-flat trip, in extract_trips' (closing) order."""
    first: dict[str, Fill] = {}
    out: list[Fill] = []
    for f in result.events(Fill):
        first.setdefault(f.root, f)
        if f.position_after == 0:
            out.append(first.pop(f.root))
    return out


def _worst_adverse_usd(frame: pd.DataFrame, rules: StageERules, trip: TripRecord,
                       entry_price: float, long: bool) -> float | None:
    """Worst adverse gross excursion per contract over the bars [entry fill, exit fill)."""
    ts = frame["ts_event"].to_numpy(dtype=np.int64)
    lo, hi = np.searchsorted(ts, trip.open_ts_ns, "left"), np.searchsorted(ts, trip.close_ts_ns,
                                                                           "left")
    if hi <= lo:
        return None
    root = trip.root
    entry = rules.price_ticks(root, entry_price)
    if long:
        ticks = rules.price_ticks(root, float(frame["low"].to_numpy()[lo:hi].min())) - entry
    else:
        ticks = entry - rules.price_ticks(root, float(frame["high"].to_numpy()[lo:hi].max()))
    return ticks * vehicle_facts(root).tick_value_usd


def trade_records(result: EngineResult, frames: Mapping[str, pd.DataFrame], rules: StageERules,
                  member: PortfolioMember) -> tuple[TradeRecord, ...]:
    """One TradeRecord per trip: P&L and worst excursion per contract in $, the plan's risk."""
    trips = extract_trips(result)
    gross = trip_gross_cents(result, trips)
    openings = _trip_openings(result)
    out = []
    for trip, g, first in zip(trips, gross, openings, strict=True):
        plan = member.plan_by_key.get((trip.root, first.decision_ts_ns))
        if plan is None:
            raise AssertionError(f"trip {trip.root} at {first.decision_ts_ns} has no schedule row")
        n = trip.contracts
        gross_pc = float(Fraction(g)) / 100.0 / n
        net_pc = float(Fraction(trip.net_cents)) / 100.0 / n
        adverse = _worst_adverse_usd(frames[trip.root], rules, trip, first.price,
                                     first.side == "buy")
        adverse = gross_pc if adverse is None else adverse
        worst_pc = min(adverse, gross_pc) - (gross_pc - net_pc)
        facts = vehicle_facts(trip.root)
        vehicle = rules.legs[trip.root].vehicle  # the q_c the engine charged (D-08a)
        out.append(TradeRecord(trip.root, plan.horizon, trip.trade_date, n, net_pc,
                               min(worst_pc, net_pc), plan.sigma_ticks, plan.loss_ticks,
                               plan.cost_ticks, facts.tick_value_usd, facts.lot_equiv,
                               plan.cluster, trip.open_ts_ns, trip.close_ts_ns,
                               int(vehicle.q_c) if vehicle is not None else None,
                               release_window=plan.release_window))
    return tuple(out)


def day_records(result: EngineResult, trades: Sequence[TradeRecord]) -> tuple[DayRecord, ...]:
    """Every closed trade date of the run, its trades in entry order (empty on no-trade dates)."""
    dates = sorted({e.trade_date for e in result.events(DayClose)})
    by_day: dict[date, list[TradeRecord]] = defaultdict(list)
    for t in trades:
        by_day[t.trade_date].append(t)
    return tuple(DayRecord(d, tuple(sorted(by_day.get(d, ()), key=lambda t: (t.entry_ts_ns,
                                                                             t.exit_ts_ns))))
                 for d in dates)


def _daily_net(days: Sequence[DayRecord], trips: Sequence[TripRecord]) -> pd.Series:
    net: dict[date, float] = defaultdict(float)
    for t in trips:
        net[t.trade_date] += t.net_usd
    index = pd.DatetimeIndex([pd.Timestamp(d.trade_date) for d in days], name="trade_date")
    return pd.Series([net.get(d.trade_date, 0.0) for d in days], index=index, dtype="float64",
                     name="net_usd")


def build_rules(roots: Sequence[str], frames: Mapping[str, pd.DataFrame],
                rules_kwargs: Mapping | None) -> PortfolioRules:
    kw = dict(rules_kwargs or {})
    window = kw.pop("window_dates", None)
    if window is None:
        window = {date.fromisoformat(str(d)) for r in roots for d in frames[r]["trade_date"]
                  .unique()}
    releases = kw.pop("releases", None)
    if releases is None:
        releases = load_release_calendar()
    legs = kw.pop("legs", None) or {r: leg_inputs(r, traded=True) for r in roots}
    own = kw.pop("product_blackout", None)
    if own is not None:
        own = {str(r): frozenset(d) for r, d in own.items()}
    return PortfolioRules(legs, frozenset(window), frozenset(kw.pop("blackout", ())), releases,
                          product_blackout=own, **kw)


def run_portfolio(frames: Mapping[str, pd.DataFrame], schedule: pd.DataFrame, risk: pd.DataFrame,
                  *, account: AccountSpec = ACCOUNT_50K, rules_kwargs: Mapping | None = None
                  ) -> PortfolioRun:
    """The schedule through the frozen engine as one multi-product XFA account (50K only: the
    frozen account model encodes 50K; 150K figures come from payout_sim's re-sizing).
    ``rules_kwargs`` may carry ``product_blackout`` (vehicle -> its own roll-blackout dates,
    V2.2); without it the frozen union ``blackout`` applies to every product."""
    if account != ACCOUNT_50K:
        raise ValueError(f"run_portfolio_account: the frozen engine encodes 50K only, not "
                         f"{account.name}")
    roots = sorted(set(schedule["root"]))
    missing = [r for r in roots if r not in frames]
    if missing:
        raise ValueError(f"run_portfolio_missing_frames: {missing}")
    rules = build_rules(roots, frames, rules_kwargs)
    member = PortfolioMember(schedule, risk, account, cpi=rules.releases.cpi)
    legs = tuple(LegSpec(r, True) for r in roots)
    result = run_engine({r: frames[r] for r in roots}, member, legs, rules)
    trips = extract_trips(result)
    days = day_records(result, trade_records(result, frames, rules, member))
    return PortfolioRun(result, trips, days, _daily_net(days, trips), tuple(member.decisions),
                        tuple(member.intents), combined_mll_audit(result, frames, rules))


__all__ = [
    "MEMBER_NAME", "CombinedMllBreach", "MemberDecision", "PortfolioMember", "PortfolioRules",
    "PortfolioRun", "build_rules", "combined_mll_audit", "day_records", "run_portfolio",
    "trade_records", "DayRecord", "TradeRecord",
]
