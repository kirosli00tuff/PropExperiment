"""Focused state-machine tests for H4PassiveFillReversal (Stage D.1b, trial #24).

Calls ``on_bar`` directly with hand-built ``Bar``/``AccountView`` objects, the same
style ``tests/test_strategy_interface.py`` and ``tests/test_passive_fills.py`` use --
no engine, no screening. These check the STATE MACHINE (passive entry, no stacking,
passive-then-market exit, session reset), not the percentile signal math (which is
copied unchanged from H1 and exercised, on real bars, by the fold-0 screen). Several
tests use small non-default ``n_minutes``/``magnitude_window``/band parameters so the
signal fires deterministically after a short, legible warm-up; ``entry_ttl_bars`` and
``exit_ttl_bars`` are left at their production default (5) everywhere, since the ttl
value itself is exactly what several assertions check.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from rules.xfa_rules import Phase, Refusal, Status
from strategy.interface import AccountView, PassiveIntent, construct_bar
from strategy.research.c_short_horizon_reversal.h4_passive_fill_reversal import (
    H4PassiveFillReversal,
)

NS_PER_S = 1_000_000_000
NS_PER_BAR = 60 * NS_PER_S
D0 = date(2026, 1, 5)
D1 = date(2026, 1, 6)
T0 = int(datetime(2026, 1, 5, 14, 30, tzinfo=UTC).timestamp()) * NS_PER_S


def build_bar(ts_event_ns: int, close: float, trade_date: date = D0):
    result = construct_bar(
        ts_event_ns=ts_event_ns, open=close, high=close, low=close, close=close, volume=10,
        instrument_id=12345, raw_symbol="MESH6", trade_date=trade_date, in_flatten_window=False,
        in_no_new_positions_window=False, early_halt_ct=None, in_scheduled_closure=False,
        is_roll_session=False, gap_before_minutes=0, vendor_degraded_day=False,
    )
    assert not isinstance(result, Refusal), result
    return result


def account(**overrides: object) -> AccountView:
    base: dict[str, object] = dict(
        phase=Phase.XFA, status=Status.ACTIVE, trade_date=D0, balance_cents=0,
        mll_floor_cents=-200_000, prior_session_balance_cents=0, max_position_micros=20,
        position_micros=0, pending_signed_micros=0, avg_entry_price=None,
        unrealized_at_close_cents=0,
    )
    base.update(overrides)
    return AccountView(**base)


def _fast_strategy() -> H4PassiveFillReversal:
    """n_minutes=1, magnitude_window=2, band [0, 1]: the signal fires on bar index 2
    (the first bar with both a nonzero 1-minute return and >=1 warmed-up abs-return),
    deterministically, without needing 60+ bars of warm-up. ttl_bars stay at the
    production default (5) on both legs."""
    return H4PassiveFillReversal(n_minutes=1, k_minutes=2, magnitude_window=2, band_low=0.0,
                                 band_high=1.0)


def _drive_to_entry_signal(strategy: H4PassiveFillReversal) -> tuple:
    """Feeds three flat bars (rising closes) and returns the third call's intents --
    the bar on which the fade signal first fires."""
    bars = [build_bar(T0, 6000.00), build_bar(T0 + NS_PER_BAR, 6000.25),
            build_bar(T0 + 2 * NS_PER_BAR, 6000.50)]
    flat = account(position_micros=0, pending_signed_micros=0)
    strategy.on_bar(bars[0], flat)
    strategy.on_bar(bars[1], flat)
    return strategy.on_bar(bars[2], flat), bars[2]


class TestPassiveEntry:
    def test_entry_emits_passive_intent_at_close_plus_one_tick_on_fade_side(self) -> None:
        strategy = _fast_strategy()
        intents, entry_bar = _drive_to_entry_signal(strategy)

        assert len(intents) == 1
        intent = intents[0]
        assert isinstance(intent, PassiveIntent)
        # Rising closes -> positive return -> fade side is "sell".
        assert intent.intent.side == "sell"
        assert intent.intent.quantity_micros == 1
        # Sell rests ABOVE the close: 6000.50 + 1 tick (0.25) = 6000.75.
        assert intent.limit_price == 6000.75
        assert intent.ttl_bars == 5  # production ENTRY_TTL_BARS default, not k_minutes

    def test_entry_fade_side_is_buy_after_a_negative_return(self) -> None:
        strategy = _fast_strategy()
        bars = [build_bar(T0, 6000.50), build_bar(T0 + NS_PER_BAR, 6000.25),
                build_bar(T0 + 2 * NS_PER_BAR, 6000.00)]
        flat = account(position_micros=0, pending_signed_micros=0)
        strategy.on_bar(bars[0], flat)
        strategy.on_bar(bars[1], flat)
        intents = strategy.on_bar(bars[2], flat)

        assert len(intents) == 1
        intent = intents[0]
        assert intent.intent.side == "buy"
        # Buy rests BELOW the close: 6000.00 - 1 tick = 5999.75.
        assert intent.limit_price == 5999.75

    def test_no_new_order_while_an_entry_order_is_already_pending(self) -> None:
        strategy = _fast_strategy()
        bars = [build_bar(T0, 6000.00), build_bar(T0 + NS_PER_BAR, 6000.25),
                build_bar(T0 + 2 * NS_PER_BAR, 6000.50), build_bar(T0 + 3 * NS_PER_BAR, 6001.00)]
        flat = account(position_micros=0, pending_signed_micros=0)
        strategy.on_bar(bars[0], flat)
        strategy.on_bar(bars[1], flat)
        first = strategy.on_bar(bars[2], flat)
        assert len(first) == 1  # entry submitted, now resting

        # Next bar: account reflects the resting entry order (still flat, but pending).
        pending = account(position_micros=0, pending_signed_micros=-1)
        second = strategy.on_bar(bars[3], pending)
        assert second == ()  # never stack a second order while one is pending


class TestHoldAndExit:
    def test_no_exit_before_the_hold_window_elapses(self) -> None:
        strategy = _fast_strategy()  # k_minutes=2
        long_flat_pending = account(position_micros=1, pending_signed_micros=0)
        bar = build_bar(T0, 6000.00)
        # First bar the fill is observed: bars_since_fill goes -1 -> 0, which is < k=2.
        intents = strategy.on_bar(bar, long_flat_pending)
        assert intents == ()

    def test_passive_exit_fires_at_close_plus_minus_one_tick_after_k_minutes_held(self) -> None:
        strategy = _fast_strategy()  # k_minutes=2
        long = account(position_micros=1, pending_signed_micros=0)
        bar0 = build_bar(T0, 6000.00)
        bar1 = build_bar(T0 + NS_PER_BAR, 6001.00)
        strategy.on_bar(bar0, long)  # bars_since_fill: -1 -> 0 (< 2, no exit)
        intents = strategy.on_bar(bar1, long)  # bars_since_fill: 0 -> 1... still < 2

        # k_minutes=2 means the exit begins once bars_since_fill >= 2, i.e. the THIRD
        # bar the position is observed open (indices 0, 1, 2).
        assert intents == ()
        bar2 = build_bar(T0 + 2 * NS_PER_BAR, 6002.00)
        intents = strategy.on_bar(bar2, long)
        assert len(intents) == 1
        intent = intents[0]
        assert isinstance(intent, PassiveIntent)
        assert intent.intent.side == "sell"  # selling a long
        assert intent.intent.quantity_micros == 1
        assert intent.limit_price == 6002.25  # close + 1 tick
        assert intent.ttl_bars == 5  # production EXIT_TTL_BARS default

    def test_short_exit_is_a_buy_at_close_minus_one_tick(self) -> None:
        strategy = _fast_strategy()
        short = account(position_micros=-2, pending_signed_micros=0)
        bar0 = build_bar(T0, 6000.00)
        bar1 = build_bar(T0 + NS_PER_BAR, 6000.00)
        bar2 = build_bar(T0 + 2 * NS_PER_BAR, 5999.00)
        strategy.on_bar(bar0, short)
        strategy.on_bar(bar1, short)
        intents = strategy.on_bar(bar2, short)

        assert len(intents) == 1
        intent = intents[0]
        assert intent.intent.side == "buy"  # covering a short
        assert intent.intent.quantity_micros == 2
        assert intent.limit_price == 5998.75  # close - 1 tick

    def test_no_new_order_while_the_passive_exit_is_pending(self) -> None:
        strategy = _fast_strategy()
        long = account(position_micros=1, pending_signed_micros=0)
        strategy.on_bar(build_bar(T0, 6000.00), long)
        strategy.on_bar(build_bar(T0 + NS_PER_BAR, 6000.00), long)
        placed = strategy.on_bar(build_bar(T0 + 2 * NS_PER_BAR, 6000.00), long)
        assert len(placed) == 1  # the passive exit is now resting

        still_open_pending = account(position_micros=1, pending_signed_micros=-1)
        again = strategy.on_bar(build_bar(T0 + 3 * NS_PER_BAR, 6000.00), still_open_pending)
        assert again == ()  # never stack a second exit order while one is pending

    def test_market_fallback_when_the_passive_exit_expires_unfilled(self) -> None:
        strategy = _fast_strategy()
        long = account(position_micros=1, pending_signed_micros=0)
        strategy.on_bar(build_bar(T0, 6000.00), long)
        strategy.on_bar(build_bar(T0 + NS_PER_BAR, 6000.00), long)
        placed = strategy.on_bar(build_bar(T0 + 2 * NS_PER_BAR, 6000.00), long)
        assert isinstance(placed[0], PassiveIntent)

        # The passive exit has expired: position still open, pending back at 0.
        expired = account(position_micros=1, pending_signed_micros=0)
        fallback = strategy.on_bar(build_bar(T0 + 3 * NS_PER_BAR, 6003.00), expired)
        assert len(fallback) == 1
        market = fallback[0]
        assert not isinstance(market, PassiveIntent)
        assert market.side == "sell"
        assert market.quantity_micros == 1


class TestSessionReset:
    def test_state_resets_on_a_new_trade_date(self) -> None:
        strategy = _fast_strategy()
        long = account(position_micros=1, pending_signed_micros=0)
        strategy.on_bar(build_bar(T0, 6000.00), long)
        strategy.on_bar(build_bar(T0 + NS_PER_BAR, 6000.00), long)
        assert strategy._bars_since_fill[0] == 1  # mid-hold, not yet due to exit

        # A new trade date arrives with the position already flattened by the engine
        # (the harness flattens across session boundaries) and no pending order.
        next_day_ts = int(datetime(2026, 1, 6, 13, 30, tzinfo=UTC).timestamp()) * NS_PER_S
        flat_next_day = account(position_micros=0, pending_signed_micros=0, trade_date=D1)
        strategy.on_bar(build_bar(next_day_ts, 6000.00, trade_date=D1), flat_next_day)

        assert strategy._current_trade_date[0] == D1
        assert strategy._bars_since_fill[0] == -1
        assert strategy._exit_attempted[0] is False
        assert len(strategy._closes) == 1
        assert len(strategy._abs_returns) == 0

    def test_refusal_from_limit_intent_passes_through_without_corrupting_state(self) -> None:
        # band [0, 1] with quantity_micros=0 would be invalid; instead force a refusal by
        # using an out-of-range quantity via direct construction is unnecessary -- the
        # simplest reliable refusal path is a marketable-on-arrival price, which cannot
        # happen through _fade_limit_price's own math. So this test instead confirms that
        # IF a Refusal came back (simulated by monkeypatching the module-level limit_intent
        # target the strategy imported), on_bar still returns it verbatim and does not
        # raise or leave stacked state.
        import strategy.research.c_short_horizon_reversal.h4_passive_fill_reversal as mod

        strategy = _fast_strategy()
        long = account(position_micros=1, pending_signed_micros=0)
        strategy.on_bar(build_bar(T0, 6000.00), long)
        strategy.on_bar(build_bar(T0 + NS_PER_BAR, 6000.00), long)

        original = mod.limit_intent
        mod.limit_intent = lambda *a, **k: Refusal("test_forced_refusal", "forced for test")
        try:
            out = strategy.on_bar(build_bar(T0 + 2 * NS_PER_BAR, 6000.00), long)
        finally:
            mod.limit_intent = original

        assert len(out) == 1
        assert isinstance(out[0], Refusal)
        assert out[0].reason == "test_forced_refusal"
        # exit_attempted was still set True even though the intent was refused, so the
        # NEXT bar (still open, pending back at 0) falls back to a market flatten rather
        # than retrying a passive order forever.
        assert strategy._exit_attempted[0] is True
        fallback = strategy.on_bar(build_bar(T0 + 3 * NS_PER_BAR, 6000.00), long)
        assert len(fallback) == 1
        assert not isinstance(fallback[0], PassiveIntent)
        assert not isinstance(fallback[0], Refusal)
