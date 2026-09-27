"""Stage E.4 K4 members of MemberCoder-A, part 1: the declarations, the ENERGY_FULL_SESSIONS pin,
K4-cp1-01, K4-cp2-01 and K4-cp3-01 (reports/stage_e4_member_specs.md sections 0-3 and 10).
K4-ovr-01 is in tests/test_e4_k4_members_a_ovr.py, which reuses this file's synthetic kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar). No bar file is read, no
runner is run, and no freeze is written into the repository (the freeze test writes under
tmp_path).
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
from strategy.members.k4 import cp1, cp2, cp3, ovr
from strategy.members.k4._calendar import (
    ENERGY_FULL_SESSIONS,
    ENERGY_FULL_SESSIONS_SOURCE,
    ENERGY_FULL_SESSIONS_SOURCE_SHA256,
)
from strategy.members.k4._port_common import EXPOSURES, exit_if_due, to_ticks
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
K4_DIR = REPO / "strategy" / "members" / "k4"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "ovr.py", "_calendar.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3, ovr)
ORDINAL_BASE = MappingProxyType({cp1: 1, cp2: 3, cp3: 5, ovr: 11})  # S0.2 table (MCL, then NG)
BASE_PRICE = MappingProxyType({"MCL": 70.0, "NG": 3.0})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


DAY_START, DAY_END = hm(7, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the Globex open of d, CT date d-1

# regular energy trade dates (EC-CAL full sessions, F 15:08)
MON, TUE, WED, THU = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4), date(2025, 6, 5)
HALT_DAY = date(2025, 5, 26)  # Memorial Day: an EC-CAL early halt, Topstep F 11:30 CT


def halt_label(day: date) -> str:
    halt = load_group_calendar("energy").early_halt_ct(day)
    assert halt is not None, day
    return halt.strftime("%H:%M")


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
    on the bars opening at ``force_at_ns`` while the leg holds exposure. MCL and NG are DCB-only
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
           instrument_id: int = 777, halt: time | None = None, base: int | None = None) -> Bar:
    b = base_ticks(root) if base is None else base
    fixed = product(root).vendor_tick_fixed
    o, h, lo, c = ((b + x) * fixed / PRICE_SCALE for x in offsets)
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, f"{root}Q5", day, False,
               False, halt, False, False, 0, False)


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k4/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K4") == []


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType) -> None:
    assert EXPOSURES == ("MCL", "NG")
    for root in EXPOSURES:
        member = vars(module)[f"make_{root.lower()}"]()
        assert isinstance(member, StageEMember)
        assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
        assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
        assert list(member.trading_windows) == [root]
    assert module.make_mcl() is not module.make_mcl()  # every call starts from fresh state
    assert not hasattr(module, "make_rb") and not hasattr(module, "make_ho")  # S0.1


def test_trading_windows_are_the_s0_12_intervals() -> None:
    for root in EXPOSURES:
        windows = {m: vars(m)[f"make_{root.lower()}"]().trading_windows[root] for m in MODULES}
        assert windows[cp1] == (TradingInterval(time(17, 0), time(17, 1), -1, -1),
                                TradingInterval(time(8, 29), time(8, 30)),
                                TradingInterval(time(12, 59), time(13, 30)))
        assert windows[cp2] == (TradingInterval(time(8, 0), time(15, 8)),)
        assert windows[cp3] == (TradingInterval(time(8, 0), time(13, 30)),)
        assert windows[ovr] == (TradingInterval(time(8, 0), time(14, 0)),)


def test_frozen_clock_and_size_are_o_0800_c_1330_and_q_c_4_mcl_1_ng() -> None:
    tables = load_frozen_tables()
    assert tables.day_session_ct["MCL"] == tables.day_session_ct["NG"] == (time(8, 0),
                                                                           time(13, 30))
    assert (tables.vehicles["MCL"].q_c, tables.vehicles["NG"].q_c) == (4, 1)


def test_the_8_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze (S0.2 ordinals) pass the real freeze code; the
    freeze is written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k4").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k4" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K4_DIR / name, members_dir / "k4" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ORDINAL_BASE[m] + i, m.__name__,
                        f"make_{root.lower()}", (LegSpec(root, True),))
             for m in MODULES for i, root in enumerate(EXPOSURES)]
    write_cluster_freeze("K4", decls, tmp_path)
    freeze = load_cluster_freeze("K4", tmp_path)
    verify_cluster_code(freeze)
    assert len(freeze.members) == 8
    assert freeze.member("K4-cp1-01 MCL").ordinal == 1
    assert freeze.member("K4-cp3-01 NG").ordinal == 6
    assert freeze.member("K4-ovr-01 MCL").ordinal == 11
    assert freeze.member("K4-ovr-01 NG").ordinal == 12


def test_prices_become_integer_vendor_ticks() -> None:
    for root in EXPOSURES:
        tick = product(root).vendor_tick
        b = base_ticks(root)
        assert to_ticks(float(b * tick), tick) == b
        assert to_ticks(float((b + 3) * tick), tick) == b + 3
        assert to_ticks(float((b - 7) * tick), tick) == b - 7


def test_a_none_bar_is_no_decision_and_changes_no_state() -> None:
    for module in MODULES:
        member = module.make_mcl()
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 59))
        assert member.on_minute(view_of("MCL", ts, None), account_of("MCL", 4)) == ()
        assert member.on_minute(view_of("MCL", ts, None), account_of("MCL")) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    bar = bar_at("MCL", TUE, hm(13, 28))
    view = view_of("MCL", bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of("MCL", 4, -4), "MCL", opened, TUE, time(13, 28)) == ()
    assert exit_if_due(view, account_of("MCL", 0, 4), "MCL", opened, TUE, time(13, 28)) == ()
    (intent,) = exit_if_due(view, account_of("MCL", -4), "MCL", opened, TUE, time(13, 28))
    assert (intent.side, intent.quantity) == ("buy", 4)
    assert exit_if_due(view, account_of("MCL", 4), "MCL", opened, TUE, time(13, 29)) == ()


# --------------------------------------------------------- ENERGY_FULL_SESSIONS pin ----
def test_energy_full_sessions_is_recomputed_from_ec_cal() -> None:
    """The pin: the literal table equals EC-CAL's trade dates over the calendar's own coverage,
    2019-05-01..2026-06-19 (K4-L-13), with no early halt, recomputed here from
    data.group_session, from the same calendar file."""
    cal = load_group_calendar("energy")
    assert tuple(cal.coverage) == (date(2019, 5, 1), date(2026, 6, 19))
    expected = tuple(d.isoformat() for d in trade_dates_between(cal, *cal.coverage)
                     if cal.early_halt_ct(d) is None)
    assert ENERGY_FULL_SESSIONS == expected
    assert (ENERGY_FULL_SESSIONS[0], ENERGY_FULL_SESSIONS[-1]) == ("2019-05-01", "2026-06-18")
    assert "2019-05-01, 2026-06-19" in ENERGY_FULL_SESSIONS_SOURCE
    assert ENERGY_FULL_SESSIONS_SOURCE_SHA256 == sha256_file(REPO / "data/calendars/energy.py")
    assert "load_group_calendar('energy')" in ENERGY_FULL_SESSIONS_SOURCE
    assert list(ENERGY_FULL_SESSIONS) == sorted(set(ENERGY_FULL_SESSIONS))


@pytest.mark.parametrize(("day", "listed"), [
    ("2025-07-03", True), ("2025-07-04", False),  # the July 4 early halt is not a full session
    ("2025-12-24", False), ("2025-12-25", False),  # early halt; full closure
    ("2025-04-18", False), ("2026-06-18", True), ("2026-06-19", False),  # closure; halt
    ("2025-07-05", False),  # a Saturday
    # K4-L-13: nothing outside EC-CAL's coverage (2019-04-19 is Good Friday, a CME closure the
    # calendar does not cover); the first covered date is listed
    ("2019-04-19", False), ("2019-04-30", False), ("2019-05-01", True), ("2026-06-22", False),
    ("2026-06-30", False)])
def test_energy_full_sessions_spot_checks(day: str, listed: bool) -> None:
    assert (day in ENERGY_FULL_SESSIONS) is listed


# ------------------------------------------------------------------------ K4-cp1-01 ----
# 17:00 bar (d-1): open B, close B+10. 08:29 bar: open B-5, close B+3. D6's s = close(08:29) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}
CP1_BUY_DAY = {hm(8, 29): (-5, 3, -5, 3)}


def cp1_day(day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", CP1_BUY_DAY)
    return Day(day, **kw)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_buys_on_a_positive_signal_at_1300_and_exits_at_1329(root: str) -> None:
    # MON: the Globex open is Sunday 17:00 CT, the calendar day before d
    res = run(vars(cp1)[f"make_{root.lower()}"](), [cp1_day(MON)])
    assert fills(res) == trade(MON, "13:00", "13:29", "buy")
    assert intents(res) == [(MON, "12:59", True, None), (MON, "13:28", True, None)]
    q_c = {"MCL": 4, "NG": 1}[root]
    assert [f.qty for f in res.events(Fill)] == [q_c, q_c]


def test_cp1_sells_on_a_negative_signal() -> None:
    # s = close(08:29) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)}, paths={hm(8, 29): (5, 5, -3, -3)})
    assert fills(run(cp1.make_mcl(), [day])) == trade(TUE, "13:00", "13:29", "sell")


def test_cp1_zero_signal_is_no_trade() -> None:
    day = cp1_day(paths={hm(8, 29): (-5, 0, -5, 0)})  # close(08:29) = open(17:00)
    assert intents(run(cp1.make_mcl(), [day])) == []


def test_cp1_missing_globex_open_bar_is_no_trade_l05() -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; E.3-L-05 names the 17:00 bar only
    res = run(cp1.make_mcl(), [cp1_day(evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_0829_signal_bar_is_no_trade() -> None:
    res = run(cp1.make_ng(), [cp1_day(skip=frozenset({hm(8, 29)}))])
    assert intents(res) == []


def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06() -> None:
    evening_differs = cp1_day(evening_id=776)
    signal_differs = cp1_day(ids={hm(8, 29): 778})
    assert intents(run(cp1.make_mcl(), [evening_differs])) == []
    assert intents(run(cp1.make_mcl(), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_differs = cp1_day(ids={m: 778 for m in range(hm(12, 59), DAY_END)})
    assert fills(run(cp1.make_mcl(), [entry_differs])) == trade(TUE, "13:00", "13:29")


def test_cp1_missing_1259_entry_bar_is_no_trade_l04() -> None:
    res = run(cp1.make_mcl(), [cp1_day(skip=frozenset({hm(12, 59)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_1328_bar_sends_the_exit_on_1329() -> None:
    res = run(cp1.make_mcl(), [cp1_day(skip=frozenset({hm(13, 28)}))])
    assert fills(res) == trade(TUE, "13:00", "13:30")
    assert intents(res)[-1] == (TUE, "13:29", True, None)


def test_cp1_a_refused_exit_is_resent_on_the_next_bar() -> None:
    # no bars 13:00..13:27: the entry fills at the 13:28 open, so the 13:28 exit comes 1 minute
    # after the fill (engine_min_hold, D9.3b); it is sent again on 13:29 and fills at 13:30
    res = run(cp1.make_mcl(), [cp1_day(skip=frozenset(range(hm(13, 0), hm(13, 28))))])
    assert intents(res) == [(TUE, "12:59", True, None), (TUE, "13:28", False, "engine_min_hold"),
                            (TUE, "13:29", True, None)]
    assert fills(res) == trade(TUE, "13:28", "13:30")


def test_cp1_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    # a release at 13:00 CT (an FOMC statement minute): the 13:00 entry fill waits for 13:02
    res = run(cp1.make_mcl(), [cp1_day()], releases=release_at("MCL", TUE, 13, 0))
    assert fills(res) == trade(TUE, "13:02", "13:29")
    assert res.counters["fill_guard_deferral"] == 2


def test_cp1_a_release_next_to_the_fill_leaves_it_alone() -> None:
    # guard [12:58, 13:00) ends before the 13:00 fill; guard [13:01, 13:03) starts after it
    for hh, mm in ((12, 58), (13, 1)):
        res = run(cp1.make_mcl(), [cp1_day()], releases=release_at("MCL", TUE, hh, mm))
        assert fills(res) == trade(TUE, "13:00", "13:29")


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp1.make_mcl(), [cp1_day(flatten_from=hm(13, 15))])
    assert fills(res) == trade(TUE, "13:00", "13:16", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["12:59"]  # the member sends no exit of its own


def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [cp1_day()]
    member = cp1.make_mcl()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(13, 10))]))
    assert fills(res) == trade(TUE, "13:00", "13:11", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["12:59"]  # no 13:28 exit, no second entry


def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry() -> None:
    # 2025-05-26 (Memorial Day): F 11:30. CP1 is a port (C line 85): it emits at 12:59 and the
    # engine refuses it (the Globex open is Sunday 05-25 17:00)
    day = cp1_day(HALT_DAY, halt=halt_label(HALT_DAY))
    res = run(cp1.make_mcl(), [day])
    assert intents(res) == [(HALT_DAY, "12:59", False, "engine_flatten_window")]
    assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(cp1.make_mcl(), [cp1_day(TUE), cp1_day(WED)])
    assert fills(res) == trade(TUE, "13:00", "13:29") + trade(WED, "13:00", "13:29")


# ------------------------------------------------------------------------ K4-cp2-01 ----
# OR bars [08:00, 08:15): the 08:05 high is B+2, the 08:10 low is B-2 (the others at B)
CP2_OR = {hm(8, 5): (0, 2, 0, 0), hm(8, 10): (0, 0, -2, 0)}
UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


def test_cp2_buffer_literals_are_4_vendor_ticks_k4_l06() -> None:
    assert cp2.BUFFER_TICKS == 4
    assert cp2.BUFFER_TICKS * product("MCL").vendor_tick == Decimal("0.04")
    assert cp2.BUFFER_TICKS * product("NG").vendor_tick == Decimal("0.004")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    res = run(vars(cp2)[f"make_{root.lower()}"](), [cp2_day({hm(8, 15): UP4})])
    assert fills(res) == trade(TUE, "08:16", "09:31", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "08:15", True, None), (TUE, "09:30", True, None)]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_the_buffer_is_exactly_four_ticks_either_side(root: str) -> None:
    up3, down3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks beyond: no entry
    make = vars(cp2)[f"make_{root.lower()}"]
    res_up = run(make(), [cp2_day({hm(8, 20): up3, hm(8, 30): UP4})])
    res_down = run(make(), [cp2_day({hm(8, 20): down3, hm(8, 30): DOWN4})])
    assert fills(res_up) == trade(TUE, "08:31", "09:46", "buy")
    assert fills(res_down) == trade(TUE, "08:31", "09:46", "sell")


def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4}, skip=frozenset({hm(8, 45)}))])
    assert fills(res) == trade(TUE, "08:16", "09:32")


def test_cp2_has_no_c_minus_2_exit() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(13, 0): UP4})])
    assert fills(res) == trade(TUE, "13:01", "14:16")  # not 13:29


def test_cp2_no_entry_from_1330() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(13, 30): UP4, hm(13, 35): UP4})])
    assert intents(res) == []


def test_cp2_the_last_eligible_bar_1329_exits_75_bars_later() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(13, 29): UP4})])
    assert fills(res) == trade(TUE, "13:30", "14:45")


def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4}, flatten_from=hm(9, 0))])
    assert fills(res) == trade(TUE, "08:16", "09:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:15"]


def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it() -> None:
    # TUE is not a window date: the 08:15 trigger is refused, the 08:25 trigger is not sent
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4, hm(8, 25): UP4})], window=[MON])
    assert intents(res) == [(TUE, "08:15", False, "engine_not_a_window_date")]


def test_cp2_one_entry_per_trade_date_after_the_exit() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4, hm(10, 0): UP4, hm(11, 0): DOWN4})])
    assert fills(res) == trade(TUE, "08:16", "09:31")


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    day = cp2_day({hm(8, 15): UP4, hm(9, 0): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(8, 0), hm(8, 15))))
    assert intents(run(cp2.make_mcl(), [day])) == []


def test_cp2_the_range_is_taken_from_the_present_bars() -> None:
    # the 08:05 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day({hm(8, 15): (0, 4, 0, 4)}, skip=frozenset({hm(8, 5)}))
    assert fills(run(cp2.make_mcl(), [day])) == trade(TUE, "08:16", "09:31")
    full = cp2_day({hm(8, 15): (0, 4, 0, 4)})
    assert intents(run(cp2.make_mcl(), [full])) == []


def test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day({hm(7, 50): (0, 30, -30, 0), hm(8, 15): UP4},
                  evening={hm(17, 0): (0, 30, -30, 0)})
    assert fills(run(cp2.make_mcl(), [day])) == trade(TUE, "08:16", "09:31")


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 08:16 CT: the entry fills at 08:18 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4})],
              releases=release_at("MCL", TUE, 8, 16))
    assert fills(res) == trade(TUE, "08:18", "09:33")


def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [cp2_day({hm(8, 15): UP4, hm(10, 0): UP4, hm(11, 0): DOWN4})]
    member = cp2.make_mcl()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(8, 40))]))
    assert fills(res) == trade(TUE, "08:16", "08:41", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:15"]


def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f() -> None:
    # 2025-05-26 (F 11:30): the port trades; the engine's flatten closes the position at F
    day = cp2_day({hm(10, 30): UP4}, HALT_DAY, halt=halt_label(HALT_DAY))
    res = run(cp2.make_mcl(), [day])
    assert intents(res)[0] == (HALT_DAY, "10:30", True, None)
    assert fills(res) == trade(HALT_DAY, "10:31", "11:30", exit_reason="forced_flatten")


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(cp2.make_mcl(), [cp2_day({hm(8, 15): UP4}), cp2_day({hm(9, 0): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "08:16", "09:31") + trade(WED, "09:01", "10:16", "sell")


# ------------------------------------------------------------------------ K4-cp3-01 ----
def daily(high: int, low: int, close: int, **kw: Any) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (13:29 close) = B+close, plus two
    extreme bars OUTSIDE [08:00, 13:30) that must not enter it."""
    return {hm(7, 50): (0, 50, -50, 0), hm(13, 45): (0, 50, -50, 0),
            hm(10, 0): (0, high, 0, 0), hm(11, 0): (0, 0, low, 0),
            hm(13, 29): (0, max(0, close), min(0, close), close), **kw}


BUY_08 = daily(10, 0, 8)  # CLV = 8/10 = 0.8 exactly
SELL_02 = daily(10, 0, 2)  # CLV = 2/10 = 0.2 exactly


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_08_buys_on_the_0800_bar_and_exits_at_1329(root: str) -> None:
    res = run(vars(cp3)[f"make_{root.lower()}"](), [Day(MON, BUY_08), Day(TUE)])
    assert fills(res) == trade(TUE, "08:01", "13:29", "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, "08:00", True, None), (TUE, "13:28", True, None)]


def test_cp3_prior_clv_at_02_sells() -> None:
    res = run(cp3.make_mcl(), [Day(MON, SELL_02), Day(TUE)])
    assert fills(res) == trade(TUE, "08:01", "13:29", "sell")


@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(close: int) -> None:
    assert intents(run(cp3.make_mcl(), [Day(MON, daily(10, 0, close)), Day(TUE)])) == []


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


def test_cp3_zero_range_is_no_trade() -> None:
    flat = {hm(7, 50): (0, 50, -50, 0)}  # the only non-flat bar is outside [08:00, 13:30)
    assert intents(run(cp3.make_mcl(), [Day(MON, flat), Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(TUE, "08:01", "13:29", "buy") + trade(WED, "08:01", "13:29",
                                                                     "sell")


def test_cp3_d_minus_1_is_the_most_recent_complete_day() -> None:
    # TUE lacks its 13:29 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade"
    tue = Day(TUE, SELL_02, skip=frozenset({hm(13, 29)}))
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), tue, Day(WED)])
    # TUE's exit, decided on 13:28, fills at the next present bar (13:30)
    assert fills(res) == trade(TUE, "08:01", "13:30", "buy") + trade(WED, "08:01", "13:29",
                                                                     "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(9, 0): 778})  # one bar in [08:00, 13:30) differs
    res = run(cp3.make_mcl(), [mon, Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(WED, "08:01", "13:29", "sell")  # TUE: no complete d-1 yet


def test_cp3_instrument_guard_compares_d_minus_1_with_the_0800_bar() -> None:
    tue = Day(TUE, BUY_08, instrument_id=778)
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, "08:01", "13:29", "buy")  # TUE refused by the guard


def test_cp3_missing_0800_bar_is_no_trade_and_the_day_is_incomplete() -> None:
    tue = Day(TUE, SELL_02, skip=frozenset({hm(8, 0)}))
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(WED, "08:01", "13:29", "buy")  # WED's d-1 is MON


def test_cp3_early_halt_day_is_not_traded_and_is_incomplete() -> None:
    # 2025-05-26 (Memorial Day, F 11:30): bars kept to 15:12 so it would be complete but for its
    # halt; the engine would accept an 08:00 entry, so the member's own test is what blocks it
    fri, tue = date(2025, 5, 23), date(2025, 5, 27)
    label = halt_label(HALT_DAY)
    days = [Day(fri, BUY_08), Day(HALT_DAY, SELL_02, halt=label),
            Day(tue, evening_halt=label)]
    res = run(cp3.make_mcl(), days)
    assert [i for i in intents(res) if i[0] == HALT_DAY] == []
    assert fills(res) == trade(tue, "08:01", "13:29", "buy")  # d-1 of 05-27 is 05-23


def test_cp3_missing_1328_bar_sends_the_exit_on_1329() -> None:
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), Day(TUE, skip=frozenset({hm(13, 28)}))])
    assert fills(res) == trade(TUE, "08:01", "13:30")


def test_cp3_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), Day(TUE)],
              releases=release_at("MCL", TUE, 8, 1))
    assert fills(res) == trade(TUE, "08:03", "13:29")


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp3.make_mcl(), [Day(MON, BUY_08), Day(TUE, flatten_from=hm(13, 0))])
    assert fills(res) == trade(TUE, "08:01", "13:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:00"]


def test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [Day(MON, BUY_08), Day(TUE)]
    member = cp3.make_mcl()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 30))]))
    assert fills(res) == trade(TUE, "08:01", "09:31", exit_reason="price_limit_exit")
    assert [i[:2] for i in intents(res)] == [(TUE, "08:00")]
