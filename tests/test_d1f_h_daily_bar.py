"""Stage D.1f Task 5: look-ahead and known-answer tests for the Family H modules.

Specification (FROZEN): reports/stage_d1f_confirmation_list.md section 2.1 A3, including its
"Look-ahead check" list, 3.1 (q = 2 micros) and 5.5.

SYNTHETIC BARS ONLY (R-7). No research parquet, train union, fold or real bar is ever loaded
into an H module here: an H run on real bars before the confirmation is a screen against N.

Synthetic sessions: RTH bars 08:30..15:12 CT on weekdays from Mon 2025-09-08 (no exchange
holiday). A session is flat at 6000.00 except where its ``Day`` says otherwise:
- the 08:30 bar spans 5999.00..6001.00, so the opening range is [5999.00, 6001.00] (30 bars);
- ``high`` is a 12:00 wick and ``low`` a 12:01 wick (the daily extremes);
- ``close`` is the 14:59 bar's close (daily C);
- ``steps`` move the flat level from a minute on, ``bars`` override whole bars (O, H, L, C).
Every expected number is written by hand beside its assert; costs are the size-5 bucket of
sim/slippage_calibration.json read through sim.costs (2 micros pay the size-5 bucket, R-8).
"""

from __future__ import annotations

import ast
import inspect
import logging
import math
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
from functools import partial
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules.xfa_rules import MES_TICK_SIZE, flatten_time_ct, no_new_positions_time_ct
from screening.runner import canonical_engine_config, screen_frame
from sim.costs import bucket_key, calibrated_size, expected_slippage_ticks, load_slippage_table
from sim.engine import BacktestResult, FillEvent, IntentEvent, iter_bars, run_backtest
from strategy.interface import Strategy
from strategy.research import h_daily_bar
from strategy.research.h_daily_bar import H_TRIALS
from strategy.research.h_daily_bar import _mechanics as mech
from strategy.research.h_daily_bar import h1_nr4_breakout as h1
from strategy.research.h_daily_bar import h2_nr7_breakout as h2
from strategy.research.h_daily_bar import h3_inside_day_breakout as h3
from strategy.research.h_daily_bar import h4_bottom_tercile_breakout as h4
from strategy.research.h_daily_bar import h5_top_tercile_fade as h5
from strategy.research.h_daily_bar import h6_prior_close_location as h6
from strategy.research.h_daily_bar._mechanics import Condition, DailyBar

CT = ZoneInfo("America/Chicago")
A, B = 4242, 4343  # two contracts: a roll is a change from A to B
BASE = 6000.0
TABLE = load_slippage_table()


def _weekdays(start: date, n: int) -> tuple[date, ...]:
    out, day = [], start
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return tuple(out)


DAYS = _weekdays(date(2025, 9, 8), 8)


def hm(text: str) -> time:
    return time.fromisoformat(text)


def ts_ns(day: date, at: time) -> int:
    return int(datetime.combine(day, at, tzinfo=CT).astimezone(UTC).timestamp()) * 10**9


def minutes(first: str, last: str) -> tuple[str, ...]:
    lo, hi = hm(first), hm(last)
    span = (hi.hour - lo.hour) * 60 + hi.minute - lo.minute
    return tuple(f"{(lo.hour * 60 + lo.minute + k) // 60:02d}:{(lo.minute + k) % 60:02d}"
                 for k in range(span + 1))


# ------------------------------------------------------------------ synthetic bars ----
@dataclass(frozen=True)
class Day:
    day: date
    high: float | None = None
    low: float | None = None
    close: float | None = None
    steps: tuple[tuple[str, float], ...] = ()
    bars: tuple[tuple[str, float, float, float, float], ...] = ()
    missing: tuple[str, ...] = ()
    instrument: int = A
    switch: tuple[str, int] | None = None  # (HH:MM, instrument from then on)
    early_halt: str = ""
    start: str = "08:30"
    end: str = "15:12"


def rows(d: Day) -> list[dict]:
    halt = hm(d.early_halt) if d.early_halt else None
    flat_at, nonew_at = flatten_time_ct(halt), no_new_positions_time_ct(halt)
    explicit = {hm(b[0]): b[1:] for b in d.bars}
    out, prev = [], None
    for label in minutes(d.start, d.end):
        at = hm(label)
        if label in d.missing:
            continue
        level = BASE
        for step, price in d.steps:
            level = price if hm(step) <= at else level
        o = h = lo = c = level
        if at == time(8, 30):
            h, lo = level + 1.0, level - 1.0
        if at == time(12, 0) and d.high is not None:
            h = d.high
        if at == time(12, 1) and d.low is not None:
            lo = d.low
        if at == time(14, 59) and d.close is not None:
            c, h, lo = d.close, max(h, d.close), min(lo, d.close)
        o, h, lo, c = explicit.get(at, (o, h, lo, c))
        switched = d.switch is not None and at >= hm(d.switch[0])
        instrument = d.switch[1] if switched and d.switch else d.instrument
        minute = at.hour * 60 + at.minute
        out.append({
            "ts_event": ts_ns(d.day, at), "open": o, "high": h, "low": lo, "close": c,
            "volume": 100, "instrument_id": instrument,
            "raw_symbol": "MESZ5" if instrument == A else "MESH6",
            "trade_date": d.day.isoformat(), "in_flatten_window": at >= flat_at,
            "in_no_new_positions_window": at >= nonew_at, "early_halt_ct": d.early_halt,
            "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0 if prev is None else minute - prev - 1,
            "vendor_degraded_day": False,
        })
        prev = minute
    return out


def scaled(d: Day) -> list[dict]:
    """Every bar of the day as a scaled copy: prices x 1.01 kept on the grid, volume x 2."""
    def s(price: float) -> float:
        return round(price * 1.01 / 0.25) * 0.25
    return [{**r, "open": s(r["open"]), "high": s(r["high"]), "low": s(r["low"]),
             "close": s(r["close"]), "volume": r["volume"] * 2} for r in rows(d)]


def frame(parts: list[Day | list[dict]] | tuple[Day, ...]) -> pd.DataFrame:
    out: list[dict] = []
    for part in parts:
        out.extend(rows(part) if isinstance(part, Day) else part)
    return pd.DataFrame(out)


def run(strategy: mech.DailyBarStrategy, parts, splices=()
        ) -> tuple[BacktestResult, dict[date, mech.DayRecord]]:
    result = run_backtest(iter_bars(frame(parts)), strategy, canonical_engine_config(splices),
                          TABLE)
    return result, {r.trade_date: r for r in strategy.day_records}


def _ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // 10**9, tz=UTC).astimezone(CT)


def fills(result: BacktestResult) -> list[tuple[date, str, str, int, float, str]]:
    return [(_ct(f.fill_ts_ns).date(), f"{_ct(f.fill_ts_ns):%H:%M}", f.side, f.qty, f.price,
             f.reason) for f in result.events(FillEvent)]


def intents(result: BacktestResult, day: date) -> list[tuple[str, str, int, bool, str | None]]:
    """(decision time, side, qty, accepted, refusal) of every intent decided on ``day``."""
    return [(f"{_ct(e.decision_ts_ns):%H:%M}", e.intent.side, e.intent.quantity_micros,
             e.accepted, None if e.refusal is None else e.refusal.reason)
            for e in result.events(IntentEvent) if _ct(e.decision_ts_ns).date() == day]


# An up breakout: the 10:00 bar CLOSES at 6001.25 > OR_high 6001.00, so the buy is decided
# on it and fills at the 10:01 open, 6001.50; the exit is decided on the 14:58 bar and fills
# at the 14:59 open, 6003.00. Daily L = 5999.00 (the OR low), C = 6003.00.
UP_BARS = (("10:00", 6000.0, 6001.25, 6000.0, 6001.25),)
UP_STEPS = (("10:01", 6001.5), ("14:59", 6003.0))
BREAKOUT_FILLS = ("10:01", 6001.5, "14:59", 6003.0)


def up(i: int, rng: int | None = None, **kw) -> Day:
    """An up-breakout session on DAYS[i] with Range = ``rng`` ticks (H = 5999.00 + rng/4)."""
    high = None if rng is None else 5999.0 + rng * 0.25
    return Day(DAYS[i], **{"high": high, "bars": UP_BARS, "steps": UP_STEPS, **kw})


def clv_day(i: int, close: float, steps: tuple[tuple[str, float], ...] = ()) -> Day:
    """H = 6005.00, L = 5995.00 (Range 40 ticks), C = ``close``."""
    return Day(DAYS[i], high=6005.0, low=5995.0, close=close, steps=steps)


# ------------------------------------------------------------ the per-module cases ----
@dataclass(frozen=True)
class Case:
    module: ModuleType
    make: Callable[[], mech.DailyBarStrategy]
    condition: Callable[..., Condition | None]
    days: tuple[Day, ...]
    trades: tuple[tuple[int, str, str, float, str, float], ...]  # day, side, fills in / out
    net_cents: int  # by hand, see test_side_costs_by_hand
    probe: int  # day d of the look-ahead pair (a trade day)
    before: Condition  # day d's condition, by hand
    new_prior: Day  # the replacement for day d-1
    after: Condition  # day d's condition after the replacement, by hand


H3_HL = ((6008, 5996), (6006, 5997), (6007, 5995), (6009, 5998), (6010, 5994),
         (6011, 5997), (6012, 5996), (6010, 5996))  # idx1 is inside idx0; no other inside day
CASES = (
    # Ranges 40 36 32 20 44 36 24 40: day 4's d-1 (20) is the NR4 bar; 5, 6, 7 fail
    # (44 vs 20 32 36; 36 vs 44 20 32; 24 vs 36 44 20). Gross 2 x 6 ticks x 125 = +1500 c.
    Case(h1, h1.factory, h1.condition,
         tuple(up(i, r) for i, r in enumerate((40, 36, 32, 20, 44, 36, 24, 40))),
         ((4, "buy", *BREAKOUT_FILLS),), 1500 - 263 - 255, 4,
         Condition(True, (20.0, 32.0, 36.0, 40.0)), up(3, 32),
         Condition(False, (32.0, 32.0, 36.0, 40.0))),  # a tie is not "strictly smaller"
    # Ranges 40 36 44 32 28 36 24 40: day 7's d-1 (24) is the NR7 bar.
    Case(h2, h2.factory, h2.condition,
         tuple(up(i, r) for i, r in enumerate((40, 36, 44, 32, 28, 36, 24, 40))),
         ((7, "buy", *BREAKOUT_FILLS),), 1500 - 263 - 255, 7,
         Condition(True, (24.0, 36.0, 28.0, 32.0, 44.0, 36.0, 40.0)), up(6, 28),
         Condition(False, (28.0, 36.0, 28.0, 32.0, 44.0, 36.0, 40.0))),
    Case(h3, h3.factory, h3.condition,
         tuple(up(i, high=float(h), low=float(lo)) for i, (h, lo) in enumerate(H3_HL)),
         ((2, "buy", *BREAKOUT_FILLS),), 1500 - 263 - 255, 2,
         Condition(True, (6006.0, 6008.0, 5997.0, 5996.0)), up(1, high=6006.0, low=5996.0),
         Condition(False, (6006.0, 6008.0, 5996.0, 5996.0))),  # equal lows: not inside
    # Warm-up shortened to 7 (d-1 plus 6). Baseline 40 32 44 32 28 48 sorted 28 32 32 40 44 48:
    # P33.33 index 5 x 0.3333 = 1.6665 between 32 and 32 -> 32.0; Range[d-1] 32 <= 32 holds.
    Case(h4, lambda: h4.H4BottomTercileBreakout(_lookback=7),
         partial(h4.condition, _lookback=7),
         tuple(up(i, r) for i, r in enumerate((40, 32, 44, 32, 28, 48, 32, 40))),
         ((7, "buy", *BREAKOUT_FILLS),), 1500 - 263 - 255, 7,
         Condition(True, (32.0, 32.0)), up(6, 36), Condition(False, (36.0, 32.0))),
    # Baseline 44 36 48 32 28 44 sorted 28 32 36 44 44 48: P66.67 index 3.3335 -> 44.0;
    # Range[d-1] 44 >= 44 holds. The fade SELLS the up breakout: gross -1500 c.
    Case(h5, lambda: h5.H5TopTercileFade(_lookback=7), partial(h5.condition, _lookback=7),
         tuple(up(i, r) for i, r in enumerate((44, 36, 48, 32, 28, 44, 44, 40))),
         ((7, "sell", *BREAKOUT_FILLS),), -1500 - 263 - 255, 7,
         Condition(True, (44.0, 44.0)), up(6, 40), Condition(False, (40.0, 44.0))),
    # CLV by day: 0.9 0.5 0.1 0.5 0.75 0.25 0.5 0.5 -> buy on day 1, sell on day 3, both
    # decided on the 08:30 bar and filled at the 08:31 open; each gross 2 x 6 x 125 = +1500 c.
    Case(h6, h6.factory, h6.condition,
         (clv_day(0, 6004.0), clv_day(1, 6000.0, (("08:31", 6000.5), ("14:59", 6002.0))),
          clv_day(2, 5996.0), clv_day(3, 6000.0, (("08:31", 5999.5), ("14:59", 5998.0))),
          clv_day(4, 6002.5), clv_day(5, 5997.5), clv_day(6, 6000.0), clv_day(7, 6000.0)),
         ((1, "buy", "08:31", 6000.5, "14:59", 6002.0),
          (3, "sell", "08:31", 5999.5, "14:59", 5998.0)), 2 * (1500 - 263 - 255), 1,
         Condition(True, (40.0, 0.9), "buy"), clv_day(0, 6002.75),
         Condition(False, (40.0, 0.775))),  # CLV 31/40
)
CASE_IDS = [c.module.NAME for c in CASES]


def expected_fills(case: Case, skip: tuple[int, ...] = ()) -> list:
    out = []
    for i, side, t_in, p_in, t_out, p_out in case.trades:
        if i not in skip:
            back = "sell" if side == "buy" else "buy"
            out += [(DAYS[i], t_in, side, 2, p_in, "strategy"),
                    (DAYS[i], t_out, back, 2, p_out, "strategy")]
    return out


# ------------------------------------------------------ 3. hand-built known answers ----
# Size-5 bucket means in sim/slippage_calibration.json: 08:30 0.5605, 10:00 0.5639,
# 14:45 0.5306 ticks. One side at 2 micros = 2 x 61 c commission + ceil(2 x slip x 125) c:
# 08:31 fill 122 + ceil(140.125) = 263; 10:01 fill 122 + ceil(140.975) = 263;
# 14:59 fill 122 + ceil(132.65) = 255.
SIDE_COST_CENTS = {"08:31": 263, "10:01": 263, "14:59": 255}
SIZE5_MEANS = {"08:30": 0.5605, "10:00": 0.5639, "14:45": 0.5306}


def test_side_costs_by_hand() -> None:
    assert calibrated_size(2, TABLE.sizes_micros) == 5
    for label, cents in SIDE_COST_CENTS.items():
        at = datetime.combine(DAYS[0], hm(label), tzinfo=CT)
        slip = expected_slippage_ticks(TABLE, at, 2)
        key = bucket_key(at, TABLE.bucket_minutes)
        assert slip == TABLE.buckets[key]["5"]["mean"] == SIZE5_MEANS[key]
        assert 2 * 61 + math.ceil(round(2 * slip * 125, 6)) == cents


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_known_answer_trades_to_the_cent(case: Case) -> None:
    strategy = case.make()
    result, records = run(strategy, case.days)
    assert fills(result) == expected_fills(case)
    for i, side, t_in, _, t_out, _ in case.trades:  # decided one bar before each fill
        back = "sell" if side == "buy" else "buy"
        assert intents(result, DAYS[i]) == [(t_in, side, 2, True, None),
                                            (t_out, back, 2, True, None)]
    gross = sum((1 if side == "buy" else -1) * 2 * round((p_out - p_in) / 0.25) * 125
                for _, side, _, p_in, _, p_out in case.trades)
    costs = sum(SIDE_COST_CENTS[t_in] + SIDE_COST_CENTS[t_out]
                for _, _, t_in, _, t_out, _ in case.trades)
    assert gross - costs == case.net_cents
    booked = sum(f.gross_realized_cents - f.commission_cents - f.slippage_cents
                 for f in result.events(FillEvent))
    assert booked == case.net_cents
    traded = {DAYS[i] for i, *_ in case.trades}
    assert {d for d, r in records.items() if r.entry_side is not None} == traded
    assert strategy.forced_exit_dates == ()
    report = screen_frame(frame(case.days), case.module.LABEL, case.make, "synthetic",
                          splice_trade_dates=())
    assert report.net_pnl_usd == case.net_cents / 100
    assert report.trip_micros == (2,) * len(case.trades)


# ----------------------------------------------------- 1. prior-day dependence pair ----
@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_condition_ignores_day_d_and_follows_day_d_minus_1(case: Case) -> None:
    d, day = case.probe, DAYS[case.probe]
    base = list(case.days[: d + 1])
    strategy = case.make()
    _, records = run(strategy, base)
    assert records[day].condition == case.before
    prior = tuple(r.daily_bar for r in strategy.day_records[:d] if r.daily_bar is not None)
    assert case.condition(prior) == case.before  # the pure function, called directly

    # Day d replaced by a scaled copy: its bars really changed (the OR moved), its condition
    # did not.
    scaled_run = case.make()
    _, scaled_records = run(scaled_run, [*base[:d], scaled(base[d])])
    assert scaled_records[day].or_high != records[day].or_high
    assert scaled_records[day].condition == case.before

    # Day d-1 replaced: the condition changes exactly as computed by hand.
    replaced = case.make()
    _, replaced_records = run(replaced, [*base[: d - 1], case.new_prior, base[d]])
    assert replaced_records[day].condition == case.after != case.before
    new_prior = tuple(r.daily_bar for r in replaced.day_records[:d] if r.daily_bar is not None)
    assert case.condition(new_prior) == case.after


def _clv(bar: DailyBar) -> float:
    return (bar.close_ticks - bar.low_ticks) / bar.range_ticks


def _next_weekday(day: date) -> date:
    return _weekdays(day + timedelta(days=1), 1)[0]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_condition_ignores_a_day_d_with_a_different_range_and_clv(case: Case) -> None:
    """N1 (outside the frozen wording, which fixes the x1.01 copy above): day d replaced by a
    copy whose 12:00 wick is 7.50 higher and whose 14:59 close is 1.00 lower, so its tick range
    AND its CLV both change; day d's condition value must not."""
    d, day = case.probe, DAYS[case.probe]
    original = case.days[d]
    assert original.high is not None  # every probe day has an explicit 12:00 wick
    changed = replace(original, high=original.high + 7.5,
                      close=(original.close if original.close is not None else 6003.0) - 1.0)
    after = Day(_next_weekday(day))  # closes day d, so its own daily bar is recorded
    bars = {}
    for label, probe_day in (("original", original), ("changed", changed)):
        strategy = case.make()
        _, records = run(strategy, [*case.days[:d], probe_day, after])
        assert records[day].condition == case.before, label
        bars[label] = records[day].daily_bar
    assert bars["original"] is not None and bars["changed"] is not None
    # The replacement bites: day d's own range and CLV really differ ...
    assert bars["changed"].range_ticks != bars["original"].range_ticks
    assert _clv(bars["changed"]) != _clv(bars["original"])
    # ... and the condition the module read on day d is still the hand-computed one.
    assert case.condition(tuple(r for r in (records[t].daily_bar for t in DAYS[:d])
                                if r is not None)) == case.before


def test_pure_conditions_use_only_what_they_are_given() -> None:
    def bar(k: int, span: int, close_ticks: int = 0) -> DailyBar:
        return DailyBar(DAYS[0] + timedelta(days=k), BASE, BASE + span * 0.25, BASE,
                        BASE + close_ticks * 0.25, A)

    # Warm-up: one bar short of the lookback gives no condition at all.
    assert h1.condition([bar(k, 20) for k in range(3)]) is None
    assert h2.condition([bar(k, 20) for k in range(6)]) is None
    assert h3.condition([bar(0, 20)]) is None and h6.condition([]) is None
    # H6: CLV exactly 0.8 buys and exactly 0.2 sells (non-strict); a zero range never trades.
    assert h6.condition([bar(0, 40, 32)]) == Condition(True, (40.0, 0.8), "buy")
    assert h6.condition([bar(0, 40, 8)]) == Condition(True, (40.0, 0.2), "sell")
    assert h6.condition([bar(0, 40, 9)]) == Condition(False, (40.0, 0.225))
    assert h6.condition([bar(0, 0)]) == Condition(False, (0.0,))
    # H4 / H5 at the PRODUCTION lookback 61: 60 baseline ranges, twenty each of 10, 20, 30.
    # P33.33: index 59 x 0.3333 = 19.6647, between 10 and 20 -> 16.647.
    # P66.67: index 59 x 0.6667 = 39.3353, between 20 and 30 -> 23.353.
    baseline = [bar(k, (10, 20, 30)[k % 3]) for k in range(60)]
    assert h4.condition(baseline) is None and h5.condition(baseline) is None
    low, high = h4.condition([*baseline, bar(60, 16)]), h4.condition([*baseline, bar(60, 17)])
    assert low is not None and high is not None
    assert low.holds and not high.holds and low.values[1] == pytest.approx(16.647)
    top, mid = h5.condition([*baseline, bar(60, 24)]), h5.condition([*baseline, bar(60, 23)])
    assert top is not None and mid is not None
    assert top.holds and not mid.holds and top.values[1] == pytest.approx(23.353)


# ---------------------------------------------------------------------- 2. timing ----
PREFIX = tuple(up(i, r) for i, r in enumerate((40, 36, 32, 20)))  # day 4 is an NR4 day


def h1_run(*days: Day | list[dict], splices=()):
    strategy = h1.factory()
    result, records = run(strategy, [*PREFIX, *days], splices)
    return strategy, result, records


def test_daily_bar_uses_ct_0830_to_1500_only() -> None:
    spikes = (("08:29", BASE, 6020.0, 5980.0, BASE), ("15:05", 6003.0, 6020.0, 5980.0, 6003.0))
    _, _, records = h1_run(up(4, 44, start="08:20", bars=(*UP_BARS, *spikes)), up(5, 36))
    # O = the 08:30 open, H = the 12:00 wick 5999 + 44/4, L = the OR low, C = the 14:59 close
    assert records[DAYS[4]].daily_bar == DailyBar(DAYS[4], 6000.0, 6010.0, 5999.0, 6003.0, A)
    assert records[DAYS[3]].daily_bar == DailyBar(DAYS[3], 6000.0, 6004.0, 5999.0, 6003.0, A)


def test_opening_range_uses_bars_before_0900_only() -> None:
    wick_0900 = ("09:00", BASE, 6010.0, BASE, BASE)  # outside the OR: must not widen it
    _, result, records = h1_run(up(4, 44, bars=(wick_0900, *UP_BARS)))
    assert (records[DAYS[4]].or_high, records[DAYS[4]].or_low) == (6001.0, 5999.0)
    assert records[DAYS[4]].or_bars == 30
    assert fills(result)[0] == (DAYS[4], "10:01", "buy", 2, 6001.5, "strategy")

    wick_0859 = ("08:59", BASE, 6002.0, BASE, BASE)  # inside the OR: the 10:00 close no
    _, result, records = h1_run(up(4, 44, bars=(wick_0859, *UP_BARS)))  # longer breaks it
    assert records[DAYS[4]].or_high == 6002.0 and fills(result) == []
    assert records[DAYS[4]].skip_reason == "no_trigger"

    trigger_0900 = ("09:00", BASE, 6001.25, BASE, 6001.25)  # the first bar after the OR
    _, result, records = h1_run(up(4, 44, bars=(trigger_0900,)))
    assert intents(result, DAYS[4])[0] == ("09:01", "buy", 2, True, None)
    assert fills(result)[0] == (DAYS[4], "09:01", "buy", 2, BASE, "strategy")


def test_trigger_reads_the_close_fills_next_open_and_exits_at_1458() -> None:
    # 09:30: the high pierces the OR but the close equals OR_high (not strictly above).
    probe = ("09:30", BASE, 6005.0, BASE, 6001.0)
    _, result, records = h1_run(up(4, 44, bars=(probe, *UP_BARS)))
    # Decided at the close of the 10:00 and 14:58 bars (decision times 10:01 and 14:59) ...
    assert intents(result, DAYS[4]) == [("10:01", "buy", 2, True, None),
                                         ("14:59", "sell", 2, True, None)]
    # ... filled at the OPEN of the next bars, 10:01 and 14:59.
    assert fills(result) == [(DAYS[4], "10:01", "buy", 2, 6001.5, "strategy"),
                             (DAYS[4], "14:59", "sell", 2, 6003.0, "strategy")]
    assert records[DAYS[4]].exit_decision_ns == ts_ns(DAYS[4], hm("14:59"))
    assert not records[DAYS[4]].forced_exit


@pytest.mark.parametrize("variant", ["gap_to_the_flatten_window", "session_ends_at_1457"])
def test_forced_flatten_fallback_is_counted_and_logged(variant: str, caplog) -> None:
    if variant == "gap_to_the_flatten_window":  # no bar in [14:58, 15:08): 15:08..15:12 remain
        day4, extra = up(4, 44, missing=minutes("14:58", "15:07")), ()
        # The engine queues its flatten on the 15:09 bar (decision 15:10) -> 15:10 open.
        forced = (DAYS[4], "15:10", "sell", 2, 6003.0, "forced_flatten")
    else:  # the session's last bar is 14:57; the next date's first bar ends it
        day4, extra = up(4, 44, end="14:57"), (Day(DAYS[5]),)
        # Closed at the 14:57 bar's close, stamped at its decision time 14:58.
        forced = (DAYS[4], "14:58", "sell", 2, 6001.5, "forced_flatten_session_end")
    with caplog.at_level(logging.WARNING, logger=mech.__name__):
        strategy, result, records = h1_run(day4, *extra)
    assert fills(result)[:2] == [(DAYS[4], "10:01", "buy", 2, 6001.5, "strategy"), forced]
    assert [i[0] for i in intents(result, DAYS[4])] == ["10:01"]  # no strategy exit
    assert records[DAYS[4]].forced_exit and records[DAYS[4]].exit_decision_ns is None
    assert strategy.forced_exit_dates == (DAYS[4],)
    assert f"forced exit on {DAYS[4]}" in caplog.text


@pytest.mark.parametrize("blackout", [False, True])
def test_one_entry_per_trade_date(blackout: bool) -> None:
    down_later = ("11:00", 6001.5, 6001.5, 5998.75, 5998.75)  # closes below OR_low at 11:00
    splices = (DAYS[6],) if blackout else ()  # blackout = DAYS[4], DAYS[5], DAYS[6]
    _, result, records = h1_run(up(4, 44, bars=(*UP_BARS, down_later)), splices=splices)
    if blackout:  # the entry is refused, and the 11:00 break still does not re-enter
        assert intents(result, DAYS[4]) == [("10:01", "buy", 2, False, "engine_roll_blackout")]
        assert fills(result) == []
    else:
        assert intents(result, DAYS[4]) == [("10:01", "buy", 2, True, None),
                                             ("14:59", "sell", 2, True, None)]
    assert records[DAYS[4]].entry_side == "buy"


# ------------------------------------------------------------ 2. no-trade days ----
def test_no_trade_on_an_early_halt_day_and_it_leaves_the_lookback() -> None:
    wide = ("11:00", 6001.5, 6010.0, 6001.5, 6001.5)  # Range 44 if the day counted
    halt = up(4, bars=(*UP_BARS, wide), early_halt="12:00", end="11:59")
    _, result, records = h1_run(halt, up(5, 36))
    assert intents(result, DAYS[4]) == []
    assert records[DAYS[4]].skip_reason == "early_halt"
    assert records[DAYS[4]].daily_bar is None
    # Day 5's d-1 is day 3 (Range 20), not the halt day: the NR4 still holds and trades.
    assert records[DAYS[5]].condition == Condition(True, (20.0, 32.0, 36.0, 40.0))
    assert fills(result)[0] == (DAYS[5], "10:01", "buy", 2, 6001.5, "strategy")


def test_no_trade_without_the_0830_bar() -> None:
    _, result, records = h1_run(up(4, 44, missing=("08:30",)))  # NR4 holds, trigger present
    assert intents(result, DAYS[4]) == [] and fills(result) == []
    assert records[DAYS[4]].skip_reason == "missing_0830_bar"
    # H6 enters ON the 08:30 bar: without it day 1 (CLV 0.9 on day 0) does not trade at a
    # later bar. Day 1 is then incomplete, so day 2's d-1 is day 0 (CLV 0.9): day 2 buys at
    # its 08:31 open 6000.00 and sells at its 14:59 open 6000.00; day 3 sells as before.
    case = CASES[5]
    days = [replace(d, missing=("08:30",)) if i == 1 else d for i, d in enumerate(case.days)]
    result, records = run(case.make(), days)
    assert records[DAYS[1]].skip_reason == "missing_0830_bar"
    assert records[DAYS[2]].condition == Condition(True, (40.0, 0.9), "buy")
    assert fills(result) == [(DAYS[2], "08:31", "buy", 2, BASE, "strategy"),
                             (DAYS[2], "14:59", "sell", 2, BASE, "strategy"),
                             *expected_fills(case, skip=(1,))]


INCOMPLETE = {
    "missing_1459": {"missing": ("14:59",)},
    "missing_0830": {"missing": ("08:30",)},
    "two_instruments": {"instrument": B, "switch": ("12:00", A)},
    "early_halt": {"early_halt": "12:00", "end": "11:59"},
}


@pytest.mark.parametrize("defect", [*INCOMPLETE, None])
def test_incomplete_days_do_not_exist_for_lookbacks(defect: str | None) -> None:
    # Day 4 has no trigger and a Range of 44 ticks (an 11:00 wick to 6010.00).
    day4 = Day(DAYS[4], bars=(("11:00", BASE, 6010.0, BASE, BASE),),
               **INCOMPLETE.get(defect or "", {}))
    _, result, records = h1_run(day4, up(5, 36))
    if defect is None:  # complete: day 4 is d-1 for day 5, 44 is not the narrowest
        assert records[DAYS[5]].condition == Condition(False, (44.0, 20.0, 32.0, 36.0))
        assert fills(result) == []
    else:  # incomplete: day 3 is d-1 for day 5
        assert records[DAYS[4]].daily_bar is None
        assert records[DAYS[5]].condition == Condition(True, (20.0, 32.0, 36.0, 40.0))
        assert fills(result)[0] == (DAYS[5], "10:01", "buy", 2, 6001.5, "strategy")


@pytest.mark.parametrize(("dropped", "trades"), [(5, True), (6, False)])
def test_opening_range_needs_25_of_30_bars(dropped: int, trades: bool) -> None:
    gone = minutes("08:31", f"08:{30 + dropped:02d}")
    _, result, records = h1_run(up(4, 44, missing=gone))
    assert records[DAYS[4]].or_bars == 30 - dropped
    if trades:
        assert fills(result)[0] == (DAYS[4], "10:01", "buy", 2, 6001.5, "strategy")
    else:
        assert fills(result) == [] and records[DAYS[4]].skip_reason == "or_coverage"


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_instrument_guard_blocks_the_first_day_after_a_roll(case: Case) -> None:
    t = case.probe  # the contract changes between day t-1 and day t
    days = [replace(d, instrument=B) if i >= t else d for i, d in enumerate(case.days)]
    result, records = run(case.make(), days)
    assert records[DAYS[t]].condition == case.before  # the condition itself still holds
    assert records[DAYS[t]].guard_ok is False
    assert records[DAYS[t]].skip_reason == "instrument_guard"
    assert fills(result) == expected_fills(case, skip=(t,))


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_instrument_guard_exempts_the_basis_free_bars(case: Case) -> None:
    t = case.probe  # the contract changes between day t-2 and day t-1
    days = [replace(d, instrument=B) if i >= t - 1 else d for i, d in enumerate(case.days)]
    result, records = run(case.make(), days)
    if case.module is h3:  # H3 guards d-1 AND d-2
        assert records[DAYS[t]].skip_reason == "instrument_guard"
        assert fills(result) == expected_fills(case, skip=(t,))
    else:  # H1, H2 earlier ranges and H4, H5 trailing ranges are exempt (NEW-9)
        assert records[DAYS[t]].guard_ok is True
        assert fills(result) == expected_fills(case)


# ------------------------------------------------------------ 4. factories and source ----
TABLE_IDS = (
    "H1 NR4 opening-range breakout",
    "H2 NR7 opening-range breakout",
    "H3 inside-day opening-range breakout",
    "H4 bottom-tercile prior range, breakout",
    "H5 top-tercile prior range, opening-range fade",
    "H6 prior-close location follow-through",
)


def test_factories_take_no_arguments_and_build_the_production_warm_up() -> None:
    assert tuple(label for label, _ in H_TRIALS) == TABLE_IDS
    production = ((4, 1, "breakout"), (7, 1, "breakout"), (2, 2, "breakout"),
                  (61, 1, "breakout"), (61, 1, "fade"), (1, 1, "open"))
    for (_, factory), (lookback, guarded, entry) in zip(H_TRIALS, production, strict=True):
        assert inspect.signature(factory).parameters == {}
        assert "_lookback" not in inspect.getsource(factory)
        strategy = factory()
        assert isinstance(strategy, Strategy) and isinstance(strategy, mech.DailyBarStrategy)
        assert (strategy.lookback, strategy.guarded_bars, strategy.entry) == (
            lookback, guarded, entry)
        assert strategy.day_records == ()
    for module in (h4, h5):  # the private override defaults to the production literal
        cls = module.H4BottomTercileBreakout if module is h4 else module.H5TopTercileFade
        assert inspect.signature(cls).parameters["_lookback"].default == 61 == module.LOOKBACK
        assert module.condition.__kwdefaults__ == {"_lookback": 61}
    assert (h4.PERCENTILE_Q, h5.PERCENTILE_Q) == (33.33, 66.67)
    assert (h6.CLV_BUY_AT_OR_ABOVE, h6.CLV_SELL_AT_OR_BELOW) == (0.8, 0.2)
    assert mech.QUANTITY_MICROS == 2 and mech.TICK_SIZE == MES_TICK_SIZE
    assert mech.OR_MIN_BARS == 25
    assert f"{mech.EXIT_CT:%H:%M} {mech.ENTRY_END_CT:%H:%M}" == "14:58 14:30"


ALLOWED_IMPORTS = {
    "__future__", "collections.abc", "dataclasses", "datetime", "functools", "logging",
    "numpy", "rules.xfa_rules", "strategy.interface", "strategy.research.h_daily_bar",
    "strategy.research.h_daily_bar._mechanics",
}


def test_modules_import_no_data_path_and_name_no_hindsight_field() -> None:
    package = Path(h_daily_bar.__file__).parent
    paths = sorted(package.glob("*.py"))
    assert len(paths) == 8  # __init__, _mechanics and the six modules
    for path in paths:
        source = path.read_text()
        assert "vendor_degraded_day" not in source, path.name
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                assert node.module in ALLOWED_IMPORTS, (path.name, node.module)
            elif isinstance(node, ast.Import):
                assert {a.name for a in node.names} <= ALLOWED_IMPORTS, path.name
        assert len(source.splitlines()) <= 800
