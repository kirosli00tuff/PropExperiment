"""Stage E.9 K8-flight-01 of MemberCoder-A, part 2: the first trigger only, C6, the missing and
late bars, T_e, and the H30 / HEOD exits (reports/stage_e9_member_specs.md section 1, S0.6, S0.7,
S0.10; readings K8-L-06, K8-L-07, K8-L-08, E.3-L-08, E.3-L-22). Direct on_minute calls with the
kit of tests/test_k8_members_flight.py (Q(d) = -3/B after ``ready``; a dip of 5 ticks
triggers). No bar file is read.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date

import pytest

from strategy.members.k8 import _releases as rel
from strategy.members.k8 import flight
from strategy.members.k8.flight import FlightToGold
from strategy.stage_e.interface import LegIntent
from tests.test_k8_members_flight import (
    DAY,
    FOMC,
    NS,
    Out,
    buy_at,
    call,
    dip_path,
    end_bar,
    entries,
    feed,
    hm,
    mes,
    mgc,
    ns_at,
    prepare,
    ready,
)

CLOSE = hm(15, 10)  # the last view the exit tests feed


def ready_as(variant: str, day: date = DAY) -> FlightToGold:
    member = flight.make_h30() if variant == "H30" else flight.make_heod()
    prepare(member, day)
    return member


def enter(member: FlightToGold, k: int, day: date = DAY) -> None:
    """Feed the block bars up to the bar at t_k - 1 with a 5-tick dip at k: the entry."""
    assert entries(feed(member, day, dip_path({k: 5}, n_values=k))) == buy_at(end_bar(k))


def hold(member: FlightToGold, start: int, end: int = CLOSE, *, day: date = DAY,
         missing: Iterable[int] = (), pending: Mapping[int, int] | None = None,
         flat_from: int | None = None) -> Out:
    """One view per minute start..end with the MGC bar (unless missing), the account long 1
    (flat from ``flat_from``), ``pending`` by minute; the outputs by minute."""
    out: Out = {}
    missing, pending = set(missing), pending or {}
    for minute in range(start, end + 1):
        g = None if minute in missing else mgc(day, minute)
        position = 0 if flat_from is not None and minute >= flat_from else 1
        got = call(member, day, minute, mes_bar=mes(day, minute), mgc_bar=g, position=position,
                   pending=pending.get(minute, 0))
        if got:
            out[minute] = got
    return out


def sells(out: Out) -> list[int]:
    """The minutes of the exit intents (sell 1 MGC)."""
    found = []
    for minute, got in sorted(out.items()):
        assert [(i.root, i.side, i.quantity) for i in got] == [("MGC", "sell", 1)], minute
        found.append(minute)
    return found


def guard_at(monkeypatch: pytest.MonkeyPatch, day: date, *minutes: int) -> None:
    monkeypatch.setitem(rel.GUARD_INSTANTS, "MGC",
                        tuple(sorted(ns_at(day, m) // NS for m in minutes)))


# ------------------------------------------------------------- first trigger only ----
def test_only_the_first_trigger_of_d_enters_even_when_refused() -> None:
    member = ready()  # the account stays flat: the engine refused the first intent
    assert entries(feed(member, DAY, dip_path({3: 5, 10: 5, 40: 9}))) == buy_at(end_bar(3))


def test_a_second_trigger_while_long_and_after_the_exit_does_nothing() -> None:
    member = ready()
    enter(member, 3)
    out = hold(member, hm(8, 45), hm(9, 20), pending={hm(9, 15): -1})
    assert sells(out) == [hm(9, 14), hm(9, 16), hm(9, 17), hm(9, 18), hm(9, 19), hm(9, 20)]
    later = {i: c for i, c in enumerate(dip_path({60: 9})) if i >= 50}
    for i, close in later.items():  # flat again, a deep dip at k = 60: no second entry
        got = call(member, DAY, end_bar(i), mes_bar=mes(DAY, end_bar(i), close),
                   mgc_bar=mgc(DAY, end_bar(i)))
        assert got == []


def test_the_next_date_enters_again() -> None:
    member = ready()
    enter(member, 3)
    hold(member, hm(8, 45), flat_from=hm(9, 15))
    nxt = date(2025, 6, 18)
    assert entries(feed(member, nxt, dip_path({3: 5}))) == buy_at(end_bar(3))


def test_no_entry_while_an_order_is_pending_on_mgc() -> None:
    member = ready()
    feed(member, DAY, dip_path(n_values=2))
    got = call(member, DAY, end_bar(3), mes_bar=mes(DAY, end_bar(3), 20000 - 5),
               mgc_bar=mgc(DAY, end_bar(3)), pending=1)
    assert got == []


# --------------------------------------------------------------------------- C6 ----
def test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305() -> None:
    member = ready(FOMC)  # r_54 = -5/B, r_55 = -5/(B - 5): both trigger (Q = -3/B)
    out = feed(member, FOMC, dip_path({54: 5, 55: 10}))  # t_54 = 13:00, t_55 = 13:05
    assert entries(out) == buy_at(hm(13, 4))
    member = ready(FOMC)
    assert entries(feed(member, FOMC, dip_path({54: 5}))) == []


def test_a_1300_trigger_on_a_non_fomc_date_enters() -> None:
    member = ready()
    assert entries(feed(member, DAY, dip_path({54: 5, 55: 10}))) == buy_at(hm(12, 59))


def test_a_skipped_trigger_with_a_missing_entry_bar_does_not_end_the_day() -> None:
    member = ready(FOMC)  # C6 first: the 13:00 trigger is skipped, its missing bar is moot
    out = feed(member, FOMC, dip_path({54: 5, 55: 10}), mgc_skip={54})
    assert entries(out) == buy_at(hm(13, 4))


@pytest.mark.parametrize(("guard_minute", "entered"), [
    (hm(10, 59), False),  # t = 11:00 in [10:59, 11:01)
    (hm(11, 0), False),  # t = R
    (hm(10, 58), True),  # t = R + 120 s: not guarded
    (hm(11, 1), True),  # t < R
])
def test_c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min(
        monkeypatch: pytest.MonkeyPatch, guard_minute: int, entered: bool) -> None:
    """k = 30: decision t = 11:00, the entry bar 10:59. A guard [R, R + 2 min) holding 11:00
    skips the trigger; the 11:05 trigger then enters."""
    guard_at(monkeypatch, DAY, guard_minute)
    member = ready()
    out = feed(member, DAY, dip_path({30: 5, 31: 10}))
    assert entries(out) == buy_at(hm(10, 59) if entered else hm(11, 4))


def test_c6_reads_the_traded_roots_instants_only(monkeypatch: pytest.MonkeyPatch) -> None:
    for root in ("6C", "MNQ"):
        monkeypatch.setitem(rel.GUARD_INSTANTS, root, (ns_at(DAY, hm(11, 0)) // NS,))
    member = ready()
    assert entries(feed(member, DAY, dip_path({30: 5}))) == buy_at(hm(10, 59))


# ------------------------------------------------------------- missing entry bar ----
def test_a_missing_entry_bar_at_the_first_trigger_ends_the_day() -> None:
    member = ready()
    assert entries(feed(member, DAY, dip_path({3: 5, 10: 5}), mgc_skip={3})) == []


def test_an_entry_bar_of_another_trade_date_counts_as_missing() -> None:
    member = ready()
    nxt = date(2025, 6, 18)
    feed(member, DAY, dip_path(n_values=2))
    got = call(member, DAY, end_bar(3), mes_bar=mes(DAY, end_bar(3), 20000 - 5),
               mgc_bar=mgc(DAY, end_bar(3), trade_date=nxt))
    assert got == []
    rest = {i: c for i, c in enumerate(dip_path({10: 5})) if i >= 4}
    for i, close in rest.items():
        assert call(member, DAY, end_bar(i), mes_bar=mes(DAY, end_bar(i), close),
                    mgc_bar=mgc(DAY, end_bar(i))) == []


# --------------------------------------------------------- MES bars late or missing ----
def test_an_mes_bar_absent_at_tk_minus_1_and_present_at_tk_is_never_used() -> None:
    member = ready()
    feed(member, DAY, dip_path(n_values=2))  # bars 08:29, 08:34, 08:39
    missing = call(member, DAY, hm(8, 44), mes_bar=None, mgc_bar=mgc(DAY, hm(8, 44)))
    assert missing == []
    late = call(member, DAY, hm(8, 45), mes_bar=mes(DAY, hm(8, 45), 20000 - 50),
                mgc_bar=mgc(DAY, hm(8, 45)))  # the 08:44 bar arrives one minute late
    assert late == []
    # block 4 (start bar 08:44 missing) is undefined too; block 5 triggers normally
    out = {}
    for i in (4, 5):
        out[end_bar(i)] = call(member, DAY, end_bar(i),
                               mes_bar=mes(DAY, end_bar(i), 20000 - 5 if i == 5 else 20000),
                               mgc_bar=mgc(DAY, end_bar(i)))
    assert entries({m: g for m, g in out.items() if g}) == buy_at(end_bar(5))


def test_no_forward_fill_of_an_earlier_mes_close() -> None:
    member = ready()
    feed(member, DAY, dip_path(n_values=2))  # 08:29, 08:34, 08:39
    call(member, DAY, hm(8, 43), mes_bar=mes(DAY, hm(8, 43), 20000 - 50),
         mgc_bar=mgc(DAY, hm(8, 43)))  # t_3 - 2 present with a dip
    got = call(member, DAY, hm(8, 44), mes_bar=None, mgc_bar=mgc(DAY, hm(8, 44)))
    assert got == []


# --------------------------------------------------------------- T_e and the exits ----
def test_h30_exit_is_sent_on_the_bar_at_te_plus_29() -> None:
    member = ready_as("H30")
    enter(member, 3)  # entry bar 08:44, fill at 08:45 = T_e
    assert sells(hold(member, hm(8, 45), hm(9, 14))) == [hm(9, 14)]


def test_heod_exit_is_sent_on_the_bar_at_1504() -> None:
    member = ready_as("HEOD")
    enter(member, 3)
    assert sells(hold(member, hm(8, 45), hm(15, 4))) == [hm(15, 4)]


@pytest.mark.parametrize(("k", "exit_bar"), [
    (72, hm(14, 59)),  # t 14:30: T_e + 29 = 14:59
    (73, hm(15, 4)),  # t 14:35: T_e + 29 = 15:04 = the cap
    (74, hm(15, 4)),  # t 14:40: capped at 15:04 (not 15:09)
    (77, hm(15, 4)),  # t 14:55: capped, a 10-minute hold
])
def test_h30_exit_is_capped_at_1504(k: int, exit_bar: int) -> None:
    member = ready_as("H30")
    enter(member, k)
    t_k = end_bar(k) + 1
    assert sells(hold(member, t_k, exit_bar)) == [exit_bar]


def test_an_mgc_bar_missing_at_tk_moves_te_and_the_h30_exit() -> None:
    member = ready_as("H30")
    enter(member, 3)  # entry bar 08:44; no MGC bar at 08:45: the engine fills at 08:46
    got = call(member, DAY, hm(8, 45), mes_bar=mes(DAY, hm(8, 45)), mgc_bar=None, position=0,
               pending=1)
    assert got == []
    assert sells(hold(member, hm(8, 46), hm(9, 15))) == [hm(9, 15)]


@pytest.mark.parametrize(("variant", "missing", "sent"), [
    ("H30", {hm(9, 14)}, hm(9, 15)),
    ("H30", {hm(9, 14), hm(9, 15), hm(9, 16)}, hm(9, 17)),
    ("HEOD", {hm(15, 4)}, hm(15, 5)),
    ("HEOD", {hm(15, 4), hm(15, 5)}, hm(15, 6)),
])
def test_a_missing_exit_bar_sends_the_exit_on_the_first_later_bar(
        variant: str, missing: set[int], sent: int) -> None:
    member = ready_as(variant)
    enter(member, 3)
    assert sells(hold(member, hm(8, 45), sent, missing=missing)) == [sent]


def test_a_refused_exit_is_resent_and_a_pending_exit_is_not_duplicated() -> None:
    member = ready_as("H30")
    enter(member, 3)
    out = hold(member, hm(8, 45), hm(9, 18), pending={hm(9, 15): -1, hm(9, 16): -1})
    assert sells(out) == [hm(9, 14), hm(9, 17), hm(9, 18)]


def test_an_engine_closed_position_gets_no_exit() -> None:
    member = ready_as("HEOD")
    enter(member, 3)
    out = hold(member, hm(8, 45), hm(15, 10), flat_from=hm(10, 0))  # D9.7 exit at 10:00
    assert out == {}


def test_t_e_resets_when_flat() -> None:
    """After the exit fills, a later position (impossible on real bars: one entry a day) would
    count its own T_e: the member keeps no stale exit time."""
    member = ready_as("H30")
    enter(member, 3)
    hold(member, hm(8, 45), hm(9, 15), pending={hm(9, 15): -1})
    hold(member, hm(9, 16), hm(9, 20), flat_from=hm(9, 16))
    assert sells(hold(member, hm(10, 0), hm(10, 29))) == [hm(10, 29)]


# ------------------------------------------------------------- never MES, never late ----
def test_the_last_fill_is_1505_for_both_variants() -> None:
    for variant in ("H30", "HEOD"):
        member = ready_as(variant)
        out = feed(member, DAY, dip_path({76: 5}))  # entry bar 14:49, fill 14:50
        assert entries(out) == buy_at(hm(14, 49))
        assert sells(hold(member, hm(14, 50), hm(15, 4))) == [hm(15, 4)]
        for minute in range(hm(15, 5), hm(15, 30)):  # flat after the 15:05 fill
            got = call(member, DAY, minute, mes_bar=mes(DAY, minute, 20000 - 80),
                       mgc_bar=mgc(DAY, minute))
            assert got == [], (variant, minute)


def test_no_entry_from_a_view_after_1454() -> None:
    member = ready()
    feed(member, DAY, dip_path())  # no trigger through 14:54
    for minute in range(hm(14, 55), hm(15, 30)):  # deep MES dips on every later minute
        got = call(member, DAY, minute, mes_bar=mes(DAY, minute, 20000 - 80 - minute % 7),
                   mgc_bar=mgc(DAY, minute))
        assert got == [], minute


def test_no_intent_on_mes_ever() -> None:
    member = ready()
    seen: list[LegIntent] = []
    for i, close in enumerate(dip_path({5: 5})):
        seen += call(member, DAY, end_bar(i), mes_bar=mes(DAY, end_bar(i), close),
                     mgc_bar=mgc(DAY, end_bar(i)))
    for minute in range(end_bar(5) + 1, hm(15, 10)):
        seen += call(member, DAY, minute, mes_bar=mes(DAY, minute), mgc_bar=mgc(DAY, minute),
                     position=1)
    assert len(seen) > 2 and {i.root for i in seen} == {"MGC"}
