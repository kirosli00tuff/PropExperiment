"""Implementation B: the per-date raw quantities ("day raw") that the features and the trailing
references of later dates read. One replay per date (replayB), then vectorised windows.

Prices are kept as exact integers: mid2 = bid_1 + ask_1 in 1e-9 price units (twice the mid), so
mid differences are exact until the final division (G7 agreement). Invalid mids are flagged by a
separate boolean (P0.3 validity: both sides, bid_1 < ask_1, not marked bad).

Grid: the 279 wall-clock minute marks g_i = 08:35 + i min, i = 0..278 (08:35..13:13) of D; the
features use i = 0..272 (G_5), the trailing references use all 279 (P0.3).
Windows: P0.3 "the last k minutes of time during which X was open, ending at t" on the open-time
axis of calB.OpenAxis; sums cover records with ts_recv in open time and open-axis position in
(P(t) - k min, P(t)] (READING B-WIN-1).
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import calB  # noqa: E402
import data33  # noqa: E402
import measure31 as m31  # noqa: E402
import mbo_book31 as mb  # noqa: E402
import replayB as rb  # noqa: E402

NS, MIN_NS = calB.NS, calB.MIN_NS
N_GRID = 279  # 08:35..13:13
LOOKBACK = 120  # F1.2 needs C(t - j min), j = 1..120
LAM_N = 60  # F3.12: the 60 one-minute intervals ending at t
OFI_K_ZM = (1, 5, 15)
OFI_K_X = (1, 5)


# ------------------------------------------------------------------ helpers ----
def mid2_asof(book: rb.BookArrays, u: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """P0.3 "as of u": the last book update with ts_recv <= u. Returns (mid2, valid, index)."""
    k = np.searchsorted(book.ts, np.asarray(u, np.int64), side="right") - 1
    kk = np.clip(k, 0, None)
    ok = (k >= 0) & (book.valid[kk] if len(book.ts) else np.zeros(len(k), bool))
    if not len(book.ts):
        return np.zeros(len(k), np.int64), ok, k
    m2 = np.where(ok, book.bpx[kk, 0] + book.apx[kk, 0], 0)
    return m2.astype(np.int64), ok, k


def ofi_terms(book: rb.BookArrays, m: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """F2.8 e_n (Cont, Kukanov and Stoikov 2014) on level m+1 between consecutive book updates
    n-1, n, and whether it can be computed (lead ruling FD3 (b), (c)): both states have level m+1
    on both sides and are not marked bad (started); crossed or locked two-sided states use the
    literal formula. Update 0 has no predecessor (ok False; it is excluded by FD3 (a) anyway)."""
    n = len(book.ts)
    e = np.zeros(n, np.int64)
    ok = np.zeros(n, bool)
    if n < 2:
        return e, ok
    pb, pa, qb, qa = book.bpx[:, m], book.apx[:, m], book.bq[:, m], book.aq[:, m]
    have = book.notbad & (pb != rb.NOPX) & (pa != rb.NOPX)
    ok[1:] = have[1:] & have[:-1]
    e1 = ((pb[1:] >= pb[:-1]) * qb[1:] - (pb[1:] <= pb[:-1]) * qb[:-1]
          - (pa[1:] <= pa[:-1]) * qa[1:] + (pa[1:] >= pa[:-1]) * qa[:-1])
    e[1:] = np.where(ok[1:], e1, 0)
    return e, ok


def ofi_included(axis: calB.OpenAxis, ts: np.ndarray) -> np.ndarray:
    """Lead ruling FD3 (a): an update's term enters window sums only if the update lies in open
    time and its predecessor lies in the same open interval; the first update after a skipped
    interval (pause, close, halt) and the stream's first update never enter any sum."""
    ts = np.asarray(ts, np.int64)
    n = len(ts)
    if n == 0:
        return np.zeros(0, bool)
    is_open = axis.is_open(ts)
    k = np.searchsorted(axis.lo, ts, side="right") - 1
    first = np.ones(n, bool)
    first[1:] = ~is_open[:-1] | (k[1:] != k[:-1])
    return is_open & ~first


class OfiWindows:
    """OFI sums over (P(t) - k min, P(t)] (B-WIN-1) of the included terms (FD3 (a)), and their
    validity: a window holding an included term that cannot be computed is invalid (FD3 (b))."""

    def __init__(self, axis: calB.OpenAxis, book: rb.BookArrays, levels: int) -> None:
        inc = ofi_included(axis, book.ts)
        vals = []
        for m in range(levels):
            e, ok = ofi_terms(book, m)
            vals.append(np.where(inc, e, 0))
            vals.append((inc & ~ok).astype(np.int64))
        self.w = Windows(axis, book.ts, *vals)

    def at(self, end_pos: np.ndarray, k_min: int, m: int = 0) -> tuple[np.ndarray, np.ndarray]:
        return self.w.at(end_pos, k_min, 2 * m), self.w.at(end_pos, k_min, 2 * m + 1) == 0


class Windows:
    """Sums over the open-time window (P(t) - k min, P(t)] of values attached to instants."""

    def __init__(self, axis: calB.OpenAxis, ts: np.ndarray, *vals: np.ndarray) -> None:
        ts = np.asarray(ts, np.int64)
        keep = axis.is_open(ts) if len(ts) else np.zeros(0, bool)
        self.pos = axis.pos(ts[keep]) if len(ts) else np.zeros(0, np.int64)
        self.cum = [np.concatenate([[0], np.cumsum(np.asarray(v)[keep])]) for v in vals]

    def at(self, end_pos: np.ndarray, k_min: int, which: int = 0) -> np.ndarray:
        hi = np.searchsorted(self.pos, end_pos, side="right")
        lo = np.searchsorted(self.pos, end_pos - k_min * MIN_NS, side="right")
        c = self.cum[which]
        return c[hi] - c[lo]


# ------------------------------------------------------------------ inputs ----
_TICKS: dict = {}


def ticks(cutoff_ns: int | None) -> dict[str, int]:
    """P0.3: tick sizes from the definitions (measure31.definition_rows / checked_tick),
    cached per cutoff within a process."""
    if cutoff_ns not in _TICKS:
        defs = m31.definition_rows(data33.definitions(cutoff_ns, outright_only=True))
        _TICKS[cutoff_ns] = {r: int(m31.checked_tick(defs, r)) for r in ("ZM", "ZS", "ZL")}
    return dict(_TICKS[cutoff_ns])


def zm_expiration(front: int | None, d: date, cutoff_ns: int | None) -> int | None:
    """C.7: expiration of the ZM front from its last definition record with ts_recv <= 08:30 CT
    on D (and <= the cutoff)."""
    if front is None:
        return None
    defs = data33.definitions(cutoff_ns, outright_only=True)
    lim = calB.ct(d, 8, 30)
    sel = defs[(defs["instrument_id"] == front) & (defs["ts_recv"] <= lim)]
    if not len(sel):
        return None
    exp = int(sel["expiration"][-1])
    return None if exp >= (1 << 63) else exp


def load_stream(root: str, days: list[date], iid: int | None,
                cutoff_ns: int | None) -> np.ndarray | None:
    if iid is None:
        return None
    parts = []
    for d in days:
        arr = data33.load_zm(d, cutoff_ns) if root == "ZM" else data33.load_mbp1(root, d,
                                                                                 cutoff_ns)
        parts.append(arr[arr["instrument_id"] == iid])
    return np.concatenate(parts) if len(parts) > 1 else parts[0]


def stream_days(d: date) -> tuple[list[date], calB.OpenAxis]:
    """The open-time axis covers the previous trade date and D; the records are D's, plus the
    previous trade date's when the 120-minute look-back from 08:35 reaches before D's ts_recv
    window (scheduled late opens; READING B-LATE-1)."""
    prev = calB.prev_trade_date(d)
    have_prev = prev is not None and prev >= calB.FIRST
    axis = calB.OpenAxis.of([prev, d] if have_prev else [d])
    need = int(axis.pos(np.array([calB.ct(d, 8, 35)]))[0]) - LOOKBACK * MIN_NS
    wall, pos, _ = axis.marks()
    k = int(np.searchsorted(pos, need))
    first = int(wall[min(k, len(wall) - 1)]) if need >= 0 else int(wall[0])
    if have_prev and first < data33.window(d)[0]:
        return [prev, d], axis
    return [d], axis


# ------------------------------------------------------------------ the day ----
def day_raw(d: date, cutoff_ns: int | None = None, tk: dict[str, int] | None = None) -> dict:
    tk = tk or ticks(cutoff_ns)
    fz, fs, fl = calB.fronts(d)
    days, axis = stream_days(d)
    start_ns = data33.window(days[0])[0]
    g = calB.grid_ns(d, N_GRID)
    zm_rec = load_stream("ZM", days, fz, cutoff_ns)
    zs_rec = load_stream("ZS", days, fs, cutoff_ns)
    zl_rec = load_stream("ZL", days, fl, cutoff_ns)
    zm = rb.replay_zm(zm_rec, g) if zm_rec is not None else None
    zs = rb.mbp_arrays(zs_rec) if zs_rec is not None else None
    zl = rb.mbp_arrays(zl_rec) if zl_rec is not None else None
    return compute_day(d, axis, start_ns, g, zm, zs, zl, tk, (fz, fs, fl), cutoff_ns)


def _mids(arr, u: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if arr is None:
        return np.zeros(len(u), np.int64), np.zeros(len(u), bool)
    m2, ok, _ = mid2_asof(arr.book, u)
    return m2, ok


def compute_day(d: date, axis: calB.OpenAxis, start_ns: int, g: np.ndarray, zm, zs, zl,
                tk: dict[str, int], fr: tuple, cutoff_ns: int | None) -> dict:
    """Everything of D that needs the records; pure numpy from here (unit-testable)."""
    out: dict = {"date": d.isoformat(), "fronts": np.array([-1 if x is None else x for x in fr]),
                 "ticks": np.array([tk["ZM"], tk["ZS"], tk["ZL"]], np.int64), "grid": g}
    # marks of the open-time axis from the stream start (P0.3 sample points)
    wall, pos, kint = axis.marks()
    keep = wall >= start_ns
    wall, pos = wall[keep], pos[keep]
    mday = np.array([axis.day[k].toordinal() for k in kint[keep]], np.int64)
    out.update(mark_wall=wall, mark_pos=pos, mark_day=mday)
    pg = axis.pos(g)
    out["grid_pos"] = pg
    for name, arr in (("zm", zm), ("zs", zs), ("zl", zl)):
        m2, ok = _mids(arr, wall)
        out[f"mark_{name}"], out[f"mark_{name}_ok"] = m2, ok
        m2, ok = _mids(arr, g)
        out[f"g_{name}"], out[f"g_{name}_ok"] = m2, ok
    for name, hh, mm in (("0830", 8, 30), ("0835", 8, 35), ("1315", 13, 15)):
        u = np.array([calB.ct(d, hh, mm)])
        for inst, arr in (("zm", zm), ("zs", zs), ("zl", zl)):
            m2, ok = _mids(arr, u)
            out[f"{inst}{name}"], out[f"{inst}{name}_ok"] = int(m2[0]), bool(ok[0])
    _zm_grid(out, axis, g, pg, zm)
    for name, arr in (("zs", zs), ("zl", zl)):
        _mbp_grid(out, name, axis, pg, arr)
    _lam60(out, axis, g, pg, zm, tk["ZM"])
    _range(out, d, g, zm)
    out["expiration"] = zm_expiration(fr[0], d, cutoff_ns) or -1
    out["release_clear"] = calB.release_clear_mask(d, g)
    return out


def _zm_grid(out: dict, axis: calB.OpenAxis, g: np.ndarray, pg: np.ndarray, zm) -> None:
    n = len(g)
    if zm is None:
        out["g_zm_state_ok"] = np.zeros(n, bool)
        for key in ("g_bq", "g_aq"):
            out[key] = np.zeros((n, rb.LEVELS), np.int64)
        out["g_bpx1"] = out["g_apx1"] = np.zeros(n, np.int64)
        for key in ("v15_zm", "b5", "s5", "b15", "s15", "ca5", "cb5", "swb5", "sws5", "rfb15",
                    "rfa15", *[f"ofi_zm_{k}" for k in OFI_K_ZM], *[f"iofi5_{m}" for m in
                                                                 range(1, 6)]):
            out[key] = np.zeros(n, np.int64)
        for key in [f"ofi_zm_{k}" for k in OFI_K_ZM] + [f"iofi5_{m}" for m in range(1, 6)]:
            out[f"{key}_ok"] = np.zeros(n, bool)
        out["seas_q"] = np.zeros((n, 2, rb.SEASON_LEVELS), np.int64)
        out["seas_ok"] = np.zeros(n, bool)
        return
    bk = zm.book
    _, ok, k = mid2_asof(bk, g)
    kk = np.clip(k, 0, None)
    out["g_zm_state_ok"] = ok
    out["g_bq"] = np.where(ok[:, None], bk.bq[kk], 0)
    out["g_aq"] = np.where(ok[:, None], bk.aq[kk], 0)
    out["g_bpx1"] = np.where(ok, bk.bpx[kk, 0], 0)
    out["g_apx1"] = np.where(ok, bk.apx[kk, 0], 0)
    # C.5 / F1.5 volume: every T record (all aggressor sides); F3.5-F3.6: sides B and A only
    side = zm.trade_side
    buy = np.where(side == mb.SIDE_BID_CODE, zm.trade_sz, 0)
    sell = np.where(side == mb.SIDE_ASK_CODE, zm.trade_sz, 0)
    tw = Windows(axis, zm.trade_ts, zm.trade_sz, buy, sell)
    out["v15_zm"] = tw.at(pg, 15, 0)
    out["b5"], out["s5"] = tw.at(pg, 5, 1), tw.at(pg, 5, 2)
    out["b15"], out["s15"] = tw.at(pg, 15, 1), tw.at(pg, 15, 2)
    ow = OfiWindows(axis, bk, rb.LEVELS)
    for k in OFI_K_ZM:
        out[f"ofi_zm_{k}"], out[f"ofi_zm_{k}_ok"] = ow.at(pg, k, 0)
    for m in range(1, rb.LEVELS + 1):
        out[f"iofi5_{m}"], out[f"iofi5_{m}_ok"] = ow.at(pg, 5, m - 1)
    ca = np.where(zm.rem_side == 1, zm.rem_qty, 0)
    cb = np.where(zm.rem_side == 0, zm.rem_qty, 0)
    rw = Windows(axis, zm.rem_ts, ca, cb)
    out["ca5"], out["cb5"] = rw.at(pg, 5, 0), rw.at(pg, 5, 1)
    sw = Windows(axis, zm.sweep_ts, (zm.sweep_dir == 1).astype(np.int64),
                 (zm.sweep_dir == -1).astype(np.int64))
    out["swb5"], out["sws5"] = sw.at(pg, 5, 0), sw.at(pg, 5, 1)
    fw = Windows(axis, zm.refill_ts, (zm.refill_side == 0).astype(np.int64),
                 (zm.refill_side == 1).astype(np.int64))
    out["rfb15"], out["rfa15"] = fw.at(pg, 15, 0), fw.at(pg, 15, 1)
    out["seas_q"], out["seas_ok"] = zm.season_q, zm.season_ok


def _mbp_grid(out: dict, name: str, axis: calB.OpenAxis, pg: np.ndarray, arr) -> None:
    if arr is None:
        out[f"v15_{name}"] = np.zeros(len(pg), np.int64)
        out[f"{name}_present"] = False
        for k in OFI_K_X:
            out[f"ofi_{name}_{k}"] = np.zeros(len(pg), np.int64)
            out[f"ofi_{name}_{k}_ok"] = np.zeros(len(pg), bool)
        return
    out[f"{name}_present"] = True
    out[f"v15_{name}"] = Windows(axis, arr.trade_ts, arr.trade_sz).at(pg, 15)
    ow = OfiWindows(axis, arr.book, 1)
    for k in OFI_K_X:
        out[f"ofi_{name}_{k}"], out[f"ofi_{name}_{k}_ok"] = ow.at(pg, k, 0)


def mark_lookup(out: dict, inst: str, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """mid2 and validity at the open-axis mark with each position (invalid when no mark)."""
    mp = out["mark_pos"]
    idx = np.searchsorted(mp, positions)
    idc = np.clip(idx, 0, max(len(mp) - 1, 0))
    found = (idx < len(mp)) & (mp[idc] == positions) if len(mp) else np.zeros(
        positions.shape, bool)
    m2 = np.where(found, out[f"mark_{inst}"][idc], 0)
    ok = found & out[f"mark_{inst}_ok"][idc]
    return m2, ok


def sample(out: dict, inst: str, jmax: int) -> tuple[np.ndarray, np.ndarray]:
    """[n_grid, jmax+1]: column 0 = the value as of the wall time t itself, column j = the mark
    at open-axis position P(t) - j min (P0.3 sample points)."""
    pg = out["grid_pos"]
    j = np.arange(jmax + 1, dtype=np.int64)
    m2, ok = mark_lookup(out, inst, pg[:, None] - j[None, :] * MIN_NS)
    m2[:, 0] = out[f"g_{inst}"]
    ok[:, 0] = out[f"g_{inst}_ok"]
    return m2, ok


def _lam60(out: dict, axis: calB.OpenAxis, g: np.ndarray, pg: np.ndarray, zm,
           tick_zm: int) -> None:
    """F3.12 slope at each grid mark: OLS (lstsq, centred regressor, intercept; P0.3) of dM_ZM
    in ticks on B - S over the intervals among the 60 ending at t that contain a T record
    (READING B-LAM-1), with valid mids at both ends (READING B-LAM-2); NaN if fewer than 30."""
    n = len(g)
    slope = np.full(n, np.nan)
    if zm is None:
        out["lam60"] = slope
        return
    side = zm.trade_side
    buy = np.where(side == mb.SIDE_BID_CODE, zm.trade_sz, 0)
    sell = np.where(side == mb.SIDE_ASK_CODE, zm.trade_sz, 0)
    tw = Windows(axis, zm.trade_ts, np.ones(len(zm.trade_ts), np.int64), buy - sell)
    m2, ok = sample(out, "zm", LAM_N)
    for i in range(n):
        ends = pg[i] - np.arange(LAM_N, dtype=np.int64) * MIN_NS  # interval j = 1..60
        cnt = tw.at(ends, 1, 0)
        x = tw.at(ends, 1, 1).astype(np.float64)
        dm = (m2[i, :-1] - m2[i, 1:]).astype(np.float64) / (2.0 * tick_zm)
        use = (cnt > 0) & ok[i, :-1] & ok[i, 1:]
        if use.sum() < 30:
            continue
        xs, ys = x[use], dm[use]
        design = np.column_stack([np.ones(len(xs)), xs - xs.mean()])
        coef, _, rank, _ = np.linalg.lstsq(design, ys, rcond=None)
        if rank < 2:
            continue
        slope[i] = coef[1]
    out["lam60"] = slope


def _range(out: dict, d: date, g: np.ndarray, zm) -> None:
    """F4.6: Hi and Lo of M_ZM over [08:30, t] on D: the value as of 08:30:00 and, for each
    distinct ts_recv in (08:30, t], the state after the LAST book update with that ts_recv, if
    valid (READING B-RP-1, lead ruling R-L11). mid2 units; ok flags."""
    n = len(g)
    hi = np.zeros(n, np.int64)
    lo = np.zeros(n, np.int64)
    ok = np.zeros(n, bool)
    if zm is not None:
        bk = zm.book
        t0 = calB.ct(d, 8, 30)
        sel = (bk.ts > t0) & (bk.ts <= g[-1])
        ts = bk.ts[sel]
        # READING R-L11 (lead, 2026-10-28): M_ZM over [08:30, t] is the as-of function M(u); an
        # update followed by another with the same ts_recv is never the state as of any instant,
        # so only the last update of each ts_recv may set Hi or Lo (valid-mid rule unchanged)
        last_of_ts = np.ones(len(ts), bool)
        last_of_ts[:-1] = ts[1:] != ts[:-1]
        v = bk.valid[sel] & last_of_ts
        m2 = (bk.bpx[sel, 0] + bk.apx[sel, 0])
        big = np.iinfo(np.int64).max
        run_hi = np.maximum.accumulate(np.where(v, m2, -big)) if len(ts) else np.zeros(0, np.int64)
        run_lo = np.minimum.accumulate(np.where(v, m2, big)) if len(ts) else np.zeros(0, np.int64)
        c = np.searchsorted(ts, g, side="right")
        base_hi = np.where(out["zm0830_ok"], out["zm0830"], -big)
        base_lo = np.where(out["zm0830_ok"], out["zm0830"], big)
        cc = np.clip(c - 1, 0, None)
        h = np.where(c > 0, np.maximum(run_hi[cc] if len(ts) else -big, base_hi), base_hi)
        lw = np.where(c > 0, np.minimum(run_lo[cc] if len(ts) else big, base_lo), base_lo)
        ok = h > -big
        hi, lo = np.where(ok, h, 0), np.where(ok, lw, 0)
    out["rp_hi"], out["rp_lo"], out["rp_ok"] = hi, lo, ok


def prev_ordinal(d: date) -> int:
    p = calB.prev_trade_date(d)
    return -1 if p is None else p.toordinal()


def as_ordinal(d: date) -> int:
    return d.toordinal()


def from_ordinal(n: int) -> date:
    return date.fromordinal(int(n))


__all__ = ["day_raw", "compute_day", "sample", "mark_lookup", "ofi_terms", "Windows",
           "mid2_asof", "ticks", "timedelta", "OfiWindows",
           "ofi_included"]
