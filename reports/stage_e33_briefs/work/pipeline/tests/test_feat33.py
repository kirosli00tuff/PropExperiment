"""Tests of feat33 (Coder-A features; brief_FeatureCoder deliverable 2). Synthetic data only.

Part A: pass 1 (the event loop) on hand-built MBO and MBP-1 records: the open-time axis, book
updates (F_LAST), OFI, trades, sweeps, refills, removals, seasoned depth, F4.6's range, G1, G6,
LT4. Part B: pass 2, every one of the 59 features on hand-built pass-1 tables, each with its
answer worked out by hand in a comment. Part C: G2, G3, G4.
"""

from __future__ import annotations

import inspect
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import feat33 as F  # noqa: E402
import mbo_book31 as mb  # noqa: E402

D = date(2023, 3, 15)  # a Wednesday (CDT)
AX = F.axis(D)
IID, IID_S, IID_L = 7, 8, 9
TICK = {"ZM": 100_000_000, "ZS": 250_000_000, "ZL": 10_000_000}
LAST, SNAP, BADF = mb.F_LAST, mb.F_SNAPSHOT, mb.F_MAYBE_BAD_BOOK
MBO = np.dtype([("ts_recv", "<i8"), ("ts_event", "<i8"), ("instrument_id", "<u4"),
                ("order_id", "<u8"), ("price", "<i8"), ("size", "<u4"), ("flags", "u1"),
                ("action", "u1"), ("side", "u1"), ("sequence", "<u4")])
MBP = np.dtype([
    ("ts_recv", "<i8"), ("ts_event", "<i8"), ("rtype", "u1"), ("publisher_id", "<u2"),
    ("instrument_id", "<u4"), ("action", "u1"), ("side", "u1"), ("depth", "u1"),
    ("price", "<i8"), ("size", "<u4"), ("flags", "u1"), ("ts_in_delta", "<i4"),
    ("sequence", "<u4"), ("bid_px_00", "<i8"), ("ask_px_00", "<i8"), ("bid_sz_00", "<u4"),
    ("ask_sz_00", "<u4"), ("bid_ct_00", "<u4"), ("ask_ct_00", "<u4")])


def w(hh: int, mm: int, ss: float = 0.0, day: date = D) -> int:
    return F.wall_ns(day, hh, mm) + int(round(ss * 1e9))


def px(ticks: int) -> int:  # ZM price in 1e-9 USD/short ton
    return ticks * TICK["ZM"]


def rec(ts: int, act: str, side: str, ticks: int, size: int, oid: int, fl: int = LAST,
        ev: int | None = None, iid: int = IID) -> tuple:
    return (ts, ts if ev is None else ev, iid, oid, px(ticks), size, fl, ord(act), ord(side), 0)


def mbo(rows: list[tuple]) -> np.ndarray:
    return np.array(rows, dtype=MBO)


def opening(t0: int) -> list[tuple]:
    """R, bid 4000 x 5 (oid 1), ask 4001 x 7 (oid 2): one batch ending with F_LAST."""
    return [rec(t0, "R", "N", 0, 0, 0, fl=0), rec(t0, "A", "B", 4000, 5, 1, fl=0),
            rec(t0, "A", "A", 4001, 7, 2)]


def zm_out(rows: list[tuple]) -> dict:
    return F.stream_zm(mbo(rows), IID, AX)


def p_of(hh: int, mm: int) -> int:
    """Mark index of a CT wall time on the axis (READING FA-1)."""
    k = np.flatnonzero(AX.marks == w(hh, mm))
    assert len(k) == 1, f"{hh}:{mm} is not a mark"
    return int(k[0])


# =========================================================== Part A: pass 1 ====
def test_axis_marks_and_open_intervals():
    # 765 overnight marks 19:01 (D-1) .. 07:45, 290 day marks 08:31 .. 13:20 (READING FA-1)
    assert len(AX.marks) == 1055
    assert AX.marks[0] == w(19, 1, day=D - timedelta(days=1))
    assert AX.marks[F.P_J] == w(7, 45) and AX.marks[F.P_J + 1] == w(8, 31)
    assert AX.marks[F.P_0835] == w(8, 35) and AX.marks[F.P_1313] == w(13, 13)
    assert AX.marks[F.P_1315] == w(13, 15) and AX.marks[-1] == w(13, 20)
    assert F.GRID_P[-1] == p_of(13, 7) and len(F.REF_P) == 279
    ts = np.array([w(19, 0, day=D - timedelta(days=1)), w(19, 0, day=D - timedelta(days=1)) + 1,
                   w(7, 45), w(7, 45) + 1, w(8, 0), w(8, 30), w(8, 30) + 1, w(13, 20),
                   w(13, 20) + 1])
    assert AX.is_open(ts).tolist() == [False, True, True, False, False, False, True, True, False]


def test_book_update_stepping_partial_batch_not_seen_at_mark():
    # P0.3: "as of u" = the last F_LAST record with ts_recv <= u. A batch whose first record is
    # before 08:40 but whose F_LAST record is after it is invisible at the 08:40 mark.
    rows = opening(w(8, 0)) + [
        rec(w(8, 39, 59.9), "A", "B", 4000, 3, 3, fl=0),  # bid level 4000 -> 8, not committed
        rec(w(8, 40, 0.2), "A", "A", 3999 + 3, 1, 4),  # F_LAST after the mark
    ]
    out = zm_out(rows)
    p = p_of(8, 40)
    assert out["zm_touch"][p] == 5 + 7  # still the opening state
    assert out["zm_touch"][p + 1] == 8 + 7
    assert out["zm_raw2"][p] == px(4000) + px(4001)


def test_mid_validity_crossed_and_bad_book():
    rows = opening(w(8, 0)) + [rec(w(8, 40, 10), "A", "B", 4001, 1, 3)]  # locked: 4001 = 4001
    out = zm_out(rows)
    assert out["zm_ok"][p_of(8, 40)] and not out["zm_ok"][p_of(8, 41)]
    rows = opening(w(8, 0)) + [rec(w(8, 40, 10), "N", "N", 0, 0, 0, fl=LAST | BADF)]
    out = zm_out(rows)
    assert not out["zm_ok"][p_of(8, 41)]  # marked bad until the next R (E.31 Book)


def test_ofi_level1_hand_case():
    # s0: bid 4000 x 5, ask 4001 x 7.  s1: bid 4000 x 8 (add 3), ask 4001 x 7.
    # e1 = 1{4000>=4000} 8 - 1{4000<=4000} 5 - 1{4001<=4001} 7 + 1{4001>=4001} 7 = 3
    # s2: ask 4000.. no: bid improves to 4000 -> new bid 4000? use bid 3999+2=4001? keep simple:
    # s2: ask level 4001 cancelled 7 -> ask side empty -> e not computable (G3) -> ofi_bad += 1
    rows = opening(w(8, 0)) + [rec(w(8, 31, 10), "N", "N", 0, 0, 0),  # first day update: no term
                               rec(w(8, 40, 10), "A", "B", 4000, 3, 3),
                               rec(w(8, 42, 10), "C", "A", 4001, 7, 2)]
    out = zm_out(rows)
    c = out["zm_cnt"]
    assert F.win(c[F.ZI["ofi"]], p_of(8, 41), 1) == 3
    assert F.win(c[F.ZI["ofi_bad"]], p_of(8, 41), 1) == 0
    assert F.win(c[F.ZI["ofi_bad"]], p_of(8, 43), 1) == 1
    # the opening batch at 08:00 is in the pause: not counted (open time only)
    assert c[F.ZI["ofi_bad"], p_of(8, 40)] == 0


def test_ofi_e_formula_price_moves():
    # bid up 4000 -> 4001 (q 2), ask same 4002 x 4: e = 1{up} 2 - 0 - 1{=} 4 + 1{=} 4 = 2
    assert F.ofi_e(4000, 5, 4002, 4, 4001, 2, 4002, 4) == 2
    # ask down 4002 -> 4001 (q 3), bid same 4000 x 5: e = 5 - 5 - 1{down} 3 + 0 = -3
    assert F.ofi_e(4000, 5, 4002, 4, 4000, 5, 4001, 3) == -3
    # bid down 4000 -> 3999 (q 9): e = 0 - 5 (old bid size) - 4 + 4 = -5
    assert F.ofi_e(4000, 5, 4002, 4, 3999, 9, 4002, 4) == -5


def test_level_m_ofi_needs_five_levels():
    # one level per side: the level-m e_n (m <= 5) is not computable -> iofi_bad (READING FA-7)
    rows = opening(w(8, 0)) + [rec(w(8, 31, 10), "N", "N", 0, 0, 0),
                               rec(w(8, 40, 10), "A", "B", 4000, 3, 3)]
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["iofi_bad"]], p_of(8, 41), 1) == 1
    # five levels per side, sizes 1..5; then +3 at the best bid only: sum_m e^(m) = 3
    rows = [rec(w(8, 0), "R", "N", 0, 0, 0, fl=0)]
    oid = 10
    for m in range(5):
        rows.append(rec(w(8, 0), "A", "B", 4000 - m, m + 1, oid, fl=0))
        rows.append(rec(w(8, 0), "A", "A", 4001 + m, m + 1, oid + 1, fl=0))
        oid += 2
    rows[-1] = rows[-1][:6] + (LAST,) + rows[-1][7:]
    rows.append(rec(w(8, 31, 10), "N", "N", 0, 0, 0))  # first day update: no term (FD3 a)
    rows.append(rec(w(8, 40, 10), "A", "B", 4000, 3, 99))
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["iofi_bad"]], p_of(8, 41), 1) == 0
    assert F.win(c[F.ZI["iofi"]], p_of(8, 41), 1) == 3
    assert F.win(c[F.ZI["ofi"]], p_of(8, 41), 1) == 3


def test_trades_volume_sides_open_time_and_lt4():
    rows = opening(w(7, 0)) + [
        rec(w(7, 50), "T", "B", 4001, 9, 0),  # in the pause: never counted
        rec(w(8, 40, 1), "T", "B", 4001, 2, 0),
        rec(w(8, 40, 2), "T", "A", 4000, 3, 0),
        rec(w(8, 40, 3), "T", "N", 4000, 4, 0),  # side N: volume, not aggressor volume
        # LT4: ts_event after ts_recv; known at its ts_recv (08:41:10), counted there
        rec(w(8, 41, 10), "T", "B", 4001, 5, 0, ev=w(8, 42, 30)),
    ]
    c = zm_out(rows)["zm_cnt"]
    p = p_of(8, 41)
    assert F.win(c[F.ZI["vol"]], p, 1) == 2 + 3 + 4
    assert F.win(c[F.ZI["buy"]], p, 1) == 2 and F.win(c[F.ZI["sell"]], p, 1) == 3
    assert F.win(c[F.ZI["ntr"]], p, 1) == 3
    assert F.win(c[F.ZI["vol"]], p + 1, 1) == 5  # by ts_recv, not ts_event
    assert c[F.ZI["vol"], p_of(8, 40)] == 0  # the 07:50 trade is in the pause


def test_window_crosses_the_pause():
    # trades at 07:44:30 (overnight, open) and 08:32:00 (day): the 5-minute window ending at
    # 08:35 is (07:45, 08:35] on the axis -> only 08:32; the 6-minute window adds (07:44, 07:45]
    rows = opening(w(7, 0)) + [rec(w(7, 44, 30), "T", "B", 4001, 1, 0),
                               rec(w(8, 10), "T", "B", 4001, 50, 0),  # pause
                               rec(w(8, 32), "T", "B", 4001, 2, 0)]
    c = zm_out(rows)["zm_cnt"][F.ZI["vol"]]
    p = F.P_0835
    assert F.win(c, p, 5) == 2 and F.win(c, p, 6) == 3


def sweep_rows() -> list[tuple]:
    """Bid 4000 x 5 (oid 1); asks 4001 x 3 (oid 2), 4002 x 4 (oid 3). At 08:40:10 a buy of 3
    takes the whole 4001 level: T, F (oid 2), C (oid 2, filled) in one batch (ts_event E)."""
    t0, ts = w(8, 0), w(8, 40, 10)
    return [rec(t0, "R", "N", 0, 0, 0, fl=0), rec(t0, "A", "B", 4000, 5, 1, fl=0),
            rec(t0, "A", "A", 4001, 3, 2, fl=0), rec(t0, "A", "A", 4002, 4, 3),
            rec(ts, "T", "B", 4001, 3, 0, fl=0, ev=ts - 500),
            rec(ts, "F", "A", 4001, 3, 2, fl=0, ev=ts - 500),
            rec(ts, "C", "A", 4001, 3, 2, ev=ts - 500)]


def test_sweep_refill_and_fill_not_removal():
    rows = sweep_rows() + [
        rec(w(8, 40, 10.05), "A", "A", 4001, 1, 4),  # 50 ms later at 4001 ask: a refill
        rec(w(8, 40, 10.30), "A", "A", 4001, 1, 5),  # 300 ms later: not a refill
        rec(w(8, 40, 20), "C", "A", 4001, 2, 4),  # voluntary: 1 lot... oid 4 has 1 lot
    ]
    c = zm_out(rows)["zm_cnt"]
    p = p_of(8, 41)
    assert F.win(c[F.ZI["swb"]], p, 1) == 1 and F.win(c[F.ZI["sws"]], p, 1) == 0
    assert F.win(c[F.ZI["rfa"]], p, 1) == 1 and F.win(c[F.ZI["rfb"]], p, 1) == 0
    # removals: the C of filled oid 2 is not a removal (DO-16); the C of oid 4 (1 lot at the
    # best ask 4001 just before it) is: Ca = 1, Cb = 0
    assert F.win(c[F.ZI["cra"]], p, 1) == 1 and F.win(c[F.ZI["crb"]], p, 1) == 0


def test_trade_set_over_two_batches_with_one_ts_event():
    # READING FA-10: the T batch ends (F_LAST) before the level is removed; a second batch with
    # the same ts_event removes it -> the buy sweep is counted at the second batch's update
    t0, ts = w(8, 0), w(8, 40, 10)
    rows = [rec(t0, "R", "N", 0, 0, 0, fl=0), rec(t0, "A", "B", 4000, 5, 1, fl=0),
            rec(t0, "A", "A", 4001, 3, 2, fl=0), rec(t0, "A", "A", 4002, 4, 3),
            rec(ts, "T", "B", 4001, 3, 0, fl=0, ev=ts), rec(ts, "F", "A", 4001, 3, 2, ev=ts),
            rec(w(8, 41, 20), "C", "A", 4001, 3, 2, ev=ts)]
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["swb"]], p_of(8, 41), 1) == 0
    assert F.win(c[F.ZI["swb"]], p_of(8, 42), 1) == 1
    # a later ts_event closes the set: the same removal then is not a sweep
    rows[-1] = rec(w(8, 41, 20), "C", "A", 4001, 3, 2, ev=ts + 1)
    c = zm_out(rows)["zm_cnt"]
    assert c[F.ZI["swb"], -1] == 0


def test_other_instruments_ignored():
    rows = opening(w(8, 0)) + [rec(w(8, 40, 10), "T", "B", 4001, 9, 0, iid=IID + 1),
                               rec(w(8, 40, 11), "A", "B", 4000, 9, 50, iid=IID + 1)]
    out = zm_out(rows)
    assert out["zm_cnt"][F.ZI["vol"], -1] == 0 and out["zm_touch"][-1] == 12


def test_partial_level_take_is_not_a_sweep():
    t0, ts = w(8, 0), w(8, 40, 10)
    rows = opening(t0) + [rec(ts, "T", "A", 4000, 2, 0, fl=0, ev=ts),
                          rec(ts, "F", "B", 4000, 2, 1, fl=0, ev=ts),
                          rec(ts, "M", "B", 4000, 3, 1, ev=ts)]  # bid 5 -> 3: level remains
    c = zm_out(rows)["zm_cnt"]
    p = p_of(8, 41)
    assert F.win(c[F.ZI["sws"]], p, 1) == 0 and F.win(c[F.ZI["swb"]], p, 1) == 0
    assert F.win(c[F.ZI["crb"]], p, 1) == 0  # the M of a filled order is the fill (DO-16)


def test_removals_modify_and_cancel_cases():
    t0 = w(8, 0)
    rows = opening(t0) + [
        rec(t0, "A", "B", 3999, 6, 3),  # second bid level
        rec(w(8, 40, 1), "M", "B", 4000, 2, 1),  # best bid 5 -> 2: Cb += 3
        rec(w(8, 40, 2), "M", "B", 3999, 9, 3),  # size increase, not at best: 0
        rec(w(8, 40, 3), "C", "B", 3999, 4, 3),  # partial cancel at 3999 (not best): 0
        rec(w(8, 40, 4), "M", "A", 4002, 7, 2),  # best ask moves 4001 -> 4002: Ca += 7
    ]
    c = zm_out(rows)["zm_cnt"]
    p = p_of(8, 41)
    assert F.win(c[F.ZI["crb"]], p, 1) == 3 and F.win(c[F.ZI["cra"]], p, 1) == 7


def test_seasoned_depth_hand_case():
    # at t = 08:40: bid 4000 has oid 1 (4 lots, added 08:39:55) and oid 3 (6 lots, added
    # 08:39:59.5); ask 4001 has oid 2 (2 lots, added 08:39:58) and oid 4 (5 lots, modified at
    # 08:39:59.1). Seasoned (last add/modify <= t - 1 s = 08:39:59): qb_1 = 4, qa_1 = 2.
    t0 = w(8, 0)
    rows = [rec(t0, "R", "N", 0, 0, 0, fl=0), rec(t0, "A", "B", 3990, 1, 50, fl=0),
            rec(t0, "A", "A", 4010, 1, 51),
            rec(w(8, 39, 55), "A", "B", 4000, 4, 1), rec(w(8, 39, 58), "A", "A", 4001, 2, 2),
            rec(w(8, 39, 58.5), "A", "A", 4001, 6, 4),
            rec(w(8, 39, 59.1), "M", "A", 4001, 5, 4),  # size down: still a modify (FA-9)
            rec(w(8, 39, 59.5), "A", "B", 4000, 6, 3)]
    out = zm_out(rows)
    i = p_of(8, 40) - F.P_0835
    qb = out["zm_seas"][:3, i]
    qa = out["zm_seas"][3:, i]
    # level 2: bid 3990 (oid 50 at 08:00) 1 lot; ask 4010 1 lot; level 3 missing -> 0
    assert qb.tolist() == [4, 1, 0] and qa.tolist() == [2, 1, 0]


def test_rp_range_seeded_at_0830_and_function_of_time():
    t0 = w(8, 0)
    rows = opening(t0) + [
        rec(w(8, 30, 0), "A", "B", 4000, 1, 9),  # as of 08:30:00: mid (4000+4001)
        rec(w(8, 33), "C", "A", 4001, 7, 2, fl=0), rec(w(8, 33), "A", "A", 4004, 7, 2),
        # two updates at one ts_recv: only the last is M(u) (READING FA-14)
        rec(w(8, 34), "A", "A", 4002, 1, 5), rec(w(8, 34), "C", "A", 4002, 1, 5),
    ]
    out = zm_out(rows)
    i = 0  # t = 08:35
    assert out["zm_hi"][i] == px(4000) + px(4004)  # max over [08:30, 08:35]
    assert out["zm_lo"][i] == px(4000) + px(4001)  # the 08:30:00 state seeds the range


def test_g1_records_after_t_change_nothing():
    base = sweep_rows() + [rec(w(9, 0), "T", "B", 4002, 1, 0), rec(w(9, 1), "A", "B", 4000, 2, 7)]
    later = base + [rec(w(9, 3, 0.5), "A", "B", 4001, 4, 8), rec(w(9, 4), "T", "A", 4001, 4, 0),
                    rec(w(9, 5), "C", "B", 4000, 5, 1)]
    a, b = zm_out(base), zm_out(later)
    p = p_of(9, 3)
    for key in ("zm_raw2", "zm_ok", "zm_touch", "zm_spread"):
        assert np.array_equal(a[key][:p + 1], b[key][:p + 1])
    assert np.array_equal(a["zm_cnt"][:, :p + 1], b["zm_cnt"][:, :p + 1])
    assert np.array_equal(a["zm_lvl"][:, :p + 1], b["zm_lvl"][:, :p + 1])
    k = p - F.P_0835
    assert np.array_equal(a["zm_seas"][:, :k + 1], b["zm_seas"][:, :k + 1], equal_nan=True)
    assert np.array_equal(a["zm_hi"][:k + 1], b["zm_hi"][:k + 1], equal_nan=True)
    assert not np.array_equal(a["zm_cnt"], b["zm_cnt"])  # the later records do count later


def test_g6_ts_event_never_a_clock():
    # shifting every ts_event by one hour (ts_recv unchanged) changes nothing
    rows = sweep_rows() + [rec(w(8, 50), "T", "A", 4000, 1, 0)]
    shifted = [r[:1] + (r[1] + 3600 * F.NS,) + r[2:] for r in rows]
    a, b = zm_out(rows), zm_out(shifted)
    for key in a:
        assert np.array_equal(a[key], b[key], equal_nan=True)
    src = inspect.getsource(F)
    for bad in ("ts_recv - ts_event", "ts_event - ts_recv", '"ts_event"] -', '"ts_recv"] - r['):
        assert bad not in src


def test_lt4_unsorted_input_refused():
    rows = opening(w(8, 0)) + [rec(w(8, 40), "A", "B", 4000, 1, 3), rec(w(8, 39), "A", "B", 4000, 1, 4)]
    with pytest.raises(ValueError):
        zm_out(rows)


def mbp_rec(ts: int, act: str, bid: int, bsz: int, ask: int, asz: int, size: int = 0,
            fl: int = LAST, iid: int = IID_S) -> tuple:
    return (ts, ts, 1, 1, iid, ord(act), ord("N"), 0, 0, size, fl, 0, 0, bid, ask, bsz, asz, 0, 0)


def test_mbp1_states_ofi_volume_and_bad_batch():
    tk = TICK["ZS"]
    rows = [mbp_rec(w(8, 0), "A", 5600 * tk, 5, 5601 * tk, 7),
            mbp_rec(w(8, 31, 10), "A", 5600 * tk, 5, 5601 * tk, 7),  # first day update: no term
            mbp_rec(w(8, 40, 10), "A", 5600 * tk, 8, 5601 * tk, 7),  # e = 8 - 5 - 7 + 7 = 3
            mbp_rec(w(8, 40, 20), "T", 5600 * tk, 8, 5601 * tk, 7, size=4),
            mbp_rec(w(8, 41, 10), "C", 5600 * tk, 8, 5601 * tk, 7, fl=BADF),  # batch flagged
            mbp_rec(w(8, 41, 10), "C", 5600 * tk, 8, 5601 * tk, 6),  # its F_LAST: bad state
            mbp_rec(w(8, 42, 10), "C", 5600 * tk, 8, 5601 * tk, 6)]  # good again
    arr = np.array(rows, dtype=MBP)
    out = F.stream_mbp1(arr, IID_S, AX, "zs")
    c = out["zs_cnt"]
    assert F.win(c[F.MI["ofi"]], p_of(8, 41), 1) == 3 + 0  # the T update repeats the state
    assert F.win(c[F.MI["vol"]], p_of(8, 41), 1) == 4
    assert F.win(c[F.MI["ofi_bad"]], p_of(8, 42), 1) == 1  # bad state (READING FA-4)
    assert F.win(c[F.MI["ofi_bad"]], p_of(8, 43), 1) == 1  # previous state was bad
    assert not out["zs_ok"][p_of(8, 42)] and out["zs_ok"][p_of(8, 43)]
    assert out["zs_raw2"][p_of(8, 43)] == (5600 + 5601) * tk


def test_mbp1_empty_side_invalid():
    rows = [mbp_rec(w(8, 0), "A", F.I64_MAX, 0, 5601 * TICK["ZS"], 7)]
    out = F.stream_mbp1(np.array(rows, dtype=MBP), IID_S, AX, "zs")
    assert not out["zs_ok"][F.P_0835]


def test_day_series_ref_values_from_counters():
    p1 = flat_p1()
    zc = p1["zm_cnt"]
    p = F.P_0835 + 10
    zc[F.ZI["swb"], p:] += 2  # 2 buy sweeps between marks p-1 and p
    zc[F.ZI["rfb"], p:] += 3
    zc[F.ZI["ofi"], p:] += -7
    zc[F.ZI["vol"], p:] += 11
    s = F.day_series(p1)
    k = 10
    assert s["ref_sw5"][k] == 2 and s["ref_sw5"][k + 4] == 2 and s["ref_sw5"][k + 5] == 0
    assert s["ref_arf15"][k] == 3 and s["ref_aofi_zm1"][k] == 7 and s["ref_aofi_zm5"][k] == 7
    assert s["ref_v15"][k] == 11 and s["ref_v15"][k + 15] == 0
    assert s["ref_dep"][0, 0] == 10 / 2  # (qb_1 + qa_1)/2 with qb_1 + qa_1 = 10


# =========================================================== pass-1 table builders ====
MID = {"zm": 4000.0, "zs": 5600.0, "zl": 6000.0}  # ticks: 400 USD/t, 1400 c/bu, 60 c/lb
TK = {"zm": TICK["ZM"], "zs": TICK["ZS"], "zl": TICK["ZL"]}


def set_mid(p1: dict, root: str, p: int | np.ndarray | slice, ticks: float | np.ndarray) -> None:
    p1[f"{root}_raw2"][p] = np.round(2 * np.asarray(ticks) * TK[root]).astype(np.int64)
    p1[f"{root}_ok"][p] = True
    sync(p1)


def sync(p1: dict) -> None:
    """Regular axis: the wall minutes 08:35..13:15 are marks, so the as-of-wall states equal
    the axis states at map_pos."""
    mp = p1["map_pos"]
    for r in ("zm", "zs", "zl"):
        if f"{r}_raw2" in p1:
            p1[f"{r}_wraw2"], p1[f"{r}_wok"] = p1[f"{r}_raw2"][mp].copy(), p1[f"{r}_ok"][mp].copy()
    if "zm_lvl" in p1:
        p1["zm_wlvl"] = p1["zm_lvl"][:, mp].copy()


def flat_p1(fronts: tuple = (IID, IID_S, IID_L)) -> dict:
    """Pass-1 tables of a quiet date: constant mids, spread 1 tick, touch 10, every level
    qb_m + qa_m = 10, seasoned 5 per level per side, counters 0, RP range a point."""
    p1 = {"marks": AX.marks.copy(), "fronts": np.array(fronts, dtype=np.int64),
          "ticks": np.array([TICK["ZM"], TICK["ZS"], TICK["ZL"]], dtype=np.int64),
          "wall_ns": AX.wall.copy(), "map_pos": AX.map_pos.copy(),
          "ax_prev": np.zeros(F.N_MARKS, bool)}
    for r in ("zm", "zs", "zl"):
        p1[f"{r}_raw2"] = np.zeros(F.N_MARKS, np.int64)
        p1[f"{r}_ok"] = np.zeros(F.N_MARKS, bool)
        set_mid(p1, r, slice(None), MID[r])
    p1["zm_spread"] = np.full(F.N_MARKS, TICK["ZM"], np.int64)
    p1["zm_touch"] = np.full(F.N_MARKS, 10, np.int64)
    p1["zm_lvl"] = np.full((F.N_LVL, F.N_MARKS), 10, np.int64)
    p1["zm_seas"] = np.full((6, F.N_GRID), 5.0)
    p1["zm_hi"] = np.full(F.N_GRID, float(p1["zm_raw2"][0]))
    p1["zm_lo"] = p1["zm_hi"].copy()
    p1["zm_cnt"] = np.zeros((len(F.ZC), F.N_MARKS), np.int64)
    p1["zs_cnt"] = np.zeros((len(F.MC), F.N_MARKS), np.int64)
    p1["zl_cnt"] = np.zeros((len(F.MC), F.N_MARKS), np.int64)
    sync(p1)
    return p1


def hist_p1(amp: tuple = (1, 2, 3)) -> dict:
    """A history date: mids alternate base, base + amp over 08:35..13:13 (every 1-minute change
    is +-amp, 139 up and 139 down: population SD = amp) and the reference series constant:
    |OFI| 10, (qb_m + qa_m)/2 = 4, sweeps 2, |refill diff| 3, lam slope 0.5, V15 99."""
    p1 = flat_p1()
    k = np.arange(F.N_REF) % 2
    for r, a in zip(("zm", "zs", "zl"), amp, strict=True):
        set_mid(p1, r, F.REF_P, MID[r] + a * k)
    for key in ("zs1", "zs5", "zl1", "zl5", "zm1", "zm5", "zm15"):
        p1[f"ref_aofi_{key}"] = np.full(F.N_REF, 10.0)
    p1["ref_dep"] = np.full((F.N_LVL, F.N_REF), 4.0)
    p1["ref_sw5"] = np.full(F.N_REF, 2.0)
    p1["ref_arf15"] = np.full(F.N_REF, 3.0)
    p1["ref_lam"] = np.full(F.N_REF, 0.5)
    p1["ref_v15"] = np.full(F.N_REF, 99.0)
    return p1


def info(day: date = D, seg: int = 1, fronts: tuple = (IID, IID_S, IID_L), **kw) -> F.DayInfo:
    return F.DayInfo(day=day, fronts=fronts, seg=seg, **kw)


def hist_list(n: int = 21, **kw) -> list:
    return [(hist_p1(), info(D - timedelta(days=n - k))) for k in range(n)] if not kw else \
        [(hist_p1(**kw), info(D - timedelta(days=n - k))) for k in range(n)]


def feats(p1: dict, inf: F.DayInfo | None = None, hist: list | None = None, do_sync: bool = True
          ) -> tuple[np.ndarray, np.ndarray, F.Refs]:
    inf = inf or info(expiry_dates=30)
    hist = hist_list() if hist is None else hist
    if do_sync:
        sync(p1)
    ref = F.build_refs((p1, inf), hist)
    v, ok = F.features_day(p1, inf, ref)
    return v, ok, ref


def val(v: np.ndarray, ok: np.ndarray, i: int, name: str) -> float | None:
    k = F.FI[name]
    return float(v[i, k]) if ok[i, k] else None


def gp(i: int) -> int:
    return F.P_0835 + i


# =========================================================== Part B: the 59 features ====
def test_refs_from_history_hand_values():
    _, _, ref = feats(flat_p1())
    # sigma: every change +-amp -> pop SD amp (ZM 1, ZS 2, ZL 3)
    assert ref.sigma == {"zm": 1.0, "zs": 2.0, "zl": 3.0}
    assert ref.obar["zs1"] == 10 and ref.dbar_sum == 5 * 4  # sum over 5 levels of mean 4
    assert ref.sbar5 == 2 and ref.rbar15 == 3 and ref.lam_med == 0.5
    assert np.all(ref.vbar == 99)


def test_c1_c2_tod():
    v, ok, _ = feats(flat_p1())
    assert val(v, ok, 139, "C_1") == pytest.approx(139 / 278)  # = 0.5
    assert val(v, ok, 139, "C_2") == pytest.approx(0.25)
    assert val(v, ok, 0, "C_1") == 0.0


def test_c3_spread_capped():
    p1 = flat_p1()
    p1["zm_spread"][gp(3)] = 3 * TICK["ZM"]
    p1["zm_spread"][gp(4)] = 7 * TICK["ZM"]
    v, ok, _ = feats(p1)
    assert val(v, ok, 3, "C_3") == 3.0 and val(v, ok, 4, "C_3") == 5.0  # min(7, 5)
    p1["zm_ok"][gp(5)] = False
    v, ok, _ = feats(p1)
    assert val(v, ok, 5, "C_3") is None and v[5, F.FI["C_3"]] == 0.0  # G3


def test_c4_touch_depth():
    v, ok, _ = feats(flat_p1())
    assert val(v, ok, 7, "C_4") == pytest.approx(math.log(11))  # log(1 + 10)


def test_c5_volume_ratio():
    p1 = flat_p1()
    p1["zm_cnt"][F.ZI["vol"], gp(20) - 3:] = 49  # 49 contracts inside (t-15, t] for i=20..
    v, ok, _ = feats(p1)
    # log((49 + 1)/(99 + 1)) = log 0.5
    assert val(v, ok, 20, "C_5") == pytest.approx(math.log(0.5))
    # i = 40: the trade is 23 minutes back -> V = 0 -> log(1/100) = -4.605 (inside the clip)
    assert val(v, ok, 40, "C_5") == pytest.approx(math.log(1 / 100))


def test_c6_log_sigma():
    v, ok, _ = feats(flat_p1(), hist=hist_list(amp=(2, 2, 3)))
    assert val(v, ok, 0, "C_6") == pytest.approx(math.log(2))  # sigma_ZM = 2


def test_c7_expiry():
    v, ok, _ = feats(flat_p1(), info(expiry_dates=30))
    assert val(v, ok, 0, "C_7") == 0.5  # 30/60
    v, ok, _ = feats(flat_p1(), info(expiry_dates=90))
    assert val(v, ok, 0, "C_7") == 1.0  # min(90, 60)/60
    v, ok, _ = feats(flat_p1(), info(expiry_dates=None))
    assert val(v, ok, 0, "C_7") is None


def test_c8_c9_release_and_c10_c15():
    inf = info(expiry_dates=30, releases=(w(11, 0),), monday_or_after_closure=True, jja=True)
    v, ok, _ = feats(flat_p1(), inf)
    assert val(v, ok, 0, "C_8") == 1.0
    assert val(v, ok, 174, "C_9") == 0.0 and val(v, ok, 175, "C_9") == 1.0  # 11:29 vs 11:30
    assert val(v, ok, 0, "C_10") == 1.0 and val(v, ok, 0, "C_15") == 1.0
    v, ok, _ = feats(flat_p1())
    assert val(v, ok, 200, "C_8") == 0.0 and val(v, ok, 200, "C_9") == 0.0
    assert val(v, ok, 0, "C_10") == 0.0 and val(v, ok, 0, "C_15") == 0.0


def crush_pattern(p1: dict, p: int, s_now: float, lo: int, n: int) -> None:
    """ZS mids (ticks) 5600 + s at marks: s = 2 at even marks, 0 at odd marks over [lo, p),
    and s_now at p. C = const - 0.25 s cents (only ZS moves; ZS tick 0.25 c/bu)."""
    q = np.arange(lo, p)
    set_mid(p1, "zs", q, MID["zs"] + np.where(q % 2 == 0, 2.0, 0.0))
    set_mid(p1, "zs", p, MID["zs"] + s_now)


def test_f1_1_zc30_and_f1_2_zc120():
    p1 = flat_p1()
    i = 140
    p = gp(i)
    crush_pattern(p1, p, -4.0, p - 120, 120)
    v, ok, _ = feats(p1)
    # window of 30 (or 120): 15 (60) marks at C0 and 15 (60) at C0 - 0.5 -> mean C0 - 0.25,
    # pop SD 0.25; C(t) = C0 + 1.0 -> z = (1.0 + 0.25)/0.25 = 5.0
    assert val(v, ok, i, "F1_1") == pytest.approx(5.0)
    assert val(v, ok, i, "F1_2") == pytest.approx(5.0)
    p1["zl_ok"][p - 31] = False  # outside the 30-window, inside the 120-window
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F1_1") == pytest.approx(5.0)
    assert val(v, ok, i, "F1_2") is None  # READING FA-5: every sample point must be defined


def test_f1_4_dzc5():
    p1 = flat_p1()
    i = 141
    p = gp(i)
    assert (p - 5) % 2 == 1  # so s(t-5) = 0: C(t-5) = C0
    crush_pattern(p1, p, -4.0, p - 40, 40)
    v, ok, _ = feats(p1)
    # zC30(t) = 5 (as above); zC30(t-5) = (C0 - (C0 - 0.25))/0.25 = 1 -> dzC5 = 4
    assert val(v, ok, i, "F1_4") == pytest.approx(4.0)


def test_f1_5_vrel15_and_f1_6():
    p1 = flat_p1()
    i = 141
    p = gp(i)
    crush_pattern(p1, p, -4.0, p - 40, 40)
    p1["zm_cnt"][F.ZI["vol"], p - 2:] = 10
    p1["zs_cnt"][F.MI["vol"], p - 2:] = 20
    p1["zl_cnt"][F.MI["vol"], p - 2:] = 70
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F1_5") == pytest.approx(0.1)  # 10/(10 + 20 + 70)
    assert val(v, ok, i, "F1_6") == pytest.approx(0.5)  # zC30 5 x 0.1
    assert val(v, ok, i + 30, "F1_5") is None  # no volume in the window: 0/0


def ols_hist(seg_of: list[int] | None = None) -> list:
    """10 (of 21) history dates whose 08:35..13:13 samples follow a 4-state cycle:
    dS, dL, e = (+1,+1,+1), (+1,-1,-1), (-1,+1,-1), (-1,-1,+1); M_ZS = 1400 + 0.25 dS c/bu,
    M_ZL = 60 + 0.01 dL c/lb, M_ZM = -180 + 0.2 M_ZS + 5 M_ZL + 0.05 e = 400 + 0.05 (dS+dL+e)
    USD/t. dS, dL, e and 1 are mutually orthogonal over a cycle, so OLS gives a = -180,
    b_S = 0.2, b_L = 5 and residuals 0.05 e: sd_e = 0.05 USD = 0.5 ZM ticks."""
    cyc = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
    out = []
    for k in range(21):
        p1 = flat_p1()
        n = (F.N_REF // 4) * 4  # 276 marks: whole cycles
        st = cyc[np.arange(n) % 4]
        ps = F.REF_P[:n]
        set_mid(p1, "zs", ps, 5600 + st[:, 0])  # ticks of 0.25 c
        set_mid(p1, "zl", ps, 6000 + st[:, 1])  # ticks of 0.01 c
        set_mid(p1, "zm", ps, 4000 + 0.5 * (st[:, 0] + st[:, 1] + st[:, 2]))  # 0.05 USD = 0.5 tick
        p1["zm_ok"][F.REF_P[n:]] = False
        sync(p1)
        p1.update(F.day_series(p1))
        seg = 1 if seg_of is None else seg_of[k]
        out.append((p1, info(D - timedelta(days=21 - k), seg=seg)))
    return out


def test_f1_3_zr_ols_hand_case():
    p1 = flat_p1()
    set_mid(p1, "zm", gp(10), 4001.0)  # M_ZM(t) = 400.10 with M_ZS = 1400, M_ZL = 60
    v, ok, ref = feats(p1, hist=ols_hist())
    a, b_s, b_l, sd_e, n, n_dates = ref.ols
    assert a == pytest.approx(-180) and b_s == pytest.approx(0.2) and b_l == pytest.approx(5)
    assert sd_e == pytest.approx(0.5) and n == 2760 and n_dates == 10
    # e(t) = (400.10 - (-180 + 0.2 x 1400 + 5 x 60))/0.10 = 0.10/0.10 = 1 tick; zR = 1/0.5 = 2
    assert val(v, ok, 10, "F1_3") == pytest.approx(2.0)
    assert val(v, ok, 11, "F1_3") == pytest.approx(0.0, abs=1e-9)  # M_ZM(t) = 400: e = 0


def test_f1_3_segment_and_release_rules():
    # only 2 of the last 10 dates in D's segment -> fewer than 3 dates -> invalid (G2)
    hist = ols_hist([2] * 19 + [1] * 2)
    v, ok, ref = feats(flat_p1(), hist=hist)
    assert ref.ols is None and val(v, ok, 0, "F1_3") is None
    # a release on every history date removes [R - 2, R + 30] = 10:58..11:30 (33 marks)
    hist = ols_hist()
    hist = [(h, F.DayInfo(day=i.day, fronts=i.fronts, seg=1,
                          releases=(F.wall_ns(D, 11, 0),))) for h, i in hist]
    for h, _ in hist:
        h["wall_ns"] = AX.wall  # the history minutes are D's in this synthetic case
    _, _, ref = feats(flat_p1(), hist=hist)
    assert ref.ols[4] == 10 * (276 - 33)


def gap_hist(g_vals: list[float], seg_of: list[int] | None = None,
             front_of: list[int] | None = None, zm_vals: list[float] | None = None) -> list:
    """21 history dates; date k's 08:35 ZS mid is 5600 - 4 g_k ticks and its 13:15 ZS mid is
    5600, so C(08:35 D_k) - C(13:15 D_k-1) = 0.25 x 4 g_k = g_k cents (C = const - 0.25 ZS
    ticks). ``zm_vals`` (default 0) moves the ZM 08:35 mid by z_k ticks: the F4.7 gap (and the
    crush by 0.22 z_k cents)."""
    out = []
    for k in range(21):
        p1 = flat_p1()
        g = g_vals[k]
        set_mid(p1, "zs", F.P_0835, MID["zs"] - 4 * g)
        set_mid(p1, "zm", F.P_0835, MID["zm"] + (0.0 if zm_vals is None else zm_vals[k]))
        p1.update(F.day_series(p1))
        seg = 1 if seg_of is None else seg_of[k]
        fr = (IID if front_of is None else front_of[k], IID_S, IID_L)
        out.append((p1, info(D - timedelta(days=21 - k), seg=seg, fronts=fr)))
    return out


def test_f1_7_gc_and_f1_8():
    hist = gap_hist([0.0] + [0.5, -0.5] * 10)  # 20 values +-0.5 -> sd_g = 0.5
    p1 = flat_p1()
    set_mid(p1, "zs", F.P_0835, MID["zs"] - 4.0)  # g(D) = 1.0 cent
    v, ok, ref = feats(p1, hist=hist)
    assert ref.gc == pytest.approx(2.0)  # 1.0/0.5
    assert val(v, ok, 0, "F1_7") == pytest.approx(2.0) and val(v, ok, 100, "F1_7") == pytest.approx(2.0)
    assert val(v, ok, 30, "F1_8") == pytest.approx(2.0 * math.exp(-1))  # exp(-30/30)


def test_f1_7_needs_ten_values_inside_the_segment():
    # dates 0..11 in segment 2, 12..20 and D in segment 1: 9 values in D's segment (date 12's
    # previous date is outside it, so 12 gives none; 13..20 give 8) -> fewer than 10: invalid
    hist = gap_hist([0.5, -0.5] * 10 + [0.5], seg_of=[2] * 12 + [1] * 9)
    _, _, ref = feats(flat_p1(), hist=hist)
    assert ref.gc is None and ref.counts["gc_values"] == 8
    # D first in its segment: g(D) crosses the boundary -> invalid even with a good sd_g
    hist = gap_hist([0.0] + [0.5, -0.5] * 10)
    v, ok, ref = feats(flat_p1(), info(seg=5, expiry_dates=30), hist=hist)
    assert ref.gc is None and val(v, ok, 0, "F1_7") is None and val(v, ok, 0, "C_11") == 0.0


def test_f2_1_to_f2_6_cross_returns():
    p1 = flat_p1()
    i = 50
    p = gp(i)
    set_mid(p1, "zs", p, MID["zs"] + 4)  # ZS +4 ticks vs t - 1 .. t - 15
    set_mid(p1, "zl", p, MID["zl"] - 6)  # ZL -6 ticks
    v, ok, _ = feats(p1)  # sigma_ZS 2, sigma_ZL 3
    assert val(v, ok, i, "F2_1") == pytest.approx(4 / 2)  # 4/(2 sqrt 1)
    assert val(v, ok, i, "F2_2") == pytest.approx(4 / (2 * math.sqrt(5)))
    assert val(v, ok, i, "F2_3") == pytest.approx(4 / (2 * math.sqrt(15)))
    assert val(v, ok, i, "F2_4") == pytest.approx(-6 / 3)
    assert val(v, ok, i, "F2_5") == pytest.approx(-6 / (3 * math.sqrt(5)))
    assert val(v, ok, i, "F2_6") == pytest.approx(-6 / (3 * math.sqrt(15)))
    p1["zs_ok"][p - 5] = False
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F2_2") is None and val(v, ok, i, "C_12") == 0.0


def test_f2_7_d5():
    p1 = flat_p1()
    i = 50
    set_mid(p1, "zs", gp(i), MID["zs"] + 4)  # dZS_5 = +1.00 c/bu
    set_mid(p1, "zl", gp(i), MID["zl"] + 10)  # dZL_5 = +0.10 c/lb
    set_mid(p1, "zm", gp(i), MID["zm"] - 2)  # dZM_5 = -0.20 USD/t
    v, ok, _ = feats(p1)
    # [(1.00 - 11 x 0.10)/2.2 - (-0.20)]/0.10/(1 x sqrt 5) = [-0.04545... + 0.20]/0.10/2.23607
    # = 1.54545.../2.23607 = 0.691149
    exp = ((1.00 - 11 * 0.10) / 2.2 + 0.20) / 0.10 / math.sqrt(5)
    assert val(v, ok, i, "F2_7") == pytest.approx(exp) and exp == pytest.approx(0.691149, abs=1e-6)


def test_f2_8_to_f2_11_ofi_ratios():
    p1 = flat_p1()
    i = 60
    p = gp(i)
    p1["zs_cnt"][F.MI["ofi"], p:] = 30  # +30 between t-1 and t
    p1["zl_cnt"][F.MI["ofi"], p - 3:] = -20  # -20 three minutes back
    v, ok, _ = feats(p1)  # Obar 10 for every k
    assert val(v, ok, i, "F2_8") == 3.0 and val(v, ok, i, "F2_9") == 3.0  # 30/10
    assert val(v, ok, i, "F2_10") == 0.0 and val(v, ok, i, "F2_11") == -2.0  # -20/10
    p1["zs_cnt"][F.MI["ofi_bad"], p - 2:] = 1  # one e_n not computable 2 minutes back
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F2_8") == 3.0 and val(v, ok, i, "F2_9") is None


def test_f3_1_to_f3_4_zm_ofi():
    p1 = flat_p1()
    i = 60
    p = gp(i)
    p1["zm_cnt"][F.ZI["ofi"], p - 10:] = 25
    p1["zm_cnt"][F.ZI["iofi"], p - 1:] = 40
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_1") == 0.0 and val(v, ok, i, "F3_2") == 0.0  # 10 min back
    assert val(v, ok, i, "F3_3") == 2.5  # 25/10
    assert val(v, ok, i, "F3_4") == 2.0  # 40/(5 x 4)
    p1["zm_cnt"][F.ZI["iofi_bad"], p:] = 1
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_4") is None


def test_f3_5_f3_6_trade_imbalance():
    p1 = flat_p1()
    i = 60
    p = gp(i)
    p1["zm_cnt"][F.ZI["buy"], p - 1:] = 30
    p1["zm_cnt"][F.ZI["sell"], p - 8:] = 10
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_5") == 1.0  # (30 - 0)/30 inside 5 minutes
    assert val(v, ok, i, "F3_6") == 0.5  # (30 - 10)/40 inside 15 minutes
    assert val(v, ok, i + 20, "F3_5") is None  # B + S = 0


def test_f3_7_f3_8_queue_imbalance_seasoned():
    p1 = flat_p1()
    i = 60
    p1["zm_seas"][:, i] = [4, 3, 2, 2, 3, 6]
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_7") == pytest.approx(1 / 3)  # (4 - 2)/(4 + 2)
    assert val(v, ok, i, "F3_8") == pytest.approx(-0.1)  # (9 - 11)/20
    p1["zm_seas"][:, i] = [0, 3, 2, 0, 3, 6]
    p1["zm_seas"][:, i + 1] = np.nan  # book not valid at t
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_7") is None and val(v, ok, i + 1, "F3_8") is None


def test_f3_9_to_f3_11():
    p1 = flat_p1()
    i = 60
    p = gp(i)
    zc = p1["zm_cnt"]
    zc[F.ZI["cra"], p - 1:] = 6
    zc[F.ZI["crb"], p - 1:] = 2
    zc[F.ZI["swb"], p:] = 3
    zc[F.ZI["sws"], p:] = 1
    zc[F.ZI["rfb"], p - 10:] = 4
    zc[F.ZI["rfa"], p:] = 1
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_9") == 0.5  # (6 - 2)/(6 + 2)
    assert val(v, ok, i, "F3_10") == 1.0  # (3 - 1)/2
    assert val(v, ok, i, "F3_11") == 1.0  # (4 - 1)/3


def test_f3_12_lambda():
    p1 = flat_p1()
    i = 100
    p = gp(i)
    q = np.arange(p - 59, p + 1)  # the 60 intervals (q-1, q]
    sv = np.where(q % 3 == 0, 2, np.where(q % 3 == 1, -1, 1))  # signed volume per interval
    zc = p1["zm_cnt"]
    for j, qq in enumerate(q):
        zc[F.ZI["buy"], qq:] += max(sv[j], 0)
        zc[F.ZI["sell"], qq:] += max(-sv[j], 0)
        zc[F.ZI["ntr"], qq:] += 1
    mids = MID["zm"] + 0.5 * np.concatenate([[0], np.cumsum(sv)])  # dM = 0.5 sv
    set_mid(p1, "zm", np.arange(p - 60, p + 1), mids)
    v, ok, _ = feats(p1)  # reference median 0.5
    assert F.lam60_at(p1, p) == pytest.approx(0.5)
    assert val(v, ok, i, "F3_12") == pytest.approx(1.0)  # 0.5/0.5
    zc[F.ZI["ntr"]] = 0  # no trades: fewer than 30 intervals
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F3_12") is None


def test_f4_1_to_f4_5_returns():
    p1 = flat_p1()
    i = 100
    set_mid(p1, "zm", gp(i), MID["zm"] + 6)
    v, ok, _ = feats(p1)  # sigma_ZM 1
    for n, k in zip((1, 2, 3, 4, 5), (1, 5, 15, 30, 60), strict=True):
        assert val(v, ok, i, f"F4_{n}") == pytest.approx(min(6 / math.sqrt(k), 5.0))  # G4 clip


def test_f4_6_range_position():
    p1 = flat_p1()
    i = 30
    lo = float(p1["zm_raw2"][gp(i)])
    p1["zm_hi"][i] = lo + 8 * TICK["ZM"]
    p1["zm_lo"][i] = lo - 0 * TICK["ZM"]
    set_mid(p1, "zm", gp(i), MID["zm"] + 1)  # raw2 + 2 ticks of raw2 units
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F4_6") == pytest.approx(2 / 8)  # (M - Lo)/(Hi - Lo)
    assert val(v, ok, i + 1, "F4_6") == 0.5  # Hi = Lo


def test_f4_7_gap_and_f4_8():
    hist = gap_hist([0.0] * 21, zm_vals=[0.0] + [1.0, -1.0] * 10)  # gaps +-1 tick: sd_gap 1
    p1 = flat_p1()
    set_mid(p1, "zm", F.P_0835, MID["zm"] + 3)  # GAP(D) = 3 ticks / 1
    v, ok, ref = feats(p1, hist=hist)
    assert ref.gap == pytest.approx(3.0)
    assert val(v, ok, 5, "F4_7") == pytest.approx(3.0)
    assert val(v, ok, 5, "C_14") == 1.0  # every F4 feature defined on this row: v4 = 1
    assert val(v, ok, 15, "F4_8") == pytest.approx(3.0 * math.exp(-0.5))
    # ZM front on D differs from the previous date's -> invalid (READING FA-20)
    v, ok, ref = feats(p1, info(fronts=(99, IID_S, IID_L), expiry_dates=30), hist=hist)
    assert ref.gap is None and val(v, ok, 5, "F4_7") is None
    # a roll inside the 20 dates: dates whose front differs from the previous date's drop out
    hist = gap_hist([0.0] * 21, zm_vals=[0.0] + [1.0, -1.0] * 10, front_of=[5] * 11 + [IID] * 10)
    _, _, ref = feats(p1, hist=hist)
    assert ref.counts["gap_values"] == 19 and ref.gap is not None


def test_f4_9_ropen_and_f4_13_late():
    p1 = flat_p1()
    set_mid(p1, "zm", gp(16), MID["zm"] + 8)
    set_mid(p1, "zm", gp(225), MID["zm"] - 15)
    v, ok, _ = feats(p1)
    assert val(v, ok, 0, "F4_9") == 0.0  # 0 at 08:35
    assert val(v, ok, 16, "F4_9") == pytest.approx(2.0)  # 8/(1 x sqrt 16)
    assert val(v, ok, 225, "F4_9") == pytest.approx(-1.0)  # -15/sqrt(225)
    assert val(v, ok, 16, "F4_13") == 0.0  # before 12:15
    assert val(v, ok, 225, "F4_13") == pytest.approx(-1.0)  # 12:20 >= 12:15


def test_f4_10_rv15():
    p1 = flat_p1()
    i = 100
    p = gp(i)
    q = np.arange(p - 15, p + 1)
    set_mid(p1, "zm", q, MID["zm"] + (q - (p - 15)) % 2)  # 15 changes: +1, -1, ... (8 up, 7 down)
    v, ok, _ = feats(p1)
    # mean 1/15; pop SD = sqrt(1 - 1/225) = 0.997775; / sigma 1
    assert val(v, ok, i, "F4_10") == pytest.approx(math.sqrt(1 - 1 / 225))


def test_f4_11_f4_12_burst():
    p1 = flat_p1()
    i = 100
    p = gp(i)
    set_mid(p1, "zm", np.arange(p - 3, p + 1), MID["zm"] + 6)  # step +6 at e* = t - 3
    v, ok, _ = feats(p1)
    # B(e) = (M(e) - M(e - 2))/(1 x sqrt 2): 6/sqrt 2 = 4.2426 for e = t-3 and e = t-2; ties go
    # to the latest e (t-2) -> e* = t-2; DB = 4.2426 (inside the clip); F4.12 = DB exp(-2/5)
    assert val(v, ok, i, "F4_11") == pytest.approx(6 / math.sqrt(2))
    assert val(v, ok, i, "F4_12") == pytest.approx(6 / math.sqrt(2) * math.exp(-2 / 5))
    set_mid(p1, "zm", np.arange(p - 3, p + 1), MID["zm"] + 4)  # 4/sqrt 2 = 2.83 < 3 -> 0
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "F4_11") == 0.0 and val(v, ok, i, "F4_12") == 0.0


def test_c11_to_c14_family_flags():
    # flat world with hist_list: every F2 feature is defined (sigma 2 and 3, zero moves, Obar 10)
    p1 = flat_p1()
    v, ok, _ = feats(p1)
    i = 100
    assert val(v, ok, i, "C_12") == 1.0
    # F1: F1.1 (sd_30 = 0) is invalid -> v1 = 0; the flag is all(valid) of its family (G3)
    assert val(v, ok, i, "C_11") == 0.0 and val(v, ok, i, "F1_1") is None
    # F3: no trades -> TI_5 = 0/0 invalid -> v3 = 0; F4: GAP has sd_gap = 0 (flat 08:35 and
    # 13:15 mids) -> invalid -> v4 = 0
    assert val(v, ok, i, "F3_5") is None and val(v, ok, i, "C_13") == 0.0
    assert val(v, ok, i, "F4_7") is None and val(v, ok, i, "C_14") == 0.0
    for fam, flag in F.FLAG_OF.items():
        k = [F.FI[n] for n in F.FAMILIES[fam]]
        assert np.array_equal(v[:, F.FI[flag]] == 1.0, ok[:, k].all(axis=1))
    p1["zs_ok"][gp(i) - 1] = False  # one ZS mid missing at t - 1 min: F2.1 invalid at row i
    v, ok, _ = feats(p1)
    assert val(v, ok, i, "C_12") == 0.0 and val(v, ok, i, "F2_1") is None
    # the missing mark t_i - 1 is used by rows i - 1 (as t), i (k=1), i + 4 (k=5), i + 14 (k=15)
    bad_rows = [r for r in range(F.N_GRID) if val(v, ok, r, "C_12") == 0.0]
    assert v[i, F.FI["F2_1"]] == 0.0 and bad_rows == [i - 1, i, i + 4, i + 14]


# =========================================================== Part C: G2, G3, G4 ====
def test_g4_clip_lists_exact():
    clipped = {"C_5", "F1_1", "F1_2", "F1_3", "F1_4", "F1_6", "F1_7", "F1_8"} \
        | {f"F2_{k}" for k in range(1, 12)} | {"F3_1", "F3_2", "F3_3", "F3_4", "F3_10", "F3_11",
                                                "F3_12"} \
        | {f"F4_{k}" for k in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13)}
    unclipped = {f"C_{k}" for k in (1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)} \
        | {"F1_5", "F3_5", "F3_6", "F3_7", "F3_8", "F3_9", "F4_6"}
    assert set(F.CLIPPED) == clipped and len(F.CLIPPED) == 38
    assert set(F.UNCLIPPED) == unclipped and len(F.UNCLIPPED) == 21
    assert len(F.FEATURES) == 59 and F.FEATURES[0] == "C_1" and F.FEATURES[-1] == "F4_13"


def test_g4_clip_applied_after_normalisation():
    p1 = flat_p1()
    p1["zs_cnt"][F.MI["ofi"], gp(60):] = 300  # 300/10 = 30 -> 5
    p1["zm_seas"][:, 60] = [9, 0, 0, 1, 0, 0]  # QI1 0.8 unclipped
    v, ok, _ = feats(p1)
    assert val(v, ok, 60, "F2_8") == 5.0 and val(v, ok, 60, "F3_7") == pytest.approx(0.8)
    p1["zs_cnt"][F.MI["ofi"], gp(60):] = -300
    v, ok, _ = feats(p1)
    assert val(v, ok, 60, "F2_8") == -5.0


def test_g3_invalid_is_zero_and_flag():
    p1 = flat_p1()
    hist = hist_list()
    for h, _ in hist:
        h["ref_sw5"][:] = 0.0  # sbar_5 = 0 -> F3.10 invalid on every row
    v, ok, _ = feats(p1, hist=hist)
    assert np.all(v[:, F.FI["F3_10"]] == 0.0) and not ok[:, F.FI["F3_10"]].any()
    assert np.all(v[:, F.FI["C_13"]] == 0.0)


def test_g2_sigma_chains_across_rolls():
    # history dates on other fronts still enter sigma (a scale): every one counts
    hist = [(hist_p1(), info(D - timedelta(days=21 - k), fronts=(100 + k, IID_S, IID_L), seg=k))
            for k in range(21)]
    _, _, ref = feats(flat_p1(), hist=hist)
    assert ref.sigma["zm"] == 1.0
    # fewer than 20 history dates -> sigma undefined (READING FA-15)
    hist[1] = None
    _, _, ref = feats(flat_p1(), hist=hist)
    assert ref.sigma["zm"] is None


def test_g1_pass2_rows_ignore_later_marks():
    p1 = flat_p1()
    hist = hist_list()
    v0, ok0, _ = feats(p1, hist=hist)
    i = 120
    p = gp(i)
    p2 = {k: (a.copy() if isinstance(a, np.ndarray) else a) for k, a in p1.items()}
    for r in ("zm", "zs", "zl"):
        p2[f"{r}_raw2"][p + 1:] += 2 * 37 * TK[r]
        p2[f"{r}_ok"][p + 1:] = False
    for key in ("zm_cnt", "zs_cnt", "zl_cnt"):
        p2[key][:, p + 1:] += 1000
    p2["zm_seas"][:, i + 1:] = np.nan
    p2["zm_hi"][i + 1:] = np.nan
    v1, ok1, _ = feats(p2, hist=hist)
    assert np.array_equal(v0[:i + 1], v1[:i + 1]) and np.array_equal(ok0[:i + 1], ok1[:i + 1])


# =========================================================== Part D: lead rulings FD1-FD5, D1 ====
DP = D - timedelta(days=1)  # the previous trade date in the late-open cases


def early_close_axis() -> F.Axis:
    """D with a 12:05 halt: open (19:00 D-1, 07:45] and (08:30, 12:05] (FD1)."""
    return F.build_axis(D, [(w(19, 0, day=DP), w(7, 45)), (w(8, 30), w(12, 5))])


def late_open_axis() -> F.Axis:
    """D with no overnight session: the previous date's day session (08:30, 13:20] on D-1, then
    D's (08:30, 13:20] (FD2)."""
    return F.build_axis(D, [(w(8, 30), w(13, 20))], (w(8, 30, day=DP), w(13, 20, day=DP)))


def test_fd1_axis_and_closed_minutes_map_to_the_halt():
    ax = early_close_axis()
    assert len(ax.marks) == 765 + 215 and ax.marks[-1] == w(12, 5)  # 08:31 .. 12:05
    i_1230 = 235  # 08:35 + 235 min = 12:30
    assert ax.marks[ax.map_pos[i_1230]] == w(12, 5) and ax.marks[ax.map_pos[210]] == w(12, 5)
    assert ax.marks[ax.map_pos[209]] == w(12, 4)
    # trades at 12:04:30 (open) and 12:20 (closed): the 15-minute window of t = 12:30 is the one
    # ending at 12:05 -> 2 contracts; the 12:20 trade is in closed time and never counted
    rows = opening(w(8, 0)) + [rec(w(12, 4, 30), "T", "B", 4001, 2, 0),
                               rec(w(12, 20), "T", "B", 4001, 9, 0),
                               rec(w(12, 25), "R", "N", 0, 0, 0)]  # book cleared after the halt
    out = F.stream_zm(mbo(rows), IID, ax)
    vol_ax = out["zm_cnt"][F.ZI["vol"]][ax.mark_at]
    p = int(ax.map_pos[i_1230])
    assert F.win(vol_ax, p, 15) == 2 and vol_ax[-1] == 2
    # the axis state at t = 12:30 is the 12:05 state (valid); the wall state as of 12:30 is the
    # cleared book (invalid): instant states (sigma, Dbar) read the wall, windows the axis
    assert out["zm_ok"][ax.mark_at[p]] and not out["zm_ok"][ax.wall_at[i_1230]]
    assert out["zm_seas"][0, i_1230] == out["zm_seas"][0, 210]  # sampled at the 12:05 mark


def test_fd2_late_open_window_reaches_previous_day_session():
    ax = late_open_axis()
    assert ax.n_prev == 290 and len(ax.marks) == 580 and ax.marks[0] == w(8, 31, day=DP)
    p = int(ax.map_pos[0])  # t = 08:35 on D
    assert p == 290 + 4 and ax.marks[p - 5] == w(13, 20, day=DP)  # 5 open minutes back
    t0 = w(8, 0, day=DP)
    rows = opening(t0) + [rec(w(13, 19, 30, day=DP), "T", "A", 4000, 3, 0),
                          rec(w(16, 0, day=DP), "T", "A", 4000, 50, 0),  # closed: not counted
                          rec(w(8, 32), "T", "B", 4001, 1, 0)]
    out = F.stream_zm(mbo(rows), IID, ax)
    vol = out["zm_cnt"][F.ZI["vol"]][ax.mark_at]
    # the 6-minute window ending at 08:35 on D: (13:19 D-1, 13:20 D-1] + (08:30, 08:35] on D
    assert F.win(vol, p, 6) == 3 + 1 and F.win(vol, p, 5) == 1


def late_p1() -> dict:
    """Pass-1 tables of a quiet late-open date on the axis above (crush pattern below)."""
    ax = late_open_axis()
    n = len(ax.marks)
    p1 = {"marks": ax.marks, "wall_ns": ax.wall, "map_pos": ax.map_pos,
          "ax_prev": np.arange(n) < ax.n_prev, "fronts": np.array([IID, IID_S, IID_L]),
          "ticks": np.array([TICK["ZM"], TICK["ZS"], TICK["ZL"]], dtype=np.int64)}
    for r in ("zm", "zs", "zl"):
        p1[f"{r}_raw2"] = np.full(n, int(2 * MID[r] * TK[r]), np.int64)
        p1[f"{r}_ok"] = np.ones(n, bool)
        p1[f"{r}_wraw2"] = p1[f"{r}_raw2"][ax.map_pos].copy()
        p1[f"{r}_wok"] = np.ones(F.N_WALL, bool)
    p1["zm_spread"] = np.full(n, TICK["ZM"], np.int64)
    p1["zm_touch"] = np.full(n, 10, np.int64)
    p1["zm_lvl"] = np.full((F.N_LVL, n), 10, np.int64)
    p1["zm_wlvl"] = np.full((F.N_LVL, F.N_WALL), 10, np.int64)
    p1["zm_seas"] = np.full((6, F.N_GRID), 5.0)
    p1["zm_hi"] = np.full(F.N_GRID, float(p1["zm_raw2"][0]))
    p1["zm_lo"] = p1["zm_hi"].copy()
    p1["zm_cnt"] = np.zeros((len(F.ZC), n), np.int64)
    p1["zs_cnt"] = np.zeros((len(F.MC), n), np.int64)
    p1["zl_cnt"] = np.zeros((len(F.MC), n), np.int64)
    p = int(ax.map_pos[0])
    q = np.arange(p - 120, p)  # ZS ticks +2 on even marks: C alternates C0, C0 - 0.5
    p1["zs_raw2"][q] = np.round(2 * (MID["zs"] + np.where(q % 2 == 0, 2.0, 0.0)) * TK["zs"])
    p1["zs_raw2"][p] = int(2 * (MID["zs"] - 4.0) * TK["zs"])  # C(t) = C0 + 1.0
    return p1


def test_fd2_g2_f1_level_samples_stop_at_the_segment_boundary():
    # the 30 and 120 marks before 08:35 on D are mostly on the previous date: with the previous
    # date in D's segment zC30 = (1.0 + 0.25)/0.25 = 5 (as in test_f1_1); outside it, invalid
    v, ok, _ = feats(late_p1(), info(expiry_dates=30, prev_same_seg=True), do_sync=False)
    assert val(v, ok, 0, "F1_1") == pytest.approx(5.0) and val(v, ok, 0, "F1_2") == pytest.approx(5.0)
    v, ok, _ = feats(late_p1(), info(expiry_dates=30, prev_same_seg=False), do_sync=False)
    assert val(v, ok, 0, "F1_1") is None and val(v, ok, 0, "F1_2") is None
    assert val(v, ok, 0, "F2_1") is not None  # only F1 level quantities are segment-bound (G2)


def test_fd3a_first_update_after_a_skipped_interval_has_no_term():
    # overnight: snapshot at 19:00:30 (first update of (19:00, 07:45]: no term), one update at
    # 20:00 (+3, a term). Day: the pre-open state at 08:20 (pause), first day update 08:30:10 (no
    # term although both states are two-sided), second at 08:31:10 (+2, a term)
    t0 = w(19, 0, 30, day=DP)
    rows = opening(t0) + [rec(w(20, 0, day=DP), "A", "B", 4000, 3, 3),  # bid 8: e = 8 - 5 = +3
                          rec(w(8, 20), "A", "A", 4000, 2, 4),  # locks the book in the pause
                          rec(w(8, 30, 10), "C", "A", 4000, 2, 4),  # unlock: first day update
                          rec(w(8, 31, 10), "A", "B", 4000, 2, 5)]  # bid 10: e = 10 - 8 = +2
    c = zm_out(rows)["zm_cnt"]
    assert c[F.ZI["ofi"], F.P_J] == 3 and c[F.ZI["ofi_bad"], F.P_J] == 0
    p = p_of(8, 32)
    assert F.win(c[F.ZI["ofi"]], p, 5) == 2 and F.win(c[F.ZI["ofi_bad"]], p, 5) == 0
    assert F.win(c[F.ZI["ofi"]], p, 3) == 2  # (07:44, 08:32] on the axis: valid, sum 2


def test_fd3b_term_with_a_missing_side_makes_the_window_invalid_and_3c_crossed_counts():
    rows = opening(w(8, 0)) + [rec(w(8, 31, 10), "N", "N", 0, 0, 0),
                               rec(w(8, 33, 10), "A", "B", 4002, 1, 3),  # crossed: bid 4002 > 4001
                               rec(w(8, 35, 10), "C", "A", 4001, 7, 2)]  # ask side empty
    c = zm_out(rows)["zm_cnt"]
    # crossed state: e = 1{4002>=4000} 1 - 0 - 1{4001<=4001} 7 + 1{4001>=4001} 7 = 1 (FD3 c)
    assert F.win(c[F.ZI["ofi"]], p_of(8, 34), 1) == 1 and F.win(c[F.ZI["ofi_bad"]], p_of(8, 34), 1) == 0
    assert F.win(c[F.ZI["ofi_bad"]], p_of(8, 36), 1) == 1  # (FD3 b): the window is invalid
    p1 = flat_p1()
    p1["zm_cnt"] = np.zeros_like(p1["zm_cnt"])
    p1["zm_cnt"][:, :] = 0
    p1["zm_cnt"][F.ZI["ofi_bad"], gp(5):] = 1
    v, ok, _ = feats(p1)
    assert val(v, ok, 5, "F3_1") is None and val(v, ok, 4, "F3_1") == 0.0


def test_fd4_refill_opens_where_the_touch_reaches_zero_through_fills():
    t0, ts = w(8, 0), w(8, 40, 10)
    base = [rec(t0, "R", "N", 0, 0, 0, fl=0), rec(t0, "A", "B", 4000, 5, 1, fl=0),
            rec(t0, "A", "A", 4001, 3, 2, fl=0), rec(t0, "A", "A", 4002, 4, 3, fl=0),
            rec(t0, "A", "A", 4003, 6, 9)]
    # a buy of 7 takes 4001 (3) and 4002 (4): 4002 becomes the touch inside the sweep and is
    # emptied by fills too -> windows at both levels; an add at 4001 later in the same batch
    # counts; an add at 4002 50 ms later counts; one at 4002 200 ms later does not
    rows = base + [rec(ts, "T", "B", 4002, 7, 0, fl=0), rec(ts, "F", "A", 4001, 3, 2, fl=0),
                   rec(ts, "F", "A", 4002, 4, 3, fl=0), rec(ts, "C", "A", 4001, 3, 2, fl=0),
                   rec(ts, "C", "A", 4002, 4, 3, fl=0), rec(ts, "A", "A", 4001, 1, 10),
                   rec(ts + 50_000_000, "A", "A", 4002, 1, 11),
                   rec(ts + 200_000_000, "A", "A", 4002, 1, 12)]
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["rfa"]], p_of(8, 41), 1) == 2 and F.win(c[F.ZI["rfb"]], p_of(8, 41), 1) == 0
    # a touch level whose last lots are cancelled (fill 1 of 3, then the rest cancelled in the
    # batch) does not open a window: the add at 4001 right after is not a refill
    rows = base + [rec(ts, "T", "B", 4001, 1, 0, fl=0), rec(ts, "F", "A", 4001, 1, 2, fl=0),
                   rec(ts, "M", "A", 4001, 2, 2, fl=0), rec(ts, "C", "A", 4001, 2, 2),
                   rec(ts + 10_000_000, "A", "A", 4001, 1, 10)]
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["rfa"]], p_of(8, 41), 1) == 0
    assert F.win(c[F.ZI["cra"]], p_of(8, 41), 1) == 2  # the cancelled 2 lots are a removal


def test_fd5_fill_lots_do_not_carry_across_batches():
    # an F record whose order is not reduced in its batch (iceberg-style refresh), then a
    # voluntary cancel in a later batch: the cancel is a removal (Ca = 7)
    rows = opening(w(8, 0)) + [rec(w(8, 40, 10), "T", "B", 4001, 2, 0, fl=0),
                               rec(w(8, 40, 10), "F", "A", 4001, 2, 2, fl=0),
                               rec(w(8, 40, 10), "M", "A", 4001, 7, 2),  # size kept (refresh)
                               rec(w(8, 40, 20), "C", "A", 4001, 7, 2)]
    c = zm_out(rows)["zm_cnt"]
    assert F.win(c[F.ZI["cra"]], p_of(8, 41), 1) == 7


def test_d1_r_carrying_bad_flag_leaves_the_book_bad():
    rows = opening(w(8, 0)) + [rec(w(8, 40, 10), "R", "N", 0, 0, 0, fl=BADF),
                               rec(w(8, 40, 10), "A", "B", 4000, 5, 1, fl=0),
                               rec(w(8, 40, 10), "A", "A", 4001, 7, 2)]
    out = zm_out(rows)
    assert out["zm_ok"][p_of(8, 40)] and not out["zm_ok"][p_of(8, 41)]
    rows[-3] = rec(w(8, 40, 10), "R", "N", 0, 0, 0, fl=0)  # the same R without the flag
    assert zm_out(rows)["zm_ok"][p_of(8, 41)]


def test_builder_decision_times_are_wall_minutes_on_any_axis():
    # t_ns of row i is 08:35 + i min on D whatever the axis (late open, early close, regular)
    import build_features33 as B  # noqa: PLC0415

    src = inspect.getsource(B.pass2)
    assert 'cur[0]["wall_ns"][:F.N_GRID]' in src and "GRID_P" not in src
    for ax in (late_open_axis(), early_close_axis(), AX):
        assert ax.wall[0] == w(8, 35) and ax.wall[F.N_GRID - 1] == w(13, 7)
