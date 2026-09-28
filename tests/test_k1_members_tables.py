"""Stage E.7 K1 tables of MemberCoder-B: the pins of strategy/members/k1/_calendar.py and
strategy/members/k1/_vxn.py (reports/stage_e7_member_specs.md S0.8, S0.11, K1-L-02, K1-L-10 and
the section 9 rulings R-1b-1..R-1b-5).

Every table is recomputed here from its sources by code independent of the generator
(reports/stage_e7_briefs/gen_k1_tables.py): EC-CAL through data.group_session, the engine's F
through rules.sessions for MNQ, M2K and MYM, and the saved Cboe file through the csv module and
Decimal. The generator is loaded from its path only to assert that each module is exactly its
output. The VXN pins skip, with the reason, only if the saved file is absent. No bar data is read.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

from data.group_session import load_group_calendar
from rules import sessions
from strategy.members.k1 import _calendar as cal_tables
from strategy.members.k1 import _event_common as common
from strategy.members.k1 import _vxn as vxn_tables
from strategy.members.k1 import vxnband

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / "reports" / "stage_e7_briefs" / "gen_k1_tables.py"
VXN_FILE = "data/vendor/index_history/vxn/VXN_History.csv"
VXN_SHA256 = "f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc"  # spec section 9
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
VXN_FIRST = date(2019, 4, 30)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
ROOTS = ("MNQ", "M2K", "MYM")
# Spec header: research-window weekdays that are not equity trade dates, and trade dates with an
# early engine F (every one of them is also an early halt).
RESEARCH_NON_TRADE = ("2025-04-18", "2025-12-25", "2026-01-01")
RESEARCH_EARLY_F = (
    "2025-05-26", "2025-06-19", "2025-07-03", "2025-07-04", "2025-09-01", "2025-11-27",
    "2025-11-28", "2025-12-24", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19")
# Section 9: the dropped rows (R-1b-3, R-1b-3, R-1b-2) and R-1b-5's research dates without V.
DROPPED = {"2021-04-02": "R-1b-3", "2021-12-24": "R-1b-3", "2024-02-01": "R-1b-2"}
R_1B_5 = ("2025-05-27", "2025-06-20", "2025-07-07", "2025-09-02", "2025-11-28", "2026-01-20",
          "2026-02-17", "2026-04-06", "2026-05-26")
needs_vxn = pytest.mark.skipif(not (REPO / VXN_FILE).is_file(),
                               reason=f"{VXN_FILE} (Task 1b's saved Cboe file) is absent")


def _sha(rel: str) -> str:
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()


def _days(first: date, last: date) -> list[date]:
    return [first + timedelta(days=n) for n in range((last - first).days + 1)]


@cache
def _generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k1_tables", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


# ------------------------------------------------------------------ the calendar ----
def test_calendar_sources_carry_the_pinned_sha256() -> None:
    pinned = dict(cal_tables.SOURCE_SHA256)
    assert set(pinned) == {"data/calendars/__init__.py", "data/calendars/equity.py",
                           "data/cme_calendar.py", "rules/sessions.py"}
    for rel, sha in pinned.items():
        assert _sha(rel) == sha, rel
    cal = load_group_calendar("equity")
    assert set(cal.module_sha256()) | {"rules/sessions.py"} == set(pinned)
    assert cal_tables.TABLE_RANGE == ("2019-05-01", "2026-06-19")
    assert cal_tables.F_ROOTS == ROOTS and cal_tables.REGULAR_F_CT == "15:08"


def test_the_modules_are_exactly_the_generators_output() -> None:
    texts = _generator().build()
    expected = {"strategy/members/k1/_calendar.py"}
    if (REPO / VXN_FILE).is_file():
        expected.add("strategy/members/k1/_vxn.py")
    assert set(texts) == expected
    for rel, text in texts.items():
        assert (REPO / rel).read_text(encoding="utf-8") == text, rel


def test_equity_trade_dates_are_every_ec_cal_trade_date_of_the_range() -> None:
    cal = load_group_calendar("equity")
    trade = [d.isoformat() for d in _days(FIRST, LAST) if cal.is_trade_date(d)]
    assert tuple(trade) == cal_tables.EQUITY_TRADE_DATES and len(trade) == 1846
    assert trade[0] == "2019-05-01" and trade[-1] == "2026-06-19"
    window = [d for d in _days(*RESEARCH) if d.weekday() < 5]
    assert tuple(d.isoformat() for d in window
                 if d.isoformat() not in set(trade)) == RESEARCH_NON_TRADE
    assert "2025-05-26" in trade  # an early-halt exchange holiday is an equity trade date


def test_full_sessions_have_no_early_halt_and_the_regular_f_on_all_three_roots() -> None:
    """S0.8 / K1-L-10 (K3-L-11): no early_halt_ct AND F = 15:08 CT on CT date d; F is the same
    for MNQ, M2K and MYM on every trade date, and the two tests never disagree."""
    cal = load_group_calendar("equity")
    full, disagree = [], []
    for iso in cal_tables.EQUITY_TRADE_DATES:
        d = date.fromisoformat(iso)
        flats = {sessions.flatten_time_ct(r, d) for r in ROOTS}
        assert len(flats) == 1, (iso, flats)
        (f,) = flats
        no_halt, regular = cal.early_halt_ct(d) is None, f == time(15, 8)
        if no_halt and regular:
            full.append(iso)
        if no_halt != regular:
            disagree.append(iso)
    assert tuple(full) == cal_tables.EQUITY_FULL_SESSIONS and len(full) == 1779
    assert disagree == []
    text = (REPO / "strategy/members/k1/_calendar.py").read_text(encoding="utf-8")
    assert "the early-halt test and the F test disagree: none" in text
    removed = [d for d in cal_tables.EQUITY_TRADE_DATES
               if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat() and d not in full]
    assert tuple(removed) == RESEARCH_EARLY_F
    assert frozenset(date.fromisoformat(d) for d in full) == common.FULL_SESSIONS


def test_previous_trade_date_is_the_table_entry_immediately_before() -> None:
    trade = [date.fromisoformat(d) for d in cal_tables.EQUITY_TRADE_DATES]
    assert {b: a for a, b in zip(trade, trade[1:], strict=False)} == common.PREVIOUS_TRADE_DATE
    assert common.PREVIOUS_TRADE_DATE[date(2025, 5, 27)] == date(2025, 5, 26)  # Memorial Day
    assert common.PREVIOUS_TRADE_DATE[date(2025, 4, 21)] == date(2025, 4, 17)  # Good Friday
    assert common.PREVIOUS_TRADE_DATE[date(2025, 5, 19)] == date(2025, 5, 16)  # a Monday
    assert date(2019, 5, 1) not in common.PREVIOUS_TRADE_DATE  # the table's first date


# ------------------------------------------------------------------ VXN ----
@cache
def _file_rows() -> list[list[str]]:
    raw = (REPO / VXN_FILE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == VXN_SHA256
    rows = list(csv.reader(io.StringIO(raw.decode("ascii"))))
    assert rows[0] == ["DATE", "OPEN", "HIGH", "LOW", "CLOSE"]
    return rows[1:]


def _iso(mdy: str) -> str:
    return datetime.strptime(mdy, "%m/%d/%Y").date().isoformat()


@needs_vxn
def test_the_vxn_file_is_section_9s() -> None:
    assert vxn_tables.VXN_SOURCE_SHA256 == ((VXN_FILE, VXN_SHA256),)
    assert _sha(VXN_FILE) == VXN_SHA256
    assert vxn_tables.VXN_RANGE == ("2019-04-30", "2026-06-19")


@needs_vxn
def test_vxn_close_is_every_row_of_the_range_less_the_three_drops() -> None:
    in_range = [(_iso(r[0]), r[4]) for r in _file_rows()
                if VXN_FIRST.isoformat() <= _iso(r[0]) <= LAST.isoformat()]
    assert len(in_range) == 1797  # R-1b-1
    kept = [(d, c) for d, c in in_range if d not in DROPPED]
    assert tuple(kept) == vxn_tables.VXN_CLOSE and len(kept) == 1794
    assert kept[0][0] == "2019-04-30" and kept[-1][0] == "2026-06-18"
    for _d, close in kept:  # the exact decimal string of the file (6 decimals)
        assert Decimal(close).as_tuple().exponent == -6
    assert {date.fromisoformat(d): Decimal(c) for d, c in kept} == vxnband._VXN


@needs_vxn
def test_the_dropped_rows_and_their_reasons() -> None:
    """R-1b-3: 2021-04-02 and 2021-12-24 repeat the prior row's close on all four fields (NYSE
    closed); R-1b-2: 2024-02-01's CLOSE is now 17.33 (11.20 in the 2024-04-19 Wayback copy)."""
    assert tuple(d for d, _ in vxn_tables.DROPPED_VXN) == tuple(DROPPED)
    for d, reason in vxn_tables.DROPPED_VXN:
        assert reason.startswith(DROPPED[d] + ":"), (d, reason)
    rows = _file_rows()
    index = {_iso(r[0]): i for i, r in enumerate(rows)}
    for d in ("2021-04-02", "2021-12-24"):
        row, prior = rows[index[d]], rows[index[d] - 1]
        assert row[1] == row[2] == row[3] == row[4] == prior[4], d
    assert rows[index["2024-02-01"]][4] == "17.330000"
    have = {d for d, _ in vxn_tables.VXN_CLOSE}
    assert not have & set(DROPPED)


@needs_vxn
def test_research_trade_dates_without_v_are_r_1b_5s() -> None:
    """K1-L-02 / R-1b-5: the trade dates d whose EC-CAL trade date d-1 has no VXN_CLOSE row; the
    drops add 2021-04-05 and 2024-02-02 (no V, not traded)."""
    have = {d for d, _ in vxn_tables.VXN_CLOSE}
    trade = cal_tables.EQUITY_TRADE_DATES
    no_v = [d for prev, d in zip(trade, trade[1:], strict=False) if prev not in have]
    research = [d for d in no_v if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    assert tuple(research) == R_1B_5
    assert {"2021-04-05", "2024-02-02"} <= set(no_v)
    for d in (*R_1B_5, "2021-04-05", "2024-02-02"):
        assert vxnband.vxn_for(date.fromisoformat(d)) is None, d
    assert vxnband.vxn_for(date(2021, 4, 6)) is not None
    # every row the members can read is an EC-CAL trade date (after the drops)
    assert all(d in set(trade) for d in have if d >= FIRST.isoformat())


def test_the_cluster_init_is_empty() -> None:
    assert (REPO / "strategy" / "members" / "k1" / "__init__.py").read_bytes() == b""
