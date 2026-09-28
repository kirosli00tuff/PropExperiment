"""Stage E.6 K7 ports of MemberCoder-A, part 1: the synthetic kit, the declarations and helpers,
and K7-cp1-01 (reports/stage_e6_member_specs.md sections 0, 1 and 8). K7-cp2-01 and K7-cp3-01 are
in tests/test_k7_members_ports_cp2.py and tests/test_k7_members_ports_cp3.py, which reuse this
file's kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar). No bar file is read, no bar
loader or runner is run, and no freeze is written into the repository (the freeze test writes
under tmp_path).

K7-L-01 (a bar is its CT date AND clock) is pinned on three kinds of trade date, each anchored to
EC-CAL by test_the_synthetic_scenarios_are_ec_cal_facts:
- a Monday before 2026-05-29: the trade date opens Sunday 17:00 CT;
- a Monday from 2026-06-01: bars from Friday 16:02 to Sunday 16:59 CT also carry Monday's trade
  date (weekend bars, built here with prices that would change the trade if a member read them);
- the trade date after a booked-forward Monday (2026-01-19 -> 2026-01-20): the holiday's session,
  Sunday 17:00 to Monday 16:00 CT, carries Tuesday's trade date, so one trade date spans the
  Sunday, Monday and Tuesday CT dates.
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

from data.calendars import crypto as crypto_calendar
from data.group_session import load_group_calendar
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
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.interface import Bar
from strategy.members.k7 import cp1, cp2, cp3
from strategy.members.k7._port_common import EXPOSURES, exit_if_due, leg_facts, shift, to_ticks
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
K7_DIR = REPO / "strategy" / "members" / "k7"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3)
ORDINAL = MappingProxyType({cp1: 1, cp2: 2, cp3: 3})  # S0.2 table
ROOT = "MBT"
BASE_PRICE = 100_000.0  # USD per bitcoin: 20000 vendor ticks of 5.00
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


DAY_START, DAY_END = hm(8, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the first bars of d, CT date d-1

# regular crypto trade dates before 2026-05-29 (EC-CAL full sessions, F 15:08)
FRI, MON, TUE, WED = date(2025, 5, 30), date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4)
# from 2026-06-01: weekend bars (Friday 16:02 to Sunday 17:00 CT) carry Monday's trade date
FRI_247, SAT_247, SUN_247 = date(2026, 6, 5), date(2026, 6, 6), date(2026, 6, 7)
MON_247, TUE_247 = date(2026, 6, 8), date(2026, 6, 9)
# a booked-forward Monday: 2026-01-19's session (Sunday 01-18 17:00 to Monday 16:00 CT) carries
# trade date 2026-01-20; the Monday itself is not a trade date
FRI_BF, SUN_BF, HOLIDAY_BF = date(2026, 1, 16), date(2026, 1, 18), date(2026, 1, 19)
TUE_BF, WED_BF = date(2026, 1, 20), date(2026, 1, 21)
# an EC-CAL crypto early halt (12:00 CT); the engine's F is 11:30
THU_HALT, HALT_DAY, MON_HALT = date(2025, 7, 3), date(2025, 7, 4), date(2025, 7, 7)


def halt_label(day: date) -> str:
    halt = load_group_calendar("crypto").early_halt_ct(day)
    assert halt is not None, day
    return halt.strftime("%H:%M")


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Segment:
    """Bars of a trade date on ANOTHER CT calendar date than d and its evening d-1: weekend bars
    from 2026-06-01, or a booked-forward holiday's session. CT minutes [start, end) of
    ``ct_day``, flat at the base unless ``paths`` overrides a minute."""

    ct_day: date
    start: int
    end: int
    paths: Mapping[int, Ticks] = field(default_factory=dict)
    instrument_id: int = 777


@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars: an evening segment [17:00, 17:05) on CT date d-1, a day
    segment [start, end) on CT date d and any ``others`` segments, flat at the base price unless
    ``paths`` or ``evening`` override a minute (tick offsets from the base). ``only`` keeps just
    those day minutes (a sparse day) and drops the evening."""

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
    others: tuple[Segment, ...] = ()


def base_ticks() -> int:
    return to_ticks(BASE_PRICE, product(ROOT).vendor_tick)


def _rows(trade_day: date, ct_day: date, minutes: Sequence[int], paths: Mapping[int, Ticks],
          skip: frozenset[int], ids: Mapping[int, int], default_id: int, halt: str,
          flatten_from: int | None) -> list[dict]:
    b, fixed = base_ticks(), product(ROOT).vendor_tick_fixed
    out = []
    for minute in minutes:
        if minute in skip:
            continue
        o, h, lo, c = (b + x for x in paths.get(minute, (0, 0, 0, 0)))
        utc = datetime.combine(ct_day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
        state = sessions.session_state(ROOT, utc)
        synthetic_f = flatten_from is not None and minute >= flatten_from
        out.append({
            "ts_event": int(utc.timestamp()) * NS, "open": o * fixed / PRICE_SCALE,
            "high": h * fixed / PRICE_SCALE, "low": lo * fixed / PRICE_SCALE,
            "close": c * fixed / PRICE_SCALE, "volume": 10,
            "instrument_id": ids.get(minute, default_id), "raw_symbol": "MBTM5",
            "trade_date": trade_day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(days: Sequence[Day]) -> pd.DataFrame:
    rows: list[dict] = []
    for d in days:
        if d.only is None:
            eve_id = d.instrument_id if d.evening_id is None else d.evening_id
            rows += _rows(d.trade_date, d.trade_date - timedelta(days=1),
                          range(EVENING_START, EVENING_END), d.evening, d.evening_skip, {},
                          eve_id, d.evening_halt, None)
        for seg in d.others:
            rows += _rows(d.trade_date, seg.ct_day, range(seg.start, seg.end), seg.paths,
                          frozenset(), {}, seg.instrument_id, "", None)
        minutes = range(d.start, d.end) if d.only is None else sorted(d.only)
        rows += _rows(d.trade_date, d.trade_date, minutes, d.paths, d.skip, d.ids,
                      d.instrument_id, d.halt, d.flatten_from)
    out = pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)
    assert out["ts_event"].is_unique
    return out


def run(member: Any, days: Sequence[Day], *, window: Sequence[date] | None = None,
        releases: ReleaseCalendar = NO_RELEASES, rules: StageERules | None = None
        ) -> EngineResult:
    dates = [d.trade_date for d in days] if window is None else list(window)
    if rules is None:
        rules = rules_for(member.legs, dates, releases)
    return run_engine({ROOT: frame(days)}, member, member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure. MBT is DCB-only (not in
    rules.price_limits.HARD_LIMIT_PRODUCTS), so the real D9.7 exit cannot fire on it; this shows
    what the member does when the engine closes its position on its own."""

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


def fill_dates(res: EngineResult) -> list[date]:
    """The CT calendar date of every fill (a trade date can span several)."""
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


def release_at(day: date, hh: int, mm: int) -> ReleaseCalendar:
    instant = datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC)
    return release_calendar(ROOT, [int(instant.timestamp()) * NS])


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({ROOT: bar}))


def account_of(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({ROOT: position}), MappingProxyType({ROOT: pending}),
                             MappingProxyType({ROOT: None}), MappingProxyType({ROOT: 0}))


def bar_at(day: date, minute: int, offsets: Ticks = (0, 0, 0, 0), *, trade_day: date | None = None,
           instrument_id: int = 777, halt: time | None = None) -> Bar:
    """A Bar opening at CT ``minute`` of CT date ``day`` carrying ``trade_day`` (default: day)."""
    fixed = product(ROOT).vendor_tick_fixed
    o, h, lo, c = ((base_ticks() + x) * fixed / PRICE_SCALE for x in offsets)
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, "MBTM5",
               day if trade_day is None else trade_day, False, False, halt, False, False, 0,
               False)


# weekend bars of a Monday from 2026-06-01 (Friday 16:02 to Sunday 16:59 CT), in segments that
# cover every clock a port reads; each port's test sets prices that would change its trade
def weekend(paths_fri: Mapping[int, Ticks] | None = None,
            paths_sat: Mapping[int, Ticks] | None = None,
            paths_sun: Mapping[int, Ticks] | None = None) -> tuple[Segment, ...]:
    fri, sat, sun = paths_fri or {}, paths_sat or {}, paths_sun or {}
    return (Segment(FRI_247, hm(16, 2), hm(16, 10), fri),
            Segment(FRI_247, hm(17, 0), hm(17, 5), fri),
            Segment(SAT_247, hm(8, 25), hm(9, 5), sat),
            Segment(SAT_247, hm(14, 25), hm(15, 5), sat),
            Segment(SUN_247, hm(8, 25), hm(9, 5), sun),
            Segment(SUN_247, hm(14, 25), hm(15, 5), sun),
            Segment(SUN_247, hm(16, 50), hm(17, 0), sun))


def holiday_session(paths_sun: Mapping[int, Ticks] | None = None,
                    paths_mon: Mapping[int, Ticks] | None = None,
                    mon_id: int = 777) -> tuple[Segment, ...]:
    """The booked-forward Monday 2026-01-19's session, which carries trade date 2026-01-20:
    Sunday 01-18 from 17:00 and Monday 01-19's day [08:00, 15:12) CT. (Tuesday's own evening,
    Monday 01-19 from 17:00, is the Day's evening segment.)"""
    return (Segment(SUN_BF, hm(17, 0), hm(17, 5), paths_sun or {}),
            Segment(HOLIDAY_BF, DAY_START, DAY_END, paths_mon or {}, mon_id))


# ------------------------------------------------------- the calendar facts the kit uses ----
def test_the_synthetic_scenarios_are_ec_cal_facts() -> None:
    cal = load_group_calendar("crypto")
    regular = (FRI, MON, TUE, WED, FRI_247, MON_247, TUE_247, FRI_BF, TUE_BF, WED_BF, THU_HALT,
               MON_HALT)
    for day in regular:
        assert cal.is_trade_date(day) and cal.early_halt_ct(day) is None, day
        assert sessions.flatten_time_ct(ROOT, day) == time(15, 8), day
    # the booked-forward Monday is not a trade date; its session belongs to 2026-01-20
    assert HOLIDAY_BF in cal.booked_forward and not cal.is_trade_date(HOLIDAY_BF)
    assert (HOLIDAY_BF.weekday(), TUE_BF.weekday(), SUN_BF.weekday()) == (0, 1, 6)
    # weekend trading is booked to Monday from 2026-06-01; MON (2025) is before 2026-05-29
    assert date(2026, 6, 1) == crypto_calendar.WEEKEND_TO_NEXT_TRADE_DATE_FROM
    assert MON < date(2026, 5, 29) < date(2026, 6, 1) < MON_247
    assert (MON.weekday(), MON_247.weekday(), SAT_247.weekday()) == (0, 0, 5)
    # the early halt: 12:00 CT, engine F 11:30
    assert halt_label(HALT_DAY) == "12:00"
    assert sessions.flatten_time_ct(ROOT, HALT_DAY) == time(11, 30)
    assert cal.is_trade_date(HALT_DAY)


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k7/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K7") == []


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType) -> None:
    assert EXPOSURES == ("MBT",)
    member = module.make_mbt()
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} MBT"  # S0.2
    assert member.root == ROOT and member.legs == (LegSpec(ROOT, True),)  # S0.1
    assert list(member.trading_windows) == [ROOT]
    assert module.make_mbt() is not module.make_mbt()  # every call starts from fresh state
    assert not hasattr(module, "make_met")  # S0.1: MET is never read


def test_member_ids_are_the_catalog_ids() -> None:
    assert (cp1.MEMBER_ID, cp2.MEMBER_ID, cp3.MEMBER_ID) == ("K7-cp1-01", "K7-cp2-01",
                                                            "K7-cp3-01")


def test_trading_windows_are_the_s0_12_intervals() -> None:
    windows = {m: m.make_mbt().trading_windows[ROOT] for m in MODULES}
    assert windows[cp1] == (TradingInterval(time(17, 0), time(17, 1), -1, -1),
                            TradingInterval(time(8, 59), time(9, 0)),
                            TradingInterval(time(14, 29), time(15, 0)))
    assert windows[cp2] == (TradingInterval(time(8, 30), time(15, 8)),)
    assert windows[cp3] == (TradingInterval(time(8, 30), time(15, 0)),)


def test_frozen_clock_size_and_tick_are_o_0830_c_1500_q_c_1_tick_5() -> None:
    tables = load_frozen_tables()
    assert tables.day_session_ct[ROOT] == (time(8, 30), time(15, 0))
    assert tables.vehicles[ROOT].q_c == 1
    assert product(ROOT).vendor_tick == Decimal("5.00")
    facts = leg_facts(ROOT)
    assert (facts.o, facts.c, facts.q, facts.tick) == (time(8, 30), time(15, 0), 1,
                                                        Decimal("5.00"))


def test_leg_facts_refuses_a_root_outside_the_cluster() -> None:
    for root in ("MET", "MES"):
        with pytest.raises(ValueError, match="not a K7 exposure"):
            leg_facts(root)


def test_the_3_port_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze for the ports (S0.2 ordinals 1-3) pass the real
    freeze code; the freeze is written under tmp_path only (never the repository's file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k7").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k7" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K7_DIR / name, members_dir / "k7" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} MBT", ORDINAL[m], m.__name__, "make_mbt",
                        (LegSpec(ROOT, True),)) for m in MODULES]
    write_cluster_freeze("K7", decls, tmp_path)
    freeze = load_cluster_freeze("K7", tmp_path)
    verify_cluster_code(freeze)
    assert [freeze.member(f"{m.MEMBER_ID} MBT").ordinal for m in MODULES] == [1, 2, 3]


def test_prices_become_integer_vendor_ticks() -> None:
    tick = product(ROOT).vendor_tick
    b = base_ticks()
    assert b == 20_000
    assert to_ticks(float(b * tick), tick) == b
    assert to_ticks(float((b + 3) * tick), tick) == b + 3
    assert to_ticks(float((b - 7) * tick), tick) == b - 7
    assert to_ticks(100_002.5, tick) == b  # round half to even (never met on the 5.00 grid)
    assert to_ticks(100_002.6, tick) == b + 1


def test_shift_moves_a_clock_time() -> None:
    assert shift(time(8, 30), 29) == time(8, 59)
    assert shift(time(15, 0), -31) == time(14, 29)
    assert shift(time(17, 0), 1) == time(17, 1)


def test_a_none_bar_is_no_decision_and_changes_no_state() -> None:
    for module in MODULES:
        member = module.make_mbt()
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 59))
        assert member.on_minute(view_of(ts, None), account_of(1)) == ()
        assert member.on_minute(view_of(ts, None), account_of()) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    bar = bar_at(TUE, hm(14, 58))
    view = view_of(bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of(1, -1), ROOT, opened, TUE, time(14, 58)) == ()
    assert exit_if_due(view, account_of(0, 1), ROOT, opened, TUE, time(14, 58)) == ()
    assert exit_if_due(view, account_of(0), ROOT, opened, TUE, time(14, 58)) == ()
    (intent,) = exit_if_due(view, account_of(-1), ROOT, opened, TUE, time(14, 58))
    assert (intent.side, intent.quantity) == ("buy", 1)
    (intent,) = exit_if_due(view, account_of(1), ROOT, opened, TUE, time(14, 57))
    assert (intent.side, intent.quantity) == ("sell", 1)
    assert exit_if_due(view, account_of(1), ROOT, opened, TUE, time(14, 59)) == ()
    # the exit bar must be on CT date d: a 14:58 bar of another CT date is not an exit bar
    assert exit_if_due(view, account_of(1), ROOT, opened, WED, time(14, 58)) == ()


# ------------------------------------------------------------------------ K7-cp1-01 ----
# 17:00 bar (d-1): open B, close B+10. 08:59 bar: open B-5, close B+3. D6's s = close(08:59) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}
CP1_BUY_DAY = {hm(8, 59): (-5, 3, -5, 3)}


def cp1_day(day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", CP1_BUY_DAY)
    return Day(day, **kw)


def test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459() -> None:
    res = run(cp1.make_mbt(), [cp1_day()])
    assert fills(res) == trade(TUE, "14:30", "14:59", "buy")
    assert intents(res) == [(TUE, "14:29", True, None), (TUE, "14:58", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1 (S0.3)


def test_cp1_sells_on_a_negative_signal() -> None:
    # s = close(08:59) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)}, paths={hm(8, 59): (5, 5, -3, -3)})
    assert fills(run(cp1.make_mbt(), [day])) == trade(TUE, "14:30", "14:59", "sell")


def test_cp1_the_signal_is_one_tick_either_side_of_zero() -> None:
    up = cp1_day(paths={hm(8, 59): (0, 1, 0, 1)})
    down = cp1_day(paths={hm(8, 59): (0, 0, -1, -1)})
    assert fills(run(cp1.make_mbt(), [up])) == trade(TUE, "14:30", "14:59", "buy")
    assert fills(run(cp1.make_mbt(), [down])) == trade(TUE, "14:30", "14:59", "sell")


def test_cp1_zero_signal_is_no_trade() -> None:
    day = cp1_day(paths={hm(8, 59): (-5, 0, -5, 0)})  # close(08:59) = open(17:00)
    assert intents(run(cp1.make_mbt(), [day])) == []


def test_cp1_missing_first_bar_is_no_trade_l05() -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; E.3-L-05 names the 17:00 bar only
    res = run(cp1.make_mbt(), [cp1_day(evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_0859_signal_bar_is_no_trade() -> None:
    # the 08:58 and 09:00 bars would both give s = +3 (close B+3)
    paths = {hm(8, 58): (0, 3, 0, 3), hm(9, 0): (0, 3, 0, 3)}
    res = run(cp1.make_mbt(), [cp1_day(paths=paths, skip=frozenset({hm(8, 59)}))])
    assert intents(res) == []


def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06() -> None:
    evening_differs = cp1_day(evening_id=776)
    signal_differs = cp1_day(ids={hm(8, 59): 778})
    assert intents(run(cp1.make_mbt(), [evening_differs])) == []
    assert intents(run(cp1.make_mbt(), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_differs = cp1_day(ids={m: 778 for m in range(hm(14, 29), DAY_END)})
    assert fills(run(cp1.make_mbt(), [entry_differs])) == trade(TUE, "14:30", "14:59")


def test_cp1_missing_1429_entry_bar_is_no_trade_l04() -> None:
    res = run(cp1.make_mbt(), [cp1_day(skip=frozenset({hm(14, 29)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_1458_bar_sends_the_exit_on_1459() -> None:
    res = run(cp1.make_mbt(), [cp1_day(skip=frozenset({hm(14, 58)}))])
    assert fills(res) == trade(TUE, "14:30", "15:00")
    assert intents(res)[-1] == (TUE, "14:59", True, None)


def test_cp1_no_exit_before_1458() -> None:
    # every bar from the fill to 14:57 is present; the first exit intent is on 14:58
    res = run(cp1.make_mbt(), [cp1_day()])
    assert [i[1] for i in intents(res)] == ["14:29", "14:58"]


def test_cp1_a_refused_exit_is_resent_on_the_next_bar() -> None:
    # no bars 14:30..14:57: the entry fills at the 14:58 open, so the 14:58 exit comes 1 minute
    # after the fill (engine_min_hold, D9.3b); it is sent again on 14:59 and fills at 15:00
    res = run(cp1.make_mbt(), [cp1_day(skip=frozenset(range(hm(14, 30), hm(14, 58))))])
    assert intents(res) == [(TUE, "14:29", True, None), (TUE, "14:58", False, "engine_min_hold"),
                            (TUE, "14:59", True, None)]
    assert fills(res) == trade(TUE, "14:58", "15:00")


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp1.make_mbt(), [cp1_day(flatten_from=hm(14, 45))])
    assert fills(res) == trade(TUE, "14:30", "14:46", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["14:29"]  # the member sends no exit of its own


def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [cp1_day()]
    member = cp1.make_mbt()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(14, 40))]))
    assert fills(res) == trade(TUE, "14:30", "14:41", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["14:29"]  # no 14:58 exit, no second entry


def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry() -> None:
    # 2025-07-04 (early halt 12:00, F 11:30). CP1 is a port (C line 127): it emits at 14:29 and
    # the engine refuses it
    day = cp1_day(HALT_DAY, halt=halt_label(HALT_DAY))
    res = run(cp1.make_mbt(), [day])
    assert intents(res) == [(HALT_DAY, "14:29", False, "engine_flatten_window")]
    assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(cp1.make_mbt(), [cp1_day(TUE), cp1_day(WED)])
    assert fills(res) == trade(TUE, "14:30", "14:59") + trade(WED, "14:30", "14:59")


def test_cp1_state_resets_each_trade_date() -> None:
    # WED has no 08:59 bar: TUE's signal must not carry over
    res = run(cp1.make_mbt(), [cp1_day(TUE), cp1_day(WED, skip=frozenset({hm(8, 59)}))])
    assert fills(res) == trade(TUE, "14:30", "14:59")


def test_cp1_monday_before_2026_05_29_opens_sunday_1700() -> None:
    # the Sunday 17:00 bar's open (B+5) decides: s = 3 - 5 = -2, a sell; the 17:01 bar's open
    # (B) would give a buy
    day = cp1_day(MON, evening={hm(17, 0): (5, 5, 0, 0)})
    res = run(cp1.make_mbt(), [day])
    assert fills(res) == trade(MON, "14:30", "14:59", "sell")
    first = min(frame([day])["ts_event"])
    assert ct(int(first)) == datetime(2025, 6, 1, 17, 0, tzinfo=CT)  # Sunday 17:00 CT


def test_cp1_monday_from_2026_06_01_reads_no_weekend_bar() -> None:
    # every weekend bar carries Monday's trade date. Friday 16:02 (the trade date's first bar
    # by CME's assignment) and the Friday 17:00 bar open at B+10 (s = 3 - 10: a sell); the
    # Saturday and Sunday 08:59 bars close at B-20 (a sell); a weekend 14:29 bar is not the entry
    # bar (an intent there would be refused and would use up the day)
    wrong_first = {hm(16, 2): (10, 10, 10, 10), hm(17, 0): (10, 10, 10, 10)}
    wrong_signal = {hm(8, 59): (0, 0, -20, -20)}
    mon = cp1_day(MON_247, others=weekend(wrong_first, wrong_signal, wrong_signal))
    res = run(cp1.make_mbt(), [cp1_day(FRI_247), mon])
    assert fills(res) == trade(FRI_247, "14:30", "14:59") + trade(MON_247, "14:30", "14:59")
    assert intents(res) == [(FRI_247, "14:29", True, None), (FRI_247, "14:58", True, None),
                            (MON_247, "14:29", True, None), (MON_247, "14:58", True, None)]
    weekend_rows = frame([mon]).query(f"ts_event < {ns_at(SUN_247, hm(17, 0))}")
    assert len(weekend_rows) == 8 + 5 + 4 * 40 + 10 and set(weekend_rows["trade_date"]) == {
        MON_247.isoformat()}


def test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides() -> None:
    # the same weekend, now with the Sunday 17:00 open at B+5: s = 3 - 5 = -2, a sell
    mon = cp1_day(MON_247, evening={hm(17, 0): (5, 5, 0, 0)}, others=weekend())
    assert fills(run(cp1.make_mbt(), [mon])) == trade(MON_247, "14:30", "14:59", "sell")
    # without the Sunday 17:00 bar there is no trade: the Friday 17:00 bar, which also carries
    # Monday's trade date, is not the first bar
    missing = cp1_day(MON_247, evening_skip=frozenset({hm(17, 0)}), others=weekend())
    assert intents(run(cp1.make_mbt(), [missing])) == []


def cp1_signal_bars(member: Any) -> None:
    """Feed a fresh member TUE's two signal bars (s = +3) by direct calls."""
    for bar in (bar_at(MON, hm(17, 0), trade_day=TUE), bar_at(TUE, hm(8, 59), (0, 3, 0, 3))):
        assert member.on_minute(view_of(bar.ts_event_ns, bar), account_of()) == ()


def test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending() -> None:
    entry = bar_at(TUE, hm(14, 29))
    view = view_of(entry.ts_event_ns, entry)
    member = cp1.make_mbt()
    cp1_signal_bars(member)
    (intent,) = member.on_minute(view, account_of())
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert member.on_minute(view, account_of()) == ()  # S0.6: once per trade date
    pending = cp1.make_mbt()
    cp1_signal_bars(pending)
    assert pending.on_minute(view, account_of(0, 1)) == ()  # S0.6: never while pending


def test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700() -> None:
    # trade date 2026-01-20 spans Sunday 01-18 17:00 to Tuesday 16:00 CT. Its first bar by CME's
    # assignment, Sunday 17:00, opens at B+10 (s = 3 - 10: a sell); the holiday's own 08:59 bar
    # closes at B-20 and its 14:29 bar would be an entry bar if read by trade date and clock
    tue = cp1_day(TUE_BF, others=holiday_session({hm(17, 0): (10, 10, 10, 10)},
                                                 {hm(8, 59): (0, 0, -20, -20)}))
    res = run(cp1.make_mbt(), [cp1_day(FRI_BF), tue])
    assert fills(res) == trade(FRI_BF, "14:30", "14:59") + trade(TUE_BF, "14:30", "14:59")
    assert [i[:2] for i in intents(res)] == [(FRI_BF, "14:29"), (FRI_BF, "14:58"),
                                             (TUE_BF, "14:29"), (TUE_BF, "14:58")]
    assert fill_dates(res)[2:] == [TUE_BF, TUE_BF]


def test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides() -> None:
    # Monday 01-19 17:00 opens at B+5: s = 3 - 5 = -2, a sell (the Sunday bar is flat at B)
    tue = cp1_day(TUE_BF, evening={hm(17, 0): (5, 5, 0, 0)}, others=holiday_session())
    assert fills(run(cp1.make_mbt(), [tue])) == trade(TUE_BF, "14:30", "14:59", "sell")
    # and without the Monday 17:00 bar there is no trade, even with the Sunday 17:00 bar present
    tue_missing = cp1_day(TUE_BF, evening_skip=frozenset({hm(17, 0)}), others=holiday_session())
    assert intents(run(cp1.make_mbt(), [tue_missing])) == []
