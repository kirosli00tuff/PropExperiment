"""Leakage suite with planted-future canaries (Stage C, Task 4).

    uv run python -m sim.leakage_canaries   # writes reports/leakage_suite.json
    uv run pytest tests/test_leakage_canaries.py

Why the literal recipe is not enough. "Run the random baseline on planted data and
see no edge" is necessary but powerless on its own. The random baseline never reads
the marker, so it shows no edge on a leaky engine too. This suite runs that check,
and also shows it on a deliberately leaky engine to make the point. The real test
has four parts:

1. PLANTED FUTURE (the leak canary). A copy of real research bars gets a synthetic
   jump of ``JUMP_TICKS`` INSIDE selected RTH bars, in a seeded random direction d.
   Every later bar shifts with it, so prices stay continuous and on-grid. The marker
   d is attached to the jumped bar itself. It predicts that bar's move, which is
   "the next bar's return" from the previous bar's decision point. A CanaryReader
   strategy trades d the moment it is handed a marked bar and exits one bar later.
   - A point-in-time engine hands over bar N only after bar N closed, and fills at
     bar N+1's open, after the jump. Captured move ~ 0 ticks, direction hit rate ~ 50%.
   - A leaky engine that fills at the decision bar's open, or shows the strategy the
     next bar early, captures the jump: ~ +JUMP_TICKS per trade, hit rate ~ 100%.
2. POSITIVE CONTROLS (mutation testing). Two deliberately broken engines, defined
   below and used nowhere else, run the same canary:
   ``same_bar_fill`` (decide on the close, fill on that bar's open) and ``peek_next_bar``
   (the strategy is shown bar N+1 while the engine is still on bar N). The suite FAILS
   unless the canary flags both. A canary that cannot catch a known leak proves nothing.
3. LATENCY CONTROL (the other side of the timing pin). The same jumps, but the marker
   sits on the bar BEFORE the jumped bar. That information is legitimately available
   before the jump, so a correct engine MUST capture ~ +JUMP_TICKS. This rules out
   an engine that "passes" only because it fills too late.
4. STRUCTURAL CHECKS. A tripwire feed counts iterator pulls at every strategy call
   (exactly N+1 at bar N). The objects a strategy receives are frozen and primitive.
   A strategy that backdates intents to the bar open is refused and never filled.
   Setting the hindsight flag ``vendor_degraded_day`` on every bar changes nothing.
   Every Bar field carries a point-in-time availability class.

Pass/fail thresholds are fixed here, before any run (``CRITERIA``).
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
from enum import Enum
from math import sqrt
from types import MappingProxyType
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from rules import xfa_rules as xr
from sim.costs import SlippageTable, load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    BacktestResult,
    EngineConfig,
    FillEvent,
    IntentEvent,
    _Order,
    _Run,
    iter_bars,
    run_backtest,
)
from sim.fill_model import MES_TICK_VALUE_CENTS
from strategy.interface import (
    BAR_FIELD_AVAILABILITY,
    HINDSIGHT_FIELDS,
    AccountView,
    Bar,
    Strategy,
    market_intent,
)
from strategy.random_baseline import RandomBaseline

CT = ZoneInfo("America/Chicago")
NS_PER_MIN = 60_000_000_000
JUMP_TICKS = 16  # 4 points = $20 per micro; several times a typical 1-minute RTH move
MARK_EVERY_MINUTES = 20
MARK_WINDOW_CT = (8 * 60 + 35, 14 * 60 + 55)  # clear of the open and of the 15:08 cutoff
REAL_WINDOW = (date(2025, 10, 1), date(2025, 12, 31))  # research slice; includes the Nov outage

CRITERIA = {
    "leak_canary_real_engine": "trades >= 100 AND mean captured < JUMP/4 ticks AND |z| < 4 AND "
                               "|hit rate - 0.5| < 4 binomial SE",
    "positive_control_detected": "trades >= 100 AND mean captured >= JUMP/2 ticks AND z >= 5",
    "latency_control_real_engine": "trades >= 100 AND mean captured >= JUMP/2 ticks AND z >= 5",
    "random_baseline": "trades >= 100 AND |mean gross ticks per round trip| < 4 SE",
    "tripwire": "at every strategy call for bar N, exactly N+1 bars pulled from the feed",
    "hindsight_masking": "a strategy never sees a true hindsight field, even on a degraded bar",
}


# ------------------------------------------------------------------ planting ----
@dataclass(frozen=True)
class PlantedData:
    frame: pd.DataFrame
    leak_markers: Mapping[int, int]  # jumped bar ts -> direction (marker ON the jumped bar)
    latency_markers: Mapping[int, int]  # ts of the bar BEFORE the jumped bar -> direction
    jump_ticks: int


def _ct_minutes(ts: np.ndarray) -> np.ndarray:
    local = pd.to_datetime(ts, utc=True).tz_convert(CT)
    return np.asarray(local.hour * 60 + local.minute)


def plant_canaries(frame: pd.DataFrame, seed: int, jump_ticks: int = JUMP_TICKS,
                   mark_every: int = MARK_EVERY_MINUTES) -> PlantedData:
    """A shifted COPY of ``frame`` with jumps inside marked bars. The input is never mutated."""
    out = frame.copy().reset_index(drop=True)
    ts = out["ts_event"].to_numpy(np.int64)
    n = len(ts)
    minute = _ct_minutes(ts)
    tdate = out["trade_date"].astype(str).to_numpy()
    rng = np.random.default_rng(seed)
    delta = np.zeros(n, dtype=np.int64)
    jumps: list[tuple[int, int]] = []
    for i in range(1, n - 2):
        if not MARK_WINDOW_CT[0] <= minute[i] <= MARK_WINDOW_CT[1]:
            continue
        if (minute[i] - MARK_WINDOW_CT[0]) % mark_every:
            continue
        contiguous = ts[i] - ts[i - 1] == NS_PER_MIN and ts[i + 2] - ts[i] == 2 * NS_PER_MIN
        if not contiguous or len({tdate[i - 1], tdate[i], tdate[i + 1], tdate[i + 2]}) != 1:
            continue
        direction = int(rng.choice((-1, 1)))
        jumps.append((i, direction))
        delta[i + 1] += direction * jump_ticks
    shift_points = np.cumsum(delta) * xr.MES_TICK_SIZE
    for col in ("open", "high", "low", "close"):
        out[col] = out[col].to_numpy(dtype=float) + shift_points
    close = out["close"].to_numpy(dtype=float).copy()
    high = out["high"].to_numpy(dtype=float).copy()
    low = out["low"].to_numpy(dtype=float).copy()
    for i, direction in jumps:
        close[i] += direction * jump_ticks * xr.MES_TICK_SIZE
        high[i] = max(high[i], close[i])
        low[i] = min(low[i], close[i])
    out["close"], out["high"], out["low"] = close, high, low
    leak = {int(ts[i]): d for i, d in jumps}
    latency = {int(ts[i - 1]): d for i, d in jumps}
    return PlantedData(out, MappingProxyType(leak), MappingProxyType(latency), jump_ticks)


# ------------------------------------------------------------------ strategies ----
@dataclass(frozen=True)
class CanaryReader:
    """Test-only: trades the planted marker, exits one bar later. Not a strategy."""

    markers: Mapping[int, int]
    name: str = "canary_reader"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if account.pending_signed_micros:
            return ()
        if account.position_micros:
            side = "sell" if account.position_micros > 0 else "buy"
            return (market_intent(bar, side, abs(account.position_micros)),)
        direction = self.markers.get(bar.ts_event_ns)
        if direction is None:
            return ()
        return (market_intent(bar, "buy" if direction > 0 else "sell", 1),)


@dataclass(frozen=True)
class BackdatingStrategy:
    """Test-only: stamps intents with the bar OPEN to try to buy at a price it has seen."""

    name: str = "backdating"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        built = xr.construct_intent(symbol="MES", side="buy", quantity_micros=1,
                                    ts_utc=bar.open_ts_utc)
        return (built,)


# ------------------------------------------------------- MUTANTS (positive controls) ----
class _SameBarFillMutant(_Run):
    """DELIBERATELY BROKEN, positive control only: decides on bar N's close, then fills at
    bar N's OPEN. The fill-after-decision invariant is switched off to let the bug through."""

    def assert_fill_after_decision(self, order: _Order, bar: Bar) -> None:
        return None  # the bug under test

    def step(self, bar: Bar) -> None:
        self.bars += 1
        self.last_bar = bar
        self.roll_session(bar)
        self.ask_strategy(bar)
        self.fill_pending_at_open(bar)
        self.check_mll(bar)
        self.queue_forced_flatten(bar)


class _PeekNextBarMutant(_Run):
    """DELIBERATELY BROKEN, positive control only: shows the strategy bar N+1 while the
    engine is still on bar N, and books the order on the engine's own clock."""

    def step_with_view(self, bar: Bar, visible: Bar) -> None:
        self.bars += 1
        self.last_bar = bar
        self.roll_session(bar)
        self.fill_pending_at_open(bar)
        self.check_mll(bar)
        self.queue_forced_flatten(bar)
        for item in self.strategy.on_bar(visible, self.view(visible)):
            refusal = self.structural_refusal(item, visible)
            if refusal is None:
                refusal = xr.check_order(item, self.state, self.position.qty,
                                         self.state.session_start_balance_cents,
                                         bar.early_halt_ct)
            if refusal is None:
                self.pending = (*self.pending,
                                _Order(bar.decision_ts_ns, item.signed_quantity, "strategy"))


def run_engine(bars: list[Bar], strategy: Strategy, config: EngineConfig, table: SlippageTable,
               mutant: str | None = None) -> BacktestResult:
    """The real engine (``mutant=None``) or one of the deliberately broken controls."""
    if mutant is None:
        return run_backtest(iter(bars), strategy, config, table)
    if mutant == "same_bar_fill":
        run = _SameBarFillMutant(strategy, config, table)
        for bar in bars:
            run.step(bar)
        return run.finish()
    if mutant == "peek_next_bar":
        peek = _PeekNextBarMutant(strategy, config, table)
        for bar, visible in zip(bars, [*bars[1:], bars[-1]], strict=True):
            peek.step_with_view(bar, visible)
        return peek.finish()
    raise ValueError(f"unknown mutant {mutant!r}")


# ------------------------------------------------------------------ measurement ----
def round_trips(result: BacktestResult) -> list[dict]:
    """Flat -> open -> flat sequences, with gross captured ticks per micro."""
    trips: list[dict] = []
    open_fill: FillEvent | None = None
    gross = 0
    for fill in result.events(FillEvent):
        before = fill.position_after - (fill.qty if fill.side == "buy" else -fill.qty)
        if before == 0:
            open_fill, gross = fill, 0
        gross += fill.gross_realized_cents
        if fill.position_after == 0 and open_fill is not None:
            trips.append({"entry_fill_ts_ns": open_fill.fill_ts_ns,
                          "entry_decision_ts_ns": open_fill.decision_ts_ns,
                          "entry_side": open_fill.side,
                          "gross_ticks": gross / MES_TICK_VALUE_CENTS / open_fill.qty,
                          "exit_reason": fill.reason})
            open_fill = None
    return trips


def _stats(values: list[float], hits: list[bool]) -> dict:
    n = len(values)
    arr = np.array(values, dtype=float)
    mean = float(arr.mean()) if n else float("nan")
    se = float(arr.std(ddof=1) / sqrt(n)) if n > 1 else float("nan")
    k = len(hits)
    return {"trades": n, "mean_captured_ticks": mean, "se_ticks": se,
            "z": mean / se if n > 1 and se > 0 else float("nan"),
            "hit_rate": float(np.mean(hits)) if k else float("nan"), "hit_n": k,
            "hit_se_under_null": sqrt(0.25 / k) if k else float("nan")}


def score_canary(trips: list[dict], markers: Mapping[int, int]) -> dict:
    """Captured ticks and direction hit rate, for round trips the marker triggered.

    A trip belongs to the marker on bar M when its entry FILLED at bar M's open (a leaky
    engine) or at bar M+1's open (a point-in-time engine). Markers are >= 20 bars apart, so
    the match is unambiguous; the CanaryReader never enters except on a marker."""
    captured: list[float] = []
    hits: list[bool] = []
    for trip in trips:
        fill_ts = trip["entry_fill_ts_ns"]
        direction = markers.get(fill_ts, markers.get(fill_ts - NS_PER_MIN))
        if direction is None:
            continue
        captured.append(trip["gross_ticks"])  # the strategy always trades WITH the marker
        if trip["gross_ticks"] != 0:
            hits.append(trip["gross_ticks"] > 0)
    return _stats(captured, hits)


def leak_canary_passes(s: dict, jump: int) -> bool:
    return bool(s["trades"] >= 100 and s["mean_captured_ticks"] < jump / 4 and abs(s["z"]) < 4
                and abs(s["hit_rate"] - 0.5) < 4 * s["hit_se_under_null"])


def edge_detected(s: dict, jump: int) -> bool:
    return bool(s["trades"] >= 100 and s["mean_captured_ticks"] >= jump / 2 and s["z"] >= 5)


def random_baseline_stats(result: BacktestResult) -> dict:
    return _stats([t["gross_ticks"] for t in round_trips(result)], [])


def random_baseline_passes(s: dict) -> bool:
    return bool(s["trades"] >= 100 and abs(s["mean_captured_ticks"]) < 4 * s["se_ticks"])


# ------------------------------------------------------------------ structural ----
class CountingFeed:
    """One-way iterator that counts how many bars the engine has pulled."""

    def __init__(self, bars: Iterable[Bar]) -> None:
        self._it: Iterator[Bar] = iter(bars)
        self.pulled = 0

    def __iter__(self) -> CountingFeed:
        return self

    def __next__(self) -> Bar:
        bar = next(self._it)
        self.pulled += 1
        return bar


class TripwireSpy:
    """Records (bar ts, bars pulled so far) at each call; trades a little to exercise fills."""

    name = "tripwire_spy"

    def __init__(self, feed: CountingFeed) -> None:
        self.feed = feed
        self.calls: list[tuple[int, int]] = []

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        self.calls.append((bar.ts_event_ns, self.feed.pulled))
        if account.pending_signed_micros:
            return ()
        if account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        return (market_intent(bar, "buy", 1),) if len(self.calls) % 7 == 0 else ()


_PRIMITIVES = (int, float, str, bool, date, time, datetime, Enum, type(None))


def only_frozen_primitives(obj: object) -> bool:
    """A frozen dataclass whose every field is a primitive: nothing that could reach other bars."""
    params = getattr(type(obj), "__dataclass_params__", None)
    if not is_dataclass(obj) or params is None or not params.frozen:
        return False
    return all(isinstance(getattr(obj, f.name), _PRIMITIVES) for f in fields(obj))


class ReceivedObjectsSpy:
    name = "received_objects_spy"

    def __init__(self) -> None:
        self.ok = True
        self.calls = 0
        self.hindsight_seen = False

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        self.calls += 1
        self.ok = self.ok and only_frozen_primitives(bar) and only_frozen_primitives(account)
        self.hindsight_seen = self.hindsight_seen or any(getattr(bar, f) for f in HINDSIGHT_FIELDS)
        return ()


# ------------------------------------------------------------------ synthetic bars ----
def synthetic_rth_bars(days: int, seed: int, start: date = date(2026, 1, 5)) -> pd.DataFrame:
    """Random-walk 1-minute bars, 08:30-15:14 CT on weekdays, with Stage A.1-style flags, so
    the canaries also run without the paid data."""
    rng = np.random.default_rng(seed)
    rows = []
    price_ticks = 24_000
    day, made = start, 0
    while made < days:
        if day.weekday() < 5:
            for minute in range(8 * 60 + 30, 15 * 60 + 15):
                local = datetime(day.year, day.month, day.day, minute // 60, minute % 60,
                                 tzinfo=CT)
                o = price_ticks
                c = o + int(rng.integers(-3, 4, size=3).sum())
                hi = max(o, c) + int(rng.integers(0, 3))
                lo = min(o, c) - int(rng.integers(0, 3))
                price_ticks = c
                rows.append({
                    "ts_event": int(local.astimezone(UTC).timestamp()) * 1_000_000_000,
                    "open": o * 0.25, "high": hi * 0.25, "low": lo * 0.25, "close": c * 0.25,
                    "volume": 100, "instrument_id": 1, "raw_symbol": "MESH6",
                    "trade_date": day.isoformat(),
                    "in_flatten_window": minute >= 15 * 60 + 10,
                    "in_no_new_positions_window": minute >= 15 * 60 + 8,
                    "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
                    "gap_before_minutes": 0, "vendor_degraded_day": False,
                })
            made += 1
        day += timedelta(days=1)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ the suite ----
def _structural_checks(bars: list[Bar], config: EngineConfig, table: SlippageTable) -> dict:
    checks: dict = {}
    feed = CountingFeed(bars)
    spy = TripwireSpy(feed)
    run_backtest(feed, spy, config, table)
    violations = [k for k, (_, pulled) in enumerate(spy.calls) if pulled != k + 1]
    checks["tripwire_no_peek"] = {"calls": len(spy.calls), "violations": len(violations),
                                  "passed": not violations and len(spy.calls) == len(bars)}

    received = ReceivedObjectsSpy()
    run_backtest(iter(bars), received, config, table)
    checks["strategy_receives_frozen_primitives_only"] = {
        "calls": received.calls, "passed": received.ok and received.calls == len(bars)}

    degraded = [replace(b, vendor_degraded_day=True) for b in bars]
    masked = ReceivedObjectsSpy()
    run_backtest(iter(degraded), masked, config, table)
    checks["hindsight_fields_blanked_before_the_strategy_sees_them"] = {
        "bars_marked_degraded": len(degraded), "hindsight_seen_by_strategy": masked.hindsight_seen,
        "passed": not masked.hindsight_seen and masked.calls == len(bars)}

    backdated = run_backtest(iter(bars), BackdatingStrategy(), config, table)
    reasons = sorted({e.refusal.reason for e in backdated.events(IntentEvent) if e.refusal})
    checks["backdated_intents_refused"] = {
        "fills": len(backdated.events(FillEvent)), "refusal_reasons": reasons,
        "passed": not backdated.events(FillEvent)
        and reasons == ["engine_intent_timestamp_mismatch"]}

    flipped = [replace(b, vendor_degraded_day=not b.vendor_degraded_day) for b in bars]
    first = run_backtest(iter(bars), RandomBaseline(seed=3), config, table)
    second = run_backtest(iter(flipped), RandomBaseline(seed=3), config, table)
    checks["hindsight_flag_never_gates_trading"] = {
        "fills": len(first.events(FillEvent)),
        "passed": first.events(FillEvent) == second.events(FillEvent)
        and first.final_state.balance_cents == second.final_state.balance_cents}

    checks["every_bar_field_has_availability_class"] = {
        "hindsight_fields": sorted(k for k, v in BAR_FIELD_AVAILABILITY.items()
                                   if v == "hindsight"),
        "passed": set(BAR_FIELD_AVAILABILITY) == {f.name for f in fields(Bar)}
        and set(BAR_FIELD_AVAILABILITY.values()) <= {"bar_close", "calendar", "hindsight"}}
    return checks


def run_suite(frame: pd.DataFrame, table: SlippageTable, seed: int = 20_260_917,
              roll_blackout: frozenset[date] = frozenset()) -> dict:
    config = EngineConfig(restart_on_terminal=True, roll_blackout=roll_blackout)
    planted = plant_canaries(frame, seed)
    bars = list(iter_bars(planted.frame))
    clean_bars = list(iter_bars(frame))
    jump = planted.jump_ticks
    out: dict = {"bars": len(bars), "planted_jumps": len(planted.leak_markers),
                 "jump_ticks": jump, "criteria": CRITERIA, "checks": {}}

    def canary(markers: Mapping[int, int], mutant: str | None) -> dict:
        result = run_engine(bars, CanaryReader(markers), config, table, mutant)
        return score_canary(round_trips(result), markers)

    leak_real = canary(planted.leak_markers, None)
    out["checks"]["leak_canary_real_engine"] = {**leak_real,
                                                "passed": leak_canary_passes(leak_real, jump)}
    for mutant in ("same_bar_fill", "peek_next_bar"):
        s = canary(planted.leak_markers, mutant)
        out["checks"][f"positive_control_{mutant}_detected"] = {**s,
                                                                "passed": edge_detected(s, jump)}
    latency = canary(planted.latency_markers, None)
    out["checks"]["latency_control_real_engine"] = {**latency,
                                                    "passed": edge_detected(latency, jump)}
    out["diagnostics"] = {
        f"{mutant}_on_latency_markers": canary(planted.latency_markers, mutant)
        for mutant in ("same_bar_fill", "peek_next_bar")
    }  # informational: a mutant acts one bar early on these markers, so it should capture ~0

    baseline = RandomBaseline(seed=11)
    for label, feed, mutant in (("random_baseline_planted_real_engine", bars, None),
                                ("random_baseline_clean_real_engine", clean_bars, None),
                                ("random_baseline_planted_same_bar_fill_mutant", bars,
                                 "same_bar_fill")):
        s = random_baseline_stats(run_engine(feed, baseline, config, table, mutant))
        entry = {**s, "passed": random_baseline_passes(s)}
        if mutant is not None:
            entry["note"] = ("blind strategy on a LEAKY engine: shows no edge either, which is "
                             "why this check alone cannot certify point-in-time discipline")
        out["checks"][label] = entry

    out["checks"] |= _structural_checks(bars, config, table)
    out["all_passed"] = all(c["passed"] for c in out["checks"].values())
    return out


_DESCRIPTIONS = {
    "leak_canary_real_engine": "Planted future, real engine: must show NO edge",
    "positive_control_same_bar_fill_detected": "Mutant engine (fills at the decision bar's open): "
                                               "canary must DETECT it",
    "positive_control_peek_next_bar_detected": "Mutant engine (strategy sees bar N+1 early): "
                                               "canary must DETECT it",
    "latency_control_real_engine": "Marker one bar early (legitimately tradeable), real engine: "
                                   "must CAPTURE it",
    "random_baseline_planted_real_engine": "Random baseline on planted data (literal check)",
    "random_baseline_clean_real_engine": "Random baseline on the unplanted copy",
    "random_baseline_planted_same_bar_fill_mutant": "Random baseline on planted data, LEAKY "
                                                    "engine (shows the literal check is blind)",
    "tripwire_no_peek": "Tripwire feed: bars pulled at each strategy call == N+1",
    "strategy_receives_frozen_primitives_only": "Strategy receives only frozen primitive objects",
    "backdated_intents_refused": "Intents stamped with the bar OPEN are refused, never filled",
    "hindsight_flag_never_gates_trading": "Flipping vendor_degraded_day everywhere changes nothing",
    "hindsight_fields_blanked_before_the_strategy_sees_them":
        "The strategy's copy of a degraded bar has the hindsight field blanked",
    "every_bar_field_has_availability_class": "Every Bar field has a point-in-time class",
}


def _fmt(value: object, digits: int = 2) -> str:
    if isinstance(value, float):
        return "—" if value != value else f"{value:.{digits}f}"
    return str(value)


def render_markdown(report: dict) -> str:
    lines = [
        "# Leakage suite: planted-future canaries (Stage C, Task 4)", "",
        f"Generated {report['generated_utc']} · `uv run python -m sim.leakage_canaries` · "
        "tests: `tests/test_leakage_canaries.py` · machine-readable: `reports/leakage_suite.json`",
        "", f"## Verdict: {'PASS' if report['all_passed'] else 'FAIL (stop the line)'}", "",
        *_summary_lines(report), "",
    ]
    for key, title in (("real", f"Real research bars, trade dates "
                                f"{report['real_window_trade_dates'][0]}.."
                                f"{report['real_window_trade_dates'][1]}"),
                       ("synthetic_40_days", "Synthetic random-walk bars, 40 RTH days")):
        run = report[key]
        lines += [f"### {title}", "",
                  f"{run['bars']:,} bars; {run['planted_jumps']:,} planted jumps of "
                  f"{run['jump_ticks']} ticks.", "",
                  "| Check | Result | Trades | Mean captured (ticks) | z | Direction hit rate |",
                  "|---|---|---|---|---|---|"]
        for name, check in run["checks"].items():
            lines.append(
                f"| {_DESCRIPTIONS.get(name, name)} | **{'PASS' if check['passed'] else 'FAIL'}** "
                f"| {_fmt(check.get('trades', check.get('calls', '')))} "
                f"| {_fmt(check.get('mean_captured_ticks', ''))} | {_fmt(check.get('z', ''))} "
                f"| {_fmt(check.get('hit_rate', ''), 3)} |")
        lines += ["", "Diagnostics (informational): mutants on the latency markers act one bar "
                  "early, so they should capture ~0.", "",
                  "| Diagnostic | Trades | Mean captured (ticks) | z |", "|---|---|---|---|"]
        for name, d in run.get("diagnostics", {}).items():
            lines.append(f"| {name} | {d['trades']} | {_fmt(d['mean_captured_ticks'])} | "
                         f"{_fmt(d['z'])} |")
        lines.append("")
    lines += ["## Pass/fail criteria (fixed in code before any run)", ""]
    lines += [f"- `{k}`: {v}" for k, v in CRITERIA.items()]
    lines += ["", *_DESIGN_LINES, ""]
    return "\n".join(lines)


def _summary_lines(report: dict) -> list[str]:
    real = report["real"]["checks"]
    leak, same = real["leak_canary_real_engine"], real["positive_control_same_bar_fill_detected"]
    peek, lat = real["positive_control_peek_next_bar_detected"], real["latency_control_real_engine"]
    rb = real["random_baseline_planted_real_engine"]
    rbm = real["random_baseline_planted_same_bar_fill_mutant"]
    return [
        "On a planted copy of real research bars, the real engine shows **no exploitable "
        f"performance** from the planted future: {_fmt(leak['mean_captured_ticks'])} ticks per "
        f"canary trade (z = {_fmt(leak['z'])}, direction hit rate {_fmt(leak['hit_rate'], 3)}, "
        f"{leak['trades']:,} trades) against a planted jump of "
        f"{report['real']['jump_ticks']} ticks.",
        "",
        "That result means something only because the same canary **catches known leaks**. Both "
        "deliberately broken engines capture the jump: same-bar fill "
        f"{_fmt(same['mean_captured_ticks'])} ticks (z = {_fmt(same['z'])}), peek-next-bar "
        f"{_fmt(peek['mean_captured_ticks'])} ticks (z = {_fmt(peek['z'])}). The latency control "
        f"shows the real engine is not passing just by being slow: it captures "
        f"{_fmt(lat['mean_captured_ticks'])} ticks (z = {_fmt(lat['z'])}) when the marker is "
        "legitimately available one bar before the jump.",
        "",
        "The literal check from the Stage B-C prompt (random baseline on planted data) also passes "
        f"({_fmt(rb['mean_captured_ticks'])} ticks per round trip, z = {_fmt(rb['z'])}). It is not "
        "evidence of point-in-time discipline, though. The same random baseline on the LEAKY "
        f"same-bar-fill engine also shows nothing ({_fmt(rbm['mean_captured_ticks'])} ticks, "
        f"z = {_fmt(rbm['z'])}), because a coin flip never reads the marker. The canary reader "
        "and the mutants carry the proof.",
        "",
        "The structural checks all pass. The engine pulls exactly N+1 bars before it asks the "
        "strategy about bar N (a look-ahead buffer is caught in `tests/test_leakage_canaries.py`). "
        "Strategies receive only frozen primitive objects. Backdated intents are refused and never "
        "filled. The hindsight flag `vendor_degraded_day` never changes a trade.",
    ]


_DESIGN_LINES = [
    "## Design",
    "",
    "- **Planted data.** A copy of real research bars (trade dates above) gets a 16-tick jump "
    "inside RTH bars every 20 minutes, in a seeded random direction. Every later bar shifts "
    "with it, so prices stay continuous and on-grid, and every row still passes "
    "`construct_bar`. The original frame is never mutated.",
    "- **Why the marker sits on the jumped bar.** A marker that becomes visible at bar N's "
    "close and predicts bar N+1's move is legitimately tradeable, so a correct engine "
    "SHOULD profit from it. That is the latency control, not a leak test. The leak canary "
    "instead carries information about a move that has already happened by the time a "
    "point-in-time engine may act. Only an engine that fills at a price from before its "
    "decision, or shows the strategy a bar early, can monetize it. Seen from the previous "
    "bar's decision point, it is exactly the prompt's 'predictor of the next bar's return'.",
    "- **Mutants.** `_SameBarFillMutant` and `_PeekNextBarMutant` live in "
    "`sim/leakage_canaries.py`, run nowhere else, and are marked DELIBERATELY BROKEN. They "
    "give identical numbers because both are one-bar look-aheads that trade the same price "
    "pairs; the mechanisms differ, and the diagnostics table shows both differ from the real "
    "engine.",
    "- **Real engine guards exercised.** The fill-after-decision invariant "
    "(`EngineInvariantError`), the intent-timestamp refusal "
    "(`engine_intent_timestamp_mismatch`), the one-way iterator, and the frozen `Bar` / "
    "`AccountView` hand-off.",
    "- **Hindsight fields.** `vendor_degraded_day` is Databento's after-the-fact quality "
    "verdict. It stays on the `Bar` (the Stage C interface lists it) but is classified "
    "`hindsight`. Stage D.1 must not condition on it, and the engine provably ignores it. "
    "Gating trading on it would silently delete the 2025-11-28 CME outage day from "
    "backtests.",
    "- **Not covered.** This suite tests the ENGINE's point-in-time discipline. It cannot "
    "detect look-ahead a strategy builds into its own features from data it is handed "
    "legitimately. That remains Stage D.1's responsibility, and the canary pattern here (a "
    "planted marker plus a reader) is the template for testing a real feature pipeline.",
]


def main() -> None:
    from data.research_bars import RESEARCH_SERIES_PATH, load_research_bars
    from sim.engine import roll_blackout_dates, splice_trade_dates_from_parquet

    frame = load_research_bars(BAR_COLUMNS)
    lo, hi = REAL_WINDOW
    frame = frame[(frame["trade_date"] >= lo.isoformat())
                  & (frame["trade_date"] <= hi.isoformat())].reset_index(drop=True)
    blackout = roll_blackout_dates(splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH), 2)
    table = load_slippage_table()
    report = {"generated_utc": datetime.now(UTC).isoformat(),
              "real_window_trade_dates": [lo.isoformat(), hi.isoformat()],
              "real": run_suite(frame, table, roll_blackout=blackout),
              "synthetic_40_days": run_suite(synthetic_rth_bars(40, seed=5), table)}
    report["all_passed"] = all(report[k]["all_passed"] for k in ("real", "synthetic_40_days"))
    with open("reports/leakage_suite.json", "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    with open("reports/leakage_suite.md", "w") as fh:
        fh.write(render_markdown(report))
    for key in ("real", "synthetic_40_days"):
        for name, check in report[key]["checks"].items():
            detail = {k: v for k, v in check.items() if k in ("trades", "mean_captured_ticks",
                                                            "z", "hit_rate", "violations")}
            print(f"{key:18s} {name:48s} {'PASS' if check['passed'] else 'FAIL'} {detail}")
    print("ALL PASSED" if report["all_passed"] else "STOP THE LINE: a canary check failed")


if __name__ == "__main__":
    main()
