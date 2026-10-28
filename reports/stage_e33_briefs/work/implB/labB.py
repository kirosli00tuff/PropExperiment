"""E.33 implementation B (Coder-B, LabelCoder2): labels, sampling, exclusions, weights and the
per-side simulated trade outcomes of protocol P3 (reports/stage_e32_discovery_protocol.md,
sha256 c4ffb9d7...), written from the protocol text alone in a vectorised style.

Input of one trade date: the ZM front's book updates (protocol 0.3: the book state after every
record that carries F_LAST, at the ts_recv of that record) as parallel arrays, plus the date's
context (P1.4 exclusion, release instants, limit prices, sigma_ZM). Every as-of lookup is a
``searchsorted(..., side="right") - 1`` on the ts_recv axis; executable prices are integer ticks
and the fee f = 0.528 is subtracted once (net = float(int tick difference) - f).

Readings (conservative choices where the protocol leaves a detail open) carry ``# READING LB-n``
and are logged in LabelCoder2_readings.md.

No I/O here: labB_book.py builds the update arrays, labB_cal.py the date context, build_labB.py
writes the INTERFACE.md 4.2 tables.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import numpy as np

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
MIN_NS = 60 * NS
L_NS = NS  # latency L = 1.000 s (selection variant; protocol 0.3)
FEE = 0.528  # ticks per round trip (protocol 0.3)
KAPPA = 1.0  # TB half-width multiplier (P3.4)
GRID_FIRST = time(8, 35)  # first decision minute (P1.3, 0.3)
GRID_LAST_PLUS_H = 277  # minute index of 13:12 counted from 08:35: G_h = {0..277 - h}
SPAN_END_LIMIT = time(13, 13)  # P3.6 rule 2
EXIT_DEADLINE = time(13, 20)  # P3.2: an exit with no valid update before 13:20:00 is marked
N_MINUTE_SLOTS = 300  # 1-minute intervals counted from 08:35 for the P3.7 weights

LABELS: dict[str, tuple[str, int]] = {
    "F05": ("FH", 5), "F15": ("FH", 15), "F30": ("FH", 30), "F60": ("FH", 60),
    "T15": ("TB", 15), "T30": ("TB", 30),
}

# s_flags bits (INTERFACE.md 4.2)
FL_ENTRY_FALLBACK = 1
FL_EXIT_FALLBACK = 2
FL_EXIT_LIMIT = 4
FL_EXIT_LAST_TOUCH = 8
FL_ENTRY_NOT_MADE = 16
FL_TB_NOT_MADE = 32

SIDES = ("long", "short")


def ct_ns(day: date, at: time) -> int:
    """UTC ns of wall-clock time ``at`` (America/Chicago, DST-aware) on calendar date ``day``."""
    stamp = datetime.combine(day, at, tzinfo=CT)
    return int(stamp.timestamp()) * NS + stamp.microsecond * 1000


# ------------------------------------------------------------------ inputs ----
@dataclass(frozen=True)
class Updates:
    """The ZM front's book updates of one trade date in ts_recv order (protocol 0.3).

    t: int64 ts_recv of the F_LAST record; bid/ask: int64 touch prices in ticks (0 when the side
    is empty); has_bid/has_ask: the side exists; bad: the book is marked bad (F_MAYBE_BAD_BOOK
    since the last R) or has not started (no R seen yet)."""

    t: np.ndarray
    bid: np.ndarray
    ask: np.ndarray
    has_bid: np.ndarray
    has_ask: np.ndarray
    bad: np.ndarray

    def __post_init__(self) -> None:
        n = len(self.t)
        for name in ("bid", "ask", "has_bid", "has_ask", "bad"):
            if len(getattr(self, name)) != n:
                raise ValueError(f"Updates.{name} length differs from t")
        if n > 1 and bool(np.any(np.diff(self.t) < 0)):
            raise ValueError("Updates.t must be non-decreasing (ts_recv order)")


@dataclass(frozen=True)
class DayContext:
    """What the label rules need about trade date ``day`` besides the book.

    excluded: P1.4 (roll date, date after a roll, early close, scheduled late open) or burn-in;
    releases_ns: the P3.6 rule 3 release instants R on ``day``; limits: (HL, LL) in ticks of the
    front's last definition with ts_recv <= 08:30 CT on ``day`` (None = rule 5 skip case);
    sigma_ticks: sigma_ZM(day) in ticks (None when undefined)."""

    day: date
    excluded: bool = False
    exclusion_reasons: tuple[str, ...] = ()
    releases_ns: tuple[int, ...] = ()
    limits: tuple[int, int] | None = None
    sigma_ticks: float | None = None
    notes: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Derived:
    """Validity arrays and fallback index helpers over one Updates (all vectorised)."""

    n: int
    ok_bid: np.ndarray  # bid exists and book not bad (an executable sell price)
    ok_ask: np.ndarray  # ask exists and book not bad (an executable buy price)
    both: np.ndarray  # both sides and not bad (P3.6 rule 5 row part, entry rule)
    mid_ok: np.ndarray  # both, not bad, bid < ask: M_ZM defined (0.3)
    s2: np.ndarray  # bid + ask in ticks = 2 x mid (int64; meaningful where mid_ok)
    not_both_cum: np.ndarray  # prefix count of updates failing ``both`` (length n + 1)
    next_ok_bid: np.ndarray  # smallest j >= k with ok_bid[j], n if none (length n + 1)
    next_ok_ask: np.ndarray
    prev_ok_bid: np.ndarray  # largest j <= k with ok_bid[j], -1 if none (length n)
    prev_ok_ask: np.ndarray


def _next_true(mask: np.ndarray) -> np.ndarray:
    n = len(mask)
    idx = np.where(mask, np.arange(n, dtype=np.int64), n)
    out = np.empty(n + 1, dtype=np.int64)
    out[n] = n
    if n:
        out[:n] = np.minimum.accumulate(idx[::-1])[::-1]
    return out


def _prev_true(mask: np.ndarray) -> np.ndarray:
    n = len(mask)
    idx = np.where(mask, np.arange(n, dtype=np.int64), -1)
    return np.maximum.accumulate(idx) if n else idx


def derive(u: Updates) -> Derived:
    n = len(u.t)
    good = ~u.bad.astype(bool)
    ok_bid = u.has_bid.astype(bool) & good
    ok_ask = u.has_ask.astype(bool) & good
    both = ok_bid & ok_ask
    bid = u.bid.astype(np.int64)
    ask = u.ask.astype(np.int64)
    mid_ok = both & (bid < ask)
    cum = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(~both, out=cum[1:])
    return Derived(n=n, ok_bid=ok_bid, ok_ask=ok_ask, both=both, mid_ok=mid_ok, s2=bid + ask,
                   not_both_cum=cum, next_ok_bid=_next_true(ok_bid),
                   next_ok_ask=_next_true(ok_ask), prev_ok_bid=_prev_true(ok_bid),
                   prev_ok_ask=_prev_true(ok_ask))


def asof(u: Updates, when: np.ndarray | int) -> np.ndarray | int:
    """Index of the last update with ts_recv <= when (-1 if none): "as of" (0.3).
    READING LB-1: updates are every F_LAST record; equal ts_recv keep record order."""
    return np.searchsorted(u.t, when, side="right") - 1


def grid(day: date, h: int) -> tuple[np.ndarray, np.ndarray]:
    """G_h(day): minute indices i = 0..277 - h and t_i = 08:35 CT + i minutes (UTC ns)."""
    i = np.arange(GRID_LAST_PLUS_H - h + 1, dtype=np.int64)
    return i, ct_ns(day, GRID_FIRST) + i * MIN_NS


# ------------------------------------------------------------------ barriers ----
def first_passage(u: Updates, d: Derived, lo: int, hi: int, s2_0: int,
                  half_width: float) -> tuple[int, int]:
    """P3.4 first touch over update indices [lo, hi): the first update with M_ZM defined and
    M >= m0 + b (direction +1) or M <= m0 - b (direction -1). Returns (index, direction), or
    (-1, 0) when neither barrier is reached. Works on 2 x mid integers: M - m0 = (s2 - s2_0)/2,
    so the test is (s2 - s2_0) >= 2b, exact on the integer side."""
    if hi <= lo:
        return -1, 0
    diff = d.s2[lo:hi] - s2_0
    ok = d.mid_ok[lo:hi]
    two_b = 2.0 * half_width
    up = ok & (diff >= two_b)
    dn = ok & (diff <= -two_b)
    if bool(np.any(up & dn)):
        raise AssertionError("one update reached both barriers (b must be > 0; P3.4)")
    hit = np.flatnonzero(up | dn)
    if not len(hit):
        return -1, 0
    j = int(hit[0])
    return lo + j, (1 if up[j] else -1)


def same_time_opposite_tie(u: Updates, d: Derived, lo: int, hi: int, s2_0: int,
                           half_width: float, j: int, direction: int) -> bool:
    """True when an update at the same ts_recv as the first touch (later in record order)
    touches the opposite barrier: tau_up == tau_dn as times. Counted only (READING LB-9)."""
    if j < 0:
        return False
    k = j + 1
    two_b = 2.0 * half_width
    while k < hi and u.t[k] == u.t[j]:
        if d.mid_ok[k]:
            diff = d.s2[k] - s2_0
            if (direction > 0 and diff <= -two_b) or (direction < 0 and diff >= two_b):
                return True
        k += 1
    return False


def tb_half_width(ctx: DayContext, h: int) -> float | None:
    """b = kappa x sigma_ZM(D) x sqrt(h) ticks (P3.4); None when sigma is undefined or not > 0."""
    s = ctx.sigma_ticks
    if s is None or not math.isfinite(s) or s <= 0.0:
        return None
    return KAPPA * float(s) * math.sqrt(h)


# ------------------------------------------------------------------ rules ----
def release_hit(t: np.ndarray, end: np.ndarray, releases_ns: tuple[int, ...]) -> np.ndarray:
    """P3.6 rule 3: span [t, end] intersects [R - 2 min, R + 30 min] for some R (closed
    intervals; a span touching a window edge counts as intersecting; READING LB-6)."""
    hit = np.zeros(len(t), dtype=bool)
    for r in releases_ns:
        hit |= (t <= r + 30 * MIN_NS) & (end >= r - 2 * MIN_NS)
    return hit


def near_limit(s2: np.ndarray, limits: tuple[int, int]) -> np.ndarray:
    """P3.6 rule 5 limit proximity: M >= HL - 0.02c or M <= LL + 0.02c, c = (HL + LL)/2.
    With M = s2/2: 100 M = 50 s2, 100 (HL - 0.01 (HL + LL)) = 99 HL - LL and
    100 (LL + 0.01 (HL + LL)) = 101 LL + HL, so the test is exact in integers (READING LB-19)."""
    hl, ll = int(limits[0]), int(limits[1])
    m100 = 50 * s2.astype(np.int64)
    return (m100 >= 99 * hl - ll) | (m100 <= 101 * ll + hl)


@dataclass
class RuleMasks:
    """Per-minute masks of the P3.6 / P3.7 rules (True = the rule removes the minute)."""

    burn_or_excluded: np.ndarray
    r1_open: np.ndarray
    r2_close: np.ndarray
    r3_release: np.ndarray
    book_t: np.ndarray  # book at t lacks a side or is marked bad (entry rule)
    mid_t: np.ndarray  # M_ZM(t) undefined (P3.7 row rule; entry by READING LB-3)
    r5_limit: np.ndarray
    tb_sigma: np.ndarray  # TB only: sigma_ZM(D) undefined (READING LB-8)
    span_row: np.ndarray  # rules 2-3 on the row's possible span beyond the entry span (LB-2)
    r5_row: np.ndarray  # a book update in the possible span lacks a side or is bad
    label_undef: np.ndarray  # TB only: M_ZM undefined at t + L (READING LB-7)


ENTRY_RULES = ("burn_or_excluded", "r1_open", "r2_close", "r3_release", "book_t", "mid_t",
               "r5_limit", "tb_sigma")
ROW_ONLY_RULES = ("span_row", "r5_row", "label_undef")
ROW_RULES = ENTRY_RULES + ROW_ONLY_RULES


def possible_span_end(t: np.ndarray, kind: str, h: int) -> np.ndarray:
    """End of the whole possible span: FH [t, t + L + h]; TB [t, t + h + 2L], the union of all
    realised spans [t, tau + L] with tau <= t + L + h (READING LB-2)."""
    end = t + L_NS + h * MIN_NS
    return end + L_NS if kind == "TB" else end


def rule_masks(u: Updates, d: Derived, ctx: DayContext, kind: str, h: int, t: np.ndarray,
               burn_in: bool) -> tuple[RuleMasks, np.ndarray]:
    """All rule masks for the grid ``t``; also returns k_t = as-of index of t."""
    n = len(t)
    day = ctx.day
    k_t = asof(u, t)
    have = k_t >= 0
    kk = np.where(have, k_t, 0)
    both_t = have & d.both[kk] if d.n else np.zeros(n, dtype=bool)
    mid_t = have & d.mid_ok[kk] if d.n else np.zeros(n, dtype=bool)
    entry_end = t + L_NS + h * MIN_NS  # the entry rules' possible span (P3.6 first paragraph)
    row_end = possible_span_end(t, kind, h)
    open_ns = ct_ns(day, GRID_FIRST)
    close_ns = ct_ns(day, SPAN_END_LIMIT)
    r5_limit = np.zeros(n, dtype=bool)
    if ctx.limits is not None and d.n:
        # READING LB-3: where M_ZM(t) is undefined the limit test cannot pass; such minutes are
        # already removed by mid_t, so r5_limit is evaluated only where M_ZM(t) is defined.
        r5_limit = mid_t & near_limit(d.s2[kk], ctx.limits)
    tb_sigma = np.full(n, kind == "TB" and tb_half_width(ctx, h) is None)
    if d.n:  # READING LB-17: updates with ts_recv in the closed [t, possible span end]
        lo = np.searchsorted(u.t, t, side="left")
        hi = np.searchsorted(u.t, row_end, side="right")
        r5_row = (d.not_both_cum[hi] - d.not_both_cum[lo]) > 0
    else:
        r5_row = np.ones(n, dtype=bool)
    r3_entry = release_hit(t, entry_end, ctx.releases_ns)
    label_undef = np.zeros(n, dtype=bool)
    if kind == "TB" and d.n:
        k1 = asof(u, t + L_NS)
        label_undef = ~((k1 >= 0) & d.mid_ok[np.where(k1 >= 0, k1, 0)])
    masks = RuleMasks(
        burn_or_excluded=np.full(n, bool(burn_in or ctx.excluded)),
        r1_open=t < open_ns,
        r2_close=entry_end > close_ns,
        r3_release=r3_entry,
        book_t=~both_t,
        mid_t=~mid_t,
        r5_limit=r5_limit,
        tb_sigma=tb_sigma,
        span_row=((row_end > close_ns) | release_hit(t, row_end, ctx.releases_ns))
        & ~((entry_end > close_ns) | r3_entry),
        r5_row=r5_row,
        label_undef=label_undef,
    )
    return masks, k_t


def combine(masks: RuleMasks, names: tuple[str, ...]) -> np.ndarray:
    out = np.zeros(len(masks.r1_open), dtype=bool)
    for name in names:
        out |= getattr(masks, name)
    return out


# ------------------------------------------------------------------ labels ----
def net_long(exit_bid: np.ndarray | int, entry_ask: np.ndarray | int) -> np.ndarray | float:
    """Ticks net of f: integer price difference first, the fee subtracted once."""
    return (np.asarray(exit_bid, dtype=np.int64) - np.asarray(entry_ask, dtype=np.int64)
            ).astype(np.float64) - FEE


def net_short(entry_bid: np.ndarray | int, exit_ask: np.ndarray | int) -> np.ndarray | float:
    return (np.asarray(entry_bid, dtype=np.int64) - np.asarray(exit_ask, dtype=np.int64)
            ).astype(np.float64) - FEE


def fh_labels(u: Updates, t: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                                          np.ndarray]:
    """P3.3 for every t (meaningful only on rows): N_long, N_short, y, span end."""
    k1 = asof(u, t + L_NS)
    k2 = asof(u, t + h * MIN_NS + L_NS)
    k1c, k2c = np.maximum(k1, 0), np.maximum(k2, 0)
    n_l = net_long(u.bid[k2c], u.ask[k1c])
    n_s = net_short(u.bid[k1c], u.ask[k2c])
    y = np.where(n_l > 0, 1, np.where(n_s > 0, -1, 0)).astype(np.int8)
    return n_l, n_s, y, t + L_NS + h * MIN_NS


@dataclass
class TbCounts:
    same_time_ties: int = 0  # counts of ties only; no class counts (INTERFACE.md 2 rule 1)


def tb_label_row(u: Updates, d: Derived, t: int, h: int, half_width: float
                 ) -> tuple[float, float, int, int, bool]:
    """P3.4 for one row (M_ZM(t + L) defined): N_long^TB, N_short^TB, y, tau + L, tie flag."""
    k1 = int(asof(u, t + L_NS))
    kend = int(asof(u, t + L_NS + h * MIN_NS))
    s2_0 = int(d.s2[k1])
    j, direction = first_passage(u, d, k1 + 1, kend + 1, s2_0, half_width)
    tie = same_time_opposite_tie(u, d, k1 + 1, kend + 1, s2_0, half_width, j, direction)
    tau = int(u.t[j]) if j >= 0 else t + L_NS + h * MIN_NS
    kx = int(asof(u, tau + L_NS))
    n_l = float(net_long(u.bid[kx], u.ask[k1]))
    n_s = float(net_short(u.bid[k1], u.ask[kx]))
    return n_l, n_s, direction, tau + L_NS, tie


# ------------------------------------------------------------------ weights ----
def intervals_covered(t: np.ndarray, span_end: np.ndarray) -> np.ndarray:
    """P3.7: number of 1-minute intervals [t + k min, t + (k+1) min) that the span [t, end]
    intersects by more than one second; t lies on a minute mark, so it is the count of k >= 0
    with k x 60 s < (end - t) - 1 s, i.e. ceil(((end - t) - 1 s) / 60 s)."""
    x = (span_end - t) - NS
    if bool(np.any(x <= 0)):
        raise AssertionError("a span shorter than one second has no interval")
    return (x + MIN_NS - 1) // MIN_NS


def uniqueness_weights(i: np.ndarray, n_int: np.ndarray) -> np.ndarray:
    """P3.7 average uniqueness: c_m = rows whose span covers interval m (interval counting by a
    difference array); u_i = mean of 1/c_m over the row's intervals (math.fsum, then / n).
    READING LB-18: clock-minute intervals from 08:35, "> 1 s" strict, row_ok rows only."""
    diff = np.zeros(N_MINUTE_SLOTS + 1, dtype=np.int64)
    np.add.at(diff, i, 1)
    np.add.at(diff, i + n_int, -1)
    c = np.cumsum(diff)[:N_MINUTE_SLOTS]
    inv = np.zeros(N_MINUTE_SLOTS, dtype=np.float64)
    pos = c > 0
    inv[pos] = 1.0 / c[pos].astype(np.float64)
    out = np.empty(len(i), dtype=np.float64)
    for r, (a, m) in enumerate(zip(i.tolist(), n_int.tolist(), strict=True)):
        out[r] = math.fsum(inv[a:a + m].tolist()) / m
    return out


# ------------------------------------------------------------------ simulation ----
@dataclass(frozen=True)
class Fill:
    made: bool
    net: float
    entry_ns: int
    exit_ns: int
    flags: int


NOT_MADE_FIELDS = (False, math.nan, -1, -1)


def simulate(u: Updates, d: Derived, ctx: DayContext, kind: str, h: int, t: int, side: str,
             half_width: float | None) -> Fill:
    """P3.2 executable fills with the fallback, P3.3 / P3.4 exits, for one side at an entry
    minute t. Market buy fills at ask_1 as of u + L, market sell at bid_1 as of u + L."""
    is_long = side == "long"
    flags = 0
    exit_deadline = ct_ns(ctx.day, EXIT_DEADLINE)
    # READING LB-4: the planned exit time is the exit decision time: t + h for FH (P3.8 "FH at
    # t + h"), the vertical barrier t + L + h for TB (the latest possible tau); an entry
    # fallback fill must come strictly before it.
    planned_exit = t + h * MIN_NS if kind == "FH" else t + L_NS + h * MIN_NS
    entry_ok_arr = d.ok_ask if is_long else d.ok_bid
    entry_next = d.next_ok_ask if is_long else d.next_ok_bid
    k1 = int(asof(u, t + L_NS))
    if k1 >= 0 and entry_ok_arr[k1]:
        je, entry_ns = k1, t + L_NS  # READING LB-5: a normal fill is timed at u + L
    else:
        flags |= FL_ENTRY_FALLBACK  # READING LB-10: bit 1 = the fallback rule was invoked
        j = int(entry_next[k1 + 1])
        if j < d.n and int(u.t[j]) < planned_exit:
            je, entry_ns = j, int(u.t[j])
        else:
            return Fill(*NOT_MADE_FIELDS, flags | FL_ENTRY_NOT_MADE)
    entry_px = int(u.ask[je]) if is_long else int(u.bid[je])
    if kind == "TB":
        if not d.mid_ok[je]:
            return Fill(*NOT_MADE_FIELDS, flags | FL_TB_NOT_MADE)
        if half_width is None:
            raise AssertionError("TB simulation needs sigma_ZM(D) (entry rule LB-8)")
        kend = int(asof(u, t + L_NS + h * MIN_NS))
        j, _direction = first_passage(u, d, je + 1, kend + 1, int(d.s2[je]), half_width)
        exit_decision = int(u.t[j]) if j >= 0 else t + L_NS + h * MIN_NS
    else:
        exit_decision = t + h * MIN_NS
    exit_ok_arr = d.ok_bid if is_long else d.ok_ask
    exit_next = d.next_ok_bid if is_long else d.next_ok_ask
    exit_prev = d.prev_ok_bid if is_long else d.prev_ok_ask
    exit_px_arr = u.bid if is_long else u.ask
    ux = exit_decision + L_NS
    kx = int(asof(u, ux))
    if kx >= 0 and exit_ok_arr[kx]:
        exit_px, exit_ns = int(exit_px_arr[kx]), ux
    else:
        flags |= FL_EXIT_FALLBACK
        j = int(exit_next[kx + 1])
        if j < d.n and int(u.t[j]) < exit_deadline:
            exit_px, exit_ns = int(exit_px_arr[j]), int(u.t[j])
        elif ctx.limits is not None:
            # the low limit for a long's exit, the high limit for a short's exit (P3.2)
            exit_px = int(ctx.limits[1]) if is_long else int(ctx.limits[0])
            exit_ns = exit_deadline  # READING LB-11: a marked exit is timed at 13:20:00
            flags |= FL_EXIT_LIMIT
        else:
            jp = int(exit_prev[kx]) if kx >= 0 else -1
            if jp < 0:
                raise AssertionError("no valid touch on the exit side before the exit")
            exit_px, exit_ns = int(exit_px_arr[jp]), exit_deadline
            flags |= FL_EXIT_LAST_TOUCH
    net = float(net_long(exit_px, entry_px)) if is_long else float(net_short(entry_px, exit_px))
    return Fill(True, net, entry_ns, exit_ns, flags)


# ------------------------------------------------------------------ the table ----
def empty_sim(n: int) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for s in SIDES:
        out[f"{s}_made"] = np.zeros(n, dtype=bool)
        out[f"{s}_net"] = np.full(n, np.nan)
        out[f"{s}_entry_ns"] = np.full(n, -1, dtype=np.int64)
        out[f"{s}_exit_ns"] = np.full(n, -1, dtype=np.int64)
        out[f"{s}_flags"] = np.zeros(n, dtype=np.int16)
    return out


COLUMNS = ("i", "t_ns", "entry_ok", "row_ok", "y", "n_long", "n_short", "w", "span_end_ns",
           "long_made", "long_net", "long_entry_ns", "long_exit_ns", "long_flags",
           "short_made", "short_net", "short_entry_ns", "short_exit_ns", "short_flags")


def label_table(u: Updates, ctx: DayContext, label: str, burn_in: bool = False
                ) -> tuple[dict[str, np.ndarray], dict]:
    """The INTERFACE.md 4.2 columns for one (label, date) and the date's exclusion counts."""
    kind, h = LABELS[label]
    d = derive(u)
    i, t = grid(ctx.day, h)
    n = len(t)
    masks, _k_t = rule_masks(u, d, ctx, kind, h, t, burn_in)
    entry_ok = ~combine(masks, ENTRY_RULES)
    row_ok = entry_ok & ~combine(masks, ROW_ONLY_RULES)
    half_width = tb_half_width(ctx, h) if kind == "TB" else None

    y = np.zeros(n, dtype=np.int8)
    n_l = np.full(n, np.nan)
    n_s = np.full(n, np.nan)
    span_end = np.full(n, -1, dtype=np.int64)
    tb = TbCounts()
    rows = np.flatnonzero(row_ok)
    if kind == "FH":
        a, b, yy, end = fh_labels(u, t, h)
        if bool(np.any((a[rows] > 0) & (b[rows] > 0))):
            raise AssertionError("N_long and N_short both positive on a row (P3.3: impossible)")
        n_l[rows], n_s[rows], y[rows], span_end[rows] = a[rows], b[rows], yy[rows], end[rows]
    else:
        for r in rows.tolist():
            a, b, yy, end, tie = tb_label_row(u, d, int(t[r]), h, float(half_width))
            n_l[r], n_s[r], y[r], span_end[r] = a, b, yy, end
            tb.same_time_ties += bool(tie)
    w = np.full(n, np.nan)
    if len(rows):
        n_int = intervals_covered(t[rows], span_end[rows])
        w[rows] = uniqueness_weights(i[rows], n_int)

    sim = empty_sim(n)
    for r in np.flatnonzero(entry_ok).tolist():
        for s in SIDES:
            f = simulate(u, d, ctx, kind, h, int(t[r]), s, half_width)
            sim[f"{s}_made"][r] = f.made
            sim[f"{s}_net"][r] = f.net
            sim[f"{s}_entry_ns"][r] = f.entry_ns
            sim[f"{s}_exit_ns"][r] = f.exit_ns
            sim[f"{s}_flags"][r] = f.flags
    check_invariant(row_ok, n_l, n_s, sim)

    cols = {"i": i.astype(np.int16), "t_ns": t.astype(np.int64), "entry_ok": entry_ok,
            "row_ok": row_ok, "y": y, "n_long": n_l, "n_short": n_s, "w": w,
            "span_end_ns": span_end, **sim}
    return {c: cols[c] for c in COLUMNS}, exclusion_counts(masks, entry_ok, row_ok, sim, ctx,
                                                           label, burn_in, tb)


def check_invariant(row_ok: np.ndarray, n_l: np.ndarray, n_s: np.ndarray,
                    sim: dict[str, np.ndarray]) -> None:
    """INTERFACE.md 4.2: where row_ok and no fallback fired, s_net equals n_s exactly."""
    for s, lab in (("long", n_l), ("short", n_s)):
        clean = row_ok & sim[f"{s}_made"] & (sim[f"{s}_flags"] == 0)
        if bool(np.any(sim[f"{s}_net"][clean] != lab[clean])):
            raise AssertionError(f"{s}: simulated net differs from the label on a clean row")
        bad = row_ok & ~sim[f"{s}_made"] & (sim[f"{s}_flags"] == 0)
        if bool(np.any(bad)):
            raise AssertionError(f"{s}: a row whose entry was not made carries no flag")


def exclusion_counts(masks: RuleMasks, entry_ok: np.ndarray, row_ok: np.ndarray,
                     sim: dict[str, np.ndarray], ctx: DayContext, label: str, burn_in: bool,
                     tb: TbCounts) -> dict:
    """Counts only (INTERFACE.md 2 rule 1): minutes and rows each rule removes, both
    non-exclusive (every rule that fails) and first-failing-rule attribution in ROW_RULES
    order; fallback, not-made and mark counts of the simulation."""
    n = len(row_ok)
    any_rule = {name: int(np.count_nonzero(getattr(masks, name))) for name in ROW_RULES}
    first: dict[str, int] = {}
    left = np.ones(n, dtype=bool)
    for name in ROW_RULES:
        hit = left & getattr(masks, name)
        first[name] = int(np.count_nonzero(hit))
        left &= ~hit
    sim_counts = {}
    for s in SIDES:
        fl = sim[f"{s}_flags"].astype(np.int64)
        sim_counts[s] = {
            "made": int(np.count_nonzero(sim[f"{s}_made"])),
            "entry_fallback": int(np.count_nonzero(fl & FL_ENTRY_FALLBACK)),
            "exit_fallback": int(np.count_nonzero(fl & FL_EXIT_FALLBACK)),
            "exit_limit_mark": int(np.count_nonzero(fl & FL_EXIT_LIMIT)),
            "exit_last_touch_mark": int(np.count_nonzero(fl & FL_EXIT_LAST_TOUCH)),
            "entry_not_made": int(np.count_nonzero(fl & FL_ENTRY_NOT_MADE)),
            "tb_entry_not_made": int(np.count_nonzero(fl & FL_TB_NOT_MADE)),
        }
    return {
        "date": ctx.day.isoformat(), "label": label, "grid_minutes": n,
        "burn_in": bool(burn_in), "excluded_date": bool(ctx.excluded),
        "exclusion_reasons": list(ctx.exclusion_reasons),
        "limits_present": ctx.limits is not None,
        "n_releases_on_date": len(ctx.releases_ns),
        "entry_minutes": int(np.count_nonzero(entry_ok)),
        "rows": int(np.count_nonzero(row_ok)),
        "removed_any_rule": any_rule,
        "removed_first_rule": first,
        "entry_rules": list(ENTRY_RULES), "row_rules": list(ROW_RULES),
        "tb_same_time_ties": tb.same_time_ties,
        "sim": sim_counts,
    }
