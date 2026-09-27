"""Stage E.3 Task 2 (MemberCoder-B): the K2 event members K2-aucpre-01, K2-aucpost-01,
K2-fomcpost-01 and K2-predrift-01 (reports/stage_e3_member_specs.md sections 4-7), and the pin of
their literal release tables (strategy/members/k2/_releases.py, S0.11, L-01, L-02).

Synthetic bars only (tests._stage_e_synthetic.product_frame); every member runs through the real
engine (screening.stage_e_engine.run_engine with StageERules via the canary kit's rules_for).
The only file read is the frozen release calendar reports/stage_e2b_release_calendar.json (and the
C9 XML check result, once the lead drops an auction). No bar file is read.
"""

from __future__ import annotations

import functools
import hashlib
import json
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from data.group_session import load_group_calendar
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import NS_PER_MINUTE, Fill, run_engine
from screening.stage_e_freeze import check_member_source
from screening.stage_e_rules import RELEASE_CALENDAR_PATH, ReleaseCalendar, load_release_calendar
from strategy.interface import Bar
from strategy.members.k2 import _event_common as common
from strategy.members.k2 import _releases, aucpost, aucpre, fomcpost, predrift
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES, release_calendar, rules_for, ts_at
from tests._stage_e_synthetic import product_frame

REPO = Path(__file__).resolve().parents[1]
CALENDAR = REPO / "reports" / "stage_e2b_release_calendar.json"
XML_CHECK = REPO / "reports" / "stage_e3_auction_xml_check.json"
FROZEN_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
MY_FILES = ("_releases", "_event_common", "aucpre", "aucpost", "fomcpost", "predrift")
CT = ZoneInfo("America/Chicago")
ET = ZoneInfo("America/New_York")
TENORS = ("2Y", "5Y", "10Y", "30Y")
ROOTS = ("ZT", "ZF", "ZN", "TN", "ZB", "UB")
FACTORIES = {"ZT": "make_zt", "ZF": "make_zf", "ZN": "make_zn", "TN": "make_tn",
             "ZB": "make_zb", "UB": "make_ub"}
BASE_TICKS = {"ZT": 26368, "ZF": 13824, "ZN": 7040, "TN": 7360, "ZB": 3680, "UB": 3840}
RESEARCH = ("2025-04-01", "2026-06-19")

# Event dates used below (each checked against the tables in test_fixture_dates_are_table_rows).
D_10Y = date(2025, 6, 11)  # 10-year, 13:00 ET close: T_a 12:00 CT
D_10Y_NEXT = date(2025, 7, 9)  # the next 10-year auction
D_30Y = date(2025, 6, 12)  # 30-year, T_a 12:00 CT
D_2Y_1130 = date(2025, 7, 28)  # 2-year, 11:30 ET close: T_a 10:30 CT
D_2Y_5Y = date(2020, 1, 27)  # 2-year at 11:30 ET and 5-year at 13:00 ET on one date
D_5Y_1000 = date(2019, 12, 24)  # the single 10:00 ET close (5-year), an early-halt date
D_FOMC, D_NOT_FOMC = date(2025, 6, 18), date(2025, 6, 17)
D_ISM, D_NOT_ISM = date(2025, 6, 4), date(2025, 6, 5)


# ------------------------------------------------------------------ helpers ----
def hm(ns: int) -> str:
    return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT).strftime("%H:%M")


def minute(hh: int, mm: int) -> int:
    return hh * 60 + mm


def bars(root: str, days: list[date], *, start: tuple[int, int] = (7, 0),
         end: tuple[int, int] = (15, 20), paths: dict | None = None, vol: float = 1.0,
         seed: int = 3) -> pd.DataFrame:
    return product_frame(root, days, seed, start=start, end=end, base_ticks=BASE_TICKS[root],
                         vol_ticks=vol, path_ticks=paths)


def drop(frame: pd.DataFrame, *ts: int) -> pd.DataFrame:
    assert frame["ts_event"].isin(ts).sum() == len(ts)
    return frame[~frame["ts_event"].isin(ts)].reset_index(drop=True)


def with_column(frame: pd.DataFrame, mask: pd.Series, column: str, value: object) -> pd.DataFrame:
    out = frame.copy()
    out.loc[mask, column] = value
    return out


def label_halt(frame: pd.DataFrame, day: date, halt: str) -> pd.DataFrame:
    return with_column(frame, frame["trade_date"] == day.isoformat(), "early_halt_ct", halt)


def run(member: object, frame: pd.DataFrame, days: list[date],
        releases: ReleaseCalendar = NO_RELEASES):
    return run_engine({member.root: frame}, member, member.legs,
                      rules_for(member.legs, days, releases))


def trips(res) -> list[tuple]:
    """(side, qty, decision bar CT, fill bar CT, reason) of every fill, in order."""
    return [(f.side, f.qty, hm(f.decision_ts_ns - NS_PER_MINUTE), hm(f.fill_ts_ns), f.reason)
            for f in res.events(Fill)]


def rt(side: str, dec_in: str, fill_in: str, dec_out: str, fill_out: str,
       out_reason: str = "strategy") -> list[tuple]:
    back = "buy" if side == "sell" else "sell"
    return [(side, 1, dec_in, fill_in, "strategy"), (back, 1, dec_out, fill_out, out_reason)]


def one_bar(root: str, day: date, hh: int, mm: int, *, o: float = 110.0, c: float = 110.0,
            iid: int = 777, halt=None) -> Bar:
    return Bar(ts_at(day, hh, mm), o, max(o, c), min(o, c), c, 1, iid, f"{root}U5", day, False,
               False, halt, False, False, 0, False)


def account(root: str, day: date, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, day, 0, 0, {root: position},
                             {root: pending}, {root: None}, {})


def view(root: str, bar: Bar) -> MinuteView:
    return MinuteView(bar.ts_event_ns, {root: bar})


# ------------------------------------------------------- the release tables ----
@functools.cache
def calendar_file() -> tuple[str, tuple[dict, ...]]:
    data = CALENDAR.read_bytes()
    return hashlib.sha256(data).hexdigest(), tuple(json.loads(data)["releases"])


def local(instant_utc: str, tz: ZoneInfo) -> datetime:
    return datetime.fromisoformat(instant_utc.replace("Z", "+00:00")).astimezone(tz)


def recomputed_tables() -> tuple[set, list, list]:
    """The three tables recomputed from the frozen calendar (brief coder_B; L-14, L-15)."""
    _, rows = calendar_file()
    auctions = set()
    for r in rows:
        if r["release"] != "TREASURY_AUCTION":
            continue
        tenor = r["id"].rsplit("-", 1)[1]
        if tenor not in TENORS:
            continue
        assert f"{tenor[:-1]}-Year" in r["release_name"], r["id"]  # the id suffix is the term
        ct = local(r["instant_utc"], CT)
        assert ct.date().isoformat() == r["date"], r["id"]
        auctions.add((r["date"], tenor, ct.strftime("%H:%M")))
    fomc = sorted(r["date"] for r in rows if r["release"] == "FOMC"
                  and local(r["instant_utc"], CT).strftime("%H:%M") == "13:00")
    ism = sorted(r["date"] for r in rows if r["release"] == "ISM_SERVICES"
                 and local(r["instant_utc"], ET).strftime("%H:%M") == "10:00")
    return auctions, fomc, ism


def tenor_key(text: str) -> str:
    """"2-Year" or "2Y" -> "2Y" (the XML check's tenor field format is its worker's choice)."""
    text = text.strip()
    return f"{int(text.split('-')[0])}Y" if text.endswith("-Year") else text.upper()


def test_release_calendar_is_the_frozen_file() -> None:
    sha, _ = calendar_file()
    assert sha == FROZEN_SHA256 == _releases.RELEASE_CALENDAR_SHA256
    assert RELEASE_CALENDAR_PATH == "reports/stage_e2b_release_calendar.json"


def test_release_tables_are_recomputed_from_the_calendar() -> None:
    auctions, fomc, ism = recomputed_tables()
    dropped = {(d, t) for d, t, _ in _releases.DROPPED_AUCTIONS}
    expected = {a for a in auctions if (a[0], a[1]) not in dropped}
    table = _releases.TREASURY_AUCTIONS
    assert len(table) == len(set(table)) and set(table) == expected
    assert [a[0] for a in table] == sorted(a[0] for a in table)
    assert list(_releases.FOMC_STATEMENT_DATES) == fomc and len(fomc) == 57
    assert list(_releases.ISM_SERVICES_DATES) == ism and len(ism) == 86
    assert {t_a for _, _, t_a in table} <= {"09:00", "10:30", "12:00"}


def test_dropped_auctions_are_exactly_the_disagreements_of_the_xml_check() -> None:
    """L-02 and L-23: every dropped auction is a calendar row marked "disagree" by the C9 XML
    check, every "disagree" record is dropped, and the check covers exactly the table's
    (date, tenor) set. The lead's C9 result: 340 records, all "agree", so nothing is dropped."""
    dropped = _releases.DROPPED_AUCTIONS
    auctions, _, _ = recomputed_tables()
    keys = {(d, t) for d, t, _ in auctions}
    assert len({(d, t) for d, t, _ in dropped}) == len(dropped)
    for d, t, reason in dropped:
        assert (d, t) in keys and reason, (d, t, reason)
        assert not any(a[0] == d and a[1] == t for a in _releases.TREASURY_AUCTIONS)
    assert XML_CHECK.is_file(), (
        f"{XML_CHECK.relative_to(REPO)} does not exist: DROPPED_AUCTIONS ({len(dropped)} entries) "
        "must be checked against the C9 XML check result (L-02, L-23)")
    raw = json.loads(XML_CHECK.read_text(encoding="utf-8"))
    assert raw["schema"] == "stage_e3_auction_xml_check/1"
    status = {(r["auction_date"], tenor_key(r["tenor"])): r["status"] for r in raw["records"]}
    assert len(status) == len(raw["records"])
    assert set(status) == keys  # the check covers every calendar auction of the four tenors
    for d, t, _ in dropped:
        assert status[(d, t)] == "disagree", (d, t, status[(d, t)])
    disagree = {k for k, s in status.items() if s == "disagree"}
    assert disagree == {(d, t) for d, t, _ in dropped}
    assert dropped == ()  # the lead's C9 ruling (L-23): all 340 agree, none dropped


def test_research_window_counts_match_the_catalog() -> None:
    """Spec lines 36-37 (C 323-328, 445-447, 512-514); dropped auctions counted back in."""
    lo, hi = RESEARCH
    rows = [r for r in _releases.TREASURY_AUCTIONS if lo <= r[0] <= hi]
    rows += [(d, t, "dropped") for d, t, _ in _releases.DROPPED_AUCTIONS if lo <= d <= hi]
    assert {t: sum(1 for r in rows if r[1] == t) for t in TENORS} == {
        "2Y": 13, "5Y": 15, "10Y": 15, "30Y": 15}
    assert sum(1 for r in _releases.TREASURY_AUCTIONS
               if lo <= r[0] <= hi and r[1] == "2Y" and r[2] == "10:30") == 3
    fomc = [d for d in _releases.FOMC_STATEMENT_DATES if lo <= d <= hi]
    assert fomc == ["2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29",
                    "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17"]
    assert sum(1 for d in _releases.ISM_SERVICES_DATES if lo <= d <= hi) == 15


def test_member_instants_are_the_harness_release_instants() -> None:
    """L-01: the fill guard and the event cost read the same instants the members trade on."""
    cal = load_release_calendar()
    tenor_roots = {t: [r for r in ROOTS if common.AUCTION_TENOR[r] == t] for t in TENORS}
    for d, tenor, t_a in _releases.TREASURY_AUCTIONS:
        ns = common.ct_open_ns(date.fromisoformat(d), common.clock_minute(t_a))
        for root in tenor_roots[tenor]:
            assert ns in cal.by_root[root], (d, tenor, root)
    for d in _releases.FOMC_STATEMENT_DATES:
        ns = common.ct_open_ns(date.fromisoformat(d), minute(13, 0))
        assert all(ns in cal.by_root[r] for r in ROOTS), d
    for d in _releases.ISM_SERVICES_DATES:
        ns = common.ct_open_ns(date.fromisoformat(d), minute(9, 0))
        assert all(ns in cal.by_root[r] for r in ("ZN", "ZB")), d


def test_fixture_dates_are_table_rows() -> None:
    table = set(_releases.TREASURY_AUCTIONS)
    for row in [(D_10Y, "10Y", "12:00"), (D_10Y_NEXT, "10Y", "12:00"), (D_30Y, "30Y", "12:00"),
                (D_2Y_1130, "2Y", "10:30"), (D_2Y_5Y, "2Y", "10:30"), (D_2Y_5Y, "5Y", "12:00"),
                (D_5Y_1000, "5Y", "09:00")]:
        assert (row[0].isoformat(), row[1], row[2]) in table, row
    assert not any(d == D_10Y.isoformat() and t != "10Y" for d, t, _ in table)
    assert sorted((t, t_a) for d, t, t_a in table if d == D_2Y_1130.isoformat()) == [
        ("2Y", "10:30"), ("5Y", "12:00")]  # 11:30 ET 2-year dates also carry a 5-year auction
    assert D_FOMC.isoformat() in _releases.FOMC_STATEMENT_DATES
    assert D_NOT_FOMC.isoformat() not in _releases.FOMC_STATEMENT_DATES
    assert D_ISM.isoformat() in _releases.ISM_SERVICES_DATES
    assert D_NOT_ISM.isoformat() not in _releases.ISM_SERVICES_DATES
    assert load_group_calendar("rates").early_halt_ct(D_5Y_1000) is not None


# -------------------------------------------------------- declarations ----
WINDOWS = {aucpre: ((7, 29), (12, 0)), aucpost: ((10, 34), (15, 6)),
           fomcpost: ((13, 29), (15, 6)), predrift: ((8, 30), (9, 6))}
IDS = {aucpre: "K2-aucpre-01", aucpost: "K2-aucpost-01", fomcpost: "K2-fomcpost-01",
       predrift: "K2-predrift-01"}


def test_my_member_files_pass_the_freeze_static_check() -> None:
    for name in MY_FILES:
        rel = f"strategy/members/k2/{name}.py"
        assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K2") == []


@pytest.mark.parametrize("module", [aucpre, aucpost, fomcpost, predrift],
                         ids=lambda m: m.__name__.rsplit(".", 1)[1])
def test_factories_names_legs_and_trading_windows(module) -> None:
    traded = ("ZN", "ZB") if module is predrift else ROOTS
    for root in ROOTS:
        factory = getattr(module, FACTORIES[root], None)
        assert (factory is not None) == (root in traded), (module.__name__, root)
        if factory is None:
            continue
        member, again = factory(), factory()
        assert member is not again and isinstance(member, StageEMember)
        assert member.name == f"{IDS[module]} {root}"
        assert member.legs == (LegSpec(root, True),)
        (sh, sm), (eh, em) = WINDOWS[module]
        start, end = datetime(2000, 1, 3, sh, sm).time(), datetime(2000, 1, 3, eh, em).time()
        assert member.trading_windows == {root: (TradingInterval(start, end),)}


def test_members_refuse_an_exposure_they_do_not_trade() -> None:
    with pytest.raises(ValueError):
        predrift.PreDrift("ZT")
    for cls in (aucpre.AucPre, aucpost.AucPost, fomcpost.FomcPost):
        with pytest.raises(ValueError):
            cls("MES")


def test_auction_schedules_follow_the_tenor_map() -> None:
    sched = {r: aucpre.AucPre(r)._core.schedule for r in ROOTS}
    assert sched["ZN"] == sched["TN"] and sched["ZB"] == sched["UB"]
    assert len({len(s) for s in (sched["ZT"], sched["ZF"], sched["ZN"], sched["ZB"])}) == 4
    assert sched["ZN"][D_10Y] == (minute(12, 0) - 181, minute(12, 0) - 2)
    assert sched["ZT"][D_2Y_1130] == (minute(10, 30) - 181, minute(10, 30) - 2)
    post = aucpost.AucPost("ZT")._core.schedule
    assert post[D_2Y_1130] == (minute(10, 30) + 4, minute(10, 30) + 184)
    assert D_10Y not in sched["ZT"] and D_2Y_1130 not in sched["ZN"]


D_REOPEN_5Y = date(2026, 1, 26)  # L-23: a 2-year note sold; original_security_term 5-Year
D_REOPEN_10Y = date(2019, 11, 5)  # L-23: a 3-year note sold; original_security_term 10-Year


def test_l23_reopenings_are_keyed_by_original_security_term() -> None:
    """L-23: 2026-01-26 is a 5-year event (ZF), not a 2-year one (ZT); 2019-11-05 is a 10-year
    event (ZN, TN), not a 3-year one. Both stay; nothing is re-keyed."""
    table = _releases.TREASURY_AUCTIONS
    assert [r for r in table if r[0] == "2026-01-26"] == [("2026-01-26", "5Y", "12:00")]
    assert [r for r in table if r[0] == "2019-11-05"] == [("2019-11-05", "10Y", "12:00")]
    for module in (aucpre, aucpost):
        assert D_REOPEN_5Y in module.make_zf()._core.schedule
        assert D_REOPEN_5Y not in module.make_zt()._core.schedule
        assert D_REOPEN_10Y in module.make_zn()._core.schedule
        assert D_REOPEN_10Y in module.make_tn()._core.schedule
        assert all(D_REOPEN_10Y not in getattr(module, f)()._core.schedule
                   for f in ("make_zt", "make_zf", "make_zb", "make_ub"))
    days = [D_REOPEN_5Y]
    assert trips(run(aucpre.make_zf(), bars("ZF", days), days)) == rt(
        "sell", "08:59", "09:00", "11:58", "11:59")
    assert trips(run(aucpre.make_zt(), bars("ZT", days), days)) == []
    assert trips(run(aucpost.make_zf(), bars("ZF", days), days)) == rt(
        "buy", "12:04", "12:05", "15:04", "15:05")
    assert trips(run(aucpost.make_zt(), bars("ZT", days), days)) == []


# ------------------------------------------------------ direct unit checks ----
def test_a_none_bar_is_no_decision() -> None:
    member = aucpre.make_zn()
    empty = MinuteView(ts_at(D_10Y, 8, 59), {"ZN": None})
    assert member.on_minute(empty, account("ZN", D_10Y)) == ()


def test_one_entry_per_trade_date_and_none_while_pending() -> None:
    member = aucpre.make_zn()
    entry_bar = one_bar("ZN", D_10Y, 8, 59)
    first = member.on_minute(view("ZN", entry_bar), account("ZN", D_10Y))
    assert [(i.side, i.quantity) for i in first] == [("sell", 1)]
    assert member.on_minute(view("ZN", entry_bar), account("ZN", D_10Y)) == ()
    fresh = aucpre.make_zn()
    assert fresh.on_minute(view("ZN", entry_bar), account("ZN", D_10Y, pending=-1)) == ()


def test_a_refused_exit_is_sent_again_and_a_pending_exit_is_not() -> None:
    member = aucpre.make_zn()
    member.on_minute(view("ZN", one_bar("ZN", D_10Y, 8, 59)), account("ZN", D_10Y))
    before = member.on_minute(view("ZN", one_bar("ZN", D_10Y, 11, 57)),
                              account("ZN", D_10Y, position=-1))
    assert before == ()
    for hh, mm in ((11, 58), (11, 59), (12, 3)):  # refused each time: resent on the next bar
        items = member.on_minute(view("ZN", one_bar("ZN", D_10Y, hh, mm)),
                                 account("ZN", D_10Y, position=-1))
        assert [(i.side, i.quantity) for i in items] == [("buy", 1)]
    pending = member.on_minute(view("ZN", one_bar("ZN", D_10Y, 12, 4)),
                               account("ZN", D_10Y, position=-1, pending=1))
    assert pending == ()


def test_state_resets_on_a_new_trade_date() -> None:
    member = predrift.make_zn()
    member.on_minute(view("ZN", one_bar("ZN", D_ISM, 8, 30, o=110.0)), account("ZN", D_ISM))
    nxt = date(2025, 7, 3)  # the next ISM date: its 08:30 bar is missing
    assert nxt.isoformat() in _releases.ISM_SERVICES_DATES
    items = member.on_minute(view("ZN", one_bar("ZN", nxt, 8, 49, c=111.0)), account("ZN", nxt))
    assert items == ()  # the prior date's 08:30 open is not carried over


# ------------------------------------------------------------- K2-aucpre-01 ----
def test_aucpre_13h_et_close_sells_0859_0900_and_exits_1158_1159() -> None:
    res = run(aucpre.make_zn(), bars("ZN", [D_10Y]), [D_10Y])
    assert trips(res) == rt("sell", "08:59", "09:00", "11:58", "11:59")
    assert all(f.trade_date == D_10Y and f.qty == 1 for f in res.events(Fill))


def test_aucpre_1130_et_close_moves_the_minutes_0729_0730_1028_1029() -> None:
    res = run(aucpre.make_zt(), bars("ZT", [D_2Y_1130]), [D_2Y_1130])
    assert trips(res) == rt("sell", "07:29", "07:30", "10:28", "10:29")


def test_aucpre_each_tenor_takes_its_own_t_a_on_a_two_auction_date() -> None:
    zt = run(aucpre.make_zt(), bars("ZT", [D_2Y_5Y]), [D_2Y_5Y])
    zf = run(aucpre.make_zf(), bars("ZF", [D_2Y_5Y]), [D_2Y_5Y])
    assert trips(zt) == rt("sell", "07:29", "07:30", "10:28", "10:29")
    assert trips(zf) == rt("sell", "08:59", "09:00", "11:58", "11:59")


def test_aucpre_the_wrong_tenor_for_the_root_is_not_traded() -> None:
    assert trips(run(aucpre.make_zt(), bars("ZT", [D_10Y]), [D_10Y])) == []
    assert trips(run(aucpre.make_zn(), bars("ZN", [D_2Y_1130]), [D_2Y_1130])) == []
    assert trips(run(aucpre.make_zn(), bars("ZN", [D_30Y]), [D_30Y])) == []
    assert trips(run(aucpre.make_ub(), bars("UB", [D_30Y]), [D_30Y])) == rt(
        "sell", "08:59", "09:00", "11:58", "11:59")


def test_aucpre_trades_each_event_date_once_and_skips_the_dates_between() -> None:
    days = [D_10Y, D_30Y, D_10Y_NEXT]
    res = run(aucpre.make_tn(), bars("TN", days), days)
    assert [f.trade_date for f in res.events(Fill)] == [D_10Y, D_10Y, D_10Y_NEXT, D_10Y_NEXT]
    assert trips(res) == 2 * rt("sell", "08:59", "09:00", "11:58", "11:59")


def test_aucpre_an_early_halt_date_is_not_traded() -> None:
    """The single 10:00 ET close (5-year, 2019-12-24, T_a 09:00 CT) is an early-halt date: its
    bars carry early_halt_ct 12:15 (EC-CAL), so no trade. With the label removed the same date
    would sell at the 05:59 decision (06:00 fill) and exit at 08:58 (08:59 fill)."""
    halt = load_group_calendar("rates").early_halt_ct(D_5Y_1000).strftime("%H:%M")
    frame = bars("ZF", [D_5Y_1000], start=(5, 0), end=(12, 20))
    assert trips(run(aucpre.make_zf(), label_halt(frame, D_5Y_1000, halt), [D_5Y_1000])) == []
    assert trips(run(aucpre.make_zf(), frame, [D_5Y_1000])) == rt(
        "sell", "05:59", "06:00", "08:58", "08:59")
    regular = label_halt(bars("ZN", [D_10Y]), D_10Y, "12:15")  # a synthetic label, same effect
    assert trips(run(aucpre.make_zn(), regular, [D_10Y])) == []


def test_aucpre_a_missing_entry_decision_bar_means_no_trade() -> None:
    frame = drop(bars("ZN", [D_10Y]), ts_at(D_10Y, 8, 59))
    assert trips(run(aucpre.make_zn(), frame, [D_10Y])) == []


def test_aucpre_a_missing_exit_bar_sends_the_exit_on_the_next_bar() -> None:
    frame = drop(bars("ZN", [D_10Y]), ts_at(D_10Y, 11, 58))
    assert trips(run(aucpre.make_zn(), frame, [D_10Y])) == rt(
        "sell", "08:59", "09:00", "11:59", "12:00")
    frame2 = drop(bars("ZN", [D_10Y]), ts_at(D_10Y, 11, 58), ts_at(D_10Y, 11, 59),
                  ts_at(D_10Y, 12, 0))
    assert trips(run(aucpre.make_zn(), frame2, [D_10Y])) == rt(
        "sell", "08:59", "09:00", "12:01", "12:02")


def test_aucpre_fill_guard_at_t_a_and_a_0730_release_inside_the_window() -> None:
    """D9.5a: a fill landing in [release, release + 2 min) waits for release + 2 min. The regular
    exit fill (T_a - 1) is outside the guard; an exit pushed to T_a by a missing bar waits; a
    07:30 CT release delays the 07:30 entry fill of an 11:30 ET close to 07:32."""
    cal = release_calendar("ZN", [ts_at(D_10Y, 12, 0)])
    res = run(aucpre.make_zn(), bars("ZN", [D_10Y]), [D_10Y], cal)
    assert trips(res) == rt("sell", "08:59", "09:00", "11:58", "11:59")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    late = run(aucpre.make_zn(), drop(bars("ZN", [D_10Y]), ts_at(D_10Y, 11, 58)), [D_10Y], cal)
    assert trips(late) == rt("sell", "08:59", "09:00", "11:59", "12:02")
    assert late.counters["fill_guard_deferral"] == 2
    cal2 = release_calendar("ZT", [ts_at(D_2Y_1130, 7, 30), ts_at(D_2Y_1130, 10, 30)])
    res2 = run(aucpre.make_zt(), bars("ZT", [D_2Y_1130]), [D_2Y_1130], cal2)
    assert trips(res2) == rt("sell", "07:29", "07:32", "10:28", "10:29")
    assert res2.events(Fill)[0].event_window  # D8: the entry pays the event-window cost


def test_aucpre_a_position_open_at_f_is_closed_by_the_engine() -> None:
    """A synthetic F at 10:00 (the flatten flag set from 10:00): the engine flattens at the next
    open and the member neither exits again nor re-enters."""
    frame = bars("ZN", [D_10Y])
    frame = with_column(frame, frame["ts_event"] >= ts_at(D_10Y, 10, 0), "in_flatten_window",
                        True)
    res = run(aucpre.make_zn(), frame, [D_10Y])
    assert trips(res) == rt("sell", "08:59", "09:00", "10:00", "10:01", "forced_flatten")


# ------------------------------------------------------------ K2-aucpost-01 ----
def test_aucpost_13h_et_close_buys_1204_1205_and_exits_1504_1505() -> None:
    res = run(aucpost.make_zb(), bars("ZB", [D_30Y]), [D_30Y])
    assert trips(res) == rt("buy", "12:04", "12:05", "15:04", "15:05")


def test_aucpost_1130_et_close_moves_the_minutes_1034_1035_1334_1335() -> None:
    res = run(aucpost.make_zt(), bars("ZT", [D_2Y_1130]), [D_2Y_1130])
    assert trips(res) == rt("buy", "10:34", "10:35", "13:34", "13:35")


def test_aucpost_fill_guard_at_t_a_does_not_touch_the_t_a_plus_5_fill() -> None:
    cal = release_calendar("ZB", [ts_at(D_30Y, 12, 0)])
    res = run(aucpost.make_zb(), bars("ZB", [D_30Y]), [D_30Y], cal)
    assert trips(res) == rt("buy", "12:04", "12:05", "15:04", "15:05")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    assert res.events(Fill)[0].event_window  # 12:05 is inside [T_a, T_a + 30 min): D8 cost


def test_aucpost_wrong_tenor_missing_entry_and_early_halt_mean_no_trade() -> None:
    assert trips(run(aucpost.make_zf(), bars("ZF", [D_30Y]), [D_30Y])) == []
    frame = drop(bars("ZB", [D_30Y]), ts_at(D_30Y, 12, 4))
    assert trips(run(aucpost.make_zb(), frame, [D_30Y])) == []
    halted = label_halt(bars("ZB", [D_30Y]), D_30Y, "12:15")
    assert trips(run(aucpost.make_zb(), halted, [D_30Y])) == []


def test_aucpost_a_missing_exit_bar_sends_the_exit_on_the_next_bar() -> None:
    frame = drop(bars("ZB", [D_30Y]), ts_at(D_30Y, 15, 4))
    assert trips(run(aucpost.make_zb(), frame, [D_30Y])) == rt(
        "buy", "12:04", "12:05", "15:05", "15:06")


def test_aucpost_missing_bars_up_to_f_leave_the_flatten_to_the_engine() -> None:
    frame = drop(bars("ZB", [D_30Y]), *(ts_at(D_30Y, 15, m) for m in range(4, 8)))
    res = run(aucpost.make_zb(), frame, [D_30Y])
    assert trips(res) == rt("buy", "12:04", "12:05", "15:08", "15:09", "forced_flatten")


# ----------------------------------------------------------- K2-fomcpost-01 ----
def test_fomcpost_buys_1329_1330_and_exits_1504_1505_release_guard_untouched() -> None:
    cal = release_calendar("ZF", [ts_at(D_FOMC, 13, 0)])
    res = run(fomcpost.make_zf(), bars("ZF", [D_FOMC]), [D_FOMC], cal)
    assert trips(res) == rt("buy", "13:29", "13:30", "15:04", "15:05")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    assert not any(f.event_window for f in res.events(Fill))  # 13:30 is outside [13:00, 13:30)


def test_fomcpost_a_non_fomc_date_is_not_traded() -> None:
    days = [D_NOT_FOMC, D_FOMC]
    res = run(fomcpost.make_ub(), bars("UB", days), days)
    assert [f.trade_date for f in res.events(Fill)] == [D_FOMC, D_FOMC]


def test_fomcpost_missing_entry_bar_and_early_halt_mean_no_trade() -> None:
    frame = drop(bars("ZN", [D_FOMC]), ts_at(D_FOMC, 13, 29))
    assert trips(run(fomcpost.make_zn(), frame, [D_FOMC])) == []
    halted = label_halt(bars("ZN", [D_FOMC]), D_FOMC, "12:15")
    assert trips(run(fomcpost.make_zn(), halted, [D_FOMC])) == []


def test_fomcpost_a_missing_exit_bar_sends_the_exit_on_the_next_bar() -> None:
    frame = drop(bars("TN", [D_FOMC]), ts_at(D_FOMC, 15, 4))
    assert trips(run(fomcpost.make_tn(), frame, [D_FOMC])) == rt(
        "buy", "13:29", "13:30", "15:05", "15:06")


def test_fomcpost_missing_bars_up_to_f_leave_the_flatten_to_the_engine() -> None:
    frame = drop(bars("ZT", [D_FOMC]), *(ts_at(D_FOMC, 15, m) for m in range(4, 8)))
    res = run(fomcpost.make_zt(), frame, [D_FOMC])
    assert trips(res) == rt("buy", "13:29", "13:30", "15:08", "15:09", "forced_flatten")


# ----------------------------------------------------------- K2-predrift-01 ----
B = BASE_TICKS["ZN"]
M_0830, M_0849 = minute(8, 30), minute(8, 49)


def drift_paths(day: date, open_0830: int, close_0830: int, open_0849: int, close_0849: int
                ) -> dict:
    return {(day, M_0830): (open_0830, max(open_0830, close_0830), min(open_0830, close_0830),
                            close_0830),
            (day, M_0849): (open_0849, max(open_0849, close_0849), min(open_0849, close_0849),
                            close_0849)}


def predrift_bars(root: str, day: date, paths: dict) -> pd.DataFrame:
    return bars(root, [day], paths=paths, vol=0.0)


def test_predrift_s_is_the_0849_close_minus_the_0830_open_in_ticks() -> None:
    # close 08:49 - open 08:30 = +2 ticks; every other pairing of the two bars' open and close
    # (08:30 close, 08:49 open) gives the opposite sign, so only the rule's pair can buy here
    up = drift_paths(D_ISM, B, B + 5, B - 3, B + 2)
    res = run(predrift.make_zn(), predrift_bars("ZN", D_ISM, up), [D_ISM])
    assert trips(res) == rt("buy", "08:49", "08:50", "09:04", "09:05")
    down = drift_paths(D_ISM, B, B - 5, B + 3, B - 2)  # -2 ticks; the other pairings: +3, +3, +8
    res = run(predrift.make_zn(), predrift_bars("ZN", D_ISM, down), [D_ISM])
    assert trips(res) == rt("sell", "08:49", "08:50", "09:04", "09:05")
    zb = drift_paths(D_ISM, BASE_TICKS["ZB"], BASE_TICKS["ZB"], BASE_TICKS["ZB"],
                     BASE_TICKS["ZB"] + 2)
    res = run(predrift.make_zb(), bars("ZB", [D_ISM], paths=zb, vol=0.0), [D_ISM])
    assert trips(res) == rt("buy", "08:49", "08:50", "09:04", "09:05")


def test_predrift_s_zero_means_no_trade() -> None:
    flat = drift_paths(D_ISM, B, B + 4, B + 4, B)  # the 08:49 close equals the 08:30 open
    assert trips(run(predrift.make_zn(), predrift_bars("ZN", D_ISM, flat), [D_ISM])) == []


def test_predrift_two_instrument_ids_on_the_signal_bars_mean_no_trade() -> None:
    up = drift_paths(D_ISM, B, B, B, B + 3)
    frame = predrift_bars("ZN", D_ISM, up)
    for hh, mm in ((8, 30), (8, 49)):
        spliced = with_column(frame, frame["ts_event"] == ts_at(D_ISM, hh, mm),
                              "instrument_id", 778)
        assert trips(run(predrift.make_zn(), spliced, [D_ISM])) == [], (hh, mm)


def test_predrift_a_missing_0830_or_0849_bar_means_no_trade() -> None:
    up = drift_paths(D_ISM, B, B, B, B + 3)
    for hh, mm in ((8, 30), (8, 49)):
        frame = drop(predrift_bars("ZN", D_ISM, up), ts_at(D_ISM, hh, mm))
        assert trips(run(predrift.make_zn(), frame, [D_ISM])) == [], (hh, mm)


def test_predrift_holds_through_the_0900_release_and_exits_at_0905() -> None:
    cal = release_calendar("ZN", [ts_at(D_ISM, 9, 0)])
    up = drift_paths(D_ISM, B, B, B, B + 3)
    res = run(predrift.make_zn(), predrift_bars("ZN", D_ISM, up), [D_ISM], cal)
    assert trips(res) == rt("buy", "08:49", "08:50", "09:04", "09:05")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    assert [f.event_window for f in res.events(Fill)] == [False, True]  # D8 on the exit


def test_predrift_a_missing_exit_bar_sends_the_exit_on_the_next_bar() -> None:
    up = drift_paths(D_ISM, B, B, B, B + 3)
    frame = drop(predrift_bars("ZN", D_ISM, up), ts_at(D_ISM, 9, 4))
    assert trips(run(predrift.make_zn(), frame, [D_ISM])) == rt(
        "buy", "08:49", "08:50", "09:05", "09:06")


def test_predrift_non_ism_date_and_early_halt_mean_no_trade() -> None:
    up = drift_paths(D_NOT_ISM, B, B, B, B + 3)
    assert trips(run(predrift.make_zn(), predrift_bars("ZN", D_NOT_ISM, up), [D_NOT_ISM])) == []
    halted = label_halt(predrift_bars("ZN", D_ISM, drift_paths(D_ISM, B, B, B, B + 3)), D_ISM,
                        "12:15")
    assert trips(run(predrift.make_zn(), halted, [D_ISM])) == []


def test_predrift_a_position_open_at_f_is_closed_by_the_engine() -> None:
    frame = predrift_bars("ZB", D_ISM, drift_paths(D_ISM, BASE_TICKS["ZB"], BASE_TICKS["ZB"],
                                                     BASE_TICKS["ZB"], BASE_TICKS["ZB"] - 2))
    frame = with_column(frame, frame["ts_event"] >= ts_at(D_ISM, 9, 0), "in_flatten_window",
                        True)
    res = run(predrift.make_zb(), frame, [D_ISM])
    assert trips(res) == rt("sell", "08:49", "08:50", "09:00", "09:01", "forced_flatten")
