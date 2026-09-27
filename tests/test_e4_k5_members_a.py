"""Stage E.4 Part 2, K5 members of MemberCoder-A, part 1: the declarations, the
METALS_FULL_SESSIONS pin, K5-cp1-01, K5-cp2-01 and K5-cp3-01 (reports/stage_e4b_member_specs.md
sections 0-3 and 10). K5-ovr-01 is in tests/test_e4_k5_members_a_ovr.py, which reuses this file's
synthetic kit (adapted from tests/test_e4_k4_members_a.py, not imported from it).

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar). No bar file is read, no
runner is run, and no freeze is written into the repository (the freeze test writes under
tmp_path). Expected clock times are written out as literals per root (gold MGC O 07:20, C 12:30;
copper MHG O 07:10, C 12:00), not derived from the code's own arithmetic.
"""

from __future__ import annotations

import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from data.group_session import load_group_calendar, sha256_file, trade_dates_between
from rules import sessions
from rules.price_limits import HARD_LIMIT_PRODUCTS
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
from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.interface import Bar
from strategy.members.k5 import cp1, cp2, cp3, ovr
from strategy.members.k5._calendar import (
    METALS_FULL_SESSIONS,
    METALS_FULL_SESSIONS_SOURCE,
    METALS_FULL_SESSIONS_SOURCE_SHA256,
)
from strategy.members.k5._port_common import EXPOSURES, exit_if_due, to_ticks
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES, release_calendar, rules_for

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
REPO = Path(__file__).resolve().parents[1]
K5_DIR = REPO / "strategy" / "members" / "k5"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "ovr.py", "_calendar.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3, ovr)
ORDINAL_BASE = MappingProxyType({cp1: 1, cp2: 3, cp3: 5, ovr: 10})  # S0.2 (MGC, then MHG)
BASE_PRICE = MappingProxyType({"MGC": 2000.0, "MHG": 4.5})
Q_C = MappingProxyType({"MGC": 1, "MHG": 2})  # S0.3, checked against the frozen table below
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


# D6's O and C per root (frozen day_session_ct; pinned by a test below), as CT minutes
O_C = MappingProxyType({"MGC": (hm(7, 20), hm(12, 30)), "MHG": (hm(7, 10), hm(12, 0))})
DAY_START, DAY_END = hm(7, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the Globex open of d, CT date d-1

# regular metals trade dates (EC-CAL full sessions, F 15:08)
MON, TUE, WED, THU = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4), date(2025, 6, 5)
HALT_DAY = date(2025, 5, 26)  # Memorial Day: an EC-CAL metals early halt, Topstep F 11:30 CT


def halt_label(day: date) -> str:
    halt = load_group_calendar("metals").early_halt_ct(day)
    assert halt is not None, day
    return halt.strftime("%H:%M")


def make(module: ModuleType, root: str) -> Any:
    return vars(module)[f"make_{root.lower()}"]()


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars: an evening segment [17:00, 17:05) on CT date d-1 and a
    day segment [start, end) on CT date d, flat at the root's base price unless ``paths`` or
    ``evening`` override a minute (tick offsets from the base). ``only`` keeps just those day
    minutes (a sparse day) and drops the evening."""

    trade_date: date
    paths: Mapping[int, Ticks] = field(default_factory=dict)
    evening: Mapping[int, Ticks] = field(default_factory=dict)
    skip: frozenset[int] = frozenset()  # CT minutes of date d with no bar
    evening_skip: frozenset[int] = frozenset()
    instrument_id: int = 777
    evening_id: int | None = None
    ids: Mapping[int, int] = field(default_factory=dict)  # per-minute instrument_id overrides
    halt: str = ""  # early_halt_ct label of CT date d
    evening_halt: str = ""  # early_halt_ct label of CT date d-1
    start: int = DAY_START
    end: int = DAY_END
    only: frozenset[int] | None = None
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this minute


def base_ticks(root: str) -> int:
    return to_ticks(BASE_PRICE[root], product(root).vendor_tick)


def _rows(root: str, trade_day: date, ct_day: date, minutes: Sequence[int],
          paths: Mapping[int, Ticks], skip: frozenset[int], ids: Mapping[int, int],
          default_id: int, halt: str, flatten_from: int | None) -> list[dict]:
    b, fixed = base_ticks(root), product(root).vendor_tick_fixed
    out = []
    for minute in minutes:
        if minute in skip:
            continue
        o, h, lo, c = (b + x for x in paths.get(minute, (0, 0, 0, 0)))
        utc = datetime.combine(ct_day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
        state = sessions.session_state(root, utc)
        synthetic_f = flatten_from is not None and minute >= flatten_from
        out.append({
            "ts_event": int(utc.timestamp()) * NS, "open": o * fixed / PRICE_SCALE,
            "high": h * fixed / PRICE_SCALE, "low": lo * fixed / PRICE_SCALE,
            "close": c * fixed / PRICE_SCALE, "volume": 10,
            "instrument_id": ids.get(minute, default_id), "raw_symbol": f"{root}Q5",
            "trade_date": trade_day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(root: str, days: Sequence[Day]) -> pd.DataFrame:
    rows: list[dict] = []
    for d in days:
        if d.only is None:
            eve_id = d.instrument_id if d.evening_id is None else d.evening_id
            rows += _rows(root, d.trade_date, d.trade_date - timedelta(days=1),
                          range(EVENING_START, EVENING_END), d.evening, d.evening_skip, {},
                          eve_id, d.evening_halt, None)
        minutes = range(d.start, d.end) if d.only is None else sorted(d.only)
        rows += _rows(root, d.trade_date, d.trade_date, minutes, d.paths, d.skip, d.ids,
                      d.instrument_id, d.halt, d.flatten_from)
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, window: Sequence[date] | None = None,
        releases: ReleaseCalendar = NO_RELEASES, rules: StageERules | None = None
        ) -> EngineResult:
    dates = [d.trade_date for d in days] if window is None else list(window)
    if rules is None:
        rules = rules_for(member.legs, dates, releases)
    return run_engine({member.root: frame(member.root, days)}, member, member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure. MGC and MHG are DCB-only
    (not in rules.price_limits.HARD_LIMIT_PRODUCTS), so the real D9.7 exit cannot fire on them;
    this shows what the member does when the engine closes its position on its own."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def ns_at(day: date, minute: int) -> int:
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def forced_limit_rules(member: Any, days: Sequence[Day], at: Sequence[tuple[date, int]]
                       ) -> StageERules:
    return rules_for(member.legs, [d.trade_date for d in days], NO_RELEASES,
                     cls=ForcedLimitRules, force_at_ns=frozenset(ns_at(d, m) for d, m in at))


def blackout_rules(member: Any, days: Sequence[Day], blackout: Sequence[date]) -> StageERules:
    """The real rules with ``blackout`` as roll-blackout dates (D4): bars delivered, opens
    refused by name (engine_roll_blackout)."""
    return StageERules({member.root: leg_inputs(member.root, traded=True)},
                       frozenset(d.trade_date for d in days), frozenset(blackout), NO_RELEASES)


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


def release_at(root: str, day: date, hh: int, mm: int) -> ReleaseCalendar:
    instant = datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC)
    return release_calendar(root, [int(instant.timestamp()) * NS])


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(root: str, ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({root: bar}))


def account_of(root: str, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({root: position}), MappingProxyType({root: pending}),
                             MappingProxyType({root: None}), MappingProxyType({root: 0}))


def bar_at(root: str, day: date, minute: int, offsets: Ticks = (0, 0, 0, 0), *,
           instrument_id: int = 777, halt: time | None = None) -> Bar:
    b = base_ticks(root)
    fixed = product(root).vendor_tick_fixed
    o, h, lo, c = ((b + x) * fixed / PRICE_SCALE for x in offsets)
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, f"{root}Q5", day, False,
               False, halt, False, False, 0, False)


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k5/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K5") == []


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType) -> None:
    assert EXPOSURES == ("MGC", "MHG")
    for root in EXPOSURES:
        member = make(module, root)
        assert isinstance(member, StageEMember)
        assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
        assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
        assert list(member.trading_windows) == [root]
    assert module.make_mgc() is not module.make_mgc()  # every call starts from fresh state
    for other in ("make_si", "make_sil", "make_pl", "make_gc", "make_hg"):  # S0.1
        assert not hasattr(module, other)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    day_minus_1 = TradingInterval(time(17, 0), time(17, 1), -1, -1)
    expected = {
        "MGC": {cp1: (day_minus_1, TradingInterval(time(7, 49), time(7, 50)),
                      TradingInterval(time(11, 59), time(12, 30))),
                cp2: (TradingInterval(time(7, 20), time(15, 8)),),
                cp3: (TradingInterval(time(7, 20), time(12, 30)),),
                ovr: (TradingInterval(time(7, 20), time(13, 20)),)},
        "MHG": {cp1: (day_minus_1, TradingInterval(time(7, 39), time(7, 40)),
                      TradingInterval(time(11, 29), time(12, 0))),
                cp2: (TradingInterval(time(7, 10), time(15, 8)),),
                cp3: (TradingInterval(time(7, 10), time(12, 0)),),
                ovr: (TradingInterval(time(7, 10), time(12, 10)),)}}
    for root in EXPOSURES:
        for module in MODULES:
            assert make(module, root).trading_windows[root] == expected[root][module]


def test_frozen_clock_size_and_ticks_are_the_spec_values() -> None:
    tables = load_frozen_tables()
    assert tables.day_session_ct["MGC"] == (time(7, 20), time(12, 30))
    assert tables.day_session_ct["MHG"] == (time(7, 10), time(12, 0))
    for root in EXPOSURES:
        o, c = O_C[root]
        assert tables.day_session_ct[root] == (time(o // 60, o % 60), time(c // 60, c % 60))
        assert tables.vehicles[root].q_c == Q_C[root]  # MGC 1, MHG 2 (S0.3)
    assert (product("MGC").vendor_tick, product("MHG").vendor_tick) == (Decimal("0.10"),
                                                                        Decimal("0.0005"))
    # MGC and MHG are DCB-only: the real D9.7 exit cannot fire (tests use ForcedLimitRules)
    assert "MGC" not in HARD_LIMIT_PRODUCTS and "MHG" not in HARD_LIMIT_PRODUCTS


def test_the_8_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze (S0.2 ordinals) pass the real freeze code; the
    freeze is written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k5").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k5" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K5_DIR / name, members_dir / "k5" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ORDINAL_BASE[m] + i, m.__name__,
                        f"make_{root.lower()}", (LegSpec(root, True),))
             for m in MODULES for i, root in enumerate(EXPOSURES)]
    write_cluster_freeze("K5", decls, tmp_path)
    freeze = load_cluster_freeze("K5", tmp_path)
    verify_cluster_code(freeze)
    assert len(freeze.members) == 8
    assert freeze.member("K5-cp1-01 MGC").ordinal == 1
    assert freeze.member("K5-cp1-01 MHG").ordinal == 2
    assert freeze.member("K5-cp3-01 MHG").ordinal == 6
    assert freeze.member("K5-ovr-01 MGC").ordinal == 10
    assert freeze.member("K5-ovr-01 MHG").ordinal == 11


def test_prices_become_integer_vendor_ticks() -> None:
    for root in EXPOSURES:
        tick = product(root).vendor_tick
        b = base_ticks(root)
        assert to_ticks(float(b * tick), tick) == b
        assert to_ticks(float((b + 3) * tick), tick) == b + 3
        assert to_ticks(float((b - 7) * tick), tick) == b - 7


@pytest.mark.parametrize("root", EXPOSURES)
def test_a_none_bar_is_no_decision_and_changes_no_state(root: str) -> None:
    for module in MODULES:
        member = make(module, root)
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 19))
        assert member.on_minute(view_of(root, ts, None), account_of(root, Q_C[root])) == ()
        assert member.on_minute(view_of(root, ts, None), account_of(root)) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    bar = bar_at("MGC", TUE, hm(12, 28))
    view = view_of("MGC", bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of("MGC", 1, -1), "MGC", opened, TUE, time(12, 28)) == ()
    assert exit_if_due(view, account_of("MGC", 0, 1), "MGC", opened, TUE, time(12, 28)) == ()
    (intent,) = exit_if_due(view, account_of("MGC", -1), "MGC", opened, TUE, time(12, 28))
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert exit_if_due(view, account_of("MGC", 1), "MGC", opened, TUE, time(12, 29)) == ()


# --------------------------------------------------------- METALS_FULL_SESSIONS pin ----
def test_metals_full_sessions_is_recomputed_from_ec_cal() -> None:
    """The pin: the literal table equals EC-CAL's metals trade dates over the calendar's own
    coverage, 2019-05-01..2026-06-19 (K4-L-13), with no early halt, recomputed here from
    data.group_session, from the same calendar file."""
    cal = load_group_calendar("metals")
    assert tuple(cal.coverage) == (date(2019, 5, 1), date(2026, 6, 19))
    expected = tuple(d.isoformat() for d in trade_dates_between(cal, *cal.coverage)
                     if cal.early_halt_ct(d) is None)
    assert METALS_FULL_SESSIONS == expected
    assert len(METALS_FULL_SESSIONS) == 1784
    assert (METALS_FULL_SESSIONS[0], METALS_FULL_SESSIONS[-1]) == ("2019-05-01", "2026-06-18")
    assert "2019-05-01, 2026-06-19" in METALS_FULL_SESSIONS_SOURCE
    assert METALS_FULL_SESSIONS_SOURCE_SHA256 == sha256_file(REPO / "data/calendars/metals.py")
    assert "load_group_calendar('metals')" in METALS_FULL_SESSIONS_SOURCE
    assert list(METALS_FULL_SESSIONS) == sorted(set(METALS_FULL_SESSIONS))


# the spec's research-window early halts and weekday non-trade dates (specs lines 27-28)
RESEARCH_EARLY_HALTS = ("2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27",
                        "2025-11-28", "2025-12-24", "2026-01-19", "2026-02-16", "2026-05-25",
                        "2026-06-19")
RESEARCH_WEEKDAY_CLOSURES = ("2025-04-18", "2025-12-25", "2026-01-01", "2026-04-03")


@pytest.mark.parametrize("day", RESEARCH_EARLY_HALTS + RESEARCH_WEEKDAY_CLOSURES)
def test_metals_full_sessions_omit_the_research_window_halts_and_closures(day: str) -> None:
    assert day not in METALS_FULL_SESSIONS


@pytest.mark.parametrize(("day", "listed"), [
    ("2025-07-03", True), ("2025-12-23", True), ("2026-06-18", True), ("2025-06-02", True),
    ("2025-07-05", False),  # a Saturday
    # K4-L-13: nothing outside EC-CAL's coverage; the first covered date is listed
    ("2019-04-19", False), ("2019-04-30", False), ("2019-05-01", True), ("2026-06-22", False)])
def test_metals_full_sessions_spot_checks(day: str, listed: bool) -> None:
    assert (day in METALS_FULL_SESSIONS) is listed


# ------------------------------------------------------------------------ K5-cp1-01 ----
# The expected clock per root, as the spec's section 1 writes it (not derived from O and C)
CP1 = MappingProxyType({
    "MGC": {"signal": hm(7, 49), "entry": hm(11, 59), "exit": hm(12, 28),
            "times": ("11:59", "12:00", "12:28", "12:29")},
    "MHG": {"signal": hm(7, 39), "entry": hm(11, 29), "exit": hm(11, 58),
            "times": ("11:29", "11:30", "11:58", "11:59")}})

# 17:00 bar (d-1): open B, close B+10. Signal bar: open B-5, close B+3. D6's s = close(signal) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}


def cp1_day(root: str, day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", {CP1[root]["signal"]: (-5, 3, -5, 3)})
    return Day(day, **kw)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_buys_on_a_positive_signal_with_the_spec_clock(root: str) -> None:
    # MON: the Globex open is Sunday 17:00 CT, the calendar day before d
    entry, entry_fill, exit_, exit_fill = CP1[root]["times"]
    res = run(make(cp1, root), [cp1_day(root, MON)])
    assert fills(res) == trade(MON, entry_fill, exit_fill, "buy")
    assert intents(res) == [(MON, entry, True, None), (MON, exit_, True, None)]
    assert [f.qty for f in res.events(Fill)] == [Q_C[root], Q_C[root]]  # q_c 1 / 2


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_sells_on_a_negative_signal(root: str) -> None:
    # s = close(signal) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)},
              paths={CP1[root]["signal"]: (5, 5, -3, -3)})
    _, entry_fill, _, exit_fill = CP1[root]["times"]
    assert fills(run(make(cp1, root), [day])) == trade(TUE, entry_fill, exit_fill, "sell")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_zero_signal_is_no_trade(root: str) -> None:
    day = cp1_day(root, paths={CP1[root]["signal"]: (-5, 0, -5, 0)})  # close = open(17:00)
    assert intents(run(make(cp1, root), [day])) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_globex_open_bar_is_no_trade_l05(root: str) -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; E.3-L-05 names the 17:00 bar only
    res = run(make(cp1, root), [cp1_day(root, evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_signal_bar_is_no_trade(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(root, skip=frozenset({CP1[root]["signal"]}))])
    assert intents(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06(root: str) -> None:
    evening_differs = cp1_day(root, evening_id=776)
    signal_differs = cp1_day(root, ids={CP1[root]["signal"]: 778})
    assert intents(run(make(cp1, root), [evening_differs])) == []
    assert intents(run(make(cp1, root), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_differs = cp1_day(root, ids={m: 778 for m in range(CP1[root]["entry"], DAY_END)})
    _, entry_fill, _, exit_fill = CP1[root]["times"]
    assert fills(run(make(cp1, root), [entry_differs])) == trade(TUE, entry_fill, exit_fill)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_entry_bar_is_no_trade_l04(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(root, skip=frozenset({CP1[root]["entry"]}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize(("root", "exit_sent", "exit_fill"), [("MGC", "12:29", "12:30"),
                                                              ("MHG", "11:59", "12:00")])
def test_cp1_missing_exit_bar_sends_the_exit_on_the_next_present_bar(
        root: str, exit_sent: str, exit_fill: str) -> None:
    res = run(make(cp1, root), [cp1_day(root, skip=frozenset({CP1[root]["exit"]}))])
    _, entry_fill, _, _ = CP1[root]["times"]
    assert fills(res) == trade(TUE, entry_fill, exit_fill)
    assert intents(res)[-1] == (TUE, exit_sent, True, None)


def test_cp1_a_refused_exit_is_resent_on_the_next_bar() -> None:
    # no MGC bars 12:00..12:27: the entry fills at the 12:28 open, so the 12:28 exit comes 1
    # minute after the fill (engine_min_hold, D9.3b); it is sent again on 12:29, fills at 12:30
    res = run(cp1.make_mgc(), [cp1_day("MGC", skip=frozenset(range(hm(12, 0), hm(12, 28))))])
    assert intents(res) == [(TUE, "11:59", True, None), (TUE, "12:28", False, "engine_min_hold"),
                            (TUE, "12:29", True, None)]
    assert fills(res) == trade(TUE, "12:28", "12:30")


@pytest.mark.parametrize(("root", "hh", "mm", "deferred"), [("MGC", 12, 0, "12:02"),
                                                            ("MHG", 11, 30, "11:32")])
def test_cp1_fill_in_the_d95a_guard_waits_two_minutes(root: str, hh: int, mm: int,
                                                      deferred: str) -> None:
    # a release at the entry fill minute: the fill waits for release + 2 min
    res = run(make(cp1, root), [cp1_day(root)], releases=release_at(root, TUE, hh, mm))
    assert fills(res) == trade(TUE, deferred, CP1[root]["times"][3])
    assert res.counters["fill_guard_deferral"] == 2


def test_cp1_a_release_next_to_the_fill_leaves_it_alone() -> None:
    # guard [11:58, 12:00) ends before the 12:00 fill; guard [12:01, 12:03) starts after it
    for hh, mm in ((11, 58), (12, 1)):
        res = run(cp1.make_mgc(), [cp1_day("MGC")], releases=release_at("MGC", TUE, hh, mm))
        assert fills(res) == trade(TUE, "12:00", "12:29")


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp1.make_mgc(), [cp1_day("MGC", flatten_from=hm(12, 15))])
    assert fills(res) == trade(TUE, "12:00", "12:16", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["11:59"]  # the member sends no exit of its own


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [cp1_day(root)]
    member = make(cp1, root)
    force = CP1[root]["entry"] + 11  # 12:10 on MGC, 11:40 on MHG
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, force)]))
    fill_at = f"{(force + 1) // 60:02d}:{(force + 1) % 60:02d}"
    assert fills(res) == trade(TUE, CP1[root]["times"][1], fill_at,
                               exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == [CP1[root]["times"][0]]  # no exit, no second entry


def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry() -> None:
    # 2025-05-26 (Memorial Day): F 11:30. CP1 is a port (S0.8): it emits and the engine refuses
    # (the Globex open is Sunday 05-25 17:00). MGC emits at 11:59, after F; MHG at 11:29, whose
    # fill would come at F itself.
    for root in EXPOSURES:
        day = cp1_day(root, HALT_DAY, halt=halt_label(HALT_DAY))
        res = run(make(cp1, root), [day])
        assert intents(res) == [(HALT_DAY, CP1[root]["times"][0], False,
                                 "engine_flatten_window")]
        assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(cp1.make_mhg(), [cp1_day("MHG", TUE), cp1_day("MHG", WED)])
    assert fills(res) == trade(TUE, "11:30", "11:59") + trade(WED, "11:30", "11:59")


# ------------------------------------------------------------------------ K5-cp2-01 ----
# per root: the OR bars' minutes, the first eligible bar, C, and the entry and exit bars of a
# trigger on the first eligible bar (fill, 75th present bar, its fill), from spec section 2
CP2 = MappingProxyType({
    "MGC": {"or": (hm(7, 20), hm(7, 35)), "first": hm(7, 35), "c": hm(12, 30),
            "times": ("07:35", "07:36", "08:50", "08:51")},
    "MHG": {"or": (hm(7, 10), hm(7, 25)), "first": hm(7, 25), "c": hm(12, 0),
            "times": ("07:25", "07:26", "08:40", "08:41")}})
UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks


def cp2_or(root: str) -> dict[int, Ticks]:
    """OR bars: the one at O+5 has high B+2, the one at O+10 has low B-2 (the others at B)."""
    o = CP2[root]["or"][0]
    return {o + 5: (0, 2, 0, 0), o + 10: (0, 0, -2, 0)}


def cp2_day(root: str, extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**cp2_or(root), **extra}, **kw)


def test_cp2_buffer_literals_are_4_vendor_ticks_k5_l07() -> None:
    assert cp2.RANGE_MINUTES == 15  # OR = [O, O+15) (R-K5-1)
    assert cp2.BUFFER_TICKS == 4
    assert cp2.BUFFER_TICKS * product("MGC").vendor_tick == Decimal("0.40")
    assert cp2.BUFFER_TICKS * product("MHG").vendor_tick == Decimal("0.0020")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    entry, entry_fill, exit_, exit_fill = CP2[root]["times"]
    res = run(make(cp2, root), [cp2_day(root, {CP2[root]["first"]: UP4})])
    assert fills(res) == trade(TUE, entry_fill, exit_fill, "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, entry, True, None), (TUE, exit_, True, None)]
    assert [f.qty for f in res.events(Fill)] == [Q_C[root], Q_C[root]]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_the_opening_range_is_o_to_o_plus_15(root: str) -> None:
    # a bar just before O and the bar at O+15 carry extremes that would widen the range; the
    # bars at O and O+14 are inside it. OR = [O, O+15): the O+15 bar is the first eligible bar.
    lo, hi = CP2[root]["or"]
    inside = {lo: (0, 3, 0, 0), hi - 1: (0, 0, -3, 0)}  # OR_high B+3, OR_low B-3
    before = {lo - 1: (0, 40, -40, 0)}
    res = run(make(cp2, root), [cp2_day(root, {**inside, **before, hi: (0, 7, 0, 7)})])
    assert intents(res)[0] == (TUE, CP2[root]["times"][0], True, None)  # B+7 = OR_high + 4
    res3 = run(make(cp2, root), [cp2_day(root, {**inside, hi: (0, 6, 0, 6)})])
    assert intents(res3) == []  # B+6 = OR_high + 3: no entry
    # the range's end (R-K5-1): the O+14 bar's B-3 low is in the range, so B-7 at O+15 sells and
    # B-6 does not; a 14-minute range (OR_low B-2) would sell at B-6
    sell = run(make(cp2, root), [cp2_day(root, {**inside, hi: (0, 0, -7, -7)})])
    assert fills(sell)[0] == (TUE, CP2[root]["times"][1], "sell", "strategy")
    sell3 = run(make(cp2, root), [cp2_day(root, {**inside, hi: (0, 0, -6, -6)})])
    assert intents(sell3) == []  # B-6 = OR_low - 3: no entry


@pytest.mark.parametrize(("root", "at", "entry", "entry_fill", "exit_fill"), [
    ("MGC", hm(7, 50), "07:50", "07:51", "09:06"), ("MHG", hm(7, 40), "07:40", "07:41", "08:56")])
def test_cp2_the_buffer_is_exactly_four_ticks_either_side(root: str, at: int, entry: str,
                                                          entry_fill: str, exit_fill: str) -> None:
    up3, down3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks beyond: no entry (10 minutes earlier)
    res_up = run(make(cp2, root), [cp2_day(root, {at - 10: up3, at: UP4})])
    res_down = run(make(cp2, root), [cp2_day(root, {at - 10: down3, at: DOWN4})])
    assert fills(res_up) == trade(TUE, entry_fill, exit_fill, "buy")
    assert fills(res_down) == trade(TUE, entry_fill, exit_fill, "sell")
    assert intents(res_up)[0] == intents(res_down)[0] == (TUE, entry, True, None)


def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar() -> None:
    res = run(cp2.make_mgc(), [cp2_day("MGC", {hm(7, 35): UP4}, skip=frozenset({hm(8, 0)}))])
    assert fills(res) == trade(TUE, "07:36", "08:52")
    assert intents(res)[-1] == (TUE, "08:51", True, None)


@pytest.mark.parametrize(("root", "trigger", "entry_fill", "exit_fill"), [
    ("MGC", hm(12, 0), "12:01", "13:16"), ("MHG", hm(11, 30), "11:31", "12:46")])
def test_cp2_has_no_c_minus_2_exit(root: str, trigger: int, entry_fill: str,
                                   exit_fill: str) -> None:
    res = run(make(cp2, root), [cp2_day(root, {trigger: UP4})])
    assert fills(res) == trade(TUE, entry_fill, exit_fill)  # not at C-1 (12:29 / 11:59)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_no_entry_from_c(root: str) -> None:
    c = CP2[root]["c"]  # 12:30 on MGC, 12:00 on MHG
    res = run(make(cp2, root), [cp2_day(root, {c: UP4, c + 5: UP4, c + 60: DOWN4})])
    assert intents(res) == []


@pytest.mark.parametrize(("root", "last", "entry_fill", "exit_fill"), [
    ("MGC", hm(12, 29), "12:30", "13:45"), ("MHG", hm(11, 59), "12:00", "13:15")])
def test_cp2_the_last_eligible_bar_c_minus_1_exits_75_bars_later(
        root: str, last: int, entry_fill: str, exit_fill: str) -> None:
    # the catalog's latest entry fill and latest exit (C lines 358-361)
    res = run(make(cp2, root), [cp2_day(root, {last: UP4})])
    assert fills(res) == trade(TUE, entry_fill, exit_fill)


def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp2.make_mgc(), [cp2_day("MGC", {hm(7, 35): UP4}, flatten_from=hm(8, 20))])
    assert fills(res) == trade(TUE, "07:36", "08:21", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["07:35"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it(root: str) -> None:
    # TUE is not a window date: the first trigger is refused, the second is not sent
    first = CP2[root]["first"]
    res = run(make(cp2, root), [cp2_day(root, {first: UP4, first + 10: UP4})], window=[MON])
    assert intents(res) == [(TUE, CP2[root]["times"][0], False, "engine_not_a_window_date")]


def test_cp2_one_entry_per_trade_date_after_the_exit() -> None:
    res = run(cp2.make_mgc(), [cp2_day("MGC", {hm(7, 35): UP4, hm(9, 0): UP4,
                                               hm(10, 0): DOWN4})])
    assert fills(res) == trade(TUE, "07:36", "08:51")


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    day = cp2_day("MHG", {hm(7, 25): UP4, hm(8, 0): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(7, 10), hm(7, 25))))
    assert intents(run(cp2.make_mhg(), [day])) == []


def test_cp2_the_range_is_taken_from_the_present_bars() -> None:
    # the O+5 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day("MGC", {hm(7, 35): (0, 4, 0, 4)}, skip=frozenset({hm(7, 25)}))
    assert fills(run(cp2.make_mgc(), [day])) == trade(TUE, "07:36", "08:51")
    full = cp2_day("MGC", {hm(7, 35): (0, 4, 0, 4)})
    assert intents(run(cp2.make_mgc(), [full])) == []


def test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day("MGC", {hm(7, 10): (0, 30, -30, 0), hm(7, 35): UP4},
                  evening={hm(17, 0): (0, 30, -30, 0)})
    assert fills(run(cp2.make_mgc(), [day])) == trade(TUE, "07:36", "08:51")


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 07:36 CT: the entry fills at 07:38 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(cp2.make_mgc(), [cp2_day("MGC", {hm(7, 35): UP4})],
              releases=release_at("MGC", TUE, 7, 36))
    assert fills(res) == trade(TUE, "07:38", "08:53")


def test_cp2_a_release_next_to_the_fill_leaves_it_alone() -> None:
    for hh, mm in ((7, 34), (7, 37)):  # guards [07:34, 07:36) and [07:37, 07:39)
        res = run(cp2.make_mgc(), [cp2_day("MGC", {hm(7, 35): UP4})],
                  releases=release_at("MGC", TUE, hh, mm))
        assert fills(res)[0] == (TUE, "07:36", "buy", "strategy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    first = CP2[root]["first"]
    days = [cp2_day(root, {first: UP4, first + 90: UP4, first + 150: DOWN4})]
    member = make(cp2, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, first + 25)]))
    fill_at = f"{(first + 26) // 60:02d}:{(first + 26) % 60:02d}"
    assert fills(res) == trade(TUE, CP2[root]["times"][1], fill_at,
                               exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == [CP2[root]["times"][0]]


def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f() -> None:
    # 2025-05-26 (F 11:30): the port trades; the engine's flatten closes the position at F
    day = cp2_day("MGC", {hm(10, 30): UP4}, HALT_DAY, halt=halt_label(HALT_DAY))
    res = run(cp2.make_mgc(), [day])
    assert intents(res)[0] == (HALT_DAY, "10:30", True, None)
    assert fills(res) == trade(HALT_DAY, "10:31", "11:30", exit_reason="forced_flatten")


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(cp2.make_mhg(), [cp2_day("MHG", {hm(7, 25): UP4}),
                               cp2_day("MHG", {hm(9, 0): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "07:26", "08:41") + trade(WED, "09:01", "10:16", "sell")


# ------------------------------------------------------------------------ K5-cp3-01 ----
# per root: the O bar and entry fill, the C-1 bar, the exit bar and its fill (spec section 3)
CP3 = MappingProxyType({
    "MGC": {"o": hm(7, 20), "c_1": hm(12, 29), "exit": hm(12, 28),
            "times": ("07:20", "07:21", "12:28", "12:29")},
    "MHG": {"o": hm(7, 10), "c_1": hm(11, 59), "exit": hm(11, 58),
            "times": ("07:10", "07:11", "11:58", "11:59")}})


def daily(root: str, high: int, low: int, close: int) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (the C-1 close) = B+close, plus two
    extreme bars OUTSIDE [O, C) (10 minutes before O and at C+15) that must not enter it."""
    o, c = O_C[root]
    return {o - 10: (0, 50, -50, 0), c + 15: (0, 50, -50, 0),
            o + 100: (0, high, 0, 0), o + 160: (0, 0, low, 0),
            c - 1: (0, max(0, close), min(0, close), close)}


def buy_08(root: str) -> dict[int, Ticks]:
    return daily(root, 10, 0, 8)  # CLV = 8/10 = 0.8 exactly


def sell_02(root: str) -> dict[int, Ticks]:
    return daily(root, 10, 0, 2)  # CLV = 2/10 = 0.2 exactly


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_08_buys_on_the_o_bar_and_exits_at_c_minus_2(root: str) -> None:
    entry, entry_fill, exit_, exit_fill = CP3[root]["times"]
    res = run(make(cp3, root), [Day(MON, buy_08(root)), Day(TUE)])
    assert fills(res) == trade(TUE, entry_fill, exit_fill, "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, entry, True, None), (TUE, exit_, True, None)]
    assert [f.qty for f in res.events(Fill)] == [Q_C[root], Q_C[root]]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_02_sells(root: str) -> None:
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    res = run(make(cp3, root), [Day(MON, sell_02(root)), Day(TUE)])
    assert fills(res) == trade(TUE, entry_fill, exit_fill, "sell")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_the_daily_bar_is_o_to_c_with_the_c_minus_1_close(root: str) -> None:
    # the extremes 10 minutes before O and at C+15 are outside the daily bar (else CLV would be
    # 58/100 = 0.58 and no trade); a close at C (not C-1) far below does not change C_d
    _, c = O_C[root]
    paths = {**buy_08(root), c: (0, 0, -30, -30)}
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    assert fills(run(make(cp3, root), [Day(MON, paths), Day(TUE)])) == trade(TUE, entry_fill,
                                                                             exit_fill)


@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(close: int) -> None:
    for root in EXPOSURES:
        res = run(make(cp3, root), [Day(MON, daily(root, 10, 0, close)), Day(TUE)])
        assert intents(res) == []


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_zero_range_is_no_trade(root: str) -> None:
    o, _ = O_C[root]
    flat = {o - 10: (0, 50, -50, 0)}  # the only non-flat bar is outside [O, C)
    assert intents(run(make(cp3, root), [Day(MON, flat), Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(cp3.make_mgc(), [Day(MON, buy_08("MGC")), Day(TUE, sell_02("MGC")), Day(WED)])
    assert fills(res) == trade(TUE, "07:21", "12:29", "buy") + trade(WED, "07:21", "12:29",
                                                                     "sell")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_d_minus_1_is_the_most_recent_complete_day(root: str) -> None:
    # TUE lacks its C-1 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade".
    # TUE's exit, decided on C-2, fills at the next present bar (C)
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    tue = Day(TUE, sell_02(root), skip=frozenset({CP3[root]["c_1"]}))
    res = run(make(cp3, root), [Day(MON, buy_08(root)), tue, Day(WED)])
    c = O_C[root][1]
    at_c = f"{c // 60:02d}:{c % 60:02d}"
    assert fills(res) == trade(TUE, entry_fill, at_c, "buy") + trade(WED, entry_fill, exit_fill,
                                                                     "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, buy_08("MGC"), ids={hm(9, 0): 778})  # one bar in [07:20, 12:30) differs
    res = run(cp3.make_mgc(), [mon, Day(TUE, sell_02("MGC")), Day(WED)])
    assert fills(res) == trade(WED, "07:21", "12:29", "sell")  # TUE: no complete d-1 yet


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_instrument_guard_compares_d_minus_1_with_the_o_bar(root: str) -> None:
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    tue = Day(TUE, buy_08(root), instrument_id=778)
    res = run(make(cp3, root), [Day(MON, buy_08(root)), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, entry_fill, exit_fill, "buy")  # TUE refused by the guard


def test_cp3_the_guard_reads_the_o_bar_only() -> None:
    # TUE's O bar carries MON's id; a bar before O (outside the daily bar, read by no rule)
    # carries another: the entry on TUE's O bar stands
    tue = Day(TUE, ids={hm(7, 15): 778})
    res = run(cp3.make_mgc(), [Day(MON, buy_08("MGC")), tue])
    assert fills(res) == trade(TUE, "07:21", "12:29", "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_missing_o_bar_is_no_trade_and_the_day_is_incomplete(root: str) -> None:
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    tue = Day(TUE, sell_02(root), skip=frozenset({CP3[root]["o"]}))
    res = run(make(cp3, root), [Day(MON, buy_08(root)), tue, Day(WED)])
    assert fills(res) == trade(WED, entry_fill, exit_fill, "buy")  # WED's d-1 is MON


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_early_halt_day_is_not_traded_and_is_incomplete(root: str) -> None:
    # 2025-05-26 (Memorial Day, F 11:30): bars kept to 15:12 so it would be complete but for its
    # halt; the engine would accept an O-bar entry, so the member's own test is what blocks it
    fri, tue = date(2025, 5, 23), date(2025, 5, 27)
    label = halt_label(HALT_DAY)
    days = [Day(fri, buy_08(root)), Day(HALT_DAY, sell_02(root), halt=label),
            Day(tue, evening_halt=label)]
    res = run(make(cp3, root), days)
    assert [i for i in intents(res) if i[0] == HALT_DAY] == []
    _, entry_fill, _, exit_fill = CP3[root]["times"]
    assert fills(res) == trade(tue, entry_fill, exit_fill, "buy")  # d-1 of 05-27 is 05-23


@pytest.mark.parametrize(("root", "exit_sent", "exit_fill"), [("MGC", "12:29", "12:30"),
                                                              ("MHG", "11:59", "12:00")])
def test_cp3_missing_exit_bar_sends_the_exit_on_the_next_present_bar(
        root: str, exit_sent: str, exit_fill: str) -> None:
    res = run(make(cp3, root), [Day(MON, buy_08(root)),
                                Day(TUE, skip=frozenset({CP3[root]["exit"]}))])
    assert fills(res) == trade(TUE, CP3[root]["times"][1], exit_fill)
    assert intents(res)[-1] == (TUE, exit_sent, True, None)


def test_cp3_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    res = run(cp3.make_mhg(), [Day(MON, buy_08("MHG")), Day(TUE)],
              releases=release_at("MHG", TUE, 7, 11))
    assert fills(res) == trade(TUE, "07:13", "11:59")
    beside = run(cp3.make_mhg(), [Day(MON, buy_08("MHG")), Day(TUE)],
                 releases=release_at("MHG", TUE, 7, 9))  # guard [07:09, 07:11)
    assert fills(beside) == trade(TUE, "07:11", "11:59")


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp3.make_mgc(), [Day(MON, buy_08("MGC")), Day(TUE, flatten_from=hm(12, 0))])
    assert fills(res) == trade(TUE, "07:21", "12:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["07:20"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [Day(MON, buy_08(root)), Day(TUE)]
    member = make(cp3, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 30))]))
    assert fills(res) == trade(TUE, CP3[root]["times"][1], "09:31",
                               exit_reason="price_limit_exit")
    assert [i[:2] for i in intents(res)] == [(TUE, CP3[root]["times"][0])]
