"""Known-answer tests for the walk-forward fold builder in data/splits.py.

Every expected value is hand-computed in a comment beside the assert; none is
read back from the implementation.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

from data import splits as sp

# Synthetic calendar: 200 consecutive dates starting at RESEARCH_START, all
# inside the research slice (RESEARCH_START=2025-04-01 .. RESEARCH_END=
# 2026-06-12 is 438 calendar days), so these are valid research dates and
# only the fold arithmetic itself is under test here.
SYNTH_START = sp.RESEARCH_START
SYNTH_DATES = tuple(SYNTH_START + timedelta(days=i) for i in range(200))


def build(dates: tuple[date, ...], **kwargs: int) -> tuple[sp.Fold, ...]:
    defaults = {"train_days": 50, "test_days": 10, "step_days": 10, "embargo_days": 2, "n_folds": 4}
    return sp.build_walk_forward_folds(dates, **{**defaults, **kwargs})


# ============================================================= derive_train_days
class TestDeriveTrainDays:
    def test_gives_142_for_the_real_311_date_research_slice(self) -> None:
        # 311 - 8*21 - 1 = 311 - 168 - 1 = 142.
        assert sp.derive_train_days(311, test_days=21, embargo_days=1, n_folds=8) == 142

    def test_matches_the_module_constant(self) -> None:
        # WF_TRAIN_DAYS = derive_train_days(311, 21, 1, 8) = 311 - 8*21 - 1
        # = 311 - 168 - 1 = 142 (n_research_days=311 is pinned separately by
        # test_311_research_trade_dates below).
        assert sp.WF_TRAIN_DAYS == 142

    def test_is_just_the_leftover_after_folds_and_embargo(self) -> None:
        # 100 days, 3 folds of 5, embargo 1: 100 - 3*5 - 1 = 84.
        assert sp.derive_train_days(100, test_days=5, embargo_days=1, n_folds=3) == 84


# ==================================================================== invariants
class TestFoldInvariants:
    """Synthetic dates: train_days=50, test_days=10, step_days=10, embargo_days=2, n_folds=4."""

    folds = build(SYNTH_DATES)

    def test_four_folds_in_chronological_order(self) -> None:
        assert [f.index for f in self.folds] == [0, 1, 2, 3]
        # index 0 must be the earliest test window, index 3 the latest.
        assert self.folds[0].test_start < self.folds[-1].test_start

    def test_no_overlap_between_train_embargo_and_test_within_a_fold(self) -> None:
        for f in self.folds:
            train_set = set(f.train_dates)
            embargo_set = set(f.embargo_dates)
            test_set = set(f.test_dates)
            assert train_set.isdisjoint(embargo_set)
            assert train_set.isdisjoint(test_set)
            assert embargo_set.isdisjoint(test_set)

    def test_train_ends_exactly_embargo_days_sessions_before_test(self) -> None:
        for f in self.folds:
            # embargo_days=2: the 2 dates strictly between train_end and test_start
            # are exactly f.embargo_dates, in order.
            idx_train_end = SYNTH_DATES.index(f.train_end)
            idx_test_start = SYNTH_DATES.index(f.test_start)
            between = SYNTH_DATES[idx_train_end + 1 : idx_test_start]
            assert between == f.embargo_dates
            assert len(f.embargo_dates) == 2

    def test_train_length_is_fixed_across_folds(self) -> None:
        for f in self.folds:
            assert len(f.train_dates) == 50  # train_days=50

    def test_test_windows_are_contiguous_non_overlapping_and_cover_the_tail(self) -> None:
        # step_days == test_days == 10, n_folds=4 -> last 40 dates of SYNTH_DATES,
        # split into 4 contiguous 10-date blocks with no gaps and no overlap.
        all_test_dates: list[date] = []
        for f in self.folds:
            assert len(f.test_dates) == 10
            all_test_dates.extend(f.test_dates)
        assert len(set(all_test_dates)) == 40  # no overlap (would collapse the set)
        assert tuple(all_test_dates) == SYNTH_DATES[-40:]  # exactly the last 40, contiguous
        # last fold's test window ends on the very last input date.
        assert self.folds[-1].test_end == SYNTH_DATES[-1]

    def test_each_fold_test_start_is_step_days_before_the_next(self) -> None:
        for earlier, later in zip(self.folds, self.folds[1:], strict=False):
            idx_earlier = SYNTH_DATES.index(earlier.test_start)
            idx_later = SYNTH_DATES.index(later.test_start)
            assert idx_later - idx_earlier == 10  # step_days=10

    def test_fold_dataclass_properties(self) -> None:
        # Fold 0 (train_days=50, embargo_days=2, test_days=10) has 50
        # train_dates and 10 test_dates, so train_dates[0]/[-1] and
        # test_dates[0]/[-1] are simply its first and last elements by
        # construction; the properties must return exactly those, not a
        # recomputed or off-by-one index.
        f = self.folds[0]
        assert f.train_start == f.train_dates[0]
        assert f.train_end == f.train_dates[-1]
        assert f.test_start == f.test_dates[0]
        assert f.test_end == f.test_dates[-1]


# ======================================================================= refusals
class TestRefusals:
    def test_unsorted_dates_refused(self) -> None:
        bad = (SYNTH_DATES[1], SYNTH_DATES[0], *SYNTH_DATES[2:])
        with pytest.raises(ValueError, match="strictly increasing"):
            build(bad)

    def test_duplicate_dates_refused(self) -> None:
        bad = (SYNTH_DATES[0], SYNTH_DATES[0], *SYNTH_DATES[1:])
        with pytest.raises(ValueError, match="strictly increasing"):
            build(bad)

    def test_holdout_date_refused_with_holdout_in_message(self) -> None:
        bad = (*SYNTH_DATES[:5], sp.HOLDOUT_START)
        with pytest.raises(ValueError, match="holdout") as exc_info:
            build(bad, train_days=1, test_days=1, step_days=1, embargo_days=0, n_folds=1)
        assert "holdout" in str(exc_info.value)

    def test_embargo_date_refused_with_embargo_in_message(self) -> None:
        bad = (*SYNTH_DATES[:5], sp.EMBARGO_START)
        with pytest.raises(ValueError, match="embargo"):
            build(bad, train_days=1, test_days=1, step_days=1, embargo_days=0, n_folds=1)

    def test_date_before_research_start_refused(self) -> None:
        before = sp.RESEARCH_START - timedelta(days=1)
        bad = (before, *SYNTH_DATES[:5])
        with pytest.raises(ValueError, match="not a research trade date"):
            build(bad, train_days=1, test_days=1, step_days=1, embargo_days=0, n_folds=1)

    def test_insufficient_history_refused(self) -> None:
        # 20 dates, but a train window of 50 can never fit before any test window.
        with pytest.raises(ValueError, match="lacks .* days of history"):
            build(SYNTH_DATES[:20])

    # ---- fold-parameter validation: these guard against IndexError / silent
    # overlap, so they check the message rather than any date arithmetic.
    def test_zero_train_days_refused(self) -> None:
        with pytest.raises(ValueError, match="train_days must be >= 1"):
            build(SYNTH_DATES, train_days=0)

    def test_negative_train_days_refused(self) -> None:
        with pytest.raises(ValueError, match="train_days must be >= 1"):
            build(SYNTH_DATES, train_days=-1)

    def test_zero_test_days_refused(self) -> None:
        with pytest.raises(ValueError, match="test_days must be >= 1"):
            build(SYNTH_DATES, test_days=0, step_days=0)

    def test_negative_test_days_refused(self) -> None:
        with pytest.raises(ValueError, match="test_days must be >= 1"):
            build(SYNTH_DATES, test_days=-1, step_days=-1)

    def test_zero_n_folds_refused(self) -> None:
        with pytest.raises(ValueError, match="n_folds must be >= 1"):
            build(SYNTH_DATES, n_folds=0)

    def test_negative_n_folds_refused(self) -> None:
        with pytest.raises(ValueError, match="n_folds must be >= 1"):
            build(SYNTH_DATES, n_folds=-1)

    def test_negative_embargo_days_refused(self) -> None:
        with pytest.raises(ValueError, match="embargo_days must be >= 0"):
            build(SYNTH_DATES, embargo_days=-1)

    def test_step_days_less_than_test_days_refused(self) -> None:
        # step_days=5 < test_days=10 would make consecutive test windows
        # overlap by 5 dates; must be refused before any index arithmetic runs.
        with pytest.raises(ValueError, match="step_days .* must be >= test_days"):
            build(SYNTH_DATES, test_days=10, step_days=5)

    def test_step_days_equal_to_test_days_is_the_boundary_and_is_accepted(self) -> None:
        # step_days == test_days (the module's own WF_STEP_DAYS = WF_TEST_DAYS
        # choice) is the boundary case and must NOT raise.
        folds = build(SYNTH_DATES, test_days=10, step_days=10)
        assert len(folds) == 4  # n_folds default is 4; no exception means acceptance


# ============================================================= the real calendar
class TestRealCalendar:
    calendar_dates = sp.research_trade_dates_from_calendar()

    def test_311_research_trade_dates(self) -> None:
        # Hand count: 2025-04-01 (Tue) .. 2026-06-12 (Fri) inclusive is 438
        # calendar days ((date(2026,6,12) - date(2025,4,1)).days + 1 = 438).
        # 438 = 62*7 + 4: 62 complete Mon-Fri weeks = 62*5 = 310 weekdays, plus
        # the trailing 4 days (Tue,Wed,Thu,Fri right before the Fri end date)
        # are all weekdays too, so 310 + 4 = 314 weekdays in range.
        # Full-closure weekdays in range (data/cme_calendar.py HOLIDAYS):
        # Good Friday 2025-04-18, Christmas 2025-12-25, New Year's 2026-01-01
        # -> 3 full closures. 314 - 3 = 311.
        assert len(self.calendar_dates) == 311

    def test_first_and_last_calendar_dates(self) -> None:
        # RESEARCH_START (2025-04-01, a Tuesday) is a weekday and not one of
        # the 3 full-closure dates, so it is calendar_dates[0]. RESEARCH_END
        # (2026-06-12, a Friday) is likewise a weekday and not a full-closure
        # date, so it is calendar_dates[-1].
        assert self.calendar_dates[0] == date(2025, 4, 1) == sp.RESEARCH_START
        assert self.calendar_dates[-1] == date(2026, 6, 12) == sp.RESEARCH_END

    def test_early_halt_days_are_kept_as_trade_dates(self) -> None:
        # 2026-04-03 Good Friday (abbreviated session, jobs report): EARLY_HALT,
        # not FULL_CLOSURE, so it must be present.
        assert date(2026, 4, 3) in self.calendar_dates

    def test_full_closure_days_are_excluded(self) -> None:
        for closure_day in (date(2025, 4, 18), date(2025, 12, 25), date(2026, 1, 1)):
            assert closure_day not in self.calendar_dates

    def test_real_folds_have_8_folds_matching_lead_endpoints(self) -> None:
        folds = sp.walk_forward_folds(self.calendar_dates)
        assert len(folds) == 8
        # Fold 0 train start on RESEARCH_START: derived so that the train
        # window of 142 dates starting at calendar_dates index 0 lands here.
        assert folds[0].train_start == date(2025, 4, 1)
        # Fold 7 test end on RESEARCH_END: the grid is anchored at the end of
        # the research slice by construction.
        assert folds[-1].test_end == date(2026, 6, 12)

    def test_every_research_date_appears_in_at_least_one_train_or_test_window(self) -> None:
        folds = sp.walk_forward_folds(self.calendar_dates)
        covered: set[date] = set()
        for f in folds:
            covered.update(f.train_dates)
            covered.update(f.test_dates)
        assert covered == set(self.calendar_dates)

    def test_real_test_windows_are_non_overlapping_and_chronological(self) -> None:
        folds = sp.walk_forward_folds(self.calendar_dates)
        seen: set[date] = set()
        prev_test_end = None
        for f in folds:
            assert seen.isdisjoint(f.test_dates)
            seen.update(f.test_dates)
            if prev_test_end is not None:
                assert f.test_start > prev_test_end
            prev_test_end = f.test_end
        # 8 folds * 21 test days = 168 out-of-sample dates total, no double count.
        assert len(seen) == 168

    def test_real_train_windows_are_exactly_142_dates(self) -> None:
        for f in sp.walk_forward_folds(self.calendar_dates):
            assert len(f.train_dates) == sp.WF_TRAIN_DAYS == 142

    def test_real_embargo_is_exactly_one_date_per_fold(self) -> None:
        # WF_EMBARGO_DAYS = 1 -- every fold's embargo_dates tuple must have
        # exactly that many entries.
        for f in sp.walk_forward_folds(self.calendar_dates):
            assert len(f.embargo_dates) == 1

    def test_full_fold_table_matches_hand_computed_boundary_dates(self) -> None:
        """Pin every fold's train/embargo/test boundaries, not just fold 0/7.

        Index arithmetic (train_days=142, test_days=step_days=21,
        embargo_days=1, n_folds=8, n_dates=311) gives, for fold f:
        test_start_idx = 311 - (8-f)*21 = 143 + 21*f, train_start_idx =
        test_start_idx - 1 (embargo) - 142 (train) = 21*f,
        embargo_start_idx = test_start_idx - 1, train_end_idx =
        embargo_start_idx - 1, test_end_idx = test_start_idx + 20. That
        fixes each fold's 5 boundary indices from f alone.

        Each boundary index below was converted to its calendar date by
        counting forward, one weekday at a time, from RESEARCH_START
        (2025-04-01, a Tuesday) -- i.e. by walking the calendar and
        skipping Saturdays, Sundays, and the 3 FULL_CLOSURE dates
        (2025-04-18, 2025-12-25, 2026-01-01; see data/cme_calendar.py) --
        done independently of both ``research_trade_dates_from_calendar``
        and ``build_walk_forward_folds``, then cross-checked against the
        two anchors already pinned above (fold 0 train_start ==
        RESEARCH_START at index 0, fold 7 test_end == RESEARCH_END at
        index 310) and against fold 1's embargo (2025-11-17) and fold 3's
        test_start (2026-01-19), both independently verified.
        """
        folds = sp.walk_forward_folds(self.calendar_dates)
        assert len(folds) == 8

        # (train_start, train_end, embargo, test_start, test_end) ISO dates
        # per fold, hand-counted as described in the docstring above.
        expected = [
            ("2025-04-01", "2025-10-16", "2025-10-17", "2025-10-20", "2025-11-17"),
            ("2025-05-01", "2025-11-14", "2025-11-17", "2025-11-18", "2025-12-16"),
            ("2025-05-30", "2025-12-15", "2025-12-16", "2025-12-17", "2026-01-16"),
            ("2025-06-30", "2026-01-15", "2026-01-16", "2026-01-19", "2026-02-16"),
            ("2025-07-29", "2026-02-13", "2026-02-16", "2026-02-17", "2026-03-17"),
            ("2025-08-27", "2026-03-16", "2026-03-17", "2026-03-18", "2026-04-15"),
            ("2025-09-25", "2026-04-14", "2026-04-15", "2026-04-16", "2026-05-14"),
            ("2025-10-24", "2026-05-13", "2026-05-14", "2026-05-15", "2026-06-12"),
        ]
        for f, row in zip(folds, expected, strict=True):
            train_start, train_end, embargo, test_start, test_end = (
                date.fromisoformat(iso) for iso in row
            )
            assert f.train_start == train_start
            assert f.train_end == train_end
            assert f.embargo_dates == (embargo,)
            assert f.test_start == test_start
            assert f.test_end == test_end


# ==================================================================== module main
class TestMain:
    def test_main_writes_the_report_json(self, tmp_path, monkeypatch) -> None:
        report_path = tmp_path / "reports" / "walk_forward_folds.json"
        monkeypatch.setattr(sp, "REPO_ROOT", tmp_path)
        sp.main()
        assert report_path.is_file()

        report = json.loads(report_path.read_text())
        # WF_TRAIN_DAYS == 142 (see TestDeriveTrainDays.test_matches_the_module_constant).
        assert report["constants"]["WF_TRAIN_DAYS"] == 142
        # WF_N_FOLDS == 8.
        assert len(report["folds"]) == 8
        # Fold 0's train window starts exactly on RESEARCH_START by construction.
        assert report["folds"][0]["train_start"] == "2025-04-01"
        # Fold 7 (the last) is anchored to end exactly on RESEARCH_END.
        assert report["folds"][-1]["test_end"] == "2026-06-12"
