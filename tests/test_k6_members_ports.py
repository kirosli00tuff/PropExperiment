"""Stage E.8 K6 ports of MemberCoder-A, part 1: the synthetic kit, the declarations and helpers,
and K6-cp1-01 on ZC, ZW, ZS, ZM, ZL, HE and LE (reports/stage_e8_member_specs.md sections 0, 1
and 9). K6-cp2-01 and K6-cp3-01 are in tests/test_k6_members_ports_cp2.py and
tests/test_k6_members_ports_cp3.py; K6-crushgap-01 is in tests/test_k6_members_crushgap.py. They
reuse this file's kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar, a bar the calendars never
produce). No bar file is read, no bar loader or runner is run, and no freeze is written into the
repository (the freeze test writes under tmp_path).

The D10 grain calendar: trade date d opens with the evening session at 19:00 CT on the calendar
day before d (Sunday 19:00 for a Monday), pauses 07:45-08:30 and closes 13:20 CT on d; a scheduled
late open (2025-11-28, 2025-12-26, 2026-01-02 in the window) has no evening session and opens at
08:30. The livestock calendar is the 08:30-13:05 day session only. Bars carry the early_halt_ct
label of their CT CALENDAR date. The kit builds a grain day as five evening bars [19:00, 19:05)
on CT date d-1, five overnight bars [07:40, 07:45) on CT date d and the day segment
[08:30, 13:20); a livestock day as [08:30, 13:05). Every date used is anchored to EC-CAL by
test_the_synthetic_scenarios_are_ec_cal_facts.
"""

from __future__ import annotations

import math
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

from data.group_session import load_group_calendar, previous_trade_date
from rules import price_limits as pl
from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import (
    MemberDecl,
    check_cluster_sources,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from screening.stage_e_frozen import load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.interface import Bar
from strategy.members.k6 import cp1, cp2, cp3
from strategy.members.k6._port_common import EXPOSURES, exit_if_due, leg_facts, shift, to_ticks
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
K6_DIR = REPO / "strategy" / "members" / "k6"
PORT_FILES = ("cp1.py", "cp2.py", "cp3.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3)
ROOTS = ("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE")  # S0.2's order
GRAIN_ROOTS = ("ZC", "ZW", "ZS", "ZM", "ZL")
LIVESTOCK_ROOTS = ("HE", "LE")
FACTORY = MappingProxyType({r: f"make_{r.lower()}" for r in ROOTS})
ORDINAL = MappingProxyType({(m, r): 7 * i + j + 1 for i, m in enumerate(MODULES)
                            for j, r in enumerate(ROOTS)})  # S0.2 table: 1..21
TICK = MappingProxyType({"ZC": Decimal("0.25"), "ZW": Decimal("0.25"), "ZS": Decimal("0.25"),
                         "ZM": Decimal("0.10"), "ZL": Decimal("0.01"), "HE": Decimal("0.025"),
                         "LE": Decimal("0.025")})
BASE_PRICE = MappingProxyType({"ZC": 450.0, "ZW": 550.0, "ZS": 1050.0, "ZM": 300.0, "ZL": 50.0,
                               "HE": 90.0, "LE": 220.0})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


def is_grain(root: str) -> bool:
    return root in GRAIN_ROOTS


def make(module: ModuleType, root: str) -> Any:
    """The module's zero-argument factory of ``root`` (S0.2)."""
    return getattr(module, FACTORY[root])()


# CT clock of the rule bars per group (grains O 08:30 C 13:15; livestock O 08:30 C 13:00)
ENTRY = MappingProxyType({"grains": "12:44", "livestock": "12:29"})  # CP1 C-31
ENTRY_FILL = MappingProxyType({"grains": "12:45", "livestock": "12:30"})
EXIT = MappingProxyType({"grains": "13:13", "livestock": "12:58"})  # C-2
EXIT_FILL = MappingProxyType({"grains": "13:14", "livestock": "12:59"})
CLOSE_BAR = MappingProxyType({"grains": hm(13, 14), "livestock": hm(12, 59)})  # C-1
C_MIN = MappingProxyType({"grains": hm(13, 15), "livestock": hm(13, 0)})


def grp(root: str) -> str:
    return "grains" if is_grain(root) else "livestock"


EVENING = range(hm(19, 0), hm(19, 5))  # grain evening bars of trade date d on CT date d-1
OVERNIGHT = range(hm(7, 40), hm(7, 45))  # grain bars of trade date d on CT date d before 07:45
GRAIN_DAY = range(hm(8, 30), hm(13, 20))
LIVESTOCK_DAY = range(hm(8, 30), hm(13, 5))

# regular grain and livestock trade dates (EC-CAL: no holiday, F 13:18 / 13:03)
FRI, MON, TUE, WED, THU = (date(2025, 5, 30), date(2025, 6, 2), date(2025, 6, 3),
                           date(2025, 6, 4), date(2025, 6, 5))
# Memorial Day 2025-05-26: a full closure of both groups (Tuesday 05-27 reads Friday 05-23)
FRI_MD, MEMORIAL, TUE_MD = date(2025, 5, 23), date(2025, 5, 26), date(2025, 5, 27)
# early halts 12:05 (grains) on 2025-11-28 (also a grain late open) and 2025-12-24 (livestock
# 12:15); grain late opens (no evening session) 2025-12-26 and 2026-01-02
WED_TG, HALT_TG, MON_TG = date(2025, 11, 26), date(2025, 11, 28), date(2025, 12, 1)
TUE_XMAS, HALT_XMAS, LATE_XMAS = date(2025, 12, 23), date(2025, 12, 24), date(2025, 12, 26)
LATE_NY = date(2026, 1, 2)
REGULAR = (FRI, MON, TUE, WED, THU, FRI_MD, TUE_MD, WED_TG, MON_TG, TUE_XMAS)


def halt_label(group: str, day: date) -> str:
    halt = load_group_calendar(group).early_halt_ct(day)
    return "" if halt is None else halt.strftime("%H:%M")


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars, flat at the base price unless ``paths`` (CT date d) or
    ``evening`` (CT date d-1, grains only) override a minute (tick offsets from the base).
    Grains: evening [19:00, 19:05) on d-1 (none if ``no_evening``), overnight [07:40, 07:45)
    and [08:30, 13:20) on d; livestock: [08:30, 13:05) on d. ``end`` cuts the bars of CT date d
    (an early halt); ``only`` keeps just those minutes of CT date d and drops the evening."""

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
    no_evening: bool = False  # a grain scheduled late open: no bar before 08:30 of d
    end: int | None = None
    only: frozenset[int] | None = None
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this minute


def base_ticks(root: str) -> int:
    return to_ticks(BASE_PRICE[root], product(root).vendor_tick)


def price(root: str, offset: int) -> float:
    """The base price plus ``offset`` vendor ticks, as the engine's float."""
    return (base_ticks(root) + offset) * product(root).vendor_tick_fixed / PRICE_SCALE


def _rows(root: str, trade_day: date, ct_day: date, minutes: Sequence[int],
          paths: Mapping[int, Ticks], skip: frozenset[int], ids: Mapping[int, int],
          default_id: int, halt: str, flatten_from: int | None) -> list[dict]:
    out = []
    for minute in minutes:
        if minute in skip:
            continue
        o, h, lo, c = (price(root, x) for x in paths.get(minute, (0, 0, 0, 0)))
        utc = datetime.combine(ct_day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
        state = sessions.session_state(root, utc)
        synthetic_f = flatten_from is not None and minute >= flatten_from
        out.append({
            "ts_event": int(utc.timestamp()) * NS, "open": o, "high": h, "low": lo, "close": c,
            "volume": 10, "instrument_id": ids.get(minute, default_id),
            "raw_symbol": f"{root}N5", "trade_date": trade_day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def day_minutes(root: str, d: Day) -> list[int]:
    if d.only is not None:
        return sorted(d.only)
    if not is_grain(root):
        minutes = list(LIVESTOCK_DAY)
    else:  # a late open has no session before 08:30 (no evening, no overnight bars)
        minutes = [*([] if d.no_evening else OVERNIGHT), *GRAIN_DAY]
    return [m for m in minutes if d.end is None or m < d.end]


def frame(days: Sequence[Day], root: str) -> pd.DataFrame:
    rows: list[dict] = []
    for d in days:
        if is_grain(root) and d.only is None and not d.no_evening:
            eve_id = d.instrument_id if d.evening_id is None else d.evening_id
            rows += _rows(root, d.trade_date, d.trade_date - timedelta(days=1), EVENING,
                          d.evening, d.evening_skip, {}, eve_id, d.evening_halt, None)
        rows += _rows(root, d.trade_date, d.trade_date, day_minutes(root, d), d.paths, d.skip,
                      d.ids, d.instrument_id, d.halt, d.flatten_from)
    out = pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)
    assert out["ts_event"].is_unique
    return out


REFERENCE = frozenset(range(hm(10, 0), hm(10, 5)))


def with_references(days: Sequence[Day], group: str) -> list[Day]:
    """``days`` plus, for every day whose previous EC-CAL trade date is not among them, that
    date's five bars [10:00, 10:05) of its own CT date (flat, with its early-halt label). Every K6
    root is a hard-limit product: the engine refuses any open without a prior-settlement proxy
    (engine_price_limit_reference_unavailable, D9.7), and any bar of the previous trade date
    gives one (rules/price_limits.settlement_proxy's fallback). No member can act on these
    bars: they hold no first, 08:59, range, 08:30, C-1 or 13:14 bar."""
    cal = load_group_calendar(group)
    have = {d.trade_date for d in days}
    refs = {p for d in days if (p := previous_trade_date(cal, d.trade_date)) not in have}
    extra = [Day(p, only=REFERENCE, halt=halt_label(group, p)) for p in refs if p is not None]
    return sorted([*days, *extra], key=lambda d: d.trade_date)


def run(member: Any, days: Sequence[Day], *, window: Sequence[date] | None = None,
        releases: ReleaseCalendar = NO_RELEASES, rules: StageERules | None = None
        ) -> EngineResult:
    """The real engine on ``days`` (plus their price-limit references) for a one-leg member. The
    window is ``days``' trade dates unless given."""
    dates = [d.trade_date for d in days] if window is None else list(window)
    if rules is None:
        rules = rules_for(member.legs, dates, releases)
    root = member.root
    return run_engine({root: frame(with_references(days, grp(root)), root)}, member,
                      member.legs, rules)


def ns_at(day: date, minute: int) -> int:
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def fills(res: EngineResult) -> list[tuple[date, str, str, str]]:
    """(trade date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(f.trade_date, f"{ct(f.fill_ts_ns):%H:%M}", f.side, f.reason)
            for f in res.events(Fill)]


def fill_qty(res: EngineResult) -> list[int]:
    return [f.qty for f in res.events(Fill)]


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


def stop_offsets(root: str, day: date, settlement_offset: int) -> tuple[int, int]:
    """D9.7's (upper, lower) stop levels on ``day`` as tick offsets from the base, for a prior
    settlement at base + ``settlement_offset`` ticks: the smallest close offset at or above the
    upper level and the largest at or below the lower one (rules.price_limits)."""
    tick = product(root).vendor_tick
    s = Decimal(repr(price(root, settlement_offset)))
    levels = pl.stop_levels(pl.limit_band(root, day, datetime.combine(day, time(10, 0),
                                                                      tzinfo=CT), s), s)
    assert levels.upper is not None and levels.lower is not None
    base = Decimal(base_ticks(root))
    return math.ceil(levels.upper / tick - base), math.floor(levels.lower / tick - base)


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(root: str, ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({root: bar}))


def account_of(root: str, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({root: position}), MappingProxyType({root: pending}),
                             MappingProxyType({root: None}), MappingProxyType({root: 0}))


def bar_at(root: str, day: date, minute: int, offsets: Ticks = (0, 0, 0, 0), *,
           trade_day: date | None = None, instrument_id: int = 777,
           halt: time | None = None) -> Bar:
    """A Bar opening at CT ``minute`` of CT date ``day`` carrying ``trade_day`` (default: day)."""
    o, h, lo, c = (price(root, x) for x in offsets)
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, f"{root}N5",
               day if trade_day is None else trade_day, False, False, halt, False, False, 0,
               False)


def feed(member: Any, bars: Sequence[Bar], position: int = 0) -> list[Any]:
    """Direct calls, in order; returns every intent emitted."""
    out: list[Any] = []
    for bar in bars:
        out += member.on_minute(view_of(member.root, bar.ts_event_ns, bar),
                                account_of(member.root, position))
    return out


# ------------------------------------------------------- the calendar facts the kit uses ----
def test_the_synthetic_scenarios_are_ec_cal_facts() -> None:
    grains, livestock = load_group_calendar("grains"), load_group_calendar("livestock")
    for cal in (grains, livestock):
        assert not cal.booked_forward
        for day in REGULAR:
            assert cal.is_trade_date(day) and cal.early_halt_ct(day) is None, day
        assert not cal.is_trade_date(MEMORIAL)
        assert previous_trade_date(cal, TUE_MD) == FRI_MD
        assert previous_trade_date(cal, MON_TG) == HALT_TG
        assert cal.early_halt_ct(HALT_TG) == time(12, 5)
    for day in REGULAR:
        assert day not in grains.scheduled_late_opens, day
        for root in GRAIN_ROOTS:
            assert sessions.flatten_time_ct(root, day) == time(13, 18), (root, day)
        for root in LIVESTOCK_ROOTS:
            assert sessions.flatten_time_ct(root, day) == time(13, 3), (root, day)
    assert grains.early_halt_ct(HALT_XMAS) == time(12, 5)
    assert livestock.early_halt_ct(HALT_XMAS) == time(12, 15)
    for day in (HALT_TG, LATE_XMAS, LATE_NY):
        assert grains.scheduled_late_opens[day] == time(8, 30), day
        assert day not in livestock.scheduled_late_opens
    for day in (HALT_TG, HALT_XMAS):
        for root in ROOTS:
            assert sessions.flatten_time_ct(root, day) == time(11, 45), (root, day)
    assert [d.weekday() for d in (MON, TUE_MD, MON_TG, LATE_XMAS, LATE_NY)] == [0, 1, 0, 4, 4]


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", PORT_FILES)
def test_every_port_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k6/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K6") == []


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType, root: str) -> None:
    assert EXPOSURES == ROOTS
    member = make(module, root)
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
    assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
    assert list(member.trading_windows) == [root]
    assert make(module, root) is not make(module, root)  # every call starts from fresh state


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_each_port_module_has_exactly_the_seven_factories(module: ModuleType) -> None:
    factories = sorted(n for n in vars(module) if n.startswith("make_"))
    assert factories == sorted(FACTORY.values())


def test_member_ids_are_the_catalog_ids() -> None:
    assert (cp1.MEMBER_ID, cp2.MEMBER_ID, cp3.MEMBER_ID) == ("K6-cp1-01", "K6-cp2-01",
                                                            "K6-cp3-01")


@pytest.mark.parametrize("root", ROOTS)
def test_trading_windows_are_the_s0_12_intervals(root: str) -> None:
    windows = {m: make(m, root).trading_windows[root] for m in MODULES}
    if is_grain(root):
        assert windows[cp1] == (TradingInterval(time(19, 0), time(19, 1), -1, -1),
                                TradingInterval(time(8, 59), time(9, 0)),
                                TradingInterval(time(12, 44), time(13, 15)))
        assert windows[cp2] == (TradingInterval(time(8, 30), time(13, 18)),)
        assert windows[cp3] == (TradingInterval(time(8, 30), time(13, 15)),)
    else:
        assert windows[cp1] == (TradingInterval(time(8, 30), time(8, 31)),
                                TradingInterval(time(8, 59), time(9, 0)),
                                TradingInterval(time(12, 29), time(13, 0)))
        assert windows[cp2] == (TradingInterval(time(8, 30), time(13, 3)),)
        assert windows[cp3] == (TradingInterval(time(8, 30), time(13, 0)),)


@pytest.mark.parametrize("root", ROOTS)
def test_frozen_clock_size_and_tick_per_root(root: str) -> None:
    tables = load_frozen_tables()
    c = time(13, 15) if is_grain(root) else time(13, 0)
    assert tables.day_session_ct[root] == (time(8, 30), c)
    assert tables.vehicles[root].q_c == 1
    assert product(root).vendor_tick == TICK[root]
    assert product(root).group == grp(root)
    facts = leg_facts(root)
    assert (facts.root, facts.group, facts.o, facts.c, facts.q, facts.tick) == (
        root, grp(root), time(8, 30), c, 1, TICK[root])
    assert facts.is_grain == is_grain(root)


def test_cp2_window_ends_are_the_engine_f_of_a_regular_day() -> None:
    for root in ROOTS:
        f = cp2.F_REGULAR_CT[product(root).group]
        assert sessions.flatten_time_ct(root, TUE) == f, root


def test_leg_facts_refuses_a_root_outside_the_cluster() -> None:
    for root in ("MES", "ZN", "GF", "KE", "NG"):
        with pytest.raises(ValueError, match="not a K6 exposure"):
            leg_facts(root)


def test_the_21_port_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze for the ports (S0.2 ordinals 1-21) pass the real
    freeze code; the freeze is written under tmp_path only (never the repository's file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k6").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k6" / "__init__.py").write_bytes(b"")
    for name in PORT_FILES:
        shutil.copyfile(K6_DIR / name, members_dir / "k6" / name)
    check_cluster_sources("K6", tmp_path)
    decls = [MemberDecl(f"{m.MEMBER_ID} {r}", ORDINAL[(m, r)], m.__name__, FACTORY[r],
                        (LegSpec(r, True),)) for m in MODULES for r in ROOTS]
    write_cluster_freeze("K6", decls, tmp_path)
    freeze = load_cluster_freeze("K6", tmp_path)
    verify_cluster_code(freeze)
    labels = [f"{m.MEMBER_ID} {r}" for m in MODULES for r in ROOTS]
    assert [freeze.member(lb).ordinal for lb in labels] == list(range(1, 22))
    assert labels[:7] == [f"K6-cp1-01 {r}" for r in ROOTS]
    assert labels[14] == "K6-cp3-01 ZC" and labels[20] == "K6-cp3-01 LE"


@pytest.mark.parametrize("root", ROOTS)
def test_prices_become_integer_vendor_ticks(root: str) -> None:
    tick = product(root).vendor_tick
    b = base_ticks(root)
    assert b == {"ZC": 1800, "ZW": 2200, "ZS": 4200, "ZM": 3000, "ZL": 5000, "HE": 3600,
                 "LE": 8800}[root]
    for k in (0, 1, 3, -1, -7):
        assert to_ticks(price(root, k), tick) == b + k
    assert to_ticks(float(BASE_PRICE[root] + float(tick) * 0.6), tick) == b + 1
    assert to_ticks(float(BASE_PRICE[root] + float(tick) * 0.4), tick) == b


def test_shift_moves_a_clock_time() -> None:
    assert shift(time(8, 30), 29) == time(8, 59)
    assert shift(time(13, 15), -31) == time(12, 44)
    assert shift(time(13, 0), -2) == time(12, 58)
    assert shift(time(19, 0), 1) == time(19, 1)


@pytest.mark.parametrize("root", ROOTS)
def test_a_none_bar_is_no_decision_and_changes_no_state(root: str) -> None:
    for module in MODULES:
        member = make(module, root)
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 59))
        assert member.on_minute(view_of(root, ts, None), account_of(root, 1)) == ()
        assert member.on_minute(view_of(root, ts, None), account_of(root)) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    root = "ZS"
    bar = bar_at(root, TUE, hm(13, 13))
    view = view_of(root, bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of(root, 1, -1), root, opened, TUE, time(13, 13)) == ()
    assert exit_if_due(view, account_of(root, 0, 1), root, opened, TUE, time(13, 13)) == ()
    assert exit_if_due(view, account_of(root, 0), root, opened, TUE, time(13, 13)) == ()
    (intent,) = exit_if_due(view, account_of(root, -1), root, opened, TUE, time(13, 13))
    assert (intent.side, intent.quantity) == ("buy", 1)
    (intent,) = exit_if_due(view, account_of(root, 2), root, opened, TUE, time(13, 12))
    assert (intent.side, intent.quantity) == ("sell", 2)  # the whole position
    assert exit_if_due(view, account_of(root, 1), root, opened, TUE, time(13, 14)) == ()
    assert exit_if_due(view, account_of(root, 1), root, opened, WED, time(13, 13)) == ()


def test_the_kit_adds_the_price_limit_reference_the_engine_needs() -> None:
    # without a bar of the previous trade date the engine refuses every open (D9.7)
    member = make(cp1, "ZC")
    bare = run_engine({"ZC": frame([cp1_day()], "ZC")}, member, member.legs,
                      rules_for(member.legs, [TUE]))
    assert intents(bare) == [(TUE, "12:44", False, "engine_price_limit_reference_unavailable")]
    (ref, tue) = with_references([cp1_day()], "grains")
    assert (ref.trade_date, ref.only, tue.trade_date) == (MON, REFERENCE, TUE)
    assert len(frame([ref], "ZC")) == 5 and len(frame([ref], "HE")) == 5
    # the reference bars alone make no port act
    for module in MODULES:
        for root in ("ZC", "HE"):
            assert intents(run(make(module, root), [ref])) == []
    (halt_ref, _) = with_references([Day(MON_TG)], "grains")
    assert (halt_ref.trade_date, halt_ref.halt) == (HALT_TG, "12:05")


# ------------------------------------------------------------------------ K6-cp1-01 ----
# grains: 19:00 bar (d-1): open B, close B+10; livestock: 08:30 bar: open B, close B+10.
# 08:59 bar: open B-5, close B+3. D6's s = close(08:59) - open(first) = +3 (buy); close - close
# would be -7 and open - open -5 (both sell).
FIRST_BUY = (0, 10, 0, 10)
SIGNAL_BUY = (-5, 3, -5, 3)


def cp1_day(day: date = TUE, root: str = "ZC", **kw: Any) -> Day:
    if is_grain(root):
        kw.setdefault("evening", {hm(19, 0): FIRST_BUY})
        kw.setdefault("paths", {hm(8, 59): SIGNAL_BUY})
    else:
        kw.setdefault("paths", {hm(8, 30): FIRST_BUY, hm(8, 59): SIGNAL_BUY})
    return Day(day, **kw)


def cp1_trade(root: str, day: date = TUE, side: str = "buy") -> list[tuple]:
    g = grp(root)
    return trade(day, ENTRY_FILL[g], EXIT_FILL[g], side)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_2(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(root=root)])
    assert fills(res) == cp1_trade(root)  # grains fill 12:45 / 13:14, livestock 12:30 / 12:59
    g = grp(root)
    assert intents(res) == [(TUE, ENTRY[g], True, None), (TUE, EXIT[g], True, None)]
    assert fill_qty(res) == [1, 1]  # q_c (S0.3)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_sells_on_a_negative_signal(root: str) -> None:
    # s = close(08:59) - open(first) = -3; close - close +7, open - open +5
    first, signal = (0, 0, -10, -10), (5, 5, -3, -3)
    if is_grain(root):
        day = Day(TUE, evening={hm(19, 0): first}, paths={hm(8, 59): signal})
    else:
        day = Day(TUE, paths={hm(8, 30): first, hm(8, 59): signal})
    res = run(make(cp1, root), [day])
    assert fills(res) == cp1_trade(root, side="sell")
    assert fill_qty(res) == [1, 1]


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_the_signal_is_one_tick_either_side_of_zero(root: str) -> None:
    first = {hm(8, 30): (0, 0, 0, 0)} if not is_grain(root) else {}
    up = cp1_day(root=root, paths={**first, hm(8, 59): (0, 1, 0, 1)})
    down = cp1_day(root=root, paths={**first, hm(8, 59): (0, 0, -1, -1)})
    assert fills(run(make(cp1, root), [up])) == cp1_trade(root)
    assert fills(run(make(cp1, root), [down])) == cp1_trade(root, side="sell")
    assert price(root, 1) - price(root, 0) == pytest.approx(float(TICK[root]))


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_zero_signal_is_no_trade(root: str) -> None:
    first = {hm(8, 30): FIRST_BUY} if not is_grain(root) else {}
    day = cp1_day(root=root, paths={**first, hm(8, 59): (-5, 0, -5, 0)})  # close = open(first)
    assert intents(run(make(cp1, root), [day])) == []


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp1_grain_monday_first_bar_is_sunday_1900_l01(root: str) -> None:
    # the Sunday 19:00 bar's open (B+5) decides: s = 3 - 5 = -2, a sell; 19:01's open (B) and
    # the 08:30 bar's open (B) would give a buy
    day = cp1_day(MON, evening={hm(19, 0): (5, 5, 0, 0)})
    res = run(make(cp1, root), [cp1_day(FRI), day])
    assert fills(res) == cp1_trade(root, FRI) + cp1_trade(root, MON, "sell")
    first = frame([day], root).iloc[0]
    assert ct(int(first["ts_event"])) == datetime(2025, 6, 1, 19, 0, tzinfo=CT)  # Sunday
    assert first["trade_date"] == MON.isoformat()


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp1_grain_missing_1900_bar_takes_the_first_later_bar_l01(root: str) -> None:
    # 19:01 opens B-5 (s = 3 + 5 = +8, a buy); 19:02 opens B+5 (would be a sell); the E.3-L-05
    # reading (the 19:00 bar only) would be no trade
    evening = {hm(19, 0): (9, 9, 9, 9), hm(19, 1): (-5, 0, -5, 0), hm(19, 2): (5, 5, 5, 5)}
    day = cp1_day(evening=evening, evening_skip=frozenset({hm(19, 0)}))
    assert fills(run(make(cp1, root), [day])) == cp1_trade(root)
    two_missing = cp1_day(evening=evening, evening_skip=frozenset({hm(19, 0), hm(19, 1)}))
    assert fills(run(make(cp1, root), [two_missing])) == cp1_trade(root, side="sell")


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp1_grain_no_evening_bar_takes_the_first_bar_of_ct_date_d_l01(root: str) -> None:
    # every evening bar missing: the earliest bar at or after 19:00 of d-1 is the 07:40 bar
    evening_gone = frozenset(EVENING)
    day = cp1_day(evening_skip=evening_gone, paths={hm(7, 40): (5, 5, 0, 0),
                                                     hm(7, 41): (-5, 0, -5, 0),
                                                     hm(8, 59): SIGNAL_BUY})
    assert fills(run(make(cp1, root), [day])) == cp1_trade(root, side="sell")


@pytest.mark.parametrize("root", GRAIN_ROOTS)
@pytest.mark.parametrize("late", [LATE_XMAS, LATE_NY], ids=str)
def test_cp1_grain_late_open_first_bar_is_the_0830_bar_l01(root: str, late: date) -> None:
    # no evening session: the 08:30 bar's open (B+5) decides, s = 3 - 5 = -2, a sell; the
    # 08:31 open (B) would give a buy
    day = Day(late, no_evening=True, paths={hm(8, 30): (5, 5, 0, 0), hm(8, 31): (0, 0, 0, 0),
                                             hm(8, 59): SIGNAL_BUY})
    assert ct(int(frame([day], root)["ts_event"].iloc[0])) == datetime.combine(
        late, time(8, 30), tzinfo=CT)
    assert fills(run(make(cp1, root), [day])) == cp1_trade(root, late, "sell")
    # the 08:30 bar missing on a late open: the first bar is 08:31 (open B), s = +3, a buy
    no_0830 = Day(late, no_evening=True, paths=day.paths, skip=frozenset({hm(8, 30)}))
    assert fills(run(make(cp1, root), [no_0830])) == cp1_trade(root, late)


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp1_grain_first_bar_is_at_or_after_1900_of_the_calendar_day_before_d(root: str) -> None:
    # direct calls with bars the calendar never produces: bars of trade date d before 19:00 CT
    # on d-1 (18:59 of d-1, 19:00 of d-2) are never the first bar; the 19:00 bar of d-1 is
    member = make(cp1, root)
    bars = [bar_at(root, TUE - timedelta(days=2), hm(19, 0), (-9, 0, -9, 0), trade_day=TUE),
            bar_at(root, MON, hm(18, 59), (-9, 0, -9, 0), trade_day=TUE),
            bar_at(root, MON, hm(19, 0), (5, 5, 0, 0), trade_day=TUE),
            bar_at(root, TUE, hm(8, 59), SIGNAL_BUY), bar_at(root, TUE, hm(12, 44))]
    (intent,) = feed(member, bars)
    assert (intent.side, intent.quantity) == ("sell", 1)  # s = 3 - 5 (B-9 would give a buy)
    # the only bars before d-1 19:00: no first bar from them, the 19:01 bar is the first
    member = make(cp1, root)
    bars = [bar_at(root, MON, hm(18, 59), (5, 5, 5, 5), trade_day=TUE),
            bar_at(root, MON, hm(19, 1), (-9, 0, -9, 0), trade_day=TUE),
            bar_at(root, TUE, hm(8, 59), SIGNAL_BUY), bar_at(root, TUE, hm(12, 44))]
    (intent,) = feed(member, bars)
    assert intent.side == "buy"


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp1_grain_first_bar_may_be_the_0859_bar_itself(root: str) -> None:
    # direct calls: no bar of trade date d before 08:59; the earliest bar is the 08:59 bar, so
    # s = close(08:59) - open(08:59) = 3 - (-5) = +8
    member = make(cp1, root)
    (intent,) = feed(member, [bar_at(root, TUE, hm(8, 59), SIGNAL_BUY),
                              bar_at(root, TUE, hm(12, 44))])
    assert intent.side == "buy"


@pytest.mark.parametrize("root", LIVESTOCK_ROOTS)
def test_cp1_livestock_first_bar_is_the_0830_bar_exactly_l02(root: str) -> None:
    # 08:30 open B+5: s = 3 - 5 = -2, a sell (08:31's open B would give a buy)
    day = cp1_day(root=root, paths={hm(8, 30): (5, 5, 0, 0), hm(8, 59): SIGNAL_BUY})
    assert fills(run(make(cp1, root), [day])) == cp1_trade(root, side="sell")
    missing = cp1_day(root=root, skip=frozenset({hm(8, 30)}))  # 08:31 present: no trade
    res = run(make(cp1, root), [missing])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", LIVESTOCK_ROOTS)
def test_cp1_livestock_first_bar_is_on_ct_date_d(root: str) -> None:
    # direct calls: an 08:30 bar of CT date d-1 carrying trade date d is not the first bar
    member = make(cp1, root)
    bars = [bar_at(root, MON, hm(8, 30), (-9, 0, -9, 0), trade_day=TUE),
            bar_at(root, TUE, hm(8, 59), SIGNAL_BUY), bar_at(root, TUE, hm(12, 29))]
    assert feed(member, bars) == []
    member = make(cp1, root)
    bars = [bar_at(root, TUE, hm(8, 30), (5, 5, 0, 0)),
            bar_at(root, TUE, hm(8, 59), SIGNAL_BUY), bar_at(root, TUE, hm(12, 29))]
    (intent,) = feed(member, bars)
    assert intent.side == "sell"


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_0859_signal_bar_is_no_trade(root: str) -> None:
    # the 08:58 and 09:00 bars would both give s = +3
    paths = {hm(8, 58): (0, 3, 0, 3), hm(9, 0): (0, 3, 0, 3)}
    if not is_grain(root):
        paths[hm(8, 30)] = FIRST_BUY
    res = run(make(cp1, root), [cp1_day(root=root, paths=paths, skip=frozenset({hm(8, 59)}))])
    assert intents(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade(root: str) -> None:
    first_differs = (cp1_day(root=root, evening_id=776) if is_grain(root)
                     else cp1_day(root=root, ids={hm(8, 30): 776}))
    signal_differs = cp1_day(root=root, ids={hm(8, 59): 778})
    assert intents(run(make(cp1, root), [first_differs])) == []
    assert intents(run(make(cp1, root), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_on = hm(12, 44) if is_grain(root) else hm(12, 29)
    entry_differs = cp1_day(root=root, ids={m: 778 for m in range(entry_on, hm(13, 20))})
    assert fills(run(make(cp1, root), [entry_differs])) == cp1_trade(root)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_entry_bar_is_no_trade(root: str) -> None:
    entry_on = hm(12, 44) if is_grain(root) else hm(12, 29)
    res = run(make(cp1, root), [cp1_day(root=root, skip=frozenset({entry_on}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_exit_bar_sends_the_exit_on_the_next_bar(root: str) -> None:
    g = grp(root)
    exit_on = hm(13, 13) if is_grain(root) else hm(12, 58)
    res = run(make(cp1, root), [cp1_day(root=root, skip=frozenset({exit_on}))])
    later = "13:15" if is_grain(root) else "13:00"
    assert fills(res) == trade(TUE, ENTRY_FILL[g], later)
    assert intents(res)[-1] == (TUE, EXIT_FILL[g], True, None)


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp1_no_exit_before_c_minus_2(root: str) -> None:
    g = grp(root)
    res = run(make(cp1, root), [cp1_day(root=root)])
    assert [i[1] for i in intents(res)] == [ENTRY[g], EXIT[g]]


@pytest.mark.parametrize("root", ("ZS", "LE"))
def test_cp1_a_refused_exit_is_resent_on_the_next_bar(root: str) -> None:
    # no bars from the entry fill minute to C-3: the entry fills at the C-2 bar's open, so the
    # C-2 exit comes 1 minute after the fill (engine_min_hold, D9.3b); it is sent again on C-1
    g = grp(root)
    entry_on = hm(12, 44) if is_grain(root) else hm(12, 29)
    exit_on = entry_on + 29
    res = run(make(cp1, root), [cp1_day(root=root, skip=frozenset(range(entry_on + 1,
                                                                        exit_on)))])
    assert intents(res) == [(TUE, ENTRY[g], True, None), (TUE, EXIT[g], False, "engine_min_hold"),
                            (TUE, EXIT_FILL[g], True, None)]
    assert fills(res) == trade(TUE, EXIT[g], "13:15" if is_grain(root) else "13:00")


@pytest.mark.parametrize("root", ("ZW", "HE"))
def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine(root: str) -> None:
    g = grp(root)
    flat_at = hm(13, 0) if is_grain(root) else hm(12, 45)
    res = run(make(cp1, root), [cp1_day(root=root, flatten_from=flat_at)])
    assert fills(res) == trade(TUE, ENTRY_FILL[g], f"{(flat_at + 1) // 60:02d}:"
                               f"{(flat_at + 1) % 60:02d}", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == [ENTRY[g]]  # the member sends no exit of its own


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    # the prior settlement is MON's reference close (B); a close at the upper stop level on
    # 12:50 makes the engine close the long at the 12:51 open (price_limit_exit; the upper side,
    # so the move is a gain and never an MLL liquidation, which a ZS lower stop would be)
    g = grp(root)
    up, _ = stop_offsets(root, TUE, 0)
    at = hm(12, 50) if is_grain(root) else hm(12, 35)
    day = cp1_day(root=root)
    day = Day(TUE, paths={**day.paths, at: (0, up, 0, up)}, evening=day.evening)
    res = run(make(cp1, root), [day])
    exit_fill = f"{(at + 1) // 60:02d}:{(at + 1) % 60:02d}"
    assert fills(res) == trade(TUE, ENTRY_FILL[g], exit_fill, exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == [ENTRY[g]]  # no C-2 exit, no second entry
    # one tick inside the stop: no forced exit, the member's own exit
    inside = Day(TUE, paths={**day.paths, at: (0, up - 1, 0, up - 1)}, evening=day.evening)
    assert fills(run(make(cp1, root), [inside])) == cp1_trade(root)


def test_cp1_grain_early_halt_day_has_no_entry_bar_and_no_trade() -> None:
    # 2025-12-24 halts at 12:05 CT (both groups' bars end there): no 12:44 / 12:29 bar
    for root in ("ZC", "LE"):
        end = hm(12, 5) if is_grain(root) else hm(12, 15)
        day = cp1_day(HALT_XMAS, root=root, halt=halt_label(grp(root), HALT_XMAS), end=end)
        res = run(make(cp1, root), [day])
        assert intents(res) == [] and fills(res) == [], root


@pytest.mark.parametrize("root", ("ZM", "HE"))
def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry(root: str) -> None:
    # bars kept to the regular close on the halt day: CP1 is a port (C line 89), it emits on the
    # entry bar and the engine refuses it (F 11:45)
    g = grp(root)
    day = cp1_day(HALT_XMAS, root=root, halt=halt_label(g, HALT_XMAS))
    res = run(make(cp1, root), [day])
    assert intents(res) == [(HALT_XMAS, ENTRY[g], False, "engine_flatten_window")]
    assert fills(res) == []


@pytest.mark.parametrize("root", ("ZL", "LE"))
def test_cp1_trades_once_per_trade_date_and_state_resets(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(TUE, root=root), cp1_day(WED, root=root)])
    assert fills(res) == cp1_trade(root, TUE) + cp1_trade(root, WED)
    # WED has no 08:59 bar: TUE's signal must not carry over
    res = run(make(cp1, root), [cp1_day(TUE, root=root),
                                cp1_day(WED, root=root, skip=frozenset({hm(8, 59)}))])
    assert fills(res) == cp1_trade(root, TUE)


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp1_tuesday_after_memorial_day(root: str) -> None:
    # grains: trade date 05-27 opens Monday 05-26 19:00 CT (the calendar day before d)
    res = run(make(cp1, root), [cp1_day(FRI_MD, root=root), cp1_day(TUE_MD, root=root)])
    assert fills(res) == cp1_trade(root, FRI_MD) + cp1_trade(root, TUE_MD)
    if is_grain(root):
        first = frame([cp1_day(TUE_MD)], root).iloc[0]
        assert ct(int(first["ts_event"])) == datetime(2025, 5, 26, 19, 0, tzinfo=CT)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending(root: str) -> None:
    def primed() -> cp1.Cp1Momentum:
        member = make(cp1, root)  # TUE's two signal bars (s = +3) by direct calls
        first = (bar_at(root, MON, hm(19, 0), trade_day=TUE) if is_grain(root)
                 else bar_at(root, TUE, hm(8, 30)))
        assert feed(member, [first, bar_at(root, TUE, hm(8, 59), (0, 3, 0, 3))]) == []
        return member

    entry = bar_at(root, TUE, hm(12, 44) if is_grain(root) else hm(12, 29))
    view = view_of(root, entry.ts_event_ns, entry)
    member = primed()
    (intent,) = member.on_minute(view, account_of(root))
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert member.on_minute(view, account_of(root)) == ()  # S0.6: once per trade date
    assert primed().on_minute(view, account_of(root, 0, 1)) == ()  # never while pending


@pytest.mark.parametrize("root", ("ZS", "LE"))
def test_cp1_signal_and_entry_bars_are_bars_of_ct_date_d(root: str) -> None:
    # direct calls: an 08:59 or an entry-clock bar of CT date d-1 carrying trade date d (never
    # produced by the calendars) is not the signal bar or the entry bar
    entry_on = hm(12, 44) if is_grain(root) else hm(12, 29)
    first = (bar_at(root, MON, hm(19, 0), trade_day=TUE) if is_grain(root)
             else bar_at(root, TUE, hm(8, 30)))
    wrong_signal = bar_at(root, MON, hm(8, 59), (0, 3, 0, 3), trade_day=TUE)
    assert feed(make(cp1, root), [first, wrong_signal, bar_at(root, TUE, entry_on)]) == []
    signal = bar_at(root, TUE, hm(8, 59), (0, 3, 0, 3))
    wrong_entry = bar_at(root, MON, entry_on, trade_day=TUE)
    assert feed(make(cp1, root), [first, signal, wrong_entry]) == []
    (intent,) = feed(make(cp1, root), [first, signal, bar_at(root, TUE, entry_on)])
    assert intent.side == "buy"
