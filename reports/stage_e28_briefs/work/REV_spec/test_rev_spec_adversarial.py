"""SpecReviewer-FableXHigh: adversarial synthetic cases against measure_core / pilot_stream.

Run from the repo root:
    uv run pytest -q reports/stage_e28_briefs/work/REV_spec/test_rev_spec_adversarial.py -p no:cacheprovider

Each test states the spec clause it probes. Tests that DOCUMENT a convention (rather than assert
the spec) say so in their docstring; a failure there means the convention changed, not a bug.
"""

from __future__ import annotations

import sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1] / "B_pilot"
REPO = PILOT.parents[3]
for entry in (str(REPO), str(PILOT), str(PILOT / "tests")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import measure_core as mc  # noqa: E402
import pilot_common as pc  # noqa: E402
from b_helpers import DAY, G, J, MS, S, Tape, book_from  # noqa: E402

ALL = mc.MeasureParams(rules=mc.RULES)


def orders(tape: Tape, plan=None):
    cols, skipped = mc.day_orders(book_from(tape, plan), ALL)
    return cols, skipped


def pick(cols, kind: str, side: int) -> int:
    hits = [i for i, (k, s) in enumerate(zip(cols["type"], cols["side"], strict=True))
            if k == kind and s == side]
    assert len(hits) == 1, (kind, side, hits)
    return hits[0]


def fill(cols, rule: str, i: int) -> int | None:
    v = cols["rules"][rule]["fill_ns"][i]
    return None if v == mc.NONE else int(v)


# ---------------------------------------------------------------- join instant ----
def test_trade_stamped_exactly_at_join_is_part_of_the_join_state_not_a_fill():
    """Spec 3: Q_ahead from the book state at j; trades after j count. A trade at exactly j
    neither fills nor touches."""
    tape = (Tape(bid=100, ask=101, bsz=3, asz=3).quote(G - S)
            .trade(J, 100, 10, "A"))  # exactly at j, would fill under any later timing
    cols, _ = orders(tape)
    i = pick(cols, "T", +1)
    assert cols["price"][i] == 100 and cols["q_ahead"][i] == 3
    assert fill(cols, mc.RULE_SPEC, i) is None
    assert cols["touch_ns"][i] == mc.NONE
    # one nanosecond later it fills
    tape2 = (Tape(bid=100, ask=101, bsz=3, asz=3).quote(G - S).trade(J + 1, 100, 10, "A"))
    cols2, _ = orders(tape2)
    assert fill(cols2, mc.RULE_SPEC, pick(cols2, "T", +1)) == J + 1


# ---------------------------------------------------------------- queue arithmetic ----
def test_partial_depletion_by_several_trades_needs_q_ahead_plus_one():
    """Spec 3: fill at the first trade making V >= Q_ahead + 1; same-side aggressor trades at
    the price never add to V."""
    tape = (Tape(bid=100, ask=101, bsz=5, asz=5).quote(G - S)
            .trade(J + 1 * S, 100, 2, "A")
            .trade(J + 2 * S, 100, 2, "A")
            .trade(J + 2 * S + 500 * MS, 100, 10, "B")  # buy aggressor at the bid: not ours
            .trade(J + 3 * S, 100, 1, "A")              # V = 5 = Q_ahead: not yet
            .trade(J + 4 * S, 100, 1, "A"))             # V = 6 >= 6: fill
    cols, _ = orders(tape)
    i = pick(cols, "T", +1)
    assert cols["q_ahead"][i] == 5
    assert fill(cols, mc.RULE_SPEC, i) == J + 4 * S
    assert fill(cols, mc.RULE_THROUGH, i) is None
    # the touch came at the first trade at the price
    assert cols["touch_ns"][i] == J + 1 * S


def test_trade_through_after_partial_depletion_fills_at_the_through_trade():
    tape = (Tape(bid=100, ask=101, bsz=5, asz=5).quote(G - S)
            .trade(J + 1 * S, 100, 2, "A")
            .trade(J + 2 * S, 99, 1, "A"))
    cols, _ = orders(tape)
    i = pick(cols, "T", +1)
    assert fill(cols, mc.RULE_SPEC, i) == J + 2 * S
    assert fill(cols, mc.RULE_THROUGH, i) == J + 2 * S


def test_side_none_trade_through_fills_under_spec_but_never_adds_to_v():
    """DOCUMENTS spec 3 'any aggressor' through clause: a trade with side N (no aggressor:
    CME tag 5797 = 0, implied-involved or opening trades) at the price never adds to V, but
    one strictly through the price fills. Finding RS-05 asks for this to be restricted or
    reported."""
    tape_at = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
               .trade(J + 1 * S, 100, 50, "N"))
    cols, _ = orders(tape_at)
    assert fill(cols, mc.RULE_SPEC, pick(cols, "T", +1)) is None
    tape_thr = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
                .trade(J + 1 * S, 99, 1, "N"))
    cols, _ = orders(tape_thr)
    assert fill(cols, mc.RULE_SPEC, pick(cols, "T", +1)) == J + 1 * S


def test_q_ahead_is_fixed_at_join_even_if_the_price_leaves_and_returns():
    """DOCUMENTS: Q_ahead is the size at j; trades at the price after the best bid moved away
    and came back count toward V (conservative under FIFO: nothing can get ahead of a resting
    order at its price)."""
    tape = (Tape(bid=100, ask=101, bsz=5, asz=5).quote(G - S)
            .quote(J + 1 * S, bid=101, ask=102, bsz=2, asz=2)
            .trade(J + 2 * S, 101, 10, "A")   # above our price: not ours
            .quote(J + 3 * S, bid=100, ask=101, bsz=1, asz=1)
            .trade(J + 4 * S, 100, 6, "A"))   # V = 6 >= 5 + 1
    cols, _ = orders(tape)
    i = pick(cols, "T", +1)
    assert cols["q_ahead"][i] == 5
    assert fill(cols, mc.RULE_SPEC, i) == J + 4 * S


# ---------------------------------------------------------------- crossed / locked ----
def test_crossed_book_during_life_no_trade_no_fill_but_touch_and_markout_drop():
    """Spec 2/3: a crossed book stops markout clocks; a quote reaching the price is a touch
    but never a fill."""
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(J + 2 * S, 100, 2, "A")                     # buy fills here
            .quote(J + 2 * S + 500 * MS, bid=102, ask=101)     # crossed 0.5 s after the fill
            .quote(J + 3 * S, bid=100, ask=101))
    cols, _ = orders(tape)
    b = pick(cols, "T", +1)
    assert fill(cols, mc.RULE_SPEC, b) == J + 2 * S
    for h in (1, 10, 60):
        assert cols["rules"][mc.RULE_SPEC][f"drop{h}"][b] == mc.DROP_INVALID
        assert cols["rules"][mc.RULE_SPEC][f"m{h}"][b] is None
    s_ = pick(cols, "T", -1)  # the sell at 101: the crossed bid 102 >= 101 is a touch, no fill
    assert fill(cols, mc.RULE_SPEC, s_) is None
    assert cols["touch_ns"][s_] == J + 2 * S + 500 * MS


def test_locked_book_then_same_side_trade_at_our_price_is_not_a_spec_fill():
    """Our buy rests at 100; the ask drops to 100 (locked) and buyers lift it: trades at 100
    with side B. Spec: not a fill (same-side aggressor); touch: yes. The firm rule
    trade_at_or_through would call it a fill (documents the sim rules' difference)."""
    tape = (Tape(bid=100, ask=101, bsz=4, asz=4).quote(G - S)
            .quote(J + 1 * S, bid=100, ask=100, bsz=4, asz=3)
            .trade(J + 2 * S, 100, 10, "B"))
    cols, _ = orders(tape)
    b = pick(cols, "T", +1)
    assert fill(cols, mc.RULE_SPEC, b) is None
    assert fill(cols, mc.RULE_AT_OR_THROUGH, b) == J + 2 * S
    assert cols["touch_ns"][b] == J + 1 * S


# ---------------------------------------------------------------- windows ----
@pytest.mark.parametrize("offset_ns, filled", [
    (60 * S + 30 * MS, True), (60 * S + 50 * MS - 1, True), (60 * S + 50 * MS, False),
    (60 * S + 51 * MS, False)])
def test_fill_inside_the_cancel_latency_counts_and_at_the_effective_cancel_does_not(offset_ns,
                                                                                   filled):
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(J + offset_ns, 100, 5, "A"))
    cols, _ = orders(tape)
    got = fill(cols, mc.RULE_SPEC, pick(cols, "T", +1))
    assert (got is not None) is filled


def test_life_window_may_extend_past_a_session_piece_end_if_the_grid_allows_it():
    """DOCUMENTS a latent dependence: the life (j, j + 60.05 s) is not clipped at the piece
    end; only the 5-minute grid edge exclusion keeps lives inside pieces. With a forced grid
    30 s before the piece end, a trade after the piece end still fills; its markouts are then
    dropped as session_end."""
    plan = pc.make_test_plan(DAY, [pc.Piece(pc.MAIN, G - 10 * 60 * S, G + 30 * S)], [G])
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(J + 45 * S, 100, 5, "A"))  # 15 s after the piece ended
    cols, _ = orders(tape, plan)
    b = pick(cols, "T", +1)
    assert fill(cols, mc.RULE_SPEC, b) == J + 45 * S
    assert cols["rules"][mc.RULE_SPEC]["drop1"][b] == mc.DROP_SESSION_END


def test_regular_grid_never_puts_a_life_across_a_piece_end():
    """Spec 2: first and last 5 minutes excluded, so g + 50 ms + 60.05 s < piece end always."""
    piece = pc.Piece(pc.MAIN, G - 10 * 60 * S, G + 10 * 60 * S)
    grid, _ = pc.placement_grid([piece])
    assert len(grid) > 0
    assert (grid + pc.LATENCY_NS + pc.LIFE_NS + pc.LATENCY_NS + 60 * S < piece.hi).all()
    assert (grid >= piece.lo + pc.EDGE_NS).all() and (grid < piece.hi - pc.EDGE_NS).all()


# ---------------------------------------------------------------- inside orders ----
def test_inside_orders_at_a_two_tick_spread_share_a_price_and_fill_by_aggressor_side():
    tape = (Tape(bid=100, ask=102, bsz=3, asz=3).quote(G - S)
            .trade(J + 1 * S, 101, 1, "A"))
    cols, _ = orders(tape)
    ib, is_ = pick(cols, "I", +1), pick(cols, "I", -1)
    assert cols["price"][ib] == 101 == cols["price"][is_]
    assert cols["q_ahead"][ib] == 0 == cols["q_ahead"][is_]
    assert fill(cols, mc.RULE_SPEC, ib) == J + 1 * S
    assert fill(cols, mc.RULE_SPEC, is_) is None
    # a trade at the OLD best bid (100) is strictly through the inside buy at 101
    tape2 = (Tape(bid=100, ask=102, bsz=3, asz=3).quote(G - S).trade(J + 1 * S, 100, 1, "A"))
    cols2, _ = orders(tape2)
    assert fill(cols2, mc.RULE_SPEC, pick(cols2, "I", +1)) == J + 1 * S


def test_one_tick_spread_takes_no_inside_placement():
    cols, skipped = orders(Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S))
    assert all(k == "T" for k in cols["type"])
    assert skipped == {"I|MAIN|buy|spread_lt_2_ticks": 1, "I|MAIN|sell|spread_lt_2_ticks": 1}


# ---------------------------------------------------------------- markout reference ----
def test_markout_uses_the_state_at_or_before_t_f_plus_h_including_one_exactly_there():
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(J + 1 * S, 100, 5, "A")              # buy fills at 100
            .quote(J + 2 * S, bid=98, ask=99)            # exactly at t_f + 1 s
            .quote(J + 11 * S + 1, bid=104, ask=105))    # 1 ns after t_f + 10 s
    cols, _ = orders(tape)
    b = pick(cols, "T", +1)
    m = cols["rules"][mc.RULE_SPEC]
    assert m["m1"][b] == pytest.approx(98.5 - 100)      # the change at exactly t_f + h counts
    assert m["m10"][b] == pytest.approx(98.5 - 100)     # the later change does not
    assert m["m60"][b] == pytest.approx(104.5 - 100)


def test_order_price_comes_from_the_book_at_j_not_at_g():
    """DOCUMENTS README convention 4 (finding RS-07): the limit price is read from the book
    50 ms after the decision time g. Here the market ticks down between g and j, so the buy
    is placed at 99 (the touch at j), never marketable at the old bid 100."""
    tape = (Tape(bid=100, ask=101, bsz=2, asz=2).quote(G - S)
            .quote(G + 10 * MS, bid=99, ask=100, bsz=7, asz=7))
    cols, _ = orders(tape)
    b = pick(cols, "T", +1)
    assert cols["price"][b] == 99 and cols["q_ahead"][b] == 7


# ---------------------------------------------------------------- stream edge cases ----
def test_bad_flag_trade_is_dropped_so_it_cannot_fill():
    tape = (Tape(bid=100, ask=101, bsz=1, asz=1).quote(G - S)
            .trade(J + 1 * S, 99, 5, "A", flags=1 << 3))  # F_BAD_TS_RECV
    cols, _ = orders(tape)
    assert fill(cols, mc.RULE_SPEC, pick(cols, "T", +1)) is None


def test_undefined_opposite_quote_at_join_takes_no_placement_on_either_side():
    """Spec 2: an empty side at j takes no placement (both sides, since the mid is undefined)."""
    cols, skipped = orders(Tape(bid=100, ask=None, bsz=1, asz=0).quote(G - S))
    assert cols["type"] == []
    assert set(skipped) == {f"{k}|MAIN|{s}|invalid_book_at_join"
                            for k in ("T", "I") for s in ("buy", "sell")}


def test_cumulative_volume_uses_int64_and_large_sizes_do_not_overflow():
    sz = np.array([2**40, 2**40], dtype=np.int64)
    px = np.array([100, 100], dtype=np.int64)
    side = np.array([ord("A"), ord("A")], dtype=np.int64)
    assert mc.spec_fill_index(px, sz, side, 100, 2**40, +1) == 1
