"""Synthetic MBO / MBP-1 records for the E.31 engine tests (no real data file is ever opened).

``mbo(rows)``: rows of (t_ns, action, side, price_usd, size, order_id[, flags]) -> the column dict
measure31_core reads (ts_recv = ts_event = t). ``random_day``: a self-consistent random ZM-like
day for the throughput probe.
"""

from __future__ import annotations

import sys
from datetime import date, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mbo_book31 as mb  # noqa: E402
import measure31_core as core  # noqa: E402
from measure31 import MBO_COMPACT, MBP_COMPACT  # noqa: E402

DAY = date(2024, 1, 10)  # a Wednesday in CST
IID, IID2 = 101, 102
TICK = 0.10


def ct(hh: int, mm: int, ss: float = 0.0, day: date = DAY) -> int:
    whole = int(ss)
    return core.ct_ns(day, time(hh, mm, whole)) + round((ss - whole) * 1e9)


def p(usd: float) -> int:
    return round(usd * 1e9)


def mbo(rows: list[tuple], iid: int = IID) -> dict[str, np.ndarray]:
    arr = np.zeros(len(rows), dtype=MBO_COMPACT)
    for k, row in enumerate(rows):
        t, act, side, price, size, oid = row[:6]
        flags = row[6] if len(row) > 6 else mb.F_LAST
        arr[k] = (t, t, row[7] if len(row) > 7 else iid, oid, p(price), size, flags, ord(act),
                  ord(side), k)
    return {name: arr[name].copy() for name in MBO_COMPACT.names}


def concat(*parts: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {k: np.concatenate([q[k] for q in parts]) for k in parts[0]}


def mbp(rows: list[tuple[int, float, float]], iid: int = 7) -> dict[str, np.ndarray]:
    arr = np.zeros(len(rows), dtype=MBP_COMPACT)
    for k, (t, bid, ask) in enumerate(rows):
        arr[k] = (t, t, iid, mb.F_LAST, p(bid), p(ask), k)
    return {name: arr[name].copy() for name in MBP_COMPACT.names}


def snapshot(t: int, bids: list[tuple[float, int, int]], asks: list[tuple[float, int, int]],
             iid: int = IID) -> list[tuple]:
    """R then A records (F_SNAPSHOT), the last one with F_LAST: (price, size, oid) per order."""
    snap = mb.F_SNAPSHOT | mb.F_BAD_TS_RECV
    rows = [(t, "R", "N", 0.0, 0, 0, snap, iid)]
    for price, size, oid in bids:
        rows.append((t, "A", "B", price, size, oid, snap, iid))
    for price, size, oid in asks:
        rows.append((t, "A", "A", price, size, oid, snap, iid))
    last = rows[-1]
    rows[-1] = (*last[:6], snap | mb.F_LAST, iid)
    return rows


def job(day: date = DAY, **kw: object) -> core.DayJob:
    syms = kw.pop("symbols", (core.SymbolJob("ZM.v.0", IID, "ZMH4"),))
    return core.DayJob(day=day, symbols=syms, zs_tick_1e9=p(0.0025), zl_tick_1e9=p(0.0001),
                       **kw)


def random_day(n_records: int, seed: int = 1, iid: int = IID, day: date = DAY
               ) -> dict[str, np.ndarray]:
    """A random but book-consistent ZM-like stream over the trade date's sessions: adds near the
    touch, cancels, size decreases and increases, price modifies, and trades (T, F per resting
    order, then the C/M records that reduce the filled orders), one 00:00 UTC snapshot first."""
    rng = np.random.default_rng(seed)
    sessions = core.regular_sessions(day)
    lo, hi = sessions[0].lo, sessions[1].hi
    times = np.sort(rng.integers(lo, hi, size=n_records)).tolist()
    mid = 3500  # in ticks (350.0 USD/short ton)
    book = mb.Book()
    rows: list[tuple] = snapshot(lo - 3_600 * core.NS, [(349.9, 5, 1)], [(350.1, 5, 2)], iid)
    book.clear(True)
    book.add(1, mb.BID, p(349.9), 5)
    book.add(2, mb.ASK, p(350.1), 5)
    book.end_snapshot()
    next_id = 3
    k = 0
    while k < len(times):
        t = times[k]
        k += 1
        bb, ba = book.best(mb.BID), book.best(mb.ASK)
        if bb is None or ba is None or rng.random() < 0.55:
            side = mb.BID if (ba is not None and (bb is None or rng.random() < 0.5)) else mb.ASK
            if side == mb.BID:
                top = (ba // 100_000_000 - 1) if ba is not None else mid - 1
                price = (top - int(rng.integers(0, 4))) * 100_000_000
            else:
                top = (bb // 100_000_000 + 1) if bb is not None else mid + 1
                price = (top + int(rng.integers(0, 4))) * 100_000_000
            size = int(rng.integers(1, 30))
            rows.append((t, "A", "B" if side == mb.BID else "A", price / 1e9, size, next_id,
                         mb.F_LAST, iid))
            book.add(next_id, side, price, size)
            next_id += 1
            continue
        u = rng.random()
        oids = list(book.orders)
        if u < 0.75 and oids:
            oid = oids[int(rng.integers(0, len(oids)))]
            o = book.orders[oid]
            sc = "B" if o[0] == mb.BID else "A"
            v = rng.random()
            if v < 0.6:
                rows.append((t, "C", sc, o[1] / 1e9, o[2], oid, mb.F_LAST, iid))
                book.cancel(oid, o[2])
            elif v < 0.8 and o[2] > 1:
                rows.append((t, "M", sc, o[1] / 1e9, o[2] - 1, oid, mb.F_LAST, iid))
                book.modify(oid, o[0], o[1], o[2] - 1)
            else:
                rows.append((t, "M", sc, o[1] / 1e9, o[2] + 2, oid, mb.F_LAST, iid))
                book.modify(oid, o[0], o[1], o[2] + 2)
            continue
        # a trade: an aggressor takes part of the best level on one side
        side = mb.BID if rng.random() < 0.5 else mb.ASK
        price = book.best(side)
        queue = book.queue(side, price)
        qty = int(rng.integers(1, max(2, sum(s for _, s, _ in queue))))
        aggr = "A" if side == mb.BID else "B"
        rest = "B" if side == mb.BID else "A"
        rows.append((t, "T", aggr, price / 1e9, qty, next_id, 0, iid))
        left, fills = qty, []
        for oid, size, _ in queue:
            if left == 0:
                break
            take = min(size, left)
            fills.append((oid, size, take))
            left -= take
        for oid, _, take in fills:
            rows.append((t, "F", rest, price / 1e9, take, oid, 0, iid))
        for n, (oid, size, take) in enumerate(fills):
            last = mb.F_LAST if n == len(fills) - 1 else 0
            if take == size:
                rows.append((t, "C", rest, price / 1e9, take, oid, last, iid))
                book.cancel(oid, take)
            else:
                rows.append((t, "M", rest, price / 1e9, size - take, oid, last, iid))
                book.modify(oid, side, price, size - take)
        next_id += 1
    return mbo(rows, iid)
