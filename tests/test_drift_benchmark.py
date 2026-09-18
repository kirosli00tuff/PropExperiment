"""Known-answer tests for the drift benchmark (Stage D.1a, Task 1).

The two cases the prompt names, run end to end through the shared runner
(``screening.runner.screen_frame``: real engine, real cost model, real power gate):

1. INJECTED DRIFT. The market rises on average (+100, +100, -20 ticks per session,
   cycling: mean +60). An unconditional RTH long IS the benchmark, restated. The OLD
   zero-edge gate passes it (p = 2/3, R ~ 4.4), which is Stage D.1's failure mode. The
   drift check must fail it, and attribute 100% of its gross P&L to drift.
2. ZERO DRIFT, REAL CONDITIONAL SIGNAL. Up and down sessions balance exactly, so the
   window's average path is flat at every minute. A 09:00 CT signal bar calls the
   session's direction right 8 days in 10. The drift attribution must be exactly $0,
   the drift-adjusted p/R must equal the raw p/R, and the candidate must pass.

Plus the mirror (a short-only rider in a falling market is not exempt), a to-the-cent
attribution example, and the bootstrap bound's behaviour at its edges.

Synthetic sessions: RTH only, 08:30-15:12 CT, weekdays 2025-09-02 .. 2025-11-24
(research dates, no exchange holiday). Price in ticks from 6000.00.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from screening.drift import (
    DRIFT_CONFIDENCE,
    attribute_drift,
    bootstrap_mean_lower_bounds,
    build_drift_path,
    minute_of_trade_date,
)
from screening.runner import ScreeningReport, screen_frame
from sim.costs import load_slippage_table
from sim.engine import NO_ROLL_BLACKOUT, EngineConfig, iter_bars, run_backtest
from strategy.interface import AccountView, Bar, market_intent

CT = ZoneInfo("America/Chicago")
BASE_TICKS = 24_000  # 6000.00
RTH_MINUTES = 403  # 08:30 .. 15:12 CT
EXIT_K = 391  # the move is complete at the 15:01 open


def weekdays(start: date, n: int) -> list[date]:
    out, day = [], start
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DAYS = weekdays(date(2025, 9, 2), 60)


def path_ticks(move: int, signal: int = 0, move_start: int = 1) -> np.ndarray:
    """Price (ticks) at each minute k of the session. A signal of +-1 tick appears at
    the close of the 09:00 bar (k=30); ``move`` accrues linearly from ``move_start``
    and is complete by k = EXIT_K. ``np.rint`` is symmetric, so +m and -m paths are
    exact mirrors and cancel in the window average."""
    k = np.arange(RTH_MINUTES + 1)
    signal_part = np.where(k >= 31, signal, 0)
    frac = np.clip((k - move_start) / (EXIT_K - move_start), 0.0, 1.0)
    return BASE_TICKS + signal_part + np.rint(move * frac).astype(int)


def session_frame(paths: list[np.ndarray]) -> pd.DataFrame:
    rows = []
    for day, p in zip(DAYS, paths, strict=False):
        start = datetime(day.year, day.month, day.day, 8, 30, tzinfo=CT)
        for k in range(RTH_MINUTES):
            ts = int((start + timedelta(minutes=k)).astimezone(UTC).timestamp()) * 10**9
            o, c = p[k] * 0.25, p[k + 1] * 0.25
            minute = 8 * 60 + 30 + k
            rows.append({
                "ts_event": ts, "open": o, "high": max(o, c), "low": min(o, c), "close": c,
                "volume": 100, "instrument_id": 4242, "raw_symbol": "MESZ5",
                "trade_date": day.isoformat(),
                "in_flatten_window": minute >= 15 * 60 + 10,
                "in_no_new_positions_window": minute >= 15 * 60 + 8,
                "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
                "gap_before_minutes": 0, "vendor_degraded_day": False,
            })
    return pd.DataFrame(rows)


def ct_hm(bar: Bar) -> tuple[int, int]:
    local = bar.open_ts_utc.astimezone(CT)
    return local.hour, local.minute


def exit_at_1500(bar: Bar, account: AccountView) -> tuple:
    if ct_hm(bar) == (15, 0) and account.position_micros:
        side = "sell" if account.position_micros > 0 else "buy"
        return (market_intent(bar, side, abs(account.position_micros)),)
    return ()


@dataclass(frozen=True)
class UnconditionalRth:
    """Enter at the 08:30 bar's decision, exit at the 15:00 bar's: no conditioning at all."""

    side: str = "buy"
    qty: int = 1
    name: str = "unconditional_rth"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if ct_hm(bar) == (8, 30) and account.position_micros == 0:
            return (market_intent(bar, self.side, self.qty),)
        return exit_at_1500(bar, account)


@dataclass(frozen=True)
class SignalFollower:
    """Trade the direction of the 09:00 bar (close vs open), exit at the 15:00 bar."""

    name: str = "signal_follower"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if ct_hm(bar) == (9, 0) and account.position_micros == 0 and bar.close != bar.open:
            return (market_intent(bar, "buy" if bar.close > bar.open else "sell", 1),)
        return exit_at_1500(bar, account)


def screen(paths: list[np.ndarray], factory) -> ScreeningReport:
    return screen_frame(session_frame(paths), "synthetic", factory, "synthetic",
                        splice_trade_dates=())


# ------------------------------------------------ 1: injected drift, unconditional ----
def test_unconditional_long_on_injected_drift_fails_the_drift_benchmark() -> None:
    moves = [100, 100, -20] * 20  # mean +60 ticks per session
    report = screen([path_ticks(m) for m in moves], UnconditionalRth)

    # The old gate alone is fooled: 40 winners at ~+$122, 20 losers at ~-$28.
    assert report.n_trips == 60 and report.exposure == "long_only"
    assert report.zero_edge.win_probability == pytest.approx(2 / 3)
    assert report.zero_edge.robust == "pass"
    # The drift benchmark IS this strategy: every tick of gross is the window's average path.
    # Gross = 40 x 100 - 20 x 20 = 3,600 ticks x $1.25 = $4,500.
    assert report.drift.candidate_gross_usd == pytest.approx(4_500.0)
    assert report.drift.drift_gross_usd == pytest.approx(4_500.0)
    assert report.drift.excess_gross_usd == pytest.approx(0.0, abs=1e-6)
    assert report.drift.drift_share_of_gross == pytest.approx(1.0)
    assert not report.drift.passes
    assert report.drift_verdict == "fail" and report.verdict == "fail"
    # The literal benchmark from the Stage B segment table agrees: +60 ticks per session.
    assert report.session_benchmark.n_sessions == 60
    assert report.session_benchmark.drift_ticks_per_session == pytest.approx(60.0)


def test_short_only_rider_in_a_falling_market_is_not_exempt() -> None:
    moves = [-100, -100, 20] * 20  # the mirror image: mean -60 ticks per session
    report = screen([path_ticks(m) for m in moves], lambda: UnconditionalRth(side="sell"))

    assert report.exposure == "short_only"
    assert report.zero_edge.robust == "pass"  # the old gate is fooled the same way
    # A short is charged NEGATIVE drift: -1 micro x -60 ticks x 60 days = +3,600 ticks.
    assert report.drift.drift_gross_usd == pytest.approx(4_500.0)
    assert report.drift.excess_gross_usd == pytest.approx(0.0, abs=1e-6)
    assert report.drift_verdict == "fail" and report.verdict == "fail"
    assert report.session_benchmark.short_net_usd > 0 > report.session_benchmark.long_net_usd


# ----------------------------------------- 2: zero drift, genuine conditional signal ----
CYCLE = [(+1, 100)] * 4 + [(-1, -100)] * 4 + [(+1, -40), (-1, 40)]  # (signal, move)


def test_conditional_signal_without_drift_is_unaffected_by_the_check() -> None:
    paths = [path_ticks(move, signal, move_start=31) for signal, move in CYCLE * 6]
    report = screen(paths, SignalFollower)

    # Up and down sessions cancel minute by minute: the counterpart earns exactly $0.
    assert report.drift.drift_gross_usd == pytest.approx(0.0, abs=1e-9)
    assert report.session_benchmark.drift_ticks_per_session == pytest.approx(0.0)
    # So drift adjustment changes nothing: adjusted p/R are the raw p/R.
    assert report.drift_adjusted.win_probability == report.zero_edge.win_probability == 0.8
    assert report.drift_adjusted.win_loss_ratio == pytest.approx(report.zero_edge.win_loss_ratio)
    assert report.exposure == "both"
    # Gross = 6 x (8 x 100 - 2 x 40) = 4,320 ticks = $5,400; all of it is excess.
    assert report.drift.excess_gross_usd == pytest.approx(5_400.0)
    assert report.drift.excess_lower_bounds_usd[DRIFT_CONFIDENCE] > 0
    assert report.zero_edge.robust == report.drift_adjusted.robust == "pass"
    assert report.drift_verdict == "pass" and report.verdict == "pass"
    assert report.reasons == ()


# -------------------------------------------------- attribution arithmetic, to the cent ----
def test_drift_attribution_to_the_cent() -> None:
    # Two sessions; day A rises 8 ticks and day B 4 ticks between the 08:31 and 15:01
    # opens. A 2-micro unconditional long on each day is charged the AVERAGE move:
    # 2 x (8 + 4) / 2 x 125 = 1,500 cents per trip. Excess: day A 2 x 8 x 125 - 1,500 =
    # +500, day B 2 x 4 x 125 - 1,500 = -500.
    frame = session_frame([path_ticks(8), path_ticks(4)])
    config = EngineConfig(restart_on_terminal=True, roll_blackout=NO_ROLL_BLACKOUT)

    result = run_backtest(iter_bars(frame), UnconditionalRth(qty=2), config,
                          load_slippage_table())
    trips = attribute_drift(result, build_drift_path(frame, NO_ROLL_BLACKOUT))

    assert [t.trade_date for t in trips] == DAYS[:2]
    assert [t.gross_cents for t in trips] == [2_000, 1_000]
    assert [t.drift_cents for t in trips] == [pytest.approx(1_500.0)] * 2
    assert [t.excess_cents for t in trips] == [pytest.approx(500.0), pytest.approx(-500.0)]
    # Adjusted net = net - drift; net carries both sides' commission and slippage.
    assert trips[0].adjusted_net_cents == pytest.approx(trips[0].net_cents - 1_500.0)


def test_minute_of_trade_date_counts_from_the_1700_ct_reopen() -> None:
    reopen = int(datetime(2025, 9, 1, 17, 0, tzinfo=CT).astimezone(UTC).timestamp()) * 10**9
    rth_open = int(datetime(2025, 9, 2, 8, 30, tzinfo=CT).astimezone(UTC).timestamp()) * 10**9
    assert minute_of_trade_date(reopen).tolist() == [0]
    assert minute_of_trade_date(rth_open).tolist() == [15 * 60 + 30]  # 17:00 -> 08:30


# ----------------------------------------------------------- bootstrap bound edges ----
def test_bootstrap_bound_of_a_constant_is_the_constant() -> None:
    bounds = bootstrap_mean_lower_bounds(np.full(50, 5.0), n_resamples=200)
    assert all(v == pytest.approx(5.0) for v in bounds.values())


def test_bootstrap_bound_of_zero_excess_is_not_positive() -> None:
    # An exactly-zero excess (the unconditional case) must never clear: 0 is not > 0.
    bounds = bootstrap_mean_lower_bounds(np.zeros(50), n_resamples=200)
    assert bounds[DRIFT_CONFIDENCE] == 0.0


def test_bootstrap_bound_is_below_the_mean_for_noisy_series() -> None:
    rng = np.random.default_rng(1)
    series = rng.normal(1.0, 10.0, 300)
    bounds = bootstrap_mean_lower_bounds(series, n_resamples=2_000)
    assert bounds[0.95] < bounds[0.90] < bounds[0.80] < series.mean()


# ------------------------------------ roll-blackout dates stay out of the path ----
def test_splice_day_is_excluded_from_the_path_and_guarded() -> None:
    # Regression for the Task 4 finding: the continuous series jumps ~+215 ticks at a
    # contract splice INSIDE a trade date. Day 2 here splices mid-session with a +200 tick
    # jump. Left in, it would add +200 / 3 ticks to the average path; excluded (as the
    # runner excludes every roll-blackout date), the path is the two clean days only.
    frame = session_frame([path_ticks(10), path_ticks(20), path_ticks(30)])
    day2 = frame["trade_date"] == DAYS[1].isoformat()
    late = day2 & (frame.index.to_series() % RTH_MINUTES >= 200)
    frame.loc[late, "instrument_id"] = 4243
    frame.loc[late, ["open", "high", "low", "close"]] += 50.0  # +200 ticks

    with pytest.raises(ValueError, match="contract splice inside path day"):
        build_drift_path(frame, NO_ROLL_BLACKOUT)
    path = build_drift_path(frame, frozenset({DAYS[1]}))
    assert path.trade_dates == (DAYS[0], DAYS[2])
    # Mean move 08:31 open -> 15:01 open over days 1 and 3: (10 + 30) / 2 = 20 ticks.
    assert path.mean_move_ticks((15 * 60 + 31, "open"), (22 * 60 + 1, "open")) == 20.0
