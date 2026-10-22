"""Stream an mbp-1 DBN file one trade date at a time, reduced to what spec sections 2-4 need.

Memory: the file is decoded in chunks (``chunk_records``, default 500,000 records of 80 bytes);
each trade date keeps only (a) every trade, (b) the records where the best bid price, best ask
price or book validity changes, (c) the book state (prices and displayed sizes) at each
placement join instant j and at each grid time g (for the stale-placement share, RS-06), and
(d) running counts. That is exact for every statistic of the spec:
the queue at join needs sizes only at j; touches, mids and the crossed/locked/empty checks
depend on prices and validity only, which change only at the kept records. So the peak stays
near one chunk plus one reduced day (well under 2 GB even for MES/MNQ-sized days).

Order of records (frozen spec section 2: "records sorted by ts_recv then the exchange sequence,
with ts_event (made non-decreasing, inversions counted) as the time axis"): each chunk segment is
stably sorted by ts_recv, then sequence (np.lexsort), which equals the file order Databento
writes. Sequence and ts_event inversions in that order are counted, never
hidden. The time axis is ts_event (exchange time), made non-decreasing by a running maximum
(the adjusted records are counted). Records with a bad-data flag (F_BAD_TS_RECV,
F_MAYBE_BAD_BOOK) are dropped from the book and trades and counted; they still count as
records for the MAIN-session gap check (a data gap is a gap in what was received). Trades are
counted by aggressor side (A, B, N) per date (RS-03: N marks implied-involved or opening trades,
which never add to V(t) and never trigger a fill; measure_core).
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

import pilot_common as pc

UNDEF_PRICE = np.iinfo(np.int64).max  # Databento's UNDEF_PRICE
F_BAD_TS_RECV = 1 << 3
F_MAYBE_BAD_BOOK = 1 << 2
FLAG_BITS = {"F_LAST": 1 << 7, "F_TOB": 1 << 6, "F_SNAPSHOT": 1 << 5, "F_MBP": 1 << 4,
             "F_BAD_TS_RECV": F_BAD_TS_RECV, "F_MAYBE_BAD_BOOK": F_MAYBE_BAD_BOOK}
ACT_TRADE = ord("T")
SIDE_ASK, SIDE_BID, SIDE_NONE = ord("A"), ord("B"), ord("N")  # trade side = the aggressor
BID_UNDEF = np.iinfo(np.int64).min
ASK_UNDEF = np.iinfo(np.int64).max
DEFAULT_CHUNK_RECORDS = 500_000


class OffTickError(ValueError):
    """A defined price is not a whole number of ticks: the tick parameter is wrong."""


def tick_units(tick: float) -> int:
    """The tick in Databento's 1e-9 price units, exactly, else ValueError."""
    units = round(tick * 1e9)
    if tick <= 0 or units <= 0 or abs(tick * 1e9 - units) > 1e-6:
        raise ValueError(f"tick {tick!r} is not a positive whole number of 1e-9 price units")
    return int(units)


def to_ticks(px: np.ndarray, tick_1e9: int, undef_fill: int) -> tuple[np.ndarray, int]:
    """Prices in ticks (int64), undefined prices set to ``undef_fill``; and the off-tick count."""
    px = px.astype(np.int64, copy=False)
    defined = px != UNDEF_PRICE
    out = np.full(px.shape, undef_fill, dtype=np.int64)
    q, r = np.divmod(px[defined], tick_1e9)
    out[defined] = q
    return out, int(np.count_nonzero(r))


@dataclass
class DayBook:
    """One trade date, reduced. Times are ts_event ns (non-decreasing)."""

    day: date
    plan: pc.DayPlan
    join_ns: np.ndarray
    j_bid: np.ndarray
    j_ask: np.ndarray
    j_bsz: np.ndarray
    j_asz: np.ndarray
    j_valid: np.ndarray
    j_has: np.ndarray
    chg_ts: np.ndarray
    chg_bid: np.ndarray
    chg_ask: np.ndarray
    chg_valid: np.ndarray
    tr_ts: np.ndarray
    tr_px: np.ndarray
    tr_sz: np.ndarray
    tr_side: np.ndarray
    counts: dict[str, int] = field(default_factory=dict)
    main_max_gap_ns: int | None = None
    main_records: int = 0
    instrument_ids: list[str] = field(default_factory=list)
    first_ts_event: int | None = None
    last_ts_event: int | None = None
    invalid_ns: dict[str, int] = field(default_factory=dict)
    g_bid: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.int64))
    g_ask: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.int64))
    g_has: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))

    def __post_init__(self) -> None:
        bad = (~self.chg_valid).astype(np.int64)
        self.chg_invalid_cum = np.concatenate([[0], np.cumsum(bad)])
        self.valid_idx = np.flatnonzero(self.chg_valid)  # for the no-drop markouts (RS-05)

    def state_index(self, t: int) -> int:
        """Index of the last kept book change at or before ``t`` (-1: none yet)."""
        return int(np.searchsorted(self.chg_ts, t, side="right")) - 1


class InstantStates:
    """The book state at fixed sorted instants: the last kept record with time <= the instant.
    An instant at or after a segment's last time waits for later segments (a later record may
    share its time); ``final`` resolves the rest from the last state seen."""

    def __init__(self, instants: np.ndarray) -> None:
        self.ns = instants
        m = len(instants)
        self.bid = np.full(m, BID_UNDEF, dtype=np.int64)
        self.ask = np.full(m, ASK_UNDEF, dtype=np.int64)
        self.bsz = np.zeros(m, dtype=np.int64)
        self.asz = np.zeros(m, dtype=np.int64)
        self.valid = np.zeros(m, dtype=bool)
        self.has = np.zeros(m, dtype=bool)
        self._next = 0

    def resolve(self, t: np.ndarray, cols: tuple[np.ndarray, ...],
                last: tuple[int, int, int, int, bool] | None, *, final: bool) -> None:
        pending = self.ns[self._next:]
        if len(pending) == 0:
            return
        n_res = len(pending) if final else int(np.searchsorted(pending, t[-1], side="left"))
        if n_res == 0:
            return
        idx = np.searchsorted(t, pending[:n_res], side="right") - 1 if len(t) \
            else np.full(n_res, -1)
        rows = np.arange(self._next, self._next + n_res)
        inside = idx >= 0
        targets = (self.bid, self.ask, self.bsz, self.asz, self.valid)
        if inside.any():
            for arr, col in zip(targets, cols, strict=True):
                arr[rows[inside]] = col[idx[inside]]
            self.has[rows[inside]] = True
        if (~inside).any() and last is not None:
            for arr, value in zip(targets, last, strict=True):
                arr[rows[~inside]] = value
            self.has[rows[~inside]] = True
        self._next += n_res


@dataclass
class _GapTracker:
    lo: int
    hi: int
    last: int
    max_gap: int = 0
    n: int = 0


class DayAccumulator:
    """Feeds one trade date's records (in segments, in file order) and builds its DayBook."""

    def __init__(self, plan: pc.DayPlan, tick_1e9: int) -> None:
        self.plan = plan
        self.tick_1e9 = tick_1e9
        self.join_ns = plan.grid_ns + pc.LATENCY_NS
        self.at_j = InstantStates(self.join_ns)
        self.at_g = InstantStates(plan.grid_ns)
        self._last: tuple[int, int, int, int, bool] | None = None
        self._last_t: int | None = None
        self._last_te: int | None = None
        self._last_recv: int | None = None
        self._last_seq: int | None = None
        self._chg: list[tuple[np.ndarray, ...]] = []
        self._tr: list[tuple[np.ndarray, ...]] = []
        self._gaps = [_GapTracker(p.lo, p.hi, p.lo) for p in plan.main_pieces()]
        self.counts: dict[str, int] = {}
        self._ids: dict[str, None] = {}
        self.first_ts_event: int | None = None
        self.last_ts_event: int | None = None

    def _add(self, key: str, n: int) -> None:
        if n:
            self.counts[key] = self.counts.get(key, 0) + int(n)

    # ------------------------------------------------------------ feed ----
    def feed(self, seg: np.ndarray) -> None:
        if len(seg) == 0:
            return
        self._count_raw(seg)
        order = np.lexsort((seg["sequence"], seg["ts_recv"]))
        if np.any(order != np.arange(len(seg))):
            self._add("records_reordered", int(np.count_nonzero(order != np.arange(len(seg)))))
            seg = seg[order]
        t = self._time_axis(seg)
        self._track_gaps(t)
        flags = seg["flags"].astype(np.int64)
        bad_ts = (flags & F_BAD_TS_RECV) != 0
        bad_book = (flags & F_MAYBE_BAD_BOOK) != 0
        self._add("dropped_bad_ts_recv", int(np.count_nonzero(bad_ts)))
        self._add("dropped_maybe_bad_book", int(np.count_nonzero(bad_book)))
        keep = ~(bad_ts | bad_book)
        self._add("dropped_bad_flag_records", int(np.count_nonzero(~keep)))
        if not keep.any():
            return
        self._feed_kept(seg[keep], t[keep])

    def _count_raw(self, seg: np.ndarray) -> None:
        self._add("records", len(seg))
        for code, n in zip(*np.unique(seg["action"], return_counts=True), strict=True):
            self._add(f"action_{code.decode() if isinstance(code, bytes) else code}", int(n))
        for sym in np.unique(seg["instrument_id"]).tolist():
            self._ids.setdefault(str(sym), None)
        te = seg["ts_event"].astype(np.int64)
        lo, hi = int(te.min()), int(te.max())
        self.first_ts_event = lo if self.first_ts_event is None else min(lo, self.first_ts_event)
        self.last_ts_event = hi if self.last_ts_event is None else max(hi, self.last_ts_event)

    def _time_axis(self, seg: np.ndarray) -> np.ndarray:
        recv = seg["ts_recv"].astype(np.int64)
        seq = seg["sequence"].astype(np.int64)
        if self._last_recv is not None and recv[0] < self._last_recv:
            self._add("ts_recv_inversions_across_segments", 1)
        seq_prev = np.concatenate([[self._last_seq if self._last_seq is not None else seq[0]],
                                   seq[:-1]])
        self._add("sequence_inversions", int(np.count_nonzero(seq < seq_prev)))
        te = seg["ts_event"].astype(np.int64)
        prev_te = np.concatenate([[self._last_te if self._last_te is not None else te[0]],
                                  te[:-1]])
        self._add("ts_event_inversions", int(np.count_nonzero(te < prev_te)))
        base = te if self._last_t is None else np.concatenate([[self._last_t], te])
        t = np.maximum.accumulate(base)
        t = t if self._last_t is None else t[1:]
        self._add("ts_event_raised_to_running_max", int(np.count_nonzero(t != te)))
        self._last_recv, self._last_seq = int(recv[-1]), int(seq[-1])
        self._last_te, self._last_t = int(te[-1]), int(t[-1])
        return t

    def _track_gaps(self, t: np.ndarray) -> None:
        for tr in self._gaps:
            a = int(np.searchsorted(t, tr.lo, side="left"))
            b = int(np.searchsorted(t, tr.hi, side="left"))
            if a == b:
                continue
            inside = t[a:b]
            gaps = np.diff(np.concatenate([[tr.last], inside]))
            tr.max_gap = max(tr.max_gap, int(gaps.max()))
            tr.last = int(inside[-1])
            tr.n += b - a

    def _feed_kept(self, seg: np.ndarray, t: np.ndarray) -> None:
        bid, off_b = to_ticks(seg["bid_px_00"], self.tick_1e9, BID_UNDEF)
        ask, off_a = to_ticks(seg["ask_px_00"], self.tick_1e9, ASK_UNDEF)
        bsz = seg["bid_sz_00"].astype(np.int64)
        asz = seg["ask_sz_00"].astype(np.int64)
        empty = (bid == BID_UNDEF) | (ask == ASK_UNDEF) | (bsz <= 0) | (asz <= 0)
        locked = ~empty & (bid == ask)
        crossed = ~empty & (bid > ask)
        valid = ~(empty | locked | crossed)
        self._add("records_empty_side", int(np.count_nonzero(empty)))
        self._add("records_locked", int(np.count_nonzero(locked)))
        self._add("records_crossed", int(np.count_nonzero(crossed)))
        for states in (self.at_j, self.at_g):
            states.resolve(t, (bid, ask, bsz, asz, valid), self._last, final=False)
        self._keep_changes(t, bid, ask, valid)
        is_tr = seg["action"].view(np.uint8) == ACT_TRADE
        if is_tr.any():
            px, off_t = to_ticks(seg["price"][is_tr], self.tick_1e9, BID_UNDEF)
            ok = px != BID_UNDEF  # a trade without a price can neither fill nor touch
            self._add("trades_undefined_price_dropped", int(np.count_nonzero(~ok)))
            self._tr.append((t[is_tr][ok], px[ok], seg["size"][is_tr][ok].astype(np.int64),
                             seg["side"][is_tr][ok].view(np.uint8).astype(np.int64)))
            self._add("trades", int(np.count_nonzero(ok)))
            sides = seg["side"][is_tr][ok].view(np.uint8)
            for name, code in (("A", SIDE_ASK), ("B", SIDE_BID), ("N", SIDE_NONE)):
                self._add(f"trades_side_{name}", int(np.count_nonzero(sides == code)))
            self._add("off_tick_prices", off_t)
        self._add("off_tick_prices", off_b + off_a)
        self._last = (int(bid[-1]), int(ask[-1]), int(bsz[-1]), int(asz[-1]), bool(valid[-1]))

    def _keep_changes(self, t: np.ndarray, bid: np.ndarray, ask: np.ndarray,
                      valid: np.ndarray) -> None:
        if self._last is None:
            lb, la, lv = bid[0], ask[0], valid[0]
        else:
            lb, la, _, _, lv = self._last
        pb, pa, pv = np.r_[lb, bid[:-1]], np.r_[la, ask[:-1]], np.r_[lv, valid[:-1]]
        changed = (bid != pb) | (ask != pa) | (valid != pv)
        if self._last is None:
            changed[0] = True  # the day's first book state
        if changed.any():
            self._chg.append((t[changed], bid[changed], ask[changed], valid[changed]))

    # ------------------------------------------------------------ finish ----
    def finish(self) -> DayBook:
        empty_i = np.zeros(0, dtype=np.int64)
        cols = (empty_i, empty_i, empty_i, empty_i, np.zeros(0, dtype=bool))
        for states in (self.at_j, self.at_g):
            states.resolve(empty_i, cols, self._last, final=True)
        chg = [_cat(self._chg, k, d) for k, d in enumerate((np.int64, np.int64, np.int64, bool))]
        tr = [_cat(self._tr, k, np.int64) for k in range(4)]
        gap = None
        if self._gaps:
            gap = max(max(g.max_gap, g.hi - g.last) for g in self._gaps)
        aj, ag = self.at_j, self.at_g
        book = DayBook(
            day=self.plan.day, plan=self.plan, join_ns=self.join_ns, j_bid=aj.bid,
            j_ask=aj.ask, j_bsz=aj.bsz, j_asz=aj.asz, j_valid=aj.valid,
            j_has=aj.has, chg_ts=chg[0], chg_bid=chg[1], chg_ask=chg[2],
            chg_valid=chg[3].astype(bool), tr_ts=tr[0], tr_px=tr[1], tr_sz=tr[2], tr_side=tr[3],
            counts=dict(self.counts), main_max_gap_ns=gap,
            main_records=sum(g.n for g in self._gaps), instrument_ids=list(self._ids),
            first_ts_event=self.first_ts_event, last_ts_event=self.last_ts_event,
            g_bid=ag.bid, g_ask=ag.ask, g_has=ag.has)
        book.invalid_ns = invalid_durations(book)
        return book


def _cat(parts: list[tuple[np.ndarray, ...]], k: int, dtype: Any) -> np.ndarray:
    return np.concatenate([p[k] for p in parts]) if parts else np.zeros(0, dtype=dtype)


def invalid_durations(book: DayBook) -> dict[str, int]:
    """Time (ns) inside each session label with a crossed, locked or empty book."""
    out = {label: 0 for label in pc.SESSIONS}
    ts, valid = book.chg_ts, book.chg_valid
    for piece in book.plan.pieces:
        if len(ts) == 0:
            out[piece.label] += piece.hi - piece.lo
            continue
        ends = np.r_[ts[1:], np.iinfo(np.int64).max]
        lo = np.clip(ts, piece.lo, piece.hi)
        hi = np.clip(ends, piece.lo, piece.hi)
        out[piece.label] += int(((hi - lo) * (~valid)).sum())
        if ts[0] > piece.lo:  # before the first state: no book
            out[piece.label] += int(min(ts[0], piece.hi) - piece.lo)
    return out


# ------------------------------------------------------------------ file streaming ----
@dataclass
class FileStats:
    """Whole-file counts gathered while streaming (verify.py reports them)."""

    records: int = 0
    rtype: dict[str, int] = field(default_factory=dict)
    action: dict[str, int] = field(default_factory=dict)
    flags: dict[str, int] = field(default_factory=dict)
    first_ts_event: int | None = None
    last_ts_event: int | None = None
    max_ts_recv: int | None = None
    records_at_or_after_cutoff_open: int = 0  # ts_event >= 2024-02-29T23:00Z (RS-01)
    records_in_cutoff_maintenance_hour: int = 0  # ts_event in [22:00Z, 23:00Z): info
    records_outside_day_range: int = 0
    late_records_dropped: int = 0
    days_seen: list[str] = field(default_factory=list)

    def add_chunk(self, chunk: np.ndarray) -> None:
        self.records += len(chunk)
        for key, col in (("rtype", "rtype"), ("action", "action")):
            table = getattr(self, key)
            for code, n in zip(*np.unique(chunk[col], return_counts=True), strict=True):
                name = code.decode() if isinstance(code, bytes) else str(int(code))
                table[name] = table.get(name, 0) + int(n)
        flags = chunk["flags"].astype(np.int64)
        for name, bit in FLAG_BITS.items():
            self.flags[name] = self.flags.get(name, 0) + int(np.count_nonzero(flags & bit))
        te = chunk["ts_event"].astype(np.int64)
        recv = chunk["ts_recv"].astype(np.int64)
        lo, hi = int(te.min()), int(te.max())
        self.first_ts_event = lo if self.first_ts_event is None else min(lo, self.first_ts_event)
        self.last_ts_event = hi if self.last_ts_event is None else max(hi, self.last_ts_event)
        mr = int(recv.max())
        self.max_ts_recv = mr if self.max_ts_recv is None else max(mr, self.max_ts_recv)
        self.records_at_or_after_cutoff_open += int(np.count_nonzero(te >= pc.CUTOFF_OPEN_NS))
        cut = pc.ns_of(pc.CUTOFF_UTC)
        self.records_in_cutoff_maintenance_hour += int(np.count_nonzero(
            (te >= cut) & (te < pc.CUTOFF_OPEN_NS)))


def open_store(path: Path) -> Any:
    import databento  # lazy: tests of the pure logic never need it

    return databento.DBNStore.from_file(Path(path))


def iter_days(store: Any, plan_for_day: Callable[[date], pc.DayPlan],
              want: Callable[[date], bool], tick_1e9: int, *,
              chunk_records: int = DEFAULT_CHUNK_RECORDS, stats: FileStats | None = None,
              chunks: Any = None) -> Iterator[DayBook]:
    """Yield the DayBook of every wanted trade date, in time order. Records are grouped by
    ts_recv into [D-1 16:00 CT, D 16:00 CT). A day is finished when a later day's record
    arrives; a record of an already finished day is counted (late_records_dropped)."""
    meta = store.metadata
    first = datetime.fromtimestamp(int(meta.start) / pc.NS, pc.CT).date() - timedelta(days=2)
    last = datetime.fromtimestamp(int(meta.end) / pc.NS, pc.CT).date() + timedelta(days=2)
    days, bounds = pc.day_boundaries(first, last)
    open_acc: dict[int, DayAccumulator] = {}
    finished = -1
    source = store.to_ndarray(count=chunk_records) if chunks is None else chunks
    for chunk in source:
        if len(chunk) == 0:
            continue
        if stats is not None:
            stats.add_chunk(chunk)
        idx = np.searchsorted(bounds, chunk["ts_recv"].astype(np.int64), side="right") - 1
        outside = (idx < 0) | (idx >= len(days) - 1)
        if stats is not None:
            stats.records_outside_day_range += int(np.count_nonzero(outside))
        for d in np.unique(idx[~outside]).tolist():
            mask = idx == d
            if d <= finished:
                if stats is not None:
                    stats.late_records_dropped += int(np.count_nonzero(mask))
                continue
            day = days[d]
            if stats is not None and day.isoformat() not in stats.days_seen:
                stats.days_seen.append(day.isoformat())
            if not want(day):
                continue
            acc = open_acc.get(d)
            if acc is None:
                acc = open_acc[d] = DayAccumulator(plan_for_day(day), tick_1e9)
            acc.feed(chunk[mask])
        top = int(idx[~outside].max()) if (~outside).any() else finished
        for d in sorted(k for k in open_acc if k < top):
            yield open_acc.pop(d).finish()
        finished = max(finished, top - 1)
    for d in sorted(open_acc):
        yield open_acc.pop(d).finish()
