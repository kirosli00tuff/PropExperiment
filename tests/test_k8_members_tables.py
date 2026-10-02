"""Stage E.9 K8 tables of MemberCoder-A: the pins of strategy/members/k8/_calendar.py and
_releases.py (reports/stage_e9_member_specs.md S0.8, S0.10, S0.11, K8-L-03, K8-L-04, K8-L-08,
K8-L-14 and the section 7 rulings R-1b-1, R-1b-3).

Every table is recomputed here from its sources by code independent of the generator
(reports/stage_e9_briefs/gen_k8_tables.py): EC-CAL through data.group_session, the engine's F
through rules.sessions for every K8 root of the group, the frozen release calendar through json.
The generator is loaded from its path only to assert that each module is exactly its output. The
earlier clusters' frozen group tables are read (read-only) to report where they differ. No bar
data is read.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo

import pytest

from data.group_session import load_group_calendar
from rules import sessions
from screening.stage_e_freeze import check_member_source
from strategy.members.k1 import _calendar as k1_calendar
from strategy.members.k3 import _calendar as k3_calendar
from strategy.members.k4 import _calendar as k4_calendar
from strategy.members.k5 import _calendar as k5_calendar
from strategy.members.k7 import _calendar as k7_calendar
from strategy.members.k8 import _calendar as cal
from strategy.members.k8 import _releases as rel

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / "reports" / "stage_e9_briefs" / "gen_k8_tables.py"
CALENDAR_JSON = "reports/stage_e2b_release_calendar.json"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"  # spec header
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
F_REGULAR = time(15, 8)
ROOTS = {"equity": ("MES", "MNQ"), "crypto": ("MBT",), "metals": ("MGC",), "energy": ("MCL",),
         "fx": ("6C",)}
TABLE = {"equity": "EQUITY", "crypto": "CRYPTO", "metals": "METALS", "energy": "ENERGY",
         "fx": "FX"}
# Spec section 7 (lead's count 22:32 PDT): research-window counts under the S0.8 definition
RESEARCH_FULL = {"equity": 303, "crypto": 304, "metals": 304, "energy": 304, "fx": 304}
RESEARCH_MEMBER = {"FLIGHT_DATES": 303, "OILCAD_DATES": 304, "WKNDBTC_DATES": 303}
RESEARCH_WKNDBTC_MONDAYS = 54
# Spec header (Task 1b A1): research-window rows per traded root, (release, ET clock) -> count
RESEARCH_ROWS = {
    "MGC": {("NFP", "08:30"): 14, ("CPI", "08:30"): 14, ("G17", "09:15"): 14,
            ("FOMC", "14:00"): 10},
    "6C": {("WPSR", "10:30"): 56, ("WPSR", "12:00"): 7, ("WPSR", "17:00"): 1, ("NFP", "08:30"): 14,
           ("FOMC", "14:00"): 10},
    "MNQ": {("ISM_SERVICES", "10:00"): 15, ("NFP", "08:30"): 14, ("CPI", "08:30"): 14,
            ("FOMC", "14:00"): 10},
}
# Earlier clusters' frozen group tables and the dates where they hold a date the K8 table (S0.8:
# no early halt AND F 15:08 for the K8 roots) does not. Reported to the lead, not "fixed":
# K4 and K5 tested the early halt only (no F test), so they keep 2024-07-03 (F 11:30, no halt);
# K3 was generated under rules/sessions.py d9a7fcfe... (before E.5's pre-2024 holidays), under
# which 6C's F on these 14 US holidays was still 15:08; the current engine F is 11:30.
K3_ONLY_FX = tuple(date.fromisoformat(s) for s in (
    "2022-01-17", "2022-02-21", "2022-05-30", "2022-06-20", "2022-07-04", "2022-09-05",
    "2022-11-24", "2023-01-16", "2023-02-20", "2023-05-29", "2023-06-19", "2023-07-04",
    "2023-09-04", "2023-11-23"))
EARLIER = {
    "equity": (k1_calendar, "EQUITY_FULL_SESSIONS", ()),
    "fx": (k3_calendar, "FX_FULL_SESSIONS", K3_ONLY_FX),
    "energy": (k4_calendar, "ENERGY_FULL_SESSIONS", (date(2024, 7, 3),)),
    "metals": (k5_calendar, "METALS_FULL_SESSIONS", (date(2024, 7, 3),)),
    "crypto": (k7_calendar, "CRYPTO_FULL_SESSIONS", ()),
}
needs_calendar_json = pytest.mark.skipif(not (REPO / CALENDAR_JSON).is_file(),
                                         reason=f"{CALENDAR_JSON} (the frozen calendar) is absent")


def _sha(path: str) -> str:
    return hashlib.sha256((REPO / path).read_bytes()).hexdigest()


def _days(first: date, last: date) -> list[date]:
    return [first + timedelta(days=n) for n in range((last - first).days + 1)]


def _in_research(d: date) -> bool:
    return RESEARCH[0] <= d <= RESEARCH[1]


@cache
def _json(path: str) -> dict:
    return json.loads((REPO / path).read_text(encoding="utf-8"))


@cache
def _generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k8_tables", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


@cache
def _full_sessions(group: str) -> frozenset[date]:
    """S0.8 recomputed: EC-CAL trade dates with no early halt and F 15:08 on every K8 root."""
    calendar = load_group_calendar(group)
    full = set()
    for d in _days(FIRST, LAST):
        if not calendar.is_trade_date(d):
            continue
        flats = {sessions.flatten_time_ct(r, d) for r in ROOTS[group]}
        assert len(flats) == 1, (group, d, flats)  # the roots of a group agree on every date
        if calendar.early_halt_ct(d) is None and flats == {F_REGULAR}:
            full.add(d)
    return frozenset(full)


def _ct_ns(d: date, hh: int, mm: int) -> int:
    return int(datetime.combine(d, time(hh, mm), tzinfo=CT).timestamp()) * NS


# ------------------------------------------------------------- sources and output ----
def test_calendar_sources_carry_the_pinned_sha256() -> None:
    pinned = dict(cal.SOURCE_SHA256)
    for path, sha in pinned.items():
        assert _sha(path) == sha, path
    expected = {"rules/sessions.py"}
    for group in ROOTS:
        expected |= set(load_group_calendar(group).module_sha256())
    assert set(pinned) == expected
    assert "data/cme_calendar.py" in pinned  # the equity calendar's holidays
    assert cal.TABLE_RANGE == ("2019-05-01", "2026-06-19")
    assert cal.REGULAR_F_CT == "15:08"
    groups = cal.GROUP_ROOTS
    assert groups == tuple(ROOTS.items())


@needs_calendar_json
def test_releases_source_is_the_frozen_calendar() -> None:
    assert _sha(CALENDAR_JSON) == CALENDAR_SHA256
    assert (rel.RELEASE_CALENDAR, rel.RELEASE_CALENDAR_SHA256) == (CALENDAR_JSON, CALENDAR_SHA256)
    assert rel.TABLE_RANGE == ("2019-05-01", "2026-06-19")
    assert rel.GUARD_ROOTS == ("MGC", "6C", "MNQ") and rel.GUARD_SECONDS == 120


@needs_calendar_json
def test_the_modules_are_exactly_the_generators_output() -> None:
    texts = _generator().build()
    assert set(texts) == {"strategy/members/k8/_calendar.py", "strategy/members/k8/_releases.py"}
    for path, text in texts.items():
        assert (REPO / path).read_text(encoding="utf-8") == text, path


@pytest.mark.parametrize("name", ["_calendar.py", "_releases.py"])
def test_the_tables_pass_the_freeze_static_check(name: str) -> None:
    path = f"strategy/members/k8/{name}"
    assert check_member_source(path, (REPO / path).read_text(encoding="utf-8"), "K8") == []


# ------------------------------------------------------------------ the calendars ----
@pytest.mark.parametrize("group", list(ROOTS))
def test_full_sessions_are_every_ec_cal_trade_date_with_no_halt_and_f_1508(group: str) -> None:
    got = getattr(cal, f"{TABLE[group]}_FULL_SESSIONS")
    assert isinstance(got, frozenset) and all(type(d) is date for d in got)
    assert got == _full_sessions(group)
    assert sum(1 for d in got if _in_research(d)) == RESEARCH_FULL[group]
    assert min(got) >= FIRST and max(got) <= LAST


@pytest.mark.parametrize("group", list(ROOTS))
def test_not_full_lists_every_other_weekday_with_a_reason(group: str) -> None:
    rows = getattr(cal, f"{TABLE[group]}_NOT_FULL")
    listed = [date.fromisoformat(s) for s, _ in rows]
    weekdays = [d for d in _days(FIRST, LAST) if d.weekday() < 5]
    assert listed == [d for d in weekdays if d not in _full_sessions(group)]
    calendar = load_group_calendar(group)
    for s, reason in rows:
        d = date.fromisoformat(s)
        if calendar.is_trade_date(d):
            assert reason.startswith("early halt "), (s, reason)
        else:
            assert reason.startswith("not a trade date: "), (s, reason)


def test_an_early_halt_and_a_closure_are_not_full_sessions() -> None:
    for group in ROOTS:
        full = getattr(cal, f"{TABLE[group]}_FULL_SESSIONS")
        assert date(2025, 11, 28) not in full and date(2025, 12, 24) not in full  # early halts
        assert date(2025, 12, 25) not in full and date(2025, 11, 27) not in full  # closures
        assert date(2025, 12, 23) in full and date(2025, 11, 26) in full
    assert date(2025, 7, 3) not in cal.EQUITY_FULL_SESSIONS  # equity early halt only
    assert date(2025, 7, 3) in cal.METALS_FULL_SESSIONS


def test_a_delayed_crypto_start_is_a_full_session_r_1b_3() -> None:
    assert date(2026, 6, 1) in cal.CRYPTO_FULL_SESSIONS
    assert date(2026, 6, 1) in cal.WKNDBTC_DATES


def test_member_dates_are_the_sorted_intersections() -> None:
    expected = {
        "FLIGHT_DATES": tuple(sorted(_full_sessions("equity") & _full_sessions("metals"))),
        "OILCAD_DATES": tuple(sorted(_full_sessions("energy") & _full_sessions("fx"))),
        "WKNDBTC_DATES": tuple(sorted(_full_sessions("equity") & _full_sessions("crypto")))}
    for name, days in expected.items():
        assert getattr(cal, name) == days, name
    for name, count in RESEARCH_MEMBER.items():
        days = getattr(cal, name)
        assert isinstance(days, tuple) and list(days) == sorted(set(days))
        assert sum(1 for d in days if _in_research(d)) == count, name
    wk = set(cal.WKNDBTC_DATES)
    mondays = [d for d in wk if _in_research(d) and d.weekday() == 0
               and d - timedelta(days=3) in wk]
    assert len(mondays) == RESEARCH_WKNDBTC_MONDAYS
    assert date(2025, 11, 28) not in cal.FLIGHT_DATES  # the brief's non-full example


@pytest.mark.parametrize("group", list(EARLIER))
def test_group_sets_against_the_earlier_clusters_frozen_tables(group: str) -> None:
    """Equal over the common range except the listed dates, which the earlier table keeps and
    the K8 definition removes (reported to the lead; the K8 table stays as S0.8 defines it)."""
    module, name, earlier_only = EARLIER[group]
    old = {date.fromisoformat(s) for s in getattr(module, name)}
    lo, hi = max(min(old), FIRST), min(max(old), LAST)
    mine = {d for d in getattr(cal, f"{TABLE[group]}_FULL_SESSIONS") if lo <= d <= hi}
    old = {d for d in old if lo <= d <= hi}
    assert sorted(mine - old) == []
    assert sorted(old - mine) == list(earlier_only)
    assert not [d for d in earlier_only if _in_research(d)]  # none in the research window


def test_previous_dates_are_the_k_most_recent_strictly_before_d() -> None:
    days = (date(2025, 1, 2), date(2025, 1, 3), date(2025, 1, 6), date(2025, 1, 7))
    prev = cal.previous_dates
    assert prev(days, date(2025, 1, 7), 2) == (date(2025, 1, 3), date(2025, 1, 6))
    assert prev(days, date(2025, 1, 5), 2) == (date(2025, 1, 2), date(2025, 1, 3))
    assert prev(days, date(2025, 1, 8), 9) == days
    assert prev(days, date(2025, 1, 3), 5) == (date(2025, 1, 2),)
    assert prev(days, date(2025, 1, 2), 3) == () and prev(days, date(2025, 1, 7), 0) == ()
    assert prev((), date(2025, 1, 7), 3) == ()
    refs = prev(cal.FLIGHT_DATES, date(2025, 12, 1), 3)  # skips 11-27 (closed) and 11-28 (halt)
    assert refs == (date(2025, 11, 24), date(2025, 11, 25), date(2025, 11, 26))
    twenty = prev(cal.FLIGHT_DATES, date(2025, 12, 1), 20)
    assert len(twenty) == 20 and twenty[-1] == date(2025, 11, 26)
    assert date(2025, 11, 28) not in twenty and twenty[0] == date(2025, 10, 30)


# ------------------------------------------------------------------ the releases ----
def _rows_naming(root: str) -> list[dict]:
    return [r for r in _json(CALENDAR_JSON)["releases"]
            if root in r["products"] and FIRST.isoformat() <= r["date"] <= LAST.isoformat()]


@needs_calendar_json
@pytest.mark.parametrize("root", ["MGC", "6C", "MNQ"])
def test_guard_instants_are_every_calendar_row_naming_the_root(root: str) -> None:
    rows = _rows_naming(root)
    expected = sorted({int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
                           .timestamp()) for r in rows})
    got = rel.GUARD_INSTANTS[root]
    assert isinstance(got, tuple) and all(type(s) is int for s in got)
    assert list(got) == expected and len(got) == {"MGC": 312, "6C": 513, "MNQ": 313}[root]
    research = {}
    for r in rows:
        if _in_research(date.fromisoformat(r["date"])):
            key = (r["release"], r["time_local"])
            research[key] = research.get(key, 0) + 1
            assert r["tz"] == "America/New_York"
    assert research == RESEARCH_ROWS[root]


@needs_calendar_json
def test_no_correction_the_e4_dropped_wpsr_rows_stay_in_r_1b_1() -> None:
    ids = {i for _, i, _ in rel.GUARD_ROWS}
    assert {"WPSR-2025-12-29", "WPSR-2026-05-28"} <= ids
    assert _ct_ns(date(2025, 12, 29), 16, 0) // NS in rel.GUARD_INSTANTS["6C"]  # 17:00 ET
    assert _ct_ns(date(2026, 5, 28), 11, 0) // NS in rel.GUARD_INSTANTS["6C"]  # 12:00 ET
    assert set(rel.GUARD_INSTANTS) == {"MGC", "6C", "MNQ"}


def test_guard_rows_are_unique_and_name_only_guard_roots() -> None:
    ids = [i for _, i, _ in rel.GUARD_ROWS]
    assert len(ids) == len(set(ids)) == 769
    assert [s for s, _, _ in rel.GUARD_ROWS] == sorted(s for s, _, _ in rel.GUARD_ROWS)
    assert all(roots and set(roots) <= {"MGC", "6C", "MNQ"} for _, _, roots in rel.GUARD_ROWS)


def test_in_guard_edges() -> None:
    """R and R + 60 s guarded; R + 120 s and R - 60 s not (integer ns, both ends)."""
    for root in ("MGC", "6C", "MNQ"):
        for r in (rel.GUARD_INSTANTS[root][0], rel.GUARD_INSTANTS[root][-1]):
            ns = r * NS
            assert rel.in_guard(root, ns) and rel.in_guard(root, ns + 60 * NS)
            assert rel.in_guard(root, ns + 120 * NS - 1)
            assert not rel.in_guard(root, ns + 120 * NS)
            assert not rel.in_guard(root, ns - 60 * NS) and not rel.in_guard(root, ns - 1)
    assert not rel.in_guard("MGC", 0)
    with pytest.raises(KeyError):
        rel.in_guard("MES", _ct_ns(date(2025, 6, 18), 13, 0))


def test_mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates() -> None:
    """Task 1b A3: of the research-window MGC instants only FOMC 13:00 CT meets a flight fill
    minute (08:35..14:55 every 5 minutes); 13:00 and 13:01 are guarded, 13:05 is not."""
    grid = {(8 * 60 + 30 + 5 * k) for k in range(1, 78)}
    hits = []
    for s in rel.GUARD_INSTANTS["MGC"]:
        local = datetime.fromtimestamp(s, tz=UTC).astimezone(CT)
        if _in_research(local.date()) and local.hour * 60 + local.minute in grid:
            hits.append(local)
    assert len(hits) == 10 and {(h.hour, h.minute) for h in hits} == {(13, 0)}
    fomc = date(2025, 6, 18)
    assert date(2025, 6, 18) in {h.date() for h in hits}
    assert rel.in_guard("MGC", _ct_ns(fomc, 13, 0)) and rel.in_guard("MGC", _ct_ns(fomc, 13, 1))
    assert not rel.in_guard("MGC", _ct_ns(fomc, 13, 5))
    assert not rel.in_guard("MGC", _ct_ns(fomc, 12, 59))
    assert not rel.in_guard("MGC", _ct_ns(date(2025, 6, 17), 13, 0))  # not an FOMC date
