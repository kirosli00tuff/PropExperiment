"""E.33 pipeline A, Coder-A labels: executable prices (P3.2), fixed-horizon labels (P3.3), triple-barrier
labels (P3.4), exclusion rules (P3.6), rows and uniqueness weights (P3.7) and the per-minute, per-side
simulated trade outcome fields of INTERFACE.md 4.2 (P3.8's per-trade inputs).

Binding text: reports/stage_e32_discovery_protocol.md (cited "P<n>") and reports/stage_e33_briefs/INTERFACE.md.
Every choice the protocol leaves open is marked ``# READING <id>`` and logged in
reports/stage_e33_briefs/work/LabelCoder_readings.md.

Event-loop style:
1. ``replay`` drives mbo_book31.Book record by record over the ZM front's MBO records in ts_recv order (the
   book-driving part of measure31_core.InstrumentRun._run_chunk, lifted: R clears and starts the book, records
   before the first R are skipped, F_MAYBE_BAD_BOOK (and F_TOB / F_MBP, which never occur in Z1) marks the
   book bad until the next R, T / F / N records leave the book unchanged). After every record carrying F_LAST
   it appends one *book update* (protocol 0.3): (ts_recv of that record, bid_1, ask_1, book good), with bid_1
   and ask_1 in integer ticks (``NO_PX`` when the side is empty). Nothing is de-duplicated, so every update is
   kept, including several at one ts_recv.
2. Everything else steps through that update history by index. "As of u" = the last update with ts_recv <= u.

Prices are integer ticks (fixed-point price / tick, exact); a net is ``float(integer tick difference) - 0.528``
so that equal inputs give bit-equal nets (brief). The clock is ts_recv only (P0.3, LT4); ts_event is never read.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PILOT = (
    HERE.parents[2] / "stage_e31_briefs" / "work" / "pilot"
)  # E.31 library (P1.2 (d)); never pilot/runs/
if str(PILOT) not in sys.path:
    sys.path.insert(0, str(PILOT))

import mbo_book31 as mb  # noqa: E402

# This module reads no files. Every real-data read happens in build_labels33.py through data33 (guard33).

NS = 1_000_000_000
L_NS = 1 * NS  # L = 1.000 s (selection; P0.3)
MIN_NS = 60 * NS
FEE_TICKS = 0.528  # f, ticks per round trip (P0.3)
KAPPA = 1.0  # TB half-width multiplier (P3.4)
NO_PX = int(np.iinfo(np.int64).min)  # empty side in the tick arrays
LAST_GRID_OFFSET = 277  # G_h(D) = {i : 0 <= i <= 277 - h} (INTERFACE 3)

LABELS: dict[str, tuple[str, int]] = {
    "F05": ("FH", 5),
    "F15": ("FH", 15),
    "F30": ("FH", 30),
    "F60": ("FH", 60),
    "T15": ("TB", 15),
    "T30": ("TB", 30),
}

# s_flags bits (INTERFACE 4.2)
FLAG_ENTRY_FALLBACK = 1
FLAG_EXIT_FALLBACK = 2
FLAG_EXIT_LIMIT = 4
FLAG_EXIT_LAST_TOUCH = 8
FLAG_ENTRY_NOT_MADE = 16
FLAG_TB_NOT_MADE = 32

LONG, SHORT = 1, -1
SIDE_NAMES = {LONG: "long", SHORT: "short"}

# exclusion-rule keys, in the order used for the first-failing-rule attribution
ENTRY_RULES = ("r4_roll_calendar", "r1_open", "r2_close", "r3_release", "r5_book_at_t", "r5_limit")
ROW_RULES = ("p37_mid_t", "tb_m0", "r5_locked_span")
ALL_RULES = ENTRY_RULES + ROW_RULES

COLUMNS = (
    "i",
    "t_ns",
    "entry_ok",
    "row_ok",
    "y",
    "n_long",
    "n_short",
    "w",
    "span_end_ns",
    "long_made",
    "long_net",
    "long_entry_ns",
    "long_exit_ns",
    "long_flags",
    "short_made",
    "short_net",
    "short_entry_ns",
    "short_exit_ns",
    "short_flags",
    "mid_move",
)


class LabelError(RuntimeError):
    """A protocol assertion failed (stop the build; the lead decides)."""


# ---------------------------------------------------------------------------------------- book replay --
@dataclass(frozen=True)
class BookHistory:
    """The book updates of the ZM front (protocol 0.3), with lookup helpers.

    t: ts_recv (int64 ns) of each F_LAST record, non-decreasing; bid, ask: bid_1 / ask_1 in integer ticks or
    NO_PX when that side is empty; good: the book has started (an R record was seen) and is not marked bad.
    """

    t: np.ndarray
    bid: np.ndarray
    ask: np.ndarray
    good: np.ndarray
    stats: dict[str, int] = field(default_factory=dict)
    # derived (filled by ``of``)
    bid_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    ask_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    both_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    mid_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    s2: np.ndarray = field(default=None)  # type: ignore[assignment]  # bid + ask (ticks) = 2 M_ZM
    bad_cum: np.ndarray = field(default=None)  # type: ignore[assignment]  # prefix count of not both_ok
    next_bid_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    next_ask_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    prev_bid_ok: np.ndarray = field(default=None)  # type: ignore[assignment]
    prev_ask_ok: np.ndarray = field(default=None)  # type: ignore[assignment]

    @classmethod
    def of(
        cls,
        t: np.ndarray,
        bid: np.ndarray,
        ask: np.ndarray,
        good: np.ndarray,
        stats: dict[str, int] | None = None,
    ) -> BookHistory:
        t = np.asarray(t, dtype=np.int64)
        bid = np.asarray(bid, dtype=np.int64)
        ask = np.asarray(ask, dtype=np.int64)
        good = np.asarray(good, dtype=bool)
        n = len(t)
        if not (len(bid) == len(ask) == len(good) == n):
            raise ValueError("history arrays differ in length")
        if n > 1 and np.any(np.diff(t) < 0):
            raise ValueError("book update times must be non-decreasing (ts_recv order)")
        bid_ok = good & (bid != NO_PX)
        ask_ok = good & (ask != NO_PX)
        both_ok = bid_ok & ask_ok
        mid_ok = both_ok & (np.where(both_ok, bid, 0) < np.where(both_ok, ask, 1))
        s2 = np.where(both_ok, bid + np.where(both_ok, ask, 0), 0).astype(np.int64)
        bad_cum = np.concatenate(([0], np.cumsum(~both_ok, dtype=np.int64)))
        return cls(
            t,
            bid,
            ask,
            good,
            dict(stats or {}),
            bid_ok,
            ask_ok,
            both_ok,
            mid_ok,
            s2,
            bad_cum,
            _next_true(bid_ok),
            _next_true(ask_ok),
            _prev_true(bid_ok),
            _prev_true(ask_ok),
        )

    @property
    def n(self) -> int:
        return len(self.t)

    def asof(self, u: int) -> int:
        """Index of the last update with ts_recv <= u (-1 when none)."""
        return int(np.searchsorted(self.t, u, side="right")) - 1

    def first_from(self, u: int) -> int:
        """Index of the first update with ts_recv >= u (n when none)."""
        return int(np.searchsorted(self.t, u, side="left"))

    def any_not_both_ok(self, lo_ns: int, hi_ns: int) -> bool:
        """Is there a book update with ts_recv in [lo_ns, hi_ns] that lacks a bid or an ask or is marked bad
        (P3.6 rule 5, row part)?"""
        a = self.first_from(lo_ns)
        b = self.asof(hi_ns) + 1
        if b <= a:
            return False
        return bool(self.bad_cum[b] - self.bad_cum[a] > 0)


def _next_true(mask: np.ndarray) -> np.ndarray:
    """next[k] = smallest j >= k with mask[j], or n; one extra slot so next[n] = n."""
    n = len(mask)
    idx = np.where(mask, np.arange(n, dtype=np.int64), n)
    out = np.minimum.accumulate(idx[::-1])[::-1] if n else idx
    return np.concatenate((out, [n])).astype(np.int64)


def _prev_true(mask: np.ndarray) -> np.ndarray:
    """prev[k] = largest j <= k with mask[j], or -1."""
    n = len(mask)
    idx = np.where(mask, np.arange(n, dtype=np.int64), -1)
    return (np.maximum.accumulate(idx) if n else idx).astype(np.int64)


def _field(records: Any, name: str) -> np.ndarray:
    return np.asarray(records[name])


def replay(records: Any, front_iid: int, tick: int, end_ns: int | None = None) -> BookHistory:
    """Rebuild the ZM front's book from MBO records (MBO_COMPACT fields; a structured array or a mapping of
    arrays) and return its book updates. Only records with instrument_id == front_iid and, when ``end_ns`` is
    given, ts_recv <= end_ns are used (LT7 truncation). Records are applied in ts_recv order; a stable sort is
    applied (and counted) if the input is not already in that order, so ties keep file order (LT4)."""
    if tick <= 0:
        raise ValueError("tick must be positive")
    iid = _field(records, "instrument_id")
    mask = iid == front_iid
    ts = _field(records, "ts_recv")[mask].astype(np.int64)
    cols = {
        k: _field(records, k)[mask]
        for k in ("action", "side", "price", "size", "order_id", "flags")
    }
    decreases = int(np.count_nonzero(np.diff(ts) < 0)) if len(ts) > 1 else 0
    if decreases:
        order = np.argsort(ts, kind="stable")
        ts = ts[order]
        cols = {k: v[order] for k, v in cols.items()}
    if end_ns is not None:
        keep = int(np.searchsorted(ts, end_ns, side="right"))
        ts = ts[:keep]
        cols = {k: v[:keep] for k, v in cols.items()}
    stats = {"front_records": int(len(ts)), "ts_recv_decreases": decreases}
    t_out, b_out, a_out, g_out = _drive_book(
        ts.tolist(),
        cols["action"].astype(np.int64).tolist(),
        cols["side"].astype(np.int64).tolist(),
        cols["price"].astype(np.int64).tolist(),
        cols["size"].astype(np.int64).tolist(),
        cols["order_id"].astype(np.uint64).tolist(),
        cols["flags"].astype(np.int64).tolist(),
        stats,
    )
    bid = _to_ticks(np.asarray(b_out, dtype=np.int64), tick)
    ask = _to_ticks(np.asarray(a_out, dtype=np.int64), tick)
    stats["updates"] = int(len(t_out))
    return BookHistory.of(
        np.asarray(t_out, dtype=np.int64), bid, ask, np.asarray(g_out, dtype=bool), stats
    )


def _to_ticks(px: np.ndarray, tick: int) -> np.ndarray:
    have = px != NO_PX
    if np.any(px[have] % tick != 0):
        raise LabelError("a book price is not a whole number of ticks")
    out = np.full(len(px), NO_PX, dtype=np.int64)
    out[have] = px[have] // tick
    return out


def _drive_book(
    ts: list,
    acts: list,
    sides: list,
    pxs: list,
    szs: list,
    oids: list,
    fls: list,
    stats: dict[str, int],
) -> tuple[list, list, list, list]:
    """The event loop (lifted from measure31_core.InstrumentRun._run_chunk, book part only; no placements,
    fill models or TOP accounting). One book update per record carrying F_LAST, after the record."""
    book = mb.Book()
    A, C, M, R = mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY, mb.ACT_CLEAR
    S_A, S_B = mb.SIDE_ASK_CODE, mb.SIDE_BID_CODE
    # READING BOOK-BAD-FLAGS: E.31 also marks the book bad on F_TOB / F_MBP (0 such Z1 records, data facts 1.5)
    BADF, SNAP, LAST = mb.F_MAYBE_BAD_BOOK | mb.F_TOB | mb.F_MBP, mb.F_SNAPSHOT, mb.F_LAST
    t_out: list[int] = []
    b_out: list[int] = []
    a_out: list[int] = []
    g_out: list[bool] = []
    before_start = side_n = bad_marks = 0
    for t, act, side, px, sz, oid, fl in zip(ts, acts, sides, pxs, szs, oids, fls, strict=True):
        if not book.started and act != R:
            before_start += 1  # no book before the first R (E.31 README convention 5)
            continue
        if book.in_snapshot and not fl & SNAP:
            book.end_snapshot()
        if act in (A, M):
            if side != S_A and side != S_B:
                side_n += 1
            else:
                bs = mb.BID if side == S_B else mb.ASK
                if act == A:
                    book.add(oid, bs, px, sz)
                else:
                    book.modify(oid, bs, px, sz)
        elif act == C:
            book.cancel(oid, sz)
        elif act == R:
            book.clear(bool(fl & SNAP))
        # T, F, N (and anything else) do not change the book
        # Lead ruling D1 (2026-10-28): the bad mark is applied after the record, so an R record that carries
        # F_MAYBE_BAD_BOOK clears first and then leaves the book bad until the next R (for every other record the
        # order makes no difference: the mark is sticky until an R).
        if fl & BADF and not book.bad:
            book.mark_bad()
            bad_marks += 1
        if fl & SNAP and fl & LAST:
            book.end_snapshot()
        if fl & LAST:
            bp, ap = book.prices
            t_out.append(t)
            b_out.append(bp[-1] if bp else NO_PX)
            a_out.append(ap[0] if ap else NO_PX)
            g_out.append(book.started and not book.bad)
    stats["records_before_start"] = before_start
    stats["book_records_side_n"] = side_n
    stats["bad_marks"] = bad_marks
    for k, v in book.anomalies.items():
        stats[f"anomaly_{k}"] = v
    return t_out, b_out, a_out, g_out


# ------------------------------------------------------------------------------------------ day inputs --
@dataclass(frozen=True)
class DayInputs:
    """Everything a label computation needs about trade date D besides the book (all times UTC ns).

    t0_ns: 08:35:00 CT on D (grid minute i = 0 and the rule 1 bound); close_ns: 13:13:00 CT (rule 2);
    session_end_ns: 13:20:00 CT (end of D's day session, P3.2 exit fallback bound); releases: release instants R
    on D (P3.6 rule 3); limits: (HL, LL) fixed-point int64 of the front's last definition with ts_recv <= 08:30
    CT on D, or None (rule 5 skip case); tick: fixed-point units per ZM tick; sigma_zm: sigma_ZM(D) in ticks
    (TB only; INTERFACE 4.1); excluded: P1.4 exclusion of D (rule 4)."""

    date: str
    t0_ns: int
    close_ns: int
    session_end_ns: int
    releases: tuple[int, ...]
    limits: tuple[int, int] | None
    tick: int
    excluded: bool
    sigma_zm: float | None = None

    def __post_init__(self) -> None:
        if self.close_ns - self.t0_ns != (13 * 60 + 13 - (8 * 60 + 35)) * MIN_NS:
            raise ValueError("close_ns must be 13:13:00 CT when t0_ns is 08:35:00 CT")
        if self.session_end_ns - self.t0_ns != (13 * 60 + 20 - (8 * 60 + 35)) * MIN_NS:
            raise ValueError("session_end_ns must be 13:20:00 CT when t0_ns is 08:35:00 CT")
        if self.limits is not None:
            hl, ll = self.limits
            if hl in (0, mb.UNDEF_PRICE) or ll in (0, mb.UNDEF_PRICE):
                raise ValueError(
                    "limits with UNDEF_PRICE or 0 must be passed as None (P3.6 rule 5)"
                )
            if not hl > ll:
                raise ValueError("high limit must exceed low limit")


def grid(h: int) -> np.ndarray:
    """Minute indices of G_h(D)."""
    return np.arange(0, LAST_GRID_OFFSET - h + 1, dtype=np.int64)


def limit_ticks(day: DayInputs) -> tuple[int, int] | None:
    """(HL, LL) in integer ticks for the P3.2 limit mark."""
    if day.limits is None:
        return None
    hl, ll = day.limits
    if hl % day.tick or ll % day.tick:
        raise LabelError(f"{day.date}: a price limit is not a whole number of ticks")
    return hl // day.tick, ll // day.tick


# --------------------------------------------------------------------------------------- entry rules --
def _release_hit(t: int, end: int, releases: Sequence[int]) -> bool:
    """P3.6 rule 3: the closed span [t, end] intersects the closed window [R - 2 min, R + 30 min]."""
    return any(t <= r + 30 * MIN_NS and end >= r - 2 * MIN_NS for r in releases)


def _near_limit(hist: BookHistory, k: int, day: DayInputs) -> bool:
    """P3.6 rule 5 limit part at book update k (exact integer arithmetic in fixed point):
    M >= HL - 0.02c  <=>  100 (bid + ask) >= 198 HL - 2 LL;  M <= LL + 0.02c  <=>  100 (bid + ask) <= 202 LL + 2 HL,
    with bid, ask fixed point, c = (HL + LL)/2."""
    hl, ll = day.limits  # type: ignore[misc]
    s_fp = (int(hist.bid[k]) + int(hist.ask[k])) * day.tick
    return 100 * s_fp >= 198 * hl - 2 * ll or 100 * s_fp <= 202 * ll + 2 * hl


def entry_rule_fails(hist: BookHistory | None, day: DayInputs, h: int, t: int) -> dict[str, bool]:
    """Which entry rules (P3.6 first paragraph) fail at decision time t for horizon h. The possible span is
    [t, t + L + h min] (P3.6). A rule that cannot be evaluated because an earlier-listed condition already fails
    (no book at t) reports False; the first-failing attribution uses ENTRY_RULES order."""
    end = t + L_NS + h * MIN_NS
    out = dict.fromkeys(ENTRY_RULES, False)
    out["r4_roll_calendar"] = bool(day.excluded)
    out["r1_open"] = t < day.t0_ns
    out["r2_close"] = end > day.close_ns
    out["r3_release"] = _release_hit(t, end, day.releases)
    if (
        hist is None
    ):  # only on an excluded date (rule 4 already fails); the book rules are not evaluated
        if not day.excluded:
            raise ValueError("the book rules need the book history on a date that is not excluded")
        return out
    k = hist.asof(t)
    # Lead ruling D2 (2026-10-28): the entry needs M_ZM(t) defined (both sides, bid_1 < ask_1, not bad) on every
    # date, with or without limit prices; a crossed or locked book at t fails r5_book_at_t. (Supersedes READING
    # R5-CROSSED, which applied only on dates with limits.)
    book_ok = k >= 0 and bool(hist.mid_ok[k])
    out["r5_book_at_t"] = not book_ok
    if day.limits is not None and book_ok:
        out["r5_limit"] = _near_limit(hist, k, day)
    return out


# ----------------------------------------------------------------------------------- trade simulation --
@dataclass(frozen=True)
class EntryFill:
    made: bool
    fill_ns: int  # -1 when not made
    k: int  # index of the entry fill update (-1 when not made)
    price: int  # ticks (ask for a long, bid for a short); NO_PX when not made
    flags: int


def planned_exit_ns(kind: str, h: int, t: int) -> int:
    """READING ENTRY-WINDOW: the planned exit time that bounds the P3.2 entry fallback. FH: the exit decision
    time t + h (P3.8 "FH at t + h"); TB: the vertical barrier t + L + h (the latest exit decision; tau depends
    on the fill itself). The fallback fill update must have ts_recv strictly before it."""
    return t + h * MIN_NS if kind == "FH" else t + L_NS + h * MIN_NS


def entry_fill(hist: BookHistory, kind: str, h: int, t: int, side: int) -> EntryFill:
    """P3.2 entry of one side decided at t: a buy fills at ask_1 as of t + L, a sell at bid_1; fallback to the
    first later update at which that side exists and the book is not bad, strictly before the planned exit; for
    TB the entry also needs M_ZM defined at the entry fill update (else not made, flag 32)."""
    u = t + L_NS
    ok = hist.ask_ok if side == LONG else hist.bid_ok
    nxt = hist.next_ask_ok if side == LONG else hist.next_bid_ok
    px = hist.ask if side == LONG else hist.bid
    k = hist.asof(u)
    flags = 0
    if k >= 0 and ok[k]:
        ke, fill_ns = k, u
    else:
        flags |= FLAG_ENTRY_FALLBACK
        j = int(nxt[k + 1])
        if j >= hist.n or hist.t[j] >= planned_exit_ns(kind, h, t):
            return EntryFill(False, -1, -1, NO_PX, flags | FLAG_ENTRY_NOT_MADE)
        ke, fill_ns = j, int(hist.t[j])
    if kind == "TB" and not hist.mid_ok[ke]:
        return EntryFill(False, -1, -1, NO_PX, flags | FLAG_TB_NOT_MADE)
    return EntryFill(True, fill_ns, ke, int(px[ke]), flags)


def entry_fill_from_records(
    records: Any, front_iid: int, tick: int, cutoff_ns: int, kind: str, h: int, t: int, side: int
) -> EntryFill:
    """LT7 hook: one side's entry fill recomputed from the given records truncated at ts_recv <= cutoff_ns
    (the production fill time: t + L, or the fallback fill update)."""
    return entry_fill(replay(records, front_iid, tick, end_ns=cutoff_ns), kind, h, t, side)


@dataclass(frozen=True)
class ExitFill:
    fill_ns: int
    price: int  # ticks
    flags: int


def exit_fill(hist: BookHistory, day: DayInputs, u: int, side: int) -> ExitFill:
    """P3.2 exit of a position of ``side`` with the exit order filling as of u (= exit decision + L): a long
    sells at bid_1, a short buys at ask_1; fallback to the first later update with that side present and the
    book good, before 13:20:00; else the limit mark (low limit for a long, high limit for a short) or, with no
    limits on D, the last valid touch on that side before it emptied or the book was marked bad."""
    ok = hist.bid_ok if side == LONG else hist.ask_ok
    nxt = hist.next_bid_ok if side == LONG else hist.next_ask_ok
    prv = hist.prev_bid_ok if side == LONG else hist.prev_ask_ok
    px = hist.bid if side == LONG else hist.ask
    k = hist.asof(u)
    if k >= 0 and ok[k]:
        return ExitFill(u, int(px[k]), 0)
    j = int(nxt[k + 1])
    if j < hist.n and hist.t[j] < day.session_end_ns:
        return ExitFill(int(hist.t[j]), int(px[j]), FLAG_EXIT_FALLBACK)
    # READING EXIT-MARK-TIME: a marked exit has no fill update; its time is 13:20:00 CT (end of the fallback window)
    lim = limit_ticks(day)
    if lim is not None:
        hl, ll = lim
        return ExitFill(
            day.session_end_ns, ll if side == LONG else hl, FLAG_EXIT_FALLBACK | FLAG_EXIT_LIMIT
        )
    j = int(prv[k]) if k >= 0 else -1
    if j < 0:
        raise LabelError(f"{day.date}: exit at {u} needs a last valid touch and none exists")
    return ExitFill(day.session_end_ns, int(px[j]), FLAG_EXIT_FALLBACK | FLAG_EXIT_LAST_TOUCH)


def barrier_half_width(sigma_zm: float | None, h: int) -> float:
    """b = kappa x sigma_ZM(D) x sqrt(h) ticks (P3.4)."""
    if sigma_zm is None or not math.isfinite(sigma_zm) or not sigma_zm > 0:
        raise LabelError("TB needs a finite positive sigma_ZM(D)")  # READING TB-SIGMA
    return KAPPA * float(sigma_zm) * math.sqrt(h)


def first_barrier(hist: BookHistory, k0: int, hi_ns: int, b: float) -> tuple[int, int]:
    """First book update after index k0 with ts_recv <= hi_ns at which M_ZM is defined and
    M - m0 >= b (up, +1) or M - m0 <= -b (down, -1), m0 = M_ZM at update k0. Returns (index, direction) or
    (-1, 0). The test is exact: (S - S0) >= 2b with S = bid + ask integer ticks (doubling is exact in float64).
    READING TB-TIE: by update order (a later update with the same ts_recv never pre-empts an earlier one)."""
    hi = hist.asof(hi_ns)
    lo = k0 + 1
    if hi < lo:
        return -1, 0
    d = (hist.s2[lo : hi + 1] - hist.s2[k0]).astype(np.float64)
    defined = hist.mid_ok[lo : hi + 1]
    two_b = 2.0 * b
    up = defined & (d >= two_b)
    dn = defined & (d <= -two_b)
    if np.any(up & dn):
        raise LabelError("one book update reached both barriers (P3.4 assertion)")
    hit = up | dn
    if not np.any(hit):
        return -1, 0
    j = int(np.argmax(hit))
    return lo + j, (1 if up[j] else -1)


@dataclass(frozen=True)
class SideOutcome:
    made: bool
    net: float
    entry_ns: int
    exit_ns: int
    flags: int


NOT_ENTERED = SideOutcome(False, math.nan, -1, -1, 0)


def simulate_side(
    hist: BookHistory, day: DayInputs, kind: str, h: int, t: int, side: int, b: float | None = None
) -> SideOutcome:
    """One side's simulated trade entered at decision time t (P3.2-P3.4, P3.8 per-trade part)."""
    ent = entry_fill(hist, kind, h, t, side)
    if not ent.made:
        return SideOutcome(False, math.nan, -1, -1, ent.flags)
    if kind == "FH":
        ex = exit_fill(hist, day, t + h * MIN_NS + L_NS, side)
    else:
        if b is None:
            b = barrier_half_width(day.sigma_zm, h)
        kh, _ = first_barrier(hist, ent.k, t + L_NS + h * MIN_NS, b)
        tau = int(hist.t[kh]) if kh >= 0 else t + L_NS + h * MIN_NS
        ex = exit_fill(hist, day, tau + L_NS, side)
    diff = ex.price - ent.price if side == LONG else ent.price - ex.price
    return SideOutcome(True, float(diff) - FEE_TICKS, ent.fill_ns, ex.fill_ns, ent.flags | ex.flags)


# -------------------------------------------------------------------------------------------- labels --
@dataclass(frozen=True)
class RowLabel:
    ok: bool
    fail: str  # the row-only rule that removed it ("" when ok)
    y: int
    n_long: float
    n_short: float
    span_end_ns: int


def _row_removed(rule: str) -> RowLabel:
    return RowLabel(False, rule, 0, math.nan, math.nan, -1)


def tb_row_end(h: int, t: int) -> int:
    """Lead ruling R-L10: the end of a TB row's whole possible span [t, t + 2L + h min]."""
    return t + 2 * L_NS + h * MIN_NS


def tb_row_rule_fail(day: DayInputs, h: int, t: int) -> str:
    """Lead ruling R-L10: P3.6 rules 2 and 3 as row rules of a TB row, on its whole possible span
    [t, t + 2L + h] (their entry part stays on [t, t + L + h]). Returns the failing rule or "". On the
    whole-minute grid G_h they cannot fail where the entry part holds (t + 2L + h <= 13:12:02 < 13:13:00; the
    release windows start on whole minutes, t + h is a whole minute); kept for the rule's literal scope."""
    end = tb_row_end(h, t)
    if end > day.close_ns:
        return "r2_close"
    if _release_hit(t, end, day.releases):
        return "r3_release"
    return ""


def label_row(hist: BookHistory, kind: str, h: int, t: int, b: float | None) -> RowLabel:
    """P3.3 / P3.4 label at t for a minute that passes the entry rules, with the row-only rules (P3.7 valid
    M_ZM(t); P3.6 rule 5 locked-book row rule over the span)."""
    k_t = hist.asof(t)
    if not (k_t >= 0 and hist.mid_ok[k_t]):
        return _row_removed("p37_mid_t")
    poss_end = t + L_NS + h * MIN_NS
    k1 = hist.asof(t + L_NS)
    if kind == "FH":
        span_end = poss_end
        if hist.any_not_both_ok(t, span_end):
            return _row_removed("r5_locked_span")
        k2 = hist.asof(t + h * MIN_NS + L_NS)
        _check_both(hist, (k1, k2))
        n_long = float(int(hist.bid[k2]) - int(hist.ask[k1])) - FEE_TICKS
        n_short = float(int(hist.bid[k1]) - int(hist.ask[k2])) - FEE_TICKS
        if n_long > 0 and n_short > 0:
            raise LabelError(f"N_long and N_short both positive at t={t} (P3.3 claim)")
        y = 1 if n_long > 0 else (-1 if n_short > 0 else 0)
        return RowLabel(True, "", y, n_long, n_short, span_end)
    if b is None:
        raise ValueError("TB needs the barrier half-width")
    # Lead ruling R-L10 (supersedes READING TB-SPAN): every P3.6 row rule of a TB row checks the whole possible
    # span [t, t + 2L + h] (every span [t, tau + L] the label can have, tau <= t + L + h), so the keep decision
    # does not depend on the realised tau; the entry rules stay on [t, t + L + h] (entry_rule_fails).
    row_end = tb_row_end(h, t)
    if not (k1 >= 0 and hist.mid_ok[k1]):
        # READING TB-M0: m0 = M_ZM(t + L) undefined -> no TB label -> the row is removed
        if hist.any_not_both_ok(t, row_end):
            return _row_removed("r5_locked_span")
        return _row_removed("tb_m0")
    kh, direction = first_barrier(hist, k1, poss_end, b)
    tau = int(hist.t[kh]) if kh >= 0 else poss_end
    span_end = tau + L_NS
    if hist.any_not_both_ok(t, row_end):  # R-L10: [t, t + 2L + h] whatever tau is
        return _row_removed("r5_locked_span")
    kx = hist.asof(span_end)
    _check_both(hist, (k1, kx))
    n_long = float(int(hist.bid[kx]) - int(hist.ask[k1])) - FEE_TICKS
    n_short = float(int(hist.bid[k1]) - int(hist.ask[kx])) - FEE_TICKS
    return RowLabel(True, "", direction, n_long, n_short, span_end)


def _check_both(hist: BookHistory, ks: Sequence[int]) -> None:
    for k in ks:
        if k < 0 or not hist.both_ok[k]:
            raise LabelError(
                "a label price lookup hit an invalid book inside a kept span (internal error)"
            )


# ------------------------------------------------------------------------------------------- weights --
def interval_set(start_ns: int, end_ns: int) -> list[int]:
    """One-minute intervals m (absolute UTC minute numbers; CT minute marks coincide with UTC ones) that the
    span [start_ns, end_ns] intersects by more than one second (P3.7)."""
    out = []
    for m in range(start_ns // MIN_NS, end_ns // MIN_NS + 1):
        overlap = min(end_ns, (m + 1) * MIN_NS) - max(start_ns, m * MIN_NS)
        if overlap > NS:
            out.append(m)
    return out


def uniqueness_weights(starts: Sequence[int], ends: Sequence[int]) -> np.ndarray:
    """P3.7 average uniqueness: c_m = rows whose span meets interval m by > 1 s; u_i = mean of 1/c_m over the
    intervals span_i meets by > 1 s; raw (no renormalisation). READING W-SUM: the mean is math.fsum(1/c_m) / n
    (correctly rounded, order-free)."""
    sets = [interval_set(int(a), int(e)) for a, e in zip(starts, ends, strict=True)]
    count: dict[int, int] = {}
    for s in sets:
        for m in s:
            count[m] = count.get(m, 0) + 1
    w = np.empty(len(sets), dtype=np.float64)
    for i, s in enumerate(sets):
        if not s:
            raise LabelError("a span meets no one-minute interval by more than one second")
        w[i] = math.fsum(1.0 / count[m] for m in s) / len(s)
    return w


def mid_move(hist: BookHistory, t: int, h: int) -> float:
    """Lead follow-up (P6.2 reported-only hit rate; never used by P8): M_ZM(t + L + h) - M_ZM(t + L) in ZM
    ticks, each mid as of the last book update with ts_recv <= that instant (P0.3); NaN when either mid is
    undefined. TB labels use the vertical h. Exact: (S2 - S1) / 2 with S = bid_1 + ask_1 integer ticks."""
    k1 = hist.asof(t + L_NS)
    k2 = hist.asof(t + L_NS + h * MIN_NS)
    if k1 < 0 or k2 < 0 or not (hist.mid_ok[k1] and hist.mid_ok[k2]):
        return math.nan
    return float(int(hist.s2[k2]) - int(hist.s2[k1])) / 2.0


# ---------------------------------------------------------------------------------------- one label --
def compute_label(
    hist: BookHistory | None, day: DayInputs, label: str
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """The INTERFACE 4.2 table of one (label, date) and its exclusion counts. ``hist`` may be None only on an
    excluded date (every flag is false; mid_move is then NaN). READING MIDMOVE-EXCL: mid_move is filled for every
    grid minute whenever a book history is given, excluded dates included (it is not a flag)."""
    kind, h = LABELS[label]
    idx = grid(h)
    n = len(idx)
    t_ns = day.t0_ns + idx * MIN_NS
    cols: dict[str, np.ndarray] = {
        "i": idx.astype(np.int16),
        "t_ns": t_ns.astype(np.int64),
        "entry_ok": np.zeros(n, bool),
        "row_ok": np.zeros(n, bool),
        "y": np.zeros(n, np.int8),
        "n_long": np.full(n, np.nan),
        "n_short": np.full(n, np.nan),
        "w": np.full(n, np.nan),
        "span_end_ns": np.full(n, -1, np.int64),
    }
    for s in ("long", "short"):
        cols[f"{s}_made"] = np.zeros(n, bool)
        cols[f"{s}_net"] = np.full(n, np.nan)
        cols[f"{s}_entry_ns"] = np.full(n, -1, np.int64)
        cols[f"{s}_exit_ns"] = np.full(n, -1, np.int64)
        cols[f"{s}_flags"] = np.zeros(n, np.int16)
    cols["mid_move"] = np.full(n, np.nan)
    if hist is not None:
        cols["mid_move"] = np.array([mid_move(hist, int(x), h) for x in t_ns], dtype=np.float64)
    any_fail = dict.fromkeys(ALL_RULES, 0)
    first_fail = dict.fromkeys(ALL_RULES, 0)
    crossed_at_t = 0
    if not day.excluded and hist is None:
        raise ValueError("a non-excluded date needs the book history")
    b = barrier_half_width(day.sigma_zm, h) if kind == "TB" and not day.excluded else None
    for r in range(n):
        t = int(t_ns[r])
        fails = entry_rule_fails(None if day.excluded else hist, day, h, t)
        for k, v in fails.items():
            any_fail[k] += int(v)
        first = next((k for k in ENTRY_RULES if fails[k]), "")
        if (
            not day.excluded
        ):  # crossed or locked at t (both sides, good, bid_1 >= ask_1): part of r5_book_at_t (D2)
            k = hist.asof(t)
            crossed_at_t += int(k >= 0 and hist.both_ok[k] and not hist.mid_ok[k])
        if first:
            first_fail[first] += 1
            continue
        cols["entry_ok"][r] = True
        for side in (LONG, SHORT):
            o = simulate_side(hist, day, kind, h, t, side, b)  # type: ignore[arg-type]
            s = SIDE_NAMES[side]
            cols[f"{s}_made"][r] = o.made
            cols[f"{s}_net"][r] = o.net
            cols[f"{s}_entry_ns"][r] = o.entry_ns
            cols[f"{s}_exit_ns"][r] = o.exit_ns
            cols[f"{s}_flags"][r] = o.flags
        row_fail = tb_row_rule_fail(day, h, t) if kind == "TB" else ""  # R-L10
        lab = _row_removed(row_fail) if row_fail else label_row(hist, kind, h, t, b)  # type: ignore[arg-type]
        if not lab.ok:
            any_fail[lab.fail] += 1
            first_fail[lab.fail] += 1
            continue
        cols["row_ok"][r] = True
        cols["y"][r] = lab.y
        cols["n_long"][r] = lab.n_long
        cols["n_short"][r] = lab.n_short
        cols["span_end_ns"][r] = lab.span_end_ns
    keep = cols["row_ok"]
    if np.any(keep):
        cols["w"][keep] = uniqueness_weights(t_ns[keep], cols["span_end_ns"][keep])
    check_invariants(cols)
    excl = {
        "date": day.date,
        "label": label,
        "grid_minutes": int(n),
        "entry_ok_minutes": int(cols["entry_ok"].sum()),
        "rows_kept": int(keep.sum()),
        "excluded_date": bool(day.excluded),
        "limits_none": day.limits is None,
        "rows_removed_by_rule": any_fail,
        "rows_removed_first_rule": first_fail,
        "entry_minutes_removed_by_rule": {k: any_fail[k] for k in ENTRY_RULES},
        "entry_minutes_removed_first_rule": {k: first_fail[k] for k in ENTRY_RULES},
        "note": "rows_removed_by_rule counts each rule where it can be evaluated (entry rules on every grid "
        "minute; row-only rules p37_mid_t, tb_m0, r5_locked_span only on minutes that pass the entry "
        "rules, in that order); *_first_rule attributes each removed minute to its first failing rule in "
        "the order r4, r1, r2, r3, r5_book_at_t, r5_limit, p37_mid_t, tb_m0, r5_locked_span. Since the lead's "
        "ruling D2, r5_book_at_t fails whenever M_ZM(t) is undefined (a side missing, a bad book, or bid_1 >= "
        "ask_1; the last case is also counted in book_crossed_or_locked_at_t), so p37_mid_t cannot fire.",
        "book_crossed_or_locked_at_t": int(crossed_at_t),
        "lt2_span_violations": span_violations(cols, hist, day, label),
        "flag_counts": {s: _flag_counts(cols[f"{s}_flags"]) for s in ("long", "short")},
        "book_stats": dict(hist.stats) if hist is not None else {},
    }
    if excl["lt2_span_violations"]:
        raise LabelError(f"{day.date} {label}: {excl['lt2_span_violations']} kept rows violate LT2")
    return cols, excl


def span_violations(
    cols: Mapping[str, np.ndarray], hist: BookHistory | None, day: DayInputs, label: str
) -> int:
    """LT2 (P4.1): re-check every kept row's span from the table's own t_ns and span_end_ns: inside
    [08:35:00, 13:13:00] on D, clear of every release window, no book update in [t, max(t + L + h, span_end)]
    (FH) or [t, t + 2L + h] (TB, lead ruling R-L10) lacking a side or marked bad, D not excluded. Returns the
    number of violating rows (must be 0)."""
    kind, h = LABELS[label]
    bad = 0
    for r in np.flatnonzero(cols["row_ok"]):
        t, e = int(cols["t_ns"][r]), int(cols["span_end_ns"][r])
        hi = max(tb_row_end(h, t) if kind == "TB" else t + L_NS + h * MIN_NS, e)
        if (
            day.excluded
            or hist is None
            or t < day.t0_ns
            or hi > day.close_ns
            or e <= t
            or _release_hit(t, hi, day.releases)
            or hist.any_not_both_ok(t, hi)
        ):
            bad += 1
    return bad


def _flag_counts(flags: np.ndarray) -> dict[str, int]:
    names = {
        FLAG_ENTRY_FALLBACK: "entry_fallback",
        FLAG_EXIT_FALLBACK: "exit_fallback",
        FLAG_EXIT_LIMIT: "exit_limit_mark",
        FLAG_EXIT_LAST_TOUCH: "exit_last_touch_mark",
        FLAG_ENTRY_NOT_MADE: "entry_not_made",
        FLAG_TB_NOT_MADE: "tb_entry_not_made",
    }
    return {v: int(np.count_nonzero(flags.astype(np.int64) & k)) for k, v in names.items()}


def check_invariants(cols: Mapping[str, np.ndarray]) -> None:
    """Schema invariants (INTERFACE 4.2); raises LabelError. Compares values only for equality (rule 1)."""
    row, ent = cols["row_ok"], cols["entry_ok"]
    if np.any(row & ~ent):
        raise LabelError("a row is kept at a minute whose entry rules fail")
    if (
        np.any(cols["y"][~row] != 0)
        or np.any(~np.isnan(cols["n_long"][~row]))
        or np.any(cols["span_end_ns"][~row] != -1)
        or np.any(~np.isnan(cols["w"][~row]))
    ):
        raise LabelError("non-row minutes must carry y = 0, NaN nets and weights, span_end -1")
    if np.any(np.isnan(cols["n_long"][row])) or np.any(np.isnan(cols["w"][row])):
        raise LabelError("a kept row lacks a net or a weight")
    for s, name in ((LONG, "long"), (SHORT, "short")):
        made = cols[f"{name}_made"]
        if np.any(made & ~ent):
            raise LabelError("a trade is made at a minute whose entry rules fail")
        if np.any(np.isnan(cols[f"{name}_net"][made])) or np.any(
            ~np.isnan(cols[f"{name}_net"][~made])
        ):
            raise LabelError("s_net must be set exactly where s_made")
        nofb = row & (
            (cols[f"{name}_flags"].astype(np.int64) & (FLAG_ENTRY_FALLBACK | FLAG_EXIT_FALLBACK))
            == 0
        )
        nlab = cols["n_long"] if s == LONG else cols["n_short"]
        if np.any(~made[nofb]) or not np.array_equal(cols[f"{name}_net"][nofb], nlab[nofb]):
            raise LabelError(f"invariant s_net == n_s failed for {name} (row_ok, no fallback)")
