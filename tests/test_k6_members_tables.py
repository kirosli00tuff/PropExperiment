"""Stage E.8 K6 tables of MemberCoder-B: the pins of strategy/members/k6/_calendar.py, _wasde.py
and _limits.py (reports/stage_e8_member_specs.md S0.8, S0.11, K6-L-06, K6-L-07, K6-L-10, K6-L-11
and the section 10 rulings R-1b-1, R-1b-2, R-1b-5).

Every table is recomputed here from its sources by code independent of the generator
(reports/stage_e8_briefs/gen_k6_tables.py): EC-CAL through data.group_session, the engine's F
through rules.sessions for every root of the group, the frozen release calendar and Task 1b's
check through json, the limits and the settlement window through rules.price_limits. The
generator is loaded from its path only to assert that each module is exactly its output. The
JSON pins skip, with the reason, only if a source file is absent. No bar data is read.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo

import pytest

from data.group_session import load_group_calendar
from rules import price_limits as pl
from rules import sessions
from rules.products import product
from strategy.members.k6 import _calendar as cal_tables
from strategy.members.k6 import _limits as limit_tables
from strategy.members.k6 import _wasde as wasde_tables
from strategy.members.k6 import limitcont

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / "reports" / "stage_e8_briefs" / "gen_k6_tables.py"
CALENDAR_JSON = "reports/stage_e2b_release_calendar.json"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"  # spec header
CHECK_JSON = "reports/stage_e8_release_check.json"
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
CT = ZoneInfo("America/Chicago")
ROOTS = {"grains": ("ZC", "ZW", "ZS", "ZM", "ZL"), "livestock": ("HE", "LE")}
REGULAR_F = {"grains": time(13, 18), "livestock": time(13, 3)}
# Spec header (EC-CAL, checked 00:15 PDT; R-1b-5 kept every date): research-window full
# closures of both groups and the early halts.
RESEARCH_CLOSURES = (
    "2025-04-18", "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27",
    "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19")
RESEARCH_HALTS = {"grains": {date(2025, 11, 28): time(12, 5), date(2025, 12, 24): time(12, 5)},
                  "livestock": {date(2025, 11, 28): time(12, 5),
                                date(2025, 12, 24): time(12, 15)}}
GRAIN_LATE_OPENS = (date(2025, 11, 28), date(2025, 12, 26), date(2026, 1, 2))
# Spec header and R-1b-1: the 14 research-window WASDE rows.
RESEARCH_WASDE = (
    "2025-04-10", "2025-05-12", "2025-06-12", "2025-07-11", "2025-08-12", "2025-09-12",
    "2025-11-14", "2025-12-09", "2026-01-12", "2026-02-10", "2026-03-10", "2026-04-09",
    "2026-05-12", "2026-06-11")
SPEC_TICKS = {("HE", "0.0400"): 160, ("HE", "0.0475"): 190, ("LE", "0.0650"): 260,
              ("LE", "0.0725"): 290}  # S0.11
needs_calendar_json = pytest.mark.skipif(not (REPO / CALENDAR_JSON).is_file(),
                                         reason=f"{CALENDAR_JSON} (the frozen calendar) is absent")
needs_check_json = pytest.mark.skipif(not (REPO / CHECK_JSON).is_file(),
                                      reason=f"{CHECK_JSON} (Task 1b's check) is absent")


def _sha(rel: str) -> str:
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()


def _days(first: date, last: date) -> list[date]:
    return [first + timedelta(days=n) for n in range((last - first).days + 1)]


@cache
def _json(rel: str) -> dict:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


@cache
def _generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k6_tables", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def _in_research(d: date) -> bool:
    return RESEARCH[0] <= d <= RESEARCH[1]


# ------------------------------------------------------------- sources and output ----
def test_calendar_sources_carry_the_pinned_sha256() -> None:
    pinned = dict(cal_tables.SOURCE_SHA256)
    assert set(pinned) == {"data/calendars/__init__.py", "data/calendars/grains.py",
                           "data/calendars/livestock.py", "rules/sessions.py"}
    for rel, sha in pinned.items():
        assert _sha(rel) == sha, rel
    for group in ROOTS:
        assert set(load_group_calendar(group).module_sha256()) < set(pinned)
    assert cal_tables.TABLE_RANGE == ("2019-05-01", "2026-06-19")
    assert ROOTS["grains"] == cal_tables.GRAIN_F_ROOTS
    assert ROOTS["livestock"] == cal_tables.LIVESTOCK_F_ROOTS
    assert (cal_tables.GRAIN_REGULAR_F_CT, cal_tables.LIVESTOCK_REGULAR_F_CT) == ("13:18", "13:03")


@needs_calendar_json
@needs_check_json
def test_wasde_and_limit_sources_carry_the_pinned_sha256() -> None:
    assert _sha(CALENDAR_JSON) == CALENDAR_SHA256
    check = (CHECK_JSON, _sha(CHECK_JSON))
    wasde_sources = wasde_tables.SOURCE_SHA256
    limit_sources = limit_tables.SOURCE_SHA256
    assert wasde_sources == ((CALENDAR_JSON, CALENDAR_SHA256), check)
    assert limit_sources == (("rules/price_limits.py", _sha("rules/price_limits.py")), check)


@needs_calendar_json
@needs_check_json
def test_the_modules_are_exactly_the_generators_output() -> None:
    texts = _generator().build()
    assert set(texts) == {"strategy/members/k6/_calendar.py", "strategy/members/k6/_wasde.py",
                          "strategy/members/k6/_limits.py"}
    for rel, text in texts.items():
        assert (REPO / rel).read_text(encoding="utf-8") == text, rel


# ------------------------------------------------------------------ the calendars ----
@pytest.mark.parametrize(("group", "table"), [("grains", "GRAIN_TRADE_DATES"),
                                              ("livestock", "LIVESTOCK_TRADE_DATES")])
def test_trade_dates_are_every_ec_cal_trade_date_of_the_range(group: str, table: str) -> None:
    cal = load_group_calendar(group)
    trade = tuple(d for d in _days(FIRST, LAST) if cal.is_trade_date(d))
    got = getattr(cal_tables, table)
    assert isinstance(got, tuple) and all(type(d) is date for d in got)
    assert got == trade and len(trade) == 1795
    assert list(got) == sorted(got) and trade[0] == FIRST and trade[-1] == date(2026, 6, 18)
    closed = tuple(d.isoformat() for d in _days(*RESEARCH) if d.weekday() < 5
                   and not cal.is_trade_date(d))
    assert closed == RESEARCH_CLOSURES
    assert date(2025, 11, 28) in got and date(2025, 12, 24) in got  # early halts are trade dates


@pytest.mark.parametrize(("group", "table", "not_full"), [
    ("grains", "GRAIN_FULL_SESSIONS", "GRAIN_NOT_FULL"),
    ("livestock", "LIVESTOCK_FULL_SESSIONS", "LIVESTOCK_NOT_FULL")])
def test_full_sessions_have_no_early_halt_and_the_regular_f_on_every_root(
        group: str, table: str, not_full: str) -> None:
    """S0.8 / K6-L-10: no early_halt_ct AND the regular F on CT date d; F is the same for every
    root of the group on every trade date; the two tests disagree only on 2024-07-03 (F 11:30,
    no CME halt), which the module's comment names."""
    cal = load_group_calendar(group)
    full, disagree, removed = set(), [], []
    for d in _days(FIRST, LAST):
        if not cal.is_trade_date(d):
            continue
        flats = {sessions.flatten_time_ct(r, d) for r in ROOTS[group]}
        assert len(flats) == 1, (group, d, flats)
        (f,) = flats
        no_halt, regular = cal.early_halt_ct(d) is None, f == REGULAR_F[group]
        if no_halt and regular:
            full.add(d)
        else:
            removed.append(d)
        if no_halt != regular:
            disagree.append(d)
    got = getattr(cal_tables, table)
    assert isinstance(got, frozenset) and got == frozenset(full) and len(full) == 1780
    assert tuple(date.fromisoformat(s) for s, _ in getattr(cal_tables, not_full)) == tuple(removed)
    assert disagree == [date(2024, 7, 3)]
    text = (REPO / "strategy/members/k6/_calendar.py").read_text(encoding="utf-8")
    assert "2024-07-03 (early halt none, F" in text
    assert [d for d in removed if _in_research(d)] == sorted(RESEARCH_HALTS[group])
    for d, halt in RESEARCH_HALTS[group].items():
        assert cal.early_halt_ct(d) == halt and d not in got


def test_a_grain_late_open_is_not_an_early_close() -> None:
    cal = load_group_calendar("grains")
    assert tuple(sorted(d for d in cal.scheduled_late_opens if _in_research(d))) == GRAIN_LATE_OPENS
    assert date(2025, 12, 26) in cal_tables.GRAIN_FULL_SESSIONS
    assert date(2026, 1, 2) in cal_tables.GRAIN_FULL_SESSIONS
    assert date(2025, 11, 28) not in cal_tables.GRAIN_FULL_SESSIONS  # also an early halt
    assert not [d for d in load_group_calendar("livestock").scheduled_late_opens
                if _in_research(d)]


def test_livestock_early_halts_are_every_ec_cal_halt_of_the_range() -> None:
    cal = load_group_calendar("livestock")
    halts = {d: cal.early_halt_ct(d) for d in _days(FIRST, LAST)
             if cal.is_trade_date(d) and cal.early_halt_ct(d) is not None}
    assert halts == cal_tables.LIVESTOCK_EARLY_HALT_CT and len(halts) == 14
    assert {d: t for d, t in halts.items() if _in_research(d)} == RESEARCH_HALTS["livestock"]


def test_previous_trade_date_is_the_latest_table_entry_before_d() -> None:
    prev = cal_tables.previous_trade_date
    for table in (cal_tables.GRAIN_TRADE_DATES, cal_tables.LIVESTOCK_TRADE_DATES):
        assert prev(table, table[0]) is None
        assert prev(table, date(2019, 4, 30)) is None
        assert {b: prev(table, b) for b in table[1:]} == dict(zip(table[1:], table, strict=False))
        assert prev(table, date(2030, 1, 1)) == table[-1]
    lv = cal_tables.LIVESTOCK_TRADE_DATES
    assert prev(lv, date(2025, 9, 2)) == date(2025, 8, 29)  # Labor Day 2025-09-01
    assert prev(lv, date(2025, 5, 31)) == date(2025, 5, 30)  # a Saturday
    assert prev(lv, date(2025, 11, 28)) == date(2025, 11, 26)  # Thanksgiving 11-27


@pytest.mark.parametrize("root", ROOTS["livestock"])
def test_member_settlement_window_is_the_engines_on_every_livestock_trade_date(root: str) -> None:
    """K6-L-06: limitcont's window from LIVESTOCK_EARLY_HALT_CT and SETTLEMENT_WINDOW_LIVESTOCK is
    rules.price_limits.settlement_window_ct(root, x) on every livestock trade date."""
    moved = 0
    for x in cal_tables.LIVESTOCK_TRADE_DATES:
        w = pl.settlement_window_ct(root, x)
        assert limitcont.settlement_window(x) == (w.start_ct, w.end_ct), x
        moved += (w.start_ct, w.end_ct) != (time(12, 59, 30), time(13, 0))
    assert moved == 14
    assert limitcont.settlement_window(date(2025, 12, 24)) == (time(12, 14, 30), time(12, 15))
    assert limitcont.settlement_window(date(2025, 11, 28)) == (time(12, 4, 30), time(12, 5))


# ----------------------------------------------------------------------- WASDE ----
def _ct_date(instant_utc: str) -> date:
    return datetime.fromisoformat(instant_utc.replace("Z", "+00:00")).astimezone(CT).date()


@needs_calendar_json
def test_wasde_dates_are_every_1200_et_wasde_row_of_the_frozen_calendar() -> None:
    rows = [r for r in _json(CALENDAR_JSON)["releases"] if r["release"] == "WASDE"]
    at_noon = [r for r in rows if r["time_local"] == "12:00" and r["tz"] == "America/New_York"]
    assert len(at_noon) == len(rows) == 85  # no row at another time
    days = {_ct_date(r["instant_utc"]) for r in at_noon}
    days = {d for d in days if FIRST <= d <= LAST}
    assert all(_ct_date(r["instant_utc"]).isoformat() == r["date"] for r in rows)
    assert isinstance(wasde_tables.WASDE_DATES, frozenset)
    assert frozenset(days) == wasde_tables.WASDE_DATES and len(days) == 85
    research = sorted(d.isoformat() for d in days if _in_research(d))
    assert tuple(research) == RESEARCH_WASDE
    assert wasde_tables.WASDE_RANGE == ("2019-05-01", "2026-06-19")
    assert wasde_tables.WASDE_RELEASE_TIME == ("12:00", "America/New_York")


@needs_calendar_json
@needs_check_json
def test_no_wasde_is_dropped_by_r_1b_1_and_the_2025_exceptions() -> None:
    verdicts = {r["date"]: r["verdict"] for r in _json(CHECK_JSON)["A"]["rows"]}
    assert tuple(sorted(verdicts)) == RESEARCH_WASDE and set(verdicts.values()) == {"keep"}
    assert wasde_tables.DROPPED_WASDE == {}
    w = wasde_tables.WASDE_DATES
    assert date(2025, 10, 9) not in w  # the cancelled October 2025 WASDE
    assert date(2025, 11, 14) in w and date(2025, 11, 10) not in w  # moved by the NASS notice
    assert all(wasde_tables.is_wasde_date(d) for d in w)
    assert not wasde_tables.is_wasde_date(date(2025, 6, 13))


def test_is_wasde_date_reads_dropped_wasde_at_call_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wasde_tables, "DROPPED_WASDE", {date(2025, 6, 12): "synthetic"})
    assert not wasde_tables.is_wasde_date(date(2025, 6, 12))
    assert wasde_tables.is_wasde_date(date(2025, 7, 11))


# ---------------------------------------------------------------------- limits ----
def _ticks(root: str, amount: Decimal) -> Decimal:
    p = product(root)
    return amount * p.vendor_price_factor / p.vendor_tick


@pytest.mark.parametrize("root", ROOTS["livestock"])
def test_limit_periods_are_the_hard_daily_periods_of_limits(root: str) -> None:
    expected = tuple((p.start, p.end, str(p.amount)) for p in pl.LIMITS[root]
                     if p.kind is pl.LimitKind.HARD_DAILY and p.end >= FIRST and p.start <= LAST)
    assert len(expected) == len(pl.LIMITS[root])  # every period is HARD_DAILY and in range
    assert limit_tables.LIMIT_PERIODS[root] == expected
    assert set(limit_tables.LIMIT_PERIODS) == {"HE", "LE"}
    text = (REPO / "strategy/members/k6/_limits.py").read_text(encoding="utf-8")
    for p in pl.LIMITS[root]:
        line = f'(date({p.start.year}, {p.start.month}, {p.start.day}), date({p.end.year}, ' \
               f'{p.end.month}, {p.end.day}), "{p.amount}"),  # {p.status}'
        assert line in text, line
    for first, last, amount in expected:
        ticks = _ticks(root, Decimal(amount))
        assert ticks == ticks.to_integral_value(), (root, amount)
        assert SPEC_TICKS.get((root, amount), int(ticks)) == int(ticks)
        assert limitcont.limit_ticks(root, first) == limitcont.limit_ticks(root, last) == ticks


@pytest.mark.parametrize("root", ROOTS["livestock"])
def test_limit_ticks_equal_limit_period_on_every_livestock_trade_date(root: str) -> None:
    for x in cal_tables.LIVESTOCK_TRADE_DATES:
        assert limitcont.limit_ticks(root, x) == _ticks(root, pl.limit_period(root, x).amount), x
    assert limitcont.limit_ticks(root, date(2019, 4, 30)) is None
    assert limitcont.limit_ticks(root, date(2026, 6, 20)) is None


def test_the_research_window_limit_ticks_and_boundaries() -> None:
    lt = limitcont.limit_ticks
    assert (lt("HE", date(2025, 8, 29)), lt("HE", date(2025, 9, 2))) == (160, 190)
    assert (lt("LE", date(2025, 5, 30)), lt("LE", date(2025, 6, 2))) == (260, 290)
    assert lt("LE", date(2026, 6, 18)) == 290  # the frozen table (dropped for the member)


def test_the_settlement_window_is_the_engines_livestock_window() -> None:
    w = pl.SETTLEMENT_WINDOW_CT["livestock"]
    assert (w.start_ct, w.end_ct) == limit_tables.SETTLEMENT_WINDOW_LIVESTOCK
    assert (time(12, 59, 30), time(13, 0)) == limit_tables.SETTLEMENT_WINDOW_LIVESTOCK


@needs_check_json
def test_dropped_limit_dates_are_the_14_le_trade_dates_of_r_1b_2() -> None:
    cal = load_group_calendar("livestock")
    june = [d for d in _days(date(2026, 6, 1), date(2026, 6, 18)) if cal.is_trade_date(d)]
    dropped = limit_tables.DROPPED_LIMIT_DATES
    assert set(dropped) == {"HE", "LE"} and dropped["HE"] == {}
    assert sorted(dropped["LE"]) == june and len(june) == 14
    b1 = _json(CHECK_JSON)["B"]["B1_summary"]
    assert b1["differing_roots"] == ["LE"]
    assert b1["differing_dates"] == [d.isoformat() for d in june]
    b2 = _json(CHECK_JSON)["B"]["B2"]
    verdicts = {(r["root"], r["start"], r["end"]): r["verdict"] for r in b2}
    assert verdicts[("LE", "2026-05-19", "2026-06-19")] == "drop"
    assert {v for k, v in verdicts.items() if k[0] == "HE"} == {"keep"}
    for d, reason in dropped["LE"].items():
        assert reason.startswith("R-1b-2: CME SER-9736") and "$0.0850" in reason, d
        assert "$0.0725" in reason and pl.limit_period("LE", d).amount == Decimal("0.0725")


def test_the_cluster_init_is_empty() -> None:
    assert (REPO / "strategy" / "members" / "k6" / "__init__.py").read_bytes() == b""
