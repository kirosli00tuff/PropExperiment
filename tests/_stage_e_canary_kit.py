"""Stage E leakage canaries (design D11.9; Stage E.2b Task 3): planting, canary members,
deliberately broken engines and scoring, for tests/test_stage_e_canaries.py.

Test-only: nothing here is imported by the runner, and no real bar is read. The canaries drive the
generalized engine through its own lower-level functions (run_engine, StageERules,
product_bar_iterator; runner report section 8) on synthetic bars of one Stage E vehicle per group.

Every class whose docstring starts "DELIBERATELY BROKEN" exists only as a positive control. A
canary that cannot catch a known leak proves nothing (sim/leakage_canaries.py, part 2), so every
canary in the test file is paired with one of these and must flag it.

Pass / fail thresholds are sim.leakage_canaries' (JUMP_TICKS, MARK_EVERY_MINUTES,
leak_canary_passes, edge_detected), fixed at Stage C before any run. The one Stage E change: the
canary reader holds for HOLD_MINUTES = 2 (the D9.3b minimum hold), so a planted jump reverts
REVERT_AFTER_BARS bars after it (after every exit), which keeps each trade date's price inside the
hard-limit products' D9.7 stop levels.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, fields, replace
from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data.group_session import assign_trade_dates, load_group_calendar, open_intervals
from rules import sessions
from rules.products import PRICE_SCALE, product
from screening.stage_e_engine import (
    NS_PER_MINUTE,
    AccountStart,
    Cancel,
    EngineResult,
    Fill,
    IntentRecord,
    _Run,
    iter_minutes,
    run_engine,
)
from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import (
    ReleaseCalendar,
    StageERules,
    _Settlement,
    product_bar_iterator,
    release_calendar_from_dict,
)
from sim import leakage_canaries as lc
from strategy.interface import NS_PER_BAR, NS_PER_S, Bar
from strategy.stage_e.interface import LegSpec, MinuteView, leg_market_intent
from tests._stage_e_synthetic import product_frame

CT = ZoneInfo("America/Chicago")
NS_MIN = NS_PER_MINUTE

# One traded Stage E vehicle per group (reports/stage_e2a_vehicles.json; data/calendars/).
GROUP_PRODUCTS: Mapping[str, str] = MappingProxyType({
    "equity": "MNQ", "rates": "ZN", "fx": "6E", "energy": "MCL", "metals": "MGC",
    "grains": "ZC", "livestock": "LE", "crypto": "MBT"})
BASE_PRICE = MappingProxyType({"MNQ": 20000.0, "ZN": 110.0, "6E": 1.13, "MCL": 65.0,
                               "MGC": 3300.0, "ZC": 440.0, "LE": 220.0, "MBT": 100000.0})
# 15 regular trade dates of every group (no holiday, regular F; checked by check_days).
DAYS: tuple[date, ...] = tuple(d for d in (date(2025, 5, 5) + timedelta(days=i)
                                           for i in range(19)) if d.weekday() < 5)
JUMP_TICKS = lc.JUMP_TICKS
MARK_EVERY_MINUTES = lc.MARK_EVERY_MINUTES
HOLD_MINUTES = 2  # D9.3b: no exit less than 2 full minutes after the opening fill
REVERT_AFTER_BARS = 6  # > HOLD_MINUTES + 1: every canary exit fills before the reversion
VOL_TICKS = 1.0
FUTURE_OFFSET_TICKS = 40
NO_RELEASES = ReleaseCalendar(MappingProxyType({}), (), date(2019, 5, 1), date(2026, 6, 19),
                              "0" * 64, "stage_e_canaries")


# ------------------------------------------------------------------ products ----
def flatten_ct(root: str, day: date = DAYS[0]) -> time:
    f = sessions.day_rule(root, day).flatten_ct
    assert f is not None, (root, day)
    return f


def _add(t: time, minutes: int) -> tuple[int, int]:
    total = t.hour * 60 + t.minute + minutes
    return total // 60, total % 60


def frame_bounds(root: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """[O_X, F + 2 min) CT: the product's D6 day session start to just past its flatten time."""
    start = load_frozen_tables().day_session_ct[root][0]
    return (start.hour, start.minute), _add(flatten_ct(root), 2)


def tick_fixed(root: str) -> int:
    return product(root).vendor_tick_fixed


def to_ticks(root: str, prices: Any) -> np.ndarray:
    return np.rint(np.asarray(prices, dtype=float) * PRICE_SCALE / tick_fixed(root)
                   ).astype(np.int64)


def from_ticks(root: str, ticks: Any) -> np.ndarray:
    return np.asarray(ticks, dtype=np.int64) * tick_fixed(root) / PRICE_SCALE


def base_ticks(root: str) -> int:
    return int(to_ticks(root, [BASE_PRICE[root]])[0])


def check_days(root: str, days: Sequence[date] = DAYS) -> None:
    """Every canary date is a regular trade date of the product's group (no holiday, no early F)."""
    for d in days:
        rule = sessions.day_rule(root, d)
        assert not rule.closed and len(rule.reasons) == 1 and rule.reasons[0].startswith(
            "regular"), (root, d, rule)


def product_bars(root: str, days: Sequence[date] = DAYS, seed: int = 0, **kw: Any
                 ) -> pd.DataFrame:
    start, end = frame_bounds(root)
    kw.setdefault("vol_ticks", VOL_TICKS)
    return product_frame(root, list(days), seed, start=start, end=end,
                         base_ticks=base_ticks(root), **kw)


def ct_minutes(ts: np.ndarray) -> np.ndarray:
    local = pd.to_datetime(np.asarray(ts, dtype=np.int64), utc=True).tz_convert(CT)
    return np.asarray(local.hour * 60 + local.minute)


def ts_at(day: date, hh: int, mm: int) -> int:
    local = datetime.combine(day, time(hh, mm), tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def mark_minutes(root: str) -> frozenset[int]:
    """Every 20 minutes from O_X + 5 to 20 minutes before the earlier of C_X and F."""
    o, c = load_frozen_tables().day_session_ct[root]
    last = min(c.hour * 60 + c.minute, flatten_ct(root).hour * 60 + flatten_ct(root).minute) - 20
    return frozenset(range(o.hour * 60 + o.minute + 5, last + 1, MARK_EVERY_MINUTES))


def rules_for(legs: Sequence[LegSpec], days: Sequence[date] = DAYS,
              releases: ReleaseCalendar = NO_RELEASES, cls: type = StageERules,
              **extra: Any) -> StageERules:
    return cls({leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in legs},
               frozenset(days), frozenset(), releases, **extra)


# ------------------------------------------------------------------ planting ----
@dataclass(frozen=True)
class PlantedJumps:
    frame: pd.DataFrame
    leak_markers: Mapping[int, int]  # jumped bar ts -> direction (marker ON the jumped bar)
    latency_markers: Mapping[int, int]  # ts of the bar BEFORE the jumped bar -> direction


def _with_ticks(frame: pd.DataFrame, root: str, o: np.ndarray, h: np.ndarray, lo: np.ndarray,
                c: np.ndarray, rows: np.ndarray) -> pd.DataFrame:
    """A COPY with the prices of ``rows`` (a boolean mask) set from ticks; every other row keeps
    its original floats bit for bit (a tick round trip can change the last bits)."""
    out = frame.copy()
    for col, arr in (("open", o), ("high", h), ("low", lo), ("close", c)):
        values = out[col].to_numpy(dtype=float).copy()
        values[rows] = from_ticks(root, arr[rows])
        out[col] = values
    return out


def plant_jumps(frame: pd.DataFrame, root: str, seed: int, marks: frozenset[int],
                jump_ticks: int = JUMP_TICKS, directions: Mapping[int, int] | None = None
                ) -> PlantedJumps:
    """A COPY of ``frame`` with a jump of d x ``jump_ticks`` INSIDE each marked bar (open
    unshifted, close shifted) that reverts inside the bar REVERT_AFTER_BARS later. Directions
    are fair coins (``seed``), or given per bar ts (``directions``: a common shock across legs).
    The input is never mutated; prices stay on the vendor grid and OHLC-consistent."""
    out = frame.reset_index(drop=True)
    ts = out["ts_event"].to_numpy(np.int64)
    n, r = len(ts), REVERT_AFTER_BARS
    minute = ct_minutes(ts)
    tdate = out["trade_date"].astype(str).to_numpy()
    o, h, lo, c = (to_ticks(root, out[k]) for k in ("open", "high", "low", "close"))
    rng = np.random.default_rng(seed)
    open_shift = np.zeros(n, dtype=np.int64)
    close_shift = np.zeros(n, dtype=np.int64)
    leak: dict[int, int] = {}
    latency: dict[int, int] = {}
    for i in range(1, n - r):
        if int(minute[i]) not in marks:
            continue
        span = ts[i - 1:i + r + 1]
        if not bool(np.all(np.diff(span) == NS_MIN)) or len(set(tdate[i - 1:i + r + 1])) != 1:
            continue
        d = int(rng.choice((-1, 1))) if directions is None else directions.get(int(ts[i]))
        if d is None:
            continue
        close_shift[i:i + r] += d * jump_ticks
        open_shift[i + 1:i + r + 1] += d * jump_ticks
        leak[int(ts[i])] = d
        latency[int(ts[i - 1])] = d
    new_o, new_c = o + open_shift, c + close_shift
    lo_shift, hi_shift = np.minimum(open_shift, close_shift), np.maximum(open_shift, close_shift)
    new_h = np.maximum.reduce([h + lo_shift, new_o, new_c])
    new_lo = np.minimum.reduce([lo + hi_shift, new_o, new_c])
    touched = (open_shift != 0) | (close_shift != 0)
    return PlantedJumps(_with_ticks(out, root, new_o, new_h, new_lo, new_c, touched),
                        MappingProxyType(leak), MappingProxyType(latency))


def plant_future(frame: pd.DataFrame, root: str, cutoff_ts: int,
                 offset_ticks: int = FUTURE_OFFSET_TICKS) -> pd.DataFrame:
    """A COPY in which every bar opening after ``cutoff_ts`` is replaced by a planted future: the
    clean future mirrored around the cutoff bar's close (every later return flips sign), then
    moved ``offset_ticks`` against the clean next close move, so the first planted close moves
    the other way from the clean one (never equal). Bars up to the cutoff are untouched."""
    out = frame.reset_index(drop=True)
    ts = out["ts_event"].to_numpy(np.int64)
    k = np.flatnonzero(ts == cutoff_ts)
    assert k.size == 1 and k[0] + 1 < len(ts), "the cutoff needs a bar and a later bar"
    k = int(k[0])
    o, h, lo, c = (to_ticks(root, out[x]) for x in ("open", "high", "low", "close"))
    clean_move = int(c[k + 1] - c[k])
    shift = -offset_ticks if clean_move >= 0 else offset_ticks
    after = ts > cutoff_ts
    ref = 2 * int(c[k])
    new_o = np.where(after, ref - o + shift, o)
    new_c = np.where(after, ref - c + shift, c)
    new_h = np.where(after, ref - lo + shift, h)
    new_lo = np.where(after, ref - h + shift, lo)
    planted_move = int(new_c[k + 1] - c[k])
    assert planted_move != 0 and (clean_move == 0 or (planted_move > 0) != (clean_move > 0))
    assert (new_lo > 0).all()
    return _with_ticks(out, root, new_o, new_h, new_lo, new_c, after)


def plant_bar(frame: pd.DataFrame, root: str, ts: int, label: date, price_ticks: int, *,
              closure_flag: bool, session_flags: bool = True) -> pd.DataFrame:
    """A COPY with one extra bar at ``ts`` (booked to ``label``), flat at ``price_ticks``, with
    ``in_scheduled_closure`` = ``closure_flag`` and its flatten flags from rules/sessions.py
    (``session_flags``) or all False (a builder that flagged nothing)."""
    assert not (frame["ts_event"] == ts).any(), "a bar already opens at that minute"
    state = sessions.session_state(root, datetime.fromtimestamp(ts / NS_PER_S, tz=UTC))
    if not session_flags:
        state = sessions.SessionState(True, False, "unflagged")
    template = frame.iloc[0].to_dict()
    price = float(from_ticks(root, [price_ticks])[0])
    template.update({"ts_event": ts, "open": price, "high": price, "low": price, "close": price,
                     "volume": 1, "trade_date": label.isoformat(),
                     "in_flatten_window": bool(state.must_be_flat),
                     "in_no_new_positions_window": bool(not state.can_open),
                     "in_scheduled_closure": closure_flag, "gap_before_minutes": 0})
    out = pd.concat([frame, pd.DataFrame([template])], ignore_index=True)
    return out.sort_values("ts_event", kind="stable").reset_index(drop=True)


# ------------------------------------------------------------------ closures ----
CLOSURE_CT = MappingProxyType({  # a CT clock inside a scheduled closure of the trade date's day
    "equity": time(16, 30), "rates": time(16, 30), "fx": time(16, 30), "energy": time(16, 30),
    "metals": time(16, 30), "grains": time(8, 0), "livestock": time(14, 0),
    "crypto": time(16, 30)})


def closure_booking(root: str, ts: int) -> tuple[bool, bool, date | None]:
    """(inside a closure of the group calendar, in the close minute of a session, the trade date
    the bar builder books it to under lead ruling L-3)."""
    cal = load_group_calendar(product(root).group)
    day = datetime.fromtimestamp(ts / NS_PER_S, tz=UTC).astimezone(CT).date()
    opened = open_intervals(cal, day - timedelta(days=6), day + timedelta(days=6))
    got = assign_trade_dates(opened, np.array([ts], dtype=np.int64),
                             close_minute_to_previous=True)
    boundary = bool(got.boundary[0]) if got.boundary is not None else False
    return bool(got.in_closure[0]), boundary, got.as_dates()[0]


def session_end_ts(root: str, day: date) -> int:
    """The end instant of the day session's open interval that contains F - 1 minute."""
    cal = load_group_calendar(product(root).group)
    opened = open_intervals(cal, day, day)
    probe = ts_at(day, *_add(flatten_ct(root, day), -1))
    inside = (opened.starts <= probe) & (probe < opened.ends)
    assert inside.sum() == 1, (root, day)
    return int(opened.ends[inside][0])


def closure_trades(result: EngineResult, closure_ts: frozenset[int]) -> list[str]:
    """What the run did ON a closure bar: an accepted member intent decided on it, a strategy
    fill decided on it, or any fill AT it (its open, its range, or its close)."""
    out: list[str] = []
    for e in result.events(IntentRecord):
        if e.accepted and e.decision_ts_ns - NS_PER_BAR in closure_ts:
            out.append(f"intent accepted on closure bar {e.decision_ts_ns - NS_PER_BAR}")
    for f in result.events(Fill):
        at_close = f.reason.endswith("session_end") or f.reason == "end_of_data"
        if (not at_close and f.fill_ts_ns in closure_ts) or (
                at_close and f.fill_ts_ns - NS_PER_BAR in closure_ts):
            out.append(f"{f.reason} fill at closure bar {f.fill_ts_ns}")
        elif f.reason == "strategy" and f.decision_ts_ns - NS_PER_BAR in closure_ts:
            out.append(f"strategy fill decided on closure bar {f.decision_ts_ns - NS_PER_BAR}")
    return out


# ------------------------------------------------------------------ members ----
@dataclass
class CanaryReader:
    """Test-only, not a strategy: on a marked bar of ``marker_root`` it trades ``traded`` in the
    marker's direction, and exits HOLD_MINUTES of engine clock later."""

    traded: str
    markers: Mapping[int, int]
    marker_root: str | None = None
    name: str = "stage_e_canary_reader"
    trading_windows: Mapping = field(default_factory=dict)
    _entry_ts: int | None = None

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        root = self.traded
        if account.pending.get(root, 0):
            return ()
        pos = account.position(root)
        if pos:
            if self._entry_ts is not None and \
                    view.ts_event_ns - self._entry_ts >= HOLD_MINUTES * NS_MIN:
                return (leg_market_intent(view, root, "sell" if pos > 0 else "buy", abs(pos)),)
            return ()
        bar = view.bars.get(self.marker_root or root)
        direction = None if bar is None else self.markers.get(bar.ts_event_ns)
        if direction is None:
            return ()
        self._entry_ts = view.ts_event_ns
        return (leg_market_intent(view, root, "buy" if direction > 0 else "sell", 1),)


@dataclass
class ReactiveMember:
    """HONEST: reads only the bars the engine hands it. Trades ``traded`` in the direction of the
    last 2-minute close move of ``signal`` (its own leg by default); exits 3 minutes later."""

    traded: str
    signal: str | None = None
    name: str = "reactive"
    trading_windows: Mapping = field(default_factory=dict)
    _closes: list = field(default_factory=list)
    _entry_ts: int = 0

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        sig = view.bars.get(self.signal or self.traded)
        if sig is not None:
            self._closes.append(sig.close)
        root = self.traded
        if view.bars.get(root) is None or account.pending.get(root, 0):
            return ()
        pos = account.position(root)
        if pos:
            if view.ts_event_ns - self._entry_ts >= 3 * NS_MIN:
                return (leg_market_intent(view, root, "sell" if pos > 0 else "buy", abs(pos)),)
            return ()
        if sig is None or len(self._closes) < 3 or self._closes[-1] == self._closes[-3]:
            return ()
        self._entry_ts = view.ts_event_ns
        side = "buy" if self._closes[-1] > self._closes[-3] else "sell"
        return (leg_market_intent(view, root, side, 1),)


class FramePeekingMember:
    """LEAKY ON PURPOSE (a member the canaries must catch): it holds the data frame of leg
    ``peek`` and reads the bar AFTER the minute it is handed. Flat, it trades ``traded`` in the
    direction of that next close move; with exposure, it emits an exit whenever the next move
    goes against it, so every minute's intents depend on the next bar."""

    name = "frame_peeker"

    def __init__(self, traded: str, peek: str, frame: pd.DataFrame) -> None:
        self.traded, self.peek = traded, peek
        self.trading_windows: Mapping = {}
        self._close = dict(zip(frame["ts_event"].astype("int64").tolist(),
                               frame["close"].astype(float).tolist(), strict=True))

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        if view.bars.get(self.traded) is None:
            return ()
        now = self._close.get(view.ts_event_ns)
        nxt = self._close.get(view.ts_event_ns + NS_MIN)
        if now is None or nxt is None or nxt == now:
            return ()
        exposure = account.position(self.traded) + account.pending.get(self.traded, 0)
        up = nxt > now
        if exposure == 0:
            return (leg_market_intent(view, self.traded, "buy" if up else "sell", 1),)
        if (exposure > 0) != up:
            return (leg_market_intent(view, self.traded, "sell" if exposure > 0 else "buy",
                                      abs(exposure)),)
        return ()


@dataclass
class ScriptMember:
    """Test-only: market orders at bar-open instants {ts: [(root, side, qty)]}; side "flat"
    closes the whole position."""

    orders: Mapping[int, Sequence[tuple[str, str, int]]]
    name: str = "script"
    trading_windows: Mapping = field(default_factory=dict)

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        out = []
        for root, side, qty in self.orders.get(view.ts_event_ns, ()):
            if side == "flat":
                pos = account.position(root)
                if not pos:
                    continue
                side, qty = ("sell" if pos > 0 else "buy"), abs(pos)
            out.append(leg_market_intent(view, root, side, qty))
        return tuple(out)


@dataclass
class HindsightReader:
    """Test-only: buys only on a bar flagged ``vendor_degraded_day`` (a hindsight field that a
    live bot cannot know), and exits 3 minutes later. It records every flag it is shown."""

    traded: str
    name: str = "hindsight_reader"
    trading_windows: Mapping = field(default_factory=dict)
    flags_seen: list = field(default_factory=list)
    _entry_ts: int = 0

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        bar = view.bars.get(self.traded)
        if bar is None:
            return ()
        self.flags_seen.append(bar.vendor_degraded_day)
        if account.pending.get(self.traded, 0):
            return ()
        pos = account.position(self.traded)
        if pos:
            if view.ts_event_ns - self._entry_ts >= 3 * NS_MIN:
                return (leg_market_intent(view, self.traded, "sell", pos),)
            return ()
        if bar.vendor_degraded_day:
            self._entry_ts = view.ts_event_ns
            return (leg_market_intent(view, self.traded, "buy", 1),)
        return ()


@dataclass
class ClosureTrader:
    """Test-only: tries to buy at every minute in ``closure_ts`` (bars planted inside a
    scheduled closure) and exits 3 minutes after a fill."""

    traded: str
    closure_ts: frozenset[int]
    name: str = "closure_trader"
    trading_windows: Mapping = field(default_factory=dict)
    _entry_ts: int = 0

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        if view.bars.get(self.traded) is None or account.pending.get(self.traded, 0):
            return ()
        pos = account.position(self.traded)
        if pos:
            if view.ts_event_ns - self._entry_ts >= 3 * NS_MIN:
                return (leg_market_intent(view, self.traded, "sell" if pos > 0 else "buy",
                                          abs(pos)),)
            return ()
        if view.ts_event_ns in self.closure_ts:
            self._entry_ts = view.ts_event_ns
            return (leg_market_intent(view, self.traded, "buy", 1),)
        return ()


class ViewSpy:
    """Wraps a member and records every view it is handed: (minute, ((root, bar), ...))."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.name = getattr(inner, "name", "spy")
        self.trading_windows = getattr(inner, "trading_windows", {})
        self.seen: list[tuple[int, tuple]] = []

    def on_minute(self, view: MinuteView, account: Any) -> Any:
        self.seen.append((view.ts_event_ns, tuple(sorted(view.bars.items()))))
        return self.inner.on_minute(view, account)


# ------------------------------------------------ DELIBERATELY BROKEN engines ----
class SameBarFillRun(_Run):
    """DELIBERATELY BROKEN, positive control only: asks the member BEFORE the minute's fills,
    back-stamps its new orders to the bar's OPEN and fills them at that same open (the price
    before the bar it just saw). The engine's fill-after-decision invariant is thereby evaded."""

    def step(self, ts: int, bars: Mapping[str, Bar]) -> None:
        assert ts > self.last_ts
        for root, bar in bars.items():
            self.previous_bar[root] = self.last_bar[root]
            self.last_instrument[root] = bar.instrument_id
            self.last_bar[root] = bar
            self.bars += 1
        self.last_ts = ts
        self.minutes += 1
        self.rules.observe(self, ts, bars)
        self.roll_session(bars)
        self.ask_member(ts, bars)
        self.pending = tuple(
            replace(o, decision_ts_ns=ts)
            if o.reason == "strategy" and o.decision_ts_ns == ts + NS_PER_BAR else o
            for o in self.pending)  # the bug under test
        for root in self.traded:
            if root in bars:
                self.fill_pending_at_open(root, bars[root])
        for root in self.traded:
            if root in bars:
                self.check_mll(root, bars[root])
        for root in self.traded:
            if root in bars:
                self.queue_forced(root, bars[root])


def run_with(frames: Mapping[str, pd.DataFrame], member: Any, legs: Sequence[LegSpec],
             rules: Any, run_cls: type = _Run) -> EngineResult:
    """run_engine's own loop with a chosen run class (the real one by default)."""
    if run_cls is _Run:
        return run_engine(frames, member, legs, rules)
    run = run_cls(member, legs, rules)
    feeds = {leg.root: rules.bar_iterator(leg.root) for leg in legs}
    for ts, bars in iter_minutes({leg.root: frames[leg.root] for leg in legs}, feeds):
        run.step(ts, bars)
    return run.finish()


def lookahead_bars(frames: Mapping[str, pd.DataFrame], roots: Sequence[str]
                   ) -> dict[str, tuple[np.ndarray, tuple[Bar, ...]]]:
    out = {}
    for r in roots:
        seq = tuple(product_bar_iterator(r)(frames[r]))
        out[r] = (np.array([b.ts_event_ns for b in seq], dtype=np.int64), seq)
    return out


@dataclass(frozen=True)
class LookaheadViewRules(StageERules):
    """DELIBERATELY BROKEN, positive control only: hands the member a LATER bar of each leg in
    ``lookahead`` -- the leg's ``steps``-th next bar at every minute (peek_next_bar), or, with
    ``only_if_missing``, only where the leg has no bar at the minute (a backward fill)."""

    lookahead: Mapping[str, tuple[np.ndarray, tuple[Bar, ...]]] = field(default_factory=dict)
    only_if_missing: bool = False
    steps: int = 1

    def call_member(self, run: Any, ts: int, bars: Mapping[str, Bar]) -> Any:
        shown = {}
        for r in run.read:
            bar = bars.get(r)
            if r in self.lookahead and (bar is None or not self.only_if_missing):
                arr, seq = self.lookahead[r]
                i = int(np.searchsorted(arr, ts, side="right")) + self.steps - 1
                bar = seq[i] if i < len(seq) else bar
            shown[r] = run.visible(bar)
        view = MinuteView(ts, MappingProxyType(shown))
        return run.member.on_minute(view, self.account_view(run))


def settlement_proxies(frame: pd.DataFrame, root: str) -> dict[date, Any]:
    """Every trade date's settlement proxy computed from the WHOLE frame (hindsight)."""
    s = _Settlement(root)
    for bar in product_bar_iterator(root)(frame):
        s.add(bar)
    s.finalize()
    return dict(s.proxies)


@dataclass(frozen=True)
class SameDaySettlementRules(StageERules):
    """DELIBERATELY BROKEN, positive control only: D9.7 reads the CURRENT trade date's
    settlement (known only once its settlement window has printed) instead of the prior date's."""

    hindsight_proxies: Mapping[tuple[str, date], Any] = field(default_factory=dict)

    def prior_settlement(self, run: Any, root: str, day: date) -> Any:
        return self.hindsight_proxies.get((root, day))


@dataclass(frozen=True)
class SettlementSpyRules(StageERules):
    """The real rules, recording every settlement value the engine consults."""

    calls: list = field(default_factory=list)

    def prior_settlement(self, run: Any, root: str, day: date) -> Any:
        value = super().prior_settlement(run, root, day)
        self.calls.append((root, day, value))
        return value


@dataclass(frozen=True)
class ClosureBlindRules(StageERules):
    """DELIBERATELY BROKEN, positive control only: an intent decided on a bar inside a scheduled
    closure skips the closure flag and the rules/sessions state (only the window, blackout, cap
    and D9.7 checks run)."""

    def structural_refusal(self, run: Any, norm: Any, ts: int, bars: Mapping[str, Bar]) -> Any:
        bar = bars.get(norm.root)
        if bar is None or not bar.in_scheduled_closure:
            return super().structural_refusal(run, norm, ts, bars)
        if self._opens(run, norm):
            decision = datetime.fromtimestamp((ts + NS_PER_BAR) / NS_PER_S, tz=UTC)
            return self._opening_refusal(run, norm, bar, decision)
        return self._exit_refusal(run, norm, ts + NS_PER_BAR)


@dataclass(frozen=True)
class LookaheadReleaseCalendar(ReleaseCalendar):
    """DELIBERATELY BROKEN, positive control only: the release lookup takes the first release AT
    OR AFTER the instant (an off-by-one searchsorted side), so a release's event window and fill
    guard reach fills made before the release happens."""

    def _latest_at_or_before(self, root: str, ts_ns: int) -> int | None:
        arr = self.by_root.get(root, ())
        i = int(np.searchsorted(np.asarray(arr, dtype=np.int64), ts_ns, side="left"))
        return None if i >= len(arr) else int(arr[i])


def release_calendar(root: str, instants_ns: Sequence[int], cls: type = ReleaseCalendar
                     ) -> ReleaseCalendar:
    raw = {"schema": "stage_e_release_calendar/1",
           "coverage": {"first": "2019-05-01", "last": "2026-06-19"},
           "releases": [{"id": f"canary{i}", "products": [root], "cpi": False,
                         "instant_utc": datetime.fromtimestamp(t / NS_PER_S, tz=UTC).isoformat(),
                         "source": "canary"} for i, t in enumerate(instants_ns)]}
    cal = release_calendar_from_dict(raw, "c" * 64, "canary")
    return cal if cls is ReleaseCalendar else cls(**{f.name: getattr(cal, f.name)
                                                     for f in fields(cal)})


# ------------------------------------------------------------------ scoring ----
def leg_trips(result: EngineResult, root: str, tick_value: Any) -> list[dict]:
    """Flat -> open -> flat trips of one leg, with gross captured ticks per contract."""
    trips: list[dict] = []
    open_fill: Fill | None = None
    gross: Any = 0
    for f in result.events(Fill):
        if f.root != root:
            continue
        before = f.position_after - (f.qty if f.side == "buy" else -f.qty)
        if before == 0:
            open_fill, gross = f, 0
        gross += f.gross_realized_cents
        if f.position_after == 0 and open_fill is not None:
            trips.append({"entry_fill_ts_ns": open_fill.fill_ts_ns,
                          "gross_ticks": float(gross / tick_value / open_fill.qty),
                          "exit_reason": f.reason})
            open_fill = None
    return trips


def jump_score(result: EngineResult, root: str, rules: StageERules,
               markers: Mapping[int, int]) -> dict:
    return lc.score_canary(leg_trips(result, root, rules.tick_value(root)), markers)


def ledger_until(result: EngineResult, cutoff_ts: int) -> tuple:
    """Everything the run did up to the cutoff bar's decision: intents decided at or before it,
    fills and cancels at bar opens at or before the cutoff bar, accounts started by then."""
    return tuple(e for e in result.ledger if _at_or_before(e, cutoff_ts))


def _at_or_before(e: Any, cutoff_ts: int) -> bool:
    if isinstance(e, IntentRecord):
        return e.decision_ts_ns <= cutoff_ts + NS_PER_BAR
    if isinstance(e, Fill):
        return e.fill_ts_ns <= cutoff_ts
    if isinstance(e, Cancel | AccountStart):
        return e.ts_ns <= cutoff_ts
    return False


def ledger_after(result: EngineResult, cutoff_ts: int) -> tuple:
    until = set(map(id, ledger_until(result, cutoff_ts)))
    return tuple(e for e in result.ledger if id(e) not in until and
                 isinstance(e, IntentRecord | Fill))


def views_until(spy: ViewSpy, cutoff_ts: int) -> list:
    return [v for v in spy.seen if v[0] <= cutoff_ts]


@cache
def group_bars(group: str, seed: int = 0) -> pd.DataFrame:
    root = GROUP_PRODUCTS[group]
    check_days(root)
    return product_bars(root, DAYS, seed)


@dataclass(frozen=True)
class TripwireRules(StageERules):
    """The real rules with a counting bar feed: ``pulls[root]`` is how many bars of the leg the
    engine has taken from its feed. ``eager`` is DELIBERATELY BROKEN, positive control only: the
    feed reads the whole leg ahead on the first pull (a look-ahead buffer)."""

    pulls: dict = field(default_factory=dict)
    eager: bool = False

    def bar_iterator(self, root: str) -> Any:
        base, pulls, eager = product_bar_iterator(root), self.pulls, self.eager

        def iterate(frame: pd.DataFrame) -> Any:
            pulls[root] = 0
            if eager:
                seq = list(base(frame))
                pulls[root] = len(seq)
                yield from seq
                return
            for bar in base(frame):
                pulls[root] += 1
                yield bar

        return iterate


class TripwireSpy:
    """Records, at every member call, the bars each leg's feed has handed the engine so far."""

    name = "tripwire_spy"

    def __init__(self, rules: TripwireRules) -> None:
        self.rules = rules
        self.trading_windows: Mapping = {}
        self.calls: list[tuple[int, dict[str, int]]] = []

    def on_minute(self, view: MinuteView, account: Any) -> tuple:
        self.calls.append((view.ts_event_ns, dict(self.rules.pulls)))
        return ()


def tripwire_violations(spy: TripwireSpy, frames: Mapping[str, pd.DataFrame]) -> list:
    """Calls at which some leg had handed over a bar opening AFTER the minute being decided."""
    ts = {r: np.sort(f["ts_event"].to_numpy(np.int64)) for r, f in frames.items()}
    out = []
    for minute, pulled in spy.calls:
        for r, n in pulled.items():
            allowed = int(np.searchsorted(ts[r], minute, side="right"))
            if n != allowed:
                out.append((minute, r, n, allowed))
    return out


def plant_one_bar(frame: pd.DataFrame, root: str, ts: int, offset_ticks: int = FUTURE_OFFSET_TICKS
                  ) -> pd.DataFrame:
    """A COPY in which only the bar opening at ``ts`` is moved by ``offset_ticks``."""
    out = frame.reset_index(drop=True)
    hit = (out["ts_event"] == ts).to_numpy()
    assert hit.sum() == 1
    o, h, lo, c = (to_ticks(root, out[k]) for k in ("open", "high", "low", "close"))
    shift = np.where(hit, offset_ticks, 0)
    return _with_ticks(out, root, o + shift, h + shift, lo + shift, c + shift, hit)


def shift_leg(frame: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """A COPY with every bar re-stamped ``minutes`` later (negative: earlier), prices unchanged."""
    out = frame.copy()
    out["ts_event"] = out["ts_event"].astype("int64") + minutes * NS_MIN
    return out


def gap_before(frame: pd.DataFrame, marked: Sequence[int], *, backfill: bool) -> pd.DataFrame:
    """A COPY without the bar one minute before each marked bar; ``backfill`` is DELIBERATELY
    BROKEN, positive control only: the hole is filled with the marked (NEXT) bar's values."""
    out = frame.reset_index(drop=True)
    holes = {int(t) - NS_MIN for t in marked}
    ts = out["ts_event"].to_numpy(np.int64)
    kept = out[~np.isin(ts, list(holes))]
    if not backfill:
        return kept.reset_index(drop=True)
    fill = out[np.isin(ts, [int(t) for t in marked])].copy()
    fill["ts_event"] = fill["ts_event"].astype("int64") - NS_MIN
    return pd.concat([kept, fill]).sort_values("ts_event", kind="stable").reset_index(drop=True)


# ------------------------------------------------------- the ML rule wrapper ----
class MLSpy:
    """Wraps ml_route.stage_e_adapter.RouteExposureMember: records, with the engine minute at
    which it was emitted, every feature row its DistilledRuleStrategy computes and every
    Decision it appends (the wrapper is unchanged; only its _features is observed)."""

    def __init__(self, member: Any) -> None:
        self.member = member
        self.name = member.name
        self.trading_windows = member.trading_windows
        self.minute: int | None = None
        self.features: list[tuple[int | None, int, tuple | None]] = []
        self.decisions: list[tuple[int, Any]] = []
        strategy = member.strategy
        original = strategy._features

        def observed(t_ns: int, day: date) -> Any:
            x = original(t_ns, day)
            row = None if x is None else tuple(np.nan_to_num(x, nan=-1e300).tolist())
            self.features.append((self.minute, t_ns, row))
            return x

        strategy._features = observed

    def on_minute(self, view: MinuteView, account: Any) -> Any:
        self.minute = view.ts_event_ns
        before = len(self.member.decisions)
        out = self.member.on_minute(view, account)
        self.decisions.extend((view.ts_event_ns, d) for d in self.member.decisions[before:])
        return out

    def emitted_until(self, cutoff_ts: int) -> tuple[list, list]:
        return ([f for f in self.features if f[0] is not None and f[0] <= cutoff_ts],
                [d for d in self.decisions if d[0] <= cutoff_ts])

    def emitted_after(self, cutoff_ts: int) -> tuple[list, list]:
        return ([f for f in self.features if f[0] is not None and f[0] > cutoff_ts],
                [d for d in self.decisions if d[0] > cutoff_ts])


class EarlyLeadMember:
    """Hands the wrapper EVERY bar of the cluster lead (a planted future included) before the
    run, as M7.7 does on the MES engine, and hides the lead leg from the adapter's per-minute
    handover so that no lead bar arrives twice. The wrapper's own filter (lead bars closed by the
    decision time) is what must keep the early bars out of every decision."""

    def __init__(self, spy: MLSpy, lead_root: str, lead_frame: pd.DataFrame) -> None:
        self.spy, self.lead_root = spy, lead_root
        self.name, self.trading_windows = spy.name, spy.trading_windows
        for bar in product_bar_iterator(lead_root)(lead_frame):
            spy.member.strategy.observe_lead(bar)

    def on_minute(self, view: MinuteView, account: Any) -> Any:
        bars = {r: (None if r == self.lead_root else b) for r, b in view.bars.items()}
        return self.spy.on_minute(MinuteView(view.ts_event_ns, MappingProxyType(bars)), account)
