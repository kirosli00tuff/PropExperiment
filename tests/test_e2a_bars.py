"""Stage E.2a Task 7: the generalized bar builder (data.build_bars, data.group_session).

Known answers on SYNTHETIC bars and synthetic group calendars (the documented structures: the
grain 19:00 start and 07:45-08:30 pause, livestock day-only, the crypto regime split with weekend
assignment), plus two real-data checks that read only MES's own research files: the MES
regression (the generalized path reproduces the MES research parquet row for row) and the pin of
that parquet's sha256.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import date, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from data.adapter import RollBoundary
from data.bars import outright_pattern, raw_symbols_on_bar_dates
from data.build_bars import (
    ROLL_BLACKOUT_SESSIONS,
    BuildRefused,
    InputFile,
    ProductSpec,
    build_product,
    existing_matches,
    grid_scale_probe,
    load_ticks,
    parse_tick,
    tick_fixed,
    write_parquet,
)
from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Holiday, HolidayKind
from data.config import REPO_ROOT
from data.group_session import (
    MES_POLICY,
    STAGE_E_POLICIES,
    GroupCalendar,
    assign_trade_dates,
    closed_windows,
    flatten_masks,
    load_group_calendar,
    open_intervals,
    roll_blackout,
    sha256_file,
    utc_midnight_ns,
)
from data.research_bars import HoldoutLeakError, refuse_dates_outside
from data.session import closed_windows_range_ns, ct_ns, trade_date
from data.validate import (
    EARLY_STOP_NOT_LISTED,
    ENTRY_NOT_OBSERVED,
    UNLISTED_CLOSURE,
    in_windows,
    validate_bars,
    validate_calendar_group,
    validate_calendar_step4b,
)

M = 60 * 1_000_000_000
T = time
INIT = REPO_ROOT / "data" / "calendars" / "__init__.py"


def _cal(group: str, segments: tuple[Segment, ...], holidays: dict | None = None,
         specs: tuple[SessionSpec, ...] | None = None, weekend_from: date | None = None,
         close: time = time(15, 0)) -> GroupCalendar:
    specs = specs or (SessionSpec(date(2025, 1, 1), None, segments, {"*": (time(8, 30), close)},
                                  "synthetic"),)
    first, last = date(2025, 1, 1), date(2026, 12, 31)

    def cover(days):  # noqa: ANN001, ANN202
        out = [d for d in days if not first <= d <= last]
        if out:
            raise CalendarCoverageError(f"outside: {out[0]}")

    return GroupCalendar(group, holidays or {}, specs, (first, last), cover, (INIT,),
                         weekend_to_next_trade_date_from=weekend_from)


GRAINS = (Segment(-1, T(19, 0), 0, T(7, 45)), Segment(0, T(8, 30), 0, T(13, 20)))
LIVESTOCK = (Segment(0, T(8, 30), 0, T(13, 5)),)
GLOBEX = (Segment(-1, T(17, 0), 0, T(16, 0)),)


def _td(cal: GroupCalendar, *instants: int) -> list[tuple[str | None, bool]]:
    opened = open_intervals(cal, date(2025, 9, 1), date(2025, 9, 30))
    got = assign_trade_dates(opened, np.array(instants, dtype=np.int64))
    return [(None if d is None else d.isoformat(), bool(c))
            for d, c in zip(got.as_dates(), got.in_closure, strict=True)]


# ------------------------------------------------------------ trade dates per group ----
def test_equity_calendar_matches_data_session_on_every_open_minute() -> None:
    cal = load_group_calendar("equity")
    first, last = date(2025, 11, 20), date(2026, 1, 10)  # Thanksgiving, Christmas, New Year
    opened = open_intervals(cal, first - timedelta(days=3), last + timedelta(days=3))
    lo, hi = utc_midnight_ns(first), utc_midnight_ns(last)
    starts, ends = closed_windows(opened, lo, hi)
    mes = closed_windows_range_ns(first, last)
    grid = np.arange(lo, hi, M, dtype=np.int64)
    closed = in_windows(grid, starts, ends)
    assert (closed == in_windows(grid, np.array([w[0] for w in mes]),
                                 np.array([w[1] for w in mes]))).all()
    open_minutes = grid[~closed][::13]
    got = assign_trade_dates(opened, open_minutes).as_dates()
    assert got == [trade_date(int(t)) for t in open_minutes]


def test_grain_session_starts_1900_and_pauses_0745_to_0830() -> None:
    cal = _cal("grains", GRAINS)
    # Sunday 2025-09-14 19:00 CT opens Monday 09-15; 18:59 is closed and belongs to Monday too.
    assert _td(cal, ct_ns(date(2025, 9, 14), T(19, 0)), ct_ns(date(2025, 9, 14), T(18, 59))) == [
        ("2025-09-15", False), ("2025-09-15", True)]
    mon = date(2025, 9, 15)
    assert _td(cal, ct_ns(mon, T(7, 44)), ct_ns(mon, T(7, 45)), ct_ns(mon, T(8, 29)),
               ct_ns(mon, T(8, 30)), ct_ns(mon, T(13, 19)), ct_ns(mon, T(13, 20)),
               ct_ns(mon, T(19, 0))) == [
        ("2025-09-15", False), ("2025-09-15", True), ("2025-09-15", True),
        ("2025-09-15", False), ("2025-09-15", False), ("2025-09-16", True),
        ("2025-09-16", False)]
    # Friday 13:20 CT to Sunday 19:00 CT is closed; it belongs to the next Monday.
    assert _td(cal, ct_ns(date(2025, 9, 19), T(13, 20)), ct_ns(date(2025, 9, 20), T(12, 0))) == [
        ("2025-09-22", True), ("2025-09-22", True)]


def test_grain_holiday_full_closure_and_early_close() -> None:
    hol = {date(2025, 9, 1): Holiday(date(2025, 9, 1), "Labor Day", HolidayKind.FULL_CLOSURE,
                                     None, "cme", "n/a"),
           date(2025, 9, 3): Holiday(date(2025, 9, 3), "x", HolidayKind.EARLY_HALT, T(12, 5),
                                     "cme", "cme")}
    cal = _cal("grains", GRAINS, hol)
    # No session opens Sunday 19:00 for the closed Monday; Monday 19:00 opens Tuesday.
    assert _td(cal, ct_ns(date(2025, 8, 31), T(20, 0)), ct_ns(date(2025, 9, 1), T(19, 0))) == [
        ("2025-09-02", True), ("2025-09-02", False)]
    assert _td(cal, ct_ns(date(2025, 9, 3), T(12, 4)), ct_ns(date(2025, 9, 3), T(12, 5))) == [
        ("2025-09-03", False), ("2025-09-04", True)]


def test_livestock_is_day_only() -> None:
    cal = _cal("livestock", LIVESTOCK)
    d = date(2025, 9, 16)
    assert _td(cal, ct_ns(d, T(8, 29)), ct_ns(d, T(8, 30)), ct_ns(d, T(13, 4)),
               ct_ns(d, T(13, 5)), ct_ns(d - timedelta(days=1), T(20, 0))) == [
        ("2025-09-16", True), ("2025-09-16", False), ("2025-09-16", False),
        ("2025-09-17", True), ("2025-09-16", True)]


def test_crypto_regime_split_and_weekend_assignment() -> None:
    split = date(2026, 5, 29)
    old = SessionSpec(date(2025, 1, 1), split - timedelta(days=1), GLOBEX,
                      {"*": (T(8, 30), T(15, 0))}, "old")
    new = SessionSpec(split, None, (Segment(-1, T(17, 0), 0, T(17, 0)),),
                      {"*": (T(8, 30), T(15, 0))}, "24/7")
    cal = _cal("crypto", GLOBEX, specs=(old, new), weekend_from=split)
    opened = open_intervals(cal, date(2026, 5, 18), date(2026, 6, 12))
    sat_old, sat_new = ct_ns(date(2026, 5, 23), T(10, 0)), ct_ns(date(2026, 6, 6), T(10, 0))
    fri_1630 = ct_ns(date(2026, 6, 5), T(16, 30))
    fri_1700 = ct_ns(date(2026, 6, 5), T(17, 0))
    got = assign_trade_dates(opened, np.array([sat_old, sat_new, fri_1630, fri_1700]))
    assert [d.isoformat() for d in got.as_dates()] == ["2026-05-25", "2026-06-08",
                                                       "2026-06-05", "2026-06-08"]
    # No holiday is listed in this synthetic calendar, so the old-regime Saturday bar is a
    # closure bar assigned to the next session (Monday 05-25); the new-regime weekend is open.
    assert got.in_closure.tolist() == [True, False, False, False]
    days = got.days[1:]
    flat, nonew = flatten_masks(cal, STAGE_E_POLICIES["crypto"], np.array([sat_new, fri_1630,
                                                                            fri_1700]), days)
    assert flat.tolist() == [True, True, True]  # weekend (TopstepX closed) and Friday >= 15:08
    assert nonew.tolist() == [True, True, True]


def test_sessions_that_overlap_are_refused() -> None:
    from data.group_session import SessionModelError

    bad = _cal("rates", (Segment(-2, T(17, 0), 0, T(16, 0)),))
    with pytest.raises(SessionModelError):
        open_intervals(bad, date(2025, 9, 15), date(2025, 9, 19))


# ------------------------------------------------------------ closed windows, flatten ----
def test_closed_windows_are_the_complement_of_the_sessions() -> None:
    cal = _cal("livestock", LIVESTOCK)
    d = date(2025, 9, 16)
    opened = open_intervals(cal, d, d)
    lo, hi = ct_ns(d, T(0, 0)), ct_ns(d, T(23, 0))
    starts, ends = closed_windows(opened, lo, hi)
    assert list(zip(starts.tolist(), ends.tolist(), strict=True)) == [
        (lo, ct_ns(d, T(8, 30))), (ct_ns(d, T(13, 5)), hi)]


def test_flatten_policies_per_group() -> None:
    assert STAGE_E_POLICIES["rates"].flatten_on(None) == T(15, 8)
    assert STAGE_E_POLICIES["rates"].no_new_on(None) == T(15, 8)
    assert STAGE_E_POLICIES["energy"].flatten_on(T(13, 45)) == T(13, 30)  # early close - 15
    assert STAGE_E_POLICIES["grains"].flatten_on(None) == T(13, 18)
    assert STAGE_E_POLICIES["grains"].flatten_on(T(12, 5)) == T(11, 50)
    assert STAGE_E_POLICIES["livestock"].flatten_on(None) == T(13, 3)
    from rules.xfa_rules import flatten_time_ct, no_new_positions_time_ct

    for halt in (None, T(12, 0), T(12, 15), T(8, 15)):
        assert MES_POLICY.flatten_on(halt) == flatten_time_ct(halt)
        assert MES_POLICY.no_new_on(halt) == no_new_positions_time_ct(halt)


def test_grain_position_may_not_be_held_into_the_pause() -> None:
    cal = _cal("grains", GRAINS)
    d = date(2025, 9, 16)
    ts = np.array([ct_ns(d, T(7, 42)), ct_ns(d, T(7, 43)), ct_ns(d, T(7, 44)),
                   ct_ns(d, T(8, 30)), ct_ns(d, T(13, 17)), ct_ns(d, T(13, 18))])
    days = np.array([np.datetime64(d, "D")] * len(ts))
    flat, nonew = flatten_masks(cal, STAGE_E_POLICIES["grains"], ts, days)
    assert flat.tolist() == [False, True, True, False, False, True]
    assert nonew.tolist() == flat.tolist()


# ------------------------------------------------------------ roll blackout ----
def test_roll_blackout_is_the_splice_and_two_group_sessions_before() -> None:
    from screening.runner import CANONICAL_ROLL_BLACKOUT_SESSIONS
    from sim.engine import roll_blackout_dates

    assert ROLL_BLACKOUT_SESSIONS == CANONICAL_ROLL_BLACKOUT_SESSIONS
    cal = _cal("rates", GLOBEX)
    splice = date(2025, 9, 16)  # Tuesday: Monday and the Friday before
    assert roll_blackout(cal, [splice], 2) == {date(2025, 9, 16), date(2025, 9, 15),
                                               date(2025, 9, 12)}
    assert roll_blackout(cal, [splice], 2) == roll_blackout_dates([splice], 2)
    hol = {date(2025, 9, 15): Holiday(date(2025, 9, 15), "group-only closure",
                                      HolidayKind.FULL_CLOSURE, None, "cme", "n/a")}
    grains = _cal("grains", GRAINS, hol)
    assert roll_blackout(grains, [splice], 2) == {date(2025, 9, 16), date(2025, 9, 12),
                                                  date(2025, 9, 11)}


# ------------------------------------------------------------ ticks ----
def test_ticks_parse_from_the_e0_strings() -> None:
    assert parse_tick("1/2 of 1/32 (0.015625)") == "0.015625"
    assert parse_tick("1/8 of 1/32 (0.00390625)") == "0.00390625"
    assert parse_tick("0.0025 (USD per bushel; quoted in cents: 1/4 cent)") == "0.0025"
    assert parse_tick("5.00 (USD per bitcoin)") == "5.00"
    assert parse_tick("0.10") == "0.10"
    assert tick_fixed("0.015625") == 15_625_000 and tick_fixed("0.0000005") == 500
    ticks = load_ticks()
    assert ticks["ZN"][0] == "0.015625" and ticks["6J"][0] == "0.0000005"
    for root, (tick, _) in ticks.items():
        assert tick_fixed(tick) > 0, root


def _raw(ts: list[int], price: int, volume: int = 3, source: str = "f.dbn.zst",
         iid: int = 7) -> pd.DataFrame:
    n = len(ts)
    return pd.DataFrame({"ts_event": np.array(ts, dtype=np.int64), "instrument_id": [iid] * n,
                         "open_fixed": [price] * n, "high_fixed": [price] * n,
                         "low_fixed": [price] * n, "close_fixed": [price] * n,
                         "volume": [volume] * n, "source_file": [source] * n})


def test_off_tick_prices_are_a_hard_failure_at_the_products_tick() -> None:
    t0 = ct_ns(date(2025, 9, 16), T(9, 0))
    empty = np.array([], dtype=np.int64)
    on_grid = _raw([t0], 110_515_625_000)  # 110.515625 = 7073 ticks of 1/64
    off_grid = _raw([t0], 110_510_000_000)
    ok, _ = validate_bars(on_grid, t0, t0 + M, empty, empty, 15_625_000, "0.015625")
    bad, _ = validate_bars(off_grid, t0, t0 + M, empty, empty, 15_625_000, "0.015625")
    assert ok.off_tick_prices == 0 and not ok.hard_failures
    assert bad.off_tick_prices == 4
    assert bad.hard_failures == ["4 prices off the 0.015625 tick grid"]
    # A cent-quoted grain on the E.0 tick 0.0025: 4.5025 (USD) is on the 1x grid only, while
    # 450.25 (cents) is on the 1x, 10x and 100x grids: the probe exposes the vendor's scale.
    assert grid_scale_probe(_raw([t0], 4_502_500_000), 2_500_000) == {"x1": 0, "x10": 4,
                                                                      "x100": 4}
    assert grid_scale_probe(_raw([t0], 450_250_000_000), 2_500_000) == {"x1": 0, "x10": 0,
                                                                        "x100": 0}


def test_outright_rule_for_any_root() -> None:
    pat = outright_pattern("6E")
    assert pat.fullmatch("6EM5") and not pat.fullmatch("6EM5-6EU5") and not pat.fullmatch("M6EM5")
    ng = outright_pattern("NG")  # NG's raw symbols carry a two-digit year from mid-2025
    assert ng.fullmatch("NGK5") and ng.fullmatch("NGN25") and ng.fullmatch("NGF26")
    assert not ng.fullmatch("NGN25-NGQ25") and not ng.fullmatch("NGN255")
    day = ct_ns(date(2025, 9, 16), T(9, 0))
    intervals = {"7": [{"d0": "2025-09-01", "d1": "2025-10-01", "s": "6EZ5"}],
                 "8": [{"d0": "2025-09-01", "d1": "2025-10-01", "s": "UD:1V: VT 0916"}]}
    syms, unmapped = raw_symbols_on_bar_dates(np.array([day, day]), np.array([7, 8]),
                                              intervals, pat, "6E")
    assert syms.tolist() == ["6EZ5", ""] and unmapped[0]["instrument_id"] == 8


# ------------------------------------------------------------ the build path ----
def _week_bars(days: list[date], start: time, end: time) -> list[int]:
    out: list[int] = []
    for d in days:
        t, stop = ct_ns(d, start), ct_ns(d, end)
        out.extend(range(t, stop, M))
    return out


@pytest.fixture
def synthetic(tmp_path: Path) -> dict:
    """A rates-like product with bars 2026-06-17..2026-06-19 plus a planted post-window bar."""
    f = tmp_path / "range=2026-06-01_2026-06-21.dbn.zst"
    f.write_bytes(b"synthetic")
    cal = _cal("rates", GLOBEX)
    days = [date(2026, 6, 17), date(2026, 6, 18), date(2026, 6, 19)]
    ts = _week_bars(days, T(9, 0), T(9, 5))
    raw = _raw(ts, 110_515_625_000, source=f.name)
    spec = ProductSpec(root="ZN", group="rates", tick="0.015625", tick_source="test",
                       files=(InputFile(f, sha256_file(f), len(raw)),),
                       rolls_path=tmp_path / "rolls.jsonl", symbology_path=None,
                       policy=STAGE_E_POLICIES["rates"], out=tmp_path / "out" / "ZN.parquet",
                       data_start=date(2026, 6, 1))
    rolls = [RollBoundary("ZN.v.0", "2026-06-18", utc_midnight_ns(date(2026, 6, 18)), "6", "7",
                          "ZNM6", "ZNU6")]
    return {"spec": spec, "cal": cal, "raw": raw, "rolls": rolls, "file": f}


def _build(s: dict, raw: pd.DataFrame | None = None):  # noqa: ANN202
    frame = s["raw"] if raw is None else raw
    return build_product(s["spec"], s["cal"], [{"date": "2026-06-18", "condition": "degraded"}],
                         s["rolls"], None, "test", load_bars=lambda _paths: frame.copy())


def test_build_stamps_metadata_and_writes_read_only(synthetic: dict) -> None:
    res = _build(synthetic)
    assert res.summary["status"] == "built", res.summary["refusal_causes"]
    sha = write_parquet(res.frame, res.meta, synthetic["spec"].out)
    out = synthetic["spec"].out
    assert stat.S_IMODE(os.stat(out).st_mode) == 0o444
    meta = json.loads(pq.read_schema(out).metadata[b"propexperiment"])
    assert meta["input_files"] == [{"name": synthetic["file"].name,
                                    "sha256": sha256_file(synthetic["file"])}]
    assert set(meta["calendar_modules"]) == {"data/calendars/__init__.py"}
    assert meta["calendar_modules"]["data/calendars/__init__.py"] == sha256_file(INIT)
    assert meta["builder_files"]["data/build_bars.py"] == sha256_file(
        REPO_ROOT / "data" / "build_bars.py")
    assert meta["rolls"][0]["to_raw_symbol"] == "ZNU6"
    assert meta["splice_trade_dates"] == ["2026-06-18"]
    assert meta["roll_blackout_dates"] == ["2026-06-16", "2026-06-17", "2026-06-18"]
    assert meta["degraded_vendor_days"] == ["2026-06-18"]
    assert meta["validation"]["rows"] == len(res.frame) and sha == sha256_file(out)
    assert existing_matches(synthetic["spec"])
    with pytest.raises(BuildRefused):
        write_parquet(res.frame, res.meta, out)
    table = pq.read_table(out).to_pandas()
    assert table["is_roll_session"].tolist() == [d == "2026-06-18" for d in table["trade_date"]]
    assert table["vendor_degraded_day"].tolist() == table["is_roll_session"].tolist()
    assert list(table.columns) == [
        "ts_event", "open", "high", "low", "close", "volume", "instrument_id", "raw_symbol",
        "in_flatten_window", "in_no_new_positions_window", "early_halt_ct",
        "in_scheduled_closure", "trade_date", "is_roll_session", "gap_before_minutes",
        "vendor_degraded_day"]


def test_out_of_window_trade_dates_are_dropped_and_refused(synthetic: dict) -> None:
    # Sunday 2026-06-21 17:00 CT opens trade date 2026-06-22 (holdout-1): dropped, counted.
    late = _week_bars([date(2026, 6, 21)], T(17, 0), T(17, 3))
    raw = pd.concat([synthetic["raw"], _raw(late, 110_515_625_000,
                                            source=synthetic["file"].name)], ignore_index=True)
    spec = synthetic["spec"]
    spec = ProductSpec(**{**spec.__dict__, "data_end": date(2026, 6, 23), "files": (InputFile(
        synthetic["file"], sha256_file(synthetic["file"]), len(raw)),)})
    res = build_product(spec, synthetic["cal"], [], synthetic["rolls"], None, "test",
                        load_bars=lambda _p: raw.copy())
    assert res.summary["status"] == "built"
    assert res.summary["drops"]["trade_date_after_window"] == {"2026-06-22": 3}
    assert res.summary["last_trade_date"] == "2026-06-19"
    assert set(res.frame["trade_date"].astype(str)) == {"2026-06-17", "2026-06-18", "2026-06-19"}
    with pytest.raises(HoldoutLeakError):
        refuse_dates_outside([date(2026, 6, 22)], frozenset({"research", "research embargo"}),
                             "test")


def test_hard_failures_leave_the_contract_unbuilt(synthetic: dict) -> None:
    bad = synthetic["raw"].copy()
    bad.loc[3, "high_fixed"] = bad.loc[3, "low_fixed"] - 15_625_000  # high below low
    res = _build(synthetic, bad)
    assert res.summary["status"] == "refused" and res.frame is None
    assert any("inconsistent" in c for c in res.summary["refusal_causes"])



def test_closure_bars_follow_ruling_l3(synthetic: dict) -> None:
    # A print in the close minute (16:00 CT) is kept, flagged, and dated to the session it
    # closes; a bar deeper inside a closure holds the product for the lead.
    close_minute = synthetic["raw"].copy()
    close_minute.loc[0, "ts_event"] = ct_ns(date(2026, 6, 17), T(16, 0))
    res = _build(synthetic, close_minute.sort_values("ts_event").reset_index(drop=True))
    assert res.summary["status"] == "built", res.summary["refusal_causes"]
    assert res.summary["closure_bars"] == [{"ct": "2026-06-17 Wed 16:00",
                                            "trade_date": "2026-06-17", "close_minute": True}]
    flagged = res.frame[res.frame["in_scheduled_closure"]]
    assert len(flagged) == 1 and str(flagged["trade_date"].iloc[0]) == "2026-06-17"
    assert bool(flagged["in_flatten_window"].iloc[0])
    deep = synthetic["raw"].copy()
    deep.loc[0, "ts_event"] = ct_ns(date(2026, 6, 17), T(16, 30))  # inside the daily halt
    res = _build(synthetic, deep.sort_values("ts_event").reset_index(drop=True))
    assert res.summary["status"] == "held_for_lead" and res.frame is None
    assert "beyond the close minute" in res.summary["refusal_causes"][0]


def test_late_open_is_checked_not_closed() -> None:
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class LateOpen:
        day: date
        name: str
        open_ct: time
        halt_from_ct: time | None = None
        halt_from_offset_days: int = -1

    base = _cal("rates", GLOBEX)
    cal = GroupCalendar(**{**base.__dict__, "late_opens": {
        date(2025, 11, 28): LateOpen(date(2025, 11, 28), "outage", T(7, 30))}})
    d = date(2025, 11, 28)
    evening = list(range(ct_ns(d - timedelta(days=1), T(17, 0)), ct_ns(d - timedelta(days=1),
                                                                      T(20, 49)), M))
    good = np.array(evening + list(range(ct_ns(d, T(7, 30)), ct_ns(d, T(16, 0)), M)))
    bad = np.array(evening + list(range(ct_ns(d, T(6, 0)), ct_ns(d, T(16, 0)), M)))
    end = utc_midnight_ns(date(2025, 12, 1))
    ok = validate_calendar_group(good, cal, d, d, {date(2025, 1, 1): T(14, 0)}, data_end_ns=end)
    assert ok.passed and (d, "late_open") in ok.entries_checked
    ev = [o for o in ok.observations if o.get("kind") == "late_open"][0]
    assert ev["last_bar_before_ct"] == "Thu 11-27 20:48"
    assert ev["first_bar_at_or_after_ct"] == "Fri 11-28 07:30"
    opened = open_intervals(cal, d, d)  # no closed window for the outage (ruling L-4)
    assert opened.starts[0] == ct_ns(d - timedelta(days=1), T(17, 0))
    no = validate_calendar_group(bad, cal, d, d, {date(2025, 1, 1): T(14, 0)}, data_end_ns=end)
    assert [x.kind for x in no.discrepancies] == [ENTRY_NOT_OBSERVED]


def test_a_sha256_mismatch_stops_the_product(synthetic: dict) -> None:
    spec = synthetic["spec"]
    spec = ProductSpec(**{**spec.__dict__, "files": (InputFile(synthetic["file"], "0" * 64,
                                                               None),)})
    res = build_product(spec, synthetic["cal"], [], synthetic["rolls"], None, "test",
                        load_bars=lambda _p: pytest.fail("loaded despite a hash mismatch"))
    assert res.summary["status"] == "refused"
    assert "sha256 mismatch" in res.summary["refusal_causes"][0]


# ------------------------------------------------------------ calendar checks ----
def _equity_bars(first: date, last: date, drop_day: date, early_day: date) -> np.ndarray:
    out = []
    day = first
    while day <= last:
        if day.weekday() < 5 and day != drop_day:
            end = T(12, 0) if day == early_day else T(16, 0)
            out.extend(range(ct_ns(day - timedelta(days=1 + 2 * (day.weekday() == 0)), T(17, 0)),
                             ct_ns(day, end), 15 * M))
            if day != early_day:
                out.append(ct_ns(day, T(14, 59)))
        day += timedelta(days=1)
    return np.array(sorted(set(out)), dtype=np.int64)


def test_group_calendar_check_agrees_with_step4b_on_the_equity_calendar() -> None:
    cal = load_group_calendar("equity")
    first, last = date(2025, 11, 3), date(2025, 12, 12)
    ts = _equity_bars(first, last, drop_day=date(2025, 12, 3), early_day=date(2025, 12, 10))
    old = validate_calendar_step4b(ts, first, last, entry_years=(2025, 2026))
    new = validate_calendar_group(ts, cal, first, last, cal.day_session_close("MNQ"),
                                  data_end_ns=utc_midnight_ns(date(2026, 1, 1)))
    # The equity module's LATE_OPENS (the 2025-11-28 outage, check-only) is unknown to the D.1f
    # step 4b; the synthetic bars trade through it, so the group check alone reports it.
    late = [d for d in new.discrepancies if "late open" in d.detail]
    assert [(d.kind, d.day) for d in late] == [(ENTRY_NOT_OBSERVED, date(2025, 11, 28))]
    assert [(d.kind, d.day) for d in new.discrepancies if d not in late] == \
        [(d.kind, d.day) for d in old.discrepancies]
    kinds = {d.kind for d in new.discrepancies}
    assert {UNLISTED_CLOSURE, EARLY_STOP_NOT_LISTED, ENTRY_NOT_OBSERVED} <= kinds
    assert date(2025, 12, 3) in {d.day for d in new.discrepancies if d.kind == UNLISTED_CLOSURE}


def test_group_calendar_check_on_grains_and_an_unobservable_reopen() -> None:
    hol = {date(2026, 6, 19): Holiday(date(2026, 6, 19), "Juneteenth", HolidayKind.FULL_CLOSURE,
                                      None, "cme", "n/a")}
    cal = _cal("grains", GRAINS, hol, close=T(13, 15))
    days = [date(2026, 6, 15), date(2026, 6, 16), date(2026, 6, 17), date(2026, 6, 18)]
    ts = []
    for d in days:
        ts += list(range(ct_ns(d - timedelta(days=1 + 2 * (d.weekday() == 0)), T(19, 0)),
                         ct_ns(d, T(7, 45)), 30 * M))
        ts += list(range(ct_ns(d, T(8, 30)), ct_ns(d, T(13, 20)), M))
    check = validate_calendar_group(np.array(ts), cal, date(2026, 6, 15), date(2026, 6, 19),
                                    {date(2025, 1, 1): T(13, 15)},
                                    data_end_ns=utc_midnight_ns(date(2026, 6, 21)))
    assert check.passed, check.discrepancies
    assert check.entries_checked == ((date(2026, 6, 19), "full_closure"),)
    assert check.notes and "not observable" in check.notes[0][1]


# ------------------------------------------------------------ MES (real files) ----
MES_RESEARCH = REPO_ROOT / "data" / "processed" / "MES" / \
    "ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet"
MES_RESEARCH_SHA256 = "aea959a518c32984832126f8314000796318efa219379a1ac4aea556a1736ae0"


@pytest.mark.skipif(not MES_RESEARCH.is_file(), reason="MES research parquet not on disk")
def test_mes_research_parquet_is_unchanged() -> None:
    assert sha256_file(MES_RESEARCH) == MES_RESEARCH_SHA256
    manifest = json.loads((REPO_ROOT / "docs" / "HOLDOUT_MANIFEST.json").read_text())
    assert manifest["research"]["sha256"] == MES_RESEARCH_SHA256


def test_mes_regression_reproduces_the_research_parquet_row_for_row(tmp_path: Path) -> None:
    from data.build_bars_run import mes_regression, mes_regression_spec

    spec = mes_regression_spec(tmp_path / "x.parquet")
    if not MES_RESEARCH.is_file() or not all(f.path.is_file() for f in spec.files):
        pytest.skip("MES research files not on disk")
    got = mes_regression(tmp_path)
    assert got["status"] == "built", got["refusal_causes"]
    assert got["same_columns_and_types"] and got["rows_equal"]
    assert got["mismatched_values_by_column"] == {}
    assert got["next_research_row_at_or_after_rebuild_end"]
    assert got["rows_rebuilt"] == 411_659 and got["last_rebuilt_trade_date"] == "2026-06-01"
    assert not got["file_bytes_equal"]  # the 2026-06 chunk is sealed: fewer rows by design
    assert sha256_file(MES_RESEARCH) == MES_RESEARCH_SHA256


# ------------------------------------------------------------ rulings L-6, metals keys ----
def test_scheduled_late_open_is_a_closed_window_and_the_outage_is_not() -> None:
    from dataclasses import dataclass

    from data.group_session import CalendarNotReady, is_scheduled_late_open

    @dataclass(frozen=True)
    class GrainLateOpen:  # the grains module's type: no stop-time field
        day: date
        name: str
        open_ct: time

    @dataclass(frozen=True)
    class OutageLateOpen:  # the rates / FX / energy / metals type
        day: date
        name: str
        open_ct: time
        halt_from_ct: time | None = None

    d = date(2025, 11, 28)
    sched = GrainLateOpen(d, "Day after Thanksgiving", T(8, 30))
    assert is_scheduled_late_open(sched)
    assert not is_scheduled_late_open(OutageLateOpen(d, "Globex outage (cooling)", T(7, 30)))
    with pytest.raises(CalendarNotReady):
        is_scheduled_late_open(OutageLateOpen(d, "Day after Thanksgiving", T(8, 30)))
    base = _cal("grains", GRAINS, {date(2025, 11, 27): Holiday(
        date(2025, 11, 27), "Thanksgiving", HolidayKind.FULL_CLOSURE, None, "cme", "n/a")})
    cal = GroupCalendar(**{**base.__dict__, "late_opens": {d: sched},
                           "scheduled_late_opens": {d: T(8, 30)}})
    opened = open_intervals(cal, d, d)
    assert list(zip(opened.starts.tolist(), opened.ends.tolist(), strict=True)) == [
        (ct_ns(d, T(8, 30)), ct_ns(d, T(13, 20)))]  # no overnight segment, so no 07:43 flatten
    got = assign_trade_dates(opened, np.array([ct_ns(d, T(6, 0)), ct_ns(d, T(8, 30))]))
    assert [x.isoformat() for x in got.as_dates()] == ["2025-11-28", "2025-11-28"]
    assert got.in_closure.tolist() == [True, False]
    ts = np.array(list(range(ct_ns(d, T(8, 30)), ct_ns(d, T(13, 20)), M)))
    check = validate_calendar_group(ts, cal, d, d, {date(2025, 1, 1): T(13, 15)},
                                    data_end_ns=utc_midnight_ns(date(2025, 12, 1)))
    assert check.passed and (d, "scheduled_late_open") in check.entries_checked
    early = np.concatenate([[ct_ns(d - timedelta(days=1), T(19, 0))], ts])
    bad = validate_calendar_group(early, cal, d, d, {date(2025, 1, 1): T(13, 15)},
                                  data_end_ns=utc_midnight_ns(date(2025, 12, 1)))
    assert [x.kind for x in bad.discrepancies] == [ENTRY_NOT_OBSERVED]


def test_metals_day_session_close_is_keyed_by_subgroup() -> None:
    from data.calendars import GROUP_OF_PRODUCT

    base = _cal("metals", GLOBEX)
    spec = SessionSpec(date(2025, 1, 1), None, GLOBEX,
                       {"gold": (T(7, 20), T(12, 30)), "copper": (T(7, 10), T(12, 0))}, "x")
    cal = GroupCalendar(**{**base.__dict__, "sessions": (spec,),
                           "subgroup_of_product": {"MGC": "gold", "MHG": "copper"}})
    assert cal.day_session_close("MGC") == {date(2025, 1, 1): T(12, 30)}
    assert cal.day_session_close("MHG") == {date(2025, 1, 1): T(12, 0)}
    assert GROUP_OF_PRODUCT["MGC"] == "metals"


# ------------------------------------------------------------ crypto (rulings L-9, L-10) ----
def test_crypto_booked_forward_and_24_7_trade_dates_from_the_module() -> None:
    cal = load_group_calendar("crypto")
    opened = open_intervals(cal, date(2025, 5, 20), date(2026, 6, 25))

    def td(day: date, at: time) -> str | None:
        got = assign_trade_dates(opened, np.array([ct_ns(day, at)])).as_dates()[0]
        return None if got is None else got.isoformat()

    # Memorial Day 2025 (booked forward): Sunday evening and Monday belong to Tuesday 05-27.
    assert not cal.is_trade_date(date(2025, 5, 26))
    assert td(date(2025, 5, 25), T(18, 0)) == "2025-05-27"
    assert td(date(2025, 5, 26), T(10, 0)) == "2025-05-27"
    assert td(date(2025, 5, 26), T(17, 30)) == "2025-05-27"
    assert td(date(2025, 5, 23), T(15, 0)) == "2025-05-23"
    # The first 24/7 weekend: Friday 05-29 16:30 (delayed start) to Monday 06-01 16:00, less
    # the Saturday 02:00-04:00 maintenance.
    first = [(s, e) for s, e, d in zip(opened.starts, opened.ends, opened.days, strict=True)
             if d == date(2026, 6, 1)]
    assert first == [(ct_ns(date(2026, 5, 29), T(16, 30)), ct_ns(date(2026, 5, 30), T(2, 0))),
                     (ct_ns(date(2026, 5, 30), T(4, 0)), ct_ns(date(2026, 6, 1), T(16, 0)))]
    assert td(date(2026, 6, 6), T(10, 0)) == "2026-06-08"  # Saturday -> Monday
    assert td(date(2026, 6, 3), T(16, 5)) == "2026-06-04"  # after the 16:00-16:02 pause
    # Juneteenth 2026 and its weekend are booked to 2026-06-22 (holdout-1): ruling L-9.
    assert td(date(2026, 6, 18), T(16, 5)) == "2026-06-22"
    assert td(date(2026, 6, 20), T(12, 0)) == "2026-06-22"
    assert td(date(2026, 6, 18), T(15, 0)) == "2026-06-18"


def test_crypto_flags_follow_each_calendar_day() -> None:
    cal = load_group_calendar("crypto")
    policy = STAGE_E_POLICIES["crypto"]
    ts = np.array([ct_ns(date(2025, 5, 26), T(10, 0)), ct_ns(date(2025, 5, 26), T(15, 10)),
                   ct_ns(date(2025, 5, 27), T(10, 0)), ct_ns(date(2026, 6, 6), T(10, 0)),
                   ct_ns(date(2026, 6, 7), T(17, 30)), ct_ns(date(2026, 6, 5), T(16, 30))])
    days = np.array(["2025-05-27", "2025-05-27", "2025-05-27", "2026-06-08", "2026-06-08",
                     "2026-06-08"], dtype="datetime64[D]")
    flat, nonew = flatten_masks(cal, policy, ts, days)
    # The booked-in holiday session flattens at its own 15:08; the weekend is closed for
    # TopstepX; Sunday from 17:00 is open again.
    assert flat.tolist() == [False, True, False, True, False, True]
    assert nonew.tolist() == flat.tolist()


def test_every_calendar_question_carries_a_lead_ruling() -> None:
    from data.build_bars_reports import QUESTION, classify_group, lead_ruling

    assert lead_ruling("fx", "2025-11-27").startswith("L-5")
    assert lead_ruling("metals", "2026-02-25").startswith("L-7: an unscheduled halt")
    assert lead_ruling("crypto", "2025-04-25").startswith("L-11")
    assert lead_ruling("energy", "2025-11-27") is None
    check = {"weekdays_checked": 1, "entries_checked": [], "notes": [], "observations": [],
             "discrepancies": [{"kind": "early_stop_not_a_listed_early_halt_at_that_time",
                                "day": "2025-07-01", "detail": "x"}]}
    got = classify_group("energy", {"CL": {"calendar_check": check}}, {"CL": 1})
    assert got["per_contract"]["CL"]["discrepancies"][0]["classification"] == QUESTION
    assert got["calendar_questions_without_ruling"] == [
        {"day": "2025-07-01", "kind": "early_stop_not_a_listed_early_halt_at_that_time"}]
