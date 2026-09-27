"""The generalized Stage E backtest engine (Stage E.2b Task 1, design D9, D11.5, D11.6).

sim/engine.py (the MES engine, D.1f-frozen) is not changed. This module is its generalization to
any Stage E product and to members with several legs, and it runs in one of two rule sets:

- ``MesRules`` (screening/stage_e_mes_rules.py): sim/engine.py's own rules, constant for
  constant (MES tick grid and $1.25 tick, sim/costs.py's slippage table, 61 cents a side,
  rules/xfa_rules.py's 15:10 flatten and 15:08 no-new-positions time, the 20-micro XFA position
  gate, no closure check). It exists so the MES regressions can
  prove that the generalized loop, fills, FIFO accounting, MLL, day close and series reproduce
  D.1 bit for bit (tests/test_stage_e_mes_regression.py).
- ``StageERules``: the Stage E constraint set, every value from frozen files or module constants:
  vendor-unit ticks and tick values (rules/products.py; cent-quoted grains and livestock carry
  factor 100), commission and the D8 slippage table (screening/stage_e_frozen.py), the event-window
  cost (D8, T12-4) and the event-minute fill guard (D9.5a) from a frozen release calendar, the
  flatten rules of rules/sessions.py (R-F1, R-F4; united with the bar's own flatten flags), roll
  blackouts from the group calendar (L-8), the member cap (D9.5, D9.11), the trade-rate floor
  (D9.3: at most 20 entries per product per trade date; no exit less than 2 full minutes after
  the last opening fill; an entry whose forced exit would come sooner is skipped for the day), the
  price-limit proximity rule with its locked-market fill (D9.7, R-08, rules/price_limits.py), and
  the CPI window (D9.12, rules/constraints.py).

The loop, per grid minute (the UTC minute of the bars' opens), in sim/engine.py's order:
1. session change (the traded legs' trade date): strategy orders pending from the old session are
   cancelled, forced orders fill at the first price available, an open position is closed at the
   last bar's close, the day is closed through rules.xfa_rules.close_trading_day, and a terminal
   account restarts;
2. fills at each traded leg's bar open (market), then resting limit orders against its range;
3. the real-time MLL on the adverse extreme;
4. forced flatten (and, Stage E, the D9.7 exit) for the next open;
5. the member's call, then the engine's structural refusals, then the gate.
A member sees only frozen copies (bars with hindsight fields masked, and an account view).

Point in time: every bar reaches the member at its decision time (open + 60 s); an order fills at
the open of a LATER bar of its own leg; the settlement proxy for D9.7 is the PRIOR trade date's
settlement window, complete before the current trade date's first bar; release instants are
scheduled (known in advance).

Money: integer cents where the tick value is a whole number of cents; an exact Fraction of cents
for ZT, ZF, ZN, TN and M6B, whose tick values are 781.25, 781.25, 1562.5, 1562.5 and 62.5 cents
(no rounding is introduced; slippage is ceil to the cent, as in the MES engine).
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from fractions import Fraction
from math import ceil, floor
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from rules import xfa_rules as xr
from rules.xfa_rules import AccountState, OrderIntent, Refusal, Status
from sim.fill_model import passive_fill_ticks
from strategy.interface import (
    HINDSIGHT_FIELDS,
    NS_PER_BAR,
    NS_PER_S,
    Bar,
)
from strategy.stage_e.interface import LegSpec

NS_PER_MINUTE = 60 * NS_PER_S
MIN_HOLD_NS = 2 * NS_PER_MINUTE  # D9.3(b)
MAX_ENTRIES_PER_DAY = 20  # D9.3(a)
EVENT_WINDOW_NS = 30 * NS_PER_MINUTE  # D8: [release, release + 30 min)
FILL_GUARD_NS = 2 * NS_PER_MINUTE  # D9.5a: [release, release + 2 min)


class EngineInvariantError(RuntimeError):
    """A structural guarantee failed. Never caught inside the engine."""


class EngineRefusedCase(RuntimeError):
    """A case the frozen rules cannot resolve without a new choice; refused by name."""


def _utc(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / NS_PER_S, tz=UTC)


# ------------------------------------------------------------------ positions ----
@dataclass(frozen=True, slots=True)
class Lot:
    qty: int
    price_ticks: int


@dataclass(frozen=True, slots=True)
class Position:
    lots: tuple[Lot, ...] = ()

    @property
    def qty(self) -> int:
        return sum(lot.qty for lot in self.lots)

    @property
    def basis_ticks(self) -> int:
        return sum(lot.qty * lot.price_ticks for lot in self.lots)


def apply_fill(position: Position, signed_qty: int, price_ticks: int, tick_value: int | Fraction
               ) -> tuple[Position, int | Fraction]:
    """FIFO (sim.engine.apply_fill with the leg's tick value)."""
    lots = list(position.lots)
    remaining = signed_qty
    realized: int | Fraction = 0
    while remaining and lots and (lots[0].qty > 0) != (remaining > 0):
        head = lots[0]
        closing = min(abs(remaining), abs(head.qty))
        direction = 1 if head.qty > 0 else -1
        realized += direction * closing * (price_ticks - head.price_ticks) * tick_value
        left = head.qty - direction * closing
        lots = ([Lot(left, head.price_ticks)] if left else []) + lots[1:]
        remaining += direction * closing
    if remaining:
        lots.append(Lot(remaining, price_ticks))
    return Position(tuple(lots)), realized


# --------------------------------------------------------------------- ledger ----
@dataclass(frozen=True, slots=True)
class IntentRecord:
    decision_ts_ns: int
    account_index: int
    root: str | None
    received: str
    accepted: bool
    refusal: Refusal | None
    position_before: int
    pending_before: int
    limit_price: float | None = None


@dataclass(frozen=True, slots=True)
class Fill:
    root: str
    fill_ts_ns: int  # the fill bar's OPEN (a close fill: that bar's decision time)
    decision_ts_ns: int
    account_index: int
    reason: str  # strategy | forced_flatten | price_limit_exit | mll_liquidation | ... end
    side: str
    qty: int
    price: float
    commission_cents: int
    slippage_cents: int
    slippage_ticks: float
    gross_realized_cents: int | Fraction
    position_after: int
    balance_after_cents: int | Fraction
    minutes_after_decision: int
    order_type: str = "market"
    trade_date: date | None = None  # the trade date the fill is billed to
    event_window: bool = False
    opening: bool = False
    locked_bars_waited: int = 0
    closure_gap: bool = False  # OC-T: filled at the last tradable close before a closure bar


@dataclass(frozen=True, slots=True)
class Cancel:
    ts_ns: int
    decision_ts_ns: int
    account_index: int
    root: str
    reason: str
    side: str
    qty: int


@dataclass(frozen=True, slots=True)
class DayClose:
    trade_date: date
    account_index: int
    status_before: str
    status_after: str
    balance_cents: int | Fraction
    day_net_cents: int | Fraction
    floor_after_cents: int | Fraction
    strategy_fills: int
    breach: Refusal | None


@dataclass(frozen=True, slots=True)
class AccountStart:
    ts_ns: int
    trade_date: date
    account_index: int
    balance_cents: int
    floor_cents: int


@dataclass(frozen=True)
class EngineResult:
    ledger: tuple[Any, ...]
    final_state: AccountState
    bars_processed: int
    minutes_processed: int
    accounts_started: int
    counters: Mapping[str, int]  # refusals, deferrals, skips by name

    def events(self, kind: type) -> tuple:
        return tuple(e for e in self.ledger if isinstance(e, kind))


@dataclass(frozen=True, slots=True)
class _Order:
    root: str
    decision_ts_ns: int
    signed_qty: int
    reason: str  # strategy | forced_flatten | price_limit_exit
    limit_ticks: int | None = None
    expires_ts_ns: int | None = None
    locked_waits: int = 0

    @property
    def is_passive(self) -> bool:
        return self.limit_ticks is not None


@dataclass(frozen=True)
class _Normalized:
    """A member's item after construction checks: what it asks, on which leg."""

    root: str
    signed_qty: int
    ts_utc: datetime
    limit_price: float | None
    ttl_bars: int | None
    intent: OrderIntent | None  # the MES OrderIntent, for the MES gate and ledger


# ------------------------------------------------------------------ bar feeds ----
def iter_minutes(frames: Mapping[str, pd.DataFrame], make_bar: Mapping[str, Any]
                 ) -> Iterator[tuple[int, dict[str, Bar]]]:
    """The shared UTC minute grid (D11.5): every minute at which any leg has a bar, ascending,
    with the legs that have a bar there. Nothing is forward filled: a leg without a bar at a
    minute is simply absent from that minute's mapping."""
    arrays = {r: f["ts_event"].to_numpy(dtype="int64") for r, f in frames.items()}
    for r, arr in arrays.items():
        if len(arr) > 1 and not bool(np.all(arr[1:] > arr[:-1])):
            raise EngineInvariantError(f"{r}: bars are not strictly increasing in time")
    if not arrays or not any(len(a) for a in arrays.values()):
        return
    grid = np.unique(np.concatenate(list(arrays.values())))
    cursor = {r: 0 for r in frames}
    feeds = {r: make_bar[r](frames[r]) for r in frames}
    for ts in grid.tolist():
        out: dict[str, Bar] = {}
        for r, arr in arrays.items():
            i = cursor[r]
            if i < len(arr) and int(arr[i]) == ts:
                bar = next(feeds[r])
                if bar.ts_event_ns != ts:
                    raise EngineInvariantError(f"{r}: feed out of step at {ts}")
                out[r] = bar
                cursor[r] = i + 1
        yield int(ts), out


# ------------------------------------------------------------------ the run ----
class _Run:
    """Mutable loop bookkeeping for one run; every object it emits is frozen."""

    def __init__(self, member: Any, legs: Sequence[LegSpec], rules: Any) -> None:
        self.member, self.rules = member, rules
        self.legs = tuple(legs)
        self.traded = tuple(leg.root for leg in legs if leg.traded)
        self.read = tuple(leg.root for leg in legs)
        self.ledger: list[Any] = []
        self.account_index = 0
        self.state = rules.new_account()
        self.last_close_balance: int | Fraction = self.state.balance_cents
        self.position = {r: Position() for r in self.traded}
        self.pending: tuple[_Order, ...] = ()
        self.trade_date: date | None = None
        self.strategy_fills_today = 0
        self.last_ts = -1
        self.last_instrument: dict[str, int | None] = {r: None for r in self.read}
        self.last_bar: dict[str, Bar | None] = {r: None for r in self.read}
        self.previous_bar: dict[str, Bar | None] = {r: None for r in self.read}
        self.bars = 0
        self.minutes = 0
        self.counters: dict[str, int] = {}
        # D9.3 bookkeeping (Stage E rules read these; MES rules ignore them)
        self.entries_today: dict[str, int] = {r: 0 for r in self.traded}
        self.last_open_fill_ns: dict[str, int | None] = {r: None for r in self.traded}
        self.skipped_today: set[str] = set()
        # OC-T: the last bar of each leg that is not a scheduled-closure print
        self.last_tradable: dict[str, Bar | None] = {r: None for r in self.read}

    # -- helpers ----------------------------------------------------------
    def count(self, name: str) -> None:
        self.counters[name] = self.counters.get(name, 0) + 1

    def pending_signed(self, root: str) -> int:
        return sum(o.signed_qty for o in self.pending if o.root == root)

    def exposure(self, root: str) -> int:
        return self.position[root].qty + self.pending_signed(root)

    # -- fills ------------------------------------------------------------
    def fill(self, order: _Order, bar: Bar, price_ticks: int, reason: str) -> None:
        if bar.ts_event_ns < order.decision_ts_ns:
            raise EngineInvariantError(
                f"fill bar opens at {bar.ts_event_ns} before the decision {order.decision_ts_ns}")
        root = order.root
        qty = abs(order.signed_qty)
        side = "buy" if order.signed_qty > 0 else "sell"
        before = self.position[root].qty
        opening = not xr.is_reducing(before, order.signed_qty)
        cost, event = self.rules.fill_cost(self, order, bar, qty, side, reason)
        tv = self.rules.tick_value(root)
        self.position[root], gross = apply_fill(self.position[root], order.signed_qty,
                                                price_ticks, tv)
        self.state = xr.record_realized_pnl(self.state, gross - cost.total_cents)
        if reason == "strategy":
            self.strategy_fills_today += 1
        if opening:
            self.entries_today[root] = self.entries_today.get(root, 0) + (reason == "strategy")
            self.last_open_fill_ns[root] = bar.ts_event_ns
        self.ledger.append(Fill(
            root=root, fill_ts_ns=bar.ts_event_ns, decision_ts_ns=order.decision_ts_ns,
            account_index=self.account_index, reason=reason, side=side, qty=qty,
            price=self.rules.ticks_price(root, price_ticks), commission_cents=cost.commission_cents,
            slippage_cents=cost.slippage_cents, slippage_ticks=cost.slippage_ticks_per_micro,
            gross_realized_cents=gross, position_after=self.position[root].qty,
            balance_after_cents=self.state.balance_cents,
            minutes_after_decision=(bar.ts_event_ns - order.decision_ts_ns) // NS_PER_MINUTE,
            order_type="passive" if order.is_passive else "market", trade_date=bar.trade_date,
            event_window=event, opening=opening and reason == "strategy",
            locked_bars_waited=order.locked_waits))

    def fill_at_close(self, order: _Order, bar: Bar, closure_gap: bool = False) -> None:
        """Close at a bar's CLOSE (end of data, a session that ended with a position open, or,
        ``closure_gap``, an exit whose leg's next bar is a scheduled-closure print: OC-T)."""
        root = order.root
        if closure_gap and order.reason == "strategy":
            self.strategy_fills_today += 1
        qty = abs(order.signed_qty)
        side = "buy" if order.signed_qty > 0 else "sell"
        cost, event = self.rules.close_cost(self, root, bar, qty, side)
        tv = self.rules.tick_value(root)
        self.position[root], gross = apply_fill(self.position[root], order.signed_qty,
                                                self.rules.price_ticks(root, bar.close), tv)
        self.state = xr.record_realized_pnl(self.state, gross - cost.total_cents)
        self.ledger.append(Fill(
            root, bar.decision_ts_ns, order.decision_ts_ns, self.account_index, order.reason, side,
            qty, bar.close, cost.commission_cents, cost.slippage_cents,
            cost.slippage_ticks_per_micro, gross, self.position[root].qty,
            self.state.balance_cents, 1, trade_date=bar.trade_date, event_window=event,
            closure_gap=closure_gap))

    def cancel_pending(self, ts_ns: int, reason: str, keep_forced: bool,
                       root: str | None = None) -> None:
        kept = []
        for order in self.pending:
            if (root is not None and order.root != root) or (
                    keep_forced and order.reason != "strategy"):
                kept.append(order)
                continue
            self.ledger.append(Cancel(ts_ns, order.decision_ts_ns, self.account_index, order.root,
                                      reason, "buy" if order.signed_qty > 0 else "sell",
                                      abs(order.signed_qty)))
        self.pending = tuple(kept)

    def _cancel(self, order: _Order, bar_ts: int, reason: str) -> None:
        self.count(reason)
        self.ledger.append(Cancel(bar_ts, order.decision_ts_ns, self.account_index, order.root,
                                  reason, "buy" if order.signed_qty > 0 else "sell",
                                  abs(order.signed_qty)))

    # -- phases -----------------------------------------------------------
    def start_account(self, bar: Bar) -> None:
        self.ledger.append(AccountStart(bar.ts_event_ns, bar.trade_date, self.account_index,
                                        self.state.balance_cents, self.state.mll_floor_cents))

    def roll_session(self, bars: Mapping[str, Bar]) -> None:
        traded_bars = [bars[r] for r in self.traded if r in bars]
        if not traded_bars:
            return
        days = {b.trade_date for b in traded_bars}
        if len(days) != 1:
            raise EngineInvariantError(f"traded legs disagree on the trade date: {sorted(days)}")
        day = days.pop()
        first = traded_bars[0]
        if self.trade_date is None:
            self.trade_date = day
            self.start_account(first)
            return
        if day == self.trade_date:
            return
        if day < self.trade_date:
            raise EngineInvariantError(f"trade date went backwards at {first.ts_event_ns}")
        self.rules.before_session_change(self)
        self.cancel_pending(first.ts_event_ns, "session_changed_before_fill", keep_forced=True)
        for order in self.pending:  # forced closes: the first price available
            bar = bars.get(order.root)
            if bar is not None and not self.is_closure(bar):
                self.fill(order, bar, self.rules.price_ticks(order.root, bar.open), order.reason)
            else:
                prev = self.session_end_bar(order.root)
                if prev is None:
                    raise EngineInvariantError(f"{order.root}: forced order with no bar")
                self.fill_at_close(replace(order, reason=f"{order.reason}_session_end"), prev)
        self.pending = ()
        for root in self.traded:
            if self.position[root].qty:
                prev = self.session_end_bar(root)
                if prev is None:
                    raise EngineInvariantError(f"{root}: position with no bar")
                self.fill_at_close(_Order(root, prev.ts_event_ns, -self.position[root].qty,
                                          "forced_flatten_session_end"), prev)
        self.close_day()
        self.trade_date = day
        self.entries_today = {r: 0 for r in self.traded}
        self.skipped_today = set()
        if self.state.status is not Status.ACTIVE and self.rules.restart_on_terminal:
            if any(p.qty for p in self.position.values()):
                raise EngineInvariantError("terminal account still holds a position")
            self.account_index += 1
            self.state = self.rules.new_account()
            self.last_close_balance = self.state.balance_cents
            self.start_account(first)

    def is_closure(self, bar: Bar) -> bool:
        """A scheduled-closure print the rules never trade (OC-T). MesRules skips none, as
        sim/engine.py does not."""
        return self.rules.skip_closure_bars and bar.in_scheduled_closure

    def session_end_bar(self, root: str) -> Bar | None:
        """The bar a session-end close uses: the last bar before the current minute, or, where
        closure prints are never traded, the last tradable bar before it (OC-T)."""
        if self.rules.skip_closure_bars:
            return self.last_tradable[root]
        return self.last_bar_before(root)

    def close_on_closure_bar(self, root: str, bar: Bar) -> None:
        """OC-T (C-1): no fill, MLL mark or forced order ever uses a closure print. A pending
        member exit or forced order, and any position still open, fills at the close of the leg's
        last tradable bar before the print (the session-end convention), flagged and counted;
        a pending opening order or resting limit order is cancelled."""
        orders = tuple(o for o in self.pending if o.root == root)
        if not orders and not self.position[root].qty:
            return
        self.rules.before_session_change(self)  # a locked exit never closes at a prior close
        self.pending = tuple(o for o in self.pending if o.root != root)
        prev = self.last_tradable[root]
        for order in orders:
            pos = self.position[root].qty
            closes = not order.is_passive and pos != 0 and xr.is_reducing(pos, order.signed_qty)
            if not closes:
                self._cancel(order, bar.ts_event_ns, "closure_bar_no_fill")
                continue
            self._fill_prior_close(order, prev)
        if self.position[root].qty:
            anchor = prev.ts_event_ns if prev is not None else bar.ts_event_ns
            self._fill_prior_close(_Order(root, anchor, -self.position[root].qty,
                                          "forced_flatten"), prev)

    def _fill_prior_close(self, order: _Order, prev: Bar | None) -> None:
        if prev is None:
            raise EngineInvariantError(f"{order.root}: an exit at a closure print with no "
                                       "tradable bar before it")
        self.count("fill_at_prior_close_closure_gap")
        self.fill_at_close(order, prev, closure_gap=True)

    def last_bar_before(self, root: str) -> Bar | None:
        """The leg's bar before the current minute (the session that is ending)."""
        return self.previous_bar[root] if self.current_has_bar(root) else self.last_bar[root]

    def current_has_bar(self, root: str) -> bool:
        bar = self.last_bar[root]
        return bar is not None and bar.ts_event_ns == self.last_ts

    def close_day(self) -> None:
        assert self.trade_date is not None
        before = self.state
        after = xr.close_trading_day(before, self.trade_date, self.strategy_fills_today)
        day_net = before.balance_cents - self.last_close_balance
        self.ledger.append(DayClose(
            self.trade_date, self.account_index, before.status.value, after.status.value,
            after.balance_cents, day_net, after.mll_floor_cents, self.strategy_fills_today,
            after.breach if after.breach is not before.breach else None))
        self.state = after
        self.last_close_balance = after.balance_cents
        self.strategy_fills_today = 0

    def fill_pending_at_open(self, root: str, bar: Bar) -> None:
        orders = tuple(o for o in self.pending if o.root == root)
        others = tuple(o for o in self.pending if o.root != root)
        self.pending = others
        resting: list[_Order] = []
        deferred: list[_Order] = []
        for order in orders:
            if order.reason == "strategy" and self.state.status is not Status.ACTIVE:
                self._cancel(order, bar.ts_event_ns, "account_not_active")
                continue
            if order.is_passive:
                resting.append(order)
                continue
            verdict = self.rules.admit_fill(self, order, bar)
            if verdict == "fill":
                self.fill(order, bar, self.rules.price_ticks(root, bar.open), order.reason)
            elif verdict == "defer":
                deferred.append(order)
            elif verdict == "defer_locked":
                deferred.append(replace(order, locked_waits=order.locked_waits + 1))
            else:
                self._cancel(order, bar.ts_event_ns, verdict)
        kept = tuple(o for o in resting if self.try_passive(o, bar))
        self.pending = (*self.pending, *deferred, *kept)

    def try_passive(self, order: _Order, bar: Bar) -> bool:
        assert order.limit_ticks is not None and order.expires_ts_ns is not None
        if bar.ts_event_ns >= order.expires_ts_ns:
            self._cancel(order, bar.ts_event_ns, "passive_expired")
            return False
        adds = not xr.is_reducing(self.position[order.root].qty, order.signed_qty)
        if adds and self.rules.passive_no_new(self, order.root, bar):
            self._cancel(order, bar.ts_event_ns, "passive_no_new_positions_window")
            return False
        root = order.root
        price = passive_fill_ticks(order.signed_qty, order.limit_ticks,
                                   self.rules.price_ticks(root, bar.low),
                                   self.rules.price_ticks(root, bar.high))
        if price is None:
            return True
        verdict = self.rules.admit_fill(self, order, bar)
        if verdict in ("defer", "defer_locked"):
            return True
        if verdict != "fill":
            self._cancel(order, bar.ts_event_ns, verdict)
            return False
        self.fill(order, bar, price, order.reason)
        return False

    def check_mll(self, root: str, bar: Bar) -> None:
        q = self.position[root].qty
        if q == 0:
            return
        tv = self.rules.tick_value(root)
        if self.state.status is Status.BREACHED:
            self.fill(_Order(root, bar.ts_event_ns, -q, "mll_liquidation"), bar,
                      self.rules.price_ticks(root, bar.open), "mll_liquidation")
            return
        if self.state.status is not Status.ACTIVE:
            return
        worst_price = bar.low if q > 0 else bar.high
        pos = self.position[root]
        worst = (pos.qty * self.rules.price_ticks(root, worst_price) - pos.basis_ticks) * tv
        checked = xr.apply_realtime_mll(self.state, worst)
        if checked.status is not Status.BREACHED:
            return
        bound = Fraction(self.state.mll_floor_cents - self.state.balance_cents
                         + pos.basis_ticks * tv, q * tv)
        touch = floor(bound) if q > 0 else ceil(bound)
        open_ticks = self.rules.price_ticks(root, bar.open)
        liquidation = min(open_ticks, touch) if q > 0 else max(open_ticks, touch)
        self.state = checked
        self.count("mll_liquidation")
        self.fill(_Order(root, bar.ts_event_ns, -q, "mll_liquidation"), bar, liquidation,
                  "mll_liquidation")

    def queue_forced(self, root: str, bar: Bar) -> None:
        for reason in self.rules.forced_reasons(self, root, bar):
            exposure = self.exposure(root)
            if not exposure:
                return
            self.cancel_pending(bar.decision_ts_ns, "superseded_by_forced_flatten",
                                keep_forced=True, root=root)
            residual = self.exposure(root)
            if residual:
                self.count(reason)
                self.pending = (*self.pending, _Order(root, bar.decision_ts_ns, -residual,
                                                      reason))
            return

    def visible(self, bar: Bar | None) -> Bar | None:
        if bar is None or not self.rules.mask_hindsight_fields:
            return bar
        return replace(bar, **{name: False for name in HINDSIGHT_FIELDS})

    def ask_member(self, ts: int, bars: Mapping[str, Bar]) -> None:
        items = self.rules.call_member(self, ts, bars)
        for item in items:
            norm, refusal = self.rules.normalize(self, item, ts, bars)
            root = norm.root if norm is not None else None
            pos_before = self.position[root].qty if root in self.position else 0
            pending_before = self.pending_signed(root) if root in self.position else 0
            if refusal is None and norm is not None:
                refusal = self.rules.structural_refusal(self, norm, ts, bars)
            if refusal is None and norm is not None:
                refusal = self.rules.gate(self, norm, ts, bars)
            accepted = refusal is None and norm is not None
            if refusal is not None:
                self.count(refusal.reason)
            self.ledger.append(IntentRecord(
                ts + NS_PER_BAR, self.account_index, root,
                self.rules.received_repr(item, norm), accepted, refusal, pos_before,
                pending_before, None if norm is None else norm.limit_price))
            if not accepted:
                continue
            assert norm is not None
            if norm.limit_price is None:
                order = _Order(norm.root, ts + NS_PER_BAR, norm.signed_qty, "strategy")
            else:
                order = _Order(norm.root, ts + NS_PER_BAR, norm.signed_qty, "strategy",
                               self.rules.price_ticks(norm.root, norm.limit_price),
                               ts + NS_PER_BAR + int(norm.ttl_bars or 0) * NS_PER_MINUTE)
            self.pending = (*self.pending, order)

    def step(self, ts: int, bars: Mapping[str, Bar]) -> None:
        if ts <= self.last_ts:
            raise EngineInvariantError(f"minute {ts} is not after {self.last_ts}")
        for root, bar in bars.items():
            if not isinstance(bar, Bar):
                raise EngineInvariantError(f"feed yielded {type(bar).__name__}, not Bar")
            last = self.last_instrument[root]
            if (root in self.position and last is not None and bar.instrument_id != last
                    and self.exposure(root)):
                raise EngineInvariantError(
                    f"{root}: instrument changed {last} -> {bar.instrument_id} with exposure "
                    f"{self.exposure(root)}: a position would span a contract splice")
        for root, bar in bars.items():
            self.previous_bar[root] = self.last_bar[root]
            self.last_instrument[root] = bar.instrument_id
            self.last_bar[root] = bar
            self.bars += 1
            if bar.in_scheduled_closure:
                self.count(f"closure_bars_seen:{root}")  # OC-T (C-3)
        self.last_ts = ts
        self.minutes += 1
        self.rules.observe(self, ts, bars)
        self.roll_session(bars)
        tradable = {r: b for r, b in bars.items() if not self.is_closure(b)}
        for root in self.traded:
            if root in tradable:
                self.fill_pending_at_open(root, bars[root])
            elif root in bars:
                self.close_on_closure_bar(root, bars[root])
        for root in self.traded:
            if root in tradable:
                self.check_mll(root, bars[root])
        for root in self.traded:
            if root in tradable:
                self.queue_forced(root, bars[root])
        self.ask_member(ts, bars)
        for root, bar in bars.items():
            if not bar.in_scheduled_closure:
                self.last_tradable[root] = bar

    def finish(self) -> EngineResult:
        if self.trade_date is not None:
            self.cancel_pending(self.last_ts + NS_PER_BAR, "end_of_data", keep_forced=False)
            for root in self.traded:
                if self.position[root].qty:
                    bar = (self.last_tradable[root] if self.rules.skip_closure_bars
                           else self.last_bar[root])
                    assert bar is not None
                    self.fill_at_close(_Order(root, bar.ts_event_ns, -self.position[root].qty,
                                              "end_of_data"), bar)
            self.close_day()
        return EngineResult(tuple(self.ledger), self.state, self.bars, self.minutes,
                            self.account_index + 1, MappingProxyType(dict(self.counters)))


def run_engine(frames: Mapping[str, pd.DataFrame], member: Any, legs: Sequence[LegSpec],
               rules: Any) -> EngineResult:
    """Replay the legs' frames on the shared minute grid through ``member`` under ``rules``."""
    missing = [leg.root for leg in legs if leg.root not in frames]
    if missing:
        raise ValueError(f"no frame for legs {missing}")
    if not any(leg.traded for leg in legs):
        raise ValueError("a member needs at least one traded leg")
    run = _Run(member, legs, rules)
    feeds = {leg.root: rules.bar_iterator(leg.root) for leg in legs}
    for ts, bars in iter_minutes({leg.root: frames[leg.root] for leg in legs}, feeds):
        run.step(ts, bars)
    return run.finish()


__all__ = [
    "EVENT_WINDOW_NS", "FILL_GUARD_NS", "MAX_ENTRIES_PER_DAY", "MIN_HOLD_NS", "AccountStart",
    "Cancel", "DayClose", "EngineInvariantError", "EngineRefusedCase", "EngineResult", "Fill",
    "IntentRecord", "Lot", "Position", "apply_fill", "iter_minutes", "run_engine",
]
