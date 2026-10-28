"""MathReviewer's own replay of one trade date (no import of feat33, lab33, build_*, implB).

Reads raw records only through data33 (guard33). The ZM front is replayed order by order through
mbo_book31.Book (the protocol names it); order times for seasoned depth are kept beside it.
Everything else (as-of lookups, windows, OFI, labels) is computed step by step in hand_*.py.
"""
from __future__ import annotations

import os
import sys

os.nice(10)
PIPE = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/pipeline"
if PIPE not in sys.path:
    sys.path.insert(0, PIPE)
import numpy as np  # noqa: E402

import cal33  # noqa: E402  (calendar helpers of the DataCoder; fronts, ct_ns, releases)
import data33  # noqa: E402
import mbo_book31 as mb  # noqa: E402

NS_MIN = 60_000_000_000
NS_SEC = 1_000_000_000
UNDEF = mb.UNDEF_PRICE


def ct(day, hhmmss: str) -> int:
    return cal33.ct_ns(day, hhmmss)


def replay_zm(day, instants=(), n_levels: int = 5) -> dict:
    """Replay the ZM front of trade date `day`. Returns per-F_LAST-record arrays (ts, bid1, ask1,
    qb[1..n], qa[1..n], two_sided, valid), the trade records (ts, size, side code), and at each
    requested instant the displayed and seasoned depth of the first 3 levels per side."""
    zm = data33.load_zm(day)
    iid = cal33.fronts(day)["ZM"]
    sel = zm[zm["instrument_id"] == iid]
    ts = sel["ts_recv"].astype(np.int64)
    act = sel["action"]
    side = sel["side"]
    px = sel["price"].astype(np.int64)
    sz = sel["size"].astype(np.int64)
    oid = sel["order_id"].astype(np.int64)
    fl = sel["flags"]
    book = mb.Book()
    otime: dict[int, int] = {}
    inst = sorted(int(x) for x in instants)
    inst_i = 0
    snaps: dict[int, dict] = {}
    n = len(sel)
    u_ts, u_b, u_a, u_two, u_val = [], [], [], [], []
    u_qb = [[] for _ in range(n_levels)]
    u_qa = [[] for _ in range(n_levels)]
    u_pb = [[] for _ in range(n_levels)]
    u_pa = [[] for _ in range(n_levels)]
    t_ts, t_sz, t_side = [], [], []
    batch_mixed = 0
    batch_ts0 = None
    last_flast_ts = -1
    for k in range(n):
        t = int(ts[k])
        # the state as of an instant is the one after the last F_LAST record with ts_recv <=
        # instant (0.3), so snapshots are taken at F_LAST records (below), never from the live
        # book while a later event is half applied; here only advance past instants
        while inst_i < len(inst) and t > inst[inst_i]:
            if inst[inst_i] not in snaps:
                snaps[inst[inst_i]] = {"instant": inst[inst_i], "missing": True,
                                       "last_flast_ts": last_flast_ts}
            inst_i += 1
        a = int(act[k])
        if a == mb.ACT_CLEAR:
            book.clear(bool(fl[k] & mb.F_SNAPSHOT))
            otime = {}
        elif not book.started:
            pass  # records before the first R never enter the book (E.31 rule)
        elif a == mb.ACT_ADD:
            book.add(int(oid[k]), mb.book_side(int(side[k])), int(px[k]), int(sz[k]))
            otime[int(oid[k])] = t
        elif a == mb.ACT_CANCEL:
            book.cancel(int(oid[k]), int(sz[k]))
        elif a == mb.ACT_MODIFY:
            book.modify(int(oid[k]), mb.book_side(int(side[k])), int(px[k]), int(sz[k]))
            otime[int(oid[k])] = t
        elif a == mb.ACT_FILL:
            book.on_fill(int(oid[k]), int(sz[k]))
        elif a == mb.ACT_TRADE:
            t_ts.append(t)
            t_sz.append(int(sz[k]))
            t_side.append(int(side[k]))
        if fl[k] & mb.F_MAYBE_BAD_BOOK:
            book.mark_bad()
        if batch_ts0 is None:
            batch_ts0 = t
        elif t != batch_ts0:
            batch_mixed += 1
        if fl[k] & mb.F_LAST:
            if book.in_snapshot:
                book.end_snapshot()
            batch_ts0 = None
            last_flast_ts = t
            if inst_i < len(inst) and t > inst[inst_i] - 30 * NS_SEC:
                snaps[inst[inst_i]] = _snapshot(book, otime, inst[inst_i], t)
            u_ts.append(t)
            bb, aa = book.best(mb.BID), book.best(mb.ASK)
            two = book.started and bb is not None and aa is not None
            u_two.append(two and not book.bad)
            u_val.append(book.is_valid())
            u_b.append(bb if bb is not None else UNDEF)
            u_a.append(aa if aa is not None else UNDEF)
            bp = book.prices[mb.BID][::-1][:n_levels]
            ap = book.prices[mb.ASK][:n_levels]
            for m in range(n_levels):
                if m < len(bp):
                    u_pb[m].append(bp[m]); u_qb[m].append(book.level_total(mb.BID, bp[m]))
                else:
                    u_pb[m].append(UNDEF); u_qb[m].append(0)
                if m < len(ap):
                    u_pa[m].append(ap[m]); u_qa[m].append(book.level_total(mb.ASK, ap[m]))
                else:
                    u_pa[m].append(UNDEF); u_qa[m].append(0)
    while inst_i < len(inst):
        if inst[inst_i] not in snaps:
            snaps[inst[inst_i]] = {"instant": inst[inst_i], "missing": True,
                                   "last_flast_ts": last_flast_ts}
        inst_i += 1
    out = {
        "day": str(day), "iid": int(iid), "n_records": int(n), "batch_mixed_ts": int(batch_mixed),
        "anomalies": dict(book.anomalies),
        "u_ts": np.array(u_ts, dtype=np.int64), "u_bid": np.array(u_b, dtype=np.int64),
        "u_ask": np.array(u_a, dtype=np.int64), "u_two": np.array(u_two, dtype=bool),
        "u_valid": np.array(u_val, dtype=bool),
        "u_qb": np.array(u_qb, dtype=np.int64), "u_qa": np.array(u_qa, dtype=np.int64),
        "u_pb": np.array(u_pb, dtype=np.int64), "u_pa": np.array(u_pa, dtype=np.int64),
        "t_ts": np.array(t_ts, dtype=np.int64), "t_sz": np.array(t_sz, dtype=np.int64),
        "t_side": np.array(t_side, dtype=np.int64), "snaps": snaps,
    }
    return out


def _snapshot(book: mb.Book, otime: dict, instant: int, last_flast_ts: int) -> dict:
    """Displayed and seasoned depth (orders whose last A/M ts_recv <= instant - 1.000 s) of the
    first 3 levels per side, in the book state after all records with ts_recv <= instant."""
    cut = instant - NS_SEC
    out = {"instant": instant, "last_flast_ts": last_flast_ts, "valid": book.is_valid(),
           "started": book.started, "bad": book.bad}
    for name, s in (("bid", mb.BID), ("ask", mb.ASK)):
        prices = book.prices[s][::-1] if s == mb.BID else book.prices[s]
        lv = []
        for p in prices[:3]:
            q = book.queue(s, p)
            disp = sum(size for _, size, _ in q)
            seas = sum(size for o, size, _ in q if otime.get(o, -1) <= cut)
            lv.append({"price": int(p), "displayed": int(disp), "seasoned": int(seas),
                       "n_orders": len(q),
                       "n_seasoned": sum(1 for o, _, _ in q if otime.get(o, -1) <= cut)})
        out[name] = lv
    return out


def asof_index(u_ts: np.ndarray, u: int) -> int:
    """Index of the last update with ts_recv <= u, or -1."""
    return int(np.searchsorted(u_ts, u, side="right")) - 1


def mid_asof(rep: dict, u: int):
    """M_ZM as of u (float, natural units 1e-9) or None when undefined (0.3)."""
    k = asof_index(rep["u_ts"], u)
    if k < 0 or not rep["u_valid"][k]:
        return None
    return (int(rep["u_bid"][k]) + int(rep["u_ask"][k])) / 2


def touch_asof(rep: dict, u: int):
    """(bid_1, ask_1, two_sided_not_bad, index) as of u."""
    k = asof_index(rep["u_ts"], u)
    if k < 0:
        return None, None, False, k
    return int(rep["u_bid"][k]), int(rep["u_ask"][k]), bool(rep["u_two"][k]), k


def load_mbp1(root: str, day) -> dict:
    """ZS or ZL MBP-1 front records of the day: all records and the F_LAST subset."""
    arr = data33.load_mbp1(root, day)
    iid = cal33.fronts(day)[root]
    sel = arr[arr["instrument_id"] == iid]
    fl = sel["flags"]
    last = (fl & mb.F_LAST) != 0
    bad = (fl & mb.F_MAYBE_BAD_BOOK) != 0
    bid = sel["bid_px_00"].astype(np.int64)
    ask = sel["ask_px_00"].astype(np.int64)
    two = (bid != UNDEF) & (ask != UNDEF)
    valid = two & (bid < ask) & ~bad
    return {"ts": sel["ts_recv"].astype(np.int64), "bid": bid, "ask": ask,
            "qb": sel["bid_sz_00"].astype(np.int64), "qa": sel["ask_sz_00"].astype(np.int64),
            "last": last, "bad": bad, "two": two, "valid": valid, "iid": int(iid),
            "action": sel["action"], "size": sel["size"].astype(np.int64), "n": len(sel)}


def mbp1_mid_asof(m: dict, u: int, flast_only: bool = True):
    ts = m["ts"][m["last"]] if flast_only else m["ts"]
    k = int(np.searchsorted(ts, u, side="right")) - 1
    if k < 0:
        return None
    idx = np.flatnonzero(m["last"])[k] if flast_only else k
    if not m["valid"][idx]:
        return None
    return (int(m["bid"][idx]) + int(m["ask"][idx])) / 2


def open_axis_mark(day, t: int, j: int) -> int:
    """The minute mark t - j minutes on the open-time axis (0.3): the 07:45-08:30 pause is
    skipped; the junction point is 07:45:00 (the coders' FA-1 (B) / B-OPEN-1 (a)); windows do not
    reach the 13:20-19:00 close for the decision times used here."""
    pause_start, pause_end = ct(day, "07:45:00"), ct(day, "08:30:00")
    u = t - j * NS_MIN
    if t > pause_end and u <= pause_end:
        # minutes 08:31..08:30+k map to themselves; the mark that would be 08:30 is 07:45
        u = u - (pause_end - pause_start)
    return u
