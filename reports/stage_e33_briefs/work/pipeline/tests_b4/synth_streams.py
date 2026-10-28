"""Record-level synthetic streams for E.33 B4 (protocol P4.2 first bullet): a ZM MBO stream (MBO_COMPACT) and ZS / ZL
MBP-1 streams (data33.MBP1_SPLIT) for 30 trade dates, with the data facts' tick sizes, spreads, volatility and event
rates (reports/stage_e32_data_facts.md 3.1: ZM.v.0 about 490k records and 400k events a trade date, ZS about 270k
and ZL about 170k MBP-1 events; P0.4: ZM sigma_1m 3.15 ticks; spreads mostly one tick), plus optional episodes that
exercise the edge rules (empty side, bad book, crossed book, ts_recv < ts_event, equal ts_recv, a second ZM
instrument, side-N adds). Synthetic data only: INTERFACE rule 1 does not bind it.

The generator keeps a latent "fair" bid in ticks; the displayed book has `depth` levels a side, 1-3 orders a level.
Each event is one of: a touch move (cancel the far-side touch level, add a new order at the vacated price), a trade
(T record with the aggressor side, F records for the resting orders hit, then C or M records), an add, a cancel, a
size-reducing modify, or a price modify. Every event ends with an F_LAST record. Prices are Databento fixed point
(1e-9 units of the quote unit)."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for p in (str(PIPE),):
    if p not in sys.path:
        sys.path.insert(0, p)

import guard33  # noqa: E402,F401  (puts the E.31 pilot folder on sys.path)
import mbo_book31 as mb  # noqa: E402
import measure31 as m31  # noqa: E402

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
MS = 1_000_000
MBO = m31.MBO_COMPACT
TICK_FP = {"ZM": 100_000_000, "ZS": 250_000_000, "ZL": 10_000_000}  # 0.10 USD/t, 0.25 c/bu, 0.01 c/lb
A_, C_, M_, R_, T_, F_, N_ = (ord(x) for x in "ACMRTFN")
SB, SA, SN = ord("B"), ord("A"), ord("N")
F_LAST, F_SNAP, F_BAD = mb.F_LAST, mb.F_SNAPSHOT, mb.F_MAYBE_BAD_BOOK


def ct_ns(day: date, hh: int, mm: int, ss: float = 0.0) -> int:
    whole = int(ss)
    stamp = datetime(day.year, day.month, day.day, hh, mm, whole, tzinfo=CT)
    return int(stamp.timestamp()) * NS + int(round((ss - whole) * NS))


def synth_dates(n: int = 30, start: date = date(2023, 2, 27)) -> list[date]:
    """n weekdays from ``start`` (crosses the 2023-03-12 DST change). Synthetic dates: calendar only."""
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


@dataclass
class Episodes:
    """Edge cases placed on a date (times are CT wall-clock (hh, mm, ss))."""

    empty_ask: tuple[tuple[int, int, float], float] | None = None  # (start, seconds) the ask side is empty
    bad_book: tuple[tuple[int, int, float], tuple[int, int, float]] | None = None  # F_MAYBE_BAD_BOOK, then R
    bad_on_clear: bool = False  # the R that ends bad_book also carries F_MAYBE_BAD_BOOK
    crossed: tuple[tuple[int, int, float], float] | None = None  # bid placed at the ask for some seconds
    neg_latency_share: float = 0.0014  # share of records with ts_recv < ts_event (data facts 1.4: 0.14-0.16%)
    equal_recv_share: float = 0.02  # share of events stamped with the previous event's ts_recv
    second_instrument: bool = True  # interleave ZM.v.1 records (another instrument id)
    side_n_adds: int = 2  # A records with side N (skipped by the book drivers)


@dataclass
class ZMParams:
    iid: int = 900_001
    iid_back: int = 900_002
    fair0: int = 4000  # ticks (400.0 USD/short ton)
    depth: int = 5
    rate_day: float = 14.0  # events per second 08:30-13:20 CT
    rate_night: float = 3.0  # events per second 19:00-07:45 CT
    sigma_1m: float = 3.15  # ticks (P0.4)
    p_trade: float = 0.05
    p_add: float = 0.40
    p_cancel: float = 0.30
    p_modify: float = 0.15
    p_price_modify: float = 0.03


@dataclass
class _Book:
    """The generator's own order book (side -> price -> list of [oid, size])."""

    levels: dict[int, dict[int, list[list[int]]]] = field(default_factory=lambda: {SB: {}, SA: {}})
    owner: dict[int, tuple[int, int]] = field(default_factory=dict)  # oid -> (side, price)
    next_oid: int = 1
    blocked: int = -1  # a side kept empty during an empty-side episode
    cross_oid: int | None = None

    def best(self, side: int) -> int | None:
        lv = self.levels[side]
        if not lv:
            return None
        return max(lv) if side == SB else min(lv)

    def new(self, side: int, px: int, size: int) -> int:
        oid = self.next_oid
        self.next_oid += 1
        self.levels[side].setdefault(px, []).append([oid, size])
        self.owner[oid] = (side, px)
        return oid

    def remove(self, oid: int) -> tuple[int, int, int]:
        side, px = self.owner.pop(oid)
        q = self.levels[side][px]
        for k, (o, s) in enumerate(q):
            if o == oid:
                q.pop(k)
                if not q:
                    del self.levels[side][px]
                return side, px, s
        raise KeyError(oid)

    def resize(self, oid: int, size: int) -> None:
        side, px = self.owner[oid]
        for o in self.levels[side][px]:
            if o[0] == oid:
                o[1] = size
                return
        raise KeyError(oid)


class _Out:
    """Accumulates records (as tuples) of one stream."""

    def __init__(self) -> None:
        self.rows: list[tuple] = []

    def rec(self, ts: int, iid: int, oid: int, px_fp: int, size: int, flags: int, act: int, side: int,
            ts_event: int | None = None) -> None:
        self.rows.append((ts, ts if ts_event is None else ts_event, iid, oid, px_fp, size, flags, act, side, 0))

    def close_event(self) -> None:
        ts, te, iid, oid, px, sz, fl, act, side, sq = self.rows[-1]
        self.rows[-1] = (ts, te, iid, oid, px, sz, fl | F_LAST, act, side, sq)


def _event_times(rng: np.random.Generator, lo: int, hi: int, rate: float) -> np.ndarray:
    n = rng.poisson(rate * (hi - lo) / NS)
    return np.sort(rng.integers(lo, hi, size=n, dtype=np.int64))


def _snapshot(out: _Out, book: _Book, iid: int, ts: int, tick_fp: int, flags_r: int = 0) -> None:
    out.rec(ts, iid, 0, 0, 0, F_SNAP | flags_r, R_, SN)
    oids = sorted(book.owner)
    for k, oid in enumerate(oids):
        side, px = book.owner[oid]
        size = next(s for o, s in book.levels[side][px] if o == oid)
        fl = F_SNAP | (F_LAST if k == len(oids) - 1 else 0)
        out.rec(ts, iid, oid, px * tick_fp, size, fl, A_, side)
    if not oids:
        out.close_event()


def _fill_levels(book: _Book, rng: np.random.Generator, fair: int, spread: int, depth: int) -> None:
    for j in range(depth):
        for side, px in ((SB, fair - j), (SA, fair + spread + j)):
            if px not in book.levels[side]:
                for _ in range(int(rng.integers(1, 4))):
                    book.new(side, px, int(rng.integers(1, 21)))


def _session_times(rng: np.random.Generator, day: date, intervals: list[tuple[int, int]] | None,
                   rate_day: float, rate_night: float, pre_open: float) -> np.ndarray:
    """Event times in the open intervals of D (the calendar's sessions; default the regular schedule) plus
    pre-open events 08:00-08:30 CT."""
    prev = day - timedelta(days=1)
    if intervals is None:
        intervals = [(ct_ns(prev, 19, 0), ct_ns(day, 7, 45)), (ct_ns(day, 8, 30), ct_ns(day, 13, 20))]
    parts = []
    for lo, hi in intervals:
        rate = rate_day if lo >= ct_ns(day, 8, 30) else rate_night
        parts.append(_event_times(rng, lo, hi, rate))
    if pre_open:
        parts.append(_event_times(rng, ct_ns(day, 8, 0), ct_ns(day, 8, 30), pre_open))
    return np.sort(np.concatenate(parts))


def make_zm_day(day: date, seed: int, prm: ZMParams | None = None, ep: Episodes | None = None,
                fair0: int | None = None, intervals: list[tuple[int, int]] | None = None
                ) -> tuple[np.ndarray, int]:
    """One trade date of ZM MBO records (MBO_COMPACT, ts_recv order). Returns (records, closing fair bid)."""
    prm = prm or ZMParams()
    ep = ep or Episodes()
    rng = np.random.default_rng(seed)
    tick = TICK_FP["ZM"]
    out = _Out()
    book = _Book()
    fair = prm.fair0 if fair0 is None else fair0
    _fill_levels(book, rng, fair, 1, prm.depth)
    prev = day - timedelta(days=1)
    t_snap = ct_ns(prev, 16, 0, 30.0)
    _snapshot(out, book, prm.iid, t_snap, tick)
    times = _session_times(rng, day, intervals, prm.rate_day, prm.rate_night, 0.5)
    # touch moves per event so that the 1-minute SD of the mid is about sigma_1m ticks
    p_move_day = min(0.5, prm.sigma_1m ** 2 / (60.0 * prm.rate_day))
    p_move_night = min(0.5, 1.0 / (60.0 * prm.rate_night))
    special = _special_times(day, ep)
    s_iter = iter(sorted(special))
    nxt = next(s_iter, None)
    last_ts = t_snap
    side_n_left = ep.side_n_adds
    for ts in times.tolist():
        while nxt is not None and nxt[0] <= ts:
            item = (max(nxt[0], last_ts + 1), nxt[1])
            fair = _special(out, book, rng, prm, item, fair, tick, ep)
            last_ts = item[0]
            nxt = next(s_iter, None)
        if ts <= last_ts:
            ts = last_ts + 1
        if rng.random() < ep.equal_recv_share:
            ts = last_ts
        last_ts = ts
        day_time = ts >= ct_ns(day, 8, 30)
        pre_open = ct_ns(day, 7, 45) <= ts < ct_ns(day, 8, 30)
        p_move = p_move_day if day_time else p_move_night
        u = rng.random()
        if pre_open:
            _ev_add(out, book, rng, prm, ts, tick)
        elif u < p_move:
            fair = _ev_move(out, book, rng, prm, ts, tick, fair, +1 if rng.random() < 0.5 else -1)
        elif u < p_move + prm.p_trade:
            last_ts = _ev_trade(out, book, rng, prm, ts, tick)
        elif u < p_move + prm.p_trade + prm.p_add:
            if side_n_left and rng.random() < 1e-4:
                out.rec(ts, prm.iid, 10**9 + side_n_left, fair * tick, 1, F_LAST, A_, SN)
                side_n_left -= 1
            else:
                _ev_add(out, book, rng, prm, ts, tick)
        elif u < p_move + prm.p_trade + prm.p_add + prm.p_cancel:
            _ev_cancel(out, book, rng, prm, ts, tick)
        elif u < p_move + prm.p_trade + prm.p_add + prm.p_cancel + prm.p_modify:
            _ev_modify(out, book, rng, prm, ts, tick, price_move=rng.random() < prm.p_price_modify / prm.p_modify)
        else:
            out.rec(ts, prm.iid, 0, 0, 0, F_LAST, N_, SN)  # an N record (no book change)
        if ep.second_instrument and rng.random() < 0.2:
            out.rec(last_ts, prm.iid_back, 7 * 10**8 + len(out.rows), (fair + 30) * tick, 1, F_LAST, A_, SB)
    arr = np.array(out.rows, dtype=MBO)
    if len(arr) > 1 and bool(np.any(np.diff(arr["ts_recv"]) < 0)):
        raise AssertionError("synthetic ZM stream is not in ts_recv order")
    _apply_latency_noise(arr, rng, ep.neg_latency_share)
    return arr, fair


def _special_times(day: date, ep: Episodes) -> list[tuple]:
    sp: list[tuple] = []
    if ep.empty_ask is not None:
        (hh, mm, ss), dur = ep.empty_ask
        t0 = ct_ns(day, hh, mm, ss)
        sp += [(t0, "empty_ask_on"), (t0 + int(dur * NS), "empty_ask_off")]
    if ep.bad_book is not None:
        (a, b) = ep.bad_book
        sp += [(ct_ns(day, *a), "bad_on"), (ct_ns(day, *b), "bad_off")]
    if ep.crossed is not None:
        (hh, mm, ss), dur = ep.crossed
        t0 = ct_ns(day, hh, mm, ss)
        sp += [(t0, "cross_on"), (t0 + int(dur * NS), "cross_off")]
    return sp


def _special(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, item: tuple, fair: int,
             tick: int, ep: Episodes) -> int:
    ts, kind = item
    iid = prm.iid
    if kind == "empty_ask_on":
        oids = [o for o, (s, _p) in book.owner.items() if s == SA]
        for oid in oids:
            _side, px, sz = book.remove(oid)
            out.rec(ts, iid, oid, px * tick, sz, 0, C_, SA)
        out.close_event()
        book.blocked = SA
    elif kind == "empty_ask_off":
        book.blocked = -1
        b = book.best(SB) or fair
        for j in range(prm.depth):
            oid = book.new(SA, b + 1 + j, int(rng.integers(1, 21)))
            out.rec(ts, iid, oid, (b + 1 + j) * tick, book.levels[SA][b + 1 + j][-1][1], 0, A_, SA)
        out.close_event()
    elif kind == "bad_on":
        out.rec(ts, iid, 0, 0, 0, F_BAD | F_LAST, N_, SN)
    elif kind == "bad_off":
        _snapshot(out, book, iid, ts, tick, flags_r=F_BAD if ep.bad_on_clear else 0)
    elif kind == "cross_on":
        a = book.best(SA)
        if a is not None:
            oid = book.new(SB, a, 1)
            out.rec(ts, iid, oid, a * tick, 1, F_LAST, A_, SB)
            book.cross_oid = oid
    elif kind == "cross_off":
        oid = book.cross_oid
        if oid is not None and oid in book.owner:
            _s, px, sz = book.remove(oid)
            out.rec(ts, iid, oid, px * tick, sz, F_LAST, C_, SB)
    return fair


def _ev_add(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, ts: int, tick: int) -> None:
    side = SB if rng.random() < 0.5 else SA
    if side == book.blocked:
        side = SB if side == SA else SA
    b, a = book.best(SB), book.best(SA)
    if b is not None and a is not None and a - b > 1 and rng.random() < 0.7:
        px = b + 1 if side == SB else a - 1  # improve inside a wide spread
    else:
        ref = (b if side == SB else a)
        if ref is None:
            ref = (a - 1) if side == SB and a is not None else ((b + 1) if b is not None else prm.fair0)
        j = int(rng.integers(0, prm.depth))
        px = ref - j if side == SB else ref + j
    oid = book.new(side, px, int(rng.integers(1, 21)))
    out.rec(ts, prm.iid, oid, px * tick, book.levels[side][px][-1][1], F_LAST, A_, side)


def _ev_cancel(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, ts: int, tick: int) -> None:
    if len(book.owner) < 4 * prm.depth:
        _ev_add(out, book, rng, prm, ts, tick)
        return
    oid = int(rng.choice(list(book.owner)))
    side, px = book.owner[oid]
    if len(book.levels[side]) <= 2 and len(book.levels[side][px]) == 1:
        _ev_add(out, book, rng, prm, ts, tick)
        return
    _s, px, sz = book.remove(oid)
    out.rec(ts, prm.iid, oid, px * tick, sz, F_LAST, C_, side)


def _ev_modify(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, ts: int, tick: int,
               price_move: bool) -> None:
    if not book.owner:
        _ev_add(out, book, rng, prm, ts, tick)
        return
    oid = int(rng.choice(list(book.owner)))
    side, px = book.owner[oid]
    size = next(s for o, s in book.levels[side][px] if o == oid)
    if price_move:
        if len(book.levels[side][px]) == 1 and len(book.levels[side]) <= 2:
            return _ev_add(out, book, rng, prm, ts, tick)
        _s, _p, sz = book.remove(oid)
        npx = px - 1 if side == SB else px + 1  # step away from the touch
        book.levels[side].setdefault(npx, []).append([oid, sz])
        book.owner[oid] = (side, npx)
        out.rec(ts, prm.iid, oid, npx * tick, sz, F_LAST, M_, side)
    else:
        if size <= 1:
            return _ev_add(out, book, rng, prm, ts, tick)
        nsz = int(rng.integers(1, size))
        book.resize(oid, nsz)
        out.rec(ts, prm.iid, oid, px * tick, nsz, F_LAST, M_, side)


def _ev_move(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, ts: int, tick: int, fair: int,
             step: int) -> int:
    """Touch move by one tick: remove the far side's touch level, add an order at the vacated price."""
    far, near = (SA, SB) if step > 0 else (SB, SA)
    px = book.best(far)
    if px is None or len(book.levels[far]) <= 2 or book.blocked in (far, near):
        _ev_add(out, book, rng, prm, ts, tick)
        return fair
    for oid, _sz in list(book.levels[far][px]):
        _s, _p, sz = book.remove(oid)
        out.rec(ts, prm.iid, oid, px * tick, sz, 0, C_, far)
    oid = book.new(near, px, int(rng.integers(1, 21)))
    out.rec(ts, prm.iid, oid, px * tick, book.levels[near][px][-1][1], 0, A_, near)
    # keep the far side `depth` deep
    edge = (max if far == SA else min)(book.levels[far])
    npx = edge + 1 if far == SA else edge - 1
    oid = book.new(far, npx, int(rng.integers(1, 21)))
    out.rec(ts, prm.iid, oid, npx * tick, book.levels[far][npx][-1][1], F_LAST, A_, far)
    return fair + step


def _ev_trade(out: _Out, book: _Book, rng: np.random.Generator, prm: ZMParams, ts: int, tick: int) -> int:
    """Aggressor buy (side B) lifts the ask touch or aggressor sell (side A) hits the bid touch: T, F..., C/M...;
    sometimes the touch empties, followed within 100 ms by a refill add (a separate event)."""
    agg = SB if rng.random() < 0.5 else SA
    rest = SA if agg == SB else SB
    px = book.best(rest)
    if px is None or len(book.levels[rest]) <= 2 or rest == book.blocked:
        _ev_add(out, book, rng, prm, ts, tick)
        return ts
    lvl = book.levels[rest][px]
    total = sum(s for _o, s in lvl)
    q = int(rng.integers(1, total + 1)) if rng.random() < 0.3 else int(rng.integers(1, max(2, total // 2 + 1)))
    out.rec(ts, prm.iid, 0, px * tick, q, 0, T_, agg)
    left = q
    hits = []
    for oid, sz in list(lvl):
        if left <= 0:
            break
        take = min(sz, left)
        hits.append((oid, sz, take))
        left -= take
    for oid, _sz, take in hits:
        out.rec(ts, prm.iid, oid, px * tick, take, 0, F_, rest)
    for oid, sz, take in hits:
        if take == sz:
            book.remove(oid)
            out.rec(ts, prm.iid, oid, px * tick, sz, 0, C_, rest)
        else:
            book.resize(oid, sz - take)
            out.rec(ts, prm.iid, oid, px * tick, sz - take, 0, M_, rest)
    out.close_event()
    if px not in book.levels[rest] and rng.random() < 0.5:  # refill within 100 ms
        t2 = ts + int(rng.integers(1, 100)) * MS
        oid = book.new(rest, px, int(rng.integers(1, 21)))
        out.rec(t2, prm.iid, oid, px * tick, book.levels[rest][px][-1][1], F_LAST, A_, rest)
        return t2
    return ts


def _event_ids(arr: np.ndarray) -> np.ndarray:
    """Event index of each record: the records up to and including an F_LAST record form one event."""
    last = (arr["flags"] & F_LAST) != 0
    return np.concatenate([[0], np.cumsum(last)[:-1]]).astype(np.int64)


def _apply_latency_noise(arr: np.ndarray, rng: np.random.Generator, share: float) -> None:
    """ts_event = ts_recv - latency (latency 0.1-2 ms), ONE value per event (Databento stamps every record of an
    event with the matching engine's time; data facts: 0 batches mix ts_events); a share of events gets
    ts_event > ts_recv (ts_recv < ts_event, F 1.4), kept in ts_recv order."""
    ev = _event_ids(arr)
    n_ev = int(ev.max()) + 1 if len(ev) else 0
    lat = rng.integers(100_000, 2_000_000, size=n_ev, dtype=np.int64)
    neg = rng.random(n_ev) < share
    lat[neg] = -rng.integers(1, 5_000_000, size=int(neg.sum()), dtype=np.int64)
    first_ts = np.zeros(n_ev, dtype=np.int64)
    first_ts[ev[::-1]] = arr["ts_recv"][::-1]  # the ts_recv of each event's first record
    te = first_ts[ev] - lat[ev]
    snap = (arr["flags"] & F_SNAP) != 0
    te[snap] = arr["ts_recv"][snap] - 3_600 * NS  # snapshot records carry an older ts_event
    arr["ts_event"] = te


# ---------------------------------------------------------------- MBP-1 (ZS, ZL) --
def make_mbp1_day(day: date, root: str, seed: int, iid: int, fair0: int, rate_day: float, rate_night: float,
                  sigma_1m: float, dtype: np.dtype, intervals: list[tuple[int, int]] | None = None
                  ) -> tuple[np.ndarray, int]:
    """One trade date of MBP-1 records for ZS or ZL (top of book after each event, trades as T records).
    Fields follow data33.MBP1_SPLIT: action, side, price, size for trades; bid/ask px and sz after the event."""
    rng = np.random.default_rng(seed)
    tick = TICK_FP[root]
    prev = day - timedelta(days=1)
    times = _session_times(rng, day, intervals, rate_day, rate_night, 0.0)
    rows = np.zeros(len(times) + 1, dtype=dtype)
    bid, spread = fair0, 1
    qb, qa = int(rng.integers(5, 60)), int(rng.integers(5, 60))
    p_move_day = min(0.5, sigma_1m ** 2 / (60.0 * rate_day))
    p_move_night = min(0.5, 1.0 / (60.0 * rate_night))
    t_snap = ct_ns(prev, 16, 0, 30.0)
    _mbp_row(rows, 0, t_snap, iid, R_, SN, 0, 0, F_SNAP | F_LAST, bid, bid + spread, qb, qa, tick)
    last = t_snap
    k = 1
    for ts in times.tolist():
        ts = max(ts, last)
        last = ts
        day_time = ts >= ct_ns(day, 8, 30)
        u = rng.random()
        pm = p_move_day if day_time else p_move_night
        act, side, px, sz = A_, SB, 0, 0
        if u < pm:
            step = 1 if rng.random() < 0.5 else -1
            bid += step
            qb, qa = int(rng.integers(1, 60)), int(rng.integers(1, 60))
            act, side = (A_, SB) if step > 0 else (A_, SA)
        elif u < pm + 0.10:
            agg = SB if rng.random() < 0.5 else SA
            sz = int(rng.integers(1, 10))
            px = (bid + spread) if agg == SB else bid
            act, side = T_, agg
            if agg == SB:
                qa = max(0, qa - sz)
                if qa == 0:
                    qa = int(rng.integers(1, 30))
            else:
                qb = max(0, qb - sz)
                if qb == 0:
                    qb = int(rng.integers(1, 30))
        else:
            side = SB if rng.random() < 0.5 else SA
            act = A_ if rng.random() < 0.55 else C_
            d = int(rng.integers(1, 6)) * (1 if act == A_ else -1)
            if side == SB:
                qb = max(1, qb + d)
            else:
                qa = max(1, qa + d)
        if day_time and rng.random() < 0.02:
            spread = 2
        elif spread == 2 and rng.random() < 0.3:
            spread = 1
        _mbp_row(rows, k, ts, iid, act, side, px, sz, F_LAST, bid, bid + spread, qb, qa, tick)
        k += 1
    arr = rows[:k]
    _apply_mbp_latency(arr, rng)
    return arr, bid


def _mbp_row(rows: np.ndarray, k: int, ts: int, iid: int, act: int, side: int, px_t: int, sz: int, fl: int,
             bid: int, ask: int, qb: int, qa: int, tick: int) -> None:
    r = rows[k]
    r["ts_recv"] = ts
    r["ts_event"] = ts
    r["instrument_id"] = iid
    r["action"] = act
    r["side"] = side
    r["price"] = px_t * tick if act == T_ else (bid * tick if side == SB else ask * tick)
    r["size"] = sz if act == T_ else (qb if side == SB else qa)
    r["flags"] = fl
    r["bid_px_00"] = bid * tick
    r["ask_px_00"] = ask * tick
    r["bid_sz_00"] = qb
    r["ask_sz_00"] = qa
    if "rtype" in rows.dtype.names:
        r["rtype"] = 1
    if "bid_ct_00" in rows.dtype.names:
        r["bid_ct_00"] = 1
        r["ask_ct_00"] = 1


def _apply_mbp_latency(arr: np.ndarray, rng: np.random.Generator) -> None:
    """MBP-1: every record is its own event (F_LAST on each), one latency per record."""
    n = len(arr)
    lat = rng.integers(100_000, 2_000_000, size=n, dtype=np.int64)
    te = arr["ts_recv"] - lat
    neg = rng.random(n) < 0.0015
    te[neg] = arr["ts_recv"][neg] + rng.integers(1, 5_000_000, size=int(neg.sum()), dtype=np.int64)
    arr["ts_event"] = te


# ---------------------------------------------------------------- 30-date set --
DEFAULT_EPISODES: dict[int, Episodes] = {
    3: Episodes(empty_ask=((10, 0, 0.4), 12.0)),
    7: Episodes(bad_book=((9, 40, 0.2), (9, 47, 30.0))),
    11: Episodes(bad_book=((12, 2, 0.0), (12, 4, 0.0)), bad_on_clear=True),
    15: Episodes(crossed=((9, 15, 0.6), 1.5)),
    19: Episodes(empty_ask=((13, 11, 0.5), 600.0)),  # empty past 13:20: the exit-mark rule
    23: Episodes(crossed=((11, 30, 0.3), 2.0)),
}


def zm_days(n: int = 30, seed: int = 4242, scale: float = 1.0) -> list[tuple[date, np.ndarray, int]]:
    """n synthetic dates of ZM MBO (records, front iid). The front rolls from iid 900001 to 900003 at date 15."""
    out = []
    fair = 4000
    for k, d in enumerate(synth_dates(n)):
        prm = ZMParams(rate_day=14.0 * scale, rate_night=3.0 * scale)
        if k >= 15:
            prm.iid, prm.iid_back = 900_003, 900_004
        ep = DEFAULT_EPISODES.get(k, Episodes())
        arr, fair = make_zm_day(d, seed + k, prm, ep, fair0=fair)
        out.append((d, arr, prm.iid))
    return out
