"""The shared screening runner: the one way to screen a hypothesis (Stage D.1a, Task 3).

    from screening import screen_candidate, fold_train_window, train_union_window
    report = screen_candidate("X-H1 my idea", MyStrategy, fold_train_window(0))

Read docs/SCREENING.md first. In one paragraph: a future research session hands
this function a label, a zero-argument strategy factory and a TRAIN window, and gets
back a frozen ``ScreeningReport`` whose ``verdict`` is "pass" only if the candidate
clears BOTH benchmarks:
1. the robust zero-edge power gate (``funnel.power_gate.screen``, unchanged) on its
   measured p/R/T; and
2. the drift benchmark (``screening.drift``): (a) its excess over its own
   unconditional counterpart is significant at one-sided 95%, and (b) its
   drift-adjusted p/R still pass the robust gate.

What the runner fixes, so no session has to remember it:
- ONE ``EngineConfig`` (``canonical_engine_config``): restart on terminal, XFA phase,
  mean slippage, hindsight fields masked, and the roll blackout (splice trade date plus
  the 2 sessions before it, from the vendor roll schedule). Stage D.1's family B diverged
  exactly here.
- The bars: the research slice only, through ``data.research_bars`` (which refuses
  holdout rows), restricted to TRAIN dates. A window with any date outside the 8
  folds' train dates is refused. Test-only dates are for out-of-sample evaluation,
  which is not a screen.
- The fill model: market orders (``market_intent``) and passive orders
  (``limit_intent``) both run through the same engine. When any passive fill occurs,
  the report carries ``sim.fill_model.PASSIVE_FILL_CAVEATS``.
- The measurement: ``screening.trips.measure``. T is snapped to the gate's grid
  {1, 2, 4}, and the approximation is flagged, the Stage D.1 convention.
- The drift benchmark, recomputed on the window's own bars.

``screen_frame`` is the same pipeline on a caller-supplied frame. It exists for the
synthetic known-answer tests; research code must not use it, because it skips the
train-date check.
"""

from __future__ import annotations

import functools
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from data.research_bars import RESEARCH_SERIES_PATH, load_research_bars
from data.splits import walk_forward_folds
from funnel.power_gate import POWER_GATE_JSON, screen
from screening.drift import (
    DRIFT_CONFIDENCE,
    DriftSignificance,
    SessionBenchmark,
    TripDrift,
    attribute_drift,
    build_drift_path,
    drift_significance,
    session_benchmark,
)
from screening.trips import measure, nearest_segments_per_day
from sim.costs import load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    EngineConfig,
    FillEvent,
    IntentEvent,
    daily_net_pnl,
    iter_bars,
    roll_blackout_dates,
    run_backtest,
    splice_trade_dates_from_parquet,
)
from sim.fill_model import PASSIVE_FILL_CAVEATS
from strategy.interface import NS_PER_BAR, Strategy

CANONICAL_ROLL_BLACKOUT_SESSIONS = 2
CANONICAL_PAYOUT_PATH = "standard"
CANONICAL_SLIPPAGE_STATISTIC = "mean"
COST_CAVEATS = (
    "costs are a LOWER BOUND: slippage rests on two days of MES book data (both now inside "
    "the sealed holdout) and excludes latency, adverse selection and queue position",
    "commission $1.22/round turn still needs confirmation at Topstep checkout (Stage A.2)",
)
DRIFT_CAVEAT = (
    "the drift benchmark removes the window's average path over the candidate's exposure: a "
    "purely clock-based unconditional hypothesis cannot clear it in-sample by construction"
)


def canonical_engine_config(splice_trade_dates: Sequence[date]) -> EngineConfig:
    """The one engine configuration every screen uses."""
    return EngineConfig(
        restart_on_terminal=True,
        roll_blackout=roll_blackout_dates(splice_trade_dates, CANONICAL_ROLL_BLACKOUT_SESSIONS),
        slippage_statistic=CANONICAL_SLIPPAGE_STATISTIC,
        mask_hindsight_fields=True,
    )


# ------------------------------------------------------------------ windows ----
@dataclass(frozen=True)
class ScreeningWindow:
    name: str
    trade_dates: tuple[date, ...]


@functools.cache
def _research_frame() -> tuple[pd.DataFrame, np.ndarray]:
    frame = load_research_bars(BAR_COLUMNS)
    days = pd.to_datetime(frame["trade_date"].astype(str)).dt.date.to_numpy()
    return frame, days


@functools.cache
def _folds() -> tuple:
    _, days = _research_frame()
    return tuple(walk_forward_folds(sorted(set(days))))


def fold_train_window(fold_index: int) -> ScreeningWindow:
    fold = _folds()[fold_index]
    return ScreeningWindow(f"fold{fold_index}_train", tuple(fold.train_dates))


def train_union_window() -> ScreeningWindow:
    """Every date in any fold's train window (Stage D.1's 289-day accounting window)."""
    return ScreeningWindow("train_union",
                           tuple(sorted({d for f in _folds() for d in f.train_dates})))


# ------------------------------------------------------------------- report ----
@dataclass(frozen=True)
class GateVerdicts:
    win_probability: float | None
    win_loss_ratio: float | None
    segments_per_day: int | None
    matched: str
    robust: str


@dataclass(frozen=True)
class ScreeningReport:
    label: str
    window: str
    n_dates: int
    first_date: date
    last_date: date
    blackout_dates_in_window: int
    n_trips: int
    trades_per_day: float
    segments_per_day_is_approximation: bool
    net_pnl_usd: float
    exposure: str  # "long_only" | "short_only" | "both" | "none"
    market_fills: int
    passive_fills: int
    passive_orders_placed: int
    zero_edge: GateVerdicts  # raw measured p/R through the existing gate
    drift_adjusted: GateVerdicts  # p/R with each trip's drift expectation removed
    drift: DriftSignificance
    session_benchmark: SessionBenchmark
    drift_verdict: str  # "pass" | "fail"
    verdict: str  # "pass" only if the zero-edge gate AND the drift benchmark both clear
    reasons: tuple[str, ...]
    caveats: tuple[str, ...]
    # Net P&L per window date, in window order, $0 on a date with no trading (Stage D.1b):
    # the series the multiple-comparisons accounting (DSR, t-hurdle, PBO) consumes.
    daily_net_usd: tuple[float, ...] = ()
    # Net USD per closed round trip, in ledger order (Stage D.1e): the per-trade series the
    # power calculation needs. Same trips, same order, as ``screening.trips.measure``.
    trip_pnls_usd: tuple[float, ...] = ()
    # Closed round trips per window date, in window order, 0 on a date with no trading
    # (Stage D.1e). A trip belongs to the trade date of its CLOSING fill, so these counts
    # partition ``trip_pnls_usd`` exactly as ``daily_net_usd`` partitions ``net_pnl_usd``.
    daily_n_trips: tuple[int, ...] = ()
    # Position size of every closed round trip, in ledger order (Stage D.1e): the maximum
    # absolute position, in micros, that trip ever held. Same trips, same order, as
    # ``trip_pnls_usd``, so a per-micro series divides each trip by its OWN size instead of by
    # one assumed size (most trials size 1 micro, but some size 1 to 5 micros by rule).
    trip_micros: tuple[int, ...] = ()

    def to_dict(self) -> dict:
        out = asdict(self)
        out["drift"]["excess_lower_bounds_usd"] = {
            f"c{round(c * 100)}": v for c, v in self.drift.excess_lower_bounds_usd.items()}
        return out


def _gate(p: float | None, r: float | None, trades_per_day: float, gate_json: Path
          ) -> GateVerdicts:
    if p is None or r is None:
        return GateVerdicts(p, r, None, "unmeasurable", "unmeasurable")
    t = nearest_segments_per_day(trades_per_day)
    matched = screen(CANONICAL_PAYOUT_PATH, p, r, t, gate_json=gate_json)["verdict"]
    robust = screen(CANONICAL_PAYOUT_PATH, p, r, t, gate_json=gate_json, robust=True)["verdict"]
    return GateVerdicts(p, r, t, matched, robust)


def _p_and_r(pnls: Sequence[float]) -> tuple[float | None, float | None]:
    """Same definitions as ``screening.trips.measure``: ties are neither wins nor losses."""
    if not pnls:
        return None, None
    wins = [x for x in pnls if x > 0]
    losses = [x for x in pnls if x < 0]
    p = len(wins) / len(pnls)
    if not wins or not losses:
        return p, None
    return p, (sum(wins) / len(wins)) / abs(sum(losses) / len(losses))


def _exposure(fills: tuple[FillEvent, ...]) -> str:
    long_ = any(f.position_after > 0 for f in fills)
    short = any(f.position_after < 0 for f in fills)
    return {(True, True): "both", (True, False): "long_only", (False, True): "short_only",
            (False, False): "none"}[(long_, short)]


def _daily_net_usd(result, dates: Sequence[date]) -> tuple[float, ...]:
    days = daily_net_pnl(result)
    by_date = days.groupby("trade_date")["day_net_cents"].sum() / 100.0
    return tuple(float(by_date.get(d, 0.0)) for d in dates)


def _fill_trade_date(bar_ts: np.ndarray, bar_days: np.ndarray, fill_ts_ns: int) -> date:
    """The engine's own trade date for a fill: the ``trade_date`` column of the bar the fill
    happened on, which is what ``sim.engine.daily_net_pnl`` attributes the fill's P&L to
    (``DayCloseEvent.trade_date`` is the run's current ``bar.trade_date``).

    A fill's ``fill_ts_ns`` is normally the fill bar's OPEN. The two forced-flatten paths that
    close at a bar's CLOSE (``_Run.fill_at_close``: a session that ended with no flatten-window
    decision time, and the end-of-data flatten) stamp the fill with that bar's DECISION time,
    one bar later; both belong to that bar's trade date, the one ``close_day`` bills."""
    for candidate in (fill_ts_ns, fill_ts_ns - NS_PER_BAR):
        i = int(np.searchsorted(bar_ts, candidate))
        if i < len(bar_ts) and int(bar_ts[i]) == candidate:
            return date.fromisoformat(str(bar_days[i]))
    raise AssertionError(f"fill at {fill_ts_ns} matches no bar in the window's frame")


def _daily_n_trips(result, frame: pd.DataFrame, dates: Sequence[date]) -> tuple[int, ...]:
    """Closed round trips per window date. The walk is ``trips.round_trip_pnls_usd``'s: a trip
    is the fill run ending at ``position_after == 0``, and it lands on its closing fill's date."""
    bar_ts = frame["ts_event"].to_numpy(dtype="int64")
    bar_days = frame["trade_date"].to_numpy()
    counts: dict[date, int] = {}
    in_trip = False
    for fill in result.events(FillEvent):
        in_trip = True
        if fill.position_after == 0:
            day = _fill_trade_date(bar_ts, bar_days, fill.fill_ts_ns)
            counts[day] = counts.get(day, 0) + 1
            in_trip = False
    if in_trip:
        raise AssertionError("_daily_n_trips: a trip never closed -- engine invariant broken")
    return tuple(counts.get(d, 0) for d in dates)


def _trip_micros(result) -> tuple[int, ...]:
    """Micros held by every closed round trip, in ledger order. The walk is
    ``trips.round_trip_pnls_usd``'s, so trip i here is trip i of ``trip_pnls_usd``: a trip is the
    fill run ending at ``position_after == 0``, and its size is the largest absolute position it
    ever held, ``max |position_after|`` over its fills. A trip that scales in is measured at its
    largest size, which is the divisor that turns its whole net into ticks per micro."""
    sizes: list[int] = []
    peak = 0
    in_trip = False
    for fill in result.events(FillEvent):
        in_trip = True
        peak = max(peak, abs(fill.position_after))
        if fill.position_after == 0:
            if peak == 0:
                raise AssertionError("_trip_micros: a trip never held a position -- engine "
                                     "invariant broken")
            sizes.append(peak)
            peak = 0
            in_trip = False
    if in_trip:
        raise AssertionError("_trip_micros: a trip never closed -- engine invariant broken")
    return tuple(sizes)


# ------------------------------------------------------------------- screen ----
def screen_frame(
    frame: pd.DataFrame, label: str, factory: Callable[[], Strategy], window_name: str,
    splice_trade_dates: Sequence[date], gate_json: Path = POWER_GATE_JSON,
) -> ScreeningReport:
    """The full pipeline on ``frame`` (all of whose trade dates form the window). For the
    synthetic known-answer tests; research code calls ``screen_candidate``."""
    table = load_slippage_table()
    config = canonical_engine_config(splice_trade_dates)
    path = build_drift_path(frame, config.roll_blackout)
    dates = tuple(sorted(set(pd.to_datetime(frame["trade_date"].astype(str)).dt.date)))
    result = run_backtest(iter_bars(frame), factory(), config, table)

    m = measure(result, len(dates))
    trips: tuple[TripDrift, ...] = attribute_drift(result, path)
    if len(trips) != m.n_trips:
        raise AssertionError("drift attribution and trip measurement disagree on trip count")
    zero_edge = _gate(m.win_probability, m.win_loss_ratio, m.trades_per_day, gate_json)
    adj_p, adj_r = _p_and_r([t.adjusted_net_cents / 100.0 for t in trips])
    adjusted = _gate(adj_p, adj_r, m.trades_per_day, gate_json)
    significance = drift_significance(trips, dates)

    reasons = []
    if zero_edge.robust != "pass":
        reasons.append(f"zero-edge gate (robust) on measured p/R: {zero_edge.robust}")
    if not significance.passes:
        reasons.append(
            f"drift benchmark: excess over the unconditional counterpart not significant at "
            f"one-sided {DRIFT_CONFIDENCE:.0%} (lower bound "
            f"${significance.excess_lower_bounds_usd[DRIFT_CONFIDENCE]:.2f}/day)")
    if adjusted.robust != "pass":
        reasons.append(f"drift benchmark: zero-edge gate (robust) on drift-adjusted p/R: "
                       f"{adjusted.robust}")
    drift_ok = significance.passes and adjusted.robust == "pass"

    fills = result.events(FillEvent)
    passive_fills = sum(f.order_type == "passive" for f in fills)
    caveats = list(COST_CAVEATS) + [DRIFT_CAVEAT]
    t_approx = zero_edge.segments_per_day is not None and (
        zero_edge.segments_per_day != round(m.trades_per_day))
    if t_approx:
        caveats.append(f"trades/day {m.trades_per_day:.2f} screened at the nearest gate grid "
                       f"point T={zero_edge.segments_per_day}")
    if passive_fills:
        caveats.extend(PASSIVE_FILL_CAVEATS)
    return ScreeningReport(
        label=label, window=window_name, n_dates=len(dates), first_date=dates[0],
        last_date=dates[-1],
        blackout_dates_in_window=len(config.roll_blackout & set(dates)),
        n_trips=m.n_trips, trades_per_day=m.trades_per_day,
        segments_per_day_is_approximation=t_approx, net_pnl_usd=round(m.net_pnl_usd, 2),
        exposure=_exposure(fills), market_fills=len(fills) - passive_fills,
        passive_fills=passive_fills,
        passive_orders_placed=sum(e.accepted and e.limit_price is not None
                                  for e in result.events(IntentEvent)),
        zero_edge=zero_edge, drift_adjusted=adjusted, drift=significance,
        session_benchmark=session_benchmark(frame, table, config.roll_blackout),
        drift_verdict="pass" if drift_ok else "fail",
        verdict="pass" if (zero_edge.robust == "pass" and drift_ok) else "fail",
        reasons=tuple(reasons), caveats=tuple(caveats),
        daily_net_usd=_daily_net_usd(result, dates),
        trip_pnls_usd=m.trip_pnls_usd,
        daily_n_trips=_daily_n_trips(result, frame, dates),
        trip_micros=_trip_micros(result),
    )


def screen_candidate(label: str, factory: Callable[[], Strategy],
                     window: ScreeningWindow) -> ScreeningReport:
    """THE entry point for hypothesis screening. See docs/SCREENING.md."""
    if not window.trade_dates:
        raise ValueError("empty screening window")
    outside = sorted(set(window.trade_dates) - set(train_union_window().trade_dates))
    if outside:
        raise ValueError(f"window {window.name!r} has {len(outside)} dates outside every fold's "
                         f"train window (first: {outside[0]}); screening runs on train dates only")
    frame, days = _research_frame()
    mask = np.isin(days, np.array(window.trade_dates, dtype=object))
    missing = set(window.trade_dates) - set(days[mask])
    if missing:
        raise ValueError(f"no bars for {len(missing)} window dates, e.g. {min(missing)}")
    return screen_frame(frame[mask].reset_index(drop=True), label, factory, window.name,
                        splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH))
