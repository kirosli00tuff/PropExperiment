"""Stage E.6 K7 members of MemberCoder-B, part 1: the calendar tables' pins, the declarations and
K7-expiry-01 (reports/stage_e6_member_specs.md sections 0, 4, 8 and lead ruling R-1b-1).
K7-rev2h-01 and K7-montrend-01 are in tests/test_k7_members_events_rev2h.py and
tests/test_k7_members_events_montrend.py, which reuse this file's synthetic kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
direct calls where the engine cannot reach a case (a None bar, a position across an instrument
change). The pin tests recompute every table from its sources (EC-CAL, rules/sessions.py, the two
Databento condition files, the E.4c and E.6 checks); no bar file is read, no runner is run, and no
freeze is written into the repository (the freeze test writes under tmp_path).
"""

from __future__ import annotations

import ast
import calendar
import hashlib
import importlib.util
import json
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from data.group_session import load_group_calendar, trade_dates_between
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
from screening.stage_e_rules import StageERules
from strategy.interface import Bar
from strategy.members.k7 import _calendar as cal_tables
from strategy.members.k7 import _event_common as common
from strategy.members.k7 import expiry, montrend, rev2h
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES, rules_for

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
REPO = Path(__file__).resolve().parents[1]
K7_DIR = REPO / "strategy" / "members" / "k7"
ROOT = "MBT"
CODER_B_FILES = ("_calendar.py", "_event_common.py", "expiry.py", "rev2h.py", "montrend.py")
GENERATOR = REPO / "reports" / "stage_e6_briefs" / "gen_k7_calendar.py"
CONDITION_FILES = (
    "data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json",
    "data/vendor/databento/condition/GLBX.MDP3_2025-04-01_2026-09-16.json")
EW_JSON = REPO / "reports" / "stage_e4c_release_check.json"
E6_CHECK_JSON = REPO / "reports" / "stage_e6_release_check.json"
E2A_BARS_JSON = REPO / "reports" / "stage_e2a_bars.json"
# (module, factory, S0.2 ordinal)
DECLS: tuple[tuple[ModuleType, str, int], ...] = (
    (expiry, "make_mbt", 4), (rev2h, "make_mbt", 5), (montrend, "make_mbt", 6))
BASE_PRICE = 100000.0  # USD per bitcoin; 20000 vendor ticks of 5.00


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


def eve(hh: int, mm: int) -> int:
    """A CT clock of the previous calendar day, as minutes from 00:00 of the trade date's date."""
    return hm(hh, mm) - 24 * 60


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """Synthetic bars of one trade date: one bar per minute in [start, end), minutes counted from
    00:00 CT of ``anchor`` (default: the trade date; negative = earlier CT dates). Every bar is
    o = h = l = c = base + ``closes[minute]`` ticks, except that ``opens[minute]`` sets the open
    alone (high and low then span open and close)."""

    trade_date: date
    start: int
    end: int
    closes: Mapping[int, int] = field(default_factory=dict)
    opens: Mapping[int, int] = field(default_factory=dict)
    skip: frozenset[int] = frozenset()
    ids: Mapping[int, int] = field(default_factory=dict)
    instrument_id: int = 777
    anchor: date | None = None


def base_ticks() -> int:
    return common.to_ticks(BASE_PRICE, product(ROOT).vendor_tick)


def ns_at(day: date, minute: int) -> int:
    """UTC ns of CT clock ``minute`` counted from 00:00 CT of ``day`` (any sign)."""
    on = day + timedelta(days=minute // 1440)
    m = minute % 1440
    utc = datetime.combine(on, time(m // 60, m % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def _px(offset: int) -> float:
    return (base_ticks() + offset) * product(ROOT).vendor_tick_fixed / PRICE_SCALE


def _rows(d: Day) -> list[dict]:
    anchor = d.anchor or d.trade_date
    out = []
    for minute in range(d.start, d.end):
        if minute in d.skip:
            continue
        c = _px(d.closes.get(minute, 0))
        o = _px(d.opens[minute]) if minute in d.opens else c
        ts = ns_at(anchor, minute)
        state = sessions.session_state(ROOT, datetime.fromtimestamp(ts // NS, tz=UTC))
        out.append({
            "ts_event": ts, "open": o, "high": max(o, c), "low": min(o, c), "close": c,
            "volume": 10, "instrument_id": d.ids.get(minute, d.instrument_id),
            "raw_symbol": "MBTM5", "trade_date": d.trade_date.isoformat(),
            "in_flatten_window": bool(state.must_be_flat),
            "in_no_new_positions_window": bool(not state.can_open),
            "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(days: Sequence[Day]) -> pd.DataFrame:
    rows = [r for d in days for r in _rows(d)]
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, rules: StageERules | None = None) -> EngineResult:
    if rules is None:
        rules = rules_for(member.legs, sorted({d.trade_date for d in days}), NO_RELEASES)
    return run_engine({ROOT: frame(days)}, member, member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure: a position the engine
    closes on its own (S0.7, K7-L-07)."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def forced_limit_rules(member: Any, days: Sequence[Day], at: Sequence[int]) -> StageERules:
    return rules_for(member.legs, sorted({d.trade_date for d in days}), NO_RELEASES,
                     cls=ForcedLimitRules, force_at_ns=frozenset(at))


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def fills(res: EngineResult) -> list[tuple[str, str, str]]:
    """(fill bar CT "YYYY-MM-DD HH:MM", side, reason) of every fill."""
    return [(f"{ct(f.fill_ts_ns):%Y-%m-%d %H:%M}", f.side, f.reason) for f in res.events(Fill)]


def intents(res: EngineResult) -> list[tuple[str, bool]]:
    """(the emitting bar's CT "YYYY-MM-DD HH:MM", accepted) of every intent."""
    return [(f"{ct(r.decision_ts_ns - 60 * NS):%Y-%m-%d %H:%M}", r.accepted)
            for r in res.events(IntentRecord)]


def at(day: date, hhmm: str, prev: bool = False) -> str:
    """The CT "YYYY-MM-DD HH:MM" of clock ``hhmm`` on ``day`` (or on day - 1)."""
    on = day - timedelta(days=1) if prev else day
    return f"{on.isoformat()} {hhmm}"


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({ROOT: bar}))


def account_of(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({ROOT: position}), MappingProxyType({ROOT: pending}),
                             MappingProxyType({ROOT: None}), MappingProxyType({ROOT: 0}))


def bar_at(trade_date: date, anchor: date, minute: int, close: int = 0, *, open_: int | None = None,
           instrument_id: int = 777) -> Bar:
    c = _px(close)
    o = c if open_ is None else _px(open_)
    return Bar(ns_at(anchor, minute), o, max(o, c), min(o, c), c, 10, instrument_id, "MBTM5",
               trade_date, False, False, None, False, False, 0, False)


def call(member: Any, bar: Bar, position: int = 0, pending: int = 0) -> tuple:
    return tuple(member.on_minute(view_of(bar.ts_event_ns, bar), account_of(position, pending)))


# ------------------------------------------------------------------ table pins ----
@cache
def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
E2A_DEGRADED_RESEARCH = ("2025-09-17", "2025-09-24", "2025-11-28", "2026-03-16", "2026-04-10")
R_1B_1_DROPS = ("2021-12-30", "2025-12-24")  # lead ruling R-1b-1: dropped, not replaced
# US federal holidays, observed dates (OPM), 2021-2026, and Good Friday: literals, independent of
# the generator's algorithm.
US_OBSERVED = (
    "2021-01-01", "2021-01-18", "2021-02-15", "2021-05-31", "2021-06-18", "2021-07-05",
    "2021-09-06", "2021-10-11", "2021-11-11", "2021-11-25", "2021-12-24", "2021-12-31",
    "2022-01-17", "2022-02-21", "2022-05-30", "2022-06-20", "2022-07-04", "2022-09-05",
    "2022-10-10", "2022-11-11", "2022-11-24", "2022-12-26",
    "2023-01-02", "2023-01-16", "2023-02-20", "2023-05-29", "2023-06-19", "2023-07-04",
    "2023-09-04", "2023-10-09", "2023-11-10", "2023-11-23", "2023-12-25",
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-05-27", "2024-06-19", "2024-07-04",
    "2024-09-02", "2024-10-14", "2024-11-11", "2024-11-28", "2024-12-25",
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-05-26", "2025-06-19", "2025-07-04",
    "2025-09-01", "2025-10-13", "2025-11-11", "2025-11-27", "2025-12-25",
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-07-03",
    "2026-09-07", "2026-10-12", "2026-11-11", "2026-11-26", "2026-12-25")
GOOD_FRIDAYS = ("2021-04-02", "2022-04-15", "2023-04-07", "2024-03-29", "2025-04-18",
                "2026-04-03")
C9_RESEARCH = (  # catalog C9: the research-window dates by the rule (before R-1b-1)
    "2025-04-25", "2025-05-30", "2025-06-27", "2025-07-25", "2025-08-29", "2025-09-26",
    "2025-10-31", "2025-11-28", "2025-12-24", "2026-01-30", "2026-02-27", "2026-03-27",
    "2026-04-24", "2026-05-29")


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k7_calendar", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def test_every_source_file_has_the_pinned_sha256() -> None:
    pinned = dict(cal_tables.SOURCE_SHA256)
    assert set(pinned) == {"data/calendars/crypto.py", "rules/sessions.py", *CONDITION_FILES,
                           "reports/stage_e4c_release_check.json",
                           "reports/stage_e6_release_check.json", "reports/stage_e2a_bars.json"}
    for rel, sha in pinned.items():
        assert _sha(REPO / rel) == sha, rel
    assert cal_tables.EC_CAL_COVERAGE == ("2019-05-01", "2026-06-19")  # K4-L-13
    assert cal_tables.MBTX_MONTHS == ("2021-05", "2026-06")  # K7-L-04


def test_the_module_is_exactly_the_generators_output() -> None:
    texts = _load_generator().build()
    rel = "strategy/members/k7/_calendar.py"
    assert set(texts) == {rel}
    assert (REPO / rel).read_text(encoding="utf-8") == texts[rel]


def test_crypto_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f() -> None:
    """K7-L-02 (K3-L-11): no early halt AND the engine's F = 15:08 CT on CT date d."""
    cal = load_group_calendar("crypto")
    assert tuple(cal.coverage) == (date(2019, 5, 1), date(2026, 6, 19))
    full, early_f = [], []
    for d in trade_dates_between(cal, *cal.coverage):
        if cal.early_halt_ct(d) is not None:
            continue
        (full if sessions.flatten_time_ct(ROOT, d) == time(15, 8) else early_f).append(
            d.isoformat())
    assert tuple(full) == cal_tables.CRYPTO_FULL_SESSIONS and len(full) == 1782
    assert tuple(early_f) == cal_tables.CRYPTO_EARLY_F_DATES == ("2024-07-03",)
    assert "The F test alone removes: 2024-07-03" in (K7_DIR / "_calendar.py").read_text()
    booked = {b.isoformat() for b in cal.booked_forward}
    assert not booked & set(full) and "2026-01-19" in booked  # not trade dates
    window = trade_dates_between(cal, *RESEARCH)
    halts = [d.isoformat() for d in window if cal.early_halt_ct(d) is not None]
    assert halts == ["2025-07-04", "2025-11-28", "2025-12-24", "2026-04-03"]  # spec header
    research_full = [d for d in full if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    assert len(research_full) == len(window) - len(halts)  # the two tests agree there (S0.8)


def test_vendor_degraded_is_the_build_bars_mapping_of_both_condition_files() -> None:
    """K7-L-03: a crypto trade date whose ISO date is a degraded (not "available") UTC date of
    either condition file (data/build_bars.py lines 685-687, 728)."""
    degraded = {str(r["date"]) for rel in CONDITION_FILES for r in _json(REPO / rel)
                if r["condition"] != "available"}
    cal = load_group_calendar("crypto")
    trade = {d.isoformat() for d in trade_dates_between(cal, *cal.coverage)}
    assert tuple(sorted(trade & degraded)) == cal_tables.VENDOR_DEGRADED
    assert (
        "2020-02-27", "2020-02-28", "2020-05-05", "2020-06-30", "2020-07-01", "2024-09-18",
        *E2A_DEGRADED_RESEARCH) == cal_tables.VENDOR_DEGRADED
    research = tuple(d for d in cal_tables.VENDOR_DEGRADED
                     if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat())
    mbt = _json(E2A_BARS_JSON)["products"][ROOT]["degraded"]
    assert research == E2A_DEGRADED_RESEARCH == tuple(mbt["on_research_trade_dates"])


def test_entry_dates_are_full_sessions_less_vendor_degraded() -> None:
    """S0.8: the three new members enter only on these trade dates."""
    full = {date.fromisoformat(d) for d in cal_tables.CRYPTO_FULL_SESSIONS}
    degraded = {date.fromisoformat(d) for d in cal_tables.VENDOR_DEGRADED}
    assert frozenset(full - degraded) == common.ENTRY_DATES
    assert len(common.ENTRY_DATES) == 1782 - 10  # 2025-11-28 is an early halt, not a full date
    assert date(2025, 11, 28) not in full and date(2025, 9, 17) in full


def _rule_mbtx() -> list[tuple[str, str]]:
    """C9 lines 176-182 recomputed: the last Friday of the month, or the preceding day that is
    a business day in both the UK (EC-EW) and the US; T_exp = 16:00 London in CT."""
    ew = {r["date"] for r in _json(EW_JSON)["ec_ew"]}
    us = set(US_OBSERVED) | set(GOOD_FRIDAYS)
    rows = []
    for y in range(2021, 2027):
        for m in range(1, 13):
            if not (2021, 5) <= (y, m) <= (2026, 6):
                continue
            d = date(y, m, calendar.monthrange(y, m)[1])
            while d.weekday() != 4:  # the last Friday
                d -= timedelta(days=1)
            while d.weekday() > 4 or d.isoformat() in ew or d.isoformat() in us:
                d -= timedelta(days=1)
            london = datetime(d.year, d.month, d.day, 16, 0, tzinfo=ZoneInfo("Europe/London"))
            local = london.astimezone(CT)
            assert local.date() == d
            rows.append((d.isoformat(), f"{local:%H:%M}"))
    return rows


def test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops() -> None:
    rule = _rule_mbtx()
    assert len(rule) == 62
    assert tuple(d for d, _ in rule if RESEARCH[0].isoformat() <= d <= "2026-05-31") == C9_RESEARCH
    assert [d for d, t in rule if t == "11:00"] == [
        "2022-03-25", "2024-03-28", "2025-03-28", "2025-10-31", "2026-03-27"]
    assert {"2021-12-30", "2024-03-28", "2025-12-24"} <= {d for d, _ in rule}
    assert tuple(r for r in rule if r[0] not in R_1B_1_DROPS) == cal_tables.MBTX
    assert len(cal_tables.MBTX) == 60
    assert not {d for d, _ in cal_tables.MBTX} & {"2021-12-31", "2025-12-26"}  # not replaced
    # the generator's OPM algorithm gives the literal list
    gen = _load_generator()
    computed = set().union(*(gen.us_federal_holidays(y) for y in range(2021, 2027)))
    in_range = {d.isoformat() for d in computed if date(2021, 1, 1) <= d <= date(2026, 12, 31)}
    assert in_range == set(US_OBSERVED)
    assert {(gen.easter(y) - timedelta(days=2)).isoformat() for y in range(2021, 2027)} == set(
        GOOD_FRIDAYS)
    text = (K7_DIR / "_calendar.py").read_text(encoding="utf-8")
    assert ("R-1b-1: CME's rule now reads 'either', the catalog's 'both' wording gives a non-final"
            in text and "dropped, not replaced" in text)


def test_the_e6_check_agrees_and_mbtx_unverified_is_its_unverifiable_research_rows() -> None:
    check = _json(E6_CHECK_JSON)
    assert [(r["rule_both_date"], r["texp_ct_both"]) for r in
            check["rule_rows_2021_05_2026_06"]] == _rule_mbtx()
    mismatches = check["A_all_cme_points_2021_05_2026_06_record_only"]["mismatches"]
    assert sorted(m["rule_both_date"] for m in mismatches) == list(R_1B_1_DROPS)
    research = check["A_ec_mbtx_research"]["rows"]
    unverified = tuple((r["rule_date"], r["texp_ct"]) for r in research
                       if r["verdict"] == "unverifiable" and not r["after_window_record_only"])
    assert unverified == cal_tables.MBTX_UNVERIFIED and len(unverified) == 10
    assert set(cal_tables.MBTX_UNVERIFIED) <= set(cal_tables.MBTX)
    assert {r["rule_date"] for r in research if r["verdict"] == "drop"} == {"2025-12-24"}


def test_the_expiry_event_set_and_its_clocks() -> None:
    """S0.8 on MBTX: 54 event dates in all; in the research window 12 (2025-11-28 is an early
    halt and vendor-degraded, 2025-12-24 dropped by R-1b-1); T_exp only 10:00 or 11:00."""
    events = expiry.event_schedule()
    mbtx = dict(cal_tables.MBTX)
    assert set(events) == {date.fromisoformat(d) for d in mbtx} & common.ENTRY_DATES
    assert len(events) == 54
    research = sorted(d.isoformat() for d in events if RESEARCH[0] <= d <= RESEARCH[1])
    assert research == [d for d in C9_RESEARCH if d not in ("2025-11-28", "2025-12-24")]
    assert set(mbtx.values()) == set(expiry.T_EXP_SLOTS) == {"10:00", "11:00"}
    for day, (entry_ns, exit_ns) in events.items():
        t = common.clock_minute(mbtx[day.isoformat()])
        assert (entry_ns, exit_ns) == (ns_at(day, t - 301), ns_at(day, t - 2))


# ------------------------------------------------------------------ declarations ----
@pytest.mark.parametrize("name", CODER_B_FILES)
def test_every_coder_b_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k7/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K7") == []


@pytest.mark.parametrize("name", CODER_B_FILES)
def test_no_member_file_uses_a_zone_other_than_the_ct_clock(name: str) -> None:
    """T_exp is a literal table; only the CT clock is a zone at run time, in _event_common."""
    text = (K7_DIR / name).read_text(encoding="utf-8")
    tree = ast.parse(text)
    zones = [ast.unparse(n.args[0]) if n.args else "" for n in ast.walk(tree)
             if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("ZoneInfo")]
    assert zones == (["'America/Chicago'"] if name == "_event_common.py" else [])
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                for a in n.names if n.module == "zoneinfo"}
    assert imported == ({"ZoneInfo"} if name == "_event_common.py" else set())


@pytest.mark.parametrize("decl", DECLS, ids=lambda d: d[0].MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(decl: tuple) -> None:
    module, factory, _ = decl
    member = vars(module)[factory]()
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} MBT"  # S0.2
    assert member.root == ROOT and member.legs == (LegSpec(ROOT, True),)  # S0.1
    assert list(member.trading_windows) == [ROOT]
    assert vars(module)[factory]() is not member  # every call starts from fresh state


def test_trading_windows_are_the_s0_12_intervals() -> None:
    assert expiry.make_mbt().trading_windows[ROOT] == (TradingInterval(time(5, 0), time(11, 0)),)
    assert rev2h.make_mbt().trading_windows[ROOT] == (TradingInterval(time(8, 30), time(14, 31)),)
    assert montrend.make_mbt().trading_windows[ROOT] == (
        TradingInterval(time(17, 0), time(14, 0), -1, 0),)


def test_size_is_the_frozen_q_c_and_prices_are_integer_ticks() -> None:
    tables = load_frozen_tables()
    assert tables.vehicles[ROOT].q_c == 1 and common.leg_facts().q == 1  # S0.3
    assert tables.day_session_ct[ROOT] == (time(8, 30), time(15, 0))  # S0.4
    assert str(common.leg_facts().tick) == "5.00" == str(product(ROOT).vendor_tick)  # S0.10
    assert common.to_ticks(100002.5, product(ROOT).vendor_tick) == 20000  # round half even
    assert common.to_ticks(100007.5, product(ROOT).vendor_tick) == 20002
    assert common.sign(3) == 1 and common.sign(0) == 0 and common.sign(-2) == -1


def test_clock_helpers_accept_exactly_their_ranges() -> None:
    assert common.ct_open_ns(MON, -1440) == ns_at(MON, -1440)  # 00:00 of CT date d-1
    assert common.ct_open_ns(MON, 1439) == ns_at(MON, 1439)
    for bad in (-1441, 1440):
        with pytest.raises(ValueError):
            common.ct_open_ns(MON, bad)
    assert common.clock_of(0) == time(0, 0) and common.clock_of(1439) == time(23, 59)
    for bad in (-1, 1440):
        with pytest.raises(ValueError):
            common.clock_of(bad)
    assert common.clock_minute("10:00") == 600 and common.clock_minute("05:59") == 359
    assert common.clock_minute(time(8, 30)) == 510


def test_the_3_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """Coder B's declarations (S0.2 ordinals 4-6) pass the real freeze code; the freeze is written
    under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k7").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k7" / "__init__.py").write_bytes(b"")
    for name in CODER_B_FILES:
        shutil.copyfile(K7_DIR / name, members_dir / "k7" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} MBT", ordinal, m.__name__, factory,
                        (LegSpec(ROOT, True),)) for m, factory, ordinal in DECLS]
    write_cluster_freeze("K7", decls, tmp_path)
    freeze = load_cluster_freeze("K7", tmp_path)
    verify_cluster_code(freeze)
    assert [(m.label, m.ordinal) for m in freeze.members] == [
        ("K7-expiry-01 MBT", 4), ("K7-rev2h-01 MBT", 5), ("K7-montrend-01 MBT", 6)]


MON = date(2025, 6, 2)
PROBES = (  # (factory, trade date, CT anchor, minute) of a bar each rule acts on
    (expiry.make_mbt, date(2025, 6, 27), date(2025, 6, 27), hm(4, 59)),
    (rev2h.make_mbt, date(2025, 6, 3), date(2025, 6, 3), hm(10, 29)),
    (montrend.make_mbt, MON, MON, eve(17, 59)))


@pytest.mark.parametrize("probe", PROBES, ids=lambda p: p[0].__module__.rsplit(".", 1)[-1])
def test_a_none_bar_is_no_decision_and_changes_no_state(probe: tuple) -> None:
    factory, day, anchor, minute = probe
    member = factory()
    assert tuple(member.on_minute(view_of(ns_at(anchor, minute), None), account_of())) == ()
    assert tuple(member.on_minute(view_of(ns_at(anchor, minute), None), account_of(1))) == ()
    fresh = factory()
    assert repr(member) == repr(fresh)


# ------------------------------------------------------------------ K7-expiry-01 ----
FRI_10 = date(2025, 6, 27)  # MBTX, T_exp 10:00 CT
FRI_11 = date(2025, 10, 31)  # MBTX, T_exp 11:00 CT (UK/US clock mismatch week)


def expiry_day(day: date, **kw: Any) -> Day:
    return Day(day, hm(4, 0), hm(11, 30), **kw)


def test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59() -> None:
    res = run(expiry.make_mbt(), [expiry_day(FRI_10)])
    assert intents(res) == [(at(FRI_10, "04:59"), True), (at(FRI_10, "09:58"), True)]
    assert fills(res) == [(at(FRI_10, "05:00"), "buy", "strategy"),
                          (at(FRI_10, "09:59"), "sell", "strategy")]


def test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59() -> None:
    res = run(expiry.make_mbt(), [expiry_day(FRI_11)])
    assert intents(res) == [(at(FRI_11, "05:59"), True), (at(FRI_11, "10:58"), True)]
    assert fills(res) == [(at(FRI_11, "06:00"), "buy", "strategy"),
                          (at(FRI_11, "10:59"), "sell", "strategy")]


@pytest.mark.parametrize("day,entry", [(FRI_10, hm(4, 59)), (FRI_11, hm(5, 59))])
def test_expiry_a_missing_entry_bar_is_no_trade(day: date, entry: int) -> None:
    res = run(expiry.make_mbt(), [expiry_day(day, skip=frozenset({entry}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("day,exit_bar", [(FRI_10, hm(9, 58)), (FRI_11, hm(10, 58))])
def test_expiry_a_missing_exit_bar_exits_on_the_first_later_bar(day: date, exit_bar: int) -> None:
    skip = frozenset({exit_bar, exit_bar + 1, exit_bar + 2})
    res = run(expiry.make_mbt(), [expiry_day(day, skip=skip)])
    later = f"{(exit_bar + 3) // 60:02d}:{(exit_bar + 3) % 60:02d}"
    after = f"{(exit_bar + 4) // 60:02d}:{(exit_bar + 4) % 60:02d}"
    assert [i for i in intents(res)][1:] == [(at(day, later), True)]
    assert fills(res)[1:] == [(at(day, after), "sell", "strategy")]


def test_expiry_no_exit_before_the_exit_bar() -> None:
    """The bar before the named exit bar (09:57) sends nothing: a mutant that exits one bar
    early fills at 09:58."""
    res = run(expiry.make_mbt(), [expiry_day(FRI_10)])
    assert (at(FRI_10, "09:57"), True) not in intents(res)


@pytest.mark.parametrize("day", [
    date(2025, 6, 20),  # a full Friday that is not an MBTX date
    date(2024, 11, 29),  # an MBTX date with an early halt (13:45): not a full session
    date(2025, 11, 28),  # an MBTX date with an early halt that is also vendor-degraded
    date(2025, 12, 24),  # dropped by R-1b-1 (also an early halt)
    date(2025, 12, 26),  # CME's December 2025 date: not added by R-1b-1
])
def test_expiry_no_trade_off_the_event_set(day: date) -> None:
    res = run(expiry.make_mbt(), [expiry_day(day)])
    assert intents(res) == [] and fills(res) == []


def test_expiry_a_vendor_degraded_mbtx_date_is_not_traded(monkeypatch: pytest.MonkeyPatch
                                                          ) -> None:
    """No MBTX date is degraded alone (2025-11-28 is also a halt), so the wiring is shown by
    removing FRI_10 from the entry dates as VENDOR_DEGRADED would."""
    monkeypatch.setattr(common, "ENTRY_DATES", common.ENTRY_DATES - {FRI_10})
    res = run(expiry.make_mbt(), [expiry_day(FRI_10)])
    assert intents(res) == [] and fills(res) == []


def test_expiry_is_long_only_and_one_entry_per_date() -> None:
    """The entry is a BUY whatever the prices do; after an engine-forced exit (D9.7, queued on the
    07:00 bar) the member sends no exit and makes no second entry."""
    member = expiry.make_mbt()
    days = [expiry_day(FRI_10, closes={hm(4, 59): -40, hm(5, 30): 40})]
    res = run(member, days, rules=forced_limit_rules(member, days, [ns_at(FRI_10, hm(7, 0))]))
    assert fills(res) == [(at(FRI_10, "05:00"), "buy", "strategy"),
                          (at(FRI_10, "07:01"), "sell", "price_limit_exit")]
    assert intents(res) == [(at(FRI_10, "04:59"), True)]


def test_expiry_reads_the_entry_bar_by_trade_date_and_ct_date() -> None:
    """K7-L-01: a bar at 04:59 CT on an MBTX date that carries another trade date (as a
    booked-forward session would) is not the entry bar; a bar at 04:59 of trade date d on
    another CT date is not either."""
    member = expiry.make_mbt()
    assert call(member, bar_at(FRI_10 + timedelta(days=3), FRI_10, hm(4, 59))) == ()
    assert call(member, bar_at(FRI_10, FRI_10 - timedelta(days=1), hm(4, 59))) == ()
    assert len(call(member, bar_at(FRI_10, FRI_10, hm(4, 59)))) == 1


def test_expiry_no_entry_while_pending_and_the_exit_waits_while_pending() -> None:
    member = expiry.make_mbt()
    assert call(member, bar_at(FRI_10, FRI_10, hm(4, 59)), pending=1) == ()
    member = expiry.make_mbt()
    (entry,) = call(member, bar_at(FRI_10, FRI_10, hm(4, 59)))
    assert (entry.side, entry.quantity) == ("buy", 1)
    assert call(member, bar_at(FRI_10, FRI_10, hm(9, 58)), position=1, pending=-1) == ()
    (exit_,) = call(member, bar_at(FRI_10, FRI_10, hm(9, 58)), position=1)
    assert (exit_.side, exit_.quantity) == ("sell", 1)
    (again,) = call(member, bar_at(FRI_10, FRI_10, hm(9, 59)), position=1)  # a refused exit
    assert again.side == "sell"
