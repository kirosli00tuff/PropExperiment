"""Engine regression tests for defects found after the first engine build (Stage C review).

Each test states the defect, and each expected value is hand-computed in its comments.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from rules.xfa_rules import OrderIntent, Status
from sim.costs import SlippageTable
from sim.engine import (
    EngineConfig,
    FillEvent,
    ForcedFlattenEvent,
    IntentEvent,
    _Run,
    daily_net_pnl,
    reconstruct_balances,
    run_backtest,
)
from strategy.interface import AccountView, Bar, construct_bar, market_intent


def _stat(mean: float) -> dict:
    return {"mean": mean, "p50": mean, "p90": mean, "p99": mean, "insufficient_depth": 0}


# Zero slippage in the 09:00 CT bucket, so every side costs exactly 61 cents per micro.
ZERO_SLIP = SlippageTable(sizes_micros=(1, 5, 10, 50), bucket_minutes=15,
                          buckets={"09:00": {str(s): _stat(0.0) for s in (1, 5, 10, 50)}},
                          windows={})
T0_NS = int(datetime(2026, 1, 14, 15, 0, tzinfo=UTC).timestamp()) * 1_000_000_000


def _bar_on(day: date, minute: int, o: float, h: float, lo: float, c: float,
            flatten: bool = False) -> Bar:
    """A bar `minute` minutes after 09:00 CT on `day` (CST: 15:00 UTC)."""
    ts = int(datetime(day.year, day.month, day.day, 15, 0, tzinfo=UTC).timestamp())
    built = construct_bar(ts_event_ns=ts * 1_000_000_000 + minute * 60_000_000_000, open=o,
                          high=h, low=lo, close=c, volume=10, instrument_id=1,
                          raw_symbol="MESH6", trade_date=day, in_flatten_window=flatten,
                          in_no_new_positions_window=flatten, early_halt_ct=None,
                          in_scheduled_closure=False, is_roll_session=False,
                          gap_before_minutes=0, vendor_degraded_day=False)
    assert isinstance(built, Bar)
    return built


def _bar(minute: int, o: float, h: float, lo: float, c: float) -> Bar:
    # 2026-01-14 is a Wednesday in CST (UTC-6): 15:00 UTC = 09:00 CT.
    built = construct_bar(ts_event_ns=T0_NS + minute * 60_000_000_000, open=o, high=h, low=lo,
                          close=c, volume=10, instrument_id=1, raw_symbol="MESH6",
                          trade_date=date(2026, 1, 14), in_flatten_window=False,
                          in_no_new_positions_window=False, early_halt_ct=None,
                          in_scheduled_closure=False, is_roll_session=False,
                          gap_before_minutes=0, vendor_degraded_day=False)
    assert isinstance(built, Bar)
    return built


@dataclass(frozen=True)
class ScheduleAt:
    """Orders keyed by absolute bar timestamp (works across trade dates)."""

    orders: dict  # bar ts_event_ns -> (side, qty)
    name: str = "schedule_at"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if bar.ts_event_ns in self.orders:
            side, qty = self.orders[bar.ts_event_ns]
            return (market_intent(bar, side, qty),)
        return ()


@dataclass(frozen=True)
class Schedule:
    orders: dict  # bar index -> (side, qty)
    name: str = "schedule"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        index = (bar.ts_event_ns - T0_NS) // 60_000_000_000
        if index in self.orders:
            side, qty = self.orders[index]
            return (market_intent(bar, side, qty),)
        return ()


def test_breach_by_entry_cost_liquidates_the_open_position_at_once() -> None:
    """Defect: a fill whose cost pushed equity onto the floor breached the account with the new
    position still open. ``check_mll`` returned early for a non-active account, so the position
    stayed open and kept accruing P&L until the 15:10 flatten."""
    bars = [
        _bar(0, 6000.00, 6000.00, 6000.00, 6000.00),  # decide: buy 20
        _bar(1, 6000.00, 6000.00, 5980.25, 5980.25),  # fill buy 20 @6000; decide: sell 20
        _bar(2, 5980.25, 5980.25, 5980.25, 5980.25),  # fill sell 20 @5980.25; decide: buy 1
        _bar(3, 5980.25, 5980.50, 5980.25, 5980.50),  # fill buy 1 -> breach at the fill
        _bar(4, 5980.50, 5980.50, 5980.50, 5980.50),
    ]
    strategy = Schedule({0: ("buy", 20), 1: ("sell", 20), 2: ("buy", 1)})
    result = run_backtest(iter(bars), strategy, EngineConfig(restart_on_terminal=False), ZERO_SLIP)

    # Bar 1 fill: cost 20 x 61 = 1,220 -> balance -1,220. Intrabar low 5980.25 is -79 ticks:
    #   equity = -1,220 + 20 x (-79) x 125 = -1,220 - 197,500 = -198,720 > floor -200,000: ok.
    # Bar 2 fill: gross 20 x (-79) x 125 = -197,500; cost 1,220 -> balance -199,940 (> floor).
    # Bar 3 fill: buy 1, cost 61 -> balance -200,001 <= -200,000 -> BREACHED with 1 micro open.
    # Fix: liquidate at bar 3's open 5980.25 -> gross 0, cost 61 -> balance -200,062, flat.
    fills = result.events(FillEvent)
    assert [f.reason for f in fills] == ["strategy", "strategy", "strategy", "mll_liquidation"]
    liquidation = fills[-1]
    assert liquidation.fill_ts_ns == bars[3].ts_event_ns
    assert (liquidation.side, liquidation.qty, liquidation.price) == ("sell", 1, 5980.25)
    assert liquidation.gross_realized_cents == 0
    assert result.final_position.qty == 0
    assert result.final_state.status is Status.BREACHED
    assert result.final_state.balance_cents == -200_062
    assert reconstruct_balances(result.ledger)[0] == -200_062


def test_position_is_closed_at_the_old_session_close_not_the_new_session_open() -> None:
    """Defect (review, high): when no decision time fell inside the flatten window — a data gap,
    or an early halt the calendar does not know — no forced flatten was queued, and the position
    survived into the NEXT session and was marked at its open. A Friday long could be closed on
    Sunday at a gapped price the account could never have traded."""
    friday, monday = date(2026, 1, 16), date(2026, 1, 19)
    bars = [
        _bar_on(friday, 0, 6000.00, 6000.00, 6000.00, 6000.00),  # decide: buy 2
        _bar_on(friday, 1, 6000.00, 6000.25, 6000.00, 6000.25),  # fill buy 2 @6000.00
        _bar_on(friday, 2, 6000.25, 6000.50, 6000.25, 6000.50),  # last Friday bar: close 6000.50
        _bar_on(monday, 0, 6100.00, 6100.00, 6100.00, 6100.00),  # new session, gapped +100
    ]
    result = run_backtest(iter(bars), ScheduleAt({bars[0].ts_event_ns: ("buy", 2)}),
                          EngineConfig(restart_on_terminal=False), ZERO_SLIP)
    fills = result.events(FillEvent)
    assert [f.reason for f in fills] == ["strategy", "forced_flatten_session_end"]
    # Closed at Friday's last CLOSE 6000.50, not Monday's 6100.00 open.
    assert fills[1].price == 6000.50
    # Gross: 2 micros x +2 ticks x 125 = 500; costs 2 x (2 x 61) = 244 -> balance 256.
    assert fills[1].gross_realized_cents == 500
    assert result.final_state.balance_cents == 256
    assert result.final_position.qty == 0
    assert len(result.events(ForcedFlattenEvent)) == 1
    # The P&L belongs to Friday; Monday's close adds nothing.
    daily = daily_net_pnl(result)
    assert list(daily["day_net_cents"]) == [256, 0]


def test_terminal_account_does_not_repeat_its_last_day_pnl() -> None:
    """Defect (review, medium): close_trading_day leaves a terminal account untouched, so
    session_start_balance_cents froze and every later day repeated the breach day's P&L. Summing
    the daily series — the documented Stage D.1 funnel input — multiplied one loss by the number
    of days left in the run."""
    day1, day2, day3 = date(2026, 1, 13), date(2026, 1, 14), date(2026, 1, 15)
    bars = [
        _bar_on(day1, 0, 6000.00, 6000.00, 6000.00, 6000.00),  # decide: buy 20
        _bar_on(day1, 1, 6000.00, 6000.00, 5900.00, 5900.00),  # fill, then breach + liquidation
        _bar_on(day2, 0, 5900.00, 5900.00, 5900.00, 5900.00),
        _bar_on(day3, 0, 5900.00, 5900.00, 5900.00, 5900.00),
    ]
    result = run_backtest(iter(bars), ScheduleAt({bars[0].ts_event_ns: ("buy", 20)}),
                          EngineConfig(restart_on_terminal=False), ZERO_SLIP)
    assert result.final_state.status is Status.BREACHED
    daily = daily_net_pnl(result)
    # Day 1 carries the whole loss; the dead account's later days are flat.
    assert list(daily["day_net_cents"])[1:] == [0, 0]
    assert list(daily["day_net_cents"])[0] == result.final_state.balance_cents


class HandBuiltIntent:
    """Test-only: bypasses construct_intent, the way a careless strategy might."""

    name = "hand_built"

    def __init__(self, intent: OrderIntent) -> None:
        self.intent = intent

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if bar.ts_event_ns != T0_NS:
            return ()
        return (OrderIntent(self.intent.symbol, self.intent.side, self.intent.quantity_micros,
                            bar.decision_ts_utc),)


def test_intent_not_built_by_construct_intent_is_refused() -> None:
    """Defect (review, low): the engine trusted OrderIntent fields. side "BUY" is not "buy", and
    OrderIntent.signed_quantity treats anything that is not "buy" as a sell, so the engine SOLD."""
    bars = [_bar(0, 6000.00, 6000.00, 6000.00, 6000.00), _bar(1, 6000.00, 6000.00, 6000.00,
                                                              6000.00)]
    for bad in (OrderIntent("ES", "buy", 5, datetime(2026, 1, 14, 15, 1, tzinfo=UTC)),
                OrderIntent("MES", "BUY", 5, datetime(2026, 1, 14, 15, 1, tzinfo=UTC)),
                OrderIntent("MES", "buy", 0, datetime(2026, 1, 14, 15, 1, tzinfo=UTC)),
                OrderIntent("MES", "buy", -3, datetime(2026, 1, 14, 15, 1, tzinfo=UTC))):
        result = run_backtest(iter(bars), HandBuiltIntent(bad),
                              EngineConfig(restart_on_terminal=False), ZERO_SLIP)
        intents = result.events(IntentEvent)
        assert len(intents) == 1 and not intents[0].accepted
        assert intents[0].refusal.reason == "engine_malformed_intent"
        assert not result.events(FillEvent)


class HindsightReader:
    """Test-only: reads the hindsight flag, which a real strategy must never do."""

    name = "hindsight_reader"

    def __init__(self) -> None:
        self.seen: list[bool] = []

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        self.seen.append(bar.vendor_degraded_day)
        return ()


def test_hindsight_flag_is_blank_in_the_bar_the_strategy_sees() -> None:
    """Defect (review, low): vendor_degraded_day (published by the vendor months later) reached
    on_bar, so a strategy could sit out the 2025-11-28 CME outage day using information nobody
    had at the time. The engine keeps the true value; the strategy's copy is blanked."""
    degraded = construct_bar(ts_event_ns=T0_NS, open=6000.0, high=6000.0, low=6000.0,
                             close=6000.0, volume=1, instrument_id=1, raw_symbol="MESH6",
                             trade_date=date(2026, 1, 14), in_flatten_window=False,
                             in_no_new_positions_window=False, early_halt_ct=None,
                             in_scheduled_closure=False, is_roll_session=False,
                             gap_before_minutes=0, vendor_degraded_day=True)
    assert isinstance(degraded, Bar) and degraded.vendor_degraded_day is True
    reader = HindsightReader()
    run_backtest(iter([degraded]), reader, EngineConfig(restart_on_terminal=False), ZERO_SLIP)
    assert reader.seen == [False]

    unmasked = HindsightReader()
    run_backtest(iter([degraded]), unmasked,
                 EngineConfig(restart_on_terminal=False, mask_hindsight_fields=False), ZERO_SLIP)
    assert unmasked.seen == [True]


def test_reducing_order_is_allowed_on_a_roll_blackout_day() -> None:
    """White-box: replay can no longer carry a position into a blackout day (the session-end
    close prevents it), so this branch of structural_refusal is checked directly."""
    bar = _bar_on(date(2026, 1, 14), 0, 6000.0, 6000.0, 6000.0, 6000.0)
    config = EngineConfig(restart_on_terminal=False, roll_blackout=frozenset({bar.trade_date}))
    from sim.engine import Lot, Position

    run = _Run(ScheduleAt({}), config, ZERO_SLIP)
    run.position = Position((Lot(2, 24_000),))
    reducing = market_intent(bar, "sell", 1)
    opening = market_intent(bar, "sell", 5)
    assert run.structural_refusal(reducing, bar) is None
    refusal = run.structural_refusal(opening, bar)
    assert refusal is not None and refusal.reason == "engine_roll_blackout"
