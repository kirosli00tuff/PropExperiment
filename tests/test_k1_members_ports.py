"""Stage E.7 K1 ports of MemberCoder-A, part 1: the synthetic kit, the declarations and helpers,
and K1-cp1-01 on MNQ, M2K and MYM (reports/stage_e7_member_specs.md sections 0, 1 and 8).
K1-cp2-01 and K1-cp3-01 are in tests/test_k1_members_ports_cp2.py and
tests/test_k1_members_ports_cp3.py; the CPI window and the event minutes of all three ports are in
tests/test_k1_members_ports_events.py. They reuse this file's kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar, a bar the equity calendar
never produces). No bar file is read, no bar loader or runner is run, and no freeze is written
into the repository (the freeze test writes under tmp_path).

The equity calendar (D10, EC-CAL) has no booked-forward dates: a trade date d runs
[d-1 17:00, d 16:00) CT, a Monday opens Sunday 17:00, and an exchange holiday on which CME's
equity session halts early (Memorial Day 2025-05-26, 12:00 CT, engine F 11:30) is its own trade
date. The next trade date's first bar is the holiday's 17:00 CT reopen, and because bars carry the
early_halt_ct label of their CT CALENDAR date (data/group_session.early_halt_labels), those
evening bars carry the holiday's "12:00". The kit builds them that way. Every date used is anchored
to EC-CAL by test_the_synthetic_scenarios_are_ec_cal_facts.
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

from data.group_session import load_group_calendar, previous_trade_date
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
from strategy.members.k1 import cp1, cp2, cp3
from strategy.members.k1._port_common import EXPOSURES, exit_if_due, leg_facts, shift, to_ticks
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
K1_DIR = REPO / "strategy" / "members" / "k1"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3)
ROOTS = ("MNQ", "M2K", "MYM")  # S0.2's order
FACTORY = MappingProxyType({"MNQ": "make_mnq", "M2K": "make_m2k", "MYM": "make_mym"})
ORDINAL = MappingProxyType({(m, r): 3 * i + j + 1 for i, m in enumerate(MODULES)
                            for j, r in enumerate(ROOTS)})  # S0.2 table: 1..9
Q_C = MappingProxyType({"MNQ": 1, "M2K": 3, "MYM": 3})  # expected; pinned against the frozen table
TICK = MappingProxyType({"MNQ": Decimal("0.25"), "M2K": Decimal("0.10"), "MYM": Decimal("1.00")})
BASE_PRICE = MappingProxyType({"MNQ": 20_000.0, "M2K": 2_000.0, "MYM": 40_000.0})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


def make(module: ModuleType, root: str) -> Any:
    """The module's zero-argument factory of ``root`` (S0.2)."""
    return getattr(module, FACTORY[root])()


DAY_START, DAY_END = hm(8, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the first bars of d, CT date d-1

# regular equity trade dates (EC-CAL: no early halt, F 15:08 on MNQ, M2K and MYM)
FRI, MON, TUE, WED = date(2025, 5, 30), date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4)
# Memorial Day 2025-05-26: an equity trade date with an early halt 12:00 CT (engine F 11:30)
THU_MD, FRI_MD, HOLIDAY_MD = date(2025, 5, 22), date(2025, 5, 23), date(2025, 5, 26)
TUE_MD, WED_MD = date(2025, 5, 27), date(2025, 5, 28)
# Independence Day week: 07-03 (halt 12:15, F 11:45) and 07-04 (halt 12:00, F 11:30)
WED_JUL, THU_JUL, FRI_JUL, MON_JUL = (date(2025, 7, 2), date(2025, 7, 3), date(2025, 7, 4),
                                      date(2025, 7, 7))
# full closures (not trade dates): Good Friday 2025-04-18 and Christmas 2025-12-25
THU_GF, GOOD_FRIDAY, MON_GF = date(2025, 4, 17), date(2025, 4, 18), date(2025, 4, 21)
CHRISTMAS, FRI_XMAS = date(2025, 12, 25), date(2025, 12, 26)
# the release calendar's research-window rows used by the events file (regular trade dates)
FRI_NFP, MON_ISM, TUE_PRE_FOMC, WED_FOMC = (date(2025, 5, 2), date(2025, 5, 5), date(2025, 5, 6),
                                            date(2025, 5, 7))
MON_PRE_CPI, TUE_CPI = date(2025, 5, 12), date(2025, 5, 13)
REGULAR = (FRI, MON, TUE, WED, THU_MD, FRI_MD, TUE_MD, WED_MD, WED_JUL, MON_JUL, THU_GF, MON_GF,
           FRI_XMAS, FRI_NFP, MON_ISM, TUE_PRE_FOMC, WED_FOMC, MON_PRE_CPI, TUE_CPI)


def halt_label(day: date) -> str:
    halt = load_group_calendar("equity").early_halt_ct(day)
    assert halt is not None, day
    return halt.strftime("%H:%M")


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars: an evening segment [17:00, 17:05) on CT date d-1 and a
    day segment [start, end) on CT date d, flat at the base price unless ``paths`` or ``evening``
    override a minute (tick offsets from the base). ``only`` keeps just those day minutes (a
    sparse day) and drops the evening."""

    trade_date: date
    paths: Mapping[int, Ticks] = field(default_factory=dict)
    evening: Mapping[int, Ticks] = field(default_factory=dict)
    skip: frozenset[int] = frozenset()  # CT minutes of date d with no bar
    evening_skip: frozenset[int] = frozenset()
    instrument_id: int = 777
    evening_id: int | None = None
    ids: Mapping[int, int] = field(default_factory=dict)  # per-minute instrument_id overrides
    halt: str = ""  # early_halt_ct label of CT date d
    evening_halt: str = ""  # early_halt_ct label of CT date d-1 (the holiday's, after one)
    start: int = DAY_START
    end: int = DAY_END
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
            "raw_symbol": f"{root}M5", "trade_date": trade_day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(days: Sequence[Day], root: str) -> pd.DataFrame:
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
    out = pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)
    assert out["ts_event"].is_unique
    return out


def with_references(days: Sequence[Day]) -> list[Day]:
    """``days`` plus, for every day whose previous EC-CAL trade date is not among them, that
    previous trade date's five evening bars [17:00, 17:05) (flat, no day segment). MNQ, M2K and
    MYM are hard-limit products: the engine refuses any open without a prior-settlement proxy
    (engine_price_limit_reference_unavailable, D9.7), and any bar of the previous trade date gives
    one (rules/price_limits.settlement_proxy's fallback). No port can act on these bars: they hold
    no 08:59, range or 08:30 bar, so they are no signal, no trigger and no complete day."""
    cal = load_group_calendar("equity")
    have = {d.trade_date for d in days}
    refs = {p for d in days if (p := previous_trade_date(cal, d.trade_date)) not in have}
    return sorted([*days, *(Day(p, start=0, end=0) for p in refs if p is not None)],
                  key=lambda d: d.trade_date)


def run(member: Any, days: Sequence[Day], *, window: Sequence[date] | None = None,
        releases: ReleaseCalendar = NO_RELEASES, rules: StageERules | None = None
        ) -> EngineResult:
    """The real engine on ``days`` (plus their price-limit references) for ``member``. The
    window is ``days``' trade dates unless given."""
    dates = [d.trade_date for d in days] if window is None else list(window)
    if rules is None:
        rules = rules_for(member.legs, dates, releases)
    return run_engine({member.root: frame(with_references(days), member.root)}, member,
                      member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure. The synthetic prices stay
    far inside the equity bands, so the real D9.7 exit never fires here; this shows what the
    member does when the engine closes its position on its own."""

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


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def fills(res: EngineResult) -> list[tuple[date, str, str, str]]:
    """(trade date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(f.trade_date, f"{ct(f.fill_ts_ns):%H:%M}", f.side, f.reason)
            for f in res.events(Fill)]


def fill_qty(res: EngineResult) -> list[int]:
    return [f.qty for f in res.events(Fill)]


def fill_dates(res: EngineResult) -> list[date]:
    """The CT calendar date of every fill."""
    return [ct(f.fill_ts_ns).date() for f in res.events(Fill)]


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
           trade_day: date | None = None, instrument_id: int = 777,
           halt: time | None = None) -> Bar:
    """A Bar opening at CT ``minute`` of CT date ``day`` carrying ``trade_day`` (default: day)."""
    o, h, lo, c = (price(root, x) for x in offsets)
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, f"{root}M5",
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
    cal = load_group_calendar("equity")
    assert not cal.booked_forward  # no booked-forward dates
    for day in REGULAR:
        assert cal.is_trade_date(day) and cal.early_halt_ct(day) is None, day
        for root in ROOTS:
            assert sessions.flatten_time_ct(root, day) == time(15, 8), (root, day)
    # early-halt exchange holidays are equity trade dates with an early engine F
    for day, label, f in ((HOLIDAY_MD, "12:00", time(11, 30)), (THU_JUL, "12:15", time(11, 45)),
                          (FRI_JUL, "12:00", time(11, 30))):
        assert cal.is_trade_date(day) and halt_label(day) == label, day
        for root in ROOTS:
            assert sessions.flatten_time_ct(root, day) == f, (root, day)
    # full closures are not trade dates
    assert not cal.is_trade_date(GOOD_FRIDAY) and not cal.is_trade_date(CHRISTMAS)
    assert [d.weekday() for d in (MON, HOLIDAY_MD, TUE_MD, MON_GF, FRI_XMAS)] == [0, 0, 1, 0, 4]


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k1/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K1") == []


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
def test_each_port_module_has_exactly_the_three_factories(module: ModuleType) -> None:
    factories = sorted(n for n in vars(module) if n.startswith("make_"))
    assert factories == ["make_m2k", "make_mnq", "make_mym"]  # S0.1: no ES, MES or full size


def test_member_ids_are_the_catalog_ids() -> None:
    assert (cp1.MEMBER_ID, cp2.MEMBER_ID, cp3.MEMBER_ID) == ("K1-cp1-01", "K1-cp2-01",
                                                            "K1-cp3-01")


@pytest.mark.parametrize("root", ROOTS)
def test_trading_windows_are_the_s0_12_intervals(root: str) -> None:
    windows = {m: make(m, root).trading_windows[root] for m in MODULES}
    assert windows[cp1] == (TradingInterval(time(17, 0), time(17, 1), -1, -1),
                            TradingInterval(time(8, 59), time(9, 0)),
                            TradingInterval(time(14, 29), time(15, 0)))
    assert windows[cp2] == (TradingInterval(time(8, 30), time(15, 8)),)
    assert windows[cp3] == (TradingInterval(time(8, 30), time(15, 0)),)


@pytest.mark.parametrize("root", ROOTS)
def test_frozen_clock_size_and_tick_per_root(root: str) -> None:
    tables = load_frozen_tables()
    assert tables.day_session_ct[root] == (time(8, 30), time(15, 0))
    assert tables.vehicles[root].q_c == Q_C[root]
    assert product(root).vendor_tick == TICK[root]
    facts = leg_facts(root)
    assert (facts.root, facts.o, facts.c, facts.q, facts.tick) == (
        root, time(8, 30), time(15, 0), Q_C[root], TICK[root])


def test_leg_facts_refuses_a_root_outside_the_cluster() -> None:
    for root in ("MES", "ES", "NQ", "RTY", "YM"):
        with pytest.raises(ValueError, match="not a K1 exposure"):
            leg_facts(root)


def test_the_9_port_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze for the ports (S0.2 ordinals 1-9) pass the real
    freeze code; the freeze is written under tmp_path only (never the repository's file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k1").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k1" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K1_DIR / name, members_dir / "k1" / name)
    check_cluster_sources("K1", tmp_path)
    decls = [MemberDecl(f"{m.MEMBER_ID} {r}", ORDINAL[(m, r)], m.__name__, FACTORY[r],
                        (LegSpec(r, True),)) for m in MODULES for r in ROOTS]
    write_cluster_freeze("K1", decls, tmp_path)
    freeze = load_cluster_freeze("K1", tmp_path)
    verify_cluster_code(freeze)
    labels = [f"{m.MEMBER_ID} {r}" for m in MODULES for r in ROOTS]
    assert [freeze.member(lb).ordinal for lb in labels] == list(range(1, 10))
    assert labels[:3] == ["K1-cp1-01 MNQ", "K1-cp1-01 M2K", "K1-cp1-01 MYM"]


@pytest.mark.parametrize("root", ROOTS)
def test_prices_become_integer_vendor_ticks(root: str) -> None:
    tick = product(root).vendor_tick
    b = base_ticks(root)
    assert b == {"MNQ": 80_000, "M2K": 20_000, "MYM": 40_000}[root]
    for k in (0, 1, 3, -1, -7):
        assert to_ticks(price(root, k), tick) == b + k
    half = float(BASE_PRICE[root] + float(tick) / 2)
    assert to_ticks(half, tick) == b  # round half to even (never met on the vendor grid)
    assert to_ticks(float(BASE_PRICE[root] + float(tick) * 0.6), tick) == b + 1


def test_shift_moves_a_clock_time() -> None:
    assert shift(time(8, 30), 29) == time(8, 59)
    assert shift(time(15, 0), -31) == time(14, 29)
    assert shift(time(17, 0), 1) == time(17, 1)


@pytest.mark.parametrize("root", ROOTS)
def test_a_none_bar_is_no_decision_and_changes_no_state(root: str) -> None:
    for module in MODULES:
        member = make(module, root)
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 59))
        assert member.on_minute(view_of(root, ts, None), account_of(root, 1)) == ()
        assert member.on_minute(view_of(root, ts, None), account_of(root)) == ()
        assert repr(vars(member)) == before


@pytest.mark.parametrize("root", ROOTS)
def test_an_exit_is_not_sent_while_an_order_is_pending(root: str) -> None:
    q = Q_C[root]
    bar = bar_at(root, TUE, hm(14, 58))
    view = view_of(root, bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of(root, q, -q), root, opened, TUE, time(14, 58)) == ()
    assert exit_if_due(view, account_of(root, 0, q), root, opened, TUE, time(14, 58)) == ()
    assert exit_if_due(view, account_of(root, 0), root, opened, TUE, time(14, 58)) == ()
    (intent,) = exit_if_due(view, account_of(root, -q), root, opened, TUE, time(14, 58))
    assert (intent.side, intent.quantity) == ("buy", q)
    (intent,) = exit_if_due(view, account_of(root, q), root, opened, TUE, time(14, 57))
    assert (intent.side, intent.quantity) == ("sell", q)
    assert exit_if_due(view, account_of(root, q), root, opened, TUE, time(14, 59)) == ()
    # the exit bar must be on CT date d: a 14:58 bar of another CT date is not an exit bar
    assert exit_if_due(view, account_of(root, q), root, opened, WED, time(14, 58)) == ()


# ------------------------------------------------------------------------ K1-cp1-01 ----
# 17:00 bar (d-1): open B, close B+10. 08:59 bar: open B-5, close B+3. D6's s = close(08:59) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}
CP1_BUY_DAY = {hm(8, 59): (-5, 3, -5, 3)}


def cp1_day(day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", CP1_BUY_DAY)
    return Day(day, **kw)


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459(root: str) -> None:
    res = run(make(cp1, root), [cp1_day()])
    assert fills(res) == trade(TUE, "14:30", "14:59", "buy")
    assert intents(res) == [(TUE, "14:29", True, None), (TUE, "14:58", True, None)]
    assert fill_qty(res) == [Q_C[root], Q_C[root]]  # q_c (S0.3): MNQ 1, M2K 3, MYM 3


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_sells_on_a_negative_signal(root: str) -> None:
    # s = close(08:59) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)}, paths={hm(8, 59): (5, 5, -3, -3)})
    res = run(make(cp1, root), [day])
    assert fills(res) == trade(TUE, "14:30", "14:59", "sell")
    assert fill_qty(res) == [Q_C[root], Q_C[root]]


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_the_signal_is_one_tick_either_side_of_zero(root: str) -> None:
    up = cp1_day(paths={hm(8, 59): (0, 1, 0, 1)})
    down = cp1_day(paths={hm(8, 59): (0, 0, -1, -1)})
    assert fills(run(make(cp1, root), [up])) == trade(TUE, "14:30", "14:59", "buy")
    assert fills(run(make(cp1, root), [down])) == trade(TUE, "14:30", "14:59", "sell")
    # one vendor tick in prices: MNQ 0.25, M2K 0.10, MYM 1.00
    assert price(root, 1) - price(root, 0) == pytest.approx(float(TICK[root]))


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_zero_signal_is_no_trade(root: str) -> None:
    day = cp1_day(paths={hm(8, 59): (-5, 0, -5, 0)})  # close(08:59) = open(17:00)
    assert intents(run(make(cp1, root), [day])) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_first_bar_is_no_trade_l05(root: str) -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; E.3-L-05 names the 17:00 bar only
    res = run(make(cp1, root), [cp1_day(evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_0859_signal_bar_is_no_trade(root: str) -> None:
    # the 08:58 and 09:00 bars would both give s = +3 (close B+3)
    paths = {hm(8, 58): (0, 3, 0, 3), hm(9, 0): (0, 3, 0, 3)}
    res = run(make(cp1, root), [cp1_day(paths=paths, skip=frozenset({hm(8, 59)}))])
    assert intents(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06(root: str) -> None:
    evening_differs = cp1_day(evening_id=776)
    signal_differs = cp1_day(ids={hm(8, 59): 778})
    assert intents(run(make(cp1, root), [evening_differs])) == []
    assert intents(run(make(cp1, root), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_differs = cp1_day(ids={m: 778 for m in range(hm(14, 29), DAY_END)})
    assert fills(run(make(cp1, root), [entry_differs])) == trade(TUE, "14:30", "14:59")


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_1429_entry_bar_is_no_trade_l04(root: str) -> None:
    # the 14:28 and 14:30 bars are present; S0.6 names the 14:29 bar only
    res = run(make(cp1, root), [cp1_day(skip=frozenset({hm(14, 29)}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_missing_1458_bar_sends_the_exit_on_1459(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(skip=frozenset({hm(14, 58)}))])
    assert fills(res) == trade(TUE, "14:30", "15:00")
    assert intents(res)[-1] == (TUE, "14:59", True, None)
    assert fill_qty(res) == [Q_C[root], Q_C[root]]  # the exit closes the whole position


def test_cp1_no_exit_before_1458() -> None:
    # every bar from the fill to 14:57 is present; the first exit intent is on 14:58
    res = run(make(cp1, "M2K"), [cp1_day()])
    assert [i[1] for i in intents(res)] == ["14:29", "14:58"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_a_refused_exit_is_resent_on_the_next_bar(root: str) -> None:
    # no bars 14:30..14:57: the entry fills at the 14:58 open, so the 14:58 exit comes 1 minute
    # after the fill (engine_min_hold, D9.3b); it is sent again on 14:59 and fills at 15:00
    res = run(make(cp1, root), [cp1_day(skip=frozenset(range(hm(14, 30), hm(14, 58))))])
    assert intents(res) == [(TUE, "14:29", True, None), (TUE, "14:58", False, "engine_min_hold"),
                            (TUE, "14:59", True, None)]
    assert fills(res) == trade(TUE, "14:58", "15:00")


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(make(cp1, "MYM"), [cp1_day(flatten_from=hm(14, 45))])
    assert fills(res) == trade(TUE, "14:30", "14:46", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["14:29"]  # the member sends no exit of its own


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [cp1_day()]
    member = make(cp1, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(14, 40))]))
    assert fills(res) == trade(TUE, "14:30", "14:41", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["14:29"]  # no 14:58 exit, no second entry


def test_cp1_on_memorial_day_there_is_no_1429_bar_and_no_trade() -> None:
    # 2025-05-26 halts at 12:00 CT: its bars end there, so the entry bar does not exist
    day = cp1_day(HOLIDAY_MD, halt=halt_label(HOLIDAY_MD), end=hm(12, 0))
    res = run(make(cp1, "MNQ"), [day])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry(root: str) -> None:
    # bars kept to 15:12 on the halt day: CP1 is a port (C line 104), it emits at 14:29 and the
    # engine refuses it (F 11:30)
    day = cp1_day(HOLIDAY_MD, halt=halt_label(HOLIDAY_MD))
    res = run(make(cp1, root), [day])
    assert intents(res) == [(HOLIDAY_MD, "14:29", False, "engine_flatten_window")]
    assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(make(cp1, "MNQ"), [cp1_day(TUE), cp1_day(WED)])
    assert fills(res) == trade(TUE, "14:30", "14:59") + trade(WED, "14:30", "14:59")


def test_cp1_state_resets_each_trade_date() -> None:
    # WED has no 08:59 bar: TUE's signal must not carry over
    res = run(make(cp1, "M2K"), [cp1_day(TUE), cp1_day(WED, skip=frozenset({hm(8, 59)}))])
    assert fills(res) == trade(TUE, "14:30", "14:59")


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_monday_opens_sunday_1700(root: str) -> None:
    # the Sunday 17:00 bar's open (B+5) decides: s = 3 - 5 = -2, a sell; the 17:01 bar's open
    # (B) would give a buy
    day = cp1_day(MON, evening={hm(17, 0): (5, 5, 0, 0)})
    res = run(make(cp1, root), [cp1_day(FRI), day])
    assert fills(res) == trade(FRI, "14:30", "14:59") + trade(MON, "14:30", "14:59", "sell")
    mon_rows = frame([day], root)
    assert ct(int(min(mon_rows["ts_event"]))) == datetime(2025, 6, 1, 17, 0, tzinfo=CT)  # Sunday


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_after_memorial_day_the_first_bar_is_the_holidays_1700_reopen(root: str) -> None:
    # trade date 2025-05-27 opens Monday 05-26 17:00 CT; those evening bars carry the holiday's
    # early_halt_ct label (CT calendar date 05-26), which CP1 does not read. The reopen's open
    # B+5 decides: s = 3 - 5 = -2, a sell. The holiday's own bars (trade date 05-26, to 12:00)
    # hold an 08:59 close of B+20, which must not carry into Tuesday
    label = halt_label(HOLIDAY_MD)
    holiday = Day(HOLIDAY_MD, paths={hm(8, 59): (0, 20, 0, 20)}, halt=label, end=hm(12, 0))
    tue = cp1_day(TUE_MD, evening={hm(17, 0): (5, 5, 0, 0)}, evening_halt=label)
    res = run(make(cp1, root), [cp1_day(FRI_MD), holiday, tue])
    assert fills(res) == trade(FRI_MD, "14:30", "14:59") + trade(TUE_MD, "14:30", "14:59",
                                                                 "sell")
    tue_rows = frame([tue], root)
    first = tue_rows.iloc[0]
    assert ct(int(first["ts_event"])) == datetime(2025, 5, 26, 17, 0, tzinfo=CT)
    assert first["early_halt_ct"] == "12:00" and first["trade_date"] == TUE_MD.isoformat()
    # without the Monday 17:00 reopen bar there is no trade on Tuesday
    tue_missing = cp1_day(TUE_MD, evening_skip=frozenset({hm(17, 0)}), evening_halt=label)
    assert intents(run(make(cp1, root), [holiday, tue_missing])) == []


def test_cp1_after_a_full_closure_the_first_bar_is_the_closure_days_1700_reopen() -> None:
    # Christmas 2025-12-25 is closed; trade date 12-26 opens Thursday 12-25 17:00 CT (B+5):
    # s = 3 - 5, a sell. After Good Friday, Monday 04-21 opens Sunday 04-20 17:00 (B-5): a buy
    fri = cp1_day(FRI_XMAS, evening={hm(17, 0): (5, 5, 0, 0)})
    assert fills(run(make(cp1, "MYM"), [fri])) == trade(FRI_XMAS, "14:30", "14:59", "sell")
    assert ct(int(frame([fri], "MYM")["ts_event"].iloc[0])).date() == CHRISTMAS
    mon = cp1_day(MON_GF, evening={hm(17, 0): (-5, 0, -5, 0)})
    res = run(make(cp1, "MYM"), [cp1_day(THU_GF), mon])
    assert fills(res) == trade(THU_GF, "14:30", "14:59") + trade(MON_GF, "14:30", "14:59")
    assert ct(int(frame([mon], "MYM")["ts_event"].iloc[0])).date() == date(2025, 4, 20)


def test_cp1_the_first_bar_is_the_1700_bar_of_ct_date_d_minus_1_only() -> None:
    # direct calls with bars the equity calendar never produces: a 17:00 bar carrying trade date
    # d on CT date d-2 or d-3 is not the trade date's first bar (S0.4: the bar at hh:mm is
    # identified by its CT date and clock)
    for first_day in (TUE - timedelta(days=2), TUE - timedelta(days=3)):
        member = make(cp1, "MNQ")
        bars = [bar_at("MNQ", first_day, hm(17, 0), (-5, 0, -5, 0), trade_day=TUE),
                bar_at("MNQ", TUE, hm(8, 59), (0, 3, 0, 3)), bar_at("MNQ", TUE, hm(14, 29))]
        assert feed(member, bars) == [], first_day
    member = make(cp1, "MNQ")
    bars = [bar_at("MNQ", TUE - timedelta(days=1), hm(17, 0), (-5, 0, -5, 0), trade_day=TUE),
            bar_at("MNQ", TUE, hm(8, 59), (0, 3, 0, 3)), bar_at("MNQ", TUE, hm(14, 29))]
    (intent,) = feed(member, bars)
    assert (intent.side, intent.quantity) == ("buy", 1)


def test_cp1_signal_and_entry_bars_are_bars_of_ct_date_d() -> None:
    # direct calls: an 08:59 or a 14:29 bar of CT date d-1 carrying trade date d (never produced
    # by the equity calendar) is not the signal bar or the entry bar
    first = bar_at("M2K", MON, hm(17, 0), trade_day=TUE)
    wrong_signal = bar_at("M2K", MON, hm(8, 59), (0, 3, 0, 3), trade_day=TUE)
    assert feed(make(cp1, "M2K"), [first, wrong_signal, bar_at("M2K", TUE, hm(14, 29))]) == []
    signal = bar_at("M2K", TUE, hm(8, 59), (0, 3, 0, 3))
    wrong_entry = bar_at("M2K", MON, hm(14, 29), trade_day=TUE)
    assert feed(make(cp1, "M2K"), [first, signal, wrong_entry]) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending(root: str) -> None:
    def primed() -> cp1.Cp1Momentum:
        member = make(cp1, root)  # TUE's two signal bars (s = +3) by direct calls
        assert feed(member, [bar_at(root, MON, hm(17, 0), trade_day=TUE),
                             bar_at(root, TUE, hm(8, 59), (0, 3, 0, 3))]) == []
        return member

    entry = bar_at(root, TUE, hm(14, 29))
    view = view_of(root, entry.ts_event_ns, entry)
    member = primed()
    (intent,) = member.on_minute(view, account_of(root))
    assert (intent.side, intent.quantity) == ("buy", Q_C[root])
    assert member.on_minute(view, account_of(root)) == ()  # S0.6: once per trade date
    assert primed().on_minute(view, account_of(root, 0, Q_C[root])) == ()  # never while pending


def test_the_kit_adds_the_price_limit_reference_the_engine_needs() -> None:
    # without a bar of the previous trade date the engine refuses every open on MNQ, M2K and MYM
    # (D9.7: no prior-settlement proxy); ``run`` adds MON's evening bars for TUE
    member = make(cp1, "MNQ")
    bare = run_engine({"MNQ": frame([cp1_day()], "MNQ")}, member, member.legs,
                      rules_for(member.legs, [TUE]))
    assert intents(bare) == [(TUE, "14:29", False, "engine_price_limit_reference_unavailable")]
    (ref, tue) = with_references([cp1_day()])
    assert (ref.trade_date, ref.start, ref.end, tue.trade_date) == (MON, 0, 0, TUE)
    assert len(frame([ref], "MNQ")) == 5
    # the reference evening alone makes no port act
    for module in MODULES:
        assert intents(run(make(module, "MNQ"), [ref])) == []
