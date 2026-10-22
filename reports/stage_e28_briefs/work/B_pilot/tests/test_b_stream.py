"""The streaming reduction: data checks of spec section 2 and the day grouping."""

from datetime import date
from types import SimpleNamespace

import numpy as np
import pilot_common as pc
import pilot_stream as ps
import pytest
from b_helpers import MS, G, J, S, Tape, book_from, main_plan, records


def test_bad_flag_records_are_dropped_and_counted():
    tape = Tape(bid=100, ask=101, bsz=2, asz=2).quote(G - S)
    tape.rows.append({"t": G, "action": "A", "bid": 103, "ask": 99, "bsz": 1, "asz": 1,
                      "flags": ps.F_MAYBE_BAD_BOOK})
    tape.rows.append({"t": G + 10 * MS, "action": "A", "bid": 103, "ask": 99, "bsz": 1,
                      "asz": 1, "flags": ps.F_BAD_TS_RECV})
    book = book_from(tape)
    assert book.counts["dropped_maybe_bad_book"] == 1
    assert book.counts["dropped_bad_ts_recv"] == 1
    assert book.counts["dropped_bad_flag_records"] == 2
    assert book.chg_ts.tolist() == [G - S]  # the bad crossed states never enter the book
    assert bool(book.j_valid[0]) and int(book.j_bid[0]) == 100


def test_size_only_records_are_reduced_but_join_sizes_kept():
    tape = Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - 3 * S)
    for k in range(10):
        tape.quote(G - 2 * S + k * 100 * MS, bsz=k + 2)
    book = book_from(tape)
    assert len(book.chg_ts) == 1  # prices and validity never changed
    assert int(book.j_bsz[0]) == 11
    assert book.counts["records"] == 11


def test_crossed_locked_empty_records_counted_and_timed():
    plan = main_plan(lo=G - 10 * S, hi=G + 50 * S)
    tape = (Tape(bid=100, ask=101).quote(G - 10 * S).quote(G, bid=101, ask=100)
            .quote(G + 2 * S, bid=100, ask=100).quote(G + 5 * S, bid=100, ask=None, asz=0)
            .quote(G + 6 * S, bid=100, ask=101, asz=1))
    book = book_from(tape, plan)
    assert book.counts["records_crossed"] == 1
    assert book.counts["records_locked"] == 1
    assert book.counts["records_empty_side"] == 1
    assert book.invalid_ns[pc.MAIN] == 6 * S  # crossed 2 s + locked 3 s + empty 1 s


def test_inversions_are_counted_and_time_axis_is_monotone():
    rows = [{"t": G - 2 * S, "action": "A", "bid": 100, "ask": 101, "bsz": 1, "asz": 1,
             "seq": 10, "recv": G - 2 * S},
            {"t": G - 1 * S, "action": "A", "bid": 100, "ask": 102, "bsz": 1, "asz": 1,
             "seq": 9, "recv": G - 1 * S + 5},
            {"t": G - 3 * S, "action": "A", "bid": 99, "ask": 102, "bsz": 1, "asz": 1,
             "seq": 11, "recv": G - 1 * S + 9}]
    book = book_from(records(rows))
    assert book.counts["sequence_inversions"] == 1
    assert book.counts["ts_event_inversions"] == 1
    assert book.counts["ts_event_raised_to_running_max"] == 1
    assert np.all(np.diff(book.chg_ts) >= 0)


def test_records_out_of_ts_recv_order_inside_a_segment_are_sorted():
    rows = [{"t": G - 2 * S, "action": "A", "bid": 100, "ask": 101, "bsz": 1, "asz": 1,
             "recv": G - S, "seq": 2},
            {"t": G - 3 * S, "action": "A", "bid": 99, "ask": 101, "bsz": 1, "asz": 1,
             "recv": G - 2 * S, "seq": 1}]
    book = book_from(records(rows))
    assert book.counts["records_reordered"] == 2
    assert int(book.j_bid[0]) == 100  # the later-received record is the state at the join


def test_main_gap_tracks_edges_and_interior():
    lo, hi = G - 100 * S, G + 100 * S
    plan = main_plan(lo=lo, hi=hi)
    tape = Tape().quote(lo + 10 * S).quote(lo + 80 * S).quote(hi - 30 * S)
    book = book_from(tape, plan, segments=3)
    # gaps: 10 s from the edge, 70 s, 90 s (lo+80 -> hi-30 is 90 s), 30 s to the end
    assert book.main_max_gap_ns == 90 * S
    assert book.main_records == 3


def test_off_tick_prices_are_counted():
    tape = Tape().quote(G - S)
    tape.rows[0]["bid"] = 100
    arr = records(tape.rows)
    arr["bid_px_00"][0] += 1  # one 1e-9 unit off the tick
    book = book_from(arr)
    assert book.counts["off_tick_prices"] == 1


def test_trades_without_a_price_are_dropped():
    tape = Tape().quote(G - S)
    tape.rows.append({"t": J + S, "action": "T", "price": None, "size": 3, "side": "A",
                      "bid": 100, "ask": 101, "bsz": 1, "asz": 1})
    book = book_from(tape)
    assert book.counts["trades_undefined_price_dropped"] == 1 and len(book.tr_ts) == 0


def test_tick_units():
    assert ps.tick_units(0.25) == 250_000_000
    assert ps.tick_units(1 / 64) == 15_625_000
    assert ps.tick_units(0.00005) == 50_000
    with pytest.raises(ValueError):
        ps.tick_units(0.0)
    with pytest.raises(ValueError):
        ps.tick_units(1e-10)


# ------------------------------------------------------------------ day grouping ----
def _fake_store(chunks, start, end):
    return SimpleNamespace(metadata=SimpleNamespace(start=start, end=end),
                           to_ndarray=lambda count: iter(chunks))


def test_iter_days_groups_by_ts_recv_at_16_ct_and_counts_late_records():
    cal = pc.calendar_for("ES")
    d1, d2 = date(2023, 11, 14), date(2023, 11, 15)
    b1 = pc.day_window_ns(d1)[1]  # 2023-11-14 16:00 CT: d2's window starts here
    rows1 = [{"t": b1 - 3600 * S, "recv": b1 - 3600 * S, "bid": 100, "ask": 101, "bsz": 1,
              "asz": 1}]
    rows2 = [{"t": b1 + 10 * S, "recv": b1 + 10 * S, "bid": 100, "ask": 101, "bsz": 1,
              "asz": 1}]
    late = [{"t": b1 - 100 * S, "recv": b1 - 100 * S, "bid": 100, "ask": 101, "bsz": 1,
             "asz": 1}]
    chunks = [records(rows1 + rows2), records(late)]
    stats = ps.FileStats()
    store = _fake_store(chunks, pc.bound_ns(pc.start_bound(d1)), b1 + 86_400 * S)
    books = list(ps.iter_days(store, lambda d: pc.build_day_plan(cal, d), lambda d: True,
                              250_000_000, stats=stats))
    assert [b.day for b in books] == [d1, d2]
    assert [b.counts["records"] for b in books] == [1, 1]
    assert stats.late_records_dropped == 1
    assert stats.records == 3 and stats.days_seen == [d1.isoformat(), d2.isoformat()]


def test_iter_days_skips_unwanted_days():
    cal = pc.calendar_for("ES")
    d1 = date(2023, 11, 14)
    b1 = pc.day_window_ns(d1)[1]
    rows = [{"t": b1 - 3600 * S, "recv": b1 - 3600 * S, "bid": 100, "ask": 101, "bsz": 1,
             "asz": 1},
            {"t": b1 + 10 * S, "recv": b1 + 10 * S, "bid": 100, "ask": 101, "bsz": 1, "asz": 1}]
    store = _fake_store([records(rows)], pc.bound_ns(pc.start_bound(d1)), b1 + 86_400 * S)
    books = list(ps.iter_days(store, lambda d: pc.build_day_plan(cal, d), lambda d: d != d1,
                              250_000_000))
    assert [b.day for b in books] == [date(2023, 11, 15)]
