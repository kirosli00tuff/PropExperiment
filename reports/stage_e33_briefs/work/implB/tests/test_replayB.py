"""Implementation B: hand-built known-answer tests of the replay and window machinery
(synthetic records only; no market data)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import calB  # noqa: E402
import dayB  # noqa: E402
import mbo_book31 as mb  # noqa: E402
import replayB as rb  # noqa: E402

NS, MS = 1_000_000_000, 1_000_000
T0 = 1_644_900_000 * NS
SNAP, LAST, BAD = mb.F_SNAPSHOT, mb.F_LAST, mb.F_MAYBE_BAD_BOOK
P = 1_000_000_000  # one price unit (1e-9 scale): price 100 -> 100 * P


def mbo(rows: list[tuple]) -> np.ndarray:
    """rows: (ts_recv, ts_event, action, side, price, size, order_id, flags)."""
    arr = np.zeros(len(rows), dtype=dayB.m31.MBO_COMPACT)
    for k, (ts, te, act, side, px, sz, oid, fl) in enumerate(rows):
        arr[k] = (ts, te, 1, oid, px * P, sz, fl, ord(act), ord(side), k)
    return arr


def scenario() -> np.ndarray:
    t = T0
    return mbo([
        (t, t, "R", "N", 0, 0, 0, SNAP),
        (t, t, "A", "B", 100, 10, 1, SNAP),
        (t, t, "A", "A", 101, 5, 2, SNAP | LAST),                      # update 0
        (t + 1 * NS, t + 1 * NS, "A", "B", 99, 7, 3, LAST),            # update 1
        (t + 2 * NS, t + 2 * NS, "C", "B", 100, 4, 1, LAST),           # update 2: removal bid 4
        (t + 3 * NS, t + 3 * NS, "T", "B", 101, 5, 0, 0),
        (t + 3 * NS, t + 3 * NS, "F", "A", 101, 5, 2, 0),
        (t + 3 * NS, t + 3 * NS, "C", "A", 101, 5, 2, LAST),           # update 3: buy sweep
        (t + 3 * NS + 50 * MS, t + 3 * NS + 50 * MS, "A", "A", 101, 3, 4, LAST),   # refill
        (t + 3 * NS + 150 * MS, t + 3 * NS + 150 * MS, "A", "A", 101, 2, 5, LAST),  # too late
        (t + 4 * NS, t + 4 * NS, "M", "B", 98, 7, 3, LAST),            # off-touch price change
        (t + 5 * NS, t + 5 * NS, "M", "B", 100, 2, 1, LAST),           # touch reduction 6 -> 2
    ])


def test_book_updates_levels_and_validity() -> None:
    z = rb.replay_zm(scenario())
    bk = z.book
    assert len(bk.ts) == 8
    assert bk.bpx[0, 0] == 100 * P and bk.bq[0, 0] == 10 and bk.apx[0, 0] == 101 * P
    assert bk.bpx[1, :2].tolist() == [100 * P, 99 * P] and bk.bq[1, :2].tolist() == [10, 7]
    assert bk.bpx[1, 2] == rb.NOPX and bk.bq[1, 2] == 0
    assert bk.bq[2, 0] == 6
    assert bool(bk.valid[2]) and not bool(bk.valid[3])  # no ask after the sweep
    assert bool(bk.valid[4]) and bk.aq[4, 0] == 3
    assert bk.aq[5, 0] == 5
    assert bk.bpx[6, 1] == 98 * P


def test_removals_fills_are_not_removals() -> None:
    z = rb.replay_zm(scenario())
    # F3.9: C of 4 at the bid touch and the size-reducing modify 6 -> 2 at the touch; the
    # fill-driven C of the ask and the off-touch price change are not counted
    assert z.rem_side.tolist() == [0, 0]
    assert z.rem_qty.tolist() == [4, 4]
    assert z.rem_ts.tolist() == [T0 + 2 * NS, T0 + 5 * NS]


def test_sweep_and_refill() -> None:
    z = rb.replay_zm(scenario())
    assert z.sweep_dir.tolist() == [1] and z.sweep_ts.tolist() == [T0 + 3 * NS]  # F3.10
    assert z.refill_side.tolist() == [1]  # F3.11: the add 50 ms after, not the one at 150 ms
    assert z.refill_ts.tolist() == [T0 + 3 * NS + 50 * MS]


def test_trades_and_seasoned_depth() -> None:
    q = np.array([T0 + 5 * NS + 500 * MS, T0 + 6 * NS + 100 * MS], np.int64)
    z = rb.replay_zm(scenario(), q)
    assert z.trade_sz.tolist() == [5] and z.trade_side.tolist() == [ord("B")]
    # at q0 the touch bid order (modified at T0+5s) is 0.5 s old: not seasoned; level 2 (98,
    # moved at T0+4s) is; ask 101: orders added at 3.05 s and 3.15 s are seasoned
    assert z.season_q[0, 0].tolist() == [0, 7, 0]
    assert z.season_q[0, 1].tolist() == [5, 0, 0]
    assert z.season_q[1, 0].tolist() == [2, 7, 0]
    assert z.season_ok.tolist() == [True, True]


def test_records_before_start_and_bad_flag() -> None:
    t = T0
    rec = mbo([(t, t, "A", "B", 100, 1, 9, LAST),
               (t + NS, t + NS, "R", "N", 0, 0, 0, SNAP),
               (t + NS, t + NS, "A", "B", 100, 1, 1, SNAP),
               (t + NS, t + NS, "A", "A", 102, 1, 2, SNAP | LAST),
               (t + 2 * NS, t + 2 * NS, "A", "B", 99, 1, 3, LAST | BAD),
               (t + 3 * NS, t + 3 * NS, "A", "B", 98, 1, 4, LAST)])
    z = rb.replay_zm(rec)
    assert z.counts["before_start"] == 1
    assert z.book.valid.tolist() == [False, True, False, False]  # bad until the next R


def test_season_capture_uses_last_complete_event() -> None:
    t = T0
    rec = mbo([(t, t, "R", "N", 0, 0, 0, SNAP),
               (t, t, "A", "B", 100, 4, 1, SNAP),
               (t, t, "A", "A", 101, 4, 2, SNAP | LAST),
               (t + 3 * NS, t + 3 * NS, "A", "B", 100, 6, 3, 0),     # mid-event at the query
               (t + 5 * NS, t + 5 * NS, "A", "A", 101, 1, 4, LAST)])
    z = rb.replay_zm(rec, np.array([t + 4 * NS], np.int64))
    assert z.season_q[0, 0, 0] == 4  # as of t+4s: the state after the first F_LAST only


def test_mbp_arrays_validity() -> None:
    arr = np.zeros(4, dtype=dayB.data33.MBP1_SPLIT)
    arr["ts_recv"] = T0 + np.arange(4) * NS
    arr["bid_px_00"] = [100 * P, 100 * P, mb.UNDEF_PRICE, 100 * P]
    arr["ask_px_00"] = [101 * P, 101 * P, 101 * P, 100 * P]
    arr["bid_sz_00"], arr["ask_sz_00"] = 3, 4
    arr["flags"] = [BAD, LAST, LAST, LAST]
    arr["action"] = [ord("A"), ord("T"), ord("C"), ord("A")]
    arr["size"] = [0, 2, 0, 0]
    m = rb.mbp_arrays(arr)
    assert m.book.valid.tolist() == [False, False, False]  # bad event, empty bid, locked
    assert m.trade_sz.tolist() == [2]


def _book(px_b: list, q_b: list, px_a: list, q_a: list, notbad: list | None = None,
          ts: list | None = None) -> rb.BookArrays:
    n = len(px_b)
    bk = rb._empty_book(n)
    bk.ts[:] = ts if ts is not None else np.arange(n)
    bk.bpx[:, 0], bk.bq[:, 0], bk.apx[:, 0], bk.aq[:, 0] = px_b, q_b, px_a, q_a
    bk.notbad[:] = True if notbad is None else notbad
    bk.valid[:] = bk.notbad & (bk.bpx[:, 0] != rb.NOPX) & (bk.apx[:, 0] != rb.NOPX) & (
        bk.bpx[:, 0] < bk.apx[:, 0])
    return bk


def test_ofi_terms_known_answer() -> None:
    bk = _book([100, 100, 101, 100], [5, 7, 2, 9], [102, 102, 102, 101], [4, 4, 6, 3])
    e, ok = dayB.ofi_terms(bk)
    # n=1: bid same price 7-5=+2; ask same 4-4=0 -> 2
    # n=2: bid up: +2; ask same: -(6-4) = -2 -> 0
    # n=3: bid down: -2; ask down: -3 -> -5
    assert e.tolist() == [0, 2, 0, -5] and ok.tolist() == [False, True, True, True]


def test_fd3c_crossed_two_sided_state_uses_literal_formula() -> None:
    # state 1 is crossed (bid 103 > ask 102) but two-sided and not bad: literal e_n
    bk = _book([100, 103, 100], [5, 7, 2], [102, 102, 102], [4, 6, 3])
    e, ok = dayB.ofi_terms(bk)
    assert not bk.valid[1]  # no mid (P0.3) ...
    assert ok.tolist() == [False, True, True]  # ... but both terms are computable (FD3 c)
    # n=1: bid up +7; ask same price -(6-4) = -2 -> 5.  n=2: bid down -7; ask same -(3-6) = +3
    assert e.tolist() == [0, 5, -4]


def test_fd3b_one_sided_or_bad_states_cannot_be_computed() -> None:
    bk = _book([100, rb.NOPX, 100, 100, 100], [5, 0, 5, 5, 6], [102, 102, 102, 102, 102],
               [4, 4, 4, 4, 4], notbad=[True, True, True, False, True])
    e, ok = dayB.ofi_terms(bk)
    # terms 1 and 2 touch the bid-less state 1; terms 3 and 4 touch the bad state 3
    assert ok.tolist() == [False, False, False, False, False]
    assert e.tolist() == [0, 0, 0, 0, 0]


def _pause_book(d: date, mid_state: tuple) -> rb.BookArrays:
    """Updates at 07:44:30 (open), 08:10 (pause), 08:31, 08:33 (open)."""
    ts = [calB.ct(d, 7, 44) + 30 * NS, calB.ct(d, 8, 10), calB.ct(d, 8, 31), calB.ct(d, 8, 33)]
    b, qb, nb = mid_state
    return _book([100, b, 100, 101], [5, qb, 8, 2], [102, 102, 102, 102], [4, 4, 4, 4],
                 notbad=[True, nb, True, True], ts=ts)


def test_fd3a_first_update_after_the_pause_never_enters_a_sum() -> None:
    d = date(2022, 2, 15)
    ax = calB.OpenAxis.of([calB.prev_trade_date(d), d])
    p0835 = ax.pos(np.array([calB.ct(d, 8, 35)]))
    for state in ((100, 5, True), (rb.NOPX, 0, True), (100, 5, False)):
        bk = _pause_book(d, state)
        inc = dayB.ofi_included(ax, bk.ts)
        assert inc.tolist() == [False, False, False, True]  # 07:44:30 is the stream's first
        ow = dayB.OfiWindows(ax, bk, 1)
        s5, ok5 = ow.at(p0835, 5)
        # only the 08:33 term: bid up +2, ask same 4-4 = 0 -> +2, valid whatever the pause state
        assert s5.tolist() == [2] and ok5.tolist() == [True]
        s15, ok15 = ow.at(p0835, 15)
        assert s15.tolist() == [2] and ok15.tolist() == [True]


def test_fd3b_window_with_an_uncomputable_term_is_invalid() -> None:
    d = date(2022, 2, 15)
    ax = calB.OpenAxis.of([calB.prev_trade_date(d), d])
    ts = [calB.ct(d, 9, 0), calB.ct(d, 9, 1), calB.ct(d, 9, 2), calB.ct(d, 9, 3)]
    bk = _book([100, rb.NOPX, 100, 100], [5, 0, 5, 6], [102, 102, 102, 102], [4, 4, 4, 4],
               ts=ts)
    ow = dayB.OfiWindows(ax, bk, 1)
    ends = ax.pos(np.array([calB.ct(d, 9, 2), calB.ct(d, 9, 3), calB.ct(d, 9, 10)]))
    s1, ok1 = ow.at(ends, 1)
    assert ok1.tolist() == [False, True, True]  # 09:02 term follows the bid-less state
    assert s1[1] == 1 and s1[2] == 0  # 09:03 term: bid same +1; (09:09, 09:10] holds no term
    s5, ok5 = ow.at(ends[2:], 10)
    assert ok5.tolist() == [False]


def test_open_axis_skips_pause_and_windows() -> None:
    d = date(2022, 2, 15)
    ax = calB.OpenAxis.of([d])
    p0835 = ax.pos(np.array([calB.ct(d, 8, 35)]))[0]
    p0830 = ax.pos(np.array([calB.ct(d, 8, 30)]))[0]
    p0745 = ax.pos(np.array([calB.ct(d, 7, 45)]))[0]
    assert p0835 - p0830 == 5 * calB.MIN_NS and p0830 == p0745
    wall, pos, _ = ax.marks()
    k = int(np.searchsorted(pos, p0835 - 6 * calB.MIN_NS))
    assert wall[k] == calB.ct(d, 7, 44)  # t - 6 open minutes from 08:35
    assert wall[k + 1] == calB.ct(d, 7, 45)  # B-OPEN-1: the shared point is 07:45:00
    assert wall[k + 2] == calB.ct(d, 8, 31) and np.all(np.diff(pos) == calB.MIN_NS)
    ts = np.array([calB.ct(d, 7, 44) + NS, calB.ct(d, 8, 0), calB.ct(d, 8, 31)], np.int64)
    w = dayB.Windows(ax, ts, np.array([1, 10, 100]))
    # window of 15 open minutes ending 08:35: 07:40..07:45 and 08:30..08:35; the 08:00 record
    # lies in the pause and is not counted
    assert int(w.at(np.array([p0835]), 15)[0]) == 101


def test_open_axis_early_close() -> None:
    d = date(2021, 11, 26)  # early halt 12:05, scheduled late open 08:30
    ax = calB.OpenAxis.of([calB.prev_trade_date(d), d])
    p1230 = ax.pos(np.array([calB.ct(d, 12, 30)]))[0]
    p1204 = ax.pos(np.array([calB.ct(d, 12, 4)]))[0]
    assert p1230 - p1204 == calB.MIN_NS
    p0830 = ax.pos(np.array([calB.ct(d, 8, 30)]))[0]
    p_prev = ax.pos(np.array([calB.ct(date(2021, 11, 24), 13, 19)]))[0]
    assert p0830 - p_prev == calB.MIN_NS  # the late open joins the previous day session


def test_mid2_asof_and_sample_columns() -> None:
    bk = rb._empty_book(3)
    bk.ts[:] = [10, 20, 30]
    bk.valid[:] = [True, False, True]
    bk.bpx[:, 0] = [100, 100, 104]
    bk.apx[:, 0] = [102, 102, 106]
    m2, ok, _ = dayB.mid2_asof(bk, np.array([5, 10, 25, 99]))
    assert ok.tolist() == [False, True, False, True]
    assert m2.tolist() == [0, 202, 0, 210]


def test_lam60_known_slope() -> None:
    d = date(2022, 2, 15)
    ax = calB.OpenAxis.of([d])
    wall, pos, kint = ax.marks()
    g = calB.grid_ns(d, 3)
    out = {"mark_pos": pos, "grid_pos": ax.pos(g)}
    # signed volume x_j in minute j and the mid moves 0.5 x_j ticks in the same minute
    rng = np.random.default_rng(1)
    x = rng.integers(-6, 7, size=len(wall))
    x[x == 0] = 1
    ticks = np.concatenate([[0], np.cumsum(0.5 * x[1:])])
    out["mark_zm"] = (2 * (400 * P + ticks * 1e8)).astype(np.int64)
    out["mark_zm_ok"] = np.ones(len(wall), bool)
    gi = np.searchsorted(wall, g)
    out["g_zm"], out["g_zm_ok"] = out["mark_zm"][gi], np.ones(3, bool)
    tr_ts = wall[1:] - NS  # one trade per minute, inside minute (wall[k-1], wall[k]]
    side = np.where(x[1:] > 0, ord("B"), ord("A")).astype(np.uint8)

    class Z:
        trade_ts, trade_sz, trade_side = tr_ts, np.abs(x[1:]).astype(np.int64), side

    dayB._lam60(out, ax, g, out["grid_pos"], Z, 100_000_000)
    assert np.allclose(out["lam60"], 0.5, rtol=0, atol=1e-12)


def test_season_query_before_start_is_invalid() -> None:
    z = rb.replay_zm(scenario(), np.array([T0 - NS], np.int64))
    assert z.season_ok.tolist() == [False]


@pytest.mark.parametrize("bad", [True])
def test_mbp_bad_flag_any_record_of_event(bad: bool) -> None:
    arr = np.zeros(3, dtype=dayB.data33.MBP1_SPLIT)
    arr["ts_recv"] = T0 + np.arange(3)
    arr["bid_px_00"], arr["ask_px_00"] = 100 * P, 101 * P
    arr["flags"] = [BAD if bad else 0, 0, LAST]
    assert rb.mbp_arrays(arr).book.valid.tolist() == [not bad]


def _zm_arrays(ts: list, bid: list, ask: list, valid: list) -> rb.ZMArrays:
    bk = rb._empty_book(len(ts))
    bk.ts[:] = ts
    bk.valid[:] = valid
    bk.bpx[:, 0], bk.apx[:, 0] = bid, ask
    bk.bq[:, 0], bk.aq[:, 0] = 1, 1
    e64, e8 = np.zeros(0, np.int64), np.zeros(0, np.int8)
    return rb.ZMArrays(bk, e64, e64, np.zeros(0, np.uint8), e64, e8, e64, e64, e8, e64, e8,
                       np.zeros((279, 2, 3), np.int64), np.zeros(279, bool), {})


def test_compute_day_junction_sample_is_0745_state() -> None:
    """B-OPEN-1: for t = 08:35 the sample at t - 5 open minutes is the state as of 07:45:00,
    not the pre-open state as of 08:30:00."""
    d = date(2022, 2, 15)
    ax = calB.OpenAxis.of([calB.prev_trade_date(d), d])
    ts = [calB.ct(d, 7, 40), calB.ct(d, 8, 0), calB.ct(d, 8, 32)]
    zm = _zm_arrays(ts, [400 * P, 402 * P, 401 * P], [401 * P, 400 * P, 402 * P],
                    [True, False, True])
    out = dayB.compute_day(d, ax, dayB.data33.window(d)[0], calB.grid_ns(d), zm, None, None,
                           {"ZM": 100_000_000, "ZS": 250_000_000, "ZL": 10_000_000},
                           (None, None, None), None)
    m2, ok = dayB.sample(out, "zm", 10)
    assert bool(ok[0, 0]) and m2[0, 0] == 803 * P  # 08:35: the 08:32 state
    assert bool(ok[0, 5]) and m2[0, 5] == 801 * P  # t - 5 = 07:45:00 state (valid)
    assert bool(ok[0, 2]) and m2[0, 2] == 803 * P  # t - 2 = 08:33
    assert not bool(ok[0, 4])  # t - 4 = 08:31: the pre-open crossed state
    assert out["zm0830_ok"] is False or not out["zm0830_ok"]
