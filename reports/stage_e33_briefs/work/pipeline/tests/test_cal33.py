"""cal33: one test (or more) per function. Calendar, symbology and definition metadata only."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import cal33 as c  # noqa: E402
import data33 as d33  # noqa: E402
import guard33 as g  # noqa: E402

NS = g.NS


def _utc(y: int, mo: int, dd: int, h: int, mi: int = 0) -> int:
    return int(datetime(y, mo, dd, h, mi, tzinfo=UTC).timestamp()) * NS


# ------------------------------------------------------------------ dates ----
def test_trade_dates_burn_in_oof() -> None:
    days, burn, oof = c.trade_dates(), c.burn_in(), c.oof_dates()
    assert (len(days), len(burn), len(oof)) == (816, 20, 796)
    assert days[0] == date(2020, 12, 1) and days[-1] == date(2024, 2, 29)
    assert burn + oof == days and oof[0] == date(2020, 12, 30)
    assert all(a < b for a, b in zip(days, days[1:], strict=False))
    assert date(2021, 12, 24) not in days and date(2022, 6, 20) not in days  # full closures
    assert c.is_trade_date("2021-06-28") and not c.is_trade_date("2021-06-27")


def test_previous_trade_dates() -> None:
    assert c.previous_trade_dates("2020-12-01", 20) == []
    prev = c.previous_trade_dates("2021-01-04", 3)
    assert prev == [date(2020, 12, 29), date(2020, 12, 30), date(2020, 12, 31)]
    assert len(c.previous_trade_dates(c.oof_dates()[0], 20)) == 20
    with pytest.raises(ValueError):
        c.previous_trade_dates("2021-01-02", 1)


def test_day_bounds_and_ct_ns_are_dst_aware() -> None:
    assert c.day_bounds("2022-03-14") == (_utc(2022, 3, 13, 21), _utc(2022, 3, 14, 21))
    assert c.day_bounds("2022-03-14") == d33.window(date(2022, 3, 14))
    assert c.ct_ns("2022-03-14", "08:30:00") == _utc(2022, 3, 14, 13, 30)
    assert c.ct_ns("2022-01-14", "08:30:00") == _utc(2022, 1, 14, 14, 30)
    assert c.ct_ns(date(2022, 1, 14), "08:30") == c.ct_ns("2022-01-14", "08:30:00")
    assert c.ct_ns("2023-11-06", "13:13:00") == _utc(2023, 11, 6, 19, 13)


# ------------------------------------------------------------------ fronts, segments ----
def test_fronts_follow_the_v0_symbology() -> None:
    assert c.fronts("2020-12-01") == {"ZM": 504886, "ZS": 295951, "ZL": 544759}
    assert c.fronts("2024-02-29") == {"ZM": 759433, "ZS": 535842, "ZL": 567056}
    assert c.fronts("2021-06-28")["ZM"] == 535389  # ZMU1 for one day inside a ZMZ1 run
    assert c.fronts("2021-06-29")["ZM"] == 794459
    with pytest.raises(ValueError):
        c.fronts("2021-06-27")


def test_segments_break_at_any_front_change() -> None:
    days = c.trade_dates()
    ids = [c.segment_id(d) for d in days]
    assert ids[0] == 0 and all(b - a in (0, 1) for a, b in zip(ids, ids[1:], strict=False))
    for a, b in zip(days, days[1:], strict=False):
        changed = c.fronts(a) != c.fronts(b)
        assert (c.segment_id(b) == c.segment_id(a) + 1) == changed
    assert c.segment_id("2020-12-18") == c.segment_id("2020-12-17") + 1  # ZM roll
    assert c.segment_id("2020-12-22") == c.segment_id("2020-12-21") + 1  # ZL roll


# ------------------------------------------------------------------ exclusions ----
def test_excluded_by_the_rule() -> None:
    assert c.excluded("2021-06-28") == (True, ("roll_day",))
    assert c.excluded("2021-06-29") == (True, ("after_roll_day", "roll_day"))
    assert c.excluded("2021-06-30") == (True, ("after_roll_day",))
    assert c.excluded("2020-12-24") == (True, ("cme_holiday_or_early_close",))
    assert c.excluded("2021-07-06") == (True, ("scheduled_late_open",))
    assert c.excluded("2021-03-03") == (False, ())
    counts = c.exclusion_counts()
    assert counts == {"after_roll_day": 23, "cme_holiday_or_early_close": 4,
                      "excluded_dates": 52, "roll_day": 23, "scheduled_late_open": 5}


def test_roll_day_means_front_differs_from_previous_trade_date() -> None:
    days = c.trade_dates()
    for prev, day in zip(days, days[1:], strict=False):
        rolled = c.fronts(prev)["ZM"] != c.fronts(day)["ZM"]
        assert ("roll_day" in c.excluded(day)[1]) == rolled
        if rolled and day != days[-1]:
            nxt = days[days.index(day) + 1]
            assert "after_roll_day" in c.excluded(nxt)[1]


# ------------------------------------------------------------------ releases ----
_HEADER = "date,time_et,report,source_url,evidence\n"


def test_release_parse_rule_on_synthetic_lines() -> None:
    lines = ["# comment line\n", _HEADER,
             "2021-01-12,12:00,USDA WASDE,u,CONFIRMED\n",
             "2021-01-12,12:00,NASS Crop Production Annual,u,UNCERTAIN\n",
             "2021-01-13,15:00,NASS Fats & Oils,u,x\n",
             "2021-01-14,07:30,FAS Weekly Export Sales,u,x\n",
             "2021-01-15-NORELEASE,12:00,USDA WASDE,u,x\n",
             "2022-11-MISSING,12:00,NOPA Monthly Crush (not USDA),u,x\n",
             "2021-01-15,11:00,NOPA Monthly Crush (not USDA),u,x\n",
             "2021-01-15,12:00,NOPA Monthly Crush,u,x\n",
             "2021-02-16,12:00,NOPA Monthly Crush (not USDA),u,RULE-DERIVED\n"]
    rows = c.parse_release_lines(lines)
    assert [(d.isoformat(), r) for d, r, _ in rows] == [
        ("2021-01-12", "USDA WASDE"), ("2021-01-12", "NASS Crop Production Annual"),
        ("2021-02-16", "NOPA Monthly Crush (not USDA)")]
    assert rows[0][2] == _utc(2021, 1, 12, 17)  # 11:00 CST
    with pytest.raises(RuntimeError, match="columns"):
        c.parse_release_lines(["a,b\n", "1,2\n"])


def test_release_table_counts_and_nopa_rule_dates() -> None:
    table = c.release_table()
    counts: dict[str, int] = {}
    for _, r, _ in table:
        counts[r] = counts.get(r, 0) + 1
    assert counts == {**c.RELEASE_EXPECTED, "NOPA rule date": 2}
    rule = [d for d, r, _ in table if r == "NOPA rule date"]
    assert rule == [date(2022, 11, 15), date(2022, 12, 15)]
    for day, _, r in table:
        assert r == c.ct_ns(day, "11:00:00") and r in c.releases(day)


def test_releases_sorted_unique_and_empty_on_quiet_dates() -> None:
    for day in c.trade_dates():
        rel = c.releases(day)
        assert rel == sorted(set(rel))
    assert c.releases("2021-03-03") == []


# ------------------------------------------------------------------ definitions ----
def test_limits_none_rule_on_synthetic_records() -> None:
    rec = np.zeros(1, dtype=[("high_limit_price", "<i8"), ("low_limit_price", "<i8")])[0]
    rec["high_limit_price"], rec["low_limit_price"] = 420 * NS, 380 * NS
    assert c.limits_of(rec) == (420 * NS, 380 * NS)
    for hl, ll in ((c.UNDEF_PRICE, 380 * NS), (420 * NS, c.UNDEF_PRICE), (0, 380 * NS),
                   (420 * NS, 0)):
        rec["high_limit_price"], rec["low_limit_price"] = hl, ll
        assert c.limits_of(rec) is None
    assert c.limits_of(None) is None


def test_limits_are_the_front_as_of_0830() -> None:
    defs = d33.definitions(outright_only=True)
    for day in c.trade_dates()[::37]:
        rec = c.front_definition(day)
        cut = c.ct_ns(day, "08:30:00")
        mine = defs[(defs["instrument_id"] == c.fronts(day)["ZM"]) & (defs["ts_recv"] <= cut)]
        assert rec is not None and rec.tobytes() == mine[-1].tobytes()
        lim = c.limits(day)
        assert lim is not None and lim[0] > lim[1] > 0
    assert c.limits_none_dates() == []


def test_expiry_trade_dates_counts_trade_dates_after_d_through_expiry() -> None:
    cal = c._calendar()
    closures = [k for k in cal.holidays if cal.is_full_closure(k)]
    for day in c.trade_dates()[::41]:
        rec = c.front_definition(day)
        exp = datetime.fromtimestamp(int(rec["expiration"]) / NS, c.CT).date()
        want = int(np.busday_count(day + timedelta(days=1), exp + timedelta(days=1),
                                   holidays=closures))
        assert c.expiry_trade_dates(day) == want
    # ZMF1 (front on 2020-12-17) expires 2021-01-14: Dec 18-31 has 9 trade dates (25 closed),
    # Jan 4-14 has 9 (Jan 1 closed)
    assert c.expiry_trade_dates("2020-12-17") == 18


# ------------------------------------------------------------------ flags, tick ----
@pytest.mark.parametrize(("day", "want"), [
    ("2021-04-05", True), ("2021-04-06", False), ("2022-06-21", True), ("2021-11-26", True),
    ("2022-12-27", True), ("2021-01-19", True), ("2021-03-03", False), ("2021-12-27", True)])
def test_monday_or_after_closure(day: str, want: bool) -> None:
    assert c.monday_or_after_closure(day) is want


@pytest.mark.parametrize(("day", "want"), [
    ("2021-06-01", True), ("2021-08-31", True), ("2021-09-01", False), ("2022-05-31", False)])
def test_jja(day: str, want: bool) -> None:
    assert c.jja(day) is want


def test_tick_per_root() -> None:
    assert c.tick("ZM") == 100_000_000  # 0.10 USD/short ton
    assert c.tick("ZS") == 250_000_000  # 0.25 c/bu
    assert c.tick("ZL") == 10_000_000  # 0.01 c/lb
    with pytest.raises(ValueError):
        c.tick("ZC")
