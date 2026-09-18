"""Constraint tests for sim/engine.py (Stage C, Task 7): forced flatten, the
real-time MLL breach/liquidation, account restart, structural refusals, roll
blackout, position limits, session-change cancellation, and the engine's
structural invariants.

Every expected number is hand-computed in a comment beside the assert that
checks it; nothing is obtained by running the engine and pasting the result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from rules.xfa_rules import MES_SYMBOL, construct_intent
from sim.costs import SlippageTable
from sim.engine import (
    NO_ROLL_BLACKOUT,
    AccountStartEvent,
    CancelEvent,
    EngineConfig,
    EngineInvariantError,
    FillEvent,
    ForcedFlattenEvent,
    IntentEvent,
    MllCheckEvent,
    run_backtest,
)
from strategy.interface import AccountView, Bar, construct_bar, market_intent

CT = ZoneInfo("America/Chicago")
INSTRUMENT = 4242
NS_PER_S = 1_000_000_000


def ct_ns(day: date, hour: int, minute: int) -> int:
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def make_bar(
    day: date,
    hour: int,
    minute: int,
    open_price: float = 6000.00,
    *,
    high: float | None = None,
    low: float | None = None,
    close: float | None = None,
) -> Bar:
    """Flag defaults follow the task convention: in_no_new_positions_window True
    from 15:08 CT, in_flatten_window True from 15:10 CT, both False again at the
    17:00 CT reopen; early_halt_ct None; every other flag False; gap 0."""
    in_no_new = (hour, minute) >= (15, 8) and (hour, minute) < (17, 0)
    in_flatten = (hour, minute) >= (15, 10) and (hour, minute) < (17, 0)
    result = construct_bar(
        ts_event_ns=ct_ns(day, hour, minute),
        open=open_price,
        high=open_price if high is None else high,
        low=open_price if low is None else low,
        close=open_price if close is None else close,
        volume=10,
        instrument_id=INSTRUMENT,
        raw_symbol="MESH6",
        trade_date=day,
        in_flatten_window=in_flatten,
        in_no_new_positions_window=in_no_new,
        early_halt_ct=None,
        in_scheduled_closure=False,
        is_roll_session=False,
        gap_before_minutes=0,
        vendor_degraded_day=False,
    )
    assert isinstance(result, Bar), f"expected a Bar, got a refusal: {result!r}"
    return result


def stat(mean: float) -> dict[str, float | int]:
    return {"mean": mean, "p50": mean, "p90": mean, "p99": mean, "insufficient_depth": 0}


TABLE = SlippageTable(
    sizes_micros=(1, 5, 10, 50),
    bucket_minutes=15,
    buckets={
        "09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.5), "50": stat(1.0)},
        "15:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)},
    },
    windows={},
)

D0 = date(2026, 1, 14)  # synthetic Wednesday
D_PREV = date(2026, 1, 13)  # Tuesday
D_NEXT = date(2026, 1, 15)  # Thursday

RESTART = EngineConfig(restart_on_terminal=True, roll_blackout=NO_ROLL_BLACKOUT)
NO_RESTART = EngineConfig(restart_on_terminal=False, roll_blackout=NO_ROLL_BLACKOUT)


@dataclass(frozen=True)
class ScheduledStrategy:
    """Emits market_intent(bar, side, qty) for each (side, qty) keyed by the bar's
    OWN ts_event_ns (the bar the strategy is looking at when it decides)."""

    name: str = "scheduled"
    schedule: dict[int, tuple[tuple[str, int], ...]] = field(default_factory=dict)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        orders = self.schedule.get(bar.ts_event_ns, ())
        return tuple(market_intent(bar, side, qty) for side, qty in orders)


# ============================================================ 8: forced flatten
def test_forced_flatten_and_the_15_08_15_10_boundary() -> None:
    # Arrange: buy 2 decided at 14:59 (fills 15:00, price 6000.00). At 15:07
    # (decision 15:08 exactly) the strategy tries buy 1 (refused:
    # no_new_positions_after_cutoff) AND sell 1 reducing 2->1 (accepted, fills at
    # 15:08's open). At 15:09 (decision 15:10 exactly) the strategy tries buy 1
    # again (refused: engine_flatten_window) while the residual 1 micro position
    # is queued for a forced flatten, filling at 15:10's open. All fills land in
    # the 15-minute CT bucket "15:00" (minutes 0, 8 and 10 each floor to 0).
    hours_minutes = [(14, 59), (15, 0), (15, 7), (15, 8), (15, 9), (15, 10), (15, 11), (15, 12)]
    bars = [make_bar(D0, h, m, 6000.00) for h, m in hours_minutes]
    by_hm = {hm: bar for hm, bar in zip(hours_minutes, bars, strict=True)}
    schedule = {
        by_hm[(14, 59)].ts_event_ns: (("buy", 2),),
        by_hm[(15, 7)].ts_event_ns: (("buy", 1), ("sell", 1)),
        by_hm[(15, 9)].ts_event_ns: (("buy", 1),),
    }

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), RESTART, TABLE)

    # Assert: the two refusals.
    intents = result.events(IntentEvent)
    refused = {e.decision_ts_ns: e.refusal.reason for e in intents if not e.accepted}
    assert by_hm[(15, 7)].decision_ts_ns in refused  # the 15:08-decision buy
    assert refused[by_hm[(15, 7)].decision_ts_ns] == "no_new_positions_after_cutoff"
    assert refused[by_hm[(15, 9)].decision_ts_ns] == "engine_flatten_window"

    # The 15:08-decision sell (reducing 2 -> 1) is accepted.
    accepted_at_1508 = [
        e for e in intents if e.decision_ts_ns == by_hm[(15, 7)].decision_ts_ns and e.accepted
    ]
    assert len(accepted_at_1508) == 1
    assert accepted_at_1508[0].intent.side == "sell"

    # The forced flatten itself: queued when the 15:09 bar's decision (15:10) is
    # inside the flatten window, for the residual 1 micro (2 - 1 already sold).
    forced = result.events(ForcedFlattenEvent)
    assert len(forced) == 1
    assert forced[0].side == "sell"
    assert forced[0].qty == 1
    assert forced[0].decision_ts_ns == by_hm[(15, 9)].decision_ts_ns

    # Three fills: buy2 @ 15:00, sell1 (reducing) @ 15:08, forced sell1 @ 15:10.
    fills = result.events(FillEvent)
    assert len(fills) == 3
    entry, partial, flatten = fills
    assert entry.fill_ts_ns == by_hm[(15, 0)].ts_event_ns
    assert partial.fill_ts_ns == by_hm[(15, 8)].ts_event_ns
    assert flatten.fill_ts_ns == by_hm[(15, 10)].ts_event_ns
    assert flatten.reason == "forced_flatten"
    assert flatten.price == 6000.00
    # every fill is flat-priced (no move), so gross realized is 0 on the closes
    assert partial.gross_realized_cents == 0
    assert flatten.gross_realized_cents == 0
    # bucket "15:00": qty 2 and qty 1 -> size-5 (0.52) and size-1 (0.5) rows
    # entry (qty 2): commission 122, slippage ceil(2*0.52*125)=ceil(130.0)=130
    assert entry.commission_cents == 122
    assert entry.slippage_cents == 130
    # partial + forced (qty 1 each): commission 61, slippage ceil(1*0.5*125)=63
    for f in (partial, flatten):
        assert f.commission_cents == 61
        assert f.slippage_cents == 63
    # final balance = -(122+130) - (61+63) - (61+63) = -252 -124 -124 = -500
    assert result.final_state.balance_cents == -500


# =============================================================== 9: MLL breach
def _breach_setup(open_price: float, low_price: float, close_price: float) -> tuple:
    """Buy 10 @ 6000.00 (fills at bar1's open); bar2 is the breach bar."""
    bar0 = make_bar(D0, 9, 0, 6000.00)
    bar1 = make_bar(D0, 9, 1, 6000.00)
    high = max(open_price, close_price)
    bar2 = make_bar(D0, 9, 2, open_price, high=high, low=low_price, close=close_price)
    schedule = {
        bar0.ts_event_ns: (("buy", 10),),
        bar2.ts_event_ns: (("buy", 1),),  # attempted AFTER the breach, on the same bar
    }
    result = run_backtest(
        [bar0, bar1, bar2], ScheduledStrategy(schedule=schedule), RESTART, TABLE
    )
    return result, bar2


def test_mll_breach_liquidates_at_the_touch_when_the_open_is_above_it() -> None:
    # Arrange/Act: entry 6000.00 (ticks 24000), qty 10.
    # entry cost: commission 610, slippage ceil(10*0.5*125)=ceil(625.0)=625 -> 1235
    # balance after entry = -1235. floor = -200000.
    # touch = floor((floor - balance + basis_ticks*125) / (qty*125))
    #       = floor((-200000 - (-1235) + 240000*125) / 1250)
    #       = floor((-198765 + 30000000) / 1250) = floor(29801235 / 1250)
    #       = floor(23840.988) = 23840 -> price 23840*0.25 = 5960.00
    # open 5970.00 (ticks 23880, above the touch) safely above; low 5950.00 (ticks
    # 23800) far below it -> liquidation = min(23880, 23840) = 23840 = 5960.00.
    result, bar2 = _breach_setup(open_price=5970.00, low_price=5950.00, close_price=5960.00)

    # Assert
    mll_checks = result.events(MllCheckEvent)
    breach_check = next(e for e in mll_checks if e.bar_ts_ns == bar2.ts_event_ns)
    assert breach_check.breached is True

    fills = result.events(FillEvent)
    assert len(fills) == 2  # entry buy10, then the liquidation
    liquidation = fills[1]
    assert liquidation.reason == "mll_liquidation"
    assert liquidation.price == 5960.00
    assert liquidation.qty == 10
    # gross = 10 * (23840-24000) * 125 = 10 * -160 * 125 = -200000
    assert liquidation.gross_realized_cents == -200_000
    # commission 610, slippage ceil(10*0.5*125)=625 -> total 1235
    assert liquidation.commission_cents == 610
    assert liquidation.slippage_cents == 625
    # balance = -1235 + (-200000 - 1235) = -202470
    assert liquidation.balance_after_cents == -202_470
    assert result.final_state.balance_cents == -202_470

    assert result.final_state.status.value == "breached"
    refusals = {e.decision_ts_ns: e.refusal for e in result.events(IntentEvent) if not e.accepted}
    assert refusals[bar2.decision_ts_ns].reason == "account_not_active"


def test_mll_breach_liquidates_at_the_open_when_the_open_is_below_the_touch() -> None:
    # Arrange/Act: same entry and touch (5960.00) as above, but this bar OPENS
    # below the touch: open 5955.00 (ticks 23820), low 5940.00 (ticks 23760).
    # liquidation = min(23820, 23840) = 23820 = 5955.00 (the open, not the touch).
    result, bar2 = _breach_setup(open_price=5955.00, low_price=5940.00, close_price=5945.00)

    # Assert
    mll_checks = result.events(MllCheckEvent)
    breach_check = next(e for e in mll_checks if e.bar_ts_ns == bar2.ts_event_ns)
    assert breach_check.breached is True

    fills = result.events(FillEvent)
    liquidation = fills[1]
    assert liquidation.price == 5955.00
    # gross = 10 * (23820-24000) * 125 = 10 * -180 * 125 = -225000
    assert liquidation.gross_realized_cents == -225_000
    # balance = -1235 + (-225000 - 1235) = -227470
    assert liquidation.balance_after_cents == -227_470
    assert result.final_state.status.value == "breached"


# ============================================================= 10: restart
def _day1_breach_bars() -> list[Bar]:
    bar0 = make_bar(D0, 9, 0, 6000.00)
    bar1 = make_bar(D0, 9, 1, 6000.00)
    bar2 = make_bar(D0, 9, 2, 5970.00, high=5970.00, low=5950.00, close=5960.00)
    return [bar0, bar1, bar2]


def test_restart_on_terminal_true_starts_a_fresh_account_on_the_next_day() -> None:
    # Arrange: day 1 breaches (as in test 9's first scenario); day 2 (Jan 15)
    # brings one bar, which should trigger a restart.
    day1 = _day1_breach_bars()
    day2_bar = make_bar(D_NEXT, 9, 0, 6000.00)
    schedule = {day1[0].ts_event_ns: (("buy", 10),)}

    # Act
    result = run_backtest(
        [*day1, day2_bar], ScheduledStrategy(schedule=schedule), RESTART, TABLE
    )

    # Assert
    starts = result.events(AccountStartEvent)
    assert len(starts) == 2
    first, second = starts
    assert first.account_index == 0
    assert second.account_index == 1
    assert second.trade_date == D_NEXT
    # a fresh XFA account: balance 0, floor = 0 - 200_000 = -200_000
    assert second.balance_cents == 0
    assert second.floor_cents == -200_000
    assert result.accounts_started == 2


def test_restart_on_terminal_false_leaves_the_account_breached() -> None:
    # Arrange: same day-1 breach, restart disabled.
    day1 = _day1_breach_bars()
    day2_bar = make_bar(D_NEXT, 9, 0, 6000.00)
    schedule = {
        day1[0].ts_event_ns: (("buy", 10),),
        day2_bar.ts_event_ns: (("buy", 1),),  # tried on day 2, still breached
    }

    # Act
    result = run_backtest(
        [*day1, day2_bar], ScheduledStrategy(schedule=schedule), NO_RESTART, TABLE
    )

    # Assert: no restart -> exactly one AccountStartEvent, still account_index 0.
    starts = result.events(AccountStartEvent)
    assert len(starts) == 1
    assert result.accounts_started == 1
    assert result.final_state.status.value == "breached"

    refusals = {e.decision_ts_ns: e.refusal for e in result.events(IntentEvent) if not e.accepted}
    assert refusals[day2_bar.decision_ts_ns].reason == "account_not_active"


# ================================================ 11: structural refusals
def test_intent_stamped_with_bar_open_time_is_refused_and_never_filled() -> None:
    # Arrange: a strategy that (incorrectly) stamps its intent with the bar's
    # OPEN time instead of its decision time (open + 60s).
    @dataclass(frozen=True)
    class BadTimestampStrategy:
        name: str = "bad_ts"

        def on_bar(self, bar: Bar, account: AccountView) -> tuple:
            return (
                construct_intent(
                    symbol=MES_SYMBOL, side="buy", quantity_micros=1, ts_utc=bar.open_ts_utc
                ),
            )

    bars = [make_bar(D0, 9, 0), make_bar(D0, 9, 1)]

    # Act
    result = run_backtest(bars, BadTimestampStrategy(), RESTART, TABLE)

    # Assert
    intents = result.events(IntentEvent)
    assert len(intents) == 2  # one attempt per bar, both refused the same way
    for e in intents:
        assert not e.accepted
        assert e.refusal.reason == "engine_intent_timestamp_mismatch"
    assert result.events(FillEvent) == ()


def test_strategy_returning_a_non_intent_object_is_refused() -> None:
    @dataclass(frozen=True)
    class NonIntentStrategy:
        name: str = "non_intent"

        def on_bar(self, bar: Bar, account: AccountView) -> tuple:
            return ("definitely not an intent",)

    bar = make_bar(D0, 9, 0)

    # Act
    result = run_backtest([bar], NonIntentStrategy(), RESTART, TABLE)

    # Assert
    intents = result.events(IntentEvent)
    assert len(intents) == 1
    assert intents[0].refusal.reason == "engine_not_an_intent"


def test_strategy_returning_a_refusal_is_wrapped_as_construction_refusal() -> None:
    @dataclass(frozen=True)
    class ConstructionRefusalStrategy:
        name: str = "bad_construction"

        def on_bar(self, bar: Bar, account: AccountView) -> tuple:
            # "ES" is not MES_SYMBOL -> construct_intent refuses with intent_bad_symbol.
            return (
                construct_intent(
                    symbol="ES", side="buy", quantity_micros=1, ts_utc=bar.decision_ts_utc
                ),
            )

    bar = make_bar(D0, 9, 0)

    # Act
    result = run_backtest([bar], ConstructionRefusalStrategy(), RESTART, TABLE)

    # Assert
    intents = result.events(IntentEvent)
    assert len(intents) == 1
    refusal = intents[0].refusal
    assert refusal.reason == "strategy_construction_refusal"
    assert "intent_bad_symbol" in refusal.arithmetic


# =============================================================== 12: roll blackout
def test_roll_blackout_refuses_a_brand_new_position() -> None:
    # Arrange: a single flat account tries to open on a blackout trade date.
    bar = make_bar(D0, 9, 0)
    config = EngineConfig(restart_on_terminal=True, roll_blackout=frozenset({D0}))
    schedule = {bar.ts_event_ns: (("buy", 1),)}

    # Act
    result = run_backtest([bar], ScheduledStrategy(schedule=schedule), config, TABLE)

    # Assert
    intents = result.events(IntentEvent)
    assert len(intents) == 1
    assert intents[0].refusal.reason == "engine_roll_blackout"


def test_roll_blackout_day_refuses_both_sides_and_cannot_inherit_a_position() -> None:
    # Construction note: a position can never be OPENED on a blackout trade date (any
    # non-reducing order is refused), and since the Stage C engine closes any position that
    # is still open when a session ends (no flatten-window bar in the data), a position can
    # never be INHERITED into a blackout day either. So on a blackout day the account is flat
    # and both sides are opening orders: both are refused. Day 1 (2026-01-13) opens a 2-micro
    # long and its session ends without a flatten-window bar; the engine closes it at that
    # session's last close (reason "forced_flatten_session_end"), so day 2 starts flat.
    day1_bar0 = make_bar(D_PREV, 9, 0, 6000.00)
    day1_bar1 = make_bar(D_PREV, 9, 1, 6000.00)
    day2_bar = make_bar(D0, 9, 0, 6000.00)
    config = EngineConfig(restart_on_terminal=True, roll_blackout=frozenset({D0}))
    schedule = {
        day1_bar0.ts_event_ns: (("buy", 2),),
        day2_bar.ts_event_ns: (("buy", 1), ("sell", 1)),
    }

    # Act
    result = run_backtest(
        [day1_bar0, day1_bar1, day2_bar], ScheduledStrategy(schedule=schedule), config, TABLE
    )

    # Assert: day 1's position is closed by the engine when the session ends.
    closing = [f for f in result.events(FillEvent) if f.reason == "forced_flatten_session_end"]
    assert len(closing) == 1 and closing[0].qty == 2 and closing[0].side == "sell"
    # Day 2 is blacked out and the account is flat, so BOTH orders are opening orders.
    day2_intents = [
        e for e in result.events(IntentEvent) if e.decision_ts_ns == day2_bar.decision_ts_ns
    ]
    assert len(day2_intents) == 2
    assert [e.accepted for e in day2_intents] == [False, False]
    assert {e.refusal.reason for e in day2_intents} == {"engine_roll_blackout"}


# ============================================================ 13: position limit
def test_position_limit_21_micros_refused_20_accepted() -> None:
    # Arrange: fresh XFA, prior session balance $0 -> base tier, 2 minis = 20 micros.
    bar_a = make_bar(D0, 9, 0)
    over_limit = run_backtest(
        [bar_a], ScheduledStrategy(schedule={bar_a.ts_event_ns: (("buy", 21),)}), RESTART, TABLE
    )
    bar_b = make_bar(D0, 9, 0)
    at_limit = run_backtest(
        [bar_b], ScheduledStrategy(schedule={bar_b.ts_event_ns: (("buy", 20),)}), RESTART, TABLE
    )

    # Assert
    over_intent = over_limit.events(IntentEvent)[0]
    assert not over_intent.accepted
    assert over_intent.refusal.reason == "position_limit_exceeded"

    at_intent = at_limit.events(IntentEvent)[0]
    assert at_intent.accepted
    assert at_intent.refusal is None


# ==================================================== 14: session-change cancel
def test_session_change_cancels_a_pending_strategy_order() -> None:
    # Arrange: trade date D's data ends at 10:00 CT with a pending buy; the next
    # bar fed belongs to D+1 at 17:00 CT.
    d_last = make_bar(D0, 10, 0, 6000.00)
    d_plus1_first = make_bar(D_NEXT, 17, 0, 6000.00)
    schedule = {
        d_last.ts_event_ns: (("buy", 1),),
        d_plus1_first.ts_event_ns: (("buy", 1),),
    }

    # Act
    strategy = ScheduledStrategy(schedule=schedule)
    result = run_backtest([d_last, d_plus1_first], strategy, RESTART, TABLE)

    # Assert: no fill ever happens for the cancelled D order.
    assert result.events(FillEvent) == ()

    cancels = [e for e in result.events(CancelEvent) if e.reason == "session_changed_before_fill"]
    assert len(cancels) == 1
    assert cancels[0].side == "buy"
    assert cancels[0].qty == 1
    assert cancels[0].decision_ts_ns == d_last.decision_ts_ns

    ledger = list(result.ledger)
    cancel_idx = next(i for i, e in enumerate(ledger) if e is cancels[0])
    day_close_idx = next(
        i for i, e in enumerate(ledger)
        if type(e).__name__ == "DayCloseEvent" and e.trade_date == D0
    )
    d_plus1_intent_idx = next(
        i
        for i, e in enumerate(ledger)
        if type(e).__name__ == "IntentEvent" and e.decision_ts_ns == d_plus1_first.decision_ts_ns
    )
    assert cancel_idx < day_close_idx < d_plus1_intent_idx


# =============================================================== 15: invariants
def test_out_of_order_bars_raise_engine_invariant_error() -> None:
    bar_a = make_bar(D0, 9, 1)
    bar_b = make_bar(D0, 9, 0)  # earlier timestamp, fed second

    with pytest.raises(EngineInvariantError):
        run_backtest([bar_a, bar_b], ScheduledStrategy(), RESTART, TABLE)


def test_instrument_change_while_holding_a_position_raises() -> None:
    bar0 = make_bar(D0, 9, 0, 6000.00)
    bar1 = make_bar(D0, 9, 1, 6000.00)  # fills the buy -> position becomes 1
    # A bar with a different instrument_id, built by hand since make_bar pins
    # INSTRUMENT for every other test.
    other_instrument = construct_bar(
        ts_event_ns=bar1.ts_event_ns + 60_000_000_000,
        open=6000.00, high=6000.00, low=6000.00, close=6000.00,
        volume=10, instrument_id=INSTRUMENT + 1, raw_symbol="MESM6",
        trade_date=D0, in_flatten_window=False, in_no_new_positions_window=False,
        early_halt_ct=None, in_scheduled_closure=False, is_roll_session=False,
        gap_before_minutes=0, vendor_degraded_day=False,
    )
    assert isinstance(other_instrument, Bar)
    schedule = {bar0.ts_event_ns: (("buy", 1),)}

    with pytest.raises(EngineInvariantError):
        run_backtest(
            [bar0, bar1, other_instrument], ScheduledStrategy(schedule=schedule), RESTART, TABLE
        )


def test_end_of_data_closes_an_open_position_at_the_last_bars_close() -> None:
    # Arrange: buy 1 decided on bar0 (09:00), fills at bar1's OPEN (6000.00,
    # ticks 24000); bar1 is also the LAST bar fed, closing at 6002.00 (ticks
    # 24008), a monotonic up-bar (open 6000.00 -> close 6002.00).
    bar0 = make_bar(D0, 9, 0, 6000.00)
    bar1 = make_bar(D0, 9, 1, 6000.00, high=6002.00, low=6000.00, close=6002.00)
    schedule = {bar0.ts_event_ns: (("buy", 1),)}

    # Act
    result = run_backtest([bar0, bar1], ScheduledStrategy(schedule=schedule), RESTART, TABLE)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 2
    entry, end_of_data = fills
    assert entry.price == 6000.00
    assert end_of_data.reason == "end_of_data"
    assert end_of_data.price == 6002.00  # the bar's CLOSE, not its open
    # gross = 1 * (24008-24000) * 125 = 1000
    assert end_of_data.gross_realized_cents == 1000
    # costs at bar1's OPEN-time bucket "09:00", size 1, mean 0.5 -> both fills
    # commission 61, slippage ceil(1*0.5*125)=63
    for f in fills:
        assert f.commission_cents == 61
        assert f.slippage_cents == 63
    # balance = (0-124) + (1000-124) = -124 + 876 = 752
    assert result.final_state.balance_cents == 752
