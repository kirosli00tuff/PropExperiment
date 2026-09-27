"""Stage E.4 Part 2 K5 members of MemberCoder-B, part 1: the release tables' pin, the declarations
and K5-preauc-01 (reports/stage_e4b_member_specs.md sections 0, 4, 10, 11). K5-pmfix-01 and
K5-fomc-01 are in tests/test_e4_k5_members_b_signal.py, which reuses this file's synthetic kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
direct calls where the engine cannot reach a case (a None bar). The pin tests read the two frozen
JSON sources the tables were generated from (and E.3's K2 table as text); no bar file is read, no
runner is run, and no freeze is written into the repository (the freeze test writes under
tmp_path).
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import (
    MemberDecl,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from screening.stage_e_frozen import load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules, release_calendar_from_dict
from strategy.interface import Bar
from strategy.members.k5 import _releases as tables
from strategy.members.k5 import fomc, pmfix, preauc
from strategy.members.k5._event_common import clock_minute, ct_open_ns, price_ticks
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES, release_calendar, rules_for

CT = ZoneInfo("America/Chicago")
LONDON = ZoneInfo("Europe/London")
NS = 1_000_000_000
ROOT = "MGC"
REPO = Path(__file__).resolve().parents[1]
K5_DIR = REPO / "strategy" / "members" / "k5"
CODER_B_FILES = ("preauc.py", "pmfix.py", "fomc.py", "_event_common.py", "_releases.py")
CALENDAR_JSON = REPO / "reports" / "stage_e2b_release_calendar.json"
CHECK_JSON = REPO / "reports" / "stage_e4b_release_check.json"
K2_RELEASES = REPO / "strategy" / "members" / "k2" / "_releases.py"
GENERATOR = REPO / "reports" / "stage_e4_briefs" / "gen_k5_releases.py"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
CHECK_SHA256 = "0715d01f0ab7f9176a7d559e4f8bde151e656c29271a9a1de22bece3218789b7"
# (module, factory, S0.2 ordinal)
DECLS: tuple[tuple[ModuleType, str, int], ...] = (
    (preauc, "make_mgc", 7), (pmfix, "make_mgc", 8), (fomc, "make_mgc", 9))
BASE_PRICE = 2300.0  # MGC, vendor units


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


DAY_START, DAY_END = hm(3, 0), hm(14, 0)  # the synthetic segment of trade date d, CT date d

# Research-window MGC trade dates (EC-CAL full sessions), table rows pinned below.
NORMAL = date(2025, 6, 4)  # Wednesday: AM 04:30 CT, PM 09:00 CT, not an FOMC date
NEXT = date(2025, 6, 5)  # Thursday, the same
FIVE_HOUR = date(2025, 10, 28)  # Tuesday of the autumn 5-hour week: AM 05:30 CT, PM 10:00 CT
UK_BANK_HOLIDAY = date(2025, 8, 25)  # Summer bank holiday (England and Wales): no auction
PM_NOT_HELD = date(2025, 12, 31)  # announced in advance: AM held, PM not held (section 11)
FOMC_DAY = date(2025, 6, 18)  # an FOMC statement date, 13:00 CT
FOMC_FIVE_HOUR = date(2025, 10, 29)  # an FOMC statement date in the 5-hour week


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic MGC bars on CT date d, [start, end), every bar flat at
    o = h = l = c = the base price plus ``closes[minute]`` ticks."""

    trade_date: date
    closes: Mapping[int, int] = field(default_factory=dict)  # CT minute -> tick offset
    skip: frozenset[int] = frozenset()  # CT minutes of date d with no bar
    ids: Mapping[int, int] = field(default_factory=dict)  # per-minute instrument_id overrides
    instrument_id: int = 777
    halt: str = ""  # early_halt_ct label of CT date d
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this minute
    start: int = DAY_START
    end: int = DAY_END


def base_ticks() -> int:
    return price_ticks(BASE_PRICE, product(ROOT).vendor_tick)


def ns_at(day: date, minute: int) -> int:
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def _rows(d: Day) -> list[dict]:
    b, fixed = base_ticks(), product(ROOT).vendor_tick_fixed
    out = []
    for minute in range(d.start, d.end):
        if minute in d.skip:
            continue
        px = (b + d.closes.get(minute, 0)) * fixed / PRICE_SCALE
        utc = datetime.combine(d.trade_date, time(minute // 60, minute % 60),
                               tzinfo=CT).astimezone(UTC)
        state = sessions.session_state(ROOT, utc)
        synthetic_f = d.flatten_from is not None and minute >= d.flatten_from
        out.append({
            "ts_event": int(utc.timestamp()) * NS, "open": px, "high": px, "low": px,
            "close": px, "volume": 10, "instrument_id": d.ids.get(minute, d.instrument_id),
            "raw_symbol": "MGCQ5", "trade_date": d.trade_date.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": d.halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(days: Sequence[Day]) -> pd.DataFrame:
    rows = [r for d in days for r in _rows(d)]
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, releases: ReleaseCalendar = NO_RELEASES,
        rules: StageERules | None = None) -> EngineResult:
    if rules is None:
        rules = rules_for(member.legs, [d.trade_date for d in days], releases)
    return run_engine({ROOT: frame(days)}, member, member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure. MGC is not in
    rules.price_limits.HARD_LIMIT_PRODUCTS (its CME limits are dynamic circuit breakers only), so
    the real D9.7 exit cannot fire on it; this shows what the member does when the engine closes
    its position on its own (S0.7)."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def forced_limit_rules(member: Any, days: Sequence[Day], at: Sequence[tuple[date, int]]
                       ) -> StageERules:
    return rules_for(member.legs, [d.trade_date for d in days], NO_RELEASES,
                     cls=ForcedLimitRules, force_at_ns=frozenset(ns_at(d, m) for d, m in at))


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def fills(res: EngineResult) -> list[tuple[date, str, str, str]]:
    """(trade date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(f.trade_date, f"{ct(f.fill_ts_ns):%H:%M}", f.side, f.reason)
            for f in res.events(Fill)]


def intents(res: EngineResult) -> list[tuple[date, str, bool, str | None]]:
    """(CT date, the emitting bar's CT hh:mm, accepted, refusal reason) of every intent."""
    out = []
    for r in res.events(IntentRecord):
        bar_open = ct(r.decision_ts_ns - 60 * NS)
        out.append((bar_open.date(), f"{bar_open:%H:%M}", r.accepted,
                    None if r.refusal is None else r.refusal.reason))
    return out


def trade(day: date, entry: str, exit_: str, side: str = "buy",
          exit_reason: str = "strategy") -> list[tuple[date, str, str, str]]:
    other = "sell" if side == "buy" else "buy"
    return [(day, entry, side, "strategy"), (day, exit_, other, exit_reason)]


def decided(day: date, *hhmm: str) -> list[tuple[date, str, bool, None]]:
    """Accepted intents emitted on the bars at ``hhmm`` of CT date ``day``."""
    return [(day, t, True, None) for t in hhmm]


def release_at(day: date, hh: int, mm: int) -> ReleaseCalendar:
    return release_calendar(ROOT, [ns_at(day, hm(hh, mm))])


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({ROOT: bar}))


def account_of(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({ROOT: position}), MappingProxyType({ROOT: pending}),
                             MappingProxyType({ROOT: None}), MappingProxyType({ROOT: 0}))


def bar_at(day: date, minute: int, offset: int = 0, *, instrument_id: int = 777,
           halt: time | None = None) -> Bar:
    px = (base_ticks() + offset) * product(ROOT).vendor_tick_fixed / PRICE_SCALE
    return Bar(ns_at(day, minute), px, px, px, px, 10, instrument_id, "MGCQ5", day, False,
               False, halt, False, False, 0, False)


def state_of(member: Any) -> dict:
    """The member's whole mutable state, its signed-move core's included."""
    core = vars(member).get("_core")
    return {**vars(member), **({} if core is None else {f"core.{k}": v
                                                        for k, v in vars(core).items()})}


# ------------------------------------------------------------------ table pin ----
@cache
def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _t_ct(day: date, hh: int, mm: int) -> str:
    """C10 recomputed here: the CT wall time of the instant at hh:mm Europe/London on day."""
    local = datetime.combine(day, time(hh, mm), tzinfo=LONDON).astimezone(CT)
    assert local.date() == day
    return f"{local:%H:%M}"


def _weekdays(first: str, last: str) -> list[date]:
    day, end, out = date.fromisoformat(first), date.fromisoformat(last), []
    while day <= end:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def _in(day: str, window: Sequence[str]) -> bool:
    return window[0] <= day <= window[1]


SECTION_11_PM_NOT_HELD = (
    "2019-12-24", "2019-12-31", "2020-12-24", "2020-12-31", "2021-12-24", "2021-12-31",
    "2022-12-23", "2022-12-30", "2023-12-22", "2023-12-29", "2024-12-24", "2024-12-31",
    "2025-12-24", "2025-12-31")
SECTION_11_FOMC_IN_WINDOW = (  # C12's list
    "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17")


def test_both_sources_have_the_pinned_sha256() -> None:
    assert _sha(CALENDAR_JSON) == CALENDAR_SHA256 == tables.RELEASE_CALENDAR_SHA256
    assert _sha(CHECK_JSON) == CHECK_SHA256 == tables.RELEASE_CHECK_SHA256
    check = _json(CHECK_JSON)
    assert tuple(check["range"]) == tables.TABLE_RANGE == ("2019-05-01", "2026-06-19")  # K5-L-01
    assert tuple(check["window"]) == tables.RESEARCH_CHECK_WINDOW == ("2025-04-01", "2026-06-19")


def test_scheduled_days_are_weekdays_less_bank_holidays_with_the_checks_instants() -> None:
    """Section 11: 1,863 weekdays less 61 England-and-Wales bank holidays = 1,802 auction days;
    each day's two CT instants recomputed with zoneinfo (C10, K5-L-02) equal the check's row."""
    check = _json(CHECK_JSON)
    weekdays = _weekdays(*tables.TABLE_RANGE)
    holidays = {h["date"] for h in check["uk_bank_holidays"]}
    days = [d for d in weekdays if d.isoformat() not in holidays]
    assert (len(weekdays), len(holidays), len(days)) == (1863, 61, 1802)
    assert all(date.fromisoformat(h).weekday() < 5 for h in holidays)
    rows = check["auction_days"]
    assert [r["date"] for r in rows] == [d.isoformat() for d in days]
    for d, r in zip(days, rows, strict=True):
        assert (r["am_ct"], r["pm_ct"]) == (_t_ct(d, 10, 30), _t_ct(d, 15, 0)), d
        assert r["five_hour_week"] == (r["am_ct"] == "05:30")
    assert check["iba_vs_govuk_crosscheck_issues"] == []  # gov.uk and IBA agree (section 11)


def test_no_auction_days_are_section_11s_14_pm_only_days() -> None:
    check = _json(CHECK_JSON)
    expected = tuple(sorted(
        (r["date"], {(True, False): "PM", (False, True): "AM", (False, False): "both"}[
            (r["am_held"], r["pm_held"])], f"{r['reason']}; LBMA notice {r['notice_date']}")
        for r in check["no_auction_days"]))
    assert expected == tables.NO_AUCTION_DAYS
    assert tuple(d for d, _, _ in tables.NO_AUCTION_DAYS) == SECTION_11_PM_NOT_HELD
    assert {kind for _, kind, _ in tables.NO_AUCTION_DAYS} == {"PM"}
    assert all(r["notice_date"] < r["date"] for r in check["no_auction_days"])  # in advance


def test_gold_am_auctions_keep_every_scheduled_day() -> None:
    check = _json(CHECK_JSON)
    expected = tuple((r["date"], _t_ct(date.fromisoformat(r["date"]), 10, 30))
                     for r in check["auction_days"])
    assert expected == tables.GOLD_AM_AUCTIONS  # no AM no-auction day (section 11)
    assert len(tables.GOLD_AM_AUCTIONS) == 1802
    times = [t for _, t in tables.GOLD_AM_AUCTIONS]
    assert (times.count("04:30"), times.count("05:30")) == (1678, 124)
    window = [row for row in tables.GOLD_AM_AUCTIONS if _in(row[0], tables.RESEARCH_CHECK_WINDOW)]
    assert len(window) == 307 and sum(1 for _, t in window if t == "05:30") == 20
    assert all(d in dict(tables.GOLD_AM_AUCTIONS) for d in SECTION_11_PM_NOT_HELD)


def test_gold_pm_auctions_leave_out_the_14_pm_no_auction_days() -> None:
    check = _json(CHECK_JSON)
    dropped = {d for d, kind, _ in tables.NO_AUCTION_DAYS if kind in ("PM", "both")}
    expected = tuple((r["date"], _t_ct(date.fromisoformat(r["date"]), 15, 0))
                     for r in check["auction_days"] if r["date"] not in dropped)
    assert expected == tables.GOLD_PM_AUCTIONS
    assert len(tables.GOLD_PM_AUCTIONS) == 1802 - 14
    assert {t for _, t in tables.GOLD_PM_AUCTIONS} == {"09:00", "10:00"}
    window = [d for d, _ in tables.GOLD_PM_AUCTIONS if _in(d, tables.RESEARCH_CHECK_WINDOW)]
    assert len(window) == 307 - 2  # 2025-12-24 and 2025-12-31 (section 11)
    assert not {d for d, _, _ in tables.NO_AUCTION_DAYS} & set(dict(tables.GOLD_PM_AUCTIONS))


def test_five_hour_week_dates_are_the_checks_and_c10s() -> None:
    """The 05:30 / 10:00 rows are exactly the checked 5-hour-week weekdays in the range (UK and
    US clocks one hour apart), and both tables move together."""
    check = _json(CHECK_JSON)
    listed = {d for year in check["five_hour_weeks"].values()
              for season in year.values() for d in season}
    am_five = {d for d, t in tables.GOLD_AM_AUCTIONS if t == "05:30"}
    pm_five = {d for d, t in tables.GOLD_PM_AUCTIONS if t == "10:00"}
    assert am_five == {d for d in listed if d in dict(tables.GOLD_AM_AUCTIONS)}
    assert pm_five == am_five - set(SECTION_11_PM_NOT_HELD)
    assert all(v["matches_c10"] for v in check["c10_table_check"].values())


def test_fomc_dates_are_the_calendars_1300_ct_rows_and_equal_e3s_k2_table() -> None:
    rows = [r for r in _json(CALENDAR_JSON)["releases"] if r["release"] == "FOMC"]
    at_1300 = []
    for r in rows:
        local = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).astimezone(CT)
        if f"{local:%H:%M}" == "13:00" and local.date().isoformat() == r["date"]:
            at_1300.append(r["date"])
    assert tuple(sorted(at_1300)) == tables.FOMC_STATEMENT_DATES
    assert len(rows) == len(at_1300) == 57
    k2 = next(ast.literal_eval(node.value) for node in ast.parse(
        K2_RELEASES.read_text(encoding="utf-8")).body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        and node.target.id == "FOMC_STATEMENT_DATES")
    assert tuple(k2) == tables.FOMC_STATEMENT_DATES  # read as text; k2 is not imported
    fomc_check = _json(CHECK_JSON)["fomc"]
    assert fomc_check["equal_to_k2_table"] and fomc_check["differences"] == []
    assert tuple(r["date"] for r in fomc_check["rows"]) == tables.FOMC_STATEMENT_DATES
    window = tuple(d for d in tables.FOMC_STATEMENT_DATES
                   if _in(d, tables.RESEARCH_CHECK_WINDOW))
    assert window == SECTION_11_FOMC_IN_WINDOW == tuple(fomc_check["research_window"])
    assert "2020-03-18" not in tables.FOMC_STATEMENT_DATES  # cancelled in the calendar


def test_the_module_is_exactly_the_generators_output() -> None:
    spec = importlib.util.spec_from_file_location("gen_k5_releases", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    text = gen.build(_json(CALENDAR_JSON), _json(CHECK_JSON))
    assert (K5_DIR / "_releases.py").read_text(encoding="utf-8") == text


def test_no_member_fill_on_any_table_date_meets_the_frozen_calendars_fill_guard() -> None:
    """K5-L-04: the frozen calendar holds no LBMA row, so D9.5a never acts at an auction start;
    its MGC rows (CPI and NFP 07:30, G.17 08:15, FOMC 13:00 CT) leave every nominal fill of the
    three members alone on every table date (a missing bar can still move a fill, S0.7)."""
    frozen = release_calendar_from_dict(_json(CALENDAR_JSON), CALENDAR_SHA256, "frozen")
    mgc = [r for r in _json(CALENDAR_JSON)["releases"] if ROOT in r["products"]]
    assert {r["release"] for r in mgc} == {"CPI", "NFP", "G17", "FOMC"}
    nominal: list[int] = []
    for day, t in tables.GOLD_AM_AUCTIONS:
        d, m = date.fromisoformat(day), clock_minute(t)
        assert not frozen.in_fill_guard(ROOT, ns_at(d, m))  # no row at the auction start
        nominal += [ns_at(d, m - 30), ns_at(d, m - 1)]
    for day, t in tables.GOLD_PM_AUCTIONS:
        d, m = date.fromisoformat(day), clock_minute(t)
        assert not frozen.in_fill_guard(ROOT, ns_at(d, m))
        nominal += [ns_at(d, m + 2), ns_at(d, m + 12)]
    for day in tables.FOMC_STATEMENT_DATES:
        d = date.fromisoformat(day)
        assert frozen.in_fill_guard(ROOT, ns_at(d, hm(13, 0)))  # the statement's guard
        nominal += [ns_at(d, hm(13, 5)), ns_at(d, hm(13, 15))]
    assert len(nominal) == 2 * (1802 + 1788 + 57)
    assert not [ns for ns in nominal if frozen.in_fill_guard(ROOT, ns)]


# ---------------------------------------------------------------- declarations ----
@pytest.mark.parametrize("name", CODER_B_FILES)
def test_every_coder_b_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k5/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K5") == []


@pytest.mark.parametrize("decl", DECLS, ids=lambda d: d[0].MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(decl: tuple) -> None:
    module, factory, _ = decl
    member = vars(module)[factory]()
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} MGC"  # S0.2
    assert member.root == ROOT and member.legs == (LegSpec(ROOT, True),)  # S0.1
    assert list(member.trading_windows) == [ROOT]
    assert module.EXPOSURES == (ROOT,)
    assert vars(module)[factory]() is not member  # every call starts from fresh state
    assert "make_mhg" not in vars(module)  # gold only (specs sections 4-6)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    assert preauc.make_mgc().trading_windows[ROOT] == (
        TradingInterval(time(3, 59), time(4, 30)), TradingInterval(time(4, 59), time(5, 30)))
    assert pmfix.make_mgc().trading_windows[ROOT] == (
        TradingInterval(time(8, 59), time(9, 13)), TradingInterval(time(9, 59), time(10, 13)))
    assert fomc.make_mgc().trading_windows[ROOT] == (TradingInterval(time(12, 59),
                                                                     time(13, 16)),)


def test_size_is_the_frozen_q_c_and_prices_are_integer_ticks() -> None:
    frozen = load_frozen_tables()
    assert frozen.vehicles[ROOT].q_c == 1  # S0.3
    assert product(ROOT).vendor_tick == Decimal("0.10")
    assert price_ticks(2300.1, product(ROOT).vendor_tick) == 23001  # S0.10
    assert price_ticks(2299.9, product(ROOT).vendor_tick) == 22999
    assert ct_open_ns(NORMAL, hm(3, 59)) == ns_at(NORMAL, hm(3, 59))
    assert clock_minute("05:30") == hm(5, 30) and clock_minute(time(13, 4)) == hm(13, 4)


def test_the_3_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """Coder B's declarations (S0.2 ordinals 7-9) pass the real freeze code; the freeze is
    written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k5").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k5" / "__init__.py").write_bytes(b"")
    for name in CODER_B_FILES:
        shutil.copyfile(K5_DIR / name, members_dir / "k5" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} MGC", ordinal, m.__name__, factory,
                        (LegSpec(ROOT, True),)) for m, factory, ordinal in DECLS]
    write_cluster_freeze("K5", decls, tmp_path)
    freeze = load_cluster_freeze("K5", tmp_path)
    verify_cluster_code(freeze)
    assert [(m.label, m.ordinal) for m in freeze.members] == [
        ("K5-preauc-01 MGC", 7), ("K5-pmfix-01 MGC", 8), ("K5-fomc-01 MGC", 9)]


def test_a_member_refuses_an_exposure_it_does_not_trade() -> None:
    for cls in (preauc.PreAuc, pmfix.PmFix, fomc.Fomc):
        for root in ("MHG", "GC", "SI"):
            with pytest.raises(ValueError):
                cls(root)


@pytest.mark.parametrize("module", [preauc, pmfix, fomc], ids=lambda m: m.MEMBER_ID)
def test_a_none_bar_is_no_decision_and_changes_no_state(module: ModuleType) -> None:
    member = module.make_mgc()
    for day, minute in ((NORMAL, hm(3, 59)), (NORMAL, hm(9, 1)), (FOMC_DAY, hm(13, 4))):
        before = state_of(member)
        assert member.on_minute(view_of(ns_at(day, minute), None), account_of()) == ()
        assert member.on_minute(view_of(ns_at(day, minute), None), account_of(-1)) == ()
        assert state_of(member) == before


# --------------------------------------------------------------------- preauc ----
def test_preauc_table_rows_used_by_the_tests() -> None:
    am = dict(tables.GOLD_AM_AUCTIONS)
    assert (am[NORMAL.isoformat()], am[NEXT.isoformat()]) == ("04:30", "04:30")
    assert am[FIVE_HOUR.isoformat()] == "05:30"  # UK on GMT, US on CDT (C10)
    assert am[PM_NOT_HELD.isoformat()] == "04:30"  # the AM auction is held (section 11)
    assert UK_BANK_HOLIDAY.isoformat() not in am
    assert preauc.schedule((("2025-06-04", "04:30"), ("2025-10-28", "05:30"))) == {
        NORMAL: (hm(3, 59), hm(4, 28)), FIVE_HOUR: (hm(4, 59), hm(5, 28))}


def test_preauc_normal_week_sells_at_0400_and_exits_at_0429() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL)])
    assert intents(res) == decided(NORMAL, "03:59", "04:28")
    assert fills(res) == trade(NORMAL, "04:00", "04:29", side="sell")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c MGC = 1


def test_preauc_is_unconditional_whatever_the_prices_do() -> None:
    """K5-L-10: no signal; rising or falling bars before the entry do not change the side."""
    for closes in ({hm(3, 58): -5, hm(3, 59): 5}, {hm(3, 58): 5, hm(3, 59): -5}):
        res = run(preauc.make_mgc(), [Day(NORMAL, closes=closes)])
        assert fills(res) == trade(NORMAL, "04:00", "04:29", side="sell")


def test_preauc_five_hour_week_moves_both_decisions_to_t_0530() -> None:
    res = run(preauc.make_mgc(), [Day(FIVE_HOUR)])
    assert intents(res) == decided(FIVE_HOUR, "04:59", "05:28")  # nothing at 03:59
    assert fills(res) == trade(FIVE_HOUR, "05:00", "05:29", side="sell")


def test_preauc_a_uk_bank_holiday_is_not_traded() -> None:
    res = run(preauc.make_mgc(), [Day(UK_BANK_HOLIDAY)])
    assert intents(res) == [] and fills(res) == []


def test_preauc_a_date_not_in_the_table_is_not_traded() -> None:
    """The same trade date trades with its row and not without it (a dropped event)."""
    without = tuple(row for row in tables.GOLD_AM_AUCTIONS if row[0] != NORMAL.isoformat())
    res = run(preauc.PreAuc(ROOT, am_auctions=without), [Day(NORMAL)])
    assert intents(res) == [] and fills(res) == []
    moved = ((NORMAL.isoformat(), "05:30"),)  # a moved instant moves both decisions
    res = run(preauc.PreAuc(ROOT, am_auctions=moved), [Day(NORMAL)])
    assert fills(res) == trade(NORMAL, "05:00", "05:29", side="sell")


def test_preauc_a_pm_only_no_auction_day_is_traded() -> None:
    """K5-L-03: 2025-12-31's PM auction was cancelled in advance; its AM auction was held."""
    res = run(preauc.make_mgc(), [Day(PM_NOT_HELD)])
    assert fills(res) == trade(PM_NOT_HELD, "04:00", "04:29", side="sell")


def test_preauc_an_early_halt_date_is_not_traded() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL, halt="12:00")])
    assert intents(res) == [] and fills(res) == []


def test_preauc_a_missing_t_minus_31_bar_means_no_trade() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL, skip=frozenset({hm(3, 59)}))])
    assert intents(res) == [] and fills(res) == []  # no late entry on the 04:00 bar


def test_preauc_a_missing_t_minus_2_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL, skip=frozenset({hm(4, 28)}))])
    assert intents(res) == decided(NORMAL, "03:59", "04:29")
    assert fills(res) == trade(NORMAL, "04:00", "04:30", side="sell")
    res = run(preauc.make_mgc(), [Day(NORMAL, skip=frozenset({hm(4, 28), hm(4, 29)}))])
    assert fills(res) == trade(NORMAL, "04:00", "04:31", side="sell")


def test_preauc_a_release_at_the_entry_fill_is_deferred_by_d9_5a() -> None:
    """What the engine's D9.5a guard does to a fill landing in [release, release + 2 min): the
    04:00 entry waits for the first bar at or after 04:02 (a synthetic release at 04:00)."""
    res = run(preauc.make_mgc(), [Day(NORMAL)], releases=release_at(NORMAL, 4, 0))
    assert intents(res) == decided(NORMAL, "03:59", "04:28")
    assert fills(res) == trade(NORMAL, "04:02", "04:29", side="sell")
    assert res.counters["fill_guard_deferral"] == 2


def test_preauc_a_release_at_the_auction_start_leaves_both_fills_alone() -> None:
    """A row at T (04:30) would guard [04:30, 04:32): the exit fills at 04:29, before it
    (C line 244); the frozen calendar has no such row anyway (K5-L-04)."""
    res = run(preauc.make_mgc(), [Day(NORMAL)], releases=release_at(NORMAL, 4, 30))
    assert fills(res) == trade(NORMAL, "04:00", "04:29", side="sell")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    frozen = release_calendar_from_dict(_json(CALENDAR_JSON), CALENDAR_SHA256, "frozen")
    res = run(preauc.make_mgc(), [Day(NORMAL), Day(FIVE_HOUR)], releases=frozen)
    assert fills(res) == (trade(NORMAL, "04:00", "04:29", side="sell")
                          + trade(FIVE_HOUR, "05:00", "05:29", side="sell"))
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_preauc_a_release_at_the_exit_fill_defers_the_exit() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL)], releases=release_at(NORMAL, 4, 29))
    assert fills(res) == trade(NORMAL, "04:00", "04:31", side="sell")


def test_preauc_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(preauc.make_mgc(), [Day(NORMAL, flatten_from=hm(4, 15))])
    assert fills(res) == trade(NORMAL, "04:00", "04:16", side="sell",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(NORMAL, "03:59")  # no exit of its own, no re-entry


def test_preauc_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = preauc.make_mgc()
    days = [Day(NORMAL)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(NORMAL, hm(4, 10))]))
    assert fills(res) == trade(NORMAL, "04:00", "04:11", side="sell",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(NORMAL, "03:59")


def test_preauc_one_entry_per_date_across_consecutive_auction_days() -> None:
    days = [Day(NORMAL), Day(NEXT), Day(UK_BANK_HOLIDAY), Day(FIVE_HOUR)]
    res = run(preauc.make_mgc(), days)
    assert fills(res) == (trade(NORMAL, "04:00", "04:29", side="sell")
                          + trade(NEXT, "04:00", "04:29", side="sell")
                          + trade(FIVE_HOUR, "05:00", "05:29", side="sell"))


def test_preauc_direct_calls_no_entry_while_pending_or_holding() -> None:
    member = preauc.make_mgc()
    entry = bar_at(NORMAL, hm(3, 59))
    assert member.on_minute(view_of(entry.ts_event_ns, entry), account_of(pending=-1)) == ()
    other = preauc.make_mgc()
    first = other.on_minute(view_of(entry.ts_event_ns, entry), account_of())
    assert [(i.side, i.quantity) for i in first] == [("sell", 1)]
    again = other.on_minute(view_of(entry.ts_event_ns, entry), account_of())
    assert again == ()  # one chance per trade date
    exit_bar = bar_at(NORMAL, hm(4, 28))
    out = other.on_minute(view_of(exit_bar.ts_event_ns, exit_bar), account_of(-1, pending=1))
    assert out == ()  # an exit is already pending
