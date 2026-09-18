"""Known-answer tests for passive (resting limit) orders (Stage D.1a, Task 2).

Rule under test (``sim/fill_model.py``, ``passive_fill_ticks``): a resting limit
fills only when a LATER bar trades at least one tick THROUGH its price, and then at
exactly the limit price, commission only (61 cents per micro per side, no slippage).
No adverse-selection price penalty is applied (the trade-through rule is the model).
A bar that merely touches the limit does not fill it.

Every expected number is hand-computed in a comment beside its assert. Synthetic
Wednesday 2026-01-14 (CST = UTC-6). 1 tick = 0.25 pt = 125 cents per micro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from rules.xfa_rules import Refusal
from sim.costs import SlippageTable
from sim.engine import (
    NO_ROLL_BLACKOUT,
    CancelEvent,
    EngineConfig,
    FillEvent,
    IntentEvent,
    reconstruct_balances,
    run_backtest,
)
from sim.fill_model import PASSIVE_FILL_CAVEATS, passive_fill_ticks, passive_side_cost
from strategy.interface import (
    AccountView,
    Bar,
    PassiveIntent,
    construct_bar,
    limit_intent,
    market_intent,
)

CT = ZoneInfo("America/Chicago")
D0 = date(2026, 1, 14)
NS_PER_S = 1_000_000_000
CONFIG = EngineConfig(restart_on_terminal=False, roll_blackout=NO_ROLL_BLACKOUT)


def ct_ns(hour: int, minute: int, day: date = D0) -> int:
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def make_bar(hour: int, minute: int, open_price: float = 6001.00, *, high: float | None = None,
             low: float | None = None, close: float | None = None, day: date = D0) -> Bar:
    """Flags follow the Topstep clock: no new positions from 15:08 CT, flatten from 15:10."""
    in_no_new = (15, 8) <= (hour, minute) < (17, 0)
    in_flatten = (15, 10) <= (hour, minute) < (17, 0)
    built = construct_bar(
        ts_event_ns=ct_ns(hour, minute, day), open=open_price,
        high=open_price if high is None else high, low=open_price if low is None else low,
        close=open_price if close is None else close, volume=10, instrument_id=4242,
        raw_symbol="MESH6", trade_date=day, in_flatten_window=in_flatten,
        in_no_new_positions_window=in_no_new, early_halt_ct=None, in_scheduled_closure=False,
        is_roll_session=False, gap_before_minutes=0, vendor_degraded_day=False,
    )
    assert isinstance(built, Bar), built
    return built


def stat(mean: float) -> dict[str, float | int]:
    return {"mean": mean, "p50": mean, "p90": mean, "p99": mean, "insufficient_depth": 0}


# Market-order slippage 0.5 ticks for 1 micro in every bucket used here.
TABLE = SlippageTable(
    sizes_micros=(1, 5, 10, 50), bucket_minutes=15,
    buckets={k: {"1": stat(0.5), "5": stat(0.5), "10": stat(0.5), "50": stat(1.0)}
             for k in ("09:00", "15:00")},
    windows={},
)


@dataclass(frozen=True)
class Scripted:
    """Returns a fixed tuple of orders keyed by the decision bar's ts_event_ns. Each entry is
    ("market", side, qty) or ("limit", side, qty, price, ttl)."""

    name: str = "scripted"
    script: dict[int, tuple[tuple, ...]] = field(default_factory=dict)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        out = []
        for spec in self.script.get(bar.ts_event_ns, ()):
            if spec[0] == "market":
                out.append(market_intent(bar, spec[1], spec[2]))
            else:
                out.append(limit_intent(bar, spec[1], spec[2], spec[3], spec[4]))
        return tuple(out)


# ----------------------------------------------------------- pure fill rule ----
def test_buy_limit_fills_only_on_a_trade_through_by_one_tick() -> None:
    # Limit 6000.00 = 24000 ticks.
    assert passive_fill_ticks(1, 24000, 23999, 24010) == 24000  # low 5999.75: through -> 24000
    assert passive_fill_ticks(1, 24000, 23990, 24010) == 24000  # far through: still the limit
    assert passive_fill_ticks(1, 24000, 24000, 24010) is None  # low == limit: touch only
    assert passive_fill_ticks(1, 24000, 24001, 24010) is None  # never reached


def test_sell_limit_is_the_mirror_image() -> None:
    assert passive_fill_ticks(-2, 24008, 23990, 24009) == 24008  # high one tick through
    assert passive_fill_ticks(-2, 24008, 23990, 24008) is None  # touch only
    with pytest.raises(ValueError):
        passive_fill_ticks(0, 24000, 23990, 24010)


def test_passive_cost_is_commission_only() -> None:
    cost = passive_side_cost(3)
    # 3 micros x 61 cents = 183 cents; no spread crossed, so slippage 0.
    assert (cost.commission_cents, cost.slippage_cents, cost.total_cents) == (183, 0, 183)
    assert cost.statistic == "passive"
    with pytest.raises(ValueError):
        passive_side_cost(0)


def test_caveats_name_queue_position_and_market_impact() -> None:
    text = " ".join(PASSIVE_FILL_CAVEATS)
    assert "queue position is NOT modelled" in text
    assert "effect on the market's subsequent path is NOT modelled" in text


# ------------------------------------------------------ engine: known answers ----
def test_limit_fills_on_trade_through_to_the_cent() -> None:
    # 09:00-09:08, flat at 6001.00 except where stated.
    bars = [make_bar(9, m) for m in range(9)]
    # 09:02 only TOUCHES 6000.00 -> no fill.
    bars[2] = make_bar(9, 2, 6001.00, low=6000.00, close=6000.50)
    # 09:03 trades THROUGH (low 5999.75) -> buy limit fills at exactly 6000.00.
    bars[3] = make_bar(9, 3, 6000.50, low=5999.75, close=6000.25)
    bars[6] = make_bar(9, 6, 6002.00)  # market exit fill price
    script = {
        bars[1].ts_event_ns: (("limit", "buy", 1, 6000.00, 10),),  # decision close 6001.00
        bars[5].ts_event_ns: (("market", "sell", 1),),
    }

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    fills = result.events(FillEvent)
    assert len(fills) == 2
    entry, exit_ = fills
    assert entry.order_type == "passive" and entry.fill_ts_ns == bars[3].ts_event_ns
    assert entry.price == 6000.00  # the limit, not the 09:03 open (6000.50) nor its low
    assert (entry.commission_cents, entry.slippage_cents) == (61, 0)
    assert entry.minutes_after_decision == 1  # decision 09:02:00, fill bar opens 09:03
    assert exit_.order_type == "market" and exit_.price == 6002.00
    # Exit: commission 61; slippage ceil(1 x 0.5 x 125) = 63.
    assert (exit_.commission_cents, exit_.slippage_cents) == (61, 63)
    # Gross: (6002.00 - 6000.00) / 0.25 = 8 ticks x 125 = 1,000 cents.
    assert exit_.gross_realized_cents == 1_000
    # Net: 1,000 - 61 - 61 - 63 = 815 cents.
    assert result.final_state.balance_cents == 815
    assert reconstruct_balances(result.ledger) == {0: 815}
    intent = result.events(IntentEvent)[0]
    assert intent.accepted and intent.limit_price == 6000.00


def test_limit_never_reached_does_not_fill_and_expires() -> None:
    # Lows never below 6000.25; the 6000.00 buy limit can never trade through.
    bars = [make_bar(9, m, 6001.00, low=6000.25) for m in range(10)]
    script = {bars[1].ts_event_ns: (("limit", "buy", 1, 6000.00, 5),)}

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    assert result.events(FillEvent) == ()
    cancels = result.events(CancelEvent)
    # Decision time 09:02:00 + 5 min = 09:07:00: the 09:07 bar cancels it.
    assert [(c.reason, c.ts_ns) for c in cancels] == [("passive_expired", bars[7].ts_event_ns)]
    assert result.final_state.balance_cents == 0


def test_sell_limit_entry_and_passive_exit_to_the_cent() -> None:
    bars = [make_bar(9, m) for m in range(8)]
    bars[2] = make_bar(9, 2, 6001.00, high=6002.25, close=6001.50)  # through 6002.00 -> short
    bars[5] = make_bar(9, 5, 6000.50, low=5999.75, close=6000.00)  # through 6000.00 -> cover
    script = {
        bars[1].ts_event_ns: (("limit", "sell", 2, 6002.00, 30),),
        bars[3].ts_event_ns: (("limit", "buy", 2, 6000.00, 30),),  # decision close 6001.00
    }

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    fills = result.events(FillEvent)
    assert [(f.side, f.price, f.order_type) for f in fills] == [
        ("sell", 6002.00, "passive"), ("buy", 6000.00, "passive")]
    # Gross: 2 micros x 8 ticks x 125 = 2,000 cents. Costs: 2 sides x 2 x 61 = 244.
    assert fills[1].gross_realized_cents == 2_000
    assert result.final_state.balance_cents == 2_000 - 244  # 1,756


def test_decision_bar_range_can_never_fill_its_own_order() -> None:
    # The decision bar trades far through the limit: information the order could not have
    # rested for. Later bars never come near it.
    bars = [make_bar(9, m) for m in range(6)]
    bars[1] = make_bar(9, 1, 6001.00, low=5990.00, close=6001.00)
    script = {bars[1].ts_event_ns: (("limit", "buy", 1, 6000.00, 30),)}

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    assert result.events(FillEvent) == ()


def test_marketable_limit_is_refused_by_constructor_and_engine() -> None:
    bar = make_bar(9, 1, 6001.00)
    refused = limit_intent(bar, "buy", 1, 6001.00, 5)  # at the close: would not rest
    assert isinstance(refused, Refusal) and refused.reason == "limit_marketable_on_arrival"
    assert isinstance(limit_intent(bar, "sell", 1, 6000.75, 5), Refusal)
    assert limit_intent(bar, "buy", 1, 6000.10, 5).reason == "limit_off_tick"
    assert limit_intent(bar, "buy", 1, 6000.00, 0).reason == "limit_bad_ttl"

    # A hand-built PassiveIntent that skips limit_intent is re-checked by the engine.
    smuggled = PassiveIntent(market_intent(bar, "buy", 1), 6002.00, 5)

    @dataclass(frozen=True)
    class Smuggler:
        name: str = "smuggler"

        def on_bar(self, b: Bar, account: AccountView) -> tuple:
            return (smuggled,) if b.ts_event_ns == bar.ts_event_ns else ()

    bars = [make_bar(9, 0), bar, make_bar(9, 2, 6003.00)]
    result = run_backtest(bars, Smuggler(), CONFIG, TABLE)
    event = result.events(IntentEvent)[0]
    assert not event.accepted and event.refusal.reason == "engine_malformed_passive"
    assert result.events(FillEvent) == ()


def test_resting_entry_is_cancelled_once_no_new_positions_window_opens() -> None:
    # Buy limit placed at 15:00 (ttl 30). The first trade-through is on the 15:08 bar,
    # inside the no-new-positions window: the order is cancelled, never filled.
    bars = [make_bar(15, m) for m in range(10)]
    bars[8] = make_bar(15, 8, 6000.50, low=5999.00, close=6000.00)
    script = {bars[0].ts_event_ns: (("limit", "buy", 1, 6000.00, 30),)}

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    assert result.events(FillEvent) == ()
    assert [c.reason for c in result.events(CancelEvent)] == ["passive_no_new_positions_window"]


def test_resting_exit_still_fills_inside_no_new_positions_window() -> None:
    # Long 1 from a 15:01 market fill at 6001.00; a sell limit exit at 6002.00 fills on the
    # 15:08 bar (high 6002.25): reducing orders are not blocked by the window.
    bars = [make_bar(15, m) for m in range(10)]
    bars[8] = make_bar(15, 8, 6001.50, high=6002.25, close=6002.00)
    script = {bars[0].ts_event_ns: (("market", "buy", 1),),
              bars[2].ts_event_ns: (("limit", "sell", 1, 6002.00, 30),)}

    result = run_backtest(bars, Scripted(script=script), CONFIG, TABLE)

    fills = result.events(FillEvent)
    assert [(f.side, f.price, f.order_type) for f in fills] == [
        ("buy", 6001.00, "market"), ("sell", 6002.00, "passive")]
    # Gross 4 ticks x 125 = 500; costs 61 + 63 (market entry) + 61 (passive exit) = 185.
    assert result.final_state.balance_cents == 500 - 185  # 315


def test_roll_blackout_refuses_a_passive_entry() -> None:
    bars = [make_bar(9, m) for m in range(4)]
    config = EngineConfig(restart_on_terminal=False, roll_blackout=frozenset({D0}))
    script = {bars[1].ts_event_ns: (("limit", "buy", 1, 6000.00, 5),)}

    result = run_backtest(bars, Scripted(script=script), config, TABLE)

    event = result.events(IntentEvent)[0]
    assert not event.accepted and event.refusal.reason == "engine_roll_blackout"


def test_engine_config_requires_an_explicit_roll_blackout() -> None:
    with pytest.raises(TypeError):
        EngineConfig(restart_on_terminal=True)  # type: ignore[call-arg]
