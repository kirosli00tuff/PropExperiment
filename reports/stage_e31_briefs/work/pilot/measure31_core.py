"""E.31 pilot engine on one trade date: placements, fill models (a) K, (b) FIFO, (c) trade-through,
markouts, conditions, the round-trip loop and the implied-liquidity check.

Binding: reports/stage_e31_pilot_spec.md sections 2 to 6 and 8 (implied check); output tables:
TABLES31.md. Every convention the spec leaves to the code is listed in README_measure31.md
("Conventions"). The engine works on one instrument's MBO records in file order (no re-sorting:
snapshot priority order and trade/fill groups depend on it) with the time axis of
mbo_book31.time_axis. One pass applies the records to the book (mbo_book31.Book) and fires timers
(placement joins at g + 50 ms, life ends at j + 60 s + 50 ms, loop joins) between records: a timer
at time T sees the book after every record stamped at or before T.

Match events (spec 3, README): consecutive T records of one instrument with the same time, price
and aggressor side, with the F records that follow them, form one event; v = the sum of its T
sizes, F = the sum of its F sizes on the passive side (the aggressor's own F record, when it
rested before, is on the other side and is left out). The event's outright volume is
Q = min(v, F). Side-N trades (implied or opening) are never match events for a virtual order.
- (a) K: at an event at the order's price on its passive side, Q is allocated (kalgo31) over the
  queue as it stood before the event (T and F records do not change the book) with the virtual
  1-lot at its time priority; the order fills when its allocation is >= 1.
- (b) FIFO: fills when Q exceeds Q_ahead = the current sizes of the orders that were at its price
  ahead of it at j and still rest there.
- (c) and the through trigger of (a) and (b): the first A/B trade strictly through the price.
A fill counts when its event time is in the open life (j, c), c = min(j + 60.05 s, session end).
"""
# ruff: noqa: I001 - the sys.path lines must run before the sibling imports

from __future__ import annotations

import bisect
import heapq
import math
import sys
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
for _p in (str(REPO_ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import kalgo31 as ka  # noqa: E402
import mbo_book31 as mb  # noqa: E402
from data.session import ct_ns  # noqa: E402

NS = 1_000_000_000
MS = 1_000_000
GRID_NS = 300 * NS
EDGE_NS = 300 * NS
LATENCY_NS = 50 * MS
LIFE_NS = 60 * NS
HORIZONS_S = (1, 10, 60)
LAGS_S = (1, 10)
MAX_DAY_GAP_NS = 60 * NS
CUTOFF_TRADE_DATE = date(2024, 3, 1)
CUTOFF_NS = 1_709_251_200 * NS  # 2024-03-01T00:00:00Z: no record on or after it is read
TOP_RULE_CHANGE = date(2023, 10, 2)  # CME S7: from trade date 2023-10-02 only resting fills count
DAY, OVERNIGHT = "DAY", "OVERNIGHT"
MODELS = ("a", "b", "c")
QUEUE, THROUGH = "queue", "through"
BID_UNDEF = int(np.iinfo(np.int64).min)
ASK_UNDEF = int(np.iinfo(np.int64).max)

REASON_NO_RECORDS = "no_records"
REASON_NO_START = "no_valid_book_start"
REASON_GAP = "day_gap_gt_60s"

PLACEMENT_COLUMNS = (
    "trade_date", "session", "symbol", "instrument_id", "raw_symbol", "model", "side", "g_ns",
    "j_ns", "price", "stale", "filled", "t_fill_ns", "trigger", "wait_s", "mid0", "c_half",
    "mo_1", "mo_10", "mo_60", "mo_nd_1", "mo_nd_10", "mo_nd_60", "zs_d1", "zs_d10", "zl_d1",
    "zl_d10", "usda_min", "imb", "touched")
LOOP_COLUMNS = ("trade_date", "symbol", "model", "round_trips", "entries_filled",
                "orders_placed", "mean_rt_s")
IMPLIED_COUNTS = ("n_ab", "vol_ab", "n_none", "vol_none", "n_short", "vol_short", "n_n", "vol_n")
IMPLIED_COLUMNS = ("trade_date", "symbol", "session", *IMPLIED_COUNTS)
DAYS_COLUMNS = ("trade_date", "symbol", "instrument_id", "raw_symbol", "included", "reason",
                "n_records", "inversions", "bad_flag_records", "crossed_moments",
                "max_gap_day_s", "placements_day", "placements_on")


TABLE_COLUMNS = {"placements": PLACEMENT_COLUMNS, "loop": LOOP_COLUMNS,
                 "implied": IMPLIED_COLUMNS, "days": DAYS_COLUMNS}
_F64 = "float64"
COLUMN_TYPES: dict[str, dict[str, str]] = {
    "*": {"trade_date": "date32", "session": "str", "symbol": "str", "instrument_id": "uint32",
          "raw_symbol": "str", "model": "str"},
    "placements": {"side": "int8", "g_ns": "int64", "j_ns": "int64", "price": _F64,
                   "stale": "bool", "filled": "bool", "t_fill_ns": "int64", "trigger": "str",
                   "wait_s": _F64, "mid0": _F64, "c_half": _F64, "imb": _F64, "touched": "bool",
                   "usda_min": _F64,
                   **{f"mo_{h}": _F64 for h in HORIZONS_S},
                   **{f"mo_nd_{h}": _F64 for h in HORIZONS_S},
                   **{f"{c}_d{lag}": _F64 for c in ("zs", "zl") for lag in LAGS_S}},
    "loop": {"round_trips": "int32", "entries_filled": "int32", "orders_placed": "int32",
             "mean_rt_s": _F64},
    "implied": dict.fromkeys(IMPLIED_COUNTS, "int64"),
    "days": {"included": "bool", "reason": "str", "n_records": "int64", "inversions": "int64",
             "bad_flag_records": "int64", "crossed_moments": "int64", "max_gap_day_s": _F64,
             "placements_day": "int64", "placements_on": "int64"}}


class MeasureRefused(RuntimeError):
    """A trade date or record outside what this pilot may measure."""


# ------------------------------------------------------------------ sessions ----
@dataclass(frozen=True, slots=True)
class Session:
    label: str
    lo: int
    hi: int

    def grid(self) -> list[int]:
        """Spec 4 (v2, lead note 2026-10-22): every 5 minutes on the clock with
        open + 5 min <= g < close - 5 min (DAY 08:35 .. 13:10 CT = 56 times, 112 placements)."""
        first = -(-(self.lo + EDGE_NS) // GRID_NS) * GRID_NS
        return list(range(first, self.hi - EDGE_NS, GRID_NS))


def regular_sessions(day: date) -> tuple[Session, Session]:
    """Spec 2 (America/Chicago clock): OVERNIGHT 19:00 CT on the previous calendar day (Sunday for
    Monday) to 07:45 CT, DAY 08:30-13:20 CT."""
    return (Session(OVERNIGHT, ct_ns(day - timedelta(days=1), time(19, 0)),
                    ct_ns(day, time(7, 45))),
            Session(DAY, ct_ns(day, time(8, 30)), ct_ns(day, time(13, 20))))


# ------------------------------------------------------------------ jobs ----
@dataclass(frozen=True)
class SymbolJob:
    symbol: str
    instrument_id: int
    raw_symbol: str
    static_reason: str = ""  # roll exclusions, known before any record is read


@dataclass(frozen=True)
class DayJob:
    day: date
    symbols: tuple[SymbolJob, ...]  # the front month (ZM.v.0) first
    calendar_reason: str = ""
    zm_tick_1e9: int = 100_000_000
    zs_tick_1e9: int | None = None
    zl_tick_1e9: int | None = None
    zs_iid: int | None = None
    zl_iid: int | None = None
    usda_ns: tuple[int, ...] = ()
    kparams: ka.KParams = ka.ZM_K

    @property
    def count_initial_aggressed(self) -> bool:
        return self.day < TOP_RULE_CHANGE


# ------------------------------------------------------------------ virtual orders ----
class VOrder:
    """One simulated passive 1-lot under one fill model (never in the book)."""

    __slots__ = ("model", "s", "bside", "price", "j", "end", "prio", "ahead", "t_fill",
                 "trigger", "mid0", "owner", "row")

    def __init__(self, model: str, s: int, price: int, j: int, end: int, prio: int,
                 ahead: tuple[int, ...] | None, owner: Any, row: int) -> None:
        self.model, self.s, self.price, self.j, self.end = model, s, price, j, end
        self.bside = mb.BID if s > 0 else mb.ASK
        self.prio, self.ahead, self.owner, self.row = prio, ahead, owner, row
        self.t_fill: int | None = None
        self.trigger = ""
        self.mid0 = math.nan


class Loop:
    """Spec 6: one 1-lot at a time in the DAY session under one model."""

    __slots__ = ("model", "session", "last_decide", "entry_side", "is_exit", "rt_start",
                 "waiting", "done", "round_trips", "entries_filled", "orders_placed", "durations",
                 "join_invalid")

    def __init__(self, model: str, session: Session, start: int) -> None:
        self.model, self.session = model, session
        self.last_decide = session.hi - EDGE_NS  # decisions only before close - 5 min
        self.entry_side, self.is_exit, self.rt_start = 1, False, start
        self.waiting = self.done = False
        self.round_trips = self.entries_filled = self.orders_placed = self.join_invalid = 0
        self.durations: list[int] = []

    def side(self) -> int:
        return -self.entry_side if self.is_exit else self.entry_side

    def decide(self, run: InstrumentRun, t: int) -> None:
        if self.done or t >= self.last_decide:
            self.done = True
            return
        run.push(t + LATENCY_NS, run.K_LOOP_JOIN, self)

    def on_join(self, run: InstrumentRun, j: int) -> None:
        if self.done:
            return
        if not run.book.is_valid():
            self.join_invalid += 1
            self.waiting = True  # decided again at the first valid book state
            return
        end = min(j + LIFE_NS + LATENCY_NS, self.session.hi)
        run.new_order(self.model, self.side(), j, end, owner=self, row=-1)
        self.orders_placed += 1

    def on_fill(self, run: InstrumentRun, t: int) -> None:
        if self.is_exit:
            self.round_trips += 1
            self.durations.append(t - self.rt_start)
            self.entry_side, self.is_exit, self.rt_start = -self.entry_side, False, t
        else:
            self.entries_filled += 1
            self.is_exit = True
        self.decide(run, t)

    def on_end(self, run: InstrumentRun, c: int) -> None:
        self.decide(run, c - LATENCY_NS)  # cancel decided at j + 60 s, replacement joins at c

    def on_valid(self, run: InstrumentRun, t: int) -> None:
        if self.waiting and not self.done:
            self.waiting = False
            self.decide(run, t)

    def abort(self) -> None:
        self.done = True


# ------------------------------------------------------------------ the pass ----
@dataclass
class Placement:
    session: Session
    g: int
    j: int
    end: int
    s: int
    price: int
    imb: float
    orders: dict[str, VOrder] = field(default_factory=dict)
    dropped: bool = False


class InstrumentRun:
    """One instrument's pass over its records of one trade date."""

    K_JOIN, K_END, K_LOOP_JOIN = 0, 1, 2

    def __init__(self, sessions: tuple[Session, ...], kparams: ka.KParams, count_initial: bool,
                 loop_session: Session | None = None) -> None:
        self.sessions = sessions
        self.kparams = kparams
        self.book = mb.Book(kparams.top_min, kparams.top_max, count_initial)
        self.count_initial = count_initial
        self.heap: list[tuple[int, int, int, Any]] = []
        self.seq = 0
        self.active: list[VOrder] = []
        self.placements: list[Placement] = []
        self.loops: list[Loop] = []
        self.hist: tuple[list[int], list[int], list[int], list[bool]] = ([], [], [], [])
        self.last_state: tuple[int, int, bool] | None = None
        self.last_valid_mid = math.nan
        self.trades: tuple[list[int], list[int], list[int]] = ([], [], [])
        self.implied = {s.label: [0] * len(IMPLIED_COUNTS) for s in sessions}
        self.diag: dict[str, int] = {}
        self.aggressed: dict[int, int] = {}
        self.bad_periods: list[list[int]] = []  # [start, end) of excluded (bad-book) periods
        for sess in sessions:
            for g in sess.grid():
                self.push(g + LATENCY_NS, self.K_JOIN, (sess, g))
        if loop_session is not None:
            grid = loop_session.grid()
            if grid:
                self.loops = [Loop(m, loop_session, grid[0]) for m in MODELS]
                for lp in self.loops:
                    lp.decide(self, grid[0])

    # ---------------------------------------------------------------- helpers ----
    def push(self, at: int, kind: int, obj: Any) -> None:
        self.seq += 1
        heapq.heappush(self.heap, (at, self.seq, kind, obj))

    def note(self, key: str, n: int = 1) -> None:
        self.diag[key] = self.diag.get(key, 0) + n

    def session_of(self, t: int) -> Session | None:
        for sess in self.sessions:
            if sess.lo <= t < sess.hi:
                return sess
        return None

    def new_order(self, model: str, s: int, j: int, end: int, owner: Any, row: int) -> VOrder:
        book = self.book
        price = book.best(mb.BID if s > 0 else mb.ASK)
        assert price is not None
        ahead = tuple(book.levels[mb.BID if s > 0 else mb.ASK][price][mb.L_ORDERS])
        v = VOrder(model, s, price, j, end, book.seq, ahead if model == "b" else None, owner, row)
        self.active.append(v)
        if owner is not None:
            self.push(end, self.K_END, v)
        return v

    def fill(self, v: VOrder, t: int, trigger: str, mid0: float) -> None:
        v.t_fill, v.trigger, v.mid0 = t, trigger, mid0
        self.active.remove(v)
        if isinstance(v.owner, Loop):
            v.owner.on_fill(self, t)

    # ---------------------------------------------------------------- timers ----
    def fire(self, at: int, kind: int, obj: Any) -> None:
        if kind == self.K_JOIN:
            self._join(obj[0], obj[1], at)
        elif kind == self.K_END:
            self._end(obj, at)
        else:
            obj.on_join(self, at)

    def _join(self, sess: Session, g: int, j: int) -> None:
        book = self.book
        if not book.is_valid():
            self.note("joins_invalid_bad_or_unstarted" if (book.bad or not book.started)
                      else "crossed_moments")
            return
        bid, ask = book.best(mb.BID), book.best(mb.ASK)
        bsz, asz = book.level_total(mb.BID, bid), book.level_total(mb.ASK, ask)
        imb = (bsz - asz) / (bsz + asz)
        end = min(j + LIFE_NS + LATENCY_NS, sess.hi)
        for s in (1, -1):
            pl = Placement(sess, g, j, end, s, bid if s > 0 else ask, s * imb)
            row = len(self.placements)
            self.placements.append(pl)
            for m in MODELS:
                pl.orders[m] = self.new_order(m, s, j, end, owner=None, row=row)
            self.push(end, self.K_END, pl)

    def _end(self, obj: Any, c: int) -> None:
        if isinstance(obj, Placement):
            for v in obj.orders.values():
                if v.t_fill is None and v in self.active:
                    self.active.remove(v)
            return
        v: VOrder = obj
        if v.t_fill is None and v in self.active:
            self.active.remove(v)
            v.owner.on_end(self, c)

    def on_bad(self, t: int) -> None:
        """Spec 2: from a possibly-bad-book record to the next clear (snapshot) the instrument is
        excluded: resting placements are dropped (not written) and resting loop orders are
        removed; a loop already running stops. The loop's row is not written when an excluded
        period overlaps the DAY session (README)."""
        self.bad_periods.append([t, ASK_UNDEF])
        for v in list(self.active):
            if v.owner is None:
                self.placements[v.row].dropped = True
        self.active = []
        for lp in self.loops:
            if not lp.done and t >= lp.session.lo:
                lp.abort()
                self.note("loops_aborted_bad_book")

    def loop_measured(self) -> bool:
        """False when an excluded (bad-book) period overlaps the loop's DAY session."""
        if not self.loops:
            return False
        sess = self.loops[0].session
        return not any(a < sess.hi and b > sess.lo for a, b in self.bad_periods)

    # ---------------------------------------------------------------- events ----
    def close_event(self, t: int, px: int, side_code: int, v_sum: int, f_sum: int,
                    mid0: float, consistent: bool = True) -> None:
        if side_code == mb.SIDE_NONE_CODE:
            return  # side-N trades are never match events for a virtual order
        self.note("events")
        q = min(v_sum, f_sum)
        if f_sum == 0:
            self.note("events_without_passive_fill")
        if not consistent:  # the queue would be read mid-update: no queue fill (conservative)
            self.note("events_mid_update")
            return
        if q <= 0 or not self.active:
            return
        passive = mb.BID if side_code == mb.SIDE_ASK_CODE else mb.ASK
        for v in [o for o in self.active if o.bside == passive and o.price == px
                  and o.model != "c" and t < o.end]:
            if v.model == "b":
                orders = self.book.orders
                q_ahead = 0
                for oid in v.ahead:
                    o = orders.get(oid)
                    if o is not None and o[mb.O_PRICE] == px and o[mb.O_SIDE] == passive:
                        q_ahead += o[mb.O_SIZE]
                if q > q_ahead:
                    self.fill(v, t, QUEUE, mid0)
            elif self._k_allocation(v, passive, px, q) >= 1:
                self.fill(v, t, QUEUE, mid0)

    def _k_allocation(self, v: VOrder, passive: int, px: int, q: int) -> int:
        queue = self.book.queue(passive, px)
        prios = [p for _, _, p in queue]
        idx = bisect.bisect_left(prios, v.prio)
        qty = [n for _, n, _ in queue]
        qty.insert(idx, 1)
        top = self.book.top_at(passive, px)
        top_idx, room = None, None
        if top is not None:
            pos = next(k for k, (oid, _, _) in enumerate(queue) if oid == top[0])
            top_idx, room = (pos + 1 if pos >= idx else pos), top[1]
        return ka.allocate(qty, q, top_idx, room, self.kparams)[idx]

    def through(self, t: int, px: int, mid0: float) -> None:
        for v in [o for o in self.active
                  if (px < o.price if o.s > 0 else px > o.price) and t < o.end]:
            self.fill(v, t, THROUGH, mid0)

    def implied_check(self, t: int, px: int, sz: int, side_code: int,
                      consistent: bool = True) -> None:
        sess = self.session_of(t)
        book = self.book
        if sess is None or not book.started or book.bad:
            return
        if not consistent:
            self.note("implied_trades_mid_update")
            return
        c = self.implied[sess.label]
        if side_code == mb.SIDE_NONE_CODE:
            c[6] += 1
            c[7] += sz
            return
        c[0] += 1
        c[1] += sz
        resting = book.level_total(mb.BID if side_code == mb.SIDE_ASK_CODE else mb.ASK, px)
        if resting == 0:
            c[2] += 1
            c[3] += sz
        if resting < sz:
            c[4] += 1
            c[5] += sz

    def commit(self, t: int) -> None:
        book = self.book
        bp, ap = book.prices
        b = bp[-1] if bp else BID_UNDEF
        a = ap[0] if ap else ASK_UNDEF
        valid = book.started and not book.bad and bool(bp) and bool(ap) and b < a
        state = (b, a, valid)
        if state == self.last_state:
            return
        self.last_state = state
        h = self.hist
        h[0].append(t)
        h[1].append(b)
        h[2].append(a)
        h[3].append(valid)
        if valid:
            self.last_valid_mid = (b + a) / 2.0
            for lp in self.loops:
                if lp.waiting:
                    lp.on_valid(self, t)

    # ---------------------------------------------------------------- main loop ----
    def run(self, rec: dict[str, np.ndarray], chunk: int = 200_000) -> None:
        n = len(rec["t"])
        for lo in range(0, n, chunk):
            hi = min(n, lo + chunk)
            self._run_chunk(rec["t"][lo:hi].tolist(), rec["action"][lo:hi].tolist(),
                            rec["side"][lo:hi].tolist(), rec["price"][lo:hi].tolist(),
                            rec["size"][lo:hi].tolist(), rec["order_id"][lo:hi].tolist(),
                            rec["flags"][lo:hi].tolist())
        self.drain()

    def drain(self) -> None:
        if self._group is not None:
            self.close_group(self._group)
            self._group = None
        while self.heap:
            at, _, kind, obj = heapq.heappop(self.heap)
            self.fire(at, kind, obj)

    # [t, price, side code, v sum, f sum, mid0, book consistent before the event, F pairs]
    _group: list | None = None
    _consistent = True  # the instrument's last record carried F_LAST (never read mid-update)
    _book_ok = True  # no book record since the last F_LAST record (T, F, N change nothing)

    def close_group(self, group: list) -> None:
        """Allocate the event on the book as it stood before it, then count its fills against
        TOP Max (review B1: the TOP room is the one before the event's own fills)."""
        self.close_event(*group[:7])
        for oid, sz in group[7]:
            self.book.on_fill(oid, sz)

    def _run_chunk(self, ts: list, acts: list, sides: list, pxs: list, szs: list, oids: list,
                   fls: list) -> None:
        book, heap = self.book, self.heap
        A, C, M, R, T, F = (mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY, mb.ACT_CLEAR,
                            mb.ACT_TRADE, mb.ACT_FILL)
        S_A, S_B, S_N = mb.SIDE_ASK_CODE, mb.SIDE_BID_CODE, mb.SIDE_NONE_CODE
        BAD, SNAP, LAST, TOBMBP = mb.F_MAYBE_BAD_BOOK, mb.F_SNAPSHOT, mb.F_LAST, mb.F_TOB | mb.F_MBP
        trades_t, trades_px, trades_side = self.trades
        group = self._group
        ok, book_ok = self._consistent, self._book_ok
        for t, act, side, px, sz, oid, fl in zip(ts, acts, sides, pxs, szs, oids, fls,
                                                 strict=True):
            was_ok, ok = ok, (fl & LAST) != 0
            was_book_ok = book_ok  # events and the implied check: the book unchanged since F_LAST
            book_ok = ok or (book_ok and act in (T, F, mb.ACT_NONE))
            if group is not None:
                if act == T:
                    if not (group[0] == t and group[1] == px and group[2] == side):
                        self.close_group(group)
                        group = None
                elif act == F:
                    if group[0] != t:
                        self.close_group(group)
                        group = None
                else:
                    self.close_group(group)
                    group = None
            if heap and heap[0][0] < t:
                if was_ok:  # timers read the book only after an F_LAST record
                    while heap and heap[0][0] < t:
                        at, _, kind, obj = heapq.heappop(heap)
                        self.fire(at, kind, obj)
                else:
                    self.note("timers_deferred_mid_update")
            if not book.started and act != R:
                self.note("records_before_valid_start")
                continue
            if fl & (BAD | TOBMBP):
                self.note("bad_book_flag_records" if fl & BAD else "tob_or_mbp_records")
                if not book.bad:
                    book.mark_bad()
                    self.on_bad(t)
                    self.commit(t)
            if book.in_snapshot and not fl & SNAP:
                book.end_snapshot()
            if act == T:
                trades_t.append(t)
                trades_px.append(px)
                trades_side.append(side)
                self.implied_check(t, px, sz, side, was_book_ok)
                if side == S_N:
                    if group is None:
                        group = [t, px, side, 0, 0, self.last_valid_mid, was_book_ok, []]
                elif group is None:
                    if self.active:
                        self.through(t, px, self.last_valid_mid)
                    group = [t, px, side, sz, 0, self.last_valid_mid, was_book_ok, []]
                else:
                    group[3] += sz
                if self.count_initial and oid and side != S_N:
                    self.aggressed[oid] = self.aggressed.get(oid, 0) + sz
                if ok:
                    self.commit(t)
                continue
            if act == F:
                if group is None:
                    self.note("fill_records_without_trade")
                elif group[2] != S_N and px == group[1] and side == (S_B if group[2] == S_A
                                                                     else S_A):
                    group[4] += sz  # a resting order on the passive side
                if group is None:
                    book.on_fill(oid, sz)
                else:
                    group[7].append((oid, sz))  # counted against TOP Max after the event
                if ok:
                    self.commit(t)
                continue
            bs = mb.BID if side == S_B else mb.ASK
            if act in (A, M) and side != S_B and side != S_A:
                self.note("book_records_with_side_n")
                continue
            if act == A:
                book.add(oid, bs, px, sz, self.aggressed.pop(oid, 0) if self.count_initial
                         else 0)
            elif act == C:
                book.cancel(oid, sz)
            elif act == M:
                book.modify(oid, bs, px, sz)
            elif act == R:
                if book.bad:
                    self.bad_periods[-1][1] = t
                book.clear(bool(fl & SNAP))
                self.note("clear_records")
            if fl & SNAP and fl & LAST:
                book.end_snapshot()
            if ok:
                self.commit(t)
        self._group = group
        self._consistent, self._book_ok = ok, book_ok


# ------------------------------------------------------------------ post-pass ----
@dataclass(frozen=True)
class History:
    t: np.ndarray
    bid: np.ndarray
    ask: np.ndarray
    valid: np.ndarray

    @classmethod
    def of(cls, run: InstrumentRun) -> History:
        h = run.hist
        return cls(np.asarray(h[0], dtype=np.int64), np.asarray(h[1], dtype=np.int64),
                   np.asarray(h[2], dtype=np.int64), np.asarray(h[3], dtype=bool))

    def index(self, at: int) -> int:
        return int(np.searchsorted(self.t, at, side="right")) - 1

    def mid(self, k: int) -> float:
        return (int(self.bid[k]) + int(self.ask[k])) / 2.0


def markouts(hist: History, inv_cum: np.ndarray, last_valid: np.ndarray, t_f: int, s: int,
             mid0: float, hi: int, tick: int, drops: dict[str, int]
             ) -> tuple[list[float], list[float]]:
    """Spec 5: (headline, no-drop) markout_h = s x (mid(t_f + h) - mid0) / tick per horizon.
    Headline: dropped when t_f + h reaches the session end, or any book state over [t_f, t_f + h]
    is invalid (crossed, locked, an empty side, or an excluded period), or no state precedes t_f.
    No-drop: the last valid state at or before t_f + h, dropped only when none is active after
    t_f (or at the session end)."""
    head, nodrop = [], []
    k_f = hist.index(t_f)
    for h in HORIZONS_S:
        t_h = t_f + h * NS
        if t_h >= hi or math.isnan(mid0):
            reason = "session_end" if t_h >= hi else "no_mid0"
            drops[reason] = drops.get(reason, 0) + 1
            head.append(math.nan)
            nodrop.append(math.nan)
            continue
        k_h = hist.index(t_h)
        if k_f < 0 or int(inv_cum[k_h + 1] - inv_cum[k_f]) > 0:
            key = "no_book" if k_f < 0 else "invalid_book"
            drops[key] = drops.get(key, 0) + 1
            head.append(math.nan)
        else:
            head.append(s * (hist.mid(k_h) - mid0) / tick)
        k_v = int(last_valid[k_h]) if k_h >= 0 else -1
        if k_f < 0 or k_v < k_f:
            drops["nodrop_no_valid"] = drops.get("nodrop_no_valid", 0) + 1
            nodrop.append(math.nan)
        else:
            nodrop.append(s * (hist.mid(k_v) - mid0) / tick)
    return head, nodrop


def last_valid_index(valid: np.ndarray) -> np.ndarray:
    idx = np.where(valid, np.arange(len(valid)), -1)
    return np.maximum.accumulate(idx) if len(idx) else idx


@dataclass(frozen=True)
class CondSeries:
    """A ZS or ZL mbp-1 state series of the trade date (time axis, mid, validity, tick)."""

    t: np.ndarray
    mid: np.ndarray
    last_valid: np.ndarray
    tick: int

    @classmethod
    def of(cls, rec: dict[str, np.ndarray] | None, tick: int | None) -> CondSeries | None:
        if rec is None or tick is None or len(rec["t"]) == 0:
            return None
        bid, ask = rec["bid_px"].astype(np.int64), rec["ask_px"].astype(np.int64)
        valid = ((bid != mb.UNDEF_PRICE) & (ask != mb.UNDEF_PRICE) & (bid != BID_UNDEF)
                 & (bid < ask) & ((rec["flags"] & mb.F_MAYBE_BAD_BOOK) == 0))
        mid = (bid.astype(np.float64) + ask.astype(np.float64)) / 2.0
        return cls(rec["t"], mid, last_valid_index(valid), tick)

    def mid_at(self, at: int, lo: int) -> float:
        """Last valid mid at or before ``at`` from a record inside the session (t >= lo)."""
        k = int(np.searchsorted(self.t, at, side="right")) - 1
        if k < 0:
            return math.nan
        kv = int(self.last_valid[k])
        if kv < 0 or int(self.t[kv]) < lo:
            return math.nan
        return float(self.mid[kv])

    def move(self, t_f: int, lag_s: int, lo: int) -> float:
        return (self.mid_at(t_f, lo) - self.mid_at(t_f - lag_s * NS, lo)) / self.tick


def usda_minutes(t_f: int, releases: tuple[int, ...]) -> float:
    """Signed minutes from the nearest release on the trade date (ties: the earlier release)."""
    if not releases:
        return math.nan
    best = min(releases, key=lambda r: (abs(t_f - r), r))
    return (t_f - best) / (60 * NS)


def touched(hist: History, trades: tuple[np.ndarray, np.ndarray], j: int, c: int, price: int,
            s: int) -> bool:
    """E.28 touch: inside (j, c) a trade at or through the price (any side), or the opposite best
    quote at or through it."""
    tt, tp = trades
    a, b = int(np.searchsorted(tt, j, side="right")), int(np.searchsorted(tt, c, side="left"))
    if a < b and bool(np.any(tp[a:b] <= price if s > 0 else tp[a:b] >= price)):
        return True
    a, b = int(np.searchsorted(hist.t, j, side="right")), int(np.searchsorted(hist.t, c,
                                                                                side="left"))
    if a >= b:
        return False
    if s > 0:
        opp = hist.ask[a:b]
        return bool(np.any((opp != ASK_UNDEF) & (opp <= price)))
    opp = hist.bid[a:b]
    return bool(np.any((opp != BID_UNDEF) & (opp >= price)))


def is_stale(hist: History, g: int, s: int, price: int) -> bool:
    k = hist.index(g)
    if k < 0:
        return True
    return int(hist.bid[k] if s > 0 else hist.ask[k]) != price


# ------------------------------------------------------------------ one symbol ----
@dataclass
class SymbolResult:
    job: SymbolJob
    reason: str
    n_records: int
    inversions: int
    bad_flag_records: int
    max_gap_day_s: float
    run: InstrumentRun | None = None
    diag: dict[str, Any] = field(default_factory=dict)


def instrument_records(zm: dict[str, np.ndarray], iid: int) -> dict[str, np.ndarray]:
    """The instrument's records in file order with the spec-2 time axis under key ``t``."""
    mask = zm["instrument_id"] == iid
    rec = {k: v[mask] for k, v in zm.items()}
    rec["t"], rec["inversions"] = mb.time_axis(rec["ts_event"], rec["ts_recv"], rec["flags"])
    return rec


def max_gap_s(t: np.ndarray, sess: Session) -> float:
    """Largest gap between consecutive records inside the session (spec 2; review B9: the open
    and close are not edges). Fewer than two records inside: the session length (excluded)."""
    inside = t[(t >= sess.lo) & (t < sess.hi)].astype(np.int64)
    if len(inside) < 2:
        return (sess.hi - sess.lo) / NS
    return float(np.max(np.diff(inside))) / NS


def has_valid_start(rec: dict[str, np.ndarray], open_lo: int) -> bool:
    """Spec 2: a clear (snapshot) record at or before the first session open."""
    clears = rec["t"][rec["action"] == mb.ACT_CLEAR]
    return bool(len(clears)) and int(clears[0]) <= open_lo


def symbol_prepass(job: SymbolJob, rec: dict[str, np.ndarray], sessions: tuple[Session, ...],
                   calendar_reason: str) -> SymbolResult:
    day = next(s for s in sessions if s.label == DAY)
    n = len(rec["t"])
    reason = calendar_reason or job.static_reason
    if not reason and n == 0:
        reason = REASON_NO_RECORDS
    if not reason and not has_valid_start(rec, min(s.lo for s in sessions)):
        reason = REASON_NO_START
    return SymbolResult(job, reason, n, int(rec["inversions"]),
                        int(np.count_nonzero(rec["flags"] & mb.F_MAYBE_BAD_BOOK)),
                        max_gap_s(rec["t"], day))


# ------------------------------------------------------------------ the day ----
def _guard(day: date, arrays: list[dict[str, np.ndarray] | None]) -> None:
    if day >= CUTOFF_TRADE_DATE:
        raise MeasureRefused(f"trade date {day} is on or after {CUTOFF_TRADE_DATE}")
    for a in arrays:
        if a is None or len(a["ts_recv"]) == 0:
            continue
        if int(a["ts_recv"].max()) >= CUTOFF_NS or int(a["ts_event"].max()) >= CUTOFF_NS:
            raise MeasureRefused(f"trade date {day}: a record is dated on or after 2024-03-01")


def measure_day(job: DayJob, zm: dict[str, np.ndarray], zs: dict[str, np.ndarray] | None,
                zl: dict[str, np.ndarray] | None) -> dict[str, Any]:
    """The four tables (TABLES31.md) of one trade date as column dicts, plus ``diag``."""
    _guard(job.day, [zm, zs, zl])
    sessions = regular_sessions(job.day)
    day_sess = sessions[1]
    results: list[SymbolResult] = []
    recs = []
    for sj in job.symbols:
        rec = instrument_records(zm, sj.instrument_id)
        recs.append(rec)
        results.append(symbol_prepass(sj, rec, sessions, job.calendar_reason))
    front_gap = results[0].max_gap_day_s if results else math.nan
    for res in results:
        if not res.reason and front_gap > MAX_DAY_GAP_NS / NS:
            res.reason = REASON_GAP
    for k, (res, rec) in enumerate(zip(results, recs, strict=True)):
        if res.reason:
            continue
        run = InstrumentRun(sessions, job.kparams, job.count_initial_aggressed,
                            loop_session=day_sess if k == 0 else None)
        run.run(rec)
        res.run = run
    conds = {"zs": CondSeries.of(_filter(zs, job.zs_iid), job.zs_tick_1e9),
             "zl": CondSeries.of(_filter(zl, job.zl_iid), job.zl_tick_1e9)}
    return build_tables(job, results, conds)


def _filter(rec: dict[str, np.ndarray] | None, iid: int | None) -> dict[str, np.ndarray] | None:
    if rec is None:
        return None
    if iid is not None:
        mask = rec["instrument_id"] == iid
        rec = {k: v[mask] for k, v in rec.items()}
    t, _ = mb.time_axis(rec["ts_event"], rec["ts_recv"], rec["flags"])
    return {**rec, "t": t}


def _empty(columns: tuple[str, ...]) -> dict[str, list]:
    return {c: [] for c in columns}


def build_tables(job: DayJob, results: list[SymbolResult],
                 conds: dict[str, CondSeries | None]) -> dict[str, Any]:
    tables = {"placements": _empty(PLACEMENT_COLUMNS), "loop": _empty(LOOP_COLUMNS),
              "implied": _empty(IMPLIED_COLUMNS), "days": _empty(DAYS_COLUMNS)}
    diag: dict[str, Any] = {"trade_date": job.day.isoformat(), "symbols": {}}
    for res in results:
        counts = {DAY: 0, OVERNIGHT: 0}
        sym_diag: dict[str, Any] = {"reason": res.reason}
        if res.run is not None:
            counts, drops = _placement_rows(job, res, conds, tables["placements"])
            _loop_rows(job, res, tables["loop"])
            _implied_rows(job, res, tables["implied"])
            sym_diag.update({"run": dict(res.run.diag), "book": dict(res.run.book.anomalies),
                             "markout_drops": drops,
                             "placements_dropped_bad_book": sum(
                                 p.dropped for p in res.run.placements)})
        diag["symbols"][res.job.symbol] = sym_diag
        sj = res.job
        row = {"trade_date": job.day, "symbol": sj.symbol, "instrument_id": sj.instrument_id,
               "raw_symbol": sj.raw_symbol, "included": not res.reason, "reason": res.reason,
               "n_records": res.n_records, "inversions": res.inversions,
               "bad_flag_records": res.bad_flag_records,
               "crossed_moments": res.run.diag.get("crossed_moments", 0) if res.run else 0,
               "max_gap_day_s": res.max_gap_day_s, "placements_day": counts[DAY],
               "placements_on": counts[OVERNIGHT]}
        for c in DAYS_COLUMNS:
            tables["days"][c].append(row[c])
    tables["diag"] = diag
    return tables


def _placement_rows(job: DayJob, res: SymbolResult, conds: dict[str, CondSeries | None],
                    out: dict[str, list]) -> tuple[dict[str, int], dict[str, int]]:
    run = res.run
    assert run is not None
    hist = History.of(run)
    inv_cum = np.concatenate(([0], np.cumsum(~hist.valid)))
    lv = last_valid_index(hist.valid)
    trades = (np.asarray(run.trades[0], dtype=np.int64), np.asarray(run.trades[1], dtype=np.int64))
    tick = job.zm_tick_1e9
    counts = {DAY: 0, OVERNIGHT: 0}
    drops: dict[str, int] = {}
    for pl in run.placements:
        if pl.dropped:
            continue
        counts[pl.session.label] += 1
        stale = is_stale(hist, pl.g, pl.s, pl.price)
        touch = touched(hist, trades, pl.j, pl.end, pl.price, pl.s)
        for m in MODELS:
            v = pl.orders[m]
            row = _fill_fields(job, v, pl, hist, inv_cum, lv, conds, tick, drops)
            row.update({"trade_date": job.day, "session": pl.session.label,
                        "symbol": res.job.symbol, "instrument_id": res.job.instrument_id,
                        "raw_symbol": res.job.raw_symbol, "model": m, "side": pl.s,
                        "g_ns": pl.g, "j_ns": pl.j, "price": pl.price / 1e9, "stale": stale,
                        "imb": pl.imb, "touched": touch})
            for c in PLACEMENT_COLUMNS:
                out[c].append(row[c])
    return counts, drops


def _fill_fields(job: DayJob, v: VOrder, pl: Placement, hist: History, inv_cum: np.ndarray,
                 lv: np.ndarray, conds: dict[str, CondSeries | None], tick: int,
                 drops: dict[str, int]) -> dict[str, Any]:
    nan = math.nan
    row: dict[str, Any] = {"filled": v.t_fill is not None,
                           "t_fill_ns": -1 if v.t_fill is None else v.t_fill,
                           "trigger": v.trigger,
                           "wait_s": (pl.end - pl.j) / NS if v.t_fill is None
                           else (v.t_fill - pl.j) / NS,
                           "mid0": nan, "c_half": nan, "usda_min": nan}
    for h in HORIZONS_S:
        row[f"mo_{h}"] = row[f"mo_nd_{h}"] = nan
    for name in ("zs", "zl"):
        for lag in LAGS_S:
            row[f"{name}_d{lag}"] = nan
    if v.t_fill is None:
        return row
    t_f, s = v.t_fill, pl.s
    row["mid0"] = v.mid0 / 1e9
    row["c_half"] = s * (v.mid0 - pl.price) / tick
    head, nodrop = markouts(hist, inv_cum, lv, t_f, s, v.mid0, pl.session.hi, tick, drops)
    for h, a, b in zip(HORIZONS_S, head, nodrop, strict=True):
        row[f"mo_{h}"], row[f"mo_nd_{h}"] = a, b
    for name, series in conds.items():
        if series is not None:
            for lag in LAGS_S:
                row[f"{name}_d{lag}"] = series.move(t_f, lag, pl.session.lo)
    row["usda_min"] = usda_minutes(t_f, job.usda_ns)
    return row


def _loop_rows(job: DayJob, res: SymbolResult, out: dict[str, list]) -> None:
    run = res.run
    assert run is not None
    if run.loops and not run.loop_measured():
        run.note("loop_rows_omitted_bad_book")
        return
    for lp in run.loops:
        mean = (float(np.mean(lp.durations)) / NS) if lp.durations else math.nan
        row = {"trade_date": job.day, "symbol": res.job.symbol, "model": lp.model,
               "round_trips": lp.round_trips, "entries_filled": lp.entries_filled,
               "orders_placed": lp.orders_placed, "mean_rt_s": mean}
        for c in LOOP_COLUMNS:
            out[c].append(row[c])


def _implied_rows(job: DayJob, res: SymbolResult, out: dict[str, list]) -> None:
    run = res.run
    assert run is not None
    for sess in run.sessions:
        counts = run.implied[sess.label]
        row = {"trade_date": job.day, "symbol": res.job.symbol, "session": sess.label,
               **dict(zip(IMPLIED_COUNTS, counts, strict=True))}
        for c in IMPLIED_COLUMNS:
            out[c].append(row[c])
