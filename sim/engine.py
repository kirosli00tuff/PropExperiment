"""Event-driven MES backtest engine (Stage C, Tasks 2-3).

Grown from the ETA-probe loop (kept verbatim in ``sim/eta_probe.py``): strict
chronological replay, one strategy call per completed bar, and now the rules
gate, the fill model and a complete ledger.

READ ``sim/fill_model.py`` BEFORE QUOTING A NUMBER. Costs come from a two-day
book calibration that excludes latency, adverse selection and queue position.
A backtest P&L from this engine is an optimistic bound, not a realistic estimate.

Point-in-time contract (``strategy/interface.py``), enforced structurally here:
- Bars come from a one-way iterator. At ``strategy.on_bar(bar N)`` the engine has
  pulled bars 0..N and nothing else. There is no look-ahead buffer, and no index
  into a frame is ever handed out.
- An intent must be stamped with bar N's decision time (close = open + 60 s).
  It fills at the OPEN of a LATER bar, never at a price the strategy saw. The
  fill routine refuses any fill whose bar opens before the order's decision time.
- A strategy sees frozen copies only: the ``Bar`` and an ``AccountView``.

Per bar, in this order:
1. Session change: if the bar starts a new trade date, strategy orders still
   pending from the old session are cancelled, the old day is closed through
   ``close_trading_day``, and a terminal account is restarted if configured.
2. Fills: pending orders fill at this bar's open, booking commission + slippage
   at the fill time bucket and size.
3. Real-time MLL: an open position is marked at the bar's adverse extreme. On a
   breach it is liquidated at the tick where equity touched the floor (or at the
   open, if the bar gapped through it), and the account is breached.
4. Forced flatten: a position still open at a decision time inside the Topstep
   flatten window gets a forced close for the next bar's open. There is no
   override.
5. Strategy call, then structural refusals, then the rules gate, in the fixed
   ``ENGINE_REFUSAL_ORDER`` + ``rules.xfa_rules.GATE_REFUSAL_ORDER``. Intents
   decided in a scheduled closure, in the flatten window, or in a roll-blackout
   session are refused by the ENGINE before the gate ever sees them.

Roll blackout: MES.v.0 splices about two sessions after volume moves (Stage A.1
``roll_volume_context``: the expiring contract trades at 20-40% of normal
volume on those sessions). New exposure is refused on the splice trade date and
the ``roll_blackout_sessions_before`` (default 2) preceding trade dates. Those
dates come from the vendor roll schedule and the exchange calendar, known in
advance, never from the bars. A position can therefore never span a splice; if
one ever did, the engine raises.

``vendor_degraded_day`` is hindsight and is never used to gate trading.

Position accounting uses FIFO lots in integer ticks, so every P&L figure is an
exact integer number of cents.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from datetime import date, datetime, time, timedelta
from enum import Enum
from fractions import Fraction
from math import ceil, floor
from pathlib import Path
from typing import Any

import pandas as pd

from data.cme_calendar import HOLIDAYS, HolidayKind
from rules import xfa_rules as xr
from rules.xfa_rules import AccountState, OrderIntent, Phase, Refusal, Status
from sim.costs import SlippageTable
from sim.fill_model import MES_TICK_VALUE_CENTS, side_cost
from strategy.interface import (
    HINDSIGHT_FIELDS,
    AccountView,
    Bar,
    Strategy,
    construct_bar,
)

ENGINE_REFUSAL_ORDER = (
    "engine_not_an_intent",
    "strategy_construction_refusal",
    "engine_malformed_intent",
    "engine_intent_timestamp_mismatch",
    "engine_scheduled_closure",
    "engine_flatten_window",
    "engine_roll_blackout",
)
BAR_COLUMNS = (
    "ts_event", "open", "high", "low", "close", "volume", "instrument_id", "raw_symbol",
    "trade_date", "in_flatten_window", "in_no_new_positions_window", "early_halt_ct",
    "in_scheduled_closure", "is_roll_session", "gap_before_minutes", "vendor_degraded_day",
)


class EngineInvariantError(RuntimeError):
    """A structural guarantee failed. Never caught inside the engine."""


# ------------------------------------------------------------------ bar feed ----
def iter_bars(frame: pd.DataFrame) -> Iterator[Bar]:
    """Rows -> ``Bar`` through ``construct_bar``; a refused row is a data defect and raises."""
    missing = [c for c in BAR_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"bar frame missing columns {missing}")
    cols = {c: frame[c].to_numpy() for c in BAR_COLUMNS}
    for i in range(len(frame)):
        halt = str(cols["early_halt_ct"][i])
        built = construct_bar(
            ts_event_ns=int(cols["ts_event"][i]),
            open=float(cols["open"][i]), high=float(cols["high"][i]),
            low=float(cols["low"][i]), close=float(cols["close"][i]),
            volume=int(cols["volume"][i]), instrument_id=int(cols["instrument_id"][i]),
            raw_symbol=str(cols["raw_symbol"][i]),
            trade_date=date.fromisoformat(str(cols["trade_date"][i])),
            in_flatten_window=bool(cols["in_flatten_window"][i]),
            in_no_new_positions_window=bool(cols["in_no_new_positions_window"][i]),
            early_halt_ct=time.fromisoformat(halt) if halt else None,
            in_scheduled_closure=bool(cols["in_scheduled_closure"][i]),
            is_roll_session=bool(cols["is_roll_session"][i]),
            gap_before_minutes=int(cols["gap_before_minutes"][i]),
            vendor_degraded_day=bool(cols["vendor_degraded_day"][i]),
        )
        if isinstance(built, Refusal):
            raise EngineInvariantError(f"row {i}: {built.reason}: {built.arithmetic}")
        yield built


# -------------------------------------------------------------- roll blackout ----
def _is_trade_date(day: date) -> bool:
    holiday = HOLIDAYS.get(day)
    return day.weekday() < 5 and not (holiday and holiday.kind is HolidayKind.FULL_CLOSURE)


def roll_blackout_dates(
    splice_trade_dates: Iterable[date], sessions_before: int
) -> frozenset[date]:
    """Splice trade dates plus the ``sessions_before`` exchange trade dates before each."""
    out: set[date] = set()
    for splice in splice_trade_dates:
        out.add(splice)
        day, found = splice, 0
        while found < sessions_before:
            day -= timedelta(days=1)
            if _is_trade_date(day):
                out.add(day)
                found += 1
    return frozenset(out)


def splice_trade_dates_from_parquet(path: Path) -> tuple[date, ...]:
    """Roll splices from the parquet's schema metadata (vendor symbology); reads no rows."""
    import pyarrow.parquet as pq

    from data.session import trade_date

    meta = json.loads(pq.read_schema(path).metadata[b"propexperiment"])
    return tuple(sorted({trade_date(int(r["ts_ns"])) for r in meta["rolls"]}))


# --------------------------------------------------------------- positions ----
@dataclass(frozen=True, slots=True)
class Lot:
    qty: int  # signed micros, never 0
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

    @property
    def avg_entry_price(self) -> float | None:
        q = self.qty
        return None if q == 0 else self.basis_ticks / q * xr.MES_TICK_SIZE

    def unrealized_cents(self, mark_ticks: int) -> int:
        return (self.qty * mark_ticks - self.basis_ticks) * MES_TICK_VALUE_CENTS


def apply_fill(position: Position, signed_qty: int, price_ticks: int) -> tuple[Position, int]:
    """FIFO: close opposite lots first, open the remainder. Returns (new position, gross
    realized cents on the closed part)."""
    lots = list(position.lots)
    remaining = signed_qty
    realized = 0
    while remaining and lots and (lots[0].qty > 0) != (remaining > 0):
        head = lots[0]
        closing = min(abs(remaining), abs(head.qty))
        direction = 1 if head.qty > 0 else -1
        realized += direction * closing * (price_ticks - head.price_ticks) * MES_TICK_VALUE_CENTS
        left = head.qty - direction * closing
        lots = ([Lot(left, head.price_ticks)] if left else []) + lots[1:]
        remaining += direction * closing
    if remaining:
        lots.append(Lot(remaining, price_ticks))
    return Position(tuple(lots)), realized


# ------------------------------------------------------------------ ledger ----
@dataclass(frozen=True, slots=True)
class IntentEvent:
    decision_ts_ns: int
    account_index: int
    intent: OrderIntent | None
    received: str  # repr of what the strategy returned
    accepted: bool
    refusal: Refusal | None
    position_before: int
    pending_before: int


@dataclass(frozen=True, slots=True)
class FillEvent:
    fill_ts_ns: int  # the fill bar's OPEN
    decision_ts_ns: int
    account_index: int
    reason: str  # "strategy" | "forced_flatten" | "mll_liquidation" | "end_of_data"
    side: str
    qty: int
    price: float
    commission_cents: int
    slippage_cents: int
    slippage_ticks_per_micro: float
    gross_realized_cents: int
    position_after: int
    balance_after_cents: int
    minutes_after_decision: int


@dataclass(frozen=True, slots=True)
class CancelEvent:
    ts_ns: int
    decision_ts_ns: int
    account_index: int
    reason: str
    side: str
    qty: int


@dataclass(frozen=True, slots=True)
class MllCheckEvent:
    bar_ts_ns: int
    account_index: int
    position: int
    worst_mark_price: float
    worst_unrealized_cents: int
    balance_cents: int
    floor_cents: int
    breached: bool


@dataclass(frozen=True, slots=True)
class ForcedFlattenEvent:
    decision_ts_ns: int
    account_index: int
    side: str
    qty: int
    arithmetic: str


@dataclass(frozen=True, slots=True)
class DayCloseEvent:
    trade_date: date
    account_index: int
    status_before: str
    status_after: str
    balance_cents: int
    day_net_cents: int
    floor_after_cents: int
    strategy_fills: int
    breach: Refusal | None


@dataclass(frozen=True, slots=True)
class AccountStartEvent:
    ts_ns: int
    trade_date: date
    account_index: int
    phase: str
    balance_cents: int
    floor_cents: int


LedgerEvent = (IntentEvent | FillEvent | CancelEvent | MllCheckEvent | ForcedFlattenEvent
               | DayCloseEvent | AccountStartEvent)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date | time):
        return value.isoformat()
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(v) for v in value]
    return value


def ledger_to_jsonl(ledger: Sequence[LedgerEvent], path: Path) -> None:
    with Path(path).open("w") as fh:
        for event in ledger:
            fh.write(json.dumps({"event": type(event).__name__, **_jsonable(event)}) + "\n")


# ------------------------------------------------------------------ engine ----
@dataclass(frozen=True)
class EngineConfig:
    restart_on_terminal: bool  # required: a breach/pass ends the account; restart or stop
    phase: Phase = Phase.XFA
    slippage_statistic: str = "mean"
    roll_blackout: frozenset[date] = field(default_factory=frozenset)
    # Hindsight fields (``strategy.interface.HINDSIGHT_FIELDS``) are blanked before the bar
    # reaches the strategy, so a strategy cannot condition on information published after the
    # fact. The engine keeps the true values for reporting. Set False only to measure what a
    # hindsight-using strategy would have made — never for a result anyone will trust.
    mask_hindsight_fields: bool = True


@dataclass(frozen=True, slots=True)
class _Order:
    decision_ts_ns: int
    signed_qty: int
    reason: str  # "strategy" | "forced_flatten"


@dataclass(frozen=True)
class BacktestResult:
    ledger: tuple[LedgerEvent, ...]
    final_state: AccountState
    final_position: Position
    bars_processed: int
    accounts_started: int

    def events(self, kind: type) -> tuple:
        return tuple(e for e in self.ledger if isinstance(e, kind))


def _new_account(phase: Phase) -> AccountState:
    return xr.new_combine_account() if phase is Phase.COMBINE else xr.new_xfa_account()


def _price_ticks(price: float) -> int:
    return xr.price_to_ticks(price)


def _touch_ticks(position: Position, balance: int, floor_cents: int) -> int:
    """The first on-grid price, in the adverse direction, at which
    balance + unrealized <= floor: the largest such tick for a long, the smallest for a short."""
    q = position.qty
    bound = Fraction(floor_cents - balance + position.basis_ticks * MES_TICK_VALUE_CENTS,
                     q * MES_TICK_VALUE_CENTS)
    return floor(bound) if q > 0 else ceil(bound)


class _Run:
    """Mutable loop bookkeeping for one run; every object it emits is frozen."""

    def __init__(self, strategy: Strategy, config: EngineConfig, table: SlippageTable) -> None:
        self.strategy, self.config, self.table = strategy, config, table
        self.previous_bar: Bar | None = None
        self.last_close_balance = 0
        self.ledger: list[LedgerEvent] = []
        self.account_index = 0
        self.state = _new_account(config.phase)
        self.position = Position()
        self.pending: tuple[_Order, ...] = ()
        self.trade_date: date | None = None
        self.strategy_fills_today = 0
        self.last_ts = -1
        self.last_instrument: int | None = None
        self.last_bar: Bar | None = None
        self.bars = 0

    # -- fills ------------------------------------------------------------
    def assert_fill_after_decision(self, order: _Order, bar: Bar) -> None:
        if bar.ts_event_ns < order.decision_ts_ns:
            raise EngineInvariantError(
                f"fill bar opens at {bar.ts_event_ns} before the decision {order.decision_ts_ns}")

    def fill(self, order: _Order, bar: Bar, price_ticks: int, reason: str) -> None:
        self.assert_fill_after_decision(order, bar)
        qty = abs(order.signed_qty)
        cost = side_cost(self.table, bar.open_ts_utc, qty, self.config.slippage_statistic)
        self.position, gross = apply_fill(self.position, order.signed_qty, price_ticks)
        self.state = xr.record_realized_pnl(self.state, gross - cost.total_cents)
        if reason == "strategy":
            self.strategy_fills_today += 1
        self.ledger.append(FillEvent(
            fill_ts_ns=bar.ts_event_ns, decision_ts_ns=order.decision_ts_ns,
            account_index=self.account_index, reason=reason,
            side="buy" if order.signed_qty > 0 else "sell", qty=qty,
            price=price_ticks * xr.MES_TICK_SIZE, commission_cents=cost.commission_cents,
            slippage_cents=cost.slippage_cents,
            slippage_ticks_per_micro=cost.slippage_ticks_per_micro, gross_realized_cents=gross,
            position_after=self.position.qty, balance_after_cents=self.state.balance_cents,
            minutes_after_decision=(bar.ts_event_ns - order.decision_ts_ns) // 60_000_000_000,
        ))

    def cancel_pending(self, ts_ns: int, reason: str, keep_forced: bool) -> None:
        kept = []
        for order in self.pending:
            if keep_forced and order.reason != "strategy":
                kept.append(order)
                continue
            self.ledger.append(CancelEvent(ts_ns, order.decision_ts_ns, self.account_index, reason,
                                           "buy" if order.signed_qty > 0 else "sell",
                                           abs(order.signed_qty)))
        self.pending = tuple(kept)

    # -- phases of one bar --------------------------------------------------
    def start_account(self, bar: Bar) -> None:
        self.ledger.append(AccountStartEvent(
            bar.ts_event_ns, bar.trade_date, self.account_index, self.state.phase.value,
            self.state.balance_cents, self.state.mll_floor_cents))

    def roll_session(self, bar: Bar) -> None:
        if self.trade_date is None:
            self.trade_date = bar.trade_date
            self.start_account(bar)
            return
        if bar.trade_date == self.trade_date:
            return
        if bar.trade_date < self.trade_date:
            raise EngineInvariantError(f"trade date went backwards at {bar.ts_event_ns}")
        self.cancel_pending(bar.ts_event_ns, "session_changed_before_fill", keep_forced=True)
        for order in self.pending:  # forced closes must still happen: first price available
            self.fill(order, bar, _price_ticks(bar.open), order.reason)
        self.pending = ()
        # A position must never span a session. If no decision time fell inside the flatten
        # window (a data gap, or an early halt the calendar does not know), no forced flatten was
        # ever queued; close at the last price of the session that is ending, not at the next
        # session's open, which the account could never have traded at.
        if self.position.qty and self.previous_bar is not None:
            self.ledger.append(ForcedFlattenEvent(
                self.previous_bar.decision_ts_ns, self.account_index,
                "sell" if self.position.qty > 0 else "buy", abs(self.position.qty),
                f"session ended on {self.trade_date} with {self.position.qty} micros open and no "
                "flatten-window decision time in the data; closed at the last bar's close"))
            self.fill_at_close(_Order(self.previous_bar.ts_event_ns, -self.position.qty,
                                      "forced_flatten_session_end"), self.previous_bar)
        self.close_day()
        self.trade_date = bar.trade_date
        if self.state.status is not Status.ACTIVE and self.config.restart_on_terminal:
            if self.position.qty:
                raise EngineInvariantError("terminal account still holds a position")
            self.account_index += 1
            self.state = _new_account(self.config.phase)
            self.last_close_balance = self.state.balance_cents
            self.start_account(bar)

    def close_day(self) -> None:
        assert self.trade_date is not None
        before = self.state
        after = xr.close_trading_day(before, self.trade_date, self.strategy_fills_today)
        # Not before.session_start_balance_cents: close_trading_day leaves a terminal account
        # unchanged, so that field freezes and would repeat the breach day's P&L forever.
        day_net = before.balance_cents - self.last_close_balance
        self.ledger.append(DayCloseEvent(
            self.trade_date, self.account_index, before.status.value, after.status.value,
            after.balance_cents, day_net, after.mll_floor_cents, self.strategy_fills_today,
            after.breach if after.breach is not before.breach else None))
        self.state = after
        self.last_close_balance = after.balance_cents
        self.strategy_fills_today = 0

    def fill_pending_at_open(self, bar: Bar) -> None:
        orders, self.pending = self.pending, ()
        for order in orders:
            if order.reason == "strategy" and self.state.status is not Status.ACTIVE:
                self.ledger.append(CancelEvent(bar.ts_event_ns, order.decision_ts_ns,
                                               self.account_index, "account_not_active",
                                               "buy" if order.signed_qty > 0 else "sell",
                                               abs(order.signed_qty)))
                continue
            self.fill(order, bar, _price_ticks(bar.open), order.reason)

    def check_mll(self, bar: Bar) -> None:
        q = self.position.qty
        if q == 0:
            return
        if self.state.status is Status.BREACHED:
            # Breached by a cost booked at a fill on this bar's open (flat-equity check inside
            # record_realized_pnl) while a position is open: Topstep liquidates at once.
            self.fill(_Order(bar.ts_event_ns, -q, "mll_liquidation"), bar, _price_ticks(bar.open),
                      "mll_liquidation")
            return
        if self.state.status is not Status.ACTIVE:
            return
        worst_price = bar.low if q > 0 else bar.high
        worst = self.position.unrealized_cents(_price_ticks(worst_price))
        checked = xr.apply_realtime_mll(self.state, worst)
        breached = checked.status is Status.BREACHED
        self.ledger.append(MllCheckEvent(bar.ts_event_ns, self.account_index, q, worst_price,
                                         worst, self.state.balance_cents,
                                         self.state.mll_floor_cents, breached))
        if not breached:
            return
        touch = _touch_ticks(self.position, self.state.balance_cents, self.state.mll_floor_cents)
        open_ticks = _price_ticks(bar.open)
        liquidation = min(open_ticks, touch) if q > 0 else max(open_ticks, touch)
        self.state = checked
        self.fill(_Order(bar.ts_event_ns, -q, "mll_liquidation"), bar, liquidation,
                  "mll_liquidation")

    def queue_forced_flatten(self, bar: Bar) -> None:
        exposure = self.position.qty + sum(o.signed_qty for o in self.pending)
        forced = xr.required_flatten(exposure, bar.decision_ts_utc, bar.early_halt_ct)
        if forced is None:
            return
        self.cancel_pending(bar.decision_ts_ns, "superseded_by_forced_flatten", keep_forced=True)
        residual = self.position.qty + sum(o.signed_qty for o in self.pending)
        if residual:
            self.ledger.append(ForcedFlattenEvent(bar.decision_ts_ns, self.account_index,
                                                  "sell" if residual > 0 else "buy",
                                                  abs(residual), forced.arithmetic))
            self.pending = (*self.pending, _Order(bar.decision_ts_ns, -residual,
                                                  "forced_flatten"))

    def view(self, bar: Bar) -> AccountView:
        q = self.position.qty
        return AccountView(
            phase=self.state.phase, status=self.state.status, trade_date=bar.trade_date,
            balance_cents=self.state.balance_cents, mll_floor_cents=self.state.mll_floor_cents,
            prior_session_balance_cents=self.state.session_start_balance_cents,
            max_position_micros=xr.max_position_micros(self.state.phase,
                                                       self.state.session_start_balance_cents),
            position_micros=q, pending_signed_micros=sum(o.signed_qty for o in self.pending),
            avg_entry_price=self.position.avg_entry_price,
            unrealized_at_close_cents=self.position.unrealized_cents(_price_ticks(bar.close))
            if q else 0,
        )

    def structural_refusal(self, item: object, bar: Bar) -> Refusal | None:
        if isinstance(item, Refusal):
            return Refusal("strategy_construction_refusal", f"{item.reason}: {item.arithmetic}")
        if not isinstance(item, OrderIntent):
            return Refusal("engine_not_an_intent", f"strategy returned {type(item).__name__}")
        # An OrderIntent built directly, bypassing construct_intent, is not trusted: a bad side
        # would otherwise be read as a sell by OrderIntent.signed_quantity.
        if item.symbol != xr.MES_SYMBOL or item.side not in xr.SIDES:
            return Refusal("engine_malformed_intent",
                           f"symbol {item.symbol!r} / side {item.side!r} did not come through "
                           "construct_intent")
        if (isinstance(item.quantity_micros, bool) or not isinstance(item.quantity_micros, int)
                or item.quantity_micros <= 0):
            return Refusal("engine_malformed_intent",
                           f"quantity {item.quantity_micros!r} is not a positive integer")
        if item.ts_utc != bar.decision_ts_utc:
            return Refusal("engine_intent_timestamp_mismatch",
                           f"intent ts {item.ts_utc.isoformat()} != bar decision time "
                           f"{bar.decision_ts_utc.isoformat()}")
        if bar.in_scheduled_closure:
            return Refusal("engine_scheduled_closure", f"bar {bar.ts_event_ns} is in a closure")
        if bar.in_flatten_window or xr.is_flatten_window(bar.decision_ts_utc, bar.early_halt_ct):
            return Refusal("engine_flatten_window",
                           f"decision {bar.decision_ts_utc.isoformat()} is in the flatten window")
        exposure = self.position.qty + sum(o.signed_qty for o in self.pending)
        if bar.trade_date in self.config.roll_blackout and not xr.is_reducing(
                exposure, item.signed_quantity):
            return Refusal("engine_roll_blackout",
                           f"trade date {bar.trade_date} is a roll-blackout session")
        return None

    def visible_bar(self, bar: Bar) -> Bar:
        if not self.config.mask_hindsight_fields:
            return bar
        return replace(bar, **{name: False for name in HINDSIGHT_FIELDS})

    def ask_strategy(self, bar: Bar) -> None:
        returned = self.strategy.on_bar(self.visible_bar(bar), self.view(bar))
        for item in returned:
            exposure = self.position.qty + sum(o.signed_qty for o in self.pending)
            pending_before = sum(o.signed_qty for o in self.pending)
            refusal = self.structural_refusal(item, bar)
            intent = item if isinstance(item, OrderIntent) else None
            if refusal is None and intent is not None:
                refusal = xr.check_order(intent, self.state, exposure,
                                         self.state.session_start_balance_cents,
                                         bar.early_halt_ct)
            accepted = refusal is None and intent is not None
            self.ledger.append(IntentEvent(bar.decision_ts_ns, self.account_index, intent,
                                           repr(item), accepted, refusal, self.position.qty,
                                           pending_before))
            if accepted:
                self.pending = (*self.pending, _Order(bar.decision_ts_ns, intent.signed_quantity,
                                                      "strategy"))

    def step(self, bar: Bar) -> None:
        if not isinstance(bar, Bar):
            raise EngineInvariantError(f"feed yielded {type(bar).__name__}, not Bar")
        if bar.ts_event_ns <= self.last_ts:
            raise EngineInvariantError(f"bar {bar.ts_event_ns} is not after {self.last_ts}")
        exposure = self.position.qty + sum(o.signed_qty for o in self.pending)
        if (self.last_instrument is not None and bar.instrument_id != self.last_instrument
                and exposure):
            raise EngineInvariantError(
                f"instrument changed {self.last_instrument} -> {bar.instrument_id} with exposure "
                f"{exposure}: a position would span a contract splice")
        self.previous_bar = self.last_bar
        self.last_ts, self.last_instrument, self.last_bar = (bar.ts_event_ns, bar.instrument_id,
                                                             bar)
        self.bars += 1
        self.roll_session(bar)
        self.fill_pending_at_open(bar)
        self.check_mll(bar)
        self.queue_forced_flatten(bar)
        self.ask_strategy(bar)

    def finish(self) -> BacktestResult:
        bar = self.last_bar
        if bar is not None:
            self.cancel_pending(bar.decision_ts_ns, "end_of_data", keep_forced=False)
            if self.position.qty:
                self.fill_at_close(_Order(bar.ts_event_ns, -self.position.qty, "end_of_data"),
                                   bar)
            self.close_day()
        return BacktestResult(tuple(self.ledger), self.state, self.position, self.bars,
                              self.account_index + 1)

    def fill_at_close(self, order: _Order, bar: Bar) -> None:
        """Close at a bar's CLOSE price (end of data, or a session that ended with a position
        open and no flatten-window bar). ``order.reason`` labels which."""
        qty = abs(order.signed_qty)
        cost = side_cost(self.table, bar.open_ts_utc, qty, self.config.slippage_statistic)
        self.position, gross = apply_fill(self.position, order.signed_qty,
                                          _price_ticks(bar.close))
        self.state = xr.record_realized_pnl(self.state, gross - cost.total_cents)
        self.ledger.append(FillEvent(
            bar.decision_ts_ns, order.decision_ts_ns, self.account_index, order.reason,
            "buy" if order.signed_qty > 0 else "sell", qty, bar.close, cost.commission_cents,
            cost.slippage_cents, cost.slippage_ticks_per_micro, gross, self.position.qty,
            self.state.balance_cents, 1))


def run_backtest(
    bars: Iterable[Bar], strategy: Strategy, config: EngineConfig, table: SlippageTable
) -> BacktestResult:
    """Replay ``bars`` (a one-way iterable, strictly increasing) through ``strategy``."""
    run = _Run(strategy, config, table)
    for bar in bars:
        run.step(bar)
    return run.finish()


# ------------------------------------------------------------- reconstruction ----
def reconstruct_balances(ledger: Sequence[LedgerEvent]) -> dict[int, int]:
    """Final balance per account rebuilt from the ledger alone (starts + fills). Used to prove
    the ledger is complete: it must equal what the engine reported."""
    balances: dict[int, int] = {}
    for event in ledger:
        if isinstance(event, AccountStartEvent):
            balances[event.account_index] = event.balance_cents
        elif isinstance(event, FillEvent):
            balances[event.account_index] += (event.gross_realized_cents - event.commission_cents
                                              - event.slippage_cents)
    return balances


def daily_net_pnl(result: BacktestResult) -> pd.DataFrame:
    """One row per (account, trade date) close: the series Stage D.1 feeds into the funnel."""
    rows = [{"trade_date": e.trade_date, "account_index": e.account_index,
             "day_net_cents": e.day_net_cents, "balance_cents": e.balance_cents,
             "status_after": e.status_after, "strategy_fills": e.strategy_fills}
            for e in result.events(DayCloseEvent)]
    return pd.DataFrame(rows, columns=["trade_date", "account_index", "day_net_cents",
                                       "balance_cents", "status_after", "strategy_fills"])


def bars_frame_to_list(frame: pd.DataFrame) -> list[Bar]:
    """Convenience for tests: materialize bars (the engine itself only iterates)."""
    return list(iter_bars(frame))


__all__ = [
    "BAR_COLUMNS", "ENGINE_REFUSAL_ORDER", "AccountStartEvent", "BacktestResult", "CancelEvent",
    "DayCloseEvent", "EngineConfig", "EngineInvariantError", "FillEvent", "ForcedFlattenEvent",
    "IntentEvent", "Lot", "MllCheckEvent", "Position", "apply_fill", "bars_frame_to_list",
    "daily_net_pnl", "iter_bars", "ledger_to_jsonl", "reconstruct_balances",
    "roll_blackout_dates", "run_backtest", "splice_trade_dates_from_parquet",
]
