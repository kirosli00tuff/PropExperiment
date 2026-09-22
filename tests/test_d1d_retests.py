"""Known-answer tests for the Stage D.1d re-tests RT1-RT7.

Everything here is pinned against section 2 of the declaration
(``reports/stage_d1d_timeframe_declaration.md``), never against the implementation's
own output. Each expected time and price is arithmetic a reader can redo by hand from
the 5-minute grid of rule R3 (RTH slot ``j`` is 08:30 CT + 5j minutes, so slot 0 is
08:30-08:34 and the last RTH slot, 77, is 14:55-14:59 CT).

What is pinned, by re-test:

- **RT1-RT4 (``OrbRetest``)**: the opening range is RTH slots 0-5 (08:30-09:00 CT); the
  trigger is a 5-minute CLOSE at least 4 ticks (1.00 point) through it; the entry is
  emitted on the 1-minute bar that COMPLETES the breakout slot (rule R6), so a break on
  the 09:05-09:09 slot is decided at 09:10 CT; the hold is counted in 5-minute bars; a
  3-tick break does not trigger; only the session's first break enters; the last RTH
  slot never enters; and a hold that would run past the RTH segment end exits on the
  last RTH slot instead. The fade leg mirrors the breakout leg's side.
- **RT5 (``SpikeFadeRetest``)**: the baseline is the trade date's own previous 20 coarse
  bars (population std), the fade is against the spike bar's direction, the hold is one
  coarse bar, ``close == open`` is no trade, fewer than 20 baseline bars is no trade,
  and a spike on the last RTH slot has no bar left to hold through.
- **RT6/RT7 (``DailyVolEstimator``)**: ``V_d`` is the root of an EWMA (lambda 0.94) over
  trade dates of the mean squared 5-minute close-to-close log return, seeded with the
  first date's mean and using dates strictly before ``d``.
- **RT7 (``DailyVolSizingRetest``)**: the declared inverse-vol size, clipped to [1, 5].
- **RT6 (``DailyVolRegimeGateRetest``)**: the low-tercile gate over a hand-built history
  of 30 ``V`` values, the fixed 1-minute base entry at bar index 60, and its 30-bar hold.

Style follows ``tests/test_c_h4_passive_reversal.py`` (``on_bar`` driven directly with
hand-built ``Bar``/``AccountView`` objects) and ``tests/test_drift_benchmark.py``
(synthetic frames through ``sim.engine``). ``drive`` applies the engine's own timing
contract -- a market order decided on bar N fills at bar N+1's open -- and one test runs
the real engine over the same synthetic frame to prove that the two agree on the fill
minute and price.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from rules.xfa_rules import MES_TICK_SIZE, OrderIntent, Phase, Refusal, Status
from sim.costs import load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    NO_ROLL_BLACKOUT,
    EngineConfig,
    FillEvent,
    iter_bars,
    run_backtest,
)
from strategy.interface import AccountView, Bar
from strategy.research.g_timeframe.resample import slot_count
from strategy.research.g_timeframe.retests import (
    BASELINE_BARS,
    EWMA_LAMBDA,
    MAX_QUANTITY_MICROS,
    MIN_BREAK_TICKS,
    MIN_HISTORY_DAYS,
    MIN_QUANTITY_MICROS,
    OR_SLOTS,
    RETEST_TF,
    TARGET_RISK_USD,
    TERCILE_LOW_MAX,
    DailyVolEstimator,
    DailyVolRegimeGateRetest,
    DailyVolSizingRetest,
    OrbRetest,
    SpikeFadeRetest,
)

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
INSTRUMENT_ID = 4242
DEFAULT_VOLUME = 10

# Three consecutive normal trade dates: no early close, no DST transition, no roll.
D1 = date(2026, 4, 14)
D2 = date(2026, 4, 15)
D3 = date(2026, 4, 16)

RTH_OPEN_CT = (8, 30)
RTH_SLOTS_5MIN = 78  # (15:00 - 08:30) / 5, the declaration's R3 count
LAST_RTH_SLOT = RTH_SLOTS_5MIN - 1  # slot 77 = 14:55-14:59 CT

# The opening range every ORB day below carries: exactly [6000.00, 6002.00].
ORB_BASE = 6001.00
OR_LOW = 6000.00
OR_HIGH = 6002.00
BREAK_BUFFER = MIN_BREAK_TICKS * MES_TICK_SIZE  # 4 ticks = 1.00 point


# ------------------------------------------------------------------ synthetic bars ----
def ct_minute(day: date, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CT)


def ct_hm(bar: Bar) -> tuple[int, int]:
    """(hour, minute) CT of the bar's OPEN."""
    local = bar.open_ts_utc.astimezone(CT)
    return local.hour, local.minute


def minute_row(trade_date: date, open_ct: datetime, price: float, volume: int) -> dict:
    """One 1-minute bar row with open = high = low = close = ``price``."""
    return {
        "ts_event": int(open_ct.astimezone(UTC).timestamp()) * NS_PER_S,
        "open": price, "high": price, "low": price, "close": price, "volume": volume,
        "instrument_id": INSTRUMENT_ID, "raw_symbol": "MESM6",
        "trade_date": trade_date.isoformat(), "in_flatten_window": False,
        "in_no_new_positions_window": False, "early_halt_ct": "",
        "in_scheduled_closure": False, "is_roll_session": False,
        "gap_before_minutes": 0, "vendor_degraded_day": False,
    }


def minute_frame(trade_date: date, first_ct: datetime, prices: Sequence[float],
                 volumes: Sequence[int] | None = None) -> pd.DataFrame:
    """One bar per minute from ``first_ct``, in order, no gaps."""
    vols = [DEFAULT_VOLUME] * len(prices) if volumes is None else list(volumes)
    rows = [minute_row(trade_date, first_ct + timedelta(minutes=i), price, volume)
            for i, (price, volume) in enumerate(zip(prices, vols, strict=True))]
    return pd.DataFrame(rows, columns=list(BAR_COLUMNS))


def minute_bars(trade_date: date, first_ct: datetime, prices: Sequence[float],
                volumes: Sequence[int] | None = None) -> tuple[Bar, ...]:
    return tuple(iter_bars(minute_frame(trade_date, first_ct, prices, volumes)))


def account_view(trade_date: date, position_micros: int = 0,
                 pending_signed_micros: int = 0) -> AccountView:
    return AccountView(
        phase=Phase.XFA, status=Status.ACTIVE, trade_date=trade_date, balance_cents=0,
        mll_floor_cents=-200_000, prior_session_balance_cents=0, max_position_micros=20,
        position_micros=position_micros, pending_signed_micros=pending_signed_micros,
        avg_entry_price=None, unrealized_at_close_cents=0,
    )


def drive(strategy, bars: Iterable[Bar]) -> list[tuple[Bar, OrderIntent]]:
    """``on_bar`` over ``bars`` under the engine's timing contract: a market order decided
    on bar N is filled at bar N+1's open, so the position the strategy sees changes only
    from the next bar on. Returns every (decision bar, intent) pair, in order."""
    events: list[tuple[Bar, OrderIntent]] = []
    position = 0
    filling = 0
    for bar in bars:
        position += filling
        filling = 0
        intents = strategy.on_bar(bar, account_view(bar.trade_date, position))
        for intent in intents:
            assert not isinstance(intent, Refusal), intent
            assert isinstance(intent, OrderIntent), intent
            # Timing contract 2: an intent is stamped with its bar's decision time.
            assert intent.ts_utc == bar.decision_ts_utc
            filling += intent.signed_quantity
            events.append((bar, intent))
    return events


def signals(events: Sequence[tuple[Bar, OrderIntent]]) -> list[tuple[tuple[int, int], str, int]]:
    """((hour, minute) CT of the decision bar's open, side, micros) per emitted order."""
    return [(ct_hm(bar), intent.side, intent.quantity_micros) for bar, intent in events]


# --------------------------------------------------------------- RT1-RT4 ORB days ----
def slot_completion_ct(slot: int) -> tuple[int, int]:
    """(hour, minute) CT of the 1-minute bar that completes RTH 5-minute ``slot`` (R6):
    the slot's last minute, 08:30 + 5*slot + 4."""
    return divmod(8 * 60 + 30 + slot * RETEST_TF + (RETEST_TF - 1), 60)


def orb_prices(slot_closes: Mapping[int, float]) -> list[float]:
    """A whole RTH session of 1-minute prices: flat at 6001.00 except the two minutes that
    make the opening range exactly [6000.00, 6002.00], and the last minute of each slot in
    ``slot_closes``, which sets that 5-minute bar's close."""
    prices = [ORB_BASE] * (RTH_SLOTS_5MIN * RETEST_TF)
    prices[1] = OR_LOW   # 08:31 CT
    prices[2] = OR_HIGH  # 08:32 CT
    for slot, close in slot_closes.items():
        prices[slot * RETEST_TF + (RETEST_TF - 1)] = close
    return prices


def orb_frame(slot_closes: Mapping[int, float], *, trade_date: date = D1,
              minute_prices: Mapping[int, float] | None = None) -> pd.DataFrame:
    prices = orb_prices(slot_closes)
    for index, price in (minute_prices or {}).items():
        prices[index] = price
    return minute_frame(trade_date, ct_minute(trade_date, *RTH_OPEN_CT), prices)


def orb_bars(slot_closes: Mapping[int, float], *, trade_date: date = D1) -> tuple[Bar, ...]:
    return tuple(iter_bars(orb_frame(slot_closes, trade_date=trade_date)))


def test_the_synthetic_orb_day_matches_the_declared_five_minute_rth_grid() -> None:
    # The arithmetic every ORB expectation below rests on, stated once.
    assert slot_count("RTH", RETEST_TF, 1328) == RTH_SLOTS_5MIN
    assert OR_SLOTS == 6 and slot_completion_ct(OR_SLOTS - 1) == (8, 59)  # OR is 08:30-09:00
    assert slot_completion_ct(6) == (9, 4)
    assert slot_completion_ct(7) == (9, 9)
    assert slot_completion_ct(8) == (9, 14)
    assert slot_completion_ct(LAST_RTH_SLOT) == (14, 59)
    assert BREAK_BUFFER == 1.00


# ============================================================ RT1/RT3 breakout leg ====
class TestOrbBreakoutLeg:
    def test_a_close_five_ticks_above_the_opening_range_buys_on_the_bar_that_completes_it(
        self,
    ) -> None:
        # Arrange: OR = [6000.00, 6002.00]; slot 7 (09:05-09:09 CT) closes at 6003.25,
        # which is >= OR high + 4 ticks (6003.00). Nothing before it breaks.
        bars = orb_bars({7: 6003.25})
        strategy = OrbRetest(hold_bars=1, leg="breakout")

        # Act
        events = drive(strategy, bars)

        # Assert: entry on the 09:09 bar, exit one 5-minute bar later, on the 09:14 bar.
        assert signals(events) == [((9, 9), "buy", 1), ((9, 14), "sell", 1)]

    def test_the_entry_is_decided_at_0910_ct_the_minute_after_the_breakout_bar_closes(
        self,
    ) -> None:
        # Arrange
        bars = orb_bars({7: 6003.25})

        # Act
        entry_bar, entry = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)[0]

        # Assert: rule R6 -- the coarse bar completes at the decision time of the 1-minute
        # bar opening in its last minute, which is 09:09 + 60s = 09:10 CT.
        assert entry.ts_utc == entry_bar.decision_ts_utc
        assert entry.ts_utc.astimezone(CT) == ct_minute(D1, 9, 10)

    def test_a_close_five_ticks_below_the_opening_range_sells_and_buys_back(self) -> None:
        # Arrange: 5998.75 <= OR low - 4 ticks (5999.00).
        bars = orb_bars({7: 5998.75})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert
        assert signals(events) == [((9, 9), "sell", 1), ((9, 14), "buy", 1)]

    def test_a_close_three_ticks_past_the_opening_range_never_triggers(self) -> None:
        # Arrange: 6002.75 is 3 ticks above the OR high, one tick short of the buffer.
        bars = orb_bars({7: 6002.75})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert: nothing, all session.
        assert signals(events) == []

    def test_a_close_exactly_four_ticks_past_the_opening_range_triggers(self) -> None:
        # Arrange: 6003.00 == OR high + 4 ticks; the trigger is ">=", not ">".
        bars = orb_bars({7: 6003.00})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert
        assert signals(events) == [((9, 9), "buy", 1), ((9, 14), "sell", 1)]

    def test_only_the_first_break_of_the_session_enters(self) -> None:
        # Arrange: a second, larger break on slot 20 (10:10-10:14 CT), long after the
        # first trade has been closed.
        bars = orb_bars({7: 6003.25, 20: 6004.00})
        assert slot_completion_ct(20) == (10, 14)

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert: one entry per session (declaration section 2).
        assert signals(events) == [((9, 9), "buy", 1), ((9, 14), "sell", 1)]

    def test_a_break_on_the_last_rth_slot_never_enters(self) -> None:
        # Arrange: the day's only break closes slot 77 (14:55-14:59 CT). There is no
        # further RTH slot to hold through, so the hold could not complete.
        bars = orb_bars({LAST_RTH_SLOT: 6003.25})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert
        assert signals(events) == []

    def test_the_first_slot_after_the_opening_range_can_trigger(self) -> None:
        # Arrange: slot 6 (09:00-09:04 CT) is the earliest slot the declaration allows to
        # trade ("the first RTH 5-min bar at slot >= 6").
        bars = orb_bars({6: 6003.25})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert
        assert signals(events) == [((9, 4), "buy", 1), ((9, 9), "sell", 1)]

    def test_a_break_inside_the_opening_range_slots_is_not_a_trigger(self) -> None:
        # Arrange: slot 3 (08:45-08:49 CT) closes far above the range being built. Slots
        # 0-5 only WIDEN the opening range; they never trade.
        bars = orb_bars({3: 6010.00})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="breakout"), bars)

        # Assert: the OR high is now 6010.00, so the flat 6001.00 rest of the day cannot
        # break it either.
        assert signals(events) == []


# ==================================================================== RT4 fade leg ====
class TestOrbFadeLeg:
    def test_the_fade_leg_sells_an_upside_break(self) -> None:
        # Arrange: the same upside break RT1 buys.
        bars = orb_bars({7: 6003.25})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="fade"), bars)

        # Assert: entry against the break direction, exit one 5-minute bar later.
        assert signals(events) == [((9, 9), "sell", 1), ((9, 14), "buy", 1)]

    def test_the_fade_leg_buys_a_downside_break(self) -> None:
        # Arrange
        bars = orb_bars({7: 5998.75})

        # Act
        events = drive(OrbRetest(hold_bars=1, leg="fade"), bars)

        # Assert
        assert signals(events) == [((9, 9), "buy", 1), ((9, 14), "sell", 1)]


# ============================================================== RT2 the 15-bar hold ====
class TestOrbFifteenBarHold:
    def test_the_exit_is_fifteen_five_minute_bars_after_the_entry(self) -> None:
        # Arrange: a break on slot 40 (11:50-11:54 CT), with 37 RTH slots left.
        bars = orb_bars({40: 6003.25})
        assert slot_completion_ct(40) == (11, 54)
        assert slot_completion_ct(40 + 15) == (13, 9)  # bar+15 = 75 minutes later

        # Act
        events = drive(OrbRetest(hold_bars=15, leg="breakout"), bars)

        # Assert
        assert signals(events) == [((11, 54), "buy", 1), ((13, 9), "sell", 1)]

    def test_an_entry_late_in_the_session_exits_on_the_last_rth_slot(self) -> None:
        # Arrange: a break on slot 70 (14:20-14:24 CT). Only 7 RTH slots remain, fewer
        # than the 15-bar hold, so "exiting earlier only if the RTH segment ends first"
        # applies (declaration RT2).
        bars = orb_bars({70: 6003.25})
        assert slot_completion_ct(70) == (14, 24)

        # Act
        events = drive(OrbRetest(hold_bars=15, leg="breakout"), bars)

        # Assert: the exit fires on the completion of slot 77, the last RTH slot.
        assert signals(events) == [((14, 24), "buy", 1), ((14, 59), "sell", 1)]


# ================================================= RT1 through the real engine ========
class TestOrbThroughTheEngine:
    def test_the_breakout_entry_and_exit_fill_at_the_next_one_minute_open(self) -> None:
        # Arrange: the RT1 day, with distinctive opens on the two minutes the fills must
        # land on -- 09:10 CT (index 40) and 09:15 CT (index 45).
        frame = orb_frame({7: 6003.25}, minute_prices={40: 6005.00, 45: 6007.00})
        config = EngineConfig(restart_on_terminal=True, roll_blackout=NO_ROLL_BLACKOUT)

        # Act
        result = run_backtest(iter_bars(frame), OrbRetest(hold_bars=1, leg="breakout"),
                              config, load_slippage_table())

        # Assert: exactly one round trip, both legs filled at the NEXT bar's open.
        fills = result.events(FillEvent)
        assert [(f.side, f.qty, f.price, f.reason) for f in fills] == [
            ("buy", 1, 6005.00, "strategy"), ("sell", 1, 6007.00, "strategy")]
        assert [f.minutes_after_decision for f in fills] == [0, 0]
        assert result.final_position.qty == 0


# ========================================================== RT5 post-spike fade ========
SPIKE_BASE = 6000.00
SPIKE_SLOT_RANGE = 1.00  # every coarse bar below spans exactly 1.00 point
BASELINE_VOLUMES = (100, 102)  # alternating: mean 101, population std exactly 1.0
SPIKE_VOLUME = 200  # z = (200 - 101) / 1.0 = 99 > 3.0
SPIKE_UP_CLOSE = SPIKE_BASE + 0.50


def slot_prices(close: float) -> list[float]:
    """Five 1-minute prices whose 5-minute aggregate opens at 6000.00, highs at 6001.00,
    lows at 6000.00 and closes at ``close`` -- a range of exactly 1.00 every time."""
    return [SPIKE_BASE, SPIKE_BASE + SPIKE_SLOT_RANGE, SPIKE_BASE, SPIKE_BASE, close]


def slot_volumes(total: int) -> list[int]:
    """Five 1-minute volumes summing to ``total``."""
    each, remainder = divmod(total, RETEST_TF)
    return [each] * (RETEST_TF - 1) + [each + remainder]


def spike_day_bars(first_ct: datetime, *, trade_date: date = D1, baseline_bars: int = 20,
                   spike_close: float = SPIKE_UP_CLOSE, spike_volume: int = SPIKE_VOLUME,
                   trailing_bars: int = 1) -> tuple[Bar, ...]:
    """``baseline_bars`` identical-range coarse bars with alternating volume, then one
    spike bar, then ``trailing_bars`` more -- as 1-minute bars from ``first_ct``."""
    prices: list[float] = []
    volumes: list[int] = []
    for index in range(baseline_bars):
        prices += slot_prices(SPIKE_BASE)
        volumes += slot_volumes(BASELINE_VOLUMES[index % 2])
    prices += slot_prices(spike_close)
    volumes += slot_volumes(spike_volume)
    for _ in range(trailing_bars):
        prices += slot_prices(SPIKE_BASE)
        volumes += slot_volumes(BASELINE_VOLUMES[0])
    return minute_bars(trade_date, first_ct, prices, volumes)


class TestSpikeFadeRetest:
    def test_a_volume_spike_that_closes_up_is_sold_and_bought_back_on_the_next_bar(
        self,
    ) -> None:
        # Arrange: 20 baseline coarse bars from the 17:00 CT reopen (17:00-18:39), so the
        # spike bar is 18:40-18:44 and the bar it is held into is 18:45-18:49.
        bars = spike_day_bars(ct_minute(D1 - timedelta(days=1), 17, 0))
        assert BASELINE_BARS == 20

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert: fade the up-close spike, hold exactly one coarse bar.
        assert signals(events) == [((18, 44), "sell", 1), ((18, 49), "buy", 1)]

    def test_a_volume_spike_that_closes_down_is_bought_and_sold_back(self) -> None:
        # Arrange
        bars = spike_day_bars(ct_minute(D1 - timedelta(days=1), 17, 0),
                              spike_close=SPIKE_BASE - 0.50)

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert
        assert signals(events) == [((18, 44), "buy", 1), ((18, 49), "sell", 1)]

    def test_no_entry_before_twenty_coarse_bars_exist_on_the_trade_date(self) -> None:
        # Arrange: the same spike, one baseline bar short of the declared window.
        bars = spike_day_bars(ct_minute(D1 - timedelta(days=1), 17, 0), baseline_bars=19)

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert
        assert signals(events) == []

    def test_a_spike_bar_whose_close_equals_its_open_does_not_trigger(self) -> None:
        # Arrange: same volume spike, no direction to fade.
        bars = spike_day_bars(ct_minute(D1 - timedelta(days=1), 17, 0),
                              spike_close=SPIKE_BASE)

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert
        assert signals(events) == []

    def test_a_spike_on_the_last_rth_slot_does_not_enter(self) -> None:
        # Arrange: 20 baseline bars over RTH slots 57-76 (13:15-14:54 CT), with the spike
        # on slot 77 (14:55-14:59). No slot is left to hold it into.
        bars = spike_day_bars(ct_minute(D1, 13, 15), trailing_bars=0)
        assert ct_hm(bars[-1]) == (14, 59)

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert
        assert signals(events) == []

    def test_a_spike_on_the_last_eth_slot_is_held_across_the_0830_hand_off(self) -> None:
        # Arrange: 20 baseline bars over 06:45-08:24 CT, the spike on the last ETH slot
        # (08:25-08:29). Rule R5 makes that slot adjacent to RTH slot 0, and the
        # declaration says RT5 "may be held across" the hand-off.
        bars = spike_day_bars(ct_minute(D1, 6, 45))

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert: the exit lands on the completion of RTH slot 0 (08:30-08:34 CT).
        assert signals(events) == [((8, 29), "sell", 1), ((8, 34), "buy", 1)]

    def test_an_ordinary_volume_on_the_twenty_first_bar_does_not_trigger(self) -> None:
        # Arrange: the baseline's own volume, well inside 3 population sds.
        bars = spike_day_bars(ct_minute(D1 - timedelta(days=1), 17, 0),
                              spike_volume=BASELINE_VOLUMES[1])

        # Act
        events = drive(SpikeFadeRetest(), bars)

        # Assert
        assert signals(events) == []


# ====================================================== RT6/RT7 the daily vol state ====
def constant_slot_bars(trade_date: date, first_ct: datetime,
                       slot_closes: Sequence[float]) -> tuple[Bar, ...]:
    """One 5-minute slot per price: five identical 1-minute bars, so each coarse bar's
    open, high, low and close are that price."""
    prices = [price for price in slot_closes for _ in range(RETEST_TF)]
    return minute_bars(trade_date, first_ct, prices)


def mean_squared_log_return(closes: Sequence[float]) -> float:
    """``m_d`` written out longhand: the mean squared 5-minute close-to-close log return
    over adjacent slot pairs (declaration RT6)."""
    squares = []
    for previous, current in zip(closes[:-1], closes[1:], strict=True):
        step = math.log(current / previous)
        squares.append(step * step)
    return sum(squares) / len(squares)


DAY1_CLOSES = (6000.00, 6001.00, 6000.00, 6001.00)  # 3 adjacent 5-minute returns
DAY2_CLOSES = (6001.00, 6003.00, 6002.00)           # 2 adjacent 5-minute returns
DAY3_CLOSES = (6002.00,)                            # no return: only one slot
M1 = mean_squared_log_return(DAY1_CLOSES)
M2 = mean_squared_log_return(DAY2_CLOSES)


def vol_state_by_day() -> dict[date, tuple[float, int]]:
    """(v_today, days_folded) snapshotted at the first bar of each trade date, in the
    order ``on_bar`` uses: ``start_day`` first, then ``push``."""
    estimator = DailyVolEstimator()
    snapshots: dict[date, tuple[float, int]] = {}
    for trade_date, closes in ((D1, DAY1_CLOSES), (D2, DAY2_CLOSES), (D3, DAY3_CLOSES)):
        for bar in constant_slot_bars(trade_date, ct_minute(trade_date, *RTH_OPEN_CT), closes):
            if estimator.start_day(bar):
                snapshots[trade_date] = (estimator.v_today, estimator.days_folded)
            estimator.push(bar)
    return snapshots


class TestDailyVolEstimator:
    def test_the_first_trade_date_has_no_prior_day_so_v_today_is_zero(self) -> None:
        # Arrange / Act
        snapshots = vol_state_by_day()

        # Assert
        assert snapshots[D1] == (0.0, 0)

    def test_the_second_date_is_seeded_with_the_first_dates_mean_squared_return(self) -> None:
        # Arrange / Act
        snapshots = vol_state_by_day()

        # Assert: seeded, so V = sqrt(m1) exactly, and one day has been folded.
        assert snapshots[D2] == (math.sqrt(M1), 1)

    def test_the_third_date_is_the_root_of_the_ewma_of_both_earlier_dates(self) -> None:
        # Arrange: the declared lambda, applied per trade date.
        assert EWMA_LAMBDA == 0.94
        expected = math.sqrt(0.94 * M1 + (1.0 - 0.94) * M2)

        # Act
        snapshots = vol_state_by_day()

        # Assert
        assert snapshots[D3] == (expected, 2)

    def test_v_today_never_uses_the_current_trade_dates_own_bars(self) -> None:
        # Arrange: day 2's own m differs from day 1's, so a leak would show up here.
        assert M1 != M2

        # Act
        snapshots = vol_state_by_day()

        # Assert: day 2's state is day 1's m alone.
        assert snapshots[D2][0] == math.sqrt(M1)
        assert snapshots[D2][0] != math.sqrt(M2)


# ============================================================ RT7 inverse-vol sizing ====
SIZING_CLOSE = 6000.00


def declared_quantity(close: float, vol: float) -> int:
    """Declaration RT7, written out: size = round(75 / risk$) clipped to [1, 5], with
    risk$ = close * V * sqrt(30/5) / 0.25 * $1.25."""
    if vol <= 0.0:
        return 5
    risk_usd = close * vol * math.sqrt(6) / 0.25 * 1.25
    return max(1, min(5, round(75 / risk_usd)))


def sizing_strategy(vol: float) -> DailyVolSizingRetest:
    strategy = DailyVolSizingRetest()
    strategy._vol.v_today = vol
    return strategy


class TestDailyVolSizing:
    def test_the_sized_quantity_follows_the_declared_inverse_vol_formula(self) -> None:
        # Arrange
        assert (TARGET_RISK_USD, MIN_QUANTITY_MICROS, MAX_QUANTITY_MICROS) == (75.0, 1, 5)
        bar = minute_bars(D1, ct_minute(D1, 9, 0), [SIZING_CLOSE])[0]

        for vol in (0.00005, 0.0002, 0.00034, 0.0005, 0.001, 0.01):
            # Act
            quantity = sizing_strategy(vol)._sized_quantity(bar)

            # Assert
            assert quantity == declared_quantity(SIZING_CLOSE, vol), vol

    def test_the_known_answer_sizes_at_a_6000_close(self) -> None:
        # Arrange: risk$ = 6000 * V * sqrt(6) / 0.25 * 1.25 = 73484.69 * V, so
        # 75 / risk$ = 0.0010206 / V.
        bar = minute_bars(D1, ct_minute(D1, 9, 0), [SIZING_CLOSE])[0]

        # Act / Assert
        assert sizing_strategy(0.00034)._sized_quantity(bar) == 3  # 3.0018 -> 3
        assert sizing_strategy(0.0005)._sized_quantity(bar) == 2   # 2.0412 -> 2
        assert sizing_strategy(0.001)._sized_quantity(bar) == 1    # 1.0206 -> 1

    def test_a_tiny_vol_is_clipped_to_five_micros_and_a_large_one_to_one(self) -> None:
        # Arrange
        bar = minute_bars(D1, ct_minute(D1, 9, 0), [SIZING_CLOSE])[0]

        # Act / Assert: 75 / risk$ is 20.4 at V = 0.00005 and 0.102 at V = 0.01.
        assert sizing_strategy(0.00005)._sized_quantity(bar) == MAX_QUANTITY_MICROS
        assert sizing_strategy(0.01)._sized_quantity(bar) == MIN_QUANTITY_MICROS

    def test_zero_vol_sizes_at_the_maximum(self) -> None:
        # Arrange: the warm-up / first-day state, where V is 0.0.
        bar = minute_bars(D1, ct_minute(D1, 9, 0), [SIZING_CLOSE])[0]

        # Act / Assert
        assert sizing_strategy(0.0)._sized_quantity(bar) == MAX_QUANTITY_MICROS


# ========================================================= RT6 the low-tercile gate ====
GATE_HISTORY = tuple(0.001 * (index + 1) for index in range(MIN_HISTORY_DAYS))  # 0.001..0.030
GATE_BARS_PER_DAY = 96  # 08:30 .. 10:05 CT, past the entry (index 60) and exit (index 90)
ENTRY_CT = (9, 30)  # 08:30 + 60 one-minute bars
EXIT_CT = (10, 0)   # 30 one-minute bars after the entry


def gate_strategy(v_today: float) -> DailyVolRegimeGateRetest:
    """A gate whose history is the 30 hand-built V values and whose first trade date's own
    V is ``v_today`` (the estimator's EWMA is seeded so that sqrt(EWMA) is it)."""
    strategy = DailyVolRegimeGateRetest()
    strategy._history.extend(GATE_HISTORY)
    strategy._vol._ewma = v_today * v_today
    return strategy


def gate_day_bars() -> tuple[Bar, ...]:
    return minute_bars(D1, ct_minute(D1, *RTH_OPEN_CT), [6000.00] * GATE_BARS_PER_DAY)


class TestDailyVolRegimeGate:
    def test_a_v_below_the_low_tercile_enters_at_bar_index_sixty_and_exits_thirty_bars_later(
        self,
    ) -> None:
        # Arrange: V = 0.0005 is below all 30 history values, so its percentile rank is
        # 0.0 <= 1/3.
        assert len(GATE_HISTORY) == MIN_HISTORY_DAYS == 30
        strategy = gate_strategy(0.0005)

        # Act
        events = drive(strategy, gate_day_bars())

        # Assert
        assert signals(events) == [(ENTRY_CT, "buy", 1), (EXIT_CT, "sell", 1)]

    def test_a_v_above_the_low_tercile_does_not_enter(self) -> None:
        # Arrange: V = 0.0255 sits above 25 of the 30 history values (rank 0.833).
        strategy = gate_strategy(0.0255)

        # Act
        events = drive(strategy, gate_day_bars())

        # Assert
        assert signals(events) == []

    def test_a_v_exactly_at_the_one_third_percentile_is_still_a_low_day(self) -> None:
        # Arrange: V = 0.0105 sits above exactly 10 of the 30 values, rank 1/3, and the
        # declared gate is "<= 1/3".
        assert TERCILE_LOW_MAX == 1.0 / 3.0
        strategy = gate_strategy(0.0105)

        # Act
        events = drive(strategy, gate_day_bars())

        # Assert
        assert signals(events) == [(ENTRY_CT, "buy", 1), (EXIT_CT, "sell", 1)]

    def test_the_entry_bar_is_the_sixty_first_bar_of_the_trade_date(self) -> None:
        # Arrange
        bars = gate_day_bars()
        strategy = gate_strategy(0.0005)

        # Act
        entry_bar, _ = drive(strategy, bars)[0]

        # Assert: index 60, counted from the trade date's first bar in the series.
        assert bars.index(entry_bar) == 60
        assert ct_hm(entry_bar) == ENTRY_CT


# ================================================= a suspected defect, reproduced ====
SUSPECTED_DROPPED_HOLD = (
    "SpikeFadeRetest.on_bar keeps only the LAST intent of a push, and clears _holding on "
    "whichever coarse bar follows the entry's own coarse bar in the SAME push. Rule R6's "
    "late completion makes that reachable: when the spike slot's last minute is missing "
    "and the next 1-minute bar the strategy receives is itself the last minute of a later "
    "slot, CoarseBarBuilder.push returns two coarse bars at once. The entry is emitted on "
    "the first of them while the account is still flat (the fill is at the next 1-minute "
    "open), then the second iteration consumes _holding, sees position_micros == 0 and "
    "emits nothing -- so the declared 1-bar hold is never closed and the position rides "
    "until the engine's 15:10 forced flatten. The same early-return pattern in "
    "OrbRetest.on_bar drops the second coarse bar of such a push from its hold count. "
    "NOT reachable on the research slice: no tf-5 push returns two coarse bars on any of "
    "the 311 research trade dates, so no D.1d figure is affected. Reported, not fixed "
    "(this file may not change strategy code). A fix would accumulate intents across the "
    "loop instead of overwriting them, and clear _holding only on a coarse bar that did "
    "not complete in the entry's own push."
)


def late_completion_spike_bars() -> tuple[Bar, ...]:
    """A trade date on which the spike bar and the bar after it complete on the SAME
    1-minute bar: 20 baseline coarse bars (17:00-18:39 CT), a spike slot 18:40-18:44
    whose up-close is set on its third minute, then minutes 18:44 through 18:48 missing,
    so the 18:49 bar both flushes the spike slot late and completes slot 18:45-18:49."""
    prices: list[float] = []
    volumes: list[int] = []
    for index in range(20):
        prices += slot_prices(SPIKE_BASE)
        volumes += slot_volumes(BASELINE_VOLUMES[index % 2])
    # The up-close is on minute 3 so that it survives the missing last minute.
    prices += [SPIKE_BASE, SPIKE_BASE + SPIKE_SLOT_RANGE, SPIKE_UP_CLOSE, SPIKE_UP_CLOSE,
               SPIKE_UP_CLOSE]
    volumes += slot_volumes(SPIKE_VOLUME)
    for _ in range(4):
        prices += slot_prices(SPIKE_BASE)
        volumes += slot_volumes(BASELINE_VOLUMES[0])
    bars = minute_bars(D1, ct_minute(D1 - timedelta(days=1), 17, 0), prices, volumes)
    missing = {(18, 44), (18, 45), (18, 46), (18, 47), (18, 48)}
    return tuple(bar for bar in bars if ct_hm(bar) not in missing)


# SUSPECTED_DROPPED_HOLD was found by this test and fixed the same day (2026-09-21):
# on_bar no longer returns from inside the completions loop, and the hold now ends at the
# first completion after the entry's decision bar at which the fill is visible.
def test_a_spike_whose_next_coarse_bar_completes_on_the_same_minute_is_still_exited() -> None:
    # Arrange: the spike bar still qualifies with its last minute missing -- volume 160
    # against a baseline mean of 101 and a population sd of 1.0 -- and still closes up.
    bars = late_completion_spike_bars()
    assert ct_hm(bars[-1]) == (19, 4)

    # Act
    events = drive(SpikeFadeRetest(), bars)

    # Assert: whatever minute the exit lands on, the declared 1-bar hold must be closed.
    assert [side for _, side, _ in signals(events)] == ["sell", "buy"]
