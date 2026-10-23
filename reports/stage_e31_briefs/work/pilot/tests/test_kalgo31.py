"""kalgo31: CME's per-step K examples (research/K_algorithm.md section c) and hand-built full
sequences. Printing errors corrected as research (d) items 4 and 5 state: E4 order 6 ends at 263
(printed 236), E2 order 3 ends at 22 (the text's 21)."""

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kalgo31 as ka  # noqa: E402

BOOK = [5, 9, 57, 4, 28, 300]  # CME's example book, orders 1..6 in time priority
PURE_FIFO = ka.KParams(fifo_pct=Fraction(1), leveling=False, fifo_exception=False)


def _remaining(qty, alloc):
    return [w - a for w, a in zip(qty, alloc, strict=True)]


def test_e1_fifo_example_1():
    alloc, left = ka.fifo_step(BOOK, 50)
    assert alloc == [5, 9, 36, 0, 0, 0]
    assert _remaining(BOOK, alloc) == [0, 0, 21, 4, 28, 300]
    assert left == 0


def test_e2_fifo_display_quantity_corrected_to_22():
    book = [5, 10, 57, 4, 28, 300]  # order 2 shows 10 of 100
    alloc, _ = ka.fifo_step(book, 50)
    assert _remaining(book, alloc) == [0, 0, 22, 4, 28, 300]  # research (d) item 5


def test_e3_pro_rata_with_pr_min_2():
    alloc, participated = ka.pro_rata_step(BOOK, 50, pr_min=2)
    assert alloc == [0, 0, 7, 0, 3, 37]  # order 2's 1 is below PR Min 2
    assert _remaining(BOOK, alloc) == [5, 9, 50, 4, 25, 263]
    assert all(participated)


def test_e3_under_zm_pr_min_1_order_2_gets_1():
    alloc, _ = ka.pro_rata_step(BOOK, 50, pr_min=1)
    assert alloc == [0, 1, 7, 0, 3, 37]


def test_e4_leveling_continuing_e3_corrected_263():
    pr, participated = ka.pro_rata_step(BOOK, 50, pr_min=2)
    rem = _remaining(BOOK, pr)
    lev = ka.leveling_step(rem, pr, participated, 50 - sum(pr))
    assert 50 - sum(pr) == 3
    assert lev == [1, 1, 0, 1, 0, 0]  # order 2, then 1, then 4 (working quantity 9, 5, 4)
    assert _remaining(rem, lev) == [4, 8, 50, 3, 25, 263]  # order 6: 263 (printed 236)


def test_e4_with_two_lots_order_4_gets_none():
    pr, participated = ka.pro_rata_step(BOOK, 50, pr_min=2)
    lev = ka.leveling_step(_remaining(BOOK, pr), pr, participated, 2)
    assert lev == [1, 1, 0, 0, 0, 0]


@pytest.mark.parametrize(("pct", "fifo", "pr"), [
    (Fraction(1), 49, 0), (Fraction(1, 5), 10, 39), (Fraction(2, 5), 20, 29), (Fraction(0), 0, 49)])
def test_e5_split_49(pct, fifo, pr):
    assert ka.split(49, pct) == (fifo, pr)


@pytest.mark.parametrize(("q", "fifo", "pr"), [(1, 1, 0), (2, 1, 1), (3, 2, 1), (5, 2, 3)])
def test_e5_split_small_and_whole_number_case(q, fifo, pr):
    assert ka.split(q, Fraction(2, 5)) == (fifo, pr)  # Q = 5: ceil(2.0) = 2 (research (d) 4)


def test_e9_pure_pro_rata_six_and_five_lots():
    six = [10] * 6
    assert ka.pro_rata_step(six, 6, pr_min=1)[0] == [1] * 6
    alloc, participated = ka.pro_rata_step(six, 5, pr_min=1)
    assert alloc == [0] * 6  # "no Pro-Rata allocation and this 5 lot moves to Leveling or FIFO"
    assert ka.leveling_step(six, alloc, participated, 5) == [1, 1, 1, 1, 1, 0]


def test_e6_e7_top_room_caps_the_top_step():
    params = ka.KParams(top_min=3, top_max=40)
    steps = ka.allocate_steps([155, 20], 50, top=0, params=params)
    assert steps["top"] == [40, 0]  # TOP Max 40 counts only fills after resting (E6/E7)
    assert sum(steps["total"]) == 50


def test_full_sequence_top_split_fifo_prorata_leveling_fifo():
    # orders A (TOP, 30), B 10, C 20, D 5, then the virtual 1-lot V; Q = 60 < 66 displayed
    steps = ka.allocate_steps([30, 10, 20, 5, 1], 60, top=0)
    assert steps["fifo_exception"] is False
    assert steps["top"] == [30, 0, 0, 0, 0]  # Q1 = 30 -> FIFO 12, pro rata 18
    assert steps["fifo"] == [0, 10, 2, 0, 0]
    assert steps["pro_rata"] == [0, 0, 13, 3, 0]  # 18*18//24 = 13, 5*18//24 = 3, 1*18//24 = 0
    assert steps["leveling"] == [0, 0, 0, 0, 1]  # 2 lots left; only V took part and got 0
    assert steps["residual"] == [0, 0, 1, 0, 0]  # the last lot FIFO: C first
    assert steps["total"] == [30, 10, 16, 3, 1]
    assert steps["unallocated"] == 0


def test_full_sequence_virtual_gets_nothing_behind_a_large_top():
    assert ka.allocate([50, 40, 1], 50, top=0) == [50, 0, 0]


def test_full_sequence_leveling_prefers_larger_then_earlier():
    # no TOP; Q = 7: FIFO ceil(2.8) = 3 to order 1 (3 of 4); pro rata 4 over [1, 2, 2, 1] (W 6):
    # 4*1//6 = 0, 4*2//6 = 1, 1, 0 -> 2 lots left; leveling: order 1 and V (both 1 lot, order 1
    # earlier) took part and got 0, so each gets one.
    steps = ka.allocate_steps([4, 2, 2, 1], 7)
    assert steps["fifo"] == [3, 0, 0, 0]
    assert steps["pro_rata"] == [0, 1, 1, 0]
    assert steps["leveling"] == [1, 0, 0, 1]
    assert steps["total"] == [4, 1, 1, 1]


def test_full_sequence_leveling_runs_out_before_virtual():
    # Q = 6, no TOP: FIFO 3 -> order 1 (3), pro rata 3 over [2, 3, 3, 1] (W 9): 0, 1, 1, 0;
    # 1 lot left: leveling order by size: order 1 (2) before V (1) -> V gets nothing
    steps = ka.allocate_steps([5, 3, 3, 1], 6)
    assert steps["fifo"] == [3, 0, 0, 0]
    assert steps["pro_rata"] == [0, 1, 1, 0]
    assert steps["leveling"] == [1, 0, 0, 0]
    assert steps["total"][3] == 0


def test_fifo_exception_at_q_equals_d_plus_1_fills_everything_with_virtual():
    assert ka.allocate([3, 4, 1], 8) == [3, 4, 1]
    steps = ka.allocate_steps([3, 4, 1], 10)
    assert steps["fifo_exception"] is True and steps["unallocated"] == 2


def test_fifo_exception_boundary_q_equals_d_runs_k():
    # Q equals the real displayed 7 but not 7 + 1, so K runs: FIFO ceil(2.8) = 3 -> order 1;
    # pro rata 4 over [0, 4, 1] (W 5): 3 and 0; 1 lot left -> leveling: V took part, got 0
    steps = ka.allocate_steps([3, 4, 1], 7)
    assert steps["fifo_exception"] is False
    assert steps["fifo"] == [3, 0, 0] and steps["pro_rata"] == [0, 3, 0]
    assert steps["total"] == [3, 3, 1]


def test_top_takes_part_in_later_steps_with_its_rest():
    # TOP 10 with room 4: takes 4, then (6 left) joins FIFO first by its timestamp
    steps = ka.allocate_steps([10, 10, 1], 9, top=0, top_room=4)
    assert steps["top"] == [4, 0, 0]
    assert steps["fifo"] == [2, 0, 0]  # ceil(0.4 x 5) = 2
    assert steps["total"][0] >= 6


def test_inputs_are_not_changed_and_zero_q():
    qty = [5, 5]
    ka.allocate(qty, 3, top=1)
    assert qty == [5, 5]
    assert ka.allocate(qty, 0) == [0, 0]
    assert ka.allocate([], 4) == []


def test_negative_quantity_refused():
    with pytest.raises(ValueError):
        ka.allocate([2, -1], 1)


def test_pure_fifo_params_match_fifo_step():
    assert ka.allocate(BOOK, 50, params=PURE_FIFO) == ka.fifo_step(BOOK, 50)[0]
