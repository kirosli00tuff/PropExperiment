"""Stage E.7 K1 members of MemberCoder-B, part 1: K1-vxnband-01 (reports/stage_e7_member_specs.md
sections 0, 4, 8 and 9; readings K1-L-01..K1-L-05, K1-L-10, K1-L-15, ruling R-1b-5), and the
synthetic kit tests/test_k1_members_vwap.py reuses.

Synthetic bars only. Each rule is pinned on hand-built MNQ bars run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules), with direct calls where the engine cannot
reach a case (the clock at which V is read). The VXN table is replaced per test by patching
vxnband._VXN, except where the real table is the point (R-1b-5). No bar file is read and no runner
is run.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import check_member_source
from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules, load_release_calendar
from strategy.interface import Bar
from strategy.members.k1 import _event_common as common
from strategy.members.k1 import vxnband
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
REPO = Path(__file__).resolve().parents[1]
ROOT = "MNQ"
ID = 777  # the synthetic instrument_id
OTHER_ID = 778
BASE = 160_000  # ticks of 0.25: 40000.00 points, so V = 19.99 gives a whole-tick band (1999)
V_IN = "10.000000"  # a VXN close inside the regime (< 20): band w = C_prev / 160 = 1000 ticks
# Research-window full sessions (EQUITY_FULL_SESSIONS), no release used unless a test loads the
# frozen calendar: Tuesday..Thursday.
D0, D1, D2 = date(2025, 5, 20), date(2025, 5, 21), date(2025, 5, 22)


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


EVENING = hm(17, 0) - 24 * 60  # 17:00 CT on CT date d-1, counted from 00:00 of d


# --------------------------------------------------------------------- synthetic bars ----
def _step(points: Mapping[int, int], minute: int, default: int) -> int:
    """A step function: the value of the latest key <= ``minute`` (``default`` before any)."""
    keys = [k for k in points if k <= minute]
    return points[max(keys)] if keys else default


@dataclass(frozen=True)
class Day:
    """Synthetic MNQ bars of one trade date, one per minute in [start, end), minutes counted from
    00:00 CT of the trade date (negative: the previous CT date). ``closes`` and ``ids`` are step
    functions (a key sets the value from that minute on); O = C unless ``opens`` sets it; H and L
    span O and C and any ``highs`` / ``lows`` offset. Prices are ticks from ``base``."""

    trade_date: date
    start: int = hm(8, 0)
    end: int = hm(15, 10)
    closes: Mapping[int, int] = field(default_factory=dict)
    opens: Mapping[int, int] = field(default_factory=dict)
    highs: Mapping[int, int] = field(default_factory=dict)
    lows: Mapping[int, int] = field(default_factory=dict)
    volumes: Mapping[int, int] = field(default_factory=dict)
    volume: int = 10
    skip: frozenset[int] = frozenset()
    ids: Mapping[int, int] = field(default_factory=dict)
    halt: str = ""  # early_halt_ct on every bar ("" = none)
    base: int = BASE
    flatten_from: int | None = None  # a synthetic F: both window flags set from this minute


def px(ticks: int) -> float:
    return ticks * product(ROOT).vendor_tick_fixed / PRICE_SCALE


def ns_at(day: date, minute: int) -> int:
    """UTC ns of CT clock ``minute`` counted from 00:00 CT of ``day`` (any sign)."""
    on = day + timedelta(days=minute // 1440)
    m = minute % 1440
    return int(datetime.combine(on, time(m // 60, m % 60), tzinfo=CT).timestamp()) * NS


def _fields(d: Day, minute: int) -> dict[str, Any]:
    c = d.base + _step(d.closes, minute, 0)
    o = d.base + d.opens[minute] if minute in d.opens else c
    h = max(o, c, d.base + d.highs[minute]) if minute in d.highs else max(o, c)
    lo = min(o, c, d.base + d.lows[minute]) if minute in d.lows else min(o, c)
    ts = ns_at(d.trade_date, minute)
    state = sessions.session_state(ROOT, datetime.fromtimestamp(ts // NS, tz=UTC))
    synthetic_f = d.flatten_from is not None and minute >= d.flatten_from
    return {
        "ts_event": ts, "open": px(o), "high": px(h), "low": px(lo), "close": px(c),
        "volume": d.volumes.get(minute, d.volume), "instrument_id": _step(d.ids, minute, ID),
        "raw_symbol": "MNQM5", "trade_date": d.trade_date.isoformat(),
        "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
        "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
        "early_halt_ct": d.halt,
        "in_scheduled_closure": False, "is_roll_session": False, "gap_before_minutes": 0,
        "vendor_degraded_day": False}


def minutes(d: Day) -> list[int]:
    return [m for m in range(d.start, d.end) if m not in d.skip]


def frame(days: Sequence[Day]) -> pd.DataFrame:
    rows = [_fields(d, m) for d in days for m in minutes(d)]
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def bars(days: Sequence[Day]) -> list[Bar]:
    """The same bars as ``frame``, as Bar objects for direct calls."""
    out = []
    for d in days:
        for m in minutes(d):
            f = _fields(d, m)
            out.append(Bar(f["ts_event"], f["open"], f["high"], f["low"], f["close"], f["volume"],
                           f["instrument_id"], f["raw_symbol"], d.trade_date, False, False,
                           time.fromisoformat(d.halt) if d.halt else None, False, False, 0,
                           False))
    return out


def rules(days: Sequence[Day], releases: ReleaseCalendar = NO_RELEASES,
          blackout: Sequence[date] = (), cls: type = StageERules, **extra: Any) -> StageERules:
    return cls({ROOT: leg_inputs(ROOT, traded=True)}, frozenset(d.trade_date for d in days),
               frozenset(blackout), releases, **extra)


def run(member: Any, days: Sequence[Day], **kw: Any) -> EngineResult:
    return run_engine({ROOT: frame(days)}, member, member.legs, rules(days, **kw))


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit queued on the bars opening at
    ``force_at_ns`` while the leg holds exposure (a position the engine closes, S0.7)."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def ct_text(ns: int) -> str:
    return f"{datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT):%Y-%m-%d %H:%M}"


def at(day: date, hhmm: str) -> str:
    return f"{day.isoformat()} {hhmm}"


def side_of(received: str) -> str:
    return "buy" if "side='buy'" in received else "sell"


def intents(res: EngineResult) -> list[tuple[str, str, bool]]:
    """(the emitting bar's CT "YYYY-MM-DD HH:MM", side, accepted) of every intent, in order."""
    return [(ct_text(r.decision_ts_ns - 60 * NS), side_of(r.received), r.accepted)
            for r in res.events(IntentRecord)]


def fills(res: EngineResult) -> list[tuple[str, str, str]]:
    """(the fill bar's CT "YYYY-MM-DD HH:MM", side, reason) of every fill, in order."""
    return [(ct_text(f.fill_ts_ns), f.side, f.reason) for f in res.events(Fill)]


def trip(day: date, side: str, intent: str, fill: str, exit_intent: str, exit_fill: str
         ) -> tuple[list[tuple[str, str, bool]], list[tuple[str, str, str]]]:
    """The intents and fills of one round trip on ``day``."""
    back = "buy" if side == "sell" else "sell"
    return ([(at(day, intent), side, True), (at(day, exit_intent), back, True)],
            [(at(day, fill), side, "strategy"), (at(day, exit_fill), back, "strategy")])


def trips(res: EngineResult) -> tuple[list[tuple[str, str, bool]], list[tuple[str, str, str]]]:
    return intents(res), fills(res)


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def account_of(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({ROOT: position}), MappingProxyType({ROOT: pending}),
                             MappingProxyType({ROOT: None}), MappingProxyType({ROOT: 0}))


def call(member: Any, bar: Bar, position: int = 0, pending: int = 0) -> tuple:
    view = MinuteView(bar.ts_event_ns, MappingProxyType({ROOT: bar}))
    return tuple(member.on_minute(view, account_of(position, pending)))


def drive(member: Any, days: Sequence[Day],
          account: Callable[[Bar], tuple[int, int]] = lambda _b: (0, 0)
          ) -> list[tuple[str, tuple]]:
    """Call the member on every bar; (CT time of the bar, items) of every non-empty answer."""
    out = []
    for bar in bars(days):
        items = call(member, bar, *account(bar))
        if items:
            out.append((ct_text(bar.ts_event_ns), items))
    return out


# ------------------------------------------------------------ vxnband helpers ----
def use_vxn(monkeypatch: pytest.MonkeyPatch, table: Mapping[date, str]) -> None:
    monkeypatch.setattr(vxnband, "_VXN", {d: Decimal(v) for d, v in table.items()})


def band_days(closes: Mapping[int, int], **kw: Any) -> list[Day]:
    """D0 complete (14:59 close at BASE), then D1 with ``closes``."""
    return [Day(D0), Day(D1, closes=closes, **kw)]


def spike(minute: int, ticks: int) -> dict[int, int]:
    """A one-bar close ``ticks`` from BASE at ``minute``, BASE before and after."""
    return {minute: ticks, minute + 1: 0}


# ------------------------------------------------------------------ declaration ----
def test_declaration_label_leg_size_and_trading_window() -> None:
    m = vxnband.make_mnq()
    assert isinstance(m, StageEMember)
    assert m.name == "K1-vxnband-01 MNQ" == vxnband.MEMBER_ID + " MNQ"
    assert m.legs == (LegSpec("MNQ", True),)
    assert m.trading_windows == {"MNQ": (TradingInterval(time(8, 30), time(15, 0)),)}
    tables = load_frozen_tables()
    assert common.leg_facts().q == tables.vehicles["MNQ"].q_c == 1
    assert tables.day_session_ct["MNQ"] == (time(8, 30), time(15, 0))
    assert common.leg_facts().tick == product("MNQ").vendor_tick == Decimal("0.25")
    assert vxnband.make_mnq() is not m  # a fresh object per call


def test_member_files_pass_the_freeze_static_check() -> None:
    for name in ("_calendar.py", "_vxn.py", "_event_common.py", "vxnband.py", "vwap.py"):
        rel = f"strategy/members/k1/{name}"
        assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K1") == [], rel


# ------------------------------------------------------------------ the round trip ----
@pytest.mark.parametrize(("ticks", "side"), [(2000, "sell"), (-2000, "buy")])
def test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar(
        monkeypatch: pytest.MonkeyPatch, ticks: int, side: str) -> None:
    """Sell above U, buy below L; the exit intent goes on intent bar + 30 min (K1-L-05)."""
    use_vxn(monkeypatch, {D0: V_IN})
    res = run(vxnband.make_mnq(), band_days(spike(hm(9, 0), ticks)))
    assert trips(res) == trip(D1, side, "09:00", "09:01", "09:30", "09:31")


def test_a_breach_on_the_0830_bar_itself_trades(monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    res = run(vxnband.make_mnq(), band_days(spike(hm(8, 30), 2000)))
    assert trips(res) == trip(D1, "sell", "08:30", "08:31", "09:00", "09:01")


# ------------------------------------------------------------------ C_prev ----
INCOMPLETE = {
    "early_halt": {"halt": "12:00"},
    "missing_1459": {"skip": frozenset({hm(14, 59)})},
    "missing_0830": {"skip": frozenset({hm(8, 30)})},
    "two_ids": {"ids": {hm(12, 0): OTHER_ID, hm(12, 1): ID}},
}
COMPLETE = {
    "complete": {},
    "other_id_at_1500": {"ids": {hm(15, 0): OTHER_ID}},  # outside [08:30, 15:00): complete
}


@pytest.mark.parametrize("kind", [*INCOMPLETE, *COMPLETE])
def test_c_prev_is_the_1459_close_of_the_most_recent_complete_date(
        monkeypatch: pytest.MonkeyPatch, kind: str) -> None:
    """K1-L-03: D1 closes at +2000 at 14:59; an incomplete D1 is skipped, so C_prev is D0's close
    (BASE) and D2's +1001 breaches w = 1000 on its 08:30 bar; a complete D1 gives C_prev = +2000,
    w = 1012.5 and no breach all day. V of D2 is D1's VXN close either way (K1-L-02)."""
    use_vxn(monkeypatch, {D1: V_IN})
    d1 = Day(D1, closes={hm(14, 59): 2000}, **{**INCOMPLETE, **COMPLETE}[kind])
    days = [Day(D0), d1, Day(D2, closes={0: 1001})]
    res = run(vxnband.make_mnq(), days)
    if kind in COMPLETE:
        assert trips(res) == ([], [])
    else:
        assert trips(res) == trip(D2, "sell", "08:30", "08:31", "09:00", "09:01")


def test_c_prev_reads_the_1459_bar_not_the_1458_or_1500_bar(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D0's 14:58 and 15:00 bars sit far away; only its 14:59 close is C_prev."""
    use_vxn(monkeypatch, {D0: V_IN})
    d0 = Day(D0, closes={hm(14, 58): 5000, hm(14, 59): 0, hm(15, 0): -5000})
    res = run(vxnband.make_mnq(), [d0, Day(D1, closes=spike(hm(9, 0), 1001))])
    assert trips(res) == trip(D1, "sell", "09:00", "09:01", "09:30", "09:31")


def test_warm_up_without_a_complete_earlier_date_does_not_trade(
        monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    res = run(vxnband.make_mnq(), [Day(D1, closes=spike(hm(9, 0), 5000))])
    assert trips(res) == ([], [])


def test_the_c_prev_instrument_guard_against_the_0830_bar(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """C_prev's instrument_id must equal d's 08:30 bar's; a mismatch means no trade on d."""
    use_vxn(monkeypatch, {D0: V_IN})
    res = run(vxnband.make_mnq(), band_days(spike(hm(9, 0), 5000), ids={hm(0, 0): OTHER_ID}))
    assert trips(res) == ([], [])


def test_a_missing_0830_bar_means_no_trade(monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days({hm(8, 31): 5000, hm(8, 32): 0}, skip=frozenset({hm(8, 30)}))
    assert trips(run(vxnband.make_mnq(), days)) == ([], [])


# ------------------------------------------------------------------ V ----
@pytest.mark.parametrize(("table", "trades"), [
    ({D0: "25.000000", D1: V_IN}, False),  # d-1's V is outside the regime, d's own is inside
    ({D0: V_IN, D1: "25.000000"}, True),
    ({D1: V_IN}, False),  # only d's own close exists: missing V
])
def test_v_is_the_close_of_trade_date_d_minus_1_never_ds_own(
        monkeypatch: pytest.MonkeyPatch, table: dict[date, str], trades: bool) -> None:
    use_vxn(monkeypatch, table)
    res = run(vxnband.make_mnq(), band_days(spike(hm(9, 0), 2000)))
    assert trips(res) == (trip(D1, "sell", "09:00", "09:01", "09:30", "09:31") if trades
                          else ([], []))


def test_a_mondays_v_is_fridays_close_not_sundays(monkeypatch: pytest.MonkeyPatch) -> None:
    friday, sunday, monday = date(2025, 5, 16), date(2025, 5, 18), date(2025, 5, 19)
    days = [Day(friday), Day(monday, closes=spike(hm(9, 0), 2000))]
    use_vxn(monkeypatch, {sunday: V_IN, friday: "25.000000"})
    assert trips(run(vxnband.make_mnq(), days)) == ([], [])
    use_vxn(monkeypatch, {friday: V_IN})
    assert trips(run(vxnband.make_mnq(), days)) == trip(monday, "sell", "09:00", "09:01",
                                                        "09:30", "09:31")


def test_missing_v_the_tuesday_after_memorial_day_2025_does_not_trade(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """K1-L-02 / R-1b-5 on the real table: 2025-05-27's trade date d-1 is 2025-05-26 (an
    early-halt equity trade date, no VXN row); C_prev is Friday 2025-05-23's close. With a
    2025-05-26 row the same bars trade."""
    friday, holiday, tuesday = date(2025, 5, 23), date(2025, 5, 26), date(2025, 5, 27)
    assert vxnband.vxn_for(tuesday) is None
    assert common.PREVIOUS_TRADE_DATE[tuesday] == holiday
    assert vxnband.vxn_for(date(2025, 5, 28)) is not None  # the row of 2025-05-27 exists
    days = [Day(friday), Day(holiday, end=hm(12, 0), halt="12:00"),
            Day(tuesday, closes=spike(hm(9, 0), 5000))]
    assert trips(run(vxnband.make_mnq(), days)) == ([], [])
    use_vxn(monkeypatch, {holiday: V_IN})
    assert trips(run(vxnband.make_mnq(), days)) == trip(tuesday, "sell", "09:00", "09:01",
                                                        "09:30", "09:31")


class RecordingVxn(dict):
    """A VXN table that records, for every read, the open of the bar being processed."""

    def __init__(self, data: Mapping[date, Decimal], clock: list[int]) -> None:
        super().__init__(data)
        self.clock = clock
        self.reads: list[tuple[int, date]] = []

    def get(self, key: Any, default: Any = None) -> Any:
        self.reads.append((self.clock[0], key))
        return super().get(key, default)

    def __getitem__(self, key: Any) -> Any:
        self.reads.append((self.clock[0], key))
        return super().__getitem__(key)


def test_v_is_read_at_the_0830_bar_and_never_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """K1-L-01: no decision before d's 08:30 bar reads V; a breach on every earlier bar of trade
    date d (from 17:00 CT on d-1) sends nothing; the 08:30 bar's breach sells."""
    clock = [0]
    table = RecordingVxn({D0: Decimal(V_IN)}, clock)
    monkeypatch.setattr(vxnband, "_VXN", table)
    member = vxnband.make_mnq()
    days = [Day(D0), Day(D1, start=EVENING, end=hm(8, 40), closes={EVENING: 5000})]
    answers = []
    for bar in bars(days):
        clock[0] = bar.ts_event_ns
        items = call(member, bar)
        if items:
            answers.append((ct_text(bar.ts_event_ns), [i.side for i in items]))
    assert table.reads == [(ns_at(D1, hm(8, 30)), D0)]
    assert answers == [(at(D1, "08:30"), ["sell"])]


# ------------------------------------------------------------------ the band ----
@pytest.mark.parametrize(("ticks", "side"), [
    (1999, None), (2000, "sell"), (-1999, None), (-2000, "buy")])
def test_the_band_is_exact_a_close_on_u_or_l_does_not_trade(
        monkeypatch: pytest.MonkeyPatch, ticks: int, side: str | None) -> None:
    """V = 19.99 (two decimals), C_prev = 160000 ticks: w = 160000 x 19.99 / 1600 = 1999 ticks
    exactly, so U = C_prev + 1999 and L = C_prev - 1999 are prices; strict breaches only."""
    use_vxn(monkeypatch, {D0: "19.990000"})
    res = run(vxnband.make_mnq(), band_days(spike(hm(10, 0), ticks)))
    expected = ([], []) if side is None else trip(D1, side, "10:00", "10:01", "10:30", "10:31")
    assert trips(res) == expected


@pytest.mark.parametrize(("close", "prev", "v", "side"), [
    (161_999, 160_000, "19.990000", None), (162_000, 160_000, "19.990000", "sell"),
    (158_001, 160_000, "19.990000", None), (158_000, 160_000, "19.990000", "buy"),
    # C_prev = 160001: w = 1999.0124... ticks, never a whole tick
    (162_000, 160_001, "19.99", None), (162_001, 160_001, "19.99", "sell"),
    (158_002, 160_001, "19.99", None), (158_001, 160_001, "19.99", "buy"),
    (160_000, 160_000, "30.00", None), (163_000, 160_000, "30.00", None),
    (163_001, 160_000, "30.00", "sell"), (157_000, 160_000, "30.00", None),
    (156_999, 160_000, "30.00", "buy"),
])
def test_breach_side_in_integers(close: int, prev: int, v: str, side: str | None) -> None:
    assert vxnband.breach_side(close, prev, Decimal(v)) == side


# ------------------------------------------------------------------ the regime ----
@pytest.mark.parametrize(("v", "trades"), [
    ("19.990000", True), ("20.000000", False), ("29.990000", False), ("30.000000", True)])
def test_the_regime_cuts_v_below_20_or_at_least_30(
        monkeypatch: pytest.MonkeyPatch, v: str, trades: bool) -> None:
    use_vxn(monkeypatch, {D0: v})
    res = run(vxnband.make_mnq(), band_days(spike(hm(9, 0), 5000)))
    assert trips(res) == (trip(D1, "sell", "09:00", "09:01", "09:30", "09:31") if trades
                          else ([], []))


def test_in_regime_exactly() -> None:
    assert [vxnband.in_regime(Decimal(v)) for v in ("19.99", "20", "20.000000", "29.99",
                                                    "29.999999", "30", "30.000000", "45")] == [
        True, False, False, False, False, True, True, True]


# ------------------------------------------------------------------ the scan ----
def test_the_first_breach_uses_the_day_a_later_breach_is_ignored(
        monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    closes = {**spike(hm(9, 0), 2000), **spike(hm(9, 10), -2000), **spike(hm(11, 0), 3000)}
    res = run(vxnband.make_mnq(), band_days(closes))
    assert trips(res) == trip(D1, "sell", "09:00", "09:01", "09:30", "09:31")


def test_a_refused_first_breach_still_uses_the_day(monkeypatch: pytest.MonkeyPatch) -> None:
    """E.3-L-08: the engine refuses the 09:00 entry (a roll-blackout date); the 09:10 breach
    sends nothing."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days({**spike(hm(9, 0), 2000), **spike(hm(9, 10), -2000)})
    res = run(vxnband.make_mnq(), days, blackout=[D1])
    assert trips(res) == ([(at(D1, "09:00"), "sell", False)], [])
    assert res.events(IntentRecord)[0].refusal.reason == "engine_roll_blackout"


@pytest.mark.parametrize(("minute", "trades"), [(hm(14, 28), True), (hm(14, 29), False)])
def test_the_scan_ends_before_1429(monkeypatch: pytest.MonkeyPatch, minute: int,
                                   trades: bool) -> None:
    """A first breach on the 14:28 bar trades and exits on the 14:58 bar (fill 14:59); on the
    14:29 bar it does not trade."""
    use_vxn(monkeypatch, {D0: V_IN})
    res = run(vxnband.make_mnq(), band_days(spike(minute, 2000)))
    assert trips(res) == (trip(D1, "sell", "14:28", "14:29", "14:58", "14:59") if trades
                          else ([], []))


def test_a_missing_scan_bar_before_the_first_breach_ends_the_search(
        monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days(spike(hm(9, 5), 2000), skip=frozenset({hm(9, 0)}))
    assert trips(run(vxnband.make_mnq(), days)) == ([], [])


@pytest.mark.parametrize("breach", [hm(9, 0), hm(9, 5)])
def test_an_instrument_change_before_the_first_breach_ends_the_search(
        monkeypatch: pytest.MonkeyPatch, breach: int) -> None:
    """The 09:00 bar carries another instrument_id: a breach on it, or after it, does not
    trade."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days(spike(breach, 2000), ids={hm(9, 0): OTHER_ID, hm(9, 1): ID})
    assert trips(run(vxnband.make_mnq(), days)) == ([], [])


def test_a_missing_bar_after_the_first_breach_does_not_matter(
        monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days(spike(hm(9, 0), 2000), skip=frozenset({hm(9, 10)}))
    res = run(vxnband.make_mnq(), days)
    assert trips(res) == trip(D1, "sell", "09:00", "09:01", "09:30", "09:31")


# ------------------------------------------------------------------ the exit ----
def test_a_missing_exit_bar_sends_the_exit_on_the_first_later_bar(
        monkeypatch: pytest.MonkeyPatch) -> None:
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days(spike(hm(9, 0), 2000), skip=frozenset({hm(9, 30), hm(9, 31)}))
    res = run(vxnband.make_mnq(), days)
    assert trips(res) == trip(D1, "sell", "09:00", "09:01", "09:32", "09:33")


def test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Direct calls (S0.7, E.3-L-22): short from the 09:01 fill; on 09:30 an order is pending, so
    no exit; on 09:31 the exit goes; the position is still open on 09:32 (refused), so it is sent
    again."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days(spike(hm(9, 0), 2000), end=hm(9, 33))

    def account(bar: Bar) -> tuple[int, int]:
        if bar.trade_date != D1 or bar.ts_event_ns < ns_at(D1, hm(9, 1)):
            return (0, 0)
        return (-1, 1 if bar.ts_event_ns == ns_at(D1, hm(9, 30)) else 0)

    got = drive(vxnband.make_mnq(), days, account)
    assert [(t, [(i.side, i.quantity) for i in items]) for t, items in got] == [
        (at(D1, "09:00"), [("sell", 1)]), (at(D1, "09:31"), [("buy", 1)]),
        (at(D1, "09:32"), [("buy", 1)])]


def test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Direct calls (S0.6): flat but with an order pending on the 09:00 breach: no intent, and the
    09:10 breach (nothing pending) sends nothing either (the first breach used the day)."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days({**spike(hm(9, 0), 2000), **spike(hm(9, 10), -2000)}, end=hm(9, 20))

    def account(bar: Bar) -> tuple[int, int]:
        return (0, 1 if bar.ts_event_ns == ns_at(D1, hm(9, 0)) else 0)

    assert drive(vxnband.make_mnq(), days, account) == []


def test_an_engine_closure_ends_the_day(monkeypatch: pytest.MonkeyPatch) -> None:
    """S0.7: the engine closes the position (D9.7 at the 09:10 bar); the member sends no exit and
    no second entry on a later breach."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days({**spike(hm(9, 0), 2000), **spike(hm(9, 40), -3000)})
    res = run_engine({ROOT: frame(days)}, vxnband.make_mnq(), (LegSpec(ROOT, True),),
                     rules(days, cls=ForcedLimitRules,
                           force_at_ns=frozenset({ns_at(D1, hm(9, 10))})))
    assert intents(res) == [(at(D1, "09:00"), "sell", True)]
    assert [(t, s, r) for t, s, r in fills(res)] == [
        (at(D1, "09:01"), "sell", "strategy"), (at(D1, "09:11"), "buy", "price_limit_exit")]


def test_a_position_open_at_a_synthetic_f_is_flattened_by_the_engine(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Audit finding 4 (R-T3-1): a synthetic F from 09:10 (both window flags set); the engine's
    forced flatten fills at 09:11; the member sends no exit and no entry on the 09:40 breach."""
    use_vxn(monkeypatch, {D0: V_IN})
    days = band_days({**spike(hm(9, 0), 2000), **spike(hm(9, 40), -3000)}, flatten_from=hm(9, 10))
    res = run(vxnband.make_mnq(), days)
    assert intents(res) == [(at(D1, "09:00"), "sell", True)]
    assert fills(res) == [(at(D1, "09:01"), "sell", "strategy"),
                          (at(D1, "09:11"), "buy", "forced_flatten")]


# ------------------------------------------------------------------ the evening ----
def test_evening_bars_after_an_early_halt_holiday_are_not_read(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Audit finding 1 (R-T3-1), the real bars' shape: Memorial Day 2025-05-26 halts at 12:00;
    Tuesday 2025-05-27 opens at 17:00 CT on the holiday, and those evening bars carry the
    holiday's "12:00" label (by CT calendar date). Only bars of CT date d are read, so:
    - Tuesday (C_prev = Friday's close, the holiday is incomplete) sells its 09:00 breach;
    - Tuesday stays complete, so Wednesday's C_prev is Tuesday's 14:59 close (+2000, w = 1012.5):
      Wednesday's +1001 is no breach, and its 10:00 close of +987 (1013 below C_prev) buys.
    Reading the evening would mark Tuesday incomplete: C_prev = Friday's close, a sell on
    Wednesday's 08:30 bar instead."""
    fri, holiday, tue, wed = (date(2025, 5, 23), date(2025, 5, 26), date(2025, 5, 27),
                              date(2025, 5, 28))
    use_vxn(monkeypatch, {holiday: V_IN, tue: V_IN})
    days = [Day(fri), Day(holiday, end=hm(12, 0), halt="12:00"),
            Day(tue, start=EVENING, end=0, halt="12:00"),
            Day(tue, closes={**spike(hm(9, 0), 2000), hm(14, 59): 2000}),
            Day(wed, start=EVENING, closes={0: 1001, hm(10, 0): 987, hm(10, 1): 1001})]
    res = run(vxnband.make_mnq(), days)
    tue_trip = trip(tue, "sell", "09:00", "09:01", "09:30", "09:31")
    wed_trip = trip(wed, "buy", "10:00", "10:01", "10:30", "10:31")
    assert trips(res) == (tue_trip[0] + wed_trip[0], tue_trip[1] + wed_trip[1])


# ------------------------------------------------------------------ dates ----
def test_a_not_full_session_date_is_not_traded(monkeypatch: pytest.MonkeyPatch) -> None:
    """2025-07-03 is an equity trade date with an early halt and an early F (not in
    EQUITY_FULL_SESSIONS); 2025-07-02 is a full session."""
    wed, thu = date(2025, 7, 2), date(2025, 7, 3)
    assert common.is_full_session(wed) and not common.is_full_session(thu)
    use_vxn(monkeypatch, {date(2025, 7, 1): V_IN, wed: V_IN})
    days = [Day(date(2025, 7, 1)), Day(wed, closes=spike(hm(9, 0), 2000)),
            Day(thu, end=hm(11, 0), closes=spike(hm(9, 0), 2000))]
    res = run(vxnband.make_mnq(), days)
    assert trips(res) == trip(wed, "sell", "09:00", "09:01", "09:30", "09:31")


# ------------------------------------------------------------------ releases ----
def test_the_cpi_window_bars_send_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """K1-L-15: on CPI date 2025-05-13 (07:30 CT) breaches on the bars at 07:25-07:35 send no
    intent; the 08:30 bar's breach trades (fill 08:31)."""
    mon, tue = date(2025, 5, 12), date(2025, 5, 13)
    use_vxn(monkeypatch, {mon: V_IN})
    days = [Day(mon), Day(tue, start=hm(7, 20),
                          closes={hm(7, 25): 5000, hm(7, 36): 0, **spike(hm(8, 30), 2000)})]
    res = run(vxnband.make_mnq(), days, releases=load_release_calendar())
    assert trips(res) == trip(tue, "sell", "08:30", "08:31", "09:00", "09:01")


def test_event_minutes_fomc_1300_and_ism_0900(monkeypatch: pytest.MonkeyPatch) -> None:
    """The member reads no release: on FOMC 2025-05-07 a 12:59 breach is sent on 12:59 and its
    exit on 13:29 (the engine moves the entry fill to 13:02, D9.5a); on ISM Services 2025-05-05 a
    09:00 breach is sent on 09:00 (fill moved to 09:02) and its exit on 09:30."""
    cal = load_release_calendar()
    fri, mon, tue, wed = (date(2025, 5, 2), date(2025, 5, 5), date(2025, 5, 6),
                          date(2025, 5, 7))
    use_vxn(monkeypatch, {tue: V_IN})
    res = run(vxnband.make_mnq(), [Day(tue), Day(wed, closes=spike(hm(12, 59), 2000))],
              releases=cal)
    assert trips(res) == trip(wed, "sell", "12:59", "13:02", "13:29", "13:30")
    use_vxn(monkeypatch, {fri: V_IN})
    res = run(vxnband.make_mnq(), [Day(fri), Day(mon, closes=spike(hm(9, 0), -2000))],
              releases=cal)
    assert trips(res) == trip(mon, "buy", "09:00", "09:02", "09:30", "09:31")
