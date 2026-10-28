"""Implementation B: one pass over a front's records into arrays (P0.3 book updates, trades and
the record-level events of F3), then everything else is vectorised in dayB.py.

ZM (MBO): mbo_book31.Book (P0.3: "ZM from MBO (mbo_book31.Book, full displayed depth)") with the
book-changing record handling of E.31 (valid start at the first R, F_MAYBE_BAD_BOOK marks the book
bad until the next R, snapshot end, A/C/M/R; T, F and N do not change the book). On top of it,
written here (not in E.31): per-order last add/modify ts_recv (seasoned depth, F3.7-F3.8), fill
classification of reductions (F3.9 "fills are not removals"), touch removals (F3.9), sweeps
(F3.10) and refills (F3.11).

ZS/ZL (MBP-1): the record's own BBO fields after each F_LAST record (vectorised).
Clock: ts_recv only (P0.3, LT4). Input arrays are in ts_recv order (data33).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import calB  # noqa: E402,F401  (sys.path for the E.31 library)
import mbo_book31 as mb  # noqa: E402

NS = 1_000_000_000
LEVELS = 5  # F3.4 uses levels 1..5
SEASON_NS = NS  # F3 preamble: at least 1.000 s before t
SEASON_LEVELS = 3  # F3.7 uses level 1, F3.8 levels 1..3
REFILL_NS = 100_000_000  # F3.11: within 100 ms (ts_recv)
INT64_MIN = int(np.iinfo(np.int64).min)
NOPX = mb.UNDEF_PRICE  # price placeholder for a missing level


@dataclass
class BookArrays:
    """Book updates (P0.3: the state after each F_LAST record, time = its ts_recv)."""

    ts: np.ndarray  # int64
    valid: np.ndarray  # bool: started, not bad, both sides, bid_1 < ask_1
    notbad: np.ndarray  # bool: started and not marked bad (OFI terms, FD3)
    bpx: np.ndarray  # int64 [n, L], level m = column m-1; NOPX where the level is missing
    apx: np.ndarray
    bq: np.ndarray  # int64 [n, L], 0 where missing
    aq: np.ndarray


@dataclass
class ZMArrays:
    book: BookArrays
    trade_ts: np.ndarray  # T records: ts_recv, size, side code, price, ts_event
    trade_sz: np.ndarray
    trade_side: np.ndarray
    rem_ts: np.ndarray  # F3.9 touch removals: ts_recv, side (0 bid, 1 ask), contracts
    rem_side: np.ndarray
    rem_qty: np.ndarray
    sweep_ts: np.ndarray  # F3.10: ts_recv of the F_LAST record that shows the depletion
    sweep_dir: np.ndarray  # +1 buy sweep (best ask emptied), -1 sell sweep (best bid emptied)
    refill_ts: np.ndarray  # F3.11: ts_recv of the add, side (0 bid, 1 ask)
    refill_side: np.ndarray
    season_q: np.ndarray  # [n_query, 2, SEASON_LEVELS] seasoned qty (bid, ask) at query times
    season_ok: np.ndarray  # [n_query] book valid at the capture update
    counts: dict


def _empty_book(n: int) -> BookArrays:
    return BookArrays(np.zeros(n, np.int64), np.zeros(n, bool), np.zeros(n, bool),
                      np.full((n, LEVELS), NOPX, np.int64), np.full((n, LEVELS), NOPX, np.int64),
                      np.zeros((n, LEVELS), np.int64), np.zeros((n, LEVELS), np.int64))


def _seasoned(book: mb.Book, last_am: dict, q: int) -> tuple[list, bool]:
    """F3 preamble: displayed quantity per level (levels of the displayed book, READING
    B-SEAS-1) counting only orders whose last add or modify ts_recv <= q - 1.000 s."""
    lim = q - SEASON_NS
    out = [[0] * SEASON_LEVELS, [0] * SEASON_LEVELS]
    for side in (mb.BID, mb.ASK):
        prices = book.prices[side]
        seq = prices[::-1] if side == mb.BID else prices
        for m, price in enumerate(seq[:SEASON_LEVELS]):
            lvl = book.levels[side][price]
            tot = 0
            for oid in lvl[mb.L_ORDERS]:
                if last_am.get(oid, lim + 1) <= lim:
                    tot += book.orders[oid][mb.O_SIZE]
            out[side][m] = tot
    return out, book.is_valid()


def replay_zm(rec: np.ndarray, query_ns: np.ndarray | None = None) -> ZMArrays:
    """One pass over the front's MBO records (already filtered to one instrument_id)."""
    n = len(rec)
    flags = rec["flags"]
    is_last = (flags & mb.F_LAST) != 0
    last_idx = np.flatnonzero(is_last)
    out = _empty_book(len(last_idx))
    out.ts[:] = rec["ts_recv"][last_idx]
    q = np.zeros(0, np.int64) if query_ns is None else np.asarray(query_ns, np.int64)
    # seasoned-depth capture: the last F_LAST record with ts_recv <= q ("as of", P0.3)
    cap_pos = np.searchsorted(out.ts, q, side="right") - 1
    cap_rec = np.where(cap_pos >= 0, last_idx[np.clip(cap_pos, 0, None)], -1)
    season_q = np.zeros((len(q), 2, SEASON_LEVELS), np.int64)
    season_ok = np.zeros(len(q), bool)
    cap_order = np.argsort(cap_rec, kind="stable")
    cap_ptr = 0
    while cap_ptr < len(q) and cap_rec[cap_order[cap_ptr]] < 0:
        cap_ptr += 1

    A, C, M, R, T, F = (mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY, mb.ACT_CLEAR, mb.ACT_TRADE,
                        mb.ACT_FILL)
    S_A, S_B = mb.SIDE_ASK_CODE, mb.SIDE_BID_CODE
    BAD, SNAP, LAST, TOBMBP = mb.F_MAYBE_BAD_BOOK, mb.F_SNAPSHOT, mb.F_LAST, mb.F_TOB | mb.F_MBP
    BID, ASK = mb.BID, mb.ASK
    book = mb.Book()
    orders, levels, prices = book.orders, None, None
    last_am: dict[int, int] = {}
    pending: dict[int, int] = {}  # F3.9: filled lots per order since the last F_LAST
    dep: dict[tuple[int, int], int] = {}  # F3.11: (side, price) -> ts of a trade depletion
    rem_ts, rem_side, rem_qty = [], [], []
    sw_ts, sw_dir, rf_ts, rf_side = [], [], [], []
    run_te, run_t, pre_b, pre_a, done_b, done_a = None, False, None, None, False, False
    cnt = {"records": n, "before_start": 0, "side_n_book": 0, "bad_flag_records": 0,
           "clears": 0}
    k_upd = 0
    ts_l = rec["ts_recv"].tolist()
    te_l = rec["ts_event"].tolist()
    act_l = rec["action"].tolist()
    side_l = rec["side"].tolist()
    px_l = rec["price"].tolist()
    sz_l = rec["size"].tolist()
    oid_l = rec["order_id"].tolist()
    fl_l = flags.tolist()
    bpx, apx, bqa, aqa, valid = out.bpx, out.apx, out.bq, out.aq, out.valid
    notbad = out.notbad

    def reduce(oid: int, red: int, order: list, ts: int) -> None:
        """F3.9/F3.11 bookkeeping for a reduction of ``red`` lots of a resting order, called
        before the book applies it."""
        side, price = order[0], order[1]
        best = book.best(side)
        fill = min(red, pending.get(oid, 0))
        if fill:
            pending[oid] -= fill
        rem = red - fill
        if rem > 0 and price == best:
            rem_ts.append(ts)
            rem_side.append(side)
            rem_qty.append(rem)
        # READING R-B3-FD6 (lead, 2026-10-28): only a record whose WHOLE reduction is fill lots
        # of its event batch (rem == 0) and that leaves the touch level at 0 opens a refill
        # window; a fill plus a voluntary remainder in one record does not (the remainder is
        # still a removal above)
        if fill > 0 and rem == 0 and price == best and book.level_total(side, price) - red <= 0:
            dep[(side, price)] = ts  # the touch reached 0 through trades

    for i in range(n):
        ts, act, fl = ts_l[i], act_l[i], fl_l[i]
        te = te_l[i]
        # F3.10 runs of records sharing one ts_event (READING B-SW-1)
        if te != run_te:
            run_te, run_t, done_b, done_a = te, False, False, False
        if book.started or act == R:
            if fl & (BAD | TOBMBP):
                cnt["bad_flag_records"] += 1
                if not book.bad:
                    book.mark_bad()
            if book.in_snapshot and not fl & SNAP:
                book.end_snapshot()
            side, px, sz, oid = side_l[i], px_l[i], sz_l[i], oid_l[i]
            if act == T:
                if not run_t:
                    run_t, pre_b, pre_a = True, book.best(BID), book.best(ASK)
            elif act == F:
                pending[oid] = pending.get(oid, 0) + sz
            elif act == R:
                book.clear(bool(fl & SNAP))
                if fl & (BAD | TOBMBP):  # READING R-B3-N10 (= R-B3-D1): clear, then mark bad
                    book.mark_bad()
                cnt["clears"] += 1
                pending.clear()
                dep.clear()
            elif act == C:
                order = orders.get(oid)
                if order is not None:
                    reduce(oid, min(sz, order[2]), order, ts)
                book.cancel(oid, sz)
            elif act == A or act == M:
                if side != S_B and side != S_A:
                    cnt["side_n_book"] += 1
                else:
                    bs = BID if side == S_B else ASK
                    if act == A:
                        key = (bs, px)
                        t0 = dep.get(key)
                        if t0 is not None and ts - t0 <= REFILL_NS:
                            rf_ts.append(ts)
                            rf_side.append(bs)
                        book.add(oid, bs, px, sz)
                    else:
                        order = orders.get(oid)
                        if order is not None:
                            if order[0] != bs or px != order[1] or sz <= 0:
                                reduce(oid, order[2], order, ts)  # leaves its level
                            elif sz < order[2]:
                                reduce(oid, order[2] - sz, order, ts)
                        book.modify(oid, bs, px, sz)
                    last_am[oid] = ts
            if fl & SNAP and fl & LAST:
                book.end_snapshot()
        else:
            cnt["before_start"] += 1
        orders = book.orders  # Book.clear rebinds the dict
        if fl & LAST:
            # P0.3 book update k_upd
            started = book.started
            bp, ap = book.prices
            nb, na = len(bp), len(ap)
            if started and nb:
                lv = book.levels[BID]
                for m in range(min(LEVELS, nb)):
                    p = bp[nb - 1 - m]
                    bpx[k_upd, m] = p
                    bqa[k_upd, m] = lv[p][0]
            if started and na:
                lv = book.levels[ASK]
                for m in range(min(LEVELS, na)):
                    p = ap[m]
                    apx[k_upd, m] = p
                    aqa[k_upd, m] = lv[p][0]
            valid[k_upd] = book.is_valid()
            notbad[k_upd] = started and not book.bad
            if run_t and started:  # F3.10 sweep checks at event ends (causal, LT1)
                if not done_a and pre_a is not None and book.level_total(ASK, pre_a) == 0:
                    sw_ts.append(ts)
                    sw_dir.append(1)
                    done_a = True
                if not done_b and pre_b is not None and book.level_total(BID, pre_b) == 0:
                    sw_ts.append(ts)
                    sw_dir.append(-1)
                    done_b = True
            pending.clear()
            while cap_ptr < len(q) and cap_rec[cap_order[cap_ptr]] == i:
                j = cap_order[cap_ptr]
                if started:
                    vals, ok = _seasoned(book, last_am, int(q[j]))
                    season_q[j] = vals
                    season_ok[j] = ok
                cap_ptr += 1
            k_upd += 1
    tr = rec["action"] == mb.ACT_TRADE
    return ZMArrays(
        out, rec["ts_recv"][tr].astype(np.int64), rec["size"][tr].astype(np.int64),
        rec["side"][tr].astype(np.uint8),
        np.array(rem_ts, np.int64), np.array(rem_side, np.int8), np.array(rem_qty, np.int64),
        np.array(sw_ts, np.int64), np.array(sw_dir, np.int8),
        np.array(rf_ts, np.int64), np.array(rf_side, np.int8),
        season_q, season_ok, cnt)


@dataclass
class MBPArrays:
    book: BookArrays  # level 1 only is filled (column 0)
    trade_ts: np.ndarray
    trade_sz: np.ndarray
    counts: dict


def mbp_arrays(rec: np.ndarray) -> MBPArrays:
    """ZS or ZL MBP-1 (one instrument): the BBO after each F_LAST record. Bad: a record of the
    event carries F_MAYBE_BAD_BOOK (READING B-MBP-BAD)."""
    n = len(rec)
    fl = rec["flags"]
    last = (fl & mb.F_LAST) != 0
    idx = np.flatnonzero(last)
    ev = np.concatenate([[0], np.cumsum(last)[:-1]]) if n else np.zeros(0, np.int64)
    bad_rec = ((fl & mb.F_MAYBE_BAD_BOOK) != 0).astype(np.int64)
    bad_ev = np.bincount(ev, weights=bad_rec, minlength=len(idx))[:len(idx)] > 0
    b = rec["bid_px_00"][idx].astype(np.int64)
    a = rec["ask_px_00"][idx].astype(np.int64)
    bq = rec["bid_sz_00"][idx].astype(np.int64)
    aq = rec["ask_sz_00"][idx].astype(np.int64)
    has_b = (b != mb.UNDEF_PRICE) & (b != INT64_MIN)
    has_a = (a != mb.UNDEF_PRICE) & (a != INT64_MIN)
    out = _empty_book(len(idx))
    out.ts[:] = rec["ts_recv"][idx]
    out.bpx[:, 0] = np.where(has_b, b, NOPX)
    out.apx[:, 0] = np.where(has_a, a, NOPX)
    out.bq[:, 0] = np.where(has_b, bq, 0)
    out.aq[:, 0] = np.where(has_a, aq, 0)
    out.valid[:] = has_b & has_a & (b < a) & ~bad_ev
    out.notbad[:] = ~bad_ev
    tr = rec["action"] == mb.ACT_TRADE
    return MBPArrays(out, rec["ts_recv"][tr].astype(np.int64), rec["size"][tr].astype(np.int64),
                     {"records": n, "updates": int(len(idx)), "bad_updates": int(bad_ev.sum())})
