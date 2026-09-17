"""Known-answer tests for sim/engine.py (Stage C, Task 7).

Every expected number is hand-computed in a comment beside the assert that
checks it; nothing is obtained by running the engine and pasting the result.

Conventions under test (see sim/engine.py, sim/fill_model.py docstrings):
- A strategy's intent on bar N (stamped with bar N's decision time, open+60s)
  fills at the OPEN of bar N+1 (the next bar the engine pulls from the feed).
- Commission = 61 cents/micro/side. Slippage = ceil(qty * slip_ticks * 125)
  cents, slip_ticks = the table's chosen statistic for the FILL bar's open
  time's 15-minute CT bucket, at the smallest calibrated size >= qty.
- 1 tick = 0.25 pt = 125 cents/micro. Gross realized = direction * qty *
  (exit_ticks - entry_ticks) * 125, FIFO across lots.
- Balance changes by (gross - commission - slippage) at EACH fill.

All bars use a synthetic Wednesday, 2026-01-14 (CST = UTC-6), built only
through strategy.interface.construct_bar. Every bar here is FLAT
(open == high == low == close) unless a test needs otherwise, which keeps
every fill's mark-to-market at the fill price itself and stays nowhere near
the XFA MLL floor (-$2,000), so mark-to-market noise never contaminates a
hand-computed P&L number.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from sim import costs as costs_module
from sim.costs import SlippageTable, load_slippage_table
from sim.engine import (
    AccountStartEvent,
    DayCloseEvent,
    EngineConfig,
    FillEvent,
    IntentEvent,
    ledger_to_jsonl,
    reconstruct_balances,
    run_backtest,
)
from strategy.interface import AccountView, Bar, construct_bar, market_intent

CT = ZoneInfo("America/Chicago")
DAY = date(2026, 1, 14)  # synthetic Wednesday
INSTRUMENT = 4242
NS_PER_S = 1_000_000_000


def ct_ns(hour: int, minute: int, day: date = DAY) -> int:
    """CT wall-clock minute on the synthetic day -> UTC ns since epoch."""
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def make_bar(
    hour: int,
    minute: int,
    open_price: float = 6000.00,
    *,
    high: float | None = None,
    low: float | None = None,
    close: float | None = None,
    day: date = DAY,
) -> Bar:
    """A flat (or explicit OHLC) bar, far from the flatten window and the MLL floor."""
    result = construct_bar(
        ts_event_ns=ct_ns(hour, minute, day),
        open=open_price,
        high=open_price if high is None else high,
        low=open_price if low is None else low,
        close=open_price if close is None else close,
        volume=10,
        instrument_id=INSTRUMENT,
        raw_symbol="MESH6",
        trade_date=day,
        in_flatten_window=False,
        in_no_new_positions_window=False,
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


@dataclass(frozen=True)
class ScheduledStrategy:
    """Emits market_intent(bar, side, qty) for each (side, qty) keyed by the bar's
    OWN ts_event_ns (i.e. the bar the strategy is looking at when it decides)."""

    name: str = "scheduled"
    schedule: dict[int, tuple[tuple[str, int], ...]] = field(default_factory=dict)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        orders = self.schedule.get(bar.ts_event_ns, ())
        return tuple(market_intent(bar, side, qty) for side, qty in orders)


CONFIG = EngineConfig(restart_on_terminal=True)


# =========================================================== 1: the prompt's test
def test_known_answer_buy_bar1_sell_bar10() -> None:
    # Arrange: 12 bars, 09:00-09:11 CT. Buy 1 decided on bar index 1 (09:01) fills
    # at bar index 2's open (09:02). Sell 1 decided on bar index 10 (09:10) fills
    # at bar index 11's open (09:11). Both fills' open time falls in the 15-minute
    # CT bucket "09:00" (minute-of-day 542 and 551 both floor to 540 = 09:00).
    bars = [make_bar(9, i) for i in range(12)]
    bars[2] = make_bar(9, 2, 6000.25)  # entry fill price
    bars[11] = make_bar(9, 11, 6003.75)  # exit fill price
    schedule = {
        bars[1].ts_event_ns: (("buy", 1),),
        bars[10].ts_event_ns: (("sell", 1),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={"09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)}},
        windows={},
    )

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    intents = result.events(IntentEvent)
    assert len(intents) == 2
    assert all(e.accepted and e.refusal is None for e in intents)

    fills = result.events(FillEvent)
    assert len(fills) == 2
    entry, exit_ = fills
    assert entry.price == 6000.25
    assert exit_.price == 6003.75
    # entry/exit ticks: 6000.25/0.25 = 24001, 6003.75/0.25 = 24015 -> 14 ticks
    # gross = 1 * 14 * 125 = 1750
    assert exit_.gross_realized_cents == 1750
    # commission = 1 * 61 = 61; slippage = ceil(1 * 0.5 * 125) = ceil(62.5) = 63
    for f in fills:
        assert f.commission_cents == 61
        assert f.slippage_cents == 63
    # final balance = 1750 - 2*(61+63) = 1750 - 248 = 1502
    assert result.final_state.balance_cents == 1502

    day_closes = result.events(DayCloseEvent)
    assert len(day_closes) == 1
    assert day_closes[0].day_net_cents == 1502  # session started at balance 0

    assert reconstruct_balances(result.ledger)[0] == 1502


# =========================================================== 2: size rounds up
def test_known_answer_three_micros_uses_the_size5_row() -> None:
    # Arrange: same schedule as test 1, but qty=3 forces calibrated_size(3, ...) to
    # round UP to the size-5 row (mean 0.52), never the (absent for 3) size-1 or a
    # cheaper row. Slippage scales by the ORDER size: ceil(3 * 0.52 * 125) = ceil(195.0) = 195.
    bars = [make_bar(9, i) for i in range(12)]
    bars[2] = make_bar(9, 2, 6000.25)
    bars[11] = make_bar(9, 11, 6003.75)
    schedule = {
        bars[1].ts_event_ns: (("buy", 3),),
        bars[10].ts_event_ns: (("sell", 3),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={"09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)}},
        windows={},
    )

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 2
    # commission = 3 * 61 = 183; slippage = ceil(3 * 0.52 * 125) = ceil(195.0) = 195
    for f in fills:
        assert f.commission_cents == 183
        assert f.slippage_cents == 195
    # gross = 3 * 14 ticks * 125 = 5250
    assert fills[1].gross_realized_cents == 5250
    # final balance = 5250 - 2*(183+195) = 5250 - 756 = 4494
    assert result.final_state.balance_cents == 4494


# ================================================ 3: fill-bucket, not decision-bucket
def test_known_answer_fill_time_bucket_not_decision_bar_bucket() -> None:
    # Arrange: buy decided on bar index 1 (09:01), fills at bar index 2 (09:02,
    # bucket "09:00"). Sell decided on the bar index 14 (09:14 open, decision
    # 09:15:00 exactly) fills at bar index 15 (09:15 open, bucket "09:15") -- a
    # DIFFERENT 15-minute bucket than the decision bar's own open (09:14, which
    # would floor to bucket "09:00" if the engine wrongly used the decision bar).
    bars = [make_bar(9, i) for i in range(16)]
    bars[2] = make_bar(9, 2, 6000.50)  # entry fill price, bucket "09:00"
    bars[15] = make_bar(9, 15, 6001.00)  # exit fill price, bucket "09:15"
    schedule = {
        bars[1].ts_event_ns: (("buy", 1),),
        bars[14].ts_event_ns: (("sell", 1),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={
            "09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)},
            "09:15": {"1": stat(0.6), "5": stat(0.62), "10": stat(0.7), "50": stat(1.1)},
        },
        windows={},
    )

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 2
    entry, exit_ = fills
    # entry: commission 61; slippage bucket "09:00" size1 mean 0.5 -> ceil(62.5) = 63
    assert entry.commission_cents == 61
    assert entry.slippage_cents == 63
    # exit: commission 61; slippage bucket "09:15" size1 mean 0.6 -> ceil(75.0) = 75
    # (NOT bucket "09:00", which is what the DECISION bar (09:14) would floor to)
    assert exit_.commission_cents == 61
    assert exit_.slippage_cents == 75
    # entry ticks 6000.50/0.25=24002, exit ticks 6001.00/0.25=24004 -> 2 ticks
    # gross = 1 * 2 * 125 = 250
    assert exit_.gross_realized_cents == 250
    # balance after entry = 0 - (61+63) = -124
    # balance after exit = -124 + 250 - (61+75) = -124 + 250 - 136 = -10
    assert result.final_state.balance_cents == -10


# ============================================================== 4: losing short
def test_known_answer_short_round_trip_loses_money_on_a_rally() -> None:
    # Arrange: sell 1 (open a short) decided on bar index 1, fills bar index 2 at
    # 6000.25; buy 1 (cover) decided on bar index 10, fills bar index 11 at
    # 6003.75 -- price rallies, so the short loses.
    bars = [make_bar(9, i) for i in range(12)]
    bars[2] = make_bar(9, 2, 6000.25)
    bars[11] = make_bar(9, 11, 6003.75)
    schedule = {
        bars[1].ts_event_ns: (("sell", 1),),
        bars[10].ts_event_ns: (("buy", 1),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={"09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)}},
        windows={},
    )

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 2
    # short entry lot: qty=-1 @ 24001 ticks; covering buy +1 @ 24015 ticks.
    # direction = -1 (closing lot qty < 0); realized = -1 * 1 * (24015-24001) * 125
    #           = -1 * 14 * 125 = -1750 (a loss)
    assert fills[1].gross_realized_cents == -1750
    # commission 61, slippage 63 per side (same "09:00" bucket, size 1, as tests 1-2)
    for f in fills:
        assert f.commission_cents == 61
        assert f.slippage_cents == 63
    # final balance = -1750 - 2*(61+63) = -1750 - 248 = -1998
    assert result.final_state.balance_cents == -1998


# ================================================================== 5: FIFO
def test_known_answer_fifo_across_two_entry_lots() -> None:
    # Arrange: buy 2 @ A (bar index1 decision -> fills bar index2), buy 1 @ B
    # (bar index2 decision -> fills bar index3), sell 3 @ C (bar index10
    # decision -> fills bar index11). A=6000.00 (ticks 24000), B=6000.50
    # (ticks 24002), C=6002.00 (ticks 24008).
    bars = [make_bar(9, i) for i in range(12)]
    bars[2] = make_bar(9, 2, 6000.00)  # A
    bars[3] = make_bar(9, 3, 6000.50)  # B
    bars[11] = make_bar(9, 11, 6002.00)  # C
    schedule = {
        bars[1].ts_event_ns: (("buy", 2),),
        bars[2].ts_event_ns: (("buy", 1),),
        bars[10].ts_event_ns: (("sell", 3),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={"09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)}},
        windows={},
    )

    # Act
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 3
    fill_a, fill_b, fill_c = fills
    assert fill_a.qty == 2 and fill_a.gross_realized_cents == 0
    assert fill_b.qty == 1 and fill_b.gross_realized_cents == 0
    # FIFO: 2 @ A closed first, then 1 @ B.
    # gross = 2*(C-A)_ticks*125 + 1*(C-B)_ticks*125
    #       = 2*(24008-24000)*125 + 1*(24008-24002)*125
    #       = 2*8*125 + 1*6*125 = 2000 + 750 = 2750
    assert fill_c.qty == 3 and fill_c.gross_realized_cents == 2750

    # costs: qty 2 and qty 3 round up to the size-5 row (mean 0.52); qty 1 uses
    # the size-1 row (mean 0.5).
    # fill_a: commission 2*61=122; slippage ceil(2*0.52*125)=ceil(130.0)=130
    assert fill_a.commission_cents == 122
    assert fill_a.slippage_cents == 130
    # fill_b: commission 1*61=61; slippage ceil(1*0.5*125)=ceil(62.5)=63
    assert fill_b.commission_cents == 61
    assert fill_b.slippage_cents == 63
    # fill_c: commission 3*61=183; slippage ceil(3*0.52*125)=ceil(195.0)=195
    assert fill_c.commission_cents == 183
    assert fill_c.slippage_cents == 195

    # final balance = (0-252) + (0-124) + (2750-378) = -252-124+2372 = 1996
    assert result.final_state.balance_cents == 1996


# ======================================================= 6: real calibration
def test_known_answer_against_real_slippage_calibration() -> None:
    # Arrange: repeat the buy-then-sell mechanics of test 1 with the REAL
    # calibration table, at 08:40 CT so the fills land in the real "08:30"
    # bucket. Buy decided on bar 0 (08:40) fills bar 1 (08:41, open=6001.00);
    # sell decided on bar 1 (08:41, right after its own fill) fills bar 2
    # (08:42, open=6002.00). Both fill minutes (41, 42) floor to bucket "08:30".
    bar0 = make_bar(8, 40, 6000.00)
    bar1 = make_bar(8, 41, 6001.00)
    bar2 = make_bar(8, 42, 6002.00)
    schedule = {
        bar0.ts_event_ns: (("buy", 1),),
        bar1.ts_event_ns: (("sell", 1),),
    }
    table = load_slippage_table()

    raw = json.loads(costs_module.CALIBRATION_PATH.read_text())
    mean_1 = raw["buckets_ct"]["08:30"]["1"]["mean"]
    # sim.fill_model.slippage_cents: ceil(round(qty * mean * 125, 6)). On the 2026-09-16
    # calibration mean_1 = 0.5408 -> ceil(67.6) = 68 cents per side; final balance 242 cents.
    expected_slippage_cents = math.ceil(round(1 * mean_1 * 125, 6))

    # Act
    result = run_backtest([bar0, bar1, bar2], ScheduledStrategy(schedule=schedule), CONFIG, table)

    # Assert
    fills = result.events(FillEvent)
    assert len(fills) == 2
    for f in fills:
        assert f.commission_cents == 61
        assert f.slippage_cents == expected_slippage_cents
    # entry 6001.00 -> ticks 24004; exit 6002.00 -> ticks 24008 -> 4 ticks
    # gross = 1 * 4 * 125 = 500
    assert fills[1].gross_realized_cents == 500
    # final balance = 500 - 2*(61 + expected_slippage_cents)
    expected_balance = 500 - 2 * (61 + expected_slippage_cents)
    assert result.final_state.balance_cents == expected_balance


# ==================================================== 7: ledger_to_jsonl
def test_ledger_to_jsonl_writes_one_event_per_line(tmp_path) -> None:
    # Arrange: reuse test 1's tiny backtest to get a non-trivial ledger.
    bars = [make_bar(9, i) for i in range(12)]
    bars[2] = make_bar(9, 2, 6000.25)
    bars[11] = make_bar(9, 11, 6003.75)
    schedule = {
        bars[1].ts_event_ns: (("buy", 1),),
        bars[10].ts_event_ns: (("sell", 1),),
    }
    table = SlippageTable(
        sizes_micros=(1, 5, 10, 50),
        bucket_minutes=15,
        buckets={"09:00": {"1": stat(0.5), "5": stat(0.52), "10": stat(0.6), "50": stat(1.0)}},
        windows={},
    )
    result = run_backtest(bars, ScheduledStrategy(schedule=schedule), CONFIG, table)
    path = tmp_path / "ledger.jsonl"

    # Act
    ledger_to_jsonl(result.ledger, path)

    # Assert
    lines = path.read_text().splitlines()
    assert len(lines) == len(result.ledger)
    expected_types = [type(e).__name__ for e in result.ledger]
    for line, expected_type, event in zip(lines, expected_types, result.ledger, strict=True):
        row = json.loads(line)
        assert row["event"] == expected_type
        if isinstance(event, AccountStartEvent):
            assert row["balance_cents"] == event.balance_cents
