"""mbo_book31: book rebuild (add, cancel, modify priority rules; snapshot clear and rebuild),
TOP set and lost, CME's TOP Max examples E6/E7 and the E2 display-quantity refresh."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mbo_book31 as mb  # noqa: E402

B, S = mb.BID, mb.ASK


def ids(book, side, price):
    return [oid for oid, _, _ in book.queue(side, price)]


def started(top_min=1, top_max=100, count_initial=False):
    book = mb.Book(top_min, top_max, count_initial)
    book.clear(snapshot=False)
    return book


def test_add_cancel_and_level_totals():
    book = started()
    book.add(1, B, 100, 5)
    book.add(2, B, 100, 3)
    book.add(3, B, 99, 4)
    book.add(4, S, 101, 2)
    assert book.best(B) == 100 and book.best(S) == 101
    assert book.level_total(B, 100) == 8 and ids(book, B, 100) == [1, 2]
    book.cancel(1, 2)  # partial: keeps priority
    assert ids(book, B, 100) == [1, 2] and book.level_total(B, 100) == 6
    book.cancel(1, 3)  # the rest: leaves
    assert ids(book, B, 100) == [2]
    book.cancel(2, 3)
    assert book.best(B) == 99 and 100 not in book.levels[B]
    assert book.is_valid()


def test_modify_size_decrease_keeps_priority_increase_loses_it():
    book = started()
    for oid in (1, 2, 3):
        book.add(oid, B, 100, 5)
    book.modify(1, B, 100, 2)
    assert ids(book, B, 100) == [1, 2, 3] and book.level_total(B, 100) == 12
    book.modify(1, B, 100, 6)
    assert ids(book, B, 100) == [2, 3, 1] and book.level_total(B, 100) == 16


def test_modify_price_change_goes_to_back_of_new_level():
    book = started()
    book.add(1, B, 100, 5)
    book.add(2, B, 99, 5)
    book.add(3, B, 99, 5)
    book.modify(1, B, 99, 5)
    assert ids(book, B, 99) == [2, 3, 1] and 100 not in book.levels[B]


def test_modify_unknown_is_add_and_unknown_cancel_is_counted():
    book = started()
    book.modify(9, S, 105, 4)
    assert ids(book, S, 105) == [9]
    book.cancel(77, 1)
    assert book.anomalies == {"modify_unknown_order_as_add": 1, "cancel_unknown_order": 1}


def test_snapshot_clear_and_rebuild_keeps_file_priority():
    book = started()
    book.add(1, B, 100, 5)
    book.clear(snapshot=True)
    assert not book.orders and book.started and book.in_snapshot
    for oid, size in ((11, 3), (12, 4), (13, 5)):
        book.add(oid, B, 99, size)
    book.add(21, S, 101, 2)
    book.end_snapshot()
    assert ids(book, B, 99) == [11, 12, 13] and not book.in_snapshot
    # conservative TOP after a snapshot: first order of each best level, 0 lots counted
    assert book.top == [11, 21] and book.top_count == [0, 0]


def test_unstarted_and_bad_books_are_invalid():
    book = mb.Book()
    assert not book.is_valid()
    book.clear(snapshot=False)
    book.add(1, B, 100, 1)
    book.add(2, S, 101, 1)
    assert book.is_valid()
    book.mark_bad()
    assert not book.is_valid()
    book.clear(snapshot=False)
    assert not book.bad


def test_crossed_and_locked_are_invalid():
    book = started()
    book.add(1, B, 100, 1)
    book.add(2, S, 100, 1)
    assert not book.is_valid()
    book.modify(2, S, 99, 1)
    assert not book.is_valid()


def test_top_set_on_bettering_and_replaced_by_a_new_top():
    book = started()
    book.add(1, B, 100, 5)  # empty side: sets the market -> TOP
    assert book.top[B] == 1
    book.add(2, B, 100, 5)  # joins: level already had a TOP -> not TOP
    assert book.top[B] == 1
    book.add(3, B, 101, 2)  # betters -> new TOP
    assert book.top[B] == 3 and book.top_at(B, 101) == (3, 100)
    assert book.top_at(B, 100) is None


def test_top_lost_on_cancel_not_conveyed():
    book = started()
    book.add(1, B, 100, 5)
    book.add(2, B, 100, 5)
    book.cancel(1, 5)
    assert book.top[B] == 0
    book.add(3, B, 100, 5)  # the level has had a TOP since it was established
    assert book.top[B] == 0


def test_top_kept_on_size_decrease_lost_on_increase():
    book = started()
    book.add(1, S, 101, 5)
    book.modify(1, S, 101, 3)
    assert book.top[S] == 1
    book.modify(1, S, 101, 4)
    assert book.top[S] == 0


def test_top_price_change_keeps_only_when_bettering():
    book = started()
    book.add(1, B, 100, 5)
    book.add(2, B, 99, 5)
    book.modify(1, B, 101, 5)  # betters: keeps TOP
    assert book.top[B] == 1
    book.add(3, B, 101, 1)
    book.modify(1, B, 99, 5)  # moves away from the market: loses TOP
    assert book.top[B] == 0


def test_top_by_joining_a_best_level_without_top():
    book = started()
    book.add(1, B, 100, 5)  # TOP at 100
    book.add(2, B, 99, 5)  # 99 established without a TOP
    book.cancel(1, 5)  # 100 empties; 99 is now best and never had a TOP
    book.add(3, B, 99, 2)
    assert book.top[B] == 3
    book.add(4, B, 99, 2)
    assert book.top[B] == 3  # 99 has had a TOP now


def test_top_max_reached_through_fills_keeps_priority():
    book = started(top_max=40)
    book.add(1, S, 100, 155)
    book.add(2, S, 100, 20)
    book.on_fill(1, 30)
    assert book.top[S] == 1 and book.top_at(S, 100) == (1, 10)
    book.on_fill(1, 10)
    assert book.top[S] == 0 and ids(book, S, 100) == [1, 2]


def test_e6_aggressor_remainder_rests_as_top():
    # TOP Min 3, TOP Max 40; bid 45 @ 100; offer 50 @ 100 matches 45, 5 rest as TOP
    book = started(top_min=3, top_max=40)
    book.add(1, B, 100, 45)
    book.cancel(1, 45)  # the matched bid leaves
    book.add(7, S, 100, 5, aggressed=45)
    assert book.top[S] == 7 and book.top_at(S, 100) == (7, 40)


def test_e6_before_2023_10_initial_aggression_counts():
    book = started(top_min=3, top_max=40, count_initial=True)
    book.add(1, B, 100, 45)
    book.cancel(1, 45)
    book.add(7, S, 100, 5, aggressed=45)
    assert book.top[S] == 0  # 45 >= TOP Max 40: not granted under the old rule


def test_e7_new_top_takes_top_from_resting_offer():
    book = started(top_min=3, top_max=40)
    book.add(5, S, 102, 25)  # resting TOP offer
    assert book.top[S] == 5
    book.add(1, B, 100, 45)
    book.cancel(1, 45)
    book.add(8, S, 100, 155, aggressed=45)
    assert book.top[S] == 8 and book.top_at(S, 102) is None and book.top_at(S, 100) == (8, 40)


def test_top_min_blocks_small_orders():
    book = started(top_min=3)
    book.add(1, B, 100, 2)
    assert book.top[B] == 0


def test_e2_display_refresh_goes_to_lowest_priority():
    book = started()
    for oid, size in ((1, 5), (2, 10), (3, 57), (4, 4), (5, 28), (6, 300)):
        book.add(oid, B, 100, size)
    book.cancel(1, 5)
    book.cancel(2, 10)  # the visible 10 filled; the hidden part refreshes as a new add
    book.modify(3, B, 100, 22)
    book.add(2, B, 100, 10)
    assert ids(book, B, 100) == [3, 4, 5, 6, 2]
    assert [n for _, n, _ in book.queue(B, 100)] == [22, 4, 28, 300, 10]


def test_time_axis_non_decreasing_and_inversions_skip_snapshots():
    ev = np.array([10, 30, 20, 40, 5, 50], dtype=np.uint64)
    recv = np.array([10, 30, 31, 41, 45, 51], dtype=np.uint64)
    flags = np.array([0, 0, 0, 0, mb.F_SNAPSHOT, 0], dtype=np.uint8)
    t, inv = mb.time_axis(ev, recv, flags)
    assert t.tolist() == [10, 30, 30, 40, 45, 50]
    assert inv == 1  # 20 < 30; the snapshot record's 5 is not an inversion
