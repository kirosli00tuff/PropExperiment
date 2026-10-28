"""E.33 implementation B: the ZM front's book updates from MBO records (protocol 0.3).

The book is mbo_book31.Book (0.3 names it); the driver around it is written here, independently
of E.31's InstrumentRun and of pipeline A. A "book update" is the book state after a record that
carries F_LAST, at that record's ts_recv. Records are applied in the order data33 returns them
(ts_recv order; data33 asserts it). Driver rules (READING LB-12, LB-13 in the readings file):
- R clears the book (snapshot or reset) and starts it; records before the first R are not
  applied and the book counts as not started (invalid);
- F_MAYBE_BAD_BOOK on any record marks the book bad until the next R; on an R record itself the
  mark is applied after the clear (the book after that record is bad);
- A/C/M change the book (A or M with side N are skipped and counted); T, F, N do not;
- F_TOB / F_MBP on MBO records do not mark the book bad (the protocol names only
  F_MAYBE_BAD_BOOK); they are counted.
Prices are converted to integer ticks (asserting the price is a tick multiple).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PILOT = HERE.parents[2] / "stage_e31_briefs" / "work" / "pilot"
if str(PILOT) not in sys.path:
    sys.path.insert(0, str(PILOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mbo_book31 as mb  # noqa: E402
from labB import MIN_NS, Updates, asof, ct_ns, derive  # noqa: E402

SIGMA_MARKS = 279  # minute marks 08:35..13:13 (P0.3 sigma_X intervals inside 08:35-13:13)
SIGMA_LOOKBACK = 20  # trade dates before D (P0.3)


def _empty_updates() -> Updates:
    z = np.zeros(0, dtype=np.int64)
    f = np.zeros(0, dtype=bool)
    return Updates(z, z.copy(), z.copy(), f, f.copy(), f.copy())


def front_updates(rec: np.ndarray, iid: int, tick: int) -> tuple[Updates, dict[str, int]]:
    """Replay the front's MBO records through mbo_book31.Book; one output row per F_LAST
    record. Returns the Updates (prices in ticks) and data-quality counts."""
    sel = rec[rec["instrument_id"] == np.uint32(iid)]
    counts = {"records": int(len(sel)), "before_start": 0, "clear_records": 0,
              "bad_flag_records": 0, "bad_flag_on_clear": 0, "tob_or_mbp_records": 0,
              "side_n_book_records": 0, "f_last_records": 0}
    if not len(sel):
        return _empty_updates(), counts
    ts_l = sel["ts_recv"].astype(np.int64).tolist()
    act_l = sel["action"].tolist()
    side_l = sel["side"].tolist()
    px_l = sel["price"].astype(np.int64).tolist()
    sz_l = sel["size"].astype(np.int64).tolist()
    oid_l = sel["order_id"].astype(np.uint64).tolist()
    fl_l = sel["flags"].tolist()

    R, A, C, M = mb.ACT_CLEAR, mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY
    S_B, S_A = mb.SIDE_BID_CODE, mb.SIDE_ASK_CODE
    LAST, SNAP, BAD, TOBMBP = mb.F_LAST, mb.F_SNAPSHOT, mb.F_MAYBE_BAD_BOOK, mb.F_TOB | mb.F_MBP
    book = mb.Book()
    out_t: list[int] = []
    out_b: list[int] = []
    out_a: list[int] = []
    out_hb: list[bool] = []
    out_ha: list[bool] = []
    out_bad: list[bool] = []
    for ts, act, side, px, sz, oid, fl in zip(ts_l, act_l, side_l, px_l, sz_l, oid_l, fl_l,
                                               strict=True):
        if fl & TOBMBP:
            counts["tob_or_mbp_records"] += 1
        if act == R:
            counts["clear_records"] += 1
            book.clear(bool(fl & SNAP))
            if fl & BAD:
                counts["bad_flag_records"] += 1
                counts["bad_flag_on_clear"] += 1
                book.mark_bad()
        elif not book.started:
            counts["before_start"] += 1
        else:
            if fl & BAD:
                counts["bad_flag_records"] += 1
                book.mark_bad()
            if book.in_snapshot and not fl & SNAP:
                book.end_snapshot()
            if act in (A, M):
                if side != S_B and side != S_A:
                    counts["side_n_book_records"] += 1
                else:
                    bs = mb.BID if side == S_B else mb.ASK
                    if act == A:
                        book.add(oid, bs, px, sz)
                    else:
                        book.modify(oid, bs, px, sz)
            elif act == C:
                book.cancel(oid, sz)
            if fl & SNAP and fl & LAST:
                book.end_snapshot()
        if fl & LAST:
            bb = book.best(mb.BID)
            ba = book.best(mb.ASK)
            out_t.append(ts)
            out_b.append(0 if bb is None else bb)
            out_a.append(0 if ba is None else ba)
            out_hb.append(bb is not None)
            out_ha.append(ba is not None)
            out_bad.append((not book.started) or book.bad)
    counts["f_last_records"] = len(out_t)
    bid_raw = np.asarray(out_b, dtype=np.int64)
    ask_raw = np.asarray(out_a, dtype=np.int64)
    hb = np.asarray(out_hb, dtype=bool)
    ha = np.asarray(out_ha, dtype=bool)
    if bool(np.any(bid_raw[hb] % tick)) or bool(np.any(ask_raw[ha] % tick)):
        raise AssertionError("a touch price is not a multiple of the tick")
    upd = Updates(t=np.asarray(out_t, dtype=np.int64), bid=bid_raw // tick,
                  ask=ask_raw // tick, has_bid=hb, has_ask=ha,
                  bad=np.asarray(out_bad, dtype=bool))
    for key, val in book.anomalies.items():
        counts[f"book_{key}"] = int(val)
    return upd, counts


def minute_mids(upd: Updates, day: date) -> tuple[np.ndarray, np.ndarray]:
    """2 x M_ZM (ticks, int64) and its validity as of the minute marks 08:35..13:13 of day."""
    from datetime import time
    marks = ct_ns(day, time(8, 35)) + np.arange(SIGMA_MARKS, dtype=np.int64) * MIN_NS
    if not len(upd.t):
        return np.zeros(SIGMA_MARKS, dtype=np.int64), np.zeros(SIGMA_MARKS, dtype=bool)
    d = derive(upd)
    k = asof(upd, marks)
    have = k >= 0
    kk = np.where(have, k, 0)
    valid = have & d.mid_ok[kk]
    return np.where(valid, d.s2[kk], 0), valid


def sigma_from_mids(history: list[tuple[np.ndarray, np.ndarray]]) -> float | None:
    """P0.3 sigma_X(D): population SD (ddof 0) of the 1-minute mid changes (ticks) over all
    intervals inside 08:35-13:13 of the given dates with valid mids at both ends, pooled."""
    parts = []
    for s2, valid in history:
        ok = valid[1:] & valid[:-1]
        parts.append(((s2[1:] - s2[:-1]).astype(np.float64) / 2.0)[ok])
    x = np.concatenate(parts) if parts else np.zeros(0)
    if not len(x):
        return None
    return float(np.std(x, ddof=0))
