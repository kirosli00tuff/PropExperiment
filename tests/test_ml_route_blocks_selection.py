"""M7.3 (block cut, CPCV, purge, embargo, fold test) and ML-A01/ML-A10 (selection metric, ties)."""

from __future__ import annotations

from datetime import date, timedelta
from itertools import combinations

import numpy as np
import pytest

from ml_route.blocks import (
    BlockCutError,
    assert_fold,
    cpcv_splits,
    cut_blocks,
    split_masks,
    training_calendar,
)
from ml_route.selection import (
    configuration_score,
    one_open_position,
    portfolio_daily,
    positions_from_predictions,
    select,
    split_score,
    trade_pnl,
)

NS_MIN = 60_000_000_000


def _dates(n: int) -> list[date]:
    out, d = [], date(2020, 1, 6)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


class TestBlockCut:
    def test_frozen_calendar_cut_is_six_blocks_of_208(self) -> None:
        cal = training_calendar()
        cut = cut_blocks(cal)
        assert len(cal) == 1248 and cal[0] == date(2019, 5, 6) and cal[-1] == date(2024, 2, 29)
        assert [b.n_dates for b in cut.blocks] == [208] * 6
        assert cut.blocks[0].first == cal[0] and cut.blocks[5].last == cal[-1]
        assert all(cut.blocks[i].last < cut.blocks[i + 1].first for i in range(5))

    def test_sixth_block_takes_the_remainder(self) -> None:
        cut = cut_blocks(_dates(13))
        assert [b.n_dates for b in cut.blocks] == [2, 2, 2, 2, 2, 3]

    def test_unsorted_or_short_calendar_refused(self) -> None:
        d = _dates(12)
        with pytest.raises(BlockCutError):
            cut_blocks(list(reversed(d)))
        with pytest.raises(BlockCutError):
            cut_blocks(d[:5])


class TestCpcv:
    def test_ten_splits_known_membership_and_embargo(self) -> None:
        d = _dates(30)  # blocks of 5
        cut = cut_blocks(d)
        splits = cpcv_splits(cut)
        assert [s.test_blocks for s in splits] == list(combinations((1, 2, 3, 4, 5), 2))
        s = splits[[x.test_blocks for x in splits].index((2, 4))]
        assert s.validation_dates == frozenset(d[5:10] + d[15:20])
        # one full trade date on each side of each validation block
        assert s.embargo_dates == frozenset({d[4], d[10], d[14], d[20]})
        assert s.training_dates == frozenset(d[0:4] + d[11:14] + d[21:25])
        for sp in splits:  # block 6 is never used by CPCV
            assert not (sp.validation_dates | sp.training_dates) & set(d[25:])

    def test_adjacent_validation_blocks_embargo_only_outer_sides(self) -> None:
        d = _dates(30)
        s = [x for x in cpcv_splits(cut_blocks(d)) if x.test_blocks == (1, 2)][0]
        assert s.embargo_dates == frozenset({d[10]})

    def test_fold_test_passes_and_purge_drops_an_overlapping_row(self) -> None:
        d = _dates(30)
        s = [x for x in cpcv_splits(cut_blocks(d)) if x.test_blocks == (2, 4)][0]
        days = np.array(d[:25] + [d[3]], dtype=object)
        base = np.array([np.datetime64(x, "ns").astype(np.int64) for x in d[:25]])
        t = np.concatenate([base + 9 * 60 * NS_MIN, [base[3] + 9 * 60 * NS_MIN]])
        x = t + 30 * NS_MIN
        x[-1] = base[5] + 10 * 60 * NS_MIN  # a planted training row whose target reaches d[5]
        tr, va, purged = split_masks(s, days, t, x)
        assert purged == 1 and not tr[-1] and tr[3]
        assert_fold(s, days, t, x, tr, va)

    def test_fold_test_raises_on_leaked_dates(self) -> None:
        d = _dates(30)
        s = [x for x in cpcv_splits(cut_blocks(d)) if x.test_blocks == (2, 4)][0]
        days = np.array(d[:25], dtype=object)
        t = np.array([np.datetime64(x, "ns").astype(np.int64) for x in d[:25]])
        x = t + 30 * NS_MIN
        tr, va, _ = split_masks(s, days, t, x)
        bad = tr.copy()
        bad[6] = True  # a validation date on the training side
        with pytest.raises(BlockCutError):
            assert_fold(s, days, t, x, bad, va)
        bad = tr.copy()
        bad[4] = True  # an embargo date on the training side
        with pytest.raises(BlockCutError):
            assert_fold(s, days, t, x, bad, va)


class TestSelectionMetric:
    def test_positions_follow_ml_a01_thresholds(self) -> None:
        y_hat = np.array([0.01, 0.0, -0.1, -0.21, -0.3])
        c = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
        assert positions_from_predictions(y_hat, c).tolist() == [1, 0, 0, -1, -1]

    def test_trade_pnl_long_and_short_at_one_and_one_and_a_half(self) -> None:
        y, c = np.array([1.0, 1.0]), np.array([0.2, 0.2])
        pos = np.array([1, -1])
        assert trade_pnl(y, c, pos, 1.0).tolist() == pytest.approx([1.0, -1.4])
        assert trade_pnl(y, c, pos, 1.5).tolist() == pytest.approx([0.9, -1.5])

    def test_one_open_position_skips_while_open(self) -> None:
        p = np.array(["A", "A", "A", "B"])
        t = np.array([0, 30, 120, 30]) * NS_MIN
        x = np.array([120, 60, 150, 60]) * NS_MIN
        pos = np.array([1, -1, 1, 1], dtype=np.int8)
        # A's 30-minute signal falls inside the first trade; 120 is free again (exit at 120)
        assert one_open_position(p, t, x, pos).tolist() == [1, 0, 1, 1]

    def test_portfolio_day_is_mean_over_products_with_rows(self) -> None:
        p = np.array(["A", "A", "B", "C", "A"])
        d = np.array(["d1", "d1", "d1", "d1", "d2"])
        pnl = np.array([1.0, 2.0, 0.0, -3.0, 4.0])
        daily = portfolio_daily(p, d, pnl)
        assert daily["d1"] == pytest.approx((3.0 + 0.0 - 3.0) / 3) and daily["d2"] == 4.0

    def test_split_score_known_answer(self) -> None:
        p = np.array(["A", "B", "A"])
        d = np.array(["d1", "d1", "d2"])
        t = np.array([0, 0, 1440]) * NS_MIN
        x = t + 30 * NS_MIN
        y = np.array([0.5, -0.2, 0.3])
        c = np.array([0.1, 0.1, 0.1])
        y_hat = np.array([0.2, -0.5, -0.05])  # long, short, flat
        s = split_score(p, d, t, x, y, c, y_hat)
        # d1: A +0.5, B -(-0.2) - 0.2 = 0.0 -> mean 0.25; d2: A flat 0 -> 0
        assert s.score == pytest.approx(0.125) and s.n_dates == 2 and s.n_trades == 2

    def test_configuration_score_needs_ten_and_ties_go_to_the_smaller_model(self) -> None:
        with pytest.raises(ValueError):
            configuration_score([0.1] * 9)
        cfgs = [({"num_leaves": 31, "min_data_in_leaf": 500, "lambda_l2": 1.0}, 0.2),
                ({"num_leaves": 7, "min_data_in_leaf": 500, "lambda_l2": 1.0}, 0.2),
                ({"num_leaves": 7, "min_data_in_leaf": 2000, "lambda_l2": 1.0}, 0.2),
                ({"num_leaves": 7, "min_data_in_leaf": 2000, "lambda_l2": 10.0}, 0.2)]
        assert select("lgbm", cfgs) == {"num_leaves": 7, "min_data_in_leaf": 2000,
                                        "lambda_l2": 10.0}
        lstm = [({"hidden": 32, "lookback": 24}, 0.1), ({"hidden": 16, "lookback": 72}, 0.1),
                ({"hidden": 16, "lookback": 24}, 0.05)]
        assert select("lstm", lstm) == {"hidden": 16, "lookback": 72}
