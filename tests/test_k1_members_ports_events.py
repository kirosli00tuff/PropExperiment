"""Stage E.7 K1 ports of MemberCoder-A, part 4: the CPI window and the event minutes of
K1-cp1-01, K1-cp2-01 and K1-cp3-01 on MNQ, M2K and MYM (reports/stage_e7_member_specs.md header
"Release calendar", S0.13 and K1-L-15; sections 1-3, "Release instants read: none").

The ports read no release: on an FOMC (13:00 CT) or ISM Services (09:00 CT) date they emit
exactly what their rule says, and the engine moves a fill that would land in [release,
release + 2 min) (D9.5a). On a CPI date no port emits an intent on a bar in [07:25, 07:35] CT
(K1-L-15). The dates are real research-window rows of the frozen release calendar
(reports/stage_e2b_release_calendar.json, loaded read-only through
screening.stage_e_rules.load_release_calendar); the bars are synthetic, built with
tests/test_k1_members_ports.py's kit and run through the real Stage E engine. No bar file is read.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime, time
from types import ModuleType

import pytest

from screening.stage_e_rules import ReleaseCalendar, load_release_calendar
from strategy.members.k1 import cp1, cp2, cp3
from tests.test_k1_members_ports import (
    CP1_BUY_DAY,
    CP1_BUY_EVENING,
    CT,
    FRI_NFP,
    MODULES,
    MON_ISM,
    MON_PRE_CPI,
    NS,
    ROOTS,
    TUE_CPI,
    TUE_PRE_FOMC,
    WED_FOMC,
    Day,
    fills,
    hm,
    intents,
    make,
    run,
    trade,
)
from tests.test_k1_members_ports_cp2 import CP2_OR, UP4
from tests.test_k1_members_ports_cp3 import BUY_08

REAL = load_release_calendar()
STRONG = (0, 200, 0, 200)  # a 200-tick jump: MNQ 50.00, M2K 20.00, MYM 200 index points


def ns_of(day: date, hh: int, mm: int) -> int:
    return int(datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC).timestamp()) * NS


def test_the_release_rows_used_are_frozen_calendar_facts() -> None:
    # FOMC 13:00 and ISM Services 09:00 CT carry MNQ, M2K and MYM (spec header); CPI 07:30 CT is
    # a CPI row, whose D9.12 window the engine applies to all three (K1-L-15)
    for root in ROOTS:
        instants = set(REAL.by_root[root])
        assert ns_of(WED_FOMC, 13, 0) in instants, root
        assert ns_of(MON_ISM, 9, 0) in instants, root
    assert datetime.combine(TUE_CPI, time(7, 30), tzinfo=CT) in {
        t.astimezone(CT) for t in REAL.cpi}
    assert REAL.first <= FRI_NFP and REAL.last >= TUE_CPI


# ---------------------------------------------------------------------------- the CPI ----
def cpi_days(module: ModuleType) -> list[Day]:
    """MON 05-12 and the CPI date TUE 05-13 (bars from 07:00 CT, a 200-tick jump on every bar
    07:25-07:35), with each port's own trade on TUE."""
    jump = {x: STRONG for x in range(hm(7, 25), hm(7, 36))}
    if module is cp1:
        return [Day(MON_PRE_CPI),
                Day(TUE_CPI, {**jump, **CP1_BUY_DAY}, CP1_BUY_EVENING, start=hm(7, 0))]
    if module is cp2:
        return [Day(MON_PRE_CPI), Day(TUE_CPI, {**jump, **CP2_OR, hm(8, 45): UP4}, start=hm(7, 0))]
    return [Day(MON_PRE_CPI, BUY_08), Day(TUE_CPI, jump, start=hm(7, 0))]


EXPECTED_CPI = {cp1: trade(TUE_CPI, "14:30", "14:59"), cp2: trade(TUE_CPI, "08:46", "10:01"),
                cp3: trade(TUE_CPI, "08:31", "14:59")}


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_no_port_emits_an_intent_in_the_cpi_window(module: ModuleType, root: str) -> None:
    res = run(make(module, root), cpi_days(module), releases=REAL)
    in_window = [i for i in intents(res) if i[0] == TUE_CPI and "07:25" <= i[1] <= "07:35"]
    assert in_window == []
    assert all(i[1] >= "08:30" for i in intents(res))  # no K1 fill before 08:31 (K1-L-15)
    assert fills(res) == EXPECTED_CPI[module]  # the port's own rule, untouched by the jump


# ------------------------------------------------------------------- the event minutes ----
def same_with_and_without(member_of: Callable[[], object], days: list[Day]) -> list:
    """The member's intents under the real release calendar; they equal those without it."""
    with_releases = run(member_of(), days, releases=REAL)
    without = run(member_of(), days)
    assert intents(with_releases) == intents(without)
    assert fills(with_releases) == fills(without)
    return intents(with_releases)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_on_fomc_and_ism_dates_is_unchanged(root: str) -> None:
    for day in (WED_FOMC, MON_ISM):
        days = [Day(day, CP1_BUY_DAY, CP1_BUY_EVENING)]
        assert same_with_and_without(lambda: make(cp1, root), days) == [
            (day, "14:29", True, None), (day, "14:58", True, None)]


@pytest.mark.parametrize("root", ROOTS)
def test_cp3_holds_through_fomc_and_ism_unchanged(root: str) -> None:
    for prior, day in ((TUE_PRE_FOMC, WED_FOMC), (FRI_NFP, MON_ISM)):
        days = [Day(prior, BUY_08), Day(day)]
        assert same_with_and_without(lambda: make(cp3, root), days) == [
            (day, "08:30", True, None), (day, "14:58", True, None)]
        assert fills(run(make(cp3, root), days, releases=REAL)) == trade(day, "08:31", "14:59")


def cp2_on(day: date, trigger: int) -> list[Day]:
    return [Day(day, {**CP2_OR, trigger: UP4})]


def cp2_run(root: str, days: list[Day], releases: ReleaseCalendar | None = None
            ) -> tuple[list, list]:
    res = run(make(cp2, root), days) if releases is None else run(make(cp2, root), days,
                                                                  releases=releases)
    return intents(res), fills(res)


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_a_trigger_at_0859_on_an_ism_date_fills_at_0902(root: str) -> None:
    days = cp2_on(MON_ISM, hm(8, 59))
    got_intents, got_fills = cp2_run(root, days, REAL)
    assert got_intents == [(MON_ISM, "08:59", True, None), (MON_ISM, "10:16", True, None)]
    assert got_fills == trade(MON_ISM, "09:02", "10:17")  # the count starts at the fill
    plain_intents, plain_fills = cp2_run(root, days)  # no release: fill 09:00
    assert plain_intents == [(MON_ISM, "08:59", True, None), (MON_ISM, "10:14", True, None)]
    assert plain_fills == trade(MON_ISM, "09:00", "10:15")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_emits_on_the_0900_ism_bar_and_the_engine_moves_the_fill(root: str) -> None:
    got_intents, got_fills = cp2_run(root, cp2_on(MON_ISM, hm(9, 0)), REAL)
    assert got_intents[0] == (MON_ISM, "09:00", True, None)  # the rule's bar, not avoided
    assert got_fills == trade(MON_ISM, "09:02", "10:17")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_emits_on_the_1300_fomc_bar_and_the_engine_moves_the_fill(root: str) -> None:
    got_intents, got_fills = cp2_run(root, cp2_on(WED_FOMC, hm(13, 0)), REAL)
    assert got_intents[0] == (WED_FOMC, "13:00", True, None)
    assert got_fills == trade(WED_FOMC, "13:02", "14:17")
    earlier_intents, earlier_fills = cp2_run(root, cp2_on(WED_FOMC, hm(12, 59)), REAL)
    assert earlier_intents[0] == (WED_FOMC, "12:59", True, None)
    assert earlier_fills == trade(WED_FOMC, "13:02", "14:17")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_an_exit_due_at_1259_on_an_fomc_date_fills_at_1302_and_is_sent_once(root: str
                                                                                  ) -> None:
    # entry on 11:44 (fill 11:45): the 75th present bar is 12:59; its exit fill would be 13:00,
    # which the engine moves to 13:02; while it waits the member sends nothing more
    got_intents, got_fills = cp2_run(root, cp2_on(WED_FOMC, hm(11, 44)), REAL)
    assert got_intents == [(WED_FOMC, "11:44", True, None), (WED_FOMC, "12:59", True, None)]
    assert got_fills == trade(WED_FOMC, "11:45", "13:02")
