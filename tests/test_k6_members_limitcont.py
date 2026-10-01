"""Stage E.8 K6-limitcont-01 (MemberCoder-B): reports/stage_e8_member_specs.md section 5,
S0.3-S0.12, K6-L-06..K6-L-09 and ruling R-1b-2; plus this file's synthetic kit, which
tests/test_k6_members_wasde.py reuses.

Synthetic bars only. The settlement proxy is pinned against rules.price_limits.settlement_proxy
over settlement_window_utc on hand-built bars. The rule is pinned by feeding the member its bars
in order with a flat account (direct calls), and its fills, exits and the engine's D9.7 entry
guard and forced exit through the real Stage E engine (screening.stage_e_engine.run_engine
under StageERules built by the canary kit's rules_for; HE and LE are hard-limit products, so
D9.7 is live). No bar file is read, no runner is run and no freeze is written.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules import price_limits as pl
from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import check_member_source
from screening.stage_e_frozen import load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules
from strategy.interface import Bar
from strategy.members.k6 import _calendar, limitcont
from strategy.members.k6._event_common import price_ticks
from strategy.stage_e.interface import (
    LegIntent,
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
K6_DIR = REPO / "strategy" / "members" / "k6"
CODER_B_FILES = ("_calendar.py", "_wasde.py", "_limits.py", "_event_common.py", "limitcont.py",
                 "wasdepre.py", "wasdepost.py")
BASE_PRICE = MappingProxyType({"HE": 90.0, "LE": 220.0, "ZC": 440.0, "ZS": 1050.0})


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


# the synthetic day segment of trade date d on CT date d, [start, end)
SEGMENT = MappingProxyType({"livestock": (hm(8, 30), hm(13, 5)), "grains": (hm(8, 30), hm(13, 20))})
# regular livestock trade dates (full sessions), a week of 2025-05 (LE 0.0650 = 260 ticks,
# HE 0.0400 = 160 ticks)
MON, TUE, WED, THU = date(2025, 5, 5), date(2025, 5, 6), date(2025, 5, 7), date(2025, 5, 8)
SETTLE = hm(12, 59)  # the bar whose close is a regular day's proxy


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars on CT date d, [start, end). Every bar's close is the
    root's base price plus ``closes.get(minute, level)`` ticks; its open is ``opens[minute]``
    ticks when given, else the close; high and low span the two."""

    trade_date: date
    level: int = 0
    closes: Mapping[int, int] = field(default_factory=dict)
    opens: Mapping[int, int] = field(default_factory=dict)
    skip: frozenset[int] = frozenset()  # CT minutes of date d with no bar
    ids: Mapping[int, int] = field(default_factory=dict)  # per-minute instrument_id overrides
    volumes: Mapping[int, int] = field(default_factory=dict)
    instrument_id: int = 777
    halt: time | None = None  # early_halt_ct of CT date d
    start: int | None = None
    end: int | None = None


def base_ticks(root: str) -> int:
    return price_ticks(BASE_PRICE[root], product(root).vendor_tick)


def px(root: str, ticks: int) -> float:
    return (base_ticks(root) + ticks) * product(root).vendor_tick_fixed / PRICE_SCALE


def ns_at(day: date, minute: int) -> int:
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def _span(root: str, d: Day) -> range:
    lo, hi = SEGMENT[product(root).group]
    return range(lo if d.start is None else d.start, hi if d.end is None else d.end)


def bars_of(root: str, d: Day) -> list[Bar]:
    out = []
    for minute in _span(root, d):
        if minute in d.skip:
            continue
        c = d.closes.get(minute, d.level)
        o = d.opens.get(minute, c)
        out.append(Bar(ns_at(d.trade_date, minute), px(root, o), px(root, max(o, c)),
                       px(root, min(o, c)), px(root, c), d.volumes.get(minute, 10),
                       d.ids.get(minute, d.instrument_id), f"{root}M5", d.trade_date, False,
                       False, d.halt, False, False, 0, False))
    return out


def frame(root: str, days: Sequence[Day]) -> pd.DataFrame:
    rows = []
    for d in days:
        for b in bars_of(root, d):
            utc = datetime.fromtimestamp(b.ts_event_ns // NS, tz=UTC)
            state = sessions.session_state(root, utc)
            rows.append({
                "ts_event": b.ts_event_ns, "open": b.open, "high": b.high, "low": b.low,
                "close": b.close, "volume": b.volume, "instrument_id": b.instrument_id,
                "raw_symbol": b.raw_symbol, "trade_date": b.trade_date.isoformat(),
                "in_flatten_window": bool(state.must_be_flat),
                "in_no_new_positions_window": bool(not state.can_open),
                "early_halt_ct": "" if d.halt is None else d.halt.isoformat(),
                "in_scheduled_closure": False, "is_roll_session": False,
                "gap_before_minutes": 0, "vendor_degraded_day": False})
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, releases: ReleaseCalendar = NO_RELEASES,
        rules: StageERules | None = None) -> EngineResult:
    if rules is None:
        rules = rules_for(member.legs, [d.trade_date for d in days], releases)
    return run_engine({member.root: frame(member.root, days)}, member, member.legs, rules)


def fills(res: EngineResult) -> list[tuple[date, str, str, str]]:
    """(CT date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(ct(f.fill_ts_ns).date(), f"{ct(f.fill_ts_ns):%H:%M}", f.side, f.reason)
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
    return release_calendar(root, [ns_at(day, hm(hh, mm))])


def view_of(root: str, ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({root: bar}))


def account_of(root: str, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({root: position}), MappingProxyType({root: pending}),
                             MappingProxyType({root: None}), MappingProxyType({root: 0}))


def feed(member: Any, days: Sequence[Day], position: int = 0, pending: int = 0
         ) -> list[tuple[date, str, str]]:
    """Every bar of ``days`` in order through ``on_minute`` with a fixed account; (CT date,
    the emitting bar's CT hh:mm, side) of every intent."""
    out = []
    for d in days:
        for bar in bars_of(member.root, d):
            items = member.on_minute(view_of(member.root, bar.ts_event_ns, bar),
                                     account_of(member.root, position, pending))
            for item in items:
                assert isinstance(item, LegIntent), item
                out.append((ct(bar.ts_event_ns).date(), f"{ct(bar.ts_event_ns):%H:%M}",
                            item.side))
    return out


# ----------------------------------------------------------------------- helpers ----
def lim(root: str) -> int:
    return {"HE": 160, "LE": 260}[root]  # the initial limit of 2025-05 in vendor ticks


def history(s3: int, s2: int, s1: int, days: Sequence[date] = (MON, TUE, WED),
            over: Mapping[int, Mapping[str, Any]] | None = None) -> list[Day]:
    """d-3, d-2, d-1 with their 12:59 closes at s3, s2, s1 ticks (every other bar at s3, s2, s1
    too); ``over`` maps a position (0, 1, 2) to Day overrides."""
    over = over or {}
    return [Day(day, level=s, **over.get(i, {}))
            for i, (day, s) in enumerate(zip(days, (s3, s2, s1), strict=True))]


def m(root: str) -> limitcont.LimitCont:
    return limitcont.make_he() if root == "HE" else limitcont.make_le()


ROOTS = ("HE", "LE")


# ------------------------------------------------------------------ declarations ----
@pytest.mark.parametrize("root", ROOTS)
def test_declaration_legs_windows_and_size(root: str) -> None:
    member = m(root)
    assert isinstance(member, StageEMember)
    assert member.name == f"K6-limitcont-01 {root}" and member.root == root
    assert member.legs == (LegSpec(root, True),)
    assert member.trading_windows == {root: (TradingInterval(time(8, 30), time(13, 0)),)}
    assert load_frozen_tables().vehicles[root].q_c == member._q == 1
    assert load_frozen_tables().day_session_ct[root] == (time(8, 30), time(13, 0))
    assert (member._open, member._exit) == (time(8, 30), time(12, 58))  # O and C - 2
    assert time(8, 44) == limitcont.ENTRY_BAR


def test_only_he_and_le_are_traded() -> None:
    with pytest.raises(ValueError, match="does not trade"):
        limitcont.LimitCont("ZC")


def test_coder_b_files_pass_the_freeze_static_check() -> None:
    for name in CODER_B_FILES:
        rel = f"strategy/members/k6/{name}"
        assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K6") == [], rel


# ------------------------------------------------------------ the settlement proxy ----
def _engine_proxy(root: str, x: date, bars: Sequence[Bar]) -> Decimal | None:
    prints = [pl.BarPrint(datetime.fromtimestamp(b.ts_event_ns // NS, tz=UTC),
                          Decimal(repr(b.close)), b.volume) for b in bars if b.trade_date == x]
    proxy = pl.settlement_proxy(prints, *pl.settlement_window_utc(root, x))
    return None if proxy is None else proxy.value


def _member_proxy(x: date, bars: Sequence[Bar]) -> tuple[Decimal | None, frozenset[int]]:
    inputs = limitcont.proxy_inputs_for(x)
    for b in bars:
        inputs.add(b.ts_event_ns, b.close, b.volume, b.instrument_id)
    return inputs.value()


@pytest.mark.parametrize("root", ROOTS)
def test_proxy_on_a_regular_day_is_the_1259_close(root: str) -> None:
    day = Day(TUE, closes={hm(12, 58): 3, SETTLE: 7, hm(13, 0): 11, hm(13, 4): 13})
    bars = bars_of(root, day)
    value, ids = _member_proxy(TUE, bars)
    assert value == _engine_proxy(root, TUE, bars) == Decimal(repr(px(root, 7)))
    assert ids == {777}


@pytest.mark.parametrize("root", ROOTS)
def test_proxy_falls_back_to_the_last_close_before_the_window_end(root: str) -> None:
    day = Day(TUE, closes={hm(12, 58): 3, hm(13, 0): 11}, skip=frozenset({SETTLE}),
              ids={hm(12, 58): 778})
    bars = bars_of(root, day)
    value, ids = _member_proxy(TUE, bars)
    assert value == _engine_proxy(root, TUE, bars) == Decimal(repr(px(root, 3)))
    assert ids == {778}  # the fallback bar's id is the one S uses


@pytest.mark.parametrize("root", ROOTS)
def test_proxy_with_no_volume_in_the_window_is_the_last_close(root: str) -> None:
    day = Day(TUE, closes={hm(12, 58): 3, SETTLE: 5}, volumes={SETTLE: 0})
    bars = bars_of(root, day)
    value, _ = _member_proxy(TUE, bars)
    assert value == _engine_proxy(root, TUE, bars) == Decimal(repr(px(root, 5)))


@pytest.mark.parametrize("root", ROOTS)
def test_proxy_on_an_early_halt_day_is_the_close_before_the_halt(root: str) -> None:
    # 2025-12-24: livestock halts at 12:15; the window is [12:14:30, 12:15:00)
    xmas = date(2025, 12, 24)
    day = Day(xmas, closes={hm(12, 13): 2, hm(12, 14): 9}, halt=time(12, 15), end=hm(12, 15))
    bars = bars_of(root, day)
    value, _ = _member_proxy(xmas, bars)
    assert value == _engine_proxy(root, xmas, bars) == Decimal(repr(px(root, 9)))


@pytest.mark.parametrize("root", ROOTS)
def test_proxy_is_undefined_with_no_bar_before_the_window_end(root: str) -> None:
    day = Day(TUE, start=hm(13, 0))
    bars = bars_of(root, day)
    assert _member_proxy(TUE, bars) == (None, frozenset())
    assert _engine_proxy(root, TUE, bars) is None


def test_proxy_vwap_arithmetic_mirrors_settlement_proxy_on_a_wider_window() -> None:
    """The volume-weighted branch on several bars (a window no livestock day has), with the same
    window given to both: the same Decimal, bar for bar."""
    root, x = "LE", TUE
    day = Day(x, closes={hm(12, 0): 1, hm(12, 1): 4, hm(12, 2): 9, hm(12, 3): 2},
              volumes={hm(12, 0): 3, hm(12, 1): 7, hm(12, 2): 0, hm(12, 3): 11},
              ids={hm(12, 2): 778, hm(12, 3): 779})  # a zero-volume bar is not used
    bars = bars_of(root, day)
    lo, end = ns_at(x, hm(12, 0)) + 20 * NS, ns_at(x, hm(12, 3))
    inputs = limitcont.ProxyInputs(ns_at(x, hm(12, 0)), end)
    for b in bars:
        inputs.add(b.ts_event_ns, b.close, b.volume, b.instrument_id)
    prints = [pl.BarPrint(datetime.fromtimestamp(b.ts_event_ns // NS, tz=UTC),
                          Decimal(repr(b.close)), b.volume) for b in bars]
    expected = pl.settlement_proxy(prints, datetime.fromtimestamp(lo / NS, tz=UTC),
                                   datetime.fromtimestamp(end // NS, tz=UTC))
    assert expected is not None and expected.method == "vwap_close"
    assert inputs.value()[0] == expected.value
    assert inputs.value()[1] == {777}


def test_moved_exactly_is_exact() -> None:
    tick = Decimal("0.025")
    assert limitcont.moved_exactly(Decimal("226.5"), Decimal("220"), 260, tick)
    assert not limitcont.moved_exactly(Decimal("226.475"), Decimal("220"), 260, tick)
    assert limitcont.moved_exactly(Decimal("213.5"), Decimal("220"), -260, tick)
    third = Decimal(1) / Decimal(3)  # an off-grid weighted mean never equals a tick multiple
    assert not limitcont.moved_exactly(Decimal("226.5") + third / 10**20, Decimal("220"), 260, tick)


# --------------------------------------------------------------------- the event ----
@pytest.mark.parametrize("root", ROOTS)
def test_a_limit_up_close_buys_on_the_0844_bar(root: str) -> None:
    days = [*history(0, 0, lim(root)), Day(THU, level=lim(root))]
    assert feed(m(root), days) == [(THU, "08:44", "buy")]


@pytest.mark.parametrize("root", ROOTS)
def test_a_limit_down_close_sells_on_the_0844_bar(root: str) -> None:
    days = [*history(5, 5, 5 - lim(root)), Day(THU, level=5 - lim(root))]
    assert feed(m(root), days) == [(THU, "08:44", "sell")]


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("off", [-1, 1])
def test_one_tick_from_the_limit_does_not_trade(root: str, off: int) -> None:
    for sign in (1, -1):
        s1 = sign * (lim(root) + off)
        assert feed(m(root), [*history(0, 0, s1), Day(THU, level=s1)]) == []


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("sign", [1, -1])
def test_d2_a_limit_close_itself_blocks_d(root: str, sign: int) -> None:
    """K6-L-07: S(d-2) - S(d-3) = +-L(d-2): d-1's limit was expanded; no trade on d."""
    s2 = sign * lim(root)
    days = [*history(0, s2, s2 + lim(root)), Day(THU, level=s2 + lim(root))]
    assert feed(m(root), days) == []
    near = sign * (lim(root) - 1)  # one tick short of a limit close on d-2: d trades
    days = [*history(0, near, near + lim(root)), Day(THU, level=near + lim(root))]
    assert feed(m(root), days) == [(THU, "08:44", "buy")]


def test_the_limit_period_boundary_reads_each_dates_own_limit() -> None:
    """HE: 160 ticks to 2025-08-29, 190 from 2025-09-02 (Labor Day 09-01 closed). For d =
    2025-09-03, L(d-1) = L(2025-09-02) = 190 and L(d-2) = L(2025-08-29) = 160."""
    d3, d2, d1, d = date(2025, 8, 28), date(2025, 8, 29), date(2025, 9, 2), date(2025, 9, 3)
    assert d in _calendar.LIVESTOCK_FULL_SESSIONS
    days = (d3, d2, d1)
    assert feed(m("HE"), [*history(0, 0, 190, days), Day(d, level=190)]) == [(d, "08:44", "buy")]
    assert feed(m("HE"), [*history(0, 0, 160, days), Day(d, level=160)]) == []
    # the guard on d-2 reads L(d-2) = 160: a 160 move blocks, a 190 move does not
    assert feed(m("HE"), [*history(0, 160, 350, days), Day(d, level=350)]) == []
    assert feed(m("HE"), [*history(0, 190, 380, days), Day(d, level=380)]) == [(d, "08:44", "buy")]
    # d = 2025-09-02 itself (L = 190): its d-1 = 2025-08-29 has L = 160, which the test reads
    early = (date(2025, 8, 27), d3, d2)
    assert feed(m("HE"), [*history(0, 0, 160, early), Day(d1, level=160)]) == [
        (d1, "08:44", "buy")]
    assert feed(m("HE"), [*history(0, 0, 190, early), Day(d1, level=190)]) == []


def test_a_dropped_limit_date_as_d1_gives_no_trade() -> None:
    """R-1b-2: LE 2026-06-01..06-18 are dropped (L = 290 ticks in the frozen table)."""
    d4, d3, d2, d1 = date(2026, 5, 27), date(2026, 5, 28), date(2026, 5, 29), date(2026, 6, 1)
    d = date(2026, 6, 2)
    assert feed(m("LE"), [*history(0, 0, 290, (d4, d3, d2)), Day(d1, level=290)]) == [
        (d1, "08:44", "buy")]  # control: d = 2026-06-01, d-1 = 05-29 (not dropped)
    assert feed(m("LE"), [*history(0, 0, 290, (d3, d2, d1)), Day(d, level=290)]) == []


def test_a_dropped_limit_date_as_d2_gives_no_trade_and_d3_is_not_read(
        monkeypatch: pytest.MonkeyPatch) -> None:
    days = [*history(0, 0, lim("LE")), Day(THU, level=lim("LE"))]
    monkeypatch.setattr(limitcont, "DROPPED_LIMIT_DATES", {"LE": {TUE: "synthetic"}})
    assert feed(m("LE"), days) == []
    monkeypatch.setattr(limitcont, "DROPPED_LIMIT_DATES", {"LE": {MON: "synthetic"}})
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]  # L(d-3) is never read
    monkeypatch.setattr(limitcont, "DROPPED_LIMIT_DATES", {"HE": {WED: "synthetic"}})
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]  # another root's drops


# ------------------------------------------------------------ c and the bars read ----
@pytest.mark.parametrize("pos", [0, 1, 2])
def test_a_settlement_bar_with_another_instrument_id_gives_no_trade(pos: int) -> None:
    days = [*history(0, 0, lim("LE"), over={pos: {"ids": {SETTLE: 778}}}),
            Day(THU, level=lim("LE"))]
    assert feed(m("LE"), days) == []


def test_a_fallback_settlement_bar_with_another_instrument_id_gives_no_trade() -> None:
    fallback = {"skip": frozenset({SETTLE}), "ids": {hm(12, 58): 778}}
    days = [*history(0, 0, lim("LE"), over={2: fallback}), Day(THU, level=lim("LE"))]
    assert feed(m("LE"), days) == []
    days = [*history(0, 0, lim("LE"), over={2: {"skip": frozenset({SETTLE})}}),
            Day(THU, level=lim("LE"))]
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]  # the fallback carries c: trades


def test_bars_the_proxy_does_not_use_are_not_guarded() -> None:
    other = {"ids": {hm(10, 0): 778, hm(13, 0): 778}}
    days = [*history(0, 0, lim("LE"), over={0: other, 1: other, 2: other}),
            Day(THU, level=lim("LE"), ids={hm(9, 0): 778})]
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]


def test_c_is_the_0830_bars_instrument_id() -> None:
    hist = history(0, 0, lim("LE"))
    # the 08:30 bar carries 778, every other bar 777: c = 778, so S and the 08:44 bar do not
    assert feed(m("LE"), [*hist, Day(THU, level=lim("LE"), ids={hm(8, 30): 778})]) == []
    assert feed(m("LE"), [*hist, Day(THU, level=lim("LE"), ids={hm(8, 44): 778})]) == []
    # the whole history and d on 778: trades
    hist778 = history(0, 0, lim("LE"), over={i: {"instrument_id": 778} for i in range(3)})
    assert feed(m("LE"), [*hist778, Day(THU, level=lim("LE"), instrument_id=778)]) == [
        (THU, "08:44", "buy")]


@pytest.mark.parametrize("missing", [hm(8, 30), hm(8, 44)])
def test_a_missing_0830_or_0844_bar_gives_no_trade(missing: int) -> None:
    days = [*history(0, 0, lim("LE")), Day(THU, level=lim("LE"), skip=frozenset({missing}))]
    assert feed(m("LE"), days) == []


def test_unseen_history_gives_no_trade() -> None:
    hist = history(0, 0, lim("LE"))
    assert feed(m("LE"), [*hist[1:], Day(THU, level=lim("LE"))]) == []  # d-3 not seen
    assert feed(m("LE"), [*hist[:2], Day(THU, level=lim("LE"))]) == []  # d-1 not seen
    # d-1 seen but with no bar before its window end: S(d-1) undefined
    late = history(0, 0, lim("LE"), over={2: {"start": hm(13, 0)}})
    assert feed(m("LE"), [*late, Day(THU, level=lim("LE"))]) == []


@pytest.mark.parametrize(("d", "prior"), [
    (date(2025, 11, 28), (date(2025, 11, 21), date(2025, 11, 24), date(2025, 11, 25),
                          date(2025, 11, 26))),
    (date(2025, 12, 24), (date(2025, 12, 17), date(2025, 12, 18), date(2025, 12, 19),
                          date(2025, 12, 22), date(2025, 12, 23)))])
def test_d_outside_livestock_full_sessions_gives_no_trade(d: date, prior: tuple[date, ...]
                                                          ) -> None:
    halt = _calendar.LIVESTOCK_EARLY_HALT_CT[d]
    assert d not in _calendar.LIVESTOCK_FULL_SESSIONS
    s = [0] * (len(prior) - 1) + [290]  # LE 0.0725 = 290 ticks; d-1 closes limit-up
    days = [Day(x, level=v) for x, v in zip(prior, s, strict=True)]
    assert feed(m("LE"), [*days, Day(d, level=290, halt=halt, end=hm(halt.hour, halt.minute))]
                ) == []


def test_an_early_halt_d1_uses_the_close_before_the_halt() -> None:
    """d = 2025-12-26 (a full session), d-1 = 2025-12-24 (halt 12:15): S(d-1) is the 12:14 close;
    the 12:14 bar must carry c."""
    d3, d2, d1, d = date(2025, 12, 22), date(2025, 12, 23), date(2025, 12, 24), date(2025, 12, 26)
    assert d in _calendar.LIVESTOCK_FULL_SESSIONS
    halted = {"halt": time(12, 15), "end": hm(12, 15), "closes": {hm(12, 14): 290}}
    days = [*history(0, 0, 0, (d3, d2, d1), over={2: halted}), Day(d, level=290)]
    assert feed(m("LE"), days) == [(d, "08:44", "buy")]
    halted_other = {**halted, "ids": {hm(12, 14): 778}}
    days = [*history(0, 0, 0, (d3, d2, d1), over={2: halted_other}), Day(d, level=290)]
    assert feed(m("LE"), days) == []


def test_no_entry_while_a_position_or_an_order_is_pending() -> None:
    days = [*history(0, 0, lim("LE")), Day(THU, level=lim("LE"))]
    assert feed(m("LE"), days, pending=1) == []
    held = feed(m("LE"), days, position=1)  # a held position is only ever exited
    assert held and all(side == "sell" for _, _, side in held)


def test_state_is_per_trade_date_and_the_entry_once() -> None:
    hist = history(0, 0, lim("LE"))
    fri = date(2025, 5, 9)
    # THU: limit-up close on WED, entry; FRI: d-1 = THU closed at WED's level, no event
    days = [*hist, Day(THU, level=lim("LE")), Day(fri, level=lim("LE"))]
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]
    # FRI after a limit-down THU: d-2 = WED was itself a limit close, so FRI is blocked
    days = [*hist, Day(THU, level=0), Day(fri, level=0)]
    assert feed(m("LE"), days) == [(THU, "08:44", "buy")]


# ------------------------------------------------------------------ the exit ----
def test_the_exit_is_on_the_first_bar_at_or_after_1258() -> None:
    held = Day(THU, level=lim("LE"))
    assert [t for _, t, _ in feed(m("LE"), [held], position=1)][:1] == ["12:58"]
    assert [t for _, t, _ in feed(m("LE"), [held], position=-1)][:1] == ["12:58"]
    late = Day(THU, level=lim("LE"), skip=frozenset({hm(12, 58), hm(12, 59)}))
    out = feed(m("LE"), [late], position=1)
    assert out[0] == (THU, "13:00", "sell")
    assert feed(m("LE"), [held], position=1, pending=-1) == []  # an exit is already pending


def test_every_exit_closes_the_whole_position() -> None:
    """S0.3: the exit is the whole position (a synthetic 2 lots; q_c is 1 for every K6 root)."""
    member = m("LE")
    bar = bars_of("LE", Day(THU, start=hm(12, 58), end=hm(12, 59)))[0]
    for position, side in ((2, "sell"), (-2, "buy")):
        (item,) = member.on_minute(view_of("LE", bar.ts_event_ns, bar), account_of("LE", position))
        assert isinstance(item, LegIntent) and (item.side, item.quantity) == (side, 2)


def test_price_ticks_rounds_to_the_nearest_tick() -> None:
    tick = Decimal("0.25")
    assert price_ticks(440.0, tick) == 1760 and price_ticks(440.25, tick) == 1761
    assert price_ticks(440.15, tick) == 1761 and price_ticks(440.1, tick) == 1760


# ---------------------------------------------------------------- engine runs ----
def _engine_days(root: str, d_kw: Mapping[str, Any] | None = None) -> list[Day]:
    kw = {"level": lim(root), **(d_kw or {})}
    return [*history(0, 0, lim(root)), Day(THU, **kw)]


def _beyond_upper(root: str, s1_ticks: int) -> int:
    """The smallest tick offset from S(d-1) at or beyond D9.7's upper stop level on THU."""
    s1 = Decimal(repr(px(root, s1_ticks)))
    band = pl.limit_band(root, THU, datetime.combine(THU, time(9, 0), tzinfo=CT), s1)
    upper = pl.stop_levels(band, s1).upper
    assert upper is not None
    k = 0
    while Decimal(repr(px(root, s1_ticks + k))) < upper:
        k += 1
    return k


@pytest.mark.parametrize("root", ROOTS)
def test_engine_fills_the_entry_at_0845_and_the_exit_at_1259(root: str) -> None:
    res = run(m(root), _engine_days(root))
    assert fills(res) == trade(THU, "08:45", "12:59")
    assert intents(res) == [(THU, "08:44", True, None), (THU, "12:58", True, None)]


def test_engine_exit_on_the_first_bar_after_a_missing_1258() -> None:
    res = run(m("LE"), _engine_days("LE", {"skip": frozenset({hm(12, 58)})}))
    assert fills(res) == trade(THU, "08:45", "13:00")


@pytest.mark.parametrize("root", ROOTS)
def test_engine_d97_forced_exit_and_no_further_member_order(root: str) -> None:
    k = _beyond_upper(root, lim(root))
    assert k > 0
    res = run(m(root), _engine_days(root, {"closes": {hm(9, 0): lim(root) + k}}))
    assert fills(res) == trade(THU, "08:45", "09:01", exit_reason="price_limit_exit")
    assert intents(res) == [(THU, "08:44", True, None)]
    # one tick short of the stop level: no forced exit
    res = run(m(root), _engine_days(root, {"closes": {hm(9, 0): lim(root) + k - 1}}))
    assert fills(res) == trade(THU, "08:45", "12:59")


@pytest.mark.parametrize("root", ROOTS)
def test_engine_refuses_the_open_beyond_the_stop_and_the_member_does_not_retry(root: str
                                                                               ) -> None:
    k = _beyond_upper(root, lim(root))
    res = run(m(root), _engine_days(root, {"level": lim(root) + k}))
    assert fills(res) == []
    assert intents(res) == [(THU, "08:44", False, "price_limit_zone_no_entry")]
