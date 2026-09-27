"""Stage E.3 K2 members of MemberCoder-A: K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-monthend-01, and the
month-end table pin (reports/stage_e3_member_specs.md sections 0-3, 8 and 10).

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
a few direct calls where the engine cannot reach a case (a None bar). No bar file is read, no
runner is run, and no freeze is written into the repository (the freeze test writes under
tmp_path).
"""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

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
from screening.stage_e_rules import ReleaseCalendar
from strategy.interface import Bar
from strategy.members.k2 import cp1, cp2, cp3, monthend
from strategy.members.k2._month_end import MONTH_END, MONTH_END_SOURCE_SHA256
from strategy.members.k2._port_common import EXPOSURES, exit_if_due, to_ticks
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
K2_DIR = REPO / "strategy" / "members" / "k2"
CODER_A_FILES = ("cp1.py", "cp2.py", "cp3.py", "monthend.py", "_month_end.py", "_port_common.py")
MODULES: tuple[ModuleType, ...] = (cp1, cp2, cp3, monthend)
ORDINAL_BASE = MappingProxyType({cp1: 1, cp2: 7, cp3: 13, monthend: 39})  # S0.2 table
BASE_PRICE = MappingProxyType({"ZT": 104.0, "ZF": 108.0, "ZN": 110.0, "TN": 112.0, "ZB": 115.0,
                               "UB": 120.0})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


DAY_START, DAY_END = hm(7, 0), hm(15, 12)  # the day segment of trade date d, CT date d
EVENING_START, EVENING_END = hm(17, 0), hm(17, 5)  # the Globex open of d, CT date d-1

# regular rates trade dates (sessions: regular F 15:08)
MON, TUE, WED, THU = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4), date(2025, 6, 5)


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars: an evening segment [17:00, 17:05) on CT date d-1 and a
    day segment [07:00, end) on CT date d, flat at the root's base price unless ``paths`` or
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
    end: int = DAY_END
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this minute


def base_ticks(root: str) -> int:
    return to_ticks(BASE_PRICE[root], product(root).vendor_tick)


def _rows(root: str, trade_day: date, ct_day: date, minutes: range, paths: Mapping[int, Ticks],
          skip: frozenset[int], ids: Mapping[int, int], default_id: int, halt: str,
          flatten_from: int | None) -> list[dict]:
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
                      range(EVENING_START, EVENING_END), d.evening, d.evening_skip, {}, eve_id,
                      d.evening_halt, None)
        rows += _rows(root, d.trade_date, d.trade_date, range(DAY_START, d.end), d.paths, d.skip,
                      d.ids, d.instrument_id, d.halt, d.flatten_from)
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, window: Sequence[date] | None = None,
        releases: ReleaseCalendar = NO_RELEASES) -> EngineResult:
    dates = [d.trade_date for d in days] if window is None else list(window)
    return run_engine({member.root: frame(member.root, days)}, member, member.legs,
                      rules_for(member.legs, dates, releases))


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


def bar_at(root: str, day: date, minute: int, offsets: Ticks = (0, 0, 0, 0)) -> Bar:
    b, fixed = base_ticks(root), product(root).vendor_tick_fixed
    o, h, lo, c = ((b + x) * fixed / PRICE_SCALE for x in offsets)
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return Bar(int(utc.timestamp()) * NS, o, h, lo, c, 10, 777, f"{root}M5", day, False, False,
               None, False, False, 0, False)


# ------------------------------------------------------------ declarations and windows ----
@pytest.mark.parametrize("name", CODER_A_FILES)
def test_every_coder_a_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k2/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K2") == []


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(module: ModuleType) -> None:
    for root in EXPOSURES:
        member = vars(module)[f"make_{root.lower()}"]()
        assert isinstance(member, StageEMember)
        assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
        assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
        assert list(member.trading_windows) == [root]
    assert module.make_zt() is not module.make_zt()  # every call starts from fresh state


def test_trading_windows_are_the_s0_12_intervals() -> None:
    windows = {m: vars(m)["make_zn"]().trading_windows["ZN"] for m in MODULES}
    assert windows[cp1] == (TradingInterval(time(17, 0), time(17, 1), -1, -1),
                            TradingInterval(time(7, 49), time(7, 50)),
                            TradingInterval(time(13, 29), time(14, 0)))
    assert windows[cp2] == (TradingInterval(time(7, 20), time(15, 8)),)
    assert windows[cp3] == (TradingInterval(time(7, 20), time(14, 0)),)
    assert windows[monthend] == (TradingInterval(time(7, 20), time(15, 6)),)


def test_the_24_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """The declarations the lead will freeze (S0.2 ordinals) pass the real freeze code; the
    freeze is written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k2").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k2" / "__init__.py").write_bytes(b"")
    for name in CODER_A_FILES:
        shutil.copyfile(K2_DIR / name, members_dir / "k2" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ORDINAL_BASE[m] + i, m.__name__,
                        f"make_{root.lower()}", (LegSpec(root, True),))
             for m in MODULES for i, root in enumerate(EXPOSURES)]
    write_cluster_freeze("K2", decls, tmp_path)
    freeze = load_cluster_freeze("K2", tmp_path)
    verify_cluster_code(freeze)
    assert len(freeze.members) == 24
    assert freeze.member("K2-cp1-01 ZT").ordinal == 1
    assert freeze.member("K2-cp3-01 UB").ordinal == 18
    assert freeze.member("K2-monthend-01 ZT").ordinal == 39
    assert freeze.member("K2-monthend-01 UB").ordinal == 44


def test_prices_become_integer_vendor_ticks() -> None:
    for root in EXPOSURES:
        tick = product(root).vendor_tick
        b = base_ticks(root)
        assert to_ticks(float(b * tick), tick) == b
        assert to_ticks(float((b + 3) * tick), tick) == b + 3


def test_a_none_bar_is_no_decision_and_changes_no_state() -> None:
    ts = int(datetime.combine(TUE, time(8, 0), tzinfo=CT).astimezone(UTC).timestamp()) * NS
    for module in MODULES:
        member = module.make_zn()
        before = repr(vars(member))
        assert member.on_minute(view_of("ZN", ts, None), account_of("ZN", 1)) == ()
        assert repr(vars(member)) == before


def test_an_exit_is_not_sent_while_an_order_is_pending() -> None:
    bar = bar_at("ZN", TUE, hm(13, 58))
    view = view_of("ZN", bar.ts_event_ns, bar)
    opened = ct(bar.ts_event_ns)
    assert exit_if_due(view, account_of("ZN", 1, -1), "ZN", opened, TUE, time(13, 58)) == ()
    assert exit_if_due(view, account_of("ZN", 0, 1), "ZN", opened, TUE, time(13, 58)) == ()
    (intent,) = exit_if_due(view, account_of("ZN", -1), "ZN", opened, TUE, time(13, 58))
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert exit_if_due(view, account_of("ZN", 1), "ZN", opened, TUE, time(13, 59)) == ()


# ------------------------------------------------------------------------ K2-cp1-01 ----
# 17:00 bar (d-1): open B, close B+10. 07:49 bar: open B-5, close B+3. D6's s = close(07:49) -
# open(17:00) = +3 (buy); close - close would be -7 and open - open -5 (both sell).
CP1_BUY_EVENING = {hm(17, 0): (0, 10, 0, 10)}
CP1_BUY_DAY = {hm(7, 49): (-5, 3, -5, 3)}


def cp1_day(day: date = TUE, **kw: Any) -> Day:
    kw.setdefault("evening", CP1_BUY_EVENING)
    kw.setdefault("paths", CP1_BUY_DAY)
    return Day(day, **kw)


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp1_buys_on_a_positive_signal_at_1330_and_exits_at_1359(root: str) -> None:
    # MON: the Globex open is Sunday 17:00 CT, the calendar day before d
    res = run(vars(cp1)[f"make_{root.lower()}"](), [cp1_day(MON)])
    assert fills(res) == trade(MON, "13:30", "13:59", "buy")
    assert intents(res) == [(MON, "13:29", True, None), (MON, "13:58", True, None)]
    assert all(f.qty == 1 for f in res.events(Fill))


def test_cp1_sells_on_a_negative_signal() -> None:
    # s = close(07:49) - open(17:00) = -3; close - close +7, open - open +5
    day = Day(TUE, evening={hm(17, 0): (0, 0, -10, -10)}, paths={hm(7, 49): (5, 5, -3, -3)})
    assert fills(run(cp1.make_zn(), [day])) == trade(TUE, "13:30", "13:59", "sell")


def test_cp1_zero_signal_is_no_trade() -> None:
    day = cp1_day(paths={hm(7, 49): (-5, 0, -5, 0)})  # close(07:49) = open(17:00)
    assert intents(run(cp1.make_zn(), [day])) == []


def test_cp1_missing_globex_open_bar_is_no_trade_l05() -> None:
    # the first PRESENT bar (17:01, open B) would give s = +3; L-05 names the 17:00 bar only
    res = run(cp1.make_zn(), [cp1_day(evening_skip=frozenset({hm(17, 0)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_0749_signal_bar_is_no_trade() -> None:
    res = run(cp1.make_zn(), [cp1_day(skip=frozenset({hm(7, 49)}))])
    assert intents(res) == []


def test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06() -> None:
    evening_differs = cp1_day(evening_id=776)
    signal_differs = cp1_day(ids={hm(7, 49): 778})
    assert intents(run(cp1.make_zn(), [evening_differs])) == []
    assert intents(run(cp1.make_zn(), [signal_differs])) == []
    # the entry bar is not guarded (L-06): only the two signal bars must agree
    entry_differs = cp1_day(ids={m: 778 for m in range(hm(13, 29), DAY_END)})
    assert fills(run(cp1.make_zn(), [entry_differs])) == trade(TUE, "13:30", "13:59")


def test_cp1_missing_1329_entry_bar_is_no_trade_l04() -> None:
    res = run(cp1.make_zn(), [cp1_day(skip=frozenset({hm(13, 29)}))])
    assert intents(res) == [] and fills(res) == []


def test_cp1_missing_1358_bar_sends_the_exit_on_1359() -> None:
    res = run(cp1.make_zn(), [cp1_day(skip=frozenset({hm(13, 58)}))])
    assert fills(res) == trade(TUE, "13:30", "14:00")
    assert intents(res)[-1] == (TUE, "13:59", True, None)


def test_cp1_a_refused_exit_is_resent_on_the_next_bar_l22() -> None:
    # no bars 13:30..13:57: the entry fills at the 13:58 open, so the 13:58 exit comes 1 minute
    # after the fill (engine_min_hold, D9.3b); it is sent again on 13:59 and fills at 14:00
    res = run(cp1.make_zn(), [cp1_day(skip=frozenset(range(hm(13, 30), hm(13, 58))))])
    assert intents(res) == [(TUE, "13:29", True, None), (TUE, "13:58", False, "engine_min_hold"),
                            (TUE, "13:59", True, None)]
    assert fills(res) == trade(TUE, "13:58", "14:00")


def test_cp1_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    # a release at 13:30 CT: the 13:30 entry fill waits for 13:32 (D9.5a); the exit is unchanged
    res = run(cp1.make_zn(), [cp1_day()], releases=release_at("ZN", TUE, 13, 30))
    assert fills(res) == trade(TUE, "13:32", "13:59")
    assert [f.event_window for f in res.events(Fill)] == [True, True]
    assert res.counters["fill_guard_deferral"] == 2


def test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp1.make_zn(), [cp1_day(flatten_from=hm(13, 45))])
    assert fills(res) == trade(TUE, "13:30", "13:46", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["13:29"]  # the member sends no exit of its own


def test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry() -> None:
    # 2021-05-31 (Memorial Day): CME early close 12:00, F 11:45. CP1 is a port (C lines 49-50):
    # it emits at 13:29 and the engine refuses it (the Globex open is Sunday 05-30 17:00)
    day = cp1_day(date(2021, 5, 31), halt="12:00")
    res = run(cp1.make_zn(), [day])
    assert intents(res) == [(date(2021, 5, 31), "13:29", False, "engine_flatten_window")]
    assert fills(res) == []


def test_cp1_trades_once_per_trade_date_on_consecutive_days() -> None:
    res = run(cp1.make_zn(), [cp1_day(TUE), cp1_day(WED)])
    assert fills(res) == trade(TUE, "13:30", "13:59") + trade(WED, "13:30", "13:59")


# ------------------------------------------------------------------------ K2-cp2-01 ----
# OR bars [07:20, 07:35): the 07:25 high is B+2, the 07:30 low is B-2 (the others at B)
CP2_OR = {hm(7, 25): (0, 2, 0, 0), hm(7, 30): (0, 0, -2, 0)}


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    res = run(vars(cp2)[f"make_{root.lower()}"](), [cp2_day({hm(8, 0): UP4})])
    assert fills(res) == trade(TUE, "08:01", "09:16", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "08:00", True, None), (TUE, "09:15", True, None)]


def test_cp2_the_buffer_is_exactly_four_ticks_either_side() -> None:
    up3, down3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks beyond: no entry
    res_up = run(cp2.make_zn(), [cp2_day({hm(7, 50): up3, hm(8, 0): UP4})])
    res_down = run(cp2.make_zn(), [cp2_day({hm(7, 50): down3, hm(8, 0): DOWN4})])
    assert fills(res_up) == trade(TUE, "08:01", "09:16", "buy")
    assert fills(res_down) == trade(TUE, "08:01", "09:16", "sell")


def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar_l07() -> None:
    res = run(cp2.make_zn(), [cp2_day({hm(8, 0): UP4}, skip=frozenset({hm(8, 30)}))])
    assert fills(res) == trade(TUE, "08:01", "09:17")


def test_cp2_has_no_c_minus_2_exit() -> None:
    res = run(cp2.make_zn(), [cp2_day({hm(13, 0): UP4})])
    assert fills(res) == trade(TUE, "13:01", "14:16")  # not 13:59


def test_cp2_no_entry_from_1400() -> None:
    res = run(cp2.make_zn(), [cp2_day({hm(14, 0): UP4, hm(14, 5): UP4})])
    assert intents(res) == []


def test_cp2_entry_at_1359_is_flattened_by_the_engine_at_f() -> None:
    res = run(cp2.make_zn(), [cp2_day({hm(13, 59): UP4, hm(14, 0): UP4})])
    assert fills(res) == trade(TUE, "14:00", "15:08", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["13:59"]  # 68 held bars < 75: no member exit


def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it_l08() -> None:
    # TUE is not a window date: the 08:00 trigger is refused, the 08:10 trigger is not sent
    res = run(cp2.make_zn(), [cp2_day({hm(8, 0): UP4, hm(8, 10): UP4})], window=[MON])
    assert intents(res) == [(TUE, "08:00", False, "engine_not_a_window_date")]


def test_cp2_without_an_opening_range_bar_there_is_no_trade_l08() -> None:
    day = cp2_day({hm(8, 0): UP4, hm(9, 0): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(7, 20), hm(7, 35))))
    assert intents(run(cp2.make_zn(), [day])) == []


def test_cp2_the_range_is_taken_from_the_present_bars_l08() -> None:
    # the 07:25 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day({hm(8, 0): (0, 4, 0, 4)}, skip=frozenset({hm(7, 25)}))
    assert fills(run(cp2.make_zn(), [day])) == trade(TUE, "08:01", "09:16")
    full = cp2_day({hm(8, 0): (0, 4, 0, 4)})
    assert intents(run(cp2.make_zn(), [full])) == []


def test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day({hm(7, 10): (0, 30, -30, 0), hm(8, 0): UP4},
                  evening={hm(17, 0): (0, 30, -30, 0)})
    assert fills(run(cp2.make_zn(), [day])) == trade(TUE, "08:01", "09:16")


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 08:01 CT: the entry fills at 08:03 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(cp2.make_zn(), [cp2_day({hm(8, 0): UP4})], releases=release_at("ZN", TUE, 8, 1))
    assert fills(res) == trade(TUE, "08:03", "09:18")


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(cp2.make_zn(), [cp2_day({hm(8, 0): UP4}), cp2_day({hm(9, 0): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "08:01", "09:16") + trade(WED, "09:01", "10:16", "sell")


# ------------------------------------------------------------------------ K2-cp3-01 ----
def daily(high: int, low: int, close: int, **kw: Any) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (13:59 close) = B+close, plus two
    extreme bars OUTSIDE [07:20, 14:00) that must not enter it."""
    return {hm(7, 10): (0, 50, -50, 0), hm(14, 30): (0, 50, -50, 0),
            hm(10, 0): (0, high, 0, 0), hm(11, 0): (0, 0, low, 0),
            hm(13, 59): (0, max(0, close), min(0, close), close), **kw}


BUY_08 = daily(10, 0, 8)  # CLV = 8/10 = 0.8 exactly
SELL_02 = daily(10, 0, 2)  # CLV = 2/10 = 0.2 exactly


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_08_buys_on_the_0720_bar_and_exits_at_1359(root: str) -> None:
    res = run(vars(cp3)[f"make_{root.lower()}"](), [Day(MON, BUY_08), Day(TUE)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, "07:20", True, None), (TUE, "13:58", True, None)]


def test_cp3_prior_clv_at_02_sells() -> None:
    res = run(cp3.make_zn(), [Day(MON, SELL_02), Day(TUE)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "sell")


@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(close: int) -> None:
    assert intents(run(cp3.make_zn(), [Day(MON, daily(10, 0, close)), Day(TUE)])) == []


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


def test_cp3_zero_range_is_no_trade() -> None:
    assert intents(run(cp3.make_zn(), [Day(MON, {hm(7, 10): (0, 50, -50, 0)}), Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(cp3.make_zn(), [Day(MON, BUY_08), Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy") + trade(WED, "07:21", "13:59",
                                                                     "sell")


def test_cp3_d_minus_1_is_the_most_recent_complete_day_l09() -> None:
    # TUE lacks its 13:59 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade"
    tue = Day(TUE, SELL_02, skip=frozenset({hm(13, 59)}))
    res = run(cp3.make_zn(), [Day(MON, BUY_08), tue, Day(WED)])
    # TUE's exit, decided on 13:58, fills at the next present bar (14:00)
    assert fills(res) == trade(TUE, "07:21", "14:00", "buy") + trade(WED, "07:21", "13:59",
                                                                     "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(9, 0): 778})  # one bar in [07:20, 14:00) differs
    res = run(cp3.make_zn(), [mon, Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(WED, "07:21", "13:59", "sell")  # TUE: no complete d-1 yet


def test_cp3_instrument_guard_compares_d_minus_1_with_the_0720_bar() -> None:
    tue = Day(TUE, BUY_08, instrument_id=778)
    res = run(cp3.make_zn(), [Day(MON, BUY_08), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, "07:21", "13:59", "buy")  # TUE refused by the guard


def test_cp3_missing_0720_bar_is_no_trade_and_the_day_is_incomplete() -> None:
    tue = Day(TUE, SELL_02, skip=frozenset({hm(7, 20)}))
    res = run(cp3.make_zn(), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(WED, "07:21", "13:59", "buy")  # WED's d-1 is MON


def test_cp3_early_halt_day_is_not_traded_and_is_incomplete() -> None:
    # 2021-05-31 (Memorial Day, halt 12:00, F 11:45): bars kept to 15:12 so it would be complete
    # but for its halt; the engine would accept a 07:20 entry, so the member's own test is seen
    fri, halt_day, tue = date(2021, 5, 28), date(2021, 5, 31), date(2021, 6, 1)
    days = [Day(fri, BUY_08), Day(halt_day, SELL_02, halt="12:00"),
            Day(tue, evening_halt="12:00")]
    res = run(cp3.make_zn(), days)
    assert [i for i in intents(res) if i[0] == halt_day] == []
    assert fills(res) == trade(tue, "07:21", "13:59", "buy")  # d-1 of 06-01 is 05-28


def test_cp3_missing_1358_bar_sends_the_exit_on_1359() -> None:
    res = run(cp3.make_zn(), [Day(MON, BUY_08), Day(TUE, skip=frozenset({hm(13, 58)}))])
    assert fills(res) == trade(TUE, "07:21", "14:00")


def test_cp3_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    res = run(cp3.make_zn(), [Day(MON, BUY_08), Day(TUE)], releases=release_at("ZN", TUE, 7, 21))
    assert fills(res) == trade(TUE, "07:23", "13:59")


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp3.make_zn(), [Day(MON, BUY_08), Day(TUE, flatten_from=hm(13, 0))])
    assert fills(res) == trade(TUE, "07:21", "13:01", exit_reason="forced_flatten")


# -------------------------------------------------------------------- K2-monthend-01 ----
JUNE_2025 = ("2025-06", "2025-06-27", "2025-06-30")
MAY_2021 = ("2021-05", "2021-05-28", "2021-05-31")  # N = Memorial Day, an early-halt trade date
N1, N = date(2025, 6, 27), date(2025, 6, 30)


def test_the_month_end_test_rows_are_in_the_table() -> None:
    assert JUNE_2025 in MONTH_END and MAY_2021 in MONTH_END
    assert len(monthend.EVENT_DATES) == 2 * len(MONTH_END)
    assert date(2025, 6, 26) not in monthend.EVENT_DATES
    assert date(2025, 7, 1) not in monthend.EVENT_DATES


@pytest.mark.parametrize("root", EXPOSURES)
def test_monthend_buys_n_minus_1_and_n_at_0721_and_exits_at_1505(root: str) -> None:
    days = [Day(date(2025, 6, 26)), Day(N1), Day(N), Day(date(2025, 7, 1))]
    res = run(vars(monthend)[f"make_{root.lower()}"](), days)
    assert fills(res) == trade(N1, "07:21", "15:05", "buy") + trade(N, "07:21", "15:05", "buy")
    assert {i[0] for i in intents(res)} == {N1, N}  # dates not in the table are not traded


def test_monthend_an_early_halt_n_is_dropped_and_n_minus_1_still_trades_l16() -> None:
    fri, halt_n, after = date(2021, 5, 28), date(2021, 5, 31), date(2021, 6, 1)
    days = [Day(fri), Day(halt_n, halt="12:00", end=hm(12, 0)), Day(after, evening_halt="12:00")]
    res = run(monthend.make_zn(), days)
    assert fills(res) == trade(fri, "07:21", "15:05")
    assert {i[0] for i in intents(res)} == {fri}  # N dropped by the member, not moved to 06-01


def test_monthend_a_missing_0720_bar_is_no_trade_that_date() -> None:
    res = run(monthend.make_zn(), [Day(N1, skip=frozenset({hm(7, 20)})), Day(N)])
    assert fills(res) == trade(N, "07:21", "15:05")


def test_monthend_a_missing_1504_bar_sends_the_exit_on_the_next_bar() -> None:
    res = run(monthend.make_zn(), [Day(N1, skip=frozenset({hm(15, 4)}))])
    assert fills(res) == trade(N1, "07:21", "15:06")


def test_monthend_fills_in_the_d95a_guard_wait_two_minutes() -> None:
    entry = run(monthend.make_zn(), [Day(N1)], releases=release_at("ZN", N1, 7, 21))
    exit_ = run(monthend.make_zn(), [Day(N1)], releases=release_at("ZN", N1, 15, 5))
    assert fills(entry) == trade(N1, "07:23", "15:05")
    assert fills(exit_) == trade(N1, "07:21", "15:07")  # still before F 15:08


def test_monthend_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(monthend.make_zn(), [Day(N1, flatten_from=hm(14, 30))])
    assert fills(res) == trade(N1, "07:21", "14:31", exit_reason="forced_flatten")


def test_monthend_guards_only_the_entry_bar_l12() -> None:
    # the guard covers the bars read at or before the entry decision (the 07:20 bar only);
    # a different id before 07:20 changes nothing
    res = run(monthend.make_zn(), [Day(N1, ids={hm(7, 0): 778}, evening_id=778)])
    assert fills(res) == trade(N1, "07:21", "15:05")


# ------------------------------------------------------------------- month-end table pin ----
def _month_end_from_the_calendar() -> tuple[tuple[str, str, str], ...]:
    """An independent recomputation from EC-CAL (not the generator's code path)."""
    cal = load_group_calendar("rates")
    first, last = cal.coverage
    rows = []
    month = date(first.year, first.month, 1)
    while month <= last:
        nxt = (month + timedelta(days=32)).replace(day=1)
        span = [month + timedelta(days=k) for k in range((nxt - month).days)]
        n = max(d for d in span if cal.is_trade_date(d))
        if cal.covers(n):
            n1 = next(n - timedelta(days=k) for k in range(1, 15)
                      if cal.is_trade_date(n - timedelta(days=k)))
            rows.append((f"{n:%Y-%m}", n1.isoformat(), n.isoformat()))
        month = nxt
    return tuple(rows)


def test_the_month_end_table_is_the_calendar_recomputed() -> None:
    assert _month_end_from_the_calendar() == MONTH_END
    assert len(MONTH_END) == 85 and MONTH_END[0][0] == "2019-05" and MONTH_END[-1][0] == "2026-05"
    assert all(month != "2026-06" for month, _, _ in MONTH_END)  # N outside the coverage (L-16)
    digest = hashlib.sha256((REPO / "data" / "calendars" / "rates.py").read_bytes()).hexdigest()
    assert digest == MONTH_END_SOURCE_SHA256


def test_early_halt_days_are_trade_dates_of_the_calendar() -> None:
    cal = load_group_calendar("rates")
    assert cal.early_halt_ct(date(2021, 5, 31)) == time(12, 0)
    assert cal.is_trade_date(date(2021, 5, 31))
    halts = [(m, d) for m, *pair in MONTH_END for d in pair
             if cal.early_halt_ct(date.fromisoformat(d)) is not None]
    assert len(halts) == 9  # listed in the table; the member drops them at run time (C4)
