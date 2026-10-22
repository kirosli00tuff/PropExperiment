"""Spec section 3 rules on hand-built books, each answer computed by hand in the comments.

Book in ticks (tick 0.25). One MAIN grid time G = 2023-11-14 15:00:00Z; the orders join at
J = G + 50 ms and live in (J, J + 60.05 s). Unless a test says otherwise the book is bid 100 /
ask 101.
"""

import measure_core as mc
import numpy as np
import pytest
from b_helpers import MS, G, J, S, Tape, book_from, main_plan

ALL = mc.MeasureParams(rules=mc.RULES)


def orders(tape, plan=None, params=ALL):
    cols, skipped = mc.day_orders(book_from(tape, plan), params)
    return cols, skipped


def pick(cols, kind, side):
    """Index of the order of ``kind`` ('T'/'I') and side (+1 buy, -1 sell)."""
    hits = [k for k, (t, s) in enumerate(zip(cols["type"], cols["side"], strict=True))
            if t == kind and s == side]
    assert len(hits) == 1, (kind, side, hits)
    return hits[0]


def fill(cols, rule, k):
    value = cols["rules"][rule]["fill_ns"][k]
    return None if value == mc.NONE else value


def test_touch_order_fills_only_after_q_ahead_plus_one_trade_at_its_price():
    # bid 100 x 3: Q_ahead = 3, so the buy needs V >= 4 sell-aggressor contracts at 100.
    tape = (Tape(bid=100, ask=101, bsz=3, asz=2).quote(G - S)
            .trade(J + 1 * S, 100, 1, "A")          # V = 1
            .trade(J + 2 * S, 100, 2, "A")          # V = 3 = Q_ahead: not yet
            .trade(J + 2500 * MS, 100, 10, "B")     # buy aggressor: not counted
            .trade(J + 2700 * MS, 100, 5, "N")      # no aggressor: not counted
            .trade(J + 3 * S, 100, 1, "A"))         # V = 4 = Q_ahead + 1: fill here
    cols, skipped = orders(tape)
    buy = pick(cols, "T", 1)
    assert cols["price"][buy] == 100 and cols["q_ahead"][buy] == 3
    assert fill(cols, "spec", buy) == J + 3 * S
    assert cols["touch_ns"][buy] == J + 1 * S       # first trade at its price
    sell = pick(cols, "T", -1)
    assert cols["price"][sell] == 101 and cols["q_ahead"][sell] == 2
    assert fill(cols, "spec", sell) is None and cols["touch_ns"][sell] == mc.NONE
    # spread 1 tick: no I order on either side
    assert skipped == {"I|MAIN|buy|spread_lt_2_ticks": 1, "I|MAIN|sell|spread_lt_2_ticks": 1}


def test_quote_touch_without_trade_is_not_a_fill():
    # bid 100 / ask 102; at J + 5 s the book moves to 99 / 100: the ask reaches the T buy's 100
    # and the I buy's 101 with no trade.
    tape = Tape(bid=100, ask=102, bsz=1, asz=1).quote(G - S).quote(J + 5 * S, bid=99, ask=100)
    cols, _ = orders(tape)
    for kind in ("T", "I"):
        k = pick(cols, kind, 1)
        assert cols["touch_ns"][k] == J + 5 * S
        assert fill(cols, "spec", k) is None
        assert fill(cols, "trade_through_only", k) is None
        assert fill(cols, "trade_at_or_through", k) is None
        assert fill(cols, "touch", k) == J + 5 * S  # the touch sim rule fills on the quote
    assert cols["price"][pick(cols, "I", 1)] == 101


def test_trade_through_fills_whatever_the_queue():
    # bid 100 x 50: 10 contracts at 100 leave V = 10 < 51; a sell at 99 trades through.
    tape = (Tape(bid=100, ask=101, bsz=50, asz=1).quote(G - S)
            .trade(J + 2 * S, 100, 10, "A").trade(J + 5 * S, 99, 1, "A"))
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    assert fill(cols, "spec", k) == J + 5 * S
    assert fill(cols, "trade_through_only", k) == J + 5 * S
    assert fill(cols, "trade_at_or_through", k) == J + 2 * S
    assert fill(cols, "touch", k) == J + 2 * S


def test_inside_order_has_q_ahead_zero_and_fills_on_first_opposite_aggressor_at_its_price():
    # bid 100 / ask 103 (3 ticks): I buy at 101 and I sell at 102, both with Q_ahead = 0.
    tape = (Tape(bid=100, ask=103, bsz=4, asz=4).quote(G - S)
            .trade(J + 4 * S, 101, 1, "A").trade(J + 6 * S, 102, 1, "B"))
    cols, _ = orders(tape)
    ib, isell = pick(cols, "I", 1), pick(cols, "I", -1)
    assert (cols["price"][ib], cols["q_ahead"][ib]) == (101, 0)
    assert (cols["price"][isell], cols["q_ahead"][isell]) == (102, 0)
    assert fill(cols, "spec", ib) == J + 4 * S
    assert fill(cols, "spec", isell) == J + 6 * S
    tb = pick(cols, "T", 1)  # the T buy at 100 is not reached by trades at 101 or 102
    assert fill(cols, "spec", tb) is None and cols["touch_ns"][tb] == mc.NONE


def test_join_latency_trade_40ms_after_creation_does_not_count():
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(G + 40 * MS, 100, 5, "A")     # before the join at G + 50 ms
            .trade(J, 100, 5, "A"))              # stamped exactly at j: part of the join state
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    assert fill(cols, "spec", k) is None and cols["touch_ns"][k] == mc.NONE


@pytest.mark.parametrize(("offset_ms", "filled"), [(60_030, True), (60_049, True),
                                                   (60_050, False), (60_060, False),
                                                   (61_000, False)])
def test_cancel_latency_and_60s_cancel(offset_ms, filled):
    # decided at J + 60 s, effective at J + 60.05 s: a trade inside the latency still fills
    tape = Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).trade(J + offset_ms * MS, 100, 2,
                                                                   "A")
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    assert (fill(cols, "spec", k) == J + offset_ms * MS) is filled
    if not filled:
        assert fill(cols, "spec", k) is None


def test_markouts_at_each_horizon():
    # buy filled at 100 at t_f = J + 3 s; mids: t_f+0.5 s 101.5, t_f+5 s 99.5, t_f+30 s 100.5
    tf = J + 3 * S
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(tf, 100, 2, "A")
            .quote(tf + 500 * MS, bid=101, ask=102)
            .quote(tf + 5 * S, bid=99, ask=100)
            .quote(tf + 30 * S, bid=100, ask=101))
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    spec = cols["rules"]["spec"]
    assert spec["fill_ns"][k] == tf
    assert spec["m1"][k] == pytest.approx(1.5)    # (101.5 - 100)
    assert spec["m10"][k] == pytest.approx(-0.5)  # (99.5 - 100)
    assert spec["m60"][k] == pytest.approx(0.5)   # (100.5 - 100)
    assert spec["drop1"][k] is None


def test_sell_markout_sign():
    # sell T at 101 filled by a buy aggressor (Q_ahead 1 -> needs 2); mid 1 s later 100.5
    tf = J + 2 * S
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).trade(tf, 101, 2, "B")
            .quote(tf + 200 * MS, bid=100, ask=101))
    cols, _ = orders(tape)
    k = pick(cols, "T", -1)
    assert cols["rules"]["spec"]["fill_ns"][k] == tf
    assert cols["rules"]["spec"]["m1"][k] == pytest.approx(0.5)  # -1 x (100.5 - 101)


def test_markout_crossing_session_end_is_dropped():
    tf = J + 3 * S
    tape = Tape(bid=100, ask=101).quote(G - S).quote(tf + 500 * MS, bid=101, ask=102)
    book = book_from(tape)
    marks = mc.markouts(book, tf, 100, 1, piece_hi=tf + 30 * S, horizons_s=(1, 10, 60))
    assert marks[0] == (pytest.approx(1.5), None)
    assert marks[1] == (pytest.approx(1.5), None)
    assert marks[2] == (None, mc.DROP_SESSION_END)
    # a horizon landing exactly on the session end is dropped too
    assert mc.markouts(book, tf, 100, 1, tf + 10 * S, (10,))[0] == (None, mc.DROP_SESSION_END)


def test_markout_with_invalid_book_inside_horizon_is_dropped():
    tf = J + 3 * S
    tape = (Tape(bid=100, ask=101).quote(G - S)
            .quote(tf + 20 * S, bid=101, ask=100)    # crossed for 1 s
            .quote(tf + 21 * S, bid=100, ask=101))
    book = book_from(tape)
    marks = mc.markouts(book, tf, 100, 1, piece_hi=tf + 600 * S, horizons_s=(1, 10, 60))
    assert marks[0] == (pytest.approx(0.5), None) and marks[1] == (pytest.approx(0.5), None)
    assert marks[2] == (None, mc.DROP_INVALID)


@pytest.mark.parametrize(("bid", "ask", "bsz", "asz"), [(101, 100, 1, 1), (100, 100, 1, 1),
                                                        (100, None, 1, 0), (100, 101, 0, 1)])
def test_crossed_locked_or_empty_book_at_join_takes_no_placement(bid, ask, bsz, asz):
    tape = Tape(bid=bid, ask=ask, bsz=bsz, asz=asz).quote(G - S)
    cols, skipped = orders(tape)
    assert cols["type"] == []
    assert sum(skipped.values()) == 4
    assert all(key.endswith("invalid_book_at_join") for key in skipped)


def test_no_book_state_before_first_record_takes_no_placement():
    tape = Tape(bid=100, ask=101).quote(J + S)  # first record after the join
    cols, skipped = orders(tape)
    assert cols["type"] == [] and all(k.endswith("no_book_state_at_join") for k in skipped)


def test_book_state_at_join_comes_from_last_record_at_or_before_j():
    # size changes at J exactly (counts) and at J + 1 ms (does not)
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).quote(J, bsz=7)
            .quote(J + MS, bsz=9))
    cols, _ = orders(tape)
    assert cols["q_ahead"][pick(cols, "T", 1)] == 7


def test_segmented_feed_gives_the_same_orders():
    tape = (Tape(bid=100, ask=101, bsz=3, asz=2).quote(G - S).trade(J + S, 100, 1, "A")
            .quote(J + 2 * S, bsz=4).trade(J + 3 * S, 100, 3, "A")
            .quote(J + 4 * S, bid=99, ask=100).quote(J + 9 * S, bid=100, ask=101))
    one = mc.day_orders(book_from(tape), ALL)
    many = mc.day_orders(book_from(tape, segments=4), ALL)
    assert one == many


def test_unknown_rule_is_refused():
    book = book_from(Tape().quote(G - S))
    with pytest.raises(ValueError, match="unknown fill rule"):
        mc.rule_fill_time("magic", book, 0, 0, 100, 0, 1, None)


def test_day_on_or_after_cutoff_is_refused():
    import datetime as dt

    import pilot_common as pc

    plan = pc.make_test_plan(dt.date(2024, 3, 1), [pc.Piece(pc.MAIN, G - 600 * S,
                                                            G + 600 * S)], [G])
    with pytest.raises(pc.PilotRefused):
        mc.day_orders(book_from(Tape().quote(G - S), plan), ALL)


def test_grid_with_two_times_and_overlapping_lives():
    grid = [G, G + 300 * S]
    tape = (Tape(bid=100, ask=101, bsz=0 + 1, asz=1).quote(G - S)
            .trade(G + 300 * S + 2 * S, 100, 2, "A"))
    cols, _ = orders(tape, plan=main_plan(grid=grid))
    buys = [k for k, (t, s) in enumerate(zip(cols["type"], cols["side"], strict=True))
            if t == "T" and s == 1]
    fills = [fill(cols, "spec", k) for k in buys]
    assert fills == [None, G + 302 * S]
    assert np.all(np.diff(cols["g_ns"]) >= 0)


# ------------------------------------------------------------------ review fixes ----
# RS-04, RS-05, RS-06 and RS-13 (reports/stage_e28_briefs/R_spec.md) on hand-built books. The
# SpecReviewer's adversarial file documents the pre-fix behaviour of RS-04 and RS-13; these
# tests assert the fixed behaviour.
def test_side_n_trade_through_never_fills_and_an_a_trade_through_does():
    # RS-04 / spec 3: the through clause needs a defined aggressor (A or B), never N
    tape = (Tape(bid=100, ask=101, bsz=50, asz=1).quote(G - S)
            .trade(J + 1 * S, 99, 1, "N")           # strictly through, no aggressor: no fill
            .trade(J + 2 * S, 99, 1, "A"))          # strictly through, sell aggressor: fill
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    assert cols["touch_ns"][k] == J + 1 * S         # the touch counts any aggressor
    for rule in ("spec", "trade_through_only", "trade_at_or_through", "touch"):
        assert fill(cols, rule, k) == J + 2 * S, rule
    assert cols["rules"]["spec"]["trigger"][k] == mc.TRIG_THROUGH
    assert cols["rules"]["spec"]["trigger_side"][k] == "A"
    only_n = Tape(bid=100, ask=101, bsz=50, asz=1).quote(G - S).trade(J + 1 * S, 99, 1, "N")
    cols, _ = orders(only_n)
    k = pick(cols, "T", 1)
    assert all(fill(cols, rule, k) is None for rule in mc.RULES)


def test_queue_fill_reports_trigger_and_aggressor():
    tape = Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).trade(J + 1 * S, 100, 2, "A")
    cols, _ = orders(tape)
    k = pick(cols, "T", 1)
    assert fill(cols, "spec", k) == J + 1 * S
    assert cols["rules"]["spec"]["trigger"][k] == mc.TRIG_QUEUE
    assert cols["rules"]["spec"]["trigger_side"][k] == "A"


def test_life_is_clipped_at_the_session_piece_end():
    # RS-13: a forced grid time 30 s before the piece end (the spec grid never allows this);
    # the order is cancelled at the piece end, so a trade 15 s after it cannot fill
    import pilot_common as pc
    from b_helpers import DAY

    plan = pc.make_test_plan(DAY, [pc.Piece(pc.MAIN, G - 600 * S, G + 30 * S)], [G])
    late = Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).trade(J + 45 * S, 100, 5, "A")
    cols, _ = orders(late, plan)
    k = pick(cols, "T", 1)
    assert cols["life_end_ns"][k] == G + 30 * S
    assert all(fill(cols, rule, k) is None for rule in mc.RULES)
    inside = Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S).trade(J + 20 * S, 100, 5, "A")
    cols, _ = orders(inside, plan)
    assert fill(cols, "spec", pick(cols, "T", 1)) == J + 20 * S
    # under the regular grid the clip never binds: life end = j + 60 s + 50 ms
    cols, _ = orders(late)
    assert cols["life_end_ns"][pick(cols, "T", 1)] == J + pc.LIFE_NS + pc.LATENCY_NS


def test_stale_flag_when_the_best_price_moves_between_g_and_j():
    # RS-06: the bid moves from 100 to 99 at G + 20 ms; the order is priced at j (bid 99)
    moved = Tape(bid=100, ask=101).quote(G - S).quote(G + 20 * MS, bid=99, ask=101)
    cols, _ = orders(moved)
    buy, sell = pick(cols, "T", 1), pick(cols, "T", -1)
    assert cols["price"][buy] == 99
    assert cols["stale"][buy] is True and cols["stale"][sell] is False
    cols, _ = orders(Tape(bid=100, ask=101).quote(G - S))
    assert cols["stale"][pick(cols, "T", 1)] is False


def test_nodrop_markout_uses_the_last_valid_mid_when_one_side_empties():
    # RS-05: the ask empties at t_f + 30 s until t_f + 70 s. Headline 60 s: dropped
    # (invalid_book); no-drop 60 s: the last valid mid (100.5) -> +0.5 for a buy at 100
    tf = J + 3 * S
    tape = (Tape(bid=100, ask=101).quote(G - S)
            .quote(tf + 30 * S, ask=None, asz=0)
            .quote(tf + 70 * S, ask=101, asz=1))
    book = book_from(tape)
    heads = mc.markouts(book, tf, 100, 1, piece_hi=tf + 600 * S, horizons_s=(10, 60))
    nodrop = mc.markouts_nodrop(book, tf, 100, 1, piece_hi=tf + 600 * S, horizons_s=(10, 60))
    assert heads == [(pytest.approx(0.5), None), (None, mc.DROP_INVALID)]
    assert nodrop == [(pytest.approx(0.5), None), (pytest.approx(0.5), None)]
    # a book already invalid at t_f that stays so to t_f + h has no valid mid after t_f
    dead = (Tape(bid=100, ask=101).quote(G - S)
            .quote(tf - 1 * S, ask=None, asz=0)
            .quote(tf + 70 * S, ask=101, asz=1))
    book = book_from(dead)
    assert mc.markouts_nodrop(book, tf, 100, 1, tf + 600 * S, (60,)) == \
        [(None, mc.DROP_NO_VALID)]
