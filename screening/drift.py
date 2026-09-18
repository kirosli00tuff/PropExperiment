"""Drift benchmark: does a candidate beat its own unconditional counterpart? (Stage D.1a, Task 1)

WHY THIS EXISTS. ``funnel.power_gate`` compares a candidate against a zero-edge coin
flipper whose drift was deliberately removed (``funnel/null_generator.py``). So the gate
grades a directional strategy's share of the sample's drift as if it were edge. Stage D.1
found that the strongest-looking trials were unconditional longs earning the research
window's drift: +13.65 ticks per RTH session (Stage B, Task 2; ``calibration_summary``
on the 310 research sessions reproduces 13.648). A second benchmark is needed that an
unconditional position clears only by luck.

THE BENCHMARK, per window (recomputed on exactly the dates being screened, never
globally; the per-fold RTH drift ranges from -5.1 to +19.5 ticks/session):
- ``DriftPath``: the window's average price path by minute of the trade date (17:00 CT
  ETH open through the 16:00 CT halt), built from the same bars the candidate trades.
- A candidate is charged, for every interval it holds a position, what an
  UNCONDITIONAL position of the same size and sign would have earned on average over
  the same clock interval: position x (mean over the window's days of P(t2) - P(t1)).
  Summed per round trip, that is the trip's drift expectation.
- For a candidate held long from the RTH open to the flatten, this is exactly the
  "hold long through the RTH session every day" benchmark: ``session_benchmark``
  reports that literal figure (and its mirror-image short) from the Stage B segment
  table, so the two constructions are checked against each other in the tests. The
  exposure-matched form is what the verdict uses, because it gives the right answer
  where the literal one cannot:
  * ETH exposure (A-H1, the A-H4 ETH leg) is charged the ETH drift, not the RTH drift;
  * a short is charged NEGATIVE drift automatically (the mirror benchmark), so a
    short-only candidate is never exempt: in a down-drifting fold (fold 4: -5.1 ticks)
    a short rider is caught exactly as a long rider is in an up-drifting one;
  * a candidate exposed one hour a day is compared with one hour of drift, not a
    session's worth. A literal "beat buy-and-hold" test would fail every
    market-neutral edge in an up-drifting window and pass any flat strategy in a
    down-drifting one.
- The path uses only the window's TRADABLE dates: roll-blackout dates are excluded.
  No position can exist on them in this harness, and every contract splice falls on
  one. The continuous series jumps +206..+226 ticks at each splice, INSIDE a trade date
  (18:00/19:00 CT), and the roll-week RTH sessions of this sample were sharply negative.
  Averaging either into the path mis-charged the Stage D.1 trials: the A-H4 ETH leg was
  over-charged on every fold, and the RTH leg under-charged, by up to ~$12/day. Found
  in the Task 4 regression; see progress.md, 2026-09-18 Stage D.1a. A path day that
  still holds two contracts raises.
- Costs cancel: the unconditional counterpart makes the same trips at the same times,
  so it pays the same commission and slippage. The excess is therefore gross.

WHAT "CLEARING" MEANS. Both must hold (composed in ``screening.runner``):
(a) SIGNIFICANCE. The mean daily excess over the benchmark is positive at one-sided
    95% confidence. The bound is a percentile stationary block bootstrap (Politis &
    Romano; mean block 5 days, the null generator's volatility-clustering assumption)
    over every date in the window, with 0 on days without a trip. 10,000 resamples at
    a fixed seed.
(b) SUFFICIENCY. With each trip's drift expectation subtracted from its net P&L, the
    re-measured p/R still pass the robust zero-edge power gate. This applies the
    existing gate to drift-free P&L, which is exactly the fix Stage D.1 asked for.
    The runner applies (b), since it owns the gate lookup.

WHY NOT A SIMPLE DOMINANCE CHECK ("excess > 0"). For an unconditional clock strategy,
the excess over its own counterpart is a mean-zero residual by construction; summed
over the window it is about $0. A dominance check would therefore pass such a candidate
about half the time, on noise alone. That is a coin flip on exactly the case the check
exists to catch. The confidence level is 95% rather than the power gate's 80% for two
reasons. The power gate's leniency buys power against a stringent funnel null. This is
a plain one-sample test on a noisy mean, and at 80% it would wave through one in five
drift-plus-noise candidates. And nothing below t ~ 1.645 survives the downstream
Deflated Sharpe accounting anyway: at N = 23 trials the expected maximum null Sharpe is
far above that (Stage D.1, Task 4). So the stricter level discards nothing that could
have survived.

A CONSEQUENCE, stated plainly: a purely clock-based unconditional hypothesis (hold
long 02:00-03:00 ET every day) cannot clear this check in-sample, however real its
seasonality, because in-sample the average path IS its whole P&L. A clock-seasonality
claim needs evidence of persistence out of sample, not an in-sample screen. That is
the intended behaviour: the check exists so that "the sample went up" is never graded
as edge.

APPROXIMATIONS. A passive or MLL-liquidation fill happens inside its bar; its drift is
anchored at that bar's open, which moves the expectation by at most one minute's
average drift (~0.02 ticks). Where a minute is missing on some days (18 single
overnight minutes in the research slice), the mean move between two minutes uses only
the days that have both.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from funnel.null_generator import (
    DEFAULT_MEAN_BLOCK_DAYS,
    REQUIRED_COLUMNS,
    build_segment_table,
    stationary_bootstrap_indices,
)
from sim.costs import CT, SlippageTable
from sim.engine import BacktestResult, FillEvent
from sim.fill_model import MES_TICK_VALUE_CENTS, side_cost_at_ct_minute

MINUTES_PER_DAY = 24 * 60
SESSION_OPEN_MINUTE_CT = 17 * 60  # a CME trade date starts at the 17:00 CT reopen
NS_PER_MINUTE = 60_000_000_000
DRIFT_CONFIDENCE = 0.95
REPORTED_CONFIDENCES = (0.80, 0.90, 0.95)
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_918
CLOSE_PRICED_REASONS = ("forced_flatten_session_end", "end_of_data")  # filled at a bar CLOSE
PATH_COLUMNS = ("ts_event", "open", "close", "trade_date", "instrument_id")


def _ticks(prices: np.ndarray) -> np.ndarray:
    return np.rint(np.asarray(prices, dtype=float) / 0.25)


@dataclass(frozen=True)
class DriftPath:
    """The window's price path, (days x minutes-of-trade-date), NaN where no bar exists."""

    trade_dates: tuple[date, ...]
    open_ticks: np.ndarray
    close_ticks: np.ndarray
    locator: dict[int, tuple[int, int]]  # bar ts_event_ns -> (day row, minute of trade date)

    def mean_move_ticks(self, start: tuple[int, str], end: tuple[int, str]) -> float:
        """Average move, over every window day with both prices, from ``start`` to ``end``;
        each point is (minute of trade date, "open" | "close")."""
        a = (self.open_ticks if start[1] == "open" else self.close_ticks)[:, start[0]]
        b = (self.open_ticks if end[1] == "open" else self.close_ticks)[:, end[0]]
        both = ~np.isnan(a) & ~np.isnan(b)
        if not both.any():
            raise ValueError(f"no window day has prices at both {start} and {end}")
        return float((b[both] - a[both]).mean())


def minute_of_trade_date(ts_ns: np.ndarray | int) -> np.ndarray:
    """Minutes since the 17:00 CT reopen that starts the trade date (0 .. 1379)."""
    local = pd.to_datetime(np.atleast_1d(ts_ns), utc=True).tz_convert(CT)
    minute = np.asarray(local.hour * 60 + local.minute)
    return (minute - SESSION_OPEN_MINUTE_CT) % MINUTES_PER_DAY


def build_drift_path(bars: pd.DataFrame, excluded_dates: frozenset[date]) -> DriftPath:
    """Pure: the window's bars -> its average-path lookup, over every date NOT in
    ``excluded_dates`` (the runner passes the roll blackout)."""
    missing = [c for c in PATH_COLUMNS if c not in bars.columns]
    if missing:
        raise ValueError(f"bars missing columns {missing}")
    all_days = pd.to_datetime(bars["trade_date"].astype(str)).dt.date.to_numpy()
    keep = ~np.isin(all_days, np.array(sorted(excluded_dates), dtype=object))
    bars, days = bars[keep], all_days[keep]
    per_day = pd.Series(bars["instrument_id"].to_numpy()).groupby(days).nunique()
    if (per_day > 1).any():
        raise ValueError(f"contract splice inside path day(s) {list(per_day[per_day > 1].index)}"
                         ": exclude roll-blackout dates from the drift path")
    ts = bars["ts_event"].to_numpy(np.int64)
    order = tuple(sorted(set(days)))
    row_of = {d: i for i, d in enumerate(order)}
    rows = np.array([row_of[d] for d in days], dtype=np.int64)
    minutes = minute_of_trade_date(ts)
    opens = np.full((len(order), MINUTES_PER_DAY), np.nan)
    closes = np.full((len(order), MINUTES_PER_DAY), np.nan)
    opens[rows, minutes] = _ticks(bars["open"].to_numpy())
    closes[rows, minutes] = _ticks(bars["close"].to_numpy())
    locator = dict(zip(ts.tolist(), zip(rows.tolist(), minutes.tolist(), strict=True),
                       strict=True))
    return DriftPath(order, opens, closes, locator)


@dataclass(frozen=True)
class TripDrift:
    """Per closed round trip, aligned with ``screening.trips.round_trip_pnls_usd``."""

    trade_date: date
    gross_cents: int
    cost_cents: int
    drift_cents: float  # what the unconditional counterpart earned over the same intervals

    @property
    def net_cents(self) -> int:
        return self.gross_cents - self.cost_cents

    @property
    def excess_cents(self) -> float:
        """Gross over the counterpart; costs cancel (same trips, same costs)."""
        return self.gross_cents - self.drift_cents

    @property
    def adjusted_net_cents(self) -> float:
        """Net P&L with the drift expectation removed: what the zero-edge gate grades."""
        return self.net_cents - self.drift_cents


def _fill_point(fill: FillEvent, path: DriftPath) -> tuple[int, int, str]:
    close_priced = fill.reason in CLOSE_PRICED_REASONS
    bar_ts = fill.fill_ts_ns - NS_PER_MINUTE if close_priced else fill.fill_ts_ns
    if bar_ts not in path.locator:
        raise ValueError(f"fill at {fill.fill_ts_ns} is on a date outside the drift path "
                         "(a roll-blackout date should never hold a position)")
    row, minute = path.locator[bar_ts]
    return row, minute, "close" if close_priced else "open"


def attribute_drift(result: BacktestResult, path: DriftPath) -> tuple[TripDrift, ...]:
    """Walk the fills in ledger order; charge each held interval its average-path move."""
    cache: dict[tuple, float] = {}
    trips: list[TripDrift] = []
    position = 0
    previous: tuple[int, int, str] | None = None
    trip_row = 0
    gross = cost = 0
    drift = 0.0
    for fill in result.events(FillEvent):
        point = _fill_point(fill, path)
        if position:
            assert previous is not None
            if previous[0] != point[0]:
                raise ValueError("a position spanned two trade dates; the engine forbids it")
            key = (previous[1], previous[2], point[1], point[2])
            if key not in cache:
                cache[key] = path.mean_move_ticks(key[:2], key[2:])
            drift += position * cache[key] * MES_TICK_VALUE_CENTS
        else:
            trip_row = point[0]
        gross += fill.gross_realized_cents
        cost += fill.commission_cents + fill.slippage_cents
        position, previous = fill.position_after, point
        if position == 0:
            trips.append(TripDrift(path.trade_dates[trip_row], gross, cost, drift))
            gross = cost = 0
            drift = 0.0
    if position:
        raise ValueError("a trip never closed: the engine flattens everything at the end")
    return tuple(trips)


def daily_series_usd(trips: tuple[TripDrift, ...], dates: tuple[date, ...],
                     attr: str) -> np.ndarray:
    """One value per window date (0 where no trip), in dollars, from a TripDrift attribute."""
    index = {d: i for i, d in enumerate(dates)}
    out = np.zeros(len(dates))
    for trip in trips:
        out[index[trip.trade_date]] += getattr(trip, attr) / 100.0
    return out


def bootstrap_mean_lower_bounds(
    series: np.ndarray, confidences: tuple[float, ...] = REPORTED_CONFIDENCES,
    n_resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED,
    mean_block_days: float = DEFAULT_MEAN_BLOCK_DAYS,
) -> dict[float, float]:
    """One-sided lower confidence bounds on the mean (percentile stationary bootstrap)."""
    values = np.asarray(series, dtype=float)
    if len(values) < 2:
        raise ValueError("need at least two days to bootstrap a mean")
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples)
    for i in range(n_resamples):
        means[i] = values[stationary_bootstrap_indices(rng, len(values), len(values),
                                                       mean_block_days)].mean()
    return {c: float(np.quantile(means, 1.0 - c)) for c in confidences}


@dataclass(frozen=True)
class SessionBenchmark:
    """The literal benchmark: 1 micro held through the RTH session every window day."""

    n_sessions: int
    drift_ticks_per_session: float
    long_net_usd: float
    short_net_usd: float  # the mirror image, for short-only candidates


def session_benchmark(bars: pd.DataFrame, table: SlippageTable,
                      excluded_dates: frozenset[date]) -> SessionBenchmark:
    """Reuses the Stage B calibration (``build_segment_table``, one segment per day) on the
    window's own tradable bars, then prices both legs with the market-order cost model."""
    days = pd.to_datetime(bars["trade_date"].astype(str)).dt.date.to_numpy()
    tradable = bars[~np.isin(days, np.array(sorted(excluded_dates), dtype=object))]
    seg = build_segment_table(tradable.loc[:, list(REQUIRED_COLUMNS)], 1)
    moves = seg.move_ticks[:, 0].astype(float)
    costs = np.array([
        side_cost_at_ct_minute(table, int(a), 1).total_cents
        + side_cost_at_ct_minute(table, int(b) % MINUTES_PER_DAY, 1).total_cents
        for a, b in zip(seg.entry_minute_ct[:, 0], seg.exit_minute_ct[:, 0], strict=True)])
    gross = moves * MES_TICK_VALUE_CENTS
    return SessionBenchmark(
        n_sessions=seg.n_days,
        drift_ticks_per_session=float(moves.mean()) if seg.n_days else 0.0,
        long_net_usd=float((gross - costs).sum() / 100.0),
        short_net_usd=float((-gross - costs).sum() / 100.0),
    )


@dataclass(frozen=True)
class DriftSignificance:
    candidate_gross_usd: float
    drift_gross_usd: float
    excess_gross_usd: float
    drift_share_of_gross: float | None  # drift / gross; about 1.0 means "all drift"
    excess_daily_mean_usd: float
    excess_lower_bounds_usd: dict[float, float]
    passes: bool  # lower bound at DRIFT_CONFIDENCE > 0


def drift_significance(trips: tuple[TripDrift, ...], dates: tuple[date, ...]
                       ) -> DriftSignificance:
    excess = daily_series_usd(trips, dates, "excess_cents")
    gross = sum(t.gross_cents for t in trips) / 100.0
    drift = sum(t.drift_cents for t in trips) / 100.0
    bounds = bootstrap_mean_lower_bounds(excess)
    return DriftSignificance(
        candidate_gross_usd=gross,
        drift_gross_usd=drift,
        excess_gross_usd=gross - drift,
        drift_share_of_gross=(drift / gross) if abs(gross) > 1e-9 else None,
        excess_daily_mean_usd=float(excess.mean()),
        excess_lower_bounds_usd=bounds,
        passes=bounds[DRIFT_CONFIDENCE] > 0.0,
    )
