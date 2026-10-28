"""E.33 P4 features, Coder-A (event-loop implementation; brief_FeatureCoder.md).

Frozen protocol: reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...), cited P<n>.
Readings (ambiguities resolved conservatively) are marked ``# READING FA-<n>`` and logged in
reports/stage_e33_briefs/work/FeatureCoder_readings.md.

Two passes per trade date D.

Pass 1 (``stream_day``): D's records are streamed once in ts_recv order (ZM MBO of the ZM front,
ZS and ZL MBP-1 of their fronts; P0.3) and, at every minute mark of D's open-time axis, the loop
samples (a) the book state as of the mark: the last book update (an F_LAST record) with
ts_recv <= mark (P0.3 "as of u"), and (b) cumulative counters of every quantity a window statistic
sums, over records with ts_recv <= mark that lie in open time. A window of k minutes ending at the
mark of index p is then exactly ``cum[p] - cum[p - k]`` (P0.3: the pause and the close are skipped
because records there are never accumulated). Everything is keyed on ts_recv (G1, LT4); ts_event
is used only to group trade records "sharing one ts_event" (F3.10, F3.11), never as a clock (G6).

Pass 2 (``features_day``): the 59 features at the 273 decision minutes i = 0..272 of D (t = 08:35
+ i min) from D's pass-1 tables and the pass-1 tables of the 21 trade dates before D (sigma_X(D),
trailing 20-date references, F1.3, F1.7, F4.7).

Units: Databento prices are int64 in 1e-9 units of the quote (ZM USD/short ton, ZS cents/bu,
ZL cents/lb). Mids are kept as the exact integer raw2 = bid_1 + ask_1 (twice the mid).
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

_PILOT = Path(__file__).resolve().parents[3] / "stage_e31_briefs" / "work" / "pilot"
if str(_PILOT) not in sys.path:
    sys.path.insert(0, str(_PILOT))

import mbo_book31 as mb  # noqa: E402  (E.31 library, P1.2 (d); imported, not copied)

# ------------------------------------------------------------------ constants ----
NS = 1_000_000_000
MIN_NS = 60 * NS
SEASON_NS = NS  # F3 seasoned depth: last add or modify at least 1.000 s before t
REFILL_NS = 100_000_000  # F3.11: an add within 100 ms (ts_recv) after the depletion
CT = ZoneInfo("America/Chicago")
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
I64_MAX = int(np.iinfo(np.int64).max)  # mbo_book31.UNDEF_PRICE
I64_MIN = int(np.iinfo(np.int64).min)

# Open-time axis of trade date D (P0.3). READING FA-1: open intervals are start-exclusive and
# end-inclusive, (lo, hi]; the regular grains schedule gives (19:00 D-1, 07:45 D] and
# (08:30 D, 13:20 D]. The open-time point where the pause is skipped is represented by 07:45:00,
# the last open instant before the pause, so no sample point carries a book state formed inside
# the skipped pause (the state as of 08:30:00 is the pre-open book; it had no valid ZM mid on all
# 3 dates measured). Minute marks of an interval (lo, hi] are lo + 1 min .. hi. A window of k
# minutes ending at mark p sums records in (mark p-k, mark p] in open time.
# Lead ruling FD1/FD2 (2026-10-28, READING FA-30): the intervals are D's actual session
# (data.group_session.session_intervals: early halts cut the day session, scheduled late opens
# remove the overnight); a decision or reference minute in closed time maps to the last mark
# before it (after a 12:05 halt: the 12:05 mark); when D has no overnight session the axis starts
# with the previous trade date's day session.
# Regular-schedule layout (tests): 765 overnight marks 19:01 .. 07:45, 290 day marks 08:31 .. 13:20.
N_ON = 765
N_DAY = 290
N_MARKS = N_ON + N_DAY
P_J = N_ON - 1  # regular axis: mark 07:45:00
P_0835 = N_ON + 4  # regular axis: mark 08:35 (769)
P_1313 = P_0835 + 278  # 1047
P_1315 = P_0835 + 280  # 1049
N_GRID = 273  # i = 0..272, t = 08:35 .. 13:07 (INTERFACE 3; G_h(D) is a prefix of it)
N_REF = 279  # wall minutes 08:35..13:13 (trailing references, sigma)
N_WALL = 281  # wall minutes 08:35..13:15 on D (j = 0..280), sampled as of the wall instant
J_1315 = 280
GRID_P = np.arange(P_0835, P_0835 + N_GRID)  # regular axis only (tests)
REF_P = np.arange(P_0835, P_1313 + 1)  # regular axis only (tests)
MAX_LOOKBACK = 120  # the longest window (F1.2): marks needed before t
N_LVL = 5  # F3.4 levels
N_SEAS = 3  # F3.8 levels
I_1130 = 175  # 08:35 + 175 min = 11:30 (C.9)
I_1215 = 220  # 08:35 + 220 min = 12:15 (F4.13)
TOD_DEN = 278.0  # C.1: (13:13 - 08:35) in minutes
N_HIST = 21  # trade dates before D needed by pass 2 (20, plus the date before the oldest)

ZM_TICK_USD = 0.10  # P0.3 / F1.3 / F2.7: one ZM tick, USD per short ton
CRUSH_ZM = 2.2  # F1: 2.2 = 44/2000 x 100
CRUSH_ZL = 11.0  # F1: 11 lb of oil per bushel

# ZM counters (pass 1), cumulative over open-time records with ts_recv <= mark
ZC = ("vol", "buy", "sell", "ntr", "ofi", "ofi_bad", "iofi", "iofi_bad",
      "swb", "sws", "rfb", "rfa", "cra", "crb")
ZI = {name: k for k, name in enumerate(ZC)}
MC = ("vol", "ofi", "ofi_bad")  # ZS, ZL counters
MI = {name: k for k, name in enumerate(MC)}

FEATURES = (
    [f"C_{k}" for k in range(1, 16)] + [f"F1_{k}" for k in range(1, 9)]
    + [f"F2_{k}" for k in range(1, 12)] + [f"F3_{k}" for k in range(1, 13)]
    + [f"F4_{k}" for k in range(1, 14)])
FI = {name: k for k, name in enumerate(FEATURES)}
N_FEAT = len(FEATURES)  # 59
# P4 G4 (ProtocolReview DO-11): clipped to [-5, 5] after their own normalisation (38)
CLIPPED = tuple(
    ["C_5"] + [f"F1_{k}" for k in (1, 2, 3, 4, 6, 7, 8)] + [f"F2_{k}" for k in range(1, 12)]
    + [f"F3_{k}" for k in (1, 2, 3, 4, 10, 11, 12)] + [f"F4_{k}" for k in (1, 2, 3, 4, 5)]
    + [f"F4_{k}" for k in range(7, 14)])
UNCLIPPED = tuple(f for f in FEATURES if f not in CLIPPED)  # 21
CLIP = 5.0
FAMILIES = {"F1": [f for f in FEATURES if f.startswith("F1_")],
            "F2": [f for f in FEATURES if f.startswith("F2_")],
            "F3": [f for f in FEATURES if f.startswith("F3_")],
            "F4": [f for f in FEATURES if f.startswith("F4_")]}
FLAG_OF = {"F1": "C_11", "F2": "C_12", "F3": "C_13", "F4": "C_14"}  # C.11-C.14 (G3)


# ------------------------------------------------------------------ the open-time axis ----
def wall_ns(day: date, hh: int, mm: int, ss: int = 0) -> int:
    """CT wall time on calendar date ``day`` as UTC ns (zoneinfo, fold 0)."""
    dt = datetime(day.year, day.month, day.day, hh, mm, ss, tzinfo=CT)
    return (dt - EPOCH) // timedelta(microseconds=1) * 1000


@dataclass(frozen=True)
class Axis:
    """D's open-time axis (P0.3) and its sampling instants.

    marks: the axis minute marks (UTC ns); n_prev of them lie on the previous trade date (FD2).
    wall: the 281 wall minutes 08:35..13:15 on D; map_pos[j]: index of the last mark <= wall[j].
    inst: every sampling instant (marks and wall minutes), sorted; mark_at / wall_at index it."""

    day: date
    intervals: tuple[tuple[int, int], ...]  # open intervals (lo, hi], increasing
    marks: np.ndarray
    n_prev: int
    wall: np.ndarray
    map_pos: np.ndarray
    inst: np.ndarray
    mark_at: np.ndarray
    wall_at: np.ndarray
    day_lo: int  # 08:30:00 on D (F4.6)

    def iv_of(self, ts: np.ndarray) -> np.ndarray:
        """Index of the open interval (lo, hi] holding each ts, or -1 (closed time)."""
        out = np.full(len(ts), -1, dtype=np.int64)
        for k, (lo, hi) in enumerate(self.intervals):
            out[(ts > lo) & (ts <= hi)] = k
        return out

    def is_open(self, ts: np.ndarray) -> np.ndarray:
        return self.iv_of(ts) >= 0


def regular_intervals(day: date) -> list[tuple[int, int]]:
    """The regular grains schedule of trade date D: 19:00 (D-1) .. 07:45, 08:30 .. 13:20."""
    prev = day - timedelta(days=1)  # READING FA-2: "19:00 on D-1" = the calendar day before D
    return [(wall_ns(prev, 19, 0), wall_ns(day, 7, 45)), (wall_ns(day, 8, 30), wall_ns(day, 13, 20))]


def build_axis(day: date, intervals: list[tuple[int, int]],
               prev_interval: tuple[int, int] | None = None) -> Axis:
    """Axis from D's open intervals (as [lo, hi) of data.group_session, read as (lo, hi]) and,
    when D has no overnight session, the previous trade date's day session first (FD2)."""
    ivs = ([prev_interval] if prev_interval is not None else []) + list(intervals)
    marks, n_prev = [], 0
    for k, (lo, hi) in enumerate(ivs):
        if (lo % MIN_NS) or (hi % MIN_NS) or hi <= lo:
            raise ValueError(f"{day}: open interval not on whole minutes")
        m = list(range(lo + MIN_NS, hi + 1, MIN_NS))
        marks.extend(m)
        if prev_interval is not None and k == 0:
            n_prev = len(m)
    marks_a = np.array(marks, dtype=np.int64)
    if np.any(np.diff(marks_a) <= 0):
        raise ValueError(f"{day}: minute marks not increasing")
    wall = np.array([wall_ns(day, (8 * 60 + 35 + j) // 60, (8 * 60 + 35 + j) % 60)
                     for j in range(N_WALL)], dtype=np.int64)
    map_pos = np.searchsorted(marks_a, wall, side="right") - 1
    if map_pos[0] < MAX_LOOKBACK:
        raise ValueError(f"{day}: fewer than {MAX_LOOKBACK} open minutes before 08:35")
    inst = np.union1d(marks_a, wall)
    return Axis(day, tuple(ivs), marks_a, n_prev, wall, map_pos, inst,
                np.searchsorted(inst, marks_a), np.searchsorted(inst, wall), wall_ns(day, 8, 30))


def axis(day: date) -> Axis:
    """The regular-schedule axis of D (tests; the builder passes D's actual session)."""
    return build_axis(day, regular_intervals(day))


def _asof(ts: np.ndarray, idx: np.ndarray, marks: np.ndarray) -> np.ndarray:
    """For each mark, the index (into the record array) of the last record of ``idx`` with
    ts_recv <= mark, or -1 (P0.3 "as of u")."""
    k = np.searchsorted(ts[idx], marks, side="right") - 1
    return np.where(k >= 0, idx[np.maximum(k, 0)], -1)


def _check_order(ts: np.ndarray, where: str) -> None:
    if len(ts) > 1 and np.any(np.diff(ts) < 0):  # LT4: the loaders return ts_recv order
        raise ValueError(f"{where}: records are not in ts_recv order")


# ------------------------------------------------------------------ OFI (F2.8, F3.1, F3.4) ----
def ofi_e(pb0: int, qb0: int, pa0: int, qa0: int, pb1: int, qb1: int, pa1: int, qa1: int) -> int:
    """F2.8 (Cont, Kukanov and Stoikov 2014): e_n = 1{Pb_n >= Pb_n-1} qb_n
    - 1{Pb_n <= Pb_n-1} qb_n-1 - 1{Pa_n <= Pa_n-1} qa_n + 1{Pa_n >= Pa_n-1} qa_n-1."""
    e = 0
    if pb1 >= pb0:
        e += qb1
    if pb1 <= pb0:
        e -= qb0
    if pa1 <= pa0:
        e -= qa1
    if pa1 >= pa0:
        e += qa0
    return e


def _levels(book: mb.Book) -> tuple[list[int], list[int], list[int], list[int]]:
    """Top N_LVL price levels per side of the displayed book: bid prices (best first), bid
    totals, ask prices (best first), ask totals."""
    bp_all, ap_all = book.prices
    lb, la = book.levels
    bp = bp_all[-N_LVL:][::-1]
    ap = ap_all[:N_LVL]
    return bp, [lb[p][0] for p in bp], ap, [la[p][0] for p in ap]


# ------------------------------------------------------------------ pass 1: ZM MBO ----
@dataclass
class _ZMState:
    """Committed ZM book state after the last F_LAST record (P0.3 book update)."""

    two_sided: bool = False  # started, not bad, both sides present (e_n computable)
    valid: bool = False  # + bid_1 < ask_1: the mid is defined (P0.3)
    bp: list = field(default_factory=list)
    bq: list = field(default_factory=list)
    ap: list = field(default_factory=list)
    aq: list = field(default_factory=list)


def _commit(book: mb.Book) -> _ZMState:
    two = book.started and not book.bad and bool(book.prices[0]) and bool(book.prices[1])
    if not two:
        return _ZMState()
    bp, bq, ap, aq = _levels(book)
    return _ZMState(True, bp[0] < ap[0], bp, bq, ap, aq)


def _e_levels(s0: _ZMState, s1: _ZMState) -> tuple[int | None, int | None]:
    """(e_n at level 1, sum over m = 1..5 of the level-m e_n) between two committed states; None
    when not computable (G3: an empty side, or fewer than m levels on a side for F3.4)."""
    if not (s0.two_sided and s1.two_sided):
        return None, None
    e1 = ofi_e(s0.bp[0], s0.bq[0], s0.ap[0], s0.aq[0], s1.bp[0], s1.bq[0], s1.ap[0], s1.aq[0])
    if min(len(s0.bp), len(s0.ap), len(s1.bp), len(s1.ap)) < N_LVL:
        return e1, None  # READING FA-7: a missing level m <= 5 makes the level-m e_n undefined
    tot = 0
    for m in range(N_LVL):
        tot += ofi_e(s0.bp[m], s0.bq[m], s0.ap[m], s0.aq[m], s1.bp[m], s1.bq[m], s1.ap[m],
                     s1.aq[m])
    return e1, tot


def _seasoned(book: mb.Book, last_am: dict, prices: list[int], side: int, cut: int) -> list:
    """F3: displayed quantity per level counting only orders whose last add or modify (ts_recv)
    is <= t - 1.000 s. READING FA-9: levels are those of the full displayed book (m = 1 the touch);
    a missing level counts 0."""
    out = []
    lvls, orders = book.levels[side], book.orders
    for m in range(N_SEAS):
        if m >= len(prices):
            out.append(0)
            continue
        q = 0
        for oid in lvls[prices[m]][1]:
            if last_am[oid] <= cut:
                q += orders[oid][2]
        out.append(q)
    return out


def _trade_set_starts(ev: list, acts: list) -> set:
    """Indices of the first T record of each run of T records sharing one ts_event."""
    starts, cur = set(), None
    for j, a in enumerate(acts):
        if a == mb.ACT_TRADE and ev[j] != cur:
            starts.add(j)
            cur = ev[j]
    return starts


def stream_zm(rec: np.ndarray, iid: int, ax: Axis) -> dict[str, np.ndarray]:
    """Pass 1 for the ZM front: one ts_recv-ordered pass over its MBO records (mbo_book31.Book,
    the book-changing branch of E.31's InstrumentRun._run_chunk; READING FA-27), sampling at the
    axis instants. Arrays are over ax.inst; zm_seas, zm_hi, zm_lo over the 273 decision minutes
    (each at its mapped mark, FD1)."""
    r = rec[rec["instrument_id"] == iid]
    ts_a = r["ts_recv"].astype(np.int64)
    _check_order(ts_a, f"ZM {ax.day}")
    fl_a = r["flags"].astype(np.int64)
    last_idx = np.flatnonzero((fl_a & mb.F_LAST) != 0)
    k_inst = _asof(ts_a, last_idx, ax.inst)  # book state as of each instant
    r_inst = np.searchsorted(ts_a, ax.inst, side="right") - 1  # counters as of each instant
    nxt_last_ts = np.full(len(ts_a), I64_MAX, dtype=np.int64)  # ts of the next F_LAST record
    if len(last_idx) > 1:
        nxt_last_ts[last_idx[:-1]] = ts_a[last_idx[1:]]
    iv = ax.iv_of(ts_a)
    grid = {}  # instant index -> decision minutes i sampled there (zm_seas, zm_hi, zm_lo)
    for i in range(N_GRID):
        grid.setdefault(int(ax.mark_at[ax.map_pos[i]]), []).append(i)
    k0830 = int(_asof(ts_a, last_idx, np.array([ax.day_lo], dtype=np.int64))[0])
    cols = {"ts": ts_a.tolist(), "fl": fl_a.tolist(), "act": r["action"].tolist(),
            "side": r["side"].tolist(), "px": r["price"].tolist(), "sz": r["size"].tolist(),
            "oid": r["order_id"].tolist(), "ev": r["ts_event"].tolist(), "iv": iv.tolist(),
            "nxt": nxt_last_ts.tolist()}
    return _zm_loop(ax, cols, _trade_set_starts(cols["ev"], cols["act"]), k_inst.tolist(),
                    r_inst.tolist(), k0830, grid)


def _zm_out(n: int) -> dict[str, np.ndarray]:
    return {
        "zm_raw2": np.zeros(n, np.int64), "zm_ok": np.zeros(n, bool),
        "zm_spread": np.zeros(n, np.int64), "zm_touch": np.zeros(n, np.int64),
        "zm_lvl": np.zeros((N_LVL, n), np.int64),  # qb_m + qa_m (missing level 0)
        "zm_seas": np.full((2 * N_SEAS, N_GRID), np.nan),  # seasoned qb_1..3, qa_1..3
        "zm_hi": np.full(N_GRID, np.nan), "zm_lo": np.full(N_GRID, np.nan),  # raw2 over [08:30, t]
        "zm_cnt": np.zeros((len(ZC), n), np.int64),
    }


def _zm_loop(ax: Axis, c: dict, set_start: set, k_inst: list, r_inst: list, k0830: int,
             grid: dict) -> dict[str, np.ndarray]:
    A, C, M, R, T, F = (mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY, mb.ACT_CLEAR, mb.ACT_TRADE,
                        mb.ACT_FILL)
    S_A, S_B = mb.SIDE_ASK_CODE, mb.SIDE_BID_CODE
    BAD, SNAP, LAST = mb.F_MAYBE_BAD_BOOK | mb.F_TOB | mb.F_MBP, mb.F_SNAPSHOT, mb.F_LAST
    BID, ASK = mb.BID, mb.ASK
    ts, fl, acts, sides, pxs, szs, oids, ev, ivs, nxt = (
        c["ts"], c["fl"], c["act"], c["side"], c["px"], c["sz"], c["oid"], c["ev"], c["iv"], c["nxt"])
    n_inst = len(k_inst)
    out = _zm_out(n_inst)
    cnt = [0] * len(ZC)
    book = mb.Book()
    orders = book.orders
    last_am: dict[int, int] = {}  # order id -> ts_recv of its last add or modify (F3 seasoned)
    pending: dict[int, int] = {}  # order id -> filled lots of this batch not yet removed (F3.9)
    dep: dict[tuple[int, int], int] = {}  # (side, price) emptied by fills -> refill deadline
    tset: list | None = None  # open trade set [ts_event, pre best bid, pre best ask, buy, sell]
    state = _ZMState()
    last_iv: int | None = None  # open interval of the previous book update (FD3 a)
    # F4.6: running max / min of the valid mids M(u), u in [08:30, t]: seeded with the state as of
    # 08:30:00 (the last update with ts_recv <= 08:30:00), then every later update
    rp_on, hi, lo = k0830 < 0, None, None
    kp, rpp = 0, 0

    def snap_book(q: int) -> None:
        if state.valid:
            raw2 = state.bp[0] + state.ap[0]
            out["zm_raw2"][q], out["zm_ok"][q] = raw2, True
            out["zm_spread"][q] = state.ap[0] - state.bp[0]
            out["zm_touch"][q] = state.bq[0] + state.aq[0]
            for m in range(N_LVL):
                out["zm_lvl"][m, q] = ((state.bq[m] if m < len(state.bq) else 0)
                                       + (state.aq[m] if m < len(state.aq) else 0))
        gi = grid.get(q)
        if gi is None:
            return
        if state.valid:
            cut = int(ax.inst[q]) - SEASON_NS
            seas = (_seasoned(book, last_am, state.bp, BID, cut)
                    + _seasoned(book, last_am, state.ap, ASK, cut))
            for i in gi:
                out["zm_seas"][:, i] = seas
        if hi is not None:
            for i in gi:
                out["zm_hi"][i], out["zm_lo"][i] = hi, lo

    def snap_cnt(q: int) -> None:
        out["zm_cnt"][:, q] = cnt

    while kp < n_inst and k_inst[kp] < 0:
        snap_book(kp)
        kp += 1
    while rpp < n_inst and r_inst[rpp] < 0:
        snap_cnt(rpp)
        rpp += 1

    for j in range(len(ts)):
        t, act, side, px, sz, oid, f = ts[j], acts[j], sides[j], pxs[j], szs[j], oids[j], fl[j]
        o = ivs[j] >= 0
        if tset is not None and ev[j] != tset[0]:
            tset = None  # READING FA-10: a trade set ends at the first record of another ts_event
        if act == T:
            if o:  # C.5/F1.5 volume (READING FA-22: sides A, B, N), F3.5 sides B/A, F3.12
                cnt[0] += sz
                cnt[3] += 1
                if side == S_B:
                    cnt[1] += sz
                elif side == S_A:
                    cnt[2] += sz
            if j in set_start and book.started:  # pre-trade touch (record level, "before")
                tset = [ev[j], book.best(BID), book.best(ASK), False, False]
        if book.started or act == R:  # E.31: no book before the first R (valid start)
            if f & BAD and not book.bad:
                book.mark_bad()
            if book.in_snapshot and not f & SNAP:
                book.end_snapshot()
            if act == F:  # F3.9: fills are not removals (ProtocolReview DO-16); ruling R-B3-FD7:
                # lots attributed by order id within the batch, whether or not the order is booked
                pending[oid] = pending.get(oid, 0) + sz
            elif act in (A, C, M, R):
                if act in (A, M) and side != S_B and side != S_A:
                    pass  # E.31: book records with side N are skipped
                elif act == R:
                    book.clear(bool(f & SNAP))
                    orders = book.orders  # Book.clear rebinds its dicts
                    if f & BAD:  # lead ruling D1: an R carrying the flag leaves the book bad
                        book.mark_bad()
                    last_am.clear()
                    pending.clear()
                    dep.clear()
                    tset = None
                else:
                    bs = BID if side == S_B else ASK
                    if act == A:
                        book.add(oid, bs, px, sz)
                        last_am[oid] = t
                        key = (bs, px)
                        dl = dep.get(key)
                        if dl is not None:
                            if t <= dl:
                                if o:
                                    cnt[10 if bs == BID else 11] += 1  # F3.11 (READING FA-23)
                            else:
                                del dep[key]
                    else:
                        emptied = _removal(book, pending, cnt, act == C, oid, bs, px, sz, o)
                        if act == C:
                            book.cancel(oid, sz)
                        else:
                            book.modify(oid, bs, px, sz)
                        if emptied is not None and book.level_total(*emptied) == 0:
                            dep[emptied] = t + REFILL_NS  # FD4: the touch emptied by fills
                        if oid in orders:
                            if act == M:
                                last_am[oid] = t
                        else:
                            last_am.pop(oid, None)
                            pending.pop(oid, None)
                if f & SNAP and f & LAST:
                    book.end_snapshot()
        if f & LAST:
            pending.clear()  # lead ruling FD5: fill lots do not carry across event batches
            new = _commit(book)
            if o:
                if last_iv != ivs[j]:
                    pass  # lead ruling FD3 (a): first update after a skipped interval: no term
                else:
                    e1, em = _e_levels(state, new)
                    if e1 is None:
                        cnt[5] += 1
                    else:
                        cnt[4] += e1
                    if em is None:
                        cnt[7] += 1
                    else:
                        cnt[6] += em
            last_iv = ivs[j]
            state = new
            if tset is not None and book.started:
                _sweep_check(book, tset, cnt, t, o)
            if rp_on and state.valid and nxt[j] > t:  # READING FA-14: M(u) is a function of u
                v = state.bp[0] + state.ap[0]
                hi = v if hi is None else max(hi, v)
                lo = v if lo is None else min(lo, v)
            if j == k0830:  # the state as of 08:30:00 opens [08:30, t]
                rp_on = True
                if state.valid:
                    hi = lo = state.bp[0] + state.ap[0]
            while kp < n_inst and k_inst[kp] == j:
                snap_book(kp)
                kp += 1
        while rpp < n_inst and r_inst[rpp] == j:
            snap_cnt(rpp)
            rpp += 1
    if kp != n_inst or rpp != n_inst:
        raise RuntimeError(f"ZM {ax.day}: {n_inst - kp} book and {n_inst - rpp} counter instants left")
    return out


def _removal(book: mb.Book, pending: dict, cnt: list, is_cancel: bool, oid: int, bs: int,
             px: int, sz: int, o: bool) -> tuple[int, int] | None:
    """F3.9 CR5: contracts removed from the level that was the best bid or ask just before the
    record, by cancels, size-reducing modifies (the reduction) and modifies to another price (the
    full size). READING FA-11 with ruling FD5: lots of an order that received F records earlier
    in the same event batch are attributed to the fill first (fills are not removals).
    Returns (side, price) when the record reduces the touch level of its side entirely by fill
    lots (ruling FD4: the level may then reach 0 through fills; the caller checks it is empty
    after the record), else None."""
    order = book.orders.get(oid)
    if order is None:
        return None
    x = _removed_lots(order, is_cancel, bs, px, sz)
    if x <= 0:
        return None
    side, price = order[0], order[1]
    touch = price == book.best(side)
    rest = _consume_fill(pending, oid, x)
    if o and touch and rest > 0:
        cnt[ZI["crb"] if side == mb.BID else ZI["cra"]] += rest
    return (side, price) if touch and rest == 0 else None


def _removed_lots(order: list, is_cancel: bool, bs: int, px: int, sz: int) -> int:
    old = order[2]
    if is_cancel:
        return min(sz, old)
    if order[0] != bs or px != order[1] or sz <= 0:
        return old  # a modify to another price (or side, or to 0): the full size leaves
    return old - sz if sz < old else 0


def _consume_fill(pending: dict, oid: int, x: int) -> int:
    f = pending.get(oid, 0)
    if not f or x <= 0:
        return x
    used = min(f, x)
    if f - used:
        pending[oid] = f - used
    else:
        del pending[oid]
    return x - used


def _sweep_check(book: mb.Book, tset: list, cnt: list, t: int, o: bool) -> None:
    """F3.10: a set of trade records sharing one ts_event that leaves the pre-trade best ask
    (bid) level's displayed quantity at 0 is a buy (sell) sweep, checked at each book update
    while the set is open; counted once per side at the first update where it holds
    (READING FA-10). Refills (F3.11) no longer depend on sweep sets (ruling FD4)."""
    _, bb, ba, done_b, done_s = tset
    if not done_b and ba is not None and book.level_total(mb.ASK, ba) == 0:
        tset[3] = True
        if o:
            cnt[ZI["swb"]] += 1
    if not done_s and bb is not None and book.level_total(mb.BID, bb) == 0:
        tset[4] = True
        if o:
            cnt[ZI["sws"]] += 1


# ------------------------------------------------------------------ pass 1: ZS / ZL MBP-1 ----
def _px_defined(p: int) -> bool:
    return p != I64_MAX and p != I64_MIN


def stream_mbp1(rec: np.ndarray, iid: int, ax: Axis, prefix: str) -> dict[str, np.ndarray]:
    """Pass 1 for a ZS or ZL front from MBP-1 (top of book and trades; P0.3), arrays over
    ax.inst. A book update is an F_LAST record; its state is that record's bid_px_00, bid_sz_00,
    ask_px_00, ask_sz_00. READING FA-4: the update is marked bad if any record of its batch (since
    the previous F_LAST record) carries F_MAYBE_BAD_BOOK."""
    r = rec[rec["instrument_id"] == iid]
    ts_a = r["ts_recv"].astype(np.int64)
    _check_order(ts_a, f"{prefix} {ax.day}")
    last_idx = np.flatnonzero((r["flags"].astype(np.int64) & mb.F_LAST) != 0)
    k_inst = _asof(ts_a, last_idx, ax.inst).tolist()
    r_inst = (np.searchsorted(ts_a, ax.inst, side="right") - 1).tolist()
    ts, fl, acts, szs = ts_a.tolist(), r["flags"].tolist(), r["action"].tolist(), r["size"].tolist()
    bpx, apx = r["bid_px_00"].tolist(), r["ask_px_00"].tolist()
    bsz, asz = r["bid_sz_00"].tolist(), r["ask_sz_00"].tolist()
    ivs = ax.iv_of(ts_a).tolist()
    n_inst = len(k_inst)
    raw2 = np.zeros(n_inst, np.int64)
    ok = np.zeros(n_inst, bool)
    cum = np.zeros((len(MC), n_inst), np.int64)
    cnt = [0, 0, 0]
    T, BAD, LAST = mb.ACT_TRADE, mb.F_MAYBE_BAD_BOOK, mb.F_LAST
    prev = None  # (bid px, bid sz, ask px, ask sz) of the last two-sided good update
    last_iv: int | None = None  # open interval of the previous book update (FD3 a)
    cur_valid, cur_raw2, batch_bad = False, 0, False
    kp, rpp = 0, 0
    while kp < n_inst and k_inst[kp] < 0:
        kp += 1
    while rpp < n_inst and r_inst[rpp] < 0:
        rpp += 1
    for j in range(len(ts)):
        f, o = fl[j], ivs[j] >= 0
        if f & BAD:
            batch_bad = True
        if acts[j] == T and o:
            cnt[0] += szs[j]  # F1.5: MBP-1 trade (T) records only (READING FA-22)
        if f & LAST:
            b, a = bpx[j], apx[j]
            two = _px_defined(b) and _px_defined(a) and not batch_bad
            new = (b, bsz[j], a, asz[j]) if two else None
            if o and last_iv == ivs[j]:  # FD3 (a): no term for the first update of an interval
                if prev is None or new is None:
                    cnt[2] += 1  # e_n not computable (G3, READING FA-6; ruling FD3 b)
                else:
                    cnt[1] += ofi_e(*prev, *new)  # crossed or locked states allowed (FD3 c)
            last_iv = ivs[j]
            prev = new
            cur_valid = two and b < a  # P0.3 mid validity
            cur_raw2 = b + a if cur_valid else 0
            batch_bad = False
            while kp < n_inst and k_inst[kp] == j:
                raw2[kp], ok[kp] = cur_raw2, cur_valid
                kp += 1
        while rpp < n_inst and r_inst[rpp] == j:
            cum[:, rpp] = cnt
            rpp += 1
    if kp != n_inst or rpp != n_inst:
        raise RuntimeError(f"{prefix} {ax.day}: instants left")
    return {f"{prefix}_raw2": raw2, f"{prefix}_ok": ok, f"{prefix}_cnt": cum}


# ------------------------------------------------------------------ pass 1: one trade date ----
def stream_day(day: date, zm: np.ndarray, zs: np.ndarray, zl: np.ndarray,
               fronts: dict[str, int], ticks: dict[str, int], ax: Axis | None = None
               ) -> dict[str, np.ndarray]:
    """Pass 1 of trade date D: book states and counters of the three fronts at the axis marks
    (windows and their sample points; FD1, FD2) and book states as of the 281 wall minutes
    08:35..13:15 (instant states: sigma, Dbar, F1.3, F1.7, F4.7), plus the per-date series the
    trailing references of later dates use. ``ax`` defaults to the regular schedule."""
    ax = axis(day) if ax is None else ax
    raw = {}
    raw.update(stream_zm(zm, int(fronts["ZM"]), ax))
    raw.update(stream_mbp1(zs, int(fronts["ZS"]), ax, "zs"))
    raw.update(stream_mbp1(zl, int(fronts["ZL"]), ax, "zl"))
    ma, wa = ax.mark_at, ax.wall_at
    out = {"marks": ax.marks, "wall_ns": ax.wall, "map_pos": ax.map_pos,
           "ax_prev": np.arange(len(ax.marks)) < ax.n_prev}
    for r in ("zm", "zs", "zl"):
        out[f"{r}_raw2"], out[f"{r}_ok"] = raw[f"{r}_raw2"][ma], raw[f"{r}_ok"][ma]
        out[f"{r}_wraw2"], out[f"{r}_wok"] = raw[f"{r}_raw2"][wa], raw[f"{r}_ok"][wa]
        out[f"{r}_cnt"] = raw[f"{r}_cnt"][:, ma]
    out["zm_spread"], out["zm_touch"] = raw["zm_spread"][ma], raw["zm_touch"][ma]
    out["zm_lvl"], out["zm_wlvl"] = raw["zm_lvl"][:, ma], raw["zm_lvl"][:, wa]
    for key in ("zm_seas", "zm_hi", "zm_lo"):
        out[key] = raw[key]
    out["fronts"] = np.array([fronts["ZM"], fronts["ZS"], fronts["ZL"]], dtype=np.int64)
    out["ticks"] = np.array([ticks["ZM"], ticks["ZS"], ticks["ZL"]], dtype=np.int64)
    out.update(day_series(out))
    return out


# ------------------------------------------------------------------ pass-1 derived series ----
def mid_ticks(p1: dict, root: str) -> np.ndarray:
    """M_X at every axis mark in ticks of X (NaN where undefined; P0.3)."""
    k = {"zm": 0, "zs": 1, "zl": 2}[root]
    tick = int(p1["ticks"][k])
    v = p1[f"{root}_raw2"] / (2.0 * tick)
    return np.where(p1[f"{root}_ok"], v, np.nan)


def wall_mid_ticks(p1: dict, root: str) -> np.ndarray:
    """M_X as of the 281 wall minutes 08:35..13:15 of D, ticks of X (NaN where undefined)."""
    k = {"zm": 0, "zs": 1, "zl": 2}[root]
    v = p1[f"{root}_wraw2"] / (2.0 * int(p1["ticks"][k]))
    return np.where(p1[f"{root}_wok"], v, np.nan)


def win(cum: np.ndarray, p: int | np.ndarray, k: int) -> np.ndarray:
    """Sum over the open-time window of k minutes ending at mark p (P0.3)."""
    return cum[..., p] - cum[..., p - k]


def _ofi_series(cnt: np.ndarray, i_val: int, i_bad: int, k: int, ps: np.ndarray) -> np.ndarray:
    """OFI_k at marks ps; NaN where an e_n of the window is not computable (READING FA-6)."""
    v = win(cnt[i_val], ps, k).astype(np.float64)
    return np.where(win(cnt[i_bad], ps, k) == 0, v, np.nan)


def lam_slope(dm: np.ndarray, sv: np.ndarray) -> float:
    """F3.12 / P0.3: OLS slope of dM on signed volume with an intercept, numpy.linalg.lstsq on
    the centred regressor. NaN when the regressor has no variation."""
    xc = sv - sv.mean()
    if not np.any(xc != 0):
        return math.nan
    a = np.column_stack([np.ones(len(xc)), xc])
    coef = np.linalg.lstsq(a, dm, rcond=None)[0]
    return float(coef[1])


def lam60_at(p1: dict, p: int, mz: np.ndarray | None = None) -> float:
    """F3.12 raw slope at mark p: the 60 one-minute intervals (q-1, q], q = p-59..p, on the
    open-time axis; those that contain trades and (READING FA-13) have valid mids at both ends;
    NaN with fewer than 30 (ProtocolReview DO-13)."""
    mz = mid_ticks(p1, "zm") if mz is None else mz
    cnt = p1["zm_cnt"]
    q = np.arange(p - 59, p + 1)
    has_tr = (cnt[ZI["ntr"], q] - cnt[ZI["ntr"], q - 1]) > 0  # READING FA-12: any T record
    dm = mz[q] - mz[q - 1]
    use = has_tr & ~np.isnan(dm)
    if int(use.sum()) < 30:
        return math.nan
    sv = ((cnt[ZI["buy"], q] - cnt[ZI["buy"], q - 1])
          - (cnt[ZI["sell"], q] - cnt[ZI["sell"], q - 1])).astype(np.float64)
    return lam_slope(dm[use], sv[use])


def day_series(p1: dict) -> dict[str, np.ndarray]:
    """Per-date values at the 279 reference minutes 08:35..13:13 that later dates' trailing
    20-date references pool (P0.3). Window statistics are taken at each minute's axis position
    (a closed minute maps to the last mark before it; ruling FD1); the depth of F3.4's Dbar is
    the book state as of the wall minute (an instant state, like sigma's mids)."""
    ps = p1["map_pos"][:N_REF]
    zc = p1["zm_cnt"]
    s = {}
    s["ref_aofi_zs1"] = np.abs(_ofi_series(p1["zs_cnt"], MI["ofi"], MI["ofi_bad"], 1, ps))
    s["ref_aofi_zs5"] = np.abs(_ofi_series(p1["zs_cnt"], MI["ofi"], MI["ofi_bad"], 5, ps))
    s["ref_aofi_zl1"] = np.abs(_ofi_series(p1["zl_cnt"], MI["ofi"], MI["ofi_bad"], 1, ps))
    s["ref_aofi_zl5"] = np.abs(_ofi_series(p1["zl_cnt"], MI["ofi"], MI["ofi_bad"], 5, ps))
    for k in (1, 5, 15):
        s[f"ref_aofi_zm{k}"] = np.abs(_ofi_series(zc, ZI["ofi"], ZI["ofi_bad"], k, ps))
    # F3.4 Dbar_m inputs: (qb_m + qa_m)/2 where the ZM book is valid (READING FA-8)
    s["ref_dep"] = np.where(p1["zm_wok"][:N_REF], p1["zm_wlvl"][:, :N_REF] / 2.0, np.nan)
    s["ref_sw5"] = (win(zc[ZI["swb"]], ps, 5) + win(zc[ZI["sws"]], ps, 5)).astype(np.float64)
    s["ref_arf15"] = np.abs(win(zc[ZI["rfb"]], ps, 15) - win(zc[ZI["rfa"]], ps, 15)).astype(
        np.float64)
    mz = mid_ticks(p1, "zm")
    s["ref_lam"] = np.array([lam60_at(p1, int(p), mz) for p in ps])
    s["ref_v15"] = win(zc[ZI["vol"]], ps, 15).astype(np.float64)  # C.5 (same minute of day)
    return s


# ------------------------------------------------------------------ pass 2 helpers ----
@dataclass(frozen=True)
class DayInfo:
    """Calendar facts of one trade date (cal33)."""

    day: date
    fronts: tuple[int, int, int]  # ZM, ZS, ZL instrument ids (P0.3)
    seg: int  # P4 G2 segment id
    releases: tuple[int, ...] = ()  # P3.6 rule 3 instants R (UTC ns)
    expiry_dates: int | None = None  # C.7 (cal33.expiry_trade_dates)
    monday_or_after_closure: bool = False  # C.10
    jja: bool = False  # C.15
    prev_same_seg: bool = True  # the previous trade date lies in D's segment (FD2 with G2)


def crush2(p1: dict, wall: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """F1 crush at every mark, exact (READING FA-29): C2 = 2e9 x C(u) cents/bu = 11 raw2_ZL
    + 2.2 raw2_ZM - raw2_ZS (raw2 = bid + ask in 1e-9 units). Returns (C2 as int64, valid)."""
    w = "w" if wall else ""  # wall: as of the wall minutes 08:35..13:15 (F1.7)
    ok = p1[f"zm_{w}ok"] & p1[f"zs_{w}ok"] & p1[f"zl_{w}ok"]
    zm = p1[f"zm_{w}raw2"]
    if np.any(zm[ok] % 10):
        raise ValueError("ZM mid not a multiple of 1e-8 USD: 2.2 x raw2 is not an integer")
    c2 = 11 * p1[f"zl_{w}raw2"] + (22 * zm) // 10 - p1[f"zs_{w}raw2"]
    return np.where(ok, c2, 0), ok


def _cents(c2: int | np.ndarray) -> float | np.ndarray:
    return c2 / 2e9


def pooled_sigma(hist20: list[dict], root: str) -> float | None:
    """P0.3 sigma_X(D): population SD of the 1-minute mid changes (ticks of X) over all
    1-minute intervals inside 08:35-13:13 of the 20 trade dates before D with valid mids at
    both ends, pooled across dates (chained across rolls). READING FA-15: undefined unless all
    20 dates exist; None if no change exists."""
    if len(hist20) != 20 or any(h is None for h in hist20):
        return None
    ch = []
    for h in hist20:
        m = wall_mid_ticks(h, root)[:N_REF]  # wall minutes 08:35..13:13 (instant states)
        d = m[1:] - m[:-1]
        ch.append(d[~np.isnan(d)])
    allc = np.concatenate(ch)
    if len(allc) == 0:
        return None
    return float(np.std(allc))


def pooled_ref(hist20: list[dict], key: str, row: int | None = None,
               median: bool = False) -> float | None:
    """P0.3 trailing 20-date reference: the mean (median where stated) of a statistic over the
    minute marks 08:35-13:13 of the 20 trade dates before D, over the marks where it is defined
    (READING FA-16). None when undefined."""
    if len(hist20) != 20 or any(h is None for h in hist20):
        return None
    vals = []
    for h in hist20:
        v = h[key] if row is None else h[key][row]
        vals.append(v[~np.isnan(v)])
    allv = np.concatenate(vals)
    if len(allv) == 0:
        return None
    return float(np.median(allv)) if median else float(np.mean(allv))


@dataclass
class Refs:
    """Everything pass 2 of D takes from the trade dates before D (constant within D)."""

    sigma: dict = field(default_factory=dict)  # "zm", "zs", "zl" -> ticks or None
    obar: dict = field(default_factory=dict)  # "zs1", "zs5", "zl1", "zl5", "zm1", "zm5", "zm15"
    dbar_sum: float | None = None  # F3.4 sum_m Dbar_m
    sbar5: float | None = None  # F3.10
    rbar15: float | None = None  # F3.11
    lam_med: float | None = None  # F3.12
    vbar: np.ndarray | None = None  # C.5, per grid minute
    ols: tuple | None = None  # F1.3 (a, b_S, b_L, sd_e in ZM ticks, n samples, n dates)
    gc: float | None = None  # F1.7 gC(D)
    gap: float | None = None  # F4.7 GAP(D)
    counts: dict = field(default_factory=dict)


def _same_seg(info: DayInfo, other: DayInfo | None) -> bool:
    return other is not None and other.seg == info.seg


def f13_fit(cur: DayInfo, hist: list[tuple[dict, DayInfo] | None]) -> tuple | None:
    """F1.3 before D's open: OLS of M_ZM = a + b_S M_ZS + b_L M_ZL + eps (natural units) on the
    1-minute samples 08:35-13:13 clear of P3.6 rule 3 of the 10 trade dates before D inside the
    current segment; at least 3 such dates (READING FA-17: dates contributing >= 1 sample),
    else None. Centred regressors with an intercept (P0.3); a = mean M_ZM - b_S mean M_ZS -
    b_L mean M_ZL; sd_e = sqrt(SSR/n) / 0.10 in ZM ticks."""
    ys, xs, xl, n_dates = [], [], [], 0
    for item in hist[-10:]:
        if item is None or not _same_seg(cur, item[1]):
            continue
        h, info = item
        ok = (h["zm_wok"] & h["zs_wok"] & h["zl_wok"])[:N_REF]  # as of the wall minutes
        clear = np.ones(N_REF, bool)
        marks = h["wall_ns"][:N_REF]
        for rel in info.releases:  # READING FA-18: mark u clear iff u not in [R-2, R+30] min
            clear &= ~((marks >= rel - 2 * MIN_NS) & (marks <= rel + 30 * MIN_NS))
        use = ok & clear
        if not use.any():
            continue
        n_dates += 1
        ys.append(h["zm_wraw2"][:N_REF][use] / 2e9)
        xs.append(h["zs_wraw2"][:N_REF][use] / 2e9)
        xl.append(h["zl_wraw2"][:N_REF][use] / 2e9)
    if n_dates < 3:
        return None
    y, s, l_ = np.concatenate(ys), np.concatenate(xs), np.concatenate(xl)
    ms, ml = s.mean(), l_.mean()
    a_mat = np.column_stack([np.ones(len(y)), s - ms, l_ - ml])
    coef, _, rank, _ = np.linalg.lstsq(a_mat, y, rcond=None)
    if rank < 3:
        return None  # READING FA-19: a rank-deficient fit is not computable
    b_s, b_l = float(coef[1]), float(coef[2])
    a = float(y.mean() - b_s * ms - b_l * ml)
    resid = y - a_mat @ coef
    sd_e = math.sqrt(float(np.sum(resid * resid)) / len(y)) / ZM_TICK_USD
    return a, b_s, b_l, sd_e, len(y), n_dates


def _gc_raw(cur: tuple[dict, DayInfo], prev: tuple[dict, DayInfo] | None) -> float | None:
    """F1.7 numerator: C(08:35:00 on D) - C(13:15:00 on the previous trade date), cents/bu;
    None if the previous date is outside D's segment (G2) or a crush is undefined."""
    if prev is None or not _same_seg(cur[1], prev[1]):
        return None
    c_now, ok_now = crush2(cur[0], wall=True)
    c_prev, ok_prev = crush2(prev[0], wall=True)
    if not (ok_now[0] and ok_prev[J_1315]):  # as of 08:35:00 on D and 13:15:00 on the previous
        return None
    return float(_cents(int(c_now[0]) - int(c_prev[J_1315])))


def _gap_raw(cur: tuple[dict, DayInfo], prev: tuple[dict, DayInfo] | None) -> float | None:
    """F4.7 numerator: M_ZM(08:35:00 on D) - M_ZM(13:15:00 on the previous trade date), ZM
    ticks; None unless the ZM front is the same at both times (READING FA-20 for D itself)."""
    if prev is None or cur[1].fronts[0] != prev[1].fronts[0]:
        return None
    m_now, m_prev = wall_mid_ticks(cur[0], "zm"), wall_mid_ticks(prev[0], "zm")
    v = m_now[0] - m_prev[J_1315]
    return None if math.isnan(v) else float(v)


def _date_scale(vals: list[float | None], minimum: int) -> float | None:
    """F1.7 sd_g / F4.7 sd_gap: population SD of the defined values; at least ``minimum``."""
    v = [x for x in vals if x is not None]
    if len(v) < minimum:
        return None
    sd = float(np.std(np.array(v)))
    return sd if sd > 0 else None


def build_refs(cur: tuple[dict, DayInfo], hist: list[tuple[dict, DayInfo] | None]) -> Refs:
    """Constant-within-D inputs of pass 2 from the trade dates before D. ``hist`` holds the
    N_HIST = 21 dates before D, oldest first (None where the date does not exist)."""
    if len(hist) != N_HIST:
        raise ValueError("hist must hold the 21 trade dates before D")
    h20 = [None if x is None else x[0] for x in hist[-20:]]
    ref = Refs()
    for root in ("zm", "zs", "zl"):
        ref.sigma[root] = pooled_sigma(h20, root)
    for key in ("zs1", "zs5", "zl1", "zl5", "zm1", "zm5", "zm15"):
        ref.obar[key] = pooled_ref(h20, f"ref_aofi_{key}")
    dbars = [pooled_ref(h20, "ref_dep", row=m) for m in range(N_LVL)]
    ref.dbar_sum = None if any(d is None for d in dbars) else float(sum(dbars))
    ref.sbar5 = pooled_ref(h20, "ref_sw5")
    ref.rbar15 = pooled_ref(h20, "ref_arf15")
    ref.lam_med = pooled_ref(h20, "ref_lam", median=True)
    if all(h is not None for h in h20):
        # C.5 Vbar: mean of V_ZM(15) at the same minute of day over the 20 dates before D
        ref.vbar = np.mean(np.stack([h["ref_v15"][:N_GRID] for h in h20]), axis=0)
    ref.ols = f13_fit(cur[1], hist[-10:])
    # F1.7: the 20 trade dates before D inside the segment; each value needs its own previous
    # date in the segment too (G2); at least 10 values
    g_vals = [_gc_raw(hist[k], hist[k - 1]) for k in range(1, N_HIST)
              if hist[k] is not None and _same_seg(cur[1], hist[k][1])]
    sd_g = _date_scale(g_vals, 10)
    g_now = _gc_raw(cur, hist[-1])
    ref.gc = None if (sd_g is None or g_now is None) else g_now / sd_g
    # F4.7: the 20 trade dates before D on which the ZM front was the same at both times
    gap_vals = [_gap_raw(hist[k], hist[k - 1]) for k in range(1, N_HIST) if hist[k] is not None]
    sd_gap = _date_scale(gap_vals, 10)
    gap_now = _gap_raw(cur, hist[-1])
    ref.gap = None if (sd_gap is None or gap_now is None) else gap_now / sd_gap
    ref.counts = {"gc_values": sum(v is not None for v in g_vals),
                  "gap_values": sum(v is not None for v in gap_vals)}
    return ref


# ------------------------------------------------------------------ pass 2: features ----
class _Row:
    """Feature values and validity of one decision minute (invalid -> 0, G3)."""

    def __init__(self) -> None:
        self.v = np.zeros(N_FEAT)
        self.ok = np.ones(N_FEAT, bool)

    def set(self, name: str, value: float | None) -> None:
        k = FI[name]
        if value is None or not math.isfinite(value):
            self.v[k], self.ok[k] = 0.0, False
        else:
            self.v[k], self.ok[k] = float(value), True


def _div(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0 or math.isnan(num) or math.isnan(den):
        return None
    return num / den


def _z_window(c: np.ndarray, ok: np.ndarray, p: int, k: int) -> float | None:
    """F1.1/F1.2: (C(t) - mean_k)/sd_k over C(t - j min), j = 1..k. READING FA-5: every sample
    point must be defined, else invalid; sd_k = 0 -> invalid. ``ok`` is False on the previous
    trade date's marks when that date is outside D's segment (G2 with ruling FD2)."""
    if p - k < 0 or not ok[p] or not ok[p - k:p].all():
        return None
    w = c[p - k:p]
    return _div(float(c[p] - w.mean()), float(w.std()))


class _DayCalc:
    """Pass-2 quantities of D shared by the rows."""

    def __init__(self, p1: dict, info: DayInfo, ref: Refs) -> None:
        self.p1, self.info, self.ref = p1, info, ref
        self.mz, self.ms, self.ml = (mid_ticks(p1, r) for r in ("zm", "zs", "zl"))
        c2, cok = crush2(p1)
        if not info.prev_same_seg:  # G2: F1 level samples stop at the segment boundary (FD2)
            cok = cok & ~p1["ax_prev"]
        self.c, self.cok = _cents(c2.astype(np.float64)), cok
        self.p0835 = int(p1["map_pos"][0])
        self.sz, self.ss, self.sl = (ref.sigma.get(r) for r in ("zm", "zs", "zl"))
        zc = p1["zm_cnt"]
        self.zc, self.scnt, self.lcnt = zc, p1["zs_cnt"], p1["zl_cnt"]

    def zc30(self, p: int) -> float | None:
        return _z_window(self.c, self.cok, p, 30)

    def ret(self, m: np.ndarray, p: int, k: int, sigma: float | None) -> float | None:
        """(M(t) - M(t - k min)) / (sigma sqrt k) in ticks (F2.1-F2.6, F4.1-F4.5)."""
        d = m[p] - m[p - k]
        return None if math.isnan(d) or sigma is None else _div(d, sigma * math.sqrt(k))

    def ofi(self, cnt: np.ndarray, iv: int, ib: int, p: int, k: int,
            obar: float | None) -> float | None:
        if win(cnt[ib], p, k) != 0:
            return None
        return _div(float(win(cnt[iv], p, k)), obar)


def _context(row: _Row, d: _DayCalc, i: int, p: int) -> None:
    """C.1-C.10, C.15 (C.11-C.14 are set after the families)."""
    p1, info, ref = d.p1, d.info, d.ref
    tod = i / TOD_DEN
    row.set("C_1", tod)  # C.1 tod
    row.set("C_2", tod * tod)  # C.2 tod^2
    ok = bool(p1["zm_ok"][p])  # READING FA-24: C.3, C.4 need a defined ZM mid at t
    tick = int(p1["ticks"][0])
    row.set("C_3", min(p1["zm_spread"][p] / tick, 5.0) if ok else None)  # C.3 spread, ticks
    row.set("C_4", math.log(1 + int(p1["zm_touch"][p])) if ok else None)  # C.4 touch depth
    v15 = float(win(d.zc[ZI["vol"]], p, 15))
    vbar = None if ref.vbar is None else float(ref.vbar[i])
    row.set("C_5", None if vbar is None else math.log((v15 + 1) / (vbar + 1)))  # C.5
    row.set("C_6", math.log(d.sz) if d.sz else None)  # C.6 log sigma_ZM(D)
    row.set("C_7", None if info.expiry_dates is None
            else min(info.expiry_dates, 60) / 60.0)  # C.7
    c8 = 1.0 if info.releases else 0.0
    row.set("C_8", c8)  # C.8 an 11:00 release of P3.6 rule 3 on D
    row.set("C_9", c8 if i >= I_1130 else 0.0)  # C.9 C.8 x 1{t >= 11:30}
    row.set("C_10", 1.0 if info.monday_or_after_closure else 0.0)  # C.10
    row.set("C_15", 1.0 if info.jja else 0.0)  # C.15


def _f1(row: _Row, d: _DayCalc, i: int, p: int) -> None:
    ref = d.ref
    z30 = d.zc30(p)
    row.set("F1_1", z30)  # F1.1 zC30
    row.set("F1_2", _z_window(d.c, d.cok, p, 120))  # F1.2 zC120
    zr = None  # F1.3 zR = e(t)/sd_e with coefficients fixed for D
    if ref.ols is not None and d.cok[p]:
        a, b_s, b_l, sd_e, _, _ = ref.ols
        mzn = d.p1["zm_raw2"][p] / 2e9
        msn = d.p1["zs_raw2"][p] / 2e9
        mln = d.p1["zl_raw2"][p] / 2e9
        e = (mzn - a - b_s * msn - b_l * mln) / ZM_TICK_USD
        zr = _div(e, sd_e)
    row.set("F1_3", zr)
    z30_5 = d.zc30(p - 5)
    row.set("F1_4", None if (z30 is None or z30_5 is None) else z30 - z30_5)  # F1.4 (FA-3)
    vz = float(win(d.zc[ZI["vol"]], p, 15))
    vs = float(win(d.scnt[MI["vol"]], p, 15))
    vl = float(win(d.lcnt[MI["vol"]], p, 15))
    vrel = _div(vz, vz + vs + vl)
    row.set("F1_5", vrel)  # F1.5 vrel15
    row.set("F1_6", None if (z30 is None or vrel is None) else z30 * vrel)  # F1.6
    row.set("F1_7", ref.gc)  # F1.7 gC(D)
    row.set("F1_8", None if ref.gc is None else ref.gc * math.exp(-i / 30.0))  # F1.8


def _f2(row: _Row, d: _DayCalc, i: int, p: int) -> None:
    ref = d.ref
    for n, k in zip((1, 2, 3), (1, 5, 15), strict=True):
        row.set(f"F2_{n}", d.ret(d.ms, p, k, d.ss))  # F2.1-F2.3 rS_k
        row.set(f"F2_{n + 3}", d.ret(d.ml, p, k, d.sl))  # F2.4-F2.6 rL_k
    # F2.7 d5 = [(dZS_5 - 11 dZL_5)/2.2 - dZM_5]/0.10/(sigma_ZM(D) sqrt 5), natural units
    d5 = None
    q = p - 5
    p1 = d.p1
    if p1["zm_ok"][p] and p1["zm_ok"][q] and p1["zs_ok"][p] and p1["zs_ok"][q] \
            and p1["zl_ok"][p] and p1["zl_ok"][q] and d.sz:
        dzs = (int(p1["zs_raw2"][p]) - int(p1["zs_raw2"][q])) / 2e9
        dzl = (int(p1["zl_raw2"][p]) - int(p1["zl_raw2"][q])) / 2e9
        dzm = (int(p1["zm_raw2"][p]) - int(p1["zm_raw2"][q])) / 2e9
        d5 = ((dzs - CRUSH_ZL * dzl) / CRUSH_ZM - dzm) / ZM_TICK_USD / (d.sz * math.sqrt(5))
    row.set("F2_7", d5)
    row.set("F2_8", d.ofi(d.scnt, MI["ofi"], MI["ofi_bad"], p, 1, ref.obar.get("zs1")))
    row.set("F2_9", d.ofi(d.scnt, MI["ofi"], MI["ofi_bad"], p, 5, ref.obar.get("zs5")))
    row.set("F2_10", d.ofi(d.lcnt, MI["ofi"], MI["ofi_bad"], p, 1, ref.obar.get("zl1")))
    row.set("F2_11", d.ofi(d.lcnt, MI["ofi"], MI["ofi_bad"], p, 5, ref.obar.get("zl5")))


def _f3(row: _Row, d: _DayCalc, i: int, p: int) -> None:
    ref, zc = d.ref, d.zc
    for n, k in zip((1, 2, 3), (1, 5, 15), strict=True):  # F3.1-F3.3 OFI_ZM_k / Obar_ZM_k
        row.set(f"F3_{n}", d.ofi(zc, ZI["ofi"], ZI["ofi_bad"], p, k, ref.obar.get(f"zm{k}")))
    iofi = None  # F3.4 IOFI5 = sum_m OFI^(m)_5 / sum_m Dbar_m
    if win(zc[ZI["iofi_bad"]], p, 5) == 0:
        iofi = _div(float(win(zc[ZI["iofi"]], p, 5)), ref.dbar_sum)
    row.set("F3_4", iofi)
    for n, k in zip((5, 6), (5, 15), strict=True):  # F3.5-F3.6 TI_k
        b, s = float(win(zc[ZI["buy"]], p, k)), float(win(zc[ZI["sell"]], p, k))
        row.set(f"F3_{n}", _div(b - s, b + s))
    seas = d.p1["zm_seas"][:, i]  # NaN when the book at t is not valid
    qi1 = qi3 = None
    if not np.isnan(seas).any():
        qb1, qa1 = seas[0], seas[N_SEAS]
        qi1 = _div(qb1 - qa1, qb1 + qa1)  # F3.7 QI1 on seasoned depth
        sb, sa = float(seas[:N_SEAS].sum()), float(seas[N_SEAS:].sum())
        qi3 = _div(sb - sa, sb + sa)  # F3.8 QI3 on seasoned depth (0 denominator -> invalid)
    row.set("F3_7", qi1)
    row.set("F3_8", qi3)
    ca, cb = float(win(zc[ZI["cra"]], p, 5)), float(win(zc[ZI["crb"]], p, 5))
    row.set("F3_9", _div(ca - cb, ca + cb))  # F3.9 CR5
    sw = float(win(zc[ZI["swb"]], p, 5) - win(zc[ZI["sws"]], p, 5))
    row.set("F3_10", _div(sw, ref.sbar5))  # F3.10 SW5
    rf = float(win(zc[ZI["rfb"]], p, 15) - win(zc[ZI["rfa"]], p, 15))
    row.set("F3_11", _div(rf, ref.rbar15))  # F3.11 RF15
    row.set("F3_12", _div(lam60_at(d.p1, p, d.mz), ref.lam_med))  # F3.12 lam60


def _f4(row: _Row, d: _DayCalc, i: int, p: int) -> None:
    ref, mz, sz = d.ref, d.mz, d.sz
    for n, k in zip((1, 2, 3, 4, 5), (1, 5, 15, 30, 60), strict=True):
        row.set(f"F4_{n}", d.ret(mz, p, k, sz))  # F4.1-F4.5 rZ_k
    rp = None  # F4.6 RP over [08:30, t] on D; 0.5 if Hi = Lo
    hi, lo = d.p1["zm_hi"][i], d.p1["zm_lo"][i]
    if d.p1["zm_ok"][p] and not math.isnan(hi):
        cur = float(d.p1["zm_raw2"][p])
        rp = 0.5 if hi == lo else (cur - lo) / (hi - lo)
    row.set("F4_6", rp)
    row.set("F4_7", ref.gap)  # F4.7 GAP(D)
    row.set("F4_8", None if ref.gap is None else ref.gap * math.exp(-i / 30.0))  # F4.8
    ropen = None  # F4.9 rOpen; 0 at 08:35 (READING FA-25: same validity as other rows)
    dm = mz[p] - mz[d.p0835]
    if not math.isnan(dm) and sz:
        ropen = 0.0 if i == 0 else dm / (sz * math.sqrt(max(1, i)))
    row.set("F4_9", ropen)
    rv = None  # F4.10 RV15: SD of the 15 one-minute mid changes ending at t / sigma_ZM(D)
    w = mz[p - 15:p + 1]
    if not np.isnan(w).any() and sz:
        rv = float(np.std(np.diff(w))) / sz
    row.set("F4_10", rv)
    db, e_off = _db(mz, p, sz)  # F4.11 DB; F4.12 DB exp(-(t - e*)/5 min)
    row.set("F4_11", db)
    row.set("F4_12", None if db is None else db * math.exp(-e_off / 5.0))
    row.set("F4_13", None if ropen is None else (ropen if i >= I_1215 else 0.0))  # F4.13 LATE


def _db(mz: np.ndarray, p: int, sz: float | None) -> tuple[float | None, int]:
    """F4.11: B(e) = (M(e) - M(e - 2 min))/(sigma sqrt 2), e = t, t-1, ..., t-13 min; B* the
    largest |B(e)| (latest e on ties); DB = B* if |B*| >= 3 else 0. READING FA-21: invalid if
    any B(e) is undefined. Returns (DB, t - e* in open minutes)."""
    if not sz:
        return None, 0
    best, best_off = None, 0
    for off in range(14):  # off = 0 is e = t (the latest); a later e wins ties
        e = p - off
        b = mz[e] - mz[e - 2]
        if math.isnan(b):
            return None, 0
        b = b / (sz * math.sqrt(2))
        if best is None or abs(b) > abs(best):
            best, best_off = b, off
    return (best if abs(best) >= 3 else 0.0), best_off


def features_day(p1: dict, info: DayInfo, ref: Refs) -> tuple[np.ndarray, np.ndarray]:
    """The 59 P4 features at i = 0..272 of D. Returns (values N_GRID x 59, valid N_GRID x 59);
    invalid values are 0 (G3), the family flags C.11-C.14 are set, G4 clipping applied."""
    d = _DayCalc(p1, info, ref)
    vals = np.zeros((N_GRID, N_FEAT))
    oks = np.zeros((N_GRID, N_FEAT), bool)
    clip_k = np.array([FI[f] for f in CLIPPED])
    for i in range(N_GRID):
        p = int(p1["map_pos"][i])  # the axis mark of t (a closed t maps back; ruling FD1)
        row = _Row()
        _context(row, d, i, p)
        _f1(row, d, i, p)
        _f2(row, d, i, p)
        _f3(row, d, i, p)
        _f4(row, d, i, p)
        for fam, names in FAMILIES.items():  # G3 family flags C.11-C.14
            row.set(FLAG_OF[fam], 1.0 if all(row.ok[FI[n]] for n in names) else 0.0)
        row.v[clip_k] = np.clip(row.v[clip_k], -CLIP, CLIP)  # G4 (READING FA-3: last step)
        vals[i], oks[i] = row.v, row.ok
    return vals, oks
