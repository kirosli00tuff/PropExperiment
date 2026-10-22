"""Sessions, the placement grid, holidays, roll days and request bounds (spec section 2)."""

from datetime import date

import numpy as np
import pilot_common as pc
import pytest


@pytest.fixture(scope="module")
def es_cal():
    return pc.calendar_for("ES")


def iso(ns):
    return pc.iso_ns(ns)[:19]


def test_equity_trade_date_pieces_and_grid(es_cal):
    # 2023-11-14 (CST): open 11-13 17:00 CT = 23:00Z to 16:00 CT = 22:00Z; MAIN 06:30-13:00 PT
    # = 14:30Z-21:00Z. Grid: MAIN 14:35Z..20:50Z = 76; evening 23:05Z..14:20Z = 184;
    # 13:00-14:00 PT 21:05Z..21:50Z = 10.
    plan = pc.build_day_plan(es_cal, date(2023, 11, 14))
    assert [(p.label, iso(p.lo), iso(p.hi)) for p in plan.pieces] == [
        ("OVERNIGHT", "2023-11-13T23:00:00", "2023-11-14T14:30:00"),
        ("MAIN", "2023-11-14T14:30:00", "2023-11-14T21:00:00"),
        ("OVERNIGHT", "2023-11-14T21:00:00", "2023-11-14T22:00:00")]
    assert np.bincount(plan.grid_piece).tolist() == [184, 76, 10]
    main = plan.grid_ns[plan.grid_piece == 1]
    assert iso(main[0]) == "2023-11-14T14:35:00" and iso(main[-1]) == "2023-11-14T20:50:00"
    assert not np.all(np.diff(plan.grid_ns) == pc.GRID_NS)  # gaps between pieces
    assert np.all(plan.grid_ns % pc.GRID_NS == 0)


def test_grains_pause_holds_no_placement():
    # ZC: overnight 19:00 CT-07:45 CT, pause, day 08:30-13:20 CT. MAIN = 08:30-13:20 CT
    # (14:30Z-19:20Z): 08:35..13:10 CT = 56; overnight 19:05..07:35 CT = 151.
    plan = pc.build_day_plan(pc.calendar_for("ZC"), date(2023, 11, 14))
    assert [(p.label, iso(p.lo), iso(p.hi)) for p in plan.pieces] == [
        ("OVERNIGHT", "2023-11-14T01:00:00", "2023-11-14T13:45:00"),
        ("MAIN", "2023-11-14T14:30:00", "2023-11-14T19:20:00")]
    assert np.bincount(plan.grid_piece).tolist() == [151, 56]


@pytest.mark.parametrize("day", [date(2023, 11, 23), date(2023, 11, 24), date(2024, 1, 15),
                                 date(2024, 2, 19)])
def test_holiday_and_early_close_dates_are_excluded(es_cal, day):
    plan = pc.build_day_plan(es_cal, day)
    assert plan.holiday is not None
    assert pc.EXCL_HOLIDAY in pc.static_exclusions(plan, 0, 2**62)


def test_closed_dates_are_not_trade_dates(es_cal):
    for day in (date(2023, 12, 25), date(2024, 1, 1), date(2023, 11, 18)):
        plan = pc.build_day_plan(es_cal, day)
        assert not plan.is_trade_date and plan.pieces == ()
        assert pc.static_exclusions(plan, 0, 2**62) == [pc.EXCL_NOT_TRADE]


def test_cutoff_and_incomplete_coverage(es_cal):
    plan = pc.build_day_plan(es_cal, date(2024, 3, 1))
    assert pc.EXCL_CUTOFF in pc.static_exclusions(plan, 0, 2**62)
    regular = pc.build_day_plan(es_cal, date(2023, 11, 14))
    assert pc.static_exclusions(regular, regular.open_lo, regular.open_hi) == []
    assert pc.static_exclusions(regular, regular.open_lo + 1, regular.open_hi) == \
        [pc.EXCL_COVERAGE]
    assert pc.static_exclusions(regular, regular.open_lo, regular.open_hi - 1) == \
        [pc.EXCL_COVERAGE]


def test_outside_calendar_coverage():
    plan = pc.build_day_plan(pc.calendar_for("ES"), date(2018, 1, 9))
    assert pc.static_exclusions(plan, 0, 2**62) == [pc.EXCL_CALENDAR]


@pytest.mark.parametrize(("day", "bound"), [
    (date(2023, 11, 14), "2023-11-13T22:00:00Z"),   # CST: 16:00 CT = 22:00Z
    (date(2023, 11, 6), "2023-11-05T22:00:00Z"),    # Monday after DST ended (Sunday 16:00 CST)
    (date(2023, 11, 3), "2023-11-02T21:00:00Z"),    # CDT: 16:00 CT = 21:00Z
])
def test_start_bound_holds_the_whole_trade_date(es_cal, day, bound):
    assert pc.start_bound(day) == bound
    assert pc.first_whole_trade_date(bound, es_cal) == day


def test_first_whole_trade_date_of_an_unaligned_start(es_cal):
    # 2023-11-01 00:00Z is 19:00 CDT of 10-31: trade date 11-01 is partial; 11-02 is whole
    assert pc.first_whole_trade_date("2023-11-01", es_cal) == date(2023, 11, 2)


def test_day_windows_group_the_preopen_into_the_next_trade_date():
    lo, hi = pc.day_window_ns(date(2023, 11, 14))
    assert iso(lo) == "2023-11-13T22:00:00" and iso(hi) == "2023-11-14T22:00:00"


def test_candidate_days_of_a_pilot_file(es_cal):
    lo = pc.bound_ns(pc.start_bound(date(2024, 2, 27)))
    hi = pc.bound_ns(pc.CUTOFF_BOUND)
    days = pc.candidate_days(es_cal, lo, hi)
    # 02-27, 02-28, 02-29 only: the request ends 2024-02-29T22:00Z (16:00 CST, RS-01), before
    # trade date 03-01 opens at 17:00 CST (23:00Z), so 03-01 is not a candidate
    assert days == [date(2024, 2, 27), date(2024, 2, 28), date(2024, 2, 29)]
    # the old bound 2024-03-01 00:00Z did hold 17:00-18:00 CST of trade date 03-01
    old_hi = pc.bound_ns("2024-03-01")
    assert pc.candidate_days(es_cal, lo, old_hi)[-1] == date(2024, 3, 1)


# ------------------------------------------------------------------ rolls ----
def test_roll_day_and_the_day_after_are_excluded(es_cal):
    ids = {date(2023, 12, 11): ["A"], date(2023, 12, 12): ["A", "B"],
           date(2023, 12, 13): ["B"], date(2023, 12, 14): ["B"]}
    got = pc.roll_exclusions(sorted(ids), ids, es_cal)
    assert got == {date(2023, 12, 12): pc.EXCL_ROLL, date(2023, 12, 13): pc.EXCL_AFTER_ROLL}


def test_roll_at_a_trade_date_boundary(es_cal):
    # Friday on A, Monday on B: Monday is the roll day, Tuesday the day after
    ids = {date(2023, 12, 8): ["A"], date(2023, 12, 11): ["B"], date(2023, 12, 12): ["B"],
           date(2023, 12, 13): ["B"]}
    got = pc.roll_exclusions(sorted(ids), ids, es_cal)
    assert got == {date(2023, 12, 11): pc.EXCL_ROLL, date(2023, 12, 12): pc.EXCL_AFTER_ROLL}


def test_mapped_ids_from_symbology_intervals(es_cal):
    # the mapping changes at 00:00Z of 2023-12-12: trade date 12-12 (open 12-11 23:00Z) has both
    intervals = [{"start_date": date(2023, 12, 1), "end_date": date(2023, 12, 12), "symbol": "A"},
                 {"start_date": date(2023, 12, 12), "end_date": date(2024, 3, 1), "symbol": "B"}]
    p11 = pc.build_day_plan(es_cal, date(2023, 12, 11))
    p12 = pc.build_day_plan(es_cal, date(2023, 12, 12))
    assert pc.mapped_ids(intervals, p11.open_lo, p11.open_hi) == ["A"]
    assert pc.mapped_ids(intervals, p12.open_lo, p12.open_hi) == ["A", "B"]
