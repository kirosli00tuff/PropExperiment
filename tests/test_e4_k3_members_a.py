"""Stage E.4 Part 3, K3 members of MemberCoder-A, part 1: the synthetic kit, the declarations, the
CP2 buffer-table pin and K3-cp1-01 (reports/stage_e4c_member_specs.md sections 0-3 and 10).
K3-cp2-01 is in tests/test_e4_k3_members_a_cp2.py and K3-cp3-01 in
tests/test_e4_k3_members_a_cp3.py; both reuse this file's kit (adapted from
tests/test_e4_k5_members_a.py, not imported from it).

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar). No bar file is read, no
runner is run, and no freeze is written into the repository (the freeze test writes under
tmp_path). All seven FX roots share D6's FX row (O 07:20, C 14:00, F 15:08); the expected clock
times are written out as literals, not derived from the code's own arithmetic.
"""

from __future__ import annotations

import hashlib
import json
import re
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

from data.group_session import load_group_calendar, trade_dates_between
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
from strategy.members.k3 import _port_common, cp1, cp2, cp3
from strategy.members.k3._port_common import EXPOSURES, exit_if_due, leg_facts, to_ticks
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
K3_DIR = REPO / "strategy" / "members" / "k3"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3)
# S0.2: ordinals in catalog order, then the exposure order 6E, 6A, 6B, 6C, 6J, 6S, 6N
ORDINAL_BASE = MappingProxyType({cp1: 1, cp2: 8, cp3: 15})
ROOT_ORDER = ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
BASE_PRICE = MappingProxyType({"6E": 1.1, "6A": 0.65, "6B": 1.3, "6C": 0.73, "6J": 0.0067,
                               "6S": 1.15, "6N": 0.6})
VENDOR_TICK = MappingProxyType({  # specs lines 29-30 (the frozen per-root values)
    "6E": Decimal("0.00005"), "6A": Decimal("0.00005"), "6B": Decimal("0.0001"),
    "6C": Decimal("0.00005"), "6J": Decimal("0.0000005"), "6S": Decimal("0.00005"),
    "6N": Decimal("0.00005")})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


O_MIN, C_MIN = hm(7, 20), hm(14, 0)  # D6's FX O and C (frozen day_session_ct; pinned below)
DAY_START, DAY_END = hm(7, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the Globex open of d, CT date d-1

# regular FX trade dates in CDT (F 15:08)
MON, TUE, WED, THU = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4), date(2025, 6, 5)
# both clock regimes: a CST date, two US/UK (and US/ECB) mismatch weeks, and the two Mondays
# whose Globex open falls on a US clock-change Sunday
CLOCK_DAYS = (date(2026, 1, 13),  # CST, London on GMT (7 h apart)
              date(2025, 6, 3),  # CDT, London on BST (6 h apart)
              date(2026, 3, 10),  # CDT, London still on GMT (5 h apart; UK switches 03-29)
              date(2025, 10, 28),  # CDT, London back on GMT (5 h apart; US switches 11-02)
              date(2026, 3, 9),  # Monday: Globex open Sunday 03-08 17:00 CDT (spring forward)
              date(2025, 11, 3))  # Monday: Globex open Sunday 11-02 17:00 CST (fall back)
# EC-CAL FX's research-window early halts (specs line 36) with the trade date before and the next
# trade date after each; Topstep F from rules.sessions (08:00 on 2026-04-03, else 11:30 / 11:45)
FX_HALTS = MappingProxyType({
    date(2025, 7, 4): (date(2025, 7, 3), date(2025, 7, 7), "11:30"),
    date(2025, 11, 28): (date(2025, 11, 27), date(2025, 12, 1), "11:45"),
    date(2025, 12, 24): (date(2025, 12, 23), date(2025, 12, 26), "11:45"),
    date(2026, 4, 3): (date(2026, 4, 2), date(2026, 4, 6), "08:00"),
    date(2026, 6, 19): (date(2026, 6, 18), date(2026, 6, 22), "11:45")})


def halt_label(day: date) -> str:
    halt = load_group_calendar("fx").early_halt_ct(day)
    assert halt is not None, day
    return halt.strftime("%H:%M")


def make(module: ModuleType, root: str) -> Any:
    return vars(module)[f"make_{root.lower()}"]()


def hhmm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars: an evening segment [17:00, 17:05) on CT date d-1 and a
    day segment [start, end) on CT date d, flat at the root's base price unless ``paths`` or
    ``evening`` override a minute (tick offsets from the base)."""

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
            "instrument_id": ids.get(minute, default_id), "raw_symbol": f"{root}M5",
            "trade_date": trade_day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(root: str, days: Sequence[Day]) -> pd.DataFrame:
    rows: list[dict] = []
    for d in days:
        eve_id = d.instrument_id if d.evening_id is None else d.evening_id
        rows += _rows(root, d.trade_date, d.trade_date - timedelta(days=1),
                      range(EVENING_START, EVENING_END), d.evening, d.evening_skip, {},
                      eve_id, d.evening_halt, None)
        rows += _rows(root, d.trade_date, d.trade_date, range(d.start, d.end), d.paths, d.skip,
                      d.ids, d.instrument_id, d.halt, d.flatten_from)
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
    on the bars opening at ``force_at_ns`` while the leg holds exposure. No FX root is in
    rules.price_limits.HARD_LIMIT_PRODUCTS (C11), so the real D9.7 exit cannot fire on them;
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
    return Bar(ns_at(day, minute), o, h, lo, c, 10, instrument_id, f"{root}M5", day, False,
               False, halt, False, False, 0, False)


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k3/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K3") == []


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType) -> None:
    assert EXPOSURES == ROOT_ORDER  # S0.2: EUR, AUD, GBP, CAD, JPY, CHF, NZD
    for root in EXPOSURES:
        member = make(module, root)
        assert isinstance(member, StageEMember)
        assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
        assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
        assert list(member.trading_windows) == [root]
    assert module.make_6e() is not module.make_6e()  # every call starts from fresh state
    for other in ("make_e7", "make_m6e", "make_m6a", "make_m6b", "make_zn"):  # S0.1, S0.13
        assert not hasattr(module, other)


def test_leg_facts_refuses_a_root_outside_the_seven_vehicles() -> None:
    for other in ("E7", "M6E", "M6A", "M6B", "ZN", "MES"):
        with pytest.raises(ValueError, match="not a K3 exposure"):
            leg_facts(other)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    expected = {
        cp1: (TradingInterval(time(17, 0), time(17, 1), -1, -1),
              TradingInterval(time(7, 49), time(7, 50)),
              TradingInterval(time(13, 29), time(14, 0))),
        cp2: (TradingInterval(time(7, 20), time(15, 8)),),
        cp3: (TradingInterval(time(7, 20), time(14, 0)),)}
    for root in EXPOSURES:
        for module in MODULES:
            assert make(module, root).trading_windows == {root: expected[module]}


def test_frozen_clock_size_and_ticks_are_the_spec_values() -> None:
    tables = load_frozen_tables()
    for root in EXPOSURES:
        assert tables.day_session_ct[root] == (time(7, 20), time(14, 0))  # D line 394
        assert tables.vehicles[root].q_c == 1  # S0.3: 1 on all seven, never a literal
        assert product(root).vendor_tick == VENDOR_TICK[root]
        assert root not in HARD_LIMIT_PRODUCTS  # C11: tests use ForcedLimitRules for D9.7
        facts = leg_facts(root)
        assert (facts.o, facts.c, facts.q, facts.tick) == (time(7, 20), time(14, 0), 1,
                                                           VENDOR_TICK[root])


def test_the_21_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze (S0.2 ordinals 1-21) pass the real freeze code; the
    freeze is written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k3").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k3" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K3_DIR / name, members_dir / "k3" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ORDINAL_BASE[m] + i, m.__name__,
                        f"make_{root.lower()}", (LegSpec(root, True),))
             for m in MODULES for i, root in enumerate(EXPOSURES)]
    write_cluster_freeze("K3", decls, tmp_path)
    freeze = load_cluster_freeze("K3", tmp_path)
    verify_cluster_code(freeze)
    assert len(freeze.members) == 21
    ordinals = {m.label: m.ordinal for m in freeze.members}
    assert (ordinals["K3-cp1-01 6E"], ordinals["K3-cp1-01 6N"]) == (1, 7)
    assert (ordinals["K3-cp2-01 6E"], ordinals["K3-cp2-01 6J"]) == (8, 12)
    assert (ordinals["K3-cp3-01 6E"], ordinals["K3-cp3-01 6N"]) == (15, 21)
    assert sorted(ordinals.values()) == list(range(1, 22))


def test_prices_become_integer_vendor_ticks() -> None:
    for root in EXPOSURES:
        tick = product(root).vendor_tick
        b = base_ticks(root)
        assert to_ticks(float(b * tick), tick) == b
        assert to_ticks(float((b + 3) * tick), tick) == b + 3
        assert to_ticks(float((b - 7) * tick), tick) == b - 7
        # a float sum that misses the grid in its last bits still lands on the right tick
        buffered = float(b * tick) + float(4 * tick)
        assert to_ticks(buffered, tick) == b + 4


@pytest.mark.parametrize("root", EXPOSURES)
def test_a_none_bar_is_no_decision_and_changes_no_state(root: str) -> None:
    for module in MODULES:
        member = make(module, root)
        before = repr(vars(member))
        ts = ns_at(TUE, hm(8, 19))
        assert member.on_minute(view_of(root, ts, None), account_of(root, 1)) == ()
        assert member.on_minute(view_of(root, ts, None), account_of(root)) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    bar = bar_at("6E", TUE, hm(13, 58))
    view = view_of("6E", bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of("6E", 1, -1), "6E", opened, TUE, time(13, 58)) == ()
    assert exit_if_due(view, account_of("6E", 0, 1), "6E", opened, TUE, time(13, 58)) == ()
    (intent,) = exit_if_due(view, account_of("6E", -1), "6E", opened, TUE, time(13, 58))
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert exit_if_due(view, account_of("6E", 1), "6E", opened, TUE, time(13, 59)) == ()
    assert exit_if_due(view, account_of("6E", 1), "6E", opened, WED, time(13, 58)) == ()


def test_the_port_helpers_are_copied_not_imported() -> None:
    """Copy, never import (the brief): no K3 file of coder A names k2, k4 or k5."""
    for name in CODER_A_FILES:
        text = (K3_DIR / name).read_text(encoding="utf-8")
        assert re.search(r"^\s*(from|import)\s+strategy\.members\.k[245]", text, re.M) is None
    assert _port_common.EXPOSURES == ROOT_ORDER


# ------------------------------------------------------ the CP2 buffer table pin ----
CATALOG = REPO / "reports" / "stage_e0_catalog_K3.md"
EXPOSURE_ROOT = MappingProxyType({"EUR": "6E", "AUD": "6A", "GBP": "6B", "CAD": "6C",
                                  "JPY": "6J", "CHF": "6S", "NZD": "6N"})


def test_cp2_buffer_table_is_recomputed_from_the_frozen_catalog() -> None:
    """The pin: the catalog's buffer table (C lines 304-312, frozen by reports/stage_e1_freeze.json)
    names each exposure's most active contract and its 4-tick buffer in price units; the code's
    BUFFER_TICKS x the vehicle's vendor tick equals it on all seven (K4-L-06)."""
    raw = CATALOG.read_bytes()
    frozen = json.loads((REPO / "reports" / "stage_e1_freeze.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == frozen["files"][
        "reports/stage_e0_catalog_K3.md"]["sha256"]
    lines = raw.decode("utf-8").splitlines()
    assert lines[303].strip().startswith("| Exposure | Most active | Buffer (price units) |")
    table = {}
    for line in lines[305:312]:
        exposure, most_active, buffer, _ = (c.strip() for c in line.strip().strip("|").split("|"))
        table[exposure] = (most_active, Decimal(buffer))
    assert list(table) == list(EXPOSURE_ROOT)  # the catalog's exposure order
    for exposure, (most_active, buffer) in table.items():
        root = EXPOSURE_ROOT[exposure]
        assert most_active == root  # the most active contract is the vehicle (S0.1)
        assert cp2.BUFFER_TICKS * product(root).vendor_tick == buffer
    assert {r: cp2.BUFFER_TICKS * VENDOR_TICK[r] for r in ("6E", "6B", "6J")} == {
        "6E": Decimal("0.0002"), "6B": Decimal("0.0004"), "6J": Decimal("0.000002")}


def test_ec_cal_fx_research_window_halts_are_the_spec_dates() -> None:
    """The five halt dates this file uses (specs line 36) are EC-CAL FX's, recomputed here."""
    cal = load_group_calendar("fx")
    days = trade_dates_between(cal, date(2025, 4, 1), date(2026, 6, 19))
    assert len(days) == 316
    halts = {d: cal.early_halt_ct(d) for d in days if cal.early_halt_ct(d) is not None}
    assert sorted(halts) == sorted(FX_HALTS)
    for day, (before, after, f) in FX_HALTS.items():
        i = days.index(day)
        assert days[i - 1] == before  # the trade date before the halt
        # the next trade date; 2026-06-19 ends EC-CAL's coverage, so its "after" is the Monday
        assert (days[i + 1] if i + 1 < len(days) else date(2026, 6, 22)) == after
        first_flat = next(m for m in range(DAY_START, DAY_END) if sessions.session_state(
            "6E", datetime.combine(day, time(m // 60, m % 60), tzinfo=CT)).must_be_flat)
        assert hhmm(first_flat) == f


# ------------------------------------------------------------------------ K3-cp1-01 ----
# The spec's clock (section 1-3 table): signal 17:00 bar of d-1 to 07:49; entry 13:29 (fills at
# 13:30); exit on the first bar at or after 13:58 (fills at 13:59)
CP1_SIGNAL, CP1_ENTRY, CP1_EXIT = hm(7, 49), hm(13, 29), hm(13, 58)
# 17:00 bar (d-1): open B, close B+10. Signal bar: open B-5, close B+3. D6's s = close(signal) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}


def cp1_day(day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", {CP1_SIGNAL: (-5, 3, -5, 3)})
    return Day(day, **kw)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_buys_on_a_positive_signal_with_the_spec_clock(root: str) -> None:
    # MON: the Globex open is Sunday 17:00 CT, the calendar day before d
    res = run(make(cp1, root), [cp1_day(MON)])
    assert fills(res) == trade(MON, "13:30", "13:59", "buy")
    assert intents(res) == [(MON, "13:29", True, None), (MON, "13:58", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_sells_on_a_negative_signal(root: str) -> None:
    # s = close(signal) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)}, paths={CP1_SIGNAL: (5, 5, -3, -3)})
    res = run(make(cp1, root), [day])
    assert fills(res) == trade(TUE, "13:30", "13:59", "sell")


@pytest.mark.parametrize("day", CLOCK_DAYS, ids=str)
def test_cp1_keeps_the_ct_clock_in_both_regimes(day: date) -> None:
    """The port reads CT only: the same 17:00 / 07:49 / 13:29 / 13:58 bars in CST, CDT, the
    US/UK mismatch weeks and across a US clock-change Sunday."""
    for root in EXPOSURES:
        res = run(make(cp1, root), [cp1_day(day)])
        assert fills(res) == trade(day, "13:30", "13:59", "buy"), root
        assert intents(res) == [(day, "13:29", True, None), (day, "13:58", True, None)]
    # the signal bar is the 07:49 CT bar: a sell-signal bar one hour off (08:49) changes nothing
    res = run(cp1.make_6e(), [cp1_day(day, paths={CP1_SIGNAL: (-5, 3, -5, 3),
                                                  hm(8, 49): (0, 0, -30, -30)})])
    assert fills(res) == trade(day, "13:30", "13:59", "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_zero_signal_is_no_trade(root: str) -> None:
    day = cp1_day(paths={CP1_SIGNAL: (-5, 0, -5, 0)})  # close = open(17:00)
    assert intents(run(make(cp1, root), [day])) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_globex_open_bar_is_no_trade_l05(root: str) -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; E.3-L-05 names the 17:00 bar only
    res = run(make(cp1, root), [cp1_day(evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_signal_bar_is_no_trade(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(skip=frozenset({CP1_SIGNAL}))])
    assert intents(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06(root: str) -> None:
    evening_differs = cp1_day(evening_id=776)
    signal_differs = cp1_day(ids={CP1_SIGNAL: 778})
    assert intents(run(make(cp1, root), [evening_differs])) == []
    assert intents(run(make(cp1, root), [signal_differs])) == []
    # the entry bar is not guarded (E.3-L-06): only the two signal bars must agree
    entry_differs = cp1_day(ids={m: 778 for m in range(CP1_ENTRY, DAY_END)})
    assert fills(run(make(cp1, root), [entry_differs])) == trade(TUE, "13:30", "13:59")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_entry_bar_is_no_trade_l04(root: str) -> None:
    # no entry on a later bar: 13:30 would be a bar the entry never names
    res = run(make(cp1, root), [cp1_day(skip=frozenset({CP1_ENTRY}))])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_missing_exit_bar_sends_the_exit_on_the_next_present_bar(root: str) -> None:
    res = run(make(cp1, root), [cp1_day(skip=frozenset({CP1_EXIT}))])
    assert fills(res) == trade(TUE, "13:30", "14:00")
    assert intents(res)[-1] == (TUE, "13:59", True, None)
    # two missing bars: the exit goes on 14:00 and fills at 14:01
    res2 = run(make(cp1, root), [cp1_day(skip=frozenset({CP1_EXIT, CP1_EXIT + 1}))])
    assert fills(res2) == trade(TUE, "13:30", "14:01")


def test_cp1_a_refused_exit_is_resent_on_the_next_bar() -> None:
    # no 6J bars 13:30..13:57: the entry fills at the 13:58 open, so the 13:58 exit comes 1
    # minute after the fill (engine_min_hold, D9.3b); it is sent again on 13:59, fills at 14:00
    res = run(cp1.make_6j(), [cp1_day(skip=frozenset(range(hm(13, 30), hm(13, 58))))])
    assert intents(res) == [(TUE, "13:29", True, None), (TUE, "13:58", False, "engine_min_hold"),
                            (TUE, "13:59", True, None)]
    assert fills(res) == trade(TUE, "13:58", "14:00")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_fill_in_the_d95a_guard_waits_two_minutes(root: str) -> None:
    # a release at the entry fill minute (13:30): the fill waits for release + 2 min
    res = run(make(cp1, root), [cp1_day()], releases=release_at(root, TUE, 13, 30))
    assert fills(res) == trade(TUE, "13:32", "13:59")
    assert res.counters["fill_guard_deferral"] == 2
    # a release at 13:29 (guard [13:29, 13:31)) also holds the 13:30 fill, to 13:31
    res29 = run(make(cp1, root), [cp1_day()], releases=release_at(root, TUE, 13, 29))
    assert fills(res29) == trade(TUE, "13:31", "13:59")


def test_cp1_a_release_next_to_or_before_the_fill_leaves_it_alone() -> None:
    # guard [13:28, 13:30) ends before the 13:30 fill; guard [13:31, 13:33) starts after it;
    # the 13:00 FOMC statement (catalog section 7 item 9) and the 07:30 BLS release sit in the
    # member's windows but meet no fill; the signal bars are read as they are
    for hh, mm in ((13, 28), (13, 31), (13, 0), (7, 30), (7, 49)):
        res = run(cp1.make_6e(), [cp1_day()], releases=release_at("6E", TUE, hh, mm))
        assert fills(res) == trade(TUE, "13:30", "13:59"), (hh, mm)
        assert res.counters.get("fill_guard_deferral", 0) == 0


def test_cp1_a_release_at_the_exit_fill_holds_the_exit() -> None:
    res = run(cp1.make_6b(), [cp1_day()], releases=release_at("6B", TUE, 13, 59))
    assert fills(res) == trade(TUE, "13:30", "14:01")
    assert [i[1] for i in intents(res)] == ["13:29", "13:58"]  # pending: no resend


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp1.make_6e(), [cp1_day(flatten_from=hm(13, 45))])
    assert fills(res) == trade(TUE, "13:30", "13:46", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["13:29"]  # the member sends no exit of its own


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [cp1_day()]
    member = make(cp1, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(13, 40))]))
    assert fills(res) == trade(TUE, "13:30", "13:41", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["13:29"]  # no exit, no second entry


@pytest.mark.parametrize("halt_day", list(FX_HALTS), ids=str)
def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry(halt_day: date) -> None:
    # every research-window FX halt has F at or before 11:45: CP1 is a port (C lines 49-50), it
    # emits on 13:29 and the engine refuses the entry in the flatten window
    for root in EXPOSURES:
        day = cp1_day(halt_day, halt=halt_label(halt_day))
        res = run(make(cp1, root), [day])
        assert intents(res) == [(halt_day, "13:29", False, "engine_flatten_window")]
        assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(cp1.make_6a(), [cp1_day(TUE), cp1_day(WED), cp1_day(THU)])
    assert fills(res) == (trade(TUE, "13:30", "13:59") + trade(WED, "13:30", "13:59")
                          + trade(THU, "13:30", "13:59"))


def test_cp1_state_resets_each_trade_date() -> None:
    # WED lacks its Globex-open bar: TUE's first bar is not carried over
    res = run(cp1.make_6c(), [cp1_day(TUE), cp1_day(WED, evening_skip=frozenset({hm(17, 0)}))])
    assert fills(res) == trade(TUE, "13:30", "13:59")


def test_cp1_a_roll_blackout_date_refuses_the_entry_and_nothing_is_resent() -> None:
    days = [cp1_day(TUE), cp1_day(WED)]
    member = cp1.make_6s()
    res = run(member, days, rules=blackout_rules(member, days, [TUE]))
    assert intents(res)[0] == (TUE, "13:29", False, "engine_roll_blackout")
    assert fills(res) == trade(WED, "13:30", "13:59")
